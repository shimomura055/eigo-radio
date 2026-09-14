# ============================================================
# er014_output/four_type_observation_01/discovery/run_discovery_a2.py
# 管理ID: EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01
#   (記事3/4: Discovery S2)
#
# 目的: 既存Production記事タイプ(Discovery S2、`PRODUCTION_WIRED`)の
# 「正常生成観測」。新しいPrompt/QA/retry方式/Validator/Story構造/
# Model routing/Production wiringは一切変更しない。
#
# Research→Verified Fact Ledger作成は、News/Trend driverと同一の
# client呼び出し構造(vfl01.build_researcher_prompt/build_verification_
# prompt + client.responses.create、web_search tool)を、topicのみ本
# タスクのTOPIC_ENへ差し替えて再現する(コピー関数の新規発明ではなく、
# er014_output/four_type_observation_01/news/run_news_a2.pyの
# run_researcher_for_topic/run_verification_for_topic/build_ledgerと
# 同一実装を、出力先ディレクトリだけ差し替えて再利用)。
#
# 記事生成自体は、Production正式関数 er003_discovery_focus_staged_
# production_01.run_one_pattern_staged_discovery_focus() をそのまま
# 呼び出す(monkeypatch・再実装なし)。呼び出し引数の型は
# er011_output/discovery_s2_production_runtime_evidence_02/
# run_happy_path_a2.pyの前例に準拠する。同ファイルの引数名は
# `topic_ja`だが、News/Trend driverの前例(TOPIC_EN=英語文字列を
# prod_gen.build_common_block()の同位置引数へ渡し正常完走した実績)から、
# この引数は実際には言語を問わない単なる「topicとして本文プロンプトへ
# 展開される文字列」であり、英語文字列を渡しても仕様上問題ない
# (Production関数のロジック自体は完全に無変更)。
#
# 出力先: er014_output/four_type_observation_01/discovery/
#   research/ (fact_ledger_draft.json, fact_ledger_verification.json,
#              verified_fact_ledger.txt, verified_fact_ledger_structured.json,
#              stage_b3_vfl.json)
#   a2/       (run_one_pattern_staged_discovery_focus()がaudit/等一式を
#              出力する場所。dirname(a2)=discovery/ の直下にresearch/が
#              あるため、Directional Fact Precheckが期待する
#              vfl_path=research/stage_b3_vfl.jsonをそのまま明示的に渡す)
#   reader_facing_article.txt (article_textをそのまま保存、本ドライバが追加)
#   run_result.json (production関数の戻り値[article_text除く]、本ドライバが追加)
#   raw_usage_log.jsonl (er005_cost_logger.installによる全API call実測ログ)
#   cost_summary.json (本ドライバが概算した費用サマリ)
#
# 費用上限: BUDGET_JPY(既定140円)。
#   (1) 事前ゲート: Research/Verification完了時点で既にBUDGET_JPYへ到達/
#       超過している場合は、Writer(run_one_pattern_staged_discovery_focus)
#       を呼び出さずSTOPする(News driverと同一方針)。
#   (2) 実行時ガード: er011_output/discovery_s2_production_runtime_
#       evidence_02/run_happy_path_a2.pyの前例と同一方式で、
#       er005_cost_logger.record()をラップし、API call 1回完了ごとに
#       累積JPYを再計算、BUDGET_JPYを超えたらRuntimeErrorを送出して
#       停止する(Discovery S2はStage1再生成/Stage2-3 retry/Point
#       Overlap retryにより実行を分割できないため、事後の一括ゲートでは
#       間に合わない。Production関数のロジック自体は無変更、外側の
#       計測フックのみを包む安全装置)。
#
# 改善禁止(ユーザー明示): Point Overlap retryが発生した場合も、本
# ドライバはそれを検知して回避・最適化する処理を一切行わない。発生
# したらそのまま記録する(OPEN-148、HIGH、意図的defer)。
# ============================================================
from __future__ import annotations

import json
import os
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
import er005_cost_logger as cl

THEME_ID = "discovery_why_silence_uncomfortable_a2"
BASE_DIR = "er014_output/four_type_observation_01/discovery"
RESEARCH_DIR = f"{BASE_DIR}/research"
ARTICLE_OUT_DIR = f"{BASE_DIR}/a2"
LOG_PATH = f"{BASE_DIR}/raw_usage_log.jsonl"

TOPIC_ID = "why_silence_uncomfortable"
LEVEL = "a2"
BUDGET_JPY = 140.0

# ユーザー指示原文のTopicを、Researcher/Writer両方へ渡すtopic文として
# 使う(Sonnet自身の知識で事実を補わない。Ledgerの事実はweb_search由来の
# VERIFIED[CONFIRMED]のみ)。
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


def cost_so_far_jpy() -> float:
    if not os.path.exists(LOG_PATH):
        return 0.0
    total_usd = 0.0
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("success") is False:
                continue
            total_usd += _call_cost_usd(rec)
    return total_usd * USD_JPY


# ============================================================
# Research / Verification(er014_output/four_type_observation_01/news/
# run_news_a2.pyのrun_researcher_for_topic/run_verification_for_topic/
# build_ledgerと同一実装、出力先ディレクトリとtopicのみ差し替え)。
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


def build_ledger(client, topic: str, topic_id: str) -> dict:
    os.makedirs(RESEARCH_DIR, exist_ok=True)

    structured_path = f"{RESEARCH_DIR}/verified_fact_ledger_structured.json"
    ledger_txt_path = f"{RESEARCH_DIR}/verified_fact_ledger.txt"
    if os.path.exists(structured_path) and os.path.exists(ledger_txt_path):
        with open(structured_path, encoding="utf-8") as f:
            structured = json.load(f)
        with open(ledger_txt_path, encoding="utf-8") as f:
            verified_ledger_text = f.read()
        print(f"[{THEME_ID}] Resume: 既存のresearch/成果物を再利用します"
              f"(API call再実行なし)。counts={structured['counts']}")
        cost = cost_so_far_jpy()
        return {"verified_ledger_text": verified_ledger_text, "counts": structured["counts"],
                "cost_jpy_after_ledger": cost}

    with cl.logging_context(THEME_ID, "researcher"):
        research_result = run_researcher_for_topic(client, topic)
    with open(f"{RESEARCH_DIR}/fact_ledger_draft.json", "w", encoding="utf-8") as f:
        json.dump(research_result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] Researcher完了: {len(research_result['parsed']['facts'])}件のFact下書き、"
          f"web_search={research_result['search_usage']}")

    with cl.logging_context(THEME_ID, "verification"):
        verification_result = run_verification_for_topic(client, topic, research_result["parsed"])
    with open(f"{RESEARCH_DIR}/fact_ledger_verification.json", "w", encoding="utf-8") as f:
        json.dump(verification_result, f, ensure_ascii=False, indent=2, default=str)

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
            lines.append(f"  numeric_value: {fact['numeric_value']} (numeric_scope: {fact.get('numeric_scope') or 'unspecified'})")
        if fact.get("date_or_period"):
            lines.append(f"  date_or_period: {fact['date_or_period']}")
        if fact.get("causal_strength") and fact["causal_strength"] != "NOT_APPLICABLE":
            lines.append(f"  causal_strength: {fact['causal_strength']}")
        if fact.get("notes_for_writer"):
            lines.append(f"  notes_for_writer: {fact['notes_for_writer']}")
        lines.append("")
    verified_ledger_text = "\n".join(lines)
    print(f"[{THEME_ID}] Verification完了: {counts}(CONFIRMED-onlyフィルタ適用後 kept={len(kept_facts)}件)")

    with open(f"{RESEARCH_DIR}/verified_fact_ledger.txt", "w", encoding="utf-8") as f:
        f.write(verified_ledger_text)
    with open(f"{RESEARCH_DIR}/verified_fact_ledger_structured.json", "w", encoding="utf-8") as f:
        json.dump({"topic": topic, "topic_id": topic_id, "kept_facts": kept_facts, "counts": counts,
                    "note": "CONFIRMED(VERIFIED)のみ採用。AMBIGUOUS/REJECTEDはfact_ledger_"
                            "verification.jsonに記録済みだが本Ledgerからは除外した。"},
                   f, ensure_ascii=False, indent=2)
    with open(f"{RESEARCH_DIR}/stage_b3_vfl.json", "w", encoding="utf-8") as f:
        json.dump({"parsed": research_result["parsed"]}, f, ensure_ascii=False, indent=2)

    cost = cost_so_far_jpy()
    print(f"[{THEME_ID}] Ledger作成完了。CONFIRMED(VERIFIED)={counts.get('VERIFIED', 0)}件、"
          f"AMBIGUOUS={counts.get('AMBIGUOUS', 0)}件。費用実測(累計): ¥{cost:.2f}")
    return {"verified_ledger_text": verified_ledger_text, "counts": counts, "cost_jpy_after_ledger": cost}


# ============================================================
# 実行時budget guard(er011_output/discovery_s2_production_runtime_
# evidence_02/run_happy_path_a2.pyと同一方式)。
# ============================================================
_original_record = cl.record


def _record_with_budget_guard(entry: dict) -> None:
    _original_record(entry)
    cost = cost_so_far_jpy()
    if cost > BUDGET_JPY:
        raise RuntimeError(
            f"費用上限超過(実測¥{cost:.2f} > 上限¥{BUDGET_JPY:.2f})。STOP。"
            f"(driver側実行時budget guard、Production関数のロジックは無変更)")


def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(f"{ARTICLE_OUT_DIR}/audit", exist_ok=True)
    cl.install(LOG_PATH)
    cl.record = _record_with_budget_guard
    started_at = datetime.now(timezone.utc).isoformat()

    client = vfl01.get_client()
    ledger_stage_result = build_ledger(client, TOPIC_EN, TOPIC_ID)
    verified_ledger_text = ledger_stage_result["verified_ledger_text"]
    counts = ledger_stage_result["counts"]

    if counts.get("VERIFIED", 0) == 0:
        result = {
            "status": "STOP_NO_CONFIRMED_FACTS", "reason": "Verification後にCONFIRMED(VERIFIED)"
            "件のFactが0件でした。記事を成立させられないためFact Safety上STOPします。",
            "counts": counts, "started_at": started_at, "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(f"{BASE_DIR}/run_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}] STOP: {result['reason']}")
        return result

    cost_after_ledger = ledger_stage_result["cost_jpy_after_ledger"]
    if cost_after_ledger >= BUDGET_JPY:
        result = {
            "status": "STOP_BUDGET_EXCEEDED", "reason": f"Research/Verification完了時点で費用実測"
            f"(累計)¥{cost_after_ledger:.2f}がBUDGET_JPY=¥{BUDGET_JPY:.2f}に到達/超過したため、"
            f"Writer(run_one_pattern_staged_discovery_focus)を実行せずSTOPします。",
            "counts": counts, "cost_jpy_after_ledger": cost_after_ledger,
            "started_at": started_at, "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(f"{BASE_DIR}/run_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}] STOP: {result['reason']}")
        return result

    print(f"[{THEME_ID}] run_one_pattern_staged_discovery_focus(A2)開始...")
    t0 = time.time()
    try:
        gen_result = s2prod.run_one_pattern_staged_discovery_focus(
            client=client,
            level=LEVEL,
            topic_ja=TOPIC_EN,
            verified_ledger_text=verified_ledger_text,
            out_dir=ARTICLE_OUT_DIR,
            theme_tag=THEME_ID,
            vfl_path=f"{RESEARCH_DIR}/stage_b3_vfl.json",
        )
        budget_stop_reason = None
    except RuntimeError as e:
        if "費用上限超過" not in str(e):
            raise
        gen_result = {"status": "STOP_BUDGET_EXCEEDED_MIDRUN", "article_text": None}
        budget_stop_reason = str(e)
    elapsed = round(time.time() - t0, 2)
    print(f"[{THEME_ID}] run_one_pattern_staged_discovery_focus(A2)完了: "
          f"status={gen_result.get('status')} elapsed={elapsed}s")

    finished_at = datetime.now(timezone.utc).isoformat()
    cost_final = cost_so_far_jpy()

    if gen_result.get("article_text"):
        with open(f"{BASE_DIR}/reader_facing_article.txt", "w", encoding="utf-8") as f:
            f.write(gen_result["article_text"])

    with open(f"{BASE_DIR}/run_result.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in gen_result.items() if k != "article_text"},
                   f, ensure_ascii=False, indent=2, default=str)

    result = {
        "status": gen_result.get("status"), "topic": TOPIC_EN, "topic_id": TOPIC_ID, "level": LEVEL,
        "counts": counts, "elapsed_seconds": elapsed, "cost_jpy_after_ledger": cost_after_ledger,
        "cost_jpy_final": cost_final, "started_at": started_at, "finished_at": finished_at,
        "budget_jpy": BUDGET_JPY, "budget_exceeded": cost_final > BUDGET_JPY,
        "budget_stop_reason_midrun": budget_stop_reason,
    }
    with open(f"{BASE_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] 完了: status={result['status']} 費用実測(累計)=¥{cost_final:.2f} "
          f"(budget=¥{BUDGET_JPY:.2f}, exceeded={result['budget_exceeded']})")
    return result


if __name__ == "__main__":
    main()
    sys.exit(0)
