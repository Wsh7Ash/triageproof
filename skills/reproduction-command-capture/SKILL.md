---
name: reproduction-command-capture
description: "Save the exact command line that crashes the target, because a description of the steps is not a reproduction and a triager cannot run prose. Use when writing the reproduction section of any crash report"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, capture, reproduction]
---

# Reproduction Command Capture

> Save the exact command line that crashes the target, because a description of the steps is not a reproduction and a triager cannot run prose

**Use when:** writing the reproduction section of any crash report

**Avoid when:** the crash is triggered by an external service you cannot script, which needs its own note

## Procedure

1. Write the command as a single line with every flag and argument.
2. Reference input files by relative path inside the evidence bundle.
3. Substitute credentials and hostnames with documented placeholders.
4. Run the command from a clean shell and confirm it still crashes.
5. Record the expected output line that indicates the crash.
6. Store the command in a file so the report copies it verbatim.

## Signals

- The command needs an environment variable that is not in the bundle.
- It fails on a fresh checkout because an input file is missing.
- The expected output is not stated, so success is ambiguous.
- The command depends on a shell history entry nobody saved.

## Patterns

**1. One line**

```text
./target --parse poc.bin --threads 8  -> every flag present
```

**2. Relative inputs**

```text
input file lives at evidence/repro/poc.bin  -> the bundle is self-contained
```

**3. Expected output**

```text
AddressSanitizer: heap-use-after-free  -> the line that means it worked
```

## Pitfalls

- Writing 'run the parser with a malformed file' and calling it a reproduction.
- Leaving an absolute path that only exists on your machine.
- Omitting the flag that makes the crash reproducible.

## Done when

- A single command reproduces the crash from the evidence bundle alone.
- The expected crash output is documented next to the command.

## References

- [OWASP - proof of concept guidance](https://owasp.org/www-project-web-security-testing-guide/)
- [Clang - AddressSanitizer example](https://clang.llvm.org/docs/AddressSanitizer.html)
