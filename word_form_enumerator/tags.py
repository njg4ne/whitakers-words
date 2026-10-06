"""Readable grammar tags for a form, such as
"imperfect active indicative 3rd person singular".

The same grammatical slot always gets the same tag string, in every word, so
the distinct tags can be offered as choices (for example, in a drop-down).
"""

import json

from .inflects import Ending
from .paths import BESPOKE_DIR

# The English word for each Whitaker code, by category: LABELS["case"]["NOM"]
# is "nominative". See data/bespoke/README.md.
LABELS = json.loads((BESPOKE_DIR / "labels.json").read_text(encoding="utf-8"))
GENDERS = LABELS["gender"]

# Parts of speech that have cases.
DECLINED = ("N", "ADJ", "PRON", "NUM")

# Whitaker gives some endings a shared gender: C (masculine or feminine) or
# X (any). On these parts of speech an X ending gets one row per gender, so
# that choosing "feminine" also finds "fortis".
SPELL_OUT_X_GENDER = ("ADJ", "NUM", "VPAR")


def genders_for(ending: Ending) -> list[str]:
    """The genders to give this ending a row each, or [""] for no gender.

    A noun's gender belongs to the noun, not to each form, so noun forms get
    no gender. Neither do indeclinable forms (case X).
    """
    if ending.pos in ("N", "SUPINE") or ending.case == "X":
        return [""]
    if ending.gender == "C":
        return ["M", "F"]
    if ending.gender == "X":
        if ending.pos in SPELL_OUT_X_GENDER:
            return ["M", "F", "N"]
        return [""]
    if ending.gender in GENDERS:
        return [ending.gender]
    return [""]


def tag_parts(ending: Ending, gender: str) -> dict[str, str]:
    """The grammar categories of one form, in the order the tag reads them.

    Categories that don't apply (Whitaker's X, or person 0) are left out.
    """
    pos = ending.pos
    parts = {}
    if pos == "NUM":
        parts["sort"] = LABELS["sort"].get(ending.sort)
    if pos in ("ADJ", "ADV"):
        parts["comparison"] = LABELS["comparison"].get(ending.comparison)
    if pos in ("V", "VPAR"):
        parts["tense"] = LABELS["tense"].get(ending.tense)
        parts["voice"] = LABELS["voice"].get(ending.voice)
        parts["mood"] = LABELS["mood"].get(ending.mood)
    if pos == "SUPINE":
        parts["mood"] = LABELS["mood"]["SUPINE"]
    if pos == "V":
        parts["person"] = LABELS["person"].get(str(ending.person))
        parts["number"] = LABELS["number"].get(ending.number)
    if pos in (*DECLINED, "VPAR", "SUPINE", "PREP"):
        parts["case"] = LABELS["case"].get(ending.case)
    if pos in (*DECLINED, "VPAR"):
        parts["number"] = LABELS["number"].get(ending.number)
        parts["gender"] = GENDERS.get(gender)
    return {name: value for name, value in parts.items() if value}


def tag_text(ending: Ending, parts: dict[str, str]) -> str:
    """Join the parts into one tag, e.g. "present active infinitive"."""
    if ending.pos == "PREP" and "case" in parts:
        return f"takes {parts['case']}"  # a preposition's case is the one it takes
    if parts:
        return " ".join(parts.values())
    if ending.pos in DECLINED:
        return "indeclinable"
    return "uninflected"
