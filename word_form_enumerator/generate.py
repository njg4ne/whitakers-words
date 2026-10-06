"""Build every form of a dictionary entry: stem + each ending that fits."""

from collections.abc import Iterator

from .dictline import Entry, keyed_stems, tackon
from .inflects import Ending
from .rules import ending_fits, pack_ending_fits, verb_form_allowed

EndingGroups = dict[tuple[str, int | None], list[Ending]]


def candidate_endings(entry: Entry, groups: EndingGroups) -> list[Ending]:
    """Endings for the entry's class, plus the ones shared by every variant."""
    pos = "PRON" if entry.pos == "PACK" else entry.pos
    if entry.decl is None:
        return groups.get((pos, None), [])
    which = entry.decl[0]
    shared = groups.get((pos, 0), []) if which != 0 else []
    return groups.get((pos, which), []) + shared


def forms_of(entry: Entry, groups: EndingGroups) -> list[str]:
    """All distinct forms of one entry, in the order they were generated."""
    return list(dict.fromkeys(form for form, _ in tagged_forms_of(entry, groups)))


def tagged_forms_of(entry: Entry, groups: EndingGroups) -> Iterator[tuple[str, Ending]]:
    """Each form of one entry with the ending that made it. A form recurs
    once per ending that spells it (amici: GEN S and NOM P)."""
    endings = candidate_endings(entry, groups)
    if entry.pos == "PACK":
        pairs = _pack_forms(entry, endings)
    else:
        pairs = (
            (stem + ending.text, ending)
            for key, stem in keyed_stems(entry)
            for ending in endings
            if ending_fits(entry, key, ending)
            and verb_form_allowed(entry, stem, ending)
        )
        # idem is "i" + dem. INFLECTS already spells these PRON 4 2 endings
        # for -dem (eun + dem -> eundem), so the bare forms aren't words.
        if entry.pos == "PRON" and tackon(entry):
            pairs = ((form + tackon(entry), ending) for form, ending in pairs)
    return ((form, ending) for form, ending in pairs if form)


def _pack_forms(entry: Entry, endings: list[Ending]) -> Iterator[tuple[str, Ending]]:
    """qu- pronoun + ending + tackon, e.g. cu + ius + cumque."""
    tack = tackon(entry)
    if not tack:
        return
    for key, stem in keyed_stems(entry):
        for ending in endings:
            if pack_ending_fits(entry, key, ending):
                form = stem + ending.text
                # m becomes n before -dam: quem + dam -> quendam
                if tack.startswith("dam") and form.endswith("m"):
                    form = form[:-1] + "n"
                yield form + tack, ending
