"""Build every form of a dictionary entry: stem + each ending that fits."""

from collections.abc import Iterator

from .dictline import Entry, keyed_stems, pack_tackon
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
    endings = candidate_endings(entry, groups)
    if entry.pos == "PACK":
        forms = _pack_forms(entry, endings)
    else:
        forms = (
            stem + ending.text
            for key, stem in keyed_stems(entry)
            for ending in endings
            if ending_fits(entry, key, ending)
            and verb_form_allowed(entry, stem, ending)
        )
    return [form for form in dict.fromkeys(forms) if form]


def _pack_forms(entry: Entry, endings: list[Ending]) -> Iterator[str]:
    """qu- pronoun + ending + tackon, e.g. cu + ius + cumque."""
    tackon = pack_tackon(entry)
    if not tackon:
        return
    for key, stem in keyed_stems(entry):
        for ending in endings:
            if pack_ending_fits(entry, key, ending):
                form = stem + ending.text
                # m becomes n before -dam: quem + dam -> quendam
                if tackon.startswith("dam") and form.endswith("m"):
                    form = form[:-1] + "n"
                yield form + tackon
