"""The flat list: every form of every word, one per line.

Each DICTLINE.GEN stem is joined to every INFLECTS.LAT ending that fits it,
then the spelled-out forms in UNIQUES.LAT are added. DICTLINE is read a line
at a time and each word's forms are written straight to the file, so only
the endings are held in memory.
"""

from collections.abc import Iterator
from pathlib import Path

from .dictline import read_entries
from .generate import forms_of
from .inflects import load_endings
from .paths import WHITAKER_DIR
from .uniques import read_unique_forms


def iter_forms(data_dir: Path = WHITAKER_DIR) -> Iterator[list[str]]:
    """Yield the forms entry by entry, then the irregular forms from UNIQUES."""
    groups = load_endings(data_dir / "INFLECTS.LAT")
    for entry in read_entries(data_dir / "DICTLINE.GEN"):
        yield forms_of(entry, groups)
    yield list(read_unique_forms(data_dir / "UNIQUES.LAT"))


def write_forms(out_path: Path, data_dir: Path = WHITAKER_DIR) -> int:
    """Write every form to out_path, one per line, and return the line count.

    Forms are unique within an entry, but the same spelling can come from
    several entries; pipe the result through `sort -u` to deduplicate.
    """
    count = 0
    with out_path.open("w", encoding="utf-8") as out:  # buffered by Python
        for forms in iter_forms(data_dir):
            out.writelines(form + "\n" for form in forms)
            count += len(forms)
    return count
