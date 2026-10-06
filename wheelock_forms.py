"""Write every form of every Wheelock vocab word to a JSON file.

    python3 wheelock_forms.py      # wheelock-vocab.json -> wheelock-forms.json

wheelock-vocab.json is the 40 chapter files behind
https://www.warmenhoven.org/latin/vocab/display.html joined into one list.
If it's missing, this downloads it. It isn't committed: it's someone else's
data, with no licence found. The output is a list with one object per
(form, tag): the fields from get_latin_forms plus the word's Wheelock
chapter and English.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from word_form_enumerator import get_latin_forms

VOCAB = Path("wheelock-vocab.json")
OUTPUT = Path("wheelock-forms.json")
CHAPTER_URL = "https://www.warmenhoven.org/latin/vocab/dict/{}.json"
CHAPTERS = 40


def download_vocab() -> None:
    words = []
    for chapter in range(1, CHAPTERS + 1):
        with urllib.request.urlopen(CHAPTER_URL.format(chapter)) as response:
            words.extend(json.load(response))
    VOCAB.write_text(json.dumps(words, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Downloaded {len(words)} words to {VOCAB}")


def main() -> None:
    if not VOCAB.exists():
        try:
            download_vocab()
        except urllib.error.URLError as error:
            # On macOS, python.org's Python needs "Install Certificates.command"
            # (in its Applications folder) before it can check HTTPS sites.
            sys.exit(f"Couldn't download the vocab ({error.reason}). If it's a "
                     "certificate error on macOS, run Install Certificates.command "
                     "from your Python's Applications folder.")
    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    rows, unmatched = [], []
    for word in vocab:
        forms = get_latin_forms(word["latin"], word["type"])
        if not forms:
            unmatched.append(word["latin"])
        for form in forms:
            rows.append(
                {"chapter": word["chapter"], "english": word["english"], **form}
            )

    # One object per line keeps a 90,000-row file readable and diffable.
    with OUTPUT.open("w", encoding="utf-8") as f:
        f.write("[\n" + ",\n".join(json.dumps(row) for row in rows) + "\n]\n")
    matched = len(vocab) - len(unmatched)
    print(f"Wrote {len(rows):,} forms of {matched} words to {OUTPUT}")
    if unmatched:
        print("No match:", "; ".join(unmatched))


if __name__ == "__main__":
    main()
