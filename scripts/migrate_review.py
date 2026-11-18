"""Carry the assistant's v1 review (codebook v1) into the v2 gold sheet (L1 split into L1a growers
and L1b hired workers). Matching: same document, page and code (v1 L1 mapped per row), and the same
passage (one contains the start of the other, or most words shared). Rows without a match are
listed for a fresh review. The v1 sheet stays in local/gold_sheet_v1.csv.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1, V2 = ROOT / "local" / "gold_sheet_v1.csv", ROOT / "local" / "gold_sheet.csv"
L1_MAP = {"12": "L1b", "13": "L1b", "14": "L1b", "39": "L1b", "40": "L1b", "41": "L1b",
          "65": "L1b", "66": "L1b", "67": "L1a"}   # v1 nr 1 (PIB L1 absent) is re-reviewed under v2
FIELDS = ["nr", "doc", "pdf_page", "code", "palm_context", "passage", "proposed_level",
          "agent_level", "agent_also", "agent_note", "YOUR_level", "YOUR_note"]


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def same(a: str, b: str) -> bool:
    if not a or not b:
        return False
    if a[:60] in b or b[:60] in a:
        return True
    wa, wb = set(a.lower().split()), set(b.lower().split())
    return len(wa & wb) / max(1, min(len(wa), len(wb))) > 0.7


def main() -> None:
    v1, v2 = read(V1), read(V2)
    for r in v1:
        if r["code"] == "L1":
            r["code"] = L1_MAP.get(r["nr"], "")
        r["agent_also"] = ";".join("L1a" if c == "L1" else c for c in r["agent_also"].split(";") if c)
    used, unmatched = set(), []
    for r in v2:
        for k, old in enumerate(v1):
            if k in used or old["code"] != r["code"] or old["doc"] != r["doc"]:
                continue
            if (not r["pdf_page"] and not old["pdf_page"]) or (
                    r["pdf_page"] == old["pdf_page"] and same(r["passage"], old["passage"])):
                r.update({f: old[f] for f in ("agent_level", "agent_also", "agent_note")})
                used.add(k)
                break
        else:
            r.update({"agent_level": "", "agent_also": "", "agent_note": ""})
            unmatched.append(r)
    for k, old in enumerate(v1):  # rows added by hand in v1 that the selection does not produce
        if k not in used and old["agent_note"].startswith("added:"):
            row = {f: old.get(f, "") for f in FIELDS}
            row["nr"] = str(len(v2) + 1)
            v2.append(row)
    for r in v2:
        r.setdefault("YOUR_level", "")
        r.setdefault("YOUR_note", "")
    with open(V2, "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter=";", lineterminator="\n",
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(v2)
    print(f"v2 rows {len(v2)}; carried over {len(used)}; to review {len(unmatched)}")
    for r in unmatched:
        print(r["nr"], r["doc"], r["pdf_page"], r["code"], r["proposed_level"])


if __name__ == "__main__":
    main()
