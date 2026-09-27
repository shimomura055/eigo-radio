# ============================================================
# er034_key_phrase_db_hybrid_source_reference_contract_trial_06_run.py
# KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06 (Phase B)
# ============================================================
# 候補ID方式(er034_..._contract)で、v1(er029 stage1)/v2(er032 stage1)の
# いずれの候補生成層もラップし、既存12本文(Family X)+ Melos A2(Family Z、
# quote-heavy)を同一条件(1本文1 selector call、article全文非送信
# assertion、共有ストア非書込み)で実行する。
#
# er023/er027/er028/er029/er030(v1 baseline)/er032(v2)・er003_key_words_*
# は一切変更しない(read-only import)。
# ============================================================

from __future__ import annotations

import json
import os

import er003_b1_p2_keywords as bk
import er006_model_routing_contract_01 as routing
import er023_key_phrase_db_ingest as ing
import er028_key_phrase_db_hybrid_trial_03_run as base
import er029_key_phrase_db_hybrid_trial_04_run as run4
import er030_key_phrase_db_hybrid_selector_01 as selector01
import er032_key_phrase_db_hybrid_core_v2_trial_05_run as run5
import er034_key_phrase_db_hybrid_source_reference_contract_trial_06_contract as contract

OUTPUT_ROOT = os.path.join("er034_output", "key_phrase_db_hybrid_source_reference_contract_trial_06")

# Family X 12本文(er029_key_phrase_db_hybrid_trial_04_run/er030既存回帰対象と
# 完全同一パス、v1/v2既存Trialとの直接比較のため)。
X_EXISTING_6_ARTICLES = dict(run4.EXISTING_6_ARTICLES)
X_ADDITIONAL_6_RAW = dict(run4._ADDITIONAL_6_RAW)

# Melos A2(Family Z、quote-heavy、既知失敗事例。er032_key_phrase_db_hybrid_
# core_v2_trial_05_runと完全同一パス)。
MELOS_ARTICLE_PATH = "er026_output/family_z_production_e2e_01/melos/run_01/article.md"
MELOS_PROCESS = "A2_SUPPORT"
MELOS_TITLE_OVERRIDE = "The Three-Day Promise"

# Guardrail(ユーザー指示 ¥40、STOP閾値¥35)。
COST_STOP_THRESHOLD_JPY = 35.0
HARD_CAP_JPY = 40.0


def run_stage1_and_shortlist_v1_wrap(article_text: str, dbs: dict, title: str) -> dict:
    """v1(Trial-04 stage1、Production er030とロジック無変更で同一)を
    そのまま呼ぶだけ(候補生成自体は無変更)。"""
    return run4.run_stage1_and_shortlist_v4(article_text, dbs, title)


def run_stage1_and_shortlist_v2_wrap(article_text: str, dbs: dict, title: str) -> dict:
    """v2(Trial-05 core v2 stage1)をそのまま呼ぶだけ(候補生成自体は
    無変更)。"""
    return run5.run_stage1_and_shortlist_core_v2(article_text, dbs, title)


def prepare_article(article_key: str, article_path: str, process: str, title_override,
                     dbs: dict, wrap_version: str) -> dict:
    """Stage1(候補生成、API呼び出しなし)+ candidate ID付与までを1回だけ
    実行し、複数サンプル呼び出し(反復安定性テスト)で使い回せる状態を
    返す。"""
    article_text = open(article_path, encoding="utf-8").read()
    title = title_override or base.extract_article_title(article_text)

    if wrap_version == "v1":
        s1r = run_stage1_and_shortlist_v1_wrap(article_text, dbs, title)
        display_type_fn = selector01._display_type
        evidence_fn = selector01._compact_evidence_string
    elif wrap_version == "v2":
        s1r = run_stage1_and_shortlist_v2_wrap(article_text, dbs, title)
        display_type_fn = run5._display_type_v2
        evidence_fn = run5._compact_evidence_string_v2
    else:
        raise ValueError(f"unknown wrap_version: {wrap_version}")

    stage1, shortlist_info = s1r["stage1"], s1r["shortlist_info"]
    id_result = contract.assign_candidate_ids(shortlist_info["shortlist"])

    static_instructions = base.extract_static_instructions(bk.load_prompt_template())
    message = contract.build_lightweight_user_message(
        title, id_result["shortlist_with_ids"], shortlist_info["sentence_reference"],
        static_instructions, display_type_fn=display_type_fn, evidence_fn=evidence_fn)
    base.assert_no_full_article_body(message, article_text)

    model = routing.require_model(process, routing.SUPPORT_MODEL)

    return {
        "article_key": article_key, "article_path": article_path, "article_text": article_text,
        "title": title, "wrap_version": wrap_version, "process": process, "model": model,
        "stage1": stage1, "shortlist_info": shortlist_info, "id_result": id_result,
        "lightweight_message": message,
    }


def call_selector_once(prepared: dict, cost_tracker: "base._RunningCost", out_dir: str,
                        article_id_prefix: str, sample_label: str = "s1") -> dict:
    """prepare_articleが返す情報を使い、selector API呼び出し1回+候補ID
    復元+既存validator(無変更)+ Source Gate相当チェックまでを実行する。"""
    os.makedirs(out_dir, exist_ok=True)
    usage_sink = []
    contract_violation_sink = []
    factory = contract.make_instrumented_selector_factory(
        prepared["lightweight_message"], prepared["model"], prepared["id_result"]["candidate_ids"],
        usage_sink, contract_violation_sink=contract_violation_sink)

    article_id = f"{article_id_prefix}_{prepared['article_key'].upper()}_{sample_label.upper()}"
    gate_result = contract.run_source_reference_contract_gate(
        article_id, factory, prepared["article_text"],
        prepared["id_result"]["id_to_candidate"], prepared["shortlist_info"]["sentence_reference"])

    usage_entry = usage_sink[0] if usage_sink else {"usage": {}}
    usage = usage_entry.get("usage", {})
    label = f"{prepared['article_key']}_{prepared['wrap_version']}_{sample_label}"
    cost_tracker.add(label, gate_result.get("model_id") or prepared["model"], usage)

    result = {
        "article_key": prepared["article_key"], "wrap_version": prepared["wrap_version"],
        "sample_label": sample_label, "article_title": prepared["title"],
        "shortlist_total_count": prepared["shortlist_info"]["shortlist_total_count"],
        "candidate_count": len(prepared["id_result"]["candidate_ids"]),
        "status": gate_result["status"],
        "model_id": gate_result.get("model_id"), "response_id": gate_result.get("response_id"),
        "usage": usage, "cost_jpy": round(contract.cost_jpy_for_usage(
            gate_result.get("model_id") or prepared["model"], usage), 4) if usage else 0.0,
        "restore_telemetry": {
            "unresolved": gate_result["restore_telemetry"].get("unresolved", []),
            "mismatch_count": gate_result["restore_telemetry"].get("mismatch_count", 0),
            "mismatch_details": gate_result["restore_telemetry"].get("mismatch_details", []),
        },
        "source_gate_missing": gate_result.get("source_gate_missing", []),
        "validation_reasons": gate_result.get("validation_reasons", []),
        "item_reasons": gate_result.get("item_reasons", []),
        "contract_violation": contract_violation_sink[0] if contract_violation_sink else None,
        "parsed": gate_result.get("parsed"),
        "prompt_char_len": len(prepared["lightweight_message"]),
        "article_char_len": len(prepared["article_text"]),
    }
    out_path = os.path.join(out_dir, f"source_reference_contract_trial_result_{sample_label}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    if sample_label == "s1":
        with open(os.path.join(out_dir, "lightweight_selector_prompt.txt"), "w", encoding="utf-8") as f:
            f.write(prepared["lightweight_message"])
    return result


def main():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    print("Loading group1 DBs...")
    dbs = ing.load_all_group1_dbs()
    cost_tracker = base._RunningCost(COST_STOP_THRESHOLD_JPY)

    all_results = {}

    try:
        # --- Phase 1: v2ラップ、Family X 12本文 + Melos A2 (13本文、各1 call) ---
        prepared_cache = {}
        for article_key, (article_path, process) in X_EXISTING_6_ARTICLES.items():
            out_dir = os.path.join(OUTPUT_ROOT, "v2_" + article_key)
            prepared = prepare_article(article_key, article_path, process, None, dbs, "v2")
            prepared_cache[("v2", article_key)] = prepared
            res = call_selector_once(prepared, cost_tracker, out_dir, "KPS2V2")
            all_results[f"v2_{article_key}"] = res
            print(f"  v2 {article_key}: status={res['status']} cost={res['cost_jpy']}")

        for article_key, (article_path, process, title_override) in X_ADDITIONAL_6_RAW.items():
            out_dir = os.path.join(OUTPUT_ROOT, "v2_" + article_key)
            prepared = prepare_article(article_key, article_path, process, title_override, dbs, "v2")
            prepared_cache[("v2", article_key)] = prepared
            res = call_selector_once(prepared, cost_tracker, out_dir, "KPS2V2")
            all_results[f"v2_{article_key}"] = res
            print(f"  v2 {article_key}: status={res['status']} cost={res['cost_jpy']}")

        out_dir = os.path.join(OUTPUT_ROOT, "v2_melos_a2")
        prepared = prepare_article("melos_a2", MELOS_ARTICLE_PATH, MELOS_PROCESS,
                                    MELOS_TITLE_OVERRIDE, dbs, "v2")
        prepared_cache[("v2", "melos_a2")] = prepared
        res = call_selector_once(prepared, cost_tracker, out_dir, "KPS2V2")
        all_results["v2_melos_a2"] = res
        print(f"  v2 melos_a2: status={res['status']} cost={res['cost_jpy']}")

        # --- Phase 2: v1ラップ、twins_a2・Melos A2 (2本文、v1既存挙動比較用) ---
        twins_path, twins_process = X_ADDITIONAL_6_RAW["twins_a2"][0], X_ADDITIONAL_6_RAW["twins_a2"][1]
        out_dir = os.path.join(OUTPUT_ROOT, "v1_twins_a2")
        prepared_v1_twins = prepare_article("twins_a2", twins_path, twins_process, "Digital Twins", dbs, "v1")
        res = call_selector_once(prepared_v1_twins, cost_tracker, out_dir, "KPS2V1")
        all_results["v1_twins_a2"] = res
        print(f"  v1 twins_a2: status={res['status']} cost={res['cost_jpy']}")

        out_dir = os.path.join(OUTPUT_ROOT, "v1_melos_a2")
        prepared_v1_melos = prepare_article("melos_a2", MELOS_ARTICLE_PATH, MELOS_PROCESS,
                                             MELOS_TITLE_OVERRIDE, dbs, "v1")
        res = call_selector_once(prepared_v1_melos, cost_tracker, out_dir, "KPS2V1")
        all_results["v1_melos_a2"] = res
        print(f"  v1 melos_a2: status={res['status']} cost={res['cost_jpy']}")

        # --- Phase 3: 反復安定性、twins_a2・Melos A2をv2ラップで追加2サンプル
        # ずつ(Phase 1のs1と合わせて計3サンプル/記事)。stage1(候補生成)は
        # prepared_cacheを再利用し、selector call自体だけを繰り返す。 ---
        for article_key in ("twins_a2", "melos_a2"):
            prepared = prepared_cache[("v2", article_key)]
            out_dir = os.path.join(OUTPUT_ROOT, "v2_" + article_key)
            for sample_label in ("s2", "s3"):
                res = call_selector_once(prepared, cost_tracker, out_dir, "KPS2V2", sample_label=sample_label)
                all_results[f"v2_{article_key}_{sample_label}"] = res
                print(f"  v2 {article_key} {sample_label}: status={res['status']} cost={res['cost_jpy']}")

    except base.CostGuardrailStop as e:
        print(f"STOP: {e}")
        with open(os.path.join(OUTPUT_ROOT, "cost_guardrail_stop.json"), "w", encoding="utf-8") as f:
            json.dump({"reason": str(e), "completed": list(all_results.keys()),
                       "cost_so_far_jpy": cost_tracker.total_jpy}, f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUTPUT_ROOT, "raw_usage_log.jsonl"), "w", encoding="utf-8") as f:
        for call in cost_tracker.calls:
            f.write(json.dumps(call, ensure_ascii=False) + "\n")
    with open(os.path.join(OUTPUT_ROOT, "cost.json"), "w", encoding="utf-8") as f:
        json.dump({"total_jpy": round(cost_tracker.total_jpy, 4), "calls": cost_tracker.calls},
                   f, ensure_ascii=False, indent=2)

    summary = {
        key: {"status": r["status"], "cost_jpy": r["cost_jpy"],
              "mismatch_count": r["restore_telemetry"]["mismatch_count"],
              "unresolved": r["restore_telemetry"]["unresolved"],
              "source_gate_missing": r["source_gate_missing"]}
        for key, r in all_results.items()
    }
    with open(os.path.join(OUTPUT_ROOT, "all_articles_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("Done. Total cost JPY:", round(cost_tracker.total_jpy, 4))
    return all_results


if __name__ == "__main__":
    main()
