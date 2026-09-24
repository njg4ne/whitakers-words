"""Read INFLECTS.LAT, the table of endings, one ending per line.

A line reads: part of speech, class ("which var", where the part of speech
has one), grammar tags, stem key, ending length, ending, age, frequency.
A length of 0 means the bare stem, and then the ending itself is absent:

    N     3 0 GEN S X  2 2 is        X A
    N     3 0 NOM S X  1 0           X A
"""

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

# The grammar tags after the class, per part of speech.
TAG_FIELDS = {
    "N": ("case", "number", "gender"),
    "PRON": ("case", "number", "gender"),
    "ADJ": ("case", "number", "gender", "comparison"),
    "NUM": ("case", "number", "gender", "sort"),
    "V": ("tense", "voice", "mood", "person", "number"),
    "VPAR": ("case", "number", "gender", "tense", "voice", "mood"),
    "SUPINE": ("case", "number", "gender"),
    "ADV": ("comparison",),
    "PREP": ("case",),
    "CONJ": (),
    "INTERJ": (),
}
NO_CLASS = ("ADV", "PREP", "CONJ", "INTERJ")

# Participles and supines are built on verb entries (Eff_Part in the Ada).
ENTRY_POS = {"VPAR": "V", "SUPINE": "V"}


@dataclass(frozen=True)
class Ending:
    pos: str
    decl: tuple[int, int] | None
    key: int
    text: str
    case: str = "X"
    number: str = "X"
    gender: str = "X"
    comparison: str = "X"
    sort: str = "X"
    tense: str = "X"
    voice: str = "X"
    mood: str = "X"
    person: int = 0


def parse_line(line: str) -> Ending | None:
    tokens = line.split("--")[0].split()
    if not tokens:
        return None
    pos = tokens[0]
    if tokens[-3].isdigit():  # length 0: no ending text
        text, key, middle = "", int(tokens[-4]), tokens[1:-4]
    else:
        text, key, middle = tokens[-3], int(tokens[-5]), tokens[1:-5]

    decl = None
    if pos not in NO_CLASS:
        decl, middle = (int(middle[0]), int(middle[1])), middle[2:]
    tags = dict(zip(TAG_FIELDS[pos], middle, strict=True))
    if "person" in tags:
        tags["person"] = int(tags["person"])
    return Ending(pos=pos, decl=decl, key=key, text=text, **tags)


def load_endings(path: Path) -> dict[tuple[str, int | None], list[Ending]]:
    """All endings, grouped by (entry part of speech, declension/conjugation).

    The table is small (~1,800 lines), so it is held in memory. Grouping lets
    each dictionary entry look at only the endings that could apply to it.
    """
    groups = defaultdict(list)
    with path.open(encoding="latin-1") as f:
        for line in f:
            ending = parse_line(line)
            if ending:
                which = ending.decl[0] if ending.decl else None
                groups[ENTRY_POS.get(ending.pos, ending.pos), which].append(ending)
    return dict(groups)
