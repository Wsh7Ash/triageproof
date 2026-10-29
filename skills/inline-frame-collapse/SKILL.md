---
name: inline-frame-collapse
description: "Decide how inlined frames are represented before hashing, because the optimizer's choices change which frames exist at all. Use when the target is built with optimisation and the stack shows inlined call sites"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, canonicalise, inlining]
---

# Inline Frame Collapse

> Decide how inlined frames are represented before hashing, because the optimizer's choices change which frames exist at all

**Use when:** the target is built with optimisation and the stack shows inlined call sites

**Avoid when:** the build is unoptimised and every source call has its own frame

## Procedure

1. Identify inlined frames, which usually share an address with their caller.
2. Decide whether to keep them as separate canonical frames or collapse to the outermost.
3. Record the build's optimisation level, since it determines the answer.
4. Apply the same rule for every report of this target.
5. Check that two optimisation levels still produce one signature.
6. Note the choice in the report so a reader can interpret the stack.

## Signals

- Two frames share an address, indicating inlining.
- A debug build shows a frame that the release build does not.
- The line number of an inlined frame points into a header.
- Optimisation level differs between the crashing host and the test host.

## Patterns

**1. Collapse to the outer**

```text
keep the outermost frame of an inlined group  -> one canonical entry
```

**2. Record the build**

```text
-O2 with inlining  -> state it next to the stack
```

**3. Cross-optimisation check**

```text
release and -O0 signatures match after collapse
```

## Pitfalls

- Comparing a debug-build stack with a release-build stack and concluding they differ.
- Keeping inlined frames and hashing an artefact of one optimizer version.
- Collapsing so aggressively that the actual failing function disappears.

## Done when

- The inlining rule is stated and applied consistently.
- Signatures from two optimisation levels agree for the same bug.

## References

- [GCC - optimisation options](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- [LLVM - debug info and inlining](https://llvm.org/docs/SourceLevelDebugging.html)
