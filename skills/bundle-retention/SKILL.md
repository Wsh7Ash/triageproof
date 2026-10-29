---
name: bundle-retention
description: "Keep the verified bundle for the life of the report, because a retest months later needs the exact bytes that were submitted. Use when a report has been submitted and may be retested or disputed"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, bundle, process]
---

# Bundle Retention

> Keep the verified bundle for the life of the report, because a retest months later needs the exact bytes that were submitted

**Use when:** a report has been submitted and may be retested or disputed

**Avoid when:** the program's policy requires immediate deletion of captured data

## Procedure

1. Store the verified bundle with its digest and verification report.
2. Keep it out of the working tree if it contains sensitive data.
3. Record where it is stored in the record.
4. Follow the program's retention and deletion policy where one exists.
5. Delete only after the report is closed and the retest window has passed.
6. Never delete the digest, even when the evidence is deleted.

## Signals

- The retest asks for evidence that was overwritten.
- The bundle lives in a temp directory that a reboot clears.
- Sensitive captures are committed to a public repository.
- Deletion happened before the disclosure window closed.

## Patterns

**1. Digest survives**

```text
evidence deleted per policy, digest and verification report kept
```

**2. Out of tree**

```text
stored outside the repo when it holds secrets
```

**3. Policy first**

```text
program deletion requirement overrides retention
```

## Pitfalls

- Keeping sensitive captures in a public repo indefinitely.
- Deleting the digest along with the evidence, losing the audit trail.
- Storing the only copy in a temporary directory.

## Done when

- The bundle's location and retention decision are recorded.
- The digest survives any evidence deletion.

## References

- [NIST - SP 800-86 forensic techniques](https://csrc.nist.gov/pubs/sp/800/86/final)
- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
