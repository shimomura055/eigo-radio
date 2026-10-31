# -*- coding: utf-8 -*-
"""SELECTION-UI-OCCURRENCE-COUNT-01 委任_02: 正式module(er140_*)で、委任_01と同じ27 member(253項目)を再集計し、(1)全ヒット (2)委任_01の結果との差分 (3)取りこぼし監査oracle の再実行結果を出力する。API 0・read-only。

実行: .venv\\Scripts\\python.exe docs\\research\\SELECTION-UI-OCCURRENCE-COUNT-01\\tools\\run_precision_02.py --root <repo/worktree> --extra-root <main tree> --out <evidence_02 dir>
出力: counts_02.tsv / hits_all_02.tsv / diff_vs_01.tsv(委任_01のhits_all.tsvとの差: 確定->保留・保留->確定・新規・消滅) / nearmiss_02.tsv(oracle) / summary_02.json
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
ROOT_DEFAULT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def load_mods(root):
    sys.path.insert(0, root)
    import er140_selection_occurrence_count_01 as oc
    import er140_selection_occurrence_sections_01 as sl
    return oc, sl


def sentences(oc, text):
    t = oc.normalize(text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", t) if s.strip()]


def stem(tok):
    t = tok.replace("'s", "")
    for suf in ("ing", "ied", "ies", "ed", "es", "ly", "ion", "s", "e", "y"):
        if t.endswith(suf) and len(t) - len(suf) >= 3:
            t = t[: -len(suf)]
            break
    return t[:4]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--extra-root", action="append", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--old-hits", default=os.path.join(HERE, "..", "evidence", "hits_all.tsv"))
    a = ap.parse_args(argv)
    oc, sl = load_mods(a.root)
    roots = [a.root] + a.extra_root
    os.makedirs(a.out, exist_ok=True)
    stop = oc._CLOSED | {"someone", "somebody", "something", "one", "oneself"}
    hits_rows, count_rows, near, members = [], [], [], {}
    files = sorted(glob.glob(os.path.join(a.root, "user_test", "selection_form_v3", "data", "*__*prod.json")))
    for f in files:
        stem_name = os.path.basename(f)[:-5]
        d = json.load(open(f, encoding="utf-8"))
        cp = d.get("source_kp_candidates_path")
        if not cp:
            members[stem_name] = "NO_CAND_PATH"
            continue
        sections, srcs = sl.load_sections(d["family"], cp, d["level"], roots)
        members[stem_name] = {"family": d["family"], "level": d["level"], "unavailable": [k for k, v in sections.items() if v is None and k != "title"]}
        cdoc = None
        for r in roots:
            if os.path.exists(os.path.join(r, cp)):
                cdoc = {c["candidate_id"]: c for c in json.load(open(os.path.join(r, cp), encoding="utf-8"))["candidates"]}
                break
        for kind, items in (("phrase", d["phrases"]), ("word", d["words"])):
            for e in items:
                term = e["term"]
                sel = e.get("selection_phrase") or term
                occ = oc.count_entry(sections, term, sel if sel != term else None, with_hits=True)
                old_n = ((cdoc or {}).get(e["id"]) or {}).get("item", {}).get("occurrence_count")
                mine = oc.exact_selection_count(sections, sel)
                count_rows.append({"member": stem_name, "family": d["family"], "level": d["level"], "kind": kind, "term": term, "selection_phrase": sel,
                                   **{k: occ["counts"].get(k) for k in ("story", "comment", "preview", "oneline", "title")}, "total": occ["total"],
                                   "uncertain": json.dumps(occ.get("uncertain", {}), ensure_ascii=False), "unavailable": ",".join(occ.get("unavailable", [])),
                                   "forms": json.dumps(occ["forms"], ensure_ascii=False), "old_occurrence_count": old_n, "exact_S_story_oneline_title": mine})
                for h in occ["hits"]:
                    hits_rows.append({"member": stem_name, "kind": kind, "term": term, "selection_phrase": sel, "section": h["section"], "rule": h["rule"],
                                      "counted": "NO(uncertain)" if h["uncertain"] else "YES", "surface": h["surface"], "sentence": h["sentence"]})
                # 取りこぼし監査oracle(緩い基準): 内容語の語幹が同一文に揃うのにヒットしない文
                U, S = oc.term_tokens(term), oc.term_tokens(sel)
                content = [t for t in dict.fromkeys(U + S) if t not in stop and len(t) > 2]
                if not content:
                    continue
                stems = {stem(t) for t in content}
                pats = oc.build_patterns(term, sel if sel != term else None)
                for sec in oc.SECTIONS:
                    for ui, para in enumerate(sections.get(sec) or []):
                        hs = oc.find_hits(para, pats)
                        covered_sent = {oc._sentence_of(oc.normalize(para), h["start"], h["end"]) for h in hs}
                        for s in sentences(oc, para):
                            if stems <= {stem(t[0]) for t in oc.tokenize(s)} and s not in covered_sent:
                                near.append({"member": stem_name, "kind": kind, "term": term, "selection_phrase": sel, "section": sec, "unit": ui, "sentence": s})

    def wr(name, rows, fields=None):
        fields = fields or (list(rows[0].keys()) if rows else ["empty"])
        with open(os.path.join(a.out, name), "w", encoding="utf-8", newline="") as fo:
            w = csv.DictWriter(fo, fieldnames=fields, delimiter="\t")
            w.writeheader()
            w.writerows(rows)

    wr("counts_02.tsv", count_rows)
    wr("hits_all_02.tsv", hits_rows)
    wr("nearmiss_02.tsv", [{**r, "judgement": "", "note": ""} for r in near], ["member", "kind", "term", "selection_phrase", "section", "unit", "sentence", "judgement", "note"])
    # 委任_01との差分(member,term,section,surface,sentence,counted の多重集合)
    def key(r):
        return (r["member"], r["term"], r["section"], r["surface"].lower(), r["sentence"], r["counted"])
    old = list(csv.DictReader(open(a.old_hits, encoding="utf-8", newline=""), delimiter="\t"))
    from collections import Counter
    co, cn = Counter(key(r) for r in old), Counter(key(r) for r in hits_rows)
    diff = []
    for k in sorted(set(co) | set(cn)):
        if co[k] != cn[k]:
            diff.append({"member": k[0], "term": k[1], "section": k[2], "surface": k[3], "counted": k[5], "old_n": co[k], "new_n": cn[k], "sentence": k[4], "judgement": "", "note": ""})
    wr("diff_vs_01.tsv", diff, ["member", "term", "section", "surface", "counted", "old_n", "new_n", "sentence", "judgement", "note"])
    mism = [r for r in count_rows if r["old_occurrence_count"] is not None and r["exact_S_story_oneline_title"] is not None and r["old_occurrence_count"] != r["exact_S_story_oneline_title"]]
    summ = {"members": len(members), "entries": len(count_rows), "hits": len(hits_rows), "hits_counted": sum(1 for h in hits_rows if h["counted"] == "YES"),
            "hits_uncertain": sum(1 for h in hits_rows if h["counted"] != "YES"), "nearmiss_rows": len(near), "diff_rows_vs_01": len(diff), "invariant_mismatches": len(mism),
            "invariant_mismatch_items": [{k: r[k] for k in ("member", "term", "old_occurrence_count", "exact_S_story_oneline_title")} for r in mism],
            "members_detail": members}
    json.dump(summ, open(os.path.join(a.out, "summary_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "members_detail"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
