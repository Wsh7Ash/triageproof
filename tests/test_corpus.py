"""Corpus rules, generated artifacts and the CLI surface."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from triageproof.corpus import BY_SLUG, PACK, SKILLS  # noqa: E402
from triageproof.render import build_pack, render_skill, word_count  # noqa: E402
from triageproof.validate import (  # noqa: E402
    MIN_PATTERNS,
    MIN_PITFALLS,
    MIN_SIGNALS,
    MIN_STEPS,
    MIN_WORDS,
    validate_pack,
)

EXAMPLES = ROOT / "examples"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {"PYTHONPATH": str(ROOT / "src"), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, "-m", "triageproof", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=120,
    )


# ---------------------------------------------------------------- corpus shape


def test_pack_declares_fifty_and_delivers_fifty() -> None:
    assert PACK["expected_skills"] == 50
    assert len(SKILLS) == 50


def test_slugs_and_titles_are_unique() -> None:
    assert len({skill.slug for skill in SKILLS}) == 50
    assert len({skill.title.lower() for skill in SKILLS}) == 50


def test_every_skill_passes_every_rule() -> None:
    assert validate_pack(PACK, SKILLS) == []


def test_phases_are_known_and_every_phase_is_represented() -> None:
    expected = {"capture", "canonicalise", "cluster", "dedupe", "grade", "bundle"}
    phases = {skill.meta_get("phase") for skill in SKILLS}
    assert phases == expected
    counts = {phase: 0 for phase in expected}
    for skill in SKILLS:
        counts[skill.meta_get("phase")] += 1
    assert min(counts.values()) >= 6


def test_skill_strength_floors_hold_for_every_skill() -> None:
    for skill in SKILLS:
        assert len(skill.steps) >= MIN_STEPS, skill.slug
        assert len(skill.signals) >= MIN_SIGNALS, skill.slug
        assert len(skill.patterns) >= MIN_PATTERNS, skill.slug
        assert len(skill.pitfalls) >= MIN_PITFALLS, skill.slug
        assert word_count(render_skill(PACK, skill)) >= MIN_WORDS, skill.slug


def test_avoid_when_is_not_a_placeholder() -> None:
    for skill in SKILLS:
        assert len(skill.avoid_when) >= 30, skill.slug
        assert "n/a" not in skill.avoid_when.lower(), skill.slug


def test_every_reference_is_https_and_labelled() -> None:
    for skill in SKILLS:
        for ref in skill.refs:
            assert ref.startswith("[") and "](https://" in ref, (skill.slug, ref)


def test_lookup_index_covers_the_corpus() -> None:
    assert set(BY_SLUG) == {skill.slug for skill in SKILLS}


def test_no_skill_is_a_copy_of_another() -> None:
    summaries = [skill.summary for skill in SKILLS]
    assert len(set(summaries)) == 50


# ----------------------------------------------------------- generated files


def test_committed_skills_match_a_fresh_render() -> None:
    """The checked-in corpus must regenerate byte-identically."""
    for skill in SKILLS:
        path = ROOT / "skills" / skill.slug / "SKILL.md"
        assert path.is_file(), f"missing generated file for {skill.slug}"
        assert path.read_text(encoding="utf-8") == render_skill(PACK, skill), skill.slug


def test_pack_json_lists_fifty_skills_with_digests() -> None:
    manifest = json.loads((ROOT / "pack.json").read_text(encoding="utf-8"))
    assert manifest["skill_count"] == 50
    assert len(manifest["skills"]) == 50
    assert all(len(entry["sha256"]) == 64 for entry in manifest["skills"])
    assert {entry["slug"] for entry in manifest["skills"]} == set(BY_SLUG)


def test_build_is_deterministic(tmp_path: Path) -> None:
    first = build_pack(tmp_path, PACK, SKILLS)
    second = build_pack(tmp_path, PACK, SKILLS)
    assert first == second
    assert len(first) == 52  # 50 skills, pack.json, results/catalog.md


def test_catalog_lists_every_skill() -> None:
    catalog = (ROOT / "results" / "catalog.md").read_text(encoding="utf-8")
    assert catalog.count("| `") == 50
    for skill in SKILLS:
        assert f"`{skill.slug}`" in catalog


# ----------------------------------------------------------------------- CLI


def test_cli_validate_reports_fifty_of_fifty() -> None:
    result = run_cli("validate")
    assert result.returncode == 0
    assert "50/50 skills valid" in result.stdout


def test_cli_validate_json_is_machine_readable() -> None:
    payload = json.loads(run_cli("validate", "--json").stdout)
    assert payload["valid"] == 50 and payload["passed"] is True
    assert payload["floors"]["min_steps"] == MIN_STEPS


def test_cli_list_filters_by_phase() -> None:
    result = run_cli("list", "--phase", "dedupe")
    assert result.returncode == 0
    assert "dedupe" in result.stdout
    listed = [line for line in result.stdout.splitlines() if line.startswith("dedupe")]
    assert len(listed) >= 6


def test_cli_list_json_counts_fifty() -> None:
    assert len(json.loads(run_cli("list", "--json").stdout)) == 50


def test_cli_show_prints_one_skill_with_front_matter() -> None:
    result = run_cli("show", "signature-bucketing", "--raw")
    assert result.returncode == 0
    assert result.stdout.startswith("---\nname: signature-bucketing")
    assert "## Procedure" in result.stdout


def test_cli_show_rejects_an_unknown_slug() -> None:
    assert run_cli("show", "no-such-skill").returncode == 2


def test_cli_search_ranks_matches() -> None:
    result = run_cli("search", "dedupe", "--limit", "5")
    assert result.returncode == 0
    assert "dedupe" in result.stdout.lower()


def test_cli_search_reports_no_matches() -> None:
    assert run_cli("search", "zzzznotaterm").returncode == 1


def test_cli_signature_json_exposes_frames() -> None:
    result = run_cli(
        "signature", str(EXAMPLES / "crashes" / "gdb-report.txt"), "--kind", "segv", "--json"
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["signature"] == "a540614c71147b9d"
    assert payload["frames"][0]["canonical"] == "parse_header@parse.c"


def test_cli_similar_calls_two_tools_the_same_bug() -> None:
    result = run_cli(
        "similar",
        str(EXAMPLES / "crashes" / "gdb-report.txt"),
        str(EXAMPLES / "crashes" / "lldb-report.txt"),
        "--kind",
        "segv",
    )
    assert result.returncode == 0
    assert "1.000 -> duplicate" in result.stdout


def test_cli_dedupe_exits_one_when_known() -> None:
    result = run_cli(
        "dedupe",
        str(EXAMPLES / "crashes" / "lldb-report.txt"),
        str(EXAMPLES / "crashes" / "gdb-report.txt"),
        "--kind",
        "segv",
        "--json",
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["verdict"] == "duplicate"
    assert payload["best_match"] == "gdb-report.txt"


def test_cli_dedupe_exits_zero_for_a_new_crash() -> None:
    result = run_cli(
        "dedupe",
        str(EXAMPLES / "crashes" / "asan-other-bug.txt"),
        str(EXAMPLES / "crashes" / "gdb-report.txt"),
        "--kind",
        "heap-buffer-overflow",
    )
    assert result.returncode == 0
    assert "new" in result.stdout


def test_cli_dedupe_needs_something_to_compare_against(tmp_path: Path) -> None:
    assert run_cli("dedupe", str(EXAMPLES / "crashes" / "gdb-report.txt"), "no-such-*.txt").returncode == 2


def test_cli_cluster_groups_the_example_reports() -> None:
    result = run_cli("cluster", "examples/crashes/*.txt", "--kind", "segv", "--json")
    assert result.returncode == 0
    groups = json.loads(result.stdout)
    assert [group["size"] for group in groups] == [2, 1]
    assert "gdb-report.txt" in groups[0]["members"]


def test_cli_check_grades_the_example_record() -> None:
    result = run_cli("check", "examples/record.json", "--root", "examples")
    assert result.returncode == 0
    assert "grade A (100/100) submittable" in result.stdout


def test_cli_check_fails_an_incomplete_record(tmp_path: Path) -> None:
    record = json.loads((EXAMPLES / "record.json").read_text(encoding="utf-8"))
    record["reproduction"]["command"] = ""
    path = tmp_path / "record.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    result = run_cli("check", str(path), "--root", "examples")
    assert result.returncode == 1
    assert "reproduction" in result.stdout


def test_cli_verify_passes_on_the_example_bundle() -> None:
    result = run_cli("verify", "examples/evidence/manifest.json", "--root", "examples/evidence")
    assert result.returncode == 0
    assert result.stdout.startswith("ok")


def test_cli_verify_fails_after_an_edit(tmp_path: Path) -> None:
    manifest = json.loads(
        (EXAMPLES / "evidence" / "manifest.json").read_text(encoding="utf-8")
    )
    manifest["files"][0]["sha256"] = "0" * 64
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    result = run_cli("verify", str(path), "--root", "examples/evidence")
    assert result.returncode == 1
    assert "digest changed" in result.stdout


def test_cli_scaffold_emits_a_record_with_the_right_schema(tmp_path: Path) -> None:
    out = tmp_path / "new.json"
    assert run_cli("scaffold", "A crash", "--out", str(out)).returncode == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["schema"] == "triageproof/v1"
    assert record["dedupe"]["checked"] is False


def test_cli_report_renders_sections() -> None:
    result = run_cli("report", "examples/record.json", "--root", "examples")
    assert result.returncode == 0
    for heading in ("## Crash", "## Reproduction", "## Dedupe", "## Root cause", "## Triage grade"):
        assert heading in result.stdout


def test_cli_bundle_writes_a_manifest(tmp_path: Path) -> None:
    out = tmp_path / "manifest.json"
    result = run_cli("bundle", "examples/evidence", "--write", str(out))
    assert result.returncode == 0
    assert json.loads(out.read_text(encoding="utf-8"))["count"] == 4


def test_cli_version_is_printed() -> None:
    result = run_cli("--version")
    assert result.returncode == 0
    assert "triageproof 1.0.0" in result.stdout
