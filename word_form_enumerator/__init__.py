"""Every inflected Latin form in Whitaker's Words.

- write_forms / iter_forms: the flat list of every form (all_forms.py).

See README.md for usage and docs/data.md for how the data files relate.
"""

from .all_forms import iter_forms, write_forms
from .paths import WHITAKER_DIR

__all__ = ["WHITAKER_DIR", "iter_forms", "write_forms"]
