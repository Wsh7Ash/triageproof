"""Evidence bundles: hashing, required artifacts and drift detection.

A triage package is a set of artifacts of different kinds — the crash log, the
stack, the reproduction command, the version output. Triage falls apart when one
is missing or was edited after the report was written, so a bundle records the
kind of every file, hashes it, and can answer three questions later:

* is every artifact still byte-identical?
* did anything appear after the bundle was sealed?
* is every artifact kind the report depends on actually present?
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "triageproof.bundle/v1"
CHUNK = 64 * 1024

KNOWN_KINDS = ("crash", "stack", "repro", "version", "screenshot", "log", "other")
DEFAULT_REQUIRED = ("crash", "stack", "repro", "version")


class BundleError(RuntimeError):
    """Raised when a bundle cannot be built or read."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def infer_kind(relative: str) -> str:
    """The first path segment names the kind when it is a known one."""
    head = relative.split("/", 1)[0].lower()
    return head if head in KNOWN_KINDS else "other"


def collect(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.name not in ("manifest.json", "bundle.json")
    )


def build_bundle(root: Path, required: Iterable[str] | None = None) -> dict[str, Any]:
    """Hash every artifact under ``root`` and record its kind."""
    files = collect(root)
    if not files:
        raise BundleError(f"no artifacts found under {root}")

    entries: list[dict[str, Any]] = []
    for path in files:
        try:
            relative = path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            relative = path.as_posix()
        entries.append(
            {
                "path": relative,
                "kind": infer_kind(relative),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    entries.sort(key=lambda entry: entry["path"])
    kinds = sorted({entry["kind"] for entry in entries})
    wanted = list(required) if required is not None else list(DEFAULT_REQUIRED)

    return {
        "schema": SCHEMA,
        "count": len(entries),
        "total_bytes": sum(entry["bytes"] for entry in entries),
        "kinds": kinds,
        "required": wanted,
        "missing": [kind for kind in wanted if kind not in kinds],
        "files": entries,
    }


def write_bundle(bundle: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8", newline="\n")


def load_bundle(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BundleError(f"bundle not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BundleError(f"bundle is not valid JSON: {exc}") from exc
    if data.get("schema") != SCHEMA:
        raise BundleError(f"unexpected bundle schema: {data.get('schema')!r}")
    return data


def verify_bundle(bundle: dict[str, Any], root: Path, bundle_path: Path | None = None) -> list[str]:
    """Re-hash every recorded artifact and report drift."""
    problems: list[str] = []
    entries = bundle.get("files")
    if not isinstance(entries, list) or not entries:
        return ["bundle records no files"]

    for entry in entries:
        raw = entry.get("path") if isinstance(entry, dict) else None
        if not isinstance(raw, str) or not raw:
            problems.append("bundle entry without a path")
            continue
        path = Path(raw)
        if not path.is_absolute():
            path = root / path
        if not path.is_file():
            problems.append(f"missing: {raw}")
            continue
        if path.stat().st_size != entry.get("bytes"):
            problems.append(f"size changed: {raw}")
        if sha256_file(path) != entry.get("sha256"):
            problems.append(f"digest changed: {raw}")

    recorded = {str(entry.get("path")) for entry in entries if isinstance(entry, dict)}
    skip = bundle_path.resolve() if bundle_path is not None else None
    for path in collect(root):
        if skip is not None and path.resolve() == skip:
            continue
        try:
            relative = path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            relative = path.as_posix()
        if relative not in recorded:
            problems.append(f"unrecorded file: {relative}")

    for kind in bundle.get("required", []):
        present = any(entry.get("kind") == kind for entry in entries if isinstance(entry, dict))
        if not present:
            problems.append(f"missing required kind: {kind}")

    return problems
