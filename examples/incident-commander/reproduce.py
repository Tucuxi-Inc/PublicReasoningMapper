# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Rebuild every generated file in this example from corpus/ and replay/.

The two human steps - the expert's review decisions and their edits to the
orchestration map - are written out below as data, so the whole run is
reproducible. In a real project you make these edits by hand in
review/moves.yaml and map/patterns.yaml.

    python reproduce.py            # from this directory
"""

import shutil
import sys
from pathlib import Path

import yaml

from reasoning_mapper.cli import main as rmap
from reasoning_mapper.mapping import load_map, save_map

HERE = Path(__file__).resolve().parent
P = "incident-commander-"

# Step 1 - the expert reviews the habit sheet (review/moves.yaml).
# (decision, merge_into, name, tier, notes)
REVIEW = {
    "m01": ("keep", None, "Ask what changed", 1,
            "Comparing what changed before each recurrence is the same habit applied across events."),
    "m02": ("keep", None, "Find who carries the cost", 1, ""),
    "m03": ("keep", None, "Prefer the move you can undo", 1,
            "Capturing evidence first and rehearsing the rollback are what keep the undo cheap."),
    "m04": ("keep", None, "Promise the next update, not the fix", 2,
            "The update time is a promise I control; the fix time is not. "
            "Never pass on someone else's estimate as ours."),
    "m05": ("keep", None, "Size the response to harm and reversibility", 3,
            "Repetition overrides size: three small events are a pattern and get a proper look. "
            "Knowing how much time you have is part of the sizing."),
    "m06": ("merge", "m07", "", None, ""),
    "m07": ("keep", None, "Price the risk, offer a cheaper path", 2,
            "Offering the smaller version is the second half of pricing the risk, not a separate habit."),
    "m08": ("keep", None, "Stabilise first, diagnose second", 3, ""),
    "m09": ("merge", "m04", "", None, ""),
    "m10": ("merge", "m03", "", None, ""),
    "m11": ("merge", "m05", "", None, ""),
    "m12": ("drop", None, "", None, "Real, but one instance is too thin to teach from."),
    "m13": ("merge", "m03", "", None, ""),
    "m14": ("merge", "m05", "", None, ""),
}


def apply_review(sheet_path: Path) -> None:
    text = sheet_path.read_text()
    head = "".join(l for l in text.splitlines(True) if l.startswith("#"))
    sheet = yaml.safe_load(text)
    for c in sheet["clusters"]:
        d, into, name, tier, notes = REVIEW[c["id"]]
        c.update(decision=d, merge_into=into, name=name, tier=tier, notes=notes)
    sheet_path.write_text(head + yaml.safe_dump(sheet, sort_keys=False, allow_unicode=True, width=100))


# Step 2 - after `rmap link`, three habits had no orchestrating tier 3 pattern:
# co-occurrence alone did not connect them. The expert's view is that deciding
# whether a risk is worth taking IS sizing by harm and reversibility.
def apply_map_edits(map_path: Path) -> None:
    m = load_map(map_path)
    by = {p["id"]: p for p in m["patterns"]}
    size = by[P + "size-the-response-to-harm-and-reversibility"]
    stab = by[P + "stabilise-first-diagnose-second"]
    for x in ("prefer-the-move-you-can-undo", "find-who-carries-the-cost",
              "price-the-risk-offer-a-cheaper-path"):
        if P + x not in size["source_skills"]:
            size["source_skills"].append(P + x)
    if P + "prefer-the-move-you-can-undo" not in stab["source_skills"]:
        stab["source_skills"].append(P + "prefer-the-move-you-can-undo")
    size["works_with"] = [stab["id"]]
    save_map(m, map_path)


def run(root: Path = HERE) -> None:
    for d in ("map", "skills"):
        shutil.rmtree(root / d, ignore_errors=True)
    for f in [root / "rmap.db", *root.glob("rmap.db-*"), *(root / "review").glob("*")]:
        f.unlink(missing_ok=True)
    r = lambda *a: rmap(["-C", str(root), *a])
    r("ingest"); r("prepare")
    try:
        r("calibrate")       # the hashing embedder is expected to FAIL; see README
    except SystemExit:
        pass
    r("redact"); r("extract")
    r("group")
    apply_review(root / "review" / "moves.yaml")
    r("draft"); r("link")
    apply_map_edits(root / "map" / "patterns.yaml")
    r("link")
    try:
        r("validate")
    except SystemExit as e:
        if e.code:
            raise
    # The recorded judge answers name catalog ids it saw in a nomic-embed-text
    # shortlist. The offline `hashing` embedder ranks differently, so show the
    # judge the whole catalog here; ids it was not shown would be discarded.
    r("align", "--shortlist", "200")
    r("write-skills")
    r("visualize")


if __name__ == "__main__":
    run(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE)
