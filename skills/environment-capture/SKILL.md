---
name: environment-capture
description: "Record the runtime conditions that make the crash happen, because a bug that needs a specific locale, thread count or allocator is not reproducible without them. Use when the crash is intermittent, or it involves concurrency, memory pressure or configuration"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, capture, environment]
---

# Environment Capture

> Record the runtime conditions that make the crash happen, because a bug that needs a specific locale, thread count or allocator is not reproducible without them

**Use when:** the crash is intermittent, or it involves concurrency, memory pressure or configuration

**Avoid when:** the crash reproduces identically on any default configuration

## Procedure

1. List the environment variables the program reads on the crashing path.
2. Record thread and worker counts, ulimits and memory limits.
3. Record the allocator and any sanitizer options in effect.
4. Record locale, timezone and filesystem type where relevant.
5. Capture the container or VM image digest if the target is containerised.
6. Attach the environment dump to the evidence bundle as its own kind.

## Signals

- The crash disappears when the container is given more memory.
- It only reproduces with a specific thread count or worker pool size.
- A different locale changes parsing and reaches the bug.
- The sanitizer options were set only in the shell that produced the crash.

## Patterns

**1. Dump the environment**

```text
env | sort > evidence/log/env.txt  -> the conditions, verbatim
```

**2. Resource limits**

```text
ulimit -a, cgroup memory.max  -> the pressure that triggers the bug
```

**3. Allocator**

```text
MALLOC_ARENA_MAX, ASAN_OPTIONS  -> part of the reproduction
```

## Pitfalls

- Recording only the OS version and calling the environment captured.
- Reproducing with a debug shell whose variables differ from the service's.
- Ignoring a cgroup memory limit that is the actual trigger.

## Done when

- Environment variables, limits and allocator settings are saved as an artifact.
- Any condition that changes the outcome is named in the reproduction section.

## References

- [Linux - proc and cgroup limits](https://man7.org/linux/man-pages/man7/cgroups.7.html)
- [Clang - ASAN options](https://clang.llvm.org/docs/AddressSanitizer.html#flags)
