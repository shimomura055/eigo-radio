# ============================================================
# er011_no18_open108_b1_support_regenerate_01.py
# ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02 / Track A
# ============================================================
# er011_no18_open108_b1_ledger_refined_regenerate_01.pyでB1B記事本文(article.md)
# をLedger精密化後の内容へ更新したが、Support(Preview/Comment1-4)とKey Phraseは
# gen.run_one_pattern()のスコープ外(er006_pool_pilot_01_support.run_support_
# for_theme()が別途担当)のため、旧article.md(Fact Checker FAIL版、"hard-to-resist
# habit"等を含む)を元にした古い内容のまま残っていた。本scriptは、実Production関数
# (er006_pool_pilot_01_support.sc.run_b1_scaffold/sc.run_key_phrases/
# support_mod.run_support_fact_check、いずれも無変更)をb1bのみに対して呼び出し、
# 新しいarticle.mdからSupport・Key Phraseを再生成する。A2は既にPASS済みのため
# 対象に含めない(無駄なコスト・変更リスクを避ける)。

from __future__ import annotations

import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_pool_pilot_01_support as support_mod
import er011_no18_specfix_v2_production_run_01 as driver

sc = support_mod.sc

THEME_ID = driver.THEME_ID
OUT_DIR = driver.OUT_DIR
LABEL = "b1b"
SOURCE_LEVEL = "B1-B(N3-01, direct generation)"

cl.install(f"{OUT_DIR}/raw_usage_log_open108_support.jsonl")

client = vfl01.get_client()
ledger_text = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()

level_out_dir = f"{OUT_DIR}/{LABEL}"
os.makedirs(f"{level_out_dir}/audit", exist_ok=True)
with open(f"{level_out_dir}/article.md", encoding="utf-8") as f:
    article_text = f.read()
parts = sc.split_article_text(article_text)
with open(f"{level_out_dir}/parts.json", "w", encoding="utf-8") as f:
    json.dump(parts, f, ensure_ascii=False, indent=2)

t0 = time.time()
with cl.logging_context(THEME_ID, "support_b1_open108_regenerate"):
    support = sc.run_b1_scaffold(client, parts, level_out_dir, article_text)

    kp_dir = f"{level_out_dir}/key_phrases"
    article_id = f"ER006_{THEME_ID}_{LABEL}"
    kp = sc.run_key_phrases(article_text, kp_dir, article_id, SOURCE_LEVEL, process="B1_SUPPORT")
    kp_status = (kp["canonicalization"] or {}).get("status") if kp["canonicalization"] else kp["selection"]["status"]
    kp_redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
    if kp.get("status") == "NG_REVIEW_REQUIRED":
        kp_status = "NG_REVIEW_REQUIRED"

    fc = support_mod.run_support_fact_check(client, support, article_text, ledger_text)
elapsed = round(time.time() - t0, 2)

with open(f"{level_out_dir}/support_fact_check.json", "w", encoding="utf-8") as f:
    json.dump(fc, f, ensure_ascii=False, indent=2, default=str)

print(f"[{THEME_ID}] {LABEL} Support再生成完了(OPEN-108, Ledger精密化後article反映)。"
      f"support={ {k: v.get('status') for k, v in support.items()} } "
      f"kp_status={kp_status} kp_redundancy_status={kp_redundancy_status} "
      f"support_fc_verdict={fc['parsed']['verdict']} issues={len(fc['parsed']['issues'])} "
      f"elapsed={elapsed}s")

summary_path = f"{OUT_DIR}/scaffold_run_summary.json"
with open(summary_path, encoding="utf-8") as f:
    summary = json.load(f)
summary[LABEL] = {
    "parts": parts, "support_statuses": {k: v.get("status") for k, v in support.items()},
    "key_phrases_status": kp_status,
    "key_phrases_redundancy_status": kp_redundancy_status,
    "key_phrases_count": len((kp.get("canonicalization") or {}).get("merged", {}).get("items", []))
                         if kp.get("canonicalization") else 0,
    "support_fact_check_verdict": fc["parsed"]["verdict"],
    "support_fact_check_issue_count": len(fc["parsed"]["issues"]),
    "regenerated_note": "OPEN-108 Ledger精密化後のarticle.mdを元に、b1bのみSupport/Key Phraseを再生成"
                         "(A2は対象外、実Production関数を無変更のまま使用)。",
}
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
print(f"[{THEME_ID}] scaffold_run_summary.json更新完了(b1bのみ)。")
