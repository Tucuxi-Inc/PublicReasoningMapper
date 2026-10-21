# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Outlook PST via libpff (`pip install reasoning-mapper[pst]`).

Two traps this module exists to avoid, both seen on a real 30GB archive:

* `get_number_of_attachments()` can RAISE on messages without attachments rather
  than return 0. A blanket per-message exception handler then discards every
  attachment-less message - three quarters of that archive - while the failure
  counter reads zero. Every per-field read here is guarded on its own, and a
  message is never dropped because one field could not be read; the reason is
  recorded in `ingest_note` instead.
* Locally composed copies in Sent Items usually carry no transport headers, so no
  Message-ID and no From address. Threading and expert attribution must not rely
  on headers alone (see threads.py and `mark_expert`).
"""

from __future__ import annotations

import re
from pathlib import Path

from . import ADDR, html_to_text, insert_messages, iso


def _s(v) -> str | None:
    if v is None:
        return None
    if isinstance(v, bytes):
        for enc in ("utf-8", "cp1252", "latin-1"):
            try:
                return v.decode(enc)
            except UnicodeDecodeError:
                pass
        return v.decode("utf-8", "replace")
    return str(v)


def _addrs(hdrs: str, field: str) -> list[str]:
    out = []
    for line in re.findall(rf"(?im)^{field}:(.*(?:\n[ \t].*)*)", hdrs):
        out += [a.lower() for a in ADDR.findall(line)]
    return list(dict.fromkeys(out))


def extract_one(m, source: str, folder: str, idx: int) -> dict:
    """Never raises."""
    notes = []

    def get(meth):
        try:
            return getattr(m, meth)()
        except Exception as e:
            notes.append(f"{meth}: {type(e).__name__}")
            return None

    hdrs = _s(get("get_transport_headers")) or ""
    date = get("get_delivery_time") or get("get_client_submit_time")
    body = None
    for meth in ("get_plain_text_body", "get_rtf_body"):
        b = get(meth)
        if b:
            body = _s(b)
            break
    if not body:
        body = html_to_text(_s(get("get_html_body")))
    frm = _addrs(hdrs, "From")
    mid = re.search(r"(?im)^Message-ID:\s*<([^>]+)>", hdrs)
    irt = re.search(r"(?im)^In-Reply-To:\s*<([^>]+)>", hdrs)
    refs = re.search(r"(?im)^References:(.*(?:\n[ \t].*)*)", hdrs)
    return {
        "source": source, "source_ref": f"{folder}#{idx}",
        "message_id": mid.group(1) if mid else None,
        "in_reply_to": irt.group(1) if irt else None,
        "refs": re.findall(r"<([^>]+)>", refs.group(1)) if refs else [],
        "subject": _s(get("get_subject")),
        "date": iso(date),
        "from_address": frm[0] if frm else None,
        "from_name": _s(get("get_sender_name")),
        "to_addresses": _addrs(hdrs, "To"),
        "cc_addresses": _addrs(hdrs, "Cc"),
        "folder": folder,
        "body_text": body or "",
        "ingest_note": "; ".join(notes) or None,
    }


def ingest_pst(conn, source: str, path: Path, batch: int = 2000) -> str:
    try:
        import pypff
    except ImportError as e:
        raise SystemExit("PST support needs libpff: pip install 'reasoning-mapper[pst]'") from e
    f = pypff.file()
    f.open(str(path))
    rows: list[dict] = []
    stats = {"walked": 0, "kept": 0, "unreadable": 0}

    def walk(folder, fpath):
        nonlocal rows
        try:
            n = folder.get_number_of_sub_messages()
        except Exception:
            n = 0
        for i in range(n):
            stats["walked"] += 1
            try:
                m = folder.get_sub_message(i)
            except Exception:
                stats["unreadable"] += 1       # counted, never silently dropped
                continue
            rows.append(extract_one(m, source, fpath, i))
            if len(rows) >= batch:
                stats["kept"] += insert_messages(conn, rows); rows = []
        try:
            k = folder.get_number_of_sub_folders()
        except Exception:
            k = 0
        for i in range(k):
            try:
                sf = folder.get_sub_folder(i)
                walk(sf, f"{fpath}/{sf.get_name()}")
            except Exception:
                stats["unreadable"] += 1

    walk(f.get_root_folder(), "")
    stats["kept"] += insert_messages(conn, rows)
    f.close()
    return (f"{source}: {stats['walked']:,} messages walked, {stats['kept']:,} new, "
            f"{stats['unreadable']:,} unreadable (reported, not hidden)")
