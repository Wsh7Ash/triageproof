---
name: duplicate-evidence-writing
description: "Document what you compared and what differs, so a duplicate verdict is auditable and a variant does not get closed by accident. Use when deciding that a new crash matches an existing report"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, dedupe, evidence]
---

# Duplicate Evidence Writing

> Document what you compared and what differs, so a duplicate verdict is auditable and a variant does not get closed by accident

**Use when:** deciding that a new crash matches an existing report

**Avoid when:** the crash is clearly new and no comparison was needed

## Procedure

1. List the reports and advisories you compared against, by id.
2. Record the similarity score or signature equality for each.
3. State what is identical: mechanism, function, access type.
4. State what differs: input, endpoint, reachability, build.
5. Conclude duplicate or variant with the reason.
6. Attach the comparison output to the evidence bundle.

## Signals

- The verdict says duplicate but no report id is listed.
- A variant is marked duplicate without noting the new path.
- The comparison was done from memory with no artifact.
- The differing field is exactly what makes the new report valuable.

## Patterns

**1. Comparison table**

```text
#441: signature equal, mechanism equal, new pre-auth path  -> variant
```

**2. Score recorded**

```text
0.92 similarity against #441, threshold 0.6
```

**3. Difference named**

```text
this report reaches it before authentication
```

## Pitfalls

- Closing a report as duplicate with no reference to the original.
- Marking a variant duplicate and losing the escalation it represents.
- Relying on a memory of the prior report instead of its text.

## Done when

- The compared ids, scores and differences are recorded in the record.
- The verdict distinguishes duplicate from variant with a reason.

## References

- [HackerOne - duplicate handling](https://docs.hackerone.com/en/articles/8475114-scope)
- [Bugcrowd - duplicate policy](https://docs.bugcrowd.com/researchers/reporting-managing-submissions/)
