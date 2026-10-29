---
name: similarity-threshold-calibration
description: "Set the duplicate threshold from known pairs rather than intuition, because too low merges distinct bugs and too high files duplicates. Use when the tooling offers a configurable similarity threshold and a corpus of known reports"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, cluster, calibration]
---

# Similarity Threshold Calibration

> Set the duplicate threshold from known pairs rather than intuition, because too low merges distinct bugs and too high files duplicates

**Use when:** the tooling offers a configurable similarity threshold and a corpus of known reports

**Avoid when:** every report has an identical canonical signature and no fuzzy matching is needed

## Procedure

1. Assemble pairs you know are the same bug and pairs you know are different.
2. Compute similarity for every pair.
3. Find the separation between the two distributions.
4. Choose a threshold inside the gap and a stronger one for automatic merges.
5. Record both values and the pairs that justified them.
6. Re-calibrate when the canonicalisation rules change.

## Signals

- Same-bug pairs score 0.6 and different pairs score 0.55, so there is no honest threshold.
- A threshold of 0.6 merges two bugs that differ in the faulting function.
- Automatic merges happen at 0.85 while the review band is 0.6 to 0.85.
- The distribution differs per target, so one global threshold is wrong.

## Patterns

**1. Two thresholds**

```text
probable at 0.6, duplicate at 0.85  -> review band in between
```

**2. Known pairs**

```text
same: 0.92, 1.0, 0.88
different: 0.11, 0.33  -> clean separation
```

**3. Per-target values**

```text
parser: 0.6
service: 0.75 because of shared middleware frames
```

## Pitfalls

- Choosing 0.5 because it sounds reasonable and merging everything.
- Setting the automatic-merge threshold at the review threshold.
- Reusing one target's threshold on another with a different frame shape.

## Done when

- The threshold is justified by same-bug and different-bug pairs.
- Automatic merge and review thresholds are distinct and recorded.

## References

- [Sentry - grouping thresholds](https://docs.sentry.io/concepts/data-management/event-grouping/)
- [Mozilla - duplicate detection](https://firefox-source-docs.mozilla.org/toolkit/crashreporter/crashreporter/index.html)
