---
name: bundle-minimisation
description: "Ship the smallest bundle that still proves the claim, because a hundred megabytes of logs buries the two lines that matter. Use when the evidence directory has grown well past what the claim needs"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, bundle, process]
---

# Bundle Minimisation

> Ship the smallest bundle that still proves the claim, because a hundred megabytes of logs buries the two lines that matter

**Use when:** the evidence directory has grown well past what the claim needs

**Avoid when:** the program explicitly asks for full captures for its own analysis

## Procedure

1. List which files each claim depends on.
2. Cut anything that no claim references.
3. Trim logs to the window around the event, keeping the boundaries.
4. Keep full captures when a claim depends on ordering.
5. Re-verify the bundle after trimming and re-hash.
6. Note what was trimmed and where the full capture is retained.

## Signals

- The bundle is mostly unrelated requests.
- A log file is hundreds of megabytes for a one-line event.
- Trimming breaks a claim that depended on an earlier request.
- The triager asks for the specific lines instead of the file.

## Patterns

**1. Claim driven**

```text
each file maps to a claim  -> unclaimed files go
```

**2. Windowed logs**

```text
keep 20 lines either side of the event plus the boundary markers
```

**3. Trim note**

```text
trimmed from 400MB to 12KB; full capture retained offline
```

## Pitfalls

- Trimming a capture that a claim depends on for ordering.
- Shipping the full raw capture with secrets in it to avoid the trimming work.
- Trimming without re-hashing, so verification fails.

## Done when

- Every shipped file maps to a claim or a reproduction step.
- Trimmed bundles are re-hashed and the trim is recorded.

## References

- [HackerOne - report writing](https://docs.hackerone.com/en/articles/8475114-scope)
- [NIST - SP 800-86 forensic techniques](https://csrc.nist.gov/pubs/sp/800/86/final)
