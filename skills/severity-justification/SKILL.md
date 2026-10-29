---
name: severity-justification
description: "Grade severity from the record's own fields rather than from a chosen label, so the number follows the evidence and can be recomputed. Use when assigning or reviewing severity"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, grade, severity]
---

# Severity Justification

> Grade severity from the record's own fields rather than from a chosen label, so the number follows the evidence and can be recomputed

**Use when:** assigning or reviewing severity

**Avoid when:** the program takes no severity and pays a flat rate

## Procedure

1. Map each graded field to its severity contribution.
2. Check the impact against the scope and reachability fields.
3. Compute the grade from the rule table, not from a target number.
4. Compare the computed grade with the label in the record.
5. Explain any adjustment in a note.
6. Re-grade after any field changes.

## Signals

- The record says critical while the reproduction is a local crash.
- Reachability says authenticated but severity assumes pre-auth.
- Two records with identical fields have different grades.
- The grade was set before the evidence was collected.

## Patterns

**1. Computed**

```text
reachable pre-auth + memory write + deterministic  -> high
```

**2. Consistent**

```text
same field vector, same grade  -> reproducible
```

**3. Adjustment note**

```text
manual downgrade: requires a non-default config
```

## Pitfalls

- Choosing a grade first and filling the fields to match.
- Letting a CVSS vector override what the record demonstrates.
- Adjusting a grade with no note, so the next reviewer cannot follow it.

## Done when

- The grade is computed from the record's fields.
- Any manual adjustment carries a reason.

## References

- [FIRST - CVSS v3.1 specification](https://www.first.org/cvss/v3-1/specification-document)
- [OWASP - risk rating methodology](https://owasp.org/www-community/OWASP_Risk_Rating_Methodology)
