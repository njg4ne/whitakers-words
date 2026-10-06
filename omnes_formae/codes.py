"""Whitaker's one-word codes, as enums with readable names.

Each enum copies an Ada type from the Whitaker's Words source,
src/latin_utils/latin_utils-inflections_package.ads (mk270), with the same
members in the same order. The values are the codes the data files use, so
a member is also that string: PartOfSpeech.VERB == "V", and json.dumps
writes "V". (Python 3.11's StrEnum would do the same, but this package
supports 3.10.)
"""

from enum import Enum


class _Code(str, Enum):
    def __str__(self) -> str:
        return self.value  # "V", not "PartOfSpeech.VERB"


class PartOfSpeech(_Code):
    """Part_Of_Speech_Type. A lookup row's "pos" is one of these."""

    UNKNOWN = "X"  # all, none, or unknown
    NOUN = "N"
    PRONOUN = "PRON"
    PACKON = "PACK"  # qu- pronoun + tackon (quicumque); its forms' pos is PRON
    ADJECTIVE = "ADJ"
    NUMERAL = "NUM"
    ADVERB = "ADV"
    VERB = "V"
    PARTICIPLE = "VPAR"  # a form of a verb entry
    SUPINE = "SUPINE"  # a form of a verb entry
    PREPOSITION = "PREP"
    CONJUNCTION = "CONJ"
    INTERJECTION = "INTERJ"
    # In ADDONS.LAT only: parts of words, not words. No row has these.
    TACKON = "TACKON"
    PREFIX = "PREFIX"
    SUFFIX = "SUFFIX"


class Frequency(_Code):
    """Frequency_Type: how common a word, or one spelling of an ending, is.

    The same letters mean slightly different things for the two. For a
    dictionary word (a row's "lemma_frequency"), A is "in every elementary
    Latin book", B "top 10 percent", C "top 10,000 words", D "top 20,000",
    E "2 or 3 citations", F "one citation". For a form (a row's
    "form_frequency"), A is "the most common", B "a not unusual variant",
    C "occasionally seen", D "unlikely", E "rare", F "very rare".
    """

    UNKNOWN = "X"
    MOST_COMMON = "A"
    FREQUENT = "B"
    COMMON = "C"
    LESSER = "D"
    UNCOMMON = "E"
    VERY_RARE = "F"
    INSCRIPTION_ONLY = "I"
    GRAFFITI = "M"
    PLINY_ONLY = "N"  # almost only in Pliny's Natural History

    @property
    def rank(self) -> int:
        """0 for the most common, rising as words get rarer; unknown last."""
        order = list(Frequency)
        return len(order) if self is Frequency.UNKNOWN else order.index(self)


class Age(_Code):
    """Age_Type: when a form was in use (a row's "form_age")."""

    ANY = "X"  # in use throughout the ages, or unknown
    ARCHAIC = "A"  # very early, obsolete by classical times
    EARLY = "B"  # pre-classical; used for effect and in poetry
    CLASSICAL = "C"  # about 150 BC to 200 AD
    LATE = "D"  # post-classical, 3rd to 5th centuries
    LATER = "E"  # 6th to 10th centuries, Christian
    MEDIEVAL = "F"  # 11th to 15th centuries
    SCHOLAR = "G"  # scholarly and scientific, 16th to 18th centuries
    MODERN = "H"  # coined recently, for new things
