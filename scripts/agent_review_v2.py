"""First-pass review of the rows new in gold sheet v2 (codebook v2 and the two added documents),
18 Nov 2026. Rows carried over from v1 are left as they are. The author checks every row afterwards."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "local" / "gold_sheet.csv"
NE_OS = "North-East mention concerns oilseed clusters, not oil palm"
R = {  # nr: (agent_level, agent_also, agent_note)
 1: ("generic", "", "FPOs and cooperatives as value chain partners of oilseed clusters"),
 2: ("generic", "", "clusters of at least 200 farmers (100 in North-eastern and hilly states); " + NE_OS),
 3: ("generic", "", "farmer training and field schools"),
 4: ("generic", "", "women community workers (Krishi Sakhi, SHGs) for scheme data collection; not farm labour"),
 5: ("generic", "", "Krishi Sakhis (women community leaders) collect and update data"),
 6: ("generic", "", "farmer incomes as a mission aim"),
 7: ("not_relevant", "", "supervision of seed variety testing"),
 8: ("not_relevant", "", "demonstrations under ICAR supervision"),
 9: ("not_relevant", "", "field schools under supervision of support agencies"),
 10: ("not_relevant", "", "fertiliser dose; agronomy, not safety"),
 11: ("not_relevant", "", "pest management kit budget; no worker safety"),
 12: ("not_relevant", "", "farmer field school, not schooling"),
 13: ("not_relevant", "", "table of contents"),
 14: ("not_relevant", "", "farmer field schools"),
 15: ("not_relevant", "", "'Union Minister', governance structure"),
 16: ("not_relevant", "", "information campaign with agencies"),
 17: ("not_relevant", "", "industry associations as eligible corporations"),
 18: ("generic", "", "tree-borne oilseeds sourced from forests; not oil palm"),
 19: ("generic", "", "plantation of tree-borne oilseeds on wasteland and degraded forest land"),
 20: ("not_relevant", "", "table of contents"),
 21: ("generic", "", "convergence with micro-irrigation"),
 22: ("generic", "", "coordination with irrigation departments"),
 23: ("not_relevant", "", "performance audits of value chain partners, not sustainability"),
 24: ("not_relevant", "", "seed certification"),
 25: ("not_relevant", "", "seed quality certification"),
 26: ("explicit_palm", "", "headline: price assurance to oil palm farmers"),
 27: ("explicit_palm", "L2", "oil palm farmers produce FFBs; price linked to international CPO prices"),
 28: ("explicit_palm", "", "repeats the headline"),
 40: ("not_relevant", "", "agarwood growers"),
 41: ("explicit_palm", "", "cumulative oil palm area in the North-East (68,324 ha by 31 March 2025)"),
 42: ("explicit_palm", "", "mills in Arunachal Pradesh and Mizoram, new mill for Assam; 'benefit farmers'"),
 52: ("explicit_palm", "E2", "smallholder farmers; sustainable farm practices"),
 53: ("explicit_palm", "E1", "smallholders with small and marginal holdings in allocated districts"),
 54: ("generic", "", "farmers in general, company profile"),
 82: ("explicit_palm", "E2", "63,915 farmers through direct FFB procurement"),
 83: ("explicit_palm", "", "FFBs procured from 63,915 farmers; nurseries and godowns"),
 84: ("explicit_palm", "", "100% of growers' FFBs purchased"),
 111: ("explicit_palm", "L6", "grower associations in Assam"),
 112: ("not_relevant", "", "method of the study (interviews with stakeholders)"),
 113: ("explicit_palm", "L6", "no oil palm FPOs found in Andhra Pradesh; corporate involvement"),
 116: ("not_relevant", "L1a", "gender of growers (95% male), not of hired workers"),
}
rows = list(csv.DictReader(open(GOLD, encoding="utf-8-sig"), delimiter=";"))
done = 0
for r in rows:
    if int(r["nr"]) in R and not r["agent_level"]:
        r["agent_level"], r["agent_also"], r["agent_note"] = R[int(r["nr"])]
        done += 1
with open(GOLD, "w", encoding="utf-8-sig", newline="") as h:
    w = csv.DictWriter(h, fieldnames=list(rows[0]), delimiter=";", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
missing = [r["nr"] for r in rows if r["pdf_page"] and not r["agent_level"]]
print(f"reviewed {done}; rows with a passage still unreviewed: {missing}")
