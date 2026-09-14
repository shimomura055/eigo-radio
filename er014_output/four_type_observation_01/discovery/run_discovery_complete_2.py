# ============================================================
# er014_output/four_type_observation_01/discovery/run_discovery_complete_2.py
# 管理ID: EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE(継続、CONT1)
#
# 目的(既存仕様内の個別修正でDiscovery A2/B1B/Key Phraseを完成させる継続。
# 新Production仕様Trialではない):
#  (1) F002文の修正完了: 前回driver(run_discovery_complete.py)のF002修正は
#      diff QA(Fact Checker A' + Ledger Deviation Checker)がblocks_
#      acceptance=Trueと判定し、resolved=False/human_review_required=True
#      のまま停止していた(ただしfix_fact_blocks()はfoundのみでapply_
#      rewritesするため、article本文には既に'37'/'Thirty-seven'という
#      具体的人数が適用済み)。今回、限定Verification(AMBIGUOUS)の結果を
#      踏まえ、Ledger F002のnotes_for_writerへ「動画視聴者数を具体的な
#      数字で断定しない」旨のhedgeを追記したうえで、既存er010_ledger_
#      local_rewrite_09.apply_diff_qa_to_resolved_rewrite()へ「operator
#      (人手)が用意した修正文」を持つrewrite_result dictを直接渡す
#      (この関数はresolved/final_textキーさえあれば呼び出し元を問わない
#      既存の汎用インターフェースであり、新Validator/QAを追加するもの
#      ではない)。diff QAが受理すればresolved=True/human_review_
#      required=Falseとして確定する。
#  (2) B1B Fact Checker FAILの原因確認: 実際のpost_fix_fact_qa.json
#      (2026-09-14 17:08時点)を読むと、FAIL理由はF002ではなくF009
#      (Nguyen/Ryan/Deci、'chosen solitude reduces stress'をStudy 4限定
#      ではなく'Across four studies'と一般化していた)とF014(Japan-US
#      survey、'people'という一般化がAmericansには見られない差を曖昧に
#      していた)の2件。Ledger F009のnotes_for_writer/scopeをStudy 4限定
#      であることを明示する形へ修正し(F014は既存Ledgerが既に正確な
#      scopeなので変更不要)、既存fix_fact_blocks()パターン(rewrite_
#      ng_item+apply_diff_qa_to_resolved_rewrite、run_discovery_
#      complete.pyから再利用)でB1Bの該当2文のみ修正する(最大1回)。
#      その後B1B最終QAを1回再実行する。
#  (3) Key Phrase B1B: 2026-09-14 17:13の時点で前任エージェントが既存
#      正式入口run_key_phrases()を手動再呼び出し(retry_key_phrase_b1b.py、
#      無変更の既存関数)しており、結果はKEY_WORDS_STRUCTURE_PASS
#      (article_id ...retry2)。追加コストなしにこの既存結果を採用し、
#      新規APIは呼ばない(1回目=INVALID、2回目=PASS、既存の「最大3回まで
#      再呼び出し」方針の範囲内)。Key Phrase A2は1回目でPASS済み
#      (変更なし)。
#  (4) jargon scan最終確認・Cross-Level Consistency突合(最終テキスト)。
#  (5) production_set_cost.json更新。
#
# 費用上限: BUDGET_JPY=90円(本タスクの新規API call分のみ)。段階ごとに、
# 現在までの実測増分 + 次段階の見込みコストを事前に合算してBUDGET_JPYと
# 比較し、超過が見込まれる場合はその段階を開始せずBudgetStopで正常
# finalizeする(run_discovery_complete.pyと同じパターン)。
# ============================================================
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 前回driver(同一ディレクトリ)。fix_fact_blocks/find_block_by_substring・
# build_cross_level_consistency_md・共有infra(vfl01/routing/cl/local_
# rewrite/artgen/scaffold_gen/jargon_scan/run_final_qa等)をそのまま再利用
# する(`if __name__ == "__main__"`ガードがあるためimportしてもmain()は
# 実行されない)。
import run_discovery_complete as base

prev_driver = base.prev_driver
THEME_ID = base.THEME_ID
BASE_DIR = base.BASE_DIR
RESEARCH_DIR = base.RESEARCH_DIR
LOG_PATH = base.LOG_PATH
TOPIC_EN = base.TOPIC_EN
REASONING_EFFORT = base.REASONING_EFFORT

BUDGET_JPY = 90.0

STAGE_ESTIMATE_JPY = {
    "f002_operator_a2_diffqa": 12.0,
    "f002_operator_b1b_diffqa": 12.0,
    "b1b_qa_fix_rewrite": 25.0,
    "b1b_final_qa_recheck": 35.0,
    "a2_final_qa_recheck": 30.0,
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
# (1) Ledger F002 notes hedge追記(決定的テキスト差替え、現在の
# research/verified_fact_ledger.txt内容に対する追記のみ)
# ============================================================
F002_NOTES_OLD = (
    "  notes_for_writer: Do not write 'all 60 students/participants watched the video' or "
    "'60 students watched a six-minute conversation.' Only 37 (18+19) watched the video; the "
    "other 23 did not watch any video. Use plain wording (avoid the word 'condition'; say "
    "'group' instead), and do not claim that four seconds is universally awkward.\n"
)

F002_NOTES_NEW = (
    "  notes_for_writer: Do not write 'all 60 students/participants watched the video' or "
    "'60 students watched a six-minute conversation.' The table-based total of 37 (18+19) "
    "watched the video; the other 23 did not watch any video. UPDATE (limited re-verification, "
    "2026-09-14, fact_fix_verification.json, verdict=AMBIGUOUS): the source separately states "
    "that a small number of participants (up to 4) were excluded from analysis for noticing the "
    "video edit, and the exact pre-exclusion breakdown by group is not fully clear from the "
    "accessible text. Therefore prefer NOT stating a specific number of video watchers at all in "
    "reader-facing text (e.g. 'students watched a six-minute video of a conversation', with no "
    "number); if a number must be used, only the table-based 37 (18+19) is supported, but do not "
    "present it as fully certain. Use plain wording (avoid the word 'condition'; say 'group' "
    "instead), and do not claim that four seconds is universally awkward.\n"
)

F009_OLD_BLOCK = (
    "[VERIFIED] F009: Across four studies, solitude generally reduced both high-arousal positive "
    "affect and high-arousal negative affect; solitude was associated with relaxation and reduced "
    "stress when participants actively chose to be alone. "
    "([selfdeterminationtheory.org](https://selfdeterminationtheory.org/wp-content/uploads/2018/05/2018_NguyenRyanDeci_PSPB.pdf?utm_source=openai))\n"
    "  scope: Four experimental studies reported in one research program\n"
    "  conditions: Conditions varied in whether participants were alone, engaged in an activity, "
    "chose what to think about, or actively chose to be alone.\n"
    "  numeric_value: 4 studies (numeric_scope: Research program)\n"
    "  date_or_period: 2018 publication; studies conducted before publication\n"
    "  causal_strength: CAUSAL_STATED_BY_SOURCE\n"
    "  notes_for_writer: This research provides evidence that unstructured alone time can reduce "
    "arousal for some conditions, contrasting with studies in which people prefer external activity.\n"
)

F009_NEW_BLOCK = (
    "[VERIFIED] F009: Across four studies, solitude generally reduced both high-arousal positive "
    "affect and high-arousal negative affect; in one of these studies (Study 4), solitude was "
    "specifically associated with relaxation and reduced stress when participants actively chose "
    "to be alone. "
    "([selfdeterminationtheory.org](https://selfdeterminationtheory.org/wp-content/uploads/2018/05/2018_NguyenRyanDeci_PSPB.pdf?utm_source=openai))\n"
    "  scope: Four experimental studies reported in one research program; the 'actively chosen "
    "solitude is linked with relaxation and reduced stress' finding is reported for Study 4 "
    "specifically, and is NOT confirmed as an identical finding replicated across all four studies.\n"
    "  conditions: Conditions varied across the four studies in whether participants were alone, "
    "engaged in an activity, chose what to think about, or actively chose to be alone; only Study 4 "
    "specifically examined actively chosen solitude in relation to relaxation and reduced stress.\n"
    "  numeric_value: 4 studies; the relaxation/reduced-stress-when-chosen result is from Study 4 "
    "(numeric_scope: Research program; do not attribute the Study 4 relaxation/stress finding to "
    "all four studies)\n"
    "  date_or_period: 2018 publication; studies conducted before publication\n"
    "  causal_strength: CAUSAL_STATED_BY_SOURCE\n"
    "  notes_for_writer: Do not write 'Across four studies, actively choosing solitude was "
    "associated with relaxation and lower stress' as if this exact link was found in all four "
    "studies. The reduced high-arousal-affect finding spans the four studies; the more specific "
    "'chosen solitude -> relaxation and lower stress' finding should be attributed to one study in "
    "this research program (Study 4), not generalized to all four.\n"
)


def apply_ledger_fix_2(ledger_text: str) -> str:
    if F002_NOTES_OLD not in ledger_text:
        raise RuntimeError("F002_NOTES_OLD not found verbatim in current ledger text; aborting ledger fix.")
    if F009_OLD_BLOCK not in ledger_text:
        raise RuntimeError("F009_OLD_BLOCK not found verbatim in current ledger text; aborting ledger fix.")
    new_text = ledger_text.replace(F002_NOTES_OLD, F002_NOTES_NEW).replace(F009_OLD_BLOCK, F009_NEW_BLOCK)
    return new_text


def build_operator_rewrite_result(original_ng_sentence: str, final_text: str, fact_id: str, note: str) -> dict:
    """operator(人手)が用意した修正文を、er010_ledger_local_rewrite_09.
    apply_diff_qa_to_resolved_rewrite()が要求する既存rewrite_result
    dictの形(resolved/final_text/original_ng_sentence等)へ組み立てる。
    この関数自体は新Validator/QAではなく、既存の汎用インターフェースへ
    渡すデータを構築するだけ(diff QAでの受理判定は既存Fact Checker A' +
    Ledger Deviation Checkerがこれまで通り行う)。"""
    return {
        "original_ng_sentence": original_ng_sentence,
        "issue": f"Operator escalation for {fact_id} (human_review_required after diff QA blocked acceptance in "
                 f"the prior task run). {note}",
        "explanation": note,
        "flags": [],
        "attempts": [{"attempt": "operator", "text": final_text, "ledger_status": "OPERATOR_PROVIDED"}],
        "final_text": final_text,
        "resolved": True,
        "human_review_required": False,
        "fact_id": fact_id,
    }


def main():
    prev_driver.cl.install(LOG_PATH)
    with open(LOG_PATH, encoding="utf-8") as f:
        baseline_lines = f.readlines()
    baseline_line_count = len(baseline_lines)
    baseline_cost_jpy = prev_driver._lines_cost_jpy(baseline_lines)
    print(f"[{THEME_ID}][COMPLETE2] baseline(前タスク分含む)line_count={baseline_line_count} "
          f"baseline_cost_jpy=¥{baseline_cost_jpy:.2f}(このタスクの予算計算からは除外)")

    def incremental_jpy() -> float:
        return prev_driver.cost_total_jpy() - baseline_cost_jpy

    def ensure_budget(stage: str):
        inc = incremental_jpy()
        est = STAGE_ESTIMATE_JPY.get(stage, 15.0)
        if inc + est > BUDGET_JPY:
            raise BudgetStop(stage, inc, est)
        print(f"[{THEME_ID}][COMPLETE2] budget check OK stage={stage} incremental_so_far=¥{inc:.2f} "
              f"+ estimate=¥{est:.2f} <= budget=¥{BUDGET_JPY:.2f}")

    started_at = datetime.now(timezone.utc).isoformat()
    client = prev_driver.vfl01.get_client()

    result = {"started_at": started_at, "budget_jpy": BUDGET_JPY,
              "baseline_cost_jpy": round(baseline_cost_jpy, 2), "stop_reason": None}
    rewrite_log_lines = ["\n# Discovery Complete 2 (F002 operator escalation + B1B F009/F014 fix) - addendum\n"]

    stopped_stage = None
    try:
        # ============================================================
        # (0) 退避
        # ============================================================
        os.makedirs(f"{BASE_DIR}/a2_before_f002_fix", exist_ok=True)
        os.makedirs(f"{BASE_DIR}/b1b_before_f002_fix", exist_ok=True)
        if os.path.isdir(f"{BASE_DIR}/a2") and not os.path.isdir(f"{BASE_DIR}/a2_before_f002_fix/a2"):
            shutil.copytree(f"{BASE_DIR}/a2", f"{BASE_DIR}/a2_before_f002_fix/a2")
        if os.path.isdir(f"{BASE_DIR}/b1b") and not os.path.isdir(f"{BASE_DIR}/b1b_before_f002_fix/b1b"):
            shutil.copytree(f"{BASE_DIR}/b1b", f"{BASE_DIR}/b1b_before_f002_fix/b1b")
        for fname in ["reader_facing_article.txt"]:
            src = f"{BASE_DIR}/{fname}"
            if os.path.exists(src):
                shutil.copy2(src, f"{BASE_DIR}/a2_before_f002_fix/{fname}")
        for fname in ["reader_facing_article_b1b.txt"]:
            src = f"{BASE_DIR}/{fname}"
            if os.path.exists(src):
                shutil.copy2(src, f"{BASE_DIR}/b1b_before_f002_fix/{fname}")

        with open(f"{BASE_DIR}/reader_facing_article.txt", encoding="utf-8") as f:
            a2_text = f.read()
        with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", encoding="utf-8") as f:
            b1b_text = f.read()

        jargon_before = {"a2": prev_driver.jargon_scan(a2_text), "b1b": prev_driver.jargon_scan(b1b_text)}
        print(f"[{THEME_ID}][COMPLETE2] jargon scan(entering task): a2={jargon_before['a2']['hit_count']} "
              f"b1b={jargon_before['b1b']['hit_count']}")

        with open(f"{RESEARCH_DIR}/verified_fact_ledger.txt", encoding="utf-8") as f:
            verified_ledger_text_old = f.read()
        vfl_path = f"{RESEARCH_DIR}/stage_b3_vfl.json"

        # ============================================================
        # Ledger修正(F002 notes hedge + F009 scope/notes)
        # ============================================================
        shutil.copy2(f"{RESEARCH_DIR}/verified_fact_ledger.txt",
                     f"{RESEARCH_DIR}/verified_fact_ledger_v2_before_fix.txt")
        verified_ledger_text = apply_ledger_fix_2(verified_ledger_text_old)
        with open(f"{RESEARCH_DIR}/verified_fact_ledger.txt", "w", encoding="utf-8") as f:
            f.write(verified_ledger_text)
        print(f"[{THEME_ID}][COMPLETE2] ledger fix v2 applied (F002 notes hedge + F009 scope/notes)")

        ledger_model_a2 = prev_driver.routing.require_model("A2_WRITER", prev_driver.routing.WRITER_MODEL)
        ledger_model_b1b = prev_driver.routing.require_model("B1_WRITER", prev_driver.routing.WRITER_MODEL)
        fact_checker_model = prev_driver.routing.require_model(
            "WRITER_FACT_CHECK", prev_driver.routing.WRITER_FACT_CHECK_MODEL)

        # ============================================================
        # (1) F002 operator escalation: A2
        # ============================================================
        stopped_stage = "f002_operator_a2_diffqa"
        ensure_budget("f002_operator_a2_diffqa")
        a2_block = base.find_block_by_substring(a2_text, "37 students watched")
        if a2_block is None:
            raise RuntimeError("A2: F002 target sentence ('37 students watched') not found.")
        a2_f002_final_text = "In one experiment, students watched a six-minute video of a conversation."
        a2_f002_note = (
            "Per corrected Verified Fact Ledger F002, do not state a specific number of video "
            "watchers; the source has an internal inconsistency about excluded participants and the "
            "exact pre-exclusion breakdown is not fully clear. Other Fact elements (effect direction, "
            "4-second silence, unawareness of the pause) are unchanged and are stated in neighboring "
            "sentences.")
        a2_f002_op = build_operator_rewrite_result(
            a2_block["target"], a2_f002_final_text, "F002", a2_f002_note)
        with prev_driver.cl.logging_context(THEME_ID, "f002_operator_a2_diffqa"):
            a2_f002_op = prev_driver.local_rewrite.apply_diff_qa_to_resolved_rewrite(
                a2_f002_op, client, TOPIC_EN, a2_block["before"], a2_block["after"],
                verified_ledger_text, ledger_model_a2, fact_checker_model)
        print(f"[{THEME_ID}][COMPLETE2] A2 F002 operator diff QA: resolved={a2_f002_op['resolved']} "
              f"human_review_required={a2_f002_op['human_review_required']} "
              f"blocks_acceptance={a2_f002_op['diff_qa'].get('blocks_acceptance')}")
        result["a2_f002_operator_diffqa"] = {
            "resolved": a2_f002_op["resolved"], "human_review_required": a2_f002_op["human_review_required"],
            "blocks_acceptance": a2_f002_op["diff_qa"].get("blocks_acceptance"),
            "fact_check_verdict": a2_f002_op["diff_qa"].get("fact_check_verdict"),
        }
        rewrite_log_lines.append("## A2 F002 operator escalation\n")
        rewrite_log_lines.append(f"  旧: {a2_f002_op['original_ng_sentence']}\n")
        rewrite_log_lines.append(f"  新(operator提供): {a2_f002_op['final_text']}\n")
        rewrite_log_lines.append(
            f"  resolved={a2_f002_op['resolved']} human_review_required={a2_f002_op['human_review_required']} "
            f"diff_qa_blocks_acceptance={a2_f002_op['diff_qa'].get('blocks_acceptance')} "
            f"fact_check_verdict={a2_f002_op['diff_qa'].get('fact_check_verdict')}\n\n")
        if a2_f002_op["human_review_required"]:
            raise RuntimeError(
                "STOP: A2 F002 operator-provided text still blocked by diff QA "
                f"(fact_check_verdict={a2_f002_op['diff_qa'].get('fact_check_verdict')}, "
                f"ledger_eval={a2_f002_op['diff_qa'].get('ledger_check_target_eval')}). "
                "This is a human-judgment-only quality issue per STOP conditions.")
        a2_text = prev_driver.local_rewrite.apply_rewrites(a2_text, [a2_f002_op])
        a2_text = prev_driver.artgen.normalize_article_formatting(a2_text)

        # ============================================================
        # (1) F002 operator escalation: B1B
        # ============================================================
        stopped_stage = "f002_operator_b1b_diffqa"
        ensure_budget("f002_operator_b1b_diffqa")
        b1b_block = base.find_block_by_substring(b1b_text, "Thirty-seven students watched")
        if b1b_block is None:
            raise RuntimeError("B1B: F002 target sentence ('Thirty-seven students watched') not found.")
        b1b_f002_final_text = "In this experiment, students watched a six-minute video of a conversation."
        b1b_f002_note = a2_f002_note
        b1b_f002_op = build_operator_rewrite_result(
            b1b_block["target"], b1b_f002_final_text, "F002", b1b_f002_note)
        with prev_driver.cl.logging_context(THEME_ID, "f002_operator_b1b_diffqa"):
            b1b_f002_op = prev_driver.local_rewrite.apply_diff_qa_to_resolved_rewrite(
                b1b_f002_op, client, TOPIC_EN, b1b_block["before"], b1b_block["after"],
                verified_ledger_text, ledger_model_b1b, fact_checker_model)
        print(f"[{THEME_ID}][COMPLETE2] B1B F002 operator diff QA: resolved={b1b_f002_op['resolved']} "
              f"human_review_required={b1b_f002_op['human_review_required']} "
              f"blocks_acceptance={b1b_f002_op['diff_qa'].get('blocks_acceptance')}")
        result["b1b_f002_operator_diffqa"] = {
            "resolved": b1b_f002_op["resolved"], "human_review_required": b1b_f002_op["human_review_required"],
            "blocks_acceptance": b1b_f002_op["diff_qa"].get("blocks_acceptance"),
            "fact_check_verdict": b1b_f002_op["diff_qa"].get("fact_check_verdict"),
        }
        rewrite_log_lines.append("## B1B F002 operator escalation\n")
        rewrite_log_lines.append(f"  旧: {b1b_f002_op['original_ng_sentence']}\n")
        rewrite_log_lines.append(f"  新(operator提供): {b1b_f002_op['final_text']}\n")
        rewrite_log_lines.append(
            f"  resolved={b1b_f002_op['resolved']} human_review_required={b1b_f002_op['human_review_required']} "
            f"diff_qa_blocks_acceptance={b1b_f002_op['diff_qa'].get('blocks_acceptance')} "
            f"fact_check_verdict={b1b_f002_op['diff_qa'].get('fact_check_verdict')}\n\n")
        if b1b_f002_op["human_review_required"]:
            raise RuntimeError(
                "STOP: B1B F002 operator-provided text still blocked by diff QA "
                f"(fact_check_verdict={b1b_f002_op['diff_qa'].get('fact_check_verdict')}, "
                f"ledger_eval={b1b_f002_op['diff_qa'].get('ledger_check_target_eval')}). "
                "This is a human-judgment-only quality issue per STOP conditions.")
        b1b_text = prev_driver.local_rewrite.apply_rewrites(b1b_text, [b1b_f002_op])
        b1b_text = prev_driver.artgen.normalize_article_formatting(b1b_text)

        # 確定(F002適用後の本文をディスクへ反映)
        with open(f"{BASE_DIR}/reader_facing_article.txt", "w", encoding="utf-8") as f:
            f.write(a2_text)
        with open(f"{BASE_DIR}/a2/article.md", "w", encoding="utf-8") as f:
            f.write(a2_text)
        with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", "w", encoding="utf-8") as f:
            f.write(b1b_text)
        with open(f"{BASE_DIR}/b1b/article.md", "w", encoding="utf-8") as f:
            f.write(b1b_text)

        # ============================================================
        # (2) B1B: F009/F014限定修正(最大1回)
        # ============================================================
        stopped_stage = "b1b_qa_fix_rewrite"
        ensure_budget("b1b_qa_fix_rewrite")
        f009_hint = (
            "Correct scope (from the corrected Verified Fact Ledger, fact F009): the finding that "
            "solitude reduces both high- and low-arousal affect spans four studies, but the more "
            "specific finding that ACTIVELY CHOSEN solitude was linked with relaxation and lower "
            "stress is reported for one specific study (Study 4) in this research program, not "
            "confirmed as identical across all four studies. Rewrite the sentence so it does not "
            "claim this specific 'chosen solitude -> relaxation and lower stress' link held 'across "
            "four studies'; instead attribute it to one study in this line of research (e.g. 'in one "
            "of these studies'), without inventing new numeric detail, in natural, plain, "
            "spoken-style English.")
        f014_hint = (
            "Correct scope (from the existing Verified Fact Ledger, fact F014): in this Japan-United "
            "States survey, ONLY Japanese respondents reported a more negative view of silence with "
            "strangers than with close friends; American respondents did NOT show that same "
            "difference. Rewrite the sentence so it does not generalize to 'people' in general; make "
            "clear the pattern was found specifically among Japanese respondents, and that American "
            "respondents did not show it, in natural, plain, spoken-style English (do not invent new "
            "numeric or causal detail).")
        b1b_qa_fixes = [
            {"fact_id": "F009", "substring": "Across four studies, actively choosing solitude",
             "hint": f009_hint},
            {"fact_id": "F014",
             "substring": "views of silence also changed depending on whether people",
             "hint": f014_hint},
        ]
        b1b_qa_fix = base.fix_fact_blocks(b1b_text, ledger_model_b1b, TOPIC_EN, "b1b_qa_fix", client,
                                           verified_ledger_text, b1b_qa_fixes)
        b1b_text = b1b_qa_fix["updated_text"]
        rewrite_log_lines.append("## B1B F009/F014 limited fix (final QA FAIL cause)\n")
        for br in b1b_qa_fix["block_results"]:
            if not br.get("found"):
                rewrite_log_lines.append(f"- {br['fact_id']}: substring not found ('{br['substring']}')\n")
                continue
            rewrite_log_lines.append(f"- {br['fact_id']}\n")
            rewrite_log_lines.append(f"  旧: {br['original_ng_sentence']}\n")
            rewrite_log_lines.append(f"  新: {br['final_text']}\n")
            rewrite_log_lines.append(f"  resolved={br['resolved']} human_review_required={br['human_review_required']} "
                                      f"diff_qa_blocks_acceptance={br['diff_qa'].get('blocks_acceptance')}\n\n")
        result["b1b_qa_fix_block_results"] = [
            {"fact_id": br["fact_id"], "found": br.get("found", False), "resolved": br.get("resolved"),
             "human_review_required": br.get("human_review_required")}
            for br in b1b_qa_fix["block_results"]]

        with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", "w", encoding="utf-8") as f:
            f.write(b1b_text)
        with open(f"{BASE_DIR}/b1b/article.md", "w", encoding="utf-8") as f:
            f.write(b1b_text)

        jargon_after_fix = {"a2": prev_driver.jargon_scan(a2_text), "b1b": prev_driver.jargon_scan(b1b_text)}
        print(f"[{THEME_ID}][COMPLETE2] jargon scan(after F002+F009/F014 fix): "
              f"a2={jargon_after_fix['a2']['hit_count']} b1b={jargon_after_fix['b1b']['hit_count']}")
        result["jargon_after_fix"] = {"a2": jargon_after_fix["a2"]["hit_count"],
                                       "b1b": jargon_after_fix["b1b"]["hit_count"]}

        # ============================================================
        # B1B最終QA再実行(1回)
        # ============================================================
        stopped_stage = "b1b_final_qa_recheck"
        ensure_budget("b1b_final_qa_recheck")
        if os.path.exists(f"{BASE_DIR}/b1b/audit/post_fix_fact_qa.json"):
            shutil.copy2(f"{BASE_DIR}/b1b/audit/post_fix_fact_qa.json",
                         f"{BASE_DIR}/b1b/audit/post_fix_fact_qa_before_complete2_fix.json")
        b1b_final_qa = prev_driver.run_final_qa(b1b_text, verified_ledger_text, ledger_model_b1b, TOPIC_EN,
                                                 f"{BASE_DIR}/b1b", vfl_path, client, "b1b_complete2")
        print(f"[{THEME_ID}][COMPLETE2] B1B final QA(recheck): {b1b_final_qa}")
        result["b1b_final_qa_recheck"] = b1b_final_qa
        if b1b_final_qa["fact_checker_verdict"] == "FAIL":
            result["b1b_final_qa_status_after_1_retry"] = "STILL_FAIL_STOP"
            print(f"[{THEME_ID}][COMPLETE2] STOP: B1B final QA still FAIL after 1 limited fix pass "
                  "(per governance: max 1 retry, then STOP).")
            raise RuntimeError(
                "STOP: B1B final Fact Checker verdict is still FAIL after the single allowed limited "
                "Ledger-based fix pass (F009/F014). This is treated as a human-judgment-only quality "
                "issue per STOP conditions.")
        else:
            result["b1b_final_qa_status_after_1_retry"] = "PASS_OR_OTHER"

        # ============================================================
        # A2最終QA再実行(F002修正の影響確認、A2は元々PASS済み)
        # ============================================================
        stopped_stage = "a2_final_qa_recheck"
        ensure_budget("a2_final_qa_recheck")
        if os.path.exists(f"{BASE_DIR}/a2/audit/post_fix_fact_qa.json"):
            shutil.copy2(f"{BASE_DIR}/a2/audit/post_fix_fact_qa.json",
                         f"{BASE_DIR}/a2/audit/post_fix_fact_qa_before_complete2_fix.json")
        a2_final_qa = prev_driver.run_final_qa(a2_text, verified_ledger_text, ledger_model_a2, TOPIC_EN,
                                                f"{BASE_DIR}/a2", vfl_path, client, "a2_complete2")
        print(f"[{THEME_ID}][COMPLETE2] A2 final QA(recheck): {a2_final_qa}")
        result["a2_final_qa_recheck"] = a2_final_qa

        # jargon再確認(retry rewriteでjargonが再混入していないか)
        jargon_final = {"a2": prev_driver.jargon_scan(a2_text), "b1b": prev_driver.jargon_scan(b1b_text)}
        with open(f"{BASE_DIR}/jargon_scan_final.json", "w", encoding="utf-8") as f:
            json.dump({"before_this_task": jargon_before, "after_f002_and_qa_fix": jargon_after_fix,
                       "final": jargon_final}, f, ensure_ascii=False, indent=2)
        result["jargon_final"] = {"a2": jargon_final["a2"]["hit_count"], "b1b": jargon_final["b1b"]["hit_count"]}

        # ============================================================
        # Cross-Level Consistency(最終テキスト)
        # ============================================================
        cross_md, cross_consistent = base.build_cross_level_consistency_md(a2_text, b1b_text)
        with open(f"{BASE_DIR}/cross_level_consistency.md", "w", encoding="utf-8") as f:
            f.write(cross_md)
        result["cross_level_consistent"] = cross_consistent

        # ============================================================
        # Key Phrase: 既存結果を採用(新規API呼び出しなし)
        # ============================================================
        kp_dir_b1b = f"{BASE_DIR}/key_phrases/b1b"
        if os.path.exists(f"{kp_dir_b1b}/keywords_runtime_metadata.json"):
            with open(f"{kp_dir_b1b}/keywords_runtime_metadata.json", encoding="utf-8") as f:
                kp_b1b_meta = json.load(f)
            result["key_phrase_b1b_status"] = kp_b1b_meta.get("final_status")
            result["key_phrase_b1b_source"] = (
                "existing on-disk result from retry_key_phrase_b1b.py (manual re-invocation of "
                "unmodified run_key_phrases(), executed prior to this task's start; attempt 1 by "
                "run_discovery_complete.py = KEY_WORDS_STRUCTURE_INVALID, attempt 2 by "
                "retry_key_phrase_b1b.py = KEY_WORDS_STRUCTURE_PASS). Reused as-is, zero new API cost.")
        else:
            result["key_phrase_b1b_status"] = "NOT_FOUND"
        kp_dir_a2 = f"{BASE_DIR}/key_phrases/a2"
        if os.path.exists(f"{kp_dir_a2}/keywords_runtime_metadata.json"):
            with open(f"{kp_dir_a2}/keywords_runtime_metadata.json", encoding="utf-8") as f:
                kp_a2_meta = json.load(f)
            result["key_phrase_a2_status"] = kp_a2_meta.get("final_status")
        else:
            result["key_phrase_a2_status"] = "NOT_FOUND"

        result["overall_status"] = "COMPLETE"
        stopped_stage = None

    except BudgetStop as e:
        result["overall_status"] = "STOP_BUDGET_EXCEEDED"
        result["stop_reason"] = str(e)
        result["stopped_before_stage"] = e.stage
        print(f"[{THEME_ID}][COMPLETE2] STOP(budget): {e}")
    except RuntimeError as e:
        result["overall_status"] = "STOP_HUMAN_REVIEW_OR_QA_FAIL"
        result["stop_reason"] = str(e)
        result["stopped_at_stage"] = stopped_stage
        print(f"[{THEME_ID}][COMPLETE2] STOP: {e}")

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
    with open(f"{BASE_DIR}/raw_usage_log_complete2_task_only.jsonl", "w", encoding="utf-8") as f:
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

    cost_summary_complete2 = {
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
    with open(f"{BASE_DIR}/cost_summary_complete_2.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary_complete2, f, ensure_ascii=False, indent=2, default=str)

    # production_set_cost.json 更新
    prod_cost_path = f"{BASE_DIR}/production_set_cost.json"
    with open(prod_cost_path, encoding="utf-8") as f:
        prod_cost = json.load(f)
    prod_cost["this_task2_f002_fix_and_b1b_qa_fix_jpy"] = this_task_cost_jpy
    prod_cost["this_task2_breakdown_by_stage_jpy"] = stage_breakdown
    prod_cost["status"] = f"COMPLETE2({result.get('overall_status')})"
    prod_cost["grand_total_jpy_including_key_phrase"] = round(
        prod_cost.get("grand_total_jpy_including_key_phrase", 0.0) + this_task_cost_jpy, 2)
    prod_cost["note"] = (
        "Discovery Production 1生成セット(共通Research/Ledger+A2+B1、Key Phrase込み)。"
        "本タスク(EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE、継続CONT1)でF002文の"
        "operator escalation(human_review解消)+B1B Fact Checker FAIL原因(F009/F014)の"
        "限定修正+最終QA再実行を実施。Key Phrase B1Bは前任エージェントが本タスク開始前に"
        "既存run_key_phrases()を再呼び出し(retry_key_phrase_b1b.py)済みでPASS、追加コスト"
        "なしで採用。50:50配賦は行わない。")
    with open(prod_cost_path, "w", encoding="utf-8") as f:
        json.dump(prod_cost, f, ensure_ascii=False, indent=2, default=str)

    result["finished_at"] = finished_at
    result["this_task_cost_jpy"] = this_task_cost_jpy
    result["budget_exceeded"] = this_task_cost_jpy > BUDGET_JPY
    result["model_ids"] = model_ids

    with open(f"{BASE_DIR}/run_result_complete_2.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{os.path.dirname(BASE_DIR)}/progress_log.md", "a", encoding="utf-8") as f:
        f.write(f"- Discovery complete2(CONT1): overall_status={result.get('overall_status')} "
                f"this_task_cost_jpy=¥{this_task_cost_jpy:.2f} "
                f"a2_fc={result.get('a2_final_qa_recheck', {}).get('fact_checker_verdict')} "
                f"b1b_fc={result.get('b1b_final_qa_recheck', {}).get('fact_checker_verdict')} "
                f"kp_a2={result.get('key_phrase_a2_status')} kp_b1b={result.get('key_phrase_b1b_status')} "
                f"({finished_at})\n")

    print(f"[{THEME_ID}][COMPLETE2] 完了。overall_status={result.get('overall_status')} "
          f"本タスク実測費用=¥{this_task_cost_jpy:.2f}(予算=¥{BUDGET_JPY:.2f})")
    return result


if __name__ == "__main__":
    main()
    sys.exit(0)
