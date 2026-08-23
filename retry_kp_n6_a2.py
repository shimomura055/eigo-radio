# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/raw_usage_log.jsonl")

import er003_v1_n3_01_scaffold_generate as sc

theme_id = "pool_n6_delivery"
out_dir = f"er006_output/pool_pilot_01/{theme_id}/a2"
article_text = open(f"{out_dir}/article.md", encoding="utf-8").read()
article_id = f"ER006_{theme_id}_a2"

with cl.logging_context(theme_id, "key_phrase_a2_retry"):
    kp = sc.run_key_phrases(article_text, f"{out_dir}/key_phrases", article_id, "A2", process="A2_SUPPORT")

print("selection status:", kp["selection"]["status"])
print("canonicalization present:", kp["canonicalization"] is not None)
if kp["canonicalization"]:
    print("overall_status:", kp["canonicalization"].get("overall_status"))
