---
name: incident-commander-stabilise-first-diagnose-second
description: While people are being harmed, stop the harm before finding the cause; schedule diagnosis for afterwards, using evidence captured before mitigating. Use when customers are failing now and an engineer wants to investigate live; a cheap mitigation exists before the cause is known.
pattern_tier: 3
skill_tier: strategic
category: orchestration
tags:
- orchestration
- site-reliability-and-incident-command
- interventionist-reasoning
- stabilise
- diagnose
when_to_apply:
- customers are failing now and an engineer wants to investigate live
- a cheap mitigation exists before the cause is known
source_skills:
- incident-commander-promise-the-next-update-not-the-fix
- incident-commander-ask-what-changed
- incident-commander-prefer-the-move-you-can-undo
orchestrates:
- incident-commander-promise-the-next-update-not-the-fix
- incident-commander-ask-what-changed
- incident-commander-prefer-the-move-you-can-undo
orchestrated_by: []
works_with:
- incident-commander-size-the-response-to-harm-and-reversibility
co_occurs_with:
- incident-commander-promise-the-next-update-not-the-fix
- incident-commander-ask-what-changed
cross_references: []
aligns_with:
- interventionist-reasoning
version: '1.0'
---

# Stabilise first, diagnose second

*Tier 3 - orchestration pattern in how the incident commander reasons.*

## Overview

While people are being harmed, stop the harm before finding the cause; schedule diagnosis for afterwards, using evidence captured before mitigating.

## When to apply

- customers are failing now and an engineer wants to investigate live
- a cheap mitigation exists before the cause is known

## Core procedure

1. Capture the evidence diagnosis will need.
2. Apply the cheapest mitigation that stops the harm.
3. Read what the mitigation's result tells you about the cause.
4. Schedule the real analysis for when no one is being hurt.

## What this orchestrates

When this pattern is active, decide which of these the situation needs and apply them in that light:

- `incident-commander-promise-the-next-update-not-the-fix` (Promise the next update, not the fix)
- `incident-commander-ask-what-changed` (Ask what changed)
- `incident-commander-prefer-the-move-you-can-undo` (Prefer the move you can undo)

Often active alongside: `incident-commander-size-the-response-to-harm-and-reversibility` (Size the response to harm and reversibility).

## Quality indicators

- time to mitigation was short
- root cause was still found afterwards from the captured evidence

## Common pitfalls

- investigating live while customers absorb the cost
- mitigating in a way that destroys the evidence

## Example

With enterprise customers' work failing, the incident commander has a heap dump and metrics captured, rolls back the morning's change, and leaves root cause for the next day's review.

## General approaches this builds on

- **Interventionist causal reasoning** - Understanding a cause as something that, if deliberately changed while holding other things fixed, would change the outcome; and reasoning about what an intervention would do.

What the incident commander adds: The habit prioritizes the temporal separation of mitigation and diagnosis to manage immediate risk, a domain-specific heuristic for high-stakes environments.

---
*Drawn from 2 episodes of the incident commander's own work.*
