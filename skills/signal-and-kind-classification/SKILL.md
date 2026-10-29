---
name: signal-and-kind-classification
description: "Separate the signal, the sanitizer class and the bug class, because dedupe compares bug classes while a report usually quotes the signal. Use when writing the crash section of a triage record"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, capture, classification]
---

# Signal and Kind Classification

> Separate the signal, the sanitizer class and the bug class, because dedupe compares bug classes while a report usually quotes the signal

**Use when:** writing the crash section of a triage record

**Avoid when:** the crash has no signal because it is a logic failure rather than a fault

## Procedure

1. Record the signal exactly as the runtime reported it, such as SIGSEGV or SIGABRT.
2. Record the sanitizer class if one exists, such as heap-buffer-overflow.
3. Decide the bug class from the mechanism, such as out-of-bounds write.
4. Check that the three do not contradict each other.
5. Use the bug class for dedupe and the signal only as context.
6. Record the mapping in the record so the reasoning is visible.

## Signals

- Two crashes share SIGSEGV but have different sanitizer classes.
- A SIGABRT follows an assertion that reveals a logic bug, not a memory bug.
- The sanitizer class is more specific than the bug class you wrote.
- The signal reported differs from the one in the core file.

## Patterns

**1. Three fields**

```text
signal SIGSEGV, class heap-buffer-overflow, bug out-of-bounds read  -> distinct
```

**2. Class from mechanism**

```text
write past the end of a heap allocation  -> out-of-bounds write
```

**3. Dedupe on class**

```text
same signal but different class  -> different bugs
```

## Pitfalls

- Deduping on the signal alone and merging unrelated crashes.
- Reading SIGABRT as a memory corruption when it is an assertion failure.
- Using the sanitizer class as the bug class without interpreting the access.

## Done when

- Signal, sanitizer class and bug class are recorded as separate fields.
- Dedupe uses the bug class rather than the signal.

## References

- [CWE - memory safety weaknesses](https://cwe.mitre.org/data/definitions/119.html)
- [Clang - sanitizer class reference](https://clang.llvm.org/docs/AddressSanitizer.html)
