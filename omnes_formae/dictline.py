"""Read DICTLINE.GEN, the lexicon, one entry per line.

Columns 1-76 hold four stem slots of 19 characters each. From column 77 on,
the fields are separated by spaces: the part of speech, its class fields, five
one-letter flags (age, area, geography, frequency, source), and the meaning.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

STEM_WIDTH = 19
STEM_SLOTS = 4
FLAG_COUNT = 5
ZZZ = "zzz"  # marks a stem that does not exist

# The class fields that follow each part of speech. "which var" is the
# declension or conjugation and its variant, e.g. "3 1".
CLASS_FIELDS = {
    "N": ("which", "var", "gender", "kind"),
    "PRON": ("which", "var", "kind"),
    "PACK": ("which", "var", "kind"),
    "ADJ": ("which", "var", "comparison"),
    "NUM": ("which", "var", "sort", "value"),
    "ADV": ("comparison",),
    "V": ("which", "var", "kind"),
    "PREP": ("case",),
    "CONJ": (),
    "INTERJ": (),
}


@dataclass(frozen=True)
class Entry:
    stems: tuple[str, ...]
    pos: str
    decl: tuple[int, int] | None = None  # (which, var)
    gender: str = "X"
    kind: str = "X"
    comparison: str = "X"
    sort: str = "X"
    case: str = "X"
    meaning: str = ""
    freq: str = "X"  # A most common ... F very rare (4th of the 5 flags)
    line: int = 0  # line number in DICTLINE.GEN; 0 for ESSE


# esse is not in DICTLINE; the Ada build adds it (makedict_main.adb, Be_Ve).
# Its second stem is deliberately empty so that "" + "es" gives "es".
ESSE = Entry(
    stems=("s", "", "fu", "fut"), pos="V", decl=(5, 1), kind="TO_BE", freq="A"
)


def parse_line(line: str, number: int = 0) -> Entry:
    stems = tuple(
        line[i * STEM_WIDTH:(i + 1) * STEM_WIDTH].strip() for i in range(STEM_SLOTS)
    )
    pos, _, rest = line[STEM_SLOTS * STEM_WIDTH:].strip().partition(" ")
    names = CLASS_FIELDS[pos]
    tokens = rest.split(None, len(names) + FLAG_COUNT)
    fields = dict(zip(names, tokens, strict=False))
    meaning = tokens[-1] if len(tokens) > len(names) + FLAG_COUNT else ""

    decl = None
    if "which" in fields:
        decl = (int(fields.pop("which")), int(fields.pop("var")))
    fields.pop("value", None)
    flags = tokens[len(names):len(names) + FLAG_COUNT]
    freq = flags[3] if len(flags) > 3 else "X"
    return Entry(
        stems=stems, pos=pos, decl=decl, meaning=meaning, freq=freq, line=number,
        **fields,
    )


def read_entries(path: Path) -> Iterator[Entry]:
    with path.open(encoding="latin-1") as f:
        for number, line in enumerate(f, 1):
            line = line.rstrip("\r\n")
            if line.strip():
                yield parse_line(line, number)
    yield ESSE


def count_entries(path: Path) -> int:
    """How many entries read_entries yields, without parsing them."""
    with path.open(encoding="latin-1") as f:
        return sum(1 for line in f if line.strip()) + 1  # + ESSE


def keyed_stems(entry: Entry) -> list[tuple[int, str]]:
    """Pair each usable stem with the key that INFLECTS endings refer to.

    Mirrors how makedict_main.adb writes STEMLIST.GEN. Key 0 means "stems 1
    and 2 are the same", and matches endings for either key.
    """
    s = entry.stems
    same_12 = s[0] == s[1] and s[0] != ZZZ

    if entry.kind == "TO_BE":
        return list(enumerate(s, 1))
    if entry.pos == "N" and same_12:
        return [(0, s[0])]
    if entry.pos in ("ADJ", "V") and same_12:
        return [(0, s[0])] + _usable([(3, s[2]), (4, s[3])])
    if entry.pos == "ADJ" and entry.comparison in ("COMP", "SUPER"):
        return [({"COMP": 3, "SUPER": 4}[entry.comparison], s[0])]
    if entry.pos == "ADV" and entry.comparison in ("COMP", "SUPER"):
        return [({"COMP": 2, "SUPER": 3}[entry.comparison], s[0])]
    if entry.pos == "NUM" and entry.sort != "X":
        return [({"CARD": 1, "ORD": 2, "DIST": 3, "ADVERB": 4}[entry.sort], s[0])]
    return _usable(list(enumerate(s, 1)))


def _usable(pairs: list[tuple[int, str]]) -> list[tuple[int, str]]:
    return [(key, stem) for key, stem in pairs if stem and stem != ZZZ]


def tackon(entry: Entry) -> str:
    """The tackon an entry always takes, from a meaning like "(w/-cumque) ..."
    or "(w/-dem ONLY, idem, eadem, idem) ...". Empty for most entries."""
    if not entry.meaning.startswith("(w/-"):
        return ""
    return entry.meaning[4:].split(")")[0].split()[0]
