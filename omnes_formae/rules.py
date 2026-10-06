"""Which endings apply to which stems, ported from the Ada parser.

Class and key matching come from Reduce_Stem_List in
src/words_engine/words_engine-word_package.adb and the "<=" operators in
src/latin_utils/latin_utils-inflections_package.adb. The verb checks come
from Allowed_Stem in src/words_engine/words_engine-list_sweep.adb.
"""

from .dictline import Entry
from .inflects import Ending

# Parts of speech where stem key 0 (stems 1 and 2 identical) matches endings
# for key 1 or key 2.
KEY_0_POS = ("N", "ADJ", "V")


def decl_fits(entry_decl, ending_decl) -> bool:
    """Exact class, or the ending's variant is 0 (all variants), or the
    ending is 0 0 (every class except 9, the abbreviations)."""
    which, _ = entry_decl
    return (
        ending_decl == entry_decl
        or ending_decl == (which, 0)
        or (ending_decl == (0, 0) and which != 9)
    )


def gender_fits(entry_gender: str, ending_gender: str) -> bool:
    """X fits any noun, and C (common) fits any noun that isn't neuter."""
    return (
        ending_gender in (entry_gender, "X")
        or (ending_gender == "C" and entry_gender != "N")
    )


def comparison_fits(entry_comparison: str, ending_comparison: str) -> bool:
    return "X" in (entry_comparison, ending_comparison) or (
        entry_comparison == ending_comparison
    )


def key_fits(pos: str, stem_key: int, ending_key: int) -> bool:
    return (
        ending_key in (stem_key, 0)
        or (stem_key == 0 and pos in KEY_0_POS and ending_key in (1, 2))
    )


def ending_fits(entry: Entry, stem_key: int, ending: Ending) -> bool:
    """Whether this ending can attach to this stem of this entry."""
    if not key_fits(entry.pos, stem_key, ending.key):
        return False
    match entry.pos:
        case "N":
            return decl_fits(entry.decl, ending.decl) and gender_fits(
                entry.gender, ending.gender
            )
        case "PRON" | "V":
            return decl_fits(entry.decl, ending.decl)
        case "ADJ":
            return decl_fits(entry.decl, ending.decl) and comparison_fits(
                entry.comparison, ending.comparison
            )
        case "NUM":
            return decl_fits(entry.decl, ending.decl) and stem_key == ending.key
        case "ADV":
            return comparison_fits(entry.comparison, ending.comparison)
        case "PREP":
            return entry.case == ending.case
        case "CONJ" | "INTERJ":
            return True
    return False


def verb_form_allowed(entry: Entry, stem: str, ending: Ending) -> bool:
    """Drop finite verb forms that a verb of this kind doesn't have."""
    if ending.pos != "V":
        return True
    tense, voice, mood, person = ending.tense, ending.voice, ending.mood, ending.person

    # dic, duc, fac, fer: the only 3rd-conjugation short imperatives.
    if (
        entry.decl == (3, 1)
        and (tense, voice, mood, person) == ("PRES", "ACTIVE", "IMP", 2)
        and ending.number == "S"
        and ending.text == ""
        and not stem.endswith(("dic", "duc", "fac", "fer"))
    ):
        return False

    # Imperatives exist only in the present 2nd person and future 2nd/3rd.
    if mood == "IMP" and not (
        (tense == "PRES" and person == 2) or (tense == "FUT" and person in (2, 3))
    ):
        return False

    # Impersonal verbs: 3rd person only. The Ada also rejects the infinitive
    # (person 0); we keep it, since forms like "oportere" are real.
    if entry.kind == "IMPERS" and person not in (3, 0):
        return False

    # Deponents: no active finite forms or infinitives, except the future
    # active infinitive.
    finite_or_inf = mood in ("IND", "SUB", "IMP", "INF")
    if entry.kind == "DEP" and voice == "ACTIVE" and finite_or_inf:
        return mood == "INF" and tense == "FUT"

    # Semi-deponents: active in the present system, passive in the perfect.
    if entry.kind == "SEMIDEP" and mood in ("IND", "SUB", "IMP"):
        if voice == "PASSIVE" and tense in ("PRES", "IMPF", "FUT"):
            return False
        if voice == "ACTIVE" and tense in ("PERF", "PLUP", "FUTP"):
            return False

    return True


def pack_ending_fits(entry: Entry, stem_key: int, ending: Ending) -> bool:
    """PACK entries (qu- + tackon) take only PRON endings of exactly their
    class (Process_Packons in word_package.adb)."""
    return (
        ending.pos == "PRON"
        and ending.decl == entry.decl
        and key_fits("PRON", stem_key, ending.key)
    )
