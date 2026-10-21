# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Known-answer checks. Every instrument earns trust on cases whose answer is not
in doubt before its output is used.

The failure this guards against is the plausible wrong number: a measurement of
something adjacent to what you meant, which looks reasonable and so survives
review. An embedding argmax always returns a nearest neighbour; a redactor always
returns text; a quote stripper always returns a string. None of them signals that
it is wrong. A similarity matcher that compared short phrases with long prose
descriptions once scored 3/8 on phrases whose answer was obvious - while its
output on real data looked entirely sensible.

Write cases from your OWN material in calibration/known.yaml (see
`rmap init`'s template). Results are recorded, and `rmap status` shows them.
"""

from __future__ import annotations

import json

import yaml

TEMPLATE = """\
# Known-answer cases. Write them from your own material: the point is that YOU
# know the right answer. Keep this file private - it contains real text.

authored:            # quote stripping: what must survive, what must be cut
  - body: |
      Fine by me, ship it Thursday.

      On Tue, Mar 4, 2025 at 9:12 AM Someone <someone@example.com> wrote:
      > Can we ship Thursday?
    keep: ["ship it Thursday"]
    drop: ["Can we ship Thursday?"]

redaction:           # identifiers that must vanish, and facts that must survive
  - text: "Dana Whitlock at Kestrel Row said the 30-day window is fine."
    must_remove: ["Dana", "Whitlock", "Kestrel Row"]
    must_keep: ["30-day window"]

embedding:           # pairs that mean the same thing vs pairs that do not
  same:
    - ["checks who carries the downside", "asks who pays if it goes wrong"]
  different:
    # Near misses matter most: pairs that SHARE WORDS but differ in meaning.
    # Without them, an embedder that measures spelling passes this check.
    - ["checks who carries the downside", "checks who carries the release"]
    - ["checks who carries the downside", "schedules the follow-up call"]
  opposite:          # same topic, opposite stance: advisory only (see calibrate.py)
    - ["checks who carries the downside", "ignores who carries the downside"]

grouping:            # moves with their known habits; checks the `rmap group` judge
  - moves:
      - {name: "checks who carries the downside", step: "Name everyone who absorbs the cost if this fails."}
      - {name: "asks who pays if it goes wrong", step: "Ask which people bear the loss when the plan fails."}
      - {name: "checks what the change costs", step: "Estimate the build cost of the proposed change."}
      - {name: "fixes the harm before the cause", step: "Mitigate the customer impact before investigating."}
      - {name: "finds the cause before mitigating", step: "Root-cause the failure before changing anything."}
    groups:
      - ["checks who carries the downside", "asks who pays if it goes wrong"]
      - ["checks what the change costs"]
      - ["fixes the harm before the cause"]
      - ["finds the cause before mitigating"]
"""


def check_authored(cases) -> tuple[int, int, list[str]]:
    from .authored import authored
    ok, notes = 0, []
    for i, c in enumerate(cases or []):
        out = authored(c["body"])
        good = all(k in out for k in c.get("keep", [])) and not any(d in out for d in c.get("drop", []))
        ok += good
        if not good:
            notes.append(f"authored case {i}: got {out[:120]!r}")
    return ok, len(cases or []), notes


def check_redaction(cases, conn, project, llm) -> tuple[int, int, list[str]]:
    from .redact import build_vocab, redact_episode
    priv = project["privacy"]
    vocab = build_vocab(conn, priv["extra_identifiers"], priv["keep_terms"])
    use_models = llm.has_model("annotate") and llm.has_model("verify")
    ok, notes = 0, []
    for i, c in enumerate(cases or []):
        out, *_ = redact_episode(llm, vocab, f"calibration:{i}", c["text"], priv["keep_terms"], use_models)
        leaked = [x for x in c.get("must_remove", []) if x.lower() in out.lower()]
        lost = [x for x in c.get("must_keep", []) if x not in out]
        ok += not leaked and not lost
        if leaked or lost:
            notes.append(f"redaction case {i}: leaked {leaked} lost {lost}")
    return ok, len(cases or []), notes


def check_embedding(spec, embed) -> tuple[int, int, list[str]]:
    """Each paraphrase must score above every `different` pair sharing its anchor.

    `opposite` pairs (same topic, opposite stance) are advisory. Embeddings measure
    topic, not stance: on every local embedder tested while building this tool,
    "find the root cause before mitigating" sat closer to "stabilise first,
    diagnose second" than genuine paraphrases did. Clusters are therefore topic
    groups, and opposite habits can share one - which is why the review sheet
    shows each move's step and the expert, not the embedder, decides."""
    spec = spec or {}
    same, diff = spec.get("same") or [], spec.get("different") or []
    if not same or not diff:
        return 0, 0, ["embedding: need at least one `same` and one `different` pair"]
    cache: dict[tuple[str, str], float] = {}

    def sim(a, b):
        if (a, b) not in cache:
            V = embed([a, b])
            cache[(a, b)] = float(V[0] @ V[1])
        return cache[(a, b)]

    ok, notes = 0, []
    for a, b in same:
        rivals = [(x, y) for x, y in diff if a in (x, y)]
        if not rivals:
            notes.append(f"embedding: {a!r} has no `different` pair to compete with - add a near miss")
            continue
        s = sim(a, b)
        worst = max(rivals, key=lambda r: sim(*r))
        if s > sim(*worst):
            ok += 1
        else:
            other = worst[1] if worst[0] == a else worst[0]
            notes.append(f"embedding: {a!r} ~ {b!r} scored {s:.2f}, below {other!r} at {sim(*worst):.2f}")
    if not any(set(x.lower().split()) & set(y.lower().split()) for x, y in diff):
        notes.append("embedding: no `different` pair shares a word with its partner - add near "
                     "misses, or a spelling-based embedder will pass this check")
        ok = min(ok, len(same) - 1)
    for a, b in spec.get("opposite") or []:
        para = [sim(x, y) for x, y in same if a in (x, y)]
        o = sim(a, b)
        if para and o >= max(para):
            notes.append(f"advisory: opposite stance {a!r} vs {b!r} scores {o:.2f}, above its "
                         f"paraphrase ({max(para):.2f}) - expect opposite habits to share clusters")
    return ok, len(same), notes


def run(conn, project, llm, embed) -> dict:
    from .align import check_alignment
    from .group import check_grouping
    path = project.path("calibration", "known.yaml")
    if not path.exists():
        raise SystemExit(f"no {path} - `rmap init` writes a template")
    spec = yaml.safe_load(path.read_text()) or {}
    results = {}
    for inst, fn in (("authored", lambda: check_authored(spec.get("authored"))),
                     ("redaction", lambda: check_redaction(spec.get("redaction"), conn, project, llm)),
                     ("embedding", lambda: check_embedding(spec.get("embedding"), embed)),
                     ("grouping", lambda: check_grouping(spec.get("grouping"), embed, llm)),
                     ("alignment", lambda: check_alignment(spec.get("alignment"), project, llm, embed))):
        ok, n, notes = fn()
        if inst == "alignment" and n == 0:
            continue                    # optional: only needed if you use `rmap align`
        # every case must pass: these are cases whose answer is not in doubt
        passed = n > 0 and ok == n
        conn.execute("INSERT OR REPLACE INTO calibration (instrument, passed, score, total, detail) "
                     "VALUES (?,?,?,?,?)", (inst, int(passed), ok, n, json.dumps(notes)))
        results[inst] = {"passed": passed, "score": f"{ok}/{n}", "notes": notes}
    conn.commit()
    return results


def passed(conn, instrument: str) -> bool | None:
    r = conn.execute("SELECT passed FROM calibration WHERE instrument=?", (instrument,)).fetchone()
    return None if r is None else bool(r["passed"])
