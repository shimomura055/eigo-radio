# ============================================================
# er064_kp_noway_01_run.py  (FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01、Trial専用・Production非接続)
# 委任_01(JPY0)では --mode prep のみ実行する(LLM呼出なし)。--mode run は有料runであり、委任_02以降でFable/ユーザーが費用上限を確認したあとだけ使う。
#   run の安全装置: 環境変数 KP_NOWAY_PAID_RUN_AUTHORIZED に数値(JPYの総額上限)が入っていること、かつ --budget-cap-jpy がそれ以下であること。
#   STOP/STOP_ALL/KP用STOP_NOTICEが存在すれば起動しない。監督ループ・自動retry・別名ラッパなし。1回だけ手動起動、外部停止後の再起動禁止。
# 選定/gate/canonicalization/Redundancy QAは既存Production関数を呼ぶ(er064_kp_int_01_run.job経由)。candidate shortlistはM2(Round1/2と同一)。
# 差分はPromptの1段落(er064_kp_noway_01_prompts.ADDED_PARAGRAPH)のみ。
# 使い方: PYTHONPATH=. PYTHONUTF8=1 .venv/Scripts/python.exe er064_kp_noway_01_run.py --mode prep
# ============================================================
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import er064_kp_int_01_machine as MC  # noqa: E402
import er064_kp_int_01_run as RUN  # noqa: E402
import er064_kp_noway_01_prompts as NP  # noqa: E402
import er064_kp_opt_01_phase2_run_03 as R  # noqa: E402
import er030_key_phrase_db_hybrid_source_reference_contract_01 as src_ref  # noqa: E402

OUT = "er064_output/kp_no_way_fix_01"
COMBO = "M2P0X"
# 実行計画(plan_01.mdに事前登録): (article, level, n)
STAGE_PLAN = {1: [("meta", "adv", 5)],
              2: [("coffee", "std", 3), ("coffee", "adv", 3), ("meta", "std", 3), ("hormuz", "std", 3), ("hormuz", "adv", 3)]}
PLAN = STAGE_PLAN[1] + STAGE_PLAN[2]
EST_PER_JOB = {"central": 0.95, "conservative": 1.185}  # 出典: cost_01.json (Round1/2実績) と委任文の保守値


def stop_present():
    return (glob.glob(f"{OUT}/STOP") + glob.glob("er026_output/family_z_production_e2e_01/STOP_ALL")
            + glob.glob("docs/pm/delegation_log/*STOP_NOTICE*KP-NO-WAY*") + glob.glob("docs/pm/delegation_log/*STOP_NOTICE*KP-INTEGRATED*"))


def authorized_cap():
    v = os.environ.get("KP_NOWAY_PAID_RUN_AUTHORIZED", "").strip()
    try:
        return float(v)
    except ValueError:
        return None


def build_ctx_x(article, levels):
    """(article, level, 'M2P0X') -> job context。RUN.build_ctxと同形。msgだけP0Xを使う。有料呼出なし。"""
    ctx = {}
    from er064_kp_opt_01_upstream_core import read_article
    for lv in levels:
        key = f"{article}_{lv}"
        b = MC.build_pattern(key, "M2")
        ids = src_ref.assign_candidate_ids(b["shortlist"])
        corr = src_ref.correct_shortlist_source_span_consistency(ids["shortlist_with_ids"], b["sentence_reference"])
        assert not corr["excluded"], f"span consistency除外あり {key}: {corr['excluded']}"
        msg = NP.render_p0x(R.cand_block(b["rows_text"]))
        ctx[(article, lv, COMBO)] = {"article_text": read_article(key), "msg": msg, "id2c": corr["id_to_candidate"], "cids": corr["candidate_ids"],
                                     "sentence_reference": b["sentence_reference"], "rows_sha256": NP.sha(b["rows_text"]),
                                     "n_candidates": len(b["shortlist"]), "prompt_sha256": NP.sha(msg)}
    return ctx


def all_specs(stage=None):
    plan = PLAN if stage is None else STAGE_PLAN[stage]
    return [(a, lv, COMBO, k) for (a, lv, n) in plan for k in range(1, n + 1)]


def prep():
    os.makedirs(OUT, exist_ok=True)
    assert not stop_present(), stop_present()
    ctx = {}
    for a, lv, _n in PLAN:
        ctx.update(build_ctx_x(a, (lv,)))
    specs = all_specs()
    ctl = {}
    for (a, lv, _c), c in ctx.items():
        fs = sorted(glob.glob(f"er064_output/kp_integrated_opt_01/round1/runs/{a}_{lv}_M2P0_run*/job_result.json"))
        rows = {json.load(open(f, encoding="utf-8"))["rows_sha256"] for f in fs}
        ctl[f"{a}_{lv}"] = {"n_control_runs_existing": len(fs), "rows_sha256_identical_to_control": rows == {c["rows_sha256"]}}
    out = {"mode": "prep", "llm_calls": 0, "n_jobs": len(specs), "plan": [{"article": a, "level": lv, "n": n} for (a, lv, n) in PLAN],
           "est_cost_jpy": {k: round(v * len(specs), 2) for k, v in EST_PER_JOB.items()},
           "cells": {f"{a}_{lv}": {"prompt_sha256": c["prompt_sha256"], "rows_sha256": c["rows_sha256"], "n_candidates": c["n_candidates"]}
                     for (a, lv, _c), c in ctx.items()},
           "control_reuse": ctl}
    json.dump(out, open(f"{OUT}/prep_run_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"n_jobs": out["n_jobs"], "est": out["est_cost_jpy"], "control_reuse": ctl}, ensure_ascii=False, indent=1))


def run(budget_cap, stage):
    cap = authorized_cap()
    if cap is None or budget_cap is None or budget_cap > cap:
        sys.exit("有料runは未承認: KP_NOWAY_PAID_RUN_AUTHORIZED(JPY上限)の設定と、それ以下の--budget-cap-jpyが必要。委任_01では実行しない。")
    if stop_present():
        sys.exit(f"STOP present {stop_present()}")
    ctx = {}
    for a, lv, _n in STAGE_PLAN[stage]:
        ctx.update(build_ctx_x(a, (lv,)))
    specs = all_specs(stage)
    est = round(EST_PER_JOB["conservative"] * len(specs), 3)
    if est > budget_cap:
        sys.exit(f"budget guard: conservative est {est} > cap {budget_cap}")
    # RUN.job をこの出力先・この費用上限で使う(Round1の成果物・cost_r1.jsonには触れない)
    RUN.OUT = OUT
    RUN.COST_PATH = f"{OUT}/cost_run_02.json"
    RUN.HARD_STOP = budget_cap
    RUN.stop_present = stop_present
    RUN.COMBOS[COMBO] = ("M2", "P0X")
    os.makedirs(f"{OUT}/runs", exist_ok=True)
    res, err = [], []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(RUN.job, s, ctx): s for s in specs}
        for f in cf.as_completed(futs):
            try:
                res.append(f.result())
            except Exception as e:  # 失敗は記録のみ。再起動・自動retryはしない
                err.append({"job": list(futs[f]), "error": f"{type(e).__name__}: {e}"})
    json.dump({"stage": stage, "runs": res, "errors": err, "cumulative_jpy": RUN.spent()}, open(f"{OUT}/run_summary_02_stage{stage}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("errors", err, "cum", RUN.spent())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["prep", "run"])
    ap.add_argument("--budget-cap-jpy", type=float, default=None)
    ap.add_argument("--stage", type=int, choices=[1, 2], default=None)
    a = ap.parse_args()
    if a.mode == "prep":
        prep()
    else:
        if a.stage is None:
            sys.exit("--stage 1|2 が必要(Stage1=meta_adv n=5、Stage2=回帰15 job。Stage2はStage1のGo判定後のみ)")
        run(a.budget_cap_jpy, a.stage)
