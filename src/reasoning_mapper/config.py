# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Project configuration: one `rmap.yaml` per expert, everything else relative to it.

A project directory looks like this once the pipeline has run:

    rmap.yaml                 this file
    rmap.db                   SQLite store (never commit it: it holds raw text)
    calibration/known.yaml    known-answer cases the instruments must pass
    review/clusters.yaml      the expert's review sheet
    map/patterns.yaml         the reviewed pattern map: tiers and orchestration
    skills/                   generated Claude skills
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CONFIG_NAME = "rmap.yaml"

DEFAULTS: dict[str, Any] = {
    "expert": {
        # Used locally to decide which text the expert wrote. Never written into
        # generated skills.
        "name": "",
        "addresses": [],
        "display_names": [],
        "sent_folders": ["sent items", "sent mail", "sent"],
    },
    "domain": "",
    # How generated skills refer to the person. Keep it a role, not a name.
    "expert_label": "the expert",
    "skill_prefix": "expert",
    "sources": [],
    "privacy": {
        # Text leaves the machine only when this is true AND the text has passed
        # redaction. See docs/PRIVACY.md.
        "allow_cloud": False,
        "extra_identifiers": [],
        "keep_terms": [],
    },
    "threading": {
        # Subjects too common to identify a conversation on their own, e.g.
        # "privileged and confidential" in a legal archive or "incident" in an
        # operations one. Lower-case.
        "generic_subjects": [],
        "max_gap_days": 45,
        "max_span_days": 365,
    },
    "episodes": {
        # Thresholds are on AUTHORED characters, never on raw body length.
        "min_message_chars": 40,
        "substantive_chars": 400,
        "curt_chars": 150,
        "max_turn_chars": 2500,
        "max_episode_chars": 18000,
        "document_chunk_chars": 6000,
    },
    "models": {
        "backend": "ollama",            # ollama | anthropic | replay
        "host": "http://127.0.0.1:11434",
        "extract_model": "",
        "annotate_model": "",
        "verify_model": "",             # should be a different model family
        "anthropic_model": "claude-sonnet-5-5",
        "num_ctx": 8192,
        # How long Ollama keeps a model resident after a call. A short value matters
        # on shared machines, where a server-wide "forever" default pins memory.
        "keep_alive": "5m",
        "timeout": 300,
        "embed_backend": "ollama",      # ollama | hashing | replay
        "embed_model": "nomic-embed-text",
        "replay_dir": "",
        "record_dir": "",               # if set, every real model response is saved here
    },
}


def _merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


@dataclass
class Project:
    root: Path
    data: dict = field(default_factory=dict)

    @classmethod
    def load(cls, root: str | Path = ".") -> "Project":
        root = Path(root).resolve()
        path = root / CONFIG_NAME
        if not path.exists():
            raise FileNotFoundError(
                f"no {CONFIG_NAME} in {root} - run `rmap init` there first")
        raw = yaml.safe_load(path.read_text()) or {}
        return cls(root=root, data=_merge(DEFAULTS, raw))

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def path(self, *parts: str) -> Path:
        return self.root.joinpath(*parts)

    @property
    def db_path(self) -> Path:
        return self.path("rmap.db")

    @property
    def expert_addresses(self) -> set[str]:
        return {a.lower() for a in self.data["expert"]["addresses"]}

    @property
    def expert_names(self) -> list[str]:
        e = self.data["expert"]
        names = list(e["display_names"])
        if e["name"]:
            names.append(e["name"])
        return [n.lower() for n in names if n]


TEMPLATE = """\
# ReasoningMapper project. Paths are relative to this file.

expert:
  # Who the expert is, so the pipeline can tell their words from everyone else's.
  # Used only on this machine; never written into generated skills.
  name: ""
  addresses: []            # every address they sent from, e.g. [me@work.com, me@old-job.com]
  display_names: []        # how mail clients showed them, e.g. ["Doe, Jane"]
  sent_folders: [sent items, sent mail, sent]

# One line naming the field, used in prompts: "commercial litigation",
# "pediatric emergency nursing", "site reliability and incident command".
domain: ""

# How generated skills refer to the person: a role, never a name.
expert_label: the expert

# Generated skills are named <prefix>-... ; the router skill is <prefix>-reasoning.
skill_prefix: expert

sources: []
#  - {type: pst,         path: archive.pst}
#  - {type: mbox,        path: mail/Takeout.mbox}
#  - {type: eml,         path: mail/eml}
#  - {type: documents,   path: docs, authored_by_expert: true}
#  - {type: transcripts, path: think_aloud}

privacy:
  allow_cloud: false       # see docs/PRIVACY.md before changing
  extra_identifiers: []    # names that must always be redacted
  keep_terms: []           # public terms that are never identifiers (statutes, standards)

threading:
  generic_subjects: []     # subjects too common to thread on, lower-case

models:
  backend: ollama          # ollama | anthropic | replay
  host: http://127.0.0.1:11434
  extract_model: ""        # e.g. a 20-30B instruct model you have pulled
  annotate_model: ""       # finds identifiers for redaction
  verify_model: ""         # audits redaction; use a DIFFERENT model family
  embed_backend: ollama
  embed_model: nomic-embed-text
"""
