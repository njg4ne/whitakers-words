# omnes_formae

*Omnes formae*, Latin for "all the forms", is a Python package that writes
every inflected Latin form known to [William Whitaker's
Words](https://en.wikipedia.org/wiki/William_Whitaker%27s_Words) to a plain
text file (about 1.2 million unique forms), and lists every form of one
vocab-list word, tagged. It needs only Python 3.10+ and the standard library,
and bundles the data it reads.

**Documentation: <https://njg4ne.github.io/whitakers-words/>**, built from
[`docs/`](docs/README.md): usage, the lookup and its row keys, the API
reference, limitations, and how the data fits.

## Install

From the release's source zip, with no Git needed:

```sh
pip install https://github.com/njg4ne/whitakers-words/archive/refs/tags/v0.2.1.zip
uv add https://github.com/njg4ne/whitakers-words/archive/refs/tags/v0.2.1.zip
```

Or with Git, which also downloads the two Ada forks in `submodules/` (they
aren't installed or used, just fetched):

```sh
pip install "git+https://github.com/njg4ne/whitakers-words.git@v0.2.1"
uv add "git+https://github.com/njg4ne/whitakers-words.git@v0.2.1"
```

Or clone the repo and run from its root, with no install.

## Quick start

```sh
omnes-formae                    # or: python3 -m omnes_formae
sort -u forms.txt -o forms.txt  # the same spelling can come from several words
```

```python
from omnes_formae import get_latin_forms

rows = get_latin_forms("amo, amare, amavi, amatum", "verb")
rows[0]["word"], rows[0]["tag"]   # ('amo', 'present active indicative 1st person singular')
```

See [Looking up one word](docs/lookup.md) for what the rows hold, and
[LIMITATIONS.md](LIMITATIONS.md) for what the lookup gets wrong.

## What's in the repo

| Path | What it is |
|---|---|
| `omnes_formae/` | The package. Its modules are listed in [How it works](docs/how-it-works.md) |
| `omnes_formae/data/whitaker/` | Whitaker's `DICTLINE.GEN`, `INFLECTS.LAT`, `UNIQUES.LAT` and licence, copied unchanged |
| `omnes_formae/data/bespoke/` | Data written for this project: tag labels and part-of-speech words |
| `submodules/mk270`, `submodules/ben-crowell` | The two maintained forks of Whitaker's Ada source, as Git submodules. Reference only: the package never reads them, and you don't need them to use it. See [docs/compare.md](docs/compare.md) |
| `docs/` | The docs site (docsify, served by GitHub Pages from this folder) |
| `build_docs.py` | Writes the site's generated pages |
| `example.py`, `vocab_forms.py`, `wheelock_forms.py`, `known_issues.py` | Example scripts, below |
| `LICENSE` | The AGPL v3 licence, which covers the code |
| `pyproject.toml` | Package metadata; [RELEASING.md](RELEASING.md) covers releases |
| `AGENTS.md`, `.agents/skills/` | Notes for AI coding agents working in the repo |

The submodules are only needed to read or build the Ada. To fetch them:
`git submodule update --init`. Both use HTTPS URLs, so no SSH keys are
needed.

### Example scripts

Run these from the repo root.

| Script | What it does |
|---|---|
| `example.py` | Looks up one word and prints its forms and tags |
| `vocab_forms.py` | Writes every N-letter form of the words in a vocab CSV (for a Wordle list) |
| `wheelock_forms.py` | Writes every form of all 880 Wheelock vocab words to `wheelock-forms.json`, downloading the vocab first if needed |
| `known_issues.py` | Shows the Wheelock words the lookup still gets wrong, with why and whether each could be fixed |

## Developing

- **Check a change:** `python3 -m omnes_formae.verify --save before.txt`
  before it, then `--compare before.txt` after. It regenerates the list,
  checks known forms and lookups, and lists what changed.
- **Lint:** `ruff check --select E,F,I,UP,B omnes_formae`.
- **Docs:** edit `docs/*.md` directly, except `docs/api.md` and
  `docs/limitations.md`, which `python3 build_docs.py` writes from the
  docstrings and `LIMITATIONS.md`. Rerun it after changing either;
  `--check` reports pages that are out of date. To preview the site, run
  `python3 -m http.server -d docs` and open <http://localhost:8000>.
- **Release:** see [RELEASING.md](RELEASING.md).

## AI disclosure

The code and docs in this repo were written with an AI assistant (Claude, by
Anthropic). [njg4ne](https://github.com/njg4ne) directed the work and reviewed it, and decides what is
committed. Whitaker's data files are copied unchanged, not AI-written.

## Licence

The code is licensed under the GNU Affero General Public License, version 3
or any later version: see
[LICENSE](https://github.com/njg4ne/whitakers-words/blob/main/LICENSE).
Whitaker's data files keep their own licence, below.

## Data and licence

The files in `omnes_formae/data/whitaker/` are copied unchanged from
the [mk270 fork](https://github.com/mk270/whitakers-words) at commit `1f2f0fb`.
They are covered by Whitaker's licence in
`omnes_formae/data/whitaker/LICENCE.txt`. The files in
`omnes_formae/data/bespoke/` were written for this project: the
English tag labels and part-of-speech words the lookup uses.
