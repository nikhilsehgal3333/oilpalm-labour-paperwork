"""Folders of the repository. `local/` holds the documents of other owners and is not published."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
LOCAL = ROOT / "local"
CORPUS_DIR = LOCAL / "corpus"
PAGES_DIR = LOCAL / "pages"
CORPUS_CSV = DATA / "corpus.csv"
LOCK_CSV = DATA / "corpus_lock.csv"
CODEBOOK = ROOT / "codebook.yaml"
