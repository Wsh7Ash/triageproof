---
name: bundle-verification-report
description: "Emit a verification artifact that names every check and its result, because a bundle that verifies silently cannot be audited when someone disputes it. Use when verify runs as part of grading or submission"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, bundle, reporting]
---

# Bundle Verification Report

> Emit a verification artifact that names every check and its result, because a bundle that verifies silently cannot be audited when someone disputes it

**Use when:** verify runs as part of grading or submission

**Avoid when:** never; the report is what an auditor reads

## Procedure

1. Name each check: manifest present, hashes match, no missing files, no extras.
2. Record pass or fail per check with the specific path on failure.
3. Include the bundle digest and the verification timestamp.
4. Write the report next to the bundle, not inside it.
5. Fail the process if any check failed.
6. Keep the report with the submission.

## Signals

- Verification prints nothing on success, so no artifact exists.
- The failure names a check but not the file.
- The report lives inside the hashed bundle and changes it.
- A disputed submission has no verification record.

## Patterns

**1. Named checks**

```text
manifest: pass, hashes: fail (evidence/trace.txt), extras: pass
```

**2. Path on failure**

```text
fail with the specific path, never a generic message
```

**3. Outside the bundle**

```text
report at bundle/../verification.json  -> does not alter the digest
```

## Pitfalls

- Writing the report inside the bundle and invalidating its digest.
- Reporting only a boolean with no per-check detail.
- Continuing to submission after a failed check.

## Done when

- Every check has a named result and failures name the path.
- The report is stored outside the hashed bundle.

## References

- [NIST - SP 800-86 forensic techniques](https://csrc.nist.gov/pubs/sp/800/86/final)
- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
