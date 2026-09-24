---
name: port-ada-rule
description: Find how the Whitaker's Words Ada code handles a morphology case (stem keys, class matching, verb kinds, packons, irregulars) and port it into word_form_enumerator without guessing.
---

# Port a rule from the Ada source

The data files don't hold every rule. Some live in the Ada. Read the Ada before
changing `rules.py` or `dictline.keyed_stems`, and never infer a rule from the
data alone.

## Where to look (`submodules/mk270/src/`)

| Question | File / symbol |
|---|---|
| Which stem gets which key | `commands/makedict_main.adb`: the branches that write STEMLIST (`Integer_IO.Put (Stemlist, <key>, 2)`) |
| Does an ending's class fit an entry's class | `latin_utils/latin_utils-inflections_package.adb`: the `"<="` operators for `Decn_Record`, `Gender_Type`, `Comparison_Type` |
| Which stem + ending pairs survive | `words_engine/words_engine-word_package.adb`: `Reduce_Stem_List` (one branch per part of speech) |
| Verb forms dropped by kind or mood | `words_engine/words_engine-list_sweep.adb`: `Allowed_Stem` |
| qu- pronoun + tackon | `word_package.adb`: `Process_Packons`, `Process_Qu_Pronouns`, and the tackons in `ADDONS.LAT` |
| Two-word tenses (PPL + esse) | `words_engine/words_engine-parse.adb` (the "PPL + esse" glosses) |
| Enum names and their order | `latin_utils/latin_utils-inflections_package.ads` (`Tense_Type`, `Mood_Type`, `Verb_Kind_Type`, ...) |
| Record field layouts in the text files | `latin_utils/*_io.adb` (for example, `inflection_record_io.adb`, `noun_entry_io.adb`) |

`grep -rn "<Symbol>" submodules/mk270/src` is usually enough. The code is
verbose but direct.

## Porting rules

1. Quote the Ada condition you're porting in your notes, including its
   argument order. Ada's `Left <= Right` isn't symmetric, and some call sites
   pass (dictionary, ending) while others pass (ending, dictionary).
2. Port Ada enum ranges (`Ind .. Inf`) as explicit tuples, using the enum order
   from the `.ads` file.
3. Put the rule in `rules.py` if it decides whether an ending fits, and in
   `dictline.keyed_stems` if it decides which stems exist. Cite the Ada file and
   symbol in the docstring.
4. If you deliberately differ from the Ada, comment it in the code and add it to
   the "Deliberate deviation" note in `AGENTS.md`.
5. Run the `verify-forms` skill and explain every line of the output diff.

The ben-crowell fork differs mostly in UX (macron stripping, environment-variable
config) and lacks the issue-101 data fixes. Only check it when a rule looks
fork-specific: `diff -r submodules/mk270/src submodules/ben-crowell/src`.
