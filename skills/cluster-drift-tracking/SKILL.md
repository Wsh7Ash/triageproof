---
name: cluster-drift-tracking
description: "Track how a cluster's membership changes over time, because a cluster that grows steadily is a different problem from one that spiked once. Use when crash volume is monitored across releases or over weeks"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, cluster, trend]
---

# Cluster Drift Tracking

> Track how a cluster's membership changes over time, because a cluster that grows steadily is a different problem from one that spiked once

**Use when:** crash volume is monitored across releases or over weeks

**Avoid when:** the corpus is a one-off snapshot with no time dimension

## Procedure

1. Record each cluster's size per time bucket.
2. Distinguish a spike from a steady climb.
3. Correlate a change with a release, a config change or a traffic pattern.
4. Flag clusters whose growth outpaces traffic growth.
5. Record the correlation next to the cluster label.
6. Re-check after a fix that the growth stops.

## Signals

- A cluster doubles the day a new feature ships.
- Growth tracks traffic exactly, suggesting normal load rather than a new bug.
- A cluster appears only on one region's build.
- Volume drops after a deploy without a fix note.

## Patterns

**1. Per-bucket size**

```text
week 1: 3, week 2: 4, week 3: 61  -> a spike, not steady load
```

**2. Correlate**

```text
spike starts at the 1.4 deploy  -> likely regression
```

**3. Normalise**

```text
traffic x3, crashes x3  -> rate unchanged
```

## Pitfalls

- Treating a traffic-driven increase as a new bug.
- Missing a steady climb that a single-week view hides.
- Attributing growth to a release without checking traffic at the same time.

## Done when

- Cluster size is tracked per time bucket and normalised against traffic.
- Each change is correlated with a release, config or traffic shift.

## References

- [Mozilla - crash statistics](https://firefox-source-docs.mozilla.org/toolkit/crashreporter/crashreporter/index.html)
- [Sentry - issue trends](https://docs.sentry.io/product/issues/)
