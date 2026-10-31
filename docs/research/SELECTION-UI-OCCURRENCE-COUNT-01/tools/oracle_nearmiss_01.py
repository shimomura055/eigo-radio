# -*- coding: utf-8 -*-
"""SELECTION-UI-OCCURRENCE-COUNT-01 委任_01: 取りこぼし(FN)監査用の『緩い照合』oracle。集計本体(occurrence_count_01)とは独立の寛容な基準で、
各項目の内容語(語幹先頭4字一致)が同一文に揃っているのに集計がヒットしなかった箇所を列挙する。列挙分を人手で分類してFN件数を確定する。API 0。

使い方: py oracle_nearmiss_01.py --root <repo> [--extra-root R] --out <evidence dir>   (run_precision_01と同じ入力)
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import occurrence_count_01 as oc          # noqa: E402
import section_loaders_01 as sl           # noqa: E402

_STOP = oc._CLOSED | {"someone", "somebody", "something", "one", "oneself"}


def sentences(text: str) -> list:
    t = oc.normalize(text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", t) if s.strip()]


def stem(tok: str) -> str:
    """語尾(ing/ed/es/s/e/ly/ion)を削ってから先頭4字(緩い基準。-ing/-eの揺れで取りこぼさない)。"""
    t = tok.replace("'s", "")
    for suf in ("ing", "ied", "ies", "ed", "es", "ly", "ion", "s", "e", "y"):
        if t.endswith(suf) and len(t) - len(suf) >= 3:
            t = t[: -len(suf)]
            break
    return t[:4]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--extra-root", action="append", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    roots = [a.root] + a.extra_root
    sys.path.insert(0, a.root)
    rows = []
    for f in sorted(glob.glob(os.path.join(a.root, "user_test", "selection_form_v3", "data", "*__*prod.json"))):
        d = json.load(open(f, encoding="utf-8"))
        cp = d.get("source_kp_candidates_path")
        if not cp:
            continue
        sections, _ = sl.load_sections(d["family"], cp, d["level"], roots)
        for kind, items in (("phrase", d["phrases"]), ("word", d["words"])):
            for e in items:
                term = e["term"]
                sel = e.get("selection_phrase") or term
                U = oc.term_tokens(term)
                S = oc.term_tokens(sel)
                content = [t for t in dict.fromkeys(U + S) if t not in _STOP and len(t) > 2]
                if not content:
                    continue
                stems = {stem(t) for t in content}
                pats = oc.build_patterns(term, sel if sel != term else None)
                for sec in oc.SECTIONS:
                    paras = sections.get(sec) or []
                    for ui, para in enumerate(paras):
                        hits = oc.find_hits(para, pats)
                        for s in sentences(para):
                            st = {stem(t[0]) for t in oc.tokenize(s)}
                            need = stems if kind == "phrase" else stems
                            # 緩い基準: phraseは内容語の語幹が全部同一文にある / wordは語幹が1つある
                            if not need <= st:
                                continue
                            covered = any(h["sentence"] == s for h in
                                          [{"sentence": oc._sentence_of(oc.normalize(para), h["start"], h["end"])} for h in hits])
                            if not covered:
                                rows.append({"member": os.path.basename(f)[:-5], "kind": kind, "term": term, "selection_phrase": sel, "section": sec, "unit": ui, "sentence": s})
    with open(os.path.join(a.out, "nearmiss.tsv"), "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=["member", "kind", "term", "selection_phrase", "section", "unit", "sentence", "judgement", "note"], delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow({**r, "judgement": "", "note": ""})
    print(json.dumps({"near_miss_rows": len(rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
