# ============================================================
# er011_point_role_planning_focus_connection_trial_04.py
# 管理ID: FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01
# (Fable修正指示1回目、STOP解除)
# ============================================================
# 経緯: FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01は
# Gate 4静的確認で一度STOPした(詳細は
# `FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01_REPORT.md`
# 1節)。原因: 再利用予定だった`er011_point_role_planning_focus_connection_
# trial_03.py`の`run_one_pattern_connected`(Trial-03[2026-09-09]時点の
# Production `run_one_pattern`のコピー)が、本タスクと同日のcommit
# ce39de7b(OPEN-141差分QA+target-sentence-matching既定ON、ユーザー正式
# 判断2026-09-13)を欠いており、新規生成する「focus+接続」記事だけが
# この新規安全ゲート(Local Rewrite受理直後のFact Checker A'再実行+Ledger
# 再確認+Point Overlap再計算)を経由しない不公平・安全装置無断回避リスクが
# あったため。
#
# Fable判断(選択肢(a)採用、Trial専用ファイルの更新はFable自律範囲・
# Production無変更): 接続関数を現行Production run_one_pattern
# (er003_v1_n3_01_articles_generate.py 818-1248行)と同等の新コピー
# として本ファイルに作り直し、hint注入以外の差分ゼロを機械的に証明した
# うえでTrialを実行する。旧er011_point_role_planning_focus_connection_
# trial_03.pyは改変しない(News向けGate 1=VALIDATED実績の履歴保全)。
#
# 【本ファイルの位置づけ】Trial(Production実装ではない)。
# Production/Prompt/SSOT編集・Git操作は一切行わない。monkeypatch・
# グローバル書き換えは行わない(client.responses.createへ渡す引数として
# の通常のFakeClientはmonkeypatchではない。テストファイル側で
# unittest.mock.patch.objectを用いる箇所があるが、これはテスト実行中のみ
# 有効な標準的モック手法であり、本ファイル[実装]自体は一切書き換えを
# 行わない)。
#
# ------------------------------------------------------------
# 0. 再利用/コピーの内訳(Gate 4)
# ------------------------------------------------------------
# 【再利用(import・無変更)】
#   - er003_v1_n3_01_articles_generate(prod_genとしてimport): 全ての
#     内部helper関数・モジュール定数はprod_gen.NAMEの形でそのまま呼び出す
#     (コピーしない、内容の変更なし)。build_common_block/build_prompt/
#     resolve_editorial_type_module_block/EDITORIAL_TYPE_MODULE_BLOCKSも
#     無変更のままimport・呼び出しのみ。
#   - er011_point_role_value_planning_01(point_planningとしてimport):
#     build_role_planning_block/run_point_value_qa/build_value_qa_
#     diagnostic_note/ROLE_PLANNING_JSON_SCHEMA/ROLE_PLANNING_DEVELOPER_
#     MESSAGE/RolePlanningModelMismatchErrorは無変更のままpoint_planning.
#     NAMEで呼び出す(Trial-03実施[2026-09-09]以降、本ファイルも無変更
#     であることをGate 4で再確認済み、git diff --stat d79a9f9a..HEAD --
#     er011_point_role_value_planning_01.pyが空)。
#   - 他の全依存モジュール(r3, ab01, vfl01, sf1r1, routing, dfp,
#     local_rewrite, canon_spelling, overlap_qa)もimportのみ、無変更。
#
# 【コピー・改変(Trial限定、理由: 呼び出しチェーンの中間に新しい引数を
#  通す接続点が必要で、Production関数のシグネチャ自体を変更せずには
#  実現できないため)】
#   - run_one_pattern_connected: er003_v1_n3_01_articles_generate.py
#     run_one_pattern()(818-1248行、431行、OPEN-141差分QA込みの現行版)
#     のコピー。変更点は (i) 関数名run_one_pattern -> run_one_pattern_
#     connected、(ii) 新規引数point_role_hint_block: str = ""の追加、
#     (iii) 2箇所のpoint_planning.run_point_role_planning(...)呼び出しを
#     run_point_role_planning_connected(..., point_role_hint_block=
#     point_role_hint_block)へ置換、(iv) 元は同一module内のbare参照
#     だったヘルパー関数・定数をprod_gen.NAMEへ明示的に修飾。ロジック・
#     分岐・文言・print文・出力ファイル名・retry上限・OPEN-141差分QA
#     (Fact Checker A'再実行+Ledger再確認+Point Overlap再計算)・
#     target-sentence-matching既定ONは一切変更していない。
#
#     この4点の差分は、er011_point_role_planning_focus_connection_
#     trial_04_test_01.pyのGate 4機械検証テストで、Production版
#     run_one_patternのソース(inspect.getsource)へ既知の置換規則
#     (関数名・シグネチャ・2箇所の呼び出し・ヘルパー参照14件の修飾)を
#     機械的に適用した結果が本ファイルのrun_one_pattern_connectedの
#     ソースとバイト単位で完全一致することを毎回自動確認する(単なる
#     目視diffではなく、再現可能な機械証明)。
#   - run_point_role_planning_connected / ROLE_PLANNING_PROMPT_TEMPLATE_
#     CONNECTED: er011_point_role_value_planning_01.py run_point_role_
#     planning()(124-145行)+ROLE_PLANNING_PROMPT_TEMPLATE(72-117行)の
#     コピー。Trial-03から変更なし(該当ファイルがTrial-03以降無変更の
#     ため、コピー元と完全に同一)。テンプレートの「【Verified Fact
#     Ledger】{verified_ledger_text}」と「Point One・Point Twoそれぞれに
#     ついて」の間に{point_role_hint_block}placeholderを追加し、関数へ
#     point_role_hint_block: str = ""引数を追加しただけ。schema/developer
#     message/JSON parse/model一致チェックは無変更(point_planning.
#     ROLE_PLANNING_JSON_SCHEMA/ROLE_PLANNING_DEVELOPER_MESSAGE/
#     RolePlanningModelMismatchErrorをそのまま再利用)。
#
# monkeypatch・グローバル書き換えは本ファイル(実装)には一切存在しない。
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
import er006_model_routing_contract_01 as routing
import er008_directional_fact_precheck_08 as dfp
import er008_point_overlap_qa_18 as overlap_qa
import er003_v1_spoken_first_01_r1_generate as sf1r1
import er010_ledger_local_rewrite_09 as local_rewrite
import er011_open146_ledger_canonical_en_spelling_production_01 as canon_spelling
import er011_point_role_value_planning_01 as point_planning

THEME_ID = "point_role_planning_focus_connection_trial_04"
OUT_DIR = f"er011_output/{THEME_ID}"


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# Point Role Planning接続版 (er011_point_role_value_planning_01.py
# ROLE_PLANNING_PROMPT_TEMPLATE 72-117行のコピー。Trial-03から無変更
# [point_planningモジュールがTrial-03以降無変更のため]。挿入箇所のみ
# 変更、他は一切変更していない)
# ============================================================
ROLE_PLANNING_PROMPT_TEMPLATE_CONNECTED = \
"""これから、以下のVerified Fact Ledgerに基づいて、英語ニュースpodcast記事の
Point One・Point Twoを書きます。本文を書く前に、まず両方の設計を計画して
ください。

【今回のテーマ】
{topic}

【Verified Fact Ledger】
{verified_ledger_text}

{point_role_hint_block}Point One・Point Twoそれぞれについて、以下を具体的に(このLedger固有の
内容で、どんな記事にも当てはまるテンプレート的な一般論にならないように)
決めてください:

- role: このPointが記事の中で担う具体的な役割(例: 意外な詳細、方法論上の
  ニュアンス、歴史的な対比、心理的な理由。固定テンプレートではなく、この
  Ledgerに合わせて決めること)
- new_listener_takeaway: 聞き手がこのPointを聞いて新しく持ち帰る、具体的な
  理解・示唆・視点(Full Storyを聞いただけでは得られないもの)
- evidence_anchor: このPointの内容が、Verified Fact Ledgerのどの事実・
  データに基づくか
- why_it_matters: このPointが「だから何なのか」に対して与える具体的な答え
  (単なる一般的な留保・免責事項ではなく、聞き手にとっての意味)
- must_not_overlap_with_full_story: Full Storyで既に説明される意味のうち、
  このPointで繰り返してはいけない具体的な内容
- must_not_overlap_with_other_point: もう一方のPointが担う内容のうち、
  このPointで重複させてはいけない具体的な内容

【禁止(重要)】
以下のようなPointは、たとえPoint OneとPoint Twoの文字列が違っていても
価値が無いとみなされます。計画段階でこれらを避けてください:
- 研究上の限界・一般化上の注意・免責事項だけで構成されるPoint
- Full Storyの要約・言い換えに留まるPoint
- もう一方のPointの要約・言い換えになっているPoint
- 「だから何なのか」を説明できないPoint
- 他のどんな記事にもほぼそのまま流用できる一般論
- 新しい理解・解釈・意外性・具体的示唆のいずれも加えていないPoint

必要な留保・注意書き自体を書くこと自体は禁止されていませんが、それだけで
Point枠全体を使わないでください(留保は、新しい価値を含む内容に添える
補足として書いてください)。

【出力】
point_one/point_twoそれぞれについて、上記6項目を1〜2文の英語で簡潔に
記述してください(内部設計用であり、リスナーには見せません)。
"""


def run_point_role_planning_connected(client, topic: str, verified_ledger_text: str, model: str,
                                       reasoning_effort: str, point_role_hint_block: str = "") -> dict:
    """er011_point_role_value_planning_01.run_point_role_planning(124-145行)
    のコピー+改変。point_role_hint_block(既定"")が空の場合、生成される
    promptはproduction版ROLE_PLANNING_PROMPT_TEMPLATE.format(...)とバイト
    単位で完全同一になる(下記単体テストで確認)。JSON schema/developer
    message/model一致チェック/例外クラスはpoint_planningモジュールの
    ものをそのまま再利用し、コピーしていない。"""
    hint_section = f"{point_role_hint_block}\n\n" if point_role_hint_block else ""
    prompt = ROLE_PLANNING_PROMPT_TEMPLATE_CONNECTED.format(
        topic=topic, verified_ledger_text=verified_ledger_text, point_role_hint_block=hint_section)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **point_planning.ROLE_PLANNING_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": point_planning.ROLE_PLANNING_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    if response.model != model:
        raise point_planning.RolePlanningModelMismatchError(
            f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Point Role Planning応答が空です")
    parsed = json.loads(text)
    return {"parsed": parsed, "model": response.model, "response_id": response.id, "prompt": prompt}


# ============================================================
# run_one_pattern_connected: er003_v1_n3_01_articles_generate.py
# run_one_pattern()(818-1248行、431行、OPEN-141差分QA込みの現行版)の
# コピー。変更点はヘッダーコメント0節に記載の4点のみ(関数名変更、新規
# 引数追加、Point Role Planning呼び出し2箇所の置換、bareヘルパー参照への
# prod_gen.修飾)。この差分がそれ以外に無いことは、er011_point_role_
# planning_focus_connection_trial_04_test_01.pyのGate 4テストが実行毎に
# 機械的に再確認する。
# ============================================================
def run_one_pattern_connected(client, theme_id: str, label: str, prompt: str, verified_ledger_text: str,
                     topic: str, out_dir: str, apply_evidence_compression: bool = True,
                     apply_directional_fact_precheck: bool = True,
                     point_role_hint_block: str = "") -> dict:
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
    role_plan_result = run_point_role_planning_connected(
        client, topic, verified_ledger_text, model=writer_model, reasoning_effort=prod_gen.REASONING_EFFORT,
        point_role_hint_block=point_role_hint_block)
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
        diagnostic_prompt = prod_gen.build_diagnostic_retry_prompt(prompt, article_text, point_overlap_result)
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
        role_plan_result = run_point_role_planning_connected(
            client, topic, verified_ledger_text, model=writer_model, reasoning_effort=prod_gen.REASONING_EFFORT,
            point_role_hint_block=point_role_hint_block)
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
    # OPEN-146-LEDGER-CANONICAL-EN-SPELLING-PRODUCTION-WIRING-01:
    # Ledgerにcanonical_en_spelling行がある場合のみ、Fact Checkerへ
    # 「記事本文の固有名詞表記がLedger記載の公式英語表記と一致するか」の
    # 照合項目を追加する。無い場合は""でありprompt出力はbyte単位で不変。
    canonical_spelling_block = canon_spelling.build_canonical_spelling_fact_check_block(verified_ledger_text)
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [],
                                            canonical_spelling_block=canonical_spelling_block)

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
            # OPEN-141-TARGET-SENTENCE-DIFF-QA-PRODUCTION-WIRING-01(ユーザー
            # 正式判断2026-09-13): target-sentence-matchingを既定ONへ切替。
            r = local_rewrite.rewrite_ng_item(client, ledger_model, prod_gen.REASONING_EFFORT,
                                               verified_ledger_text, point_context, target,
                                               deviation, before_ctx, after_ctx, _run_check_window,
                                               use_target_sentence_matching=True)
            # 同上ユーザー判断: Local Rewrite受理直後に差分QA案I(Fact Checker
            # A'再実行+Ledger Deviation Checker再確認)を実行する。FAIL相当の
            # みresolvedをFalseへ反転させ、既存human_review_requiredの流れへ
            # 合流させる(新規機構は作らない)。Fact Checker A'のmodelは
            # 既存Production呼び出し元(本ファイルL997)と同一のrouting
            # ("WRITER_FACT_CHECK")で解決する。
            diff_qa_fact_checker_model = routing.require_model(
                "WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL)
            r = local_rewrite.apply_diff_qa_to_resolved_rewrite(
                r, client, topic, before_ctx, after_ctx, verified_ledger_text, ledger_model,
                diff_qa_fact_checker_model)
            # Point Overlap rule-based再計算(¥0、LLM再呼び出しなし)。対象文が
            # Point One/Two本文に属する場合のみ記録(non-blocking、記録のみ)。
            sections_for_overlap = prod_gen.split_common_sections_for_point_qa(article_text)
            r["diff_qa_point_overlap"] = overlap_qa.recompute_point_overlap_for_target_sentence(
                sections_for_overlap, target, replacement_text=r.get("final_text"))
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


if __name__ == "__main__":
    print("このファイルは関数定義のみを提供します。単体テストは"
          "er011_point_role_planning_focus_connection_trial_04_test_01.pyを、"
          "runtime実行はer011_discovery_focus_role_planning_connection_trial_01_run.pyを"
          "使用してください。")
