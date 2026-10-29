---
name: prior-report-comparison
description: "Compare against the program's own disclosed and internal reports, using signatures rather than titles, because two reports can describe one bug in unrelated words. Use when the program has a disclosure history or an internal tracker you can query"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, dedupe, program]
---

# Prior Report Comparison

> Compare against the program's own disclosed and internal reports, using signatures rather than titles, because two reports can describe one bug in unrelated words

**Use when:** the program has a disclosure history or an internal tracker you can query

**Avoid when:** the program is brand new with no prior submissions

## Procedure

1. Collect the prior reports that touch the same component.
2. Compute or extract a signature for each where a stack exists.
3. Compare signatures first, then root causes.
4. Read the closest prior report's root cause section, not just its title.
5. Record which reports were compared and the similarity.
6. If it is a duplicate, note the original id and what differs.

## Signals

- The prior title names a different function but the root cause is identical.
- The prior report was closed as informational for lack of impact.
- A prior report has the same signature with a different input.
- The program's internal tracker id appears in a public advisory.

## Patterns

**1. Signature first**

```text
9f2c.. vs 9f2c.. -> duplicate regardless of title
```

**2. Root cause second**

```text
same missing bounds check, different endpoint  -> duplicate
```

**3. Difference note**

```text
duplicate of #441; this report adds a pre-auth path  -> say so
```

## Pitfalls

- Comparing titles and missing a duplicate described in different words.
- Treating a closed informational report as non-existent.
- Filing the same bug again with a better PoC and no reference to the original.

## Done when

- Prior reports are compared by signature and root cause, and the comparison is recorded.
- A duplicate verdict names the original and what this report adds.

## References

- [HackerOne - duplicate handling](https://docs.hackerone.com/en/articles/8475114-scope)
- [Bugcrowd - duplicate policy](https://docs.bugcrowd.com/researchers/reporting-managing-submissions/)
