"""Look up a vocab-list word and list every form of it, with readable tags.

    >>> rows = get_latin_forms("amo, amare, amavi, amatum", "verb")
    >>> rows[0]["word"], rows[0]["tag"]
    ('amo', 'present active indicative 1st person singular')

The steps, each in its own module:

1. spelling.py finds the first Latin word in the entry ("amo").
2. words.py groups the data files' lines into dictionary words.
3. citation.py decides which words that entry names, and how a dictionary
   prints each one ("amo, amare, amavi, amatus").
4. This module narrows homographs by the entry's other words, tags each
   form with tags.py, and merges homographs whose forms are all the same.

Each row's "tag" is the same string for the same grammatical slot in every
word, so the distinct tags can be the options of a multi-select.
"""

import json
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from .citation import TaggedForms, citation_forms, dictionary_form
from .codes import Age, Frequency, PartOfSpeech
from .dictline import CLASS_FIELDS
from .generate import EndingGroups
from .inflects import Ending, load_endings
from .paths import BESPOKE_DIR, WHITAKER_DIR
from .spelling import first_word, is_enclitic, normalize, other_words
from .tags import genders_for, tag_parts, tag_text
from .words import Word, read_words

# English part-of-speech words -> PartOfSpeech codes. Several may apply, as
# in Wheelock's "adjective, cardinal". See data/bespoke/README.md.
POS_WORDS = json.loads((BESPOKE_DIR / "pos_words.json").read_text(encoding="utf-8"))

# Called as progress(done, total) while a long run works through the words.
Progress = Callable[[int, int], None]

# Every key a row can have, in the order a table shows them. The grammar
# keys (case to sort) are present only when they apply.
ROW_KEYS = (
    "word", "root", "lemma", "meaning", "pos", "tag",
    "case", "number", "gender", "tense", "voice", "mood", "person",
    "comparison", "sort",
    "lemma_frequency", "form_frequency", "form_age", "entry_id", "entry_ids",
)


def get_latin_forms(
    word: str, pos: str | PartOfSpeech | None = None, data_dir: Path = WHITAKER_DIR
) -> list[dict]:
    """Every form of the dictionary word that a vocab-list entry names.

    Args:
        word: the vocab entry, e.g. "amo, amare, amavi, amatum", "femina",
            or "in (+ abl.)". Its first Latin word is the dictionary word's
            citation form (the form a dictionary lists it under), and the
            other spelled-out words help choose among homographs ("os, oris"
            is mouth, not bone). Case, macrons, i/j and u/v don't matter.
        pos: optional part of speech: English words ("noun",
            "adjective, cardinal"), a PartOfSpeech, or its code ("V").

    Returns:
        One dict per (form, grammatical slot). See docs/lookup.md for every key.
        An empty list means no word matched, or the entry is an enclitic
        ("-que") or a prefix, which Whitaker doesn't keep as words.

    The data is loaded on the first call (a fraction of a second) and kept,
    so later calls, one word or thousands, take about a millisecond each.
    """
    if is_enclitic(word):
        return []
    target = first_word(word)
    if not target:
        raise ValueError(f"no Latin word in {word!r}")
    codes = pos_codes(pos)
    if codes == set():
        return []

    data = _load(data_dir)
    candidates = []
    for found in data.candidates(target):
        candidates.append((found, found.tagged_forms(data.groups)))
    matches = _named_words(candidates, target, codes)
    matches = _narrow_by_other_words(matches, other_words(word))

    row_lists = [list(_rows(word, *match)) for match in matches]
    return _merge_same_forms(row_lists)


def iter_tagged_forms(
    data_dir: Path = WHITAKER_DIR, progress: Progress | None = None
) -> Iterator[dict]:
    """Every tagged form of every word in the dictionary, as rows.

    The rows have the same keys as get_latin_forms's, and come word by
    word in dictionary order. With no vocab entry to name a word, each row's
    "root" is the word's dictionary heading, the same as its "lemma".
    Homographs aren't merged: caelum "heaven" and caelum "chisel" each get
    their own rows.

    The words are read into memory (a fraction of a second); the rows are
    made one word at a time, so they can be written out as they come. If
    given, progress(done, total) is called after each word.
    """
    groups = load_endings(data_dir / "INFLECTS.LAT")
    words = read_words(data_dir)
    for done, word in enumerate(words, 1):
        yield from _rows(None, word, word.tagged_forms(groups))
        if progress:
            progress(done, len(words))


def pos_codes(pos: str | PartOfSpeech | None) -> set[str] | None:
    """PartOfSpeech codes for a part of speech. None means any part of
    speech, and an empty set means one that DICTLINE has no words for
    ("enclitic").

    "adjective, cardinal" -> {"ADJ", "NUM"}
    """
    if not pos:
        return None
    codes = set()
    known = False
    for token in pos.replace(",", " ").replace("(", " ").split():
        if token in CLASS_FIELDS:
            codes.add(token)
            known = True
        elif token.lower() in POS_WORDS:
            codes.update(POS_WORDS[token.lower()])
            known = True
    if not known:
        raise ValueError(f"unknown part of speech {pos!r}")
    return codes


@dataclass
class _Data:
    """Everything a lookup needs, loaded once."""

    words_by_stem: dict[str, list[Word]]  # normalized stem -> words
    groups: EndingGroups  # the endings, as generate.py wants them
    ending_spellings: dict[str, set[str]]  # part of speech -> ending spellings

    def candidates(self, target: str) -> list[Word]:
        """The words that could spell `target`, in dictionary order. Only
        stems that start `target` are looked at, so this is quick."""
        found = {}
        for length in range(len(target) + 1):
            for word in self.words_by_stem.get(target[:length], []):
                spellings = self.ending_spellings.get(word.entry.pos, set())
                if word.could_spell(target, spellings):
                    found[word.order] = word
        return [found[order] for order in sorted(found)]


@cache
def _load(data_dir: Path) -> _Data:
    words = read_words(data_dir)
    words_by_stem: dict[str, list[Word]] = {}
    for word in words:
        # A UNIQUES-only word has no stems; its whole forms act as stems.
        for stem in word.stems | word.spelled_keys:
            words_by_stem.setdefault(stem, []).append(word)

    groups = load_endings(data_dir / "INFLECTS.LAT")
    ending_spellings: dict[str, set[str]] = {}
    for (pos, _), endings in groups.items():
        spellings = ending_spellings.setdefault(pos, set())
        spellings.update(normalize(ending.text) for ending in endings)
    return _Data(words_by_stem, groups, ending_spellings)


# A word the entry names, its tagged forms, and the endings of the forms
# that matched the entry's first word.
Match = tuple[Word, TaggedForms, list[Ending]]


def _named_words(
    candidates: list[tuple[Word, TaggedForms]], target: str, codes: set[str] | None
) -> list[Match]:
    """The words whose citation form is `target`. Tries the strictest rules
    first, and loosens them only when nothing matched:

    1. the usual citation form, in the given part of speech;
    2. other forms vocab lists use (insidiae, me, coepisse);
    3. both again in any part of speech, since a vocab list's labels may
       not be Whitaker's (Wheelock's adverb etiam is a conjunction there).
    """
    passes = [(codes, True), (codes, False)]
    if codes:
        passes += [(None, True), (None, False)]

    for wanted, strict in passes:
        matches = []
        for word, tagged in candidates:
            if wanted and word.entry.pos not in wanted:
                continue
            cited = []
            for form, ending in citation_forms(word.entry, tagged, strict):
                if normalize(form) == target:
                    cited.append(ending)
            if cited:
                matches.append((word, tagged, cited))
        if matches:
            return matches
    return []


def _narrow_by_other_words(matches: list[Match], others: list[str]) -> list[Match]:
    """Narrow homographs by what the entry spells out: keep the words that
    have the most of its other words among their forms ("os, oris" is
    mouth, not bone, since oris is a form only of mouth). With no other
    words, or none found, every match is kept."""
    if len(matches) < 2 or not others:
        return matches
    counts = [_count_found(tagged, others) for _, tagged, _ in matches]
    best = max(counts)
    if best == 0:
        return matches
    return [match for match, n in zip(matches, counts, strict=True) if n == best]


def _count_found(tagged: TaggedForms, wanted: list[str]) -> int:
    """How many of the `wanted` words are among the forms."""
    forms = {normalize(form) for form, _ in tagged}
    return sum(1 for word in wanted if word in forms)


def _merge_same_forms(row_lists: list[list[dict]]) -> list[dict]:
    """Combine homographs whose heading and (form, tag) rows are all the
    same, such as caelum "heaven" and caelum "chisel". They differ only in
    meaning, so one set of rows carries both meanings."""
    merged: dict[tuple, list[dict]] = {}
    for rows in row_lists:
        if not rows:
            continue
        key = (rows[0]["lemma"], frozenset((row["word"], row["tag"]) for row in rows))
        if key not in merged:
            merged[key] = rows
            continue
        kept, other = merged[key][0], rows[0]
        frequencies = (kept["lemma_frequency"], other["lemma_frequency"])
        combined = {
            "meaning": kept["meaning"] + " | " + other["meaning"],
            "entry_ids": kept["entry_ids"] + other["entry_ids"],
            "lemma_frequency": min(frequencies, key=lambda f: f.rank),
        }
        for row in merged[key]:
            row.update(combined)
    return [row for rows in merged.values() for row in rows]


def _rows(
    root: str | None,
    word: Word,
    tagged: TaggedForms,
    cited: list[Ending] | None = None,
) -> Iterator[dict]:
    """One row per (form, tag) of the word, without repeats. With no root,
    the root is the word's dictionary heading."""
    entry = word.entry
    lemma = dictionary_form(entry, tagged)
    if root is None:
        root = lemma

    # A numeral entry holds four words (unus, primus, singuli, semel). Keep
    # only the sort that the vocab entry named.
    if entry.pos == "NUM" and cited is not None:
        sorts = {ending.sort for ending in cited}
        tagged = [(form, ending) for form, ending in tagged if ending.sort in sorts]

    seen = set()
    for form, ending in tagged:
        for gender in genders_for(ending):
            parts = tag_parts(ending, gender)
            tag = tag_text(ending, parts)
            if (form, tag) in seen:
                continue
            seen.add((form, tag))
            yield {
                "word": form,
                "root": root,
                "lemma": lemma,
                "meaning": word.meaning,
                "entry_id": entry.line,
                "entry_ids": [entry.line],
                "lemma_frequency": Frequency(entry.freq),
                "pos": PartOfSpeech(ending.pos),
                "tag": tag,
                **parts,
                "form_age": Age(ending.age),
                "form_frequency": Frequency(ending.freq),
            }
