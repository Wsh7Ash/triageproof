---
name: bundle-manifest-writing
description: "Write a manifest that lists every evidence file with its hash, because a bundle without one cannot be checked for completeness or tampering. Use when assembling the evidence directory for a report"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, bundle, evidence]
---

# Bundle Manifest Writing

> Write a manifest that lists every evidence file with its hash, because a bundle without one cannot be checked for completeness or tampering

**Use when:** assembling the evidence directory for a report

**Avoid when:** never; the manifest is what makes a bundle a bundle

## Procedure

1. Collect every artifact the record references.
2. List each with its relative path and SHA-256.
3. Record the total count and the bundle digest.
4. Check that no file in the directory is missing from the manifest.
5. Check that every manifest entry exists on disk.
6. Write the manifest last, after the evidence is final.

## Signals

- A file exists in the directory but is absent from the manifest.
- A manifest entry points to a file that was renamed.
- The bundle digest was computed before the last file was added.
- Two files have the same hash, suggesting a duplicate capture.

## Patterns

**1. Path plus hash**

```text
evidence/crash.txt  9f2c..  -> one line per file
```

**2. Both directions**

```text
files not in manifest and manifest entries without files  -> both checked
```

**3. Written last**

```text
manifest computed after the final artifact  -> no drift
```

## Pitfalls

- Writing the manifest before the last capture and leaving it stale.
- Hashing only the files the record names, missing extras.
- Using absolute paths, which break when the bundle moves.

## Done when

- Every evidence file appears in the manifest with a hash.
- The manifest and directory agree in both directions.

## References

- [NIST - SP 800-86 forensic techniques](https://csrc.nist.gov/pubs/sp/800/86/final)
- [RFC 8785 - JSON canonicalization](https://www.rfc-editor.org/rfc/rfc8785)
