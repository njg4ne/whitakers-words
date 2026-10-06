---
name: refresh-words-data
description: Update the bundled Whitaker's Words data in omnes_formae/data/whitaker from a newer mk270 submodule commit, and check what changed in the generated forms.
---

# Refresh the bundled data

The package reads only `omnes_formae/data/` (`whitaker/` for
Whitaker's files, `bespoke/` for ours). The submodules are reference copies,
so a refresh is a deliberate copy.

1. **Ask the user before fetching.** Updating the submodule needs network
   access (`git -C submodules/mk270 fetch`). Then read the new commits for
   data changes (`DICTLINE.GEN`, `INFLECTS.LAT`, `UNIQUES.LAT`) and for
   engine changes to the rules ported in `rules.py` (see `AGENTS.md` for the
   mapping). An engine change may need porting: use the `port-ada-rule`
   skill.

2. **Save the current forms:** run step 1 of the `verify-forms` skill.

3. **Copy the four files** `DICTLINE.GEN`, `INFLECTS.LAT`, `UNIQUES.LAT` and
   `LICENCE.txt` from `submodules/mk270/` into
   `omnes_formae/data/whitaker/`, unchanged.

4. **Update the recorded commit** in `omnes_formae/data/whitaker/README.md`,
   `README.md` (the "Data and licence" section), `AGENTS.md`, and the baseline
   counts in `.agents/skills/verify-forms/SKILL.md`.

5. **Compare:** run step 2 of the `verify-forms` skill. A parse error usually
   means a new field layout (`zip(strict=True)` in `inflects.py` catches wrong
   tag counts).

6. **Stage your changes** (including the submodule pointer), and report the
   count changes and a suggested commit message. The user commits. Don't commit.
