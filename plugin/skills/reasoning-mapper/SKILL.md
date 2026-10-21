---
name: reasoning-mapper
description: Guide a ReasoningMapper project, from an expert's email archive, documents and think-aloud transcripts to orchestrated Claude skills. Use when someone wants to extract their own (or a consenting expert's) reasoning approaches into skills, or asks about any rmap stage - ingest, prepare, calibrate, redact, extract, group, review, draft, link, align, validate, write-skills.
---

# Running a ReasoningMapper project

You are helping someone turn an expert's record of their own work into Claude skills that reason the way that expert does. The `rmap` command line does the heavy lifting. Your job is to:

- run the stages in order;
- read and explain each stage's output;
- stop at the two points that belong to the expert;
- never let a plausible-looking number slip through unchecked.

Background reading, if needed: `docs/METHOD.md`, `docs/SKILL_FORMAT.md`, `docs/PRIVACY.md` and `docs/THINK_ALOUD.md` in the ReasoningMapper repository.

## Before anything runs

1. **Confirm consent and rights.** The archive holds other people's words. Ask whether the user is entitled to process it: employment terms, client confidentiality, privilege and data-protection law all apply. If they are unsure, stop and say so.
2. `rmap -C <dir> init`, then fill in `rmap.yaml` with the user. The expert's addresses and display names matter most: if they are wrong, nothing is attributed to the expert. Also set `domain`, `expert_label` (a role, never a name), `sources`, `privacy.extra_identifiers`, and local models for `extract`, `annotate` and `verify`. `verify` must be a *different model family* from `annotate`.
3. Keep `privacy.allow_cloud: false` unless the user explicitly decides otherwise after reading `docs/PRIVACY.md`.

## Stages

| Stage | Run | Then check |
|---|---|---|
| ingest | `rmap ingest` | counts per source; "unreadable" counts are reported, not hidden |
| prepare | `rmap prepare` | expert-authored count is plausible (zero means the addresses are wrong); episode types include `adjustment` and `curt_decision` |
| calibrate | `rmap calibrate` | help the user write `calibration/known.yaml` from **their own** material first. Include near misses (shared words, different meaning). Every instrument they will rely on must PASS. |
| redact | `rmap redact` | `clean` vs `residual` vs `unverified`; open a few redacted episodes with the user |
| extract | `rmap extract` | error count; `rmap status` item counts |
| group | `rmap group` | writes `review/moves.yaml` |
| **review** | the expert edits `review/moves.yaml` | see below |
| draft | `rmap draft` | `map/patterns.yaml` filled from evidence |
| link | `rmap link` (on a large map, `rmap link --judge`) | the "unorchestrated" and "orchestrating nothing" lists; judged links are proposals to review |
| **orchestration** | the expert edits `map/patterns.yaml`, using `rmap visualize` (`map/graph.html`) to see it | `rmap validate` is clean |
| align | `rmap align` | which habits build on which general approaches, and what each adds |
| write | `rmap write-skills` | `rmap validate --skills skills`; read the skills with the user |

## The two decisions that belong to the expert

**Review** (`review/moves.yaml`). For each candidate habit the expert sets `decision` (keep / merge / drop), `merge_into`, `name` (their own words), `tier` and `notes`. Help them, but do not decide for them.
- Show each habit's `core` members and `evidence`, not just its label.
- Tier guidance: a habit that chooses between approaches or sizes the effort is tier 3. How they handle a kind of situation or person is tier 2. A way of analysing that they use everywhere is tier 1.
- The grouping judge errs towards splitting, so expect merges. If most habits are seen only once, check `rmap calibrate` grouping before blaming the material.

**Orchestration** (`map/patterns.yaml`). Every tier 1 and tier 2 habit needs a tier 3 parent. Co-occurrence proposes links. Where it leaves an orphan, ask the expert which tier 3 habit decides when this one is needed.

## Rules for you

- **Never put pattern names, catalog entries or example moves into an extraction prompt**, and never suggest adding them. Labels in a prompt come back as output.
- **Treat an unexpected number as a question about the instrument.** Zero, everything, or a suspiciously round share all point that way: check what the instrument actually measured before reporting the number. Calibration exists for this.
- Do not quote raw corpus text into chat beyond what the user needs to see; it is their colleagues' correspondence.
- Before the user shares generated skills, read them together for anything identifying. A distinctive situation can identify a matter even with every name removed.
