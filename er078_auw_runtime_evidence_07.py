# -*- coding: utf-8 -*-
"""AUW 委任_07: 06e申し送り(d) narrator A2外側ループ(generate_a2_segment_with_slowdown)の通算3回目減速後NG -> HR末端の実音声1件。
計測・隔離・累計ledgerは 06b/06d/06d_z/06e を再利用し、証跡先(evidence_07)・上限(JPY 5)だけ差し替える。
Production入口(Z.run_tts_stage、kind=narrator)をそのまま実行。故障注入は06dのdlg_cap2と同一方式(減速段階の出力を別文の実音声に差替)。
有料APIは --execute 指定時のみ。1回のみ実行(再起動・監督ループ・自動再試行なし)。
使い方: .venv\Scripts\python.exe er078_auw_runtime_evidence_07.py narr_cap3 [--execute --budget-jpy N]
"""
from __future__ import annotations

import argparse
import json
import os

import er078_auw_runtime_evidence_06 as e6
import er078_auw_runtime_evidence_06b as b
import er078_auw_runtime_evidence_06d as m
import er078_auw_runtime_evidence_06d_z as zz
import er078_auw_runtime_evidence_06e as e6e

EV = "er058_output/unified_all_roles_production_wiring_01/evidence_07"
m.EV = EV
b.EV = EV
b.LEDGER = f"{EV}/cost/spend_ledger.jsonl"
b.CAP_JPY = 5.0
if "AUW-07" not in e6.MANAGED_IDS:
    e6.MANAGED_IDS.append("AUW-07")

NARR_TEXT = "I did not see a lower price today."
CLIP = "full_story_part1_c3"


def _narr_post(res, out, run_dir):
    res["attempt_history_rows"] = m.table_from_attempt_history("narr_cap3")
    res["review_lock_state"] = e6e._lock(f"{run_dir}/a2/audit/review_lock_state.json")
    res["hr_queue_lines"] = m._line_count(f"{out}/human_review_queue.jsonl")
    p = f"{run_dir}/a2/audit/tts_generation_results.json"
    d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    e = (d.get("segments") or {}).get(CLIP) or {}
    res["narrator_entry"] = {k: e.get(k) for k in ("status", "tts_generations_used", "tts_generation_cap_reached", "slowdown_attempts_log", "reason",
                                                    "post_slowdown_classification", "slowdown_applied", "asr_verified", "clip_kind")}
    aj = e.get("asr_judgement") or {}
    res["narrator_entry"]["asr_judgement_state"] = aj.get("state")
    res["narrator_entry"]["asr_judgement_pre_slowdown_present"] = e.get("asr_judgement_pre_slowdown") is not None


def run_narr_cap3(execute, budget):
    Z = zz._z_prep()
    plan = [Z.ClipSpec(CLIP, "a2", "narrator", NARR_TEXT, voice="Aoede", speaker="narrator", role_key="NARRATOR_FULL_STORY_STD", part=1, language="en")]
    zz._run_z("narr_cap3", "a2", plan, execute, budget, zz._dlg_patch({1, 2, 3}, zz.DLG_DECOY2), _narr_post)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=["narr_cap3"])
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--budget-jpy", type=float, default=0.0)
    a = ap.parse_args()
    os.chdir(e6.ROOT)
    run_narr_cap3(a.execute, a.budget_jpy)


if __name__ == "__main__":
    main()
