---
name: urp-sp9-scenario-construction-contingency-planning
description: Strategic pattern for systematically building plausible future scenarios based on key uncertainties and developing adaptive response strategies for each.
pattern_tier: 1
skill_tier: foundational
orchestrated_by:
- urp-mc12-depth-calibration
- urp-mc16-approach-selection
cross_references:
- urp-ip9-creative-option-generation
tags:
- strategic
- strategic-design
- scenario-planning
- contingency
- uncertainty-management
confidence_level: HIGH
category: strategic_patterns
validated_by: Literature Synthesis
validated_date: '2025-12-30'
validation_type: literature_synthesis
source_type: academic_research
mentoring_priority: 8
version: '1.0'
---

# URP-SP9: Scenario Construction and Contingency Planning

**Type:** Strategic Pattern (Tier 1)
**Function:** Building future scenarios and adaptive response strategies
**Domain Independence:** Universal across any uncertain environment
**Orchestration Role:** Prepares for multiple futures rather than betting on one prediction

## Pattern Definition

### Trigger Condition
Situations involving:
- Significant uncertainty about how situation will evolve
- High-stakes decisions requiring robustness to different futures
- Need to prepare for multiple possible outcomes
- Long time horizons where prediction is unreliable
- Complex environments with many variables

### Core Procedure

1. **Uncertainty Identification**
   - What key factors are uncertain?
   - Which uncertainties most affect outcomes?
   - What are the critical branching points?
   - Which uncertainties are independent vs. correlated?

2. **Scenario Construction**
   - What are the plausible combinations of uncertainty resolutions?
   - What distinct future states are possible?
   - What makes each scenario internally consistent?
   - What would each scenario look like concretely?

3. **Scenario Analysis**
   - What are the implications of each scenario?
   - What opportunities and threats does each present?
   - How does our position change across scenarios?
   - What early signals would indicate which scenario is emerging?

4. **Strategy Development per Scenario**
   - What's the optimal approach in each scenario?
   - What's robust across scenarios?
   - What's scenario-specific?
   - Where do strategies conflict across scenarios?

5. **Contingency Preparation**
   - What triggers activate which contingency?
   - What advance preparation enables rapid response?
   - How do I preserve optionality until clarity emerges?
   - What monitoring tracks scenario emergence?

### Expert Heuristic

> "The future is not predictable, but it is preparable. Don't try to predict which scenario will occur—prepare for the range of plausible scenarios, and watch for signals that reveal which is emerging."

## Evidence from Literature

### Example 1: Shell Scenario Planning
**Context:** Royal Dutch Shell strategic planning
**Evidence:** Scenario planning helped Shell navigate oil shocks by preparing for multiple futures
**Insight:** Scenario planning outperforms single-point prediction in volatile environments

### Example 2: Robust Decision Making
**Context:** RAND Corporation decision frameworks
**Evidence:** Strategies should be evaluated across scenarios, not just expected-case
**Insight:** Robustness across scenarios is valuable

### Example 3: Real Options
**Context:** Financial strategy research
**Evidence:** Preserving options has value under uncertainty; scenario planning identifies option value
**Insight:** Scenarios inform option valuation

### Example 4: Early Warning Systems
**Context:** Strategic foresight research
**Evidence:** Identifying scenario-specific signals enables earlier response
**Insight:** Scenarios enable proactive monitoring

## Decision Criteria

**Criterion 1: Scenario Completeness**
- IF major plausible futures covered, THEN adequate
- IF important scenarios missing, THEN expand
- Rationale: Preparation requires scenario coverage

**Criterion 2: Strategy Robustness**
- IF strategy works across scenarios, THEN more robust
- IF strategy optimal for one but fails in others, THEN risky
- Rationale: Value robustness over optimization

**Criterion 3: Contingency Readiness**
- IF triggers defined and responses prepared, THEN ready
- IF contingencies exist but aren't prepared, THEN false security
- Rationale: Contingencies must be actionable

**Criterion 4: Monitoring Implementation**
- IF watching for scenario signals, THEN can respond early
- IF not monitoring, THEN will be surprised
- Rationale: Early signal detection enables proactive response

## Contrast with Naive Approaches

**Naive Approach**: Predict most likely future; plan for that.
**Expert Approach**: Identify range of plausible futures; prepare for multiple.

**Naive Approach**: Optimize for expected case.
**Expert Approach**: Balance optimization and robustness across scenarios.

**Naive Approach**: Create contingencies but don't prepare them.
**Expert Approach**: Pre-position resources and pre-design responses.

**Naive Approach**: React when future clarifies.
**Expert Approach**: Watch for signals; respond as scenario emerges.

## Integration with Pattern Tiers

### As Planning Foundation

URP-SP9 enables robust strategy under uncertainty:

```
URP-SP9: Scenario Construction and Contingency Planning
  ↓ provides scenarios for
URP-SP5: Multi-Dimensional Risk Assessment (risk per scenario)
URP-SP10: Adaptive Strategy Design (strategy flexibility across scenarios)
URP-IP9: Creative Option Generation (options per scenario)
URP-IP21: Crisis Resource Triage (prepared responses)
  ↓ enables
URP-MC18: Contingency Planning (specific contingencies)
```

### Orchestration Relationships

**Orchestrated By (MC Patterns):**
- **URP-MC18 → URP-SP9**: Contingency planning uses scenario framework
- **URP-MC39 → URP-SP9**: Uncertainty tracking identifies scenario dimensions
- **URP-MC43 → URP-SP9**: Belief revision as scenario signals emerge

**Orchestrates (IP Patterns):**
- **URP-SP9 → URP-IP9**: Scenarios frame creative option generation
- **URP-SP9 → URP-IP21**: Pre-builds crisis response options
- **URP-SP9 → URP-IP23**: Frames recovery coordination options

## Expertise Level Indicators

| Level | URP-SP9 Application |
|-------|-----------------|
| **Novice** | Single-future assumption; no scenario thinking; surprised by changes |
| **Competent** | Recognizes uncertainty; basic scenarios; limited contingencies |
| **Expert** | Systematic scenario construction; robust strategies; prepared contingencies |
| **Master** | Intuitive scenario sensing; elegant multi-scenario strategies; early signal detection |
| **Sage** | Designs scenario processes; teaches futures thinking; builds organizational foresight |

## Theoretical Foundations

- **Scenario Planning**: Multiple futures approach (Schwartz, 1991; Shell)
- **Robust Decision Making**: Performance across scenarios (Lempert et al., 2003)
- **Real Options**: Option value under uncertainty (Dixit & Pindyck, 1994)
- **Strategic Foresight**: Systematic futures preparation
- **Early Warning Systems**: Signal detection for emerging scenarios

---

## Metadata

```yaml
pattern_id: URP-SP9
pattern_name: Scenario Construction and Contingency Planning
tier: 1 (Strategic)
core_question: "What futures are plausible, and how do I prepare for multiple of them?"
domain_independence: Universal
transfer_rate: ">90% (scenario thinking applies everywhere)"
extraction_confidence: 0.91
orchestration_function: futures_preparation
related_patterns:
  - URP-SP5: Multi-Dimensional Risk Assessment
  - URP-SP10: Adaptive Strategy Design
  - URP-MC18: Contingency Planning
```
