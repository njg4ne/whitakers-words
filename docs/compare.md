# mk270 vs ben-crowell forks

## Background

[William Whitaker's Words](https://en.wikipedia.org/wiki/William_Whitaker%27s_Words) is a
Latin–English dictionary and morphological parser. It was written in Ada by William A.
Whitaker (1936–2010), a retired USAF colonel who had chaired DARPA's High Order Language
Working Group, the effort that produced Ada. Given an inflected form such as *amabantur*, it
identifies the stem and ending, tags the grammar (imperfect passive indicative, 3rd person
plural), and prints the dictionary entry and meaning. It also does English→Latin lookup. Its
dictionary has about 39,000 entries, which Wikipedia notes "would result in hundreds of
thousands of variations" once declensions and conjugations are counted.

**Why it's worth using.** Our goal in another project is to take a starter such as *mater*
or *ago, agere* and produce every form of that noun or verb, filtered by case, tense, mood
and so on. WORDS already contains the two things that requires, as open, plain-text data:

- **A lexicon that records stems and classes.** For example:
  - `ag / ag / eg / act`, `V 3 1` (*ago, agere, egi, actus*)
  - `mater / matr`, `N 3 1 F` (*mater, matris*)
- **A table of about 1,800 tagged endings** (`INFLECTS.LAT`) that says which stem each ending
  attaches to.

Joining the two gives the full paradigm. Irregular words are covered by a separate list of
unique forms. The program itself only parses in one direction, from a form back to the
dictionary entry, but that makes it a ready-made check on any forms we generate.

**Why look at forks and not a primary source.** Whitaker distributed WORDS as source code and
DOS/Windows binaries from his personal website, and the last release was version 1.97F. After
he died in 2010 the site went offline, and it survives only on the Internet Archive. There is
no official repository and no maintainer. The canonical code is effectively Martin Keegan's
cleanup on GitHub (mk270), which later stalled and stopped compiling on newer GNAT. Ben
Crowell forked it in 2024 to keep it building. mk270 has since become active again. The two
forks now differ in both code and data, so choosing a base means comparing them directly.

## The forks

Two forks are compared here:

- `submodules/mk270` is Martin Keegan's cleanup of Whitaker's Ada source, hosted on GitHub.
  The submodule tracks our fork of it, `njg4ne/whitakers-words` (branch `main`).
- `submodules/ben-crowell` is Ben Crowell's 2024 fork of mk270, hosted on Bitbucket.

The forks split at `9b11477` (2023-02-23). Since then mk270 has 46 commits and was last
active in Aug 2026. ben-crowell has 39 commits and was last active in Apr 2026.

The notes below come from reading the source, the history and the CI configs. Neither fork
has been built locally yet.

## File types

Whitaker wrote WORDS for DOS, so every file has an 8.3 name and a three-letter extension
that says what role the file plays. Both forks keep the same layout.

| Extension | Role | Files |
|---|---|---|
| `.LAT` | Hand-edited Latin source data, in plain text | `INFLECTS.LAT`, `UNIQUES.LAT`, `ADDONS.LAT` |
| `.GEN` | The "GENERAL" dictionary. `DICTLINE.GEN` is edited by hand; `make` generates the rest from it | `DICTLINE.GEN`, plus `STEMLIST`, `STEMFILE`, `INDXFILE`, `DICTFILE`, `EWDSLIST` and `EWDSFILE` |
| `.SEC` | Compiled inflection table, built from `INFLECTS.LAT` | `INFLECTS.SEC` |
| `.SPE` / `.LOC` | Optional SPECIAL and LOCAL dictionaries with the same format as `DICTLINE`. They are loaded if present, and neither fork ships them | — |
| `.MOD` / `.MDV` | Saved user and developer settings, written from the interactive menus | `WORD.MOD`, `WORD.MDV` |
| `.OUT` / `.UNK` / `.STA` / `.DBG` | Optional runtime output: results, unknown words, statistics and debug output | `WORD.OUT`, `WORD.UNK`, `WORD.STA`, `WORD.DBG` |

The hand-edited files:

- **`DICTLINE.GEN`** (about 39k lines) has one entry per line in fixed columns. Each entry
  gives the stems, part of speech, declension or conjugation (`N 3 1`, `V 1 1`), gender,
  flags for age, area, frequency and source, and the English meaning.
- **`INFLECTS.LAT`** (about 1,800 entries) has one ending per line. Each line gives the part
  of speech, class and variant, the grammar tags (for example `ABL S F`), which stem the ending
  attaches to, the ending itself, and flags for age and frequency.
- **`UNIQUES.LAT`** holds fully inflected irregular forms, such as *agatur*, that don't fit the
  stem-plus-ending scheme.
- **`ADDONS.LAT`** holds prefixes, suffixes and tackons (`-que`, `-ne`, `ec-`, and so on).

`WORD.MOD` and `WORD.MDV` store settings as plain `NAME Y/N` lines (see
`test/WORD.MDV_template`). ben-crowell also lets you set them with the `WHITAKER_USER` and
`WHITAKER_DEV` environment variables.

For a paradigm generator, only `DICTLINE.GEN`, `INFLECTS.LAT` and `UNIQUES.LAT` matter.
Everything else is either a compiled index for the parser or a runtime setting.

## Closer to the original

**ben-crowell, narrowly.**

- **Data:** its `INFLECTS.LAT`, `DICTLINE.GEN` and `UNIQUES.LAT` are still Whitaker's.
  mk270 changed them for issue #101 (Greek 2nd-declension `2 7` forms), plus a whitespace
  fix in `DICTLINE.GEN`. The three files differ by about 90 lines in total.
- **Behavior:** ben-crowell does change the default behavior, and mk270 doesn't. It strips
  macrons, turns off the "MORE" pause, sets the screen size to 50, and adds the
  `WHITAKER_USER` / `WHITAKER_DEV` environment variables.
- **Lineage:** mk270 is still the main upstream. ben-crowell forked because mk270 went quiet,
  and mk270 has since picked back up.

## Works better

**mk270 for correctness, ben-crowell for scripting.**

- **mk270:** has fixes from 2026 for new GNAT versions (paren and old-style qualification
  warnings) and CRLF handling. It also fixes a `-que` tackon bug and adds a test for it
  (`test/05_multusque`), and it includes the issue-101 inflection fixes. CI runs build and
  test on every push, plus Linux and Windows binary builds.
- **ben-crowell:** has fixes from 2024–25 for GNAT bitrot and has repaired the
  `dictpage`/`uniqpage` tools. It also has the macron stripping, environment-variable config
  and no pager listed above, which help when shelling out to it. It has a `make install`
  target, but it hard-codes `/lib`, `/bin` and `/usr/share`.

## Easier to build in Podman

**About the same; mk270 is slightly safer.**

- **Same build:** both need only `gnat gprbuild make` from Debian/Ubuntu apt, then `make`.
- **mk270:** its CI (`.github/workflows/ci.yml`) is exactly that recipe running on
  `ubuntu-latest`, so it has been shown to work on a current toolchain.
- **Keeping it cheap:** use a multi-stage build. Compile in a `debian:stable-slim` image with
  GNAT installed, then copy `bin/words` and the data files (`*.GEN`, `*.LAT`, `INFLECTS.SEC`)
  into a slim runtime image. The GNAT toolchain is the big layer, and the runtime doesn't need
  it.

## For generating paradigms (all forms of *amo* / *mater*, with filters)

**Use mk270's data files. Neither fork can generate paradigms itself.**

- **Neither generates paradigms:** both forks only parse (form → lemma). A generator would be
  new code, most easily a small Python tool. It would read `DICTLINE.GEN` for the stems and
  the declension or conjugation class, then read `INFLECTS.LAT` for the tagged endings, and
  filter on those tags.
- **mk270's data is more correct:** its `INFLECTS.LAT` includes the issue-101 fixes, and those
  files are the input that matters here.
- **Checking the output:** feed the generated forms back into a built `words` binary to confirm
  that each one parses to the expected lemma. ben-crowell's no-pager default and environment
  variables make that step easier to script, but mk270 works with a `WORD.MOD` file too.
