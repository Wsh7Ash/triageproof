# Contributing

## Setup

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
triageproof validate
```

There is no runtime dependency and there should not be one: the tool has to run
on an air-gapped triage host.

## The two gates

Every change must leave both of these green:

```bash
triageproof validate                  # 50/50 skills valid
python -m pytest -q                   # 83 passing
```

Plus the artifact check, which is what CI runs last:

```bash
triageproof build
git diff --exit-code -- skills pack.json results
```

`build` is the only writer of `skills/`, `pack.json` and `results/`. Never edit a
generated `SKILL.md` by hand — edit the corpus and rebuild.

## Adding or editing a skill

Skills live in `src/triageproof/corpus/part{1,2,3}.py` as plain dicts. The rules
are enforced, not advisory:

- slug and title unique across the pack, slug kebab-case
- 6+ steps, 4+ signals, 3+ patterns, 3+ pitfalls, 2+ done-when criteria
- 180+ rendered words
- 2+ tags, each kebab-case
- at least one reference, formatted `[label](https://...)`
- no `TODO`, `FIXME`, `TBD`, lorem ipsum or placeholder text
- no machine-local path (`C:\`, `/Users/`, `/home/`)

Beyond the mechanical rules, a skill is only worth adding if it changes a
decision. State when **not** to use it (`avoid_when`) — a skill that always
applies teaches nothing.

## Changing the logic

Anything that changes a signature, a similarity score or a grading rule needs a
test that fails before the change and passes after. If a rule becomes more
permissive, say why in the pull request; a threshold edit to make one record pass
is not a fix.

New parsing formats are welcome, especially with a real capture attached. Add the
shape to `tests/test_stack.py` and check it against an existing format: two tools
describing one bug must produce one key at a shared depth.

## Style

- Python 3.10+, standard library only
- `from __future__ import annotations` in every module
- Type hints on public functions
- CLI output ASCII only (it has to survive a cp1252 console)
- No printing from library modules; `cli.py` owns stdout and exit codes

## Reporting a problem

Open an issue with the command, the input, the output you got and the output you
expected. If a signature is unstable, include both captures.
