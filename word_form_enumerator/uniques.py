"""Read UNIQUES.LAT: irregular forms spelled out in full.

Each record is three lines: the form, its grammar tags, its meaning.

    agatur
    V      3 1 PRES PASSIVE SUB 3 S  IMPERS             F  X  X  E  E
    let it be treated; let it be a matter or question of;
"""

from collections.abc import Iterator
from pathlib import Path

RECORD_LINES = 3


def read_unique_forms(path: Path) -> Iterator[str]:
    with path.open(encoding="latin-1") as f:
        lines = [line.strip() for line in f if line.strip()]
    yield from lines[::RECORD_LINES]
