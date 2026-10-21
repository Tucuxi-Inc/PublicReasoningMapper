# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
from reasoning_mapper.validate import check_patterns


def pat(pid, tier, **kw):
    return {"id": pid, "tier": tier, "description": "d", "steps": ["s"], "when_to_apply": ["w"], **kw}


def good():
    return [pat("x-orch", 3, source_skills=["x-a", "x-b"], works_with=["x-orch2"]),
            pat("x-orch2", 3, source_skills=["x-a"], works_with=["x-orch"]),
            pat("x-a", 1, orchestrated_by=["x-orch", "x-orch2"]),
            pat("x-b", 2, orchestrated_by=["x-orch"])]


def test_good_map_is_clean():
    assert check_patterns(good()) == ([], [])


def test_orphan_tier1_is_an_error():
    ps = good() + [pat("x-c", 1)]
    errs, _ = check_patterns(ps)
    assert any("x-c" in e and "orphaned" in e for e in errs)


def test_one_sided_orchestration_is_an_error():
    ps = good()
    ps[3]["orchestrated_by"] = []          # x-orch still lists x-b
    errs, _ = check_patterns(ps)
    assert any("does not list it in orchestrated_by" in e for e in errs)


def test_non_reciprocal_works_with():
    ps = good()
    ps[1]["works_with"] = []
    errs, _ = check_patterns(ps)
    assert any("not reciprocal" in e for e in errs)


def test_unknown_reference_and_bad_id():
    ps = good() + [pat("Bad_ID", 2, orchestrated_by=["nope"])]
    errs, _ = check_patterns(ps)
    assert any("unknown pattern 'nope'" in e for e in errs)
    assert any("Bad_ID: id must be" in e for e in errs)


def test_tier3_cannot_orchestrate_tier3():
    ps = good()
    ps[0]["source_skills"].append("x-orch2")
    errs, _ = check_patterns(ps)
    assert any("a tier 3 pattern - use works_with" in e for e in errs)
