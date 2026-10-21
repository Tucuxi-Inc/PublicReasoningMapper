# ReasoningMapper Claude Code plugin

Two skills:

- **reasoning-mapper** guides a project stage by stage: what to run, what to check after each stage, and the two decisions (review and orchestration) that belong to the expert.
- **think-aloud-session** turns Claude into the facilitator for a text-based think-aloud session, and writes the transcript in the format `rmap ingest` reads.

Install from a clone of this repository:

```bash
claude plugin marketplace add /path/to/ReasoningMapper
claude plugin install reasoning-mapper@tucuxi-reasoning-mapper
```

The `rmap` command line itself is installed separately: `pip install -e '.[docs]'` from the repository root.
