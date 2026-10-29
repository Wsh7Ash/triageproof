"""Stack canonicalisation, similarity, clustering, bundles and grading."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from triageproof.bundle import (  # noqa: E402
    DEFAULT_REQUIRED,
    BundleError,
    build_bundle,
    infer_kind,
    load_bundle,
    sha256_file,
    verify_bundle,
    write_bundle,
)
from triageproof.stack import (  # noqa: E402
    Frame,
    canonical_frames,
    cluster,
    dedupe_verdict,
    is_noise,
    load_report,
    parse_line,
    parse_stack,
    report_from_text,
    signature,
    signature_text,
    similarity,
)
from triageproof.triage import grade, load_record  # noqa: E402

EXAMPLES = ROOT / "examples"

GDB = """\
Program received signal SIGSEGV, Segmentation fault.
#0  0x000055d1a2f13f2a in parse_header (buf=0x0, len=512) at /build/release/src/parse.c:88
#1  0x000055d1a2f14a11 in handle_request (req=0x7fff) at /build/release/src/handler.c:142
#2  0x000055d1a2f16120 in serve_forever () at /build/release/src/server.c:57
#3  0x00007f2c88a29f8a in start_thread (arg=0x7f2c) at pthread_create.c:442
"""

GDB_SAME_BUG_OTHER_BUILD = """\
#0  0x00007f00deadbeef in parse_header (buf=0x0, len=512) at /home/dev/checkout/src/parse.c:88
#1  0x00007f00deadc0de in handle_request (req=0x9) at /home/dev/checkout/src/handler.c:142
#2  0x00007f00dead1234 in serve_forever () at /home/dev/checkout/src/server.c:57
"""

LLDB = """\
* thread #4, stop reason = EXC_BAD_ACCESS (code=1, address=0x0)
    frame #0: 0x0000000100003f2a app`parse_header at parse.c:88
    frame #1: 0x0000000100003faa app`handle_request at handler.c:142
    frame #2: 0x00000001000040b0 app`serve_forever at server.c:57
"""

MINIDUMP = """\
libapp.so!parse_header+0x2a
libapp.so!handle_request+0x1b
libapp.so!serve_forever+0x70
"""

PYTHON_TRACE = """\
Traceback (most recent call last):
  File "/srv/handlers/orders.py", line 42, in get_order
    total = self.price * qty
  File "/srv/models/order.py", line 88, in price
    return self.unit_price * self.quantity
"""

ASAN = """\
==4411==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x60200000eff0
    #0 0x4f2a1b in tokenize_line /build/release/src/lexer.c:214:9
    #1 0x4f31c7 in lex_source /build/release/src/lexer.c:301:12
    #2 0x4f44a0 in compile_module /build/release/src/compile.c:77:5
"""


# ----------------------------------------------------------------- parsing


def test_gdb_frames_parse_with_file_and_line() -> None:
    frames = parse_stack(GDB)
    assert [frame.function for frame in frames][:3] == [
        "parse_header",
        "handle_request",
        "serve_forever",
    ]
    assert frames[0].file == "/build/release/src/parse.c"
    assert frames[0].line == 88


def test_lldb_frames_parse_with_module() -> None:
    frames = parse_stack(LLDB)
    assert frames[0].function == "parse_header"
    assert frames[0].module == "app"
    assert frames[0].line == 88


def test_minidump_frames_parse() -> None:
    frames = parse_stack(MINIDUMP)
    assert [frame.function for frame in frames] == [
        "parse_header",
        "handle_request",
        "serve_forever",
    ]
    assert frames[0].module == "libapp.so"


def test_python_traceback_parses() -> None:
    frames = parse_stack(PYTHON_TRACE)
    assert frames[0].function == "get_order"
    assert frames[0].file.endswith("orders.py")
    assert frames[0].line == 42


def test_unrecognised_lines_are_ignored_not_fatal() -> None:
    text = "Thread 4 (Thread 0x7f) crashed.\n" + GDB
    assert [frame.function for frame in parse_stack(text)][0] == "parse_header"


def test_template_arguments_are_folded() -> None:
    frame = parse_line("#0  0x1 in std::vector<int, std::allocator<int>>::push_back()")
    assert frame is not None
    assert "<>" in frame.function


def test_thread_suffix_is_stripped() -> None:
    frame = parse_line("#0  0x1 in worker_main (Thread 0x7f2c)")
    assert frame is not None
    assert frame.function == "worker_main"


# ---------------------------------------------------------------- signatures


def test_noise_frames_are_dropped() -> None:
    frames = parse_stack(GDB)
    assert is_noise(frames[-1])  # start_thread
    kept = canonical_frames(frames, depth=10)
    assert "start_thread" not in [frame.function for frame in kept]


def test_allocator_frames_are_noise() -> None:
    frames = parse_stack("#0 0x1 in malloc (n=16)\n#1 0x2 in parse_header ()")
    assert is_noise(frames[0])
    assert [frame.function for frame in canonical_frames(frames)] == ["parse_header"]


def test_signature_is_stable_across_addresses_and_build_paths() -> None:
    one = signature(parse_stack(GDB), "segv", 5)
    two = signature(parse_stack(GDB_SAME_BUG_OTHER_BUILD), "segv", 5)
    assert one == two
    assert one


def test_signature_is_stable_across_capture_tools_at_a_shared_depth() -> None:
    """gdb, lldb and a minidump of one bug must share a key at a common depth.

    A minidump of a stripped build records fewer frames than gdb, so depth has
    to be chosen to what every report can supply before signatures can be
    compared. At depth 3 all three agree.
    """
    keys = {signature(parse_stack(text), "segv", 3) for text in (GDB, LLDB, MINIDUMP)}
    assert len(keys) == 1


def test_signature_does_not_contain_a_module_or_path() -> None:
    assert "!" not in signature_text(parse_stack(MINIDUMP))
    assert ".c" not in signature_text(parse_stack(GDB))


def test_signature_ignores_line_numbers() -> None:
    moved = GDB.replace("parse.c:88", "parse.c:131")
    assert signature(parse_stack(GDB), "segv") == signature(parse_stack(moved), "segv")


def test_signature_separates_crash_kinds() -> None:
    frames = parse_stack(GDB)
    assert signature(frames, "segv") != signature(frames, "heap-buffer-overflow")


def test_signature_respects_depth() -> None:
    frames = parse_stack(GDB + "#3 0x3 in http_dispatch () at http.c:204\n")
    assert signature(frames, "segv", 2) != signature(frames, "segv", 4)


def test_empty_stack_has_no_signature() -> None:
    assert signature([]) == ""


# ---------------------------------------------------------------- similarity


def test_similarity_is_one_for_the_same_bug_from_different_tools() -> None:
    assert similarity(parse_stack(GDB), parse_stack(LLDB), 5, "segv", "segv") == pytest.approx(1.0)


def test_similarity_is_symmetric() -> None:
    left, right = parse_stack(GDB), parse_stack(ASAN)
    assert similarity(left, right) == pytest.approx(similarity(right, left))


def test_similarity_is_zero_across_crash_kinds() -> None:
    assert similarity(parse_stack(GDB), parse_stack(GDB), 5, "segv", "heap-buffer-overflow") == 0.0


def test_similarity_matches_by_function_not_by_module() -> None:
    one = [Frame("parse_header", module="libapp.so")]
    two = [Frame("parse_header", file="/src/parse.c")]
    assert similarity(one, two) == pytest.approx(1.0)


def test_similarity_penalises_a_different_file_basename() -> None:
    one = [Frame("parse_header", file="/a/parse.c")]
    two = [Frame("parse_header", file="/b/render.c")]
    assert similarity(one, two) == 0.0


def test_similarity_of_partial_overlap_is_between_zero_and_one() -> None:
    score = similarity(parse_stack(GDB), parse_stack(ASAN), 5)
    assert 0.0 <= score < 0.5


# ---------------------------------------------------------------- clustering


def test_cluster_groups_the_same_bug_reported_by_two_tools() -> None:
    reports = [
        report_from_text("gdb.txt", GDB, "segv", 5),
        report_from_text("lldb.txt", LLDB, "segv", 5),
        report_from_text("asan.txt", ASAN, "heap-buffer-overflow", 5),
    ]
    groups = cluster(reports, threshold=0.6, depth=5)
    assert [group.size for group in groups] == [2, 1]
    assert groups[0].fingerprint == reports[0].fingerprint


def test_cluster_fingerprint_matches_the_signature_helper() -> None:
    report = report_from_text("gdb.txt", GDB, "segv", 5)
    groups = cluster([report], depth=5)
    assert groups[0].fingerprint == signature(report.frames, "segv", 5)
    assert groups[0].fingerprint == report.fingerprint


def test_cluster_of_a_lone_report_is_a_singleton() -> None:
    groups = cluster([report_from_text("a.txt", ASAN, "asan", 5)], depth=5)
    assert len(groups) == 1 and groups[0].size == 1


def test_dedupe_verdict_boundaries() -> None:
    assert dedupe_verdict(1.0) == "duplicate"
    assert dedupe_verdict(0.85) == "duplicate"
    assert dedupe_verdict(0.8499) == "probable"
    assert dedupe_verdict(0.6) == "probable"
    assert dedupe_verdict(0.5999) == "new"
    assert dedupe_verdict(0.0) == "new"


def test_load_report_reads_the_example_stack() -> None:
    report = load_report(EXAMPLES / "crashes" / "gdb-report.txt", 5, "segv")
    assert report.fingerprint == "a540614c71147b9d"


# ------------------------------------------------------------------- bundles


def test_infer_kind_uses_the_first_path_segment() -> None:
    assert infer_kind("crash/crash.log") == "crash"
    assert infer_kind("notes/readme.txt") == "other"


def test_bundle_records_every_file_with_a_digest(tmp_path: Path) -> None:
    for name, body in (("crash/a.log", "segv"), ("stack/b.txt", "#0 x"), ("repro/c.sh", "sh")):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    bundle = build_bundle(tmp_path)
    assert bundle["count"] == 3
    assert bundle["kinds"] == ["crash", "repro", "stack"]
    assert all(len(entry["sha256"]) == 64 for entry in bundle["files"])


def test_bundle_reports_missing_required_kinds(tmp_path: Path) -> None:
    (tmp_path / "crash").mkdir()
    (tmp_path / "crash" / "a.log").write_text("segv", encoding="utf-8")
    bundle = build_bundle(tmp_path)
    assert bundle["missing"] == [kind for kind in DEFAULT_REQUIRED if kind != "crash"]


def test_bundle_rejects_an_empty_directory(tmp_path: Path) -> None:
    with pytest.raises(BundleError):
        build_bundle(tmp_path)


def _complete_evidence(tmp_path: Path) -> None:
    """The four kinds a triage bundle must carry."""
    for kind in DEFAULT_REQUIRED:
        (tmp_path / kind).mkdir()
        (tmp_path / kind / "a.txt").write_text(kind, encoding="utf-8")


def test_verify_accepts_an_untouched_bundle(tmp_path: Path) -> None:
    _complete_evidence(tmp_path)
    bundle = build_bundle(tmp_path)
    write_bundle(bundle, tmp_path / "bundle.json")
    loaded = load_bundle(tmp_path / "bundle.json")
    assert verify_bundle(loaded, tmp_path, tmp_path / "bundle.json") == []


def test_verify_detects_an_edited_artifact(tmp_path: Path) -> None:
    (tmp_path / "crash").mkdir()
    target = tmp_path / "crash" / "a.log"
    target.write_text("segv", encoding="utf-8")
    bundle = build_bundle(tmp_path)
    target.write_text("segv edited", encoding="utf-8")
    problems = verify_bundle(bundle, tmp_path)
    assert any("digest changed" in problem for problem in problems)


def test_verify_detects_an_unrecorded_file(tmp_path: Path) -> None:
    (tmp_path / "crash").mkdir()
    (tmp_path / "crash" / "a.log").write_text("segv", encoding="utf-8")
    bundle = build_bundle(tmp_path)
    (tmp_path / "extra.txt").write_text("smuggled in", encoding="utf-8")
    problems = verify_bundle(bundle, tmp_path)
    assert any("unrecorded file: extra.txt" in problem for problem in problems)


def test_verify_does_not_flag_the_manifest_itself(tmp_path: Path) -> None:
    _complete_evidence(tmp_path)
    write_bundle(build_bundle(tmp_path), tmp_path / "manifest.json")
    loaded = load_bundle(tmp_path / "manifest.json")
    assert verify_bundle(loaded, tmp_path, tmp_path / "manifest.json") == []


def test_load_bundle_rejects_a_foreign_schema(tmp_path: Path) -> None:
    path = tmp_path / "bundle.json"
    path.write_text(json.dumps({"schema": "other/v9"}), encoding="utf-8")
    with pytest.raises(BundleError):
        load_bundle(path)


def test_sha256_file_matches_a_known_vector(tmp_path: Path) -> None:
    path = tmp_path / "abc.txt"
    path.write_bytes(b"abc")
    assert sha256_file(path) == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


# ------------------------------------------------------------------ grading


def example_record() -> dict:
    return load_record(EXAMPLES / "record.json")


def test_example_record_is_submittable() -> None:
    report = grade(example_record(), EXAMPLES)
    assert report.grade == "A"
    assert report.score == 100
    assert report.submittable
    assert report.signature == "a540614c71147b9d"


def test_example_bundle_verifies() -> None:
    bundle = load_bundle(EXAMPLES / "evidence" / "manifest.json")
    root = EXAMPLES / "evidence"
    assert verify_bundle(bundle, root, root / "manifest.json") == []


def test_missing_version_blocks(tmp_path: Path) -> None:
    record = example_record()
    record["target"]["version"] = ""
    report = grade(record, EXAMPLES)
    assert not report.submittable
    assert "version" in {finding.rule for finding in report.blocking}


def test_signature_that_does_not_reproduce_blocks() -> None:
    record = example_record()
    record["signature"] = "deadbeefdeadbeef"
    report = grade(record, EXAMPLES)
    assert "signature-mismatch" in {finding.rule for finding in report.blocking}


def test_absent_stack_file_blocks(tmp_path: Path) -> None:
    record = example_record()
    record["crash"]["stack_file"] = "evidence/stack/missing.txt"
    report = grade(record, EXAMPLES)
    assert "stack-exists" in {finding.rule for finding in report.blocking}


def test_unchecked_dedupe_blocks() -> None:
    record = example_record()
    record["dedupe"]["checked"] = False
    report = grade(record, EXAMPLES)
    assert "dedupe-checked" in {finding.rule for finding in report.blocking}


def test_duplicate_verdict_without_a_target_blocks() -> None:
    record = example_record()
    record["dedupe"] = {"checked": True, "against": [], "verdict": "duplicate"}
    report = grade(record, EXAMPLES)
    assert "dedupe-evidence" in {finding.rule for finding in report.blocking}


def test_tampered_evidence_blocks() -> None:
    record = example_record()
    record["evidence"][0]["sha256"] = "0" * 64
    report = grade(record, EXAMPLES)
    assert "evidence-drift" in {finding.rule for finding in report.blocking}


def test_wrong_schema_blocks() -> None:
    record = example_record()
    record["schema"] = "something/else"
    assert not grade(record, EXAMPLES).submittable


def test_unknown_verdict_is_major_not_blocking() -> None:
    record = example_record()
    record["dedupe"]["verdict"] = "maybe"
    report = grade(record, EXAMPLES)
    assert report.submittable
    assert "dedupe-verdict" in {finding.rule for finding in report.findings}


def test_grade_without_a_root_skips_file_checks() -> None:
    record = example_record()
    record["evidence"] = [{"kind": "crash", "ref": "nowhere.log"}]
    assert grade(record, None).submittable
    assert not grade(record, EXAMPLES).submittable
