# AGENTS.md

Context for agents working in this repo. User-facing usage is in `README.md`. The
data formats are covered in depth in `docs/data.md`, and the choice of fork in
`docs/compare.md`.

## What this repo is

`word_form_enumerator/` is a pure-Python (stdlib-only) generator. It writes
every inflected Latin form in William Whitaker's Words to a text file, one per
line, and looks up every tagged form of one vocab-list word
(`get_latin_forms`), which a student project uses to build Wordle lists.

- This repo lives at `git@github.com:njg4ne/whitakers-words.git`, branch
  `main`. GitHub still lists it as a fork of mk270, but its `main` holds this
  project, not the Ada code. Use `main` for new branches here, never `master`.
- `submodules/mk270` (GitHub, upstream branch `master`; the local branch is
  named `main`) and `submodules/ben-crowell` (Bitbucket) are the two maintained
  forks of the Ada source. They are **reference only**: the
  enumerator never reads them at runtime.
- `word_form_enumerator/data/whitaker/` holds `DICTLINE.GEN`, `INFLECTS.LAT`,
  `UNIQUES.LAT` and `LICENCE.txt`, copied unchanged from mk270 at `1f2f0fb`.
  `data/bespoke/` holds our own data (tag labels, part-of-speech words); keep
  hard-coded data there, not in the code. The user explicitly wants the code
  not to depend on the submodules still being there.

## Decisions already made (don't re-litigate without a reason)

- **Python, not Ada.** The Ada engine only parses (form → lemma). It has no
  generation loop to reuse, and the generated `.GEN`/`.SEC` files are only
  lookup indexes built from `DICTLINE.GEN` and `INFLECTS.LAT`. So we read those
  two text files directly and port the rules that live in the code. Ada is only
  worth building as a **test oracle**: feed it generated forms and flag the ones
  it can't parse. That hasn't been done yet.
- **The mk270 data.** It includes the issue-101 fixes to Greek-style `2 7` nouns
  that ben-crowell lacks, and mk270 is active again (2026) with CI.
- **Stdlib only.** Ask the user before adding any dependency.
- **Stream the output.** Hold only the ~1,800 endings in memory. Read
  `DICTLINE` a line at a time, and write each entry's forms through Python's
  buffered file. There is no global deduplication, because that would hold
  every form in memory; users run `sort -u`.
- **The output is words only.** No tags or lemma, and two-word compound tenses
  (*amatus est*) are left out.
- **Tagged lookup is separate.** `get_latin_forms(word, pos)` returns one
  dict per (form, tag) for the word that a vocab-list entry names: the root,
  not every word the spelling could be a form of (that's what the Ada parser
  does). Returning more and letting the caller filter is fine; silently
  dropping a word is not, so nothing is dropped for being rare. A teacher
  picks forms by the distinct `tag` strings, so keep those stable. The lookup
  holds the data in memory (loaded once, indexed by stem), an exception to
  streaming. Its modules, in the order a lookup uses them: `spelling.py`,
  `words.py` (lines grouped into words: `|` continuation lines, each qu-
  pronoun's partial paradigms, UNIQUES records as their own words),
  `citation.py` (citation forms: verbs by their active form unless deponent;
  dictionary headings), `lookup.py` (looser passes only when nothing matched,
  homographs narrowed by the entry's other words, identical ones merged), and
  `tags.py`. `known_issues.py` in the repo root lists the cases it still gets wrong.

## How the rules map to the Ada source (all under `submodules/mk270/src/`)

| Python | Ada origin |
|---|---|
| `dictline.keyed_stems` | `commands/makedict_main.adb`: how STEMLIST keys are written. Stems 1 and 2 equal → key 0 (N/ADJ/V). An ADJ entry marked COMP-only puts stem 1 at key 3, and SUPER-only at key 4. An ADV marked COMP/SUPER puts it at 2/3. A NUM's sort (CARD/ORD/DIST/ADVERB) puts it at 1/2/3/4. `zzz` or blank stems are skipped |
| `dictline.ESSE` | `makedict_main.adb`, `Be_Ve`: *esse* isn't in DICTLINE. It is `V 5 1 TO_BE` with stems `s`, `""`, `fu`, `fut`, and the blank stem 2 is intentional (`""` + `es`) |
| `rules.decl_fits` / `gender_fits` / `comparison_fits` | `"<="` operators in `latin_utils/latin_utils-inflections_package.adb` |
| `rules.ending_fits`, `key_fits` | `Reduce_Stem_List` in `words_engine/words_engine-word_package.adb`. Note that its gender rule (`C` fits anything non-neuter) differs slightly from the one in `inflections_package` |
| `rules.verb_form_allowed` | `Allowed_Stem` in `words_engine/words_engine-list_sweep.adb` |
| `rules.pack_ending_fits`, `generate._pack_forms` | `Process_Packons` in `word_package.adb`. The tackon comes from the meaning text `(w/-cumque) ...`. A PRON ending's class must equal the PACK class exactly. Final `m` becomes `n` before `-dam` (*quendam*) |
| `generate.tagged_forms_of` (PRON + tackon) | TACKON `dem` in `ADDONS.LAT` and `Subtract_Tackon` in `words_engine/words_engine-parse.adb`: the Ada strips `-dem` and parses the rest as `PRON 4 2`, whose endings INFLECTS already spells for it (`eun`, `eorun`). So the `(w/-dem ONLY ...)` entry yields *idem, eundem, ...* and never its bare stubs |
| `codes.PartOfSpeech` | `Part_Of_Speech_Type` in `latin_utils/latin_utils-inflections_package.ads`, same members and order. The values are the upper-case codes the data files use |
| `codes.Age`, `codes.Frequency` | `Age_Type` and `Frequency_Type` in the same `.ads` file. Frequency's letters mean slightly different things for dictionary entries and for endings; both scales are in its docstring |
| `inflects.ENTRY_POS` | `Eff_Part` in `support_utils/support_utils-word_support_package.adb` (VPAR and SUPINE → V) |

**Deliberate deviation:** the Ada rejects infinitives (person 0) of `IMPERS`
verbs. We keep them, because forms like *oportere* are real. Document any new
deviation in `rules.py` and here.

## Data-format gotchas

- **Encoding:** the data files are ASCII with CRLF line endings. Open them with
  `encoding="latin-1"` and strip `\r\n`.
- **`DICTLINE` layout:** four 19-character stem columns (1–76), then fields
  separated by spaces. The number of class fields varies by part of speech
  (`dictline.CLASS_FIELDS`), then come 5 flags, then the meaning (kept intact
  via `split(maxsplit=...)`).
- **Parsing `INFLECTS` lines:** parse from the right: `freq`, `age`, then either
  `key len ending` or `key 0` (an empty ending leaves out the text token).
  Strip `--` comments first. Tag counts per part of speech are in
  `inflects.TAG_FIELDS`, and `zip(strict=True)` enforces them. It passes on the
  current data.
- **`UNIQUES.LAT`:** strict 3-line records (form, tags, meaning). That's 79
  records in 237 lines, so don't count lowercase lines.
- **Spelling:** it follows the data, which sometimes uses `j` (*cujus*). The
  Ada normalizes i/j and u/v only when reading input.
- **Enum order matters** for the Ada range checks, which are ported as explicit
  tuples. Tense: `X PRES IMPF FUT PERF PLUP FUTP`. Mood:
  `X IND SUB IMP INF PPL`.

## Checking changes

Use the `verify-forms` skill: `python3 -m word_form_enumerator.verify` with
`--save` before a change and `--compare` after it. It's one stdlib command
that regenerates the list (about 2 s), checks known forms and lookups, and
lists what changed. Prefer it, and short Python, over shell pipelines,
`git stash` or ad hoc temp directories, which need extra approval.

Lint is ruff (`ruff check --select E,F,I,UP,B word_form_enumerator`). The
user runs it; don't install it or fetch it with `uvx` without asking.

## Working with this user

- **Commits:** the user commits. Their commits are SSH-signed, and `git commit`
  hangs waiting for a passphrase when no agent is loaded. **Stage your changes
  and report back with a suggested message.** Don't commit unless asked, and
  don't turn signing off.
- **Containers:** Podman is installed (`podman machine`), but the user declined
  an unrequested container build. Ask before running one.
- **Docs style:** the docs in `docs/` are short and factual. Check every claim
  against the files or the source before writing it.
