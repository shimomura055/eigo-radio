# -*- coding: utf-8 -*-
"""SELECTION-UI-OCCURRENCE-COUNT-01 委任_01: 『選定フォーム生成時点のrun dir本文』で数えた件数 と 『公開済みenduser page(enduser_article_v1)の実表示本文』で数えた件数 を
項目ごとに突き合わせる(区分: story/comment/preview/oneline)。差分があれば、本文の後工程書換え(Local Rewrite・intro patch等)による乖離として列挙する。API 0・read-only。
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

SEC4 = ("story", "comment", "preview", "oneline")


def slug_of_enduser(dirname: str) -> str:
    s = re.sub(r"^family_[xyz]_(production_)?", "", dirname)
    s = re.sub(r"_(reselect_)?\d+$", "", s)
    s = re.sub(r"_kphr_evidence_r\d+$", "", s)
    return s


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--extra-root", action="append", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    roots = [a.root] + a.extra_root
    sys.path.insert(0, a.root)
    eu = {}
    for p in glob.glob(os.path.join(a.root, "user_test", "family_*", "enduser", "data", "article.json")):
        d = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(p))))
        eu.setdefault(slug_of_enduser(d), []).append((d, p))
    rows, summ = [], {"entries_compared": 0, "entries_identical": 0, "entries_diff": 0, "pages": []}
    for f in sorted(glob.glob(os.path.join(a.root, "user_test", "selection_form_v3", "data", "*__*prod.json"))):
        stem = os.path.basename(f)[:-5]
        slug = stem.split("__")[0].replace("_prod", "")
        slug = {"melos_prod": "melos"}.get(slug, slug)
        if slug not in eu:
            continue
        d = json.load(open(f, encoding="utf-8"))
        cp = d.get("source_kp_candidates_path")
        if not cp:
            continue
        lv_eu = {"a2": "std", "b1b": "adv"}[d["level"]]
        sections, _ = sl.load_sections(d["family"], cp, d["level"], roots)
        for (dirn, ap_) in eu[slug]:
            eus = sl.load_enduser_sections(ap_, lv_eu)
            summ["pages"].append(f"{stem} <-> {dirn}/{lv_eu}")
            for kind, items in (("phrase", d["phrases"]), ("word", d["words"])):
                for e in items:
                    term = e["term"]
                    sel = e.get("selection_phrase")
                    sel = sel if sel and sel != term else None
                    A = oc.count_entry(sections, term, sel)
                    B = oc.count_entry({**eus, "title": eus.get("title")}, term, sel)
                    ca = {k: A["counts"].get(k) for k in SEC4}
                    cb = {k: B["counts"].get(k) for k in SEC4}
                    same = ca == cb
                    summ["entries_compared"] += 1
                    summ["entries_identical" if same else "entries_diff"] += 1
                    if not same:
                        rows.append({"member": stem, "enduser": dirn, "kind": kind, "term": term, "rundir": json.dumps(ca), "enduser_page": json.dumps(cb)})
    with open(os.path.join(a.out, "crosscheck_enduser.tsv"), "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=["member", "enduser", "kind", "term", "rundir", "enduser_page"], delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(a.out, "crosscheck_enduser_summary.json"), "w", encoding="utf-8") as fo:
        json.dump(summ, fo, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "pages"}, ensure_ascii=False), len(summ["pages"]), "pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
