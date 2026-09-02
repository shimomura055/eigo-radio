# ============================================================
# er011_no18_open107_b1_text_patch_requa_03.py
# ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03
# ============================================================
# ユーザー正式決定により、No.18 B1B本文(article.md / parts.json、OPEN-108
# Ledger精密化後版)のPoint One本文中、以下1文をユーザー指定文へ個別差し替え
# 済み(このscript自体は本文を書き換えない、既にhand-editで反映済み):
#   旧: "Responses were slower, and a brain-wave signal linked by the
#        researchers to staying on task became larger. They interpret this
#        pattern as automatic attention capture, not necessarily a
#        deliberate choice to check."
#   新: "Responses were slower, while a brain-wave signal associated with
#        cognitive control became larger. The researchers interpreted this
#        as a sign that staying on task required extra mental effort after
#        the notification sound."
# この個別差し替えは一般Writer仕様(gen.B1_B_DIRECT_INSTRUCTION等)への
# hardcodeではなく、記事本文ファイルへの直接編集としてのみ反映する
# (ユーザー指示§8「一般Prompt変更は禁止」)。
#
# 本scriptは、gen.run_one_pattern()のWriter生成"以降"の既存公式QA工程
# (Point Overlap QA -> Point Value QA -> metrics/length_report -> Fact
# Checker -> Ledger Deviation Check[Local Rewrite Loop込み、Hook-aware] ->
# Directional Fact Precheck)を、新規コード追加なしで既存関数をそのまま
# 呼び出す形で、この個別差し替え後のarticle_textに対して再実行する
# (gen.run_one_pattern本体の該当ロジックの移設であり、新しい判定ロジックは
# 追加しない)。Point Overlap QAはPOINT_ONLY_REGENERATION_ENABLED=False
# (既存Production設定)のため、NGでも本文を自動変更しない(検出のみ)。
#
# Fact Checker FAIL、またはLedger Deviation MAJORがLocal Rewrite Loopの
# 上限まで実行しても解消しない場合は、NG_REVIEW_REQUIREDを返しSTOPする
# (Writer再生成・Fact Checker閾値変更・PASS強制のための削除は一切行わない)。

from __future__ import annotations

import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er003_v1_spoken_first_01_r1_generate as sf1r1
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_directional_fact_precheck_08 as dfp
import er010_ledger_local_rewrite_09 as local_rewrite
import er011_key_phrase_set_redundancy_qa_01  # noqa: F401 (re-QA一覧の対象であることの明示、実呼び出しはsc経由)
import er011_no18_specfix_v2_production_run_01 as driver
import er011_point_role_value_planning_01 as point_planning

THEME_ID = driver.THEME_ID
OUT_DIR = driver.OUT_DIR
LABEL = "B1B"
LEVEL_OUT_DIR = f"{OUT_DIR}/b1b"


def run_requa_on_patched_article(client, article_text: str, verified_ledger_text: str, topic: str,
                                  out_dir: str, label: str = LABEL) -> dict:
    writer_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)
    ledger_model = writer_model

    print(f"[{THEME_ID}] {label}: 個別差し替え後Re-QA開始 - Point Overlap QA...")
    point_qa_result = gen.run_point_overlap_qa_and_regenerate(
        client, article_text, verified_ledger_text, model=writer_model,
        reasoning_effort=gen.REASONING_EFFORT, out_dir=out_dir)
    overlap_report = point_qa_result.get("report") or {}
    lexical_flagged = point_qa_result["status"] == "OK" and any(
        overlap_report.get(key, {}).get("before_overlap", {}).get("flagged")
        for key in ("point_one", "point_two"))

    sections_for_value_qa = gen.split_common_sections_for_point_qa(article_text)
    value_qa_result = None
    value_qa_flagged = False
    if sections_for_value_qa is not None:
        print(f"[{THEME_ID}] {label}: Point Value QA...")
        value_qa_result = point_planning.run_point_value_qa(
            client, sections_for_value_qa["full_story"], sections_for_value_qa["point_one_body"],
            sections_for_value_qa["point_two_body"], model=writer_model, reasoning_effort=gen.REASONING_EFFORT)
        with open(f"{out_dir}/audit/point_value_qa_requa_open107_03.json", "w", encoding="utf-8") as f:
            json.dump(value_qa_result, f, ensure_ascii=False, indent=2, default=str)
        value_qa_flagged = value_qa_result["status"] == "NG"

    still_flagged = lexical_flagged or value_qa_flagged
    if still_flagged:
        print(f"[{THEME_ID}] {label}: Point Overlap/Value QA NGのためSTOP "
              f"(lexical={lexical_flagged}, value_qa={value_qa_flagged})。本文の自動変更は行いません。")
        return {"status": "NG_REVIEW_REQUIRED", "stage": "point_overlap_or_value_qa",
                "lexical_flagged": lexical_flagged, "value_qa_flagged": value_qa_flagged,
                "overlap_report": overlap_report, "value_qa_result": value_qa_result,
                "article_text": article_text}

    metrics = gen.compute_metrics(article_text)
    section_wc = sf1r1.section_word_counts(article_text)
    length_report = {
        **section_wc, "total": metrics["word_count"],
        "point_one_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_one"] <= gen.POINT_TARGET_UPPER,
        "point_one_within_tolerance":
            gen.POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= gen.POINT_TOLERANCE_UPPER,
        "point_two_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_two"] <= gen.POINT_TARGET_UPPER,
        "point_two_within_tolerance":
            gen.POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= gen.POINT_TOLERANCE_UPPER,
        "total_within_soft_range": gen.TOTAL_SOFT_LOWER <= metrics["word_count"] <= gen.TOTAL_SOFT_UPPER,
    }
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] {label}: metrics={metrics} sections={section_wc}")

    print(f"[{THEME_ID}] {label}: Fact Checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[{THEME_ID}] {label}: fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    if verdict == "FAIL":
        print(f"[{THEME_ID}] {label}: Fact Checker FAIL。STOPし、これ以降(Ledger逸脱チェック等)は実行しません。")
        return {"status": "NG_REVIEW_REQUIRED", "stage": "fact_checker", "fact_status": fc_status,
                "fact_verdict": verdict, "fact_check_result": fc_result, "article_text": article_text}

    print(f"[{THEME_ID}] {label}: Ledger逸脱チェック開始(Hook-aware)...")
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
    print(f"[{THEME_ID}] {label}: deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")

    local_rewrite_results = []
    local_rewrite_cycles = []
    cycle = 0
    previously_seen_claims = set()

    def _run_check_window(window_text: str) -> dict:
        r = vfl01.run_deviation_check(client, verified_ledger_text, window_text, model=ledger_model, hook_aware=True)
        return r["parsed"]

    major_items = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]

    while major_items and cycle < local_rewrite.MAX_REWRITE_CYCLES:
        cycle += 1
        newly_discovered_claims = [d["claim_in_article"] for d in major_items
                                    if d["claim_in_article"] not in previously_seen_claims]
        print(f"[{THEME_ID}] {label}: Local Rewrite cycle {cycle}/{local_rewrite.MAX_REWRITE_CYCLES} - "
              f"Ledger MAJOR {len(major_items)}件を検出。局所Rewrite開始...")

        cycle_results = []
        sentences = local_rewrite.split_sentences(article_text)
        for idx, deviation in enumerate(major_items, start=1):
            target, location_method = local_rewrite.locate_target_sentence(
                deviation["claim_in_article"], article_text)
            if target is None:
                cycle_results.append({
                    "cycle": cycle, "item_idx": idx, "original_ng_sentence": deviation["claim_in_article"],
                    "issue": deviation["issue"], "explanation": deviation["explanation"],
                    "attempts": [], "final_text": None, "resolved": False,
                    "human_review_required": True, "location_method": "not_found",
                })
                continue
            try:
                sidx = sentences.index(target)
            except ValueError:
                sidx = -1
            before_ctx = sentences[sidx - 1] if 0 <= sidx - 1 else ""
            after_ctx = sentences[sidx + 1] if 0 <= sidx and sidx + 1 < len(sentences) else ""
            r = local_rewrite.rewrite_ng_item(client, ledger_model, gen.REASONING_EFFORT,
                                               verified_ledger_text, target, deviation,
                                               before_ctx, after_ctx, _run_check_window)
            r["cycle"] = cycle
            r["item_idx"] = idx
            r["location_method"] = location_method
            cycle_results.append(r)

        article_text = local_rewrite.apply_rewrites(article_text, cycle_results)
        article_text = gen.normalize_article_formatting(article_text)
        with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(article_text)

        metrics = gen.compute_metrics(article_text)
        section_wc = sf1r1.section_word_counts(article_text)
        length_report = {
            **section_wc, "total": metrics["word_count"],
            "point_one_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_one"] <= gen.POINT_TARGET_UPPER,
            "point_one_within_tolerance":
                gen.POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= gen.POINT_TOLERANCE_UPPER,
            "point_two_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_two"] <= gen.POINT_TARGET_UPPER,
            "point_two_within_tolerance":
                gen.POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= gen.POINT_TOLERANCE_UPPER,
            "total_within_soft_range": gen.TOTAL_SOFT_LOWER <= metrics["word_count"] <= gen.TOTAL_SOFT_UPPER,
        }
        with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
            json.dump(length_report, f, ensure_ascii=False, indent=2)

        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
        recheck_major = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
        print(f"[{THEME_ID}] {label}: cycle {cycle} 再判定 overall_status="
              f"{deviation_result['parsed']['overall_status']} MAJOR={len(recheck_major)}件")

        previously_seen_claims |= {d["claim_in_article"] for d in major_items}
        local_rewrite_results.extend(cycle_results)
        local_rewrite_cycles.append({
            "cycle": cycle, "targeted_major_count": len(major_items),
            "newly_discovered_claims": newly_discovered_claims, "results": cycle_results,
            "full_recheck_overall_status": deviation_result["parsed"]["overall_status"],
            "full_recheck_major_count": len(recheck_major),
            "full_recheck_remaining_major_claims": [d["claim_in_article"] for d in recheck_major],
        })
        major_items = recheck_major

    cycle_exhausted = bool(major_items) and cycle >= local_rewrite.MAX_REWRITE_CYCLES

    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/deviation_full_record_requa_open107_03.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2,
                   default=str)
    if local_rewrite_results:
        with open(f"{out_dir}/audit/local_rewrite_results_requa_open107_03.json", "w", encoding="utf-8") as f:
            json.dump(local_rewrite_results, f, ensure_ascii=False, indent=2, default=str)
        with open(f"{out_dir}/audit/local_rewrite_cycles_requa_open107_03.json", "w", encoding="utf-8") as f:
            json.dump(local_rewrite_cycles, f, ensure_ascii=False, indent=2, default=str)

    remaining_major = major_items
    any_human_review = any(r.get("human_review_required") for r in local_rewrite_results)
    if remaining_major or any_human_review:
        print(f"[{THEME_ID}] {label}: Local Rewrite cycleを尽くしてもLedger MAJORが残存。STOPします。")
        return {
            "status": "NG_REVIEW_REQUIRED", "stage": "ledger_deviation", "article_text": article_text,
            "fact_status": fc_status, "fact_verdict": verdict,
            "ledger_status": deviation_result["parsed"]["overall_status"],
            "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
            "local_rewrite_results": local_rewrite_results, "local_rewrite_cycles": local_rewrite_cycles,
            "local_rewrite_cycle_exhausted": cycle_exhausted,
        }

    print(f"[{THEME_ID}] {label}: 比較方向Fact事前チェック開始...")
    vfl_path = f"{os.path.dirname(out_dir)}/research/stage_b3_vfl.json"
    directional_result = dfp.audit_article_directional_facts(article_text, verified_ledger_text, vfl_path=vfl_path)
    directional_precheck_status = directional_result["overall_status"]
    with open(f"{out_dir}/audit/directional_fact_precheck.json", "w", encoding="utf-8") as f:
        json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] {label}: 比較方向Fact事前チェック完了。overall_status={directional_precheck_status}")

    return {
        "status": "OK", "article_text": article_text, "metrics": metrics, "section_word_counts": section_wc,
        "length_report": length_report, "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "local_rewrite_results": local_rewrite_results, "local_rewrite_cycles": local_rewrite_cycles,
        "local_rewrite_cycle_exhausted": cycle_exhausted,
        "directional_fact_precheck_status": directional_precheck_status,
        "point_overlap_report": overlap_report, "point_value_qa_result": value_qa_result,
    }


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log_open107_b1_text_patch_requa.jsonl")
    client = vfl01.get_client()
    with open(f"{LEVEL_OUT_DIR}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    verified_ledger_text = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()

    with cl.logging_context(THEME_ID, "requa_b1_open107_text_patch"):
        result = run_requa_on_patched_article(client, article_text, verified_ledger_text, driver.TOPIC_JA,
                                               LEVEL_OUT_DIR, label=LABEL)

    with open(f"{LEVEL_OUT_DIR}/audit/text_patch_requa_open107_03_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print(f"[{THEME_ID}] {LABEL}: 個別文章差し替え後Re-QA完了。status={result.get('status')} "
          f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')}")
