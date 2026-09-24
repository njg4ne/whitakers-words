# word_form_enumerator

Writes every inflected Latin form known to
[William Whitaker's Words](https://en.wikipedia.org/wiki/William_Whitaker%27s_Words)
to a plain text file, one form per line: *amo*, *amabantur*, *mater*, *matris*,
*egit*, *actus*, and about 1.2 million more.

It needs only Python 3.10+ and the standard library. No Ada compiler is needed,
and it doesn't use the submodules. The data it reads is bundled in
`word_form_enumerator/data/`.

## Usage

From the repo root:

```sh
python3 -m word_form_enumerator              # writes forms.txt
python3 -m word_form_enumerator -o out.txt   # choose the output file
python3 -m word_form_enumerator --data-dir path/to/words   # use other data files
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
| `__init__.py` | `write_forms` / `iter_forms`: runs everything and streams the output |
| `dictline.py` | Reads dictionary entries and pairs each stem with its key |
| `inflects.py` | Reads the ending table |
| `rules.py` | Decides which endings fit which stems (ported from the Ada) |
| `generate.py` | Builds one entry's forms |
| `uniques.py` | Reads the irregular forms |

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

The files in `word_form_enumerator/data/` are copied unchanged from the
[mk270 fork](https://github.com/mk270/whitakers-words) at commit `1f2f0fb`. They
are covered by Whitaker's licence in `word_form_enumerator/data/LICENCE.txt`.
