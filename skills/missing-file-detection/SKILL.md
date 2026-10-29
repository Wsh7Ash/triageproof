---
name: missing-file-detection
description: "Check both directions of the manifest, because a referenced-but-absent file breaks the claim and an unreferenced-but-present file is unreviewed evidence. Use when verifying a bundle or reviewing one someone else assembled"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, bundle, completeness]
---

# Missing File Detection

> Check both directions of the manifest, because a referenced-but-absent file breaks the claim and an unreferenced-but-present file is unreviewed evidence

**Use when:** verifying a bundle or reviewing one someone else assembled

**Avoid when:** never; both directions are cheap and both matter

## Procedure

1. List the files the record references.
2. List the files the manifest declares.
3. List the files actually on disk.
4. Report references missing from disk, and disk files missing from the manifest.
5. Fail verification if either set is non-empty.
6. Record the three lists in the verification output.

## Signals

- The record cites evidence/trace.txt but the file was renamed.
- A capture file exists that the record never mentions.
- The manifest is a subset of the directory.
- Verify passes because it only checks declared files.

## Patterns

**1. Three lists**

```text
referenced, declared, present  -> set differences
```

**2. Fail closed**

```text
any difference  -> verify fails
```

**3. Show the diff**

```text
print the specific missing or extra paths
```

## Pitfalls

- Checking only that declared files exist and ignoring extras.
- Passing verification because the record's paths were never resolved.
- Silently ignoring a stray file that contains a credential.

## Done when

- Both directions are compared and reported explicitly.
- Any difference fails verification.

## References

- [NIST - SP 800-86 forensic techniques](https://csrc.nist.gov/pubs/sp/800/86/final)
- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
