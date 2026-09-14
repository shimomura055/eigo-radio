# ============================================================
# er014_output/four_type_observation_01/discovery/run_discovery_complete_3.py
# 管理ID: EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE(継続CONT2)
#
# 目的(既存仕様内の個別修正でDiscovery A2/B1B/Key Phraseを完成させる。
# 新Production仕様Trialではない):
#  (1) A2記事全体final QA(Fact Checker A' + Ledger Deviation Checker +
#      Directional Fact Precheck)を、CONT1のF002 operator修正後の最終
#      本文に対して初めて再実行する(CONT1はbudget STOPで未実行だった)。
#      FAILの場合は既存fix_fact_blocks()パターンで最大1回だけ限定修正し
#      再QA、それでもFAILならSTOP(新Validator/QAは追加しない)。
#  (2) Key Phrase A2: 既存keywords_canonicalized.jsonの5件のsource_
#      sentenceが最終A2本文にそのまま存在するかをローカル文字列照合のみで
#      確認する(API不要)。1件でも不在ならrun_key_phrases()を1回だけ
#      再実行する。
#  (3) Key Phrase B1B: 最終b1b/article.mdに対し既存正式入口run_key_
#      phrases()を実行する(旧3回は旧本文に対するものであり、本文が変わった
#      ため無効。これは確定canonical本文への正規の初回生成として扱う)。
#      構造不合格ならもう1回だけ再呼び出し(合計最大2回)。出力は事故防止の
#      ためkey_phrases/b1b_final/へ書き、成功時のみkey_phrases/b1b/へ
#      同期コピーし旧結果をkey_phrases/b1b_old_attempts/へ退避する。
#  (4) jargon scan最終確認・Cross-Level Consistency突合(最終テキスト、
#      F002 video watchersマーカーのF012への誤ヒットを解消)。
#  (5) production_set_cost.json更新。
#
# 費用上限: BUDGET_JPY=70円(本タスクの新規API call分のみ)。段階ごとに、
# 現在までの実測増分 + 次段階の見込みコストを事前に合算してBUDGET_JPYと
# 比較し、超過が見込まれる場合はその段階を開始せずBudgetStopで正常
# finalizeする(run_discovery_complete_2.pyと同じパターン)。
# ============================================================
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 前回driver(同一ディレクトリ)。fix_fact_blocks・run_final_qa・
# jargon_scan・cost logging・Key Phrase呼び出しをそのまま再利用する
# (`if __name__ == "__main__"`ガードがあるためimportしてもmain()は実行
# されない)。complete_2の`base`属性=run_discovery_complete、
# `prev_driver`属性=run_discovery_fix_b1b_kp(run_final_qa/jargon_scan/
# cost系の実体が定義されているモジュール)。
import run_discovery_complete_2 as complete2

base = complete2.base                # run_discovery_complete
prev_driver = complete2.prev_driver  # run_discovery_fix_b1b_kp

THEME_ID = complete2.THEME_ID
BASE_DIR = complete2.BASE_DIR
RESEARCH_DIR = complete2.RESEARCH_DIR
LOG_PATH = complete2.LOG_PATH
TOPIC_EN = complete2.TOPIC_EN

BUDGET_JPY = 70.0

STAGE_ESTIMATE_JPY = {
    "a2_final_qa_recheck": 30.0,
    "a2_limited_fix_retry": 15.0,
    "a2_final_qa_recheck_retry": 30.0,
    "key_phrase_a2_rerun": 5.0,
    "key_phrase_b1b_call1": 5.0,
    "key_phrase_b1b_call2": 5.0,
}


class BudgetStop(Exception):
    def __init__(self, stage, incremental, estimate):
        self.stage = stage
        self.incremental = incremental
        self.estimate = estimate
        super().__init__(
            f"budget guard: stage={stage} incremental_so_far=¥{incremental:.2f} "
            f"+ estimate=¥{estimate:.2f} > budget=¥{BUDGET_JPY:.2f}")


# ============================================================
# Cross-Level Consistency(最終テキスト再生成、F002 video watchersの
# F012誤ヒット副作用を解消。API呼び出しなし、決定的チェック。既存
# NUMERIC_MARKERS/残存表現チェックはbaseからそのまま再利用し、F002 video
# watchers行だけ文脈を見て誤ヒットを避けるロジックへ差し替える)
# ============================================================
def build_cross_level_consistency_md_v3(a2_text: str, b1b_text: str):
    lines = ["# Cross-Level Consistency: A2 vs B1B (Discovery, post fact-fix, CONT2 final)\n",
             "| Marker | A2 | B1B | Consistent? |",
             "|---|---|---|---|"]
    all_consistent = True
    notes = []
    for label, patterns in base.NUMERIC_MARKERS:
        if label == "F002 video watchers":
            def _hit(text: str) -> bool:
                for m in re.finditer(r"\b37\b", text):
                    window = text[max(0, m.start() - 20):m.end() + 20].lower()
                    if "stud" in window:  # 'studies'/'study' (F012)を除外
                        continue
                    return True
                return False
            a2_hit = _hit(a2_text)
            b1b_hit = _hit(b1b_text)
            notes.append(
                "F002 video watchers: 単純な部分一致'37'はF012('review of 37 studies')へ誤ヒットする"
                "(CONT1のoperator修正でF002の視聴者数は本文から削除済みのため)。このため'37'の直近"
                "20文字に'stud'(study/studies)を含む場合は除外し、それ以外の独立した'37'のみを"
                "hitとする。A2/B1Bとも現在は視聴者の具体的人数を明記していないため、この行は"
                "'no/no'になる想定。")
        else:
            a2_hit = any(p in a2_text for p in patterns)
            b1b_hit = any(p in b1b_text for p in patterns)
        note = "present in both" if (a2_hit and b1b_hit) else (
            "present in A2 only" if a2_hit else ("present in B1B only" if b1b_hit else "absent in both"))
        lines.append(f"| {label} | {'yes' if a2_hit else 'no'} | {'yes' if b1b_hit else 'no'} | {note} |")

    residual_issues = []
    for label, text in (("A2", a2_text), ("B1B", b1b_text)):
        if re.search(r"\b(60|Sixty)\s+(students|participants)\s+watched", text, re.IGNORECASE):
            residual_issues.append(f"{label}: unfixed '60/Sixty students watched' phrasing still present")
            all_consistent = False
        if re.search(r"\b46\s+students\b", text) and "about 46" not in text.lower() and \
                "roughly 46" not in text.lower() and "approximately 46" not in text.lower():
            residual_issues.append(f"{label}: unhedged '46 students' phrasing still present")
            all_consistent = False

    lines.append("")
    lines.append(f"Overall consistent (no direct numeric contradiction detected): {all_consistent}")
    if residual_issues:
        lines.append("\nResidual issues:")
        for issue in residual_issues:
            lines.append(f"- {issue}")
    lines.append("\nNotes:")
    for n in notes:
        lines.append(f"- {n}")
    lines.append(
        "\nAll quotations/markers in this table are derived directly from the final canonical files "
        "`a2/article.md` and `b1b/article.md` as of this task "
        "(EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE, CONT2).")
    return "\n".join(lines) + "\n", all_consistent


def main():
    prev_driver.cl.install(LOG_PATH)
    with open(LOG_PATH, encoding="utf-8") as f:
        baseline_lines = f.readlines()
    baseline_line_count = len(baseline_lines)
    baseline_cost_jpy = prev_driver._lines_cost_jpy(baseline_lines)
    print(f"[{THEME_ID}][COMPLETE3] baseline(前タスク分含む)line_count={baseline_line_count} "
          f"baseline_cost_jpy=¥{baseline_cost_jpy:.2f}(このタスクの予算計算からは除外)")

    def incremental_jpy() -> float:
        return prev_driver.cost_total_jpy() - baseline_cost_jpy

    def ensure_budget(stage: str):
        inc = incremental_jpy()
        est = STAGE_ESTIMATE_JPY.get(stage, 15.0)
        if inc + est > BUDGET_JPY:
            raise BudgetStop(stage, inc, est)
        print(f"[{THEME_ID}][COMPLETE3] budget check OK stage={stage} incremental_so_far=¥{inc:.2f} "
              f"+ estimate=¥{est:.2f} <= budget=¥{BUDGET_JPY:.2f}")

    started_at = datetime.now(timezone.utc).isoformat()
    client = prev_driver.vfl01.get_client()

    result = {"started_at": started_at, "budget_jpy": BUDGET_JPY,
              "baseline_cost_jpy": round(baseline_cost_jpy, 2), "stop_reason": None}
    rewrite_log_lines = ["\n# Discovery Complete 3 (CONT2: A2 final QA + Key Phrase A2/B1B completion) - addendum\n"]

    stopped_stage = None
    try:
        with open(f"{RESEARCH_DIR}/verified_fact_ledger.txt", encoding="utf-8") as f:
            verified_ledger_text = f.read()
        vfl_path = f"{RESEARCH_DIR}/stage_b3_vfl.json"

        with open(f"{BASE_DIR}/a2/article.md", encoding="utf-8") as f:
            a2_text = f.read()
        with open(f"{BASE_DIR}/b1b/article.md", encoding="utf-8") as f:
            b1b_text = f.read()
        with open(f"{BASE_DIR}/reader_facing_article.txt", encoding="utf-8") as f:
            a2_reader_text = f.read()
        with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", encoding="utf-8") as f:
            b1b_reader_text = f.read()

        result["a2_sync_before_task"] = (a2_text == a2_reader_text)
        result["b1b_sync_before_task"] = (b1b_text == b1b_reader_text)
        print(f"[{THEME_ID}][COMPLETE3] sync check(before task): a2={result['a2_sync_before_task']} "
              f"b1b={result['b1b_sync_before_task']}")

        ledger_model_a2 = prev_driver.routing.require_model("A2_WRITER", prev_driver.routing.WRITER_MODEL)
        fact_checker_model = prev_driver.routing.require_model(
            "WRITER_FACT_CHECK", prev_driver.routing.WRITER_FACT_CHECK_MODEL)

        # ============================================================
        # (1) A2記事全体final QA再実行
        # ============================================================
        stopped_stage = "a2_final_qa_recheck"
        ensure_budget("a2_final_qa_recheck")
        os.makedirs(f"{BASE_DIR}/a2/audit", exist_ok=True)
        if os.path.exists(f"{BASE_DIR}/a2/audit/post_fix_fact_qa.json"):
            shutil.copy2(f"{BASE_DIR}/a2/audit/post_fix_fact_qa.json",
                         f"{BASE_DIR}/a2/audit/post_fix_fact_qa_before_complete3_fix.json")
        if os.path.exists(f"{BASE_DIR}/a2/audit/post_fix_ledger_deviation.json"):
            shutil.copy2(f"{BASE_DIR}/a2/audit/post_fix_ledger_deviation.json",
                         f"{BASE_DIR}/a2/audit/post_fix_ledger_deviation_before_complete3_fix.json")
        if os.path.exists(f"{BASE_DIR}/a2/audit/post_fix_directional_fact_precheck.json"):
            shutil.copy2(f"{BASE_DIR}/a2/audit/post_fix_directional_fact_precheck.json",
                         f"{BASE_DIR}/a2/audit/post_fix_directional_fact_precheck_before_complete3_fix.json")

        a2_final_qa = prev_driver.run_final_qa(a2_text, verified_ledger_text, ledger_model_a2, TOPIC_EN,
                                                f"{BASE_DIR}/a2", vfl_path, client, "a2_complete3")
        print(f"[{THEME_ID}][COMPLETE3] A2 final QA(recheck): {a2_final_qa}")
        result["a2_final_qa_recheck"] = a2_final_qa
        result["a2_final_qa_limited_fix_applied"] = False

        if a2_final_qa["fact_checker_verdict"] == "FAIL":
            # 限定修正(最大1回): post_fix_fact_qa.jsonのcontradictions/
            # unsupported_specific_claimsを確認し、Ledger整合の範囲で
            # 直せる場合のみfix_fact_blocks経路で1回だけ再QAする。ここでは
            # 事前に具体的な指摘内容が不明なため、まずFAIL理由を記録し、
            # Ledgerだけでは機械的に解消できない場合はSTOPする(新規
            # Validator/QAや黙示的なfact改変は行わない)。
            with open(f"{BASE_DIR}/a2/audit/post_fix_fact_qa.json", encoding="utf-8") as f:
                a2_fc_detail = json.load(f)
            result["a2_final_qa_fail_detail"] = a2_fc_detail.get("result")
            raise RuntimeError(
                "STOP: A2 final Fact Checker verdict is FAIL. Detail saved to "
                "a2/audit/post_fix_fact_qa.json (result field). This task does not have a "
                "pre-authorized automatic rewrite mapping for this FAIL; per STOP conditions, treating "
                "as a human-judgment-only quality issue unless the flagged sentence is unambiguously the "
                "same class as prior operator-escalated fixes (not detected automatically here).")

        # ============================================================
        # (2) Key Phrase A2: 最終本文との整合確認(API不要)
        # ============================================================
        stopped_stage = "key_phrase_a2_local_check"
        with open(f"{BASE_DIR}/key_phrases/a2/keywords_canonicalized.json", encoding="utf-8") as f:
            kp_a2_canonical = json.load(f)
        kp_a2_check = []
        kp_a2_all_present = True
        for item in kp_a2_canonical["items"]:
            src_sentence = item.get("source_sentence", "")
            present = src_sentence in a2_text
            kp_a2_all_present = kp_a2_all_present and present
            kp_a2_check.append({"rank": item["rank"], "key_phrase": item["key_phrase"],
                                 "japanese_gloss": item["japanese_gloss"],
                                 "source_sentence": src_sentence, "present_in_final_a2": present})
        result["key_phrase_a2_local_check"] = kp_a2_check
        result["key_phrase_a2_all_present"] = kp_a2_all_present
        result["key_phrase_a2_rerun"] = False
        print(f"[{THEME_ID}][COMPLETE3] Key Phrase A2 local check: all_present={kp_a2_all_present}")

        if not kp_a2_all_present:
            stopped_stage = "key_phrase_a2_rerun"
            ensure_budget("key_phrase_a2_rerun")
            if os.path.isdir(f"{BASE_DIR}/key_phrases/a2") and not os.path.isdir(f"{BASE_DIR}/key_phrases/a2_old"):
                shutil.copytree(f"{BASE_DIR}/key_phrases/a2", f"{BASE_DIR}/key_phrases/a2_old")
            kp_a2_new = prev_driver.scaffold_gen.run_key_phrases(
                a2_text, f"{BASE_DIR}/key_phrases/a2", f"{THEME_ID}_a2_complete3",
                "A2(V2改1, N3-01, fact-fix complete3)", process="A2_SUPPORT")
            kp_a2_new_status = (kp_a2_new["canonicalization"] or {}).get("status") \
                if kp_a2_new["canonicalization"] else kp_a2_new["selection"]["status"]
            result["key_phrase_a2_rerun"] = True
            result["key_phrase_a2_rerun_status"] = kp_a2_new_status
            print(f"[{THEME_ID}][COMPLETE3] Key Phrase A2 rerun status={kp_a2_new_status}")

        # ============================================================
        # (3) Key Phrase B1B: 確定canonical本文への正規の初回生成(最大2回)
        # ============================================================
        kp_dir_b1b_final = f"{BASE_DIR}/key_phrases/b1b_final"
        os.makedirs(kp_dir_b1b_final, exist_ok=True)

        def _line_count() -> int:
            with open(LOG_PATH, encoding="utf-8") as f:
                return len(f.readlines())

        kp_b1b_attempts = []
        kp_b1b_final_status = None
        kp_b1b_last_result = None
        for call_no in (1, 2):
            stage_key = f"key_phrase_b1b_call{call_no}"
            stopped_stage = stage_key
            ensure_budget(stage_key)
            start_line = _line_count()
            kp_b1b = prev_driver.scaffold_gen.run_key_phrases(
                b1b_text, kp_dir_b1b_final, f"{THEME_ID}_b1b_complete3_call{call_no}",
                "B1-B(N3-01, fact-fix complete3, canonical final text)", process="B1_SUPPORT")
            end_line = _line_count()
            status = (kp_b1b["canonicalization"] or {}).get("status") \
                if kp_b1b["canonicalization"] else kp_b1b["selection"]["status"]
            with open(LOG_PATH, encoding="utf-8") as f:
                _lines_for_cost = f.readlines()
            call_cost = round(prev_driver._lines_cost_jpy(_lines_for_cost[start_line:end_line]), 2)
            sel_items = kp_b1b["selection"].get("original_items") if kp_b1b.get("selection") else None
            item_reasons = None
            if kp_b1b["selection"] and kp_b1b["selection"].get("status") != "KEY_WORDS_STRUCTURE_PASS":
                item_reasons = kp_b1b["selection"]
            kp_b1b_attempts.append({
                "call": call_no, "status": status, "cost_jpy": call_cost,
                "selection_status": kp_b1b["selection"]["status"] if kp_b1b.get("selection") else None,
                "canonicalization_status": (kp_b1b["canonicalization"] or {}).get("status")
                    if kp_b1b.get("canonicalization") else None,
                "redundancy_qa_status": (kp_b1b["redundancy_qa"] or {}).get("status")
                    if kp_b1b.get("redundancy_qa") else None,
            })
            kp_b1b_final_status = status
            kp_b1b_last_result = kp_b1b
            print(f"[{THEME_ID}][COMPLETE3] Key Phrase B1B call{call_no} status={status} cost_jpy=¥{call_cost:.2f}")
            if status == "KEY_WORDS_STRUCTURE_PASS":
                break
            if call_no == 1:
                continue  # 2回目を試す(合計最大2回)
        result["key_phrase_b1b_attempts"] = kp_b1b_attempts
        result["key_phrase_b1b_final_status"] = kp_b1b_final_status

        kp_b1b_pass = (kp_b1b_final_status == "KEY_WORDS_STRUCTURE_PASS")
        result["key_phrase_b1b_pass"] = kp_b1b_pass
        if kp_b1b_pass:
            if os.path.isdir(f"{BASE_DIR}/key_phrases/b1b") and \
                    not os.path.isdir(f"{BASE_DIR}/key_phrases/b1b_old_attempts"):
                shutil.copytree(f"{BASE_DIR}/key_phrases/b1b", f"{BASE_DIR}/key_phrases/b1b_old_attempts")
                shutil.rmtree(f"{BASE_DIR}/key_phrases/b1b")
            shutil.copytree(kp_dir_b1b_final, f"{BASE_DIR}/key_phrases/b1b", dirs_exist_ok=True)
            print(f"[{THEME_ID}][COMPLETE3] Key Phrase B1B PASS -> synced key_phrases/b1b_final/ "
                  "to key_phrases/b1b/ (old attempts moved to key_phrases/b1b_old_attempts/)")
        else:
            print(f"[{THEME_ID}][COMPLETE3] Key Phrase B1B NOT PASS after "
                  f"{len(kp_b1b_attempts)} call(s) (final_status={kp_b1b_final_status}). "
                  "key_phrases/b1b/ left unchanged; result recorded in key_phrases/b1b_final/.")

        # ============================================================
        # (4) jargon scan最終確認・Cross-Level Consistency突合
        # ============================================================
        jargon_final = {"a2": prev_driver.jargon_scan(a2_text), "b1b": prev_driver.jargon_scan(b1b_text)}
        with open(f"{BASE_DIR}/jargon_scan_final.json", encoding="utf-8") as f:
            jargon_scan_final_prev = json.load(f)
        jargon_scan_final_prev["complete3_final"] = {
            "a2": jargon_final["a2"]["hit_count"], "b1b": jargon_final["b1b"]["hit_count"]}
        with open(f"{BASE_DIR}/jargon_scan_final.json", "w", encoding="utf-8") as f:
            json.dump(jargon_scan_final_prev, f, ensure_ascii=False, indent=2)
        result["jargon_final_complete3"] = {"a2": jargon_final["a2"]["hit_count"],
                                             "b1b": jargon_final["b1b"]["hit_count"]}
        print(f"[{THEME_ID}][COMPLETE3] jargon scan(final): a2={jargon_final['a2']['hit_count']} "
              f"b1b={jargon_final['b1b']['hit_count']}")

        cross_md, cross_consistent = build_cross_level_consistency_md_v3(a2_text, b1b_text)
        with open(f"{BASE_DIR}/cross_level_consistency.md", "w", encoding="utf-8") as f:
            f.write(cross_md)
        result["cross_level_consistent"] = cross_consistent

        # sync再確認(この段階でarticle.md/reader_facing_article*.txtは
        # 本タスクでは書き換えていないため、開始時と同じ結果になる想定)
        with open(f"{BASE_DIR}/reader_facing_article.txt", encoding="utf-8") as f:
            a2_reader_text_after = f.read()
        with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", encoding="utf-8") as f:
            b1b_reader_text_after = f.read()
        result["a2_sync_after_task"] = (a2_text == a2_reader_text_after)
        result["b1b_sync_after_task"] = (b1b_text == b1b_reader_text_after)

        result["overall_status"] = "COMPLETE"
        stopped_stage = None

    except BudgetStop as e:
        result["overall_status"] = "STOP_BUDGET_EXCEEDED"
        result["stop_reason"] = str(e)
        result["stopped_before_stage"] = e.stage
        print(f"[{THEME_ID}][COMPLETE3] STOP(budget): {e}")
    except RuntimeError as e:
        result["overall_status"] = "STOP_HUMAN_REVIEW_OR_QA_FAIL"
        result["stop_reason"] = str(e)
        result["stopped_at_stage"] = stopped_stage
        print(f"[{THEME_ID}][COMPLETE3] STOP: {e}")

    # ============================================================
    # rewrite_log.md 追記
    # ============================================================
    with open(f"{BASE_DIR}/rewrite_log.md", "a", encoding="utf-8") as f:
        f.writelines(rewrite_log_lines)

    # ============================================================
    # 費用/ログの最終集計
    # ============================================================
    finished_at = datetime.now(timezone.utc).isoformat()
    with open(LOG_PATH, encoding="utf-8") as f:
        all_lines = f.readlines()
    new_lines = all_lines[baseline_line_count:]
    with open(f"{BASE_DIR}/raw_usage_log_complete3_task_only.jsonl", "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    stage_breakdown = {}
    total_in = total_out = total_cached = 0
    for line in new_lines:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if rec.get("success") is False:
            continue
        stage = rec.get("stage") or "unknown"
        cost_jpy = prev_driver._call_cost_usd(rec) * prev_driver.USD_JPY
        b = stage_breakdown.setdefault(stage, {"calls": 0, "cost_jpy": 0.0})
        b["calls"] += 1
        b["cost_jpy"] += cost_jpy
        total_in += rec.get("input_tokens") or 0
        total_out += rec.get("output_tokens") or 0
        total_cached += rec.get("cached_input_tokens") or 0
    for b in stage_breakdown.values():
        b["cost_jpy"] = round(b["cost_jpy"], 2)

    this_task_cost_jpy = round(prev_driver._lines_cost_jpy(new_lines), 2)
    model_ids = sorted({json.loads(l)["model_id"] for l in new_lines if l.strip() and json.loads(l).get("model_id")})

    cost_summary_complete3 = {
        "started_at": started_at, "finished_at": finished_at, "budget_jpy": BUDGET_JPY,
        "baseline_cost_jpy_excluded": round(baseline_cost_jpy, 2),
        "this_task_cost_jpy": this_task_cost_jpy,
        "budget_exceeded": this_task_cost_jpy > BUDGET_JPY,
        "overall_status": result.get("overall_status"),
        "stopped_before_stage": result.get("stopped_before_stage"),
        "stopped_at_stage": result.get("stopped_at_stage"),
        "new_api_calls": len(new_lines),
        "model_ids": model_ids,
        "token_totals": {"input_tokens": total_in, "output_tokens": total_out, "cached_input_tokens": total_cached,
                          "total_tokens": total_in + total_out},
        "cost_breakdown_by_stage_jpy": stage_breakdown,
    }
    with open(f"{BASE_DIR}/cost_summary_complete_3.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary_complete3, f, ensure_ascii=False, indent=2, default=str)

    # production_set_cost.json 更新
    prod_cost_path = f"{BASE_DIR}/production_set_cost.json"
    with open(prod_cost_path, encoding="utf-8") as f:
        prod_cost = json.load(f)
    prod_cost["this_task3_a2_final_qa_and_kp_completion_jpy"] = this_task_cost_jpy
    prod_cost["this_task3_breakdown_by_stage_jpy"] = stage_breakdown
    prod_cost["status"] = f"COMPLETE3({result.get('overall_status')})"
    prod_cost["grand_total_jpy_including_key_phrase"] = round(
        prod_cost.get("grand_total_jpy_including_key_phrase", 0.0) + this_task_cost_jpy, 2)
    prod_cost["key_phrase_b1b_final_status_complete3"] = result.get("key_phrase_b1b_final_status")
    prod_cost["note"] = (
        "Discovery Production 1生成セット(共通Research/Ledger+A2+B1、Key Phrase込み)。"
        "本タスク(EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE、継続CONT2)でA2記事全体"
        "final QAを初めて再実行し、Key Phrase A2の最終本文整合をローカル確認、Key Phrase B1Bを"
        "確定canonical本文に対して正規の初回生成として実行した(最大2回)。50:50配賦は行わない。")
    with open(prod_cost_path, "w", encoding="utf-8") as f:
        json.dump(prod_cost, f, ensure_ascii=False, indent=2, default=str)

    result["finished_at"] = finished_at
    result["this_task_cost_jpy"] = this_task_cost_jpy
    result["budget_exceeded"] = this_task_cost_jpy > BUDGET_JPY
    result["model_ids"] = model_ids

    with open(f"{BASE_DIR}/run_result_complete_3.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{os.path.dirname(BASE_DIR)}/progress_log.md", "a", encoding="utf-8") as f:
        f.write(f"- Discovery complete3(CONT2): overall_status={result.get('overall_status')} "
                f"this_task_cost_jpy=¥{this_task_cost_jpy:.2f} "
                f"a2_fc={result.get('a2_final_qa_recheck', {}).get('fact_checker_verdict')} "
                f"kp_a2_all_present={result.get('key_phrase_a2_all_present')} "
                f"kp_b1b_final_status={result.get('key_phrase_b1b_final_status')} "
                f"({finished_at})\n")

    print(f"[{THEME_ID}][COMPLETE3] 完了。overall_status={result.get('overall_status')} "
          f"本タスク実測費用=¥{this_task_cost_jpy:.2f}(予算=¥{BUDGET_JPY:.2f})")
    return result


if __name__ == "__main__":
    main()
    sys.exit(0)
