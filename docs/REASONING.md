# Reasoning: what the literature names, and where it starts

ReasoningMapper extracts *one person's* reasoning. This document places that work in two contexts.

1. **The established map.** These are the kinds of reasoning that logic, mathematics, cognitive science and decision research have named and studied. They make up the catalog in [`catalog/`](../catalog).
2. **A working theory.** This is Tucuxi's hypothesis about what sits underneath all of them: that reasoning begins with, and is continuously governed by, a single operation, *whether*.

The first part is textbook. The second part is a hypothesis, and the evidence for each piece is marked as you go.

---

## Part 1 · The established map

Each family below is a group of entries in the catalog, with the works it is usually traced to.

**Logical and deductive.** These are conclusions that follow necessarily from premises: modus ponens and modus tollens, syllogisms, disjunctive elimination, case analysis, proof by contradiction, and necessary-versus-sufficient conditions. People mostly reason deductively by building and searching *mental models* of what the premises allow, rather than by applying formal rules (Johnson-Laird).

**Mathematical and quantitative.** These are the heuristics of problem solving that Pólya made explicit (*How to Solve It*, 1945): work backwards, specialise to a simpler case, look at the extremes, exploit symmetry, find what stays invariant. To them add estimation and the habits of quantitative sense-making: order of magnitude, units, rates and margins.

**Inductive and abductive.** Induction runs from cases to generalisations. Abduction runs from a surprising observation to the hypothesis that would explain it, which is Peirce's third mode of inference and Lipton's *inference to the best explanation*. Differential diagnosis, which generates rival hypotheses and eliminates them, is abduction run as a discipline.

**Probabilistic and statistical.** This family covers Bayesian updating, base rates, regression to the mean, sample size and selection, expected value, and attention to the tails. The heuristics-and-biases programme (Tversky & Kahneman) is largely a map of where intuition departs from these norms.

**Causal and counterfactual.** Mill's methods of agreement and difference come first. Pearl's ladder then separates association, intervention ("what if I do X?") and counterfactuals ("what if X had not happened?"). Practitioners add mechanism tracing, root-cause analysis and the premortem.

**Analogical and case-based.** Structure mapping carries relations, not surface features, from a known case to a new one (Gentner). Case-based reasoning retrieves and adapts prior cases (Kolodner). Precedent and reference-class forecasting are disciplined forms of the same move.

**Problem solving and search.** Newell & Simon (1972) framed problem solving as search through a problem space. Its methods include means-ends analysis, subgoals, decomposition, generate-and-test, and constraint satisfaction, plus *representation change*: reframing the problem so the search becomes easy.

**Decision-making.** Decisions have to cope with multiple objectives, uncertainty and limited means. Simon's satisficing, multi-attribute trade-offs and dominance belong here. So do reversibility and option value, staged commitment, robustness, the value of information, and Klein's recognition-primed decision, the way experts actually decide under time pressure.

**Systems and temporal.** These approaches cover feedback loops, delays, stocks and flows, second-order effects, leverage points (Meadows, Sterman), path dependence, time horizons and scenario planning.

**Argumentation and dialectical.** Toulmin's claim–data–warrant structure, Walton's argument schemes and their critical questions, steelmanning, and burden of proof. They end in synthesis: holding opposed positions until a better one emerges.

**Social cognition and strategic.** Theory of mind and perspective taking come first. Then incentives, game-theoretic and repeated-game reasoning, signalling and credible commitment (Schelling), and the interests behind positions (Fisher & Ury). Trust calibration and coalitions complete the family.

**Communication and framing.** Reasoning has to reach someone, so this family covers audience modelling, common ground, framing effects, sequencing, the curse of knowledge, and how to express uncertainty.

**Metacognitive monitoring and control.** This is thinking about thinking (Flavell, 1979). In Nelson & Narens' framework, *monitoring* watches cognition: feeling of knowing, judgements of learning, error detection, confidence calibration, knowledge boundaries. *Control* steers it: choosing a strategy, allocating effort, deciding when to stop, revising beliefs, debiasing, and reflecting afterwards.

Two cross-cutting ideas run through all of the above. **Dual-process accounts** (Stanovich, Kahneman) separate fast, intuitive processing from slow, deliberate reasoning. **Meta-reasoning research** (Thompson, Ackerman) asks what decides *whether* the slow kind engages at all. That second question is where Part 2 begins.

---

## Part 2 · A working theory: reasoning starts with *whether*

> **Status: hypothesis.** This is Tucuxi's working theory of reasoning primitives. Where it rests on published evidence, the evidence is cited. Where it is interpretation, it says so.

### The trunk: "whether"

Before anyone reasons *if P then Q*, something has to hold P open: P might be the case, or it might not. Call that operation **doubt**, and its linguistic form **whether**:

- *"Whether P"* holds both P and not-P open, before any particular line of reasoning is chosen. It is undifferentiated doubt.
- *"If P then Q"* is formal reasoning. It comes **after** commitment to premises. It is a branch of reasoning, not the trunk.

So doubt comes before conditional reasoning. **Doubt is not scepticism.** Scepticism is a conclusion: committed, arrived at. Doubt is an operation, a possibility held open while it is evaluated.

The same pairing distinguishes *being* from *doing*. Accepting what is presented is reception. Doubting it is evaluation. Reasoning is the move from the first to the second.

### "Whether" is a continuous governor, not an ignition switch

"Whether" does not fire once at the start. It governs reasoning all the way through:

| The governor asks… | Catalog entry |
|---|---|
| whether to doubt at all (**ignition**) | `deliberation-trigger` |
| whether *this* dimension needs doubt (**selection**) | `strategy-selection` |
| whether the current depth is enough (**depth**) | `effort-allocation` |
| whether to keep holding open or commit (**stopping**) | `stopping-rule` |
| whether to reopen a closed question (**revision**) | `belief-revision` |

Commitment is the moment the recursive *whether* resolves to "sufficient". Knowing when to stop is a compiled *whether*.

**Evidence.** Meta-reasoning research supports the ignition step directly. In Thompson, Prowse Turner & Pennycook (2011), the *feeling of rightness* that comes with an intuitive answer predicted whether people went on to reason deliberately. The other four rows are each established topics in metacognitive control. What is new here is the claim that they are **one operation** viewed at different moments.

### Six branches: doubt applied to six domains

When doubt is directed at a particular domain, it becomes a particular kind of reasoning. Natural language lexicalises the six directions as interrogatives:

| Interrogative | Doubt applied to… | becomes | Catalog entries |
|---|---|---|---|
| **When?** | temporal predictions | consequence modelling | `second-order-effects`, `time-horizon-reasoning`, `counterfactual-simulation`, `premortem` |
| **Who?** | models of other minds | perspective revision | `theory-of-mind`, `perspective-taking` |
| **Why?** | one's own emotional response | affect regulation | `affect-regulation` |
| **What?** | the focus of attention | attentional reallocation | `attentional-reallocation`, `triage-prioritization` |
| **How?** | one's own process | metacognitive monitoring | `comprehension-monitoring`, `error-detection`, `progress-monitoring` |
| **Where?** | spatial and contextual configuration | constraint-surface evaluation | `constraint-satisfaction`, `situation-awareness-monitoring` |

English lexicalises the trunk (*whether*) and all six branches. Ashéninka Campa, an Arawakan language of Peru, was reported to have a single interrogative word, *tsika*, for every content question (Givón 2001, citing D. Payne; see also Reed & Payne 1986). Cysouw's corpus study confirms the single interrogative root, but finds that auxiliary-like verbs following *tsika* fix the specific meaning: "who", "where", "how much" and so on. On this theory, Ashéninka lexicalises the trunk with one word and marks the branches with what follows it.

**What the typology supports, and what it does not.** Cysouw's survey of interrogative words across the world's languages (*Interrogative words: an exercise in lexical typology*, 2004) bears on the six-branch claim:

- **Supported.** *Why* is the derived one. Cysouw found English *why* to be the only non-reducible word for REASON in his sample. Elsewhere, REASON is "almost universally derived from THING ('for what')" — French *pourquoi*, and many more. That fits the claim that *why* was the last dimension to get its own word. Whether the reason-dimension is nonetheless *cognitively* independent of *what* is a separate claim, which the theory makes and the typology cannot settle.
- **Not supported as stated.** The six are not equally primary across languages. Cysouw's major categories are *who, what, which, where*, which are basic words in most languages. *When* and *how* are minor: each is an unanalysable word in only about 40% of languages, and *how* is most often built from *what* ("what way"). Languages also lexicalise further categories (selection, quantity, extent, utterance). If the six branches are the right cut, these must be shown to be refinements of the six rather than additional dimensions. That remains open.

### Three levels of doubt

Doubt can also be applied to itself:

1. **Level 1, within a dimension.** What are the alternatives here?
2. **Level 2, about which dimensions to activate.** Does timing matter here at all? Does anyone's mind need modelling?
3. **Level 3, about the activation triggers themselves.** Am I right about what matters in situations like this?

A novice works at level 1, an expert at levels 1–2, and a master at all three. **Level 2 failure is the characteristic expert error:** they didn't know to look. **Level 3 failure is calcification:** they stopped doubting their own triggers.

The hierarchy stops at three because doubting whether to doubt further *is* doubt. Doubt applied to itself returns doubt, which is a fixed point; Descartes' *cogito* is doubt discovering itself through its own application.

### What experts have, and what mentors pass on

On this theory, an expert's tacit knowledge is mostly **compiled doubt**. It is a calibrated sense of *when* to doubt *which* things, and *how much*, together with the cues that set it off. A great mentor does not teach what to know. They teach when to doubt which things. The highest form of the skill is knowing how much doubt each situation deserves.

> Time is what not knowing everything feels like.
> Doubt is the engine that converts not-knowing into seeking.

---

## Part 3 · What this means for ReasoningMapper

The theory and the tool were developed separately, but they meet at several points.

- **Tier 3 is the expert's compiled "whether".** Orchestration habits decide whether a situation needs analysis at all, which dimensions matter, how deep to go and when to stop. Both tier 3 habits in the [worked example](../examples/incident-commander) are of this kind. *Size the response to harm and reversibility* is ignition and depth. *Stabilise first, diagnose second* decides which question gets doubted now and which is deferred.
- **The router's activation cues are level 2.** They tell an agent which habits a situation calls for. That is exactly the knowledge whose absence produces the characteristic expert error, not knowing to look.
- **Curt decisions are compiled "whether".** When trust is established, the governor resolves instantly and the reasoning disappears from the record. That is why `prepare` keeps short replies as the contrast set, and why think-aloud sessions, which slow the governor down enough to hear it, are the richest source.
- **Calibration and review guard against level 3 failure, for the tool and for the expert.** Every instrument must pass known-answer cases before its output is trusted. The expert is asked when each habit does *not* apply.
- **The theory is a lens, not a prompt.** Like the catalog, it is never shown to the extractor; a framework named in a prompt comes back as output. Use it to read the results.

### A test the tool makes possible

If the theory is right, three things should hold:

1. Experts' tier 3 habits should align mostly with the governor entries (`deliberation-trigger`, `strategy-selection`, `effort-allocation`, `stopping-rule`, `belief-revision`).
2. Their tier 1 and tier 2 habits should spread across the six branches.
3. What separates a more experienced practitioner from a less experienced one should show up mainly at level 2 and above: *which* habits they activate, not the habits themselves.

`rmap align` records the first two for any project. The third needs two experts in the same field.

---

### References for Part 2

- Ackerman, R., & Thompson, V. A. (2017). Meta-reasoning: Monitoring and control of thinking and reasoning. *Trends in Cognitive Sciences*, 21(8), 607–617.
- Cysouw, M. (2004). *Interrogative words: an exercise in lexical typology.* Handout, Bantu Grammar Workshop 3, ZAS Berlin.
- Cysouw, M. *Content interrogatives in Asheninca Campa (Arawak): corpus study and typological comparison.* Manuscript, cysouw.de.
- Givón, T. (2001). *Syntax: An Introduction* (2 vols.), pp. 303–304. John Benjamins.
- Reed, J., & Payne, D. L. (1986). Asheninca (Campa) pronominals. In U. Wiesemann (ed.), *Pronominal Systems*, 323–331. Gunter Narr.
- Thompson, V. A., Prowse Turner, J. A., & Pennycook, G. (2011). Intuition, reason, and metacognition. *Cognitive Psychology*, 63(3), 107–140.

Part 1's sources are listed per entry in [`catalog/reasoning_catalog.yaml`](../catalog/reasoning_catalog.yaml).
