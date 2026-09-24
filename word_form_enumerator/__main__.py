"""python -m word_form_enumerator [-o forms.txt] [--data-dir DIR]"""

import argparse
from pathlib import Path

from . import DATA_DIR, write_forms


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m word_form_enumerator",
        description="Write every Latin form in Whitaker's Words, one per line.",
    )
    parser.add_argument("-o", "--output", type=Path, default=Path("forms.txt"))
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()

    count = write_forms(args.output, args.data_dir)
    print(f"Wrote {count:,} forms to {args.output}")


if __name__ == "__main__":
    main()
