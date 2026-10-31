# -*- coding: utf-8 -*-
"""SELECTION-UI-OCCURRENCE-COUNT-01 委任_01: 同形異義(品詞違い)による誤カウント(FP)リスクの評価用oracle。
集計本体にはNLTK(品詞推定)を使わない(Production依存追加なし・決定論は字面+活用表のみ)。ここでは『もし品詞が混ざっていたら』を件数化するため、
ローカルにあるNLTK perceptron taggerで各ヒット語の品詞(N/V/J/R)を推定し、同一項目内で品詞が割れる項目を列挙する(評価専用。確定判定には使わない)。
入力: run_precision_01の hits_all.tsv。出力: pos_audit.tsv(項目別の品詞分布)と、品詞が割れた項目のヒット一覧 pos_split_hits.tsv。
"""
from __future__ import annotations

import argparse
import collections
import csv
import os
import sys

import nltk

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import occurrence_count_01 as oc          # noqa: E402


def coarse(tag: str) -> str:
    if tag.startswith("NN"):
        return "N"
    if tag.startswith("VB"):
        return "V"
    if tag.startswith("JJ"):
        return "J"
    if tag.startswith("RB"):
        return "R"
    return tag


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    a = ap.parse_args(argv)
    rows = list(csv.DictReader(open(os.path.join(a.evidence, "hits_all.tsv"), encoding="utf-8"), delimiter="\t"))
    by = collections.defaultdict(list)
    for r in rows:
        if r["counted"] != "YES":
            continue
        sent = oc.normalize(r["sentence"])
        toks = nltk.word_tokenize(sent) if False else [t[0] for t in oc.tokenize(sent)]
        # ヒット語の位置: 文中でsurfaceの先頭tokenを探す(初出)
        first = oc.term_tokens(r["surface"])[0] if oc.term_tokens(r["surface"]) else ""
        raw = [m.group(0) for m in oc._TOKEN_RE.finditer(sent)]
        tags = nltk.pos_tag(raw)
        pos = None
        for w, t in tags:
            if w.lower() == first:
                pos = coarse(t)
                break
        by[(r["member"], r["kind"], r["term"])].append((pos, r))
    out, split_hits = [], []
    for key, lst in sorted(by.items()):
        c = collections.Counter(p for p, _ in lst)
        out.append({"member": key[0], "kind": key[1], "term": key[2], "n_hits": len(lst), "pos_dist": dict(c), "split": len(c) > 1})
        if len(c) > 1:
            for p, r in lst:
                split_hits.append({"member": key[0], "term": key[2], "pos": p, "section": r["section"], "surface": r["surface"], "sentence": r["sentence"]})
    with open(os.path.join(a.evidence, "pos_audit.tsv"), "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(out[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(out)
    with open(os.path.join(a.evidence, "pos_split_hits.tsv"), "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=["member", "term", "pos", "section", "surface", "sentence"], delimiter="\t")
        w.writeheader()
        w.writerows(split_hits)
    print({"entries_with_hits": len(out), "entries_pos_split": sum(1 for o in out if o["split"]), "split_hit_rows": len(split_hits)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
