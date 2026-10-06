# How it works

Whitaker's Words stores its Latin as plain-text data, not code:

- **`DICTLINE.GEN`** is about 39,000 dictionary entries. Each entry lists up to
  four stems and a class. For example, `am am amav amat V 1 1` is *amo*, a
  1st-conjugation verb.
- **`INFLECTS.LAT`** is about 1,800 endings. Each ending is tagged with its
  grammar and says which stem it attaches to. For example,
  `V 1 1 IMPF PASSIVE IND 3 P 1 7 abantur` attaches to stem 1.
- **`UNIQUES.LAT`** is 79 irregular forms, spelled out in full.

A form is a stem plus an ending, so `am` + `abantur` = *amabantur*. For each
dictionary entry, the package tries every ending for that entry's class, keeps
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
| `verify.py` | Checks after a change: `python3 -m omnes_formae.verify` |

For more detail, see [data.md](data.md) for the data formats and
matching rules, and [compare.md](compare.md) for the background and
a comparison of the source forks.


---

AI disclosure: written with an AI assistant (Claude, by Anthropic), directed
and reviewed by [njg4ne](https://github.com/njg4ne).
