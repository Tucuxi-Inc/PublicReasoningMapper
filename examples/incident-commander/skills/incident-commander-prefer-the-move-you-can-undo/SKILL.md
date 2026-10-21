---
name: incident-commander-prefer-the-move-you-can-undo
description: When choosing between actions under pressure, prefer the one that can be undone quickly, and do what is needed beforehand (capturing evidence, rehearsing the rollback) so that undoing stays cheap. Use when a mitigation is available and the cause is not yet known; a tempting action cannot be reversed, such as deleting data; a launch relies on a rollback nobody has run.
pattern_tier: 1
skill_tier: foundational
orchestrated_by:
- incident-commander-size-the-response-to-harm-and-reversibility
- incident-commander-stabilise-first-diagnose-second
co_occurs_with:
- incident-commander-find-who-carries-the-cost
- incident-commander-price-the-risk-offer-a-cheaper-path
aligns_with:
- reversibility-assessment
- staged-commitment
version: '1.0'
---

# Prefer the move you can undo

*Tier 1 - structural pattern in how the incident commander reasons.*

## Overview

When choosing between actions under pressure, prefer the one that can be undone quickly, and do what is needed beforehand (capturing evidence, rehearsing the rollback) so that undoing stays cheap.

## When to apply

- a mitigation is available and the cause is not yet known
- a tempting action cannot be reversed, such as deleting data
- a launch relies on a rollback nobody has run

## Core procedure

1. For each candidate action, ask how quickly and completely it can be undone.
2. Capture the evidence you will need later before acting.
3. Take the reversible action first and watch what it tells you.
4. Treat an untested rollback as the riskiest part of a plan and rehearse it.

## Orchestrated by

- `incident-commander-size-the-response-to-harm-and-reversibility` (Size the response to harm and reversibility)
- `incident-commander-stabilise-first-diagnose-second` (Stabilise first, diagnose second)

## Quality indicators

- the first action taken could have been reversed within minutes
- evidence survived the mitigation
- the rollback had been exercised before it was needed

## Common pitfalls

- making an irreversible change when tired or rushed
- rolling back without capturing the state needed for diagnosis

## In the incident commander's words

Capturing evidence first and rehearsing the rollback are what keep the undo cheap.

## Example

Paged at night for a disk filling up, the incident commander lowers a log level or pauses a batch job - both undoable - and refuses to delete files on the primary to buy space.

## General approaches this builds on

- **Reversibility assessment** - Classifying a decision by how costly it would be to undo, and matching the deliberation and caution to that irreversibility.
- **Staged commitment** - Breaking a large commitment into sequential steps with decision points, so each later step is taken with information from earlier ones.

What the incident commander adds: The habit adds specific operational safety protocols, such as pre-emptive evidence capture and rehearsing rollbacks, to ensure that the 'undo' mechanism is technically viable before it is needed.

---
*Drawn from 4 episodes of the incident commander's own work.*
