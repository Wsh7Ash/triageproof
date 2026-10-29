---
name: address-stripping
description: "Remove every runtime address before hashing, because ASLR and build layout change them between runs of the identical binary. Use when building a signature from frames that carry instruction or frame pointers"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, canonicalise, signature]
---

# Address Stripping

> Remove every runtime address before hashing, because ASLR and build layout change them between runs of the identical binary

**Use when:** building a signature from frames that carry instruction or frame pointers

**Avoid when:** the addresses are the finding, such as a fixed-address mapping bug

## Procedure

1. List which fields of a frame are runtime values: address, offset, register dump.
2. Strip the address prefix and any plus-offset from the function token.
3. Keep the module name, which is stable and meaningful.
4. Verify the signature is identical across two runs of the same binary.
5. Verify the signature changes when the top frame changes.
6. Record that stripping happened so nobody re-adds addresses later.

## Signals

- Two runs of the same input produce different signatures.
- The only difference between two stacks is the hex prefix.
- A plus-offset encodes an inline depth that matters, so it must stay as structure not text.
- The module name is missing because it was inside the address token.

## Patterns

**1. Strip the prefix**

```text
0x000055d1 in parse_header  -> parse_header
```

**2. Strip the offset**

```text
parse_header+0x2a  -> parse_header  (keep module separately)
```

**3. Stability test**

```text
two runs, one signature  -> addresses are not part of identity
```

## Pitfalls

- Hashing the raw line and getting a different signature on every run.
- Stripping so much that two different functions collapse into one token.
- Removing the module name along with the address and losing cross-library distinctions.

## Done when

- Two runs of the identical binary produce the same signature.
- The stripped fields and the retained ones are both documented.

## References

- [Wikipedia - address space layout randomization](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [GDB - frame information](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Frame-Info.html)
