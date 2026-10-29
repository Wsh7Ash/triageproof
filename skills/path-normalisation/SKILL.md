---
name: path-normalisation
description: "Reduce build paths to a basename before hashing, because the same source file sits under a different prefix on every build machine. Use when frames carry source paths that differ between CI, developer machines and release builds"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, canonicalise, signature]
---

# Path Normalisation

> Reduce build paths to a basename before hashing, because the same source file sits under a different prefix on every build machine

**Use when:** frames carry source paths that differ between CI, developer machines and release builds

**Avoid when:** two different files share a basename on the crashing path, which needs the prefix kept

## Procedure

1. Collect the paths from the frames and group them by basename.
2. Check whether any basename is ambiguous within the stack.
3. Reduce paths to basenames when they are unambiguous.
4. Keep the full path as an extra field for localisation, outside the signature.
5. Re-run the stability check across two build directories.
6. Record the normalisation rule in the parser notes.

## Signals

- The same file appears as /build/rel/src/x.c and /build/dev/src/x.c.
- Two frames share a basename, making the reduction ambiguous.
- A Windows path appears with backslashes in one report and slashes in another.
- The path embeds a commit hash, which changes per build.

## Patterns

**1. Basename**

```text
/build/rel/src/parse.c -> parse.c  -> stable across machines
```

**2. Ambiguity check**

```text
src/a/util.c and src/b/util.c  -> keep the parent directory
```

**3. Full path out of the signature**

```text
store the raw path in the frame, hash only the basename
```

## Pitfalls

- Hashing absolute paths and producing a new signature for every build machine.
- Collapsing two same-named files and merging unrelated bugs.
- Forgetting Windows separators, so one report never normalises.

## Done when

- Paths are reduced only where unambiguous, and the rule is recorded.
- Signatures match across two different build directories.

## References

- [CWE - path handling](https://cwe.mitre.org/data/definitions/22.html)
- [Clang - debug info paths](https://clang.llvm.org/docs/DebugInfo.html)
