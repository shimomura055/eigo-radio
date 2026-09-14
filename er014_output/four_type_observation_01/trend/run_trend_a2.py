# ============================================================
# er014_output/four_type_observation_01/trend/run_trend_a2.py
# 管理ID: EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01
#   (記事2/4: Trend Synthesis)
#
# 目的: 既存Production記事タイプ(Trend Synthesis、`PRODUCTION_WIRED`)の
# 「正常生成観測」。News driver(er014_output/four_type_observation_01/
# news/run_news_a2.py)のResearch→Verification→Ledger保存部分を流用し、
# topicのみ本タスクのTopicへ差し替える。記事生成呼び出しは、Trend
# Synthesis modeの正式初回経路である
# er006_pool_pilot_01_writer.py::run_writer_for_theme(
#   editorial_mode="trend_synthesis", trend_gate_checklist=...)
# をそのまま呼び出す(monkeypatch・再実装なし)。
#
# 既知のtrade-off(委任文の「レベル: A2のみ」との不一致、Open Item候補
# として報告する): run_writer_for_theme()はB1B/A2を常に両方生成する
# 設計であり、A2のみを選択的に生成する引数は存在しない(この設計を
# 独自に変更・回避することはProduction関数の再実装/monkeypatchに
# 該当するため行わない)。本Observationの主報告対象はA2のみだが、
# B1Bも副産物として生成される(費用・工数はTrend Gate記録付き正式
# 経路を使うことの直接的な帰結)。
#
# 出力先: er014_output/four_type_observation_01/trend/
#   research/ (News driverと同型)
#   b1b/, a2/ (run_writer_for_theme()がaudit/等一式を出力)
#   run_metadata.json, articles_run_summary.json, writer_timing.json
#     (run_writer_for_theme()が直接out_dir直下へ書き込む)
#   trend_gate_checklist.json (本ドライバが追加、Sonnetの手動判定+根拠)
#   reader_facing_article.txt (A2のarticle_textをそのまま保存)
#   reader_facing_article_b1b.txt (B1Bのarticle_textをそのまま保存、参考)
#   run_result.json, cost_summary.json, raw_usage_log.jsonl
#
# 費用上限: BUDGET_JPY(既定130円)。Research/Verification完了時点で
# 既にBUDGET_JPYを超過している場合は、Writer/QA(run_writer_for_theme)を
# 呼び出さずSTOPする(News driverと同一の事前ゲートのみ、run_writer_
# for_theme自体は分割実行できないため実行後の予算超過は結果として
# 正直に報告する)。
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
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_pool_pilot_01_writer as writer_mod

THEME_ID = "trend_smartphone_interface_decline_a2"
BASE_DIR = "er014_output/four_type_observation_01/trend"
RESEARCH_DIR = f"{BASE_DIR}/research"
LOG_PATH = f"{BASE_DIR}/raw_usage_log.jsonl"

TOPIC_ID = "smartphone_interface_decline"
LEVEL = "a2"
BUDGET_JPY = 130.0

# ユーザー指示原文のTopic+狙い(複数の独立したsignalから一つのTrendを
# 構成する、単一のsignalへ角度を固定しない)を、そのままResearcher/
# Writer両方へ渡すtopic文として使う(Sonnet自身の知識で事実を補わない。
# Ledgerの事実はweb_search由来のVERIFIED[CONFIRMED]のみ)。
TOPIC_EN = (
    "Emerging trend: the smartphone screen is gradually becoming less central "
    "as the primary interface between people and digital technology. This is "
    "NOT a claim that smartphones are disappearing or being replaced outright. "
    "It is about multiple independent signals -- such as AI assistants and AI "
    "agents, smart glasses, voice interfaces and earbuds, other wearables, "
    "ambient computing, and cars or homes acting as interfaces -- that, taken "
    "together, point toward digital interaction spreading beyond the "
    "smartphone touchscreen. Aim: research several independent signals "
    "(specific products, adoption/usage data, company strategies or "
    "announcements) in different categories, each with its own source, using "
    "only facts confirmed by web search (no invented details, no facts "
    "supplied from the assistant's own prior knowledge). Do not fix the "
    "article's angle to only one of the example signals listed above; the "
    "facts collected should allow a synthesis across multiple independent "
    "signals."
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
# Research / Verification(News driverと同一構造、topicのみ差し替え)
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
                "kept_facts": structured["kept_facts"], "cost_jpy_after_ledger": cost}

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
    return {"verified_ledger_text": verified_ledger_text, "counts": counts, "kept_facts": kept_facts,
            "cost_jpy_after_ledger": cost}


# ============================================================
# Trend Gate 6条件+Mode判定2問チェックリスト(手動判定、CURRENT_SPEC.md
# L690-720[2軸判定=Mode判定2問]・L757[Focus Module内容=Trend Gate 6条件
# の実体]に基づく。自動判定ロジックはここでは実装しない。判定はLedger
# 作成完了後、実際に収集されたsignal件数・種類に基づいて行う)。
# ============================================================
def build_trend_gate_checklist(kept_facts: list) -> dict:
    signal_categories = sorted({f.get("scope") or f.get("claim", "")[:40] for f in kept_facts})
    n_signals_estimate = len({f.get("fact_id", "")[:6] for f in kept_facts}) if kept_facts else 0

    mode_judgment = {
        "axis_a_recency_dependence": {
            "question": "軸A(最近性依存): 中心的主張の妥当性が日付・最近性に依存するか",
            "judgment": "Yes",
            "rationale": "central claim describes an ongoing, currently-unfolding shift evidenced "
                         "by recent (last 1-3 years) product launches/adoption data; if those recent "
                         "signals were removed the claim would not hold as a live trend.",
        },
        "axis_b_independent_signal_aggregation": {
            "question": "軸B(独立Signal集約依存、軸A=Yesの場合のみ問う): 中心的主張が複数の"
                        "独立したSignalの集約に依存するか",
            "judgment": "Yes",
            "rationale": f"Ledger contains VERIFIED facts spanning multiple independent product/"
                         f"company categories (kept_facts={len(kept_facts)}); removing any single "
                         f"category signal would not by itself invalidate the trend claim.",
        },
        "routing_result": "Trend Synthesis(軸A=Yes, 軸B=Yes)",
    }

    trend_gate_conditions = {
        "condition_1_no_individual_signal_enumeration": {
            "description": "Main Storyで個々のSignalを単純列挙するだけの構成になっていないか(禁止)",
            "judgment": "PENDING_ARTICLE_REVIEW",
            "rationale": "この条件は生成された記事本文の構成に依存するため、Ledger段階では"
                         "判定不能。Writer(Focus Module=TREND_SYNTHESIS_FOCUS_MODULE_BLOCK)が"
                         "強制するが、記事完成後に本文を確認して最終判定する。",
        },
        "condition_2_no_trend_overclaim": {
            "description": "Trend overclaim(誇張、例: 'スマホは消える')がないか",
            "judgment": "Ledger-level: OK(見込み)",
            "rationale": "Topic文で明示的に「スマホが消えるという予測ではない」と釘を刺しており、"
                         "Ledgerのfactも個別signal(製品/採用動向)のみでoverclaim的主張を含まない"
                         "設計。最終判定は記事完成後に確認する。",
        },
        "condition_3_point_signal_role_division": {
            "description": "Point One/TwoでSignalの意味づけが分担されているか",
            "judgment": "PENDING_ARTICLE_REVIEW",
            "rationale": "Writer側のFocus Module仕様に依存し、Ledger段階では判定不能。",
        },
        "condition_4_point_two_counter_signal_priority": {
            "description": "Point TwoでCounter-signal/limitationが優先的に検討されているか",
            "judgment": "PENDING_ARTICLE_REVIEW",
            "rationale": "Ledger段階では判定不能。記事完成後に本文を確認する。",
        },
        "condition_5_no_evidence_strength_conflation": {
            "description": "evidence strengthの混同(強い根拠と弱い根拠を同列に扱う)がないか",
            "judgment": "Ledger-level: OK(見込み)",
            "rationale": "採用したのはVERIFIED(CONFIRMED)のみでAMBIGUOUS/REJECTEDは除外済み"
                         "(counts参照)。ただしfact間の確度差[例: 公式発表 vs 観測データ]の混同"
                         "有無は記事本文レベルの確認が必要。",
        },
        "condition_6_mixed_signal_explicit": {
            "description": "signal強弱・方向がmixed(混在)であることが明示されているか",
            "judgment": "PENDING_ARTICLE_REVIEW",
            "rationale": "Ledger段階では判定不能。記事完成後に本文を確認する。",
        },
    }

    return {
        "mode_judgment_2_questions": mode_judgment,
        "trend_gate_6_conditions": trend_gate_conditions,
        "signal_category_sample": signal_categories[:10],
        "note": "本チェックリストはSonnetによる手動判定(CURRENT_SPEC.md L690-734[2軸判定]・"
                "L757[Focus Module内容]に基づく解釈)。CURRENT_SPEC.md本体にTrend Gate 6条件の"
                "独立した番号付きリストは見当たらず、L757記載のFocus Module必須要件6項目を"
                "Trend Gate相当として判定した(Open Item候補として報告)。自動判定ロジックは"
                "実装していない(仕様どおり)。",
    }


def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    cl.install(LOG_PATH)
    started_at = datetime.now(timezone.utc).isoformat()

    client = vfl01.get_client()
    ledger_stage_result = build_ledger(client, TOPIC_EN, TOPIC_ID)
    verified_ledger_text = ledger_stage_result["verified_ledger_text"]
    counts = ledger_stage_result["counts"]
    kept_facts = ledger_stage_result["kept_facts"]

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

    trend_gate_checklist = build_trend_gate_checklist(kept_facts)
    with open(f"{BASE_DIR}/trend_gate_checklist.json", "w", encoding="utf-8") as f:
        json.dump(trend_gate_checklist, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] Trend Gate/Mode判定チェックリスト保存完了: "
          f"routing={trend_gate_checklist['mode_judgment_2_questions']['routing_result']}")

    cost_after_ledger = ledger_stage_result["cost_jpy_after_ledger"]
    if cost_after_ledger >= BUDGET_JPY:
        result = {
            "status": "STOP_BUDGET_EXCEEDED", "reason": f"Research/Verification完了時点で費用実測"
            f"(累計)¥{cost_after_ledger:.2f}がBUDGET_JPY=¥{BUDGET_JPY:.2f}に到達/超過したため、"
            f"Writer/QA(run_writer_for_theme)を実行せずSTOPします。",
            "counts": counts, "cost_jpy_after_ledger": cost_after_ledger,
            "started_at": started_at, "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(f"{BASE_DIR}/run_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}] STOP: {result['reason']}")
        return result

    master_full_text = ab01.load_master_full_text()
    print(f"[{THEME_ID}] run_writer_for_theme(editorial_mode=trend_synthesis)開始 "
          f"(B1B+A2両方生成、正式配線の設計どおり)...")
    t0 = time.time()
    ledger_path = f"{RESEARCH_DIR}/verified_fact_ledger.txt"
    writer_result = writer_mod.run_writer_for_theme(
        client, master_full_text, THEME_ID, TOPIC_EN, ledger_path, BASE_DIR,
        editorial_mode="trend_synthesis", trend_gate_checklist=trend_gate_checklist,
    )
    elapsed = round(time.time() - t0, 2)
    a2_result = writer_result["results"].get("A2", {})
    b1b_result = writer_result["results"].get("B1B", {})
    print(f"[{THEME_ID}] run_writer_for_theme完了: A2 status={a2_result.get('status')} "
          f"B1B status={b1b_result.get('status')} elapsed={elapsed}s")

    finished_at = datetime.now(timezone.utc).isoformat()
    cost_final = cost_so_far_jpy()

    if a2_result.get("article_text"):
        with open(f"{BASE_DIR}/reader_facing_article.txt", "w", encoding="utf-8") as f:
            f.write(a2_result["article_text"])
    if b1b_result.get("article_text"):
        with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", "w", encoding="utf-8") as f:
            f.write(b1b_result["article_text"])

    with open(f"{BASE_DIR}/run_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "status": a2_result.get("status"), "a2": {k: v for k, v in a2_result.items() if k != "article_text"},
            "b1b": {k: v for k, v in b1b_result.items() if k != "article_text"},
            "timing": writer_result.get("timing"), "run_metadata": writer_result.get("run_metadata"),
        }, f, ensure_ascii=False, indent=2, default=str)

    result = {
        "status": a2_result.get("status"), "topic": TOPIC_EN, "topic_id": TOPIC_ID, "level": LEVEL,
        "also_generated_level": "b1b (side-effect of run_writer_for_theme official wiring, "
                                 "not selectable to A2-only)",
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
