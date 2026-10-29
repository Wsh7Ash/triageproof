---
name: record-immutability
description: "Freeze the record once evidence is hashed, because editing a finding after its bundle digest is recorded breaks the only link between the claim and the artifact. Use when a record has been graded and its evidence hashed"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, grade, integrity]
---

# Record Immutability

> Freeze the record once evidence is hashed, because editing a finding after its bundle digest is recorded breaks the only link between the claim and the artifact

**Use when:** a record has been graded and its evidence hashed

**Avoid when:** the bundle has not been hashed yet and the record is still being written

## Procedure

1. Hash the evidence bundle and record the digest in the record.
2. Treat any later edit as a new revision with its own digest.
3. Never edit a record in place after submission.
4. Record corrections as an addendum with the original digest referenced.
5. Check the digest before any retest.
6. Note the revision in the record's history.

## Signals

- The digest in the record does not match the bundle on disk.
- The record was edited after the triager opened it.
- A correction was made in place with no revision history.
- Two copies of the record exist with different evidence.

## Patterns

**1. Digest link**

```text
bundle sha256 in the record  -> verify before retest
```

**2. Addendum**

```text
revision 2: original digest 4f2c.., correction below
```

**3. No in-place edits**

```text
submit, then append; never rewrite
```

## Pitfalls

- Fixing a typo in the record after hashing and invalidating the digest.
- Re-hashing the bundle to match the edited record.
- Keeping no revision history so the triager cannot tell what changed.

## Done when

- The record carries the bundle digest and any revision is an addendum.
- The digest is verified before a retest.

## References

- [NIST - SP 800-86 forensic techniques](https://csrc.nist.gov/pubs/sp/800/86/final)
- [RFC 8785 - JSON canonicalization](https://www.rfc-editor.org/rfc/rfc8785)
