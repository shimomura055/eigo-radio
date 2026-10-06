# -*- coding: utf-8 -*-
"""prompt衛生チェック: patterns配下の全テキストに禁止語・対象fact_idが含まれないことを検査する。
example_pattern(H1のダミー)は除外する(--include-dummyで含める)。"""
import argparse
import sys
from pathlib import Path


def load_terms(path):
    out = []
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            out.append(ln)
    return out


def scan(patterns_dir, terms, include_dummy=False):
    hits, files = [], []
    for p in sorted(Path(patterns_dir).rglob("*")):
        if not p.is_file() or p.suffix not in (".txt", ".json", ".md"):
            continue
        if not include_dummy and "example_pattern" in p.parts:
            continue
        files.append(str(p))
        text = p.read_text(encoding="utf-8")
        low = text.lower()
        for t in terms:
            if t in text or t.lower() in low:
                hits.append({"file": str(p), "term": t})
    return files, hits


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", required=True)
    ap.add_argument("--forbidden", required=True)
    ap.add_argument("--include-dummy", action="store_true")
    a = ap.parse_args(argv)
    files, hits = scan(a.patterns, load_terms(a.forbidden), a.include_dummy)
    print("files_scanned=%d" % len(files))
    for h in hits:
        print("HIT %(file)s: %(term)s" % h)
    print("PASS" if not hits else "FAIL")
    return 0 if not hits else 1


if __name__ == "__main__":
    sys.exit(main())
