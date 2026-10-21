# Reasoning Catalog

Copyright (C) 2026 Tucuxi, Inc. Licensed under the Apache License, Version 2.0.

`reasoning_catalog.yaml` is a reference library of general human reasoning
approaches drawn from cognitive science, logic, mathematics, decision theory,
argumentation theory and metacognition research. It has about 150 entries
across 14 families. Every entry is general and academic. None of it is
specific to a domain, an organization or a person.

Every source was checked against a publisher page, library record, DOI or
bibliography in October 2026 (authors, year, title, venue, and fit to the
entry). Book years are first editions unless an edition is named.

## How it is used

ReasoningMapper first extracts an expert's reasoning habits from their own
material, and the expert reviews and names them. Only then does `rmap align`
compare each habit with this catalog. Embeddings shortlist candidate entries,
and a model judge decides which ones the habit actually applies: it must name
the step of the habit that performs each one. The result is recorded as
`aligns_with`, together with `beyond_general`, which says what the habit adds
beyond those general approaches.

Expect most habits to apply something general, because almost every expert
move performs some general operation. The informative part is usually
`beyond_general`: the domain conditions under which the expert uses the
approach. A habit with no match at all is rarer, and worth attention.

**The catalog is used only for post-hoc alignment. It must never appear in an
extraction prompt.** If you name candidate labels in a prompt, the model will
use those labels in its output. The extraction would then find the catalog
instead of the expert, and the "no match" signal would be lost.

## Families

| id | covers |
|----|--------|
| `logical` | conditionals, syllogisms, elimination, contradiction, case analysis |
| `mathematical` | induction, invariants, extremes, symmetry, estimation, units, margins, sensitivity |
| `inductive-abductive` | generalization, best explanation, hypothesis generation and elimination, diagnosis |
| `probabilistic` | Bayesian updating, base rates, regression, sampling, expected value, tails |
| `causal` | Mill's methods, interventions, confounders, counterfactuals, mechanisms, root causes, premortem |
| `analogical` | structure mapping, case-based reasoning, precedent, reference classes, disanalogy |
| `problem-solving` | problem definition, means-ends, decomposition, search, constraints, reframing, insight |
| `decision` | tradeoffs, dominance, satisficing, reversibility, options, staging, regret, robustness, value of information |
| `systems-temporal` | feedback, stocks and flows, delays, second-order effects, leverage, path dependence, scenarios |
| `argumentation` | Toulmin structure, charity, burden of proof, critical questions, definitions, synthesis |
| `social-strategic` | theory of mind, perspective taking, incentives, games, signaling, negotiation, trust, coalitions |
| `communication` | audience design, common ground, framing, sequencing, curse of knowledge, uncertainty language |
| `metacognitive-monitoring` | comprehension, feeling of knowing, errors, calibration, uncertainty, sources, assumptions |
| `metacognitive-control` | strategy selection and switching, effort, stopping, help-seeking, revision, debiasing, planning, reflection, transfer |

## Schema

```yaml
version: "1.0"
license: Apache-2.0
families:
  - {id, name, description}
entries:
  - id: deduction-modus-tollens     # lowercase-hyphen, unique, stable: never rename
    name: "Human-readable name"
    family: logical                  # must be a declared family id
    typical_tier: 1                  # 1 structural, 2 behavioral, 3 orchestration/meta-cognitive
    description: "1-2 plain-language sentences"
    procedure: ["3-5 short imperative steps"]
    signals: ["4-8 phrases of 2-8 words, as an expert would say or write them"]
    failure_modes: ["1-3 items"]
    sources: ["Author (Year). Title."]   # 1-3 well-known works
    related: [other-entry-ids]           # every id must exist
```

`typical_tier` is a default, not a constraint. An expert can use any approach
at a different tier.

`signals` matter most for matching. Write them as natural professional speech
("that rules it out", "what's the denominator here"), not as textbook
definitions. They are what extracted expert phrasing gets compared against.

## Contributing

1. Add a new approach only if it is distinct from every existing entry. If two
   entries would match the same expert phrase, merge or sharpen them.
2. Keep the content general. Do not include domain jargon, organization names,
   people (other than cited authors) or material from any real corpus.
3. Cite only well-established works that you have verified. If you are unsure
   of a citation, leave it out.
4. Never rename or reuse an `id`. Downstream alignments depend on them.
5. Validate before submitting. The YAML must parse, ids must be unique, every
   `related` id must exist, every family must be declared, `typical_tier` must
   be in {1, 2, 3}, all required fields must be present, and each signal must
   be 2-8 words.

## A note on citations

Sources point to well-known books and papers so readers can see where each
idea comes from. They were written from general knowledge, not checked
against the original publications. Before any academic use, check every
author, year, title and venue against the original.
