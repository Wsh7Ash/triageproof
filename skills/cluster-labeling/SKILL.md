---
name: cluster-labeling
description: "Give every cluster a human name tied to the faulting function, so triage discussions refer to one bug instead of a hex signature. Use when a cluster set will be reviewed by more than one person"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, cluster, reporting]
---

# Cluster Labeling

> Give every cluster a human name tied to the faulting function, so triage discussions refer to one bug instead of a hex signature

**Use when:** a cluster set will be reviewed by more than one person

**Avoid when:** the corpus is a single report with no clustering

## Procedure

1. Take the faulting frame and the next two canonical frames.
2. Name the cluster by function plus the failure mode.
3. Keep the signature as the machine key alongside the label.
4. Check that no two clusters share a label.
5. Use the label in every report, ticket and retest note.
6. Rename only with a note explaining why, since tickets reference the old name.

## Signals

- Two clusters have the same label but different signatures.
- A label describes the symptom rather than the function.
- Tickets reference a signature nobody can read.
- A rename breaks links in earlier reports.

## Patterns

**1. Function plus mode**

```text
parse_header: heap overflow on length field  -> readable and specific
```

**2. Machine key kept**

```text
label for humans, 9f2c.. for the tooling
```

**3. Uniqueness check**

```text
labels are unique across clusters  -> asserted
```

## Pitfalls

- Labelling by sanitizer class only, so three distinct overflow bugs share a name.
- Renaming a cluster without noting it and orphaning existing tickets.
- Dropping the signature once a label exists, losing machine comparability.

## Done when

- Each cluster has a unique label naming its function and failure mode.
- The signature remains the machine key in the same report.

## References

- [Mozilla - crash signature naming](https://firefox-source-docs.mozilla.org/toolkit/crashreporter/crashreporter/index.html)
- [Sentry - issue titles](https://docs.sentry.io/concepts/data-management/event-grouping/)
