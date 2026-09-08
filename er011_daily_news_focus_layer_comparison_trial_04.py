# ============================================================
# er011_daily_news_focus_layer_comparison_trial_04.py
# FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04 (Lane A)
# ============================================================
# 目的(ユーザー決定 A-UDR-12): FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-
# CONNECTION-TRIAL-03_REPORT.md(VALIDATED)で検証した接続案(b)(Point Role
# Planningへのmode別Point Role候補hint)を用いて、Hanshin Ledger固定で
# baseline(hint=""・Focus Moduleなし、Production既定と同一)と focus
# (Trial-02のMajor/Daily Focus Module + 案(b)のPoint Role hint)を、
# A2/B1B x N=3で再比較する。1回の成功例だけで結論を出さない。
# **Trial(Production実装ではない)**。Production/Prompt/SSOT編集・Git操作は
# 一切行わない。monkeypatch・グローバル書き換えなし。TTSは実行しない
# (text-onlyまで)。
#
# 再利用(import・無変更、コピー改変はしない):
#   - er011_point_role_planning_focus_connection_trial_03(既存VALIDATED
#     Trial、Lane A、Fable受入済み): run_one_pattern_connected /
#     run_point_role_planning_connected / MAJOR_DAILY_NEWS_POINT_ROLE_
#     HINT_BLOCK / MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK / load_text /
#     HANSHIN_LEDGER_PATH / HANSHIN_TOPIC_JA をそのままimportする
#     (このTrialでの再改変・再コピーは行わない)。
#   - er003_v1_n3_01_articles_generate(prod_gen): build_common_block /
#     build_prompt / A2_KAI1_INSTRUCTION / B1_B_DIRECT_INSTRUCTION /
#     compute_metrics / split_common_sections_for_point_qa。無変更。
#   - er003_v1_en_direct_vfl_01_generate(vfl01): get_client。
#   - er003_v1_en_direct_ab_01_generate(ab01): load_master_full_text。
#   - er003_v1_spoken_first_01_r1_generate(sf1r1): section_word_counts。
#   - er005_cost_logger(cl): install / logging_context(既存の全費用計測
#     機構、無変更)。
#
# Gate 4根拠: 本ファイルは新規コード追加のみで、上記いずれのモジュール・
# 関数も編集していない(grep差分なし、import only)。Trial-03のコピー済み
# 関数(run_one_pattern_connected等)を「再度コピー」することはせず、
# Trial-03モジュールをimportして直接呼ぶ(二重コピーを避ける)。
# ============================================================
from __future__ import annotations

import json
import os
import re
import time

import er003_v1_n3_01_articles_generate as prod_gen
import er003_v1_spoken_first_01_r1_generate as sf1r1
import er005_cost_logger as cl
import er011_point_role_planning_focus_connection_trial_03 as t3

THEME_ID = "daily_news_focus_layer_comparison_trial_04"
OUT_DIR = f"er011_output/{THEME_ID}"

N_RUNS = 3  # A-UDR-12指定。費用超過見込みの場合はmain()内でN=2へ縮退する。

CONDITIONS = {
    "baseline": {
        "editorial_type_module_block": "",  # Production既定(Focus Moduleなし)
        "point_role_hint_block": "",  # Production既定(hintなし)
    },
    "focus": {
        "editorial_type_module_block": t3.MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK,
        "point_role_hint_block": t3.MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK,
    },
}

LEVELS = [
    ("B1B", prod_gen.B1_B_DIRECT_INSTRUCTION, "b1b", "writer_b1"),
    ("A2", prod_gen.A2_KAI1_INSTRUCTION, "a2", "writer_a2"),
]

# ============================================================
# 役割分類ヒューリスティック(機械判定、簡易・主観混在は明記)。
# Trial-02のFocus Module文言が言及する3カテゴリ(mechanism /
# beyond-the-headline factor / limitation)へ、Point Role Planning出力の
# role文言・Point本文をキーワード一致で粗く分類する。厳密なNLU判定では
# なく、報告用の簡易・機械的な仕分けであることを明記する。
# ============================================================
MECHANISM_KEYWORDS = [
    "mechanism", "decided the outcome", "what decided", "how the", "caused",
    "led to", "brought about", "the reason", "sequence that", "process that",
    "what made the difference", "what turned",
]
BEYOND_HEADLINE_KEYWORDS = [
    "beyond the headline", "additional", "contributing factor", "another factor",
    "also played", "besides", "in addition to", "wider context", "broader context",
    "another angle", "more than", "not just",
]
LIMITATION_KEYWORDS = [
    "limitation", "unconfirmed", "does not establish", "does not confirm",
    "cannot confirm", "not clear", "uncertain", "caveat", "what remains",
    "cannot be certain", "no clear evidence", "does not prove", "does not show",
    "not yet clear", "cannot say", "not settled", "stopping short of",
]


def classify_role_text(text: str) -> dict:
    """role文言(Point Role Planning出力)を3カテゴリ+otherへ機械分類する。
    キーワード一致ベースの簡易判定(厳密なNLU判定ではない)。"""
    if not text:
        return {"category": "other", "matched_keywords": []}
    lower = text.lower()
    hits = {
        "mechanism": [kw for kw in MECHANISM_KEYWORDS if kw in lower],
        "beyond_the_headline": [kw for kw in BEYOND_HEADLINE_KEYWORDS if kw in lower],
        "limitation": [kw for kw in LIMITATION_KEYWORDS if kw in lower],
    }
    for cat in ("mechanism", "beyond_the_headline", "limitation"):
        if hits[cat]:
            return {"category": cat, "matched_keywords": hits[cat]}
    return {"category": "other", "matched_keywords": []}


def body_embodies_role(body_text: str, category: str) -> dict:
    """Point本文(実際の英語本文)が、計画されたroleカテゴリを体現している
    ように読めるか、同じキーワード群での粗い一致判定+根拠を返す
    (機械判定+短い根拠、厳密な意味理解ではない簡易チェック)。"""
    if not body_text or category == "other":
        return {"match": None, "matched_keywords": [], "note": "role=otherのため判定対象外"}
    keyword_map = {
        "mechanism": MECHANISM_KEYWORDS,
        "beyond_the_headline": BEYOND_HEADLINE_KEYWORDS,
        "limitation": LIMITATION_KEYWORDS,
    }
    lower = body_text.lower()
    hits = [kw for kw in keyword_map[category] if kw in lower]
    return {
        "match": bool(hits),
        "matched_keywords": hits,
        "note": f"本文キーワード一致{len(hits)}件" if hits else "本文中に対応キーワードなし(意味的には体現している可能性はあるが機械判定では検出不可)",
    }


def load_role_planning_used(out_dir: str, retry_attempts: int) -> dict | None:
    """最終記事生成に実際に使われたPoint Role Planning出力(retryがあれば
    最後のretry版、なければinitial版)を読む。"""
    path = f"{out_dir}/audit/point_role_planning_retry{retry_attempts}.json" if retry_attempts else \
        f"{out_dir}/audit/point_role_planning_initial.json"
    if not os.path.exists(path):
        path = f"{out_dir}/audit/point_role_planning_initial.json"
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def analyze_run(out_dir: str, result: dict) -> dict:
    """生成済みrunの成果物を読み、集計用の指標(overlap ratio、role分類、
    body一致、語数等)を機械的に抽出する。"""
    retry_attempts = result.get("point_overlap_article_retry_attempts") or 0
    overlap_log_path = f"{out_dir}/point_overlap_article_retry_log.json"
    final_overlap_report = None
    if os.path.exists(overlap_log_path):
        with open(overlap_log_path, encoding="utf-8") as f:
            overlap_log = json.load(f)
        if overlap_log:
            final_overlap_report = overlap_log[-1].get("report")
    point_one_overlap = point_two_overlap = None
    point_one_flagged = point_two_flagged = None
    if final_overlap_report:
        po = final_overlap_report.get("point_one", {}).get("before_overlap", {})
        pt = final_overlap_report.get("point_two", {}).get("before_overlap", {})
        point_one_overlap, point_one_flagged = po.get("overlap_ratio"), po.get("flagged")
        point_two_overlap, point_two_flagged = pt.get("overlap_ratio"), pt.get("flagged")

    article_path = f"{out_dir}/article.md"
    word_count = None
    section_wc = None
    role_one_text = role_two_text = None
    role_one_class = role_two_class = None
    body_one_match = body_two_match = None
    if os.path.exists(article_path):
        with open(article_path, encoding="utf-8") as f:
            article_text = f.read()
        metrics = prod_gen.compute_metrics(article_text)
        word_count = metrics["word_count"]
        section_wc = sf1r1.section_word_counts(article_text)
        sections = prod_gen.split_common_sections_for_point_qa(article_text)
        role_plan = load_role_planning_used(out_dir, retry_attempts)
        if role_plan and role_plan.get("parsed"):
            role_one_text = role_plan["parsed"].get("point_one", {}).get("role")
            role_two_text = role_plan["parsed"].get("point_two", {}).get("role")
            role_one_class = classify_role_text(role_one_text)
            role_two_class = classify_role_text(role_two_text)
            if sections is not None:
                body_one_match = body_embodies_role(sections["point_one_body"], role_one_class["category"])
                body_two_match = body_embodies_role(sections["point_two_body"], role_two_class["category"])

    return {
        "status": result.get("status"),
        "retry_attempts": retry_attempts,
        "fact_verdict": result.get("fact_verdict"),
        "ledger_status": result.get("ledger_status"),
        "ledger_deviation_count": result.get("ledger_deviation_count"),
        "directional_fact_precheck_status": result.get("directional_fact_precheck_status"),
        "word_count": word_count,
        "section_word_counts": section_wc,
        "point_one_overlap_ratio": point_one_overlap,
        "point_one_overlap_flagged": point_one_flagged,
        "point_two_overlap_ratio": point_two_overlap,
        "point_two_overlap_flagged": point_two_flagged,
        "point_one_role_text": role_one_text,
        "point_one_role_category": role_one_class["category"] if role_one_class else None,
        "point_one_role_matched_keywords": role_one_class["matched_keywords"] if role_one_class else None,
        "point_one_body_embodies_role": body_one_match,
        "point_two_role_text": role_two_text,
        "point_two_role_category": role_two_class["category"] if role_two_class else None,
        "point_two_role_matched_keywords": role_two_class["matched_keywords"] if role_two_class else None,
        "point_two_body_embodies_role": body_two_match,
    }


def run_one_combo(client, master_full_text: str, verified_ledger_text: str,
                   condition_name: str, run_idx: int, label: str, instruction: str,
                   level_dir: str, stage_tag: str) -> dict:
    cond = CONDITIONS[condition_name]
    out_dir = f"{OUT_DIR}/{level_dir}/{condition_name}/run{run_idx}"
    common_block = prod_gen.build_common_block(
        master_full_text, t3.HANSHIN_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=cond["editorial_type_module_block"])
    prompt = prod_gen.build_prompt(common_block, instruction)
    theme_tag = f"{THEME_ID}_{condition_name}_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, stage_tag):
        result = t3.run_one_pattern_connected(
            client, theme_tag, label, prompt, verified_ledger_text, t3.HANSHIN_TOPIC_JA, out_dir,
            point_role_hint_block=cond["point_role_hint_block"])
    elapsed = round(time.time() - t0, 2)
    analysis = analyze_run(out_dir, result)
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


def run_batch(run_idx: int, client, master_full_text: str, verified_ledger_text: str) -> list:
    batch_results = []
    for condition_name in ("baseline", "focus"):
        for label, instruction, level_dir, stage_tag in LEVELS:
            analysis = run_one_combo(
                client, master_full_text, verified_ledger_text, condition_name, run_idx,
                label, instruction, level_dir, stage_tag)
            batch_results.append(analysis)
    return batch_results


if __name__ == "__main__":
    import sys

    n_runs_arg = int(sys.argv[1]) if len(sys.argv) > 1 else N_RUNS
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

    client = t3.vfl01.get_client()
    master_full_text = t3.ab01.load_master_full_text()
    verified_ledger_text = t3.load_text(t3.HANSHIN_LEDGER_PATH)

    all_results = []
    for run_idx in range(1, n_runs_arg + 1):
        batch = run_batch(run_idx, client, master_full_text, verified_ledger_text)
        all_results.extend(batch)
        with open(f"{OUT_DIR}/all_results_so_far.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}] === run{run_idx} 完了({len(batch)}本) ===")
