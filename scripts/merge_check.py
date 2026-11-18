"""Copy the author's YOUR_level / YOUR_note from a check sheet (e.g. local/cp1_check.csv) into
local/gold_sheet.csv, matched on nr. Empty cells in the check sheet change nothing.

    uv run python scripts/merge_check.py local/cp1_check.csv
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "local" / "gold_sheet.csv"
VALID = {"explicit_palm", "generic", "not_relevant", "absent"}


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def main(check_path: str) -> None:
    check = {r["nr"]: r for r in read(check_path)}
    gold = read(GOLD)
    changed = 0
    for row in gold:
        c = check.get(row["nr"])
        if not c:
            continue
        level = c.get("YOUR_level", "").strip()
        if level and level not in VALID:
            raise SystemExit(f"row {row['nr']}: '{level}' is not one of {sorted(VALID)}")
        if level or c.get("YOUR_note", "").strip():
            row["YOUR_level"], row["YOUR_note"] = level, c.get("YOUR_note", "").strip()
            changed += 1
    with open(GOLD, "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(gold[0]), delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(gold)
    print(f"{changed} rows updated in {GOLD.name}")


if __name__ == "__main__":
    main(sys.argv[1])
