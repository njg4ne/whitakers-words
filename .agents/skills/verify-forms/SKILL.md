---
name: verify-forms
description: Check omnes_formae after a change - regenerate the forms list, compare it with the list from before the change, and run the built-in checks of known forms, known non-forms and lookups.
---

# Verify the forms and the lookup

Everything runs through one stdlib module, so there are no shell pipelines,
temporary-directory tricks or `git stash`. Save the "before" list somewhere
the session can write, such as its scratch directory.

## 1. Before the change

```sh
python3 -m omnes_formae.verify --save <scratch>/before.txt
```

## 2. After the change

```sh
python3 -m omnes_formae.verify --compare <scratch>/before.txt
```

It prints the line and unique counts (the baseline at data commit `1f2f0fb`
is 1,399,668 lines and 1,185,902 unique), then:

- `MISSING` / `UNEXPECTED` for the forms in `PRESENT` and `ABSENT` in
  `omnes_formae/verify.py`, which cover each conjugation and
  declension, esse, deponents, short imperatives, PACK and -dem tackons, and
  impersonals;
- `LOOKUP` for any `get_latin_forms` call in `LOOKUPS` whose headings changed;
- with `--compare`, up to 50 forms added and 50 removed.

It exits with status 1 if a check fails. Every added or removed form should
be explained by the change. When a change is meant to alter a checked form or
lookup, update the lists in `verify.py` in the same change.

## 3. Ada parser as an oracle (not done yet; ask the user first)

Building the Ada parser needs a container (`debian:stable-slim` with `gnat
gprbuild make`, the recipe in mk270's `.github/workflows/ci.yml`). The user
declined an unrequested container build, so propose it and wait. Run with
it, a sample of forms goes through `bin/words`, and any form it reports as
`UNKNOWN` is either a generator bug or a deviation listed in `AGENTS.md`.
