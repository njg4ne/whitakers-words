"""How a word is named: its citation form and its dictionary form.

The citation form is the one form a vocab list uses to name a word: amo
for a verb, femina for a noun, bonus for an adjective. The dictionary form
is the longer heading a dictionary prints, like "amo, amare, amavi, amatus".

Both are picked out of a word's tagged forms, the (form, ending) pairs that
generate.tagged_forms_of makes.
"""

from .dictline import Entry
from .inflects import Ending
from .tags import DECLINED, LABELS

TaggedForms = list[tuple[str, Ending]]

GENDER_ABBREVIATIONS = LABELS["gender_abbreviation"]  # "f." in "femina, feminae, f."


def first_with(tagged: TaggedForms, **wanted: tuple) -> str | None:
    """The first form whose ending has one of the wanted values for each
    attribute, e.g. first_with(tagged, case=("NOM",), number=("S",))."""
    for form, ending in tagged:
        if all(getattr(ending, name) in values for name, values in wanted.items()):
            return form
    return None


def citation_forms(entry: Entry, tagged: TaggedForms, strict: bool) -> TaggedForms:
    """The tagged forms that may name this word in a vocab list.

    Strict means the usual citation form: the nominative singular (masculine
    for adjectives), or the 1st person singular present indicative of a verb.
    Not strict also allows what vocab lists use for words that lack the
    usual form: any nominative (insidiae, nos), any case of a pronoun (me),
    and a verb's infinitive or perfect (-, coepisse, coepi).
    """
    if entry.pos == "V":
        return _verb_citations(entry, tagged, strict)
    if entry.pos in DECLINED or entry.pos == "PACK":
        return _declined_citations(entry, tagged, strict)
    if entry.pos == "ADV":
        return [(form, e) for form, e in tagged if e.comparison in ("POS", "X")]
    return tagged  # uninflected words have just the one form


def _verb_citations(entry: Entry, tagged: TaggedForms, strict: bool) -> TaggedForms:
    """amo, not amor: a dictionary lists a verb by its active form, or by
    its passive one for a deponent (conor). So a plain "amor" names the noun.

    Only the loose pass, used when nothing else matched, accepts the other
    voice. That finds the root of a passive that a vocab list gives its own
    entry: videor ("seem") is video. With pos="verb", "amor" gives amo.
    """
    person = 3 if entry.kind == "IMPERS" else 1  # oportet
    voices = ["PASSIVE" if entry.kind == "DEP" else "ACTIVE", "X"]
    listed = [("PRES", "IND", person, "S")]
    if not strict:
        voices += ["ACTIVE", "PASSIVE"]
        listed += [
            ("PRES", "INF", 0, "X"),
            ("PERF", "INF", 0, "X"),
            ("PERF", "IND", person, "S"),
        ]
    return [
        (form, e)
        for form, e in tagged
        if e.pos == "V"
        and e.voice in voices
        and (e.tense, e.mood, e.person, e.number) in listed
    ]


def _declined_citations(
    entry: Entry, tagged: TaggedForms, strict: bool
) -> TaggedForms:
    nominative = ("NOM", "X")  # X: an indeclinable word such as nihil
    if strict:
        masculine_only = entry.pos in ("ADJ", "NUM")  # bonus, not bona
        comparisons = _naming_comparisons(entry)
        return [
            (form, e)
            for form, e in tagged
            if e.case in nominative
            and e.number in ("S", "X")
            and (not masculine_only or e.gender in ("M", "C", "X"))
            and e.comparison in comparisons
        ]
    if entry.pos == "PRON":
        return tagged
    return [(form, e) for form, e in tagged if e.case in nominative]


def _naming_comparisons(entry: Entry) -> tuple[str, str]:
    """magnus is named by its positive, not by maximus. A word that exists
    only as a comparative or superlative (maximus) is named by that."""
    if entry.comparison in ("COMP", "SUPER"):
        return (entry.comparison, "X")
    return ("POS", "X")


def dictionary_form(entry: Entry, tagged: TaggedForms) -> str:
    """The heading a dictionary prints for this word."""
    if not tagged:
        return ""
    if entry.pos == "N":
        return _noun_heading(entry, tagged)
    if entry.pos == "V":
        return _verb_heading(entry, tagged)
    if entry.pos == "NUM":
        return _numeral_heading(tagged)
    if entry.pos in ("ADJ", "PRON", "PACK"):
        return _adjective_heading(entry, tagged)
    return tagged[0][0]


def _noun_heading(entry: Entry, tagged: TaggedForms) -> str:
    """femina, feminae, f. (plural-only nouns use their plural: insidiae)"""
    parts = []
    for number in ("S", "P", "X"):
        nominative = first_with(tagged, case=("NOM", "X"), number=(number,))
        if nominative:
            parts.append(nominative)
            genitive = first_with(tagged, case=("GEN",), number=(number,))
            if genitive:
                parts.append(genitive)
            break
    if entry.gender in GENDER_ABBREVIATIONS:
        parts.append(GENDER_ABBREVIATIONS[entry.gender])
    return ", ".join(parts)


def _verb_heading(entry: Entry, tagged: TaggedForms) -> str:
    """amo, amare, amavi, amatus; conor, conari, conatus sum"""
    voice = ("PASSIVE",) if entry.kind == "DEP" else ("ACTIVE",)
    person = (3,) if entry.kind == "IMPERS" else (1,)
    present = first_with(
        tagged, pos=("V",), tense=("PRES",), mood=("IND",), person=person,
        number=("S",), voice=voice,
    )
    infinitive = first_with(
        tagged, pos=("V",), tense=("PRES",), mood=("INF",), voice=voice
    )
    # esse has no perfect participle; its stem 4 + us would make "futus".
    participle_tense = ("FUT",) if entry.kind == "TO_BE" else ("PERF",)
    participle = first_with(
        tagged, pos=("VPAR",), tense=participle_tense, case=("NOM",),
        number=("S",), gender=("M", "C", "X"),
    )

    if entry.kind in ("DEP", "SEMIDEP"):
        perfect = participle + " sum" if participle else None
        parts = [present, infinitive, perfect]
    else:
        perfect = first_with(
            tagged, pos=("V",), tense=("PERF",), mood=("IND",), person=person,
            number=("S",), voice=("ACTIVE",),
        )
        parts = [present, infinitive, perfect, participle]
    return ", ".join(part or "-" for part in parts)


def _numeral_heading(tagged: TaggedForms) -> str:
    """One form per sort: unus, primus, singuli, semel"""
    parts = []
    for sort in LABELS["sort"]:
        form = first_with(
            tagged, sort=(sort,), case=("NOM", "X"), gender=("M", "C", "X")
        )
        if form:
            parts.append(form)
    return ", ".join(parts)


def _adjective_heading(entry: Entry, tagged: TaggedForms) -> str:
    """bonus, bona, bonum; fortis, forte; ingens, gen. ingentis; hic, haec, hoc"""
    gender_endings = {"M": ("M", "C", "X"), "F": ("F", "C", "X"), "N": ("N", "X")}
    parts = []
    for genders in gender_endings.values():
        form = first_with(
            tagged, case=("NOM",), number=("S",), gender=genders,
            comparison=_naming_comparisons(entry),
        )
        if form and form not in parts:
            parts.append(form)

    # One form for all genders: add the genitive, as dictionaries do.
    if len(parts) == 1 and entry.pos == "ADJ":
        genitive = first_with(tagged, case=("GEN",), number=("S",))
        if genitive and genitive != parts[0]:
            parts.append(f"gen. {genitive}")
    return ", ".join(parts) or tagged[0][0]
