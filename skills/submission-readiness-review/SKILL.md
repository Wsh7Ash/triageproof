---
name: submission-readiness-review
description: "Do a final pass against the program's own requirements, because a record can be internally perfect and still miss the fields the program asks for. Use when a record grades submittable and is about to be sent"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, grade, process]
---

# Submission Readiness Review

> Do a final pass against the program's own requirements, because a record can be internally perfect and still miss the fields the program asks for

**Use when:** a record grades submittable and is about to be sent

**Avoid when:** the report is internal with no program requirements

## Procedure

1. Read the program's submission requirements.
2. Check each required field against the record.
3. Check the record against a prior accepted report's shape.
4. Confirm the reproduction runs on the program's stated environment.
5. Check that no credential, token or third-party data is in the bundle.
6. Record the review and submit.

## Signals

- The program asks for a CVSS vector the record lacks.
- The record is written for a different environment than the program's.
- Evidence contains a real user's session token.
- The record's steps assume tooling the triager will not have.

## Patterns

**1. Requirement checklist**

```text
program fields vs record fields  -> gap list
```

**2. Environment match**

```text
reproduced on the program's stated build
```

**3. Redaction**

```text
tokens and personal data removed before bundling
```

## Pitfalls

- Submitting a well-graded record that ignores the program's template.
- Leaving a captured session token in the evidence bundle.
- Assuming the triager will install your toolchain to reproduce.

## Done when

- Every program requirement is checked against the record.
- The bundle contains no credentials or third-party personal data.

## References

- [HackerOne - report writing](https://docs.hackerone.com/en/articles/8475114-scope)
- [Bugcrowd - submission guidelines](https://docs.bugcrowd.com/researchers/reporting-managing-submissions/)
