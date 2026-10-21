---
name: incident-commander-reasoning
description: 'How the incident commander approaches problems in site reliability and incident command. Start here for any situation in that field: it says which reasoning patterns to activate and in what order.'
role: router
version: '1.0'
---

# Reasoning like the incident commander

This skill set encodes how the incident commander reasons about problems in site reliability and incident command, drawn from their own correspondence, documents and think-aloud sessions. It has three tiers:

- **Tier 3 - orchestration**: how they decide what a situation needs. Start here.
- **Tier 2 - behavioral**: how they apply analysis in particular kinds of situation.
- **Tier 1 - structural**: the core analytical moves.

## Procedure

1. Read the situation. Before analysing, check it against the activation cues below and note every tier 3 pattern that matches.
2. Open each matching tier 3 skill. It names the tier 1 and 2 skills it orchestrates; use the ones the situation actually calls for.
3. Work the problem with those skills, in the order the orchestrating pattern suggests.
4. Say plainly where the situation falls outside what these patterns cover. They describe how the incident commander has reasoned, not every case; do not stretch a pattern to fit.

## Activation cues (tier 3)

- `incident-commander-size-the-response-to-harm-and-reversibility` - **Size the response to harm and reversibility**: deciding whether something is an incident at all; deciding how many people to page; deciding how large a post-incident review should be; a small event has happened before
- `incident-commander-stabilise-first-diagnose-second` - **Stabilise first, diagnose second**: customers are failing now and an engineer wants to investigate live; a cheap mitigation exists before the cause is known

## Orchestration map

- `incident-commander-size-the-response-to-harm-and-reversibility` orchestrates: `incident-commander-ask-what-changed`, `incident-commander-prefer-the-move-you-can-undo`, `incident-commander-find-who-carries-the-cost`, `incident-commander-price-the-risk-offer-a-cheaper-path`
- `incident-commander-stabilise-first-diagnose-second` orchestrates: `incident-commander-promise-the-next-update-not-the-fix`, `incident-commander-ask-what-changed`, `incident-commander-prefer-the-move-you-can-undo`

## All patterns

| Skill | Tier | Pattern |
|---|---|---|
| `incident-commander-size-the-response-to-harm-and-reversibility` | 3 | Size the response to harm and reversibility |
| `incident-commander-stabilise-first-diagnose-second` | 3 | Stabilise first, diagnose second |
| `incident-commander-price-the-risk-offer-a-cheaper-path` | 2 | Price the risk, offer a cheaper path |
| `incident-commander-promise-the-next-update-not-the-fix` | 2 | Promise the next update, not the fix |
| `incident-commander-ask-what-changed` | 1 | Ask what changed |
| `incident-commander-find-who-carries-the-cost` | 1 | Find who carries the cost |
| `incident-commander-prefer-the-move-you-can-undo` | 1 | Prefer the move you can undo |
