---
name: noise-frame-removal
description: "Drop the allocator, startup and crash-handler frames before hashing, because they appear in almost every crash and dilute the signature. Use when building a signature from a sanitizer or debugger stack that includes libc and runtime frames"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, canonicalise, signature]
---

# Noise Frame Removal

> Drop the allocator, startup and crash-handler frames before hashing, because they appear in almost every crash and dilute the signature

**Use when:** building a signature from a sanitizer or debugger stack that includes libc and runtime frames

**Avoid when:** the crash is inside the allocator itself, where those frames are the finding

## Procedure

1. List the functions that appear in nearly every crash of this target.
2. Write them as an explicit pattern list rather than guessing per report.
3. Remove them before taking the top frames for the signature.
4. Check that the vulnerable frame is never matched by the noise list.
5. Keep the removed frames in the artifact for context.
6. Re-run the stability and discrimination checks after changing the list.

## Signals

- Every signature starts with the same three runtime frames.
- Two unrelated bugs share a signature because only noise frames are in the top five.
- The noise list accidentally matches a prefix of the vulnerable function.
- Removing noise makes the signature change for existing reports, so they must be re-baselined.

## Patterns

**1. Explicit list**

```text
^(malloc|free|__libc_|start_thread|abort)$  -> reviewed, not per-report
```

**2. Never the fault**

```text
assert the vulnerable frame survives  -> a test on every corpus change
```

**3. Context kept**

```text
the raw stack still contains the removed frames
```

## Pitfalls

- Removing frames with a broad prefix match that eats the vulnerable function.
- Changing the noise list and silently invalidating every stored signature.
- Keeping allocator frames because they were present in the first example.

## Done when

- The noise list is explicit, tested, and does not match the faulting frame.
- Signature stability and discrimination both hold after removal.

## References

- [Clang - sanitizer stack contents](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Mozilla - crash signature generation](https://firefox-source-docs.mozilla.org/toolkit/crashreporter/crashreporter/index.html)
