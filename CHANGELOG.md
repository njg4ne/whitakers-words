# Changelog

Each release of `omnes_formae`, newest first. Versions follow
[semantic versioning](https://semver.org): while the major version is 0, a
minor bump (0.3.0) adds features and a patch bump (0.2.1) only fixes things.

## 0.3.0 (2026-10-06)

- **`--format csv` and `--format json`** (`-f`) write one row per form and
  grammatical slot of every word, with the same keys as `get_latin_forms`'s
  rows. `txt`, one form per line, stays the default. Without `-o`, the output
  file is `forms.txt`, `forms.csv` or `forms.json`.
- **`iter_tagged_forms()`** yields those rows from Python, and
  `write_forms(..., format="csv")` writes them. `ROW_KEYS` gives the column
  order.
- **A progress bar** on stderr while the command runs, shown only when stderr
  is a terminal. `--no-progress` turns it off. From Python, pass
  `progress=callback` to `write_forms` or `iter_tagged_forms`.
- This changelog, also on the docs site.

## 0.2.1 (2026-10-06)

- **Git installs work without SSH keys.** Both submodules are registered
  with `https://` URLs; the mk270 one used SSH, so
  `pip install "git+https://..."` failed for most people.
- The docs show both ways to install: the release zip, or Git.

## 0.2.0 (2026-10-06)

The first packaged release.

- Renamed from `word_form_enumerator` to `omnes_formae`; the command is
  `omnes-formae`.
- Installable with pip or uv from the release's zip (`pyproject.toml`).
- Licensed under the GNU AGPL v3 or later. Whitaker's data keeps its own
  licence.
- A docs site, served from `docs/`, with a generated API reference.
- Includes the work before packaging: the flat list of every form
  (`write_forms`, `iter_forms`), the tagged lookup (`get_latin_forms`), and
  `python -m omnes_formae.verify`.

---

AI disclosure: written with an AI assistant (Claude, by Anthropic), directed
and reviewed by [njg4ne](https://github.com/njg4ne).
