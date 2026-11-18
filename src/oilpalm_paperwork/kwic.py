"""Find candidate passages for each code (keyword in context) and prepare the gold sheet.

Keywords only find candidates. A person decides the level of each document and code by reading the
passages. Full passages stay in `local/` (text of the document owners). The repository publishes
counts, page references and, later, short excerpts.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import yaml

from .paths import CODEBOOK, LOCAL, PAGES_DIR, RESULTS

WIDTH = 220          # characters of context on each side of a keyword
PER_CELL = 3         # passages per document and code that go to the gold sheet
LEVELS = ("explicit_palm", "generic", "absent")
GOLD_FIELDS = ["nr", "doc", "pdf_page", "code", "palm_context", "passage", "proposed_level",
               "YOUR_level", "YOUR_note"]


def load_codebook(path: Path = CODEBOOK) -> dict:
    book = yaml.safe_load(path.read_text(encoding="utf-8"))
    book["palm_re"] = re.compile(book["palm_context"], re.I)
    for code in book["codes"].values():
        code["res"] = [re.compile(k, re.I) for k in code["keywords"]]
    return book


def squeeze(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def windows(text: str, patterns: list[re.Pattern], width: int = WIDTH) -> list[dict]:
    """Merged windows around every keyword match in one page. Each window lists its keywords."""
    hits = []
    for pattern in patterns:
        for m in pattern.finditer(text):
            hits.append((max(0, m.start() - width), min(len(text), m.end() + width), m.group(0).lower()))
    hits.sort()
    merged: list[dict] = []
    for start, end, word in hits:
        if merged and start <= merged[-1]["end"]:
            merged[-1]["end"] = max(merged[-1]["end"], end)
            merged[-1]["keywords"].add(word)
        else:
            merged.append({"start": start, "end": end, "keywords": {word}})
    for w in merged:
        w["text"] = squeeze(text[w["start"]:w["end"]])
    return merged


def candidates(book: dict, pages_dir: Path = PAGES_DIR) -> list[dict]:
    """All candidate passages: one row per document, page, code and merged window."""
    rows = []
    for path in sorted(pages_dir.glob("*.pages.json")):
        doc = path.name.removesuffix(".pages.json")
        pages = json.loads(path.read_text(encoding="utf-8"))
        for number, page in enumerate(pages, start=1):
            norm = squeeze(page)
            for code_id, code in book["codes"].items():
                for w in windows(norm, code["res"]):
                    palm = bool(book["palm_re"].search(w["text"]))
                    rows.append({"doc": doc, "pdf_page": number, "code": code_id, "palm": palm,
                                 "keywords": sorted(w["keywords"]), "text": w["text"],
                                 "score": len(w["keywords"]) + (3 if palm else 0)})
    return rows


def counts(rows: list[dict], docs: list[str], codes: list[str]) -> list[list]:
    """Candidates per document and code, and how many sit near a palm or North-East word."""
    table = [["doc", "code", "candidates", "near_palm_word"]]
    for doc in docs:
        for code in codes:
            cell = [r for r in rows if r["doc"] == doc and r["code"] == code]
            table.append([doc, code, len(cell), sum(r["palm"] for r in cell)])
    return table


def gold_rows(rows: list[dict], docs: list[str], codes: list[str], per_cell: int = PER_CELL) -> list[dict]:
    """The best few candidates per document and code, with a rule-based proposal to be checked.

    Proposal rule: explicit_palm when the passage sits near a palm or North-East word, otherwise
    generic; a cell with no candidate gets one row proposed as absent.
    """
    out = []
    for doc in docs:
        for code in codes:
            cell = sorted((r for r in rows if r["doc"] == doc and r["code"] == code),
                          key=lambda r: (-r["score"], r["pdf_page"], r["text"]))[:per_cell]
            if not cell:
                out.append({"doc": doc, "pdf_page": "", "code": code, "palm_context": "",
                            "passage": "", "proposed_level": "absent"})
            for r in cell:
                out.append({"doc": doc, "pdf_page": r["pdf_page"], "code": code,
                            "palm_context": "yes" if r["palm"] else "no", "passage": r["text"],
                            "proposed_level": "explicit_palm" if r["palm"] else "generic"})
    for i, row in enumerate(out, start=1):
        row.update({"nr": i, "YOUR_level": "", "YOUR_note": ""})
    return out


def write_csv(path: Path, header: list[str], rows: list, delimiter: str = ",", bom: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as handle:
        if rows and isinstance(rows[0], dict):
            writer = csv.DictWriter(handle, fieldnames=header, delimiter=delimiter, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        else:
            writer = csv.writer(handle, delimiter=delimiter, lineterminator="\n")
            writer.writerow(header)
            writer.writerows(rows)


def run(docs: list[str], gold_path: Path = LOCAL / "gold_sheet.csv") -> dict:
    """Write results/candidate_counts.csv, local/candidates.jsonl and (if absent) the gold sheet."""
    book = load_codebook()
    codes = list(book["codes"])
    rows = candidates(book)
    table = counts(rows, docs, codes)
    write_csv(RESULTS / "candidate_counts.csv", table[0], table[1:])
    LOCAL.mkdir(exist_ok=True)
    with open(LOCAL / "candidates.jsonl", "w", encoding="utf-8") as handle:
        for r in rows:
            handle.write(json.dumps(r, ensure_ascii=False) + "\n")
    if not gold_path.exists():  # never overwrite hand coding
        write_csv(gold_path, GOLD_FIELDS, gold_rows(rows, docs, codes), delimiter=";", bom=True)
    return {"candidates": len(rows), "gold_sheet": str(gold_path)}
