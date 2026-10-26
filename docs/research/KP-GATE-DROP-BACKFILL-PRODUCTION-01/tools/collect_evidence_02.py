# -*- coding: utf-8 -*-
"""KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_03: fresh 8 level-run + replay 7件の証拠を evidence_01.json に集計する(読取りのみ・API 0)。
実行: .venv\\Scripts\\python.exe docs\\research\\KP-GATE-DROP-BACKFILL-PRODUCTION-01\\tools\\collect_evidence_02.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

D = "docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01"
XO = "er019_output/family_x_audio_production_wiring_01"
FRESH = [
    ("X", "AI島(ai_island_temple)", "a2", f"{XO}/ai_island_temple__run_kpbf_ev_01/a2/key_phrases/kp_candidates.json", f"{XO}/ai_island_temple__run_kpbf_ev_01/raw_usage_log.jsonl"),
    ("X", "AI島(ai_island_temple)", "b1b", f"{XO}/ai_island_temple__run_kpbf_ev_01/b1b/key_phrases/kp_candidates.json", f"{XO}/ai_island_temple__run_kpbf_ev_01/raw_usage_log.jsonl"),
    ("Y", "再配達(redelivery_fee)", "a2", "er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01/key_phrases/a2/kp_candidates.json", "er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01/cost_log.jsonl"),
    ("Y", "再配達(redelivery_fee)", "b1b", "er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01/key_phrases/b1b/kp_candidates.json", "er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01/cost_log.jsonl"),
    ("Z", "走れメロス(melos)", "a2", "er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01/key_phrases/a2/kp_candidates.json", "er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01/cost_log.jsonl"),
    ("Z", "走れメロス(melos)", "b1b", "er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01/key_phrases/b1b/kp_candidates.json", "er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01/cost_log.jsonl"),
    ("X(R-9)", "コーヒー価格(coffee_prices)", "a2", f"{XO}/coffee_prices__run_kpbf_ev_02/a2/key_phrases/kp_candidates.json", f"{XO}/coffee_prices__run_kpbf_ev_02/raw_usage_log.jsonl"),
    ("X(R-9)", "コーヒー価格(coffee_prices)", "b1b", f"{XO}/coffee_prices__run_kpbf_ev_02/b1b/key_phrases/kp_candidates.json", f"{XO}/coffee_prices__run_kpbf_ev_02/raw_usage_log.jsonl"),
    ("X(R-9)", "中東情勢(middle_east_yemen_saudi)", "a2", f"{XO}/middle_east_yemen_saudi__run_kpbf_ev_03/a2/key_phrases/kp_candidates.json", f"{XO}/middle_east_yemen_saudi__run_kpbf_ev_03/raw_usage_log.jsonl"),
    ("X(R-9)", "中東情勢(middle_east_yemen_saudi)", "b1b", f"{XO}/middle_east_yemen_saudi__run_kpbf_ev_03/b1b/key_phrases/kp_candidates.json", f"{XO}/middle_east_yemen_saudi__run_kpbf_ev_03/raw_usage_log.jsonl"),
]
REPLAYS = ["R1_X_ai_island_a2", "R2_X_uk_a2", "R3_Y_redelivery_a2", "R4_Y_sns_b1b", "R5a_Z_monkeys_paw_b1b_frozen_only", "R5b_Z_monkeys_paw_b1b_dup_inject", "R6_Z_melos_b1b"]


def _j(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def summarize(doc: dict) -> dict:
    import er119_kp_prompt_2v_01 as p2v
    cands = doc["candidates"]
    bf = doc.get("backfill") or {}
    E = bf.get("E") or {}
    att = (bf.get("attempts") or [{}])[0]
    return {
        "n_candidates": len(cands), "n_auto_eligible": sum(1 for c in cands if c.get("auto_eligible")),
        "origins": {o: sum(1 for c in cands if c.get("origin") == o) for o in ("call1", "call2", "backfill")},
        "backfill_status": bf.get("status"), "triggered": bf.get("triggered"), "reason": bf.get("reason"),
        "E": {"total": E.get("total"), "phrase": E.get("phrase"), "word": E.get("word"), "by_stage": E.get("by_stage"), "items": E.get("items")},
        "N": bf.get("N"), "added": [a["used_form"] for a in bf.get("added") or []], "added_ai_rank": [a["ai_rank"] for a in bf.get("added") or []],
        "surplus": [a["used_form"] for a in bf.get("surplus") or []], "backfill_dropped_by_stage": bf.get("dropped_by_stage"),
        "backfill_call": {"n_selected": att.get("n_selected"), "n_kept": att.get("n_kept"), "n_dropped": att.get("n_dropped"), "model": att.get("model")},
        "backfill_prompt_sha256": bf.get("prompt_sha256"), "backfill_prompt_sha_pinned_match": (bf.get("prompt_sha256") == p2v.PROMPT_2V_SHA256_PINNED) if bf.get("triggered") else None,
        "dropped": [{"origin": x.get("origin"), "stage": x.get("stage"), "phrase": x.get("phrase")} for x in doc.get("dropped") or []],
        "backfill_duplicate_dropped": sum(1 for x in doc.get("dropped") or [] if x.get("stage") == "backfill_duplicate"),
        "rescued": [{"used_form": c["used_form"], "codes": (c.get("flags") or {}).get("rescue_codes"), "auto_eligible": c.get("auto_eligible")} for c in cands if (c.get("flags") or {}).get("rescued")],
        "outer_attempts": doc.get("outer_attempts"), "outer_retry_log": doc.get("outer_retry_log"),
        "rescued_not_auto": (doc.get("outer_retry_log") or [{}])[-1].get("rescued_not_auto"),
        "shortfall": doc.get("shortfall"), "shortfall_detail": doc.get("shortfall_detail"),
        "src_d1": sorted({(c.get("gates") or {}).get("src_d1") for c in cands}),
        "model_id": doc.get("model_id"), "model_requested": doc.get("model_requested"),
        "prompt_sha256": doc.get("prompt_sha256"),
        "prompt_sha_pinned_match": {"call2_2V": (doc.get("prompt_sha256") or {}).get("call2") == p2v.PROMPT_2V_SHA256_PINNED},
        "candidates_sha256": doc.get("candidates_sha256"),
    }


def main():
    import er019_family_x_audio_production_runner_01 as x
    out = {"fresh": [], "replay": []}
    for fam, art, lv, cp, up in FRESH:
        if not os.path.exists(cp):
            out["fresh"].append({"family": fam, "article": art, "level": lv, "missing": cp})
            continue
        s = summarize(_j(cp))
        s.update(family=fam, article=art, level=lv, cand_path=cp, file_sha256=hashlib.sha256(open(cp, "rb").read()).hexdigest())
        out["fresh"].append(s)
    costs = {}
    for up in sorted({f[4] for f in FRESH}):
        if os.path.exists(up):
            total, _ = x.compute_cost_jpy_so_far(up)
            costs[up] = round(total, 4)
    out["fresh_run_cost_jpy"] = costs
    for r in REPLAYS:
        rp = f"{D}/replay_results/{r}/replay_result.json"
        dp = f"{D}/replay_results/{r}/kp_candidates_doc.json"
        if not os.path.exists(dp):
            out["replay"].append({"case": r, "missing": dp})
            continue
        s = summarize(_j(dp))
        rr = _j(rp)
        total, _ = x.compute_cost_jpy_so_far(f"{D}/replay_results/{r}/raw_usage_log.jsonl")
        s.update(case=r, frozen=rr.get("frozen"), cost_jpy=round(total, 4), api_calls=rr.get("api_calls_logged"), api_by_stage=rr.get("api_calls_by_stage"),
                 backfill_raw=rr.get("backfill_raw"), vocab_calls=rr.get("vocab_calls"), canon_calls=rr.get("canon_calls"))
        out["replay"].append(s)
    out["total_cost_jpy"] = round(sum(costs.values()) + sum(r.get("cost_jpy", 0) for r in out["replay"]), 4)
    with open(f"{D}/evidence_01.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({"fresh_cost": costs, "replay_cost": {r.get("case"): r.get("cost_jpy") for r in out["replay"]}, "total": out["total_cost_jpy"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
