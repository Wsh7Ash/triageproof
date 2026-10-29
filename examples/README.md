# Examples

One bug, captured two ways, plus a different bug and a complete verifiable
package. Everything here is synthetic: the stack frames are written to match the
real output formats rather than captured from a live crash.

## Crash reports

| File | Format | What it is |
|---|---|---|
| `crashes/gdb-report.txt` | gdb | The bug: 7 frames, paths, no module, includes `start_thread` and `clone` as noise |
| `crashes/lldb-report.txt` | lldb | The same bug: 5 frames, module-qualified (`app!parse_header`), no noise frames |
| `crashes/asan-other-bug.txt` | AddressSanitizer | A different bug in the lexer, used to prove dedupe does not merge unrelated crashes |

The first two hash to the same signature:

```console
$ triageproof signature examples/crashes/gdb-report.txt --kind segv
signature a540614c71147b9d  (7 frame(s) parsed, depth 5)

$ triageproof signature examples/crashes/lldb-report.txt --kind segv
signature a540614c71147b9d  (5 frame(s) parsed, depth 5)
```

Both accept `--depth 3` as well and still agree, which is the comparison to use
when one tool captured fewer frames.

## Evidence

```text
evidence/
  crash/crash.log      the raw crash output, unchanged
  stack/stack.txt      the stack the signature was computed from
  repro/repro.sh       the reproduction command, runnable but never run by this tool
  version/version.txt  version, build id, binary hash
  manifest.json        generated: path, kind, size and SHA-256 per artifact
```

The manifest was produced with `triageproof bundle evidence --write
evidence/manifest.json` and checks clean:

```console
$ triageproof verify examples/evidence/manifest.json --root examples/evidence
ok  4 file(s) match examples/evidence/manifest.json
```

Editing any file under `evidence/` makes it fail, which is the point.

## The record

`record.json` is the claim, graded **A (100/100)**:

```console
$ triageproof check examples/record.json --root examples --verbose
parserd-2.3.0-segv-parse-header: grade A (100/100) submittable
  signature a540614c71147b9d
```

Its `signature` field is the value the tool prints for `crash.stack_file`. Change
it and `check` blocks with `signature-mismatch`; append a byte to `crash.log` and
`check` blocks with `evidence-drift`.

Render the submission text with:

```console
$ triageproof report examples/record.json --root examples
```

## Things worth trying

```bash
# the same bug from two tools is one cluster member set
triageproof cluster 'examples/crashes/*.txt' --kind segv

# a different crash kind is never a duplicate
triageproof dedupe examples/crashes/asan-other-bug.txt examples/crashes/gdb-report.txt \
  --kind heap-buffer-overflow

# break the record on purpose and watch the blocking rules fire
python - <<'PY'
import json, pathlib
p = pathlib.Path("examples/record.json")
r = json.loads(p.read_text())
r["dedupe"]["against"] = []
r["dedupe"]["verdict"] = "duplicate"
pathlib.Path("bad.json").write_text(json.dumps(r, indent=2))
PY
triageproof check bad.json --root examples
```
