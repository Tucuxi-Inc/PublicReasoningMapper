# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Cluster the free-text moves and considerations into candidate patterns, and
write a review sheet for the expert.

A cluster is a CANDIDATE. Only the expert can say whether "checks who absorbs the
downside" and "asks who pays if this goes wrong" are one habit or two, and what
it should be called. The sheet records those calls; nothing downstream reads a
cluster the expert has not kept.

Inspection aids, each from a way review went wrong before:
* `core` lists the members nearest the centroid, and `sample` a seeded random
  draw. A sorted head (alphabetical) makes every cluster look equally
  miscellaneous.
* `coherence` is the mean cosine of members to their centroid, so the judgement
  does not rest on eyeballing alone.
* A cluster holding over 40% of names is flagged as a catch-all: k is too small.
"""

from __future__ import annotations

import collections
import json
import random

import numpy as np
import yaml

SHEET_HELP = """\
# Review sheet. For each cluster set:
#   decision:   keep | drop | merge      (undecided clusters are ignored)
#   merge_into: <cluster id>             (when decision is merge)
#   name:       what YOU call this habit, in your own words
#   tier:       1 structural   - a core way of analysing (framing, weighing, testing)
#               2 behavioral   - how you apply it in a kind of situation or with people
#               3 orchestration - how you decide WHICH approach a situation needs
#   notes:      anything an apprentice should know that the evidence misses
# Similarities compress: rank by `episodes`, do not threshold coherence into a verdict.
"""


def load_items(conn, kind: str):
    rows = conn.execute("""SELECT i.episode_id, i.name, i.detail, e.episode_type
                           FROM items i JOIN episodes e ON e.id = i.episode_id
                           WHERE i.kind = ?""", (kind,)).fetchall()
    return [(r["name"].strip().lower(), r["episode_id"], json.loads(r["detail"] or "{}"),
             r["episode_type"]) for r in rows]


def cluster(conn, embed, kind: str = "move", k: int = 0, seed: int = 0) -> dict:
    from sklearn.cluster import AgglomerativeClustering

    items = load_items(conn, kind)
    names = sorted({n for n, *_ in items})
    if len(names) < 4:
        raise SystemExit(f"only {len(names)} distinct {kind} names - extract more episodes first")
    V = embed(names)
    k = k or max(2, min(len(names) - 1, int(round((len(names) / 2) ** 0.5))))
    labels = AgglomerativeClustering(n_clusters=k, metric="cosine",
                                     linkage="average").fit_predict(V)
    by_name = collections.defaultdict(list)
    for n, eid, det, et in items:
        by_name[n].append((eid, det, et))

    out = []
    for c in range(k):
        idx = [i for i, l in enumerate(labels) if l == c]
        members = [names[i] for i in idx]
        cent = V[idx].mean(axis=0)
        cent /= np.linalg.norm(cent) + 1e-9
        sims = V[idx] @ cent
        order = sorted(range(len(members)), key=lambda i: -float(sims[i]))
        occ = [o for m in members for o in by_name[m]]
        eps = sorted({eid for eid, _, _ in occ})
        types = collections.Counter(et for _, _, et in occ)
        evidence = []
        for eid, det, _ in occ[:200]:
            q = det.get("evidence")
            if q and len(evidence) < 6:
                evidence.append({"episode": eid, "move": det.get("name") or det.get("what"),
                                 "step": det.get("step"), "cue": det.get("cue"), "quote": q})
        out.append({
            "members": members, "episodes": eps, "mentions": len(occ),
            "coherence": round(float(sims.mean()), 3),
            "core": [members[i] for i in order[:8]],
            "sample": random.Random(seed + c).sample(members, min(8, len(members))),
            "sources": dict(types), "evidence": evidence,
        })
    out.sort(key=lambda r: (-len(r["episodes"]), -r["mentions"]))
    prefix = "m" if kind == "move" else "c"
    for n, r in enumerate(out, 1):
        r["id"] = f"{prefix}{n:02d}"
    big = max(out, key=lambda r: len(r["members"]))
    warn = None
    if len(big["members"]) > 0.4 * len(names):
        warn = (f"{big['id']} holds {len(big['members'])}/{len(names)} names - a catch-all. "
                f"Re-run with a larger --k.")
    return {"kind": kind, "k": k, "distinct": len(names), "mentions": len(items),
            "embedder": embed.name, "clusters": out, "warning": warn}


def write_sheet(result: dict, path, force: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        old = yaml.safe_load(path.read_text()) or {}
        if any(c.get("decision") not in (None, "undecided") for c in old.get("clusters", [])):
            raise SystemExit(f"{path} already holds review decisions; pass --force to overwrite "
                             f"them, or --sheet to write elsewhere")
    sheet = {"kind": result["kind"], "embedder": result["embedder"], "k": result["k"],
             "distinct_names": result["distinct"], "mentions": result["mentions"],
             "warning": result["warning"], "clusters": []}
    for c in result["clusters"]:
        sheet["clusters"].append({
            "id": c["id"], "decision": "undecided", "merge_into": None, "name": "",
            "tier": None, "notes": "",
            "episodes": len(c["episodes"]), "mentions": c["mentions"],
            "coherence": c["coherence"], "sources": c["sources"],
            "core": c["core"], "sample": c["sample"],
            "evidence": [{k: v for k, v in e.items() if k != "episode"} for e in c["evidence"][:4]],
        })
    path.write_text(SHEET_HELP + yaml.safe_dump(sheet, sort_keys=False, allow_unicode=True, width=100))
    path.with_suffix(".json").write_text(json.dumps(result, indent=1, ensure_ascii=False))
