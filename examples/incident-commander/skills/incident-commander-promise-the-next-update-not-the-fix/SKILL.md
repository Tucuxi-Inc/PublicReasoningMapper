---
name: incident-commander-promise-the-next-update-not-the-fix
description: During an incident, commit to when people will next hear from you rather than when the problem will be fixed, and never adopt another party's estimate as your own commitment. Use when people affected by an incident are asking when it will be fixed; a vendor or another team has given a fix estimate; someone proposes telling customers a resolution time.
pattern_tier: 2
skill_tier: applied
category: behavioral
tags:
- behavioral
- site-reliability-and-incident-command
- trust-calibration
- credible-commitment
- promise
- next
- update
- fix
when_to_apply:
- people affected by an incident are asking when it will be fixed
- a vendor or another team has given a fix estimate
- someone proposes telling customers a resolution time
source_skills: []
orchestrates: []
orchestrated_by:
- incident-commander-stabilise-first-diagnose-second
works_with: []
co_occurs_with:
- incident-commander-stabilise-first-diagnose-second
- incident-commander-ask-what-changed
cross_references: []
aligns_with:
- trust-calibration
- credible-commitment
version: '1.0'
---

# Promise the next update, not the fix

*Tier 2 - behavioral pattern in how the incident commander reasons.*

## Overview

During an incident, commit to when people will next hear from you rather than when the problem will be fixed, and never adopt another party's estimate as your own commitment.

## When to apply

- people affected by an incident are asking when it will be fixed
- a vendor or another team has given a fix estimate
- someone proposes telling customers a resolution time

## Core procedure

1. Tell affected people what is affected, what you are doing, and the time of the next update.
2. Keep that update time even if the update is 'no change'.
3. If you pass on someone else's estimate, label it as theirs and say you are not relying on it.
4. Describe any workaround you control alongside the estimate you do not.

## Orchestrated by

- `incident-commander-stabilise-first-diagnose-second` (Stabilise first, diagnose second)

## Quality indicators

- every promised update time was met
- no resolution time was given that the team did not control
- later updates were believed rather than discounted

## Common pitfalls

- relaying a vendor ETA as your own and missing it, which discounts every later update
- giving no time at all, which reads as not knowing what you are doing

## In the incident commander's words

The update time is a promise I control; the fix time is not. Never pass on someone else's estimate as ours.

## Example

A storage provider says its fix will land within the hour. Rather than telling customers it will be resolved by a specific time, the incident commander has them told that downloads are degraded, a workaround is rolling out, and the next update will come at the top of the hour whether or not it is fixed.

## General approaches this builds on

- **Trust calibration** - Adjusting how much to rely on another party based on evidence of their ability, integrity and goodwill, and on what is at stake.
- **Credible commitment and focal points** - Influencing others by making one's own future actions credible (binding oneself) and by identifying natural focal points on which parties can coordinate.

What the incident commander adds: The habit incorporates specific domain knowledge regarding the psychological impact of 'no change' updates on stakeholder anxiety during high-pressure incidents.

---
*Drawn from 3 episodes of the incident commander's own work.*
