# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Group moves into habits with a model judge; embeddings only shortlist.

Why not embedding clusters alone
--------------------------------
Embedding similarity measures topic, not stance or action. On every local
embedder tested while building this tool, a lexical near miss ("find what the
change costs") scored above a true paraphrase ("ask who pays if this goes wrong")
for "find who carries the cost", and the opposite habit ("diagnose first,
stabilise second") scored 0.89-0.99 against "stabilise first, diagnose second".
Clusters built that way put opposite habits together and split paraphrases apart.

So: moves are taken most-frequent first. For each, the embedder shortlists the
nearest existing habits (recall is cheap), and a model decides whether the move
is an instance of one of them - the same kind of thing, for the same reason, in
the same stance - or starts a new habit. An earlier, stricter wording ("same
action, same purpose, same stance") merged almost nothing on a real archive:
most moves stayed habits of one. Re-judging singletons, the shortlist length
made no difference (8 or 30); the wording did, several times over, and the looser
wording still passed every calibrated grouping, opposite-stance traps included.
The judge is itself calibrated on known groupings (`grouping` in known.yaml).

Output has the same shape as cluster.py, so the review sheet is identical.
"""

from __future__ import annotations

import collections
import random

import numpy as np

from .cluster import load_items

JUDGE = """You are grouping the reasoning moves of one experienced practitioner into habits.

A habit is a recurring way of reasoning that the practitioner would recognise and name, applied across different matters. Two moves are the same habit when they do the same kind of thing for the same reason, even if the specific situation, party or document differs. They are DIFFERENT habits if they do a different kind of thing, serve a different purpose, or take the opposite stance (for example, diagnosing before stabilising, versus stabilising before diagnosing).

NEW MOVE:
  {move}

EXISTING HABITS:
{habits}

Is the new move an instance of one of these habits? Return ONLY JSON:
{{"habit": <the habit's number, or null if none is the same habit>, "why": "one short sentence"}}"""


def _desc(name: str, det: dict) -> str:
    step = (det.get("step") or "").strip()
    return f"{name} - {step}" if step else name


def group(conn, embed, llm, kind: str = "move", shortlist: int = 8, seed: int = 0,
          key_prefix: str = "") -> dict:
    items = load_items(conn, kind)
    occ = collections.defaultdict(list)
    for n, eid, det, et in items:
        occ[n].append((eid, det, et))
    names = sorted(occ, key=lambda n: (-len(occ[n]), n))      # frequent first: they seed habits
    if len(names) < 2:
        raise SystemExit(f"only {len(names)} distinct {kind} names - extract more episodes first")
    desc = {n: _desc(n, occ[n][0][1]) for n in names}
    V = dict(zip(names, embed([desc[n] for n in names])))

    habits: list[dict] = []          # {"seed": name, "members": [...], "centroid": vec}
    calls = fails = 0
    for n in names:
        target = None
        if habits:
            C = np.vstack([h["centroid"] for h in habits])
            order = np.argsort(-(C @ V[n]))[:shortlist]
            listing = "\n".join(f"  {i + 1}. {desc[habits[h]['seed']]}" for i, h in enumerate(order))
            j, _, _ = llm.complete_json(JUDGE.format(move=desc[n], habits=listing), role="extract",
                                        task="group", key=f"{key_prefix}{kind}:{n}", redacted=True,
                                        max_tokens=200)
            calls += 1
            pick = (j or {}).get("habit") if isinstance(j, dict) else None
            if j is None:
                fails += 1
            if isinstance(pick, int) and 1 <= pick <= len(order):
                target = habits[int(order[pick - 1])]
        if target is None:
            habits.append({"seed": n, "members": [n], "centroid": V[n].copy()})
        else:
            target["members"].append(n)
            c = np.mean([V[m] for m in target["members"]], axis=0)
            target["centroid"] = c / (np.linalg.norm(c) + 1e-9)

    out = []
    for c, h in enumerate(habits):
        members = h["members"]
        sims = np.array([float(V[m] @ h["centroid"]) for m in members])
        order = sorted(range(len(members)), key=lambda i: -sims[i])
        o = [x for m in members for x in occ[m]]
        evidence = [{"episode": eid, "move": det.get("name") or det.get("what"),
                     "step": det.get("step"), "cue": det.get("cue"), "quote": det.get("evidence")}
                    for eid, det, _ in o if det.get("evidence")][:6]
        out.append({"members": members, "episodes": sorted({eid for eid, _, _ in o}),
                    "mentions": len(o), "coherence": round(float(sims.mean()), 3),
                    "core": [members[i] for i in order[:8]],
                    "sample": random.Random(seed + c).sample(members, min(8, len(members))),
                    "sources": dict(collections.Counter(et for _, _, et in o)),
                    "evidence": evidence})
    out.sort(key=lambda r: (-len(r["episodes"]), -r["mentions"]))
    prefix = "m" if kind == "move" else "c"
    for i, r in enumerate(out, 1):
        r["id"] = f"{prefix}{i:02d}"
    warn = None
    if calls and fails / calls > 0.1:
        warn = f"the judge gave no usable answer on {fails}/{calls} calls; those moves became new habits"
    return {"kind": kind, "k": len(out), "distinct": len(names), "mentions": len(items),
            "embedder": f"{embed.name} shortlist + model judge", "clusters": out, "warning": warn}


def check_grouping(cases, embed, llm) -> tuple[int, int, list[str]]:
    """Known groupings: every pair of moves must land together iff expected."""
    import sqlite3
    from .store import SCHEMA
    ok, notes = 0, []
    for ci, case in enumerate(cases or []):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.executescript(SCHEMA)
        conn.execute("INSERT INTO episodes (id, kind, episode_type, text) VALUES ('c', 'thread', 'x', '')")
        import json
        for m in case["moves"]:
            m = m if isinstance(m, dict) else {"name": m}
            conn.execute("INSERT INTO items (episode_id, kind, name, detail) VALUES ('c','move',?,?)",
                         (m["name"], json.dumps(m)))
        res = group(conn, embed, llm, "move", key_prefix=f"calibration{ci}:")
        got = {n: i for i, c in enumerate(res["clusters"]) for n in c["members"]}
        want = {n.lower(): i for i, g in enumerate(case["groups"]) for n in g}
        wrong = [(a, b) for a in want for b in want if a < b
                 and (want[a] == want[b]) != (got.get(a) == got.get(b))]
        ok += not wrong
        if wrong:
            notes.append(f"grouping case {ci}: {len(wrong)} pair(s) wrong, e.g. {wrong[0]}")
    return ok, len(cases or []), notes
