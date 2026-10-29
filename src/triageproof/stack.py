"""Crash stack parsing, canonicalisation, signatures and clustering.

Two reports of the same bug almost never have the same text: addresses move with
ASLR, paths differ between build machines, thread counts change, and the allocator
frames shift. A signature is only useful if it is stable across all of that, so
canonicalisation strips the volatile parts before anything is hashed.

Supported input shapes, tried in order per line:

    #0  0x000055d1 in parse_header (buf=0x0) at /src/app/parse.c:88   (gdb, asan)
    File "/app/handlers/orders.py", line 42, in get_order              (python)
    liborders.so!parse_header+0x2a                                     (minidump)
    frame #0: 0x0000000100003f2a app`parse_header at parse.c:88        (lldb)

Unrecognised lines are ignored, so a crash report with preamble text parses
cleanly instead of failing.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

MAX_FRAMES = 128

# Frames that appear in nearly every crash and say nothing about which bug it is.
NOISE_PATTERNS = (
    r"^_?(start|start_thread|clone|clone3|__clone)$",
    r"^(abort|raise|__GI_raise|__GI_abort|__assert_fail|__stack_chk_fail)$",
    r"^(malloc|calloc|realloc|free|operator new|operator delete)",
    r"^(__libc_|libc_start_main|__libc_start_call_main)",
    r"^(std::terminate|__cxa_throw|_Unwind_Resume)",
    r"^(pthread_|__pthread_)",
)
NOISE_RE = [re.compile(pattern) for pattern in NOISE_PATTERNS]

GDB_RE = re.compile(
    r"^\s*#(?P<index>\d+)\s+(?:(?:0x[0-9a-fA-F]+)\s+in\s+)?"
    r"(?P<func>[A-Za-z_~][\w:<>~,$.\-]*)"
    r"(?:\s*\([^)]*\))?"
    r"(?:\s+(?:at|from)\s+(?P<loc>[^\s:]+)(?::(?P<line>\d+))?)?"
)
PY_RE = re.compile(
    r'^\s*File "(?P<loc>[^"]+)",\s+line\s+(?P<line>\d+),\s+in\s+(?P<func>[\w<>.]+)'
)
MODULE_RE = re.compile(
    r"^\s*(?:#\d+\s+)?(?P<mod>[A-Za-z0-9_.\-]+)!(?P<func>[A-Za-z_~][\w:<>~$@.\-]*)"
    r"\+0x[0-9a-fA-F]+"
)
LLDB_RE = re.compile(
    r"^\s*frame\s+#(?P<index>\d+):\s*(?:0x[0-9a-fA-F]+)?\s*"
    r"(?P<mod>[A-Za-z0-9_.\-]+)?`(?P<func>[A-Za-z_~][\w:<>~$.\-]*)"
    r"(?:\s+at\s+(?P<loc>[^\s:]+):(?P<line>\d+))?"
)

ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]+")
OFFSET_RE = re.compile(r"\+0x[0-9a-fA-F]+")
TEMPLATE_RE = re.compile(r"<[^<>]*>")
THREAD_SUFFIX_RE = re.compile(r"^(?P<func>.+?)\s*\((?:Thread|TID)\s*[0-9a-fA-Fx]+\)$")


@dataclass(frozen=True)
class Frame:
    """One canonical stack frame."""

    function: str
    module: str = ""
    file: str = ""
    line: int | None = None

    def canonical(self) -> str:
        """Stable text form: no address, no offset, basename only, no line."""
        base = self.file.rsplit("/", 1)[-1].rsplit("\\", 1)[-1] if self.file else ""
        parts = [part for part in (self.module, self.function) if part]
        text = "!".join(parts) if len(parts) == 2 else self.function
        return f"{text}@{base}" if base else text

    def key(self) -> str:
        """Module-free, path-free key: the only thing every tool agrees on.

        gdb records paths, lldb and minidumps record modules, and a minidump of
        a stripped build records neither. Only the function name survives every
        capture path, so it is what a signature may hash.
        """
        return self.function

    def as_dict(self) -> dict[str, object]:
        return {
            "function": self.function,
            "module": self.module,
            "file": self.file,
            "line": self.line,
            "canonical": self.canonical(),
        }


def _fold_template_spaces(line: str) -> str:
    """Remove spaces inside template arguments so ``std::map<K, V>`` is one token.

    Depth counting rather than a regex, because template arguments nest:
    ``std::vector<int, std::allocator<int>>`` has a space the inner match would
    cut in half.
    """
    out: list[str] = []
    depth = 0
    for char in line:
        if char == "<":
            depth += 1
        elif char == ">" and depth:
            depth -= 1
        if depth and char == " ":
            continue
        out.append(char)
    return "".join(out)


def _strip_template_args(text: str) -> str:
    """Collapse every balanced template span to ``<>``.

    ``std::vector<int, std::allocator<int>>::push_back`` and
    ``std::vector<char>::push_back`` are the same code path, so the arguments
    must not reach a signature. Unbalanced input (an ``operator<``) is returned
    untouched rather than swallowing the rest of the frame.
    """
    out: list[str] = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char != "<":
            out.append(char)
            index += 1
            continue
        depth = 0
        cursor = index
        while cursor < length:
            if text[cursor] == "<":
                depth += 1
            elif text[cursor] == ">":
                depth -= 1
                if depth == 0:
                    break
            cursor += 1
        if depth != 0:
            out.append(text[index:])
            return "".join(out)
        out.append("<>")
        index = cursor + 1
    return "".join(out)


def _clean_function(text: str) -> str:
    value = OFFSET_RE.sub("", text.strip())
    value = ADDRESS_RE.sub("", value).strip(" +")
    value = THREAD_SUFFIX_RE.sub(lambda m: m.group("func"), value)
    value = _strip_template_args(value)
    return value.strip()


def _basename(path: str) -> str:
    return path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]


def parse_line(line: str) -> Frame | None:
    """Parse one frame line in any supported format."""
    line = _fold_template_spaces(line)

    match = PY_RE.match(line)
    if match:
        return Frame(
            function=_clean_function(match.group("func")),
            file=match.group("loc"),
            line=int(match.group("line")),
        )

    match = LLDB_RE.match(line)
    if match:
        return Frame(
            function=_clean_function(match.group("func")),
            module=match.group("mod") or "",
            file=match.group("loc") or "",
            line=int(match.group("line")) if match.group("line") else None,
        )

    match = MODULE_RE.match(line)
    if match:
        return Frame(
            function=_clean_function(match.group("func")),
            module=match.group("mod"),
        )

    match = GDB_RE.match(line)
    if match:
        return Frame(
            function=_clean_function(match.group("func")),
            file=match.group("loc") or "",
            line=int(match.group("line")) if match.group("line") else None,
        )

    return None


def parse_stack(text: str) -> list[Frame]:
    """Every frame we can recognise, in order, capped at ``MAX_FRAMES``."""
    frames: list[Frame] = []
    for line in text.splitlines():
        frame = parse_line(line)
        if frame is not None and frame.function:
            frames.append(frame)
        if len(frames) >= MAX_FRAMES:
            break
    return frames


def is_noise(frame: Frame) -> bool:
    return any(pattern.search(frame.function) for pattern in NOISE_RE)


def canonical_frames(
    frames: Sequence[Frame], depth: int = 5, keep_noise: bool = False
) -> list[Frame]:
    """Drop noise frames and keep the top ``depth`` of what is left."""
    kept = [frame for frame in frames if keep_noise or not is_noise(frame)]
    return list(kept[:depth])


def canonical_text(frames: Sequence[Frame], crash_kind: str = "", depth: int = 5) -> str:
    """Human-facing canonical stack: module-qualified where a module is known."""
    top = canonical_frames(frames, depth=depth)
    lines = [frame.canonical() for frame in top]
    return "\n".join(([f"kind:{crash_kind}"] if crash_kind else []) + lines)


def signature_text(frames: Sequence[Frame], crash_kind: str = "", depth: int = 5) -> str:
    """The exact text that gets hashed: function names only, so tools agree.

    A signature is the machine key used for bucketing, so it must be the same
    for one bug no matter which tool captured it. gdb records paths and no
    module, lldb and minidumps record a module, and a minidump of a stripped
    build records neither. Any of those in the hash would put one crash into
    two buckets — precisely the failure exact bucketing exists to prevent.

    Paths and modules still reach the human-facing text and still separate
    near-identical functions in :func:`similarity`, which compares frames
    pairwise and can afford a tiebreak a hash cannot.
    """
    top = canonical_frames(frames, depth=depth)
    lines = [frame.key() for frame in top]
    return "\n".join(([f"kind:{crash_kind}"] if crash_kind else []) + lines)


def signature(
    frames: Sequence[Frame], crash_kind: str = "", depth: int = 5
) -> str:
    """A stable 16-hex signature over the canonical top frames."""
    text = signature_text(frames, crash_kind=crash_kind, depth=depth)
    if not text.strip():
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def signature_from_text(text: str, crash_kind: str = "", depth: int = 5) -> str:
    return signature(parse_stack(text), crash_kind=crash_kind, depth=depth)


def _frames_match(one: Frame, other: Frame) -> bool:
    """Same function, and the files agree whenever both reports carry one."""
    if one.function != other.function:
        return False
    left = _basename(one.file) if one.file else ""
    right = _basename(other.file) if other.file else ""
    return not left or not right or left == right


def similarity(
    left: Sequence[Frame],
    right: Sequence[Frame],
    depth: int = 5,
    left_kind: str = "",
    right_kind: str = "",
) -> float:
    """Dice overlap of the top frames, tolerant of a missing module or path.

    Reports of one bug arrive from different tools: gdb has paths and no module,
    minidumps have modules and no paths, and addresses always differ. Frames are
    therefore matched on function name, with the file basename required to agree
    when both sides have one. Two different sanitizer classes are different bugs,
    so a kind mismatch returns 0.0 outright.
    """
    if left_kind and right_kind and left_kind != right_kind:
        return 0.0

    a = canonical_frames(left, depth=depth)
    b = canonical_frames(right, depth=depth)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0

    used: set[int] = set()
    matched = 0
    for frame in a:
        for index, other in enumerate(b):
            if index in used:
                continue
            if _frames_match(frame, other):
                used.add(index)
                matched += 1
                break
    return (2 * matched) / (len(a) + len(b))


@dataclass(frozen=True)
class Report:
    """A crash report reduced to what triage needs."""

    name: str
    fingerprint: str
    frames: list[Frame]
    crash_kind: str = ""

    def summary(self, depth: int = 3) -> list[str]:
        return [frame.canonical() for frame in canonical_frames(self.frames, depth=depth)]


def report_from_text(name: str, text: str, crash_kind: str = "", depth: int = 5) -> Report:
    frames = parse_stack(text)
    return Report(name=name, fingerprint=signature(frames, crash_kind, depth), frames=frames, crash_kind=crash_kind)


def load_report(path: Path, depth: int = 5, crash_kind: str = "") -> Report:
    """Load a saved stack. ``crash_kind`` must match the kind used elsewhere.

    A report loaded with an empty kind cannot be separated from a report of a
    different sanitizer class, so callers that compare reports must pass the
    same kind they used to sign them.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError as exc:
        raise ValueError(f"crash report not found: {path}") from exc
    return report_from_text(path.name, text, crash_kind=crash_kind, depth=depth)


@dataclass
class Cluster:
    fingerprint: str
    members: list[Report]

    @property
    def size(self) -> int:
        return len(self.members)


def cluster(reports: Iterable[Report], threshold: float = 0.6, depth: int = 5) -> list[Cluster]:
    """Group reports whose canonical frames overlap at least ``threshold``.

    Grouping is by similarity rather than by exact signature so that a report
    whose frames shifted by one (a partial inlining, an extra helper) still
    lands with its bug. Exact signatures remain the cheap first pass, and the
    group's fingerprint is the head report's, computed at the same depth and
    kind that grouping used.
    """
    clusters: list[Cluster] = []
    for report in reports:
        placed = False
        for group in clusters:
            head = group.members[0]
            if (
                similarity(head.frames, report.frames, depth, head.crash_kind, report.crash_kind)
                >= threshold
            ):
                group.members.append(report)
                placed = True
                break
        if not placed:
            clusters.append(
                Cluster(signature(report.frames, report.crash_kind, depth), [report])
            )
    clusters.sort(key=lambda group: (-group.size, group.fingerprint))
    return clusters


def best_match(
    candidate: Report, existing: Iterable[Report], threshold: float = 0.6, depth: int = 5
) -> tuple[float, Report | None]:
    """Highest similarity against existing reports, with the matching report."""
    best_score = 0.0
    best: Report | None = None
    for report in existing:
        score = similarity(
            candidate.frames, report.frames, depth, candidate.crash_kind, report.crash_kind
        )
        if score > best_score:
            best_score, best = score, report
    return best_score, best


def dedupe_verdict(score: float, threshold: float = 0.6, strong: float = 0.85) -> str:
    """duplicate above ``strong``, probable above ``threshold``, else new."""
    if score >= strong:
        return "duplicate"
    if score >= threshold:
        return "probable"
    return "new"
