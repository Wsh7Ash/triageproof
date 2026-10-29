"""triageproof command line interface.

Corpus commands (validate / list / show / search / build) come from the pack
harness. The domain commands work the triage angle:

    triageproof signature crash.txt
    triageproof similar a.txt b.txt
    triageproof dedupe new.txt known/*.txt
    triageproof cluster crashes/*.txt --threshold 0.6
    triageproof bundle evidence/ --write evidence/manifest.json
    triageproof verify evidence/manifest.json --root evidence
    triageproof check record.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .bundle import (
    DEFAULT_REQUIRED,
    BundleError,
    build_bundle,
    load_bundle,
    verify_bundle,
    write_bundle,
)
from .corpus import BY_SLUG, PACK, SKILLS
from .render import build_pack, render_skill
from .stack import (
    best_match,
    canonical_frames,
    cluster,
    dedupe_verdict,
    load_report,
    parse_stack,
    report_from_text,
    signature as compute_signature,
    similarity,
)
from .triage import TriageError, grade, load_record, render_report, scaffold
from .validate import (
    MAX_DESCRIPTION,
    MIN_DONE,
    MIN_PATTERNS,
    MIN_PITFALLS,
    MIN_SIGNALS,
    MIN_STEPS,
    MIN_SUMMARY,
    MIN_WORDS,
    Issue,
    validate_pack,
)

FLOORS = {
    "min_steps": MIN_STEPS,
    "min_signals": MIN_SIGNALS,
    "min_patterns": MIN_PATTERNS,
    "min_pitfalls": MIN_PITFALLS,
    "min_done_when": MIN_DONE,
    "min_summary_chars": MIN_SUMMARY,
    "min_words": MIN_WORDS,
    "max_description_chars": MAX_DESCRIPTION,
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _report(issues: list[Issue], total: int, as_json: bool, title: str) -> int:
    bad = {issue.slug for issue in issues if issue.slug}
    valid = total - len(bad)
    if as_json:
        print(
            json.dumps(
                {
                    "pack": title,
                    "checked": total,
                    "valid": valid,
                    "passed": not issues,
                    "floors": FLOORS,
                    "issues": [{"slug": i.slug, "rule": i.rule, "message": i.message} for i in issues],
                },
                indent=2,
            )
        )
    else:
        print(f"{title}: {valid}/{total} skills valid")
        for issue in issues:
            print(f"  FAIL {issue}")
        if not issues:
            print(
                f"  ok  steps>={MIN_STEPS} signals>={MIN_SIGNALS} patterns>={MIN_PATTERNS} "
                f"pitfalls>={MIN_PITFALLS} words>={MIN_WORDS} refs canonical https"
            )
    return 0 if not issues else 1


def cmd_validate(args: argparse.Namespace) -> int:
    return _report(validate_pack(PACK, SKILLS), len(SKILLS), args.json, PACK["name"])


def cmd_list(args: argparse.Namespace) -> int:
    rows = [
        skill
        for skill in SKILLS
        if (not args.tag or args.tag in skill.tags)
        and (not args.phase or skill.meta_get("phase") == args.phase)
    ]
    if args.json:
        print(
            json.dumps(
                [
                    {"slug": s.slug, "title": s.title, "phase": s.meta_get("phase"), "tags": list(s.tags)}
                    for s in rows
                ],
                indent=2,
            )
        )
        return 0
    for skill in rows:
        print(f"{skill.meta_get('phase'):14s} {skill.slug:40s} {skill.title}")
    print(f"# {len(rows)} skill(s)")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    skill = BY_SLUG.get(args.slug)
    if skill is None:
        print(f"unknown skill: {args.slug}", file=sys.stderr)
        return 2
    text = render_skill(PACK, skill)
    print(text if args.raw else text.split("---\n", 2)[-1].lstrip())
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    terms = [term.lower() for term in args.terms]

    def score(skill) -> int:
        blob = " ".join([skill.slug, skill.title, skill.summary, *skill.tags, *skill.steps]).lower()
        return sum(blob.count(term) for term in terms)

    ranked = sorted(
        ((score(skill), skill) for skill in SKILLS if score(skill)),
        key=lambda pair: (-pair[0], pair[1].slug),
    )[: args.limit]
    if not ranked:
        print("no matches", file=sys.stderr)
        return 1
    for points, skill in ranked:
        print(f"{points:3d}  {skill.slug:40s} {skill.title}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else repo_root()
    written = build_pack(root, PACK, SKILLS)
    print(f"wrote {len(written)} file(s) under {root}")
    return 0


def cmd_signature(args: argparse.Namespace) -> int:
    path = Path(args.stack)
    if not path.is_file():
        print(f"stack file not found: {path}", file=sys.stderr)
        return 2
    frames = parse_stack(path.read_text(encoding="utf-8", errors="replace"))
    if not frames:
        print("no frames recognised in that file", file=sys.stderr)
        return 1
    fingerprint = compute_signature(frames, args.kind, args.depth)
    if args.json:
        print(
            json.dumps(
                {
                    "file": str(path),
                    "kind": args.kind,
                    "depth": args.depth,
                    "signature": fingerprint,
                    "frames": [frame.as_dict() for frame in canonical_frames(frames, args.depth)],
                },
                indent=2,
            )
        )
        return 0
    print(f"signature {fingerprint}  ({len(frames)} frame(s) parsed, depth {args.depth})")
    for index, frame in enumerate(canonical_frames(frames, args.depth), start=1):
        print(f"  {index}. {frame.canonical()}")
    return 0


def cmd_similar(args: argparse.Namespace) -> int:
    left = Path(args.left)
    right = Path(args.right)
    for path in (left, right):
        if not path.is_file():
            print(f"stack file not found: {path}", file=sys.stderr)
            return 2
    a = load_report(left, args.depth, args.kind)
    b = load_report(right, args.depth, args.kind)
    score = similarity(a.frames, b.frames, args.depth, args.kind, args.kind)
    verdict = dedupe_verdict(score, args.threshold, args.strong)
    if args.json:
        print(
            json.dumps(
                {
                    "left": a.name,
                    "right": b.name,
                    "left_signature": a.fingerprint,
                    "right_signature": b.fingerprint,
                    "similarity": round(score, 4),
                    "verdict": verdict,
                },
                indent=2,
            )
        )
    else:
        print(f"{a.name} vs {b.name}: {score:.3f} -> {verdict}")
        print(f"  {a.fingerprint}  {', '.join(a.summary())}")
        print(f"  {b.fingerprint}  {', '.join(b.summary())}")
    return 0


def cmd_dedupe(args: argparse.Namespace) -> int:
    candidate_path = Path(args.candidate)
    if not candidate_path.is_file():
        print(f"stack file not found: {candidate_path}", file=sys.stderr)
        return 2
    candidate = load_report(candidate_path, args.depth, args.kind)
    known = []
    for pattern in args.known:
        for path in sorted(Path().glob(pattern)) if any(ch in pattern for ch in "*?[") else [Path(pattern)]:
            if path.is_file():
                known.append(load_report(path, args.depth, args.kind))
    if not known:
        print("no existing reports to compare against", file=sys.stderr)
        return 2

    score, match = best_match(candidate, known, args.threshold, args.depth)
    verdict = dedupe_verdict(score, args.threshold, args.strong)
    if args.json:
        print(
            json.dumps(
                {
                    "candidate": candidate.name,
                    "signature": candidate.fingerprint,
                    "best_match": match.name if match else None,
                    "best_signature": match.fingerprint if match else None,
                    "similarity": round(score, 4),
                    "verdict": verdict,
                    "compared": len(known),
                },
                indent=2,
            )
        )
    else:
        print(f"{candidate.name} ({candidate.fingerprint}): {verdict}  similarity {score:.3f}")
        if match is not None:
            print(f"  closest: {match.name} ({match.fingerprint})")
        print(f"  compared against {len(known)} report(s)")
    return 0 if verdict == "new" else 1


def cmd_cluster(args: argparse.Namespace) -> int:
    reports = []
    for pattern in args.paths:
        paths = sorted(Path().glob(pattern)) if any(ch in pattern for ch in "*?[") else [Path(pattern)]
        for path in paths:
            if path.is_file():
                reports.append(load_report(path, args.depth, args.kind))
    if not reports:
        print("no stack files found", file=sys.stderr)
        return 2

    groups = cluster(reports, args.threshold, args.depth)
    if args.json:
        print(
            json.dumps(
                [
                    {
                        "fingerprint": group.fingerprint,
                        "size": group.size,
                        "members": [member.name for member in group.members],
                    }
                    for group in groups
                ],
                indent=2,
            )
        )
    else:
        for group in groups:
            print(f"{group.fingerprint}  {group.size} report(s)")
            for member in group.members:
                print(f"    {member.name}")
        print(f"# {len(reports)} report(s) in {len(groups)} cluster(s)")
    return 0


def cmd_bundle(args: argparse.Namespace) -> int:
    root = Path(args.directory)
    required = [item for item in (args.require or "").split(",") if item] or list(DEFAULT_REQUIRED)
    try:
        bundle = build_bundle(root, required)
    except BundleError as exc:
        print(f"cannot build bundle: {exc}", file=sys.stderr)
        return 2
    if args.write:
        write_bundle(bundle, Path(args.write))
        print(f"bundled {bundle['count']} file(s) into {args.write}")
    else:
        print(json.dumps(bundle, indent=2))
    if bundle["missing"]:
        print("missing required kind(s): " + ", ".join(bundle["missing"]), file=sys.stderr)
        return 1
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    try:
        bundle = load_bundle(Path(args.manifest))
    except BundleError as exc:
        print(f"cannot read bundle: {exc}", file=sys.stderr)
        return 2
    problems = verify_bundle(bundle, Path(args.root), Path(args.manifest))
    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        return 1
    print(f"ok  {bundle['count']} file(s) match {args.manifest}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    try:
        record = load_record(Path(args.record))
    except TriageError as exc:
        print(f"cannot read record: {exc}", file=sys.stderr)
        return 2
    report = grade(record, Path(args.root) if args.root else None)
    if args.json:
        print(json.dumps(report.as_dict(), indent=2))
    else:
        verdict = "submittable" if report.submittable else "NOT submittable"
        print(f"{report.record_id}: grade {report.grade} ({report.score}/100) {verdict}")
        if report.signature:
            print(f"  signature {report.signature}")
        for finding in report.findings:
            print(f"  {finding.severity:8s} {finding.rule}: {finding.message}")
            if finding.hint and args.verbose:
                print(f"           -> {finding.hint}")
    return 0 if report.submittable else 1


def cmd_scaffold(args: argparse.Namespace) -> int:
    record = scaffold(args.title, args.id)
    text = json.dumps(record, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
    else:
        print(text, end="")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    try:
        record = load_record(Path(args.record))
    except TriageError as exc:
        print(f"cannot read record: {exc}", file=sys.stderr)
        return 2
    report = grade(record, Path(args.root) if args.root else None)
    text = render_report(record, report)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
    else:
        print(text, end="")
    return 0 if report.submittable else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PACK["name"], description=PACK["description"])
    parser.add_argument("--version", action="version", version=f"{PACK['name']} {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="run every corpus rule")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("list", help="list skills")
    p.add_argument("--tag", default=None)
    p.add_argument("--phase", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="print one SKILL.md")
    p.add_argument("slug")
    p.add_argument("--raw", action="store_true")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("search", help="rank skills by keyword")
    p.add_argument("terms", nargs="+")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("build", help="regenerate skills/, pack.json and results/")
    p.add_argument("--root", default=None)
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("signature", help="canonical signature for a stack file")
    p.add_argument("stack")
    p.add_argument("--kind", default="")
    p.add_argument("--depth", type=int, default=5)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_signature)

    p = sub.add_parser("similar", help="compare two stack files")
    p.add_argument("left")
    p.add_argument("right")
    p.add_argument("--depth", type=int, default=5)
    p.add_argument("--kind", default="")
    p.add_argument("--threshold", type=float, default=0.6)
    p.add_argument("--strong", type=float, default=0.85)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_similar)

    p = sub.add_parser("dedupe", help="compare a new crash against known reports")
    p.add_argument("candidate")
    p.add_argument("known", nargs="+")
    p.add_argument("--depth", type=int, default=5)
    p.add_argument("--kind", default="")
    p.add_argument("--threshold", type=float, default=0.6)
    p.add_argument("--strong", type=float, default=0.85)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_dedupe)

    p = sub.add_parser("cluster", help="group stack files into clusters")
    p.add_argument("paths", nargs="+")
    p.add_argument("--depth", type=int, default=5)
    p.add_argument("--kind", default="")
    p.add_argument("--threshold", type=float, default=0.6)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_cluster)

    p = sub.add_parser("bundle", help="hash an evidence directory into a manifest")
    p.add_argument("directory")
    p.add_argument("--write", default=None)
    p.add_argument("--require", default="")
    p.set_defaults(func=cmd_bundle)

    p = sub.add_parser("verify", help="re-hash a bundle and report drift")
    p.add_argument("manifest")
    p.add_argument("--root", default=".")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("check", help="grade a triage record")
    p.add_argument("record")
    p.add_argument("--root", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("scaffold", help="emit an empty triage record")
    p.add_argument("title")
    p.add_argument("--id", default="new-crash")
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_scaffold)

    p = sub.add_parser("report", help="render a triage report")
    p.add_argument("record")
    p.add_argument("--root", default=None)
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
