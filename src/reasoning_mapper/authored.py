# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Authored text: the part of a message its sender actually wrote.

Why this is the first transformation, not an optional one
---------------------------------------------------------
In a real reply-heavy archive the quoted chain is most of every body. On the
archive this tool was developed against, authored text was under a tenth of raw
body text, and half of all messages carried under 200 authored characters while
looking long on raw length. Anything measured on raw length - a "substantial
message" filter, an explanatory-vs-terse classification, an embedding window -
measures reply convention instead. One measured trend there reversed sign once
quotes were stripped. So the stripped text is stored once and every downstream
step reads it.

Conservative by design: cut at the FIRST marker. Over-cutting loses some authored
text that follows an inline quote and biases lengths down uniformly; under-cutting
leaves the quote tail and biases lengths up with thread age, which is a confound.
Uniform error beats age-correlated error.
"""

from __future__ import annotations

import re

# Ordered by how unambiguous they are. Each anchors at a line start.
MARKERS = [
    r"^-{2,}\s*Original Message\s*-{2,}",
    r"^_{10,}\s*$",
    r"^\s*From:\s.+$(?=\n\s*(Sent|Date|To):)",          # Outlook header block
    r"^On [^\n]{4,120}(?:\n[^\n]{0,120})?\swrote:\s*$",   # "On <date>, <x> wrote:", maybe wrapped
    r"^\s*>",                                             # classic quote prefix
    r"^\s*-{5,}\s*Forwarded message\s*-{5,}",
    r"^\s*\*?From:\*?\s.{0,120}\n\s*\*?Sent:\*?",
    r"^\s*Le .{4,80}\sa écrit\s*:\s*$",
    r"^\s*Am .{4,80}\sschrieb .{0,80}:\s*$",
]
_RE = re.compile("|".join(f"(?:{m})" for m in MARKERS), re.M | re.I)

# Signature blocks are authored but are not reasoning, and their length is
# constant per sender, which would distort any length comparison.
_SIG = re.compile(
    r"^\s*(?:--\s*$|Best regards|Kind regards|Warm regards|Regards,|Thanks,|"
    r"Thank you,|Best,|Cheers,|Sincerely|Sent from my )",
    re.M | re.I)


def authored(body: str, drop_signature: bool = True) -> str:
    """The part of `body` this sender actually wrote in this message."""
    if not body:
        return ""
    match = _RE.search(body)
    text = body[:match.start()] if match else body
    if drop_signature:
        sig = _SIG.search(text)
        # cut only when something precedes it: "Thanks, will do" is the message
        if sig and text[:sig.start()].strip():
            text = text[:sig.start()]
    return text.strip()


def materialise(conn, batch: int = 5000) -> int:
    """Compute and store authored text for every message that lacks it."""
    done = 0
    while True:
        rows = conn.execute(
            "SELECT id, body_text FROM messages WHERE authored_chars IS NULL LIMIT ?",
            (batch,)).fetchall()
        if not rows:
            return done
        vals = []
        for r in rows:
            t = authored(r["body_text"] or "")
            vals.append((t, len(t), r["id"]))
        conn.executemany(
            "UPDATE messages SET authored_text=?, authored_chars=? WHERE id=?", vals)
        conn.commit()
        done += len(rows)
