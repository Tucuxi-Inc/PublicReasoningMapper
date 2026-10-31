# Skill format

`rmap write-skills` writes one folder per pattern plus a router:

```
skills/
  <prefix>-reasoning/SKILL.md          router: start here
  <prefix>-<habit>/SKILL.md            one per pattern
```

Each folder also contains an empty `.rmap-generated` marker. On a re-run, `write-skills` deletes and rewrites only the folders that carry this marker, so skills you wrote by hand in the same directory are never touched.

## Three tiers

```
TIER 3 · ORCHESTRATION   how the expert decides what a situation needs
   │  source_skills ▼           works_with ◄► other tier 3s
TIER 2 · BEHAVIORAL      applying analysis in kinds of situation / with people
   │  orchestrated_by ▲
TIER 1 · STRUCTURAL      the core analytical moves
      orchestrated_by ▲
```

The tool ships these tiers **empty**. Which habits exist, and which tier each belongs in, are decided by the expert in review. Some rules of thumb:

- If the habit **chooses between approaches**, sizes the effort, or sequences other habits, it is tier 3.
- If it is **how they handle a kind of situation or a kind of person** (a launch, an exception request, an anxious stakeholder), it is tier 2.
- If it is **a way of analysing** that they use across situations (asking what changed, finding who carries the cost), it is tier 1.

## Frontmatter (native style, the default)

```yaml
---
name: incident-commander-size-the-response-to-harm-and-reversibility   # = folder name, lower-case-hyphen, <= 64
description: Decide how much process ... Use when deciding whether something is an incident at all; ...
pattern_tier: 3                     # 1 structural, 2 behavioral, 3 orchestration
skill_tier: strategic               # foundational (1), applied (2), strategic (3)
category: orchestration             # structural (1), behavioral (2), orchestration (3)
tags:                               # hand-written `tags` in the map, else derived (never empty)
- orchestration
- site-reliability-and-incident-command
- size
when_to_apply:                      # activation cues (never empty, see below)
- deciding whether something is an incident at all
source_skills:                      # tier 3: the tier 1/2 skills it orchestrates
- incident-commander-ask-what-changed
- incident-commander-prefer-the-move-you-can-undo
orchestrates:                       # tier 3: same list as source_skills (URP convention)
- incident-commander-ask-what-changed
- incident-commander-prefer-the-move-you-can-undo
orchestrated_by: []                 # tier 1/2: the tier 3s that activate them
works_with:                         # tier 3: peer tier 3s (must be reciprocal)
- incident-commander-stabilise-first-diagnose-second
co_occurs_with:                     # data-derived: appear in the same episodes
- incident-commander-ask-what-changed
cross_references: []                # optional, any tier, for readers
version: '1.0'
---
```

**Every key is always written.** A key is an empty list only where the tier rules forbid it, or where the map has no data:

| key | tier 1/2 | tier 3 |
|---|---|---|
| `source_skills`, `orchestrates` | always `[]` | what it orchestrates |
| `orchestrated_by` | the tier 3s that activate it | always `[]` |
| `works_with` | always `[]` | peer tier 3s |
| `co_occurs_with` | `[]` if it shares no episodes with another pattern | same |
| `cross_references` | `[]` unless written by hand in the map | same |

All references are exact skill names, so loaders that build a graph from the frontmatter resolve every one of them. **Mentee** is an example: it reads `when_to_apply`, `tags`, `category`, `orchestrated_by`, `works_with`, `source_skills` and the router's `role: router`. With the native style, every skill sits in at least one orchestration link and nothing is left unresolved.

**Fallback cues.** If a pattern has no `when_to_apply` in the map, the cues are built from its orchestrators ("*Choose how deep to go* calls for it: list the options") or, for tier 3, from its name. `rmap validate` still warns about the pattern, because recorded cues are better.

**Portable style** (`--style portable`) keeps only `name` and `description` at the top level, and puts everything else under `metadata` as comma-separated strings. Use it with loaders that accept only the core Agent Skills keys. In `metadata`, `when_to_apply` is joined with `; ` because cues can contain commas. Both styles read back identically through `rmap validate --skills`. Loaders that read top-level keys only, Mentee among them, need the native style.

## Body

```markdown
# <name>
*Tier N - <tier> pattern in how <expert_label> reasons.*
## Overview
## When to apply              -> also in frontmatter `when_to_apply` and folded into `description`
## Core procedure
## What this orchestrates     (tier 3)
## Orchestrated by            (tier 1/2)
## Quality indicators
## Common pitfalls
## In <expert_label>'s words  the expert's own note from review, verbatim
## Example                    a composite, without identifiers
## Evidence                   only with --include-evidence, and only from verified-clean episodes
```

## Rules `rmap validate` enforces

Errors:
- ids are unique, lower-case-hyphen and at most 64 characters
- `tier` is 1, 2 or 3, and every pattern has a description
- every tier 1/2 pattern has at least one `orchestrated_by`, and each of those is a tier 3 that lists it back in `source_skills`
- every tier 3 has at least one `source_skills` entry, and each is a tier 1/2 that lists it back in `orchestrated_by`
- `works_with` is reciprocal and only between tier 3s
- every reference names a pattern that exists
- there is at least one tier 3

Warnings: no `steps`, or no `when_to_apply` (the router cannot activate a pattern without cues).

## The pattern map

`map/patterns.yaml` is the source of truth, and you edit it by hand. `rmap draft` and `rmap link` only fill fields that are empty, so a re-run never overwrites what a person wrote. `link_basis` records why each proposed link was proposed (shared episodes and lift). `map/pattern_episodes.json` holds episode membership and evidence references. It stays local to the project and is not meant for hand-editing.
