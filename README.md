# triageproof

Canonicalise crash stacks, cluster by signature, dedupe across reports, and verify
evidence bundles — plus **50 validated skills** for making a crash claim survive
triage.

The premise is narrow: a crash is not a finding until it has a **stable
signature**, a **dedupe check** against what is already known, and an **evidence
bundle that still matches** what was submitted. Most rejected reports fail on one
of those three, not on the bug. This repo is the tool and the playbook for those
three.

Zero runtime dependencies. Python 3.10+. Everything works offline.

## The three failures it exists to catch

| Failure | What it looks like | What happens here |
|---|---|---|
| **Unstable signature** | The same bug reported by gdb and by a minidump has two different hashes | Hashed text is function-only, so one bug has one key across tools |
| **Filing a known bug** | A crash that matches an advisory, an upstream issue, or a closed report | `dedupe` compares before you write, and the record blocks without a check |
| **Evidence that moved** | A log edited after the hash was taken still ships and still looks like proof | `verify` re-hashes every file and fails on drift, edits and extras |

## Install and run

```bash
python -m pip install -e ".[dev]"
triageproof validate              # the 50/50 gate
triageproof signature crash.txt --kind segv
```

Nothing else is required: `triageproof` runs directly from a checkout with
`PYTHONPATH=src python -m triageproof ...`.

## The four domain commands

### 1. `signature` — one bug, one key

```text
$ triageproof signature examples/crashes/gdb-report.txt --kind segv
signature a540614c71147b9d  (7 frame(s) parsed, depth 5)
  1. parse_header@parse.c
  2. handle_request@handler.c
  3. serve_forever@server.c
  4. http_dispatch@http.c
  5. connection_loop@http.c
```

Parses gdb, lldb, AddressSanitizer, minidump (`lib!symbol+0x..`) and Python
traceback frames. Canonicalisation strips the volatile parts: addresses, frame
offsets, template arguments, thread suffixes, absolute paths, line numbers, and
the frames present in every crash (`start_thread`, `malloc`/`free`, `abort`).

### 2. `similar` / `dedupe` — is this already known?

```text
$ triageproof similar examples/crashes/gdb-report.txt examples/crashes/lldb-report.txt --kind segv
gdb-report.txt vs lldb-report.txt: 1.000 -> duplicate
```

Similarity is Dice overlap over canonical frames, matched on function with the
file basename as a tiebreak when both reports carry one, so a module-qualified
lldb stack and a path-qualified gdb stack agree. A crash-kind mismatch returns
`0.0` outright: a heap overflow and a null dereference in one function are two
bugs.

`dedupe` adds the verdict band and exits non-zero when the crash is not new:

```text
duplicate  >= 0.85   (blocking gate in the record)
probable   >= 0.60   (review by a human)
new        <  0.60
```

### 3. `cluster` — work the noisy bug once

```text
$ triageproof cluster 'examples/crashes/*.txt' --kind segv
a540614c71147b9d  2 report(s)
    gdb-report.txt
    lldb-report.txt
7277f3f0946cb192  1 report(s)
    asan-other-bug.txt
# 3 report(s) in 2 cluster(s)
```

Sorted by size, because one signature with two hundred reports matters more than
forty singletons.

### 4. `bundle` / `verify` — evidence that cannot drift

```text
$ triageproof bundle examples/evidence --write examples/evidence/manifest.json
bundled 4 file(s) into examples/evidence/manifest.json

$ triageproof verify examples/evidence/manifest.json --root examples/evidence
ok  4 file(s) match examples/evidence/manifest.json
```

The manifest records every file with its kind (`crash/`, `stack/`, `repro/`,
`version/`), size and SHA-256. `verify` fails on a changed digest, a changed
size, a file that appeared after sealing, or a required artifact kind that is
missing.

## `check` — the blocking gate

A triage record is JSON. `check` grades it and refuses to call it submittable
while any blocking rule fails:

```text
$ triageproof check examples/record.json --root examples
parserd-2.3.0-segv-parse-header: grade A (100/100) submittable

$ triageproof check tampered.json --root examples --verbose
parserd-2.3.0-segv-parse-header: grade D (25/100) NOT submittable
  blocking version: target.version is missing
  blocking signature-mismatch: declared signature deadbeefdeadbeef does not match the stack (a540614c71147b9d)
  blocking dedupe-evidence: verdict is 'duplicate' but nothing is listed under against
```

Blocking rules are exactly what triagers close reports for:

- the target has no scope reference
- no version, so the bug cannot be deduped or retested
- no saved stack file, or a signature that does not reproduce from it
- no reproduction command
- no dedupe check, or a non-`new` verdict with an empty `against` list
- no impact statement
- evidence missing, or a digest that no longer matches the file

`triageproof scaffold "title" --out record.json` emits an empty record.
`triageproof report record.json` renders the submission text.

## The 50 skills

| Phase | Skills | What it covers |
|---|---|---|
| `capture` | 8 | Getting a stack that is worth hashing: debug symbols, build ids, frame capture, tool choice |
| `canonicalise` | 9 | Stripping addresses, paths, noise frames, inline frames, template args; choosing depth; proving stability |
| `cluster` | 8 | Exact bucketing, threshold calibration, cross-tool comparison, threads, labels, regressions, size triage |
| `dedupe` | 8 | Advisory search, prior reports, root-cause equality, symptom vs cause, variants, verdict recording |
| `grade` | 9 | Completeness, oracle pairs, determinism, impact-scope matching, severity, blocking gates, immutability |
| `bundle` | 8 | Manifests, hash verification, missing files, redaction before hashing, replay, minimisation, retention |

Every skill is validated against the same rules `triageproof validate` enforces:
6+ steps, 4+ signals, 3+ patterns, 3+ pitfalls, 180+ rendered words, canonical
https references, no placeholders, no machine-local paths, unique slug and title.

```bash
triageproof list --phase dedupe
triageproof show advisory-search-first
triageproof search "negative control"
```

## Layout

```text
src/triageproof/
  stack.py     parsing, canonicalisation, signatures, similarity, clustering
  bundle.py    evidence hashing, required kinds, drift detection
  triage.py    record rules, grading, submission rendering
  cli.py       the command surface
  corpus/      the 50 skills as plain dicts, split across three parts
  validate.py  the corpus rules
  render.py    deterministic SKILL.md rendering
skills/        generated SKILL.md files (one directory per skill)
pack.json      generated manifest with a SHA-256 per skill
results/       generated catalog and demo transcript
examples/      a real report, three crash files and a verifiable bundle
```

## Verification

- `triageproof validate` → **50/50 skills valid**
- `pytest -q` → **83 passing**
- Generated files are compared against a fresh render in the test suite, and CI
  re-runs `build` and fails on any diff
- The example record grades **A (100/100)**; tampering with its evidence drops it
  to **D** and fails `verify`

See [RESULTS.md](RESULTS.md) for the exact commands and their output, and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for why the signature is
function-only.

## Scope

This is a triage and evidence tool. It does not fuzz, exploit or scan anything.
It works on crash reports and artifacts you already have, and it is meant to be
run on targets you are authorised to test.

## License

MIT.
