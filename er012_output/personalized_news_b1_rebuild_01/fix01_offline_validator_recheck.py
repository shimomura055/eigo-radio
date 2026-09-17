# ============================================================
# er012_output/personalized_news_b1_rebuild_01/fix01_offline_validator_recheck.py
# 管理ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01-FIX-01
# ============================================================
# 目的: ユーザー試聴Feedbackで修正した記事(r8_attempt1/article.md、Hook代名詞
# he/Voice A heading his/Voice A本文の一文削除)に対し、Writerを再生成せず、
# 既存Validator(Analytical Leakage Check 2V・Ledger Deviation Checker)を
# そのままoffline再実行して整合を確認する。er012_b_family_voices_writer_
# generic_01.run_analytical_leakage_check_2v()とer003_v1_en_direct_vfl_01_
# generate.run_deviation_check()を直接呼ぶだけで、Local Rewrite loop
# (run_ledger_deviation_and_local_rewrite)は使わない(MAJOR 0件が想定どおり
# 出た場合はLocal Rewrite自体が発火しないためロジック上安全だが、Writer
# 再生成しないという指示を明確に守るため、あえてより薄い直接呼び出しにする)。
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er012_b_family_voices_production_01 as b1prod
import er012_b_family_voices_writer_generic_01 as writer_generic
import er006_model_routing_contract_01 as routing
import er005_cost_logger as cl

BASE_DIR = "er012_output/personalized_news_b1_rebuild_01"
ARTICLE_PATH = f"{BASE_DIR}/b1_2v_new_theme_r8_attempt1/article.md"
LEDGER_PATH = f"{BASE_DIR}/research/verified_fact_ledger.txt"
OUT_DIR = f"{BASE_DIR}/b1_2v_new_theme_r8_attempt1/fix01_recheck"
LABEL = "B1B"  # run_writer_stage_generic()の既定label(r8実行時と同一)。
# gen._writer_process("B1B") == "B1_WRITER"(r8実行時と同一process key)。


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log_fix01_recheck.jsonl")

    with open(ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()
    with open(LEDGER_PATH, encoding="utf-8") as f:
        ledger_text = f.read()

    sections = b1prod.split_five_voice_sections(article_text)
    if sections is None:
        raise RuntimeError("5区切り構造の検出に失敗しました(FIX-01の編集で構造を壊していないか確認してください)")

    from openai import OpenAI
    client = OpenAI()

    writer_model = routing.require_model(gen._writer_process(LABEL), routing.WRITER_MODEL)
    reasoning_effort = gen.REASONING_EFFORT  # = vfl01.REASONING_EFFORT = r3.WRITER_REASONING_EFFORT = "high"(コード定数確認済み)

    print(f"[FIX-01-RECHECK] Analytical Leakage Check 2V再実行(model={writer_model}, effort={reasoning_effort})...")
    leakage = writer_generic.run_analytical_leakage_check_2v(
        client, sections, writer_model, reasoning_effort, OUT_DIR, attempt="fix01")

    print(f"[FIX-01-RECHECK] Ledger Deviation Checker再実行(vfl01.run_deviation_check、hook_aware=True、"
          f"Local Rewrite loopは使用しない直接呼び出し)...")
    deviation = vfl01.run_deviation_check(client, ledger_text, article_text, model=writer_model, hook_aware=True)

    with open(f"{OUT_DIR}/ledger_deviation_fix01_recheck.json", "w", encoding="utf-8") as f:
        json.dump(deviation["parsed"], f, ensure_ascii=False, indent=2)

    summary = {
        "analytical_leakage_check_any_flagged": leakage["any_flagged"],
        "analytical_leakage_check_flagged_items": leakage["flagged_items"],
        "ledger_deviation_overall_status": deviation["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation["parsed"]["deviations"]),
        "ledger_deviation_major_count": sum(
            1 for d in deviation["parsed"]["deviations"] if d.get("severity") == "MAJOR"),
    }
    with open(f"{OUT_DIR}/fix01_recheck_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"[FIX-01-RECHECK] DONE summary={summary}")


if __name__ == "__main__":
    main()
