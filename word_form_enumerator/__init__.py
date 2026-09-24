"""Enumerate every inflected form in Whitaker's Words, one per line.

The forms come from joining each DICTLINE.GEN stem to every INFLECTS.LAT
ending that fits it, plus the spelled-out forms in UNIQUES.LAT. See
docs/data.md for how the files relate.
"""

from collections.abc import Iterator
from pathlib import Path

from .dictline import read_entries
from .generate import forms_of
from .inflects import load_endings
from .uniques import read_unique_forms

DATA_DIR = Path(__file__).parent / "data"


def iter_forms(data_dir: Path = DATA_DIR) -> Iterator[list[str]]:
    """Yield the forms entry by entry, reading DICTLINE a line at a time."""
    groups = load_endings(data_dir / "INFLECTS.LAT")
    for entry in read_entries(data_dir / "DICTLINE.GEN"):
        yield forms_of(entry, groups)
    yield list(read_unique_forms(data_dir / "UNIQUES.LAT"))


def write_forms(out_path: Path, data_dir: Path = DATA_DIR) -> int:
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
