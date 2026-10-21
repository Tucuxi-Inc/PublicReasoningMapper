# Privacy

An email archive holds other people's words, names and confidences, and often privileged or regulated material. ReasoningMapper is built so that the default path keeps all of it on your machine.

## What stays local, always

- `rmap.db`: every message, document and transcript, unredacted, plus each episode's redaction legend (tag → original). The `.gitignore` that `rmap init` writes excludes it. Keep it off shared drives.
- `calibration/known.yaml`: real text from your material. It is also git-ignored.
- `review/*.json` and `map/pattern_episodes.json`: episode references and evidence quotes. These are git-ignored too.
- **Redaction itself.** The annotate and verify roles always run on your local Ollama server, even when extraction uses the Claude API, because they see text before it is clean.

## What can leave, and when

With the default `backend: ollama`, nothing leaves the machine.

With `backend: anthropic`, only the `extract` and `draft` steps call the API, and only when **all** of these hold:

1. `privacy.allow_cloud: true` in `rmap.yaml`;
2. `rmap calibrate` has passed its redaction cases on this project;
3. the episode's redaction was **verified clean** by the second-family audit. An unverified episode is refused, not sent.

## What ends up in the skills

Generated skills contain the habit's name, description, procedure, cues, quality indicators, pitfalls, a composite example, and the expert's own review note. They are drafted from redacted evidence, and the drafting prompt forbids identifiers. Raw quotes appear only with `--include-evidence`, and only from verified-clean episodes. **Read the skills before you share them.** Redaction lowers risk; it does not remove it. A distinctive situation can identify a matter even with every name removed.

## Before you start

- Check that you have the right to process the archive: employment agreements, client confidentiality, privilege and data-protection law all apply. The tool cannot decide this for you.
- Put names that must never appear in `privacy.extra_identifiers` (clients, codenames, matters). Put public terms that are not identifiers (statutes, standards, public products) in `privacy.keep_terms`.
- Write redaction calibration cases from your hardest material, such as documents that name people merely discussed. The vocabulary floor is weakest there.
