# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Episodes: the units the extractor reads.

A thread becomes one episode, classified by its shape. The classes come from how
expertise shows up in correspondence: the "why" is articulated while trust is
being built - when someone pushes back and the expert has to explain - and
compressed once trust exists. So:

    adjustment         expert -> other -> expert, the last turn substantive:
                       pushback answered. The richest explanatory material.
    substantive_reply  the expert says something substantive in response.
    curt_decision      the expert decides without explaining. The same expertise
                       with the reasoning compressed out - the contrast set, not noise.
    exchange           anything else with the expert in it.
    expert_only / no_expert

Every threshold is on AUTHORED characters. On raw body length, "substantive"
fires on any reply with a quote tail and "curt" on almost nothing.

Documents and think-aloud sessions are chunked into episodes of their own.
"""

from __future__ import annotations

import re

EXTRACT_BY_DEFAULT = ("adjustment", "substantive_reply", "document", "think_aloud")


def classify(turns_in: list[tuple[bool, int]], substantive: int, curt: int) -> str:
    """turns_in: [(is_expert, authored_chars)] in date order."""
    expert = [c for e, c in turns_in if e]
    if not expert:
        return "no_expert"
    if len(expert) == len(turns_in):
        return "expert_only"
    turns: list[list] = []                      # merge consecutive same-side messages
    for e, c in turns_in:
        if turns and turns[-1][0] == e:
            turns[-1][1] += c
        else:
            turns.append([e, c])
    if any(turns[i][0] and not turns[i + 1][0] and turns[i + 2][0]
           and turns[i + 2][1] >= substantive for i in range(len(turns) - 2)):
        return "adjustment"
    if any(t[0] and not turns[i - 1][0] and t[1] >= substantive
           for i, t in enumerate(turns) if i > 0):
        return "substantive_reply"
    if sum(expert) / len(expert) < curt:
        return "curt_decision"
    return "exchange"


def _thread_text(rows, max_turn: int, max_total: int) -> tuple[str, int]:
    parts, total = [], 0
    for n, r in enumerate(rows, 1):
        text = (r["authored_text"] or "").strip()
        if not text:
            continue
        # Trim long turns rather than drop late ones: an episode's shape is its
        # sequence, and cutting the tail removes the adjustment.
        if len(text) > max_turn:
            text = text[:max_turn].rsplit(" ", 1)[0] + " ..."
        tag = "EXPERT" if r["is_expert"] else "OTHER"
        parts.append(f"[{n}] {tag} ({(r['date'] or '')[:10]}):\n{text}")
        total += len(text)
        if total > max_total:
            break
    return "\n\n".join(parts), len(parts)


def chunk(text: str, size: int) -> list[str]:
    """Split on headings/blank-line paragraphs, packing up to `size` chars."""
    blocks = re.split(r"\n(?=#{1,3} )|\n\s*\n", text)
    out, cur = [], ""
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if cur and len(cur) + len(b) > size:
            out.append(cur)
            cur = ""
        while len(b) > size:
            out.append(b[:size])
            b = b[size:]
        cur = f"{cur}\n\n{b}" if cur else b
    if cur:
        out.append(cur)
    return out


def session_problems(text: str) -> list[str]:
    """A think-aloud transcript covering several problems is split at its problem
    markers ("## Problem", "PROBLEM:", "Exercise 3") so each becomes an episode."""
    parts = [p.strip() for p in re.split(
        r"(?im)^(?=(?:#{1,3}\s*)?(?:problem|exercise|scenario|case)\b[^\n]{0,80}$)", text) if p.strip()]
    if len(parts) > 1 and len(parts[0]) < 400:     # a title/preamble, not a problem
        parts = parts[1:]
    return parts


def build(conn, cfg: dict) -> dict[str, int]:
    sub, curt = cfg["substantive_chars"], cfg["curt_chars"]
    counts: dict[str, int] = {}
    conn.execute("DELETE FROM episodes WHERE id NOT IN (SELECT episode_id FROM extractions)")

    def put(eid, kind, et, n_turns, text):
        conn.execute(
            "INSERT INTO episodes (id, kind, episode_type, n_turns, text) VALUES (?,?,?,?,?) "
            "ON CONFLICT(id) DO UPDATE SET episode_type=excluded.episode_type, "
            "n_turns=excluded.n_turns, text=excluded.text, "
            "redacted=CASE WHEN episodes.text=excluded.text THEN episodes.redacted END",
            (eid, kind, et, n_turns, text))
        counts[et] = counts.get(et, 0) + 1

    for (tk,) in conn.execute("SELECT thread_key FROM threads WHERE n_messages >= 2").fetchall():
        rows = conn.execute(
            """SELECT m.is_expert, m.date, m.authored_text, coalesce(m.authored_chars,0) ac
               FROM thread_members tm JOIN messages m ON m.id = tm.message
               WHERE tm.thread_key = ? ORDER BY m.date""", (tk,)).fetchall()
        et = classify([(bool(r["is_expert"]), r["ac"]) for r in rows], sub, curt)
        conn.execute("UPDATE threads SET episode_type=? WHERE thread_key=?", (et, tk))
        text, n = _thread_text(rows, cfg["max_turn_chars"], cfg["max_episode_chars"])
        if n >= 2:
            put(f"thread:{tk}", "thread", et, n, text)

    size = cfg["document_chunk_chars"]
    for d in conn.execute("SELECT id, title, text FROM documents WHERE authored_by_expert=1"):
        for i, c in enumerate(chunk(d["text"], size)):
            put(f"doc:{d['id']}:{i}", "document", "document", 1, c)
    for s in conn.execute("SELECT id, title, text FROM sessions"):
        i = 0
        for prob in session_problems(s["text"]):
            for c in chunk(prob, size * 2):    # keep a problem's route together
                put(f"session:{s['id']}:{i}", "session", "think_aloud", 1, c)
                i += 1
    conn.commit()
    return counts
