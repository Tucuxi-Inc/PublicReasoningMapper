# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Thread reconstruction.

Threading on normalised subject alone collapses unrelated mail - and worst on the
most interesting subjects, because a profession's generic labels ("privileged and
confidential", "incident", "urgent") are reused for years. So: RFC headers first,
then subject + shared participant inside a time window, then a separate pass that
attaches the expert's own sent copies, which often carry no headers at all.

Short messages are threaded too. Do not add a minimum-length filter here: a
two-word "approved, go ahead" is a thread turn, and it is the curt end of the
explanatory-vs-terse contrast the episode classifier needs.
"""

from __future__ import annotations

import collections
import hashlib
import re
from datetime import datetime, timedelta

from .store import loads

NORM = re.compile(r"^((re|fw|fwd|aw|tr|sv)\s*(\[[0-9]+\])?\s*:\s*)+", re.I)
BASE_GENERIC = {"", "re", "fw", "fwd", "question", "quick question", "update", "follow up",
                "hello", "hi", "thanks", "meeting", "introduction", "confidential", "urgent",
                "fyi", "call", "checking in"}


def norm_subject(s: str | None) -> str:
    return NORM.sub("", s or "").strip().lower()


def _dt(s: str | None) -> datetime:
    return datetime.fromisoformat(s) if s else datetime.min


def build(conn, generic_subjects=(), max_gap_days=45, max_span_days=365,
          min_chars=1) -> dict[str, list[int]]:
    max_gap, max_span = timedelta(days=max_gap_days), timedelta(days=max_span_days)
    generic = BASE_GENERIC | {g.lower() for g in generic_subjects}
    rows = conn.execute(
        """SELECT id, message_id, in_reply_to, refs, subject, date, from_address,
                  to_addresses, cc_addresses, is_expert
           FROM messages WHERE length(coalesce(body_text,'')) >= ? AND date IS NOT NULL
           ORDER BY date""", (min_chars,)).fetchall()
    if not rows:
        return {}
    parent = {r["id"]: r["id"] for r in rows}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    by_mid = {}
    for r in rows:
        if r["message_id"]:
            by_mid.setdefault(r["message_id"], r["id"])
    meta = {}
    for r in rows:
        people = {r["from_address"]} if r["from_address"] else set()
        people |= set(loads(r["to_addresses"], [])) | set(loads(r["cc_addresses"], []))
        meta[r["id"]] = (norm_subject(r["subject"]), _dt(r["date"]), people)

    # 1. RFC links
    for r in rows:
        for ref in ([r["in_reply_to"]] if r["in_reply_to"] else []) + loads(r["refs"], []):
            p = by_mid.get(ref)
            if p is not None and p != r["id"]:
                union(r["id"], p)

    # 2. distinctive subject + shared participant + no long gap
    bysub = collections.defaultdict(list)
    for eid, (ns, _, _) in meta.items():
        if ns and ns not in generic and len(ns) >= 12:
            bysub[ns].append(eid)
    for ids in bysub.values():
        ids.sort(key=lambda i: meta[i][1])
        for a, b in zip(ids, ids[1:]):
            if meta[b][1] - meta[a][1] <= max_gap and meta[a][2] & meta[b][2]:
                union(a, b)

    # 3. the expert's sent copies: nearest message with the same subject and a
    #    shared participant within 30 days. Generic subjects are allowed here -
    #    the participant overlap and tight window carry the constraint.
    sub_index = collections.defaultdict(list)
    for eid, (ns, d, _) in meta.items():
        if ns:
            sub_index[ns].append((d, eid))
    for r in rows:
        if not r["is_expert"]:
            continue
        ns, d, people = meta[r["id"]]
        best = None
        for od, oid in sub_index.get(ns, []):
            if oid == r["id"] or find(oid) == find(r["id"]):
                continue
            gap = abs((d - od).days)
            if gap <= 30 and people & meta[oid][2] and (best is None or gap < best[0]):
                best = (gap, oid)
        if best:
            union(r["id"], best[1])

    # 4. split anything still spanning too long
    groups = collections.defaultdict(list)
    for eid in parent:
        groups[find(eid)].append(eid)
    out = {}
    for ids in groups.values():
        ids.sort(key=lambda i: meta[i][1])
        cur = [ids[0]]
        for prev, nxt in zip(ids, ids[1:]):
            if meta[nxt][1] - meta[prev][1] > max_gap or meta[nxt][1] - meta[cur[0]][1] > max_span:
                out[_key(cur)] = cur
                cur = [nxt]
            else:
                cur.append(nxt)
        out[_key(cur)] = cur
    return out


def _key(ids: list[int]) -> str:
    return hashlib.sha1(",".join(map(str, sorted(ids))).encode()).hexdigest()[:16]


def persist(conn, threads: dict[str, list[int]]) -> None:
    conn.execute("DELETE FROM thread_members")
    conn.execute("DELETE FROM threads")
    for key, ids in threads.items():
        conn.execute("INSERT INTO threads (thread_key, n_messages) VALUES (?, ?)",
                     (key, len(ids)))
        conn.executemany(
            "INSERT INTO thread_members (thread_key, message, position) VALUES (?, ?, ?)",
            [(key, eid, n) for n, eid in enumerate(ids)])
    conn.execute("""
        UPDATE threads SET
          first_date = (SELECT min(m.date) FROM thread_members tm JOIN messages m ON m.id=tm.message
                        WHERE tm.thread_key = threads.thread_key),
          last_date  = (SELECT max(m.date) FROM thread_members tm JOIN messages m ON m.id=tm.message
                        WHERE tm.thread_key = threads.thread_key),
          expert_authored_chars = (
                        SELECT coalesce(sum(m.authored_chars),0) FROM thread_members tm
                        JOIN messages m ON m.id=tm.message
                        WHERE tm.thread_key = threads.thread_key AND m.is_expert=1)""")
    conn.commit()
