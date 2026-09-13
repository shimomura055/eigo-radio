# ============================================================
# er011_open141_target_sentence_diff_qa_integration_trial_b_01.py
# OPEN-141-TARGET-SENTENCE-MATCHING-AND-DIFF-QA-COMMON-BASE-TRIAL-01
# Phase B(B2: 差分QA案I実装、B5/B6: A-Family既存Ledger再現+1記事統合Trial)
# ============================================================
# 位置づけ: Trial専用スクリプト。Production自動実行経路
# (er003_v1_n3_01_articles_generate.py::run_one_pattern、
# er012_b_family_voices_writer_generic_01.py)には一切配線しない
# (無断混入禁止、APPROVED_FOR_PRODUCTIONはユーザーのみが判断できる)。
# 既存Production関数(vfl01.run_deviation_check/r3.build_fact_check_prompt/
# r3.run_fact_checker_with_gates/er010_ledger_local_rewrite_09の
# classify_deviation_role・evaluate_target_sentence_status・
# split_sentences、er003_v1_n3_01_articles_generate.split_common_sections_
# for_point_qa、er008_point_overlap_qa_18.flag_possible_paraphrase)を
# そのまま呼び出すのみで、新しいLLM判定基準・promptは一切作らない。
#
# 対象記事(Fable判断2026-09-13、案(b)採用): A-Family News、
# `er011_output/daily_news_focus_layer_comparison_trial_04/b1b/focus/run2`
# (保存済みVerified Fact Ledger[`er003_output/n3_01/hanshin/research/
# verified_fact_ledger.txt`]+保存済みclaim_in_article・article.mdを使用、
# 新規記事生成なし)。この記事の局所Rewrite実データには、B3で修正した
# split_sentences()の見出し混入バグの実例(cycle 1 item 2)が含まれており、
# その結果apply_rewrites()の文字列置換がサイレントに失敗し、
# 「resolved=True」と記録されたにもかかわらず出荷記事本文はMAJOR判定
# された元の文のまま変わっていなかったことを確認済み(OPEN-141 Phase B
# REPORT参照)。本Trialはこの対象文を使い、B3修正後の正しい文単位・
# B1のtarget-sentence-matching・B2の差分QA(案I)を実LLM呼び出しで検証する。

from __future__ import annotations

import json
import os

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er008_point_overlap_qa_18 as overlap_qa
import er010_ledger_local_rewrite_09 as local_rewrite

LEDGER_PATH = "er003_output/n3_01/hanshin/research/verified_fact_ledger.txt"
ARTICLE_PATH = "er011_output/daily_news_focus_layer_comparison_trial_04/b1b/focus/run2/article.md"
TOPIC_JA = (
    "2026年8月16日、マツダスタジアムで行われた広島東洋カープ対阪神タイガース戦。"
    "阪神は初回の佐藤輝明の2ランホームランで先制し、先発伊原陵人が5回2安打1失点と"
    "試合を作り、7回・8回にも加点して8-1で完勝した。広島の得点は5回のモンテロの"
    "ソロホームラン1点のみだった。"
)
OUT_DIR = "er011_output/open141_target_sentence_diff_qa_integration_trial_b_01"

# 実データから再構成した対象文(B3修正後の正しい単文境界、article.mdに
# 現在も未変更のまま残っている、cycle 1 item 2の対象、location_method=
# sentence_fallback(overlap=0.43)だった旧不具合ケース)。
TARGET_SENTENCE = ("The early lead faced one clear challenge, not repeated waves of pressure.")
BEFORE_CTX = ("Its only run came on Montero’s solo shot, while Ihara allowed just two hits "
              "and one run over five innings.")
AFTER_CTX = "Late in the game, more than one hitter supplied the scoring."
ORIGINAL_DEVIATION_ISSUE = (
    "Ledgerは広島の得点がモンテロのソロ"
    "ホームランによる1点のみだったこ"
    "とは保証するが、試合中に長い攻撃"
    "の連続や複数のプレッシャーがなか"
    "ったことまでは保証していない。"
)


# ============================================================
# B2: 差分QA(案I)。既存関数のみ呼び出す薄いラッパー。
# ============================================================
# 既存MAX_REWRITE_CYCLES(記事全体cycle上限、=3)・MAX_REWRITE_ATTEMPTS
# (文単位rewrite試行上限、=3)とは全く別軸の「差分QA呼び出し回数」カウンタ。
# 上限混同を避けるため、独立した定数名で明示する(このTrialでは対象文1件
# につきFact Checker A' 1回+Ledger Deviation Checker 1回のみ、上限運用は
# 別途Production採用時にFable/ユーザー判断)。
DIFF_QA_CALLS_PER_ITEM = 1


def run_diff_qa_for_target_sentence(client, topic_ja: str, target_sentence: str, before_ctx: str,
                                     after_ctx: str, verified_ledger_text: str, ledger_model: str,
                                     fact_checker_model: str, fact_checker_reasoning_effort: str) -> dict:
    """Local Rewrite確定後、対象文(+前後1文)をFact Checker A'(既存関数、
    web_search込み)とLedger Deviation Checker(既存関数、Hook-aware)へ
    再投入する(OPEN-141 Phase B、案I)。既存のPoint Overlap/Value QAは
    ここでは呼ばない(B2の別関数recompute_point_overlap_if_in_point_
    sectionが担当、rule-basedのみでLLM再呼び出しなし)。"""
    window_text = f"{before_ctx} {target_sentence} {after_ctx}".strip()

    fc_prompt = r3.build_fact_check_prompt(topic_ja, window_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt, client=client, model=fact_checker_model,
                                        reasoning_effort=fact_checker_reasoning_effort)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn)
    fc_verdict = fc_result.get("verdict") if fc_result else None

    ledger_result = vfl01.run_deviation_check(client, verified_ledger_text, window_text,
                                               model=ledger_model, hook_aware=True)
    ledger_eval = local_rewrite.evaluate_target_sentence_status(
        ledger_result["parsed"], target_sentence, before_ctx, after_ctx)

    return {
        "diff_qa_calls": DIFF_QA_CALLS_PER_ITEM,
        "window_text": window_text,
        "fact_check_status": fc_status,
        "fact_check_verdict": fc_verdict,
        "fact_check_result": fc_result,
        "fact_check_model": fc_model,
        "fact_check_response_id": fc_response_id,
        "fact_check_search_usage": fc_search_usage,
        "ledger_check_full": ledger_result["parsed"],
        "ledger_check_target_eval": ledger_eval,
        "requires_escalation": (fc_verdict == "FAIL") or (ledger_eval["overall_status"] == "LEDGER_DEVIATION"),
    }


def recompute_point_overlap_if_in_point_section(article_text: str, target_sentence: str) -> dict:
    """対象文がPoint One/Twoのいずれかのsection内にある場合のみ、既存の
    rule-based Point Overlap(er008_point_overlap_qa_18.flag_possible_
    paraphrase、¥0・LLM再呼び出しなし)をそのsectionについて再計算する
    (Fable判断2026-09-13: Point Overlap/ValueはLLM再呼び出しなしの
    section単位rule-based再計算のみをスコープに含める。Point Value QA
    [LLMベース]自体は対象外)。"""
    sections = prod_gen.split_common_sections_for_point_qa(article_text)
    if sections is None:
        return {"applicable": False, "reason": "想定構造(###見出々2つ)が見つからない"}
    if target_sentence in sections["point_one_body"]:
        key, other_key = "point_one", "point_two_body"
    elif target_sentence in sections["point_two_body"]:
        key, other_key = "point_two", "point_one_body"
    else:
        return {"applicable": False, "reason": "対象文はPoint One/Twoのいずれにも属さない"}
    body = sections[f"{key}_body"]
    overlap_vs_story = overlap_qa.flag_possible_paraphrase(body, sections["full_story"])
    overlap_vs_other = overlap_qa.flag_possible_paraphrase(body, sections[other_key])
    return {
        "applicable": True, "point": key,
        "overlap_vs_full_story": overlap_vs_story,
        "overlap_vs_other_point": overlap_vs_other,
        "flagged": overlap_vs_story["flagged"] or overlap_vs_other["flagged"],
    }


# ============================================================
# B5/B6: 1記事統合Trial実行
# ============================================================
def run_trial() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    client = vfl01.get_client()
    ledger_model = vfl01.MODEL
    verified_ledger_text = open(LEDGER_PATH, encoding="utf-8").read()
    article_text = open(ARTICLE_PATH, encoding="utf-8").read()

    # --- (1) B3確認: 見出し除外後の文分割で対象文が正しく単文として得られる ---
    sentences = local_rewrite.split_sentences(article_text)
    assert TARGET_SENTENCE in sentences, "target sentence not found after split_sentences fix"
    idx = sentences.index(TARGET_SENTENCE)
    reconstructed_before = sentences[idx - 1] if idx > 0 else ""
    reconstructed_after = sentences[idx + 1] if idx + 1 < len(sentences) else ""
    b3_check = {
        "target_found_as_single_sentence": True,
        "reconstructed_before_ctx": reconstructed_before,
        "reconstructed_after_ctx": reconstructed_after,
        "matches_manual_before_ctx": reconstructed_before == BEFORE_CTX,
        "matches_manual_after_ctx": reconstructed_after == AFTER_CTX,
    }

    # --- (2) Before(現行window方式): window全体をLedger Deviation Checker
    #     (Hook-aware、Production同一関数)へ再投入し、window全体の
    #     overall_statusのみで受理判定した場合の結果(実LLM呼び出し) ---
    window_text = f"{BEFORE_CTX} {TARGET_SENTENCE} {AFTER_CTX}".strip()
    window_check = vfl01.run_deviation_check(client, verified_ledger_text, window_text,
                                              model=ledger_model, hook_aware=True)
    before_method_status = window_check["parsed"]["overall_status"]

    # --- (3) After(B1 target-sentence-matching、同一window_checkの
    #     deviations配列を対象文へ対応付けて再計算、追加API呼び出し0件) ---
    target_eval = local_rewrite.evaluate_target_sentence_status(
        window_check["parsed"], TARGET_SENTENCE, BEFORE_CTX, AFTER_CTX)
    after_method_status = target_eval["overall_status"]

    # --- (4) B2差分QA(案I): 対象文+前後1文をFact Checker A'
    #     (web_search込み)+Ledger Deviation Checkerへ再投入(実LLM呼び出し) ---
    diff_qa = run_diff_qa_for_target_sentence(
        client, TOPIC_JA, TARGET_SENTENCE, BEFORE_CTX, AFTER_CTX, verified_ledger_text,
        ledger_model, r3.FACT_CHECKER_MODEL, r3.FACT_CHECKER_REASONING_EFFORT)

    # --- (5) Point Overlap rule-based再計算(¥0、対象文がPoint section内か) ---
    point_overlap = recompute_point_overlap_if_in_point_section(article_text, TARGET_SENTENCE)

    result = {
        "article_path": ARTICLE_PATH,
        "ledger_path": LEDGER_PATH,
        "target_sentence": TARGET_SENTENCE,
        "before_ctx": BEFORE_CTX,
        "after_ctx": AFTER_CTX,
        "b3_heading_exclusion_check": b3_check,
        "before_method_window_overall_status": before_method_status,
        "before_method_full_check_result": window_check["parsed"],
        "after_method_target_sentence_eval": target_eval,
        "diff_qa_result": diff_qa,
        "point_overlap_recompute": point_overlap,
        "verdict_changed_by_target_sentence_matching": before_method_status != after_method_status,
    }
    with open(f"{OUT_DIR}/trial_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    return result


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    r = run_trial()
    print("before_method_window_overall_status:", r["before_method_window_overall_status"])
    print("after_method_target_sentence_status:", r["after_method_target_sentence_eval"]["overall_status"])
    print("diff_qa fact_check_verdict:", r["diff_qa_result"]["fact_check_verdict"])
    print("diff_qa ledger_check_target_eval overall_status:",
          r["diff_qa_result"]["ledger_check_target_eval"]["overall_status"])
    print("point_overlap_recompute:", r["point_overlap_recompute"])
    print(f"saved to {OUT_DIR}/trial_result.json")
