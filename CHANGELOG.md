# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-29

First release: 50 validated skills and the tooling behind them.

### Added

- **Stack canonicalisation and signatures.** Parses gdb, lldb, AddressSanitizer,
  minidump (`lib!symbol+0x..`) and CPython traceback frames. Strips addresses,
  frame offsets, template arguments, thread suffixes, absolute paths, line
  numbers and the frames common to every crash.
- **Similarity and dedupe.** Dice overlap over canonical frames, matched on
  function with a file basename tiebreak; a crash-kind mismatch returns `0.0`.
  Verdict bands at `0.85` (duplicate) and `0.60` (probable).
- **Clustering.** Greedy grouping by similarity, sorted by size, each group
  carrying the signature of its head report.
- **Evidence bundles.** Manifest with a kind, size and SHA-256 per artifact;
  verification fails on a changed digest, a changed size, a file that appeared
  after sealing, or a missing required kind.
- **Record grading.** Blocking and non-blocking rules over a JSON triage record,
  with the signature recomputed from the record's own stack file and evidence
  digests re-checked on disk.
- **CLI:** `validate`, `list`, `show`, `search`, `build`, `signature`, `similar`,
  `dedupe`, `cluster`, `bundle`, `verify`, `check`, `scaffold`, `report`.
- **50 skills** across six phases: capture 8, canonicalise 9, cluster 8,
  dedupe 8, grade 9, bundle 8.
- CI matrix on Python 3.10, 3.12 and 3.13 that validates the corpus, runs the
  tests, and rebuilds to fail on committed-artifact drift.

### Fixed during development

- **Signature was module-qualified**, so one bug captured by gdb and by lldb had
  two keys and landed in two buckets. The hashed text is now function-only.
- **Cross-tool similarity scored `0.0`** when one report carried a module and
  the other did not, because frames were compared on their text form rather than
  on function plus file.
- **Template arguments with a space** (`std::map<K, V>`) truncated the function
  name at the comma; folding is now depth-counted, so nested templates fold
  correctly.
- **`--kind` was silently ignored** by `dedupe` and `cluster`, disabling the
  crash-kind gate for file-based comparisons.
- **A cluster's fingerprint** was computed without the kind used for grouping, so
  it disagreed with `triageproof signature` for the same stack.
