# ============================================================
# er014_output/four_type_observation_01/discovery/run_discovery_fix_b1b_kp.py
# 管理ID: EDITORIAL-4TYPE-FOLLOWUP-03-DISCOVERY-NOJARGON-B1-KEYPHRASE
#
# 目的:
#  (1) A2 Reader-facing本文のNo Jargon(既存Production正式原則、
#      CURRENT_SPEC.md「No Jargon」行、PRODUCTION_WIRED)個別非遵守を、
#      既存の正式Local Rewrite経路(er010_ledger_local_rewrite_09.py:
#      rewrite_ng_item/apply_diff_qa_to_resolved_rewrite/apply_rewrites/
#      extract_point_context/split_sentences)へ「No Jargon違反」という
#      独自issue/explanationを乗せて適用し、専門語を平易な語へ言い換える。
#      新しいNo Jargon Validator/Checker/QAは追加しない(既存のLedger
#      Deviation Checker[hook_aware]による受理判定+既存Fact Checker A'
#      による差分QAをそのまま安全装置として使う)。
#  (2) 同一Verified Fact Ledgerを再利用し、Production正式関数
#      er003_discovery_focus_staged_production_01.run_one_pattern_staged_
#      discovery_focus(level="b1b")でB1Bを新規生成する(Research再実行なし)。
#  (3) 修正版A2・生成済みB1Bそれぞれについて、Production正式Key Phrase
#      経路 er003_v1_n3_01_scaffold_generate.run_key_phrases()(選定→
#      Canonicalization→Key Phrase Set Redundancy QA)でKey Phraseを
#      再生成する(旧記事由来のKey Phraseは再利用しない)。
#
# 費用上限: BUDGET_JPY(既定130円、本タスクの新規API call分のみ。
# 既存raw_usage_log.jsonlに混ざっている前回[A2初回生成]分の実測コスト
# [cost_baseline_jpy]は起動時に一度だけ計測し、以後の累計から差し引いた
# 「本タスクの増分」でガードする)。実行時ガードは
# er014_output/four_type_observation_01/discovery/run_discovery_a2.pyと
# 同一方式(er005_cost_logger.record()をラップし、API call 1回完了ごとに
# 増分JPYを再計算、超過したらRuntimeErrorで停止)。
# ============================================================
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import er002_ja_web_research_r3 as r3
import er003_discovery_focus_staged_production_01 as s2prod
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as artgen
import er003_v1_n3_01_scaffold_generate as scaffold_gen
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_directional_fact_precheck_08 as dfp
import er010_ledger_local_rewrite_09 as local_rewrite
import er011_open146_ledger_canonical_en_spelling_production_01 as canon_spelling

THEME_ID = "discovery_why_silence_uncomfortable_a2"
BASE_DIR = "er014_output/four_type_observation_01/discovery"
RESEARCH_DIR = f"{BASE_DIR}/research"
LOG_PATH = f"{BASE_DIR}/raw_usage_log.jsonl"
BUDGET_JPY = 130.0
REASONING_EFFORT = vfl01.REASONING_EFFORT

# run_discovery_a2.pyと同一のTOPIC_EN(Ledger/A2生成時に使用した文字列を
# そのまま再利用。Fact Checker A'差分QA・B1B生成のtopic_ja引数にも
# 同一文字列を渡す)。
TOPIC_EN = (
    "Discovery topic: why can silence feel uncomfortable? Aim: research "
    "psychological and behavioral science findings about why many people "
    "find silence -- especially unexpected silence in conversation, or "
    "being alone without any stimulation or activity -- uncomfortable or "
    "unpleasant. Cover findings such as: research on awkward or "
    "uncomfortable silences in conversation, research on people's general "
    "preference for having something to do rather than sitting alone with "
    "only their own thoughts (including studies where participants chose "
    "to self-administer a mild electric shock rather than sit quietly "
    "with their thoughts), physiological or arousal responses associated "
    "with silence or unstructured alone time, and any documented "
    "individual or cultural variation in how comfortable people are with "
    "silence. Use only facts confirmed by web search (no invented "
    "details, no facts supplied from the assistant's own prior "
    "knowledge)."
)

PRICING_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0


def _load_pricing():
    with open(PRICING_PATH, encoding="utf-8") as f:
        return json.load(f)["prices"]


PRICING = _load_pricing()


def _price(provider, model, meter, tier="Standard"):
    return next(p["price"] for p in PRICING if p["provider"] == provider and p["model"] == model
                and p["meter"] == meter and p.get("tier", "Standard") == tier)


def _call_cost_usd(rec: dict) -> float:
    provider, model = rec.get("provider"), rec.get("model_id")
    if provider != "openai":
        return 0.0
    it, ot = rec.get("input_tokens") or 0, rec.get("output_tokens") or 0
    ct = rec.get("cached_input_tokens") or 0
    billable_in = max(it - ct, 0)
    in_price = _price("openai", model, "input_tokens")
    cached_price = _price("openai", model, "cached_input_tokens")
    out_price = _price("openai", model, "output_tokens")
    cost = (billable_in / 1e6) * in_price + (ct / 1e6) * cached_price + (ot / 1e6) * out_price
    web_search_calls = rec.get("web_search_call_count") or 0
    web_search_price = _price("openai", "N/A (tool, all models)", "web_search_call")
    cost += (web_search_calls / 1000) * web_search_price
    return cost


def _lines_cost_jpy(lines: list) -> float:
    total_usd = 0.0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if rec.get("success") is False:
            continue
        total_usd += _call_cost_usd(rec)
    return total_usd * USD_JPY


def cost_total_jpy() -> float:
    if not os.path.exists(LOG_PATH):
        return 0.0
    with open(LOG_PATH, encoding="utf-8") as f:
        return _lines_cost_jpy(f.readlines())


# ============================================================
# No Jargon個別非遵守 検出(決定的grep、新Validatorではなく本ドライバの
# 検出/報告専用ロジック)。委任文指定リスト+reader_facing_article.txtで
# 見つかった同種語。
# ============================================================
JARGON_PATTERNS = [
    r"parasympathetic", r"sympathetic activity", r"\bfMRI\b", r"\bEKG\b",
    r"counterbalanced", r"acoustic noise", r"need for cognition",
    r"physiological arousal", r"positive affect", r"\bcorrelates\b",
]

TERM_HINTS = {
    "parasympathetic": "the body's calming, rest-and-digest nervous system activity",
    "sympathetic activity": "the body's alert, stress-response nervous system activity",
    "fmri": "the MRI scanner (its noise)",
    "ekg": "a heart-monitoring device/experiment",
    "counterbalanced": "with the order of conditions balanced so no condition had an unfair advantage",
    "acoustic noise": "noise/sound",
    "need for cognition": "how much someone naturally enjoys thinking things through",
    "physiological arousal": "the body's measured activation level",
    "positive affect": "being in a good mood",
    "correlates": "things that showed up together in the data, not things proven to cause it",
}


def jargon_scan(text: str) -> dict:
    hits = []
    for pat in JARGON_PATTERNS:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            hits.append({"pattern": pat, "match": m.group(0), "start": m.start()})
    return {"hit_count": len(hits), "hits": hits}


def find_jargon_blocks(article_text: str) -> list:
    """split_sentences()(既存local_rewrite関数)で文単位に分割し、
    専門語を含む文のindexを特定、隣接するindexは1つのRewrite対象
    block(複数文)へまとめる(委任文のEKG段落=2文の例に対応)。"""
    sentences = local_rewrite.split_sentences(article_text)
    flagged = [i for i, s in enumerate(sentences) if jargon_scan(s)["hit_count"] > 0]
    if not flagged:
        return []
    blocks = []
    start = prev = flagged[0]
    for i in flagged[1:]:
        if i == prev + 1:
            prev = i
            continue
        blocks.append((start, prev))
        start = prev = i
    blocks.append((start, prev))
    result = []
    for (i1, i2) in blocks:
        target = " ".join(sentences[i1:i2 + 1])
        before = sentences[i1 - 1] if i1 - 1 >= 0 else ""
        after = sentences[i2 + 1] if i2 + 1 < len(sentences) else ""
        terms = sorted({h["match"] for h in jargon_scan(target)["hits"]})
        result.append({"target": target, "before": before, "after": after, "terms": terms})
    return result


def build_deviation_for_block(block: dict) -> dict:
    terms = block["terms"]
    hint_lines = []
    for t in terms:
        hint = TERM_HINTS.get(t.lower())
        if hint:
            hint_lines.append(f"'{t}' -> {hint}")
    issue = (
        "No Jargon violation (existing Production Writer principle, PRODUCTION_WIRED; "
        "this is NOT a Ledger fact error). This sentence uses technical/academic/"
        "physiological jargon that a general listener cannot understand by ear: "
        f"{', '.join(repr(t) for t in terms)}. Rewrite in plain, natural spoken English "
        "that a non-expert listener can follow, without inventing new facts, without "
        "changing which condition/group was compared to which, without changing the "
        "direction of any comparison, without changing the strength/certainty of the "
        "claim, and without adding or removing any item from any list of factors "
        "mentioned in the sentence."
    )
    explanation = (
        "Suggested plain-language meaning for each flagged term (you may adjust wording "
        "for natural flow, but keep exactly the same meaning): "
        + ("; ".join(hint_lines) if hint_lines else "(no specific hint available; "
           "just explain the term's meaning in plain everyday words)")
    )
    return {"issue": issue, "explanation": explanation}


def fix_all_jargon(article_text: str, ledger_model: str, topic: str, label: str, client,
                    verified_ledger_text: str) -> dict:
    """委任文(1)(a)優先経路: 既存rewrite_ng_item+apply_diff_qa_to_resolved_
    rewrite(Fact Checker A'+Ledger Deviation Checker、Hook-aware)を、
    自動検出したNo Jargon違反文へ適用する。受理後もjargon_scanで残存が
    無いか確認し、残存する場合のみ最大2回、同じgenerate_rewrite()
    (既存関数)を使った追加escalationを行う(新規Validator/機構ではない、
    既存のbuilding blockの追加呼び出し)。"""
    fact_checker_model = routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL)

    def check_window(window_text: str) -> dict:
        with cl.logging_context(THEME_ID, f"{label}_jargon_fix_ledger_check"):
            return vfl01.run_deviation_check(client, verified_ledger_text, window_text,
                                              model=ledger_model, hook_aware=True)["parsed"]

    blocks = find_jargon_blocks(article_text)
    block_results = []
    for block in blocks:
        deviation = build_deviation_for_block(block)
        point_context = local_rewrite.extract_point_context(article_text, block["target"])
        point_context_found = point_context is not None
        if point_context is None:
            point_context = f"{block['before']} {block['target']} {block['after']}".strip()
        with cl.logging_context(THEME_ID, f"{label}_jargon_fix_rewrite"):
            r = local_rewrite.rewrite_ng_item(
                client, ledger_model, REASONING_EFFORT, verified_ledger_text,
                point_context, block["target"], deviation, block["before"], block["after"],
                check_window, use_target_sentence_matching=True)
        with cl.logging_context(THEME_ID, f"{label}_jargon_fix_diff_qa"):
            r = local_rewrite.apply_diff_qa_to_resolved_rewrite(
                r, client, topic, block["before"], block["after"], verified_ledger_text,
                ledger_model, fact_checker_model)
        r["point_context_found"] = point_context_found
        r["terms_detected"] = block["terms"]

        manual_rounds = []
        for esc in range(2):
            candidate = r.get("final_text")
            if not candidate:
                break
            remaining = jargon_scan(candidate)
            if remaining["hit_count"] == 0:
                break
            esc_prompt = (
                "The following sentence(s) still contain jargon/technical terms that must "
                "be replaced with plain spoken English, without changing the facts, scope, "
                "causality, or certainty:\n\n" + candidate + "\n\nRemaining jargon terms "
                f"found: {[h['match'] for h in remaining['hits']]}\n\nRewrite the sentence(s) "
                "again, replacing ONLY these jargon terms with plain, everyday spoken English "
                "while keeping every other fact, comparison, and hedge word unchanged. Return "
                "only the revised sentence(s)."
            )
            with cl.logging_context(THEME_ID, f"{label}_jargon_fix_manual_escalation"):
                new_text = local_rewrite.generate_rewrite(client, ledger_model, REASONING_EFFORT, esc_prompt)
                check = check_window(f"{block['before']} {new_text} {block['after']}".strip())
            manual_rounds.append({
                "round": esc + 1, "candidate_before_round": candidate,
                "jargon_remaining_before_round": remaining, "new_text": new_text,
                "ledger_status": check["overall_status"],
            })
            if check["overall_status"] == "LEDGER_COMPLIANT":
                r["final_text"] = new_text
                r["resolved"] = True
                r["human_review_required"] = False
            else:
                r["resolved"] = False
                r["human_review_required"] = True
                break
        r["manual_escalation_rounds"] = manual_rounds
        r["jargon_after"] = jargon_scan(r.get("final_text") or "")
        block_results.append(r)

    updated_text = local_rewrite.apply_rewrites(article_text, block_results) if block_results else article_text
    updated_text = artgen.normalize_article_formatting(updated_text)
    return {"updated_text": updated_text, "block_results": block_results, "blocks_detected": blocks}


def run_final_qa(article_text: str, verified_ledger_text: str, ledger_model: str, topic: str,
                  out_dir: str, vfl_path: str, client, label: str) -> dict:
    """委任文(1)後段: 修正後にFact Checker A'/Ledger Deviation Checker
    (Hook-aware)/Directional Fact Precheckを通常どおり実行する(既存
    Production final QA、er003_discovery_focus_staged_production_01.py
    Stage2-3終了後の処理と同一パターン)。"""
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    canonical_spelling_block = canon_spelling.build_canonical_spelling_fact_check_block(verified_ledger_text)
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [], canonical_spelling_block=canonical_spelling_block)

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    with cl.logging_context(THEME_ID, f"{label}_final_fact_checker"):
        fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
            r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    fact_verdict = fc_result.get("verdict") if fc_result else None
    with open(f"{out_dir}/audit/post_fix_fact_qa.json", "w", encoding="utf-8") as f:
        json.dump({"final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
                    "attempts": len(fc_attempts), "result": fc_result}, f, ensure_ascii=False, indent=2, default=str)

    with cl.logging_context(THEME_ID, f"{label}_final_ledger_check"):
        deviation_result = vfl01.run_deviation_check(client, verified_ledger_text, article_text,
                                                       model=ledger_model, hook_aware=True)
    with open(f"{out_dir}/audit/post_fix_ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2, default=str)

    with cl.logging_context(THEME_ID, f"{label}_final_directional_precheck"):
        directional_result = dfp.audit_article_directional_facts(article_text, verified_ledger_text, vfl_path=vfl_path)
    with open(f"{out_dir}/audit/post_fix_directional_fact_precheck.json", "w", encoding="utf-8") as f:
        json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)

    return {
        "fact_checker_status": fc_status, "fact_checker_verdict": fact_verdict,
        "ledger_deviation_overall_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_major_count": len([d for d in deviation_result["parsed"]["deviations"]
                                              if d["severity"] == "MAJOR"]),
        "directional_fact_precheck_status": directional_result["overall_status"],
    }


def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    cl.install(LOG_PATH)

    baseline_lines = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, encoding="utf-8") as f:
            baseline_lines = f.readlines()
    baseline_line_count = len(baseline_lines)
    baseline_cost_jpy = _lines_cost_jpy(baseline_lines)
    print(f"[{THEME_ID}][FIX] baseline(前回分)line_count={baseline_line_count} "
          f"baseline_cost_jpy=¥{baseline_cost_jpy:.2f}(このタスクの予算計算からは除外)")

    _original_record = cl.record

    def _record_with_budget_guard(entry: dict) -> None:
        _original_record(entry)
        total = cost_total_jpy()
        incremental = total - baseline_cost_jpy
        if incremental > BUDGET_JPY:
            raise RuntimeError(
                f"費用上限超過(本タスク増分実測¥{incremental:.2f} > 上限¥{BUDGET_JPY:.2f})。STOP。"
                f"(driver側実行時budget guard、Production関数のロジックは無変更)")

    cl.record = _record_with_budget_guard

    started_at = datetime.now(timezone.utc).isoformat()
    client = vfl01.get_client()

    # ---- Ledger再利用(Research再実行なし) ----
    with open(f"{RESEARCH_DIR}/verified_fact_ledger.txt", encoding="utf-8") as f:
        verified_ledger_text = f.read()
    vfl_path = f"{RESEARCH_DIR}/stage_b3_vfl.json"

    result = {"started_at": started_at, "budget_jpy": BUDGET_JPY, "baseline_cost_jpy": round(baseline_cost_jpy, 2)}

    # ================================================================
    # (0) A2旧版の退避
    # ================================================================
    os.makedirs(f"{BASE_DIR}/a2_before_fix", exist_ok=True)
    if os.path.isdir(f"{BASE_DIR}/a2") and not os.path.isdir(f"{BASE_DIR}/a2_before_fix/a2"):
        shutil.copytree(f"{BASE_DIR}/a2", f"{BASE_DIR}/a2_before_fix/a2")
    for fname in ["reader_facing_article.txt", "run_result.json", "cost_summary.json"]:
        src = f"{BASE_DIR}/{fname}"
        if os.path.exists(src):
            shutil.copy2(src, f"{BASE_DIR}/a2_before_fix/{fname}")

    with open(f"{BASE_DIR}/reader_facing_article.txt", encoding="utf-8") as f:
        a2_article_text = f.read()

    jargon_scan_before = {"a2": jargon_scan(a2_article_text)}
    with open(f"{BASE_DIR}/jargon_scan_before.json", "w", encoding="utf-8") as f:
        json.dump(jargon_scan_before, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}][FIX] A2 jargon scan(before): hit_count="
          f"{jargon_scan_before['a2']['hit_count']}")

    rewrite_log_lines = ["# Discovery No Jargon Fix / B1B / Key Phrase - rewrite_log\n"]

    # ================================================================
    # (1) A2 No Jargon修正(既存rewrite_ng_item経路優先)
    # ================================================================
    ledger_model_a2 = routing.require_model("A2_WRITER", routing.WRITER_MODEL)
    a2_fix = fix_all_jargon(a2_article_text, ledger_model_a2, TOPIC_EN, "a2", client, verified_ledger_text)
    a2_fixed_text = a2_fix["updated_text"]

    a2_route_used = "local_rewrite_existing_path(rewrite_ng_item+apply_diff_qa_to_resolved_rewrite)"
    a2_needs_regeneration_fallback = any(
        (not br.get("resolved")) or br.get("human_review_required") for br in a2_fix["block_results"])

    rewrite_log_lines.append("## A2 修正\n")
    rewrite_log_lines.append(f"使用経路: {a2_route_used}(理由: 委任文(1)(a)優先指示)\n")
    for br in a2_fix["block_results"]:
        rewrite_log_lines.append(f"- terms_detected: {br['terms_detected']}\n")
        rewrite_log_lines.append(f"  旧: {br['original_ng_sentence']}\n")
        rewrite_log_lines.append(f"  新: {br['final_text']}\n")
        rewrite_log_lines.append(f"  resolved={br['resolved']} human_review_required="
                                  f"{br['human_review_required']} attempts={len(br['attempts'])} "
                                  f"manual_escalation_rounds={len(br['manual_escalation_rounds'])}\n")
        rewrite_log_lines.append(f"  diff_qa: applied={br['diff_qa']['applied']} "
                                  f"blocks_acceptance={br['diff_qa'].get('blocks_acceptance')}\n")
        rewrite_log_lines.append(f"  jargon_after: hit_count={br['jargon_after']['hit_count']}\n\n")

    if a2_needs_regeneration_fallback:
        result["a2_fix_status"] = "STOP_HUMAN_REVIEW_REQUIRED"
        result["a2_fix_reason"] = ("既存rewrite経路で専門語を除去しつつFactの意味を維持する書き換えが"
                                    "3+2回の試行内で受理されなかった(diff QAがblocks_acceptance=True、"
                                    "またはLedger Deviation Checkerが不合格)。Factの意味を変えずに"
                                    "専門語だけ除去できないケースのためSTOP。")
        with open(f"{BASE_DIR}/rewrite_log.md", "w", encoding="utf-8") as f:
            f.writelines(rewrite_log_lines)
        with open(f"{BASE_DIR}/run_result_fix.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}][FIX] STOP: {result['a2_fix_reason']}")
        return result

    # 修正版A2を確定
    with open(f"{BASE_DIR}/reader_facing_article.txt", "w", encoding="utf-8") as f:
        f.write(a2_fixed_text)
    with open(f"{BASE_DIR}/a2/article.md", "w", encoding="utf-8") as f:
        f.write(a2_fixed_text)

    jargon_scan_a2_after = jargon_scan(a2_fixed_text)
    print(f"[{THEME_ID}][FIX] A2 jargon scan(after fix): hit_count={jargon_scan_a2_after['hit_count']}")

    a2_final_qa = run_final_qa(a2_fixed_text, verified_ledger_text, ledger_model_a2, TOPIC_EN,
                                f"{BASE_DIR}/a2", vfl_path, client, "a2")
    print(f"[{THEME_ID}][FIX] A2 final QA: {a2_final_qa}")

    result["a2_fix_status"] = "OK"
    result["a2_route_used"] = a2_route_used
    result["a2_block_results_summary"] = [
        {"terms_detected": br["terms_detected"], "resolved": br["resolved"],
         "human_review_required": br["human_review_required"],
         "attempts": len(br["attempts"]), "manual_escalation_rounds": len(br["manual_escalation_rounds"])}
        for br in a2_fix["block_results"]
    ]
    result["a2_final_qa"] = a2_final_qa
    result["a2_jargon_after"] = jargon_scan_a2_after

    # ================================================================
    # (2) B1B生成(同一Ledger、Production正式関数)
    # ================================================================
    incremental_so_far = cost_total_jpy() - baseline_cost_jpy
    if incremental_so_far >= BUDGET_JPY:
        result["b1b_status"] = "STOP_BUDGET_EXCEEDED_BEFORE_B1B"
        with open(f"{BASE_DIR}/rewrite_log.md", "w", encoding="utf-8") as f:
            f.writelines(rewrite_log_lines)
        with open(f"{BASE_DIR}/run_result_fix.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}][FIX] STOP: B1B開始前に予算(増分¥{incremental_so_far:.2f})へ到達。")
        return result

    b1b_out_dir = f"{BASE_DIR}/b1b"
    os.makedirs(f"{b1b_out_dir}/audit", exist_ok=True)
    print(f"[{THEME_ID}][FIX] run_one_pattern_staged_discovery_focus(B1B)開始...")
    t0 = time.time()
    try:
        b1b_gen_result = s2prod.run_one_pattern_staged_discovery_focus(
            client=client, level="b1b", topic_ja=TOPIC_EN, verified_ledger_text=verified_ledger_text,
            out_dir=b1b_out_dir, theme_tag=f"{THEME_ID}_b1b_fix", vfl_path=vfl_path,
        )
        b1b_budget_stop_reason = None
    except RuntimeError as e:
        if "費用上限超過" not in str(e):
            raise
        b1b_gen_result = {"status": "STOP_BUDGET_EXCEEDED_MIDRUN", "article_text": None}
        b1b_budget_stop_reason = str(e)
    elapsed = round(time.time() - t0, 2)
    print(f"[{THEME_ID}][FIX] B1B生成完了: status={b1b_gen_result.get('status')} elapsed={elapsed}s")

    result["b1b_status"] = b1b_gen_result.get("status")
    result["b1b_budget_stop_reason_midrun"] = b1b_budget_stop_reason
    result["b1b_elapsed_seconds"] = elapsed

    if not b1b_gen_result.get("article_text"):
        with open(f"{BASE_DIR}/rewrite_log.md", "w", encoding="utf-8") as f:
            f.writelines(rewrite_log_lines)
        with open(f"{BASE_DIR}/run_result_fix.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}][FIX] STOP: B1B article_textが得られませんでした(status={result['b1b_status']})。")
        return result

    b1b_article_text = b1b_gen_result["article_text"]
    with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", "w", encoding="utf-8") as f:
        f.write(b1b_article_text)

    jargon_scan_b1b_before = jargon_scan(b1b_article_text)
    print(f"[{THEME_ID}][FIX] B1B jargon scan(生成直後): hit_count={jargon_scan_b1b_before['hit_count']}")

    rewrite_log_lines.append("## B1B\n")
    rewrite_log_lines.append(f"生成直後 jargon scan hit_count={jargon_scan_b1b_before['hit_count']}\n\n")

    b1b_final_text = b1b_article_text
    b1b_fix_applied = False
    if jargon_scan_b1b_before["hit_count"] > 0:
        b1b_fix_applied = True
        ledger_model_b1b = routing.require_model("B1_WRITER", routing.WRITER_MODEL)
        b1b_fix = fix_all_jargon(b1b_article_text, ledger_model_b1b, TOPIC_EN, "b1b", client, verified_ledger_text)
        b1b_final_text = b1b_fix["updated_text"]
        for br in b1b_fix["block_results"]:
            rewrite_log_lines.append(f"- B1B terms_detected: {br['terms_detected']}\n")
            rewrite_log_lines.append(f"  旧: {br['original_ng_sentence']}\n")
            rewrite_log_lines.append(f"  新: {br['final_text']}\n")
            rewrite_log_lines.append(f"  resolved={br['resolved']} human_review_required="
                                      f"{br['human_review_required']}\n\n")
        with open(f"{b1b_out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(b1b_final_text)
        with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", "w", encoding="utf-8") as f:
            f.write(b1b_final_text)
        ledger_model_b1b_final_qa = run_final_qa(b1b_final_text, verified_ledger_text, ledger_model_b1b, TOPIC_EN,
                                                   b1b_out_dir, vfl_path, client, "b1b")
        result["b1b_final_qa_post_fix"] = ledger_model_b1b_final_qa

    jargon_scan_b1b_after = jargon_scan(b1b_final_text)
    print(f"[{THEME_ID}][FIX] B1B jargon scan(final): hit_count={jargon_scan_b1b_after['hit_count']}")

    result["b1b_fix_applied"] = b1b_fix_applied
    result["b1b_jargon_before"] = jargon_scan_b1b_before
    result["b1b_jargon_after"] = jargon_scan_b1b_after
    result["b1b_word_count"] = b1b_gen_result.get("word_count")

    with open(f"{BASE_DIR}/jargon_scan_after.json", "w", encoding="utf-8") as f:
        json.dump({"a2": jargon_scan_a2_after, "b1b": jargon_scan_b1b_after}, f, ensure_ascii=False, indent=2)

    # ================================================================
    # (3) Key Phrase再生成(A2/B1B、Production正式経路)
    # ================================================================
    incremental_so_far = cost_total_jpy() - baseline_cost_jpy
    if incremental_so_far >= BUDGET_JPY:
        result["key_phrase_status"] = "STOP_BUDGET_EXCEEDED_BEFORE_KEY_PHRASE"
        with open(f"{BASE_DIR}/rewrite_log.md", "w", encoding="utf-8") as f:
            f.writelines(rewrite_log_lines)
        with open(f"{BASE_DIR}/run_result_fix.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}][FIX] STOP: Key Phrase開始前に予算(増分¥{incremental_so_far:.2f})へ到達。")
        return result

    kp_dir_a2 = f"{BASE_DIR}/key_phrases/a2"
    kp_dir_b1b = f"{BASE_DIR}/key_phrases/b1b"
    print(f"[{THEME_ID}][FIX] Key Phrase再生成(A2)開始...")
    kp_a2 = scaffold_gen.run_key_phrases(a2_fixed_text, kp_dir_a2, f"{THEME_ID}_a2_fix",
                                          "A2(V2改1, N3-01, jargon-fix)", process="A2_SUPPORT")
    kp_a2_status = (kp_a2["canonicalization"] or {}).get("status") if kp_a2["canonicalization"] else kp_a2["selection"]["status"]
    print(f"[{THEME_ID}][FIX] Key Phrase(A2) status={kp_a2_status}")

    print(f"[{THEME_ID}][FIX] Key Phrase再生成(B1B)開始...")
    kp_b1b = scaffold_gen.run_key_phrases(b1b_final_text, kp_dir_b1b, f"{THEME_ID}_b1b",
                                           "B1-B(N3-01, direct generation)", process="B1_SUPPORT")
    kp_b1b_status = (kp_b1b["canonicalization"] or {}).get("status") if kp_b1b["canonicalization"] else kp_b1b["selection"]["status"]
    print(f"[{THEME_ID}][FIX] Key Phrase(B1B) status={kp_b1b_status}")

    result["key_phrase_status"] = "OK"
    result["key_phrase_a2_status"] = kp_a2_status
    result["key_phrase_b1b_status"] = kp_b1b_status
    result["key_phrase_a2_redundancy_qa"] = kp_a2.get("redundancy_qa")
    result["key_phrase_b1b_redundancy_qa"] = kp_b1b.get("redundancy_qa")

    with open(f"{BASE_DIR}/rewrite_log.md", "w", encoding="utf-8") as f:
        f.writelines(rewrite_log_lines)

    # ================================================================
    # 費用/ログの最終集計
    # ================================================================
    finished_at = datetime.now(timezone.utc).isoformat()
    with open(LOG_PATH, encoding="utf-8") as f:
        all_lines = f.readlines()
    new_lines = all_lines[baseline_line_count:]
    with open(f"{BASE_DIR}/raw_usage_log_fix_task_only.jsonl", "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # stage tag別の内訳(本ドライバが明示的にcl.logging_contextで付与した
    # stageタグを利用。B1B生成内部(s2prod)のstageタグはそのまま尊重する)。
    stage_breakdown = {}
    for line in new_lines:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if rec.get("success") is False:
            continue
        stage = rec.get("stage") or "unknown"
        cost_jpy = _call_cost_usd(rec) * USD_JPY
        b = stage_breakdown.setdefault(stage, {"calls": 0, "cost_jpy": 0.0})
        b["calls"] += 1
        b["cost_jpy"] += cost_jpy
    for b in stage_breakdown.values():
        b["cost_jpy"] = round(b["cost_jpy"], 2)

    this_task_cost_jpy = round(_lines_cost_jpy(new_lines), 2)

    cost_summary_fix = {
        "started_at": started_at, "finished_at": finished_at, "budget_jpy": BUDGET_JPY,
        "baseline_cost_jpy_excluded": round(baseline_cost_jpy, 2),
        "this_task_cost_jpy": this_task_cost_jpy,
        "budget_exceeded": this_task_cost_jpy > BUDGET_JPY,
        "new_api_calls": len(new_lines),
        "cost_breakdown_by_stage_jpy": stage_breakdown,
    }
    with open(f"{BASE_DIR}/cost_summary_fix.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary_fix, f, ensure_ascii=False, indent=2, default=str)

    result["finished_at"] = finished_at
    result["this_task_cost_jpy"] = this_task_cost_jpy
    result["budget_exceeded"] = this_task_cost_jpy > BUDGET_JPY

    with open(f"{BASE_DIR}/run_result_fix.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print(f"[{THEME_ID}][FIX] 完了。本タスク実測費用=¥{this_task_cost_jpy:.2f}"
          f"(予算=¥{BUDGET_JPY:.2f}, exceeded={cost_summary_fix['budget_exceeded']})")
    return result


if __name__ == "__main__":
    main()
    sys.exit(0)
