# -*- coding: utf-8 -*-
"""AUW 委任_06e: 06dで判明した実run不整合F1(Z kp_en)・F2(Z circuit-open KeyError)・F3(A2外側ループ最終NG)の是正後の再実run。
計測・隔離・累計ledgerは er078_auw_runtime_evidence_06b/06d/06d_z を再利用し、証跡先(evidence_06e)・累計上限(JPY 10)・管理IDだけ差し替える。
Production入口(Z.run_tts_stage)をそのまま実行(故障注入は06dと同一: tstop=Secondaryのみmock障害 / dlg_cap2=減速段階の出力を別文の実音声に差替)。
有料APIは --execute 指定時のみ。各partは1回のみ実行(再起動・監督ループ・自動再試行なし)。
使い方: .venv\\Scripts\\python.exe er078_auw_runtime_evidence_06e.py <tstop|kp4|dlg_cap2> [--execute --budget-jpy N]
"""
from __future__ import annotations

import argparse
import json
import os

import er078_auw_runtime_evidence_06 as e6
import er078_auw_runtime_evidence_06b as b
import er078_auw_runtime_evidence_06d as m
import er078_auw_runtime_evidence_06d_z as zz

EV = "er058_output/unified_all_roles_production_wiring_01/evidence_06e"
m.EV = EV
b.EV = EV
b.LEDGER = f"{EV}/cost/spend_ledger.jsonl"
b.CAP_JPY = 10.0
if "AUW-06E" not in e6.MANAGED_IDS:
    e6.MANAGED_IDS.append("AUW-06E")


def _lock(path):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None


def _kp4_post(res, out, run_dir):
    res["attempt_history_rows"] = m.table_from_attempt_history("kp4")
    res["review_lock_state"] = _lock(f"{run_dir}/a2/audit/review_lock_state.json")
    res["hr_queue_lines"] = m._line_count(f"{out}/human_review_queue.jsonl")
    p = f"{run_dir}/a2/audit/tts_generation_results.json"
    d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    ent = ((d.get("key_phrases") or {}).get("1") or {}).get("english") or {}
    res["kp_entry"] = {k: ent.get(k) for k in ("status", "reason", "tts_generations_used")}
    res["kp_entry"]["n_attempts"] = len(ent.get("attempts") or [])
    res["kp_entry"]["attempt_instruction_labels"] = [a.get("instruction_label") for a in (ent.get("attempts") or [])]
    aj = ent.get("asr_judgement") or {}
    res["kp_entry"]["asr_judgement_state"] = aj.get("state")
    res["kp_entry"]["asr_judgement_slot"] = aj.get("slot")


def run_kp4(execute, budget):
    Z = zz._z_prep()
    plan = [Z.ClipSpec("kp1_en", "a2", "kp_en", zz.KP4_TEXT, voice="Aoede", role_key="KP_EN", rank=1, language="en")]
    zz._run_z("kp4", "a2", plan, execute, budget, None, _kp4_post)


def _dlg_post(res, out, run_dir):
    zz._dlg_post("dlg_cap2")(res, out, run_dir)
    res["review_lock_state"] = _lock(f"{run_dir}/a2/audit/review_lock_state.json")
    res["hr_queue_lines"] = m._line_count(f"{out}/human_review_queue.jsonl")
    p = f"{run_dir}/a2/audit/tts_generation_results.json"
    d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    e = (d.get("segments") or {}).get("full_story_part1_c2") or {}
    res["dialogue_entry"]["asr_judgement_state"] = (e.get("asr_judgement") or {}).get("state")
    res["dialogue_entry"]["asr_judgement_none"] = e.get("asr_judgement") is None


def run_dlg_cap2(execute, budget):
    zz._run_z("dlg_cap2", "a2", zz._dlg_plan(zz._z_prep()), execute, budget, zz._dlg_patch({1, 2, 3}, zz.DLG_DECOY2), _dlg_post)


def _ts_post(res, out, run_dir):
    zz._ts_post(res, out, run_dir)
    p = f"{run_dir}/b1b/audit/tts_generation_results.json"
    res["results_json_exists"] = os.path.exists(p)
    ev = f"{run_dir}/b1b/audit/runtime_evidence_04C.json"
    res["evidence_json_exists"] = os.path.exists(ev)


def run_tstop(execute, budget):
    Z = zz._z_prep()
    plan = [Z.ClipSpec(f"comment_{i + 1}", "b1b", "comment", t, voice="Charon", role_key="ADV_EN_COMMENT", language="en")
            for i, t in enumerate(zz.TS_TEXTS)]
    zz._run_z("tstop", "b1b", plan, execute, budget, zz._ts_patch, _ts_post)


PARTS = {"tstop": run_tstop, "kp4": run_kp4, "dlg_cap2": run_dlg_cap2}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=sorted(PARTS))
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--budget-jpy", type=float, default=0.0)
    a = ap.parse_args()
    os.chdir(e6.ROOT)
    PARTS[a.part](a.execute, a.budget_jpy)


if __name__ == "__main__":
    main()
