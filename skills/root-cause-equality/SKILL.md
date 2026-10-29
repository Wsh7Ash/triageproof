---
name: root-cause-equality
description: "Decide duplicate status on the mechanism rather than the entry point, because two endpoints calling one broken function are one bug. Use when the crashes share a suspicious function but arrive through different features"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, dedupe, root-cause]
---

# Root Cause Equality

> Decide duplicate status on the mechanism rather than the entry point, because two endpoints calling one broken function are one bug

**Use when:** the crashes share a suspicious function but arrive through different features

**Avoid when:** the two crashes are in genuinely unrelated code with no shared function

## Procedure

1. Write the mechanism for each crash in one sentence: what is unchecked and where.
2. Compare the sentences, not the endpoints.
3. Check whether both reach the same line with the same missing check.
4. If the mechanism is identical, treat them as one bug with two entry points.
5. If the mechanisms differ, keep them separate even when frames overlap.
6. Record both mechanisms in the dedupe block.

## Signals

- Two endpoints both call parse_header with an attacker-controlled length.
- The same line appears in both stacks but with different callers.
- One is a missing bounds check and the other is a use-after-free in the same function.
- The bugs share a frame but not the faulting operation.

## Patterns

**1. One sentence each**

```text
no length check before memcpy at parse.c:88  -> identical mechanism
```

**2. Entry points differ**

```text
/upload and /import both reach it  -> one bug, two paths
```

**3. Different operation**

```text
read past the end vs write past the end  -> separate bugs
```

## Pitfalls

- Merging two bugs because they share a frame in a busy function.
- Splitting one bug by endpoint and filing the same defect twice.
- Describing the mechanism as a symptom, such as a crash in the parser.

## Done when

- Each crash has a one-sentence mechanism and they are compared explicitly.
- The duplicate verdict follows mechanism equality, not frame overlap alone.

## References

- [CWE - memory safety](https://cwe.mitre.org/data/definitions/119.html)
- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
