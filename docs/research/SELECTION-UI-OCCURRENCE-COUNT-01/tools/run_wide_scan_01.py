# -*- coding: utf-8 -*-
"""SELECTION-UI-OCCURRENCE-COUNT-01 委任_01: batch member以外も含む既存の全kp_candidates.json(X/Y/Z・過去run含む)に集計を走らせ、
『exact以外で確定/保留になったヒット』(活用形・人称スロット・分離・逆引き活用)を全件出力する(人手確認用。API 0)。
exactヒットは項目数が多いため件数のみ集計し、一覧は non-exact のみ(exactは選定表層S/一般化形Uとのトークン完全一致=誤りの余地は同形異義のみ)。
"""
from __future__ import annotations

import argparse
import csv
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import occurrence_count_01 as oc          # noqa: E402
import section_loaders_01 as sl           # noqa: E402

PATTERNS = [
    ("X", "er019_output/family_x_audio_production_wiring_01/*/*/key_phrases/kp_candidates.json"),
    ("Y", "er121_output/family_y_production_01/*/*/key_phrases/*/kp_candidates.json"),
    ("Z", "er026_output/family_z_production_e2e_01/*/*/key_phrases/*/kp_candidates.json"),
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--extra-root", action="append", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    roots = [a.root] + a.extra_root
    sys.path.insert(0, a.root)
    seen, files = set(), []
    for fam, pat in PATTERNS:
        for r in roots:
            for p in glob.glob(os.path.join(r, pat)):
                rel = os.path.relpath(p, r).replace("\\", "/")
                if "/kp_candidates/round_" in rel or rel in seen or "_backup" in rel or "pre02a" in rel:
                    continue
                seen.add(rel)
                files.append((fam, rel))
    rows, stat = [], collections.Counter()
    docs_used = 0
    for fam, rel in sorted(files):
        try:
            doc = json.load(open(next(os.path.join(r, rel) for r in roots if os.path.exists(os.path.join(r, rel))), encoding="utf-8"))
        except Exception:
            stat["doc_unreadable"] += 1
            continue
        lv = doc.get("level") or ("b1b" if "/b1b/" in rel else "a2")
        lv = "b1b" if lv in ("b1b", "B1B", "b1") else "a2"
        sections, _ = sl.load_sections(fam, rel, lv, roots)
        if sections["story"] is None:
            stat["no_story_text"] += 1
            continue
        docs_used += 1
        for c in doc.get("candidates") or []:
            term = c.get("used_form") or c.get("selection_phrase")
            sel = c.get("selection_phrase") or term
            if not term:
                continue
            occ = oc.count_entry(sections, term, sel if sel != term else None, with_hits=True)
            stat["entries"] += 1
            for h in occ["hits"]:
                stat["hits_" + h["rule"] + ("_unc" if h["uncertain"] else "")] += 1
                if h["rule"] != "exact":
                    rows.append({"doc": rel, "term": term, "selection_phrase": sel, "section": h["section"], "rule": h["rule"], "counted": "NO(uncertain)" if h["uncertain"] else "YES",
                                 "surface": h["surface"], "sentence": h["sentence"]})
    with open(os.path.join(a.out, "wide_scan_nonexact_hits.tsv"), "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=["doc", "term", "selection_phrase", "section", "rule", "counted", "surface", "sentence", "judgement"], delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow({**r, "judgement": ""})
    stat["docs_used"] = docs_used
    stat["docs_found"] = len(files)
    with open(os.path.join(a.out, "wide_scan_summary.json"), "w", encoding="utf-8") as fo:
        json.dump(dict(stat), fo, ensure_ascii=False, indent=1)
    print(json.dumps(dict(stat), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
