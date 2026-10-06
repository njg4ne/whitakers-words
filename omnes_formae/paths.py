"""Where the data files are."""

from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
WHITAKER_DIR = DATA_DIR / "whitaker"  # copied unchanged from Whitaker's Words
BESPOKE_DIR = DATA_DIR / "bespoke"  # written for this project
