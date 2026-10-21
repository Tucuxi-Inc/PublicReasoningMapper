# Method

ReasoningMapper was first built against one practitioner's real 20-year archive. Most of what it does differently comes from things that went wrong there. In each case the tool produced a number that looked right, and the error surfaced only when someone tried to use that number for a decision. This document records each lesson and the design choice it led to, so you can judge whether it applies to your material.

## 1. What expertise looks like in a record of work

An expert explains their reasoning while trust is being built, and compresses it once trust exists. Early in a working relationship, or when someone pushes back, they say why. Later the same judgement arrives as "approved, go ahead".

So the record holds two kinds of evidence:

- **adjustment exchanges**: the expert answers, someone pushes back, and the expert explains or revises. This is the richest explanatory material.
- **curt decisions**: the same expertise with the reasoning compressed out. They are the contrast set, not noise.

`prepare` classifies every thread by this shape (`adjustment`, `substantive_reply`, `curt_decision`, `exchange`), and `extract` reads the explanatory classes by default.

## 2. Measure authored text, never raw length

A reply quotes everything before it. On the original archive, authored text was under a tenth of raw body text. Half of all messages carried under 200 authored characters while looking long on raw length.

Every length-based decision built on raw bodies was measuring reply convention instead:

- a "substantial message" filter (raw length > 200) removed 4% of messages while half the corpus was short. It never selected for substance, and it hid most of the curt decisions;
- an explanatory-vs-curt classifier fired "explanatory" on nearly any reply with a quote tail;
- a trend over a matter's lifetime ("the expert gets wordier") reversed sign once quotes were stripped.

So `prepare` strips quoted replies and signatures once, stores the result, and everything downstream reads it. Stripping cuts at the *first* quote marker on purpose. Over-cutting biases every message's length down by the same amount, while under-cutting biases it up with thread age, and that age-correlated error is the confound that matters.

## 3. Don't put the answer in the question

Every candidate label placed in an extraction prompt came back as output:

- naming four candidate "dimensions" of reasoning made the first of them appear on 94% of episodes. A label that fires on everything discriminates nothing;
- five example move names in a prompt became the five most-extracted names;
- a list of known patterns to "match where one fits" anchored the output to that list.

So `extract` asks an open question, with no taxonomy, no examples and no dimensions. The output fragments (nearly every move name is distinct), and grouping is what makes it countable. The fragmentation is the price of not seeding the answer.

The same rule governs the reference catalog of general reasoning approaches in `catalog/`. It is used only *after* the expert has reviewed and named their habits, to see which general approaches they draw on. It is never shown to the extractor.

## 4. Topic is not stance: grouping needs a judge

Grouping thousands of free-text move names by embedding similarity is the obvious approach, and it is not reliable for reasoning. Four local embedders were tested on short move names (nomic-embed-text, qwen3-embedding, embeddinggemma, granite-embedding):

- a lexical near miss beat a true paraphrase. "Find what the change costs" scored above "ask who pays if this goes wrong" as a match for "find who carries the cost";
- the opposite habit scored 0.89–0.99. "Diagnose first, stabilise second" sat almost on top of "stabilise first, diagnose second".

Embeddings measure topic. Habits differ in action and stance. So `rmap group` uses embeddings only to shortlist candidate habits, and a model judge decides whether each move is an instance of an existing habit: the same kind of thing, for the same reason, in the same stance. A 12B local judge grouped the same test cases correctly on repeated runs.

The judge's wording matters more than its shortlist. The first wording asked for "the same action, the same purpose, the same stance". On a real archive it left most moves as habits of one, which is a review sheet nobody can use. Re-judging a sample of those singletons, a longer shortlist (30 candidates instead of 8) changed nothing. Asking instead whether the practitioner would file both moves under one habit merged several times as many, and the new wording still passed every calibrated grouping, opposite-stance traps included. The judge still errs towards splitting, which is the safer direction: merging two habits in review is one line, but splitting one is impossible from the review sheet.

`rmap cluster` (embedding-only) remains as a fast first look, and it says so when it runs.

## 5. Every instrument earns trust on known answers

A quote stripper always returns a string, a redactor always returns text, and a similarity argmax always returns a nearest neighbour. None of them signals when it is wrong. A plausible wrong number has no symptom of its own: it shows up as whatever symptom the surrounding system happens to produce.

So `rmap calibrate` runs each instrument on cases whose answer is not in doubt, which you write from your own material:

| instrument | passes when |
|---|---|
| `authored` | every `keep` string survives and every `drop` string is cut |
| `redaction` | every `must_remove` identifier is gone and every `must_keep` fact survives |
| `embedding` | each paraphrase outscores every near miss sharing its anchor; near misses must share words, or a spelling-based embedder could pass |
| `grouping` | the judge places every pair of moves together exactly when you said they belong together |

Two habits make calibration honest. First, include **near misses**: pairs that share words but differ in meaning. Without them, the dependency-free `hashing` embedder passes the embedding check. That happened while this tool was being built. Second, prefer a verifier from a **different model family** from the thing it audits, because a same-family reader shares the same blind spots.

## 6. Redact the input, audit with a different family

Asking the extraction model to replace names in its own output works on short snippets and fails on long, entity-dense episodes. On the original archive it failed on every episode tested at episode scale. A model cannot emit a name it was never shown, so redaction happens on the input:

1. **A vocabulary floor built from the corpus itself.** It covers correspondent names, address local parts, mail domains, and recurring capitalised non-dictionary tokens. This is strong on mail, where the identifiers are the correspondents, and weak on documents, which name people merely discussed.
2. **A local model lists identifiers**, which are then replaced deterministically.
3. **A model from a different family audits the result**, without seeing the annotator's list. Anything it finds is replaced and audited once more. An audit that returns nothing usable leaves the episode *unverified*, not clean.

Three failures from the first real-archive calibration are now guarded by tests. A codename written in capitals slipped past a vocabulary that matched only the Title-case form, and so did a name in an all-caps signature. The annotator listed years, counts and "99.9 percent" as identifiers, so a listed entity now needs a capital letter. And it listed "the Americans with Disabilities Act" with its article, which slipped past an exact-match keep list, so `keep_terms` are now masked from every replacement pass.

Aliases stay stable within an episode (`[PERSON_1]`, `[COMPANY_A]`), because reasoning about how one party compares with another depends on telling them apart. Numbers, dates and thresholds are never tagged: they carry no identity, and they are what makes a procedure specific.

## 7. Threads, and the expert's own side of them

Threading on subject alone collapses unrelated conversations, worst of all on a profession's generic subject lines, which get reused for years. `prepare` threads on RFC headers first. Next it falls back to a distinctive subject plus a shared participant within a time window. Finally it attaches the expert's sent copies, which in Outlook archives often carry no headers at all. Any thread still spanning more than a year is split.

## 8. The richest source is the one nobody recorded

Email preserves the decision, and a training deck preserves the answer. When an expert teaches live, though, they narrate how they got there, and that narration is usually spoken once and lost. A think-aloud session over real problems in the field captures problem, route and answer together. [THINK_ALOUD.md](THINK_ALOUD.md) explains how to run one, and `ingest` treats transcripts as their own source type.

## 9. Co-occurrence proposes, the expert disposes

`rmap link` proposes orchestration from co-occurrence: habits that appear in the same episodes. It fills only empty fields and records its basis (shared episodes, lift) beside each link. On small corpora co-occurrence leaves gaps. In the worked example, three habits had no tier 3 parent until the expert placed them, and `rmap validate` refuses to pass a map with orphans.

On a large map the gaps become most of the map. Two habits seen in a handful of episodes each rarely share two of them, so co-occurrence links only the most frequent habits, and the expert would have to place the rest by hand. `rmap link --judge` asks the model, for each orphan, which tier 3 habit would call on it. Judged links say so in their `link_basis` (`judged:` with the model's reason, instead of shared episodes and lift), so the expert can review them apart from links the episodes support. The judge almost never answers "none": treat its proposals as a first draft of the orchestration, not as evidence.

`rmap visualize` draws the map as an interactive 3D graph (`map/graph.html`): tier 3 habits as hubs, orchestration as directed links, judged links in their own colour, and every habit that nothing orchestrates (or that orchestrates nothing) flagged. It is the quickest way to review a large orchestration. The page embeds only the map, and loads its 3D libraries from a CDN.

## 10. Aligning with general reasoning: what "subset" means

It is tempting to assume an expert's habits are a subset of the general reasoning approaches cognitive science has named. `rmap align` tests that assumption rather than building it in, and building the worked example showed what the test can and cannot say.

- **Almost every habit applies something general.** A habit that looked like pure domain know-how (move a shipment to the next carrier window once the cutoff passes) really is timing-and-window reasoning. "Matched / unmatched" is therefore a weak measure.
- **The content is in the conditioning.** "Ask what changed" applies the method of difference. What the expert adds is *when* to reach for it first, and what to look at. `beyond_general` records that, and it is usually the part worth teaching.
- **Judges over-match.** Asked only "which approaches does this resemble", a 12B judge returned up to five per habit, several of them doubtful. Requiring the judge to name the step of the habit that performs each approach cut that to one or two, stable across runs. `alignment` calibration cases (including a `forbid` list) measure this on your material.

So the honest finding to expect is not "the expert's reasoning is a subset of the catalog". It is closer to "the expert's habits are general operations, *conditioned* on domain cues the catalog does not contain". Those conditions are what the generated skills preserve.
