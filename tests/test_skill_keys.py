# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Generated skills carry the full orchestration and trigger set, so graph-building loaders
(for example Mentee's) see every skill and every link. Synthetic data only."""
import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

from reasoning_mapper.config import Project
from reasoning_mapper.skills import write
from reasoning_mapper.validate import check_skills_dir, read_frontmatter

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "incident-commander"
KEYS = ["name", "description", "pattern_tier", "skill_tier", "category", "tags", "when_to_apply",
        "source_skills", "orchestrates", "orchestrated_by", "works_with", "co_occurs_with",
        "cross_references", "version"]
REFS = ("source_skills", "orchestrates", "orchestrated_by", "works_with", "co_occurs_with",
        "cross_references")


def _skills(root: Path) -> dict[str, dict]:
    out = {}
    for f in sorted(root.glob("*/SKILL.md")):
        fm = read_frontmatter(f)
        if fm.get("role") != "router":
            out[fm["name"]] = fm
    return out


def _check(skills: dict[str, dict]) -> None:
    linked = set()
    for name, fm in skills.items():
        assert [k for k in KEYS if k not in fm] == [], name
        assert fm["when_to_apply"] and fm["tags"] and fm["category"], name
        for k in REFS:
            assert isinstance(fm[k], list), (name, k)
            for r in fm[k]:
                assert r in skills, f"{name}: {k} -> {r!r} is not a generated skill name"
        if fm["pattern_tier"] == 3:
            assert fm["orchestrates"] == fm["source_skills"] and fm["orchestrated_by"] == []
        else:
            assert fm["source_skills"] == fm["orchestrates"] == fm["works_with"] == []
        for k in ("source_skills", "orchestrated_by", "works_with"):
            if fm[k]:
                linked |= {name, *fm[k]}
    assert linked == set(skills), f"skills in no orchestration link: {set(skills) - linked}"


def test_example_skills_carry_every_key():
    _check(_skills(EXAMPLE / "skills"))


def _synthetic_map(tmp_path: Path) -> Path:
    """A map whose patterns have no cues, tags, co-occurrence or cross-references."""
    pats = [
        {"id": "demo-choose-depth", "tier": 3, "name": "Choose how deep to go",
         "description": "Decide how much analysis a question deserves.",
         "source_skills": ["demo-list-options", "demo-check-the-baseline"]},
        {"id": "demo-list-options", "tier": 1, "name": "List the options",
         "description": "Write down every option before judging any.",
         "orchestrated_by": ["demo-choose-depth"]},
        {"id": "demo-check-the-baseline", "tier": 2, "name": "Check the baseline",
         "description": "Compare against what normally happens.", "tags": ["baseline"],
         "orchestrated_by": ["demo-choose-depth"]},
    ]
    path = tmp_path / "map" / "patterns.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(yaml.safe_dump({"expert_label": "the analyst", "patterns": pats}))
    return path


@pytest.mark.parametrize("style", ["native", "portable"])
def test_fallbacks_fill_cues_and_tags(tmp_path, style):
    p = Project.load(EXAMPLE)
    write(p, _synthetic_map(tmp_path), tmp_path / "skills", style=style)
    errors, warnings = check_skills_dir(tmp_path / "skills")
    assert errors == []
    if style == "native":
        sk = _skills(tmp_path / "skills")
        _check(sk)
        assert sk["demo-list-options"]["when_to_apply"] == [
            "Choose how deep to go calls for it: list the options"]
        assert sk["demo-check-the-baseline"]["tags"] == ["baseline"]   # hand-written tags win
        assert "orchestration" in sk["demo-choose-depth"]["tags"]
    body = (tmp_path / "skills" / "demo-choose-depth" / "SKILL.md").read_text()
    assert "## When to apply" in body
    router = (tmp_path / "skills" / "incident-commander-reasoning" / "SKILL.md").read_text()
    assert "(no cues recorded)" not in router


MENTEE_CHECK = """
import json, sys
from pathlib import Path
from mentee.mind.map_loader import load_map
m = load_map(Path(sys.argv[1]), None)
in_edge = {x for e in m.edges for x in e}
print(json.dumps({"skills": sorted(m.skills), "unresolved": m.unresolved,
                  "no_cues": sorted(n for n, s in m.skills.items() if not s.when_to_apply),
                  "no_tags": sorted(n for n, s in m.skills.items() if not s.tags),
                  "unlinked": sorted(set(m.skills) - in_edge),
                  "router": bool(m.router), "router_cues": sorted(m.router_cues)}))
"""


@pytest.mark.skipif(not os.environ.get("MENTEE_PYTHON"),
                    reason="set MENTEE_PYTHON to a Python with Mentee installed")
@pytest.mark.parametrize("which", ["example", "synthetic"])
def test_mentee_loader_reads_everything(tmp_path, which):
    if which == "example":
        root = EXAMPLE / "skills"
    else:
        root = tmp_path / "skills"
        write(Project.load(EXAMPLE), _synthetic_map(tmp_path), root)
    out = subprocess.run([os.environ["MENTEE_PYTHON"], "-c", MENTEE_CHECK, str(root)],
                         capture_output=True, text=True, check=True).stdout
    r = json.loads(out.strip().splitlines()[-1])
    assert r["skills"] == sorted(_skills(root))
    assert r["unresolved"] == [] and r["no_cues"] == [] and r["no_tags"] == []
    assert r["unlinked"] == []
    t3 = sorted(n for n, fm in _skills(root).items() if fm["pattern_tier"] == 3)
    assert r["router"] and r["router_cues"] == t3
