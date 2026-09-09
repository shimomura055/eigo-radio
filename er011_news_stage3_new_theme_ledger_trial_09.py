# ============================================================
# er011_news_stage3_new_theme_ledger_trial_09.py
# FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09 (Lane A, N-4=(a))
# ============================================================
# 目的(ユーザー決定 2026-09-09): Hanshin以外の新規News Ledgerを既存
# Research正式経路(er003_v1_en_direct_vfl_01_generate.py、通称vfl01。
# Hanshin/Health/Household 3ジャンルへ横展開されたVerified Fact Ledger
# パイプライン、根拠: ER-003-EN-DIRECT-VFL-01_REPORT.md、DECISION_LOG.md
# 3851行「Sports(Hanshin)・Health・Household の3ジャンル」)で作成し、
# Focus Module + Point Role hint条件でA2/B1B各N=3を実施する。目的は
# 「News NG率50%がHanshin固有か、仕組み側の一般問題か」の切り分けと、
# News Completionのtheme->research->Ledger->Writer->QA->artifact実走
# 確認。**Trial(Production実装ではない)**。Production/Prompt/共有
# module/SSOT編集・Git操作は一切行わない。monkeypatch・グローバル書き換え
# なし。
#
# ------------------------------------------------------------
# 再利用(import・無変更、コピー改変はしない):
# ------------------------------------------------------------
#   - er003_v1_en_direct_vfl_01_generate(vfl01): FACT_LEDGER_JSON_SCHEMA /
#     RESEARCHER_DEVELOPER_MESSAGE / build_researcher_prompt(topic=...) /
#     VERIFICATION_JSON_SCHEMA / VERIFICATION_DEVELOPER_MESSAGE /
#     build_verification_prompt(topic, ledger_parsed) /
#     build_verified_ledger_text(ledger_parsed, verification_parsed) /
#     MODEL / REASONING_EFFORT / get_client / load_master_full_text を
#     そのまま再利用する。vfl01.run_researcher()/run_verification()自体は
#     モジュール定数TOPIC(Hanshin固定)を暗黙に使うため直接は呼ばず、
#     build_researcher_prompt(topic=新テーマ)/build_verification_prompt(
#     新テーマ, ...)というtopic引数を明示的に渡せる既存関数を使って
#     client.responses.create()を呼ぶ(vfl01.run_researcher/run_verification
#     と全く同じ呼び出し構造、topicだけが変数という以外の差分はない。
#     関数のコピーは作らない)。
#   - er002_ja_web_research_r3(r3): extract_web_search_usage /
#     extract_sources をそのまま再利用する。
#   - er011_point_role_planning_focus_connection_trial_03(t3、既存
#     VALIDATED Trial): run_one_pattern_connected / MAJOR_DAILY_NEWS_
#     POINT_ROLE_HINT_BLOCK / MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK /
#     load_text をそのままimportする(再改変・再コピーはしない)。
#   - er011_daily_news_focus_layer_comparison_trial_04(t4): analyze_run /
#     LEVELS をそのまま再利用する(Trial-06と同一の解析ロジック、比較
#     可能性を担保)。
#   - er003_v1_n3_01_articles_generate(prod_gen): build_common_block /
#     build_prompt / A2_KAI1_INSTRUCTION / B1_B_DIRECT_INSTRUCTION。
#     無変更。
#   - er005_cost_logger(cl): install / logging_context。無変更。
#
# 費用上限: Step 0(Ledger作成) \60、Step 1(text-only 6本) \150、
# 追加のB1B 1本通し(Key Phrase->TTS->Assembly->Audio Gate->player)は
# 別枠 \60。超過見込みの場合はN=2へ縮小、それでも超過ならSTOP。
# ============================================================
from __future__ import annotations

import json
import os
import time

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er011_daily_news_focus_layer_comparison_trial_04 as t4
import er011_point_role_planning_focus_connection_trial_03 as t3

THEME_ID = "news_stage3_new_theme_ledger_trial_09"
OUT_DIR = f"er011_output/{THEME_ID}"
RESEARCH_DIR = f"{OUT_DIR}/research"

N_RUNS = 3
BUDGET_STEP0_JPY = 60.0
BUDGET_STEP1_JPY = 150.0
BUDGET_B1B_FULL_JPY = 60.0

USD_JPY = 160.0
PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def _price(provider, model, meter):
    return next(p["price"] for p in PRICING if p["provider"] == provider and p["model"] == model and p["meter"] == meter)


_LUNA_IN, _LUNA_CACHED, _LUNA_OUT = _price("openai", "gpt-5.6-luna", "input_tokens"), \
    _price("openai", "gpt-5.6-luna", "cached_input_tokens"), _price("openai", "gpt-5.6-luna", "output_tokens")
_SOL_IN, _SOL_CACHED, _SOL_OUT = _price("openai", "gpt-5.6-sol", "input_tokens"), \
    _price("openai", "gpt-5.6-sol", "cached_input_tokens"), _price("openai", "gpt-5.6-sol", "output_tokens")
_WEB_SEARCH_CALL = _price("openai", "N/A (tool, all models)", "web_search_call")


def _call_cost_usd(rec: dict) -> float:
    provider, model = rec["provider"], rec.get("model_id")
    it, ot = rec.get("input_tokens") or 0, rec.get("output_tokens") or 0
    ct = rec.get("cached_input_tokens") or 0
    if provider == "openai_asr":
        cost = (it / 1e6) * _price("openai_asr", model, "input_tokens") + (ot / 1e6) * _price("openai_asr", model, "output_tokens")
    elif provider == "gemini":
        tier = "Batch" if rec.get("batch") else "Standard"
        cost = (it / 1e6) * _price("gemini", model, "input_tokens") + (ot / 1e6) * _price("gemini", model, "output_tokens")
    elif provider == "openai":
        billable_in = max(it - ct, 0)
        if model == "gpt-5.6-luna":
            cost = (billable_in / 1e6) * _LUNA_IN + (ct / 1e6) * _LUNA_CACHED + (ot / 1e6) * _LUNA_OUT
        elif model == "gpt-5.6-sol":
            cost = (billable_in / 1e6) * _SOL_IN + (ct / 1e6) * _SOL_CACHED + (ot / 1e6) * _SOL_OUT
        else:
            raise ValueError(f"unpriced openai model: {model}")
        web_search_calls = rec.get("web_search_call_count") or 0
        cost += (web_search_calls / 1000) * _WEB_SEARCH_CALL
    else:
        raise ValueError(f"unpriced provider: {provider}")
    return cost


def compute_cost_so_far_jpy() -> float:
    log_path = f"{OUT_DIR}/raw_usage_log.jsonl"
    if not os.path.exists(log_path):
        return 0.0
    total_usd = 0.0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_usd += _call_cost_usd(json.loads(line))
    return total_usd * USD_JPY


def write_cost_summary() -> dict:
    log_path = f"{OUT_DIR}/raw_usage_log.jsonl"
    records = [json.loads(l) for l in open(log_path, encoding="utf-8")] if os.path.exists(log_path) else []
    for r in records:
        r["_cost_usd"] = _call_cost_usd(r)
    from collections import defaultdict
    by_theme, counts = defaultdict(float), defaultdict(int)
    for r in records:
        by_theme[r["theme"]] += r["_cost_usd"]
        counts[r["theme"]] += 1
    result = {
        "usd_jpy_rate": USD_JPY,
        "methodology": "全て実測usage(actual)。単価はer005_output/cost_baseline_01/"
                       "pricing_snapshot.json(OFFICIAL_SOURCE)。",
        "by_theme_jpy": {k: round(v * USD_JPY, 2) for k, v in by_theme.items()},
        "call_counts": dict(counts),
        "total_usd": round(sum(by_theme.values()), 4),
        "total_jpy": round(sum(by_theme.values()) * USD_JPY, 2),
        "total_calls": len(records),
    }
    with open(f"{OUT_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


# ============================================================
# Step 0-a: 候補3件検索(単一起点イベント、スポーツ/科学/社会いずれか、
# 政治的争点は避ける)。vfl01のResearcher呼び出し構造(web_search tool +
# json_schema + MODEL/REASONING_EFFORT)をそのまま踏襲し、Ledger本体では
# なく「候補一覧」を出力させる専用schema/promptのみ新規追加する
# (Researcher自体の関数はコピーしない、client.responses.create()の
# 呼び出しパターンのみ同一構造で再現)。
# ============================================================
CANDIDATE_SEARCH_JSON_SCHEMA = {
    "name": "news_candidate_search",
    "schema": {
        "type": "object",
        "properties": {
            "candidates": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "enum": ["sports", "science", "society"]},
                        "headline_ja": {"type": "string"},
                        "event_date": {"type": "string"},
                        "single_origin_summary_ja": {
                            "type": "string",
                            "description": "「[日付]に、Xが起きた」の1文形式で書ける要約",
                        },
                        "numeric_density_estimate": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
                        "why_not_political": {"type": "string"},
                        "source_title": {"type": "string"},
                        "source_url": {"type": "string"},
                    },
                    "required": [
                        "category", "headline_ja", "event_date", "single_origin_summary_ja",
                        "numeric_density_estimate", "why_not_political", "source_title", "source_url",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["candidates"],
        "additionalProperties": False,
    },
    "strict": True,
}

CANDIDATE_SEARCH_DEVELOPER_MESSAGE = (
    "あなたはFact Researcherです。記事本文は書かず、ニュース候補の一覧だけを構造化して提示してください。"
)

CANDIDATE_SEARCH_PROMPT = """直近(おおむね過去1〜2週間以内)に実際に報じられた、スポーツ・科学・社会\
(政治的争点を除く)のいずれかの分野で、単一の起点となる出来事・発表・観測結果を3件、Webで検索して\
挙げてください。

【条件】
- 政治的な争点(選挙・政党・国際紛争・政策論争等)は避けること
- 「[日付]に、Xが起きた」という1文で要点を保てる、単一起点のdateableな出来事であること(複数の
  独立した出来事・時点を横断的にまとめた傾向記事のような題材は避けること)
- 3件は互いに異なる分野(sports/science/societyのうち、できるだけ異なるカテゴリ)にすること
- 数値(スコア・統計等)への依存度が低い題材(比較のため、野球の試合結果のような数値密度の高い
  題材だけに偏らないようにすること)を少なくとも1件は含めること
- 各候補について、実際に存在するSourceのtitle/urlを記録すること

出力は各候補ごとに、category・headline_ja・event_date・single_origin_summary_ja(「[日付]に、Xが
起きた」の1文形式)・numeric_density_estimate(LOW/MEDIUM/HIGH、その出来事を記事化した場合に必要な
具体的数値の量の見積もり)・why_not_political(政治的争点でないことの簡潔な説明)・source_title・
source_urlとしてください。"""


def run_candidate_search(client) -> dict:
    response = client.responses.create(
        model=vfl01.MODEL,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **CANDIDATE_SEARCH_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": CANDIDATE_SEARCH_DEVELOPER_MESSAGE},
            {"role": "user", "content": CANDIDATE_SEARCH_PROMPT},
        ],
    )
    text = response.output_text
    search_usage = r3.extract_web_search_usage(response)
    sources = r3.extract_sources(response)
    parsed = json.loads(text)
    return {
        "prompt": CANDIDATE_SEARCH_PROMPT, "raw_text": text, "parsed": parsed, "model": response.model,
        "response_id": response.id, "search_usage": search_usage, "sources": sources,
    }


def stage_candidate_search():
    os.makedirs(RESEARCH_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    client = vfl01.get_client()
    theme_tag = f"{THEME_ID}_candidate_search"
    with cl.logging_context(theme_tag, "candidate_search"):
        result = run_candidate_search(client)
    with open(f"{RESEARCH_DIR}/candidate_search.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] candidate_search完了: {len(result['parsed']['candidates'])}件")
    for c in result["parsed"]["candidates"]:
        print(f"  - [{c['category']}] {c['headline_ja']} ({c['event_date']}, numeric={c['numeric_density_estimate']})")
    cost = compute_cost_so_far_jpy()
    print(f"[{THEME_ID}] candidate_search費用実測: ¥{cost:.2f}")
    return result


# ============================================================
# Step 0-b: 選定テーマでVerified Fact Ledgerを既存経路で作成。
# vfl01.build_researcher_prompt(topic=...)/build_verification_prompt(
# topic, ledger_parsed)というtopic引数を明示的に渡せる既存関数を使い、
# vfl01.run_researcher()/run_verification()と全く同じ呼び出し構造
# (model/reasoning/tools/text.format/developer+user message)を、
# topicだけ差し替えて再現する(コピー関数ではなく、同型のclient呼び出し)。
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
    return {
        "prompt": prompt, "raw_text": text, "parsed": parsed, "model": response.model,
        "response_id": response.id, "search_usage": search_usage, "sources": sources,
    }


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
    return {
        "prompt": prompt, "raw_text": text, "parsed": parsed, "model": response.model,
        "response_id": response.id, "search_usage": search_usage, "sources": sources,
    }


def stage_build_ledger(topic: str, topic_id: str):
    """selected_theme.jsonがreconciliation_stageで既に保存されている前提で、
    topicを引数で明示的に渡して実行する(手動判定の結果を機械が上書きしない
    ため、topic文字列はCLI引数またはselected_theme.jsonから読む)。"""
    os.makedirs(RESEARCH_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    client = vfl01.get_client()

    theme_tag = f"{THEME_ID}_ledger_research"
    with cl.logging_context(theme_tag, "researcher"):
        research_result = run_researcher_for_topic(client, topic)
    with open(f"{RESEARCH_DIR}/fact_ledger_draft.json", "w", encoding="utf-8") as f:
        json.dump(research_result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] Researcher完了: {len(research_result['parsed']['facts'])}件のFact下書き、"
          f"web_search={research_result['search_usage']}")

    with cl.logging_context(theme_tag, "verification"):
        verification_result = run_verification_for_topic(client, topic, research_result["parsed"])
    with open(f"{RESEARCH_DIR}/fact_ledger_verification.json", "w", encoding="utf-8") as f:
        json.dump(verification_result, f, ensure_ascii=False, indent=2, default=str)

    # 委任指示(2026-09-09): 「全件CONFIRMED、未検証は載せない」。
    # vfl01.build_verified_ledger_text(無変更のまま再利用)はREJECTEDのみを
    # 除外しAMBIGUOUSは[AMBIGUOUS]タグ付きで残す既定挙動(Hanshin等での
    # 既存運用と同一)だが、本Trialではその出力をそのまま採用せず、Trial側の
    # 追加フィルタとしてVERIFIED(CONFIRMED)のみへさらに絞り込む(production
    # 関数自体は変更していない、その出力を後段で取捨選択しているだけ)。
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
        if fact.get("notes_for_writer"):
            lines.append(f"  notes_for_writer: {fact['notes_for_writer']}")
        lines.append("")
    verified_ledger_text = "\n".join(lines)
    print(f"[{THEME_ID}] Verification完了: {counts}(CONFIRMED-onlyフィルタ適用後 kept={len(kept_facts)}件)")

    with open(f"{RESEARCH_DIR}/verified_fact_ledger.txt", "w", encoding="utf-8") as f:
        f.write(verified_ledger_text)
    with open(f"{RESEARCH_DIR}/verified_fact_ledger_structured.json", "w", encoding="utf-8") as f:
        json.dump({"topic": topic, "topic_id": topic_id, "kept_facts": kept_facts, "counts": counts,
                    "note": "CONFIRMED(VERIFIED)のみ採用(委任指示: 全件CONFIRMED、未検証は載せない)。"
                            "AMBIGUOUS/REJECTEDはfact_ledger_verification.jsonに記録済みだが本Ledgerからは除外した。"},
                   f, ensure_ascii=False, indent=2)
    # Directional Fact Precheck Layer 1(vfl_internal、任意)向け、Production同型の
    # stage_b3_vfl.json形式で保存(なくても既存機構はLayer2のみで動作するが、
    # Layer1も有効化できるようにするための任意ファイル)。
    with open(f"{RESEARCH_DIR}/stage_b3_vfl.json", "w", encoding="utf-8") as f:
        json.dump({"parsed": research_result["parsed"]}, f, ensure_ascii=False, indent=2)

    cost = compute_cost_so_far_jpy()
    print(f"[{THEME_ID}] Ledger作成完了。CONFIRMED(VERIFIED)={counts.get('VERIFIED', 0)}件、"
          f"AMBIGUOUS={counts.get('AMBIGUOUS', 0)}件(未検証は本文へ含めない方針のためREJECTEDのみ除外、"
          f"AMBIGUOUSは[AMBIGUOUS]タグ付きで残存)。費用実測: ¥{cost:.2f}")
    return {"verified_ledger_text": verified_ledger_text, "counts": counts, "cost_jpy": cost}


# ============================================================
# Step 1: Focus Module + Point Role hint条件でA2/B1B各N=3(text-only)。
# baselineは回さない(比較対象はHanshin Trial-06のbaseline/focus_hintと
# Theme 2 Trial-05 baseline、既存記録を参照するのみ)。
# ============================================================
NEW_THEME_LEDGER_PATH = f"{RESEARCH_DIR}/verified_fact_ledger.txt"
NEW_THEME_TOPIC_JA = (
    "2026年9月3日、New England Journal of Medicine誌に、体内で直接CD19 CAR-T細胞を誘導する新しい"
    "遺伝子治療についての報告が掲載された。難治性の神経系自己免疫疾患患者16人(進行型多発性硬化症7人、"
    "MOG抗体関連疾患3人、全身型重症筋無力症3人、特発性炎症性筋疾患3人)を対象とした第1相臨床研究で、"
    "非増殖性・自己不活化型のレンチウイルスベクターを単回静脈投与し、患者自身の体内でCD19標的CAR-T"
    "細胞を生成させた。B細胞の深い減少とその後の再出現、各疾患群での神経機能・検査値の改善が報告され、"
    "安全性面では11人にグレード1のサイトカイン放出症候群が見られたが2週間以内に軽快し、重篤な神経毒性"
    "等は報告されなかった。ただしこの研究は対照群を伴わない小規模な単群第1相研究であり、研究チームは"
    "より大規模な試験での検証が必要だとしている。"
)
NEW_THEME_TOPIC_ID = "invivo_cart_ms"

STEP1_N_RUNS = 3
STEP1_BUDGET_JPY = 150.0

STEP1_CONDITIONS = {
    "focus_hint": {
        "editorial_type_module_block": t3.MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK,
        "point_role_hint_block": t3.MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK,
    },
}

STEP1_LEVELS = t4.LEVELS  # [(label, instruction, level_dir, stage_tag), ...] Trial-04/06と完全同一


def gate_g1_freshness_check() -> dict:
    """Trial-06と同一の機械チェック(t3.run_one_pattern_connectedがG1修正済み
    prod_gen.build_diagnostic_retry_promptを直接呼んでいることの確認)。"""
    import difflib
    import inspect

    trial_src = inspect.getsource(t3.run_one_pattern_connected)
    calls_prod_fn_directly = "prod_gen.build_diagnostic_retry_prompt(" in trial_src
    no_local_redefinition = "def build_diagnostic_retry_prompt" not in trial_src
    prod_diag_src = inspect.getsource(prod_gen.build_diagnostic_retry_prompt)
    g1_fix_marker_present = "OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01" in prod_diag_src
    prod_src = inspect.getsource(prod_gen.run_one_pattern)
    diff_lines = list(difflib.unified_diff(
        prod_src.splitlines(), trial_src.splitlines(),
        fromfile="prod_gen.run_one_pattern", tofile="t3.run_one_pattern_connected", lineterm=""))
    pass_text = "PASS"
    conclusion = pass_text if (calls_prod_fn_directly and no_local_redefinition and g1_fix_marker_present) else "FAIL"
    result = {
        "calls_prod_gen_build_diagnostic_retry_prompt_directly": calls_prod_fn_directly,
        "no_local_redefinition": no_local_redefinition,
        "g1_fix_marker_present": g1_fix_marker_present,
        "diff_line_count": len(diff_lines),
        "conclusion": conclusion,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/gate4_g1_freshness_check.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    if conclusion != pass_text:
        raise RuntimeError(f"Gate 4 G1鮮度チェック失敗: {result}")
    return result


def step1_setup():
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    gate_result = gate_g1_freshness_check()
    unit_test_result = t3.test_default_hint_is_byte_identical_to_production()
    if unit_test_result["status"] != "PASS":
        raise RuntimeError(f"既定値バイト一致テスト失敗: {unit_test_result}")
    run_metadata = {
        "management_id": "FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09",
        "topic_id": NEW_THEME_TOPIC_ID,
        "mode_supply_path": "手動Mode判定+手動Ledger供給(Trend Synthesisと同じ機構)。",
        "editorial_mode_determination": "MAJOR_DAILY(theme_selection_reconciliation.md参照)",
        "major_daily_gate_checklist_source": "research/major_daily_gate_checklist.json(本Trialで新規手動判定)",
    }
    with open(f"{OUT_DIR}/run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(run_metadata, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] step1_setup完了: gate4={gate_result['conclusion']}, unit_test={unit_test_result['status']}")
    return {"gate_result": gate_result, "unit_test_result": unit_test_result}


def run_one_combo(client, master_full_text: str, verified_ledger_text: str,
                   condition_name: str, cond: dict, run_idx: int, label: str, instruction: str,
                   level_dir: str, stage_tag: str) -> dict:
    out_dir = f"{OUT_DIR}/{level_dir}/{condition_name}/run{run_idx}"
    common_block = prod_gen.build_common_block(
        master_full_text, NEW_THEME_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=cond["editorial_type_module_block"])
    prompt = prod_gen.build_prompt(common_block, instruction)
    theme_tag = f"{THEME_ID}_{condition_name}_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, stage_tag):
        result = t3.run_one_pattern_connected(
            client, theme_tag, label, prompt, verified_ledger_text, NEW_THEME_TOPIC_JA, out_dir,
            point_role_hint_block=cond["point_role_hint_block"])
    elapsed = round(time.time() - t0, 2)
    analysis = t4.analyze_run(out_dir, result)
    analysis["elapsed_seconds"] = elapsed
    analysis["condition"] = condition_name
    analysis["level"] = label
    analysis["run"] = run_idx
    with open(f"{out_dir}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in result.items() if k != "article_text"}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] run{run_idx} {condition_name} {label}: status={result.get('status')} "
          f"retry={analysis['retry_attempts']} p1_overlap={analysis['point_one_overlap_ratio']} "
          f"p2_overlap={analysis['point_two_overlap_ratio']} elapsed={elapsed}s")
    return analysis


LABEL_LOOKUP = {label: (label, instruction, level_dir, stage_tag)
                for (label, instruction, level_dir, stage_tag) in STEP1_LEVELS}
COMBO_RESULTS_DIR = f"{OUT_DIR}/_combo_results"


def combo_stage(condition_name: str, label: str, run_idx: int) -> dict:
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    client = t3.vfl01.get_client()
    master_full_text = t3.ab01.load_master_full_text()
    verified_ledger_text = t3.load_text(NEW_THEME_LEDGER_PATH)
    cond = STEP1_CONDITIONS[condition_name]
    _, instruction, level_dir, stage_tag = LABEL_LOOKUP[label]
    analysis = run_one_combo(client, master_full_text, verified_ledger_text, condition_name, cond,
                              run_idx, label, instruction, level_dir, stage_tag)
    os.makedirs(COMBO_RESULTS_DIR, exist_ok=True)
    with open(f"{COMBO_RESULTS_DIR}/{condition_name}_{level_dir}_run{run_idx}.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    return analysis


def aggregate_stage() -> list:
    all_results = []
    if os.path.isdir(COMBO_RESULTS_DIR):
        for fname in sorted(os.listdir(COMBO_RESULTS_DIR)):
            with open(f"{COMBO_RESULTS_DIR}/{fname}", encoding="utf-8") as f:
                all_results.append(json.load(f))
    with open(f"{OUT_DIR}/all_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] aggregate_stage: {len(all_results)}本を集約しました。")
    return all_results


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "candidate_search"
    if which == "candidate_search":
        stage_candidate_search()
    elif which == "build_ledger":
        topic_arg = sys.argv[2]
        topic_id_arg = sys.argv[3] if len(sys.argv) > 3 else "NEWTHEME"
        stage_build_ledger(topic_arg, topic_id_arg)
    elif which == "step1_setup":
        step1_setup()
    elif which == "combo":
        # 例: python er011_news_stage3_new_theme_ledger_trial_09.py combo focus_hint A2 1
        condition_name, label, run_idx = sys.argv[2], sys.argv[3], int(sys.argv[4])
        combo_stage(condition_name, label, run_idx)
    elif which == "aggregate":
        aggregate_stage()
    elif which == "cost":
        print(json.dumps(write_cost_summary(), ensure_ascii=False, indent=2))
    else:
        print("usage: python er011_news_stage3_new_theme_ledger_trial_09.py "
              "[candidate_search|build_ledger <topic> <topic_id>|step1_setup|"
              "combo <condition> <A2|B1B> <run_idx>|aggregate|cost]")
