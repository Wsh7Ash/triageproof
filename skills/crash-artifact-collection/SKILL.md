---
name: crash-artifact-collection
description: "Collect the four artifacts every crash needs before triage starts, because a stack without a version or a build id cannot be deduped or retested. Use when a crash has been observed and nothing has been saved yet"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, capture, evidence]
---

# Crash Artifact Collection

> Collect the four artifacts every crash needs before triage starts, because a stack without a version or a build id cannot be deduped or retested

**Use when:** a crash has been observed and nothing has been saved yet

**Avoid when:** the artifact set is already complete and hashed, and you are only re-reading it

## Procedure

1. Save the raw crash output exactly as the runtime produced it, before any editing.
2. Record the exact version, build id or commit the binary was built from.
3. Save the command that produced the crash, including environment variables and input.
4. Record the platform, architecture and sanitizer or debug settings.
5. Copy the files into one evidence directory organised by kind.
6. Hash the directory before analysis, so later edits are detectable.

## Signals

- The stack was pasted into a chat and the original file is gone.
- The version was taken from the documentation rather than the running binary.
- The reproduction command references an input file that was never saved.
- The crash only reproduces with a flag nobody wrote down.

## Patterns

**1. Four artifacts**

```text
crash log, stack, reproduction command, version output  -> the minimum set
```

**2. Save before editing**

```text
cp crash.log evidence/crash/segv-raw.log  -> then analyse a copy
```

**3. Hash early**

```text
triageproof bundle evidence/  -> the baseline for every later check
```

## Pitfalls

- Cleaning up a stack trace before saving it, destroying the evidence of the original output.
- Recording the package version while the binary is a local build from an unknown commit.
- Leaving the crashing input out of the evidence set so nobody can reproduce it.

## Done when

- Crash output, version, reproduction command and environment are all saved as files.
- The directory is hashed before any analysis edits.

## References

- [Clang - AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html)
- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
