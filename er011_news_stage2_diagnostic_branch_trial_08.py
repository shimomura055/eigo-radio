# ============================================================
# er011_news_stage2_diagnostic_branch_trial_08.py
# FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08 (Lane A, Part A)
# ============================================================
# 目的(ユーザー決定 2026-09-09、N-1=(a)): value QA単独NG時に無条件構築
# されるoverlap診断文(er003_v1_n3_01_articles_generate.build_diagnostic_
# retry_prompt -> er009_diagnostic_full_retry_modules_12.pyのoverlap断定文)
# を、lexical_flagged/value_qa_flaggedのflag状態に応じて構築する条件分岐
# へ差し替えた場合の効果を、**Trial harness内**で検証する。
#
# 条件分岐は「診断文の精度是正」であり、判定ロジック(still_flagged =
# lexical_flagged or value_qa_flagged)・閾値(0.40)・Loop Budget
# (POINT_OVERLAP_ARTICLE_RETRY_MAX=2)・Prompt原則(Storytelling First/No
# Jargon等)は一切変更しない。Production/Prompt/共有module/SSOT編集・Git
# 操作は行わない。monkeypatch・グローバル書き換えは行わない。TTSは実行
# しない(text-onlyまで)。
#
# ------------------------------------------------------------
# 0. Reconciliation再確認(作業1)
# ------------------------------------------------------------
# `FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01_REPORT.md` (c) の
# 引用:「ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14の原設計は『lexical
# overlap flagのみをトリガー』としていた(value QAは未存在)。その後
# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01がvalue QAを追加した際の記録
# (DECISION_LOG.md該当エントリ)には『上記3つをstill_flagged =
# lexical_flagged or value_qa_flaggedとして既存のDiagnostic Full Retry
# ループへ統合し、retry時はvalue QA NGの理由を既存の診断section直後に
# 追加する』と明記されている。すなわち設計意図は『overlap診断sectionは
# 基盤として維持し、value QA理由を追加する』という加算的設計であり、
# コードの挙動(overlap診断section無条件構築+value QA診断メモ条件付き
# 追加)と一致する。Reconciliation判定: 基本構造は『仕様どおり』
# (実装漏れではない)。ただし、value単独NG(lexical flagged=Falseが2点
# とも)の場合にテンプレート冒頭の断定文が事実と異なる内容をWriterへ
# 提示するという具体的な文言精度の問題は、ER-011-NO18の設計記録に明示的
# な検討の痕跡がない。この文言精度の問題自体は『不明(未検討)』と判定
# する」。
#
# 本Trialはこの「不明(未検討)」だった文言精度問題**だけ**を対象とする。
# still_flaggedのOR判定・閾値0.40・Loop Budget 2・Point Role Planningの
# 毎回再計画・Prompt原則はいずれも不変(下記diff_from_t3_g1_freshness_
# checkで機械確認する)。
#
# ------------------------------------------------------------
# 1. 再利用(import・無変更) / コピー・改変の内訳(Gate 4)
# ------------------------------------------------------------
# 【再利用(import・無変更)】
#   - er003_v1_n3_01_articles_generate (prod_gen): build_common_block /
#     build_prompt / build_diagnostic_retry_prompt / compute_metrics /
#     split_common_sections_for_point_qa / run_point_overlap_qa_and_
#     regenerate / _generate_and_compress_article / _writer_process /
#     REASONING_EFFORT / POINT_OVERLAP_ARTICLE_RETRY_MAX / POINT_TARGET_*
#     / POINT_TOLERANCE_* / TOTAL_SOFT_* / normalize_article_formatting。
#     無変更。
#   - er011_point_role_planning_focus_connection_trial_03 (t3、既存
#     VALIDATEDトライアル): run_point_role_planning_connected /
#     MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK /
#     MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK / load_text /
#     HANSHIN_LEDGER_PATH / HANSHIN_TOPIC_JA / vfl01 / ab01 / r3 /
#     routing / dfp / sf1r1 / local_rewrite / point_planning をそのまま
#     importする(再改変・再コピーはしない、t3経由でモジュール参照を得る
#     ことで二重import・バージョンずれを避ける)。
#   - er011_daily_news_focus_layer_comparison_trial_04 (t4): analyze_run
#     をそのまま再利用する(word count / overlap ratio / fact / ledger /
#     role原文抽出。役割分類ヒューリスティック[classify_role_text /
#     body_embodies_role]自体は本Trialの判定には使わない、ユーザー決定
#     D-2(a)方針=Point本文原文で見る、に基づく。analyze_runの返り値の
#     うち*_role_categoryフィールドは参考記録として残すのみで判定根拠
#     にしない)。
#   - er011_daily_news_focus_layer_comparison_trial_02 (t2):
#     MAJOR_DAILY_GATE_CHECKLIST をそのまま再利用する。
#   - er005_cost_logger (cl): install / logging_context。無変更。
#
# 【コピー・改変(Trial限定)】
#   - run_one_pattern_diagnostic_branch: t3.run_one_pattern_connected の
#     コピー(t3自体がer003_v1_n3_01_articles_generate.run_one_patternの
#     コピーであることは既にt3のGate 4根拠として確認済み)。変更点は以下
#     3点のみ:
#       (i) 関数名 run_one_pattern_connected ->
#           run_one_pattern_diagnostic_branch
#       (ii) diagnostic_prompt構築部分(t3の383-386行相当)を、
#           lexical_flagged=Trueの時だけ prod_gen.build_diagnostic_retry_
#           prompt(...)を呼ぶ(=overlap断定文+shared_words+前回Point本文
#           を含む既存テンプレートをそのまま使う)、Falseの時は
#           diagnostic_prompt = prompt(overlap診断section自体を構築しない)
#           という条件分岐へ差し替え。value_qa_flaggedによる
#           build_value_qa_diagnostic_note追加は無条件分岐のまま不変
#           (両方Trueなら両方含まれる)。新しい文言・新しいテンプレートは
#           一切作成していない(既存テンプレートの呼び出し可否を分岐した
#           だけ)。
#       (iii) 検証用に、各retry attemptで実際に使われたdiagnostic_prompt
#           全文をaudit/diagnostic_prompt_retry{N}.txtへ保存する処理を
#           追加(既存にはなかった、生成ロジック自体には影響しない追加の
#           監査ログ出力のみ)。log_entryへ
#           "diagnostic_construction_mode"フィールド
#           ("full_diagnostic_lexical_flagged" /
#           "overlap_section_skipped_value_only" /
#           "full_diagnostic_both_flagged")も追加する(記録用、ロジックに
#           影響しない)。
#     上記以外(still_flaggedのOR判定、Loop Budget、Point Role Planningの
#     毎回再計画、Fact Checker/Ledger Deviation/Local Rewrite/Directional
#     Fact Precheckの呼び出し順序・条件、print文、出力ファイル名)は一切
#     変更していない。下記gate4_diff_check()で t3.run_one_pattern_
#     connected とのunified diffを機械記録する。
#
# monkeypatch・グローバル書き換えは一切行っていない。
#
# ------------------------------------------------------------
# 2. 条件設計
# ------------------------------------------------------------
# 全条件は Focus Module + Point Role hint(Trial-06 focus_hint、現行最良
# 組み合わせ)に固定する。診断構築方式のみを2水準で比較する:
#   - "current_diagnostic": 無条件構築(現行Production挙動)。**新規生成
#     しない**。既存 er011_output/news_focus_hint_comparison_trial_06/
#     {a2,b1b}/focus_hint/run{1,2,3}/ の成果物(同一Hanshin Ledger・同一
#     harness・同一focus_hint条件)をそのまま再利用する(理由: 委任文
#     「Trial-06のfocus_hint 6本は『現行診断』条件として再利用可(同一
#     harness・同一Ledgerなら再生成せず)」に基づく。再利用の妥当性:
#     (1) 同一Hanshin Ledger・同一Focus Module・同一hint文言・同一G1修正
#     済みProduction関数、(2) run_one_pattern_connectedはdiagnostic_prompt
#     を無条件構築する経路であり本Trialの"branch_diagnostic"との唯一の
#     差分がまさにdiagnostic構築の条件分岐であるため、対照条件として
#     直接比較可能)。
#   - "branch_diagnostic": 条件分岐構築(本Trial新規実装)。新規6本
#     (A2×3, B1B×3)を生成する。
#
# 費用上限: ¥120(超過見込みならSTOP、Trial-06の focus_hint 6本実績
# ¥41.7を参考に見積る)。冒頭で必ずcl.install()を有効化する。
# ============================================================
from __future__ import annotations

import inspect
import difflib
import json
import os
import time

import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er011_daily_news_focus_layer_comparison_trial_02 as t2
import er011_daily_news_focus_layer_comparison_trial_04 as t4
import er011_point_role_planning_focus_connection_trial_03 as t3
import er011_point_role_value_planning_01 as point_planning

r3 = t3.r3
routing = t3.routing
dfp = t3.dfp
sf1r1 = t3.sf1r1
local_rewrite = t3.local_rewrite
vfl01 = t3.vfl01
ab01 = t3.ab01

THEME_ID = "news_stage2_diagnostic_branch_trial_08"
OUT_DIR = f"er011_output/{THEME_ID}"
PARTA_DIR = f"{OUT_DIR}/parta"

N_RUNS = 3
BUDGET_JPY = 120.0

CURRENT_DIAGNOSTIC_SOURCE_DIR = "er011_output/news_focus_hint_comparison_trial_06"

CONDITION = {
    "editorial_type_module_block": t3.MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK,
    "point_role_hint_block": t3.MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK,
}

LEVELS = t4.LEVELS  # [(label, instruction, level_dir, stage_tag), ...] Trial-04/06と完全同一


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# Gate 4: t3.run_one_pattern_connected との unified diff を機械記録する
# (差分が上記ヘッダー記載の3点由来のものだけであることの支援的確認)。
# ============================================================
def gate4_diff_check() -> dict:
    t3_src = inspect.getsource(t3.run_one_pattern_connected)
    branch_src = inspect.getsource(run_one_pattern_diagnostic_branch)
    diff_lines = list(difflib.unified_diff(
        t3_src.splitlines(), branch_src.splitlines(),
        fromfile="t3.run_one_pattern_connected", tofile="run_one_pattern_diagnostic_branch", lineterm=""))
    calls_prod_fn_directly = "prod_gen.build_diagnostic_retry_prompt(" in branch_src
    still_flagged_unchanged = "still_flagged = lexical_flagged or value_qa_flagged" in branch_src
    loop_budget_unchanged = "prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX" in branch_src
    role_replan_unchanged = branch_src.count("run_point_role_planning_connected(") == 2
    conclusion = "PASS" if (calls_prod_fn_directly and still_flagged_unchanged
                             and loop_budget_unchanged and role_replan_unchanged) else "FAIL_NEEDS_REVIEW"
    result = {
        "diff_line_count": len(diff_lines),
        "calls_prod_gen_build_diagnostic_retry_prompt_directly": calls_prod_fn_directly,
        "still_flagged_or_judgement_unchanged": still_flagged_unchanged,
        "loop_budget_reference_unchanged": loop_budget_unchanged,
        "role_replanning_called_twice_unchanged": role_replan_unchanged,
        "conclusion": conclusion,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/gate4_diff_check.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/gate4_diff_from_t3.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(diff_lines))
    print(f"[{THEME_ID}] gate4_diff_check: {result['conclusion']} (diff_line_count={len(diff_lines)})")
    if conclusion != "PASS":
        raise RuntimeError(f"Gate 4 diff確認失敗: {result}")
    return result


# ============================================================
# run_one_pattern_diagnostic_branch: t3.run_one_pattern_connected の
# コピー+改変(変更点はヘッダーコメント1節の(i)〜(iii)のみ)。
# ============================================================
def run_one_pattern_diagnostic_branch(client, theme_id: str, label: str, prompt: str,
                                       verified_ledger_text: str, topic: str, out_dir: str,
                                       apply_evidence_compression: bool = True,
                                       apply_directional_fact_precheck: bool = True,
                                       point_role_hint_block: str = "") -> dict:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    writer_model = routing.require_model(prod_gen._writer_process(label), routing.WRITER_MODEL)

    role_plan_result = t3.run_point_role_planning_connected(
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

        point_overlap_result = {
            "point_one": overlap_report["point_one"]["before_overlap"],
            "point_two": overlap_report["point_two"]["before_overlap"],
        }

        # ---- (ii) N-1=(a) 条件分岐: lexical_flaggedがTrueの時だけoverlap
        # 診断section(既存テンプレート、断定文+shared_words+前回Point本文
        # を含む)を構築する。Falseの場合(value単独NG)はoverlap診断section
        # 自体を構築せず、diagnostic_promptは元のpromptのまま。文言・
        # テンプレート自体は無変更(既存build_diagnostic_retry_promptの
        # 呼び出し可否のみを分岐)。----
        if lexical_flagged:
            diagnostic_prompt = prod_gen.build_diagnostic_retry_prompt(prompt, article_text, point_overlap_result)
            diagnostic_mode = "full_diagnostic_both_flagged" if value_qa_flagged else "full_diagnostic_lexical_flagged"
        else:
            diagnostic_prompt = prompt
            diagnostic_mode = "overlap_section_skipped_value_only"
        if value_qa_flagged:
            diagnostic_prompt = diagnostic_prompt + "\n\n" + point_planning.build_value_qa_diagnostic_note(
                value_qa_result)
        log_entry["diagnostic_construction_mode"] = diagnostic_mode
        log_entry["diagnostic_used"] = {
            "point_one_score": point_overlap_result["point_one"]["overlap_ratio"],
            "point_one_flagged": point_overlap_result["point_one"]["flagged"],
            "point_two_score": point_overlap_result["point_two"]["overlap_ratio"],
            "point_two_flagged": point_overlap_result["point_two"]["flagged"],
            "point_one_vs_point_two_flagged": overlap_report.get("point_one_vs_point_two", {}).get("flagged"),
            "value_qa_flagged": value_qa_flagged,
        }

        role_plan_result = t3.run_point_role_planning_connected(
            client, topic, verified_ledger_text, model=writer_model, reasoning_effort=prod_gen.REASONING_EFFORT,
            point_role_hint_block=point_role_hint_block)
        with open(f"{out_dir}/audit/point_role_planning_retry{retry_attempt}.json", "w",
                  encoding="utf-8") as f:
            json.dump(role_plan_result, f, ensure_ascii=False, indent=2, default=str)
        diagnostic_prompt = diagnostic_prompt + "\n" + point_planning.build_role_planning_block(
            role_plan_result["parsed"])

        # ---- (iii) 検証用: 実際にWriterへ渡されたdiagnostic_prompt全文を
        # 保存する(既存にはなかった追加の監査ログのみ、生成ロジックへの
        # 影響なし)。----
        with open(f"{out_dir}/audit/diagnostic_prompt_retry{retry_attempt}.txt", "w", encoding="utf-8") as f:
            f.write(diagnostic_prompt)

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

    point_overlap_qa_applied = False
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
        article_text = prod_gen.normalize_article_formatting(article_text)

        with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(article_text)

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
# 費用実測(Trial-06と同一ロジック、この専用ログパス向けに再実装)。
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
    total_usd = sum(r["_cost_usd"] for r in records)
    result = {
        "usd_jpy_rate": USD_JPY,
        "methodology": "全て実測usage(actual)。単価はer005_output/cost_baseline_01/"
                       "pricing_snapshot.json(OFFICIAL_SOURCE、Trial-06 cost_computeと同一"
                       "参照元・同一ロジック)。branch_diagnostic条件の新規生成分のみ課金対象"
                       "(current_diagnostic条件はTrial-06既存成果物の再利用のため追加課金なし)。",
        "total_usd": round(total_usd, 4),
        "total_jpy": round(total_usd * USD_JPY, 1),
        "total_calls": len(records),
    }
    with open(f"{OUT_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def build_run_metadata() -> dict:
    return {
        "management_id": "FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08",
        "mode_supply_path": "A3-UDR-2=(i)踏襲: 手動Mode判定+手動Ledger供給(Trend Synthesisと"
                            "同じ機構)。",
        "major_daily_gate_checklist_source": "er011_daily_news_focus_layer_comparison_trial_02"
                                              ".MAJOR_DAILY_GATE_CHECKLIST(再確認、再判定なし)",
        "major_daily_gate_checklist": t2.MAJOR_DAILY_GATE_CHECKLIST,
        "editorial_mode_determination": "MAJOR_DAILY(既存Trial-02/06の手動判定を再利用、本Trialで"
                                          "新規判定は行っていない)。",
    }


def run_one_combo_branch(client, master_full_text: str, verified_ledger_text: str,
                          run_idx: int, label: str, instruction: str, level_dir: str, stage_tag: str) -> dict:
    out_dir = f"{PARTA_DIR}/{level_dir}/branch_diagnostic/run{run_idx}"
    common_block = prod_gen.build_common_block(
        master_full_text, t3.HANSHIN_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=CONDITION["editorial_type_module_block"])
    prompt = prod_gen.build_prompt(common_block, instruction)
    theme_tag = f"{THEME_ID}_branch_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, stage_tag):
        result = run_one_pattern_diagnostic_branch(
            client, theme_tag, label, prompt, verified_ledger_text, t3.HANSHIN_TOPIC_JA, out_dir,
            point_role_hint_block=CONDITION["point_role_hint_block"])
    elapsed = round(time.time() - t0, 2)
    analysis = t4.analyze_run(out_dir, result)
    analysis["elapsed_seconds"] = elapsed
    analysis["condition"] = "branch_diagnostic"
    analysis["level"] = label
    analysis["run"] = run_idx
    with open(f"{out_dir}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in result.items() if k != "article_text"}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] run{run_idx} branch_diagnostic {label}: status={result.get('status')} "
          f"retry={analysis['retry_attempts']} p1_overlap={analysis['point_one_overlap_ratio']} "
          f"p2_overlap={analysis['point_two_overlap_ratio']} elapsed={elapsed}s")
    return analysis


LABEL_LOOKUP = {label: (label, instruction, level_dir, stage_tag)
                for (label, instruction, level_dir, stage_tag) in LEVELS}
COMBO_RESULTS_DIR = f"{PARTA_DIR}/_combo_results"


def setup_stage() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(PARTA_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    gate4_result = gate4_diff_check()
    unit_test_result = t3.test_default_hint_is_byte_identical_to_production()
    if unit_test_result["status"] != "PASS":
        raise RuntimeError(f"既定値バイト一致テスト失敗: {unit_test_result}")
    run_metadata = build_run_metadata()
    with open(f"{OUT_DIR}/run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(run_metadata, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] setup_stage完了: gate4={gate4_result['conclusion']}, "
          f"unit_test={unit_test_result['status']}")
    return {"gate4_result": gate4_result, "unit_test_result": unit_test_result, "run_metadata": run_metadata}


def combo_stage(label: str, run_idx: int) -> dict:
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    verified_ledger_text = load_text(t3.HANSHIN_LEDGER_PATH)
    _, instruction, level_dir, stage_tag = LABEL_LOOKUP[label]
    analysis = run_one_combo_branch(client, master_full_text, verified_ledger_text,
                                     run_idx, label, instruction, level_dir, stage_tag)
    os.makedirs(COMBO_RESULTS_DIR, exist_ok=True)
    with open(f"{COMBO_RESULTS_DIR}/branch_{level_dir}_run{run_idx}.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    return analysis


def cost_stage() -> dict:
    result = write_cost_summary()
    print(f"[{THEME_ID}] 費用実測合計(branch_diagnostic新規生成分のみ): ¥{result['total_jpy']}")
    return result


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "setup"
    if which == "setup":
        setup_stage()
    elif which == "combo":
        # 例: python er011_news_stage2_diagnostic_branch_trial_08.py combo A2 1
        label, run_idx = sys.argv[2], int(sys.argv[3])
        combo_stage(label, run_idx)
    elif which == "cost":
        cost_stage()
    else:
        print("usage: python er011_news_stage2_diagnostic_branch_trial_08.py "
              "[setup|combo <A2|B1B> <run_idx>|cost]")
