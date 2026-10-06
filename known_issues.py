"""Show the Wheelock words that get_latin_forms still handles poorly.

    python3 known_issues.py

Above each case: why it happens, then whether and how it could be fixed.
"""

from word_form_enumerator import get_latin_forms

# Return nothing. (Wheelock "latin", Wheelock "type")
NO_MATCH = [
    # Why: enclitics are TACKONs in ADDONS.LAT, which the Ada strips off the
    # end of a word before parsing it. They aren't dictionary words, so an
    # entry starting with "-" now returns nothing on purpose.
    # Fix: not needed for a Wordle. They never stand alone.
    ("-ne", "enclitic"),
    # Why and fix: same as -ne.
    ("-que", "enclitic, conjunction"),
    # Why and fix: same as -ne.
    ("-ve", "enclitic, conjunction"),
    # Why: prefixes are PREFIX records in ADDONS.LAT, stripped off the front
    # of a word before the rest is looked up.
    # Fix: not needed. The compound verbs that use it are their own entries.
    ("re-, red-", "prefix"),
    # Why: Whitaker has no entry for Troia; it lists few proper names.
    # Fix: only by adding data, such as a local supplement file of
    # DICTLINE-format lines read after DICTLINE.
    ("Troia, -ae", "noun"),
    # Why: compound numbers are two words; Whitaker has viginti and unus
    # separately and parses each on its own.
    # Fix: possible but our own logic (join agreeing forms of both parts).
    # Not useful for a Wordle, since every form has a space.
    ("viginti unus", "adjective, cardinal"),
    # Why and fix: same as viginti unus.
    ("viginti duo", "adjective, cardinal"),
    # Why and fix: same as viginti unus.
    ("viginti tres", "adjective, cardinal"),
    # Why and fix: same as viginti unus.
    ("viginti quattuor", "adjective, cardinal"),
    # Why and fix: same as viginti unus.
    ("viginti quinque", "adjective, cardinal"),
    # Why and fix: same as viginti unus, for a two-word ordinal.
    ("tertius decimus, -a, -um", "adjective, ordinal"),
    # Why and fix: same as tertius decimus.
    ("quintus decimus, -a, -um", "adjective, ordinal"),
    # Why and fix: same as tertius decimus.
    ("septimus decimus, -a, -um", "adjective, ordinal"),
    # Why and fix: same as tertius decimus.
    ("vicesimus primus, -a, -um", "adjective, ordinal"),
    # Why and fix: same as tertius decimus.
    ("vicesimus secundus, -a, -um", "adjective, ordinal"),
    # Why and fix: same as tertius decimus.
    ("vicesimus tertius, -a, -um", "adjective, ordinal"),
    # Why and fix: same as tertius decimus.
    ("vicesimus quartus, -a, -um", "adjective, ordinal"),
    # Why and fix: same as tertius decimus.
    ("vicesimus quintus, -a, -um", "adjective, ordinal"),
]

# Match, but with the wrong word, more than one word, or a surprising tag.
POOR_MATCH = [
    # Why: Whitaker has only the masculine noun philosophus (N 2 1 M). With no
    # noun named philosopha, the fallback ignores the part of speech and finds
    # the feminine of the adjective philosophus ("philosophical").
    # Fix: only by adding data (philosopha, N 1 1 F), or by listing it as
    # philosophus.
    ("philosopha, -ae", "noun"),
    # Why: Whitaker has no entry for melior; it's the comparative of bonus.
    # The loose pass finds it among bonus's forms and returns all of bonus.
    # Fix: yes. When the match came through a comparative or superlative,
    # keep only the rows of that degree, as numerals keep only their sort.
    ("melior, melius", "adjective"),
    # Why: Wheelock calls it an adverb, Whitaker a conjunction, so it only
    # matches on the fallback that ignores the part of speech.
    # Fix: not needed. The forms are right; only the label differs.
    ("etiam", "adverb"),
    # Why: Whitaker has no conjunction cum; it files "when" as an adverb.
    # The fallback then finds both the adverb and the preposition.
    # Fix: yes, a small table of Wheelock-to-Whitaker labels (conjunction ->
    # ADV for cum). For a Wordle it doesn't matter: both are just "cum".
    ("cum", "conjunction"),
    # Why: Whitaker has two prepositions "in", one taking the ablative and one
    # the accusative. The "(+ abl.)" note is dropped before matching.
    # Fix: yes. Read "+ abl." or "+ acc." from the note and keep the
    # preposition whose tag is "takes ablative". Same form either way.
    ("in (+ abl.)", "preposition"),
    # Why: Wheelock's "ne" covers both of Whitaker's: the adverb "not" and
    # the conjunction "that not, lest". Both are as frequent.
    # Fix: not needed. Both are the one form "ne".
    ("ne", "adverb, conjunction"),
    # Why: "adjective, ordinal" maps to both ADJ and NUM, and Whitaker has
    # both: the adjective secundus ("following, favorable") and the ordinal
    # stem of duo. Their forms are the same.
    # Fix: yes. Map "ordinal" and "cardinal" to NUM only, ignoring
    # "adjective" when they appear with it.
    ("secundus, -a, -um", "adjective, ordinal"),
    # Why: Whitaker splits qui by kind and meaning: relative (REL),
    # indefinite (INDEF) and two adjectival ones (ADJECT). Three have the same
    # forms and are merged; the indefinite "any" has qua for quae, so it stays
    # separate.
    # Fix: not needed. Both are real; for a Wordle, deduplicate by word.
    ("qui, quae, quod", "pronoun"),
    # Why: the same split for quis: interrogative "who?" and indefinite
    # "anyone", whose forms differ a little.
    # Fix: same as qui.
    ("quis, quid", "pronoun"),
    # Why: DICTLINE has scio twice with the same meaning, as 4th conjugation
    # (V 3 4) and as V 6 1. Their forms differ slightly.
    # Fix: yes. Merge words with the same first stem, part of speech and
    # meaning, keeping every form.
    ("scio, scire, scivi, scitum", "verb"),
    # Why: Whitaker splits vis into "vis, vis" (singular) and "vis, viris"
    # (plural, "strength"). Wheelock's "vis, vis" names the first, but
    # "viris" doesn't appear in the entry to break the tie.
    # Fix: yes. Merge them (Wheelock teaches one noun), or give the teacher
    # both.
    ("vis, vis", "noun"),
    # Why: Whitaker tags deponent forms by their shape, so conor is PASSIVE.
    # The entry's kind (DEP) is what says it's active in meaning.
    # Fix: yes, but it's a decision: leave voice out of deponent tags, or say
    # "deponent". It changes tag strings, so decide before the students
    # build on them.
    ("conor, conari, conatus sum", "verb"),
    # Why: Whitaker files the personal pronoun as one word, ego, and me is
    # one of its forms.
    # Fix: probably not needed. All of ego is likely what a teacher wants.
    ("me", "pronoun"),
]

# Match the right word, but common forms are missing.
MISSING_FORMS = [
    # Why: vult, vis and vultis are only in UNIQUES.LAT, as records that
    # don't say which word they belong to, so they became a separate word.
    # Fix: yes. Attach each record to the word with the same class whose
    # citation form it belongs to (a hand-made table for the ~15 sets would
    # be the reliable way; matching by meaning was tried and was wrong).
    ("volo, velle, volui", "verb", ["vult", "vis", "vultis"]),
    # Why: same as volo; di, dii and dis are UNIQUES records. Also, the only
    # common deus in DICTLINE is the capitalized "De" line ("God (Christian
    # text); god"), so the forms come back capitalized: Deus, Dei.
    # Fix: same as volo for the missing forms. Lowercase forms when building
    # a Wordle list.
    ("deus, -i", "noun", ["di", "dii", "dis"]),
]


def describe(latin: str, pos: str) -> list[dict]:
    rows = get_latin_forms(latin, pos)
    words = {}
    for row in rows:
        words.setdefault(row["entry_id"], (row["lemma"], row["pos"], row["meaning"]))
    print(f"{latin!r} ({pos}): {len(rows)} forms from {len(words)} words")
    for lemma, form_pos, meaning in words.values():
        print(f"    {lemma} [{form_pos}] {meaning[:50]}")
    return rows


def main() -> None:
    print("== No match ==")
    for latin, pos in NO_MATCH:
        describe(latin, pos)

    print("\n== Poor match ==")
    for latin, pos in POOR_MATCH:
        rows = describe(latin, pos)
        if latin.startswith("conor"):
            print(f"    first tag: {rows[0]['tag']}")

    print("\n== Missing forms ==")
    for latin, pos, expected in MISSING_FORMS:
        found = {row["word"] for row in describe(latin, pos)}
        missing = [form for form in expected if form not in found]
        print(f"    missing: {', '.join(missing) or 'none'}")


if __name__ == "__main__":
    main()
