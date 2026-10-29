---
name: reopened-issue-check
description: "Check whether a closed report on the same signature was reopened or fixed incompletely, because a partial fix is a new report with an old id. Use when the matching report was closed as fixed and the crash still occurs"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, dedupe, process]
---

# Reopened Issue Check

> Check whether a closed report on the same signature was reopened or fixed incompletely, because a partial fix is a new report with an old id

**Use when:** the matching report was closed as fixed and the crash still occurs

**Avoid when:** the prior report is still open and clearly the same bug

## Procedure

1. Find the prior report and its closure reason.
2. Check whether the fix commit is in the deployed build.
3. Re-run the reproduction on the deployed build.
4. If it still crashes, identify whether the same line or a sibling is at fault.
5. Ask for a reopen or file a variant with the new evidence.
6. Record the prior id and the closure reason in the new record.

## Signals

- The fix commit is absent from the deployed build.
- The same function crashes but at a different offset.
- The prior fix guarded one branch and left the sibling open.
- The report was closed as unable to reproduce.

## Patterns

**1. Closure reason**

```text
closed as fixed in 2.3.1, deployed 2.3.0  -> still vulnerable
```

**2. Same line or sibling**

```text
same line: ask for reopen
sibling: file a variant with the id
```

**3. Evidence**

```text
reproduction output on the deployed build plus the fix commit id
```

## Pitfalls

- Filing a fresh report with no reference to the closed one.
- Assuming a closed-as-fixed report means the deployed build is patched.
- Reopening with no new evidence, which reads as a duplicate complaint.

## Done when

- The prior report, its closure reason and the deployed build are all recorded.
- The new evidence distinguishes a reopen from a variant.

## References

- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
- [HackerOne - report states](https://docs.hackerone.com/en/articles/8475114-scope)
