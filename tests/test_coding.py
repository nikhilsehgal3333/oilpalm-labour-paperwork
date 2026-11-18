"""The presence matrix rebuilds from a gold sheet, with the author's check overriding the assistant."""
from oilpalm_paperwork import coding


def row(nr, code, page, agent, yours="", also=""):
    return {"nr": str(nr), "doc": "d", "pdf_page": page, "code": code, "passage": "word " * 40,
            "proposed_level": "", "agent_level": agent, "agent_also": also,
            "YOUR_level": yours, "YOUR_note": ""}


GOLD = [
    row(1, "L2", "3", "generic"),
    row(2, "L2", "7", "explicit_palm", yours="generic"),   # author downgrades
    row(3, "L4", "9", "not_relevant", also="L6"),
    row(4, "E1", "4", "generic", also="L1"),
    {"nr": "5", "doc": "d", "pdf_page": "", "code": "S1", "passage": "", "proposed_level": "absent",
     "agent_level": "absent", "agent_also": "", "YOUR_level": "", "YOUR_note": ""},
]


def test_author_overrides_and_also_codes():
    table = {r["code"]: r for r in coding.presence(GOLD, ["d"], ["L1", "L2", "L4", "L6", "E1", "S1"])}
    assert table["L2"]["level"] == "generic" and table["L2"]["all_checked_by_author"] == "no"
    assert table["L1"]["level"] == "generic" and table["L1"]["pdf_pages"] == "4"   # via 'also'
    assert table["L4"]["level"] == "absent" and table["L6"]["level"] == "absent"   # not_relevant
    assert table["S1"]["level"] == "absent" and table["S1"]["all_checked_by_author"] == "n/a"


def test_excerpt_is_short():
    passages = coding.coded_passages(GOLD)
    assert all(len(p["excerpt"].split()) <= coding.EXCERPT_WORDS + 1 for p in passages)
    assert passages[2]["excerpt"] == ""          # not_relevant rows publish no text
