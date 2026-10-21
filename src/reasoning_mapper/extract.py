# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Open extraction: what reasoning moves did the expert make, in their own terms?

The prompt names no patterns, no dimensions and no example moves. Every one of
those was tried on the archive this method was developed against, and each one
came back as output:

* naming four candidate "dimensions" made the first of them appear on 94% of
  episodes - a label that fires on everything discriminates nothing;
* five example move names in a prompt became the five most extracted names;
* a list of known patterns to "match where one fits" anchored the output to the
  list.

So the question is open, the output fragments (nearly every name is distinct),
and clustering (cluster.py) is what makes it countable. That fragmentation is
the price of not seeding the answer, not a defect.

The extractor reads REDACTED text, and only EXPERT turns count as the expert's
reasoning: OTHER turns are the situation they were responding to.
"""

from __future__ import annotations

import collections
import json

PROMPT_VERSION = "open-v1"

INTRO = {
    "thread": """You are studying how one experienced practitioner in {domain} reasons, from a complete exchange of messages. Turns are tagged EXPERT (the person being studied) or OTHER. Identifiers are replaced with tags like [PERSON_1] and [COMPANY_A]; reason about roles and do not try to recover names.

Attribute reasoning ONLY to EXPERT turns. OTHER turns are the situation the expert faced - the ask, the pushback, the pressure. Use them to understand what the expert was responding to, never as the expert's own reasoning.""",
    "document": """You are studying how one experienced practitioner in {domain} reasons, from a passage of a document they wrote (a memo, guide, training material or analysis). Identifiers are replaced with tags like [PERSON_1] and [COMPANY_A]; reason about roles and do not try to recover names.""",
    "session": """You are studying how one experienced practitioner in {domain} reasons, from a transcript of them thinking aloud while working a problem in their field. This is the richest kind of evidence: they are saying what they notice, what they weigh and why they choose. Identifiers are replaced with tags like [PERSON_1] and [COMPANY_A]; reason about roles and do not try to recover names.""",
}

BODY = """

IF THIS CONTAINS NO PROFESSIONAL REASONING - scheduling, logistics, a file hand-off, social, or purely administrative - return exactly {{"no_reasoning": true, "why": "..."}} and nothing else. Do not invent reasoning for material that has none. This is a common and correct answer.

Otherwise capture the reasoning moves the expert actually made. Name each move in your OWN words as the expert might describe it. Do not force moves into any framework or taxonomy you know.

Return ONLY JSON:
{{"no_reasoning": false,
 "situation": "what the expert was facing, in one sentence, without identifiers",
 "decision": "what the expert decided, recommended or did, or null",
 "moves": [{{"name": "the reasoning move, 3-8 words",
            "step": "how an apprentice would perform it, one imperative sentence",
            "cue": "what in the situation prompted this move",
            "evidence": "the expert's words that show it, quoted or closely paraphrased",
            "ref": "turn number, slide or paragraph where it appears, or null"}}],
 "considerations": [{{"what": "something beyond the immediate technical question that visibly shaped the answer, in the expert's terms, 2-6 words",
                     "evidence": "the expert's words that show it"}}],
 "explained_why": true,
 "trust_state": "explaining|assumed|unclear"}}

{label}:

{body}"""

LABEL = {"thread": "EXCHANGE ({n} messages)", "document": "PASSAGE", "session": "TRANSCRIPT"}


def prompt_for(kind: str, domain: str, body: str, n_turns: int) -> str:
    return (INTRO[kind] + BODY).format(domain=domain or "their field", body=body,
                                       label=LABEL[kind].format(n=n_turns))


def run(conn, project, llm, types=None, limit: int | None = None,
        retry_errors: bool = False) -> dict:
    from .episodes import EXTRACT_BY_DEFAULT
    types = list(types or EXTRACT_BY_DEFAULT)
    rows = conn.execute(
        f"""SELECT e.id, e.kind, e.n_turns, e.redacted, e.verified FROM episodes e
            LEFT JOIN extractions x ON x.episode_id = e.id AND x.prompt_version = ?
            WHERE e.episode_type IN ({','.join('?' * len(types))})
              AND (x.episode_id IS NULL {"OR x.error IS NOT NULL" if retry_errors else ""})
            ORDER BY e.id""", (PROMPT_VERSION, *types)).fetchall()
    if limit:
        rows = rows[:limit]
    stats = collections.Counter()
    for r in rows:
        if r["redacted"] is None:
            stats["skipped: not redacted yet"] += 1
            continue
        out, err, model = None, None, None
        try:
            out, raw, model = llm.complete_json(
                prompt_for(r["kind"], project["domain"], r["redacted"], r["n_turns"] or 1),
                role="extract", task="extract", key=r["id"],
                redacted=r["verified"] == 1, max_tokens=4000)   # 1600 truncated dense real episodes
            if out is None:
                err = "unparseable" if raw else "no response"
        except Exception as e:                  # recorded per episode, never fatal
            if type(e).__name__ == "CloudRefused":
                raise
            err = f"{type(e).__name__}: {e}"
        conn.execute(
            "INSERT OR REPLACE INTO extractions (episode_id, prompt_version, model, output, error) "
            "VALUES (?,?,?,?,?)", (r["id"], PROMPT_VERSION, model,
                                   json.dumps(out) if out else None, err))
        conn.execute("DELETE FROM items WHERE episode_id=?", (r["id"],))
        if out and not out.get("no_reasoning"):
            for kind, key, field in (("move", "moves", "name"), ("consideration", "considerations", "what")):
                for it in out.get(key) or []:
                    if isinstance(it, dict) and str(it.get(field, "")).strip():
                        conn.execute("INSERT INTO items (episode_id, kind, name, detail) VALUES (?,?,?,?)",
                                     (r["id"], kind, str(it[field]).strip(), json.dumps(it)))
            stats["reasoning"] += 1
        elif out:
            stats["no reasoning"] += 1
        else:
            stats["error"] += 1
        conn.commit()
    return dict(stats)
