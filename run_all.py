"""Rebuild the study with one command.

    uv run python run_all.py            # fetch what is missing, then rebuild
    uv run python run_all.py --offline  # use only the files in local/corpus (verified against the lock)

Stages: corpus (fetch, lock, page text). Later stages (candidates, coding, report) are added as the
study is built.
"""
from __future__ import annotations

import sys
from pathlib import Path

from oilpalm_paperwork import coding, corpus, kwic, report


def main() -> None:
    offline = "--offline" in sys.argv
    if not offline:
        for row in corpus.fetch():
            print(f"{row['id']:22s} {row['status']}")
        corpus.write_lock()
    bad = corpus.verify()
    if bad:
        raise SystemExit(f"files changed since the lock was written: {bad} (re-run online to re-pin)")
    pages = corpus.extract_pages()
    for doc_id, n in pages.items():
        print(f"{doc_id:22s} {n} pages")
    docs = [row["id"] for row in corpus.load_corpus() if row["id"] in pages]
    print(kwic.run(docs))
    codes = list(kwic.load_codebook()["codes"])
    coding.run(docs, codes)
    print(report.run())
    import importlib.util  # site/build.py is a script, not a package module
    spec = importlib.util.spec_from_file_location("site_build", Path(__file__).parent / "site" / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print(module.build())


if __name__ == "__main__":
    main()
