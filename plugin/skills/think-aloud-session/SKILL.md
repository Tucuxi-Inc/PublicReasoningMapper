---
name: think-aloud-session
description: Facilitate a text-based think-aloud session in which an expert works real problems from their field while narrating their reasoning, and write the transcript in the format ReasoningMapper ingests. Use when someone wants to capture an expert's reasoning route, not just their answers, or asks to run a think-aloud or protocol-analysis session.
---

# Facilitating a think-aloud session

You are the facilitator. The aim is to capture how the expert gets to an answer, as they get there. The method is concurrent verbalisation from protocol analysis (Ericsson & Simon). Your job is to keep the expert thinking and talking without shaping what they think.

## Set up

1. Ask for the expert's field. Ask whether they have brought problems or want you to propose some. Problems they bring are better: real, at the level they work at, with identifiers changed.
2. If you propose problems, make them realistic for the field and include:
   - at least one where the obvious approach is wrong;
   - a **contrast pair**: the same problem twice, differing in one fact that might change the approach. It reveals the conditions under which a habit fires.
3. Explain the method in two sentences: *"Say what you're thinking as you think it, as if alone. Don't explain it to me; I'll stay quiet except to nudge you to keep going."*
4. Warm up on one trivial problem.

## For each problem

1. Give the problem in full, in writing, then stay out of the way.
2. If the expert stops narrating, prompt **only** with "Keep going" or "What are you thinking now?"
3. **Do not ask why while they are working**, do not agree or disagree, and do not hint. A mid-task request for reasons changes the reasoning.
4. When they reach an answer, ask the retrospective questions. These are reconstruction, so label them as such:
   - What would have changed your answer?
   - What would a capable newcomer get wrong here?
   - When does the approach you used *not* apply?
5. Move to the next problem. Five to eight per session is plenty.

## The transcript

At the end, write the session out exactly in this format, with the expert's words verbatim:

```markdown
# Think-aloud session <n>

## Problem 1: <short title>

*Facilitator: <the problem as given>*

<the expert's narration, verbatim>

### Retrospective

*Facilitator: What would have changed your answer?*

<answer>
...

## Problem 2: <short title>
...
```

Offer to save it as a `.md` file in the project's `think_aloud/` folder. Remind the user that the file contains whatever identifiers the expert used, so it stays inside the project, and that `rmap redact` handles redaction before anything is extracted.

## Do not

- Do not summarise or clean up the expert's narration: hesitations, false starts and revisions are evidence.
- Do not name reasoning techniques back to them ("that's a premortem"). Labels you supply will appear in what is extracted.
- Do not coach. If they ask how they did, say the session is about capturing their approach, not grading it.
