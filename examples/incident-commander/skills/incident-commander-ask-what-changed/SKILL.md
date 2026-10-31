---
name: incident-commander-ask-what-changed
description: Begin diagnosis by asking what changed shortly before the problem appeared, and suspect that change first. Use when a sudden regression or new failure; a resource starts behaving differently; a small problem keeps recurring.
pattern_tier: 1
skill_tier: foundational
category: structural
tags:
- structural
- site-reliability-and-incident-command
- method-of-difference
- ask
- changed
when_to_apply:
- a sudden regression or new failure
- a resource starts behaving differently
- a small problem keeps recurring
source_skills: []
orchestrates: []
orchestrated_by:
- incident-commander-size-the-response-to-harm-and-reversibility
- incident-commander-stabilise-first-diagnose-second
works_with: []
co_occurs_with:
- incident-commander-size-the-response-to-harm-and-reversibility
- incident-commander-stabilise-first-diagnose-second
- incident-commander-promise-the-next-update-not-the-fix
cross_references: []
aligns_with:
- method-of-difference
version: '1.0'
---

# Ask what changed

*Tier 1 - structural pattern in how the incident commander reasons.*

## Overview

Begin diagnosis by asking what changed shortly before the problem appeared, and suspect that change first.

## When to apply

- a sudden regression or new failure
- a resource starts behaving differently
- a small problem keeps recurring

## Core procedure

1. List deploys, configuration pushes, jobs and vendor changes in the window before the problem started.
2. Suspect the most recent relevant change first.
3. For recurring events, compare what changed before each occurrence.
4. Look at what is causing the symptom, not at the symptom itself.

## Orchestrated by

- `incident-commander-size-the-response-to-harm-and-reversibility` (Size the response to harm and reversibility)
- `incident-commander-stabilise-first-diagnose-second` (Stabilise first, diagnose second)

## Quality indicators

- the change log was checked before diagnostic tools were opened
- a recurring problem was tested for a common preceding change

## Common pitfalls

- starting with deep diagnosis of the symptom while the recent change goes unexamined
- assuming a reviewed change cannot be the cause

## In the incident commander's words

Comparing what changed before each recurrence is the same habit applied across events.

## Example

Checkout latency jumps minutes after a rate-limiter configuration deploy; the incident commander asks what changed this morning before anyone opens a profiler.

## General approaches this builds on

- **Method of difference (contrast cases)** - Comparing a case where the outcome occurred with an otherwise similar case where it did not, and attributing the outcome to the factor that differs.

What the incident commander adds: The habit incorporates specific domain-specific heuristics, such as prioritizing 'recent' changes and distinguishing between 'symptoms' and 'causes' to narrow the search space in high-pressure environments.

---
*Drawn from 4 episodes of the incident commander's own work.*
