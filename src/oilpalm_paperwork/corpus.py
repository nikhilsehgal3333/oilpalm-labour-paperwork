"""Collect the corpus, record a lock file, and extract the text page by page.

The documents belong to their owners. This repository does not contain them. It stores the address,
the SHA-256 value, the size and the page count of each file in `data/corpus_lock.csv`. Files that a
server refuses to scripts (column `manual` = yes) can be saved by hand from a browser as
`local/corpus/<id>.pdf`; the pipeline then treats them like any other file.
"""
from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import re
from datetime import date
from pathlib import Path

from pypdf import PdfReader

from .net import get
from .paths import CORPUS_CSV, CORPUS_DIR, LOCK_CSV, PAGES_DIR

PIB_START = "innner-page-main-about-us-content-right-part"
PIB_END = "ReleaseLang"
LOCK_FIELDS = ["id", "file", "sha256", "bytes", "pages", "retrieved", "status"]


def load_corpus(path: Path = CORPUS_CSV) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stored_file(doc_id: str, folder: Path = CORPUS_DIR) -> Path | None:
    for ext in (".pdf", ".html"):
        path = folder / f"{doc_id}{ext}"
        if path.exists():
            return path
    return None


def html_to_text(raw: str) -> str:
    """Text of an HTML page. For PIB pages keep only the body of the release."""
    # match the class attribute, not the same name inside a CSS rule
    start = re.search(r'class="[^"]*' + PIB_START, raw)
    if start:
        end = re.search(r'class="[^"]*' + PIB_END, raw[start.start():])
        raw = raw[start.start():start.start() + end.start() if end else None]
        raw = raw[raw.find(">") + 1:]  # drop the rest of the opening tag
    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</tr>", "\n", raw)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw)).replace("�", "-")  # server-side lost dash
    lines = [re.sub(r"[ \t ]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def pages_of(path: Path) -> list[str]:
    """One string per page. An HTML document is one page."""
    data = path.read_bytes()
    if data.startswith(b"%PDF"):
        reader = PdfReader(io.BytesIO(data))
        return [(page.extract_text() or "") for page in reader.pages]
    try:
        raw = data.decode("utf-8")
    except UnicodeDecodeError:  # PIB serves some pages in Windows-1252
        raw = data.decode("cp1252", errors="replace")
    return [html_to_text(raw)]


def fetch(rows: list[dict] | None = None, folder: Path = CORPUS_DIR) -> list[dict]:
    """Download what is missing. Return one status row per document."""
    folder.mkdir(parents=True, exist_ok=True)
    status = []
    for row in rows if rows is not None else load_corpus():
        if stored_file(row["id"], folder):
            status.append({"id": row["id"], "status": "present"})
            continue
        try:
            body, _ = get(row["url"])
            ext = ".pdf" if body.startswith(b"%PDF") else ".html"
            (folder / f"{row['id']}{ext}").write_bytes(body)
            status.append({"id": row["id"], "status": "downloaded"})
        except Exception as error:  # one refusing server must not stop the rest
            hint = " (save it by hand from a browser)" if row.get("manual") == "yes" else ""
            status.append({"id": row["id"], "status": f"failed: {type(error).__name__}{hint}"})
    return status


def write_lock(rows: list[dict] | None = None, folder: Path = CORPUS_DIR, lock: Path = LOCK_CSV) -> None:
    """Record hash, size and pages of every file present. Keep old dates for unchanged files."""
    old = {}
    if lock.exists():
        with open(lock, encoding="utf-8", newline="") as handle:
            old = {r["id"]: r for r in csv.DictReader(handle)}
    out = []
    for row in rows if rows is not None else load_corpus():
        path = stored_file(row["id"], folder)
        if path is None:
            out.append({"id": row["id"], "file": "", "sha256": "", "bytes": "", "pages": "",
                        "retrieved": "", "status": "missing"})
            continue
        data = path.read_bytes()
        digest = sha256(data)
        same = old.get(row["id"], {}).get("sha256") == digest
        out.append({"id": row["id"], "file": path.name, "sha256": digest, "bytes": len(data),
                    "pages": len(pages_of(path)),
                    "retrieved": old[row["id"]]["retrieved"] if same else date.today().isoformat(),
                    "status": "ok"})
    lock.parent.mkdir(parents=True, exist_ok=True)
    with open(lock, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOCK_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out)


def verify(folder: Path = CORPUS_DIR, lock: Path = LOCK_CSV) -> list[str]:
    """Return the ids whose file no longer matches the lock. An empty list means all match."""
    with open(lock, encoding="utf-8", newline="") as handle:
        rows = [r for r in csv.DictReader(handle) if r["status"] == "ok"]
    bad = []
    for row in rows:
        path = folder / row["file"]
        if not path.exists() or sha256(path.read_bytes()) != row["sha256"]:
            bad.append(row["id"])
    return bad


def extract_pages(rows: list[dict] | None = None, folder: Path = CORPUS_DIR,
                  out: Path = PAGES_DIR) -> dict[str, int]:
    """Write local/pages/<id>.pages.json for every file present. Return pages per document."""
    out.mkdir(parents=True, exist_ok=True)
    counts = {}
    for row in rows if rows is not None else load_corpus():
        path = stored_file(row["id"], folder)
        if path is None:
            continue
        pages = pages_of(path)
        (out / f"{row['id']}.pages.json").write_text(json.dumps(pages, ensure_ascii=False),
                                                       encoding="utf-8")
        counts[row["id"]] = len(pages)
    return counts
