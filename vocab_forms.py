"""Write every N-letter form of the words in a vocab CSV.

    python3 vocab_forms.py                 # 5-letter forms -> vocab-forms.txt
    python3 vocab_forms.py -n 6 -o six.txt --vocab vocab.csv

The CSV needs "Part of speech" and "Dictionary Entry" columns, with entries
like "amo, amare, amavi, amatum" or "fama, -ae, f.". Each entry is looked up
with get_latin_forms, which finds the dictionary word it names. vocab.csv
isn't committed; use any CSV with those columns.
"""

import argparse
import csv
import sys
from pathlib import Path

from word_form_enumerator import get_latin_forms


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("-n", "--length", type=int, default=5, help="letters per form")
    parser.add_argument("-o", "--output", type=Path, default=Path("vocab-forms.txt"))
    parser.add_argument("--vocab", type=Path, default=Path("vocab.csv"))
    args = parser.parse_args()

    with args.vocab.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    forms, unmatched = set(), []
    for row in rows:
        entry = row["Dictionary Entry"]
        found = get_latin_forms(entry, row["Part of speech"])
        if not found:
            unmatched.append(entry)
        forms.update(r["word"] for r in found if len(r["word"]) == args.length)

    args.output.write_text("".join(f + "\n" for f in sorted(forms)), encoding="utf-8")
    print(f"Wrote {len(forms):,} {args.length}-letter forms to {args.output}")
    if unmatched:
        print("No dictionary match:", "; ".join(unmatched), file=sys.stderr)


if __name__ == "__main__":
    main()
