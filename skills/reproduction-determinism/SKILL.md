---
name: reproduction-determinism
description: "Require the reproduction to succeed repeatedly from a clean state, because a crash that fires one run in five is a different claim from a deterministic one. Use when the reproduction involves timing, memory layout or accumulated state"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, grade, reproduction]
---

# Reproduction Determinism

> Require the reproduction to succeed repeatedly from a clean state, because a crash that fires one run in five is a different claim from a deterministic one

**Use when:** the reproduction involves timing, memory layout or accumulated state

**Avoid when:** the crash is trivially deterministic and one run is enough

## Procedure

1. Note whether the reproduction is deterministic or probabilistic.
2. For probabilistic crashes, record the observed rate over a stated number of runs.
3. Reset state between runs.
4. Record the seed or environment when it affects the outcome.
5. State the rate in the record rather than implying certainty.
6. Grade a probabilistic crash lower than a deterministic one at equal impact.

## Signals

- The crash needs the heap in a particular shape.
- The rate changes with the number of worker threads.
- It never reproduces on a fresh container but always does after a warm-up.
- The record says always without a run count.

## Patterns

**1. Rate stated**

```text
7/10 runs on a warmed heap  -> probabilistic, say so
```

**2. Seed pinned**

```text
PYTHONHASHSEED=0  -> removes one source of variance
```

**3. Clean state**

```text
fresh container per run  -> deterministic or not, recorded
```

## Pitfalls

- Claiming determinism after a single successful run.
- Retrying until it crashes and reporting the successful attempt only.
- Leaving state from a previous run and calling the reproduction clean.

## Done when

- The record states deterministic or a rate with a run count.
- Reset and seed steps are recorded where they matter.

## References

- [NIST - SP 800-115 testing guide](https://csrc.nist.gov/pubs/sp/800/115/final)
- [Clang - sanitizer reproducibility](https://clang.llvm.org/docs/AddressSanitizer.html)
