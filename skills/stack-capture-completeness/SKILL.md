---
name: stack-capture-completeness
description: "Capture the full stack rather than the first three frames, because the frame that explains the bug is often deeper than the crash site. Use when the sanitizer or debugger is configured with a default trace depth"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, capture, stack]
---

# Stack Capture Completeness

> Capture the full stack rather than the first three frames, because the frame that explains the bug is often deeper than the crash site

**Use when:** the sanitizer or debugger is configured with a default trace depth

**Avoid when:** the crash is a single-frame abort with no callers of interest

## Procedure

1. Check the configured trace depth in the sanitizer or debugger options.
2. Raise it until the trace reaches the request or input entry point.
3. Save the full trace, then work from a truncated copy for reading.
4. Confirm the top frame is the fault and the bottom is a real entry point.
5. Record the depth used, since it affects future comparisons.
6. Compare the frame count with the expected call path from the source.

## Signals

- The trace ends in the allocator with no caller visible.
- The bottom frame is libc startup rather than the application's entry.
- Two reports of one bug show different frame counts because of the depth setting.
- ASAN_OPTIONS shows a non-default fast_unwind limit.

## Patterns

**1. Raise the depth**

```text
ASAN_OPTIONS=fast_unwind_on_malloc=0:malloc_context_size=30  -> full trace
```

**2. Entry point check**

```text
bottom frame is main or a request handler  -> the path is complete
```

**3. Depth in the record**

```text
trace depth 30, frames kept for signature 5  -> both stated
```

## Pitfalls

- Reporting the top three frames and missing the caller that passes the bad length.
- Comparing traces captured with different depth settings as if they were equal.
- Truncating the trace before saving it, so the deep frames are unrecoverable.

## Done when

- The saved trace reaches an application entry point.
- The capture depth is recorded with the artifact.

## References

- [Clang - sanitizer flags](https://clang.llvm.org/docs/AddressSanitizer.html#flags)
- [GDB - backtrace settings](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Backtrace.html)
