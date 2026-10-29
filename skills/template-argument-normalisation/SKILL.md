---
name: template-argument-normalisation
description: "Collapse template arguments in canonical frames, because the same instantiation prints differently across compilers and standard libraries. Use when the target is C++ and stack frames carry template parameters"
pack: triageproof
version: 1.0.0
category: bug-bounty-triage
tags: [triage, canonicalise, c-plus-plus]
---

# Template Argument Normalisation

> Collapse template arguments in canonical frames, because the same instantiation prints differently across compilers and standard libraries

**Use when:** the target is C++ and stack frames carry template parameters

**Avoid when:** the template argument is the finding, such as a fixed-size buffer type

## Procedure

1. Collect the symbols with template arguments from the stack.
2. Normalise them to a placeholder form, keeping the function name.
3. Check that distinct instantiations of one function are expected to be one bug.
4. Keep the full demangled symbol as an extra field for reading.
5. Re-check stability across two compilers or standard library versions.
6. Record the rule and the demangler used.

## Signals

- One instantiation appears as std::vector<int> and another as std::vector<int, std::allocator<int> >.
- The same bug crashes in three instantiations of the same template.
- A demangler version difference changes the printed symbol.
- Nested templates produce unbalanced angle brackets in the raw text.

## Patterns

**1. Placeholder form**

```text
parse<std::string> -> parse<>  -> one canonical token
```

**2. Keep the raw symbol**

```text
raw symbol stored separately for localisation
```

**3. Group instantiations**

```text
three instantiations, one bug  -> one signature is correct
```

## Pitfalls

- Hashing full template arguments and getting one cluster per instantiation.
- Stripping so much that overloads of different arity collapse together.
- Assuming every compiler prints the same demangled form.

## Done when

- Template arguments are normalised consistently and the rule is recorded.
- Distinct instantiations of one bug share a signature, as intended.

## References

- [Itanium C++ ABI - name mangling](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#mangling)
- [GDB - demangling](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Symbols.html)
