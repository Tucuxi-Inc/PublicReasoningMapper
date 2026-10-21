# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""mbox (including Gmail Takeout) and directories of .eml files."""

from __future__ import annotations

import email
import mailbox
import re
from email import policy
from email.utils import getaddresses, parsedate_to_datetime
from pathlib import Path

from . import html_to_text, insert_messages, iso


def _body(msg) -> tuple[str, str | None]:
    note = None
    try:
        part = msg.get_body(preferencelist=("plain", "html"))
    except Exception as e:                       # malformed MIME: keep the message
        part, note = None, f"body: {type(e).__name__}"
    if part is None:
        return "", note or "no text body"
    try:
        text = part.get_content()
    except Exception as e:
        payload = part.get_payload(decode=True) or b""
        text, note = payload.decode("utf-8", "replace"), f"decode: {type(e).__name__}"
    if part.get_content_subtype() == "html":
        text = html_to_text(text)
    return text, note


def _addrs(msg, field: str) -> list[str]:
    return [a.lower() for _, a in getaddresses(msg.get_all(field, []) or []) if a]


def parse(msg, source: str, ref: str, folder: str | None = None) -> dict:
    body, note = _body(msg)
    try:
        date = iso(parsedate_to_datetime(msg["Date"])) if msg["Date"] else None
    except Exception:
        date, note = None, (note or "") + " date unparsed"
    frm = getaddresses([msg.get("From", "")])
    mid = (msg.get("Message-ID") or "").strip().strip("<>") or None
    irt = (msg.get("In-Reply-To") or "").strip()
    labels = msg.get("X-Gmail-Labels") or ""
    return {
        "source": source, "source_ref": ref,
        "message_id": mid,
        "in_reply_to": irt.strip("<>") or None,
        "refs": re.findall(r"<([^>]+)>", msg.get("References") or ""),
        "subject": str(msg.get("Subject") or ""),
        "date": date,
        "from_address": (frm[0][1].lower() if frm and frm[0][1] else None),
        "from_name": (frm[0][0] if frm else None),
        "to_addresses": _addrs(msg, "To"),
        "cc_addresses": _addrs(msg, "Cc"),
        # Gmail puts Sent in a label rather than a folder.
        "folder": folder or ("Sent" if "sent" in labels.lower().split(",") else labels or None),
        "body_text": body,
        "ingest_note": note,
    }


def ingest_mbox(conn, source: str, path: Path, batch: int = 2000) -> str:
    box = mailbox.mbox(str(path), factory=lambda f: email.message_from_binary_file(
        f, policy=policy.default))
    rows, n, kept = [], 0, 0
    for i, msg in enumerate(box):
        n += 1
        if msg is None:
            continue
        rows.append(parse(msg, source, str(i)))
        if len(rows) >= batch:
            kept += insert_messages(conn, rows); rows = []
    kept += insert_messages(conn, rows)
    return f"{source}: {n:,} messages read, {kept:,} new"


def ingest_eml_dir(conn, source: str, path: Path) -> str:
    rows = []
    files = sorted(p for p in path.rglob("*.eml"))
    for p in files:
        with open(p, "rb") as fh:
            msg = email.message_from_binary_file(fh, policy=policy.default)
        folder = str(p.parent.relative_to(path)) if p.parent != path else None
        rows.append(parse(msg, source, str(p.relative_to(path)), folder))
    kept = insert_messages(conn, rows)
    return f"{source}: {len(files):,} files read, {kept:,} new"
