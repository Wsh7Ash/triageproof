---
name: sanitizer-output-preservation
description: "Keep the sanitizer's own report intact, because its classification, access type and shadow bytes are the strongest evidence of what went wrong. Use when the crash came from ASan, MSan, TSan or UBSan rather than a plain signal"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, capture, sanitizer]
---

# Sanitizer Output Preservation

> Keep the sanitizer's own report intact, because its classification, access type and shadow bytes are the strongest evidence of what went wrong

**Use when:** the crash came from ASan, MSan, TSan or UBSan rather than a plain signal

**Avoid when:** the crash is a plain SIGSEGV with no sanitizer instrumentation

## Procedure

1. Save stdout and stderr separately, since the report is split across them.
2. Keep the header line that names the sanitizer class verbatim.
3. Keep the memory access description, including the access size and offset.
4. Keep the shadow byte legend and the free/alloc stack pairs.
5. Do not reformat or summarise the block before saving it.
6. Quote the first two lines of the sanitizer header in the report.

## Signals

- The report says heap-use-after-free but the summary calls it a buffer overflow.
- The free stack is present while the alloc stack was truncated.
- The shadow bytes show a redzone read one byte past the allocation.
- The sanitizer class differs between two runs of the same input.

## Patterns

**1. Header survives**

```text
ERROR: AddressSanitizer: heap-use-after-free on address 0x...  -> the class
```

**2. Access detail**

```text
READ of size 8 at 0x... thread T0  -> what was accessed
```

**3. Two stacks**

```text
freed by thread T0 here: ... previously allocated by thread T0 here: ...  -> both kept
```

## Pitfalls

- Summarising the sanitizer output and losing the access size and offset.
- Treating a sanitizer class as a bug title without reading the stacks.
- Discarding the alloc stack because it was long, which removes the evidence of the owner.

## Done when

- The sanitizer header, access description and both stacks are preserved verbatim.
- The report quotes the class exactly as the sanitizer emitted it.

## References

- [Clang - AddressSanitizer report format](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Clang - UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html)
