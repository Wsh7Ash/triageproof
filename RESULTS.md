# Results

Reproducible evidence for every claim in [README.md](README.md). All commands run
from the repository root with `PYTHONPATH=src`.

## Environment

- Windows 11 (MSYS2 shell), Python 3.14.0
- Runtime: Python standard library only; `pytest>=8` as the sole dev dependency
- Network: none required at any point

## 1. Corpus gate

```console
$ triageproof validate
triageproof: 50/50 skills valid
  ok  steps>=6 signals>=4 patterns>=3 pitfalls>=3 words>=180 refs canonical https
```

Phase distribution: `capture` 8, `canonicalise` 9, `cluster` 8, `dedupe` 8,
`grade` 9, `bundle` 8 — 50 unique slugs, 50 unique titles, 50 unique summaries.

## 2. One bug, one signature across capture tools

gdb records paths and no module; lldb records a module and a path. Both hash to
the same key:

```console
$ triageproof signature examples/crashes/gdb-report.txt --kind segv
signature a540614c71147b9d  (7 frame(s) parsed, depth 5)
  1. parse_header@parse.c
  2. handle_request@handler.c
  3. serve_forever@server.c
  4. http_dispatch@http.c
  5. connection_loop@http.c

$ triageproof signature examples/crashes/lldb-report.txt --kind segv
signature a540614c71147b9d  (5 frame(s) parsed, depth 5)
  1. app!parse_header@parse.c
  2. app!handle_request@handler.c
  3. app!serve_forever@server.c
  4. app!http_dispatch@http.c
  5. app!connection_loop@http.c
```

The `gdb` report parses 7 frames because it includes `start_thread` and `clone`,
which are noise and dropped before hashing. The `app!` module qualifier stays in
the human-facing text and is excluded from the hash.

## 3. Dedupe

```console
$ triageproof similar examples/crashes/gdb-report.txt examples/crashes/lldb-report.txt --kind segv
gdb-report.txt vs lldb-report.txt: 1.000 -> duplicate

$ triageproof dedupe examples/crashes/asan-other-bug.txt examples/crashes/gdb-report.txt --kind heap-buffer-overflow
asan-other-bug.txt (27206d47267e4014): new  similarity 0.000
  compared against 1 report(s)
exit=0
```

## 4. Clustering

```console
$ triageproof cluster 'examples/crashes/*.txt' --kind segv
a540614c71147b9d  2 report(s)
    gdb-report.txt
    lldb-report.txt
7277f3f0946cb192  1 report(s)
    asan-other-bug.txt
# 3 report(s) in 2 cluster(s)
```

## 5. Bundle verification

```console
$ triageproof bundle examples/evidence --write examples/evidence/manifest.json
bundled 4 file(s) into examples/evidence/manifest.json

$ triageproof verify examples/evidence/manifest.json --root examples/evidence
ok  4 file(s) match examples/evidence/manifest.json
exit=0
```

Tampering is detected in three distinct ways:

```console
# one byte appended to an artifact
$ triageproof verify examples/evidence/manifest.json --root examples/evidence
FAIL size changed: crash/crash.log
FAIL digest changed: crash/crash.log
exit=1

# a file added after the bundle was sealed
FAIL unrecorded file: log/notes.txt
exit=1
```

## 6. Record grading

```console
$ triageproof check examples/record.json --root examples
parserd-2.3.0-segv-parse-header: grade A (100/100) submittable
  signature a540614c71147b9d
exit=0
```

Three independent blocking failures on the same record:

```console
$ triageproof check bad.json --root examples --verbose
parserd-2.3.0-segv-parse-header: grade D (25/100) NOT submittable
  blocking version: target.version is missing
           -> A crash without a version cannot be deduped or retested.
  blocking signature-mismatch: declared signature deadbeefdeadbeef does not match the stack (a540614c71147b9d)
           -> A signature that does not reproduce is how duplicates get filed twice.
  blocking dedupe-evidence: verdict is 'duplicate' but nothing is listed under against
           -> Name the report or advisory this was matched to.
exit=1
```

And an edited artifact is caught at the record level, not just the bundle level:

```console
$ triageproof check examples/record.json --root examples   # after appending to crash.log
parserd-2.3.0-segv-parse-header: grade D (75/100) NOT submittable
  blocking evidence-drift: evidence changed since it was hashed: evidence/crash/crash.log
exit=1
```

## 7. Test suite

```console
$ python -m pytest
83 passed in 3.92s

tests/test_corpus.py: 35
tests/test_stack.py: 48
```

`tests/test_stack.py` (48) covers parsing (gdb, lldb, minidump, Python traceback,
template arguments with spaces, thread suffixes, junk lines), signature
stability (ASLR, build paths, cross-tool equality at a shared depth, kind
separation, depth), similarity (symmetry, kind gate, module-free matching, file
tiebreak, partial overlap), clustering, dedupe verdict boundaries, bundles
(digests, required kinds, empty directory, tamper, extras, manifest
self-exclusion, a published SHA-256 vector) and every blocking grade rule.

`tests/test_corpus.py` (35) covers the 50/50 gate, slug and title uniqueness,
writing floors, phase coverage, https references, deterministic rendering,
committed-artifact sync, `pack.json` digests, and every CLI subcommand with its
exit code and JSON shape.

## 8. Determinism of generated files

```console
$ triageproof build && git diff --exit-code -- skills pack.json results
(no output, exit 0)
```

The test suite also renders every skill fresh and compares it byte-for-byte with
the committed file, so a corpus edit without a rebuild fails CI.

## What was not run

- No real crash was captured or reproduced: the example stacks are authored to
  match the documented gdb, lldb, ASan, minidump and CPython traceback formats,
  and the parser tests assert on those shapes rather than on live captures.
- No Frida, WinDbg or `minidump_stackwalk` output was fed in. Minidump support is
  the `lib!symbol+0x..` line shape, which those tools emit, not their container
  format.
- `dedupe` was not run against a live bug tracker or advisory API. Advisory
  search is a documented procedure in the `dedupe` skills; the CLI takes the
  prior reports you have already exported.
