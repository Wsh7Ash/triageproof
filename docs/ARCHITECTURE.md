# Architecture

Four modules, one direction of dependency:

```text
stack.py   parsing -> canonicalisation -> signature / similarity / clustering
bundle.py  hashing -> manifest -> drift detection
triage.py  record rules -> grade -> submission text          (uses stack, bundle)
cli.py     argument parsing and exit codes                   (uses all three)
```

`corpus/` holds the 50 skills as plain dicts; `model.py` turns each into a frozen
`Skill`; `validate.py` enforces the rules; `render.py` is the only writer of
generated files. No module below `cli.py` prints anything.

## Why the signature hashes function names only

A signature is the machine key used for bucketing, so it must be identical for
one bug regardless of who captured it. The capture tools disagree about almost
everything:

| Tool | Addresses | Module | File | Line |
|---|---|---|---|---|
| gdb | yes | no | yes | yes |
| lldb | yes | yes | yes | yes |
| minidump (`lib!sym+0x..`) | offset | yes | no | no |
| CPython traceback | no | no | yes | yes |
| ASan | yes | no | yes | yes |

Only the function name is always present. Hashing `Frame.canonical()` — which
includes the module — gave one bug two keys: `parse_header@parse.c` from gdb and
`app!parse_header@parse.c` from lldb. That is the exact failure exact bucketing
exists to prevent, and an early version of this module had it. `signature_text`
therefore hashes `Frame.key()`, which is the function name after cleaning.

The cost is real and accepted: two distinct bugs whose top five frames are
identically named (impossible to distinguish without a path) collide on the
signature. `similarity` is not affected — it compares frames pairwise and can
afford to require the file basename to match when both reports carry one.

Depth is a parameter for the same reason. A minidump of a stripped build has
three frames where gdb has seven, so reports can only be compared at a depth
every report can supply; `signature` takes `--depth` and the tests assert
cross-tool equality at depth 3.

## What canonicalisation removes

| Removed | Why | Where |
|---|---|---|
| `0x...` addresses | ASLR makes them different on every run | `ADDRESS_RE`, `OFFSET_RE` |
| Absolute path, keeping the basename | Build machines differ | `Frame.canonical` |
| Line numbers | Any edit above the bug shifts them | `Frame.canonical` |
| Template arguments | `vector<int>` and `vector<char>` are the same code path | `_strip_template_args` |
| `(Thread 0x...)` suffixes | Thread ids vary per run | `THREAD_SUFFIX_RE` |
| Allocator, start, abort, unwind frames | Present in nearly every crash, so they carry no signal | `NOISE_PATTERNS` |

`_strip_template_args` counts depth instead of using a regex: `std::vector<int,
std::allocator<int>>` contains a `>` that a non-nesting pattern would cut in
half, leaving a stray `>` in the function name and a different signature.

## Similarity

Dice overlap over the canonical top frames:

```text
2 * matched / (len(left) + len(right))
```

A frame matches when the function names are equal and the file basenames agree
*whenever both sides have one*. A module never blocks a match, because the other
tool may not record one. Different crash kinds short-circuit to `0.0`: a heap
overflow and a null dereference in one function are two bugs, and no frame
overlap should be able to merge them.

Clustering is greedy and order-dependent by design — it is a reading aid, not a
partition, and the fingerprint of each group is recomputed from the group's head
at the same depth and kind that grouping used.

## Why grading is blocking

`grade` returns a score *and* a list of findings, each tagged `blocking`,
`major` or `minor`. Any blocking finding forces grade `D` and makes the record
non-submittable regardless of the score. The score alone would be misleading: a
record can be 97/100 and still be unsubmittable because the one missing thing is
the dedupe check.

A blocking rule is only used where the missing field makes the claim unfalsifiable:

- no scope reference — the work was not authorised
- no version — the bug cannot be deduped or retested
- no saved stack — the signature came from memory
- a signature that does not reproduce from its own stack — the most common way a
  duplicate is filed twice
- no reproduction — nothing to verify
- no dedupe check, or a non-`new` verdict with an empty `against` list
- no impact statement
- evidence missing or changed since hashing

Everything else is penalised but does not block: an unstated repro rate, a
missing environment, an unrecognised status.

## Evidence bundles

`bundle` records the relative path, kind, byte size and SHA-256 of every file
under the directory, then the manifest is written *outside* or beside what it
describes. `verify` answers four questions:

1. does every recorded file still hash to its recorded digest?
2. did any size change?
3. did a file appear that the manifest does not mention?
4. is every required artifact kind present?

The manifest excludes itself by name (`manifest.json`, `bundle.json`) and by
resolved path, because a manifest that hashes itself can never verify.

Kinds come from the first path segment (`crash/`, `stack/`, `repro/`,
`version/`), so the directory layout is the contract, and a bundle missing
`version/` fails without any extra configuration.
