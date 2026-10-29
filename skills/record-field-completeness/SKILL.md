---
name: record-field-completeness
description: "Require every field the gate reads to be present, because a missing field silently weakens a check rather than failing it. Use when writing or reviewing a triage record before submission"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, grade, completeness]
---

# Record Field Completeness

> Require every field the gate reads to be present, because a missing field silently weakens a check rather than failing it

**Use when:** writing or reviewing a triage record before submission

**Avoid when:** never; an incomplete record cannot be graded

## Procedure

1. List the fields the grader requires: target, mechanism, oracle, reproduction and evidence.
2. Fill each from the artifact rather than from memory.
3. Check that the mechanism names a condition and an operation.
4. Check that the oracle has both a success and a negative condition.
5. Run validate and fix findings before grading.
6. Re-run after every edit, since grading reads the file.

## Signals

- The mechanism field reads like a title rather than a cause.
- The oracle is a single sentence with no negative case.
- Evidence paths are relative to a different directory.
- The target string is a bare hostname with no scheme or path.

## Patterns

**1. Cause plus operation**

```text
no length check before memcpy at parse.c:88  -> gradeable
```

**2. Oracle pair**

```text
success: exit 139
negative: exit 0 on truncated input
```

**3. Absolute evidence**

```text
evidence/crash.txt resolved from the record's directory
```

## Pitfalls

- Filling the mechanism with the sanitizer output and calling it a cause.
- Leaving the negative control out because the positive one was convincing.
- Assuming the grader defaults a missing field to safe when it errors instead.

## Done when

- Every required field is present and filled from an artifact.
- Validate and grade both run cleanly on the record.

## References

- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
- [Bugcrowd - vulnerability rating taxonomy](https://bugcrowd.com/vulnerability-rating-taxonomy)
