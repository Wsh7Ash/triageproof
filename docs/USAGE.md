# Usage

The workflow this tool supports, in the order a report actually happens.

## 1. Capture a stack you can hash

Save the raw output, not a screenshot and not a paste into chat:

```bash
gdb -batch -ex run -ex "thread apply all bt" ./target > stack.txt 2>&1
lldb --batch -o run -o "thread backtrace all" ./target > stack.txt 2>&1
ASAN_OPTIONS=symbolize=1 ./target 2> stack.txt
```

Keep the build id next to it — it is what makes the report retestable:

```bash
./target --version > version.txt
sha256sum ./target >> version.txt
```

## 2. Sign it

```bash
triageproof signature stack.txt --kind segv
```

`--kind` separates crash classes. Use the sanitizer class (`heap-buffer-overflow`,
`stack-use-after-return`, `segv`, `abort`) or the signal, but use the *same* value
for every report of that bug. A kind mismatch forces similarity to `0.0`, so
inconsistency here manufactures duplicates.

If the raw capture contains several threads, the faulting thread's stack must be
first: the parser takes frames in file order and `--depth` truncates from the top.

## 3. Check whether it is already known

```bash
triageproof dedupe new-stack.txt known/*.txt --kind segv --threshold 0.6 --strong 0.85
```

Exit status is `1` when the verdict is `probable` or `duplicate`, so it can gate a
script:

```bash
if triageproof dedupe new.txt known/*.txt --kind segv; then
  echo "new bug, write it up"
else
  echo "already known, add evidence to the existing report"
fi
```

Then do the human half, which no similarity score replaces: search the vendor
advisory feed, the package registry and the upstream issue tracker for the
faulting function. The `dedupe` skills describe exactly what to search and what
to record.

## 4. Cluster the backlog

```bash
triageproof cluster reports/*.txt --kind segv --threshold 0.6
```

Work the largest cluster first, then singletons. A singleton is either a new bug
or a canonicalisation gap; check which before filing.

## 5. Assemble the bundle

```text
evidence/
  crash/crash.log        the raw crash output
  stack/stack.txt        the saved stack the signature came from
  repro/repro.sh         the exact command, runnable
  version/version.txt    version, build id, binary hash
```

```bash
triageproof bundle evidence --write evidence/manifest.json
```

If an artifact holds a session token or a real user's data, redact it *before*
hashing. Hashing first means either shipping the secret or breaking the digest.

Required kinds default to `crash`, `stack`, `repro`, `version`; override with
`--require crash,stack` when a claim genuinely needs fewer.

## 6. Write and grade the record

```bash
triageproof scaffold "Zero-length body crashes parse_header" --id parse-header-segv --out record.json
$EDITOR record.json
triageproof check record.json --root . --verbose
```

The `signature` field must be the value `triageproof signature` printed for
`crash.stack_file`; `check` recomputes it and blocks on a mismatch.

Blocking findings force grade `D`. Fix the record, never the rule: a threshold
edit to make a record pass is how a gate stops meaning anything.

## 7. Render and submit

```bash
triageproof report record.json --root . --out report.md
```

## 8. Verify before a retest

```bash
triageproof verify evidence/manifest.json --root evidence
```

A retest months later needs the bytes that were submitted. If the digest no
longer matches, recapture the evidence — do not update the digest to match the
file.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | success; for `dedupe`/`check`, the record is clean or the crash is new |
| `1` | a gate failed: not submittable, known duplicate, drift detected, no matches |
| `2` | usage error: unknown slug, missing file, unreadable record |

## Working in an agent loop

The skills are `skills/<slug>/SKILL.md`, each with front matter naming the pack,
category and tags. `triageproof search "negative control"` and
`triageproof show <slug>` are the lookup surface, so an agent can load one
procedure instead of the whole pack.
