---
name: cluster-size-triage
description: "Order work by cluster size and reachability rather than by report arrival, because one signature with two hundred hits matters more than forty singletons. Use when the corpus is large enough that not everything can be triaged at once"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, cluster, prioritisation]
---

# Cluster Size Triage

> Order work by cluster size and reachability rather than by report arrival, because one signature with two hundred hits matters more than forty singletons

**Use when:** the corpus is large enough that not everything can be triaged at once

**Avoid when:** the corpus has fewer than a handful of reports

## Procedure

1. Sort clusters by member count.
2. Annotate each with reachability, pre-auth or authenticated.
3. Rank by size and reachability together, not size alone.
4. Check whether the largest cluster is a crash on a path users cannot reach.
5. Start with the largest reachable cluster and record the ordering.
6. Re-rank when a new report changes a cluster's size.

## Signals

- The largest cluster comes from a debug-only code path.
- A small cluster is pre-auth and reachable from the internet.
- One signature dominates because a retry loop multiplies reports.
- Report volume reflects scraping, not impact.

## Patterns

**1. Size plus reach**

```text
9f2c.. x210, pre-auth  -> first
4a11.. x40, local-only   -> later
```

**2. Deduplicate the volume**

```text
200 reports from one loop are one bug, not 200 findings
```

**3. Ordering recorded**

```text
triage order and the reason for it
```

## Pitfalls

- Working the loudest cluster first when it is unreachable in production.
- Letting a retry loop inflate a cluster and distort priority.
- Ignoring a small pre-auth cluster because the queue is ordered by volume.

## Done when

- Clusters are ranked by size and reachability with the ordering recorded.
- Report volume is normalised against retries before ranking.

## References

- [Bugcrowd - vulnerability rating taxonomy](https://bugcrowd.com/vulnerability-rating-taxonomy)
- [FIRST - CVSS v3.1 specification](https://www.first.org/cvss/v3-1/specification-document)
