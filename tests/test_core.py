# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
import json
import re

import pytest

from reasoning_mapper.authored import authored
from reasoning_mapper.episodes import classify, session_problems
from reasoning_mapper.redact import Redactor


def test_authored_cuts_quote_and_signature():
    body = ("Ship it Thursday.\n\nThanks,\nAlex\n\n"
            "On Tue, Mar 4, 2025 at 9:12 AM Someone <s@example.com> wrote:\n> Can we ship?")
    assert authored(body) == "Ship it Thursday."


def test_authored_keeps_a_message_that_is_only_thanks():
    assert authored("Thanks, will do.") == "Thanks, will do."


def test_authored_wrapped_gmail_marker():
    body = "Yes.\n\nOn Tue, Mar 4, 2025 at 9:12 AM A Very Long Name <\nlong.name@example.com> wrote:\n> q"
    assert authored(body) == "Yes."


@pytest.mark.parametrize("turns,want", [
    ([(False, 100), (True, 50), (False, 120), (True, 600)], "adjustment"),
    ([(False, 100), (True, 600)], "substantive_reply"),
    ([(False, 300), (True, 30)], "curt_decision"),
    ([(True, 30), (True, 40)], "expert_only"),
    ([(False, 30), (False, 40)], "no_expert"),
])
def test_classify(turns, want):
    assert classify(turns, substantive=400, curt=150) == want


def test_session_split_drops_short_preamble():
    t = "# Session\n\nintro\n\n## Problem 1: a\n\nthink a\n\n## Problem 2: b\n\nthink b"
    parts = session_problems(t)
    assert len(parts) == 2 and parts[0].startswith("## Problem 1")


def test_redactor_aliases_are_stable_and_numbers_survive():
    r = Redactor({"PERSON": {"jordan"}, "COMPANY": set(), "PRODUCT": set(), "IDENT": {"acme widgets"}})
    a = r.floor("Jordan says Acme Widgets will pay $40,000 within 30 days.")
    b = r.floor("acme widgets agreed; Jordan confirmed.")
    assert "Jordan" not in a and "Acme" not in a and "$40,000" in a and "30 days" in a
    assert a.startswith("[PERSON_1] says [IDENT_1]")
    assert b == "[IDENT_1] agreed; [PERSON_1] confirmed."
    assert r.legend()["[PERSON_1]"] == "jordan"


def test_lowercase_ordinary_word_is_not_a_name():
    r = Redactor({"PERSON": {"grant"}, "COMPANY": set(), "PRODUCT": set(), "IDENT": set()})
    assert r.floor("we grant the licence; Grant agreed") == "we grant the licence; [PERSON_1] agreed"


def _map(tmp_path, pats, eps):
    from reasoning_mapper.mapping import save_map
    path = tmp_path / "map" / "patterns.yaml"; path.parent.mkdir()
    save_map({"expert_label": "expert", "patterns": pats}, path)
    (path.with_name("pattern_episodes.json")).write_text(json.dumps({k: {"episodes": v} for k, v in eps.items()}))
    return path


class Picks:
    """Judge that names a fixed orchestrator (by name) for each habit, or none."""
    def __init__(self, picks):
        self.picks, self.asked = picks, []

    def complete_json(self, prompt, *, role, task, key, redacted, max_tokens=0):
        self.asked.append(key)
        want = self.picks.get(key)
        names = [l.split(". ", 1)[1].split(":")[0] for l in prompt.splitlines() if re.match(r"\s+\d+\. ", l)]
        return {"orchestrator": names.index(want) + 1 if want in names else None, "why": "w"}, "", "m"


def test_link_judges_orchestrators_only_for_orphans(tmp_path):
    from reasoning_mapper.mapping import link, load_map
    P = lambda i, t, n: {"id": i, "tier": t, "name": n, "description": n}
    pats = [P("a", 1, "Linked"), P("b", 1, "Orphan"), P("c", 2, "Unclaimed"),
            P("o1", 3, "Gate"), P("o2", 3, "Budget")]
    eps = {"a": ["e1", "e2"], "o1": ["e1", "e2"], "b": ["e3"], "c": ["e4"], "o2": ["e5"], "x": ["e6", "e7"]}
    path = _map(tmp_path, pats, eps)
    judge = Picks({"b": "Budget"})          # c gets null: stays orphaned
    r = link(path, 2, judge)
    m = {p["id"]: p for p in load_map(path)["patterns"]}
    assert judge.asked == ["b", "c"]        # co-occurrence already linked a
    assert m["a"]["orchestrated_by"] == ["o1"]
    assert m["b"]["orchestrated_by"] == ["o2"] and "b" in m["o2"]["source_skills"]
    assert m["b"]["link_basis"]["o2"] == {"judged": "w"}
    assert r["orchestrators judged"] == 1 and r["unorchestrated"] == ["c"]
    assert r["orchestrating nothing"] == []


def test_link_without_judge_is_unchanged(tmp_path):
    from reasoning_mapper.mapping import link
    P = lambda i, t, n: {"id": i, "tier": t, "name": n, "description": n}
    path = _map(tmp_path, [P("b", 1, "Orphan"), P("o2", 3, "Budget")], {"b": ["e1"], "o2": ["e2"], "z": ["e3"]})
    r = link(path, 2)
    assert "orchestrators judged" not in r and r["unorchestrated"] == ["b"] and r["orchestrating nothing"] == ["o2"]


def test_graph_data_edges_and_flags():
    from reasoning_mapper.visualize import graph_data, render
    P = lambda i, t, **k: {"id": i, "tier": t, "name": i.upper(), **k}
    m = {"patterns": [
        P("o", 3, source_skills=["a"], works_with=["q"], link_basis={"a": {"judged": "fits"}}),
        P("q", 3, works_with=["o"]),
        P("a", 1, orchestrated_by=["o"], co_occurs_with=["o", "b"]),
        P("b", 2, name="</script><b>x"),
    ]}
    g = graph_data(m)
    kinds = sorted((l["kind"], l["source"], l["target"], l["judged"]) for l in g["links"])
    assert kinds == [("co_occurs", "a", "b", False), ("orchestrates", "o", "a", True), ("works_with", "o", "q", False)]
    flags = {n["id"]: n["orphan"] for n in g["nodes"]}
    assert flags == {"o": False, "q": True, "a": False, "b": True}
    page = render(m)
    assert "</script><b>" not in page and render(m) == page   # escaped, deterministic
