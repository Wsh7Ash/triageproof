---
name: hash-verification
description: "Recompute every hash before trusting the bundle, because evidence that was edited after capture still looks like evidence. Use when verifying a bundle before submission or during a retest"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, bundle, integrity]
---

# Hash Verification

> Recompute every hash before trusting the bundle, because evidence that was edited after capture still looks like evidence

**Use when:** verifying a bundle before submission or during a retest

**Avoid when:** never; an unverified hash is a claim about a claim

## Procedure

1. Recompute the hash of every file in the manifest.
2. Compare with the recorded value and fail on any mismatch.
3. Recompute the bundle digest over the canonical manifest.
4. Record the verification result with a timestamp.
5. If a mismatch exists, do not repair the hash; re-capture the evidence.
6. Re-verify after any file is added.

## Signals

- One file differs while the rest match, suggesting a targeted edit.
- The bundle digest matches but a file hash does not.
- The manifest was regenerated to match edited files.
- Hashes match on Linux but not after a copy via a text-mode transfer.

## Patterns

**1. Fail on mismatch**

```text
one differing file  -> verify fails, no partial credit
```

**2. Recapture**

```text
mismatch  -> re-run the reproduction, do not edit the hash
```

**3. Line endings**

```text
text-mode transfer changed CRLF  -> hash the bytes, not the text
```

## Pitfalls

- Updating the manifest to match an edited file.
- Verifying only the files the record names.
- Copying evidence through a tool that rewrites line endings.

## Done when

- Every file hash and the bundle digest are re-verified.
- A mismatch causes recapture, not a manifest update.

## References

- [NIST - SP 800-86 forensic techniques](https://csrc.nist.gov/pubs/sp/800/86/final)
- [RFC 6234 - SHA algorithms](https://www.rfc-editor.org/rfc/rfc6234)
