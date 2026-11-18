"""Parts of the methodology page: the clickable process diagram and the detail panel of each step.
Every count is passed in from the result files by site/build.py."""
import html

REPO = "https://github.com/nikhilsehgal3333/oilpalm-labour-paperwork"


def _esc(text) -> str:
    return html.escape(str(text))


def svg_diagram(m: dict, rows: int, coded: int, obtained: int) -> str:
    """Clickable flow diagram. Each box links to the detail panel of its step."""
    def box(x, y, w, h, href, title, sub, cls="node"):
        sub_text = f'<text x="{x + w / 2}" y="{y + 46}" class="t2">{_esc(sub)}</text>' if sub else ""
        ty = y + 26 if sub else y + h / 2 + 5
        return (f'<a href="#{href}" class="{cls}" aria-label="{_esc(title)}: open the details">'
                f'<title>{_esc(title)}: open the details</title>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
                f'<text x="{x + w / 2}" y="{ty}" class="t1">{_esc(title)}</text>{sub_text}</a>')

    def arrow(x1, y1, x2, y2):
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge" marker-end="url(#arr)"/>'

    return "".join([
        '<div class="diagram-wrap"><svg class="flow" viewBox="0 0 1040 410" role="group" '
        'aria-label="Process diagram of the study. Each box links to its step.">',
        '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="arrowhead"/></marker></defs>',
        '<text x="20" y="24" class="lane">INPUTS</text>',
        '<text x="20" y="342" class="lane">RECORD</text>',
        box(20, 36, 150, 62, "step-1", "Fingerprints", "SHA-256 lock file"),
        box(360, 36, 170, 62, "step-2", "2 Codebook", "10 codes, 3 levels"),
        box(20, 165, 150, 70, "step-1", "1 Documents", f"{obtained} public files"),
        box(200, 165, 140, 70, "step-1", "Page text", "page by page"),
        box(370, 165, 150, 70, "step-3", "3 Candidates", f"{m['candidates']} by keyword"),
        '<a href="#step-4" class="node group" aria-label="4 Coding: open the details">'
        '<title>4 Coding in three layers: open the details</title>'
        '<rect x="550" y="122" width="170" height="196" rx="12"/>'
        '<text x="635" y="146" class="t1">4 Coding</text>'
        f'<text x="635" y="164" class="t2">{rows} rows, {coded} passages</text></a>',
        box(565, 178, 140, 34, "step-4", "Keyword rule", "", "chip"),
        box(565, 222, 140, 34, "step-4", "First review", "", "chip"),
        box(565, 266, 140, 34, "step-5", "Author check", "", "chip"),
        box(750, 165, 130, 70, "step-5", "5 Matrix", f"{m['cells']} cells"),
        box(905, 112, 120, 54, "step-6", "6 Note", "NOTE.pdf"),
        box(905, 173, 120, 54, "step-6", "Figure", "heatmap"),
        box(905, 234, 120, 54, "step-6", "Site", "this page"),
        box(200, 356, 640, 40, "deviations", "Every change to the plan is logged with its date and reason",
            "", "chip wide"),
        arrow(95, 98, 95, 162), arrow(170, 200, 197, 200), arrow(340, 200, 367, 200),
        arrow(520, 200, 547, 200), arrow(720, 200, 747, 200),
        arrow(445, 98, 445, 162), arrow(530, 67, 632, 67),
        '<line x1="635" y1="67" x2="635" y2="119" class="edge" marker-end="url(#arr)"/>',
        arrow(635, 212, 635, 219), arrow(635, 256, 635, 263),
        arrow(880, 190, 902, 142), arrow(880, 200, 902, 200), arrow(880, 210, 902, 258),
        '</svg></div>',
        '<p class="meta">Click a box to open the details of that step. On a narrow screen the diagram '
        'scrolls sideways.</p>',
    ])


def detail_panels(m, log, passages, relevant, not_relevant, changed_by_review, added_by_review,
                  checked, changed_by_author, rounds, gl1b, obtained, listed) -> str:
    gh = f"{REPO}/blob/main"

    def panel(pid, title, goes_in, happens, comes_out, numbers, example, files):
        links = " · ".join(f'<a href="{gh}/{f}"><code>{_esc(f)}</code></a>' for f in files)
        return (f'<details id="{pid}" class="step"><summary><span class="num">{pid[-1]}</span>{title}</summary>'
                '<div class="panel">'
                f'<p><b>What goes in.</b> {goes_in}</p><p><b>What happens.</b> {happens}</p>'
                f'<p><b>What comes out.</b> {comes_out}</p><p><b>In numbers.</b> {numbers}</p>'
                f'<p class="example"><b>Example from this study.</b> {example}</p>'
                f'<p class="meta">Files: {links}</p></div></details>')

    return "".join([
        panel("step-1", "Collect and fingerprint the documents",
              "A list of public documents, each with its owner, type, period and web address.",
              "Each file is downloaded, or saved by hand from a browser where a government server refuses "
              "scripted downloads. Its SHA-256 fingerprint, size and page count go into a lock file, and the "
              "text is extracted page by page. A later run stops if any file no longer matches its "
              "fingerprint.",
              "The page text of each document, kept locally, and the lock file, which is published. The "
              "documents themselves stay with their owners.",
              f"{obtained} of {listed} listed documents obtained. The oil palm mission's operational "
              "guidelines could not be downloaded and are named as a limit.",
              "The Lok Sabha answer and the oilseeds-mission guidelines were refused to scripts from outside "
              "India. The author saved them by hand, and their fingerprints were recorded like every other "
              "file.",
              ["data/corpus.csv", "data/corpus_lock.csv", "src/oilpalm_paperwork/corpus.py"]),
        panel("step-2", "Fix the codebook before coding",
              "The four literatures named in the PALMWORK project: labour regime analysis, feminist labour "
              "geography, environmental labour studies and political ecology.",
              "Ten codes are defined, each with a description and a keyword list, and three levels per "
              "document and code: explicit for oil palm, generic (company-wide or scheme-wide), absent. "
              "The codebook was refined on two documents before any coding and changed once afterwards, "
              "with the reason logged.",
              "<code>codebook.yaml</code>, version 2.",
              "Ten codes: growers, hired workers, pay and price, recruitment and control, health and safety, "
              "social reproduction, voice, land and tenure, environment of work, standards.",
              "After the first round, the author split \"who works\" into growers and hired workers, because "
              "labour regime analysis separates growers on their own land from wage workers. Earlier "
              "reviews were carried over by matching passages.",
              ["codebook.yaml", "DEVIATIONS.md"]),
        panel("step-3", "Find candidate passages",
              "The page text of every document and the keyword lists of the codebook.",
              "For each code, a keyword search marks a window of text around every match and merges "
              "overlapping windows. Each candidate is flagged when it sits near an oil palm or North-East "
              "word (palm, mill, fresh fruit bunch, Assam, Mizoram and others). Keywords only find "
              "candidates; they decide nothing.",
              "A count of candidates per document and code (published) and the candidate passages (kept "
              "locally, because they are the owners' text).",
              f"{m['candidates']} candidate passages across {m['documents']} documents and {m['codes']} codes.",
              f"In the Godrej Agrovet BRSR the code for hired workers has {gl1b['candidates']} candidates, and "
              f"{gl1b['near_palm_word']} of them sit near an oil palm or North-East word: an early sign of "
              "the main finding.",
              ["results/candidate_counts.csv", "src/oilpalm_paperwork/kwic.py"]),
        panel("step-4", "Code the passages in three layers",
              "The strongest candidates for each document and code, plus one row for every empty cell.",
              "A keyword rule proposes a level (explicit when the passage is near an oil palm word, otherwise "
              "generic). A first review reads every passage and corrects the proposal, marks passages that "
              "match a keyword in another sense as not relevant, and notes when a passage also counts for a "
              "second code. The author then checks the levels.",
              "A coding log with all three layers for every row, and short excerpts with page numbers.",
              f"{len(log)} rows; {len(passages)} passages coded; {len(changed_by_review)} rule proposals "
              f"changed by the first review; {len(not_relevant)} passages not relevant; "
              f"{len(added_by_review)} passage added by hand; {len(relevant)} passages speak to their code.",
              "\"Union Cabinet\" matched the keyword for unions and was marked not relevant. The passage on "
              "intermediaries in Goalpara, Assam, where growers \"reported receiving as less as Rs 5 per "
              "kg\", was proposed as generic by the rule and corrected to explicit for oil palm.",
              ["results/coding_log.csv", "results/coded_passages.csv", "src/oilpalm_paperwork/coding.py"]),
        panel("step-5", "Check what decides each result",
              "The coded passages and the author's checks.",
              "Each cell of the result (one document and one code) takes the level of its strongest relevant "
              "passage, the deciding passage. The author checked the deciding passage of every non-empty "
              "cell, in two rounds.",
              "The presence matrix: one level per document and code, with the pages and rows that decide it.",
              f"{m['cells']} cells: {m['cells_explicit_palm']} explicit, {m['cells_generic']} generic, "
              f"{m['cells_absent']} absent. {len(checked)} rows checked ({rounds.get('CP1', 0)} at the first "
              f"checkpoint, {rounds.get('S3', 0)} at the second); {m['deciding_checked']} of "
              f"{m['deciding_total']} deciding passages checked; {len(changed_by_author)} levels changed by "
              "the author.",
              "The Godrej Agrovet cell for standards is explicit, decided by the passage on PDF page 18 that "
              "reports the company's verification under the Indian Palm Oil Sustainability Framework.",
              ["results/presence_matrix.csv"]),
        panel("step-6", "Report from the files, not by hand",
              "The presence matrix, the coded passages and the candidate counts.",
              "A script writes the heatmap, a numbers file and the results block of the README and the note; "
              "the note's prose cites documents by page. Tests check that every number in the results block "
              "comes from the numbers file, that the published text is clean, and that a second run gives "
              "byte-identical results.",
              "The figure, the numbers file, the note (Markdown and PDF) and this site.",
              f"In both BRSRs, {m['brsr_labour_cells_generic']} of {m['brsr_labour_cells']} hired-labour "
              f"cells are generic. Growers appear in an oil palm context in {m['L1a_explicit_docs']} of "
              f"{m['documents']} documents, hired workers in {m['L1b_explicit_docs']}.",
              "The results block of the note and of the README is identical, and a test fails if either is "
              "edited by hand.",
              ["results/manifest.json", "src/oilpalm_paperwork/report.py", "NOTE.md",
               "tests/test_integrity.py"]),
    ])


DIAGRAM_CSS = """
.diagram-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; padding: 8px; }
svg.flow { min-width: 760px; width: 100%; height: auto; display: block; }
svg.flow .lane { font: 600 13px system-ui, sans-serif; fill: var(--muted); letter-spacing: .08em; }
svg.flow .node rect, svg.flow .chip rect { fill: var(--bg); stroke: var(--accent); stroke-width: 1.6; }
svg.flow .group rect { stroke-dasharray: 4 3; }
svg.flow .chip rect { stroke-width: 1.2; }
svg.flow .chip.wide rect { stroke-dasharray: 5 4; }
svg.flow a:hover rect, svg.flow a:focus rect { fill: var(--hover); stroke-width: 2.4; }
svg.flow a { cursor: pointer; outline: none; }
svg.flow .t1 { font: 700 17px system-ui, sans-serif; fill: var(--fg); text-anchor: middle; }
svg.flow .chip .t1 { font-size: 15px; }
svg.flow .t2 { font: 14px system-ui, sans-serif; fill: var(--muted); text-anchor: middle; }
svg.flow .edge { stroke: var(--muted); stroke-width: 1.5; fill: none; }
svg.flow .arrowhead { fill: var(--muted); }
:root { --hover: #dbe8f6; }
@media (prefers-color-scheme: dark) { :root { --hover: #1d3550; } }
details.step { border: 1px solid var(--line); border-radius: 8px; margin: .7rem 0; scroll-margin-top: 12px; }
details.step[open] { border-color: var(--accent); }
details.step summary { cursor: pointer; padding: .7rem 1rem; font-weight: 700; }
details.step .num { display: inline-block; width: 1.6rem; height: 1.6rem; border-radius: 50%;
  background: var(--accent); color: var(--bg); text-align: center; font: 600 13px/1.6rem system-ui, sans-serif;
  margin-right: .5rem; }
details.step .panel { padding: 0 1rem .6rem; }
.example { border-left: 3px solid var(--accent); padding-left: .7rem; }
h2:target { color: var(--accent); }
"""

OPEN_SCRIPT = """<script>
(function () {
  function openTarget() {
    var el = document.getElementById(location.hash.slice(1));
    if (el && el.tagName === 'DETAILS') { el.open = true; el.scrollIntoView({block: 'start'}); }
  }
  window.addEventListener('hashchange', openTarget);
  openTarget();
})();
</script>"""
