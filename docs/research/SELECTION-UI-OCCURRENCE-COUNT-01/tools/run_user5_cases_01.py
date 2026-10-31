# -*- coding: utf-8 -*-
"""SELECTION-UI-OCCURRENCE-COUNT-01 委任_01: ユーザー指定の5表現(put away / in the way / force away / leave out / in sight)を、
family_x_untidiness_family_resource_01 の Standard(a2)・Advanced(b1b) の実本文(run dir)に対して集計し、全ヒットを出力する(API 0)。
これらは選定フォームの候補には入っていない表現だが、分離形(put it away)・活用形(left out)・同形異義(in a way)を含む実本文での集計規則検証用の実例。
"""
import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import occurrence_count_01 as oc          # noqa: E402
import section_loaders_01 as sl           # noqa: E402

TERMS = ("put away", "in the way", "force away", "leave out", "in sight")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--extra-root", action="append", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    roots = [a.root] + a.extra_root
    sys.path.insert(0, a.root)
    rows, summ = [], {}
    for lv in ("b1b", "a2"):
        d = json.load(open(os.path.join(a.root, "user_test", "selection_form_v3", "data", f"untidiness_family_resource__{lv}__prod.json"), encoding="utf-8"))
        sec, _ = sl.load_sections("X", d["source_kp_candidates_path"], lv, roots)
        for t in TERMS:
            o = oc.count_entry(sec, t, None, with_hits=True)
            summ[f"{lv}:{t}"] = {"counts": o["counts"], "total": o["total"], "uncertain": o.get("uncertain", {}), "forms": o["forms"]}
            for h in o["hits"]:
                rows.append({"level": lv, "term": t, "section": h["section"], "rule": h["rule"], "counted": "NO(uncertain)" if h["uncertain"] else "YES", "surface": h["surface"], "sentence": h["sentence"]})
    with open(os.path.join(a.out, "user5_hits.tsv"), "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(a.out, "user5_summary.json"), "w", encoding="utf-8") as fo:
        json.dump(summ, fo, ensure_ascii=False, indent=1)
    for k, v in summ.items():
        print(k, v["counts"], "total", v["total"], "unc", v["uncertain"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
