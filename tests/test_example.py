# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""The worked example must rebuild byte-for-byte from its corpus and recordings."""
import importlib.util
import shutil
from pathlib import Path

from reasoning_mapper.skills import write
from reasoning_mapper.config import Project
from reasoning_mapper.validate import check_skills_dir

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "incident-commander"


def load_reproduce():
    spec = importlib.util.spec_from_file_location("reproduce", EXAMPLE / "reproduce.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_example_reproduces(tmp_path):
    root = tmp_path / "ex"
    shutil.copytree(EXAMPLE, root, ignore=shutil.ignore_patterns("rmap.db*", "__pycache__"))
    load_reproduce().run(root)
    for f in sorted((EXAMPLE / "skills").rglob("SKILL.md")):
        rel = f.relative_to(EXAMPLE)
        assert (root / rel).read_text() == f.read_text(), f"{rel} differs from the committed example"
    assert (root / "map" / "patterns.yaml").read_text() == (EXAMPLE / "map" / "patterns.yaml").read_text()
    for g in ("graph.html", "graph.mmd"):
        assert (root / "map" / g).read_text() == (EXAMPLE / "map" / g).read_text(), g
    errors, warnings = check_skills_dir(root / "skills")
    assert errors == [] and warnings == []


def test_portable_style_reads_back_identically(tmp_path):
    p = Project.load(EXAMPLE)
    write(p, EXAMPLE / "map" / "patterns.yaml", tmp_path / "portable", style="portable")
    errors, _ = check_skills_dir(tmp_path / "portable")
    assert errors == []
    fm = (tmp_path / "portable" / "incident-commander-ask-what-changed" / "SKILL.md").read_text()
    top = [l.split(":")[0] for l in fm.split("---")[1].splitlines() if l and not l.startswith(" ")]
    assert top == ["name", "description", "metadata"]


def test_universal_reasoning_primer_sample_validates():
    root = EXAMPLE.parent / "universal-reasoning-primer" / "skills"
    errors, warnings = check_skills_dir(root)
    assert errors == [] and len(list(root.glob("*/SKILL.md"))) == 9


def test_readme_diagram_is_the_example_map():
    readme = (EXAMPLE.parents[1] / "README.md").read_text()
    block = readme.split("```mermaid\n", 1)[1].split("```", 1)[0]
    assert block == (EXAMPLE / "map" / "graph.mmd").read_text()
