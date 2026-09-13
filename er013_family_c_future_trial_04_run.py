# ============================================================
# er013_family_c_future_trial_04_run.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04
# ============================================================
# 目的: 構造診断(er013_family_c_future_writer_04.py冒頭コメント参照)を
# 踏まえたFamily C v4契約での最小再Trial driver。Trial-02の同一Ledger・
# 同一World Scaffold・同一Layer2/3・同一World Package原本を無変更のまま
# read-onlyで再利用し(Research/Scaffold/Layer2-3の再生成費用¥0)、
# コード側で決定的に場面数を2へ絞り込んだWorld Package(v4版)を作成した
# うえで、Writer(v4)→編集Gate v3(v3から無変更、v4のword_count_target_
# rangeのみ異なる)→Fact Checker A'(Layer1のみ、既存関数無改変)→Ledger
# Deviation Checker(Layer1のみ、既存関数無改変)→Local Rewrite(既存関数
# 無改変、cycle上限1)→Future Framing QA v2(既存関数無改変)、までを実行
# する。
#
# **Production採用・配線ではない**(Gate 1材料までのTrial)。既存
# Production経路(A-Family/B-Family)・並行中のDiscovery Trial成果物・
# SSOT本文・既存er013_*_01/_02/_03は一切変更しない。Git操作は行わない。
# 同一テーマ(家庭用ロボットと家事)のみ、別テーマへは進まない。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er013_family_c_future_trial_04_run.py [stage ...]
#   stage: reuse_research | a2 | b1 | evaluate | cost | all(省略時)
# ============================================================
from __future__ import annotations

import json
import os
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er010_ledger_local_rewrite_09 as rewrite09
import er013_family_c_future_qa_01 as fcq_v1
import er013_family_c_future_qa_03 as fcq3
import er013_family_c_future_writer_04 as fcw4

THEME_ID = "family_c_future_trial_04"
OUT_DIR = f"er013_output/{THEME_ID}"
BUDGET_JPY_CAP = 30.0
LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"

FAMILY_C_TOPIC_JA_PLACEHOLDER = "家庭用ロボットと家事(home robots and housework)"

# Trial-02で既に確定済みのResearch/World Scaffold/Layer2-3成果物を再利用
# する(ユーザー指示書「同一Ledger・同一テーマ」)。v4独自の絞り込み
# World Packageはこのファイル内で新たに組み立てる(¥0、決定的)。
TRIAL01_LAYER1_LEDGER_PATH = "er013_output/family_c_future_trial_01/research/layer1_only_ledger.txt"
TRIAL02_RESEARCH_DIR = "er013_output/family_c_future_trial_02/research"
REUSED_RESEARCH_FILES = (
    "world_scaffold_result.json", "world_scaffold_text.txt", "layer23_v2_result.json",
)

WORLD_SCAFFOLD_PATH = f"{OUT_DIR}/research/world_scaffold_result.json"
LAYER23_PATH = f"{OUT_DIR}/research/layer23_v2_result.json"
WORLD_PACKAGE_TEXT_V4_PATH = f"{OUT_DIR}/research/world_package_text_v4.txt"
WORLD_PACKAGE_TRIM_SUMMARY_PATH = f"{OUT_DIR}/research/world_package_trim_summary.json"


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# 費用実測(Trial-01/02/03と同一ロジック、read-onlyで転記)。
# ============================================================
USD_JPY = 160.0
_PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def _price(provider, model, meter, tier="Standard"):
    for p in _PRICING:
        if p["provider"] == provider and p["model"] == model and p["meter"] == meter and p.get("tier", "Standard") == tier:
            return p["price"]
    raise KeyError((provider, model, meter, tier))


def _call_cost_usd(r: dict) -> tuple:
    provider = r.get("provider")
    model = r.get("model_id") or r.get("model")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    try:
        if provider == "openai":
            billable_in = max(it - ct, 0)
            cost = (billable_in / 1e6) * _price("openai", model, "input_tokens") \
                + (ct / 1e6) * _price("openai", model, "cached_input_tokens") \
                + (ot / 1e6) * _price("openai", model, "output_tokens")
            wsc = r.get("web_search_call_count") or 0
            cost += (wsc / 1000) * _price("openai", "N/A (tool, all models)", "web_search_call")
            return cost, False
        return 0.0, True
    except KeyError:
        return 0.0, True


def compute_cost_jpy_so_far() -> dict:
    if not os.path.exists(LOG_PATH):
        return {"total_jpy": 0.0, "by_provider_jpy": {}, "unpriced_records": 0, "total_records": 0}
    total_usd, by_provider, unpriced = 0.0, {}, 0
    n = 0
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            cost, up = _call_cost_usd(rec)
            total_usd += cost
            by_provider[rec.get("provider")] = by_provider.get(rec.get("provider"), 0.0) + cost
            unpriced += int(up)
            n += 1
    return {
        "total_jpy": round(total_usd * USD_JPY, 2),
        "by_provider_jpy": {k: round(v * USD_JPY, 2) for k, v in by_provider.items()},
        "unpriced_records": unpriced, "total_records": n,
    }


def cost_stage(stop_on_over_budget: bool = True) -> dict:
    result = compute_cost_jpy_so_far()
    save_json(f"{OUT_DIR}/cost_summary.json", result)
    print(f"[{THEME_ID}][cost] 実測合計={result['total_jpy']} JPY (上限{BUDGET_JPY_CAP}) "
          f"by_provider={result['by_provider_jpy']} unpriced_records={result['unpriced_records']}")
    if stop_on_over_budget and result["total_jpy"] > BUDGET_JPY_CAP:
        raise RuntimeError(f"費用上限超過(実測{result['total_jpy']}円 > 上限{BUDGET_JPY_CAP}円)。STOP。")
    return result


# ============================================================
# Step 0: Trial-02のResearch/World Scaffold/Layer2-3をread-onlyで再利用
# し(コピーのみ、LLM呼び出し無し、費用¥0)、v4用に決定的に絞り込んだ
# World Packageを組み立てる(追加LLM呼び出しなし、費用¥0)。
# ============================================================
def reuse_research_stage() -> dict:
    os.makedirs(f"{OUT_DIR}/research", exist_ok=True)
    for fname in REUSED_RESEARCH_FILES:
        src = f"{TRIAL02_RESEARCH_DIR}/{fname}"
        if not os.path.exists(src):
            raise RuntimeError(f"Trial-02のResearch成果物が見つかりません: {src}"
                                f"(同一Ledger・World Scaffold再利用の前提が崩れているためSTOP)")
        shutil.copyfile(src, f"{OUT_DIR}/research/{fname}")
    scaffold_parsed = load_json(WORLD_SCAFFOLD_PATH)["parsed"]
    layer23_parsed = load_json(LAYER23_PATH)["parsed"]
    selected_scenes = fcw4.select_scenes_for_v4(layer23_parsed, max_scenes=2)
    world_package_text_v4, trim_summary = fcw4.build_trimmed_world_package_text(
        scaffold_parsed, layer23_parsed, selected_scenes)
    save_text(WORLD_PACKAGE_TEXT_V4_PATH, world_package_text_v4)
    save_json(WORLD_PACKAGE_TRIM_SUMMARY_PATH, trim_summary)
    print(f"[{THEME_ID}] Trial-02のResearch成果物を再利用しました(費用¥0): "
          f"{TRIAL02_RESEARCH_DIR} → {OUT_DIR}/research")
    print(f"[{THEME_ID}] v4決定的絞り込み: 場面{len(layer23_parsed.get('imagined_futures') or [])}→"
          f"{len(selected_scenes)}件、Scaffold項目{trim_summary['dropped_scaffold_count']}件削減")
    return {"scaffold_parsed": scaffold_parsed, "layer23_parsed": layer23_parsed,
            "selected_scenes": selected_scenes, "trim_summary": trim_summary}


# ============================================================
# Step 1: 記事生成(Writer v4)+編集Gate v3(v3から無変更、word_count_
# target_rangeのみv4値)+Fact Checker A'(Layer1のみ)+Ledger Deviation
# Checker(Layer1のみ)+Local Rewrite(cycle上限1)+Future Framing QA v2。
# ============================================================
MAX_WRITER_MARKER_RETRY = 2  # マーカー不整合時のみ(技術的retry)
MAX_EDITORIAL_GATE_ATTEMPTS = 2  # 初回+regen最大1回(指示書「再生成余裕1回」)
LOCAL_REWRITE_MAX_CYCLES_TRIAL = 1  # Trial-01/02/03と同一の保守的な上限


def _run_layer1_deviation_check(client, layer1_only_ledger_text: str, layer1_article_text: str) -> dict:
    return vfl01.run_deviation_check(client, layer1_only_ledger_text, layer1_article_text,
                                      model=vfl01.MODEL, hook_aware=False)


def _generate_writer_output_with_marker_retry(client, out_dir: str, level: str, prompt: str) -> tuple:
    """マーカー([[IMAGINED:]]と[[FACT:]]の両方)が整合するまで、技術的
    retryを行う(内容不満による再生成ではない、Trial-02/03と同一パターン)。"""
    article_text, writer_attempts = None, []
    for attempt in range(1, MAX_WRITER_MARKER_RETRY + 1):
        with cl.logging_context(THEME_ID, f"writer_{level}_attempt{attempt}"):
            writer_result = fcw4.generate_family_c_article_v4(
                client, model=vfl01.MODEL, reasoning_effort=vfl01.REASONING_EFFORT, prompt=prompt)
        candidate = writer_result["raw_text"]
        text_no_meta = fcq3.strip_meta_blocks(candidate)
        imagined_check = fcq_v1.validate_markers_balanced(text_no_meta)
        fact_check_balance = fcq3.validate_fact_markers_balanced(text_no_meta)
        balanced = imagined_check["balanced"] and fact_check_balance["balanced"]
        writer_attempts.append({"attempt": attempt, "imagined_check": imagined_check,
                                 "fact_check_balance": fact_check_balance,
                                 "response_id": writer_result["response_id"]})
        if balanced:
            article_text = candidate
            break
        print(f"[{THEME_ID}][{level}] Writer attempt {attempt}: マーカー不整合検出 "
              f"imagined={imagined_check} fact={fact_check_balance}(technical retry)")
    save_json(f"{out_dir}/writer_attempts.json", writer_attempts)
    return article_text, writer_attempts


def generate_and_qa_family_c_article_v4(level: str) -> dict:
    assert level in ("a2", "b1")
    out_dir = f"{OUT_DIR}/{level}"
    world_package_text = load_text(WORLD_PACKAGE_TEXT_V4_PATH)
    scaffold_parsed = load_json(WORLD_SCAFFOLD_PATH)["parsed"]
    banned_product_names = scaffold_parsed.get("product_names_mentioned") or []
    layer1_only_ledger_text = load_text(TRIAL01_LAYER1_LEDGER_PATH)
    word_count_range = fcw4.WORD_COUNT_TARGET_RANGE[level]

    cl.install(LOG_PATH)
    client = vfl01.get_client()

    gate_feedback = ""
    article_text, routed, gate_result, gate_attempts = None, None, None, []
    for gate_attempt in range(1, MAX_EDITORIAL_GATE_ATTEMPTS + 1):
        prompt = fcw4.build_family_c_writer_v4_prompt(FAMILY_C_TOPIC_JA_PLACEHOLDER, level, world_package_text,
                                                        gate_feedback=gate_feedback)
        save_text(f"{out_dir}/writer_prompt_attempt{gate_attempt}.txt", prompt)
        candidate_article, writer_attempts = _generate_writer_output_with_marker_retry(client, out_dir, level, prompt)
        if candidate_article is None:
            raise RuntimeError(f"[{level}] マーカー整合の取れたWriter出力が{MAX_WRITER_MARKER_RETRY}回の技術的"
                                f"retryでも得られませんでした。STOP(NG_REVIEW_REQUIRED)。")
        save_text(f"{out_dir}/writer_raw_article_gate_attempt{gate_attempt}.txt", candidate_article)

        candidate_routed = fcq3.route_article_for_qa_v2(candidate_article)
        candidate_gate = fcq3.scan_editorial_gate_v3(
            candidate_routed["reader_text"], candidate_routed["fact_blocks"], banned_product_names,
            candidate_routed["imagined_blocks"], level, word_count_range)
        gate_attempts.append({"gate_attempt": gate_attempt, "gate_result": candidate_gate})
        article_text, routed, gate_result = candidate_article, candidate_routed, candidate_gate
        if candidate_gate["overall_status"] == "PASS":
            break
        gate_feedback = "; ".join(candidate_gate["fail_reasons"])
        print(f"[{THEME_ID}][{level}] 編集Gate(v3、v4語数目安) attempt {gate_attempt}: FAIL "
              f"({candidate_gate['fail_reasons']})")

    save_json(f"{out_dir}/editorial_gate_attempts.json", gate_attempts)
    save_text(f"{out_dir}/writer_raw_article.txt", article_text)
    save_json(f"{out_dir}/qa_routing.json", {
        "marker_check_imagined": routed["marker_check_imagined"], "marker_check_fact": routed["marker_check_fact"],
        "fact_inside_imagined_issues": routed["fact_inside_imagined_issues"],
        "imagined_blocks": routed["imagined_blocks"], "fact_blocks": routed["fact_blocks"],
        "meta_blocks": routed["meta_blocks"],
        "present_tense_leakage_heuristic": routed["present_tense_leakage_heuristic"],
        "unhedged_future_claims_outside_markers_heuristic": routed["unhedged_future_claims_outside_markers_heuristic"],
    })
    save_text(f"{out_dir}/reader_facing_article.txt", routed["reader_text"])
    save_text(f"{out_dir}/layer1_only_article_text.txt", routed["layer1_text_for_fact_check"])
    save_json(f"{out_dir}/editorial_gate_result_final_pre_rewrite.json", gate_result)

    # --- 診断用(ブロッキングGateではない): [[IMAGINED]]場面数の実測 ---
    imagined_scene_count = len(routed["imagined_blocks"])
    print(f"[{THEME_ID}][{level}] 診断: [[IMAGINED]]場面数(実測)={imagined_scene_count}"
          f"(v4目標: 2場面)")

    # --- Fact Checker A'(Layer1のみ、既存関数そのまま) ---
    fc_prompt = r3.build_fact_check_prompt(
        FAMILY_C_TOPIC_JA_PLACEHOLDER, routed["layer1_text_for_fact_check"], writer_sources=[])
    fc_model = routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL)
    with cl.logging_context(THEME_ID, f"fact_check_{level}"):
        (fc_parsed, fc_final_status, fc_attempts_detail, fc_used_model, fc_response_id,
         fc_search_usage, fc_sources) = r3.run_fact_checker_with_gates(
            lambda: r3.make_fact_checker_fn(fc_prompt, client=client, model=fc_model, reasoning_effort="high"))
    if fc_final_status != "FACT_CHECK_COMPLETED":
        raise RuntimeError(f"[{level}] Fact Checker A'技術的失敗: {fc_final_status}(attempts={fc_attempts_detail})")
    save_json(f"{out_dir}/fact_check_result.json", {"parsed": fc_parsed, "final_status": fc_final_status,
                                                     "model": fc_used_model, "response_id": fc_response_id,
                                                     "search_usage": fc_search_usage})
    print(f"[{THEME_ID}][{level}] Fact Checker A'(Layer1) verdict={fc_parsed['verdict']}")

    # --- Ledger Deviation Checker(Layer1のみ、hook_aware既定False)+
    #     Local Rewrite(MAJORのみ、cycle上限1) ---
    layer1_article_text = routed["layer1_text_for_fact_check"]
    with cl.logging_context(THEME_ID, f"deviation_check_{level}_cycle0"):
        dev_result = _run_layer1_deviation_check(client, layer1_only_ledger_text, layer1_article_text)
    rewrite_log = []
    cycle = 0
    while dev_result["parsed"]["overall_status"] == "LEDGER_DEVIATION" and cycle < LOCAL_REWRITE_MAX_CYCLES_TRIAL:
        cycle += 1
        majors = [d for d in dev_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
        cycle_results = []
        for d in majors:
            ng_sentence, match_kind = rewrite09.locate_target_sentence(d["claim_in_article"], layer1_article_text)
            if ng_sentence is None:
                cycle_results.append({"deviation": d, "resolved": False, "reason": "sentence_not_located"})
                continue
            point_context = rewrite09.extract_point_context(layer1_article_text, ng_sentence) or ng_sentence
            sentences = rewrite09.split_sentences(layer1_article_text)
            idx = sentences.index(ng_sentence) if ng_sentence in sentences else None
            before_ctx = sentences[idx - 1] if idx and idx > 0 else ""
            after_ctx = sentences[idx + 1] if idx is not None and idx + 1 < len(sentences) else ""

            def _run_check_window(window_text: str) -> dict:
                return _run_layer1_deviation_check(client, layer1_only_ledger_text, window_text)["parsed"]

            with cl.logging_context(THEME_ID, f"local_rewrite_{level}_cycle{cycle}"):
                r_result = rewrite09.rewrite_ng_item(
                    client, vfl01.MODEL, vfl01.REASONING_EFFORT, layer1_only_ledger_text,
                    point_context, ng_sentence, d, before_ctx, after_ctx, _run_check_window)
            cycle_results.append({"deviation": d, "match_kind": match_kind, **r_result})
        rewrite_log.append({"cycle": cycle, "results": cycle_results})

        accepted = [r for r in cycle_results if r.get("resolved")]
        if accepted:
            layer1_article_text = rewrite09.apply_rewrites(layer1_article_text, accepted)
            article_text = rewrite09.apply_rewrites(article_text, accepted)
        with cl.logging_context(THEME_ID, f"deviation_check_{level}_cycle{cycle}"):
            dev_result = _run_layer1_deviation_check(client, layer1_only_ledger_text, layer1_article_text)

    save_json(f"{out_dir}/deviation_check_result.json", dev_result["parsed"])
    save_json(f"{out_dir}/local_rewrite_log.json", rewrite_log)
    print(f"[{THEME_ID}][{level}] Ledger Deviation(Layer1) overall_status={dev_result['parsed']['overall_status']} "
          f"(rewrite cycles used={cycle})")

    if rewrite_log:
        routed = fcq3.route_article_for_qa_v2(article_text)
        gate_result = fcq3.scan_editorial_gate_v3(
            routed["reader_text"], routed["fact_blocks"], banned_product_names,
            routed["imagined_blocks"], level, word_count_range)
        save_text(f"{out_dir}/reader_facing_article.txt", routed["reader_text"])
        save_text(f"{out_dir}/writer_raw_article_after_rewrite.txt", article_text)
        save_json(f"{out_dir}/editorial_gate_result_final_post_rewrite.json", gate_result)
        print(f"[{THEME_ID}][{level}] rewrite後の編集Gate再確認: overall_status={gate_result['overall_status']}")

    # --- Future Framing QA v2(既存関数無改変) ---
    deterministic_scan_summary = json.dumps({
        "numeric_hits_count": len(gate_result["numeric_hits"]),
        "research_term_hits_count": len(gate_result["research_term_hits"]),
        "product_name_hits": gate_result["product_name_hits"],
        "fact_exception_count": gate_result["fact_exception_count"],
        "imagined_hedge_density": gate_result["imagined_hedge_density_result"]["hedge_density"],
        "word_count": gate_result["word_count_result"]["word_count"],
    }, ensure_ascii=False)
    with cl.logging_context(THEME_ID, f"future_framing_qa_v2_{level}"):
        ffqa_result = fcq3.run_future_framing_qa_v2(
            client, FAMILY_C_TOPIC_JA_PLACEHOLDER, layer1_only_ledger_text, routed["imagined_blocks"],
            routed["reader_text"], deterministic_scan_summary,
            model=vfl01.MODEL, reasoning_effort=vfl01.REASONING_EFFORT)
    save_json(f"{out_dir}/future_framing_qa_result.json", ffqa_result["parsed"])
    print(f"[{THEME_ID}][{level}] Future Framing QA v2 overall_status={ffqa_result['parsed']['overall_status']}")

    overall_pass = (
        gate_result["overall_status"] == "PASS"
        and fc_parsed["verdict"] == "PASS"
        and dev_result["parsed"]["overall_status"] == "LEDGER_COMPLIANT"
        and ffqa_result["parsed"]["overall_status"] == "PASS"
    )
    summary = {
        "level": level, "word_count": gate_result["word_count_result"]["word_count"],
        "word_count_target_range": list(word_count_range),
        "word_count_within_range": gate_result["word_count_result"]["within_range"],
        "imagined_scene_count": imagined_scene_count,
        "imagined_hedge_density": gate_result["imagined_hedge_density_result"]["hedge_density"],
        "imagined_hedge_density_within_limit": gate_result["imagined_hedge_density_result"]["within_limit"],
        "gate_attempts_used": len(gate_attempts), "writer_attempts_last_gate": len(writer_attempts),
        "editorial_gate_final_status": gate_result["overall_status"],
        "editorial_gate_fail_reasons": gate_result["fail_reasons"],
        "fact_check_verdict": fc_parsed["verdict"],
        "deviation_overall_status": dev_result["parsed"]["overall_status"],
        "local_rewrite_cycles_used": cycle,
        "future_framing_qa_v2_overall_status": ffqa_result["parsed"]["overall_status"],
        "present_tense_leakage_heuristic_hits": len(routed["present_tense_leakage_heuristic"]),
        "unhedged_future_claims_heuristic_hits": len(routed["unhedged_future_claims_outside_markers_heuristic"]),
        "overall_status": "PASS" if overall_pass else "NG_REVIEW_REQUIRED",
    }
    save_json(f"{out_dir}/run_summary.json", summary)
    cost = cost_stage()
    print(f"[{THEME_ID}][{level}] 完了: overall_status={summary['overall_status']} 費用実測={cost['total_jpy']}円")
    return summary


def evaluate_stage() -> dict:
    results = {}
    for level in ("a2", "b1"):
        p = f"{OUT_DIR}/{level}/run_summary.json"
        if os.path.exists(p):
            results[level] = load_json(p)
    save_json(f"{OUT_DIR}/e2e_evaluate_summary.json", results)
    return results


def main() -> dict:
    stages = sys.argv[1:] or ["all"]
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(LOG_PATH)

    if stages == ["all"]:
        results = {}
        results["reuse_research"] = reuse_research_stage()
        for level in ("a2", "b1"):
            results[level] = generate_and_qa_family_c_article_v4(level)
            cost_stage()
        results["evaluate"] = evaluate_stage()
        save_json(f"{OUT_DIR}/e2e_run_summary.json", results)
        print(f"[{THEME_ID}] 完了。")
        return results

    result = {}
    for s in stages:
        if s == "reuse_research":
            result["reuse_research"] = reuse_research_stage()
        elif s in ("a2", "b1"):
            result[s] = generate_and_qa_family_c_article_v4(s)
        elif s == "evaluate":
            result["evaluate"] = evaluate_stage()
        elif s == "cost":
            result["cost"] = cost_stage(stop_on_over_budget=False)
        else:
            raise ValueError(f"未知のstage: {s}")
    return result


if __name__ == "__main__":
    main()
