---
name: blocking-gate-review
description: "Treat grade failures as blocking rather than advisory, because a record with an unmet gate is not submittable and shipping it invites a triage rejection. Use when the grader reports any unmet check"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, grade, process]
---

# Blocking Gate Review

> Treat grade failures as blocking rather than advisory, because a record with an unmet gate is not submittable and shipping it invites a triage rejection

**Use when:** the grader reports any unmet check

**Avoid when:** never; the gate exists because these failures are the ones triagers reject

## Procedure

1. Run grade and read which checks are unmet.
2. Fix the record rather than the grade.
3. Re-run grade and confirm the checks pass.
4. For a deliberately accepted risk, record it as a note and keep the gate unmet.
5. Do not lower a threshold to make a record pass.
6. Submit only a record that grades as submittable.

## Signals

- A threshold was edited between runs.
- The unmet check is about the negative control.
- The record is submitted with grade C and a promise to follow up.
- The gate is skipped because the finding feels obvious.

## Patterns

**1. Fix the record**

```text
missing control  -> add the control and re-run, not a waiver
```

**2. Explicit risk**

```text
accepted: no control possible because the API has one input  -> recorded
```

**3. No threshold edits**

```text
the rule table is versioned  -> diff it
```

## Pitfalls

- Editing the rule table so the record passes.
- Submitting a partially graded record and fixing it after rejection.
- Waiving a control requirement without recording why it cannot exist.

## Done when

- Every unmet check is either fixed or recorded as an accepted risk.
- The submitted record is graded submittable.

## References

- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
- [NIST - SP 800-115 testing guide](https://csrc.nist.gov/pubs/sp/800/115/final)
