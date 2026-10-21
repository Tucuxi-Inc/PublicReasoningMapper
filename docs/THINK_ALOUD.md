# Think-aloud sessions

Email preserves the decision. Documents and decks preserve the answer. When an expert teaches live, they show the answer *and narrate how they got there*, and that narration is spoken once and never recorded. A think-aloud session recovers it: problem, route and answer together, which no archive does.

An hour of good sessions is often worth more than a year of email. Schedule them.

## Choosing problems

- **Real problems from the field, at the level the expert actually works at.** Use redacted or composite cases if needed. Don't use textbook exercises.
- **Problems where the obvious approach is wrong.** The habits worth capturing are the ones a capable newcomer would miss.
- **Contrast pairs.** Two versions of one problem that differ in one fact the expert thinks matters ("same request, but the change can't be rolled back"). The difference in their route shows the *condition* under which a habit fires, and conditions are what make a skill trigger at the right moment.
- **A few they decide in seconds.** Ask them to slow down and say what they noticed. This is where the curt, trust-established decisions come from.

Five to eight problems per hour-long session is plenty.

## Running a session

The method follows protocol analysis (Ericsson & Simon, *Protocol Analysis: Verbal Reports as Data*, 1993):

1. **Warm up** on a trivial problem so that talking while thinking feels normal.
2. **Give the problem in writing and let them work.** Ask them to say what they are thinking as they think it, not to explain it to you.
3. **Prompt only with "keep talking"** when they go quiet. Don't ask "why" during the problem. A request for reasons mid-task changes the reasoning and invites after-the-fact justification.
4. **After the problem, ask the retrospective questions.** What would have changed your answer? What would a newcomer get wrong here? When does this approach *not* apply? Mark this part clearly in the transcript: it is reconstruction, and valuable as such, but it is a different kind of evidence.
5. **Don't coach and don't agree.** Neutral acknowledgements only.

## Recording and transcripts

Record locally. For audio, `pip install 'reasoning-mapper[audio]'`. `rmap ingest` then transcribes it on your machine with faster-whisper and caches the transcript beside the recording.

Give each problem a heading, so that `prepare` splits the session into one episode per problem:

```markdown
## Problem 1: <short title>

*Facilitator: <the problem as given>*

<the expert's words>

### Retrospective

<answers to the follow-up questions>
```

Lines beginning `## Problem`, `## Exercise`, `## Scenario` or `## Case` start a new episode.

Then add the folder to `rmap.yaml`:

```yaml
sources:
  - {type: transcripts, path: think_aloud}
```

## The Claude Code skill

`plugin/skills/think-aloud-session` turns Claude into the facilitator for a text-based session. It gives problems one at a time, prompts only with "keep going", asks the retrospective questions after each problem, and writes the transcript in the format above. That works for experts who think best in writing. Spoken sessions capture more of the route, so prefer them where you can.
