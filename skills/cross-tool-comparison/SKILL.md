---
name: cross-tool-comparison
description: "Compare stacks captured by different tools, because one report from gdb and one from a minidump describe the same bug in incompatible text. Use when the corpus mixes gdb, lldb, sanitizer and minidump reports"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, cluster, interop]
---

# Cross Tool Comparison

> Compare stacks captured by different tools, because one report from gdb and one from a minidump describe the same bug in incompatible text

**Use when:** the corpus mixes gdb, lldb, sanitizer and minidump reports

**Avoid when:** every report came from the same harness with the same formatter

## Procedure

1. Normalise each report into frames before comparing anything.
2. Compare on function and file, ignoring the module when only one side has it.
3. Check that the sanitizer class matches when both reports carry one.
4. Verify the comparison on a known pair from two different tools.
5. Record which tool produced each report in the cluster output.
6. Treat a zero score as a canonicalisation gap until proven otherwise.

## Signals

- gdb reports include paths and no module; minidumps include modules and no paths.
- The same bug scores 0.0 because one side has a module prefix.
- A sanitizer report names the class while a raw signal report does not.
- Frame numbering differs but the function order matches.

## Patterns

**1. Module optional**

```text
app!parse_header vs parse_header  -> compare the function only
```

**2. File tiebreak**

```text
both sides have a file: require the basename to agree
```

**3. Kind gate**

```text
heap-use-after-free vs stack-buffer-overflow  -> never the same bug
```

## Pitfalls

- Comparing raw text from two tools and concluding the bugs differ.
- Requiring a module name that only one tool records.
- Letting a missing sanitizer class merge two different memory bugs.

## Done when

- A known same-bug pair from two tools compares as a duplicate.
- The source tool is recorded for every report in a cluster.

## References

- [Microsoft - minidump format](https://learn.microsoft.com/en-us/windows/win32/api/minidumpapiset/)
- [LLDB - stack frames](https://lldb.llvm.org/use/map.html)
