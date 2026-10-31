# -*- coding: utf-8 -*-
"""SELECTION-UI-OCCURRENCE-COUNT-01 委任_01: 既存batch member(選定フォームデータ)全件に対し出現回数集計を走らせ、全ヒットを人手確認用に出力する。API 0・read-only。

実行: .venv\\Scripts\\python.exe docs\\research\\SELECTION-UI-OCCURRENCE-COUNT-01\\tools\\run_precision_01.py --root <repo or worktree> [--extra-root <fallback>] --out <evidence dir>
出力: hits_all.tsv(全ヒット) / counts.tsv(候補別の区分別件数) / summary.json / invariants.json(既存occurrence_countとの整合)
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import occurrence_count_01 as oc          # noqa: E402
import section_loaders_01 as sl           # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--extra-root", action="append", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--members", default=None, help="カンマ区切りstem(既定: data/*__*prod.json のうち legacy/dummy除く全件)")
    a = ap.parse_args(argv)
    roots = [a.root] + a.extra_root
    sys.path.insert(0, a.root)
    os.makedirs(a.out, exist_ok=True)
    data_dir = os.path.join(a.root, "user_test", "selection_form_v3", "data")
    files = sorted(glob.glob(os.path.join(data_dir, "*__*prod.json")))
    if a.members:
        want = set(a.members.split(","))
        files = [f for f in files if os.path.basename(f)[:-5] in want]
    hits_rows, count_rows, summary, inv = [], [], {"members": {}, "totals": {}}, []
    for f in files:
        stem = os.path.basename(f)[:-5]
        d = json.load(open(f, encoding="utf-8"))
        cp = d.get("source_kp_candidates_path")
        if not cp:
            summary["members"][stem] = {"status": "NO_CAND_PATH"}
            continue
        sections, srcs = sl.load_sections(d["family"], cp, d["level"], roots)
        # 候補docのselection情報(occurrence_count等。N5一般化形と本文実表現の対応)
        cdoc = None
        cpath = None
        for r in roots:
            if os.path.exists(os.path.join(r, cp)):
                cpath = os.path.join(r, cp)
                break
        if cpath:
            cdoc = {c["candidate_id"]: c for c in json.load(open(cpath, encoding="utf-8"))["candidates"]}
        msum = {"family": d["family"], "level": d["level"], "sources": {k: (os.path.relpath(v, a.root) if v and os.path.isabs(v) and v.startswith(a.root) else v) for k, v in srcs.items()},
                "unavailable": [k for k, v in sections.items() if v is None and k != "title"], "n_phrase": len(d["phrases"]), "n_word": len(d["words"])}
        for kind, items in (("phrase", d["phrases"]), ("word", d["words"])):
            for e in items:
                term = e["term"]
                sel = e.get("selection_phrase") or term
                occ = oc.count_entry(sections, term, sel if sel != term else None, with_hits=True)
                row = {"member": stem, "family": d["family"], "level": d["level"], "kind": kind, "id": e["id"], "term": term, "selection_phrase": sel,
                       "story": occ["counts"].get("story"), "comment": occ["counts"].get("comment"), "preview": occ["counts"].get("preview"),
                       "oneline": occ["counts"].get("oneline"), "title": occ["counts"].get("title"), "total": occ["total"],
                       "uncertain": json.dumps(occ.get("uncertain", {}), ensure_ascii=False), "unavailable": ",".join(occ.get("unavailable", [])),
                       "forms": json.dumps(occ["forms"], ensure_ascii=False)}
                c = (cdoc or {}).get(e["id"]) or {}
                it = c.get("item") or {}
                old_n = it.get("occurrence_count")
                # 不変条件: 選定時の厳密一致件数(er105 occurrence_count, 全文=title含む)==本集計のS表層厳密一致件数(title+story+oneline[X article.mdはIn One Lineを末尾段落として含む])
                _n = lambda x: x.lower().replace("’", "'").removesuffix("'s")
                exact_s = sum(1 for h in occ["hits"] if h["section"] in ("story", "title", "oneline") and not h["uncertain"] and h["rule"] == "exact" and _n(h["surface"]) == _n(sel))
                row["old_occurrence_count"] = old_n
                row["exact_S_story_title_oneline"] = exact_s
                count_rows.append(row)
                if old_n is not None and exact_s != old_n:
                    inv.append({"member": stem, "id": e["id"], "term": term, "sel": sel, "old": old_n, "mine_exact_S": exact_s})
                for h in occ["hits"]:
                    hits_rows.append({"member": stem, "kind": kind, "term": term, "selection_phrase": sel, "section": h["section"], "unit": h["unit"], "rule": h["rule"],
                                      "counted": "NO(uncertain)" if h["uncertain"] else "YES", "surface": h["surface"], "sentence": h["sentence"]})
        summary["members"][stem] = msum
    with open(os.path.join(a.out, "hits_all.tsv"), "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(hits_rows[0].keys()) if hits_rows else ["member"], delimiter="\t")
        w.writeheader()
        w.writerows(hits_rows)
    with open(os.path.join(a.out, "counts.tsv"), "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(count_rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(count_rows)
    with open(os.path.join(a.out, "invariants.json"), "w", encoding="utf-8") as fo:
        json.dump({"exact_S_vs_old_occurrence_count_mismatches": inv}, fo, ensure_ascii=False, indent=1)
    summary["totals"] = {"members": len(summary["members"]), "entries": len(count_rows), "hits": len(hits_rows),
                         "hits_counted": sum(1 for h in hits_rows if h["counted"] == "YES"), "hits_uncertain": sum(1 for h in hits_rows if h["counted"] != "YES"),
                         "invariant_mismatches": len(inv)}
    with open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8") as fo:
        json.dump(summary, fo, ensure_ascii=False, indent=1)
    print(json.dumps(summary["totals"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
