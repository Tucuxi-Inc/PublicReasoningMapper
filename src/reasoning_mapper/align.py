# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Align the expert's reviewed habits with the catalog of general reasoning approaches.

Runs only AFTER review. The catalog never reaches the extractor: a label in an
extraction prompt comes back as output, and the extraction would find the catalog
instead of the expert. Here the habits already exist, in the expert's own names.

Same shape as `group`: embeddings shortlist (they measure topic, so recall is all
they are trusted with), and a model judge decides which approaches the habit
actually applies. "None" is a first-class answer - a habit that no general
approach supplies is domain expertise, and often the most valuable thing found.
"""

from __future__ import annotations

import collections
from pathlib import Path

import numpy as np
import yaml

from .mapping import load_map, save_map

JUDGE = """Below is one reasoning habit of an experienced practitioner in {domain}, followed by general reasoning approaches from cognitive science, logic and decision research.

Which of these general approaches does the habit actually APPLY? Count an approach only if a specific step of the habit performs it - sharing a topic or a word is not enough. Most habits apply one or two; many apply none, because they encode domain know-how no general approach supplies. Returning an empty list is a correct and common answer.

HABIT: {name}
{description}
Steps:
{steps}

GENERAL APPROACHES:
{listing}

Return ONLY JSON:
{{"aligns_with": [{{"id": "approach-id", "step": "the habit step that performs it"}}],
 "beyond_general": "what the habit adds beyond the approaches it applies, one sentence"}}"""


def catalog_path(project=None) -> Path:
    if project is not None and project.data.get("catalog_path"):
        return project.path(project["catalog_path"])
    here = Path(__file__).resolve().parent
    for p in (here / "catalog" / "reasoning_catalog.yaml",                 # installed wheel
              here.parents[1] / "catalog" / "reasoning_catalog.yaml"):     # source checkout
        if p.exists():
            return p
    raise SystemExit("reasoning catalog not found; set catalog_path in rmap.yaml")


def load_catalog(project=None) -> dict:
    return yaml.safe_load(catalog_path(project).read_text())


def _entry_text(e: dict) -> str:
    return f"{e['name']}. {e['description']} " + "; ".join(e.get("signals") or [])


def _habit_text(p: dict) -> str:
    return f"{p['name']}. {p.get('description') or ''} " + " ".join(p.get("steps") or [])


def align_one(p: dict, entries: list[dict], E: np.ndarray, embed, llm, domain: str,
              shortlist: int, key: str):
    v = embed([_habit_text(p)])[0]
    order = np.argsort(-(E @ v))[:shortlist]
    cands = [entries[i] for i in order]
    listing = "\n".join(f"- {e['id']}: {e['name']} - {e['description']}" for e in cands)
    j, _, _ = llm.complete_json(
        JUDGE.format(domain=domain or "their field", name=p["name"],
                     description=p.get("description") or "",
                     steps="\n".join(f"- {s}" for s in p.get("steps") or []), listing=listing),
        role="extract", task="align", key=key, redacted=True, max_tokens=500)
    if not isinstance(j, dict):
        return None, None
    allowed = {e["id"] for e in cands}
    ids = []
    for a in j.get("aligns_with") or []:
        i, step = (a.get("id"), a.get("step")) if isinstance(a, dict) else (a, None)
        # never trust an id it was not shown, nor a match with no step behind it
        if i in allowed and step and i not in ids:
            ids.append(i)
    return ids, j.get("beyond_general")


def run(project, llm, embed, map_path: Path, shortlist: int = 12, redo: bool = False) -> dict:
    cat = load_catalog(project)
    entries = cat["entries"]
    E = embed([_entry_text(e) for e in entries])
    m = load_map(map_path)
    stats = collections.Counter()
    for p in m["patterns"]:
        if p.get("aligns_with") is not None and not redo:
            continue
        ids, beyond = align_one(p, entries, E, embed, llm, project["domain"], shortlist, p["id"])
        if ids is None:
            stats["judge failed"] += 1
            continue
        p["aligns_with"] = ids
        if beyond:
            p["beyond_general"] = beyond
        stats["aligned" if ids else "no general match"] += 1
    save_map(m, map_path)
    by_id = {e["id"]: e for e in entries}
    fams = collections.Counter(by_id[i]["family"] for p in m["patterns"]
                               for i in p.get("aligns_with") or [] if i in by_id)
    return {**stats,
            "unmatched (domain-specific)": [p["id"] for p in m["patterns"] if p.get("aligns_with") == []],
            "families drawn on": dict(fams.most_common()),
            "catalog entries used": len({i for p in m["patterns"] for i in p.get("aligns_with") or []}),
            "catalog size": len(entries)}


def check_alignment(cases, project, llm, embed, shortlist: int = 12) -> tuple[int, int, list[str]]:
    """Known alignments: every `expect` id returned, no `forbid` id returned, and
    nothing at all for `expect_none` cases - which test the judge's tendency to
    find a general approach in everything."""
    if not cases:
        return 0, 0, []
    entries = load_catalog(project)["entries"]
    E = embed([_entry_text(e) for e in entries])
    ok, notes = 0, []
    for i, c in enumerate(cases):
        p = {"name": c["name"], "description": c.get("description", ""), "steps": c.get("steps", [])}
        ids, _ = align_one(p, entries, E, embed, llm, project["domain"], shortlist, f"calibration{i}")
        ids = ids or []
        miss = [x for x in c.get("expect", []) if x not in ids]
        bad = [x for x in c.get("forbid", []) if x in ids]
        if c.get("expect_none"):        # pure domain know-how: any match is over-matching
            bad += [x for x in ids if x not in bad]
        ok += not miss and not bad
        if miss or bad:
            notes.append(f"alignment case {i}: missing {miss}, wrongly matched {bad}, got {ids}")
    return ok, len(cases), notes
