"""The flat list: every form of every word, one per line, or tagged rows.

Each DICTLINE.GEN stem is joined to every INFLECTS.LAT ending that fits it,
then the spelled-out forms in UNIQUES.LAT are added. DICTLINE is read a line
at a time and each word's forms are written straight to the file, so only
the endings are held in memory.

The csv and json formats write lookup.iter_tagged_forms's rows instead,
also as they come.
"""

import csv
import json
from collections.abc import Iterator
from pathlib import Path

from .dictline import count_entries, read_entries
from .generate import forms_of
from .inflects import load_endings
from .lookup import ROW_KEYS, Progress, iter_tagged_forms
from .paths import WHITAKER_DIR
from .uniques import read_unique_forms


def iter_forms(data_dir: Path = WHITAKER_DIR) -> Iterator[list[str]]:
    """Yield the forms entry by entry, then the irregular forms from UNIQUES."""
    groups = load_endings(data_dir / "INFLECTS.LAT")
    for entry in read_entries(data_dir / "DICTLINE.GEN"):
        yield forms_of(entry, groups)
    yield list(read_unique_forms(data_dir / "UNIQUES.LAT"))


FORMATS = ("txt", "csv", "json")


def write_forms(
    out_path: Path,
    data_dir: Path = WHITAKER_DIR,
    format: str = "txt",
    progress: Progress | None = None,
) -> int:
    """Write every form to out_path and return how many forms or rows.

    Args:
        format: "txt" writes one form per line. Forms are unique within an
            entry, but the same spelling can come from several entries;
            pipe the result through `sort -u` to deduplicate. "csv" and
            "json" write one row per (form, tag) of every word, with the
            keys of get_latin_forms's rows (see iter_tagged_forms): a CSV
            with ROW_KEYS as its header, or a JSON array of objects.
        progress: if given, called as progress(done, total) as the run
            works through the dictionary's entries (txt) or words (csv,
            json). The command line uses it to draw a progress bar.
    """
    if format not in FORMATS:
        raise ValueError(f"format must be one of {FORMATS}, not {format!r}")
    count = 0
    # newline="" lets the csv module end rows itself.
    with out_path.open("w", encoding="utf-8", newline="") as out:
        if format == "txt":
            total = count_entries(data_dir / "DICTLINE.GEN") + 1  # + UNIQUES
            for done, forms in enumerate(iter_forms(data_dir), 1):
                out.writelines(form + "\n" for form in forms)
                count += len(forms)
                if progress:
                    progress(done, total)
        elif format == "csv":
            writer = csv.DictWriter(out, ROW_KEYS, lineterminator="\n")
            writer.writeheader()
            for row in iter_tagged_forms(data_dir, progress):
                row["entry_ids"] = " ".join(map(str, row["entry_ids"]))
                writer.writerow(row)
                count += 1
        else:
            out.write("[")
            for row in iter_tagged_forms(data_dir, progress):
                out.write(",\n" if count else "\n")
                ordered = {key: row[key] for key in ROW_KEYS if key in row}
                out.write(json.dumps(ordered, ensure_ascii=False))
                count += 1
            out.write("\n]\n")
    return count
