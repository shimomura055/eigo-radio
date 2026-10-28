# -*- coding: utf-8 -*-
"""M-4 初回経路のruntime evidence: 実在のProduction関数 run_family_x_a2_scaffold をscratch out_dirで1回だけ実API実行する(LLM 5回想定)。
公開物には使わない。AI島のpartsを入力にする(overlay前の素のparts)。"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import er005_cost_logger as cl
import er019_family_x_audio_production_runner_01 as runner
import er003_v1_en_direct_vfl_01_generate as vfl01

OUT = "docs/research/FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01/evidence_first_path"
PARTS = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/a2/parts.json"
os.makedirs(OUT, exist_ok=True)
cl.install(f"{OUT}/raw_usage_log.jsonl")
client = vfl01.get_client()
parts = json.load(open(PARTS, encoding="utf-8"))
with cl.logging_context("ai_island_temple", "evidence_first_path"):
    res = runner.run_family_x_a2_scaffold(client, parts, OUT)
summary = {k: {"status": v.get("status"), "text": v.get("text"),
               "response_id": [a.get("response_id") for a in v.get("attempts", []) if a.get("status") == "OK"],
               "model": [a.get("model") for a in v.get("attempts", []) if a.get("status") == "OK"]} for k, v in res.items()}
json.dump(summary, open(f"{OUT}/first_path_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
c3 = res["comment_3"]
json.dump({"prompt": c3.get("prompt"), "comment3_z_audit": c3.get("comment3_z_audit"), "status": c3.get("status"), "text": c3.get("text")},
          open(f"{OUT}/first_path_comment3_prompt_audit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE", {k: v["status"] for k, v in summary.items()})
print("C3:", c3.get("text"))
