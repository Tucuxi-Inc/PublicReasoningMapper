# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Structural checks on a pattern map, or on a directory of generated skills.

Errors make the orchestration graph wrong; warnings make it thin."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def check_patterns(patterns: list[dict]) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    by_id: dict[str, dict] = {}
    for p in patterns:
        pid = p.get("id")
        if not pid:
            errors.append(f"pattern {p.get('name')!r} has no id")
            continue
        if pid in by_id:
            errors.append(f"{pid}: duplicate id")
        by_id[pid] = p
        if not NAME.match(pid) or len(pid) > 64:
            errors.append(f"{pid}: id must be lower-case letters, digits and single hyphens, <= 64 chars")
        if p.get("tier") not in (1, 2, 3):
            errors.append(f"{pid}: tier must be 1, 2 or 3 (got {p.get('tier')!r})")
        if not p.get("description"):
            errors.append(f"{pid}: no description")
        if not p.get("steps"):
            warnings.append(f"{pid}: no steps")
        if not p.get("when_to_apply"):
            warnings.append(f"{pid}: no when_to_apply - the router cannot activate it")

    def refs(p, field):
        return list(p.get(field) or [])

    for pid, p in by_id.items():
        t = p.get("tier")
        for field in ("source_skills", "orchestrated_by", "works_with", "co_occurs_with",
                      "cross_references"):
            for r in refs(p, field):
                if r not in by_id:
                    errors.append(f"{pid}: {field} references unknown pattern {r!r}")
        if t in (1, 2):
            if not refs(p, "orchestrated_by"):
                errors.append(f"{pid}: tier {t} pattern has no orchestrated_by (orphaned)")
            if refs(p, "source_skills") or refs(p, "works_with"):
                errors.append(f"{pid}: only tier 3 patterns may orchestrate or have works_with")
            for r in refs(p, "orchestrated_by"):
                q = by_id.get(r)
                if q and q.get("tier") != 3:
                    errors.append(f"{pid}: orchestrated_by {r}, which is not tier 3")
                if q and pid not in refs(q, "source_skills"):
                    errors.append(f"{pid}: orchestrated_by {r}, but {r} does not list it in source_skills")
        if t == 3:
            if not refs(p, "source_skills"):
                errors.append(f"{pid}: tier 3 pattern has no source_skills (orchestrates nothing)")
            if refs(p, "orchestrated_by"):
                errors.append(f"{pid}: tier 3 patterns are not orchestrated_by anything")
            for r in refs(p, "source_skills"):
                q = by_id.get(r)
                if q and q.get("tier") == 3:
                    errors.append(f"{pid}: source_skills includes {r}, a tier 3 pattern - use works_with")
                if q and pid not in refs(q, "orchestrated_by"):
                    errors.append(f"{pid}: source_skills includes {r}, but {r} does not list it in orchestrated_by")
            for r in refs(p, "works_with"):
                q = by_id.get(r)
                if q and pid not in refs(q, "works_with"):
                    errors.append(f"{pid}: works_with {r} is not reciprocal")
    if patterns and not any(p.get("tier") == 3 for p in patterns):
        errors.append("no tier 3 pattern: nothing orchestrates the others")
    return errors, warnings


def read_frontmatter(path: Path) -> dict:
    text = path.read_text()
    if not text.startswith("---"):
        raise ValueError(f"{path}: no YAML frontmatter")
    _, fm, _ = text.split("---", 2)
    return yaml.safe_load(fm) or {}


def skill_to_pattern(fm: dict) -> dict:
    """Read either frontmatter style back into a pattern dict."""
    meta = fm.get("metadata") or {}

    def lst(v):
        if v is None:
            return []
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return list(v)

    get = (lambda k: fm.get(k, meta.get(k)))
    tier = get("pattern_tier")
    cues = get("when_to_apply")
    if isinstance(cues, str):
        cues = [x.strip() for x in cues.split(";") if x.strip()]
    return {"id": fm.get("name"), "tier": int(tier) if tier is not None else None,
            "description": fm.get("description"), "steps": ["(in body)"],
            "when_to_apply": list(cues) if cues else ["(in body)"],
            **{k: lst(get(k)) for k in ("source_skills", "orchestrated_by", "works_with",
                                         "co_occurs_with", "cross_references")},
            "_router": get("role") == "router"}


def check_skills_dir(root: Path) -> tuple[list[str], list[str]]:
    errors, warnings, pats = [], [], []
    for sk in sorted(root.glob("*/SKILL.md")):
        try:
            fm = read_frontmatter(sk)
        except Exception as e:
            errors.append(str(e))
            continue
        if fm.get("name") != sk.parent.name:
            errors.append(f"{sk.parent.name}: frontmatter name {fm.get('name')!r} must match its folder")
        d = fm.get("description") or ""
        if not d or len(d) > 1024:
            errors.append(f"{sk.parent.name}: description must be 1-1024 characters")
        p = skill_to_pattern(fm)
        if not p.pop("_router"):
            pats.append(p)
    e2, w2 = check_patterns(pats)
    return errors + e2, warnings + w2
