# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""The pattern map: reviewed clusters become patterns with tiers and orchestration.

`map/patterns.yaml` is the source of truth for the generated skills, and it is
meant to be edited by hand. `draft` and `link` only ever FILL empty fields; they
never overwrite something a person wrote.

Three tiers (docs/SKILL_FORMAT.md):
    1 structural     core analytical moves              orchestrated_by -> tier 3
    2 behavioral     applying them in kinds of situation orchestrated_by -> tier 3
    3 orchestration  choosing what a situation needs    source_skills   -> tier 1/2 (what it orchestrates)
                                                        works_with      <-> tier 3
"""

from __future__ import annotations

import collections
import json
import re
from pathlib import Path

import yaml

FIELDS = ["id", "tier", "name", "description", "when_to_apply", "steps",
          "quality_indicators", "failure_modes", "example", "notes",
          "source_skills", "orchestrated_by", "works_with", "co_occurs_with",
          "cross_references", "aligns_with", "beyond_general", "clusters", "support"]
SKILL_TIER = {1: "foundational", 2: "applied", 3: "strategic"}


def slug(s: str, limit: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:limit].rstrip("-") or "pattern"


def load_map(path: Path) -> dict:
    if not path.exists():
        return {"expert_label": "the expert", "patterns": []}
    return yaml.safe_load(path.read_text()) or {"patterns": []}


def save_map(m: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = []
    for p in m.get("patterns", []):
        ordered.append({k: p.get(k) for k in FIELDS if k in p}
                       | {k: v for k, v in p.items() if k not in FIELDS})
    head = ("# Pattern map. Edit freely: `rmap draft` and `rmap link` only fill empty fields.\n"
            "# expert_label is how skills refer to the person; keep it a role, not a name.\n")
    path.write_text(head + yaml.safe_dump({**{k: v for k, v in m.items() if k != "patterns"},
                                           "patterns": ordered},
                                          sort_keys=False, allow_unicode=True, width=100))


def kept_clusters(sheet_paths: list[Path]) -> list[dict]:
    """Apply keep/merge decisions. Returns one entry per kept (merged) cluster."""
    kept: dict[str, dict] = {}
    merges = []
    for sp in sheet_paths:
        sheet = yaml.safe_load(sp.read_text()) or {}
        full = json.loads(sp.with_suffix(".json").read_text())
        detail = {c["id"]: c for c in full["clusters"]}
        for c in sheet.get("clusters", []):
            d = (c.get("decision") or "undecided").lower()
            if d == "keep":
                if not c.get("tier"):
                    raise SystemExit(f"{sp.name}: cluster {c['id']} is kept but has no tier")
                kept[c["id"]] = {**c, "detail": detail[c["id"]], "from": [c["id"]]}
            elif d == "merge":
                merges.append((c, detail[c["id"]]))
    for c, det in merges:
        tgt = kept.get(c.get("merge_into"))
        if tgt is None:
            raise SystemExit(f"cluster {c['id']} merges into {c.get('merge_into')!r}, "
                             f"which is not a kept cluster")
        tgt["from"].append(c["id"])
        tgt["detail"] = {**tgt["detail"],
                         "members": tgt["detail"]["members"] + det["members"],
                         "episodes": sorted(set(tgt["detail"]["episodes"]) | set(det["episodes"])),
                         "evidence": tgt["detail"]["evidence"] + det["evidence"],
                         "mentions": tgt["detail"].get("mentions", 0) + det.get("mentions", 0),
                         "sources": dict(collections.Counter(tgt["detail"].get("sources") or {})
                                         + collections.Counter(det.get("sources") or {}))}
    return list(kept.values())


DRAFT = """You are writing one entry in an apprentice's guide to how a particular experienced practitioner in {domain} reasons. The entry describes ONE habit of reasoning, which the practitioner has named "{name}". Below is the evidence: moves extracted from their own work, with the cues that prompted them and their own words.

Write only what the evidence supports. Do not add textbook advice, generic best practice, or steps that no evidence shows. If the evidence is thin, write less. Never include names of people, companies or products; bracketed tags like [PERSON_1] stand for them - describe roles instead. Refer to the practitioner as "{label}".

Practitioner's own note on this habit (authoritative where it conflicts with the evidence): {notes}

EVIDENCE:
{evidence}

Return ONLY JSON:
{{"description": "one or two sentences: what this habit is and what it achieves",
 "when_to_apply": ["a situation cue that should trigger this habit", "..."],
 "steps": ["imperative step an apprentice can follow", "..."],
 "quality_indicators": ["how you can tell it was done well", "..."],
 "failure_modes": ["how it goes wrong or gets misapplied", "..."],
 "example": "a short composite example in the abstract, with no identifiers"}}"""


def _evidence_text(det: dict, limit: int = 12) -> str:
    lines = []
    for m in det["members"][:20]:
        lines.append(f"- move name: {m}")
    for e in det["evidence"][:limit]:
        lines.append(f"- step: {e.get('step')} | cue: {e.get('cue')} | words: {e.get('quote')}")
    return "\n".join(lines)


def draft(project, llm, sheet_paths: list[Path], map_path: Path) -> dict:
    m = load_map(map_path)
    if not map_path.exists():
        m["expert_label"] = project["expert_label"]
    by_cluster = {cid: p for p in m["patterns"] for cid in (p.get("clusters") or [])}
    by_id = {p["id"]: p for p in m["patterns"]}
    prefix = slug(project["skill_prefix"], 20)
    stats = collections.Counter()
    for c in kept_clusters(sheet_paths):
        name = c.get("name") or c["detail"]["core"][0]
        pid = f"{prefix}-{slug(name, 63 - len(prefix))}"
        # matched by cluster id, or by name when the clusters were regenerated
        p = by_cluster.get(c["id"]) or by_id.get(pid)
        if p is None:
            p = {"id": pid, "tier": int(c["tier"]), "name": name, "clusters": c["from"]}
            m["patterns"].append(p)
            by_id[pid] = p
            stats["new"] += 1
        else:
            p["clusters"] = c["from"]
        p["support"] = {"episodes": len(c["detail"]["episodes"]),
                        "sources": c["detail"].get("sources", {})}
        p["_episodes"] = {"episodes": c["detail"]["episodes"],
                          "evidence": [{"episode": e["episode"], "quote": e["quote"]}
                                       for e in c["detail"]["evidence"] if e.get("quote")]}
        if c.get("notes") and not p.get("notes"):
            p["notes"] = c["notes"]
        if p.get("description") and p.get("steps"):
            continue
        j, _, _ = llm.complete_json(
            DRAFT.format(domain=project["domain"] or "their field", name=p["name"],
                         label=m["expert_label"], notes=p.get("notes") or "(none)",
                         evidence=_evidence_text(c["detail"])),
            role="extract", task="draft", key=p["id"], redacted=True, max_tokens=1400)
        if not j:
            stats["draft failed"] += 1
            continue
        for k in ("description", "when_to_apply", "steps", "quality_indicators",
                  "failure_modes", "example"):
            if not p.get(k) and j.get(k):
                p[k] = j[k]
        stats["drafted"] += 1
    _persist_episodes(m, map_path)
    save_map(m, map_path)
    return dict(stats)


def _persist_episodes(m: dict, map_path: Path) -> None:
    """Episode membership is bulky and not for hand-editing: keep it beside the map."""
    side = map_path.with_name("pattern_episodes.json")
    side.parent.mkdir(parents=True, exist_ok=True)
    old = json.loads(side.read_text()) if side.exists() else {}
    for p in m["patterns"]:
        if "_episodes" in p:
            old[p["id"]] = p.pop("_episodes")
    side.write_text(json.dumps(old, indent=1))


ORCHESTRATE = """An experienced practitioner's reasoning has been mapped into habits. Tier 3 habits are orchestration: they decide WHICH approach a situation needs, how deep to go, and when to stop. Every other habit should be called on by at least one of them.

HABIT (tier {tier}): {name}
  {description}

ORCHESTRATION HABITS:
{listing}

Which ONE orchestration habit, when it fires, is the one that would call on this habit? Choose null if none of them plausibly would. Return ONLY JSON:
{{"orchestrator": <its number, or null>, "why": "one short sentence"}}"""


def _judge_orchestrators(pats: dict, eps: dict, llm, listing_cap: int = 25) -> int:
    """For tier 1/2 patterns that co-occurrence left without an orchestrator, ask a
    model which tier 3 pattern would call on them. Co-occurrence is sparse on a large
    map (most habit pairs never share two episodes), so without this most of the map
    is orphaned. Judged links are marked as such in link_basis for review."""
    t3 = [a for a, p in pats.items() if p["tier"] == 3]
    n = 0
    for a, p in pats.items():
        if p["tier"] not in (1, 2) or p.get("orchestrated_by") or not t3:
            continue
        A = set(eps.get(a, []))
        cands = sorted(t3, key=lambda b: (-len(A & set(eps.get(b, []))), b))[:listing_cap]
        listing = "\n".join(f"  {i + 1}. {pats[b]['name']}: {(pats[b].get('description') or '').strip()[:240]}"
                            for i, b in enumerate(cands))
        j, _, _ = llm.complete_json(
            ORCHESTRATE.format(tier=p["tier"], name=p["name"], listing=listing,
                               description=(p.get("description") or "").strip()[:400]),
            role="extract", task="link", key=a, redacted=True, max_tokens=200)
        pick = j.get("orchestrator") if isinstance(j, dict) else None
        if not (isinstance(pick, int) and 1 <= pick <= len(cands)):
            continue
        b = cands[pick - 1]
        p["orchestrated_by"] = [b]
        pats[b]["source_skills"] = list(pats[b].get("source_skills") or []) + [a]
        why = str(j.get("why") or "").strip()
        p.setdefault("link_basis", {})[b] = {"judged": why}
        pats[b].setdefault("link_basis", {})[a] = {"judged": why}
        n += 1
    return n


def link(map_path: Path, min_shared: int = 2, llm=None) -> dict:
    """Propose orchestration from co-occurrence: patterns that show up in the same
    episodes. Fills only EMPTY relationship fields, and records the basis so a
    reviewer can see why a link was proposed. With `llm`, a model then proposes an
    orchestrator for each tier 1/2 pattern that co-occurrence left without one."""
    m = load_map(map_path)
    side = json.loads(map_path.with_name("pattern_episodes.json").read_text())
    eps = {k: v["episodes"] for k, v in side.items()}
    pats = {p["id"]: p for p in m["patterns"]}
    universe = set().union(*[set(v) for v in eps.values()]) if eps else set()
    N = max(len(universe), 1)

    def lift(a, b):
        A, B = set(eps.get(a, [])), set(eps.get(b, []))
        s = len(A & B)
        return s, (s * N / (len(A) * len(B)) if A and B else 0.0)

    pairs = {}
    ids = list(pats)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            s, l = lift(a, b)
            if s >= min_shared and l > 1.0:
                pairs[(a, b)] = (s, round(l, 2))

    def related(a):
        out = []
        for (x, y), v in pairs.items():
            if a in (x, y):
                out.append((y if x == a else x, *v))
        return sorted(out, key=lambda t: (-t[2], -t[1]))

    stats = collections.Counter()
    for a, p in pats.items():
        rel = related(a)
        if not p.get("co_occurs_with"):
            p["co_occurs_with"] = [b for b, *_ in rel]
        if p["tier"] == 3:
            if not p.get("source_skills"):
                p["source_skills"] = [b for b, *_ in rel if pats[b]["tier"] in (1, 2)]
                stats["source_skills proposed"] += bool(p["source_skills"])
            if not p.get("works_with"):
                p["works_with"] = [b for b, *_ in rel if pats[b]["tier"] == 3]
        p["link_basis"] = {b: {"shared_episodes": s, "lift": l} for b, s, l in rel}
    # mirror downward links upward, and make works_with reciprocal
    for a, p in pats.items():
        if p["tier"] != 3:
            continue
        for b in p.get("source_skills") or []:
            q = pats.get(b)
            if q is not None and a not in (q.get("orchestrated_by") or []):
                q.setdefault("orchestrated_by", [])
                q["orchestrated_by"] = list(q["orchestrated_by"] or []) + [a]
        for b in p.get("works_with") or []:
            q = pats.get(b)
            if q is not None and a not in (q.get("works_with") or []):
                q["works_with"] = list(q.get("works_with") or []) + [a]
    if llm is not None:
        stats["orchestrators judged"] = _judge_orchestrators(pats, eps, llm)
    save_map(m, map_path)
    orphans = [a for a, p in pats.items() if p["tier"] in (1, 2) and not p.get("orchestrated_by")]
    idle = [a for a, p in pats.items() if p["tier"] == 3 and not p.get("source_skills")]
    return {**stats, "pairs": len(pairs), "unorchestrated": orphans, "orchestrating nothing": idle}
