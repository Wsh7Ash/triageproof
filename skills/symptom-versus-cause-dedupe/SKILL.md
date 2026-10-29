---
name: symptom-versus-cause-dedupe
description: "Separate crashes that share a symptom but not a cause, because an allocator abort and a bounds overflow can both end in SIGABRT. Use when several crashes share a signal or a top frame but the reports feel different"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, dedupe, root-cause]
---

# Symptom Versus Cause Dedupe

> Separate crashes that share a symptom but not a cause, because an allocator abort and a bounds overflow can both end in SIGABRT

**Use when:** several crashes share a signal or a top frame but the reports feel different

**Avoid when:** the mechanism is already established and identical

## Procedure

1. List the symptom for each crash: signal, sanitizer class, top frame.
2. List the cause: the unchecked condition and the faulty operation.
3. Check for shared symptoms with different causes.
4. Check for shared causes presenting with different symptoms.
5. Record the mapping from symptom to cause for each.
6. Dedupe on the cause and report the symptom separately.

## Signals

- Both crash in free but one is a double free and one is a heap overflow.
- The top frame differs but the same missing check is behind both.
- One sanitizer class covers several distinct mechanisms.
- The same cause aborts in a different function on a different build.

## Patterns

**1. Symptom table**

```text
SIGABRT / heap-buffer-overflow / parse_header  -> symptom, not cause
```

**2. Cause column**

```text
no bounds check on length before copy  -> the actual identity
```

**3. Split honestly**

```text
same top frame, different faulty operation  -> two bugs
```

## Pitfalls

- Deduping on the sanitizer class and merging unrelated overflows.
- Splitting a bug whose top frame differs only because of inlining.
- Treating a signal as a cause and never writing the actual mechanism.

## Done when

- Symptom and cause are recorded separately for each crash.
- The duplicate decision cites the cause, not the signal.

## References

- [Clang - sanitizer classes](https://clang.llvm.org/docs/AddressSanitizer.html)
- [CWE - memory corruption](https://cwe.mitre.org/data/definitions/787.html)
