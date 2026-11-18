"""Corpus handling: HTML release extraction, lock writing and hash verification (synthetic files)."""
from pathlib import Path

from oilpalm_paperwork import corpus

PIB_PAGE = """<html><head><script>var x = 1;</script>
<style>.innner-page-main-about-us-content-right-part ul > li { list-style: none; }</style></head><body>
<div class="menu">Home | Ministries</div>
<div class="innner-page-main-about-us-content-right-part">
<h2>Cabinet approves Mission</h2><p>The scheme focuses on the North East.</p>
<p>Farmers get a viability price.</p></div>
<div class="ReleaseLang">Read in Hindi</div></body></html>"""


def test_pib_release_body_only():
    text = corpus.html_to_text(PIB_PAGE)
    assert "North East" in text and "viability price" in text
    assert "Ministries" not in text and "Read in Hindi" not in text and "var x" not in text


def test_lock_and_verify(tmp_path: Path):
    folder, lock = tmp_path / "corpus", tmp_path / "lock.csv"
    folder.mkdir()
    (folder / "a.html").write_text(PIB_PAGE, encoding="utf-8")
    rows = [{"id": "a", "manual": "no"}, {"id": "b", "manual": "yes"}]
    corpus.write_lock(rows, folder, lock)
    text = lock.read_text(encoding="utf-8")
    assert "a,a.html," in text and "b,,,,,,missing" in text
    assert corpus.verify(folder, lock) == []
    (folder / "a.html").write_text(PIB_PAGE + " changed", encoding="utf-8")
    assert corpus.verify(folder, lock) == ["a"]


def test_pages_of_html_is_one_page(tmp_path: Path):
    path = tmp_path / "x.html"
    path.write_text(PIB_PAGE, encoding="utf-8")
    assert len(corpus.pages_of(path)) == 1
