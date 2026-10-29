---
name: variant-detection
description: "Look for the same defect in sibling functions before closing as duplicate, because one unchecked copy usually implies several. Use when the matched bug is a missing check in a function with similar siblings"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, dedupe, variants]
---

# Variant Detection

> Look for the same defect in sibling functions before closing as duplicate, because one unchecked copy usually implies several

**Use when:** the matched bug is a missing check in a function with similar siblings

**Avoid when:** the function is unique with no parallel implementation

## Procedure

1. Find functions that share the vulnerable pattern with the matched bug.
2. Check each for the same missing check rather than a similar name.
3. Test the easiest one to reach with the same input class.
4. Record which variants are vulnerable, fixed or not reachable.
5. Report variants as an addition to the original if the program allows it.
6. Do not file each variant as a separate finding.

## Signals

- Three parsers share a copy-pasted length check.
- One sibling was patched and the others were not.
- A generic wrapper calls both the fixed and unfixed implementations.
- The same input crashes two different endpoints.

## Patterns

**1. Pattern search**

```text
grep for the unchecked memcpy shape across the module  -> candidate list
```

**2. Reachability first**

```text
test the pre-auth variant before the admin-only one
```

**3. Report as one**

```text
one finding covering three variants, each with a request
```

## Pitfalls

- Filing each variant separately and collecting duplicate verdicts.
- Assuming a fixed sibling means all siblings are fixed.
- Listing variants you never tested and implying they are vulnerable.

## Done when

- Sibling functions are enumerated and each is tested or marked unreachable.
- Variants are reported as one finding with per-variant evidence.

## References

- [CWE-119 - buffer overflow variants](https://cwe.mitre.org/data/definitions/119.html)
- [OWASP - code review guidance](https://owasp.org/www-project-code-review-guide/)
