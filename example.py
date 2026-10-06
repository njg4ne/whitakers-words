"""Look up one vocab word and print its forms.

    python3 example.py
"""

from omnes_formae import PartOfSpeech, get_latin_forms

if __name__ == "__main__":
    entry = "liber, libri"
    rows = get_latin_forms(entry, PartOfSpeech.NOUN)
    print(f"{len(rows)} forms of {entry!r}: {rows[0]['lemma']} ({rows[0]['meaning']})")
    for row in rows:
        print(f"  {row['word']:<10} {row['tag']}")
