"""Group the data files' lines into dictionary words.

Most words are one DICTLINE line. A few span several, and are merged here:

- A line whose meaning starts with "|" continues the meaning of the line
  before it.
- Whitaker splits each qu- pronoun (qui, quis, aliquis) into partial
  paradigms, one line per class variant, that share a kind and a meaning.
- A UNIQUES.LAT record spells out one irregular form (quisquis, vult,
  boum). Records that share a meaning become one word of their own. They
  don't join the DICTLINE word they belong to (vult isn't a form of volo
  here), because the records don't say which word that is.
"""

from dataclasses import dataclass, field
from pathlib import Path

from .dictline import ZZZ, Entry, read_entries, tackon
from .generate import EndingGroups, tagged_forms_of
from .inflects import Ending
from .spelling import normalize
from .uniques import read_unique_records


@dataclass
class Word:
    """One dictionary word: its DICTLINE lines and any spelled-out forms."""

    entries: list[Entry]
    meaning: str
    order: int  # position in the dictionary, to keep results in that order
    stems: set[str] = field(default_factory=set)  # normalized
    spelled_out: list[tuple[str, Ending]] = field(default_factory=list)
    spelled_keys: set[str] = field(default_factory=set)  # spelled_out, normalized

    @property
    def entry(self) -> Entry:
        """The first line, which names the word and gives its class."""
        return self.entries[0]

    def add(self, entry: Entry) -> None:
        self.entries.append(entry)
        for stem in entry.stems:
            # Blank and zzz slots are unused stems; only esse really has a
            # blank stem ("" + es), as in dictline.keyed_stems.
            if stem == ZZZ or (stem == "" and entry.kind != "TO_BE"):
                continue
            self.stems.add(normalize(stem))

    def spell_out(self, form: str, ending: Ending) -> None:
        self.spelled_out.append((form, ending))
        self.spelled_keys.add(normalize(form))

    def could_spell(self, target: str, ending_spellings: set[str]) -> bool:
        """A quick test, before generating any forms: could a stem plus a
        real ending, or a spelled-out form, spell `target`?"""
        if target in self.spelled_keys:
            return True
        # idem is i + dem: check the part before the tackon.
        tack = tackon(self.entry)
        if self.entry.pos == "PRON" and tack and target.endswith(tack):
            target = target[: -len(tack)]
        for stem in self.stems:
            if not target.startswith(stem):
                continue
            # PACK forms also carry a tackon (quicumque), so the stem is enough.
            if self.entry.pos == "PACK" or target[len(stem):] in ending_spellings:
                return True
        return False

    def tagged_forms(self, groups: EndingGroups) -> list[tuple[str, Ending]]:
        """Every (form, ending) pair of the word, generated ones first."""
        tagged = []
        for entry in self.entries:
            if entry.stems:  # a UNIQUES-only word has no stems
                tagged.extend(tagged_forms_of(entry, groups))
        return tagged + self.spelled_out


def read_words(data_dir: Path) -> list[Word]:
    """Every dictionary word in DICTLINE.GEN and UNIQUES.LAT."""
    words = _read_dictline_words(data_dir / "DICTLINE.GEN")
    _add_unique_forms(words, data_dir / "UNIQUES.LAT")
    return words


def _read_dictline_words(path: Path) -> list[Word]:
    words: list[Word] = []
    pronouns: dict[tuple, Word] = {}  # partial qu- paradigms, by what they share
    for entry in read_entries(path):
        previous = words[-1].entries[-1] if words else None
        if _continues(entry, previous):
            words[-1].add(entry)
            words[-1].meaning += " " + entry.meaning.lstrip("|")
            continue

        shared = _pronoun_paradigm(entry)
        if shared and shared in pronouns:
            pronouns[shared].add(entry)
            continue

        word = Word([], entry.meaning, order=len(words))
        word.add(entry)
        words.append(word)
        if shared:
            pronouns[shared] = word
    return words


def _pronoun_paradigm(entry: Entry) -> tuple | None:
    """What a pronoun's partial paradigms have in common: the stem, the
    declension (but not its variant), the kind and the meaning."""
    if entry.pos not in ("PRON", "PACK"):
        return None
    return (entry.pos, entry.stems[0], entry.decl[0], entry.kind, entry.meaning)


def _continues(entry: Entry, previous: Entry | None) -> bool:
    """Whether `entry` is a "|" line continuing the line before it."""
    return (
        previous is not None
        and entry.meaning.startswith("|")
        and (entry.pos, entry.stems) == (previous.pos, previous.stems)
    )


def _add_unique_forms(words: list[Word], path: Path) -> None:
    """Make a word of each set of UNIQUES records that share a meaning."""
    by_meaning: dict[tuple, Word] = {}
    for form, ending, entry in read_unique_records(path):
        key = (entry.pos, entry.meaning)
        if key not in by_meaning:
            by_meaning[key] = Word([entry], entry.meaning, order=len(words))
            words.append(by_meaning[key])
        by_meaning[key].spell_out(form, ending)
