# ============================================================
# er011_discovery_stage3_rule_adjustment_trial_09.py
# FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09 (Lane A, D-3=(a))
# ============================================================
# 目的(ユーザー決定 2026-09-09): Household Verified Fact Ledger v5
# (`HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03_REPORT.md`、FACT-03から
# バナナ・トマトを除外しFACT-04との矛盾を解消済み)を前提として、現行
# Discovery Focus Module(見出し改稿版、Trial-07/Trial-08のcurrent_focusと
# 一字一句同一の本体)と、最小調整版(Trial-08 Part A案1、断定回避段落末尾
# へTrend Synthesis Focus Module:389-390と同型のscope一般化禁止文を追加。
# 案2[位置移動]は使わない)を、Article-only N=3で比較する。
#
# 目的の評価軸: REVIEW_REQUIREDを減らせるか / Fact Safety維持 /
# Discoveryらしさ / Pointの深さ / Point多様性 / 型にはまりすぎていないか。
# **Fact Checker側の緩和は禁止**、Writer側(Focus Module文言)の最小調整
# のみを検証する。Role文字列のヒューリスティック分類は行わない(D-2=(a)
# を踏襲、Point本文の目視比較へ切り替え)。
#
# **Trial(Production実装ではない)**。Production/Prompt/共有module/
# registry/SSOT編集・Ledger改変・Fact Checker緩和・Git操作は一切行わない。
# TTSは実行しない(text-onlyまで)。
#
# ------------------------------------------------------------
# 再利用(import・無変更、Trial-08と同一構成):
# ------------------------------------------------------------
#   - er003_v1_n3_01_articles_generate(prod_gen): THEMES(household、
#     ledger_pathは`er003_output/n3_01/household/research/
#     verified_fact_ledger.txt`を指し、v5修正が既に反映済みのファイルを
#     そのまま参照する。本Trialではファイルを一切書き換えない)/
#     build_common_block/build_prompt/A2_KAI1_INSTRUCTION/
#     B1_B_DIRECT_INSTRUCTION/compute_metrics/
#     split_common_sections_for_point_qa/run_one_pattern。無変更。
#   - er011_open112_a_family_4layer_prompt_trial_05(t5):
#     DISCOVERY_FOCUS_MODULE_BLOCK本文をそのまま再利用し、見出し行のみ
#     改稿(Trial-07/08と同型)。本体は一字一句不変(current_focus条件)。
#     adjusted_focus条件は、この不変本体の断定回避段落へ1文だけ追加する
#     (Trial-08で使用したadjusted版と完全同一文言、Trend Synthesis Focus
#     Module:389-390と同型の文言を再利用。新原則の追加ではない)。
#   - er005_cost_logger(cl): install / logging_context。無変更。
#
# 費用上限: ¥130(Trial-08実測¥70.8/8本→12本(N=3)で約¥106の投影。超過
# 見込みならN=2へ縮小し報告する。run_idxごとにバッチ実行し、都度
# cumulative費用を確認しながら進める)。冒頭で必ずcl.install()を有効化する。
# ============================================================
from __future__ import annotations

import difflib
import json
import os
import re
import time
from collections import defaultdict

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er003_v1_spoken_first_01_r1_generate as sf1r1
import er005_cost_logger as cl
import er011_open112_a_family_4layer_prompt_trial_05 as t5

THEME_ID = "discovery_stage3_rule_adjustment_trial_09"
OUT_DIR = f"er011_output/{THEME_ID}"

N_RUNS_PLANNED = 3  # ユーザー指定(N=3)。費用状況に応じて縮小する場合がある(下記run_budget_guard参照)。
BUDGET_JPY = 130.0

HOUSEHOLD_THEME = next(t for t in prod_gen.THEMES if t["theme_id"] == "household")
HOUSEHOLD_TOPIC_JA = HOUSEHOLD_THEME["topic"]
HOUSEHOLD_LEDGER_PATH = HOUSEHOLD_THEME["ledger_path"]  # v5(2026-09-09、FACT-03/04整合修正済み)を直接参照

LEVELS = [
    ("B1B", prod_gen.B1_B_DIRECT_INSTRUCTION, "b1b", "writer_b1"),
    ("A2", prod_gen.A2_KAI1_INSTRUCTION, "a2", "writer_a2"),
]

# ------------------------------------------------------------
# current_focus: Trial-05本体をそのまま再利用、見出しのみTrial-09向けに
# 改稿(VALIDATED/Production採用を偽って主張しない)。
# ------------------------------------------------------------
_ORIGINAL_BLOCK = t5.DISCOVERY_FOCUS_MODULE_BLOCK
_ORIGINAL_HEADER_LINE = ("【Discovery/Why Focus(今回のTrialで追加する、記事タイプ固有の焦点。"
                          "OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05、Production未採用)】")
assert _ORIGINAL_BLOCK.startswith(_ORIGINAL_HEADER_LINE + "\n"), (
    "Trial-05のDISCOVERY_FOCUS_MODULE_BLOCK見出し行が想定と異なります。本文が変更されている"
    "可能性があるため、内容不変の前提が崩れます(STOP条件)。")
_BODY_AFTER_HEADER = _ORIGINAL_BLOCK[len(_ORIGINAL_HEADER_LINE) + 1:]

CURRENT_HEADER_LINE = (
    "【Discovery/Why Focus(記事タイプ固有の焦点。OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-"
    "TRIAL-05でArticle-only N=1検証(VALIDATED)、FAMILY-A-COMPLETION-A4-DISCOVERY-LAYER3-"
    "TRIAL-07でHousehold Ledger v3によるN=3再検証、FAMILY-A-DISCOVERY-STAGE2-INTERPRETATION-"
    "RULE-TRIAL-08でHousehold Ledger v4によるN=2再検証、FAMILY-A-DISCOVERY-STAGE3-RULE-"
    "ADJUSTMENT-TRIAL-09でHousehold Ledger v5(FACT-03/04整合修正版)によるN=3再検証中。"
    "Production未採用。editorial_mode=\"discovery_why\"は未登録の想定名)】"
)
CURRENT_FOCUS_BLOCK = CURRENT_HEADER_LINE + "\n" + _BODY_AFTER_HEADER
assert CURRENT_FOCUS_BLOCK[len(CURRENT_HEADER_LINE):] == "\n" + _BODY_AFTER_HEADER
assert _BODY_AFTER_HEADER == _ORIGINAL_BLOCK[len(_ORIGINAL_HEADER_LINE) + 1:]

# ------------------------------------------------------------
# adjusted_focus: Trial-08 Part A案1(scope-clause追加)と完全同一文言。
# 断定回避段落(現行:161-165相当)の末尾へ、Trend Synthesis Focus Module
# :389-390「証拠が一部の当事者・一部の期間・一部の地域にしか及ばない場合
# は、その範囲を実際より広く一般化しないでください」と同型の1文を追加する
# のみ。新しい原則の追加ではなく、既存の断定回避段落を、対象の広さ
# (scope)という観点でも具体化する最小変更。他の段落は一切変更しない。
# 案2(位置移動)は使わない(委任文の指定どおり)。
# ------------------------------------------------------------
_HEDGE_PARAGRAPH_ANCHOR = (
    "Ledgerが直接支持していない限り、「自動的」「不随意的」「必ず」のような\n"
    "断定表現は使わないでください。"
)
assert _HEDGE_PARAGRAPH_ANCHOR in _BODY_AFTER_HEADER, (
    "断定回避段落の末尾アンカー文字列が本体に見つかりません。本文が変更されている可能性が"
    "あるため、挿入位置の前提が崩れます(STOP条件)。")

_SCOPE_CLAUSE = (
    " また、ある品目・状況について成り立つ仕組みの説明を、Verified Fact Ledgerが名指しして"
    "いない他の品目・状況にまで広げて一般化しないでください。証拠が特定の品目や条件にしか"
    "及んでいない場合は、その範囲を実際より広く一般化しないでください。"
)
_ADJUSTED_BODY_AFTER_HEADER = _BODY_AFTER_HEADER.replace(
    _HEDGE_PARAGRAPH_ANCHOR, _HEDGE_PARAGRAPH_ANCHOR + _SCOPE_CLAUSE, 1)
assert _ADJUSTED_BODY_AFTER_HEADER != _BODY_AFTER_HEADER
# 挿入が単一のinsertであることを機械確認する(Gate 4相当、新規段落の追加ではなく
# 既存段落末尾への1文追加のみであることの静的確認)。
_body_diff_ops = [op for op in difflib.SequenceMatcher(
    a=_BODY_AFTER_HEADER, b=_ADJUSTED_BODY_AFTER_HEADER, autojunk=False).get_opcodes() if op[0] != "equal"]
assert len(_body_diff_ops) == 1 and _body_diff_ops[0][0] == "insert", (
    f"adjusted_focus本体への変更が単一のinsertではありません(STOP条件、実際: {_body_diff_ops})")

ADJUSTED_HEADER_LINE = (
    "【Discovery/Why Focus(記事タイプ固有の焦点、最小調整版[Trial-08 Part A案1と完全同一文言、"
    "未承認候補]。既存の断定回避段落の末尾へscope-generalization禁止の1文のみ追加[Trend "
    "Synthesis Focus Module:389-390と同型の文言を再利用]、他は現行版[Trial-05/07/08]と一字一句"
    "同一。FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09でHousehold Ledger v5(FACT-03/04"
    "整合修正版)によるN=3検証中。Production未採用。editorial_mode=\"discovery_why\"は未登録の"
    "想定名)】"
)
ADJUSTED_FOCUS_BLOCK = ADJUSTED_HEADER_LINE + "\n" + _ADJUSTED_BODY_AFTER_HEADER

CONDITIONS = {
    "current_focus": {"editorial_type_module_block": CURRENT_FOCUS_BLOCK},
    "adjusted_focus": {"editorial_type_module_block": ADJUSTED_FOCUS_BLOCK},
}

# ------------------------------------------------------------
# claim→evidence id 機械分類用キーワード(Trial-07/08から再利用、無変更)。
# FACT-03/04起因かどうかの一次分類に使う(ユーザー決定の計測要件)。
# ------------------------------------------------------------
HOUSEHOLD_FACT_KEYWORDS = {
    "FACT-01": ["crisper", "drawer", "low-humidity", "low humidity", "high-humidity", "high humidity",
                "two settings", "two types", "vent", "sealed", "airtight", "slider", "dial"],
    "FACT-02": ["ethylene", "ripen", "ripening", "gas", "spoil", "spoiling"],
    "FACT-03": ["ethylene", "wilt", "wilting", "moisture", "water", "apple", "pear", "banana", "tomato",
                "kale", "leafy", "broccoli", "strawberr", "citrus", "orange", "exception", "fruit-or-vegetable",
                "fruit-versus-vegetable", "category"],
    "FACT-04": ["tomato", "banana", "potato", "sweet potato", "onion", "garlic", "room temperature",
                "counter", "refrigerat", "cool", "dry spot", "cool, dry"],
}


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# Gate 4: 静的diff(Production関数を再定義・monkeypatchしていないことの
# 機械確認、Trial-07/08と同一ロジック)。
# ============================================================
def gate4_static_check() -> dict:
    used_names = ["THEMES", "build_common_block", "build_prompt", "A2_KAI1_INSTRUCTION",
                  "B1_B_DIRECT_INSTRUCTION", "compute_metrics", "split_common_sections_for_point_qa",
                  "run_one_pattern", "POINT_TARGET_LOWER", "POINT_TARGET_UPPER",
                  "POINT_TOLERANCE_LOWER", "POINT_TOLERANCE_UPPER"]
    not_reassigned = all(name in vars(prod_gen) for name in used_names)

    placeholder_present = "{editorial_type_module_block}" in prod_gen.COMMON_BLOCK_TEMPLATE

    master_full_text = ab01.load_master_full_text()
    verified_ledger_text = load_text(HOUSEHOLD_LEDGER_PATH)
    baseline_common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text, editorial_type_module_block="")
    legacy_style_block = prod_gen.COMMON_BLOCK_TEMPLATE.format(
        hanshin_master_full_text=master_full_text, topic=HOUSEHOLD_TOPIC_JA,
        verified_ledger_text=verified_ledger_text, shared_point_blueprint_block="",
        evidence_compression_block="", editorial_type_module_block="")
    baseline_byte_identical_to_legacy_template = baseline_common_block == legacy_style_block

    current_common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=CURRENT_FOCUS_BLOCK)
    adjusted_common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=ADJUSTED_FOCUS_BLOCK)
    # baseline(block="")との比較は、それぞれが「baselineへの単一insert」で
    # あることを確認する(見出し行はcurrent/adjustedで意図的に異なるため、
    # current対adjustedの直接diffではなく、baseline基準で個別に確認する)。
    current_vs_baseline_ops = [op for op in difflib.SequenceMatcher(
        a=baseline_common_block, b=current_common_block, autojunk=False).get_opcodes() if op[0] != "equal"]
    adjusted_vs_baseline_ops = [op for op in difflib.SequenceMatcher(
        a=baseline_common_block, b=adjusted_common_block, autojunk=False).get_opcodes() if op[0] != "equal"]
    current_single_clean_insert = (len(current_vs_baseline_ops) == 1 and current_vs_baseline_ops[0][0] == "insert")
    adjusted_single_clean_insert = (len(adjusted_vs_baseline_ops) == 1 and adjusted_vs_baseline_ops[0][0] == "insert")
    # current対adjustedの本体(見出し除く)への変更が単一insertであることは
    # モジュール読み込み時に_body_diff_opsで既に機械assert済み(この関数へ
    # 到達している時点でPASS済み)。ここでは記録のみ行う。
    body_diff_op_count = len(_body_diff_ops)

    # Ledgerがv5であることの機械確認(FACT-03からbanana/tomatoの低湿度ドロワー
    # 例が除外されていることをgrepで確認、STOP条件「新しいLedger課題」を
    # 誤って古いv4のまま検証しないための安全弁)。
    ledger_has_v5_marker = "v5" in verified_ledger_text

    conclusion = ("PASS" if (not_reassigned and placeholder_present
                              and baseline_byte_identical_to_legacy_template
                              and current_single_clean_insert and adjusted_single_clean_insert
                              and body_diff_op_count == 1 and ledger_has_v5_marker)
                  else "FAIL_NEEDS_REVIEW")

    result = {
        "prod_gen_used_names_present_and_not_reassigned": not_reassigned,
        "common_block_template_has_editorial_type_module_block_placeholder": placeholder_present,
        "baseline_common_block_byte_identical_to_legacy_pre_placeholder_template": baseline_byte_identical_to_legacy_template,
        "current_vs_baseline_diff_is_single_clean_insert": current_single_clean_insert,
        "adjusted_vs_baseline_diff_is_single_clean_insert": adjusted_single_clean_insert,
        "current_vs_adjusted_body_diff_op_count": body_diff_op_count,
        "ledger_has_v5_marker": ledger_has_v5_marker,
        "conclusion": conclusion,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/gate4_static_check.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit_current_focus_block.txt", "w", encoding="utf-8") as f:
        f.write(CURRENT_FOCUS_BLOCK)
    with open(f"{OUT_DIR}/audit_adjusted_focus_block.txt", "w", encoding="utf-8") as f:
        f.write(ADJUSTED_FOCUS_BLOCK)
    diff_lines = list(difflib.unified_diff(
        CURRENT_FOCUS_BLOCK.splitlines(keepends=True), ADJUSTED_FOCUS_BLOCK.splitlines(keepends=True),
        fromfile="current_focus_block", tofile="adjusted_focus_block", n=2))
    with open(f"{OUT_DIR}/audit_current_vs_adjusted_diff.txt", "w", encoding="utf-8") as f:
        f.writelines(diff_lines)
    print(f"[{THEME_ID}] gate4_static_check: {result['conclusion']}")
    if conclusion != "PASS":
        raise RuntimeError(f"Gate 4静的diff失敗: {result}")
    return result


def build_run_metadata() -> dict:
    return {
        "management_id": "FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09",
        "mode_supply_path": "手動Mode判定+手動Ledger供給(Trial-07/08と同じ機構)。",
        "editorial_mode_determination": "DISCOVERY_WHY",
        "two_axis_determination": {
            "source": "FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-02_REPORT.md §2.1"
                      "(既決A-UDR-9の再確認・転記のみ、本Trialで新規判定は行っていない)。",
            "result": "DISCOVERY_WHY(Household、Trial-07/08と同一)。",
        },
        "ledger_version": "v5(2026-09-09、HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03[OPEN-138継続]で"
                          "FACT-03からりんご・洋梨のみに絞り込み[バナナ・トマトを除外、FACT-04との矛盾を"
                          "解消]。FACT-04は無変更)。",
        "role_string_classification": "実施しない(D-2=(a)を踏襲、Role文字列のヒューリスティック分類は行わず、"
                                       "Point本文の目視比較[comparison.html]へ切り替え)。",
        "fact_checker_side_changes": "なし(Fact Checker緩和は禁止。Writer側[Focus Module文言]の"
                                     "最小調整のみを検証)。",
    }


# ============================================================
# 費用実測ヘルパー(Trial-07/08と同一の参照元・同一ロジック)。
# ============================================================
USD_JPY = 160.0
PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def _price(provider, model, meter):
    return next(p["price"] for p in PRICING if p["provider"] == provider and p["model"] == model and p["meter"] == meter)


_LUNA_IN, _LUNA_CACHED, _LUNA_OUT = _price("openai", "gpt-5.6-luna", "input_tokens"), \
    _price("openai", "gpt-5.6-luna", "cached_input_tokens"), _price("openai", "gpt-5.6-luna", "output_tokens")
_SOL_IN, _SOL_CACHED, _SOL_OUT = _price("openai", "gpt-5.6-sol", "input_tokens"), \
    _price("openai", "gpt-5.6-sol", "cached_input_tokens"), _price("openai", "gpt-5.6-sol", "output_tokens")
_WEB_SEARCH_CALL = _price("openai", "N/A (tool, all models)", "web_search_call")


def _call_cost_usd(r: dict) -> float:
    provider, model = r["provider"], r.get("model_id")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    if provider != "openai":
        raise ValueError(f"unpriced provider (text-only trial, no TTS/ASR expected): {provider}")
    billable_in = max(it - ct, 0)
    if model == "gpt-5.6-luna":
        cost = (billable_in / 1e6) * _LUNA_IN + (ct / 1e6) * _LUNA_CACHED + (ot / 1e6) * _LUNA_OUT
    elif model == "gpt-5.6-sol":
        cost = (billable_in / 1e6) * _SOL_IN + (ct / 1e6) * _SOL_CACHED + (ot / 1e6) * _SOL_OUT
    else:
        raise ValueError(f"unpriced openai model: {model}")
    web_search_calls = r.get("web_search_call_count") or 0
    cost += (web_search_calls / 1000) * _WEB_SEARCH_CALL
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
    by_theme, counts = defaultdict(float), defaultdict(int)
    for r in records:
        by_theme[r["theme"]] += r["_cost_usd"]
        counts[r["theme"]] += 1
    by_condition, by_level, by_run = defaultdict(float), defaultdict(float), defaultdict(float)
    for theme, cost in by_theme.items():
        rest = theme[len(THEME_ID) + 1:]
        parts = rest.rsplit("_run", 1)
        if len(parts) == 2:
            cond_level, run_idx = parts
            cond_parts = cond_level.rsplit("_", 1)
            if len(cond_parts) == 2:
                condition, level = cond_parts
                by_run[f"run{run_idx}"] += cost
                by_condition[condition] += cost
                by_level[level] += cost
    result = {
        "usd_jpy_rate": USD_JPY,
        "methodology": "全て実測usage(actual)。単価はer005_output/cost_baseline_01/"
                       "pricing_snapshot.json(OFFICIAL_SOURCE、Trial-07/08と同一参照元・同一ロジック)。"
                       "text-onlyのためprovider=openaiのみを想定。",
        "by_theme_jpy": {k: round(v * USD_JPY, 1) for k, v in by_theme.items()},
        "by_run_jpy": {k: round(v * USD_JPY, 1) for k, v in by_run.items()},
        "by_condition_jpy": {k: round(v * USD_JPY, 1) for k, v in by_condition.items()},
        "by_level_jpy": {k: round(v * USD_JPY, 1) for k, v in by_level.items()},
        "call_counts": dict(counts),
        "total_usd": round(sum(by_theme.values()), 4),
        "total_jpy": round(sum(by_theme.values()) * USD_JPY, 1),
        "total_calls": len(records),
    }
    with open(f"{OUT_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


# ============================================================
# 分析ヘルパー(Trial-07/08と同一ロジック)。
# ============================================================
def classify_claim_to_evidence(claim_text: str) -> dict:
    lower = claim_text.lower()
    scores = {fid: sum(1 for kw in kws if kw in lower) for fid, kws in HOUSEHOLD_FACT_KEYWORDS.items()}
    best_fid, best_score = max(scores.items(), key=lambda kv: kv[1])
    if best_score == 0:
        return {"judgement": "LEDGER_OUTSIDE_OR_NO_LEXICAL_MATCH", "evidence_id": None,
                "score": 0, "scores": scores}
    return {"judgement": f"LIKELY_INTERPRETATION_OF_{best_fid}", "evidence_id": best_fid,
            "score": best_score, "scores": scores}


_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"])")


def split_sentences_simple(text: str) -> list[str]:
    flat = " ".join(line.strip() for line in text.splitlines()
                     if line.strip() and not line.strip().startswith("#"))
    return [s.strip() for s in _SENT_SPLIT_RE.split(flat) if s.strip()]


def detect_near_duplicate_sentences(sentences: list[str], ratio_threshold: float = 0.55,
                                     min_words: int = 6) -> list[dict]:
    pairs = []
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            a, b = sentences[i], sentences[j]
            if len(a.split()) < min_words or len(b.split()) < min_words:
                continue
            ratio = difflib.SequenceMatcher(a=a.lower(), b=b.lower()).ratio()
            if ratio >= ratio_threshold:
                pairs.append({"sentence_a": a, "sentence_b": b, "ratio": round(ratio, 3)})
    return pairs


def analyze_run(out_dir: str, result: dict) -> dict:
    retry_attempts = result.get("point_overlap_article_retry_attempts") or 0

    word_count = None
    section_wc = None
    word_overflow = None
    duplicate_pairs = None
    point_one_text = point_two_text = full_story_text = None
    article_path = f"{out_dir}/article.md"
    if os.path.exists(article_path):
        article_text = load_text(article_path)
        metrics = prod_gen.compute_metrics(article_text)
        word_count = metrics["word_count"]
        section_wc = sf1r1.section_word_counts(article_text)
        word_overflow = {
            key: {
                "word_count": section_wc.get(key),
                "exceeds_tolerance_upper": (section_wc.get(key) or 0) > prod_gen.POINT_TOLERANCE_UPPER,
                "exceeds_target_upper": (section_wc.get(key) or 0) > prod_gen.POINT_TARGET_UPPER,
            } for key in ("point_one", "point_two")
        }
        sentences = split_sentences_simple(article_text)
        duplicate_pairs = detect_near_duplicate_sentences(sentences)

        sections = prod_gen.split_common_sections_for_point_qa(article_text)
        if sections:
            full_story_text = sections["full_story"]
            point_one_text = sections["point_one_heading"] + "\n" + sections["point_one_body"]
            point_two_text = sections["point_two_heading"] + "\n" + sections["point_two_body"]
    else:
        metrics = {}

    fact_qa_path = f"{out_dir}/fact_qa.json"
    fact_verdict = result.get("fact_verdict")
    unsupported_claims = []
    if os.path.exists(fact_qa_path):
        fact_qa = json.load(open(fact_qa_path, encoding="utf-8"))
        fc_result = fact_qa.get("result") or {}
        fact_verdict = fc_result.get("verdict", fact_verdict)
        unsupported_claims = fc_result.get("unsupported_specific_claims") or []

    ledger_deviation_count = result.get("ledger_deviation_count")
    local_rewrite_cycles_count = 0
    local_rewrite_item_count = 0
    local_rewrite_human_review_count = 0
    local_rewrite_cycles_path = f"{out_dir}/audit/local_rewrite_cycles.json"
    local_rewrite_results_path = f"{out_dir}/audit/local_rewrite_results.json"
    if os.path.exists(local_rewrite_cycles_path):
        cycles = json.load(open(local_rewrite_cycles_path, encoding="utf-8"))
        local_rewrite_cycles_count = len(cycles)
    if os.path.exists(local_rewrite_results_path):
        items = json.load(open(local_rewrite_results_path, encoding="utf-8"))
        local_rewrite_item_count = len(items)
        local_rewrite_human_review_count = sum(1 for it in items if it.get("human_review_required"))

    # cross_point_overlap(Point間分化度、既存Production機構[run_point_overlap_qa_and_regenerate]の
    # 出力をそのまま読むだけ。新しい指標は計算しない)。
    cross_point_overlap = None
    point_overlap_qa_path = f"{out_dir}/point_overlap_qa.json"
    if os.path.exists(point_overlap_qa_path):
        qa = json.load(open(point_overlap_qa_path, encoding="utf-8"))
        p1 = qa.get("point_one", {}).get("cross_point_overlap", {})
        p2 = qa.get("point_two", {}).get("cross_point_overlap", {})
        cross_point_overlap = {
            "point_one_vs_point_two_ratio": p1.get("overlap_ratio"),
            "point_one_vs_point_two_flagged": p1.get("flagged"),
            "point_two_vs_point_one_ratio": p2.get("overlap_ratio"),
            "point_two_vs_point_one_flagged": p2.get("flagged"),
        }

    return {
        "status": result.get("status"),
        "retry_attempts": retry_attempts,
        "word_count": word_count,
        "section_word_counts": section_wc,
        "word_overflow": word_overflow,
        "near_duplicate_sentence_pairs": duplicate_pairs,
        "near_duplicate_sentence_pair_count": len(duplicate_pairs) if duplicate_pairs is not None else None,
        "avg_sentence_length": metrics.get("avg_sentence_length"),
        "max_sentence_length": metrics.get("max_sentence_length"),
        "fact_verdict": fact_verdict,
        "fact_unsupported_specific_claims": unsupported_claims,
        "fact_unsupported_specific_claims_count": len(unsupported_claims),
        "ledger_status": result.get("ledger_status"),
        "ledger_deviation_count": ledger_deviation_count,
        "local_rewrite_cycles_count": local_rewrite_cycles_count,
        "local_rewrite_item_count": local_rewrite_item_count,
        "local_rewrite_human_review_count": local_rewrite_human_review_count,
        "directional_fact_precheck_status": result.get("directional_fact_precheck_status"),
        "cross_point_overlap": cross_point_overlap,
        "full_story_text": full_story_text,
        "point_one_text": point_one_text,
        "point_two_text": point_two_text,
    }


def run_one_combo(client, master_full_text: str, verified_ledger_text: str,
                   condition_name: str, run_idx: int, label: str, instruction: str,
                   level_dir: str, stage_tag: str) -> dict:
    cond = CONDITIONS[condition_name]
    out_dir = f"{OUT_DIR}/{level_dir}/{condition_name}/run{run_idx}"
    common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=cond["editorial_type_module_block"])
    prompt = prod_gen.build_prompt(common_block, instruction)
    theme_tag = f"{THEME_ID}_{condition_name}_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, stage_tag):
        result = prod_gen.run_one_pattern(
            client, theme_tag, label, prompt, verified_ledger_text, HOUSEHOLD_TOPIC_JA, out_dir)
    elapsed = round(time.time() - t0, 2)
    analysis = analyze_run(out_dir, result)
    analysis["elapsed_seconds"] = elapsed
    analysis["condition"] = condition_name
    analysis["level"] = label
    analysis["run"] = run_idx

    analysis["claim_to_evidence_table"] = [
        {"claim": c, **classify_claim_to_evidence(c)}
        for c in analysis["fact_unsupported_specific_claims"]
    ] if analysis["fact_unsupported_specific_claims"] else []

    with open(f"{out_dir}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in result.items() if k != "article_text"}, f, ensure_ascii=False,
                   indent=2, default=str)
    with open(f"{out_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] run{run_idx} {condition_name} {label}: status={result.get('status')} "
          f"fact_verdict={analysis['fact_verdict']} unsupported_claims={analysis['fact_unsupported_specific_claims_count']} "
          f"ledger_status={analysis['ledger_status']} local_rewrite_items={analysis['local_rewrite_item_count']} "
          f"word_count={analysis['word_count']} elapsed={elapsed}s")
    return analysis


LABEL_LOOKUP = {label: (label, instruction, level_dir, stage_tag)
                for (label, instruction, level_dir, stage_tag) in LEVELS}
COMBO_RESULTS_DIR = f"{OUT_DIR}/_combo_results"


def setup_stage() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    gate4_result = gate4_static_check()
    run_metadata = build_run_metadata()
    with open(f"{OUT_DIR}/run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(run_metadata, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] setup_stage完了: gate4={gate4_result['conclusion']}")
    return {"gate4_result": gate4_result, "run_metadata": run_metadata}


def combo_stage(condition_name: str, label: str, run_idx: int) -> dict:
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    verified_ledger_text = load_text(HOUSEHOLD_LEDGER_PATH)
    _, instruction, level_dir, stage_tag = LABEL_LOOKUP[label]
    analysis = run_one_combo(client, master_full_text, verified_ledger_text, condition_name,
                              run_idx, label, instruction, level_dir, stage_tag)
    os.makedirs(COMBO_RESULTS_DIR, exist_ok=True)
    with open(f"{COMBO_RESULTS_DIR}/{condition_name}_{level_dir}_run{run_idx}.json", "w",
              encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    return analysis


def cost_stage() -> dict:
    result = write_cost_summary()
    print(f"[{THEME_ID}] 費用実測合計: ¥{result['total_jpy']}")
    return result


def aggregate_stage() -> list:
    all_results = []
    if os.path.isdir(COMBO_RESULTS_DIR):
        for fname in sorted(os.listdir(COMBO_RESULTS_DIR)):
            with open(f"{COMBO_RESULTS_DIR}/{fname}", encoding="utf-8") as f:
                all_results.append(json.load(f))
    with open(f"{OUT_DIR}/all_results_so_far.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] aggregate_stage: {len(all_results)}本を集約しました。")
    return all_results


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "setup"
    if which == "setup":
        setup_stage()
    elif which == "combo":
        condition_name, label, run_idx = sys.argv[2], sys.argv[3], int(sys.argv[4])
        combo_stage(condition_name, label, run_idx)
    elif which == "cost":
        cost_stage()
    elif which == "aggregate":
        aggregate_stage()
    else:
        print("usage: python er011_discovery_stage3_rule_adjustment_trial_09.py "
              "[setup|combo <condition> <A2|B1B> <run_idx>|cost|aggregate]")
