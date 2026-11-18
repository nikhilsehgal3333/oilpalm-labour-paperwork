"""Turn the gold sheet into the presence matrix and the list of coded passages.

Order of authority for each passage: the author's check (YOUR_level) overrides the assistant's first
review (agent_level), which overrides the keyword rule (proposed_level). A passage also counts for
the codes in its `also` column. The level of a document and code is the strongest relevant level:
explicit_palm > generic > absent.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .paths import LOCAL, RESULTS

RANK = {"explicit_palm": 2, "generic": 1}
EXCERPT_WORDS = 30


def read_gold(path: Path = LOCAL / "gold_sheet.csv") -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def final_level(row: dict) -> tuple[str, bool]:
    """(level, checked_by_author)."""
    if row.get("YOUR_level", "").strip():
        return row["YOUR_level"].strip(), True
    return (row.get("agent_level") or row.get("proposed_level") or "").strip(), False


def excerpt(text: str, words: int = EXCERPT_WORDS) -> str:
    parts = text.split()
    return " ".join(parts[:words]) + (" ..." if len(parts) > words else "")


def coded_passages(gold: list[dict]) -> list[dict]:
    out = []
    for row in gold:
        level, checked = final_level(row)
        if not row.get("pdf_page"):
            continue  # an 'absent' placeholder row carries no passage
        out.append({"nr": row["nr"], "doc": row["doc"], "pdf_page": row["pdf_page"], "code": row["code"],
                    "also": row.get("agent_also", ""), "level": level,
                    "checked_by_author": "yes" if checked else "no",
                    "excerpt": excerpt(row["passage"]) if level in RANK else ""})
    return out


def presence(gold: list[dict], docs: list[str], codes: list[str]) -> list[dict]:
    passages = coded_passages(gold)
    table = []
    for doc in docs:
        for code in codes:
            best, pages, checked, evidence = 0, [], [], []
            for p in passages:
                if p["doc"] != doc or p["level"] not in RANK:
                    continue
                if p["code"] != code and code not in p["also"].split(";"):
                    continue
                best = max(best, RANK[p["level"]])
                pages.append(int(p["pdf_page"]))
                checked.append(p["checked_by_author"] == "yes")
                evidence.append(p)
            level = {2: "explicit_palm", 1: "generic", 0: "absent"}[best]
            deciding = [p for p in evidence if RANK[p["level"]] == best]
            table.append({"doc": doc, "code": code, "level": level,
                          "pdf_pages": ";".join(str(n) for n in sorted(set(pages))),
                          "deciding_rows": ";".join(p["nr"] for p in deciding),
                          "deciding_checked_by_author":
                              "n/a" if not deciding else
                              ("yes" if any(p["checked_by_author"] == "yes" for p in deciding) else "no"),
                          "all_checked_by_author": "yes" if checked and all(checked) else
                                                   ("n/a" if not checked else "no")})
    return table


def write(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def coding_log(gold: list[dict]) -> list[dict]:
    """The decision trail for every row, without the document text: keyword rule, first review,
    author's check, and the level that counts."""
    out = []
    for row in gold:
        level, checked = final_level(row)
        out.append({"nr": row["nr"], "doc": row["doc"], "pdf_page": row["pdf_page"], "code": row["code"],
                    "keyword_rule": row.get("proposed_level", ""),
                    "first_review": row.get("agent_level", ""), "first_review_note": row.get("agent_note", ""),
                    "also_codes": row.get("agent_also", ""),
                    "author_check": row.get("YOUR_level", ""), "author_note": row.get("YOUR_note", ""),
                    "final_level": level, "checked_by_author": "yes" if checked else "no"})
    return out


def run(docs: list[str], codes: list[str]) -> list[dict]:
    gold = read_gold()
    write(coded_passages(gold), RESULTS / "coded_passages.csv")
    write(coding_log(gold), RESULTS / "coding_log.csv")
    table = presence(gold, docs, codes)
    write(table, RESULTS / "presence_matrix.csv")
    return table
