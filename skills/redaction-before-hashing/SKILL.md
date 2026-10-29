---
name: redaction-before-hashing
description: "Redact secrets before the hash is taken, because hashing first means either the secret ships with the bundle or the hash is broken by the edit. Use when evidence contains tokens, cookies, personal data or internal hostnames"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, bundle, redaction]
---

# Redaction Before Hashing

> Redact secrets before the hash is taken, because hashing first means either the secret ships with the bundle or the hash is broken by the edit

**Use when:** evidence contains tokens, cookies, personal data or internal hostnames

**Avoid when:** the evidence contains no sensitive data and no third-party records

## Procedure

1. Identify secrets: tokens, cookies, keys, personal data, internal hosts.
2. Replace each with a stable placeholder that preserves the shape.
3. Check that the redacted evidence still supports the claim.
4. Hash the redacted file, not the original.
5. Keep the original outside the bundle and unshared.
6. Record what was redacted and why in the record.

## Signals

- A session cookie appears in a request capture.
- A real user's email is in a response body.
- The hash was taken before redaction.
- A placeholder changes the byte length and breaks a parser replay.

## Patterns

**1. Shape preserving**

```text
Bearer abc123..  ->  Bearer REDACTED  -> still parses
```

**2. Hash after**

```text
redact, then hash  -> digest matches the shipped file
```

**3. Manifest note**

```text
redacted: session cookie, one user email  -> recorded
```

## Pitfalls

- Hashing the original and shipping a redacted copy with a stale digest.
- Redacting so aggressively the reproduction no longer works.
- Leaving the original in the bundle directory by accident.

## Done when

- No secret or personal data remains in the shipped bundle.
- Hashes were computed after redaction and still verify.

## References

- [NIST - SP 800-86 forensic techniques](https://csrc.nist.gov/pubs/sp/800/86/final)
- [OWASP - sensitive data exposure](https://owasp.org/www-project-top-ten/)
