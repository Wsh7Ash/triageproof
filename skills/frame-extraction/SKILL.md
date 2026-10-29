---
name: frame-extraction
description: "Parse frames from whatever format the tool emitted, because a signature built from a hand-copied stack cannot be reproduced. Use when the stack came from gdb, lldb, a minidump, a sanitizer or a language traceback"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, canonicalise, parsing]
---

# Frame Extraction

> Parse frames from whatever format the tool emitted, because a signature built from a hand-copied stack cannot be reproduced

**Use when:** the stack came from gdb, lldb, a minidump, a sanitizer or a language traceback

**Avoid when:** the frames are already in a structured format with a stable schema

## Procedure

1. Identify which tool produced the stack by its frame line shape.
2. Parse frames in order rather than filtering by pattern first.
3. Reject lines that do not match any known frame shape instead of guessing.
4. Record how many lines were parsed and how many were skipped.
5. Print the parsed frames next to the raw stack to spot misfires.
6. Store the parser version with the signature so a change is visible.

## Signals

- A frame is missing where the stack clearly shows a call.
- A parameter line is parsed as a frame.
- The frame count differs from the numbered frames in the raw text.
- One format is parsed correctly and another silently yields nothing.

## Patterns

**1. Format per line**

```text
gdb: #0 0x.. in f at file:88
python: File "x.py", line 42, in f
minidump: mod!f+0x2a
```

**2. Count check**

```text
raw has #0..#7, parsed 8 frames  -> complete
```

**3. Skip, do not guess**

```text
unrecognised preamble lines are ignored, not turned into frames
```

## Pitfalls

- Regexing the whole file at once and losing frame order.
- Parsing a caller line like 'called by' as a frame.
- Silently dropping half the stack because one format was assumed.

## Done when

- Every numbered frame in the raw stack appears in the parsed output.
- Skipped lines are counted and visible to the reader.

## References

- [GDB - backtraces](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Backtrace.html)
- [LLDB - frame formats](https://lldb.llvm.org/use/map.html)
