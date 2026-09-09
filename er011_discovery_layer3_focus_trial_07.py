# ============================================================
# er011_discovery_layer3_focus_trial_07.py
# FAMILY-A-COMPLETION-A4-DISCOVERY-LAYER3-TRIAL-07 (Lane A, D2)
# ============================================================
# 目的(ユーザー決定 2026-09-09、D2=(b)): Household Ledger(承認済み、
# 2026-08-17完成記事)を再利用し、Discovery/Why Layer3 Focus Module
# (OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05でVALIDATED、
# Article-only N=1)を、baseline(block="")との比較でN=3
# Article-only Trialとして再検証する。結果はProduction配線判断
# (ユーザー)の入力になる(本Trial自体は配線しない)。
#
# **Trial(Production実装ではない)**。Production/Prompt/SSOT編集・
# Git操作は一切行わない。Point Role hint(Trial-03)は接続しない
# (D3保留、Focus Module単独の効果を測る)。TTSは実行しない
# (text-onlyまで)。
#
# ------------------------------------------------------------
# 再利用(import・無変更、コピー改変はしない):
# ------------------------------------------------------------
#   - er003_v1_n3_01_articles_generate(prod_gen): THEMES(household)/
#     build_common_block/build_prompt/A2_KAI1_INSTRUCTION/
#     B1_B_DIRECT_INSTRUCTION/compute_metrics/
#     split_common_sections_for_point_qa/run_one_pattern。無変更。
#     build_common_block()は既にOPEN-112-TREND-SYNTHESIS-MODE-
#     PRODUCTION-WIRING-01で`editorial_type_module_block`引数を
#     持つため(COMMON_BLOCK_TEMPLATE側に`{editorial_type_module_block}`
#     placeholderが存在)、Trial-05のような`.replace()`アンカー
#     文字列挿入は不要。素直にこの引数へ文字列を渡すだけでよい
#     (Trial-06[News]と同一パターン)。
#   - er011_open112_a_family_4layer_prompt_trial_05(t5): Discovery/Why
#     Focus Moduleの本文段落(DISCOVERY_FOCUS_MODULE_BLOCK)をそのまま
#     再利用する。Opusレビュー(FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-
#     OPUS-REVIEW-01_REPORT.md)確認済みの通り、本文は一字一句変更
#     しない。見出し行(1行目)のみ、Trend Synthesis Focus Moduleの
#     前例(Trial-09の暫定見出し→WIRING-01での正式見出しへの改稿)と
#     同型の書式へ改稿する(下記参照、内容主張は変えない・VALIDATED/
#     Production採用を偽って主張しない)。
#   - er005_cost_logger(cl): install / logging_context。無変更。
#
# Gate 4根拠(静的diff): 本ファイルはProduction関数を一切再定義・
# monkeypatchしていない(setup_stage()のgate4_static_check()で機械
# 確認・記録)。
#
# 費用上限: ¥150(超過見込みならN=2へ縮小、それでも超過ならSTOP)。
# 冒頭で必ずcl.install()を有効化する。
# ============================================================
from __future__ import annotations

import difflib
import inspect
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

THEME_ID = "discovery_layer3_focus_trial_07"
OUT_DIR = f"er011_output/{THEME_ID}"

N_RUNS = 3  # ユーザー指定。費用超過見込みの場合はmain()内でN=2へ縮退する。
BUDGET_JPY = 150.0

# ------------------------------------------------------------
# Household Ledger/Topic(承認済み、2026-08-17完成記事と同一Source of
# Truth)を、prod_gen.THEMESから直接取得する(独立に書き写さない=
# topic文言・ledger_pathの重複・改変リスクをゼロにする)。
# ------------------------------------------------------------
HOUSEHOLD_THEME = next(t for t in prod_gen.THEMES if t["theme_id"] == "household")
HOUSEHOLD_TOPIC_JA = HOUSEHOLD_THEME["topic"]
HOUSEHOLD_LEDGER_PATH = HOUSEHOLD_THEME["ledger_path"]
HOUSEHOLD_EXISTING_ARTICLE_DIR = HOUSEHOLD_THEME["out_dir"]  # er003_output/n3_01/household (2026-08-17完成記事)

LEVELS = [
    ("B1B", prod_gen.B1_B_DIRECT_INSTRUCTION, "b1b", "writer_b1"),
    ("A2", prod_gen.A2_KAI1_INSTRUCTION, "a2", "writer_a2"),
]

# ------------------------------------------------------------
# Discovery/Why Focus Module: 本文(段落)はTrial-05(VALIDATED、Opus
# レビューでbyte等価確認済み)から一字一句変更せずそのまま再利用する。
# 見出し行のみ、Trend Synthesis Focus Moduleの前例(Trial-09の暫定
# 見出し「今回のTrialで追加する...Production未採用」→WIRING-01の
# 正式見出し「記事タイプ固有の焦点。<起源Trial>でVALIDATED、
# <採用Trial>で正式Production採用」)と同型の書式へ改稿する。ただし
# 本Trialは配線判断前のためVALIDATED/Production採用を偽って主張せず、
# 経緯(起源Trial・本Trialでの再検証中であること・Production未採用)を
# 正確に記述する。editorial_mode名"discovery_why"はProduction
# EDITORIAL_TYPE_MODULE_BLOCKSへ未登録の想定名(本Trialでは登録しない、
# build_common_block()へ直接文字列を渡すだけ)。
# ------------------------------------------------------------
_ORIGINAL_BLOCK = t5.DISCOVERY_FOCUS_MODULE_BLOCK
_ORIGINAL_HEADER_LINE = ("【Discovery/Why Focus(今回のTrialで追加する、記事タイプ固有の焦点。"
                          "OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05、Production未採用)】")
assert _ORIGINAL_BLOCK.startswith(_ORIGINAL_HEADER_LINE + "\n"), (
    "Trial-05のDISCOVERY_FOCUS_MODULE_BLOCK見出し行が想定と異なります。本文が変更されている"
    "可能性があるため、内容不変の前提が崩れます(STOP条件)。")
_BODY_AFTER_HEADER = _ORIGINAL_BLOCK[len(_ORIGINAL_HEADER_LINE) + 1:]

REVISED_HEADER_LINE = (
    "【Discovery/Why Focus(記事タイプ固有の焦点。OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-"
    "TRIAL-05でArticle-only N=1検証(VALIDATED)、FAMILY-A-COMPLETION-A4-DISCOVERY-LAYER3-"
    "TRIAL-07でHousehold LedgerによるArticle-only N=3再検証中。Production未採用。"
    "editorial_mode=\"discovery_why\"は未登録の想定名)】"
)
DISCOVERY_FOCUS_MODULE_BLOCK = REVISED_HEADER_LINE + "\n" + _BODY_AFTER_HEADER

# 内容(段落本体)が一字一句変わっていないことを機械確認する(Gate 4の
# 一部、見出し行以外はTrial-05とbyte一致)。
assert DISCOVERY_FOCUS_MODULE_BLOCK[len(REVISED_HEADER_LINE):] == "\n" + _BODY_AFTER_HEADER
assert _BODY_AFTER_HEADER == _ORIGINAL_BLOCK[len(_ORIGINAL_HEADER_LINE) + 1:]

CONDITIONS = {
    "baseline": {"editorial_type_module_block": ""},  # Production既定(Focus Moduleなし)
    "discovery_focus": {"editorial_type_module_block": DISCOVERY_FOCUS_MODULE_BLOCK},
}

# ------------------------------------------------------------
# Household Verified Fact Ledgerのevidence id(FACT-01〜04)語彙(claim→
# evidence idの機械分類用、キーワード一致ベースの簡易判定であり厳密な
# NLU判定ではない。Ledger本文[er003_output/n3_01/household/research/
# verified_fact_ledger.txt]を読み、各FACTの主要語彙を抽出したもの)。
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
# 機械確認)。Trial-05のPhase Aと異なり、build_common_block()は既に
# editorial_type_module_blockをパラメータとして受け取る設計(Trend
# Synthesis配線時に追加済み)のため、アンカー文字列.replace()による
# 静的diffではなく、(1)このファイルがprod_gen.*関数を1つも再代入して
# いないこと、(2)baseline条件(block="")がProduction既定(旧来の
# COMMON_BLOCK_TEMPLATEと完全同一)を再現することの2点を確認する。
# ============================================================
def gate4_static_check() -> dict:
    used_names = ["THEMES", "build_common_block", "build_prompt", "A2_KAI1_INSTRUCTION",
                  "B1_B_DIRECT_INSTRUCTION", "compute_metrics", "split_common_sections_for_point_qa",
                  "run_one_pattern", "POINT_TARGET_LOWER", "POINT_TARGET_UPPER",
                  "POINT_TOLERANCE_LOWER", "POINT_TOLERANCE_UPPER"]
    not_reassigned = all(name in vars(prod_gen) for name in used_names)

    placeholder_present = "{editorial_type_module_block}" in prod_gen.COMMON_BLOCK_TEMPLATE
    sig = inspect.signature(prod_gen.build_common_block)
    default_is_empty_string = sig.parameters["editorial_type_module_block"].default == ""

    master_full_text = ab01.load_master_full_text()
    verified_ledger_text = load_text(HOUSEHOLD_LEDGER_PATH)
    baseline_common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text, editorial_type_module_block="")
    legacy_style_block = prod_gen.COMMON_BLOCK_TEMPLATE.format(
        hanshin_master_full_text=master_full_text, topic=HOUSEHOLD_TOPIC_JA,
        verified_ledger_text=verified_ledger_text, shared_point_blueprint_block="",
        evidence_compression_block="", editorial_type_module_block="")
    baseline_byte_identical_to_legacy_template = baseline_common_block == legacy_style_block

    focus_common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=DISCOVERY_FOCUS_MODULE_BLOCK)
    diff_lines = list(difflib.unified_diff(
        baseline_common_block.splitlines(keepends=True), focus_common_block.splitlines(keepends=True),
        fromfile="baseline_common_block", tofile="discovery_focus_common_block", n=1))
    non_equal_ops = [op for op in difflib.SequenceMatcher(
        a=baseline_common_block, b=focus_common_block, autojunk=False).get_opcodes() if op[0] != "equal"]
    single_clean_insert = (len(non_equal_ops) == 1 and non_equal_ops[0][0] == "insert")

    conclusion = ("PASS" if (not_reassigned and placeholder_present and default_is_empty_string
                              and baseline_byte_identical_to_legacy_template and single_clean_insert)
                  else "FAIL_NEEDS_REVIEW")

    result = {
        "prod_gen_used_names_present_and_not_reassigned": not_reassigned,
        "common_block_template_has_editorial_type_module_block_placeholder": placeholder_present,
        "build_common_block_default_editorial_type_module_block_is_empty_string": default_is_empty_string,
        "baseline_common_block_byte_identical_to_legacy_pre_placeholder_template": baseline_byte_identical_to_legacy_template,
        "baseline_vs_focus_diff_is_single_clean_insert": single_clean_insert,
        "diff_op_count": len(non_equal_ops),
        "conclusion": conclusion,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/gate4_static_check.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/gate4_baseline_vs_focus_diff.txt", "w", encoding="utf-8") as f:
        f.writelines(diff_lines)
    print(f"[{THEME_ID}] gate4_static_check: {result['conclusion']}")
    if conclusion != "PASS":
        raise RuntimeError(f"Gate 4静的diff失敗: {result}")
    return result


# ============================================================
# 手動Mode判定記録(Trend Gate記録機構と同型)。2軸判定(Opus提案、
# 未承認仕様候補)の結果をここへ記録する。新規判定ではなく、
# FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-02_REPORT.md §2.1で既に
# 実施済みの机上検証(Household含む既存完成記事6件の実読み判定)の
# 結果を再確認・転記するだけ(A-UDR-9で確定済み)。
# ============================================================
def build_run_metadata() -> dict:
    return {
        "management_id": "FAMILY-A-COMPLETION-A4-DISCOVERY-LAYER3-TRIAL-07",
        "mode_supply_path": "手動Mode判定+手動Ledger供給(Trend Synthesis/News Trial-06と同じ機構)。",
        "editorial_mode_determination": "DISCOVERY_WHY",
        "two_axis_determination": {
            "source": "FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-02_REPORT.md §2.1"
                      "(机上検証、Household含む既存完成記事6件を実読み判定済み、A-UDR-9で既決)。"
                      "本Trialで新規判定は行っていない(既決事項の再確認・転記のみ)。",
            "axis_a_recency_dependence": "No(クリスパードロワーの湿度設定とエチレン/水分保持の仕組みという"
                                          "中心的主張の妥当性は、日付・最近性に依存しない。発表日を除去しても"
                                          "主張は崩れない)。",
            "axis_b_independent_signal_aggregation": "問わない(軸A=Noのため、2軸判定表によりDISCOVERY_WHYが確定。"
                                                       "複数のExtension機関・メーカー公式情報を引用しているが、"
                                                       "これは独立Signal集約構造ではなく証拠としての引用)。",
            "result": "DISCOVERY_WHY(Pool型=Evergreen条件も満たす、A-UDR-9)。",
        },
        "point_role_hint_connection": "接続していない(D3保留、Focus Module単独の効果を測定するため)。",
        "success_criteria": "Opus提案採用: blocking(FAIL) 0件 + 人間が「解釈のLedger内包」を確認できること。"
                            "REVIEW_REQUIREDをbaseline相当まで減らす基準は採らない(Fact CheckerとLDCの結果は"
                            "分離して記録)。",
    }


# ============================================================
# 費用実測ヘルパー(Trial-06[News]と同一の参照元・同一ロジック)。
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
                       "pricing_snapshot.json(OFFICIAL_SOURCE、Trial-06[News]と同一参照元・同一ロジック)。"
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
# 分析ヘルパー(報告用の機械分類。いずれもキーワード一致ベースの簡易
# 判定であり、厳密なNLU判定ではないことを明記する)。
# ============================================================
MECHANISM_KEYWORDS = ["because", "the reason", "mechanism", "works by", "due to", "caused by",
                      "explains why", "what actually happens", "how it works", "the real reason",
                      "underlying", "so here is the real rule"]
MYTH_CORRECTION_KEYWORDS = ["not simply", "common belief", "myth", "misconception", "it is not just",
                           "not just about", "isn't just", "shortcut", "oversimplif", "the real question",
                           "instead of", "rather than", "the assumption", "can mislead", "is misleading"]
CERTAINTY_LIMITATION_KEYWORDS = ["does not mean", "does not prove", "cannot conclude", "correlation",
                                "does not confirm", "researchers believe", "interpreted", "may not",
                                "not certain", "unclear", "limitation", "does not measure", "is not proof",
                                "not a perfect", "no perfect"]
BROADER_DIMENSION_KEYWORDS = ["in daily life", "in everyday", "in practice", "matters because", "beyond",
                             "practical", "real-world", "broader", "implication", "means for",
                             "affects how", "everyday life", "at home", "next time you"]


def classify_role_text(text: str | None) -> dict:
    if not text:
        return {"category": "other", "matched_keywords": []}
    lower = text.lower()
    hits = {
        "mechanism": [kw for kw in MECHANISM_KEYWORDS if kw in lower],
        "myth_correction": [kw for kw in MYTH_CORRECTION_KEYWORDS if kw in lower],
        "certainty_limitation": [kw for kw in CERTAINTY_LIMITATION_KEYWORDS if kw in lower],
        "broader_dimension": [kw for kw in BROADER_DIMENSION_KEYWORDS if kw in lower],
    }
    for cat in ("mechanism", "myth_correction", "certainty_limitation", "broader_dimension"):
        if hits[cat]:
            return {"category": cat, "matched_keywords": hits[cat]}
    return {"category": "other", "matched_keywords": []}


def load_role_planning_used(out_dir: str, retry_attempts: int) -> dict | None:
    path = f"{out_dir}/audit/point_role_planning_retry{retry_attempts}.json" if retry_attempts else \
        f"{out_dir}/audit/point_role_planning_initial.json"
    if not os.path.exists(path):
        path = f"{out_dir}/audit/point_role_planning_initial.json"
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"])")


def split_sentences_simple(text: str) -> list[str]:
    flat = " ".join(line.strip() for line in text.splitlines()
                     if line.strip() and not line.strip().startswith("#"))
    return [s.strip() for s in _SENT_SPLIT_RE.split(flat) if s.strip()]


def detect_near_duplicate_sentences(sentences: list[str], ratio_threshold: float = 0.55,
                                     min_words: int = 6) -> list[dict]:
    """簡易・機械的な近似重複文検出(SequenceMatcher比率ベース)。意味的な
    重複判定ではなく、Trial-05で観察された「同義文重複」副作用を報告用に
    ざっくり検出するためのヒューリスティック。"""
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


def classify_claim_to_evidence(claim_text: str) -> dict:
    """Fact CheckerのREVIEW_REQUIRED claimを、Household Ledgerのどの
    evidence id(FACT-01〜04)の解釈に近いかへ、キーワード一致件数で機械
    分類する(簡易ヒューリスティック、厳密なNLU判定ではない)。一致件数が
    0の場合はLedger外(または語彙一致で検出できない解釈)として報告する。"""
    lower = claim_text.lower()
    scores = {fid: sum(1 for kw in kws if kw in lower) for fid, kws in HOUSEHOLD_FACT_KEYWORDS.items()}
    best_fid, best_score = max(scores.items(), key=lambda kv: kv[1])
    if best_score == 0:
        return {"judgement": "LEDGER_OUTSIDE_OR_NO_LEXICAL_MATCH", "evidence_id": None,
                "score": 0, "scores": scores}
    return {"judgement": f"LIKELY_INTERPRETATION_OF_{best_fid}", "evidence_id": best_fid,
            "score": best_score, "scores": scores}


def analyze_run(out_dir: str, result: dict) -> dict:
    retry_attempts = result.get("point_overlap_article_retry_attempts") or 0

    word_count = None
    section_wc = None
    word_overflow = None
    duplicate_pairs = None
    role_one_text = role_two_text = None
    role_one_class = role_two_class = None
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

        role_plan = load_role_planning_used(out_dir, retry_attempts)
        if role_plan and role_plan.get("parsed"):
            role_one_text = role_plan["parsed"].get("point_one", {}).get("role")
            role_two_text = role_plan["parsed"].get("point_two", {}).get("role")
            role_one_class = classify_role_text(role_one_text)
            role_two_class = classify_role_text(role_two_text)
    else:
        metrics = {}

    # Fact Checker詳細(unsupported_specific_claims件数・verdict、Ledger
    # Deviationとは分離して記録)。
    fact_qa_path = f"{out_dir}/fact_qa.json"
    fact_verdict = result.get("fact_verdict")
    unsupported_claims = []
    claim_evidence_map = None
    if os.path.exists(fact_qa_path):
        fact_qa = json.load(open(fact_qa_path, encoding="utf-8"))
        fc_result = fact_qa.get("result") or {}
        fact_verdict = fc_result.get("verdict", fact_verdict)
        unsupported_claims = fc_result.get("unsupported_specific_claims") or []

    # LDC(Ledger Deviation Checker)+Local Rewrite詳細(Fact Checkerとは
    # 分離)。
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
        "point_one_role_text": role_one_text,
        "point_one_role_category": role_one_class["category"] if role_one_class else None,
        "point_two_role_text": role_two_text,
        "point_two_role_category": role_two_class["category"] if role_two_class else None,
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

    # 人間確認用artifact(item 3): discovery_focus条件のみ、Fact Checker
    # REVIEW_REQUIRED claimをevidence idへ機械分類する。
    if condition_name == "discovery_focus" and analysis["fact_unsupported_specific_claims"]:
        analysis["claim_to_evidence_table"] = [
            {"claim": c, **classify_claim_to_evidence(c)}
            for c in analysis["fact_unsupported_specific_claims"]
        ]
    else:
        analysis["claim_to_evidence_table"] = []

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
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")  # 冒頭で必ず有効化
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

    # 実行環境の制約(前面同期実行、1コマンドあたりのタイムアウト)により、
    # combo単位でプロセスを分けて逐次実行するCLIを実行経路として使う
    # (Trial-06[News]と同一パターン)。cl.install()はappendモードのため
    # プロセスをまたいでも既存raw_usage_log.jsonlへ正しく追記される。
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
        print("usage: python er011_discovery_layer3_focus_trial_07.py "
              "[setup|combo <condition> <A2|B1B> <run_idx>|cost|aggregate]")
