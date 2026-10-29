---
name: advisory-search-first
description: "Search the advisories before writing a report, because a fixed issue with a published CVE is a duplicate no matter how good the PoC is. Use when the component has a public security history or ships in a widely used package"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, dedupe, research]
---

# Advisory Search First

> Search the advisories before writing a report, because a fixed issue with a published CVE is a duplicate no matter how good the PoC is

**Use when:** the component has a public security history or ships in a widely used package

**Avoid when:** the target is a private build with no public disclosure channel

## Procedure

1. Search the vendor's advisory feed for the component and version.
2. Search the package registry for security releases around the version.
3. Search the upstream repository issues and pull requests for the crash function.
4. Check whether the fix is in the deployed build, not just in a release note.
5. Record every search and its result in the dedupe block.
6. If a fix exists, retest the deployed build before writing anything up.

## Signals

- The changelog mentions a bounds check added in the same function.
- An advisory names the exact input class you are crashing with.
- The upstream issue was closed as fixed two minor versions ago.
- The deployed build predates the fix and nobody noticed.

## Patterns

**1. Search by function**

```text
advisory search: parse_header bounds  -> closer than searching the product name
```

**2. Version check**

```text
fix shipped in 2.3.1, deployed 2.3.0  -> still vulnerable, not a duplicate
```

**3. Record the negative**

```text
searched: CVE feed, upstream issues, changelog  -> nothing matching
```

## Pitfalls

- Searching the product name and concluding there is no advisory.
- Assuming a fix release means the deployed build has it.
- Skipping the search and discovering the CVE during triage.

## Done when

- Advisory, registry and upstream searches are recorded with their results.
- The deployed build is checked against any fix that was found.

## References

- [CVE - search published advisories](https://www.cve.org/)
- [NVD - vulnerability database](https://nvd.nist.gov/)
