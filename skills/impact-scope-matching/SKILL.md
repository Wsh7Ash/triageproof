---
name: impact-scope-matching
description: "Tie the claimed impact to what the reproduction actually shows, because a crash is not remote code execution no matter how it feels. Use when writing or grading the impact statement"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, grade, impact]
---

# Impact Scope Matching

> Tie the claimed impact to what the reproduction actually shows, because a crash is not remote code execution no matter how it feels

**Use when:** writing or grading the impact statement

**Avoid when:** never; impact is what the program pays for

## Procedure

1. State what the reproduction demonstrates: crash, read, write or control flow.
2. State what an attacker gains from exactly that, with no extra steps assumed.
3. Separate demonstrated impact from possible impact.
4. Note the preconditions: authentication, network position, configuration.
5. Grade the demonstrated impact, and list the speculative one separately.
6. Remove any impact claim the evidence does not support.

## Signals

- The record claims RCE from a null dereference.
- The impact assumes a second bug that is not demonstrated.
- Preconditions are in a footnote rather than next to the claim.
- The severity is argued from the CVSS vector rather than the evidence.

## Patterns

**1. Demonstrated**

```text
read of 8 bytes past the buffer, value not returned to the attacker  -> information disclosure limited
```

**2. Preconditions**

```text
requires an authenticated editor role  -> state it up front
```

**3. Speculative split**

```text
possible: heap grooming to control the write; not shown
```

## Pitfalls

- Escalating a crash to RCE without a control-flow demonstration.
- Hiding a strong precondition to keep the severity high.
- Grading the worst case the bug could theoretically reach.

## Done when

- Demonstrated and speculative impact are stated separately.
- Preconditions are next to the impact claim.

## References

- [FIRST - CVSS v3.1 specification](https://www.first.org/cvss/v3-1/specification-document)
- [Bugcrowd - vulnerability rating taxonomy](https://bugcrowd.com/vulnerability-rating-taxonomy)
