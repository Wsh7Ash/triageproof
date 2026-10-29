---
name: signature-stability-check
description: "Prove the signature survives addresses, paths, thread counts and runs, because a signature that changes is not an identity. Use when before relying on signatures for dedupe across sessions or machines"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, canonicalise, verification]
---

# Signature Stability Check

> Prove the signature survives addresses, paths, thread counts and runs, because a signature that changes is not an identity

**Use when:** before relying on signatures for dedupe across sessions or machines

**Avoid when:** the crash is genuinely nondeterministic in its top frame

## Procedure

1. Capture the same crash twice with different ASLR layout.
2. Capture once from a different build directory.
3. Capture with a different thread count if the target is concurrent.
4. Compare all signatures and require equality.
5. For anything unequal, find the volatile field and strip it.
6. Record the stability tests performed.

## Signals

- Signatures differ only when the build directory changes.
- A thread id embedded in a function name changes the signature.
- The top frame alternates between two functions for one bug.
- An inline depth suffix changes between runs.

## Patterns

**1. Three-way test**

```text
run A: 9f2c..
run B: 9f2c..
other build dir: 9f2c..  -> stable
```

**2. Volatile field hunt**

```text
difference is a TID in the function name  -> strip it
```

**3. Alternating top frame**

```text
two frames alternate  -> widen identity to the shared pair
```

## Pitfalls

- Testing stability only within one session and never across builds.
- Normalising until the signature is stable but no longer discriminates.
- Ignoring an alternating top frame, which fragments the cluster at the root.

## Done when

- The signature is equal across address, path and thread variation.
- Every volatile field that was stripped is documented.

## References

- [Mozilla - signature stability](https://firefox-source-docs.mozilla.org/toolkit/crashreporter/crashreporter/index.html)
- [Sentry - grouping configuration](https://docs.sentry.io/concepts/data-management/event-grouping/)
