"""Read UNIQUES.LAT: irregular forms spelled out in full.

Each record is three lines: the form, its grammar tags, its meaning.

    agatur
    V      3 1 PRES PASSIVE SUB 3 S  IMPERS             F  X  X  E  E
    let it be treated; let it be a matter or question of;

The tags line is an INFLECTS-style part of speech, class and tags, then the
word's kind (IMPERS, ADJECT, ...) where it has one, then five flags (age,
area, geography, frequency, source).
"""

from collections.abc import Iterator
from pathlib import Path

from .dictline import FLAG_COUNT, Entry
from .inflects import ENTRY_POS, NO_CLASS, TAG_FIELDS, Ending

RECORD_LINES = 3


def read_unique_forms(path: Path) -> Iterator[str]:
    with path.open(encoding="latin-1") as f:
        lines = [line.strip() for line in f if line.strip()]
    yield from lines[::RECORD_LINES]


def read_unique_records(path: Path) -> Iterator[tuple[str, Ending, Entry]]:
    """Each record as (form, its ending's tags, a one-form entry).

    The entry's line is the record's first line number, negated, so that it
    can't be mistaken for a DICTLINE line.
    """
    with path.open(encoding="latin-1") as f:
        numbered = [(n, line.strip()) for n, line in enumerate(f, 1) if line.strip()]
    for i in range(0, len(numbered), RECORD_LINES):
        (number, form), (_, tags), (_, meaning) = numbered[i:i + RECORD_LINES]
        ending, entry = _parse_tags(form, tags, meaning, -number)
        yield form, ending, entry


def _parse_tags(
    form: str, line: str, meaning: str, number: int
) -> tuple[Ending, Entry]:
    tokens = line.split()
    flags = tokens[-FLAG_COUNT:]
    pos, rest = tokens[0], tokens[1:-FLAG_COUNT]

    decl = None
    if pos not in NO_CLASS:
        decl, rest = (int(rest[0]), int(rest[1])), rest[2:]
    names = TAG_FIELDS[pos]
    tags = dict(zip(names, rest, strict=False))
    if "person" in tags:
        tags["person"] = int(tags["person"])
    kind = rest[len(names)] if len(rest) > len(names) else "X"

    age, freq = flags[0], flags[3]
    ending = Ending(
        pos=pos, decl=decl, key=0, text=form, age=age, freq=freq, **tags
    )
    entry = Entry(
        stems=(),
        pos=ENTRY_POS.get(pos, pos),
        decl=decl,
        gender=tags.get("gender", "X") if pos == "N" else "X",
        kind=kind,
        meaning=meaning,
        freq=freq,
        line=number,
    )
    return ending, entry
