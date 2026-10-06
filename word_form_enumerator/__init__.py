"""Every inflected Latin form in Whitaker's Words.

- write_forms / iter_forms: the flat list of every form (all_forms.py).
- get_latin_forms: every form of one vocab-list word, tagged (lookup.py).
- PartOfSpeech, Frequency, Age: Whitaker's codes as enums (codes.py).

See README.md for usage and docs/data.md for how the data files relate.
"""

from .all_forms import iter_forms, write_forms
from .codes import Age, Frequency, PartOfSpeech
from .lookup import get_latin_forms
from .paths import WHITAKER_DIR

__all__ = [
    "WHITAKER_DIR",
    "Age",
    "Frequency",
    "PartOfSpeech",
    "get_latin_forms",
    "iter_forms",
    "write_forms",
]
