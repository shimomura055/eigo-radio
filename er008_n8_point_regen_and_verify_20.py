# -*- coding: utf-8 -*-
# ============================================================
# er008_n8_point_regen_and_verify_20.py
# ER-008-N8-FINAL-AUDIO-AND-REMAINING-PRODUCTION-WIRING-20
# ============================================================
# No.8(pool_n8_airport_line)の既存article.mdに対して、記事全体を
# 再生成せずPoint-only regeneration(er008_point_regenerate_19)だけを
# 実データへ適用する薄いスクリプト(er008_n8_factcheck_recheck_01.py/
# er008_n8_deviation_recheck_01.pyと同じ「記事全体の再生成はしない」
# 方針)。run_one_pattern()はWriter呼び出しから全部やり直してしまう
# ため使わず、run_point_overlap_qa_and_regenerate()を直接呼び出した
# うえで、差し替えが発生した場合のみFact Checker/Ledger Deviation
# Checkを再実行する(既存の安全確認プロセスは省略しない)。
from __future__ import annotations

import json
import os
import shutil
import time

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er006_model_routing_contract_01 as routing

OUT_DIR = "er006_output/pool_pilot_01/pool_n8_airport_line"
TITLE_EN = "The Airport Line That Starts Before It Needs To"

LEVELS = [("a2", "A2"), ("b1b", "B1B")]


def backup(path: str):
    if os.path.exists(path):
        shutil.copy(path, path + ".pre_point_regen_20.bak")


def rerun_fact_checker(level: str, article_text: str) -> dict:
    fc_prompt = r3.build_fact_check_prompt(TITLE_EN, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[N8-POINT-REGEN-20][{level}] fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": "B1B" if level == "b1b" else "A2", "final_status": fc_status, "model": fc_model,
        "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": fc_attempts, "result": fc_result,
    }
    with open(f"{OUT_DIR}/{level}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2, default=str)
    return {"status": fc_status, "verdict": verdict}


def rerun_deviation_check(client, level: str, article_text: str, ledger_text: str, label: str) -> dict:
    model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)
    result = vfl01.run_deviation_check(client, ledger_text, article_text, model=model)
    parsed = result["parsed"]
    print(f"[N8-POINT-REGEN-20][{level}] deviation overall_status={parsed['overall_status']} "
          f"deviations={len(parsed['deviations'])}")
    with open(f"{OUT_DIR}/{level}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)
    return {"overall_status": parsed["overall_status"], "deviation_count": len(parsed["deviations"])}


def main():
    client = gen.vfl01.get_client()
    ledger_text = gen.load_text(f"{OUT_DIR}/research/verified_fact_ledger.txt")

    summary = {}
    for subdir, label in LEVELS:
        level_out_dir = f"{OUT_DIR}/{subdir}"
        article_path = f"{level_out_dir}/article.md"
        article_text = gen.load_text(article_path)

        print(f"[N8-POINT-REGEN-20] {label}: Point-Full Story重複QA開始...")
        result = gen.run_point_overlap_qa_and_regenerate(
            client, article_text, ledger_text,
            model=routing.require_model(gen._writer_process(label), routing.WRITER_MODEL),
            reasoning_effort=gen.REASONING_EFFORT, out_dir=level_out_dir)

        entry = {"point_qa_status": result["status"], "report": result.get("report"), "applied_keys": []}

        if result["status"] == "OK" and result["patched_article_text"] != article_text:
            backup(article_path)
            new_article_text = result["patched_article_text"]
            with open(article_path, "w", encoding="utf-8") as f:
                f.write(new_article_text)

            parts_path = f"{level_out_dir}/parts.json"
            backup(parts_path)
            with open(parts_path, encoding="utf-8") as f:
                parts = json.load(f)
            for key in ("point_one", "point_two"):
                if result["report"].get(key, {}).get("applied"):
                    parts[f"{key}_body"] = result["report"][key]["new_text"]
                    entry["applied_keys"].append(key)
            with open(parts_path, "w", encoding="utf-8") as f:
                json.dump(parts, f, ensure_ascii=False, indent=2)

            print(f"[N8-POINT-REGEN-20] {label}: 差し替え発生(applied_keys={entry['applied_keys']})。"
                  f"Fact Checker/Ledger Deviation Check再実行...")
            entry["fact_check_rerun"] = rerun_fact_checker(subdir, new_article_text)
            entry["deviation_rerun"] = rerun_deviation_check(client, subdir, new_article_text, ledger_text, label)
        else:
            print(f"[N8-POINT-REGEN-20] {label}: 差し替えなし(status={result['status']})。")

        summary[label] = entry

    with open(f"{OUT_DIR}/point_regen_20_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[N8-POINT-REGEN-20] 完了。")


if __name__ == "__main__":
    main()
