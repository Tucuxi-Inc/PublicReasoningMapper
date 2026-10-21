# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""rmap - the ReasoningMapper command line.

Stages, in order:

    rmap init         write rmap.yaml and calibration/known.yaml templates
    rmap ingest       read every configured source into rmap.db
    rmap prepare      authored text, expert attribution, threads, episodes
    rmap redact       input-side redaction with an independent audit
    rmap calibrate    known-answer checks on stripping, redaction, embedding
    rmap extract      open extraction of reasoning moves
    rmap group        moves -> candidate habits (model judge) + a review sheet
    rmap cluster      faster alternative: embedding clusters only (topic, not stance)
    rmap draft        reviewed clusters -> map/patterns.yaml
    rmap link         propose orchestration links from co-occurrence
    rmap align        which general reasoning approaches each habit builds on
    rmap validate     check the map (or a skills folder)
    rmap write-skills generate the Claude skills
    rmap visualize    the orchestration map as a 3D graph (HTML) and a Mermaid flowchart
    rmap status       where the project stands
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import CONFIG_NAME, TEMPLATE, Project


def _ctx(args):
    from .store import connect
    p = Project.load(args.project)
    return p, connect(p.db_path)


def cmd_init(args):
    root = Path(args.project)
    root.mkdir(parents=True, exist_ok=True)
    cfg = root / CONFIG_NAME
    if cfg.exists():
        print(f"{cfg} exists; leaving it alone")
    else:
        cfg.write_text(TEMPLATE)
        print(f"wrote {cfg}")
    from .calibrate import TEMPLATE as KNOWN
    known = root / "calibration" / "known.yaml"
    if not known.exists():
        known.parent.mkdir(parents=True, exist_ok=True)
        known.write_text(KNOWN)
        print(f"wrote {known}")
    gi = root / ".gitignore"
    if not gi.exists():
        gi.write_text("# raw text and identifiers: never commit these\nrmap.db*\ncalibration/\n"
                      "review/*.json\nmap/pattern_episodes.json\n*.pst\n*.mbox\n")
        print(f"wrote {gi}")


def cmd_ingest(args):
    from .ingest import ingest_source
    p, conn = _ctx(args)
    if not p["sources"]:
        sys.exit("no sources in rmap.yaml")
    for src in p["sources"]:
        print(ingest_source(conn, p, src))


def cmd_prepare(args):
    from . import authored, episodes, threads
    from .ingest import mark_expert
    p, conn = _ctx(args)
    e = p["expert"]
    if not (e["addresses"] or e["display_names"] or e["name"]):
        sys.exit("set expert.addresses (and ideally display_names) in rmap.yaml first")
    print(f"authored text: {authored.materialise(conn):,} messages stripped of quoted replies")
    n = mark_expert(conn, p.expert_addresses, p.expert_names, e["sent_folders"])
    total = conn.execute("SELECT count(*) FROM messages").fetchone()[0]
    print(f"expert-authored: {n:,} of {total:,} messages")
    if total and n == 0:
        print("  WARNING: no message attributed to the expert - check expert.addresses")
    th = p["threading"]
    t = threads.build(conn, th["generic_subjects"], th["max_gap_days"], th["max_span_days"])
    threads.persist(conn, t)
    print(f"threads: {len(t):,} ({sum(1 for v in t.values() if len(v) >= 2):,} with 2+ messages)")
    counts = episodes.build(conn, p["episodes"])
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {k:20} {v:7,}")


def cmd_redact(args):
    from . import redact
    from .llm import LLM
    p, conn = _ctx(args)
    llm = LLM(p)
    r = redact.run(conn, p, llm, args.limit, args.redo, args.types, args.sample, args.seed)
    if not r["models"]:
        print("NOTE: annotate_model/verify_model not set - vocabulary floor only, nothing verified.\n"
              "      Fine for a local-only run; the cloud backend will refuse unverified text.")
    print(json.dumps(r, indent=1))


def cmd_calibrate(args):
    from . import calibrate
    from .llm import LLM, Embedder
    p, conn = _ctx(args)
    res = calibrate.run(conn, p, LLM(p), Embedder(p))
    bad = False
    for inst, r in res.items():
        print(f"{inst:10} {'PASS' if r['passed'] else 'FAIL'}  {r['score']}")
        for n in r["notes"]:
            print(f"           {n}")
        bad |= not r["passed"]
    sys.exit(1 if bad else 0)


def cmd_extract(args):
    from . import extract
    from .calibrate import passed
    from .llm import LLM
    p, conn = _ctx(args)
    if p["models"]["backend"] == "anthropic" and not passed(conn, "redaction"):
        sys.exit("the cloud backend needs `rmap calibrate` to pass its redaction cases first")
    print(json.dumps(extract.run(conn, p, LLM(p), args.types, args.limit, args.retry_errors), indent=1))


def cmd_cluster(args):
    from . import cluster
    from .calibrate import passed
    from .llm import Embedder
    p, conn = _ctx(args)
    emb = Embedder(p)
    ok = passed(conn, "embedding")
    if ok is not True:
        print(f"WARNING: the embedder has {'not been calibrated' if ok is None else 'FAILED calibration'}"
              f" ({emb.name}). Cluster membership may measure spelling, not meaning.")
    res = cluster.cluster(conn, emb, args.kind, args.k)
    sheet = Path(args.sheet) if args.sheet else p.path("review", f"{args.kind}s.yaml")
    cluster.write_sheet(res, sheet, args.force)
    print(f"{res['distinct']} distinct {args.kind} names in {res['mentions']} mentions -> "
          f"{res['k']} clusters\nreview sheet: {sheet}")
    if res["warning"]:
        print("WARNING:", res["warning"])


def cmd_group(args):
    from . import cluster, group
    from .calibrate import passed
    from .llm import LLM, Embedder
    p, conn = _ctx(args)
    if passed(conn, "grouping") is not True:
        print("WARNING: the grouping judge has not passed calibration (rmap calibrate).")
    res = group.group(conn, Embedder(p), LLM(p), args.kind, args.shortlist)
    sheet = Path(args.sheet) if args.sheet else p.path("review", f"{args.kind}s.yaml")
    cluster.write_sheet(res, sheet, args.force)
    print(f"{res['distinct']} distinct {args.kind} names in {res['mentions']} mentions -> "
          f"{res['k']} habits\nreview sheet: {sheet}")
    if res["warning"]:
        print("WARNING:", res["warning"])


def cmd_draft(args):
    from . import mapping
    from .llm import LLM
    p, _ = _ctx(args)
    sheets = [Path(s) for s in args.sheets] or sorted(p.path("review").glob("*.yaml"))
    print(json.dumps(mapping.draft(p, LLM(p), sheets, p.path("map", "patterns.yaml")), indent=1))


def cmd_link(args):
    from . import mapping
    from .llm import LLM
    p, _ = _ctx(args)
    r = mapping.link(p.path("map", "patterns.yaml"), args.min_shared, LLM(p) if args.judge else None)
    print(json.dumps(r, indent=1))
    if r["unorchestrated"] or r["orchestrating nothing"]:
        print("Edit map/patterns.yaml to give these an orchestrating tier 3 pattern"
              + ("." if args.judge else ", or rerun with --judge to have the model propose one."))


def cmd_align(args):
    from . import align
    from .calibrate import passed
    from .llm import LLM, Embedder
    p, conn = _ctx(args)
    if passed(conn, "alignment") is not True:
        print("NOTE: no passing `alignment` calibration cases - judge accuracy is unmeasured.")
    print(json.dumps(align.run(p, LLM(p), Embedder(p), p.path("map", "patterns.yaml"),
                               args.shortlist, args.redo), indent=1))


def cmd_visualize(args):
    from . import visualize
    p, _ = _ctx(args)
    out = Path(args.out) if args.out else p.path("map", "graph.html")
    print(json.dumps(visualize.write(p.path("map", "patterns.yaml"), out), indent=1))


def cmd_validate(args):
    from .mapping import load_map
    from .validate import check_patterns, check_skills_dir
    if args.skills:
        errors, warnings = check_skills_dir(Path(args.skills))
    else:
        p = Project.load(args.project)
        errors, warnings = check_patterns(load_map(p.path("map", "patterns.yaml")).get("patterns") or [])
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:  ", e)
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


def cmd_write_skills(args):
    from . import skills
    p = Project.load(args.project)
    out = Path(args.out) if args.out else p.path("skills")
    r = skills.write(p, p.path("map", "patterns.yaml"), out, args.style,
                     args.include_evidence, args.version, args.force)
    for w in r["warnings"]:
        print("warning:", w)
    print(f"wrote {r['skills']} skills to {out} (router: {r['router']})")


def cmd_status(args):
    from .calibrate import passed
    p, conn = _ctx(args)
    q = lambda s: conn.execute(s).fetchone()[0]
    print(f"project      {p.root}")
    print(f"messages     {q('SELECT count(*) FROM messages'):,} "
          f"({q('SELECT count(*) FROM messages WHERE is_expert=1'):,} by the expert)")
    print(f"documents    {q('SELECT count(*) FROM documents'):,}")
    print(f"sessions     {q('SELECT count(*) FROM sessions'):,}")
    print(f"episodes     {q('SELECT count(*) FROM episodes'):,}")
    for r in conn.execute("SELECT episode_type, count(*) n FROM episodes GROUP BY 1 ORDER BY 2 DESC"):
        print(f"  {r[0]:18} {r[1]:7,}")
    print(f"redacted     {q('SELECT count(*) FROM episodes WHERE redacted IS NOT NULL'):,} "
          f"(verified clean {q('SELECT count(*) FROM episodes WHERE verified=1'):,}, "
          f"residuals {q('SELECT count(*) FROM episodes WHERE verified=0'):,})")
    print(f"extracted    {q('SELECT count(*) FROM extractions WHERE error IS NULL'):,} "
          f"(errors {q('SELECT count(*) FROM extractions WHERE error IS NOT NULL'):,})")
    moves = q("SELECT count(*) FROM items WHERE kind='move'")
    cons = q("SELECT count(*) FROM items WHERE kind='consideration'")
    print(f"items        {moves:,} moves, {cons:,} considerations")
    for inst in ("authored", "redaction", "embedding", "grouping", "alignment"):
        v = passed(conn, inst)
        print(f"calibration  {inst:10} {'not run' if v is None else 'pass' if v else 'FAIL'}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="rmap", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-C", "--project", default=".", help="project directory (default: .)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    sub.add_parser("ingest").set_defaults(fn=cmd_ingest)
    sub.add_parser("prepare").set_defaults(fn=cmd_prepare)
    s = sub.add_parser("redact"); s.set_defaults(fn=cmd_redact)
    s.add_argument("--limit", type=int); s.add_argument("--redo", action="store_true")
    s.add_argument("--types", nargs="+", help="episode types (default: those extract reads)")
    s.add_argument("--sample", type=int, help="redact a seeded random subset of this size")
    s.add_argument("--seed", type=int, default=0)
    sub.add_parser("calibrate").set_defaults(fn=cmd_calibrate)
    s = sub.add_parser("extract"); s.set_defaults(fn=cmd_extract)
    s.add_argument("--types", nargs="+"); s.add_argument("--limit", type=int)
    s.add_argument("--retry-errors", action="store_true")
    s = sub.add_parser("cluster"); s.set_defaults(fn=cmd_cluster)
    s.add_argument("--kind", choices=["move", "consideration"], default="move")
    s.add_argument("--k", type=int, default=0); s.add_argument("--sheet")
    s.add_argument("--force", action="store_true")
    s = sub.add_parser("group"); s.set_defaults(fn=cmd_group)
    s.add_argument("--kind", choices=["move", "consideration"], default="move")
    s.add_argument("--shortlist", type=int, default=8); s.add_argument("--sheet")
    s.add_argument("--force", action="store_true")
    s = sub.add_parser("draft"); s.set_defaults(fn=cmd_draft)
    s.add_argument("sheets", nargs="*")
    s = sub.add_parser("link"); s.set_defaults(fn=cmd_link)
    s.add_argument("--min-shared", type=int, default=2)
    s.add_argument("--judge", action="store_true",
                   help="have the model propose an orchestrator for patterns co-occurrence leaves orphaned")
    s = sub.add_parser("align"); s.set_defaults(fn=cmd_align)
    s.add_argument("--shortlist", type=int, default=12); s.add_argument("--redo", action="store_true")
    s = sub.add_parser("visualize"); s.set_defaults(fn=cmd_visualize)
    s.add_argument("--out", help="HTML file to write (default: map/graph.html)")
    s = sub.add_parser("validate"); s.set_defaults(fn=cmd_validate)
    s.add_argument("--skills", help="validate a generated skills folder instead of the map")
    s = sub.add_parser("write-skills"); s.set_defaults(fn=cmd_write_skills)
    s.add_argument("--out"); s.add_argument("--style", choices=["native", "portable"], default="native")
    s.add_argument("--include-evidence", action="store_true")
    s.add_argument("--version", default="1.0"); s.add_argument("--force", action="store_true")
    sub.add_parser("status").set_defaults(fn=cmd_status)
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
