---
name: signature-bucketing
description: "Group reports by exact signature before doing anything fuzzy, because identical canonical stacks are the cheapest and most trustworthy duplicates. Use when there are more than a handful of crash reports to organise"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, cluster, signature]
---

# Signature Bucketing

> Group reports by exact signature before doing anything fuzzy, because identical canonical stacks are the cheapest and most trustworthy duplicates

**Use when:** there are more than a handful of crash reports to organise

**Avoid when:** every report has a unique signature and bucketing produces singletons only

## Procedure

1. Compute a signature for every report with one depth and kind.
2. Group by exact signature and sort groups by size.
3. Treat exact groups as confirmed duplicates without further comparison.
4. Send the remaining singletons to fuzzy comparison.
5. Record the number of exact groups and singletons.
6. Recompute after any canonicalisation change.

## Signals

- One signature covers more than half the reports.
- A group of one has a signature that differs by a single frame.
- Two reports of the same crash land in different buckets.
- Bucket sizes change after a parser update.

## Patterns

**1. Exact first**

```text
9f2c.. x12, 4a11.. x3, singletons 40  -> 12 confirmed before fuzzy work
```

**2. Order by size**

```text
largest cluster first  -> triage the noisy bug once
```

**3. Singletons next**

```text
40 singletons  -> run similarity against the big groups
```

## Pitfalls

- Going straight to fuzzy matching and paying for comparisons exact equality already answers.
- Bucketting across different depths, which mixes incompatible signatures.
- Assuming a singleton is a new bug rather than a canonicalisation gap.

## Done when

- Exact groups and singletons are counted separately.
- Singletons are examined for canonicalisation gaps before being called new.

## References

- [Sentry - event grouping](https://docs.sentry.io/concepts/data-management/event-grouping/)
- [Mozilla - crash signature rules](https://firefox-source-docs.mozilla.org/toolkit/crashreporter/crashreporter/index.html)
