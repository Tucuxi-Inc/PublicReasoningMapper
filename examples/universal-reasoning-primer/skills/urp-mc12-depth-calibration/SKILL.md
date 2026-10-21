---
name: urp-mc12-depth-calibration
description: Meta-cognitive pattern for deciding how deeply to analyze, think, or process—matching cognitive investment to situation demands and avoiding both under- and over-analysis.
pattern_tier: 3
skill_tier: strategic
source_skills:
- urp-sp2-information-gap-analysis
- urp-sp9-scenario-construction-contingency-planning
- urp-ip4-information-sufficiency-calibration
works_with:
- urp-mc16-approach-selection
- urp-mc24-confidence-calibration
tags:
- meta-cognitive
- control
- depth-of-processing
- satisficing
- analysis-calibration
confidence_level: HIGH
category: meta_cognitive
validated_by: Literature Synthesis
validated_date: '2025-12-30'
validation_type: literature_synthesis
source_type: academic_research
mentoring_priority: 9
version: '1.0'
---

# URP-MC12: Depth Calibration

**Type:** Meta-Cognitive Pattern (Tier 3)
**Function:** Matching analysis depth to situation requirements
**Domain Independence:** Universal across all decision and analysis contexts
**Orchestration Role:** Determines HOW MUCH to apply other cognitive patterns

## Pattern Definition

### Trigger Condition
Situations involving:
- Any decision or analysis requiring resource allocation
- Tension between thoroughness and efficiency
- Stakes varying across different aspects
- Time pressure competing with accuracy needs
- Uncertainty about how much analysis is "enough"

### Core Procedure

1. **Stakes Assessment**
   - What's at stake if I get this wrong?
   - Is this reversible or irreversible?
   - What are the consequences of different error types?
   - Does this decision enable or foreclose future options?

2. **Marginal Value Analysis**
   - How much would additional analysis improve the decision?
   - Am I in region of diminishing returns?
   - Is more information likely to change the answer?
   - What's the cost of additional depth?

3. **Depth Selection**
   - Quick/intuitive: trust pattern recognition, minimal explicit analysis
   - Standard: systematic consideration of main factors
   - Deep: exhaustive analysis, multiple perspectives, verification
   - Expert: everything in Deep plus adversarial testing and external review

4. **Depth Monitoring**
   - Am I analyzing at the calibrated depth?
   - Am I going deeper than warranted (over-analysis)?
   - Am I staying shallower than needed (under-analysis)?
   - Have circumstances changed warranting recalibration?

5. **Termination Decision**
   - Have I analyzed enough for this decision?
   - Would I be comfortable defending this level of analysis?
   - Is the remaining uncertainty acceptable given the stakes?

### Expert Heuristic

> "The goal isn't maximum depth—it's appropriate depth. Analyzing a lunch decision like a career decision wastes resources; analyzing a career decision like a lunch decision courts disaster. Most people under-analyze high-stakes and over-analyze low-stakes."

## Evidence from Literature

### Example 1: Satisficing vs. Maximizing
**Context:** Simon (1956) bounded rationality
**Evidence:** Optimal decisions require matching search/analysis to stakes and costs
**Insight:** "Good enough" is the goal, not "best possible"

### Example 2: Deliberation Calibration
**Context:** Gigerenzer (2007) heuristics research
**Evidence:** Simple heuristics often outperform complex analysis for certain problems
**Insight:** More analysis isn't always better; match method to problem

### Example 3: Analysis Paralysis
**Context:** Iyengar & Lepper (2000) choice overload
**Evidence:** Excessive analysis and option consideration degrades decision quality
**Insight:** Over-analysis has real costs

## Integration with Pattern Tiers

### As Orchestration Operator

URP-MC12 functions as an **analysis depth governor**:

```
INPUT: Decision/analysis task + stakes + resources
  ↓
URP-MC12: Calibrate appropriate depth
  ↓
EVALUATION:
  - Stakes (consequences of error)
  - Reversibility
  - Marginal value of more analysis
  - Resource constraints
  ↓
OUTPUT: Depth level (quick/standard/deep/expert)
  ↓
APPLY: Execute at calibrated depth
  ↓
MONITOR: Staying at appropriate depth? Recalibrate?
```

### Composition with Other MC Patterns

**Foundation Relationships:**
- **URP-MC12 orchestrates all other MC patterns**: Determines how deeply to apply each
- **URP-MC12 + URP-MC29**: Depth decision is a form of effort allocation
- **URP-MC12 + URP-MC30**: Priority informs where to invest depth
- **URP-MC12 + URP-MC7**: Load capacity constrains achievable depth

**Activation Patterns:**
- URP-MC12 gates entry into deep analysis modes
- URP-MC12 triggers termination of analysis when sufficient
- URP-MC12 prevents over-analysis spirals

## Decision Criteria

**Criterion 1: Stakes Threshold**
- IF consequences severe and irreversible, THEN deep analysis
- IF consequences minor or easily reversible, THEN quick analysis
- Rationale: Match analysis investment to outcome importance

**Criterion 2: Marginal Returns**
- IF more analysis would change decision, THEN continue
- IF decision stable regardless of more analysis, THEN stop
- Rationale: Analysis past decision change point is waste

**Criterion 3: Time Pressure**
- IF decision has deadline, THEN allocate depth within time
- IF no deadline but low stakes, THEN don't let it expand
- Rationale: Time is a real constraint; respect it

**Criterion 4: Uncertainty Tolerance**
- IF remaining uncertainty acceptable for stakes, THEN stop
- IF uncertainty too high for stakes, THEN continue analysis
- Rationale: Not all uncertainty needs resolving

## Contrast with Naive Approaches

**Naive Approach**: Analyze everything at the same depth; thoroughness is always virtue.
**Expert Approach**: Calibrate depth to stakes; efficient allocation of analysis resources.

**Naive Approach**: Deeper is always better; you can't be too careful.
**Expert Approach**: Recognize over-analysis costs; satisfice strategically.

**Naive Approach**: Rely on gut for easy things, extensive analysis for hard things.
**Expert Approach**: Rely on stakes, not difficulty, to determine depth.

**Naive Approach**: Finish analysis when it "feels complete."
**Expert Approach**: Finish analysis when additional work wouldn't change decision.

## Expertise Level Indicators

| Level | URP-MC12 Application |
|-------|------------------|
| **Novice** | Uniform depth; often over-analyzes trivia, under-analyzes important |
| **Competent** | Some stakes awareness; occasional calibration; still prone to over-analysis |
| **Expert** | Consistent calibration; efficient depth allocation; appropriate termination |
| **Master** | Immediate appropriate depth selection; rarely over- or under-analyzes |
| **Sage** | Teaches depth calibration; designs systems supporting appropriate depth |

## Theoretical Foundations

- **Bounded Rationality**: Satisficing under constraints (Simon, 1956)
- **Ecological Rationality**: Match strategy to environment (Gigerenzer, 2007)
- **Decision Quality**: Relationship between analysis and outcome quality (Huber, 1980)
- **Analysis Paralysis**: Costs of excessive deliberation (Schwartz, 2004)

---

## Metadata

```yaml
pattern_id: URP-MC12
pattern_name: Depth Calibration
tier: 3 (Meta-Cognitive)
core_question: "How deeply should I analyze this given what's at stake?"
domain_independence: Universal
transfer_rate: ">95% (calibration is fundamental to all cognition)"
extraction_confidence: 0.93
orchestration_function: analysis_depth_governance
related_patterns:
  - URP-MC29: Effort Allocation
  - URP-MC30: Strategic Priority Setting
  - URP-MC24: Confidence Calibration
```
