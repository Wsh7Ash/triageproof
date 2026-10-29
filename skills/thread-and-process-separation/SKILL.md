---
name: thread-and-process-separation
description: "Keep per-thread stacks apart before comparing, because a race shows different faulting threads on each run and looks like a new bug each time. Use when the crash involves threads, worker pools or multiple crashing processes"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, cluster, concurrency]
---

# Thread and Process Separation

> Keep per-thread stacks apart before comparing, because a race shows different faulting threads on each run and looks like a new bug each time

**Use when:** the crash involves threads, worker pools or multiple crashing processes

**Avoid when:** the target is single-threaded and each crash has one stack

## Procedure

1. Identify every thread's stack in the report, not just the faulting one.
2. Record which thread faulted and which threads appear in the free or alloc stacks.
3. Compare the faulting thread's stack first.
4. For races, compare the pair of stacks rather than one.
5. Record the thread count so two reports with different topology are flagged.
6. Treat a differing faulting thread as a variant, not a new bug.

## Signals

- Run one faults in thread 3 and run two in thread 7 on the same function.
- The free stack and the alloc stack belong to different threads.
- Thread count differs between the crashing host and the test host.
- The same function appears in several threads' stacks.

## Patterns

**1. Fault first**

```text
compare the stack of the thread that faulted, then the rest
```

**2. Race pair**

```text
compare (thread A stack, thread B stack) as one unit
```

**3. Topology note**

```text
8 workers vs 16 workers  -> the race window differs
```

## Pitfalls

- Concatenating all thread stacks and hashing them, so the signature changes per run.
- Comparing only the faulting thread for a race and missing the partner stack.
- Assuming thread ids are stable identifiers across runs.

## Done when

- The comparisons name which thread's stack was used.
- Races are compared as a stack pair, and topology is recorded.

## References

- [Clang - ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html)
- [GDB - thread backtraces](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Threads.html)
