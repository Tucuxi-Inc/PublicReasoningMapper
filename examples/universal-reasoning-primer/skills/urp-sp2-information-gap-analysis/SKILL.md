---
name: urp-sp2-information-gap-analysis
description: Strategic pattern for systematically cataloging missing critical information, assessing its impact on decision quality, and prioritizing which unknowns must be resolved versus accepted.
pattern_tier: 1
skill_tier: foundational
orchestrated_by:
- urp-mc12-depth-calibration
- urp-mc24-confidence-calibration
cross_references:
- urp-ip4-information-sufficiency-calibration
tags:
- strategic
- situation-analysis
- information-gaps
- uncertainty-management
- decision-quality
confidence_level: HIGH
category: strategic_patterns
validated_by: Literature Synthesis
validated_date: '2025-12-30'
validation_type: literature_synthesis
source_type: academic_research
mentoring_priority: 8
version: '1.0'
---

# URP-SP2: Information Gap Analysis

**Type:** Strategic Pattern (Tier 1)
**Function:** Systematic identification and prioritization of missing information
**Domain Independence:** Universal across any decision-making context
**Orchestration Role:** Enables informed decisions about what to investigate vs. accept as unknown

## Pattern Definition

### Trigger Condition
Situations involving:
- Decisions with incomplete information
- Need to prioritize investigation efforts
- Risk of analysis paralysis vs. premature action
- Resource constraints limiting information gathering
- High-stakes decisions where gaps matter

### Core Procedure

1. **Gap Identification**
   - What do I need to know to make this decision?
   - What information is missing or uncertain?
   - What assumptions am I making due to lack of data?
   - What questions can't I currently answer?

2. **Gap Categorization**
   - Is this knowable or fundamentally uncertain?
   - Is this resolvable with available resources?
   - Is this a fact gap, interpretation gap, or prediction gap?
   - What type of information would fill this gap?

3. **Impact Assessment**
   - How much would filling this gap change my decision?
   - What's the cost of being wrong about this unknown?
   - Does this gap affect the core decision or periphery?
   - Would different gap resolutions lead to different actions?

4. **Resolution Prioritization**
   - Which gaps are worth the cost to investigate?
   - Which gaps can I accept and proceed despite?
   - What's the investigation cost vs. value of resolution?
   - What's the time cost of resolution vs. decision urgency?

5. **Action Planning**
   - For priority gaps: How do I fill them?
   - For accepted gaps: How do I hedge against uncertainty?
   - For unknowable gaps: How do I make robust decisions anyway?
   - What triggers would change my gap priorities?

### Expert Heuristic

> "You'll never have complete information—but you need to know what you don't know. The key question isn't 'do I have enough information?' but 'would more information change what I do?' If not, stop investigating and act."

## Evidence from Literature

### Example 1: Bounded Rationality
**Context:** Simon (1956) decision-making research
**Evidence:** Decisions are always made with incomplete information; the question is how to decide well under information constraints
**Insight:** Information gap analysis is inherent to rational decision-making

### Example 2: Value of Information
**Context:** Decision analysis (Howard, 1966)
**Evidence:** Information has calculable value based on how it changes decisions; some information isn't worth acquiring
**Insight:** Gap prioritization has theoretical foundation in decision theory

### Example 3: Intelligence Analysis
**Context:** Heuer (1999) psychology of intelligence analysis
**Evidence:** Analysts must distinguish what they know from what they assume; gap identification prevents false confidence
**Insight:** Explicit gap tracking is professional intelligence practice

### Example 4: Satisficing
**Context:** Simon's bounded rationality framework
**Evidence:** "Good enough" information is often optimal given investigation costs
**Insight:** Not all gaps need filling; some should be accepted

## Decision Criteria

**Criterion 1: Decision Relevance**
- IF gap resolution would change decision, THEN high priority to resolve
- IF decision is same regardless of resolution, THEN low priority
- Rationale: Focus on decision-relevant gaps

**Criterion 2: Cost-Benefit of Resolution**
- IF resolution cost < expected value of better decision, THEN investigate
- IF resolution cost > expected value, THEN accept gap
- Rationale: Information acquisition should be economically rational

**Criterion 3: Resolvability**
- IF gap is practically resolvable, THEN consider investigation
- IF gap is fundamentally unknowable, THEN focus on robustness
- Rationale: Don't waste resources on unresolvable gaps

**Criterion 4: Time Constraints**
- IF decision deadline is near, THEN accept more gaps
- IF time permits investigation, THEN resolve high-value gaps
- Rationale: Time pressure changes optimal gap tolerance

## Contrast with Naive Approaches

**Naive Approach**: Gather all available information before deciding.
**Expert Approach**: Identify which gaps matter and focus investigation there.

**Naive Approach**: Assume current information is sufficient.
**Expert Approach**: Explicitly identify gaps and assess their impact.

**Naive Approach**: Treat all unknowns as equally important.
**Expert Approach**: Prioritize gaps by decision impact and resolution cost.

**Naive Approach**: Either investigate everything or accept all gaps.
**Expert Approach**: Strategic mix of investigation and accepted uncertainty.

## Integration with Pattern Tiers

### As Foundation for Investigation

URP-SP2 guides where to invest investigation effort:

```
URP-SP2: Information Gap Analysis
  ↓ identifies gaps requiring
URP-SP13: Risk-Prioritized Investigation (what to investigate)
URP-IP4: Information Sufficiency Calibration (when to stop)
URP-IP12: Multi-Source Data Reconciliation (how to fill gaps)
  ↓ informs
URP-MC39: Uncertainty Tracking (what remains uncertain)
URP-MC32: Satisficing Decision (when good enough is enough)
```

### Orchestration Relationships

**Orchestrated By (MC Patterns):**
- **URP-MC39 → URP-SP2**: Uncertainty tracking identifies areas needing gap analysis
- **URP-MC40 → URP-SP2**: Knowledge boundary awareness reveals knowledge gaps
- **URP-MC2 → URP-SP2**: Comprehension monitoring detects understanding gaps

**Orchestrates (IP Patterns):**
- **URP-SP2 → URP-IP4**: Gap analysis informs information sufficiency standards
- **URP-SP2 → URP-IP12**: Priority gaps guide data reconciliation efforts
- **URP-SP2 → URP-SP13**: Gap priorities drive investigation focus

## Expertise Level Indicators

| Level | URP-SP2 Application |
|-------|-----------------|
| **Novice** | Doesn't identify gaps; assumes information is sufficient; or investigates everything |
| **Competent** | Identifies obvious gaps; some prioritization; may over- or under-investigate |
| **Expert** | Systematic gap identification; decision-relevant prioritization; efficient investigation |
| **Master** | Intuitive gap sensing; accurate impact assessment; optimal investigation/acceptance balance |
| **Sage** | Designs information systems; teaches gap analysis; creates organizational practices |

## Theoretical Foundations

- **Bounded Rationality**: Decision-making under information constraints (Simon, 1956)
- **Value of Information**: Economic framework for information acquisition (Howard, 1966)
- **Intelligence Analysis**: Distinguishing knowledge from assumption (Heuer, 1999)
- **Satisficing**: Optimal stopping in information search (Simon, 1956)
- **Decision Analysis**: Structuring decisions under uncertainty (Raiffa, 1968)

---

## Metadata

```yaml
pattern_id: URP-SP2
pattern_name: Information Gap Analysis
tier: 1 (Strategic)
core_question: "What don't I know, how much does it matter, and what should I do about it?"
domain_independence: Universal
transfer_rate: ">95% (applies to all decisions under uncertainty)"
extraction_confidence: 0.91
orchestration_function: investigation_prioritization
related_patterns:
  - URP-SP13: Risk-Prioritized Investigation
  - URP-IP4: Information Sufficiency Calibration
  - URP-MC39: Uncertainty Tracking
```
