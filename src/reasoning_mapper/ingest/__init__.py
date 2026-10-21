# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Importers. Each source type writes rows into one shared schema; nothing
downstream needs to know where a message came from."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

from ..store import dumps

HTML_TAG = re.compile(r"<[^>]+>")
ADDR = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")


def html_to_text(h: str | None) -> str:
    if not h:
        return ""
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>", "\n", h)
    h = HTML_TAG.sub(" ", h)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&#39;", "'")):
        h = h.replace(a, b)
    return re.sub(r"[ \t]+", " ", h).strip()


def iso(d: datetime | None) -> str | None:
    if d is None:
        return None
    if d.tzinfo is not None:
        d = d.astimezone(timezone.utc).replace(tzinfo=None)
    return d.isoformat(timespec="seconds")


COLS = ["source", "source_ref", "message_id", "in_reply_to", "refs", "subject", "date",
        "from_address", "from_name", "to_addresses", "cc_addresses", "folder",
        "body_text", "ingest_note"]


def insert_messages(conn, rows: list[dict]) -> int:
    """Insert, skipping rows already ingested from the same source position."""
    vals = []
    for r in rows:
        r = dict(r)
        for k in ("refs", "to_addresses", "cc_addresses"):
            r[k] = dumps(r.get(k) or [])
        vals.append([r.get(c) for c in COLS])
    cur = conn.executemany(
        f"INSERT OR IGNORE INTO messages ({','.join(COLS)}) "
        f"VALUES ({','.join('?' * len(COLS))})", vals)
    conn.commit()
    return cur.rowcount


def insert_text(conn, table: str, source: str, path: Path, title: str, text: str,
                **extra) -> bool:
    sha = hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()
    cols = ["source", "path", "title", "text", "sha256", *extra]
    cur = conn.execute(
        f"INSERT OR IGNORE INTO {table} ({','.join(cols)}) "
        f"VALUES ({','.join('?' * len(cols))})",
        [source, str(path), title, text, sha, *extra.values()])
    conn.commit()
    return cur.rowcount == 1


def mark_expert(conn, addresses: set[str], names: list[str], sent_folders: list[str]) -> int:
    """Flag messages the expert sent. Address match first; display name and Sent
    folder as fallbacks, because locally composed copies often carry no address."""
    sent = [f.lower() for f in sent_folders]
    n = 0
    for r in conn.execute("SELECT id, from_address, from_name, folder FROM messages"):
        fa = (r["from_address"] or "").lower()
        fn = (r["from_name"] or "").lower()
        folder = (r["folder"] or "").lower().rstrip("/").rsplit("/", 1)[-1]
        mine = (fa in addresses
                or any(nm and nm in fn for nm in names)
                or folder in sent)
        if mine:
            n += 1
        conn.execute("UPDATE messages SET is_expert=? WHERE id=?", (int(mine), r["id"]))
    conn.commit()
    return n


def ingest_source(conn, project, src: dict) -> str:
    kind = src["type"]
    path = project.path(src["path"])
    name = src.get("name") or f"{kind}:{src['path']}"
    if kind == "pst":
        from .pst import ingest_pst
        return ingest_pst(conn, name, path)
    if kind == "mbox":
        from .mail import ingest_mbox
        return ingest_mbox(conn, name, path)
    if kind == "eml":
        from .mail import ingest_eml_dir
        return ingest_eml_dir(conn, name, path)
    if kind == "documents":
        from .documents import ingest_documents
        return ingest_documents(conn, name, path, bool(src.get("authored_by_expert", True)))
    if kind == "transcripts":
        from .transcripts import ingest_transcripts
        return ingest_transcripts(conn, name, path)
    raise ValueError(f"unknown source type {kind!r}")
