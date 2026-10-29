"""Triage record rules, grading and report rendering.

A triage record is the claim that a crash has been understood: that it has a
stable signature, a reproduction, a dedupe check against what is already known,
a root cause, and an evidence bundle that still matches. The rules below check
exactly those, and recompute the signature from the stack file when one is
given — a typed signature that does not match its own stack is the most common
way a duplicate slips through.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .bundle import BundleError, sha256_file
from .stack import parse_stack, signature as compute_signature

SCHEMA = "triageproof/v1"
SEVERITIES = ("low", "medium", "high", "critical")
REACHABILITY = ("pre-auth", "authenticated", "local", "unknown")
VERDICTS = ("new", "probable", "duplicate")
STATUSES = ("triaged", "needs-info", "duplicate", "invalid")

BLOCKING = "blocking"
MAJOR = "major"
MINOR = "minor"
PENALTY = {BLOCKING: 25, MAJOR: 10, MINOR: 3}


class TriageError(RuntimeError):
    """Raised when a triage record cannot be read."""


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str
    hint: str = ""

    def as_dict(self) -> dict[str, str]:
        return {"rule": self.rule, "severity": self.severity, "message": self.message, "hint": self.hint}


@dataclass
class Report:
    record_id: str
    score: int
    grade: str
    signature: str = ""
    findings: list[Finding] = field(default_factory=list)

    @property
    def blocking(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == BLOCKING]

    @property
    def submittable(self) -> bool:
        return not self.blocking

    def as_dict(self) -> dict[str, Any]:
        return {
            "record": self.record_id,
            "signature": self.signature,
            "score": self.score,
            "grade": self.grade,
            "submittable": self.submittable,
            "counts": {s: len([f for f in self.findings if f.severity == s]) for s in PENALTY},
            "findings": [f.as_dict() for f in self.findings],
        }


def load_record(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TriageError(f"record not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise TriageError(f"record is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise TriageError("record must be a JSON object")
    return data


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _items(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _block(record: dict[str, Any], key: str) -> dict[str, Any]:
    value = record.get(key)
    return value if isinstance(value, dict) else {}


def _resolve(path_text: str, root: Path | None) -> Path:
    path = Path(path_text)
    if root is not None and not path.is_absolute():
        path = root / path
    return path


def grade(record: dict[str, Any], root: Path | None = None) -> Report:
    findings: list[Finding] = []
    computed = ""

    def add(rule: str, severity: str, message: str, hint: str = "") -> None:
        findings.append(Finding(rule, severity, message, hint))

    if _text(record.get("schema")) != SCHEMA:
        add("schema", BLOCKING, f"record schema must be {SCHEMA!r}")

    record_id = _text(record.get("id")) or "unnamed"
    if not _text(record.get("id")):
        add("id", MAJOR, "record has no stable id")

    target = _block(record, "target")
    if not _text(target.get("scope_ref")):
        add("scope-ref", BLOCKING, "target has no scope reference")
    if not _text(target.get("asset")):
        add("asset", MAJOR, "target.asset is missing")
    if not _text(target.get("version")):
        add(
            "version",
            BLOCKING,
            "target.version is missing",
            "A crash without a version cannot be deduped or retested.",
        )
    if not _text(target.get("build_id")) and not _text(target.get("commit")):
        add("build-id", MAJOR, "record names neither build_id nor commit")

    crash = _block(record, "crash")
    kind = _text(crash.get("kind"))
    if not kind:
        add("crash-kind", MAJOR, "crash.kind is missing, so sanitizer classes cannot be separated")
    stack_file = _text(crash.get("stack_file"))
    if not stack_file:
        add(
            "stack-file",
            BLOCKING,
            "crash.stack_file is missing",
            "The signature must come from a saved stack, not from memory.",
        )
    elif root is not None:
        path = _resolve(stack_file, root)
        if not path.is_file():
            add("stack-exists", BLOCKING, f"stack file does not exist: {stack_file}")
        else:
            computed = compute_signature(parse_stack(path.read_text(encoding="utf-8", errors="replace")), kind)
            declared = _text(record.get("signature"))
            if not declared:
                add(
                    "signature",
                    BLOCKING,
                    "record has no signature",
                    f"The stack hashes to {computed}; record that value.",
                )
            elif declared != computed:
                add(
                    "signature-mismatch",
                    BLOCKING,
                    f"declared signature {declared} does not match the stack ({computed})",
                    "A signature that does not reproduce is how duplicates get filed twice.",
                )

    repro = _block(record, "reproduction")
    if not _text(repro.get("command")):
        add("reproduction", BLOCKING, "no reproduction command")
    if not _text(repro.get("rate")):
        add(
            "repro-rate",
            MAJOR,
            "reproduction does not state a success rate",
            "Intermittent crashes need N of M attempts, or they get closed as flaky.",
        )
    if not _text(repro.get("environment")):
        add("repro-environment", MINOR, "reproduction does not name the environment")

    dedupe = _block(record, "dedupe")
    if dedupe.get("checked") is not True:
        add(
            "dedupe-checked",
            BLOCKING,
            "no dedupe check recorded",
            "Search advisories and prior reports, then record what you compared against.",
        )
    verdict = _text(dedupe.get("verdict")).lower()
    if verdict not in VERDICTS:
        add("dedupe-verdict", MAJOR, f"dedupe.verdict must be one of {VERDICTS}")
    elif verdict != "new" and not [item for item in _items(dedupe.get("against")) if _text(item)]:
        add(
            "dedupe-evidence",
            BLOCKING,
            f"verdict is {verdict!r} but nothing is listed under against",
            "Name the report or advisory this was matched to.",
        )

    severity = _block(record, "severity")
    if not _text(severity.get("impact")):
        add("impact", BLOCKING, "severity.impact is missing")
    if _text(severity.get("claim")).lower() not in SEVERITIES:
        add("severity-claim", MINOR, f"severity.claim must be one of {SEVERITIES}")
    if _text(severity.get("reachability")).lower() not in REACHABILITY:
        add("reachability", MAJOR, f"severity.reachability must be one of {REACHABILITY}")

    root_cause = _block(record, "root_cause")
    if not _text(root_cause.get("mechanism")):
        add("root-cause", MAJOR, "root_cause.mechanism is missing")
    line = root_cause.get("line")
    if not isinstance(line, int) or line <= 0:
        add("root-cause-line", MINOR, "root_cause.line must be a positive integer")
    if not _text(root_cause.get("file")):
        add("root-cause-file", MINOR, "root_cause.file is missing")

    evidence = [item for item in _items(record.get("evidence")) if isinstance(item, dict)]
    if not evidence:
        add("evidence", BLOCKING, "no evidence entries")
    for index, item in enumerate(evidence, start=1):
        ref = _text(item.get("ref"))
        if not ref:
            add("evidence-ref", BLOCKING, f"evidence {index} has no ref")
            continue
        digest = _text(item.get("sha256"))
        if digest and (len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower())):
            add("evidence-digest", MAJOR, f"evidence {index} sha256 is not 64 hex characters")
        if root is not None and _text(item.get("kind")) in ("crash", "stack", "log", "repro"):
            path = _resolve(ref, root)
            if not path.is_file():
                add("evidence-missing", BLOCKING, f"evidence file is missing: {ref}")
            elif digest and sha256_file(path) != digest.lower():
                add("evidence-drift", BLOCKING, f"evidence changed since it was hashed: {ref}")

    status = _text(record.get("status")).lower()
    if status not in STATUSES:
        add("status", MINOR, f"status must be one of {STATUSES}")

    if not _text(record.get("reported_at")):
        add("reported-at", MINOR, "reported_at is missing")

    penalty = sum(PENALTY[f.severity] for f in findings)
    score = max(0, 100 - penalty)
    if any(f.severity == BLOCKING for f in findings):
        letter = "D"
    elif score >= 90:
        letter = "A"
    elif score >= 75:
        letter = "B"
    elif score >= 55:
        letter = "C"
    else:
        letter = "D"

    return Report(record_id, score, letter, computed or _text(record.get("signature")), findings)


def scaffold(title: str, record_id: str = "new-crash") -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "id": record_id,
        "title": title,
        "reported_at": "",
        "status": "triaged",
        "target": {"asset": "", "scope_ref": "", "version": "", "build_id": ""},
        "crash": {"kind": "", "signal": "", "stack_file": ""},
        "signature": "",
        "reproduction": {"command": "", "rate": "", "environment": ""},
        "dedupe": {"checked": False, "against": [], "verdict": "new"},
        "severity": {"claim": "medium", "impact": "", "reachability": "unknown"},
        "root_cause": {"file": "", "line": 0, "mechanism": ""},
        "evidence": [],
    }


def render_report(record: dict[str, Any], report: Report) -> str:
    target = _block(record, "target")
    severity = _block(record, "severity")
    crash = _block(record, "crash")
    lines = [
        f"# {_text(record.get('title')) or report.record_id}",
        "",
        f"**Record:** `{report.record_id}`  ",
        f"**Asset:** {_text(target.get('asset'))}  ",
        f"**Scope reference:** {_text(target.get('scope_ref'))}  ",
        f"**Version:** {_text(target.get('version'))} (`{_text(target.get('build_id')) or _text(target.get('commit'))}`)",
        "",
        "## Crash",
        "",
        f"- Kind: {_text(crash.get('kind'))}",
        f"- Signal: {_text(crash.get('signal'))}",
        f"- Stack: `{_text(crash.get('stack_file'))}`",
        f"- Signature: `{report.signature}`",
        "",
        "## Reproduction",
        "",
        "```text",
        _text((record.get("reproduction") or {}).get("command")) or "(none)",
        "```",
        "",
        f"- Rate: {_text((record.get('reproduction') or {}).get('rate'))}",
        f"- Environment: {_text((record.get('reproduction') or {}).get('environment'))}",
        "",
        "## Dedupe",
        "",
        f"- Checked: {'yes' if (record.get('dedupe') or {}).get('checked') is True else 'no'}",
        f"- Verdict: {_text((record.get('dedupe') or {}).get('verdict'))}",
    ]
    for item in _items((record.get("dedupe") or {}).get("against")):
        lines.append(f"- Compared against: {item}")
    lines += [
        "",
        "## Impact",
        "",
        f"- What: {_text(severity.get('impact'))}",
        f"- Reachability: {_text(severity.get('reachability'))}",
        f"- Claimed severity: {_text(severity.get('claim'))}",
        "",
        "## Root cause",
        "",
        f"- `{_text((record.get('root_cause') or {}).get('file'))}:{(record.get('root_cause') or {}).get('line')}` "
        f"— {_text((record.get('root_cause') or {}).get('mechanism'))}",
        "",
        "## Evidence",
        "",
    ]
    for item in _items(record.get("evidence")):
        if isinstance(item, dict):
            lines.append(f"- `{item.get('kind')}` {_text(item.get('ref'))}")
    lines += [
        "",
        "## Triage grade",
        "",
        f"- Grade: **{report.grade}** ({report.score}/100), submittable: "
        f"{'yes' if report.submittable else 'no'}",
    ]
    for finding in report.findings:
        lines.append(f"- `{finding.severity}` {finding.rule}: {finding.message}")
    lines.append("")
    return "\n".join(lines)
