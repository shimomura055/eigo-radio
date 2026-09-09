# ============================================================
# er011_point_overlap_gap_fix_trial_05.py
# FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05 (Lane A)
# ============================================================
# 目的: FAMILY-A-POINT-OVERLAP-COUNTERMEASURE-PRE-AUDIT-01_REPORT.md が
# 発見した2つの実装ギャップのうち、Reconciliation Check(本ファイル本体
# ではなくFAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05_REPORT.md参照)で
# 「承認済み範囲内の実装漏れ」と判定されたG1のみを修正するTrial。
#
# G1: `er009_diagnostic_full_retry_modules_12.py::build_diagnostic_section()`
#   が、前回のPoint One/Two本文をハードコードされたプレースホルダー文字列
#   "(Point One body from previous attempt)"/"(Point Two body from previous
#   attempt)"のままWriterへ渡している(実テキストが一切埋め込まれていない)。
#   Reconciliation Checkにより、この関数を含むmodule自体を追加した同一
#   commit(f46b6e1)内で、並行して作られた検証済みscript
#   (`er009_n1_diagnostic_full_retry_production_12.py`、DECISION_LOG.md
#   ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14が引用する実runtime evidence
#   [3/3 PASS・Household実発火]の元になったスクリプト)は
#   `previous_point_one=previous_article["point_one_body"]`のように実テキスト
#   を正しく渡していたことを確認した(同じ変換元スクリプト
#   `er009_n1_diagnostic_retry_11.py`も同様)。よってG1は「承認済み・実際に
#   runtime evidenceで検証された設計」からの実装漏れ(module化時の配線漏れ、
#   バグ)であり、新規仕様ではない。
#
# G2(cross_point_overlapの値・共有語を診断promptへ追加)は、Reconciliation
# Checkの結果、CURRENT_SPEC.md「Point One対Point Twoのlexical overlap検査」
# 行(ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01、DECIDED/PRODUCTION_WIRED)
# が承認している内容は「既存のFull Story対Point One/Twoチェックと同じ
# still_flagged判定・同じDiagnostic Full Retryループへの統合」(=retry判定
# トリガーとしての使用)のみであり、「cross_point_overlapの値・共有語を
# 診断prompt本文のテキストとして明示的に追加する」ことまでは、いずれの
# 承認済み記録にも明記されていない。よってこの部分は仕様追加候補と判定し、
# 本Trialでは実装しない(Fableへの指示通りSTOP、詳細はREPORTの§1参照)。
# なお、retry判定トリガーとしてのcross_point_overlap使用自体は今回の
# タスク範囲外(閾値・Loop Budget不変のため、Fableから明示的に対象外と
# 指定)であり、これも変更していない。
#
# 本ファイルはTrial専用(root、新規)。Production関数(run_point_overlap_qa_
# and_regenerate/split_common_sections_for_point_qa/_generate_and_compress_
# article/compute_metrics/run_deviation_check/build_fact_check_prompt/
# run_fact_checker_with_gates/audit_article_directional_facts/local_rewrite
# 一式/run_point_role_planning/run_point_value_qa/build_role_planning_block/
# build_value_qa_diagnostic_note/normalize_article_formatting/
# resolve_editorial_type_module_block/build_common_block/build_prompt)は
# すべてimportのみで無変更。`build_diagnostic_section()`のみ、G1修正版
# として本ファイルへコピー改変し、`run_one_pattern()`もその1呼び出し箇所
# だけを差し替えたコピー(`run_one_pattern_gapfix`)として持つ
# (monkeypatch禁止指示に従い、既存関数のパッチではなくコピー関数として
# 実装)。閾値(0.40)・`POINT_OVERLAP_ARTICLE_RETRY_MAX`(2)・retry判定
# ロジック(`lexical_flagged`/`still_flagged`の定義)は一切変更していない。
#
# baseline(現行=プレースホルダーのまま)は、Production関数
# `prod_gen.run_one_pattern`を完全に無変更のまま直接呼び出す(コピーでは
# ない、正真正銘のProduction経路)。
#
# 費用ロガー: スクリプト冒頭で`cl.install()`を必ず呼ぶ(本日2回の未設置
# 事故の再発防止、CLAUDE.md/PM_GOVERNANCE.md参照)。
# ============================================================
from __future__ import annotations

import difflib
import inspect
import json
import os
import sys
import time

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er003_v1_spoken_first_01_r1_generate as sf1r1
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_directional_fact_precheck_08 as dfp
import er009_diagnostic_full_retry_modules_12 as diagnostic_mod
import er010_ledger_local_rewrite_09 as local_rewrite
import er011_point_role_value_planning_01 as point_planning

THEME_ID = "point_overlap_gap_fix_trial_05"
OUT_DIR = f"er011_output/{THEME_ID}"
COST_LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"

N_RUNS = 3  # ユーザー決定指定。費用上限¥200超過見込みの場合はmain()内でN=2へ縮退する。

# ------------------------------------------------------------
# Hanshin Ledger(Production既存reference、無変更)
# ------------------------------------------------------------
HANSHIN_LEDGER_PATH = "er003_output/n3_01/hanshin/research/verified_fact_ledger.txt"
HANSHIN_TOPIC_JA = (
    "2026年6月某日、阪神対広島戦(甲子園)で、阪神が守備の乱れから広島に先制点を許す"
    "も、直後の攻撃でモンテロの適時打などで逆転し、最終的に接戦を制した一戦。ホーム"
    "ランではなく、堅実な攻守の積み重ねと1点を争う緊迫した展開が特徴の試合。"
)

# ------------------------------------------------------------
# Theme 2 Ledger(承認済み、OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-
# WIRING-01のrunnerと同一パス・同一文面をfile path経由で直接参照。
# 当該runnerモジュール自体はimportせず[importすると`if __name__=="__main__"`
# 配下のrun()以外は安全に読めるが、二重コピーを避けるためpath文字列だけを
# ここへ複製する。runner側は編集していない]。
# ------------------------------------------------------------
THEME2_LEDGER_PATH = ("er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/research/"
                       "theme2_verified_fact_ledger_CORRECTED_trial12.txt")
THEME2_TOPIC_JA = (
    "2026年9月時点、日本の若者(とくに男性)の旅行に対する意識には、「もっと自分の"
    "ペースで、ゆっくり過ごしたい」という願望の高まりがいくつもの独立した調査で確認"
    "されている。日本交通公社(JTBF)の2025年調査では、29歳以下の男性が好む旅行"
    "スタイルの上位に「ひとり旅」(25.2%)・「趣味を深める旅行」(24.3%)が挙がり、海外"
    "旅行経験のある日本のZ世代の約9割が「ツアー内に自由時間が欲しい」と回答し、その"
    "うち約8割が半日以上の自由時間を希望している。じゃらんリサーチセンターの調査では、"
    "1カ月休暇が取れた場合に希望する旅行日数として「1週間程度」と答えた人が24.1%で"
    "最多だった。しかし、同じじゃらんリサーチセンターの別の調査(2024年秋)では、実際の"
    "旅行意向者の宿泊日数は平均1.8泊・中央値2.0泊にとどまっている。観光庁の「令和7年版"
    "観光白書」も、政策的課題として「一人当たり旅行回数の増加や滞在長期化を図る必要が"
    "ある」と明記しており、これは現時点では滞在がまだ十分に長期化していないことを政府"
    "自身が認めた形になっている。また、29歳以下の女性では「有名な観光地を巡る」ことへの"
    "関心が依然として44.7%と高く、性別によって傾向は異なる。今回の記事が扱うのは、"
    "「名所巡りからゆっくり滞在へ、すでに完全に変わった」という単純な話ではなく、意識・"
    "願望としてのスロー志向の高まりと、実際に測定されている短い滞在日数との間のギャップ"
    "という、Trend Synthesisタイプの記事である。"
)
THEME2_EDITORIAL_MODE = "trend_synthesis"

THEMES = {
    "hanshin": {
        "ledger_path": HANSHIN_LEDGER_PATH,
        "topic_ja": HANSHIN_TOPIC_JA,
        "editorial_mode": None,
    },
    "theme2": {
        "ledger_path": THEME2_LEDGER_PATH,
        "topic_ja": THEME2_TOPIC_JA,
        "editorial_mode": THEME2_EDITORIAL_MODE,
    },
}

LEVELS = [
    ("B1B", prod_gen.B1_B_DIRECT_INSTRUCTION, "b1b", "writer_b1"),
    ("A2", prod_gen.A2_KAI1_INSTRUCTION, "a2", "writer_a2"),
]

# Hanshin baselineの再利用元(FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-
# TRIAL-04、baseline条件、N=3。新規生成しない。同一Production関数
# [prod_gen.run_one_pattern経由、editorial_type_module_block=""]・同一
# Hanshin Ledgerで生成済みのため比較可能と判断する。Focus Moduleの有無は
# 本Trialの対象外[diagnostic promptの中身にのみ差分がある]ため、この
# 再利用は妥当)。
HANSHIN_BASELINE_REUSE_DIR = "er011_output/daily_news_focus_layer_comparison_trial_04"


# ============================================================
# G1修正: build_diagnostic_section() のコピー改変版
# ============================================================
def build_diagnostic_section_gapfix(previous_article_text: str, point_one_overlap: dict,
                                     point_two_overlap: dict, previous_point_one_text: str,
                                     previous_point_two_text: str) -> tuple:
    """diagnostic_mod.build_diagnostic_section()のG1修正版コピー。
    DIAGNOSTIC_SECTION_TEMPLATE自体(diagnostic_mod、無変更)・
    classify_overlap()/compose_diagnosis()(診断語彙拡張ではない、既存の
    まま無変更)は一切変更しない。唯一の変更点は、
    previous_point_one/previous_point_twoへハードコードされたプレース
    ホルダー文字列ではなく、実際の前回Point One/Two本文を渡すこと。"""
    diagnosis_one = diagnostic_mod.compose_diagnosis(point_one_overlap)
    diagnosis_two = diagnostic_mod.compose_diagnosis(point_two_overlap)

    return diagnostic_mod.DIAGNOSTIC_SECTION_TEMPLATE.format(
        previous_full_story=previous_article_text,
        point_one_score=point_one_overlap["overlap_ratio"],
        point_one_flagged=point_one_overlap["flagged"],
        previous_point_one=previous_point_one_text,
        diagnosis_one=diagnosis_one,
        point_two_score=point_two_overlap["overlap_ratio"],
        point_two_flagged=point_two_overlap["flagged"],
        previous_point_two=previous_point_two_text,
        diagnosis_two=diagnosis_two,
    ), {
        "diagnosis_one": diagnosis_one,
        "diagnosis_two": diagnosis_two,
    }


def build_diagnostic_retry_prompt_gapfix(original_prompt: str, previous_article_text: str,
                                          point_overlap: dict) -> str:
    """prod_gen.build_diagnostic_retry_prompt()のG1修正版コピー。
    split_common_sections_for_point_qa()はProduction関数をそのまま呼ぶ
    (無変更)。既存コードは、この関数がpoint_one_body/point_two_bodyを
    既に抽出しているにもかかわらず、それらをbuild_diagnostic_section()へ
    渡していなかった(G1の実装漏れそのもの)。本修正はその2つのフィールド
    を渡すことのみを追加する。"""
    sections = prod_gen.split_common_sections_for_point_qa(previous_article_text)
    if sections is None:
        return original_prompt

    diagnostic_section, _ = build_diagnostic_section_gapfix(
        sections["full_story"],
        point_overlap["point_one"],
        point_overlap["point_two"],
        sections["point_one_body"],
        sections["point_two_body"],
    )

    return original_prompt + "\n\n" + diagnostic_section


# ============================================================
# run_one_pattern() のコピー改変版(run_one_pattern_gapfix)
# 変更箇所は1箇所のみ: Diagnostic Full Retry prompt構築の呼び出し先を
# prod_gen.build_diagnostic_retry_prompt -> build_diagnostic_retry_prompt_gapfix
# へ差し替えるのみ。それ以外は全てprod_gen.*経由でProduction関数を
# そのまま呼ぶ(ロジックのコピー箇所ですら、実処理は全てProduction関数
# 呼び出しでありcopy-pasteされているのは制御フローの骨格のみ)。
# ============================================================
def run_one_pattern_gapfix(client, theme_id: str, label: str, prompt: str, verified_ledger_text: str,
                     topic: str, out_dir: str, apply_evidence_compression: bool = True,
                     apply_directional_fact_precheck: bool = True) -> dict:
    """apply_evidence_compression(既定True、ER-008-EVIDENCE-COMPRESSION-
    PROD-AND-N7-AUDIO-06でProduction既定へ昇格): WriterがFact-safeな記事
    を生成した直後、Lossless Editor(方式C、er003_v1_n3_01_evidence_
    compression_editor.py)でspoken layerだけを軽量化する。Research/
    Evidence Pack/VFL/Fact Ledger自体は変更しない。EditorはWriterでは
    なく、意味を保ったまま聴取負荷を下げるだけの工程(禁止事項は
    er003_v1_n3_01_evidence_compression_editor.py参照)。Editor適用後の
    テキストに対してmetrics/Fact Check/Ledger Deviationを実行するため、
    既存の安全確認プロセスがそのままEditor出力にも適用される。DEV/test
    でOFFにしたい場合はFalseを渡す(Production既定はTrue)。"""
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    writer_model = routing.require_model(prod_gen._writer_process(label), routing.WRITER_MODEL)

    # ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: Point One/Twoの本文を書く
    # 前に、Verified Fact Ledgerに基づいてrole/new_listener_takeaway/
    # evidence_anchor/why_it_matters/重複禁止事項を明示的に計画させ、その
    # 計画をWriter promptへ挿入する(Point Role Planning)。
    role_plan_result = point_planning.run_point_role_planning(
        client, topic, verified_ledger_text, model=writer_model, reasoning_effort=prod_gen.REASONING_EFFORT)
    with open(f"{out_dir}/audit/point_role_planning_initial.json", "w", encoding="utf-8") as f:
        json.dump(role_plan_result, f, ensure_ascii=False, indent=2, default=str)
    prompt_with_plan = prompt + "\n" + point_planning.build_role_planning_block(role_plan_result["parsed"])

    gen = prod_gen._generate_and_compress_article(client, theme_id, label, prompt_with_plan, out_dir,
                                          apply_evidence_compression, writer_model)
    if gen["status"] != "OK":
        return {"label": label, "status": gen["status"], "article_text": None}
    article_text = gen["article_text"]
    fact_usage_report = gen["fact_usage_report"]
    evidence_compression_applied = gen["evidence_compression_applied"]

    # ER-22 + ER-009-N1-DIAGNOSTIC-FULL-RETRY-PRODUCTION-WIRING-13:
    # Point overlap NG時は記事全体をWriterから再生成する(最大
    # POINT_OVERLAP_ARTICLE_RETRY_MAX回)。Diagnostic Full Retry により、
    # retry時は前回の記事・overlap score・shared words・簡易診断を
    # NG例として prompt へ追加し、Evidence/VFL固定で全文再生成させる。
    # retry対象はWriter+Evidence Compression+overlap再チェックのみで、
    # Fact Checker/Ledger Deviationはループの外(最終確定後)で一度だけ実行。
    overlap_retry_log = []
    retry_attempt = 0
    while True:
        print(f"[N3-01][{theme_id}] {label}: Point-Full Story/Point-Point重複QA開始"
              f"(retry {retry_attempt}/{prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX})...")
        point_qa_result = prod_gen.run_point_overlap_qa_and_regenerate(
            client, article_text, verified_ledger_text, model=writer_model,
            reasoning_effort=prod_gen.REASONING_EFFORT, out_dir=out_dir)
        overlap_report = point_qa_result.get("report") or {}
        lexical_flagged = point_qa_result["status"] == "OK" and any(
            overlap_report.get(key, {}).get("before_overlap", {}).get("flagged")
            for key in ("point_one", "point_two"))

        # ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: Point Value QA
        # (No.18 A2で発見された「重複はしていないが新しい価値も無い」
        # Pointを検知する。lexical overlapとは独立した意味判定)。
        # split_common_sections_for_point_qaが構造を認識できた場合のみ実行
        # する(想定外構造の場合は既存のoverlap QA同様スキップし、後段の
        # 構造検証[restore_r2.validate_point_structure]に委ねる)。
        sections_for_value_qa = prod_gen.split_common_sections_for_point_qa(article_text)
        value_qa_result = None
        value_qa_flagged = False
        if sections_for_value_qa is not None:
            value_qa_result = point_planning.run_point_value_qa(
                client, sections_for_value_qa["full_story"], sections_for_value_qa["point_one_body"],
                sections_for_value_qa["point_two_body"], model=writer_model,
                reasoning_effort=prod_gen.REASONING_EFFORT)
            with open(f"{out_dir}/audit/point_value_qa_attempt{retry_attempt}.json", "w",
                      encoding="utf-8") as f:
                json.dump(value_qa_result, f, ensure_ascii=False, indent=2, default=str)
            value_qa_flagged = value_qa_result["status"] == "NG"

        still_flagged = lexical_flagged or value_qa_flagged
        log_entry = {
            "attempt": retry_attempt, "qa_status": point_qa_result["status"], "flagged": still_flagged,
            "lexical_flagged": lexical_flagged, "value_qa_flagged": value_qa_flagged,
            "report": overlap_report,
            "value_qa_status": value_qa_result["status"] if value_qa_result else None,
        }
        overlap_retry_log.append(log_entry)
        if not still_flagged or retry_attempt >= prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX:
            break
        retry_attempt += 1
        print(f"[N3-01][{theme_id}] {label}: Point overlap/value QA NG"
              f"(lexical={lexical_flagged}, value_qa={value_qa_flagged})。"
              f"Point Role Planningを再計画し、Diagnostic Full Retryで全文再生成します"
              f"(article retry {retry_attempt}/{prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX})...")

        # Diagnostic section を build(lexical overlap診断は既存機構をそのまま使用)
        point_overlap_result = {
            "point_one": overlap_report["point_one"]["before_overlap"],
            "point_two": overlap_report["point_two"]["before_overlap"],
        }
        diagnostic_prompt = build_diagnostic_retry_prompt_gapfix(prompt, article_text, point_overlap_result)  # G1修正: 実Point本文を埋め込む版
        if value_qa_flagged:
            diagnostic_prompt = diagnostic_prompt + "\n\n" + point_planning.build_value_qa_diagnostic_note(
                value_qa_result)
        log_entry["diagnostic_used"] = {
            "point_one_score": point_overlap_result["point_one"]["overlap_ratio"],
            "point_one_flagged": point_overlap_result["point_one"]["flagged"],
            "point_two_score": point_overlap_result["point_two"]["overlap_ratio"],
            "point_two_flagged": point_overlap_result["point_two"]["flagged"],
            "point_one_vs_point_two_flagged": overlap_report.get("point_one_vs_point_two", {}).get("flagged"),
            "value_qa_flagged": value_qa_flagged,
        }

        # ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: Diagnostic Full Retryは
        # 「必要な生成単位全体をLedgerから再生成する」既存方針に従い、Point
        # Role Planningも記事全体と同じ単位として毎回再計画する(前回の計画を
        # 使い回さない)。
        role_plan_result = point_planning.run_point_role_planning(
            client, topic, verified_ledger_text, model=writer_model, reasoning_effort=prod_gen.REASONING_EFFORT)
        with open(f"{out_dir}/audit/point_role_planning_retry{retry_attempt}.json", "w",
                  encoding="utf-8") as f:
            json.dump(role_plan_result, f, ensure_ascii=False, indent=2, default=str)
        diagnostic_prompt = diagnostic_prompt + "\n" + point_planning.build_role_planning_block(
            role_plan_result["parsed"])

        gen = prod_gen._generate_and_compress_article(client, theme_id, label, diagnostic_prompt, out_dir,
                                              apply_evidence_compression, writer_model)
        if gen["status"] != "OK":
            print(f"[N3-01][{theme_id}] {label}: article retry中にwriterが失敗しました status={gen['status']}")
            overlap_retry_log.append({"attempt": retry_attempt, "qa_status": "WRITER_FAILED_DURING_RETRY"})
            break
        article_text = gen["article_text"]
        fact_usage_report = gen["fact_usage_report"]
        evidence_compression_applied = gen["evidence_compression_applied"]

    with open(f"{out_dir}/point_overlap_article_retry_log.json", "w", encoding="utf-8") as f:
        json.dump(overlap_retry_log, f, ensure_ascii=False, indent=2, default=str)

    point_overlap_qa_applied = False  # Point-only regeneration自体は撤去済み(常にFalse)
    if overlap_retry_log[-1].get("flagged"):
        print(f"[N3-01][{theme_id}] {label}: Point overlapが{prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX}回の記事全体"
              f"再生成後もNGのままでした。自動続行せずNG_REVIEW_REQUIREDとして報告します"
              f"(Fact Checker以降は実行しません)。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "point_overlap_article_retry_attempts": retry_attempt,
            "point_overlap_final_report": overlap_retry_log[-1].get("report"),
            "evidence_compression_applied": evidence_compression_applied,
            "fact_usage_report": fact_usage_report,
            "point_overlap_qa_applied": point_overlap_qa_applied,
        }
    print(f"[N3-01][{theme_id}] {label}: Point-Full Story重複QA完了(overlapなし、"
          f"記事全体retry {retry_attempt}回で解消)。")

    metrics = prod_gen.compute_metrics(article_text)
    section_wc = sf1r1.section_word_counts(article_text)
    length_report = {
        **section_wc, "total": metrics["word_count"],
        "point_one_within_target": prod_gen.POINT_TARGET_LOWER <= section_wc["point_one"] <= prod_gen.POINT_TARGET_UPPER,
        "point_one_within_tolerance": prod_gen.POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= prod_gen.POINT_TOLERANCE_UPPER,
        "point_two_within_target": prod_gen.POINT_TARGET_LOWER <= section_wc["point_two"] <= prod_gen.POINT_TARGET_UPPER,
        "point_two_within_tolerance": prod_gen.POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= prod_gen.POINT_TOLERANCE_UPPER,
        "total_within_soft_range": prod_gen.TOTAL_SOFT_LOWER <= metrics["word_count"] <= prod_gen.TOTAL_SOFT_UPPER,
    }
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    print(f"[N3-01][{theme_id}] {label}: metrics={metrics} sections={section_wc}")

    print(f"[N3-01][{theme_id}] {label}: fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[N3-01][{theme_id}] {label}: fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    # ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12(ユーザー正式Decision):
    # Fact Checkerのverdict="REVIEW_REQUIRED"(確認できない具体的主張・解釈・
    # certainty nuance等、fact_checker_prompt_template_r3.txt参照)は、原則
    # non-blocking advisoryとして扱い、記事生成・QA工程を継続する(status=OKの
    # 判定材料にしない)。指摘は最終artifact提示時に「Fact Checker参考指摘」
    # として別途ユーザーへ提示する(fact_qa.jsonのcontradictions/
    # unsupported_specific_claims/notesがその内容)。一方、verdict="FAIL"
    # (信頼できる情報と明確に矛盾する場合のみ付与される)は、Ledger Deviation
    # MAJORや Point overlap未解消と同様にblockingとして扱い、それ以降の
    # 工程(Ledger逸脱チェック・Directional Fact Precheck)は実行せず
    # NG_REVIEW_REQUIREDを返す。役割はLedger Deviation Checkerとは異なる
    # (Ledgerは記事とVerified Fact Ledgerの整合性、Fact Checkerは独立Web
    # 検索によるexternal factとの整合性)ため、判定を混同しない。
    if verdict == "FAIL":
        print(f"[N3-01][{theme_id}] {label}: fact checkerがFAIL(信頼できる情報と明確に矛盾)と"
              f"判定しました。自動続行せずNG_REVIEW_REQUIREDとして報告します"
              f"(ledger逸脱チェック以降は実行しません)。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
            "fact_status": fc_status, "fact_verdict": verdict, "fact_check_result": fc_result,
            "fact_usage_report": fact_usage_report,
            "evidence_compression_applied": evidence_compression_applied,
            "point_overlap_qa_applied": point_overlap_qa_applied,
            "point_overlap_article_retry_attempts": retry_attempt,
        }

    print(f"[N3-01][{theme_id}] {label}: ledger逸脱チェック開始(Hook-aware)...")
    ledger_model = routing.require_model(prod_gen._writer_process(label), routing.WRITER_MODEL)
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
    print(f"[N3-01][{theme_id}] {label}: deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")

    # ER-010-NO9-LOCAL-REWRITE-LOOP-FINAL-10: MAJOR検出時は記事全体を再生成
    # せず、局所Rewriteのみを行う。局所Rewrite後は記事全体をLedger Deviation
    # Checkerへ再投入し(Hook-aware)、そこで新たなMAJORが見つかった場合も
    # 「一度直したから終了」とはせず、MAX_REWRITE_CYCLES回まで同じ局所
    # Rewriteを繰り返す(cycle上限の根拠はer010_ledger_local_rewrite_09.py
    # のMAX_REWRITE_CYCLES定義を参照)。対象はMAJORのみ、MINORは記録のみで
    # 対象外。上限まで繰り返してもMAJORが残る場合はNG_REVIEW_REQUIREDとし、
    # 無限ループや黙示的PASSは行わない。
    local_rewrite_results = []
    local_rewrite_cycles = []
    cycle = 0
    previously_seen_claims = set()

    def _run_check_window(window_text: str) -> dict:
        r = vfl01.run_deviation_check(client, verified_ledger_text, window_text,
                                       model=ledger_model, hook_aware=True)
        return r["parsed"]

    major_items = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]

    while major_items and cycle < local_rewrite.MAX_REWRITE_CYCLES:
        cycle += 1
        newly_discovered_claims = [d["claim_in_article"] for d in major_items
                                    if d["claim_in_article"] not in previously_seen_claims]
        print(f"[N3-01][{theme_id}] {label}: Local Rewrite cycle {cycle}/"
              f"{local_rewrite.MAX_REWRITE_CYCLES} - Ledger MAJOR {len(major_items)}件を検出"
              f"({len(newly_discovered_claims)}件は前cycleまでに未出現の新規MAJOR)。局所Rewrite開始...")

        cycle_results = []
        sentences = local_rewrite.split_sentences(article_text)
        for idx, deviation in enumerate(major_items, start=1):
            target, location_method = local_rewrite.locate_target_sentence(
                deviation["claim_in_article"], article_text)
            if target is None:
                cycle_results.append({
                    "cycle": cycle, "item_idx": idx, "original_ng_sentence": deviation["claim_in_article"],
                    "issue": deviation["issue"], "explanation": deviation["explanation"],
                    "attempts": [], "final_text": None, "resolved": False,
                    "human_review_required": True, "location_method": "not_found",
                })
                print(f"[N3-01][{theme_id}] {label}: cycle {cycle} NG item {idx}: 対象文が特定できず"
                      f"human_review_required=Trueとして記録します。")
                continue
            try:
                sidx = sentences.index(target)
            except ValueError:
                sidx = -1
            before_ctx = sentences[sidx - 1] if 0 <= sidx - 1 else ""
            after_ctx = sentences[sidx + 1] if 0 <= sidx and sidx + 1 < len(sentences) else ""
            # OPEN-113-POINT-CONTEXT-PRODUCTION-WIRING-04(ユーザー正式採用、
            # OPEN-113 Trial-03でVALIDATED): 対象文が属するPoint(またはsection)
            # 全文をRewriteモデルへ参考contextとして渡す。既存のbefore/after
            # context(check windowの範囲)・System Prompt・attempt escalation
            # 文言・Retry上限・Ledger再チェック方法は一切変更しない。対象文の
            # 所属section特定に失敗した稀なケースのみ、追加前の挙動(前後1文)へ
            # fallbackする。
            point_context = local_rewrite.extract_point_context(article_text, target)
            point_context_found = point_context is not None
            if point_context is None:
                point_context = f"{before_ctx} {target} {after_ctx}".strip()
            r = local_rewrite.rewrite_ng_item(client, ledger_model, prod_gen.REASONING_EFFORT,
                                               verified_ledger_text, point_context, target,
                                               deviation, before_ctx, after_ctx, _run_check_window)
            r["cycle"] = cycle
            r["item_idx"] = idx
            r["location_method"] = location_method
            r["point_context_found"] = point_context_found
            r["point_context"] = point_context
            cycle_results.append(r)
            print(f"[N3-01][{theme_id}] {label}: cycle {cycle} NG item {idx}: resolved={r['resolved']} "
                  f"human_review={r['human_review_required']} attempts={len(r['attempts'])}")

        article_text = local_rewrite.apply_rewrites(article_text, cycle_results)

        # Formatting normalization (emoji・unnecessary bold削除)
        article_text = prod_gen.normalize_article_formatting(article_text)

        with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(article_text)

        # 局所Rewriteで本文が変わったため、metrics/length_reportを再計算し
        # 上書きする(Rewrite前のword countがそのまま記録され続けるのを防ぐ)。
        metrics = prod_gen.compute_metrics(article_text)
        section_wc = sf1r1.section_word_counts(article_text)
        length_report = {
            **section_wc, "total": metrics["word_count"],
            "point_one_within_target": prod_gen.POINT_TARGET_LOWER <= section_wc["point_one"] <= prod_gen.POINT_TARGET_UPPER,
            "point_one_within_tolerance": prod_gen.POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= prod_gen.POINT_TOLERANCE_UPPER,
            "point_two_within_target": prod_gen.POINT_TARGET_LOWER <= section_wc["point_two"] <= prod_gen.POINT_TARGET_UPPER,
            "point_two_within_tolerance": prod_gen.POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= prod_gen.POINT_TOLERANCE_UPPER,
            "total_within_soft_range": prod_gen.TOTAL_SOFT_LOWER <= metrics["word_count"] <= prod_gen.TOTAL_SOFT_UPPER,
        }
        with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
            json.dump(length_report, f, ensure_ascii=False, indent=2)

        print(f"[N3-01][{theme_id}] {label}: cycle {cycle} Local Rewrite後、Ledger全体を再判定...")
        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
        recheck_major = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
        print(f"[N3-01][{theme_id}] {label}: cycle {cycle} 再判定 overall_status="
              f"{deviation_result['parsed']['overall_status']} MAJOR={len(recheck_major)}件")

        previously_seen_claims |= {d["claim_in_article"] for d in major_items}
        local_rewrite_results.extend(cycle_results)
        local_rewrite_cycles.append({
            "cycle": cycle,
            "targeted_major_count": len(major_items),
            "newly_discovered_claims": newly_discovered_claims,
            "results": cycle_results,
            "full_recheck_overall_status": deviation_result["parsed"]["overall_status"],
            "full_recheck_major_count": len(recheck_major),
            "full_recheck_remaining_major_claims": [d["claim_in_article"] for d in recheck_major],
        })

        major_items = recheck_major

    cycle_exhausted = bool(major_items) and cycle >= local_rewrite.MAX_REWRITE_CYCLES
    if cycle_exhausted:
        print(f"[N3-01][{theme_id}] {label}: Local Rewrite cycle上限"
              f"({local_rewrite.MAX_REWRITE_CYCLES}回)に達してもMAJORが残存しています。")

    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/audit/local_rewrite_results.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_results, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/audit/local_rewrite_cycles.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_cycles, f, ensure_ascii=False, indent=2, default=str)

    remaining_major = major_items
    any_human_review = any(r.get("human_review_required") for r in local_rewrite_results)
    if remaining_major or any_human_review:
        print(f"[N3-01][{theme_id}] {label}: Local Rewrite cycleを尽くしてもLedger MAJORが残存、"
              f"またはhuman_review_requiredな項目があります。自動続行せずNG_REVIEW_REQUIREDとして"
              f"報告します(Directional Fact Precheck以降は実行しません)。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": prod_gen.compute_metrics(article_text),
            "fact_status": fc_status, "fact_verdict": verdict,
            "ledger_status": deviation_result["parsed"]["overall_status"],
            "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
            "local_rewrite_results": local_rewrite_results,
            "local_rewrite_cycles": local_rewrite_cycles,
            "local_rewrite_cycle_exhausted": cycle_exhausted,
            "fact_usage_report": fact_usage_report,
            "evidence_compression_applied": evidence_compression_applied,
            "point_overlap_qa_applied": point_overlap_qa_applied,
            "point_overlap_article_retry_attempts": retry_attempt,
        }

    directional_precheck_status = None
    if apply_directional_fact_precheck:
        print(f"[N3-01][{theme_id}] {label}: 比較方向Fact事前チェック(暫定、"
              f"ER-008-DIRECTIONAL-FACT-PRECHECK-08)開始...")
        vfl_path = f"{os.path.dirname(out_dir)}/research/stage_b3_vfl.json"
        directional_result = dfp.audit_article_directional_facts(
            article_text, verified_ledger_text, vfl_path=vfl_path)
        directional_precheck_status = directional_result["overall_status"]
        with open(f"{out_dir}/audit/directional_fact_precheck.json", "w", encoding="utf-8") as f:
            json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[N3-01][{theme_id}] {label}: 比較方向Fact事前チェック完了。"
              f"overall_status={directional_precheck_status}"
              + ("(POTENTIAL_DIRECTION_REVERSALあり、詳細はdirectional_fact_precheck.jsonを確認)"
                 if directional_precheck_status == "POTENTIAL_DIRECTION_REVERSAL" else ""))

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "local_rewrite_results": local_rewrite_results,
        "local_rewrite_cycles": local_rewrite_cycles,
        "local_rewrite_cycle_exhausted": cycle_exhausted,
        "fact_usage_report": fact_usage_report,
        "evidence_compression_applied": evidence_compression_applied,
        "point_overlap_qa_applied": point_overlap_qa_applied,
        "point_overlap_article_retry_attempts": retry_attempt,
        "directional_fact_precheck_status": directional_precheck_status,
    }

# ============================================================
# 単体テスト(既定経路バイト一致・G1修正の差分が前回Point本文の埋め込み
# のみであることの静的/動的検証、Trial-03/04と同じ方式)
# ============================================================
def test_g1_gapfix_only_differs_by_point_body_text() -> dict:
    """G1修正版の診断promptが、baseline(プレースホルダーのまま)から
    「前回Point本文の埋め込み」以外の差分を一切持たないことを、合成
    fixtureで検証する。"""
    synthetic_article = (
        "# Test Title\n"
        "Full story sentence one. Full story sentence two about an unrelated topic zeta.\n\n"
        "### Point One Heading\n"
        "UNIQUE_POINT_ONE_BODY_TEXT_ABC123 that never appears elsewhere in this fixture.\n\n"
        "### Point Two Heading\n"
        "UNIQUE_POINT_TWO_BODY_TEXT_XYZ789 that also never appears elsewhere in this fixture.\n\n"
        "## In one line\n"
        "A single summary line.\n"
    )
    point_overlap_result = {
        "point_one": {"overlap_ratio": 0.5, "flagged": True, "shared_words": ["study", "percent"], "threshold": 0.40},
        "point_two": {"overlap_ratio": 0.45, "flagged": True, "shared_words": ["worker", "guilty"], "threshold": 0.40},
    }
    original_prompt = "ORIGINAL PROMPT BODY"

    baseline_prompt = prod_gen.build_diagnostic_retry_prompt(original_prompt, synthetic_article, point_overlap_result)
    gapfix_prompt = build_diagnostic_retry_prompt_gapfix(original_prompt, synthetic_article, point_overlap_result)

    assert "(Point One body from previous attempt)" in baseline_prompt
    assert "(Point Two body from previous attempt)" in baseline_prompt
    assert "UNIQUE_POINT_ONE_BODY_TEXT_ABC123" not in baseline_prompt
    assert "UNIQUE_POINT_TWO_BODY_TEXT_XYZ789" not in baseline_prompt

    assert "UNIQUE_POINT_ONE_BODY_TEXT_ABC123" in gapfix_prompt
    assert "UNIQUE_POINT_TWO_BODY_TEXT_XYZ789" in gapfix_prompt
    assert "(Point One body from previous attempt)" not in gapfix_prompt
    assert "(Point Two body from previous attempt)" not in gapfix_prompt

    reconstructed = gapfix_prompt.replace(
        "UNIQUE_POINT_ONE_BODY_TEXT_ABC123 that never appears elsewhere in this fixture.",
        "(Point One body from previous attempt)",
    ).replace(
        "UNIQUE_POINT_TWO_BODY_TEXT_XYZ789 that also never appears elsewhere in this fixture.",
        "(Point Two body from previous attempt)",
    )
    assert reconstructed == baseline_prompt, (
        "G1修正版とbaselineの差分が前回Point本文の埋め込み以外にも存在します(想定外の差分)")
    return {"status": "PASS"}


def test_run_one_pattern_gapfix_matches_production_except_diagnostic_call() -> dict:
    """run_one_pattern_gapfix()が、prod_gen.run_one_pattern()から
    「診断prompt構築の呼び出し先変更」1箇所以外で逸脱していないことを
    ソースコードの静的diffで確認する(コピー時のtypo・意図しないretry
    判定/閾値変更を検出するためのGate 4的な安全確認)。"""
    prod_src = inspect.getsource(prod_gen.run_one_pattern)
    gapfix_src = inspect.getsource(run_one_pattern_gapfix)

    def normalize(src: str, old_name: str) -> str:
        src = src.replace(f"def {old_name}(", "def FUNC(")
        src = src.replace(
            "diagnostic_prompt = build_diagnostic_retry_prompt(prompt, article_text, point_overlap_result)",
            "diagnostic_prompt = DIAGNOSTIC_BUILDER_CALL")
        src = src.replace(
            "diagnostic_prompt = build_diagnostic_retry_prompt_gapfix(prompt, article_text, point_overlap_result)"
            "  # G1修正: 実Point本文を埋め込む版",
            "diagnostic_prompt = DIAGNOSTIC_BUILDER_CALL")
        for name in ("_writer_process", "_generate_and_compress_article",
                     "run_point_overlap_qa_and_regenerate", "split_common_sections_for_point_qa",
                     "compute_metrics", "normalize_article_formatting",
                     "POINT_OVERLAP_ARTICLE_RETRY_MAX", "REASONING_EFFORT",
                     "POINT_TARGET_LOWER", "POINT_TARGET_UPPER", "POINT_TOLERANCE_LOWER",
                     "POINT_TOLERANCE_UPPER", "TOTAL_SOFT_LOWER", "TOTAL_SOFT_UPPER"):
            src = src.replace(f"prod_gen.{name}", name)
        return src

    prod_norm = normalize(prod_src, "run_one_pattern")
    gapfix_norm = normalize(gapfix_src, "run_one_pattern_gapfix")
    diff = list(difflib.unified_diff(prod_norm.splitlines(), gapfix_norm.splitlines(), lineterm=""))
    assert prod_norm == gapfix_norm, (
        "run_one_pattern_gapfixがG1の診断prompt呼び出し1箇所以外でprod_gen.run_one_patternと"
        "逸脱しています(意図しない変更の疑い):\n" + "\n".join(diff[:300])
    )
    return {"status": "PASS", "diff_line_count": len(diff)}


def run_all_unit_tests() -> dict:
    results = {
        "test_g1_gapfix_only_differs_by_point_body_text": test_g1_gapfix_only_differs_by_point_body_text(),
        "test_run_one_pattern_gapfix_matches_production_except_diagnostic_call":
            test_run_one_pattern_gapfix_matches_production_except_diagnostic_call(),
    }
    all_pass = all(r.get("status") == "PASS" for r in results.values())
    results["all_pass"] = all_pass
    print(f"[GAPFIX-05][tests] all_pass={all_pass}")
    for name, r in results.items():
        if name != "all_pass":
            print(f"  {name}: {r.get('status')}")
    return results


# ============================================================
# 実行・計測ハーネス
# ============================================================
def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def analyze_run(out_dir: str, result: dict) -> dict:
    """生成済み(または再利用済み)runの成果物を読み、集計用の指標を
    機械的に抽出する(Trial-04のanalyze_run方式を踏襲、role分類は本
    Trialの対象外のため含めない)。"""
    retry_attempts = result.get("point_overlap_article_retry_attempts") or 0
    overlap_log_path = f"{out_dir}/point_overlap_article_retry_log.json"
    overlap_log = []
    if os.path.exists(overlap_log_path):
        with open(overlap_log_path, encoding="utf-8") as f:
            overlap_log = json.load(f)
    final_overlap_report = overlap_log[-1].get("report") if overlap_log else None

    point_one_overlap = point_two_overlap = None
    point_one_flagged = point_two_flagged = None
    cross_p1v2_ratio = cross_p1v2_flagged = cross_p2v1_ratio = cross_p2v1_flagged = None
    if final_overlap_report:
        po = final_overlap_report.get("point_one", {}).get("before_overlap", {})
        pt = final_overlap_report.get("point_two", {}).get("before_overlap", {})
        point_one_overlap, point_one_flagged = po.get("overlap_ratio"), po.get("flagged")
        point_two_overlap, point_two_flagged = pt.get("overlap_ratio"), pt.get("flagged")
        c12 = final_overlap_report.get("point_one_vs_point_two", {})
        c21 = final_overlap_report.get("point_two_vs_point_one", {})
        cross_p1v2_ratio, cross_p1v2_flagged = c12.get("overlap_ratio"), c12.get("flagged")
        cross_p2v1_ratio, cross_p2v1_flagged = c21.get("overlap_ratio"), c21.get("flagged")

    article_path = f"{out_dir}/article.md"
    word_count = None
    section_wc = None
    if os.path.exists(article_path):
        article_text = load_text(article_path)
        metrics = prod_gen.compute_metrics(article_text)
        word_count = metrics["word_count"]
        section_wc = sf1r1.section_word_counts(article_text)

    retry_history = [{
        "attempt": e.get("attempt"),
        "flagged": e.get("flagged"),
        "lexical_flagged": e.get("lexical_flagged"),
        "value_qa_flagged": e.get("value_qa_flagged"),
        "point_one_overlap_ratio": e.get("report", {}).get("point_one", {}).get("before_overlap", {}).get("overlap_ratio"),
        "point_two_overlap_ratio": e.get("report", {}).get("point_two", {}).get("before_overlap", {}).get("overlap_ratio"),
        "cross_point_one_vs_two_ratio": e.get("report", {}).get("point_one_vs_point_two", {}).get("overlap_ratio"),
        "cross_point_two_vs_one_ratio": e.get("report", {}).get("point_two_vs_point_one", {}).get("overlap_ratio"),
    } for e in overlap_log]

    return {
        "status": result.get("status"),
        "retry_attempts": retry_attempts,
        "diagnostic_full_retry_fired": retry_attempts > 0,
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
        "cross_point_one_vs_two_ratio": cross_p1v2_ratio,
        "cross_point_one_vs_two_flagged": cross_p1v2_flagged,
        "cross_point_two_vs_one_ratio": cross_p2v1_ratio,
        "cross_point_two_vs_one_flagged": cross_p2v1_flagged,
        "retry_history": retry_history,
    }


def run_one_combo(client, master_full_text: str, theme_key: str, condition_name: str,
                   run_idx: int, label: str, instruction: str, level_dir: str, stage_tag: str) -> dict:
    theme = THEMES[theme_key]
    verified_ledger_text = load_text(theme["ledger_path"])
    editorial_type_module_block = prod_gen.resolve_editorial_type_module_block(theme["editorial_mode"])
    out_dir = f"{OUT_DIR}/{theme_key}/{level_dir}/{condition_name}/run{run_idx}"
    common_block = prod_gen.build_common_block(
        master_full_text, theme["topic_ja"], verified_ledger_text,
        editorial_type_module_block=editorial_type_module_block)
    prompt = prod_gen.build_prompt(common_block, instruction)

    theme_tag = f"{THEME_ID}_{theme_key}_{condition_name}_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, stage_tag):
        if condition_name == "baseline":
            result = prod_gen.run_one_pattern(client, theme_tag, label, prompt, verified_ledger_text,
                                               theme["topic_ja"], out_dir)
        elif condition_name == "gapfix":
            result = run_one_pattern_gapfix(client, theme_tag, label, prompt, verified_ledger_text,
                                             theme["topic_ja"], out_dir)
        else:
            raise ValueError(f"unknown condition_name: {condition_name}")
    elapsed = round(time.time() - t0, 2)

    analysis = analyze_run(out_dir, result)
    analysis.update({
        "elapsed_seconds": elapsed, "condition": condition_name, "theme": theme_key,
        "level": label, "run": run_idx, "source": "generated",
    })
    with open(f"{out_dir}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in result.items() if k != "article_text"}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    print(f"[GAPFIX-05][{theme_key}][{condition_name}][{label}] run{run_idx}: status={result.get('status')} "
          f"retry={analysis['retry_attempts']} p1_overlap={analysis['point_one_overlap_ratio']} "
          f"p2_overlap={analysis['point_two_overlap_ratio']} elapsed={elapsed}s")
    return analysis


# Hanshin baselineの再利用(新規生成しない)。FAMILY-A-DAILY-NEWS-FOCUS-
# LAYER-COMPARISON-TRIAL-04のbaseline条件N=3を、そのまま読み込むだけ。
HANSHIN_BASELINE_LEVEL_DIR = {"A2": "a2", "B1B": "b1b"}


def reuse_hanshin_baseline(label: str, run_idx: int) -> dict:
    level_dir = HANSHIN_BASELINE_LEVEL_DIR[label]
    source_dir = f"{HANSHIN_BASELINE_REUSE_DIR}/{level_dir}/baseline/run{run_idx}"
    if not os.path.exists(f"{source_dir}/run_summary.json"):
        raise FileNotFoundError(f"Hanshin baseline reuse source not found: {source_dir}")
    with open(f"{source_dir}/run_summary.json", encoding="utf-8") as f:
        result = json.load(f)
    analysis = analyze_run(source_dir, result)
    analysis.update({
        "elapsed_seconds": None, "condition": "baseline", "theme": "hanshin",
        "level": label, "run": run_idx, "source": "reused_from_trial_04", "source_dir": source_dir,
    })
    out_dir = f"{OUT_DIR}/hanshin/{level_dir}/baseline/run{run_idx}"
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/reused_from.txt", "w", encoding="utf-8") as f:
        f.write(f"reused (no new generation): {source_dir}\n"
                f"rationale: FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05_REPORT.md. "
                f"Same production function (prod_gen.run_one_pattern, editorial_type_module_block=\"\") "
                f"and same Hanshin Ledger as this Trial's baseline condition would use.\n")
    print(f"[GAPFIX-05][hanshin][baseline][{label}] run{run_idx}: reused (no new generation) "
          f"source={source_dir} status={analysis['status']} retry={analysis['retry_attempts']}")
    return analysis


COMBOS = [
    ("hanshin", "gapfix", "B1B"),
    ("hanshin", "gapfix", "A2"),
    ("theme2", "baseline", "B1B"),
    ("theme2", "baseline", "A2"),
    ("theme2", "gapfix", "B1B"),
    ("theme2", "gapfix", "A2"),
]

LEVEL_META = {
    "B1B": (prod_gen.B1_B_DIRECT_INSTRUCTION, "b1b", "writer_b1"),
    "A2": (prod_gen.A2_KAI1_INSTRUCTION, "a2", "writer_a2"),
}


def run_single(theme_key: str, condition_name: str, label: str, run_idx: int) -> dict:
    """1 combo(1 theme x 1 condition x 1 level x 1 run)だけを実行する。
    費用ロガーは呼び出し側(__main__)で既にinstall済みである前提。"""
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    instruction, level_dir, stage_tag = LEVEL_META[label]
    return run_one_combo(client, master_full_text, theme_key, condition_name, run_idx,
                          label, instruction, level_dir, stage_tag)


def aggregate() -> dict:
    """既に生成済み・再利用済みの全analysis.jsonを収集し、集計表を作る。"""
    all_analyses = []
    for run_idx in (1, 2, 3):
        for label in ("A2", "B1B"):
            level_dir = HANSHIN_BASELINE_LEVEL_DIR[label]
            path = f"{OUT_DIR}/hanshin/{level_dir}/baseline/run{run_idx}/analysis.json"
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    all_analyses.append(json.load(f))
    for theme_key, condition_name, label in COMBOS:
        _, level_dir, _ = LEVEL_META[label]
        for run_idx in (1, 2, 3):
            path = f"{OUT_DIR}/{theme_key}/{level_dir}/{condition_name}/run{run_idx}/analysis.json"
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    all_analyses.append(json.load(f))

    with open(f"{OUT_DIR}/all_analyses.json", "w", encoding="utf-8") as f:
        json.dump(all_analyses, f, ensure_ascii=False, indent=2, default=str)

    summary = {}
    for a in all_analyses:
        key = (a["theme"], a["condition"], a["level"])
        summary.setdefault(key, []).append(a)
    table = []
    for key, items in sorted(summary.items()):
        n = len(items)
        ng = sum(1 for i in items if i["status"] == "NG_REVIEW_REQUIRED")
        fired = sum(1 for i in items if i["diagnostic_full_retry_fired"])
        avg_retry = round(sum(i["retry_attempts"] for i in items) / n, 2) if n else None
        table.append({
            "theme": key[0], "condition": key[1], "level": key[2], "n": n,
            "ng_review_required": ng, "ng_rate": round(ng / n, 3) if n else None,
            "diagnostic_full_retry_fired_count": fired,
            "avg_retry_attempts": avg_retry,
        })
    with open(f"{OUT_DIR}/aggregate_summary.json", "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps(table, ensure_ascii=False, indent=2))
    return {"all_analyses": all_analyses, "table": table}


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(COST_LOG_PATH)

    cmd = sys.argv[1] if len(sys.argv) > 1 else "test"
    if cmd == "test":
        run_all_unit_tests()
    elif cmd == "reuse_hanshin_baseline":
        for label in ("A2", "B1B"):
            for run_idx in (1, 2, 3):
                reuse_hanshin_baseline(label, run_idx)
    elif cmd == "run":
        theme_key_arg, condition_arg, label_arg, run_idx_arg = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
        run_single(theme_key_arg, condition_arg, label_arg, run_idx_arg)
    elif cmd == "aggregate":
        aggregate()
    else:
        print("usage: python er011_point_overlap_gap_fix_trial_05.py [test|reuse_hanshin_baseline|"
              "run <theme_key> <condition> <label> <run_idx>|aggregate]")
