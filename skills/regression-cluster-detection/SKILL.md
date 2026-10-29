---
name: regression-cluster-detection
description: "Watch for a signature that disappeared after a fix and returned, because a reintroduced bug is a regression and triage priority differs. Use when the target has a history of fixes and the corpus spans releases"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, cluster, regression]
---

# Regression Cluster Detection

> Watch for a signature that disappeared after a fix and returned, because a reintroduced bug is a regression and triage priority differs

**Use when:** the target has a history of fixes and the corpus spans releases

**Avoid when:** there is no prior baseline and every signature is new

## Procedure

1. Keep a baseline of signatures per released version.
2. After each release, compare the new signature set with the previous one.
3. Flag any signature that was absent from the last two releases and is present now.
4. Check the fix history for a matching patch.
5. Label the cluster as a regression and reference the original report.
6. Record the version where it disappeared and the one where it returned.

## Signals

- A signature returns after three clean releases.
- The code path was refactored, so the same bug has a slightly different signature.
- A fix was reverted for an unrelated reason.
- The regression appears only on one platform's build.

## Patterns

**1. Version baseline**

```text
1.2: 9f2c.. present
1.3: absent
1.4: present  -> regression
```

**2. Fix reference**

```text
original report #441, patched in 1.3  -> cite it
```

**3. Refactor caveat**

```text
signature shifted by one frame after the refactor  -> confirm by mechanism
```

## Pitfalls

- Treating a returning signature as new and losing the regression context.
- Missing a regression because a refactor changed the canonical frames.
- Assuming absence from one release means the bug was fixed rather than masked.

## Done when

- The returning signature is matched to an earlier report and fix.
- The versions of disappearance and return are recorded.

## References

- [Linux kernel - handling regressions](https://docs.kernel.org/process/handling-regressions.html)
- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
