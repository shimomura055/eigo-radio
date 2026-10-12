# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01: Std Comment 4 をProduction Prompt定数
(plan.FAMILY_X_A2_COMMENT_4_ROLE、Trial-03採用版)で1回だけ文章再生成する。
Production runnerのrun_family_x_a2_scaffold()内のComment 4の1 callと同一の呼び出し
(a2gen.run_support_text + _a2_support_model() + 同一c4_context)。Preview/Comment1-3はv4原稿のまま変更しない
(scaffold全体を再実行するとv4原稿が変わるため、Comment 4のみを実行する)。LLM 1 call。再実行しない。"""
import os, sys, json
sys.path.insert(0, os.getcwd())
import er005_cost_logger as cl
import er019_family_x_audio_production_runner_01 as runner
import er019_family_x_audio_plan_01 as plan
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_en_direct_vfl_01_generate as vfl01

OUT = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_v5_ms_01"
a2 = f"{OUT}/a2"
sup_path = f"{a2}/a2_support_texts.json"
orig_path = f"{OUT}/audit/a2_support_texts_v4_original.json"
assert not os.path.exists(f"{a2}/audit/a2_comment4_regeneration.json"), "already regenerated; do not rerun"
parts = runner.load_json(f"{a2}/parts.json")
sup = runner.load_json(sup_path)
os.makedirs(f"{a2}/audit", exist_ok=True)
runner.save_json(orig_path, sup)
cl.install(f"{OUT}/raw_usage_log.jsonl")
client = vfl01.get_client()
c4_context = f"【本文1】\n{parts['part1']}\n\n【本文2】\n{parts['part2']}\n\n【本文3】\n{parts['part3']}"
with cl.logging_context("coffee_prices", "scaffold"):
    c4 = a2gen.run_support_text(client, plan.FAMILY_X_A2_COMMENT_4_ROLE, c4_context, model=runner._a2_support_model())
runner.save_json(f"{a2}/audit/a2_comment4_regeneration.json", {
    "prompt_const": "er019_family_x_audio_plan_01.FAMILY_X_A2_COMMENT_4_ROLE", "model": runner._a2_support_model(),
    "v4_comment_4": sup["comment_4"], "result": c4})
print(json.dumps(c4, ensure_ascii=False, indent=1))
