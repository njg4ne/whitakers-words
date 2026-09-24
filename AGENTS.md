# AGENTS.md

Context for agents working in this repo. User-facing usage is in `README.md`. The
data formats are covered in depth in `docs/data.md`, and the choice of fork in
`docs/compare.md`.

## What this repo is

`word_form_enumerator/` is a pure-Python (stdlib-only) generator. It writes
every inflected Latin form in William Whitaker's Words to a text file, one per
line. The larger goal, in another project, is to go from a lemma (*ago, agere*;
*mater, matris*) to all of its forms. The flat list is the first deliverable, and
a lemma → forms lookup is the likely next one.

- `submodules/mk270` and `submodules/ben-crowell` (Bitbucket) are the two
  maintained forks of the Ada source. `submodules/mk270` tracks the user's fork,
  `git@github.com:njg4ne/whitakers-words.git` on branch `main` (renamed from
  `master`). Martin Keegan's original is the remote `upstream` there, on
  branch `master`. They are **reference only**: the
  enumerator never reads them at runtime.
- `word_form_enumerator/data/` holds `DICTLINE.GEN`, `INFLECTS.LAT`,
  `UNIQUES.LAT` and `LICENCE.txt`, copied unchanged from mk270 at `1f2f0fb`.
  The user explicitly wants the code not to depend on the submodules still being
  there.

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

## How the rules map to the Ada source (all under `submodules/mk270/src/`)

| Python | Ada origin |
|---|---|
| `dictline.keyed_stems` | `commands/makedict_main.adb`: how STEMLIST keys are written. Stems 1 and 2 equal → key 0 (N/ADJ/V). An ADJ entry marked COMP-only puts stem 1 at key 3, and SUPER-only at key 4. An ADV marked COMP/SUPER puts it at 2/3. A NUM's sort (CARD/ORD/DIST/ADVERB) puts it at 1/2/3/4. `zzz` or blank stems are skipped |
| `dictline.ESSE` | `makedict_main.adb`, `Be_Ve`: *esse* isn't in DICTLINE. It is `V 5 1 TO_BE` with stems `s`, `""`, `fu`, `fut`, and the blank stem 2 is intentional (`""` + `es`) |
| `rules.decl_fits` / `gender_fits` / `comparison_fits` | `"<="` operators in `latin_utils/latin_utils-inflections_package.adb` |
| `rules.ending_fits`, `key_fits` | `Reduce_Stem_List` in `words_engine/words_engine-word_package.adb`. Note that its gender rule (`C` fits anything non-neuter) differs slightly from the one in `inflections_package` |
| `rules.verb_form_allowed` | `Allowed_Stem` in `words_engine/words_engine-list_sweep.adb` |
| `rules.pack_ending_fits`, `generate._pack_forms` | `Process_Packons` in `word_package.adb`. The tackon comes from the meaning text `(w/-cumque) ...`. A PRON ending's class must equal the PACK class exactly. Final `m` becomes `n` before `-dam` (*quendam*) |
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

```sh
python3 -m word_form_enumerator -o /tmp/forms.txt   # ~1.2 s, 1,399,668 lines, 1,185,893 after sort -u (as of 1f2f0fb)
uvx ruff check --select E,F,I,UP,B word_form_enumerator
```

Before and after a change, compare the line counts and `cmp` the outputs, or
diff the `sort -u` outputs. Then use the `verify-forms` skill in
`.agents/skills/` for spot checks.

## Working with this user

- **Commits:** the user commits. Their commits are SSH-signed, and `git commit`
  hangs waiting for a passphrase when no agent is loaded. **Stage your changes
  and report back with a suggested message.** Don't commit unless asked, and
  don't turn signing off.
- **Containers:** Podman is installed (`podman machine`), but the user declined
  an unrequested container build. Ask before running one.
- **Docs style:** the docs in `docs/` are short and factual. Check every claim
  against the files or the source before writing it.
