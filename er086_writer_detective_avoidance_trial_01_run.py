# -*- coding: utf-8 -*-
"""FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01 Trial実行(Pattern A/B/Cのいずれか1つ)。

Production runner(er019_family_x_entertainment_production_runner_01.py)は**起動しない**(Risk Flaggerが共有
review_queue/へ書込むため。本Trialは本文生成のみが対象)。代わりに同runnerが呼ぶ同一のProduction関数を
そのまま呼ぶ: w1.run_w1_writer(R0->R1->R2) / efam.run_writer_stage(advanced -> standard)。
入力はrun_mey_02の research_ledger/ と storyline_b3/ のコピー(sha一致を記録)。TTS/Assembly/web_searchは呼ばない。
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import shutil
import sys
import time

import er086_writer_detective_avoidance_trial_01_lib as lib


def file_shas(root: str) -> dict:
    out = {}
    for dp, _dn, fn in os.walk(root):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            out[os.path.relpath(p, root).replace("\\", "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", required=True, choices=sorted(lib.PATTERN_TEXT))
    ap.add_argument("--source-run", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--budget-jpy", type=float, default=40.0)
    ap.add_argument("--theme", default="中東情勢が悪化、イエメン・サウジ周辺で攻撃続く")
    ap.add_argument("--slug", default="middle_east_yemen_saudi")
    ap.add_argument("--dry-prompts-only", action="store_true", help="APIを呼ばずPrompt組立だけ確認(test用)")
    a = ap.parse_args()

    import er005_cost_logger as cl
    import er012_e_family_entertainment_two_level_runner_01 as efam
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er053_family_x_factlock_ja_writer_01 as w1
    import er053_cost_aggregate_01 as ca

    out, src = a.out_dir, a.source_run
    os.makedirs(out, exist_ok=True)
    if os.path.exists(f"{out}/ja_writer") or os.path.exists(f"{out}/b1b/article.md"):
        raise SystemExit("[STOP] out-dirに既に生成物があります(再実行・上書き禁止。再現確認は別out-dirで)。")
    # 入力コピー(Research/Ledger/B3の再実行はしない)
    for sub in ("research_ledger", "storyline_b3"):
        shutil.copytree(f"{src}/{sub}", f"{out}/{sub}")
    in_shas = {sub: {"source": file_shas(f"{src}/{sub}"), "copy": file_shas(f"{out}/{sub}")} for sub in ("research_ledger", "storyline_b3")}
    sha_match = all(v["source"] == v["copy"] for v in in_shas.values())
    lib.write_json(f"{out}/input_copy_evidence.json", {"sha_match": sha_match, "files": in_shas})
    if not sha_match:
        raise SystemExit("[STOP] 入力コピーのsha不一致")

    cl.install(f"{out}/raw_usage_log.jsonl")
    ledger_text = lib.read_text(f"{out}/research_ledger/verified_fact_ledger.txt")
    theme = {"theme_id": a.slug, "topic": a.theme, "out_dir": out,
             "ledger_path": f"{out}/research_ledger/verified_fact_ledger.txt"}
    dumper = lib.PromptDumper(f"{out}/prompt_dump", a.pattern)
    t_start = time.time()
    timings = {"started": datetime.datetime.now().isoformat(timespec="seconds")}
    client = vfl01.get_client()
    summary = {"trial_id": lib.TRIAL_ID, "pattern": a.pattern, "pattern_text": lib.PATTERN_TEXT[a.pattern],
               "pattern_text_sha256": lib.sha256_text(lib.PATTERN_TEXT[a.pattern]), "out_dir": out,
               "budget_jpy": a.budget_jpy, "rf_run": False, "rf_skip_reason": "RFは共有review_queue/へ書込むため本Trialでは実行しない(本文は変更しない検査系)"}
    prod_before = {"USER_TMPL": w1.USER_TMPL}
    try:
        with lib.injected(a.pattern, dumper):
            if a.dry_prompts_only:
                return
            # Writer R0 -> R1 -> R2 (Production W-1そのまま)
            t0 = time.time()
            with cl.logging_context("DWA_TRIAL_01", "writer"):
                res = w1.run_w1_writer(out, client=client,
                                       budget_check=lambda: efam.assert_budget_ok(out, a.budget_jpy, "dwa w1 writer"))
            ja_text = res["ja_text"]
            timings["writer_sec"] = round(time.time() - t0, 1)
            efam.assert_budget_ok(out, a.budget_jpy, "dwa after ja_writer")
            # Advanced
            t0 = time.time()
            with cl.logging_context("DWA_TRIAL_01", "advanced"):
                efam.run_writer_stage(client, theme, ja_text, ledger_text, a.budget_jpy, only="advanced")
            timings["advanced_sec"] = round(time.time() - t0, 1)
            # Standard
            t0 = time.time()
            with cl.logging_context("DWA_TRIAL_01", "standard"):
                efam.run_writer_stage(client, theme, ja_text, ledger_text, a.budget_jpy, only="standard")
            timings["standard_sec"] = round(time.time() - t0, 1)
    finally:
        timings["total_sec"] = round(time.time() - t_start, 1)
        timings["ended"] = datetime.datetime.now().isoformat(timespec="seconds")
        summary["timings"] = timings
        summary["prompt_dump"] = dumper.records
        summary["production_restored"] = {"USER_TMPL": w1.USER_TMPL == prod_before["USER_TMPL"]}
        bd = ca.compute_stage_cost_breakdown_multi(f"{out}/raw_usage_log.jsonl")
        summary["cost"] = bd
        lib.write_json(f"{out}/trial_run_summary.json", summary)
        lib.write_json(f"{out}/cost.json", bd)
    print(f"[DWA] pattern={a.pattern} done total_jpy={bd.get('total_jpy')} sec={timings['total_sec']}")


if __name__ == "__main__":
    sys.exit(main())
