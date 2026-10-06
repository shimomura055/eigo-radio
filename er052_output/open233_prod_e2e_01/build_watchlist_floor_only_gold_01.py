# -*- coding: utf-8 -*-
"""OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 委任_04: ¥0事前replay。保存済みrun(段階A 42 run=Stage 1のみ・旧E2E 9 run=Stage 2込み)と
旧floor分析(floor_fire_analysis_01.json)から、「floor(機械判定)だけで重大にしていたgold」のwatch listを作る。
読み取り専用(runner globalは変更しない)。出力=watchlist_floor_only_gold.json。E2E集計で個別追跡する。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402

ANALYSIS = "er052_output/open233_floor_selectivity_offline_01/floor_fire_analysis_01.json"
LEGACY_FLAGS = ("changed_actor", "changed_number", "changed_negation", "changed_comparison", "changed_time")


def norm(t):
    return runner._norm_for_residual(t)


def matches_def(d, claim_text):
    t = norm(claim_text)
    if norm(d["text_substring"]).lower() in t.lower():
        return True
    return bool(d.get("text_pattern") and re.search(d["text_pattern"], t, re.I))


def load_json(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def scan_e2e(e2e_dir):
    """旧E2E 9 run: SC gold定義に一致するStage 2結果を全cycleから集め、floorだけで重大化していたかを分類。"""
    rows = []
    for p in sorted(glob.glob(os.path.join(e2e_dir, "s*", "*.json"))):
        r = load_json(p)
        iid = r.get("instance_id")
        for d in runner._safety_critical_defs(iid):
            for ci, c in enumerate(r.get("cycles") or []):
                for sr in c.get("stage2_results") or []:
                    if sr.get("detected_by_enumeration") or not matches_def(d, sr.get("claim_text") or ""):
                        continue
                    dev = sr.get("dev") or {}
                    flags = [k for k in LEGACY_FLAGS if dev.get(k)]
                    fr = sr.get("floor_reason") or ""
                    llm = sr.get("llm_materiality")
                    rows.append({"instance_id": iid, "sample": r.get("sample"), "sub_id": d["sub_id"], "cycle_index": ci,
                                 "claim": (sr.get("claim_text") or "")[:160], "llm_materiality": llm, "final_materiality": sr.get("materiality"),
                                 "floor_reason": fr or None, "legacy_flags_true": flags,
                                 "floor_only": bool(fr.startswith("deterministic_floor:") and llm != "BLOCKING"),
                                 "would_fire_under_number_only": "changed_number" in flags,
                                 "s1_second_opinion_blocking": fr == "s1_second_opinion_blocking"})
    return rows


def scan_stagea(stagea_dir):
    """段階A(Stage 1のみ): SC gold定義に一致するr3/r5候補の有無とフラグ(Stage 2判定は無い)。"""
    rows = []
    for p in sorted(glob.glob(os.path.join(stagea_dir, "runs", "s*", "*.json"))):
        r = load_json(p)
        iid = r.get("instance_id")
        defs = runner._safety_critical_defs(iid)
        if not defs:
            continue
        for d in defs:
            hit = flags = None
            for route in ("r3", "r5"):
                for c in ((r.get("audit") or {}).get("per_route", {}).get(route) or {}).get("candidates", []):
                    if matches_def(d, c.get("claim_text") or ""):
                        hit = True
                        flags = sorted(set(flags or []) | {k for k, v in (c.get("flags") or {}).items() if v and k in LEGACY_FLAGS})
            rows.append({"instance_id": iid, "sample": r.get("sample"), "sub_id": d["sub_id"], "stage1_candidate_found": bool(hit),
                         "legacy_flags_true": flags or []})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stagea-dir", required=True)
    ap.add_argument("--e2e-dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    e2e = scan_e2e(a.e2e_dir)
    stagea = scan_stagea(a.stagea_dir)
    ana = load_json(ANALYSIS)
    legit = [{"no": x["no"], "run": x["run"], "cycle": x["cycle"], "claim": x["claim"][:160], "floor_reason": x["floor_reason"],
              "llm_materiality": x["llm_materiality"], "legacy_flags_true": x["reason_flags"],
              "would_fire_under_number_only": "changed_number" in x["reason_flags"], "label_RCA_suggested": x["label_RCA_suggested"]}
             for x in ana["rows"] if x.get("label_RCA_suggested") == "正当"]
    floor_only = [x for x in e2e if x["floor_only"]]
    watch = [x for x in floor_only if not x["would_fire_under_number_only"]]
    out = {"provenance": "frozen(保存run json、¥0)。旧仕様の保存結果の再集計であり新仕様のEvidenceではない。",
           "n_e2e_gold_matches": len(e2e), "n_floor_only_gold_old_e2e": len(floor_only),
           "n_floor_only_gold_lost_under_number_only": len(watch),
           "watch_list_old_e2e_floor_only_gold": watch,
           "legit_floor_6_from_old_analysis": legit,
           "n_legit_floor_6_lost_under_number_only": sum(1 for x in legit if not x["would_fire_under_number_only"]),
           "analysis_floor_only_gold": ana["sc_gold_holdout_summary"].get("list_floor_only_gold"),
           "e2e_gold_rows": e2e, "stagea_gold_stage1_rows": stagea,
           "stagea_gold_candidate_found_rate": {"found": sum(1 for x in stagea if x["stage1_candidate_found"]), "total": len(stagea)},
           "note": "watch=旧仕様でfloorだけが重大化していたgoldで数字floorでは残らないもの。新E2Eは再分類+Stage 2+S1でこれらが拾われるかを個別追跡する。"}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("n_e2e_gold_matches", "n_floor_only_gold_old_e2e", "n_floor_only_gold_lost_under_number_only",
                                          "n_legit_floor_6_lost_under_number_only", "stagea_gold_candidate_found_rate")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
