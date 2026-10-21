# Example: hand-written general reasoning skills

Nine skills from Tucuxi's **Universal Reasoning Primer**, a library of general reasoning patterns synthesised from the cognitive-science and decision literature. They are not drawn from anyone's correspondence. They are included to show the other kind of skill set ReasoningMapper's format can hold:

| | [`incident-commander`](../incident-commander) | this example |
|---|---|---|
| source | one expert's own work | the research literature |
| scope | one person, one field | domain-general |
| made by | `rmap` pipeline + expert review | written by hand |

An expert's extracted habits are typically general operations like these, *conditioned* on cues from the expert's own field. `rmap align` records that relationship against `catalog/`. See [docs/METHOD.md §10](../../docs/METHOD.md).

## The sample

```
TIER 3  urp-mc12 Depth calibration ──────┬─ urp-sp2  Information gap analysis          (1)
        urp-mc16 Approach selection ─────┼─ urp-sp6  Multi-perspective analysis        (1)
        urp-mc24 Confidence calibration ─┼─ urp-sp9  Scenario construction & contingency (1)
                                         ├─ urp-ip4  Information sufficiency calibration (2)
                                         ├─ urp-ip9  Creative option generation        (2)
                                         └─ urp-ip28 Trust calibration                 (2)
```

`rmap validate --skills examples/universal-reasoning-primer/skills` passes.

## How the originals were adapted

- **Bodies are verbatim.** Their prose sometimes mentions primer patterns outside this sample (for example URP-MC29); those references are left as in the original.
- **The frontmatter was normalised** to ReasoningMapper's three-tier rules, under which only tier 3 orchestrates:
  - each tier 3 skill's `source_skills` names the tier 1 and 2 skills in this sample;
  - links that pointed outside the sample were removed;
  - the primer's own tier 1 → tier 2 links became `cross_references`;
  - provenance fields (`validated_by`, `source_type`, `tags` and others) were kept.

Copyright (C) 2026 Tucuxi, Inc. Licensed under the Apache License, Version 2.0.
