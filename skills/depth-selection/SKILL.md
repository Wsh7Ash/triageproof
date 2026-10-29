---
name: depth-selection
description: "Choose how many canonical frames define identity, because one frame is too shallow to discriminate and twenty makes two reports of one bug differ. Use when calibrating the signature function for a target"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, canonicalise, signature]
---

# Depth Selection

> Choose how many canonical frames define identity, because one frame is too shallow to discriminate and twenty makes two reports of one bug differ

**Use when:** calibrating the signature function for a target

**Avoid when:** the stack has a single frame and depth has no meaning

## Procedure

1. Collect a sample of known-distinct crash reports.
2. Collect at least two reports of the same known bug.
3. Compute signatures at depths three, five and eight.
4. Check that same-bug reports collapse and distinct bugs stay separate.
5. Pick the smallest depth that achieves both.
6. Record the chosen depth with the signature and keep it fixed.

## Signals

- At depth three, unrelated bugs collide on a shared prefix.
- At depth eight, one bug splits because a tail frame differs.
- A depth change re-baselines every stored signature.
- Depth five works for callers but fails for parser bugs with a fixed prologue.

## Patterns

**1. Collision test**

```text
two distinct bugs, depth 3 -> same signature  -> too shallow
```

**2. Split test**

```text
one bug, depth 8 -> two signatures  -> too deep
```

**3. Fix the depth**

```text
depth 5 recorded in the record and in the tool default
```

## Pitfalls

- Choosing a depth without testing it against known duplicates and known distinct pairs.
- Changing depth mid-engagement and losing comparability with earlier reports.
- Using a large depth to be safe, which fragments every cluster.

## Done when

- The depth is chosen by testing same-bug and distinct-bug pairs.
- The depth is recorded and applied to every report of the target.

## References

- [Mozilla - crash signature rules](https://firefox-source-docs.mozilla.org/toolkit/crashreporter/crashreporter/index.html)
- [Sentry - stack trace grouping](https://docs.sentry.io/concepts/data-management/event-grouping/)
