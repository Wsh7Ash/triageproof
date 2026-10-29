---
name: reproduction-replay-from-bundle
description: "Rebuild the run from the bundle alone, because evidence that only makes sense with the author's shell history is not reproducible. Use when before submission, or when a triager cannot reproduce the finding"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, bundle, reproduction]
---

# Reproduction Replay From Bundle

> Rebuild the run from the bundle alone, because evidence that only makes sense with the author's shell history is not reproducible

**Use when:** before submission, or when a triager cannot reproduce the finding

**Avoid when:** the finding is fully described by a live endpoint the triager can hit

## Procedure

1. Move the bundle to a clean directory with no other state.
2. Run only the commands the record lists, in order.
3. Check that the success condition is met and the control is not.
4. Record any step that needed outside knowledge.
5. Add the missing step to the record rather than explaining it in chat.
6. Re-verify the bundle after adding a file.

## Signals

- The reproduction needs an environment variable the record omits.
- A file path points to the author's home directory.
- The control cannot be run from the bundle alone.
- The replay works only with the author's config file.

## Patterns

**1. Clean room**

```text
copy bundle to /tmp/replay  -> run listed commands only
```

**2. Self contained**

```text
inputs, scripts and expected output all inside the bundle
```

**3. Gap logging**

```text
needed PYTHONPATH=src  -> record it
```

## Pitfalls

- Replaying in place where leftover files make it work.
- Explaining a missing step in the submission comment instead of the record.
- Assuming the triager has the same toolchain version.

## Done when

- The bundle replays in a clean directory using only listed commands.
- Any outside dependency is written into the record.

## References

- [NIST - SP 800-115 testing guide](https://csrc.nist.gov/pubs/sp/800/115/final)
- [OWASP - testing guide](https://owasp.org/www-project-web-security-testing-guide/)
