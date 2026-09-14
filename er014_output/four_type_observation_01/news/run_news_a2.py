# ============================================================
# er014_output/four_type_observation_01/news/run_news_a2.py
# 管理ID: EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01
#   (記事1/4: News、Fable修正指示1回目)
#
# 目的: 既存Production記事タイプ(News/A2)の「正常生成観測」。新しい
# Prompt/QA/retry方式/Validator/Story構造/Model routing/Production
# wiringは一切変更しない。Research→Verified Fact Ledger作成は、
# 既存の承認済み先例(er011_news_stage3_new_theme_ledger_trial_09.py /
# er011_discovery_generalization_wake_before_alarm_trial_12_run.py)と
# 同一のclient呼び出し構造(vfl01.build_researcher_prompt/
# build_verification_prompt + client.responses.create、web_search
# tool)を、topicだけ本タスクのTopicへ差し替えて再現する(コピー関数の
# 新規発明ではなく、同型の呼び出しをtopicパラメータ化しただけ)。
# 記事生成自体は、Production関数 er003_v1_n3_01_articles_generate.
# run_one_pattern() をそのまま呼び出す(monkeypatch・再実装なし、
# editorial_mode=None相当[Focus Module/Point Role hintなし]のNews既定)。
#
# 出力先: er014_output/four_type_observation_01/news/
#   research/ (fact_ledger_draft.json, fact_ledger_verification.json,
#              verified_fact_ledger.txt, verified_fact_ledger_structured.json,
#              stage_b3_vfl.json)
#   a2/       (run_one_pattern()がaudit/等一式を出力する場所。
#              dirname(a2)=news/ の直下にresearch/があるため、
#              run_one_pattern内のDirectional Fact Precheckが期待する
#              vfl_path=f"{dirname(out_dir)}/research/stage_b3_vfl.json"
#              と自然に一致する。out_dirの相対位置を変えるだけで、
#              run_one_pattern自体には一切手を入れていない)。
#   reader_facing_article.txt (article_textをそのまま保存、本ドライバが追加)
#   run_result.json (run_one_pattern()の戻り値そのまま保存、本ドライバが追加)
#   raw_usage_log.jsonl (er005_cost_logger.installによる全API call実測ログ)
#   cost_summary.json (本ドライバが概算した費用サマリ)
#
# 費用上限: BUDGET_JPY(既定130円)。Research/Verification完了時点で
# 既にBUDGET_JPYを超過している場合は、Writer/QA(run_one_pattern)を
# 呼び出さずSTOPし、status="STOP_BUDGET_EXCEEDED"を記録して終了する
# (run_one_pattern自体は分割実行できないため、事前ゲートのみ)。
# ============================================================
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

# 本スクリプトはer014_output/four_type_observation_01/news/配下にあるため、
# repo root(実行時cwd、実行コマンドは常にC:\Users\tensh\eigo-radioから)を
# sys.pathへ追加する(repo root直下のer0xx_*.pyモジュールをimportするため。
# Production/Trialコード自体は無変更)。
sys.path.insert(0, os.getcwd())

# Windowsコンソール(cp932)は¥記号等を出力できずcrashするため、標準出力を
# utf-8へ明示的に再設定する(ロジック・Production処理には無関係、print()の
# 文字化け/クラッシュ防止のみ)。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl

THEME_ID = "news_ai_regulation_vs_ai_race_a2"
BASE_DIR = "er014_output/four_type_observation_01/news"
RESEARCH_DIR = f"{BASE_DIR}/research"
ARTICLE_OUT_DIR = f"{BASE_DIR}/a2"
LOG_PATH = f"{BASE_DIR}/raw_usage_log.jsonl"

TOPIC_ID = "ai_regulation_vs_ai_race"
LEVEL = "a2"
BUDGET_JPY = 130.0

# ユーザー指示原文のTopic+狙いを、そのままResearcher/Writer両方へ渡す
# topic文として使う(Sonnet自身の知識で事実を補わない。Ledgerの事実は
# web_search由来のVERIFIED[CONFIRMED]のみ)。
TOPIC_EN = (
    "Current news topic: the tension between AI regulation and the AI race. "
    "On one side, governments, regulators, and international bodies are pushing "
    "new AI safety rules, oversight requirements, and governance frameworks. "
    "On the other side, major AI companies and competing nations continue to "
    "race intensely to build and deploy more powerful AI systems faster than "
    "rivals. Aim: cover this tension between AI safety/regulation efforts and "
    "the competitive AI race as a current-events news story, using only facts "
    "confirmed by web search (no invented details, no facts supplied from the "
    "assistant's own prior knowledge)."
)

# er005_output/cost_baseline_01/pricing_snapshot.json(既存Production
# コスト計測基盤、読み取り専用で再利用。ここでは金額計算ロジックを一切
# 変更していない、er011_news_stage3_new_theme_ledger_trial_09.pyの
# _price/_call_cost_usd/compute_cost_so_far_jpyと同一ロジックの複製)。
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
# Research / Verification(先例: er011_discovery_generalization_wake_
# before_alarm_trial_12_run.py L277-315のrun_researcher_for_topic/
# run_verification_for_topicと同一のclient呼び出し構造。topicのみ
# 本タスクのTOPIC_ENへ差し替え)。
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

    # Resume guard(本タスク固有、Production機構ではない): 直前の実行が
    # Research/Verification完了後、print()のcp932エンコード例外で異常終了
    # した際に、同一API callを課金し直さないための再実行防止。research/
    # 配下の全成果物が既に揃っていればAPI呼び出しをスキップし、ディスクの
    # verified_fact_ledger.txt/countsをそのまま再利用する。
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

    # 先例(Trial-09)と同一方針: 全件CONFIRMED(VERIFIED)のみ採用、
    # AMBIGUOUS/REJECTEDは本Ledgerに含めない(未検証は本文へ含めない)。
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
    # Directional Fact Precheck Layer 1(vfl_internal、任意)向け、
    # Production同型のstage_b3_vfl.json形式で保存。
    with open(f"{RESEARCH_DIR}/stage_b3_vfl.json", "w", encoding="utf-8") as f:
        json.dump({"parsed": research_result["parsed"]}, f, ensure_ascii=False, indent=2)

    cost = cost_so_far_jpy()
    print(f"[{THEME_ID}] Ledger作成完了。CONFIRMED(VERIFIED)={counts.get('VERIFIED', 0)}件、"
          f"AMBIGUOUS={counts.get('AMBIGUOUS', 0)}件。費用実測(累計): ¥{cost:.2f}")
    return {"verified_ledger_text": verified_ledger_text, "counts": counts, "cost_jpy_after_ledger": cost}


def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    cl.install(LOG_PATH)
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
            f"Writer/QA(run_one_pattern)を実行せずSTOPします。",
            "counts": counts, "cost_jpy_after_ledger": cost_after_ledger,
            "started_at": started_at, "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(f"{BASE_DIR}/run_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}] STOP: {result['reason']}")
        return result

    master_full_text = ab01.load_master_full_text()
    common_block = prod_gen.build_common_block(master_full_text, TOPIC_EN, verified_ledger_text)
    prompt = prod_gen.build_prompt(common_block, prod_gen.A2_KAI1_INSTRUCTION)

    print(f"[{THEME_ID}] run_one_pattern(A2)開始...")
    t0 = time.time()
    with cl.logging_context(THEME_ID, "writer_a2"):
        gen_result = prod_gen.run_one_pattern(
            client, THEME_ID, "A2", prompt, verified_ledger_text, TOPIC_EN, ARTICLE_OUT_DIR)
    elapsed = round(time.time() - t0, 2)
    print(f"[{THEME_ID}] run_one_pattern(A2)完了: status={gen_result.get('status')} elapsed={elapsed}s")

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
    }
    with open(f"{BASE_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] 完了: status={result['status']} 費用実測(累計)=¥{cost_final:.2f} "
          f"(budget=¥{BUDGET_JPY:.2f}, exceeded={result['budget_exceeded']})")
    return result


if __name__ == "__main__":
    main()
    sys.exit(0)
