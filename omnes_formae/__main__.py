"""python -m omnes_formae [-o forms.txt] [--data-dir DIR]"""

import argparse
from pathlib import Path

from .all_forms import write_forms
from .paths import WHITAKER_DIR


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m omnes_formae",
        description="Write every Latin form in Whitaker's Words, one per line.",
    )
    parser.add_argument("-o", "--output", type=Path, default=Path("forms.txt"))
    parser.add_argument(
        "--data-dir", type=Path, default=WHITAKER_DIR,
        help="folder with DICTLINE.GEN, INFLECTS.LAT and UNIQUES.LAT",
    )
    args = parser.parse_args()

    count = write_forms(args.output, args.data_dir)
    print(f"Wrote {count:,} forms to {args.output}")


if __name__ == "__main__":
    main()
