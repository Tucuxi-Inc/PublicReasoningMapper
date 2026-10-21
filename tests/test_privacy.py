# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
import pytest

from reasoning_mapper.config import Project
from reasoning_mapper.llm import LLM, CloudRefused
from reasoning_mapper.redact import Redactor, redact_episode


def project(tmp_path, **models):
    (tmp_path / "rmap.yaml").write_text("expert: {addresses: [a@example.com]}\n")
    p = Project.load(tmp_path)
    p.data["models"].update(models)
    return p


def test_cloud_refused_unless_allowed(tmp_path):
    llm = LLM(project(tmp_path, backend="anthropic"))
    with pytest.raises(CloudRefused):
        llm.complete_json("x", role="extract", task="t", key="k", redacted=True)


def test_cloud_refused_for_unverified_text(tmp_path):
    p = project(tmp_path, backend="anthropic")
    p.data["privacy"]["allow_cloud"] = True
    with pytest.raises(CloudRefused):
        LLM(p).complete_json("x", role="extract", task="t", key="k", redacted=False)


def test_redaction_roles_never_use_the_cloud(tmp_path):
    p = project(tmp_path, backend="anthropic")
    p.data["privacy"]["allow_cloud"] = True
    with pytest.raises(SystemExit, match="always run locally"):
        LLM(p).complete_json("x", role="annotate", task="t", key="k", redacted=False)


class SilentVerifier:
    """Annotator finds nothing; verifier returns nothing usable."""
    def complete_json(self, prompt, *, role, task, key, redacted, max_tokens=0):
        return (({"people": []}, "", "m") if role == "annotate" else (None, "", "m"))


def test_failed_verifier_is_not_clean():
    vocab = {"PERSON": set(), "COMPANY": set(), "PRODUCT": set(), "IDENT": set()}
    _, _, resid, verified = redact_episode(SilentVerifier(), vocab, "e", "Some text.")
    assert verified is None and resid


class Scripted:
    """Annotator returns fixed lists; verifier reports clean."""
    def __init__(self, found):
        self.found = found

    def complete_json(self, prompt, *, role, task, key, redacted, max_tokens=0):
        if role == "annotate":
            return self.found, "", "m"
        return {"residual_identifiers": [], "clean": True}, "", "m"


EMPTY = {"PERSON": set(), "COMPANY": set(), "PRODUCT": set(), "IDENT": set()}


def test_numbers_listed_as_identifiers_survive():
    # Models list years, counts and percentages as identifiers; none carry identity.
    llm = Scripted({"people": ["2011"], "other_identifiers": ["(3)", "450", "99.9 percent", "Dana"]})
    out, *_ = redact_episode(llm, EMPTY, "e", "Dana: since 2011 we hit 99.9 percent on 450 units (3) times.")
    assert "Dana" not in out
    for keep in ("2011", "99.9 percent", "450", "(3)"):
        assert keep in out


def test_keep_terms_survive_annotator_and_vocabulary():
    # The annotator lists the statute with an article; the vocabulary holds a word inside it.
    llm = Scripted({"companies": ["the Clean Air Act", "Ferrolume"]})
    vocab = dict(EMPTY, PRODUCT={"clean"})
    out, *_ = redact_episode(llm, vocab, "e", "Ferrolume says the Clean Air Act applies.",
                             keep=["Clean Air Act"])
    assert "Clean Air Act" in out and "Ferrolume" not in out


def test_vocabulary_matches_any_capitalised_form():
    vocab = dict(EMPTY, PRODUCT={"osprey", "kwillow"}, PERSON={"grant"})
    out = Redactor(vocab).floor("OSPREY and Osprey and kWillow; Grant will grant it. GRANT")
    assert "OSPREY" not in out and "Osprey" not in out and "kWillow" not in out
    assert "Grant " not in out and "GRANT" not in out
    assert "will grant it" in out          # lower case is an ordinary word
