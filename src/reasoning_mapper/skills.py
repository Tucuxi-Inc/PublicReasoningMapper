# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Write the pattern map as Claude skills: one folder per pattern, plus a router.

Two frontmatter styles:

    native    orchestration fields at the top level of the frontmatter
              (pattern_tier, orchestrated_by, source_skills, ...). Readable by
              any tool that loads the YAML; Claude Code ignores keys it does not use.
    portable  only `name` and `description` at the top level, everything else
              under `metadata` as comma-separated strings, for loaders that accept
              only the core Agent Skills keys.

Both read back identically through `validate.check_skills_dir`.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from .mapping import SKILL_TIER, load_map
from .validate import check_patterns

TIER_LABEL = {1: "Tier 1 - structural", 2: "Tier 2 - behavioral", 3: "Tier 3 - orchestration"}
REL = ("source_skills", "orchestrated_by", "works_with", "co_occurs_with", "cross_references")
GENERATED = ".rmap-generated"


def _desc(p: dict) -> str:
    d = (p.get("description") or "").strip()
    w = p.get("when_to_apply") or []
    if w:
        d += " Use when " + "; ".join(x.rstrip(".") for x in w[:4]) + "."
    return d[:1024]


def frontmatter(p: dict, style: str, version: str) -> dict:
    rel = {k: list(p.get(k) or []) for k in REL}
    rel = {k: v for k, v in rel.items() if v or k in (("source_skills", "works_with")
                                                     if p["tier"] == 3 else ("orchestrated_by",))}
    core = {"pattern_tier": p["tier"], "skill_tier": SKILL_TIER[p["tier"]], **rel}
    if p.get("aligns_with"):
        core["aligns_with"] = list(p["aligns_with"])    # catalog ids, not skills
    core["version"] = version
    if style == "portable":
        meta = {k: (", ".join(v) if isinstance(v, list) else str(v)) for k, v in core.items()}
        return {"name": p["id"], "description": _desc(p), "metadata": meta}
    return {"name": p["id"], "description": _desc(p), **core}


def _bullets(xs) -> str:
    return "\n".join(f"- {x}" for x in xs or [])


def body(p: dict, pats: dict, label: str, include_evidence: bool, evidence: list,
         catalog: dict | None = None) -> str:
    def ref(i):
        q = pats.get(i)
        return f"`{i}` ({q['name']})" if q else f"`{i}`"

    out = [f"# {p['name']}", "", f"*{TIER_LABEL[p['tier']]} pattern in how {label} reasons.*", "",
           "## Overview", "", (p.get("description") or "").strip(), ""]
    if p.get("when_to_apply"):
        out += ["## When to apply", "", _bullets(p["when_to_apply"]), ""]
    if p.get("steps"):
        out += ["## Core procedure", ""]
        out += [f"{n}. {s}" for n, s in enumerate(p["steps"], 1)] + [""]
    if p["tier"] == 3 and p.get("source_skills"):
        out += ["## What this orchestrates", "",
                "When this pattern is active, decide which of these the situation needs and "
                "apply them in that light:", "",
                _bullets(ref(i) for i in p["source_skills"]), ""]
        if p.get("works_with"):
            out += ["Often active alongside: " + ", ".join(ref(i) for i in p["works_with"]) + ".", ""]
    if p.get("orchestrated_by"):
        out += ["## Orchestrated by", "", _bullets(ref(i) for i in p["orchestrated_by"]), ""]
    if p.get("quality_indicators"):
        out += ["## Quality indicators", "", _bullets(p["quality_indicators"]), ""]
    if p.get("failure_modes"):
        out += ["## Common pitfalls", "", _bullets(p["failure_modes"]), ""]
    if p.get("notes"):
        out += [f"## In {label}'s words", "", p["notes"].strip(), ""]
    if p.get("example"):
        out += ["## Example", "", p["example"].strip(), ""]
    if p.get("aligns_with") is not None and catalog is not None:
        out += ["## General approaches this builds on", ""]
        if p["aligns_with"]:
            out += [f"- **{catalog[i]['name']}** - {catalog[i]['description']}"
                    for i in p["aligns_with"] if i in catalog]
        else:
            out += ["None in the general catalog: this is domain know-how."]
        if p.get("beyond_general"):
            out += ["", f"What {label} adds: {p['beyond_general'].strip()}"]
        out += [""]
    if include_evidence and evidence:
        out += ["## Evidence", "", "Redacted excerpts from the work this pattern was drawn from:", ""]
        out += [f"> {e}" for e in evidence[:3]] + [""]
    sup = p.get("support") or {}
    if sup.get("episodes"):
        out += ["---", f"*Drawn from {sup['episodes']} episodes of {label}'s own work.*", ""]
    return "\n".join(out)


def router(m: dict, pats: dict, prefix: str, domain: str, style: str, version: str) -> tuple[str, str]:
    label = m.get("expert_label") or "the expert"
    name = f"{prefix}-reasoning"
    desc = (f"How {label} approaches problems in {domain or 'their field'}. Start here for any "
            f"situation in that field: it says which reasoning patterns to activate and in what order.")[:1024]
    fm = {"name": name, "description": desc}
    fm.update({"metadata": {"role": "router", "version": version}} if style == "portable"
              else {"role": "router", "version": version})
    t3 = [p for p in pats.values() if p["tier"] == 3]
    lines = [f"# Reasoning like {label}", "",
             f"This skill set encodes how {label} reasons about problems in {domain or 'their field'}, "
             "drawn from their own correspondence, documents and think-aloud sessions. It has three tiers:", "",
             "- **Tier 3 - orchestration**: how they decide what a situation needs. Start here.",
             "- **Tier 2 - behavioral**: how they apply analysis in particular kinds of situation.",
             "- **Tier 1 - structural**: the core analytical moves.", "",
             "## Procedure", "",
             "1. Read the situation. Before analysing, check it against the activation cues below "
             "and note every tier 3 pattern that matches.",
             "2. Open each matching tier 3 skill. It names the tier 1 and 2 skills it orchestrates; "
             "use the ones the situation actually calls for.",
             "3. Work the problem with those skills, in the order the orchestrating pattern suggests.",
             f"4. Say plainly where the situation falls outside what these patterns cover. They describe "
             f"how {label} has reasoned, not every case; do not stretch a pattern to fit.", "",
             "## Activation cues (tier 3)", ""]
    for p in sorted(t3, key=lambda x: x["id"]):
        cues = "; ".join(p.get("when_to_apply") or []) or "(no cues recorded)"
        lines += [f"- `{p['id']}` - **{p['name']}**: {cues}"]
    lines += ["", "## Orchestration map", ""]
    for p in sorted(t3, key=lambda x: x["id"]):
        lines += [f"- `{p['id']}` orchestrates: "
                  + (", ".join(f"`{i}`" for i in p.get("source_skills") or []) or "-")]
    lines += ["", "## All patterns", "", "| Skill | Tier | Pattern |", "|---|---|---|"]
    for p in sorted(pats.values(), key=lambda x: (-x["tier"], x["id"])):
        lines += [f"| `{p['id']}` | {p['tier']} | {p['name']} |"]
    text = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=1000) + "---\n\n" + "\n".join(lines) + "\n"
    return name, text


def write(project, map_path: Path, out_dir: Path, style: str = "native",
          include_evidence: bool = False, version: str = "1.0", force: bool = False) -> dict:
    m = load_map(map_path)
    patterns = m.get("patterns") or []
    errors, warnings = check_patterns(patterns)
    if errors and not force:
        raise SystemExit("pattern map has errors (rmap validate); fix them or pass --force:\n  "
                         + "\n  ".join(errors))
    pats = {p["id"]: p for p in patterns}
    label = m.get("expert_label") or "the expert"
    out_dir.mkdir(parents=True, exist_ok=True)
    # remove only folders this tool generated before, never hand-made ones
    for d in out_dir.iterdir():
        if d.is_dir() and (d / GENERATED).exists():
            shutil.rmtree(d)
    ev = {}
    if include_evidence:
        import json
        side = map_path.with_name("pattern_episodes.json")
        ev = _evidence(project, json.loads(side.read_text()) if side.exists() else {})
    catalog = None
    if any(p.get("aligns_with") is not None for p in patterns):
        from .align import load_catalog
        catalog = {e["id"]: e for e in load_catalog(project)["entries"]}
    for p in patterns:
        d = out_dir / p["id"]
        d.mkdir(parents=True, exist_ok=True)
        fm = frontmatter(p, style, version)
        (d / "SKILL.md").write_text(
            "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=1000) + "---\n\n"
            + body(p, pats, label, include_evidence, ev.get(p["id"], []), catalog))
        (d / GENERATED).write_text("")
    from .mapping import slug
    name, text = router(m, pats, slug(project["skill_prefix"], 20), project["domain"], style, version)
    (out_dir / name).mkdir(exist_ok=True)
    (out_dir / name / "SKILL.md").write_text(text)
    (out_dir / name / GENERATED).write_text("")
    return {"skills": len(patterns) + 1, "router": name, "warnings": warnings}


def _evidence(project, side: dict) -> dict:
    """Redacted quotes, only from episodes whose redaction was verified clean."""
    from .store import connect
    conn = connect(project.db_path)
    ok = {r["id"] for r in conn.execute("SELECT id FROM episodes WHERE verified = 1")}
    return {pid: [e["quote"] for e in v.get("evidence", []) if e["episode"] in ok]
            for pid, v in side.items()}
