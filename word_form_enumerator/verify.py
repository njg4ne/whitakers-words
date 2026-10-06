"""Check the forms list and the lookup after a change. One command, no shell
pipelines:

    python3 -m word_form_enumerator.verify --save before.txt   # before a change
    python3 -m word_form_enumerator.verify --compare before.txt   # after it

It prints the line and unique counts, checks forms that must and must not be
in the list, checks a few lookups, and with --compare lists the forms added
and removed since the saved run. It exits with status 1 if a check fails.
"""

import argparse
import sys
import tempfile
from pathlib import Path

from .all_forms import write_forms
from .lookup import get_latin_forms

# Forms that must be in the list, by what they cover.
PRESENT = {
    "1st conjugation": "amo amabantur amabar amatus",
    "3rd conjugation, perfect, participle": "ago agere egit actus",
    "3rd declension, two stems": "mater matris matrem matribus",
    "esse (made up in the Ada, not in DICTLINE)": "sum es est fuit esse",
    "sum compound": "abes",
    "deponent": "sequor sequi secutus",
    "irregular stems": "tuli latus eo it",
    "short imperatives": "dic fer",
    "qu- pronoun + tackon": "quicumque cujuscumque quendam",
    "idem (pronoun + -dem)": "idem eundem eiusdem",
    "impersonal, with its infinitive": "oportet oportere",
}
# Forms that must not be: deponents have no active forms, and the bare
# stems of idem aren't words.
ABSENT = "sequo eun eorun"

# Vocab entry, part of speech, and the headings get_latin_forms must return.
LOOKUPS = [
    ("amo, amare, amavi, amatum", "verb", {"amo, amare, amavi, amatus"}),
    ("amor", None, {"amor, amoris, m."}),  # the noun, not the passive of amo
    ("videor", "verb", {"video, videre, vidi, visus"}),
    ("os, oris", "noun", {"os, oris, n."}),
    ("idem, eadem, idem", "pronoun", {"idem, eadem"}),
    ("quisquis", "pronoun", {"quisquis"}),
    ("semel", "adverb", {"unus, primus, singuli, semel"}),
]


def main() -> None:
    parser = argparse.ArgumentParser(prog="python3 -m word_form_enumerator.verify")
    parser.add_argument("--save", type=Path, help="save the unique forms here")
    parser.add_argument("--compare", type=Path, help="compare with saved forms")
    args = parser.parse_args()

    forms = _generate()
    forms_ok = _check_forms(forms)
    lookups_ok = _check_lookups()
    ok = forms_ok and lookups_ok
    if args.save:
        args.save.write_text("".join(f + "\n" for f in sorted(forms)), encoding="utf-8")
        print(f"Saved {len(forms):,} unique forms to {args.save}")
    if args.compare:
        _compare(forms, args.compare)
    sys.exit(0 if ok else 1)


def _generate() -> set[str]:
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "forms.txt"
        lines = write_forms(path)
        forms = set(path.read_text(encoding="utf-8").split())
    print(f"{lines:,} lines, {len(forms):,} unique")
    return forms


def _check_forms(forms: set[str]) -> bool:
    ok = True
    for covers, words in PRESENT.items():
        for word in words.split():
            if word not in forms:
                print(f"MISSING {word} ({covers})")
                ok = False
    for word in ABSENT.split():
        if word in forms:
            print(f"UNEXPECTED {word}")
            ok = False
    if ok:
        print("All forms as expected")
    return ok


def _check_lookups() -> bool:
    ok = True
    for entry, pos, expected in LOOKUPS:
        headings = {row["lemma"] for row in get_latin_forms(entry, pos)}
        if headings != expected:
            print(f"LOOKUP {entry!r}: got {sorted(headings)}")
            print(f"    expected {sorted(expected)}")
            ok = False
    if ok:
        print("All lookups as expected")
    return ok


def _compare(forms: set[str], saved_path: Path) -> None:
    saved = set(saved_path.read_text(encoding="utf-8").split())
    added, removed = sorted(forms - saved), sorted(saved - forms)
    print(f"Since {saved_path}: {len(added)} added, {len(removed)} removed")
    for word in added[:50]:
        print(f"  + {word}")
    for word in removed[:50]:
        print(f"  - {word}")


if __name__ == "__main__":
    main()
