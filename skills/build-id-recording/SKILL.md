---
name: build-id-recording
description: "Record the build id or commit hash from the binary itself, because a version string from a manifest is a claim and a build id is a fact. Use when the crash report will be compared against other reports or retested after a fix"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, capture, versioning]
---

# Build ID Recording

> Record the build id or commit hash from the binary itself, because a version string from a manifest is a claim and a build id is a fact

**Use when:** the crash report will be compared against other reports or retested after a fix

**Avoid when:** the target is a source-only finding with no deployed binary

## Procedure

1. Read the build id from the binary or the running process mapping.
2. Record the commit hash if the build system stamps one.
3. Save the output of the version command alongside the crash.
4. Check whether the deployed binary matches the repository commit.
5. Store the build id in every artifact's metadata, not just the report.
6. Re-read it after any redeploy before comparing reports.

## Signals

- The version command reports a release tag while the binary is a local build.
- Two hosts run different build ids under the same version string.
- The commit hash is unknown because the build ran from a dirty tree.
- The build id changes without the version changing.

## Patterns

**1. Read the binary**

```text
readelf -n ./target | grep 'Build ID'  -> a fact, not a manifest claim
```

**2. Commit stamp**

```text
strings ./target | grep -E '^[0-9a-f]{40}$'  -> build system stamp
```

**3. Match the deployment**

```text
build id on host == build id in the report  -> same artifact
```

## Pitfalls

- Quoting a version from a changelog and never checking the running binary.
- Comparing reports from two builds that share a version string.
- Losing the build id when the binary is rebuilt during the engagement.

## Done when

- The build id comes from the binary and is recorded with the crash artifacts.
- The deployed build is shown to match the one under review.

## References

- [readelf - note sections](https://man7.org/linux/man-pages/man1/readelf.1.html)
- [GNU - build-id specification](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Separate-Debug-Files.html)
