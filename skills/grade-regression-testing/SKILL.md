---
name: grade-regression-testing
description: "Keep a graded set of known records as tests, so a change to the rules cannot silently start passing records it should reject. Use when modifying the grader, the validator or the similarity comparison"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, grade, testing]
---

# Grade Regression Testing

> Keep a graded set of known records as tests, so a change to the rules cannot silently start passing records it should reject

**Use when:** modifying the grader, the validator or the similarity comparison

**Avoid when:** never after the first record exists; graders drift like anything else

## Procedure

1. Keep a record that must grade as submittable and one that must not.
2. Include a record for each blocking rule.
3. Run the set before and after any rule change.
4. Add a case for every rule you add.
5. Assert the exact grade, not just pass or fail.
6. Check the tests in CI so a fix cannot loosen a gate unnoticed.

## Signals

- A rule change makes a previously rejected record pass.
- The test set has no failing example for a new rule.
- Only the submittable path is tested, so blocking is untested.
- A refactor changes scores and no test notices.

## Patterns

**1. Paired cases**

```text
good record grades A, missing-control record grades below threshold  -> one test
```

**2. Rule coverage**

```text
one failing record per blocking rule
```

**3. Exact grade**

```text
assert grade == 'A', not grade is not None
```

## Pitfalls

- Testing only that grading does not raise.
- Adding a rule with no corresponding failure test.
- Updating the expected grade to match new behaviour without checking it is right.

## Done when

- Every blocking rule has a record that fails on it.
- Tests assert exact grades and run in CI.

## References

- [pytest - parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
