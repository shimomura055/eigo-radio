# ============================================================
# er011_daily_news_focus_layer_comparison_trial_02.py
# FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-02 (Lane A-1)
# ============================================================
# 目的: FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01_REPORT.md (A-UDR-8
# でユーザー承認、Status=VALIDATED、Production採用は未承認)が設計した
# Major/Daily News Focus Module(Layer3、未実装ドラフト文言)を、承認済みの
# 同一Hanshin Ledger(er003_output/n3_01/hanshin/research/verified_fact_
# ledger.txt)に対して (a) Focus Moduleなし(既定) と (b) Focus Moduleあり
# の2条件でA2/B1各1本ずつ(計4本、text-onlyでTTSは行わない)生成し、News
# 固有編集層の効果を比較する。
#
# Production Writer正式path(er006_pool_pilot_01_writer.run_writer_for_
# theme -> er003_v1_n3_01_articles_generate.build_common_block/build_
# prompt/run_one_pattern)を変更せず利用する。ただし run_writer_for_theme
# は (1) editorial_mode文字列 -> 登録済みEDITORIAL_TYPE_MODULE_BLOCKS辞書
# のみを受け付け、生のblock文字列を直接は受け付けない(本Major/Daily
# variantは未登録、resolve_editorial_type_module_block()はfail-closedで
# ValueErrorを送出する設計、意図的な安全装置であり回避しない)、(2)
# 出力先を常に f"{out_dir}/b1b" / f"{out_dir}/a2" に固定しており、本Trialが
# 要求する {a2,b1b}/{baseline,focus} のネスト構造を作れない、という2点で
# 本Trialの要件に合わない。そのため、run_writer_for_theme内部が呼んでいる
# のと全く同じ下位の公開関数(gen.build_common_block / gen.build_prompt /
# gen.run_one_pattern、いずれもmonkeypatchなし・テンプレート文字列置換なし)
# を、本Trialスクリプトから直接同じ順序で呼び出す。baseline条件は
# editorial_type_module_block=""(既定値と同一、run_writer_for_theme に
# editorial_mode=None を渡した場合とバイト単位で同一のprompt)、focus条件は
# editorial_type_module_block=MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK(下記、
# DESIGN-TRIAL-01 §1.3ドラフトを無改変で使用)を渡す。
#
# 既存Editor(Evidence Compression/Numeric Precision、apply_evidence_
# compression_editor既定True)・Fact Checker・Ledger Deviation Checker・
# Point Overlap QA・Diagnostic Full Retryはいずれも run_one_pattern() の
# 既定引数のまま(変更しない)。TTSは行わない(text-onlyのarticle.md/QA
# jsonまでで完了)。
#
# 費用上限: 本タスクの上限\80(超過見込みならSTOP)。参考: OPEN-112-TREND-
# SYNTHESIS-MODE-PRODUCTION-WIRING-01実績(Theme2、A2+B1 text-onlyで
# Diagnostic Full Retry込み約\37.11)。Hanshinは単一起点Ledgerで
# Trend Synthesisより短いため、baseline実行後に実測costをcost_compute
# スクリプトで確認し、focus条件へ進む前に予算内かを判定する。
from __future__ import annotations

import os

HANSHIN_LEDGER_PATH = "er003_output/n3_01/hanshin/research/verified_fact_ledger.txt"

# er003_v1_n3_01_articles_generate.py THEMES[0]["topic"] (Hanshin) と
# 完全同一の文面(Lane A-1 SSOT編集タスクの成果物は参照せず、本ファイルを
# 直接読んで転記した)。
HANSHIN_TOPIC_JA = (
    "2026年8月16日、マツダスタジアムで行われた広島東洋カープ対阪神タイガース戦。"
    "阪神は初回の佐藤輝明の2ランホームランで先制し、先発伊原陵人が5回2安打1失点と"
    "試合を作り、7回・8回にも加点して8-1で完勝した。広島の得点は5回のモンテロの"
    "ソロホームラン1点のみだった。"
)

THEME_ID = "daily_news_focus_layer_comparison_trial_02"
OUT_DIR = f"er011_output/{THEME_ID}"

# ------------------------------------------------------------
# Major/Daily Gate 6項目(FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01
# §2.1が新規提案・§2.2でHanshin実記事に当てはめ済み)の再確認。本Trialでは
# 記事生成前に、実施者(本タスク)が同じ6項目をHanshin Ledgerへ再度手動で
# 当てはめた記録。自動判定ロジックは実装しない(Trend Gate 6条件の既存
# 手動記録パターンと同型)。
MAJOR_DAILY_GATE_CHECKLIST = {
    "note": "DESIGN-TRIAL-01 §2.1の6項目を、本タスク実施者がverified_fact_ledger.txt"
            "(Hanshin)を読んで再度手動で当てはめた(自動判定ロジックではない、"
            "DESIGN-TRIAL-01 §2.2の既存判定の再確認)。",
    "evaluated_at": "2026-09-08",
    "criteria": {
        "1_single_origin_confirmed": {
            "result": "PASS",
            "evidence": "Main Storyは『2026年8月16日、広島対阪神戦で阪神が8-1で勝利した』"
                        "の1文で要点を保てる、単一試合・単一日付の単一起点イベント。",
        },
        "2_importance_independent": {
            "result": "PASS(該当なし)",
            "evidence": "重要度の高低(プロ野球の1試合)自体はMAJOR_DAILY判定に影響しない"
                        "(DESIGN-08の一般原則をそのまま適用)。",
        },
        "3_ledger_sufficiency": {
            "result": "PASS",
            "evidence": "単一のverified_fact_ledger.txtだけで、Main Story + Point One"
                        "(初回の佐藤輝明2ランが試合の形を決めたmechanism)+ Point Two"
                        "(7-8回の追加点という見出し以外の貢献の広がり)という異なる"
                        "2つの意味づけを支える確認済み情報がある。",
        },
        "4_uncertainty_explicit": {
            "result": "PASS(該当事項なし)",
            "evidence": "試合結果は既に確定した事実であり、投影的・未確定要素を含まない"
                        "(Health記事のような単一研究発表とは異なりこの項目は実質NA)。",
        },
        "5_no_recent_duplicate": {
            "result": "PASS",
            "evidence": "同一起点イベント(2026-08-16の広島対阪神戦)についての別記事は"
                        "本Trial実施時点で存在しない。",
        },
        "6_not_disguised_trend": {
            "result": "PASS",
            "evidence": "記事化にあたり複数の独立した時点・出来事を横断的に参照する必要は"
                        "なく、単一試合の内部推移(1試合の中の複数イニング)のみで完結する。",
        },
    },
    "verdict": "MAJOR_DAILY(本タスク実施者による手動再確認、DESIGN-TRIAL-01 §2.2の判定と一致)",
}

# ------------------------------------------------------------
# Major/Daily News Focus Module本文。FAMILY-A-DAILY-NEWS-FOCUS-LAYER-
# DESIGN-TRIAL-01_REPORT.md §1.3のドラフト文言を無改変で使用する(本
# Trial自身が新規創作しない)。Production未採用・未実装(Trialスクリプト
# 内でのみ editorial_type_module_block 引数へ直接渡す。er003_v1_n3_01_
# articles_generate.py の EDITORIAL_TYPE_MODULE_BLOCKS 辞書へは登録しない
# =Productionコードは無変更)。
MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK = """【Major/Daily News Focus(記事タイプ固有の焦点。FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01 \
§1.3で設計ドラフト化、FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-02が比較検証のため本Trialスクリプト内で \
そのまま使用。Production未採用・未実装、本文言はProductionコードへは一切登録していない)】

This article covers a single, dateable news event or announcement — not an aggregated trend across
independent occurrences. Do not present this story as if it were a pattern seen across multiple
separate events over time.

Point One and Point Two must each add a distinct layer of meaning to what Main Story already
established (for example: the mechanism that decided the outcome, why this matters, who is affected,
an additional contributing factor beyond the headline fact, or what remains unconfirmed). Do not let
either Point simply restate a fact already given in Main Story, and do not force a role the Ledger
does not actually support — choose the role Point Role Planning is designed to choose.

If any part of this event is a projection, an ongoing situation, a single study's finding, or
otherwise not yet fully settled, state plainly what is confirmed and what is not — do not smooth an
unconfirmed detail into settled fact."""


def run_one_condition(client, master_full_text, gen, condition_label: str, editorial_type_module_block: str):
    """run_writer_for_theme() の内部ループ(er006_pool_pilot_01_writer.py 28-89行)と
    全く同じ呼び出し順序(build_common_block -> build_prompt -> run_one_pattern)を、
    出力先ディレクトリ構造のみ本Trial向け({level}/{condition})に変えて再現する。
    prompt/instruction/Fact Checker/Ledger Deviation/Point Overlap QA/Diagnostic Full
    Retry/Evidence Compression Editorはいずれも無変更(gen側の既定引数のまま)。"""
    import time

    import er005_cost_logger as cl

    verified_ledger_text = gen.load_text(HANSHIN_LEDGER_PATH)
    results = {}
    timing = {}
    for label, instruction, level_dir, stage_tag in [
        ("B1B", gen.B1_B_DIRECT_INSTRUCTION, "b1b", "writer_b1"),
        ("A2", gen.A2_KAI1_INSTRUCTION, "a2", "writer_a2"),
    ]:
        level_out_dir = f"{OUT_DIR}/{level_dir}/{condition_label}"
        common_block = gen.build_common_block(
            master_full_text, HANSHIN_TOPIC_JA, verified_ledger_text,
            editorial_type_module_block=editorial_type_module_block)
        prompt = gen.build_prompt(common_block, instruction)
        theme_tag = f"{THEME_ID}_{condition_label}"
        t0 = time.time()
        with cl.logging_context(theme_tag, stage_tag):
            result = gen.run_one_pattern(client, theme_tag, label, prompt, verified_ledger_text,
                                          HANSHIN_TOPIC_JA, level_out_dir)
        timing[stage_tag] = round(time.time() - t0, 2)
        results[label] = result
        print(f"[{THEME_ID}][{condition_label}] {label}: status={result.get('status')} "
              f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')} "
              f"point_overlap_article_retry_attempts={result.get('point_overlap_article_retry_attempts')}")

    import json
    os.makedirs(f"{OUT_DIR}/{condition_label}", exist_ok=True)
    with open(f"{OUT_DIR}/{condition_label}/articles_run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "article_text"} for k, v in results.items()},
                   f, ensure_ascii=False, indent=2, default=str)
    with open(f"{OUT_DIR}/{condition_label}/writer_timing.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    if condition_label == "focus":
        with open(f"{OUT_DIR}/{condition_label}/major_daily_gate_checklist.json", "w", encoding="utf-8") as f:
            json.dump(MAJOR_DAILY_GATE_CHECKLIST, f, ensure_ascii=False, indent=2)
        with open(f"{OUT_DIR}/{condition_label}/major_daily_news_focus_module_block.txt", "w",
                  encoding="utf-8") as f:
            f.write(MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK)
    return results


def run_baseline():
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er003_v1_n3_01_articles_generate as gen

    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    return run_one_condition(client, master_full_text, gen, "baseline", "")


def run_focus():
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er003_v1_n3_01_articles_generate as gen

    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    return run_one_condition(client, master_full_text, gen, "focus", MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK)


if __name__ == "__main__":
    import sys

    import er005_cost_logger as cl

    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("baseline", "all"):
        run_baseline()
    if which in ("focus", "all"):
        run_focus()
