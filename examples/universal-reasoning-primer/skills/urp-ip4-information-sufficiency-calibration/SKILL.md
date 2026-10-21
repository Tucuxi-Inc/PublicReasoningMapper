---
name: urp-ip4-information-sufficiency-calibration
description: Intelligence pattern for determining appropriate levels of information sufficiency for different decision types, avoiding both analysis paralysis and premature action.
pattern_tier: 2
skill_tier: applied
orchestrated_by:
- urp-mc12-depth-calibration
- urp-mc24-confidence-calibration
cross_references:
- urp-sp2-information-gap-analysis
tags:
- intelligence
- opportunity-assessment
- information-sufficiency
- decision-readiness
- stopping-rules
confidence_level: HIGH
category: intelligence_patterns
validated_by: Literature Synthesis
validated_date: '2025-12-30'
validation_type: literature_synthesis
source_type: academic_research
mentoring_priority: 8
version: '1.0'
---

# URP-IP4: Information Sufficiency Calibration

**Type:** Intelligence Pattern (Tier 2)
**Function:** Determining when you have enough information to decide
**Domain Independence:** Universal across any decision context
**Orchestration Role:** Gates transition from information gathering to decision-making

## Pattern Definition

### Trigger Condition
- Decisions pending with incomplete information
- Risk of either over-analysis or under-analysis
- Need to determine investigation stopping point
- Trade-offs between information quality and timeliness
- Different decision types requiring different sufficiency standards

### Core Procedure

1. **Decision Characterization**: What type of decision is this? What's reversibility? What are the stakes?

2. **Sufficiency Standard Setting**: What information level does this decision type require? What's the appropriate standard?

3. **Current State Assessment**: What do we know? What's the confidence level? Where are the gaps?

4. **Marginal Value Evaluation**: Would more information change the decision? What's the value of additional information?

5. **Sufficiency Declaration**: Is current information sufficient for this decision? Proceed or gather more?

### Expert Heuristic

> "You'll never have perfect information—but you need enough to make a good decision. The right question isn't 'do I know everything?' but 'would more information change what I do?' When the answer is probably no, stop investigating and decide."

## Evidence from Literature

- **Bounded Rationality** (Simon): Satisficing with "good enough" information
- **Value of Information** (Howard): Information has calculable value
- **Satisficing** (Simon): Optimal stopping in information search
- **Decision Analysis**: Information sufficiency frameworks

## Decision Criteria

- IF additional information unlikely to change decision, THEN sufficient
- IF decision is high-stakes and irreversible, THEN higher standard
- IF decision is low-stakes or reversible, THEN lower standard acceptable
- IF time cost of gathering exceeds information value, THEN sufficient

---

## Metadata

```yaml
pattern_id: URP-IP4
pattern_name: Information Sufficiency Calibration
tier: 2 (Intelligence)
core_question: "Do I have enough information to make this decision well?"
domain_independence: Universal
transfer_rate: ">90%"
extraction_confidence: 0.89
```
