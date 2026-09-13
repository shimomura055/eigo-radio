# ============================================================
# er013_family_c_future_trial_01_run.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-PROTOTYPE-TRIAL-01
# ============================================================
# 目的: 新Family C(Future、独立経路、1人ナレーター)の記事生成Trial
# driver。テーマ「家庭用ロボットと家事」(ユーザー確定)で、
# Research→3層Ledger→Family C記事(A2/B1、各1本)→QA(既存Fact Checker A'
# [Layer1のみ]/既存Ledger Deviation Checker[Layer1のみ]/新設Future
# Framing QA[Layer2/3のみ])までを実行する。
#
# **Production採用・配線ではない**(Gate 1材料までのTrial)。既存
# Production経路(A-Family/B-Family)・並行中のDiscovery Trial成果物・
# SSOT本文は一切変更しない。
#
# 再利用(import・無変更、read-onlyでの参照+既存Production関数の直接
# 呼び出しのみ。改変・monkeypatchは一切行わない):
#   - er003_v1_en_direct_vfl_01_generate(vfl01): get_client / MODEL /
#     REASONING_EFFORT / FACT_LEDGER_JSON_SCHEMA / RESEARCHER_DEVELOPER_
#     MESSAGE / build_researcher_prompt(topic=) / VERIFICATION_JSON_SCHEMA /
#     VERIFICATION_DEVELOPER_MESSAGE / build_verification_prompt(topic,...) /
#     run_deviation_check(既存Ledger Deviation Checker、hook_aware既定False
#     のまま=Trial呼び出し、Production[hook_aware=True]とは別呼び出し)。
#   - er002_ja_web_research_r3(r3): extract_web_search_usage / extract_sources
#     / build_fact_check_prompt / make_fact_checker_fn / run_fact_checker_
#     with_gates / parse_and_validate_fact_check_output(既存Fact Checker A'、
#     無変更)。
#   - er010_ledger_local_rewrite_09(rewrite09): split_sentences /
#     locate_target_sentence / extract_point_context / rewrite_ng_item /
#     apply_rewrites(既存Local Rewrite、無変更。Trial向けにcycle上限を
#     Production[3]よりも保守的な1に制限する。安全装置を緩めるのではなく
#     厳しくする方向の変更であり、上限まで解決しなければNG_REVIEW_REQUIRED
#     として人手レビューへ回す=安全側)。
#   - er005_cost_logger(cl): install / logging_context。
#   - er006_model_routing_contract_01(routing): require_model
#     ("WRITER_FACT_CHECK", ...)(Fact Checker A'呼び出し時のみ、既存
#     Production Approved Modelを使用)。
#   - er013_family_c_future_ledger_01(fcl) / er013_family_c_future_writer_01
#     (fcw) / er013_family_c_future_qa_01(fcq): 本Trialのために新設した
#     独立Family Cモジュール(A/B-Familyへは一切import/配線しない)。
#
# 費用上限: 合計¥300(Research+Ledger Verification+Layer2/3整理+
# Writer A2/B1+Fact Checker A'[Layer1]+Ledger Deviation[Layer1]+Future
# Framing QA[Layer2/3]+Local Rewrite/retry余裕、全て込み)。実行中に
# cost_stage()で都度実測し、上限到達時はRuntimeErrorでSTOPする
# (Trial-11と同一の安全装置パターン)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er013_family_c_future_trial_01_run.py [stage ...]
#   stage: ledger | layer23 | write_a2 | write_b1 | evaluate | cost | all(省略時)
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er010_ledger_local_rewrite_09 as rewrite09
import er013_family_c_future_ledger_01 as fcl
import er013_family_c_future_qa_01 as fcq
import er013_family_c_future_writer_01 as fcw

THEME_ID = "family_c_future_trial_01"
OUT_DIR = f"er013_output/{THEME_ID}"
RESEARCH_DIR = f"{OUT_DIR}/research"
BUDGET_JPY_CAP = 300.0
LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"

RESEARCH_QUESTION_JA = (
    "「家庭用ロボットと家事(home robots and housework)」というテーマについて調査してください。"
    "家庭内の掃除・洗濯物たたみ・食器洗い・片付け等を行う消費者向け家庭用ロボット(ロボット掃除機、"
    "折り畳みロボット、汎用home robot試作機・製品を含む)の、現在の普及状況・性能の限界・価格帯・"
    "利用者の時間節約や満足度に関する調査結果・専門家の見解・今後の技術トレンド(AI・センサー・"
    "汎用ロボット技術の進展、家事労働時間への影響見通し等)について、信頼できる情報源(市場調査機関、"
    "大学・研究機関、家電メーカー、専門メディア等)に基づいて調査してください。"
)

FAMILY_C_LEDGER_PATH = f"{RESEARCH_DIR}/three_layer_ledger.txt"
LAYER1_ONLY_LEDGER_PATH = f"{RESEARCH_DIR}/layer1_only_ledger.txt"


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


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


# ============================================================
# 費用実測(HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01/Towels Trial-11と同一
# ロジック、read-onlyで転記して再利用)。
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
# Step 0: Research + Verified Fact Ledger(Layer 1、既存経路そのまま。
# News Trial-09/Towels Trial-11と同一手順、topicのみ差し替え)。
# ============================================================
def run_researcher_for_topic(client, topic: str) -> dict:
    prompt = vfl01.build_researcher_prompt(topic=topic)
    response = client.responses.create(
        model=vfl01.MODEL,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **vfl01.FACT_LEDGER_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": vfl01.RESEARCHER_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    search_usage = r3.extract_web_search_usage(response)
    sources = r3.extract_sources(response)
    parsed = json.loads(text)
    return {"prompt": prompt, "raw_text": text, "parsed": parsed, "model": response.model,
            "response_id": response.id, "search_usage": search_usage, "sources": sources}


def run_verification_for_topic(client, topic: str, ledger_parsed: dict) -> dict:
    prompt = vfl01.build_verification_prompt(topic, ledger_parsed)
    response = client.responses.create(
        model=vfl01.MODEL,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **vfl01.VERIFICATION_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": vfl01.VERIFICATION_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    search_usage = r3.extract_web_search_usage(response)
    sources = r3.extract_sources(response)
    parsed = json.loads(text)
    return {"prompt": prompt, "raw_text": text, "parsed": parsed, "model": response.model,
            "response_id": response.id, "search_usage": search_usage, "sources": sources}


def ledger_stage() -> dict:
    os.makedirs(RESEARCH_DIR, exist_ok=True)
    cl.install(LOG_PATH)
    client = vfl01.get_client()

    theme_tag = f"{THEME_ID}_ledger_research"
    with cl.logging_context(theme_tag, "researcher"):
        research_result = run_researcher_for_topic(client, RESEARCH_QUESTION_JA)
    save_json(f"{RESEARCH_DIR}/fact_ledger_draft.json", research_result)
    print(f"[{THEME_ID}] Researcher完了: {len(research_result['parsed']['facts'])}件のFact下書き、"
          f"web_search={research_result['search_usage']}")

    with cl.logging_context(theme_tag, "verification"):
        verification_result = run_verification_for_topic(client, RESEARCH_QUESTION_JA, research_result["parsed"])
    save_json(f"{RESEARCH_DIR}/fact_ledger_verification.json", verification_result)

    ledger_parsed = research_result["parsed"]
    verdict_map = {v["fact_id"]: v for v in verification_result["parsed"]["verifications"]}
    lines, kept_facts = [], []
    counts = {"VERIFIED": 0, "AMBIGUOUS": 0, "REJECTED": 0}
    for fact in ledger_parsed["facts"]:
        v = verdict_map.get(fact["fact_id"])
        verdict = v["verdict"] if v else "AMBIGUOUS"
        counts[verdict] = counts.get(verdict, 0) + 1
        if verdict != "VERIFIED":
            continue
        kept_facts.append({**fact, "verification_verdict": verdict, "verification_notes": v["verification_notes"]})
        lines.append(f"[VERIFIED] {fact['fact_id']}: {fact['claim']}")
        if fact.get("scope"):
            lines.append(f"  scope: {fact['scope']}")
        if fact.get("conditions"):
            lines.append(f"  conditions: {fact['conditions']}")
        if fact.get("numeric_value"):
            lines.append(f"  numeric_value: {fact['numeric_value']} (numeric_scope: {fact.get('numeric_scope') or '未指定'})")
        if fact.get("date_or_period"):
            lines.append(f"  date_or_period: {fact['date_or_period']}")
        if fact.get("causal_strength") and fact["causal_strength"] != "NOT_APPLICABLE":
            lines.append(f"  causal_strength: {fact['causal_strength']}")
        if fact.get("source_title"):
            lines.append(f"  source: {fact['source_title']} ({fact.get('source_url', '')})")
        if fact.get("notes_for_writer"):
            lines.append(f"  notes_for_writer: {fact['notes_for_writer']}")
        lines.append("")
    verified_ledger_text = "\n".join(lines)
    print(f"[{THEME_ID}] Verification完了: {counts}(CONFIRMED-onlyフィルタ適用後 kept={len(kept_facts)}件)")

    layer1_ledger_text = fcl.build_layer1_ledger_text(verified_ledger_text)
    save_text(LAYER1_ONLY_LEDGER_PATH, layer1_ledger_text)
    save_json(f"{RESEARCH_DIR}/verified_fact_ledger_structured.json", {
        "topic_id": "home_robots_housework", "research_question_ja": RESEARCH_QUESTION_JA,
        "kept_facts": kept_facts, "counts": counts,
        "note": "CONFIRMED(VERIFIED)のみ採用(News Trial-09/Towels Trial-11と同一方針)。"
                "AMBIGUOUS/REJECTEDはfact_ledger_verification.jsonに記録済みだが本Ledgerからは除外した。",
    })

    cost = cost_stage()
    print(f"[{THEME_ID}] Ledger(Layer1)作成完了。CONFIRMED(VERIFIED)={counts.get('VERIFIED', 0)}件、"
          f"AMBIGUOUS={counts.get('AMBIGUOUS', 0)}件、REJECTED={counts.get('REJECTED', 0)}件。"
          f"費用実測: {cost['total_jpy']}円")
    return {"layer1_ledger_text": layer1_ledger_text, "counts": counts, "kept_facts": kept_facts, "cost": cost}


# ============================================================
# Step 1: Layer 2/3材料生成(LLM 1回)+3層Ledger組み立て。
# ============================================================
FAMILY_C_TOPIC_JA_PLACEHOLDER = "家庭用ロボットと家事(home robots and housework)"


def layer23_stage() -> dict:
    layer1_ledger_text = open(LAYER1_ONLY_LEDGER_PATH, encoding="utf-8").read()
    present_fact_ids = fcl.extract_present_fact_ids(layer1_ledger_text)

    cl.install(LOG_PATH)
    client = vfl01.get_client()
    with cl.logging_context(THEME_ID, "layer23_generation"):
        layer23_result = fcl.run_layer23_generation(
            client, FAMILY_C_TOPIC_JA_PLACEHOLDER, layer1_ledger_text,
            model=vfl01.MODEL, reasoning_effort=vfl01.REASONING_EFFORT)
    save_json(f"{RESEARCH_DIR}/layer23_generation_result.json", layer23_result)

    grounding_issues = fcl.validate_layer23_grounding(present_fact_ids, layer23_result["parsed"])
    save_json(f"{RESEARCH_DIR}/layer23_grounding_issues.json", grounding_issues)
    print(f"[{THEME_ID}] Layer2/3生成完了: assumptions={len(layer23_result['parsed']['future_assumptions'])}件、"
          f"imagined_futures={len(layer23_result['parsed']['imagined_futures'])}件、"
          f"grounding_issues={len(grounding_issues)}件")
    if grounding_issues:
        raise RuntimeError(f"Layer2/3のbased_on/grounded_inに未知の参照IDがあります: {grounding_issues}")

    three_layer_ledger_text = fcl.assemble_three_layer_ledger_text(layer1_ledger_text, layer23_result["parsed"])
    save_text(FAMILY_C_LEDGER_PATH, three_layer_ledger_text)

    cost = cost_stage()
    print(f"[{THEME_ID}] 3層Ledger作成完了。費用実測: {cost['total_jpy']}円")
    return {"three_layer_ledger_text": three_layer_ledger_text, "layer23_parsed": layer23_result["parsed"],
            "cost": cost}


# ============================================================
# Step 2: 記事生成(Writer)+QAルーティング+Fact Checker A'(Layer1のみ)+
# Ledger Deviation Checker(Layer1のみ、hook_aware既定False)+Future
# Framing QA(Layer2/3のみ、新設)+Local Rewrite(MAJOR検出時、Trial向けに
# cycle上限1へ保守化)。
# ============================================================
MAX_WRITER_MARKER_RETRY = 2  # マーカー不整合時のみ(記事内容の不満による再生成ではない、技術的retry)
LOCAL_REWRITE_MAX_CYCLES_TRIAL = 1  # Production(3)より保守的な上限。安全側(緩和ではない)。


def _run_layer1_deviation_check(client, layer1_only_ledger_text: str, layer1_article_text: str) -> dict:
    return vfl01.run_deviation_check(client, layer1_only_ledger_text, layer1_article_text,
                                      model=vfl01.MODEL, hook_aware=False)


def generate_and_qa_family_c_article(level: str) -> dict:
    assert level in ("a2", "b1")
    out_dir = f"{OUT_DIR}/{level}"
    three_layer_ledger_text = open(FAMILY_C_LEDGER_PATH, encoding="utf-8").read()
    layer1_only_ledger_text = open(LAYER1_ONLY_LEDGER_PATH, encoding="utf-8").read()

    cl.install(LOG_PATH)
    client = vfl01.get_client()

    prompt = fcw.build_family_c_writer_prompt(FAMILY_C_TOPIC_JA_PLACEHOLDER, level, three_layer_ledger_text)
    save_text(f"{out_dir}/writer_prompt.txt", prompt)

    article_text, marker_check, writer_attempts = None, None, []
    for attempt in range(1, MAX_WRITER_MARKER_RETRY + 1):
        with cl.logging_context(THEME_ID, f"writer_{level}_attempt{attempt}"):
            writer_result = fcw.generate_family_c_article(
                client, model=vfl01.MODEL, reasoning_effort=vfl01.REASONING_EFFORT, prompt=prompt)
        candidate = writer_result["raw_text"]
        check = fcq.validate_markers_balanced(candidate)
        writer_attempts.append({"attempt": attempt, "marker_check": check, "response_id": writer_result["response_id"]})
        if check["balanced"]:
            article_text, marker_check = candidate, check
            break
        print(f"[{THEME_ID}][{level}] Writer attempt {attempt}: マーカー不整合検出 {check}(technical retry)")
    save_json(f"{out_dir}/writer_attempts.json", writer_attempts)
    if article_text is None:
        raise RuntimeError(f"[{level}] マーカー整合の取れたWriter出力が{MAX_WRITER_MARKER_RETRY}回の技術的retryでも"
                            f"得られませんでした。STOP(NG_REVIEW_REQUIRED)。")
    save_text(f"{out_dir}/writer_raw_article.txt", article_text)

    routed = fcq.route_article_for_qa(article_text)
    save_json(f"{out_dir}/qa_routing.json", {
        "marker_check": routed["marker_check"], "imagined_blocks": routed["imagined_blocks"],
        "present_tense_leakage_heuristic": routed["present_tense_leakage_heuristic"],
        "unhedged_future_claims_outside_markers_heuristic": routed["unhedged_future_claims_outside_markers_heuristic"],
    })
    save_text(f"{out_dir}/reader_facing_article.txt", routed["reader_text"])
    save_text(f"{out_dir}/layer1_only_article_text.txt", routed["layer1_text_for_fact_check"])

    # --- Fact Checker A'(Layer1のみ、既存関数そのまま。r3.run_fact_checker_
    #     with_gates()は内部でparse_and_validate_fact_check_output()まで
    #     適用した(parsed_result, final_status, attempts_detail, model_id,
    #     response_id, search_usage, sources)を返す) ---
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
    #     Local Rewrite(MAJORのみ、Trial向けcycle上限1) ---
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
        # rewriteが発生した場合、reader向け本文/routing結果を最新のarticle_textで再構築する。
        routed = fcq.route_article_for_qa(article_text)
        save_text(f"{out_dir}/reader_facing_article.txt", routed["reader_text"])
        save_text(f"{out_dir}/writer_raw_article_after_rewrite.txt", article_text)

    # --- Future Framing QA(Layer2/3のみ、新設) ---
    with cl.logging_context(THEME_ID, f"future_framing_qa_{level}"):
        ffqa_result = fcq.run_future_framing_qa(
            client, FAMILY_C_TOPIC_JA_PLACEHOLDER, layer1_only_ledger_text, routed["imagined_blocks"],
            layer1_article_text[:6000], model=vfl01.MODEL, reasoning_effort=vfl01.REASONING_EFFORT)
    save_json(f"{out_dir}/future_framing_qa_result.json", ffqa_result["parsed"])
    print(f"[{THEME_ID}][{level}] Future Framing QA overall_status={ffqa_result['parsed']['overall_status']}")

    overall_pass = (
        fc_parsed["verdict"] == "PASS"
        and dev_result["parsed"]["overall_status"] == "LEDGER_COMPLIANT"
        and ffqa_result["parsed"]["overall_status"] == "PASS"
    )
    summary = {
        "level": level, "word_count": len(routed["reader_text"].split()),
        "marker_check_initial": marker_check, "writer_attempts": len(writer_attempts),
        "fact_check_verdict": fc_parsed["verdict"],
        "deviation_overall_status": dev_result["parsed"]["overall_status"],
        "local_rewrite_cycles_used": cycle,
        "future_framing_qa_overall_status": ffqa_result["parsed"]["overall_status"],
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
        results["ledger"] = ledger_stage()
        results["layer23"] = layer23_stage()
        for level in ("a2", "b1"):
            results[level] = generate_and_qa_family_c_article(level)
            cost_stage()
        results["evaluate"] = evaluate_stage()
        save_json(f"{OUT_DIR}/e2e_run_summary.json", results)
        print(f"[{THEME_ID}] 完了。")
        return results

    result = {}
    for s in stages:
        if s == "ledger":
            result["ledger"] = ledger_stage()
        elif s == "layer23":
            result["layer23"] = layer23_stage()
        elif s in ("a2", "b1"):
            result[s] = generate_and_qa_family_c_article(s)
        elif s == "evaluate":
            result["evaluate"] = evaluate_stage()
        elif s == "cost":
            result["cost"] = cost_stage(stop_on_over_budget=False)
        else:
            raise ValueError(f"未知のstage: {s}")
    return result


if __name__ == "__main__":
    main()
