"""First-pass review of the rule proposals (18 Nov 2026), written into the
local gold sheet. The author checks every row afterwards (columns YOUR_level, YOUR_note).
Passage levels: explicit_palm, generic, not_relevant. A cell with no relevant passage is absent."""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "local" / "gold_sheet.csv"
R = {  # nr: (agent_level, agent_also, agent_note)
 1: ("absent", "", "only 'employment generation' in general; no category of worker"),
 3: ("explicit_palm", "", "headline repeats the price assurance of row 2"),
 8: ("not_relevant", "", "'Union Cabinet', not a trade union"),
 12: ("generic", "L5", "human rights assessment 'across factories' incl. contract workers, women, migrants; not plantations"),
 20: ("not_relevant", "L6", "supervisors in a whistle-blower clause, not labour control"),
 28: ("not_relevant", "", "trade and industry chambers, not workers' voice"),
 30: ("explicit_palm", "L1", "smallholder growers with small and marginal holdings in allocated districts"),
 32: ("not_relevant", "", "BRSR template list of standards (FSC named as an example)"),
 34: ("explicit_palm", "L1", "smallholder farmers named; irrigation practice"),
 37: ("not_relevant", "", "traceability refers to dairy; palm part is drone monitoring"),
 38: ("explicit_palm", "L1;E1", "FFB from farmers in Government-allocated districts, over 90% of input costs"),
 40: ("generic", "", "location wage table; no palm content"),
 42: ("generic", "", "same location wage table"),
 45: ("not_relevant", "", "third-party product certification"),
 46: ("not_relevant", "L4;L6", "hazard reporting to supervisors"),
 47: ("not_relevant", "L4", "supervision of safety practice"),
 50: ("generic", "S1", "OHSAS 45001 among certifications of manufacturing units"),
 53: ("not_relevant", "", "consumer nutrition"),
 57: ("not_relevant", "", "BRSR template list of standards"),
 58: ("not_relevant", "", "template question on sensitive areas; no answer in the passage"),
 63: ("explicit_palm", "", "names a new oil palm mill at Niglok, Arunachal Pradesh"),
 69: ("not_relevant", "", "table of contents"),
 71: ("explicit_palm", "L2", "intermediaries; growers paid as little as Rs 5 per kg against Rs 9.80"),
 72: ("not_relevant", "", "organisation chart of the mission"),
 73: ("explicit_palm", "L2", "trading company and local intermediaries in Goalpara, Assam; payment modes"),
 74: ("explicit_palm", "E2", "pesticide knowledge and unregulated use among growers"),
 76: ("not_relevant", "", "processors' associations as implementers"),
 78: ("explicit_palm", "L2", "growers not reimbursed for transport; FPOs and associations help"),
}
EXTRA = [  # rows the top-3 selection missed
 {"doc": "patanjali_brsr_fy25", "pdf_page": "22", "code": "L3", "palm_context": "no",
  "passage": "(see candidates.jsonl, p. 22: human rights policy extends to vendors and contractors)",
  "proposed_level": "", "agent_level": "generic", "agent_also": "L6",
  "agent_note": "added: human rights policy covers contractors; freedom of association named"},
]
rows = list(csv.DictReader(open(GOLD, encoding="utf-8-sig"), delimiter=";"))
fields = ["nr", "doc", "pdf_page", "code", "palm_context", "passage", "proposed_level",
          "agent_level", "agent_also", "agent_note", "YOUR_level", "YOUR_note"]
for r in rows:
    lvl, also, note = R.get(int(r["nr"]), (r["proposed_level"], "", ""))
    r.update({"agent_level": lvl, "agent_also": also, "agent_note": note})
for e in EXTRA:
    e.update({"nr": len(rows) + 1, "YOUR_level": "", "YOUR_note": ""}); rows.append(e)
with open(GOLD, "w", encoding="utf-8-sig", newline="") as h:
    w = csv.DictWriter(h, fieldnames=fields, delimiter=";", lineterminator="\n"); w.writeheader(); w.writerows(rows)
from collections import Counter
print(len(rows), Counter(r["agent_level"] for r in rows))
