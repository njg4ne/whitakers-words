---
name: refresh-words-data
description: Update the bundled Whitaker's Words data in word_form_enumerator/data from a newer mk270 submodule commit, and check what changed in the generated forms.
---

# Refresh the bundled data

The enumerator reads only `word_form_enumerator/data/`. The submodules are
reference copies, so a refresh is a deliberate copy.

1. **Update the reference fork.**
   ```sh
   git -C submodules/mk270 fetch && git -C submodules/mk270 log --oneline HEAD..origin/master
   git -C submodules/mk270 checkout origin/master
   ```
   Read the commit list for data changes (`DICTLINE.GEN`, `INFLECTS.LAT`,
   `UNIQUES.LAT`) and for engine changes to the rules ported in `rules.py` (see
   `AGENTS.md` for the mapping). An engine change may need porting: use the
   `port-ada-rule` skill.

2. **Save the current output, then copy the new data.**
   ```sh
   python3 -m word_form_enumerator -o /tmp/before.txt
   cp submodules/mk270/{DICTLINE.GEN,INFLECTS.LAT,UNIQUES.LAT,LICENCE.txt} word_form_enumerator/data/
   ```

3. **Update the recorded commit** in `word_form_enumerator/data/README.md`,
   `README.md` (the "Data and licence" section), `AGENTS.md`, and the baseline
   counts in `.agents/skills/verify-forms/SKILL.md`.

4. **Regenerate and diff.** A parse error here usually means a new field layout
   (`zip(strict=True)` in `inflects.py` catches wrong tag counts).
   ```sh
   python3 -m word_form_enumerator -o /tmp/after.txt
   diff <(sort -u /tmp/before.txt) <(sort -u /tmp/after.txt) | head
   ```
   Then run the `verify-forms` spot checks.

5. **Stage your changes** (including the submodule pointer), and report the
   count changes and a suggested commit message. The user commits. Don't commit.
