"""Keyword-in-context retrieval and the gold-sheet proposal rule, on synthetic pages."""
import re

from oilpalm_paperwork import kwic

BOOK = {
    "palm_re": re.compile(r"\b(oil palm|plantation|mizoram)\b", re.I),
    "codes": {
        "L2": {"res": [re.compile(r"\bwages?\b", re.I)]},
        "L6": {"res": [re.compile(r"\bunions?\b", re.I)]},
    },
}


def test_planted_keyword_is_found_with_palm_context():
    page = "Intro text. Harvesters on the oil palm plantation in Mizoram receive daily wages in cash. End."
    found = kwic.windows(page, BOOK["codes"]["L2"]["res"], width=40)
    assert len(found) == 1 and "daily wages" in found[0]["text"]
    assert BOOK["palm_re"].search(found[0]["text"])


def test_overlapping_windows_merge():
    page = "wage and wages and wage again"
    assert len(kwic.windows(page, BOOK["codes"]["L2"]["res"], width=10)) == 1


def test_proposal_rule_and_absent_cell():
    rows = [
        {"doc": "d", "pdf_page": 2, "code": "L2", "palm": True, "text": "palm wages", "score": 4},
        {"doc": "d", "pdf_page": 5, "code": "L2", "palm": False, "text": "company wages", "score": 1},
    ]
    gold = kwic.gold_rows(rows, ["d"], ["L2", "L6"])
    levels = [(g["code"], g["proposed_level"]) for g in gold]
    assert levels == [("L2", "explicit_palm"), ("L2", "generic"), ("L6", "absent")]
    assert [g["nr"] for g in gold] == [1, 2, 3]
