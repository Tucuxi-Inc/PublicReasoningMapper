---
name: incident-commander-find-who-carries-the-cost
description: For each option, identify who would bear the cost if it goes wrong and when that cost would land, looking past the person making the request. Use when choosing between mitigating now and investigating longer; a risky launch date is proposed; someone asks for an exception to a rule that protects others.
pattern_tier: 1
skill_tier: foundational
orchestrated_by:
- incident-commander-size-the-response-to-harm-and-reversibility
co_occurs_with:
- incident-commander-prefer-the-move-you-can-undo
- incident-commander-price-the-risk-offer-a-cheaper-path
aligns_with:
- asymmetric-error-costs
version: '1.0'
---

# Find who carries the cost

*Tier 1 - structural pattern in how the incident commander reasons.*

## Overview

For each option, identify who would bear the cost if it goes wrong and when that cost would land, looking past the person making the request.

## When to apply

- choosing between mitigating now and investigating longer
- a risky launch date is proposed
- someone asks for an exception to a rule that protects others

## Core procedure

1. Name everyone who absorbs the downside of each option, including people not in the conversation.
2. Note when the cost lands - now, overnight, over a weekend.
3. Weigh costs to people who did not accept the risk more heavily than costs to the person asking.

## Orchestrated by

- `incident-commander-size-the-response-to-harm-and-reversibility` (Size the response to harm and reversibility)

## Quality indicators

- the cost to absent parties was stated explicitly
- the timing of the cost was part of the decision

## Common pitfalls

- weighing only the requester's needs
- treating an investigation as free when customers are paying for it

## Example

Asked to skip a maintenance notice for one partner, the incident commander first asks which other customers would carry the cost if the upgrade went badly.

## General approaches this builds on

- **Weighing asymmetric error costs** - Setting a decision threshold by comparing the cost of a false alarm with the cost of a miss, and leaning toward the cheaper error.

What the incident commander adds: The habit adds a specific focus on the temporal dimension of risk (when the cost lands) and the distinction between the requester and the ultimate stakeholder.

---
*Drawn from 3 episodes of the incident commander's own work.*
