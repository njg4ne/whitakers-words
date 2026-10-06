"""python -m omnes_formae [--format txt|csv|json] [-o FILE] [--data-dir DIR]"""

import argparse
import sys
from pathlib import Path

from .all_forms import FORMATS, write_forms
from .paths import WHITAKER_DIR


class ProgressBar:
    """A one-line bar on stderr, redrawn only when the percentage changes."""

    WIDTH = 30

    def __init__(self, label: str) -> None:
        self.label = label
        self.percent = -1

    def __call__(self, done: int, total: int) -> None:
        percent = done * 100 // total
        if percent == self.percent:
            return
        self.percent = percent
        filled = self.WIDTH * done // total
        bar = "#" * filled + "-" * (self.WIDTH - filled)
        sys.stderr.write(f"\r{self.label} [{bar}] {percent:3d}%")
        sys.stderr.flush()

    def close(self) -> None:
        if self.percent >= 0:
            sys.stderr.write("\r\033[K")  # clear the bar's line
            sys.stderr.flush()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m omnes_formae",
        description=(
            "Write every Latin form in Whitaker's Words: one per line (txt), "
            "or one row per form and tag with the lookup's keys (csv, json)."
        ),
    )
    parser.add_argument(
        "-f", "--format", choices=FORMATS, default="txt",
        help="output format (default: txt)",
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="output file (default: forms.FORMAT)"
    )
    parser.add_argument(
        "--data-dir", type=Path, default=WHITAKER_DIR,
        help="folder with DICTLINE.GEN, INFLECTS.LAT and UNIQUES.LAT",
    )
    parser.add_argument(
        "--no-progress", action="store_true",
        help="no progress bar (it is shown only when stderr is a terminal)",
    )
    args = parser.parse_args()

    output = args.output or Path(f"forms.{args.format}")
    bar = None
    if not args.no_progress and sys.stderr.isatty():
        bar = ProgressBar(f"Writing {output.name}")
    try:
        count = write_forms(output, args.data_dir, args.format, bar)
    finally:
        if bar:
            bar.close()
    unit = "forms" if args.format == "txt" else "rows"
    print(f"Wrote {count:,} {unit} to {output}")


if __name__ == "__main__":
    main()
