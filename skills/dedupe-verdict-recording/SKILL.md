---
name: dedupe-verdict-recording
description: "Record new, probable or duplicate explicitly with the threshold used, so the decision can be reviewed instead of inferred later. Use when every triage record, whether or not a match was found"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, dedupe, process]
---

# Dedupe Verdict Recording

> Record new, probable or duplicate explicitly with the threshold used, so the decision can be reviewed instead of inferred later

**Use when:** every triage record, whether or not a match was found

**Avoid when:** never; an unrecorded dedupe check is indistinguishable from none

## Procedure

1. Set checked to true only after the searches actually ran.
2. Record the verdict from the tool's thresholds, not from intuition.
3. List what was compared against, by id or advisory.
4. Record the threshold and similarity for a probable or duplicate verdict.
5. Note the search sources used, such as advisory feed and tracker.
6. Re-run the check after new advisories are published.

## Signals

- checked is true but no sources are listed.
- The verdict is duplicate with an empty against list.
- A probable verdict has no score recorded.
- The check ran against a stale advisory snapshot.

## Patterns

**1. Verdict plus score**

```text
probable, 0.71 against #441 (threshold 0.6)  -> reviewable
```

**2. Search sources**

```text
searched: CVE feed 2026-10-29, upstream issues, program disclosures
```

**3. Empty against**

```text
verdict new and no matches  -> explicitly recorded as searched
```

## Pitfalls

- Marking the check complete before searching, to clear a validation error.
- Recording duplicate with no reference, which cannot be audited.
- Skipping the check because the crash looked unusual.

## Done when

- The verdict, evidence and threshold are recorded for every record.
- Search sources and their date are listed.

## References

- [HackerOne - triage process](https://docs.hackerone.com/en/articles/8475114-scope)
- [CVE - advisory sources](https://www.cve.org/)
