---
name: oracle-pair-checking
description: "Grade a crash only when the oracle has a failing condition and a control that does not crash, because a crash alone proves a bug but not its boundary. Use when the finding is a crash, abort or sanitizer report"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, grade, oracle]
---

# Oracle Pair Checking

> Grade a crash only when the oracle has a failing condition and a control that does not crash, because a crash alone proves a bug but not its boundary

**Use when:** the finding is a crash, abort or sanitizer report

**Avoid when:** the finding is a logic flaw proven by comparing two identities instead

## Procedure

1. Record the exact command and the exit status that means success.
2. Record a nearby input that must not trigger it.
3. Run both and keep the output.
4. Check that the control reaches the same code path minus the trigger.
5. Record both outputs in the evidence bundle.
6. Grade only when both conditions are recorded.

## Signals

- The control crashes too, so the trigger is not the cause.
- The control never reaches the parser, so it proves nothing.
- The success condition is a substring that also appears in normal output.
- Exit status differs between runs of the same input.

## Patterns

**1. Status pair**

```text
success: exit 139
control: exit 0 on a 4-byte shorter field
```

**2. Reachability control**

```text
control parses the same header without the length trigger
```

**3. Recorded runs**

```text
both commands and both statuses in evidence/
```

## Pitfalls

- Using a control that fails earlier, before the buggy path.
- Matching a success string that normal output also contains.
- Recording the oracle after the run instead of before it.

## Done when

- The record carries a success condition and a negative control.
- Both were run and their outputs are in the bundle.

## References

- [NIST - SP 800-115 testing guide](https://csrc.nist.gov/pubs/sp/800/115/final)
- [OWASP - testing guide](https://owasp.org/www-project-web-security-testing-guide/)
