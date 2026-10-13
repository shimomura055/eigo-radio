# ============================================================
# er064_kp_noway_01_analyze.py  (FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01、評価専用・Trial専用・JPY0)
# job_result.json群(対照=Round1のM2P0、処置=委任_02のM2P0X)から、事前登録の判定指標を同じ関数で算出する。LLM呼出なし。
# 使い方: PYTHONPATH=. PYTHONUTF8=1 .venv/Scripts/python.exe er064_kp_noway_01_analyze.py --glob "<runsのglob>" --label control_M2P0 --out <json>
# 評価語(アンカー・no way等)はこの解析側だけが参照する(Prompt/shortlistには入れない)。
# ============================================================
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import er064_kp_int_01_eval as EV  # noqa: E402
import er064_kp_opt_01_upstream_core as U  # noqa: E402

CONT_NEXT = {"to", "of", "for", "with", "that", "in", "on", "at", "by", "from", "as", "than"}
TOK = re.compile(r"[A-Za-z][A-Za-z'-]*")
PLACEHOLDER = {"one's", "someone's", "somebody's", "someone", "somebody", "oneself", "one"}


def words(s):
    return TOK.findall(s or "")


def stems(s):
    return [U._stem(t) for t in words(s)]


def tolerant_verbatim(display, sentence):
    """displayの全語(placeholder語を除く)が、語幹正規化後にsentence内でこの順に現れるか(連続は要求しない=基本形化・語形差を許す)。"""
    sent = stems(sentence)
    pos = 0
    for t in [U._stem(w) for w in words(display) if w.lower() not in PLACEHOLDER]:
        try:
            pos = sent.index(t, pos) + 1
        except ValueError:
            return False
    return True


def literal_verbatim(display, sentence):
    return re.sub(r"\s+", " ", display.lower()) in re.sub(r"\s+", " ", sentence.lower())


def classify_construction_fragment(it):
    """一般化指標(特定語を使わない): display==候補surface(語幹同一)、2語以内、本文でそのspanの直後が構文を完結させる閉クラス語(to/of/for…)。"""
    sp = it.get("source_span") or ""
    sent = it.get("source_sentence") or ""
    if len(words(sp)) > 2 or stems(it.get("display_phrase")) != stems(sp):
        return False
    m = re.search(re.escape(sp) + r"\s+(\w+)", sent, re.I)
    return bool(m and m.group(1).lower() in CONT_NEXT)


def no_way_class(raw_items, final_keys):
    """評価専用(特定語)。A=no wayを含む最終語句なし / B=no wayを含み3語以上 / bare=no way単独。"""
    ks = [k.lower() for k in final_keys]
    hit = [k for k in ks if "no way" in k]
    if not hit:
        return "A"
    return "bare" if any(k.strip() == "no way" for k in hit) else "B"


def analyze_cell(runs):
    n = len(runs)
    out = {"n": n, "runs": []}
    gate = collections.Counter()
    keyfreq = collections.Counter()
    anchor_cnt = collections.Counter()
    score, low = [], []
    cls = collections.Counter()
    overext = 0
    finite_aux_invalid = 0
    frag_sel = 0
    verb_lit = verb_tol = tot_items = 0
    for r in runs:
        gate[f"sel:{r.get('selection_status')}"] += 1
        gate[f"canon:{r.get('canonicalization_status')}"] += 1
        gate[f"red:{r.get('redundancy_status')}"] += 1
        gate[f"merged:{r.get('merged_overall_status')}"] += 1
        if any("有限助動詞" in x for ir in (r.get("item_reasons") or []) for x in ir.get("reasons", [])):
            finite_aux_invalid += 1
        items = r.get("selected_items") or []
        raw = r.get("raw_selected_items") or []
        keys = [c["key_phrase"] for c in r.get("canonicalized", [])] or [i["display_phrase"] for i in items]
        for k in keys:
            keyfreq[k.lower()] += 1
        sc = EV.run_score(items) if items else {"score": 0, "full_ranks": [], "fragment_ranks": [], "low_slots": 0}
        score.append(sc["score"])
        low.append(sc["low_slots"])
        for rk in sc["full_ranks"]:
            anchor_cnt[rk] += 1
        cls[no_way_class(raw, keys)] += 1
        for it in raw:
            tot_items += 1
            nd = len(words(it["display_phrase"]))
            nc = len(words(it.get("resolved_candidate_surface_form") or it["source_span"]))
            if nd - nc >= 2:
                overext += 1
            if classify_construction_fragment(it):
                frag_sel += 1
            verb_lit += literal_verbatim(it["display_phrase"], it["source_sentence"])
            verb_tol += tolerant_verbatim(it["display_phrase"], it["source_sentence"])
        out["runs"].append({"tag": r["tag"], "final_keys": keys, "no_way_class": no_way_class(raw, keys), "score": sc["score"], "anchors": sc["full_ranks"],
                            "gate": [r.get("selection_status"), r.get("canonicalization_status"), r.get("redundancy_status"), r.get("merged_overall_status")],
                            "cost_jpy": r.get("cost_jpy")})
    out.update(gate=dict(gate), merged_pass=gate.get("merged:PASS", 0), no_way_class=dict(cls), anchor_adoption_by_rank=dict(sorted(anchor_cnt.items())),
               mean_score=round(sum(score) / n, 2) if n else None, mean_low_slots=round(sum(low) / n, 2) if n else None,
               over_extended_items=overext, construction_fragment_selected_items=frag_sel, finite_aux_selection_invalid_runs=finite_aux_invalid,
               verbatim_literal=f"{verb_lit}/{tot_items}", verbatim_tolerant=f"{verb_tol}/{tot_items}", key_phrase_freq=dict(keyfreq.most_common()),
               cost_mean=round(sum(r.get("cost_jpy", 0) for r in runs) / n, 4) if n else None)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cells = collections.defaultdict(list)
    for f in sorted(glob.glob(a.glob)):
        j = json.load(open(f, encoding="utf-8"))
        cells[f"{j['article']}_{j['level']}"].append(j)
    res = {"label": a.label, "glob": a.glob, "cells": {k: analyze_cell(v) for k, v in sorted(cells.items())}}
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in res["cells"].items():
        print(k, "n", v["n"], "merged_PASS", v["merged_pass"], "no_way", v["no_way_class"], "score", v["mean_score"], "low", v["mean_low_slots"],
              "overext", v["over_extended_items"], "frag_sel", v["construction_fragment_selected_items"], "tol_verb", v["verbatim_tolerant"])


if __name__ == "__main__":
    main()
