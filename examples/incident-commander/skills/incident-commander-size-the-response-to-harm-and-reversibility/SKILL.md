---
name: incident-commander-size-the-response-to-harm-and-reversibility
description: Decide how much process, escalation and review a situation deserves from how many people are being hurt and whether the harm can be undone - and look harder whenever a small problem recurs. Use when deciding whether something is an incident at all; deciding how many people to page; deciding how large a post-incident review should be; a small event has happened before.
pattern_tier: 3
skill_tier: strategic
category: orchestration
tags:
- orchestration
- site-reliability-and-incident-command
- reversibility-assessment
- size
- response
- harm
- reversibility
when_to_apply:
- deciding whether something is an incident at all
- deciding how many people to page
- deciding how large a post-incident review should be
- a small event has happened before
source_skills:
- incident-commander-ask-what-changed
- incident-commander-prefer-the-move-you-can-undo
- incident-commander-find-who-carries-the-cost
- incident-commander-price-the-risk-offer-a-cheaper-path
orchestrates:
- incident-commander-ask-what-changed
- incident-commander-prefer-the-move-you-can-undo
- incident-commander-find-who-carries-the-cost
- incident-commander-price-the-risk-offer-a-cheaper-path
orchestrated_by: []
works_with:
- incident-commander-stabilise-first-diagnose-second
co_occurs_with:
- incident-commander-ask-what-changed
cross_references: []
aligns_with:
- reversibility-assessment
version: '1.0'
---

# Size the response to harm and reversibility

*Tier 3 - orchestration pattern in how the incident commander reasons.*

## Overview

Decide how much process, escalation and review a situation deserves from how many people are being hurt and whether the harm can be undone - and look harder whenever a small problem recurs.

## When to apply

- deciding whether something is an incident at all
- deciding how many people to page
- deciding how large a post-incident review should be
- a small event has happened before

## Core procedure

1. Estimate the blast radius: who is hurt now, and how many.
2. Ask whether the harm can be undone; treat irreversible harm as large regardless of reach.
3. Estimate how much time you have before the harm grows.
4. Choose the smallest process that fits: ticket, short review, or full incident process.
5. Escalate a small, repeated event: three occurrences are a pattern.

## What this orchestrates

When this pattern is active, decide which of these the situation needs and apply them in that light:

- `incident-commander-ask-what-changed` (Ask what changed)
- `incident-commander-prefer-the-move-you-can-undo` (Prefer the move you can undo)
- `incident-commander-find-who-carries-the-cost` (Find who carries the cost)
- `incident-commander-price-the-risk-offer-a-cheaper-path` (Price the risk, offer a cheaper path)

Often active alongside: `incident-commander-stabilise-first-diagnose-second` (Stabilise first, diagnose second).

## Quality indicators

- the effort spent was proportionate to the harm
- irreversible harm always got the full process
- recurring small events were investigated

## Common pitfalls

- running the full process for everything, which costs more than the incidents
- dismissing each recurrence as small on its own

## In the incident commander's words

Repetition overrides size: three small events are a pattern and get a proper look. Knowing how much time you have is part of the sizing.

## Example

A three-minute authentication blip gets a half-page review instead of a full postmortem - but because it is the third since spring, the half page must answer what changed before each one.

## General approaches this builds on

- **Reversibility assessment** - Classifying a decision by how costly it would be to undo, and matching the deliberation and caution to that irreversibility.

What the incident commander adds: The habit incorporates specific domain-specific heuristics for incident management, such as identifying patterns in recurring small events and calculating the 'blast radius' to determine the appropriate level of organizational process.

---
*Drawn from 3 episodes of the incident commander's own work.*
