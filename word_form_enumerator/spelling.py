"""Compare Latin spellings, and pick words out of a vocab-list entry.

A vocab list writes a word the way a textbook does: "amo, amare, amavi,
amatum", "fama, -ae, f.", "in (+ abl.)", "utrum...an". These helpers find
the Latin words in such an entry and spell them so they can be compared
with Whitaker's forms.
"""

import re
import unicodedata


def normalize(text: str) -> str:
    """Spell a word for comparing: letters only, lowercase, no macrons, and
    i for j and u for v, as Whitaker's parser does with its input.

    "Āmō" -> "amo", "iuvenis" and "juvenis" -> "iuuenis"
    """
    letters = unicodedata.normalize("NFD", text)  # splits ā into a + macron
    letters = "".join(c for c in letters if c.isascii() and c.isalpha())
    return letters.lower().replace("j", "i").replace("v", "u")


def entry_parts(entry: str) -> list[str]:
    """The comma-separated parts of a vocab entry, without notes in brackets.

    "in (+ abl.)" -> ["in"]; "utrum...an" -> ["utrum", "an"]
    """
    entry = re.sub(r"\(.*?\)", "", entry)
    parts = re.split(r",|\.\.\.", entry)
    return [part.strip() for part in parts if part.strip()]


def first_word(entry: str) -> str:
    """The first part that is a Latin word, normalized.

    "amo, amare, amavi, amatum" -> "amo"; "-, coepisse, coepi" -> "coepisse"
    """
    for part in entry_parts(entry):
        if normalize(part):
            return normalize(part)
    return ""


def is_enclitic(entry: str) -> bool:
    """Whether the entry is a word ending such as "-que" or "-ne"."""
    parts = entry_parts(entry)
    return bool(parts) and parts[0].startswith("-") and bool(normalize(parts[0]))


def other_words(entry: str) -> list[str]:
    """The spelled-out words after the first, normalized. Abbreviations
    ("-ae", "f.", "gen. ingentis") and two-word parts ("ausus sum") are
    skipped, since they aren't single forms.

    "amo, amare, amavi, amatum" -> ["amare", "amaui", "amatum"]
    """
    words = []
    for part in entry_parts(entry)[1:]:
        if part.startswith("-") or part.endswith(".") or " " in part:
            continue
        if normalize(part):
            words.append(normalize(part))
    return words
