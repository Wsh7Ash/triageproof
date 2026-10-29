---
name: crash-rate-measurement
description: "Measure how often the crash reproduces and report it as a rate, because a flaky crash described as certain gets closed the first time a triager cannot reproduce it. Use when the crash involves concurrency, memory pressure or timing"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, capture, reliability]
---

# Crash Rate Measurement

> Measure how often the crash reproduces and report it as a rate, because a flaky crash described as certain gets closed the first time a triager cannot reproduce it

**Use when:** the crash involves concurrency, memory pressure or timing

**Avoid when:** the crash reproduces on every attempt from a clean state

## Procedure

1. Run the reproduction command ten times from a clean state.
2. Count successes and note the conditions of the failures.
3. Identify what varies: thread scheduling, allocator state or input ordering.
4. Reduce the variance where possible and re-measure.
5. Report both rates, before and after the fix, as N of M.
6. State the retry loop in the reproduction command if repeats are needed.

## Signals

- The first attempt after boot succeeds and later attempts fail.
- Success correlates with ASLR or thread count.
- The crash appears only under memory pressure.
- The rate improves markedly with a delay added.

## Patterns

**1. Rate before and after**

```text
default: 3/10
with --threads 1: 10/10  -> the race is the trigger
```

**2. Retry loop**

```text
for i in $(seq 10); do ./target poc.bin && break; done  -> bounded, documented
```

**3. Note the variance**

```text
heap layout is the variable; no deterministic order exists
```

## Pitfalls

- Reporting one success as deterministic and losing credibility on the retest.
- Running a hundred attempts against a shared CI runner and tripping a limit.
- Averaging a controlled and an uncontrolled run into one number.

## Done when

- A success rate with its sample size is recorded for both configurations.
- The varying condition is named in the reproduction section.

## References

- [OWASP - business logic testing](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/)
- [Clang - leak and race detection](https://clang.llvm.org/docs/ThreadSanitizer.html)
