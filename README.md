# word_form_enumerator

Writes every inflected Latin form known to
[William Whitaker's Words](https://en.wikipedia.org/wiki/William_Whitaker%27s_Words)
to a plain text file, one form per line: *amo*, *amabantur*, *mater*, *matris*,
*egit*, *actus*, and about 1.2 million more.

It can also list every form of one word, tagged, for a vocab list: see
[Looking up one word](#looking-up-one-word).

It needs only Python 3.10+ and the standard library. No Ada compiler is needed,
and it doesn't use the submodules. The data it reads is bundled in
`word_form_enumerator/data/`.

## Usage

From the repo root:

```sh
python3 -m word_form_enumerator              # writes forms.txt
python3 -m word_form_enumerator -o out.txt   # choose the output file
python3 -m word_form_enumerator --data-dir path/to/words   # other Whitaker files
```

A full run takes a few seconds and writes about 1.4 million lines (16 MB).

### Removing duplicates

The same spelling can come from more than one dictionary entry. For example,
*amatus* comes from the verb *amo* and from the adjective *amatus*. Each entry's
forms are unique, but the file as a whole isn't. The enumerator streams to disk
instead of holding every form in memory, so remove duplicates afterwards:

```sh
sort -u forms.txt -o forms.txt    # about 1.19 million unique forms
```

### Loading into SQLite

```sh
sqlite3 forms.db "CREATE TABLE forms (form TEXT PRIMARY KEY);"
sort -u forms.txt | sqlite3 forms.db ".import /dev/stdin forms"
```

### From Python

```python
from pathlib import Path
from word_form_enumerator import iter_forms, write_forms

write_forms(Path("forms.txt"))           # returns the number of lines written

for forms in iter_forms():               # one list of forms per dictionary entry
    ...
```

## Looking up one word

`get_latin_forms(word, pos=None)` takes a vocab-list entry and returns every
form of the dictionary word it names, one dict per form and grammatical slot.

```python
from word_form_enumerator import Frequency, PartOfSpeech, get_latin_forms

rows = get_latin_forms("amo, amare, amavi, amatum", "verb")
rows[0]["word"]   # 'amo'
rows[0]["tag"]    # 'present active indicative 1st person singular'

five_letter = {r["word"] for r in rows if len(r["word"]) == 5}
common_only = [r for r in rows if r["form_frequency"] == Frequency.MOST_COMMON]
```

**`word`** is the entry as a textbook writes it: `"amo, amare, amavi,
amatum"`, `"femina, -ae, f."`, `"in (+ abl.)"`, or just `"amo"`. Its first
Latin word must be the word's citation form, the form a dictionary lists it
under (the nominative, or a verb's 1st person singular present). The other
spelled-out words help choose among homographs: `"os, oris"` is "mouth", not
"bone". Case, macrons, *i*/*j* and *u*/*v* don't matter.

**`pos`** is optional: English words (`"noun"`, `"adjective, cardinal"`), a
`PartOfSpeech`, or its code (`"V"`). Without it, every part of speech is
searched, so a bare `"liber"` returns "children", "free" and "book".

It returns the root's forms, not every word the spelling could be a form of:
`"amor"` is the noun, not the passive of *amo*. When more than one word fits,
all of them come back, rare ones too, and each row says which word it is
from; filter the rows as you need. Words whose forms are all the same (*caelum*
"heaven" and "chisel") come back once, with both meanings. An empty list
means nothing matched, or the entry is an enclitic or prefix (`"-que"`).

The data loads on the first call (under a second); after that each call
takes about a millisecond, so looking up a whole vocab list is quick.

### The keys of each row

| Key | Example | Meaning |
|---|---|---|
| `word` | `"amabat"` | the form |
| `root` | `"amo, amare, amavi, amatum"` | the `word` argument, as given |
| `lemma` | `"amo, amare, amavi, amatus"` | Whitaker's dictionary heading for the word |
| `meaning` | `"love, like; ..."` | Whitaker's English; merged homographs' meanings are joined with `" \| "` |
| `pos` | `PartOfSpeech.VERB` | the form's part of speech (participles are `PARTICIPLE` under a verb) |
| `tag` | `"imperfect active indicative 3rd person singular"` | every grammar category of the form, in a fixed order; the same slot has the same tag in every word |
| `case`, `number`, `gender`, `tense`, `voice`, `mood`, `person`, `comparison`, `sort` | `"imperfect"` | the parts of the tag, each present only when it applies |
| `lemma_frequency` | `Frequency.MOST_COMMON` | how common the word is |
| `form_frequency` | `Frequency.MOST_COMMON` | how common this spelling of the form is |
| `form_age` | `Age.ANY` | when the form was in use |
| `entry_id`, `entry_ids` | `2871`, `[2871]` | the word's line in `DICTLINE.GEN` (negative: in `UNIQUES.LAT`); stable only while the data files are |

`PartOfSpeech`, `Frequency` and `Age` are Whitaker's own codes, with readable
names. Each member is also its code as a string, so `row["pos"] == "V"` is
true and JSON output shows `"V"`.

| `Frequency` | Code | For a word | For a form |
|---|---|---|---|
| `MOST_COMMON` | A | in every elementary Latin book | the usual form |
| `FREQUENT` | B | top 10 percent | a not unusual variant |
| `COMMON` | C | top 10,000 words | occasionally seen |
| `LESSER` | D | top 20,000 words | unlikely |
| `UNCOMMON` | E | 2 or 3 citations | rare |
| `VERY_RARE` | F | one citation | very rare |
| `INSCRIPTION_ONLY`, `GRAFFITI`, `PLINY_ONLY`, `UNKNOWN` | I, M, N, X | | |

`Age` runs `ARCHAIC` (A), `EARLY` (B), `CLASSICAL` (C), `LATE` (D), `LATER`
(E), `MEDIEVAL` (F), `SCHOLAR` (G), `MODERN` (H), with `ANY` (X) for forms
used throughout. See `LIMITATIONS.md` for what the lookup gets wrong.

### Scripts in the repo root

| Script | What it does |
|---|---|
| `example.py` | Looks up one word and prints its forms and tags |
| `vocab_forms.py` | Writes every N-letter form of the words in a vocab CSV (for a Wordle list) |
| `wheelock_forms.py` | Writes every form of all 880 Wheelock vocab words to `wheelock-forms.json`, downloading the vocab first if needed |
| `known_issues.py` | Shows the Wheelock words the lookup still gets wrong, with why and whether each could be fixed |

## How it works

Whitaker's Words stores its Latin as plain-text data, not code:

- **`DICTLINE.GEN`** is about 39,000 dictionary entries. Each entry lists up to
  four stems and a class. For example, `am am amav amat V 1 1` is *amo*, a
  1st-conjugation verb.
- **`INFLECTS.LAT`** is about 1,800 endings. Each ending is tagged with its
  grammar and says which stem it attaches to. For example,
  `V 1 1 IMPF PASSIVE IND 3 P 1 7 abantur` attaches to stem 1.
- **`UNIQUES.LAT`** is 79 irregular forms, spelled out in full.

A form is a stem plus an ending, so `am` + `abantur` = *amabantur*. For each
dictionary entry, the enumerator tries every ending for that entry's class, keeps
the ones that fit, and writes the results. The rules for what "fits" are ported
from the original Ada parser. They check the declension or conjugation and its
variant, the gender, and which stem an ending needs. They also drop forms a verb
can't have, such as active forms of deponents like *sequor*. Finally, the unique
forms are appended.

| Module | Role |
|---|---|
| `all_forms.py` | `write_forms` / `iter_forms`: runs everything and streams the flat list |
| `dictline.py` | Reads dictionary entries and pairs each stem with its key |
| `inflects.py` | Reads the ending table |
| `rules.py` | Decides which endings fit which stems (ported from the Ada) |
| `generate.py` | Builds one entry's forms, with the ending that made each |
| `uniques.py` | Reads the irregular forms |
| `lookup.py` | `get_latin_forms`: finds the word an entry names, and lists its forms |
| `spelling.py` | Finds the Latin words in a vocab entry, and compares spellings |
| `words.py` | Groups the data's lines into dictionary words |
| `citation.py` | A word's citation form and dictionary heading |
| `tags.py` | Readable grammar tags |
| `codes.py` | `PartOfSpeech`, `Frequency`, `Age` |
| `paths.py` | Where the data folders are |
| `verify.py` | Checks after a change: `python3 -m word_form_enumerator.verify` |

For more detail, see `docs/data.md` for the data formats and matching rules, and
`docs/compare.md` for the background and a comparison of the source forks.

## Limitations

- **No compound tenses.** Tenses such as *amatus est* are two words, and both
  words are already in the list on their own.
- **Spelling follows the data.** Some entries use *j*, so the list has
  *cujuscumque*. It doesn't add *i*/*j* or *u*/*v* variants.
- **Abbreviations are included.** The dictionary lists some, such as `A` for
  *Aulus*.
- **Not checked against the parser.** The output hasn't yet been run through
  the original Ada `words` parser to catch generated forms that don't exist.

## Data and licence

The files in `word_form_enumerator/data/whitaker/` are copied unchanged from
the [mk270 fork](https://github.com/mk270/whitakers-words) at commit `1f2f0fb`.
They are covered by Whitaker's licence in
`word_form_enumerator/data/whitaker/LICENCE.txt`. The files in
`word_form_enumerator/data/bespoke/` were written for this project: the
English tag labels and part-of-speech words the lookup uses.
