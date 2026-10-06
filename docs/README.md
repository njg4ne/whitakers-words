# omnes_formae

*Omnes formae*, Latin for "all the forms", is a Python package that writes
every inflected Latin form known to [William Whitaker's
Words](https://en.wikipedia.org/wiki/William_Whitaker%27s_Words) to a plain
text file, one form per line: *amo*, *amabantur*, *mater*, *matris*, *egit*,
*actus*, and about 1.2 million more. It can also list every form of one word,
tagged, for a vocab list: see [Looking up one word](lookup.md).

It needs only Python 3.10+ and the standard library. Whitaker's data files are
bundled in the package.

## Install

Install a tagged release from its source zip (no Git needed):

```sh
pip install https://github.com/njg4ne/whitakers-words/archive/refs/tags/v0.2.0.zip
uv add https://github.com/njg4ne/whitakers-words/archive/refs/tags/v0.2.0.zip
```

Or clone [the repo](https://github.com/njg4ne/whitakers-words) and run the
commands below from its root, with no install.

## Usage

```sh
omnes-formae                         # once installed: writes forms.txt
python3 -m omnes_formae              # the same, installed or from a clone
python3 -m omnes_formae -o out.txt   # choose the output file
python3 -m omnes_formae --data-dir path/to/words   # other Whitaker files
```

A full run takes a few seconds and writes about 1.4 million lines (16 MB).

### Removing duplicates

The same spelling can come from more than one dictionary entry. For example,
*amatus* comes from the verb *amo* and from the adjective *amatus*. Each entry's
forms are unique, but the file as a whole isn't. The package streams to disk
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
from omnes_formae import iter_forms, write_forms

write_forms(Path("forms.txt"))           # returns the number of lines written

for forms in iter_forms():               # one list of forms per dictionary entry
    ...
```


## More

- [Looking up one word](lookup.md): `get_latin_forms` and the keys of each row.
- [API reference](api.md): every public name, its signature and docstring.
- [Limitations](limitations.md): what the forms and the lookup get wrong.
- [How it works](how-it-works.md), [how the data fits](data.md), and
  [the source forks](compare.md).

## Licence

The code is licensed under the GNU Affero General Public License, version 3
or any later version: see
[LICENSE](https://github.com/njg4ne/whitakers-words/blob/main/LICENSE).
Whitaker's data files keep their own licence, below.

## Data and licence

Whitaker's data files are copied unchanged from the
[mk270 fork](https://github.com/mk270/whitakers-words) at commit `1f2f0fb` and
ship with the package, covered by Whitaker's licence in
`omnes_formae/data/whitaker/LICENCE.txt`.

---

AI disclosure: written with an AI assistant (Claude, by Anthropic), directed
and reviewed by njg4ne.
