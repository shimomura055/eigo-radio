# ============================================================
# er011_discovery_generalization_towels_trial_11_run.py
# 管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11
# ============================================================
# 目的(ユーザー決定 2026-09-10): Discovery Focus Module(Discovery/Why型
# 記事のためのPrompt拡張モジュール。Part A本体のみ。保険文抑制Prompt制約案
# [Part B案1、`cautionary_constrained`]は使わない=Part A単独条件)の一般化
# 可能性を、Household(冷蔵庫クリスパー)とは異なる新テーマ「洗濯したのに、
# なぜタオルは臭うことがあるのか?("Why do towels sometimes smell even
# after washing?")」でN=1確認する。A2/B1B各1本、記事生成→既存QA一式まで。
# Support(Preview/Comment/Key Phrase)・Audioは実施しない(記事品質確認が
# 目的)。**Trial(Production実装ではない)。Production採用はしない**
# (Gate 1=VALIDATED相当までが上限)。
#
# ------------------------------------------------------------
# Reconciliation Check(PM_GOVERNANCE 2-1、実施記録):
# ------------------------------------------------------------
# - er011_household_unified_final_candidate_01_run.py(Household一本化
#   最終候補の実行script)を確認し、同じ経路(prod_gen.build_common_block/
#   build_prompt/run_one_pattern、既存Production関数を無変更で直接呼ぶ)を
#   踏襲した。Household固有のVerified Fact Ledger v5は使えないため、新規
#   Ledgerを作成する(下記)。
# - er011_discovery_stage4_cautionary_language_trial_10.py(Trial-10)の
#   Part A単独(`current_focus`)条件は、er011_discovery_stage3_rule_
#   adjustment_trial_09.py(t9)のCURRENT_FOCUS_BLOCKを一字一句不変のまま
#   再利用している(Trial-05本体、Part B文言は含まない)。本Trialも同じ
#   CURRENT_FOCUS_BLOCKを無変更でimportし、Part B文言(cautionary_clause)は
#   一切使わない。
# - er011_news_stage3_new_theme_ledger_trial_09.py(News Trial-09)が新テーマ
#   Verified Fact Ledgerを作成した手順(vfl01.build_researcher_prompt(topic=)/
#   build_verification_prompt(topic, ledger_parsed)というtopic引数を明示的に
#   渡せる既存関数を使い、vfl01.run_researcher/run_verificationと同一の
#   client呼び出し構造をtopicだけ差し替えて再現、VERIFIED[CONFIRMED]のみへ
#   フィルタしAMBIGUOUS/REJECTEDは除外)を踏襲する。
#
# 再利用(import・無変更、read-onlyでの参照のみ):
#   - er011_discovery_stage3_rule_adjustment_trial_09(t9): CURRENT_FOCUS_
#     BLOCK(Part A本体、一字一句不変)/ analyze_run / load_text(分析ロジック、
#     無変更、Household最終候補artifactの再分析にも同一関数を使い比較可能性を
#     担保する)。
#   - er003_v1_en_direct_ab_01_generate(ab01): load_master_full_text。
#   - er003_v1_en_direct_vfl_01_generate(vfl01): FACT_LEDGER_JSON_SCHEMA /
#     RESEARCHER_DEVELOPER_MESSAGE / build_researcher_prompt(topic=...) /
#     VERIFICATION_JSON_SCHEMA / VERIFICATION_DEVELOPER_MESSAGE /
#     build_verification_prompt(topic, ledger_parsed) / MODEL /
#     REASONING_EFFORT / get_client。無変更。
#   - er002_ja_web_research_r3(r3): extract_web_search_usage / extract_sources。
#   - er003_v1_n3_01_articles_generate(prod_gen): build_common_block/
#     build_prompt/A2_KAI1_INSTRUCTION/B1_B_DIRECT_INSTRUCTION/
#     run_one_pattern(Point Role Planning/Point Value QA/Point Overlap QA+
#     記事全体retry[Loop Budget 2]/Local Rewrite/Fact Checker/Ledger
#     Deviation Checker/Directional Fact Precheck含む既存Production経路
#     そのもの)。無変更。
#   - er005_cost_logger(cl): install / logging_context。無変更。
#
# 費用上限: 合計¥150(見込み¥30〜80。Ledger作成+A2/B1B各1本の記事生成、
# retryを含む)。同期実行のみ。バックグラウンド待機・二重起動禁止。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_discovery_generalization_towels_trial_11_run.py [stage ...]
#   stage: ledger | gate4 | a2 | b1b | evaluate | cost | all(省略時)
# ============================================================
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er011_discovery_stage3_rule_adjustment_trial_09 as t9  # 読み取り専用の再利用(t9のOUT_DIRへは書き込まない)

THEME_ID = "discovery_generalization_towels_trial_11"
OUT_DIR = f"er011_output/{THEME_ID}"
RESEARCH_DIR = f"{OUT_DIR}/research"
BUDGET_JPY_CAP = 150.0

# Part A本体のみ(t9.CURRENT_FOCUS_BLOCKを無変更でそのまま使う。Part B文言
# [cautionary_clause]は一切追加しない=Part A単独条件)。
DISCOVERY_FOCUS_MODULE_PART_A_BLOCK = t9.CURRENT_FOCUS_BLOCK

LEVELS = {
    "a2": {"label": "A2", "instruction": prod_gen.A2_KAI1_INSTRUCTION, "stage_tag": "writer_a2"},
    "b1b": {"label": "B1B", "instruction": prod_gen.B1_B_DIRECT_INSTRUCTION, "stage_tag": "writer_b1"},
}

TOWELS_LEDGER_PATH = f"{RESEARCH_DIR}/verified_fact_ledger.txt"
TOWELS_STAGE_B3_VFL_PATH = f"{RESEARCH_DIR}/stage_b3_vfl.json"

# ------------------------------------------------------------
# Researcher入力(研究質問。ユーザー確定テーマの英語表現をそのまま含める。
# 「なぜ」を問う形にとどめ、結論を先取りしない=Ledger側にバイアスを
# 与えない)。
# ------------------------------------------------------------
RESEARCH_QUESTION_JA = (
    "\"Why do towels sometimes smell even after washing?\"(洗濯したのに、なぜタオルは臭うことが"
    "あるのか?)というテーマについて調査してください。家庭用洗濯機でタオル・衣類を洗濯した後、"
    "乾燥後や保管中に生乾き臭・雑巾のようなニオイが残る現象の原因(原因菌・繊維内のバイオフィルム、"
    "洗濯槽内の残留物、部分的に湿った状態での放置時間、低温洗濯での洗浄効果の限界、洗剤・柔軟剤の"
    "残留蓄積、タオルの繊維素材による違い等)について、微生物学研究・繊維科学・家電メーカーや大学の"
    "Extensionサービス等、信頼できる情報源に基づいて調査してください。"
)

# ------------------------------------------------------------
# 保険文検出regex(FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10の
# comparisonスクリプト/HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01と同一定義、
# read-onlyで転記して再利用。既存検出器を独自判断で変更しない)。
# ------------------------------------------------------------
_VERB = r"(?:check|consult|ask|see|refer to|look at|read|follow)"
_SOURCE = r"(?:instructions?|manuals?|guides?|guidelines?|manufacturers?|makers?|professionals?|experts?|labels?|packagings?|packages?)"
INSURANCE_RE = re.compile(_VERB + r"[^.!?]{0,80}" + _SOURCE, re.IGNORECASE)


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def detect_insurance_sentences(article_text: str) -> list:
    return [m.group(0) for m in INSURANCE_RE.finditer(article_text or "")]


# ============================================================
# 費用実測(全provider対応、HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01の
# compute_cost_jpy_so_farと同一ロジック、read-onlyで転記して再利用)。
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
    log_path = f"{OUT_DIR}/raw_usage_log.jsonl"
    if not os.path.exists(log_path):
        return {"total_jpy": 0.0, "by_provider_jpy": {}, "unpriced_records": 0, "total_records": 0}
    total_usd, by_provider, unpriced = 0.0, {}, 0
    n = 0
    with open(log_path, encoding="utf-8") as f:
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


def cost_stage() -> dict:
    result = compute_cost_jpy_so_far()
    save_json(f"{OUT_DIR}/cost_summary.json", result)
    print(f"[{THEME_ID}][cost] 実測合計={result['total_jpy']} JPY (上限{BUDGET_JPY_CAP}) "
          f"by_provider={result['by_provider_jpy']} unpriced_records={result['unpriced_records']}")
    if result["total_jpy"] > BUDGET_JPY_CAP:
        raise RuntimeError(f"費用上限超過(実測{result['total_jpy']}円 > 上限{BUDGET_JPY_CAP}円)。STOP。")
    return result


# ============================================================
# Gate 4相当の静的確認(Production関数の再定義・monkeypatchをしていない
# ことの機械確認。Household最終候補と同一ロジック)。
# ============================================================
def gate4_check_stage() -> dict:
    used_names = ["THEMES", "build_common_block", "build_prompt", "A2_KAI1_INSTRUCTION",
                  "B1_B_DIRECT_INSTRUCTION", "run_one_pattern", "POINT_OVERLAP_ARTICLE_RETRY_MAX"]
    not_reassigned = all(name in vars(prod_gen) for name in used_names)
    placeholder_present = "{editorial_type_module_block}" in prod_gen.COMMON_BLOCK_TEMPLATE

    part_a_block_byte_identical_to_t9 = DISCOVERY_FOCUS_MODULE_PART_A_BLOCK == t9.CURRENT_FOCUS_BLOCK
    part_b_clause_absent = "取扱説明書" not in DISCOVERY_FOCUS_MODULE_PART_A_BLOCK

    result = {
        "prod_gen_used_names_present_and_not_reassigned": not_reassigned,
        "common_block_template_has_editorial_type_module_block_placeholder": placeholder_present,
        "part_a_block_byte_identical_to_t9_current_focus_block": part_a_block_byte_identical_to_t9,
        "part_b_cautionary_clause_absent_from_block": part_b_clause_absent,
        "point_overlap_article_retry_max_loop_budget": prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX,
        "focus_module_source": ("er011_discovery_stage3_rule_adjustment_trial_09.CURRENT_FOCUS_BLOCK"
                                 "(read-only reuse, unmodified, Part A only)"),
        "conclusion": "PASS" if (not_reassigned and placeholder_present and part_a_block_byte_identical_to_t9
                                  and part_b_clause_absent) else "FAIL_NEEDS_REVIEW",
    }
    save_json(f"{OUT_DIR}/audit/gate4_check.json", result)
    print(f"[{THEME_ID}] gate4_check_stage: {result['conclusion']}")
    if result["conclusion"] != "PASS":
        raise RuntimeError(f"Gate 4静的確認失敗: {result}")
    return result


# ============================================================
# Step 0: 新テーマVerified Fact Ledger作成(News Trial-09の手順を踏襲。
# vfl01.build_researcher_prompt(topic=)/build_verification_prompt(topic,...)
# というtopic引数を明示的に渡せる既存関数を使い、vfl01.run_researcher/
# run_verificationと同一のclient呼び出し構造をtopicだけ差し替えて再現)。
# VERIFIED[CONFIRMED]のみへフィルタし、AMBIGUOUS/REJECTEDは本Ledgerから
# 除外する(全件CONFIRMED、未検証は載せない方針、News Trial-09と同一)。
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
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
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

    with open(TOWELS_LEDGER_PATH, "w", encoding="utf-8") as f:
        f.write(verified_ledger_text)
    save_json(f"{RESEARCH_DIR}/verified_fact_ledger_structured.json", {
        "topic_id": "towels_odor", "research_question_ja": RESEARCH_QUESTION_JA,
        "kept_facts": kept_facts, "counts": counts,
        "note": "CONFIRMED(VERIFIED)のみ採用(News Trial-09と同一方針: 全件CONFIRMED、未検証は載せない)。"
                "AMBIGUOUS/REJECTEDはfact_ledger_verification.jsonに記録済みだが本Ledgerからは除外した。",
    })
    # Directional Fact Precheck Layer 1(vfl_internal、任意)向け、Production同型形式で保存
    save_json(TOWELS_STAGE_B3_VFL_PATH, {"parsed": research_result["parsed"]})

    cost = cost_stage()
    print(f"[{THEME_ID}] Ledger作成完了。CONFIRMED(VERIFIED)={counts.get('VERIFIED', 0)}件、"
          f"AMBIGUOUS={counts.get('AMBIGUOUS', 0)}件、REJECTED={counts.get('REJECTED', 0)}件。"
          f"費用実測: {cost['total_jpy']}円")
    return {"verified_ledger_text": verified_ledger_text, "counts": counts, "kept_facts": kept_facts, "cost": cost}


# ------------------------------------------------------------
# Writer用topic(TOWELS_TOPIC_JA): Ledger確定後(実際にledger_stage()を実行し
# `research/verified_fact_ledger.txt`のCONFIRMED[VERIFIED] 15件を確認した
# 上で)、そのfactのみを要約した短い「発見」記述(Household
# THEMES["household"]["topic"]と同型のstyle: 数文+出典注記)。Ledgerに
# 存在しない新しい主張・数字は追加していない(F008/F009/F010の3件に基づく)。
# ------------------------------------------------------------
TOWELS_TOPIC_JA = (
    "洗濯した綿タオルが乾燥後や保管中に生乾き臭・雑巾のようなニオイを放つことがあるのは、皮脂・汗を"
    "栄養源とする細菌が繊維の内部に入り込んでバイオフィルムを形成し、通常の洗濯では完全には除去され"
    "ないまま残ることが、綿とポリエステルを用いた実験室モデルの研究で報告されているためである。"
    "日本の26世帯で6か月間タオルを使用・追跡した研究では、使用開始からわずか2か月後にはすでに"
    "ニオイとくすみが観察され、タオルの糸の内部を中心にバイオフィルムが時間とともに蓄積したことが"
    "報告された。(Analysis of biofilm and bacterial communities in the towel environment with daily use、"
    "The Bacterial Life Cycle in Textiles is Governed by Fiber Hydrophobicity等の査読論文に基づく)"
)


# ============================================================
# Step 1: 記事生成(Part A単独条件、A2/B1B各1本、Loop Budget等既存経路の
# まま。再抽選[N追加]は行わない)。
# ============================================================
def generate_article_stage(level: str) -> dict:
    meta = LEVELS[level]
    out_dir = f"{OUT_DIR}/{level}"
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    verified_ledger_text = open(TOWELS_LEDGER_PATH, encoding="utf-8").read()
    common_block = prod_gen.build_common_block(
        master_full_text, TOWELS_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=DISCOVERY_FOCUS_MODULE_PART_A_BLOCK)
    prompt = prod_gen.build_prompt(common_block, meta["instruction"])

    t0 = time.time()
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    with cl.logging_context(THEME_ID, meta["stage_tag"]):
        result = prod_gen.run_one_pattern(
            client, THEME_ID, meta["label"], prompt, verified_ledger_text, TOWELS_TOPIC_JA, out_dir)
    elapsed = round(time.time() - t0, 2)

    article_text = result.get("article_text")
    insurance_hits = detect_insurance_sentences(article_text) if article_text else []
    summary = {k: v for k, v in result.items() if k != "article_text"}
    summary["elapsed_seconds"] = elapsed
    summary["word_count"] = len((article_text or "").split())
    summary["insurance_sentence_hits_broad_regex"] = insurance_hits
    summary["insurance_sentence_hit_count"] = len(insurance_hits)
    save_json(f"{out_dir}/run_summary.json", summary)
    print(f"[{THEME_ID}][{level}] article: status={result.get('status')} "
          f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')} "
          f"word_count={summary['word_count']} insurance_hits={len(insurance_hits)} elapsed={elapsed}s")
    return summary


# ============================================================
# Step 2: 評価(t9.analyze_runを無変更で流用。towels(本Trial)/Household
# 最終候補(HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01)双方の既存artifactを
# 同一関数で再分析し、比較可能な指標を得る。Household側artifactは
# 読み取りのみで一切変更しない)。
# ============================================================
HOUSEHOLD_FINAL_DIR = "er011_output/household_unified_final_candidate_01"


def evaluate_stage() -> dict:
    towels_analysis = {}
    for level in ("a2", "b1b"):
        out_dir = f"{OUT_DIR}/{level}"
        run_summary_path = f"{out_dir}/run_summary.json"
        if not os.path.exists(run_summary_path):
            print(f"[{THEME_ID}][evaluate] {level}: run_summary.jsonが無く、analyze_runをスキップします。")
            continue
        result = load_json(run_summary_path)
        analysis = t9.analyze_run(out_dir, result)
        analysis["insurance_sentence_hit_count"] = result.get("insurance_sentence_hit_count")
        analysis["insurance_sentence_hits_broad_regex"] = result.get("insurance_sentence_hits_broad_regex")
        save_json(f"{out_dir}/analysis.json", analysis)
        towels_analysis[level] = analysis

    household_analysis = {}
    for level in ("a2", "b1b"):
        out_dir = f"{HOUSEHOLD_FINAL_DIR}/{level}"
        run_summary_path = f"{out_dir}/run_summary.json"
        if not os.path.exists(run_summary_path):
            print(f"[{THEME_ID}][evaluate] household {level}: run_summary.jsonが見つかりません(スキップ)。")
            continue
        result = load_json(run_summary_path)
        analysis = t9.analyze_run(out_dir, result)
        household_analysis[level] = analysis

    comparison = {"towels_trial_11": towels_analysis, "household_unified_final_candidate_01": household_analysis}
    save_json(f"{OUT_DIR}/comparison_vs_household.json", comparison)
    print(f"[{THEME_ID}] evaluate_stage完了。towels={list(towels_analysis.keys())} "
          f"household={list(household_analysis.keys())}")
    return comparison


def main() -> dict:
    stages = sys.argv[1:] or ["all"]
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

    if stages == ["all"]:
        results = {}
        results["ledger"] = ledger_stage()
        results["gate4"] = gate4_check_stage()
        for level in ("a2", "b1b"):
            try:
                results[level] = generate_article_stage(level)
            except (RuntimeError, AssertionError) as e:
                results[level] = {"level": level, "status": "STOP", "error": str(e)}
                print(f"[{THEME_ID}][{level}] STOP: {e}")
            cost_stage()
        results["evaluate"] = evaluate_stage()
        save_json(f"{OUT_DIR}/e2e_run_summary.json", results)
        print(f"[{THEME_ID}] 完了。")
        return results

    result = {}
    for s in stages:
        if s == "ledger":
            result["ledger"] = ledger_stage()
        elif s == "gate4":
            result["gate4"] = gate4_check_stage()
        elif s in ("a2", "b1b"):
            result[s] = generate_article_stage(s)
        elif s == "evaluate":
            result["evaluate"] = evaluate_stage()
        elif s == "cost":
            result["cost"] = cost_stage()
        else:
            print(f"unknown stage: {s}")
    save_json(f"{OUT_DIR}/e2e_run_summary_partial_{'_'.join(stages)}.json", result)
    return result


if __name__ == "__main__":
    main()
