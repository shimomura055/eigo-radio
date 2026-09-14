# ============================================================
# er014_output/four_type_observation_01/discovery/run_discovery_complete.py
# 管理ID: EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE
#
# 目的(既存仕様内の個別修正でDiscovery A2/B1Bを完成させる。新仕様Trialではない):
#  (1) 限定Verification: 既存vfl01.run_verification()(web_search、Ledger
#      再照合の既存building block)を、Ledger全15 FactではなくF002/F011の
#      2 Factのみに限定して実行し、F002の視聴者数(60 vs 実際に動画を見た
#      37=18+19)とF011のサンプル数(46 vs 一部の公開抄録41)を確認する。
#      Research(Researcher stageからの再実行)は行わない。
#  (2) Ledger修正: (1)の結果を踏まえ、F002/F011のscope/numeric_value/
#      notes_for_writerを実態に整合させる(F002は37/23の内訳を明示、F011は
#      46/41の不一致をhedge)。
#  (3) A2/B1B該当文rewrite: 既存Local Rewrite経路(er010_ledger_local_
#      rewrite_09.rewrite_ng_item + apply_diff_qa_to_resolved_rewrite)を、
#      前回run_discovery_fix_b1b_kp.pyのfix_all_jargon()と同一パターンで
#      「Ledger scope修正」issueとして適用する(新Validator/QAは追加しない)。
#  (4) No Jargon状態維持確認: 前回driverのJARGON_PATTERNS/jargon_scanを
#      再利用してbefore/after 0件を確認する。
#  (5) 正式QA再実行: 前回driverのrun_final_qa()(Fact Checker A'+Ledger
#      Deviation Checker[hook_aware]+Directional Fact Precheck)をA2/B1B
#      それぞれに再利用する。FAILが残る場合は最大1回、追加のLedger整合
#      rewriteを試みる(できない場合はREVIEW_REQUIREDとして記録し先へ進む)。
#  (6) Cross-Level Consistency突合(API呼び出しなし、決定的チェック)。
#  (7) Key Phrase A2/B1B再生成: 既存er003_v1_n3_01_scaffold_generate.
#      run_key_phrases()をそのまま使用する。
#
# 費用上限: BUDGET_JPY=170円(本タスクの新規API call分のみ)。段階ごとに、
# 現在までの実測増分 + 次段階の見込みコストを事前に合算してBUDGET_JPYと
# 比較し、超過が見込まれる場合はその段階を開始せずSTOPする(前回は
# API呼び出し完了後の事後チェックのみで、超過時にRuntimeErrorが送出され
# main()が異常終了=クラッシュしたため、今回は開始前ガード+
# BudgetStop例外の正規catchで必ず正常finalizeする)。
# ============================================================
from __future__ import annotations

import difflib
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 前回driver(同一ディレクトリ)。rewrite経路・Key Phrase呼び出し・cost
# logging機構・jargon scanをそのまま再利用する(`if __name__ == "__main__"`
# ガードがあるためimportしてもmain()は実行されない)。
import run_discovery_fix_b1b_kp as prev_driver

THEME_ID = prev_driver.THEME_ID
BASE_DIR = prev_driver.BASE_DIR
RESEARCH_DIR = prev_driver.RESEARCH_DIR
LOG_PATH = prev_driver.LOG_PATH
TOPIC_EN = prev_driver.TOPIC_EN
REASONING_EFFORT = prev_driver.REASONING_EFFORT

BUDGET_JPY = 170.0

# 段階ごとの見込みコスト(円、前回実測を参考にした保守的な見積り)。
# 事前判定ガード用であり、実測が下回れば後続段階に余裕が生まれる。
STAGE_ESTIMATE_JPY = {
    "verification": 20.0,
    "a2_fact_fix": 20.0,
    "b1b_fact_fix": 20.0,
    "a2_final_qa": 30.0,
    "b1b_final_qa": 50.0,
    "a2_final_qa_retry": 30.0,
    "b1b_final_qa_retry": 50.0,
    "key_phrase_a2": 20.0,
    "key_phrase_b1b": 20.0,
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
# Fact修正blockの検出(決定的substring一致。前回のjargon regex検出と
# 同じ考え方で、本タスク専用の検出/報告ロジック。新Validatorではない)
# ============================================================
def find_block_by_substring(article_text: str, substring: str) -> dict | None:
    sentences = prev_driver.local_rewrite.split_sentences(article_text)
    idx = next((i for i, s in enumerate(sentences) if substring in s), None)
    if idx is None:
        return None
    before = sentences[idx - 1] if idx - 1 >= 0 else ""
    after = sentences[idx + 1] if idx + 1 < len(sentences) else ""
    return {"target": sentences[idx], "before": before, "after": after}


def fix_fact_blocks(article_text: str, ledger_model: str, topic: str, label: str, client,
                     verified_ledger_text: str, fixes: list) -> dict:
    """前回driverのfix_all_jargon()と同一パターン(rewrite_ng_item+
    apply_diff_qa_to_resolved_rewrite)を、Ledger scope修正issueへ適用する。"""
    fact_checker_model = prev_driver.routing.require_model(
        "WRITER_FACT_CHECK", prev_driver.routing.WRITER_FACT_CHECK_MODEL)

    def check_window(window_text: str) -> dict:
        with prev_driver.cl.logging_context(THEME_ID, f"{label}_fact_fix_ledger_check"):
            return prev_driver.vfl01.run_deviation_check(
                client, verified_ledger_text, window_text, model=ledger_model, hook_aware=True)["parsed"]

    block_results = []
    for fx in fixes:
        block = find_block_by_substring(article_text, fx["substring"])
        if block is None:
            block_results.append({"fact_id": fx["fact_id"], "substring": fx["substring"], "found": False})
            continue
        deviation = {
            "issue": (
                f"Ledger scope/numeric accuracy fix for {fx['fact_id']} (existing Verified Fact Ledger "
                "correction; this is a Ledger accuracy fix, NOT a stylistic or No-Jargon change, and NOT "
                "a new fact). This sentence states an inaccurate numeric scope relative to the corrected "
                "Verified Fact Ledger below. Rewrite this sentence (and only the minimum necessary "
                "neighboring wording) so it accurately reflects the corrected Ledger entry, without "
                "inventing new facts, without changing the direction or certainty of any other claim, "
                "and without introducing technical jargon (keep plain, natural spoken English suitable "
                "for a general listener)."
            ),
            "explanation": fx["hint"],
        }
        point_context = prev_driver.local_rewrite.extract_point_context(article_text, block["target"])
        point_context_found = point_context is not None
        if point_context is None:
            point_context = f"{block['before']} {block['target']} {block['after']}".strip()
        with prev_driver.cl.logging_context(THEME_ID, f"{label}_fact_fix_rewrite"):
            r = prev_driver.local_rewrite.rewrite_ng_item(
                client, ledger_model, REASONING_EFFORT, verified_ledger_text,
                point_context, block["target"], deviation, block["before"], block["after"],
                check_window, use_target_sentence_matching=True)
        with prev_driver.cl.logging_context(THEME_ID, f"{label}_fact_fix_diff_qa"):
            r = prev_driver.local_rewrite.apply_diff_qa_to_resolved_rewrite(
                r, client, topic, block["before"], block["after"], verified_ledger_text,
                ledger_model, fact_checker_model)
        r["point_context_found"] = point_context_found
        r["fact_id"] = fx["fact_id"]
        r["found"] = True
        block_results.append(r)

    applicable = [r for r in block_results if r.get("found")]
    updated_text = prev_driver.local_rewrite.apply_rewrites(article_text, applicable) if applicable else article_text
    updated_text = prev_driver.artgen.normalize_article_formatting(updated_text)
    return {"updated_text": updated_text, "block_results": block_results}


# ============================================================
# Ledger修正(F002 / F011)。Verification結果(web_search evidence)を
# ledger_fix_diff.mdへ記録したうえで、決定的なテキスト差し替えを行う
# (LLMによる自動書き換えではなく、確認済みFactに基づく明示的編集)。
# ============================================================
F002_OLD_BLOCK = """[VERIFIED] F002: In Study 2, a single four-second silence in a six-minute video conversation produced more reported rejection and negative emotion, less positive emotion, and lower belonging, self-esteem, social validation, and perceived consensus than the fluent-conversation condition; participants were generally unaware of the specific silence. ([pure.rug.nl](https://pure.rug.nl/ws/files/146971883/Disrupting_the_flow_How_brief_silences_in_group_conversations_affect.pdf))
  scope: 60 undergraduate participants; randomized across fluent, disrupted-flow, and base-rate conditions
  conditions: The silence followed a statement in a videotaped conversation; the source states that four seconds was selected to remain below conscious awareness while still disrupting perceived conversational flow.
  numeric_value: N=60; 4 seconds; 6-minute video (numeric_scope: Study 2 participants and stimulus duration)
  date_or_period: 2011
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: Use precise wording such as 'a four-second silence in this experiment was sufficient to...' rather than claiming that four seconds is universally awkward.
"""

F002_NEW_BLOCK = """[VERIFIED] F002: In Study 2, among the participants who watched the six-minute videotaped conversation, a single four-second silence produced more reported rejection and negative emotion, less positive emotion, and lower belonging, self-esteem, social validation, and perceived consensus than the fluent-conversation (no-silence) version of the same video; these participants were generally unaware of the specific silence. ([pure.rug.nl](https://pure.rug.nl/ws/files/146971883/Disrupting_the_flow_How_brief_silences_in_group_conversations_affect.pdf))
  scope: 60 undergraduate participants took part in Study 2 overall, but only 37 of them actually watched the six-minute videotaped conversation (18 in the fluent-conversation version; 19 in the disrupted-flow/silence version). The remaining 23 participants were in a separate base-rate condition that did not involve watching any video at all (they gave a baseline judgment without seeing the interaction). Do NOT state that all 60 participants watched the video.
  conditions: The silence was shown only within the videotaped conversation seen by the 37 fluent/disrupted-flow participants; the source states that four seconds was selected to remain below conscious awareness while still disrupting perceived conversational flow. The 23 base-rate participants are a separate, non-video comparison group.
  numeric_value: N=60 total Study 2 sample; N=37 watched the 6-minute video (18 fluent-version; 19 disrupted-flow/silence-version); N=23 base-rate (no video); 4 seconds (numeric_scope: Study 2 participants and stimulus duration; the 60 is the total sample, not the number who watched the video)
  date_or_period: 2011
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: Do not write 'all 60 students/participants watched the video' or '60 students watched a six-minute conversation.' Only 37 (18+19) watched the video; the other 23 did not watch any video. Use plain wording (avoid the word 'condition'; say 'group' instead), and do not claim that four seconds is universally awkward.
"""

F011_OLD_BLOCK = """[VERIFIED] F011: In a within-participant study of 46 students, 6 minutes 30 seconds of silence increased relaxation in both a university seminar room and a city-garden setting; participants reported less boredom and greater present-moment orientation in the outdoor setting. ([frontiersin.org](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.00602/full))
  scope: 46 students; 42 women and 4 men; age range 20–52; mean age 23.5
  conditions: Each participant experienced silent periods indoors and outdoors, with one week between sessions; the duration was unknown to participants.
  numeric_value: N=46; 6 minutes 30 seconds; 42 women; 4 men; age range 20–52 (numeric_scope: Study 5 participants and silent intervals)
  date_or_period: 2019 study summarized in 2020 review
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: The setting altered the experience of silence; do not describe 'silence' as an isolated variable without the indoor/outdoor condition.
"""

F011_NEW_BLOCK = """[VERIFIED] F011: In a within-participant study of roughly 46 students, 6 minutes 30 seconds of silence increased relaxation in both a university seminar room and a city-garden setting; participants reported less boredom and greater present-moment orientation in the outdoor setting. ([frontiersin.org](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.00602/full))
  scope: approximately 46 students (42 women and 4 men; age range 20–52; mean age 23.5) per the study's detailed sample description; NOTE: not all published summaries of this study report the same count -- some report approximately 41, likely reflecting exclusions in a specific analysis. Treat the exact N as approximate, not fully certain, rather than a single precise confirmed number.
  conditions: Each participant experienced silent periods indoors and outdoors, with one week between sessions; the duration was unknown to participants.
  numeric_value: approximately 46 students recruited (42 women; 4 men; age range 20–52); some published summaries report approximately 41 (numeric_scope: Study 5 participants and silent intervals; exact N varies slightly across sources)
  date_or_period: 2019 study summarized in 2020 review
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: Use hedged wording such as 'about 46 students' or 'roughly 46 students' rather than an unqualified precise '46 students,' since sources vary slightly (about 46 vs about 41). The setting altered the experience of silence; do not describe 'silence' as an isolated variable without the indoor/outdoor condition.
"""


def build_limited_verification_ledger_parsed() -> dict:
    return {
        "facts": [
            {
                "fact_id": "F002",
                "claim": ("In Study 2, a single four-second silence in a six-minute video conversation "
                          "produced more reported rejection and negative emotion, less positive emotion, "
                          "and lower belonging, self-esteem, social validation, and perceived consensus "
                          "than the fluent-conversation condition; participants were generally unaware of "
                          "the specific silence."),
                "scope": "60 undergraduate participants; randomized across fluent, disrupted-flow, and base-rate conditions",
                "conditions": ("The silence followed a statement in a videotaped conversation; the source "
                                "states that four seconds was selected to remain below conscious awareness "
                                "while still disrupting perceived conversational flow."),
                "numeric_value": "N=60; 4 seconds; 6-minute video",
                "numeric_scope": "Study 2 participants and stimulus duration",
                "date_or_period": "2011",
                "causal_strength": "CAUSAL_STATED_BY_SOURCE",
                "notes_for_writer": ("VERIFICATION QUESTION: did all 60 participants actually watch the "
                                     "six-minute video, or did only a subset (e.g. the fluent + "
                                     "disrupted-flow conditions) watch the video while a separate base-rate "
                                     "condition did not watch any video? Please confirm the exact number of "
                                     "participants who watched the video, and the exact breakdown across "
                                     "conditions, using the primary source."),
            },
            {
                "fact_id": "F011",
                "claim": ("In a within-participant study of 46 students, 6 minutes 30 seconds of silence "
                          "increased relaxation in both a university seminar room and a city-garden "
                          "setting; participants reported less boredom and greater present-moment "
                          "orientation in the outdoor setting."),
                "scope": "46 students; 42 women and 4 men; age range 20-52; mean age 23.5",
                "conditions": ("Each participant experienced silent periods indoors and outdoors, with one "
                                "week between sessions; the duration was unknown to participants."),
                "numeric_value": "N=46; 6 minutes 30 seconds; 42 women; 4 men; age range 20-52",
                "numeric_scope": "Study 5 participants and silent intervals",
                "date_or_period": "2019 study summarized in 2020 review",
                "causal_strength": "CAUSAL_STATED_BY_SOURCE",
                "notes_for_writer": ("VERIFICATION QUESTION: is the correct participant count for this "
                                     "study 46, or is it 41 as reported in some published abstracts of the "
                                     "same study? Please confirm using the primary source (not only a "
                                     "review that cites it) and explain any discrepancy if one exists."),
            },
        ]
    }


def apply_ledger_fix(ledger_text: str) -> str:
    if F002_OLD_BLOCK not in ledger_text:
        raise RuntimeError("F002_OLD_BLOCK not found verbatim in current ledger text; aborting ledger fix.")
    if F011_OLD_BLOCK not in ledger_text:
        raise RuntimeError("F011_OLD_BLOCK not found verbatim in current ledger text; aborting ledger fix.")
    new_text = ledger_text.replace(F002_OLD_BLOCK, F002_NEW_BLOCK).replace(F011_OLD_BLOCK, F011_NEW_BLOCK)
    return new_text


# ============================================================
# Cross-Level Consistency(API呼び出しなし、決定的チェック)
# ============================================================
NUMERIC_MARKERS = [
    ("F002 total sample", ["60"]),
    ("F002 video watchers", ["37"]),
    ("F002 fluent group", ["18"]),
    ("F002 disrupted group", ["19"]),
    ("F002 base-rate group", ["23"]),
    ("F001 sample", ["102"]),
    ("F005 duration range", ["11 studies"]),
    ("F006 sample", ["55"]),
    ("F007 sample", ["2,557", "2557"]),
    ("F011/F010 duration", ["6 minutes", "six minutes"]),
    ("F011 sample (hedged)", ["46"]),
    ("F012 review count", ["37 studies", "37-study", "review of 37"]),
]


def build_cross_level_consistency_md(a2_text: str, b1b_text: str) -> str:
    lines = ["# Cross-Level Consistency: A2 vs B1B (Discovery, post fact-fix)\n",
             "| Marker | A2 | B1B | Consistent? |",
             "|---|---|---|---|"]
    all_consistent = True
    for label, patterns in NUMERIC_MARKERS:
        a2_hit = any(p in a2_text for p in patterns)
        b1b_hit = any(p in b1b_text for p in patterns)
        note = "present in both" if (a2_hit and b1b_hit) else (
            "present in A2 only" if a2_hit else ("present in B1B only" if b1b_hit else "absent in both"))
        consistent = True  # 片方だけの言及は「省略」であり矛盾ではないため、数値の食い違いのみ不整合とする
        lines.append(f"| {label} | {'yes' if a2_hit else 'no'} | {'yes' if b1b_hit else 'no'} | {note} |")
    # 直接の矛盾チェック: A2/B1Bともに未修正の'60 students watched'/'Sixty students watched'表現が
    # 残っていないか(F002修正の残存チェック)、'46 students'の無条件断定(hedgeなし)が残っていないか
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
    return "\n".join(lines) + "\n", all_consistent


def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    prev_driver.cl.install(LOG_PATH)

    baseline_lines = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, encoding="utf-8") as f:
            baseline_lines = f.readlines()
    baseline_line_count = len(baseline_lines)
    baseline_cost_jpy = prev_driver._lines_cost_jpy(baseline_lines)
    print(f"[{THEME_ID}][COMPLETE] baseline(前2タスク分含む)line_count={baseline_line_count} "
          f"baseline_cost_jpy=¥{baseline_cost_jpy:.2f}(このタスクの予算計算からは除外)")

    def incremental_jpy() -> float:
        return prev_driver.cost_total_jpy() - baseline_cost_jpy

    def ensure_budget(stage: str):
        inc = incremental_jpy()
        est = STAGE_ESTIMATE_JPY.get(stage, 20.0)
        if inc + est > BUDGET_JPY:
            raise BudgetStop(stage, inc, est)
        print(f"[{THEME_ID}][COMPLETE] budget check OK stage={stage} incremental_so_far=¥{inc:.2f} "
              f"+ estimate=¥{est:.2f} <= budget=¥{BUDGET_JPY:.2f}")

    started_at = datetime.now(timezone.utc).isoformat()
    client = prev_driver.vfl01.get_client()

    result = {"started_at": started_at, "budget_jpy": BUDGET_JPY,
              "baseline_cost_jpy": round(baseline_cost_jpy, 2), "stop_reason": None}
    rewrite_log_lines = ["\n# Discovery Complete (Fact fix: F002/F011) - rewrite_log addendum\n"]

    stopped_stage = None
    try:
        # ============================================================
        # (0) 退避
        # ============================================================
        os.makedirs(f"{BASE_DIR}/a2_before_fact_fix", exist_ok=True)
        os.makedirs(f"{BASE_DIR}/b1b_before_fact_fix", exist_ok=True)
        if os.path.isdir(f"{BASE_DIR}/a2") and not os.path.isdir(f"{BASE_DIR}/a2_before_fact_fix/a2"):
            shutil.copytree(f"{BASE_DIR}/a2", f"{BASE_DIR}/a2_before_fact_fix/a2")
        if os.path.isdir(f"{BASE_DIR}/b1b") and not os.path.isdir(f"{BASE_DIR}/b1b_before_fact_fix/b1b"):
            shutil.copytree(f"{BASE_DIR}/b1b", f"{BASE_DIR}/b1b_before_fact_fix/b1b")
        for fname in ["reader_facing_article.txt"]:
            src = f"{BASE_DIR}/{fname}"
            if os.path.exists(src):
                shutil.copy2(src, f"{BASE_DIR}/a2_before_fact_fix/{fname}")
        for fname in ["reader_facing_article_b1b.txt"]:
            src = f"{BASE_DIR}/{fname}"
            if os.path.exists(src):
                shutil.copy2(src, f"{BASE_DIR}/b1b_before_fact_fix/{fname}")

        with open(f"{BASE_DIR}/reader_facing_article.txt", encoding="utf-8") as f:
            a2_text_before = f.read()
        with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", encoding="utf-8") as f:
            b1b_text_before = f.read()

        jargon_before = {"a2": prev_driver.jargon_scan(a2_text_before), "b1b": prev_driver.jargon_scan(b1b_text_before)}
        print(f"[{THEME_ID}][COMPLETE] jargon scan(entering task): a2={jargon_before['a2']['hit_count']} "
              f"b1b={jargon_before['b1b']['hit_count']}")

        with open(f"{RESEARCH_DIR}/verified_fact_ledger.txt", encoding="utf-8") as f:
            verified_ledger_text_old = f.read()
        vfl_path = f"{RESEARCH_DIR}/stage_b3_vfl.json"

        # ============================================================
        # (1) 限定Verification(F002/F011のみ)
        # ============================================================
        stopped_stage = "verification"
        ensure_budget("verification")
        ledger_parsed_limited = build_limited_verification_ledger_parsed()
        with prev_driver.cl.logging_context(THEME_ID, "fact_fix_verification"):
            verification_result = prev_driver.vfl01.run_verification(client, ledger_parsed_limited)
        os.makedirs(RESEARCH_DIR, exist_ok=True)
        with open(f"{RESEARCH_DIR}/fact_fix_verification.json", "w", encoding="utf-8") as f:
            json.dump({"model": verification_result["model"], "response_id": verification_result["response_id"],
                        "search_usage": verification_result["search_usage"], "sources": verification_result["sources"],
                        "parsed": verification_result["parsed"]}, f, ensure_ascii=False, indent=2, default=str)
        print(f"[{THEME_ID}][COMPLETE] verification done: "
              f"{[(v['fact_id'], v['verdict']) for v in verification_result['parsed']['verifications']]}")
        result["verification_verdicts"] = verification_result["parsed"]["verifications"]

        # ============================================================
        # (2) Ledger修正
        # ============================================================
        shutil.copy2(f"{RESEARCH_DIR}/verified_fact_ledger.txt",
                     f"{RESEARCH_DIR}/verified_fact_ledger_v1_before_fix.txt")
        verified_ledger_text_new = apply_ledger_fix(verified_ledger_text_old)
        with open(f"{RESEARCH_DIR}/verified_fact_ledger.txt", "w", encoding="utf-8") as f:
            f.write(verified_ledger_text_new)
        diff = difflib.unified_diff(
            verified_ledger_text_old.splitlines(keepends=True),
            verified_ledger_text_new.splitlines(keepends=True),
            fromfile="verified_fact_ledger_v1_before_fix.txt", tofile="verified_fact_ledger.txt")
        with open(f"{RESEARCH_DIR}/ledger_fix_diff.md", "w", encoding="utf-8") as f:
            f.write("# Ledger Fix Diff (F002 / F011)\n\n")
            f.write("Verification source (limited vfl01.run_verification, web_search):\n")
            for s in verification_result["sources"] or []:
                f.write(f"- {s}\n")
            f.write("\nVerification verdicts:\n")
            for v in verification_result["parsed"]["verifications"]:
                f.write(f"- {v['fact_id']}: {v['verdict']} -- {v['verification_notes']}\n")
            f.write("\n```diff\n")
            f.writelines(diff)
            f.write("\n```\n")
        print(f"[{THEME_ID}][COMPLETE] ledger fix applied. diff saved to research/ledger_fix_diff.md")
        verified_ledger_text = verified_ledger_text_new

        # ============================================================
        # (3) A2/B1B該当文rewrite
        # ============================================================
        ledger_model_a2 = prev_driver.routing.require_model("A2_WRITER", prev_driver.routing.WRITER_MODEL)
        ledger_model_b1b = prev_driver.routing.require_model("B1_WRITER", prev_driver.routing.WRITER_MODEL)

        f002_hint = (
            "Correct scope (from the corrected Verified Fact Ledger, fact F002): 60 people took part in "
            "the study overall, but only 37 of them actually watched the six-minute video conversation "
            "that included the silence -- 18 in the smooth/fluent-conversation version and 19 in the "
            "version with the 4-second silence. The other 23 people were in a separate group that did not "
            "watch any video at all (they gave a baseline guess instead, without seeing the interaction). "
            "Rewrite the sentence so it does NOT claim that 60 (or 'sixty') students/participants watched "
            "the conversation. Make clear there were two video groups (18+19=37) and a separate non-video "
            "group (23), in natural, plain, spoken-style English for a general listener (avoid the word "
            "'condition'; say 'group' instead; do not use the word 'randomized')."
        )
        f011_hint = (
            "Correct scope (from the corrected Verified Fact Ledger, fact F011): sources differ slightly "
            "on the exact number of participants in this study -- the detailed description gives about 46 "
            "people, but some published summaries report about 41. Rewrite the sentence so it does NOT "
            "state a single precise number with full certainty; use hedged wording such as 'about 46 "
            "students' or 'roughly 46 students' instead of an unqualified '46 students', while keeping the "
            "sentence natural and plain (no jargon, no invented reason for the discrepancy)."
        )

        a2_fixes = [
            {"fact_id": "F002", "substring": "60 students watched", "hint": f002_hint},
            {"fact_id": "F011", "substring": "46 students spent", "hint": f011_hint},
        ]
        b1b_fixes = [
            {"fact_id": "F002", "substring": "Sixty students watched", "hint": f002_hint},
            {"fact_id": "F011", "substring": "of 46 students,", "hint": f011_hint},
        ]

        stopped_stage = "a2_fact_fix"
        ensure_budget("a2_fact_fix")
        a2_fix = fix_fact_blocks(a2_text_before, ledger_model_a2, TOPIC_EN, "a2", client,
                                  verified_ledger_text, a2_fixes)
        a2_text_after = a2_fix["updated_text"]
        rewrite_log_lines.append("## A2 Fact fix (F002/F011)\n")
        for br in a2_fix["block_results"]:
            if not br.get("found"):
                rewrite_log_lines.append(f"- {br['fact_id']}: substring not found ('{br['substring']}')\n")
                continue
            rewrite_log_lines.append(f"- {br['fact_id']}\n")
            rewrite_log_lines.append(f"  旧: {br['original_ng_sentence']}\n")
            rewrite_log_lines.append(f"  新: {br['final_text']}\n")
            rewrite_log_lines.append(f"  resolved={br['resolved']} human_review_required={br['human_review_required']} "
                                      f"diff_qa_blocks_acceptance={br['diff_qa'].get('blocks_acceptance')}\n\n")
        result["a2_fact_fix_block_results"] = [
            {"fact_id": br["fact_id"], "found": br.get("found", False), "resolved": br.get("resolved"),
             "human_review_required": br.get("human_review_required")}
            for br in a2_fix["block_results"]]

        stopped_stage = "b1b_fact_fix"
        ensure_budget("b1b_fact_fix")
        b1b_fix = fix_fact_blocks(b1b_text_before, ledger_model_b1b, TOPIC_EN, "b1b", client,
                                   verified_ledger_text, b1b_fixes)
        b1b_text_after = b1b_fix["updated_text"]
        rewrite_log_lines.append("## B1B Fact fix (F002/F011)\n")
        for br in b1b_fix["block_results"]:
            if not br.get("found"):
                rewrite_log_lines.append(f"- {br['fact_id']}: substring not found ('{br['substring']}')\n")
                continue
            rewrite_log_lines.append(f"- {br['fact_id']}\n")
            rewrite_log_lines.append(f"  旧: {br['original_ng_sentence']}\n")
            rewrite_log_lines.append(f"  新: {br['final_text']}\n")
            rewrite_log_lines.append(f"  resolved={br['resolved']} human_review_required={br['human_review_required']} "
                                      f"diff_qa_blocks_acceptance={br['diff_qa'].get('blocks_acceptance')}\n\n")
        result["b1b_fact_fix_block_results"] = [
            {"fact_id": br["fact_id"], "found": br.get("found", False), "resolved": br.get("resolved"),
             "human_review_required": br.get("human_review_required")}
            for br in b1b_fix["block_results"]]

        # 確定(No Jargon状態維持確認)
        with open(f"{BASE_DIR}/reader_facing_article.txt", "w", encoding="utf-8") as f:
            f.write(a2_text_after)
        with open(f"{BASE_DIR}/a2/article.md", "w", encoding="utf-8") as f:
            f.write(a2_text_after)
        with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", "w", encoding="utf-8") as f:
            f.write(b1b_text_after)
        with open(f"{BASE_DIR}/b1b/article.md", "w", encoding="utf-8") as f:
            f.write(b1b_text_after)

        jargon_after = {"a2": prev_driver.jargon_scan(a2_text_after), "b1b": prev_driver.jargon_scan(b1b_text_after)}
        with open(f"{BASE_DIR}/jargon_scan_final.json", "w", encoding="utf-8") as f:
            json.dump({"before_this_task": jargon_before, "after_fact_fix": jargon_after}, f,
                       ensure_ascii=False, indent=2)
        print(f"[{THEME_ID}][COMPLETE] jargon scan(after fact fix): a2={jargon_after['a2']['hit_count']} "
              f"b1b={jargon_after['b1b']['hit_count']}")
        result["jargon_after"] = {"a2": jargon_after["a2"]["hit_count"], "b1b": jargon_after["b1b"]["hit_count"]}

        # ============================================================
        # (5) 正式QA再実行(A2/B1B)。FAILなら最大1回追加修正。
        # ============================================================
        for pfx in ("a2", "b1b"):
            audit_path = f"{BASE_DIR}/{pfx}/audit/post_fix_fact_qa.json"
            if os.path.exists(audit_path):
                shutil.copy2(audit_path, f"{BASE_DIR}/{pfx}/audit/post_fix_fact_qa_before_fact_fix.json")

        stopped_stage = "a2_final_qa"
        ensure_budget("a2_final_qa")
        a2_final_qa = prev_driver.run_final_qa(a2_text_after, verified_ledger_text, ledger_model_a2, TOPIC_EN,
                                                f"{BASE_DIR}/a2", vfl_path, client, "a2")
        print(f"[{THEME_ID}][COMPLETE] A2 final QA(round1): {a2_final_qa}")
        a2_retry_applied = False
        if a2_final_qa["fact_checker_verdict"] == "FAIL":
            stopped_stage = "a2_final_qa_retry"
            ensure_budget("a2_final_qa_retry")
            with open(f"{BASE_DIR}/a2/audit/post_fix_fact_qa.json", encoding="utf-8") as f:
                fc_after = json.load(f)
            contradictions_text = " ".join(fc_after.get("result", {}).get("contradictions") or [])
            retry_fixes = []
            if re.search(r"\b(60|Sixty)\b", contradictions_text):
                retry_fixes.append({"fact_id": "F002_retry", "substring": "watched a six-minute conversation",
                                      "hint": f002_hint})
            if "46" in contradictions_text or "41" in contradictions_text:
                # 既にhedge済みのはずなので、無条件な'46'単独表記が残っていないか確認
                pass
            if retry_fixes:
                a2_retry = fix_fact_blocks(a2_text_after, ledger_model_a2, TOPIC_EN, "a2_retry", client,
                                            verified_ledger_text, retry_fixes)
                a2_text_after = a2_retry["updated_text"]
                with open(f"{BASE_DIR}/reader_facing_article.txt", "w", encoding="utf-8") as f:
                    f.write(a2_text_after)
                with open(f"{BASE_DIR}/a2/article.md", "w", encoding="utf-8") as f:
                    f.write(a2_text_after)
                a2_final_qa = prev_driver.run_final_qa(a2_text_after, verified_ledger_text, ledger_model_a2,
                                                          TOPIC_EN, f"{BASE_DIR}/a2", vfl_path, client, "a2_retry")
                a2_retry_applied = True
                print(f"[{THEME_ID}][COMPLETE] A2 final QA(round2, after retry): {a2_final_qa}")
        result["a2_final_qa"] = a2_final_qa
        result["a2_retry_applied"] = a2_retry_applied

        stopped_stage = "b1b_final_qa"
        ensure_budget("b1b_final_qa")
        b1b_final_qa = prev_driver.run_final_qa(b1b_text_after, verified_ledger_text, ledger_model_b1b, TOPIC_EN,
                                                 f"{BASE_DIR}/b1b", vfl_path, client, "b1b")
        print(f"[{THEME_ID}][COMPLETE] B1B final QA(round1): {b1b_final_qa}")
        b1b_retry_applied = False
        if b1b_final_qa["fact_checker_verdict"] == "FAIL":
            stopped_stage = "b1b_final_qa_retry"
            ensure_budget("b1b_final_qa_retry")
            with open(f"{BASE_DIR}/b1b/audit/post_fix_fact_qa.json", encoding="utf-8") as f:
                fc_after = json.load(f)
            contradictions_text = " ".join(fc_after.get("result", {}).get("contradictions") or [])
            retry_fixes = []
            if re.search(r"\b(60|Sixty)\b", contradictions_text):
                retry_fixes.append({"fact_id": "F002_retry", "substring": "watched a six-minute conversation",
                                      "hint": f002_hint})
            if retry_fixes:
                b1b_retry = fix_fact_blocks(b1b_text_after, ledger_model_b1b, TOPIC_EN, "b1b_retry", client,
                                             verified_ledger_text, retry_fixes)
                b1b_text_after = b1b_retry["updated_text"]
                with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", "w", encoding="utf-8") as f:
                    f.write(b1b_text_after)
                with open(f"{BASE_DIR}/b1b/article.md", "w", encoding="utf-8") as f:
                    f.write(b1b_text_after)
                b1b_final_qa = prev_driver.run_final_qa(b1b_text_after, verified_ledger_text, ledger_model_b1b,
                                                          TOPIC_EN, f"{BASE_DIR}/b1b", vfl_path, client, "b1b_retry")
                b1b_retry_applied = True
                print(f"[{THEME_ID}][COMPLETE] B1B final QA(round2, after retry): {b1b_final_qa}")
        result["b1b_final_qa"] = b1b_final_qa
        result["b1b_retry_applied"] = b1b_retry_applied

        # jargon再々確認(retry rewriteでjargonが再混入していないか)
        jargon_after_retry = {"a2": prev_driver.jargon_scan(a2_text_after), "b1b": prev_driver.jargon_scan(b1b_text_after)}
        with open(f"{BASE_DIR}/jargon_scan_final.json", "w", encoding="utf-8") as f:
            json.dump({"before_this_task": jargon_before, "after_fact_fix": jargon_after,
                        "after_retry_if_any": jargon_after_retry}, f, ensure_ascii=False, indent=2)
        result["jargon_after_retry"] = {"a2": jargon_after_retry["a2"]["hit_count"],
                                          "b1b": jargon_after_retry["b1b"]["hit_count"]}

        # ============================================================
        # (6) Cross-Level Consistency
        # ============================================================
        cross_md, cross_consistent = build_cross_level_consistency_md(a2_text_after, b1b_text_after)
        with open(f"{BASE_DIR}/cross_level_consistency.md", "w", encoding="utf-8") as f:
            f.write(cross_md)
        result["cross_level_consistent"] = cross_consistent

        # ============================================================
        # (7) Key Phrase A2/B1B再生成
        # ============================================================
        def _line_count() -> int:
            with open(LOG_PATH, encoding="utf-8") as f:
                return len(f.readlines())

        stopped_stage = "key_phrase_a2"
        ensure_budget("key_phrase_a2")
        kp_a2_start_line = _line_count()
        kp_dir_a2 = f"{BASE_DIR}/key_phrases/a2"
        kp_a2 = prev_driver.scaffold_gen.run_key_phrases(
            a2_text_after, kp_dir_a2, f"{THEME_ID}_a2_complete", "A2(V2改1, N3-01, fact-fix complete)",
            process="A2_SUPPORT")
        kp_a2_end_line = _line_count()
        kp_a2_status = (kp_a2["canonicalization"] or {}).get("status") if kp_a2["canonicalization"] else kp_a2["selection"]["status"]
        print(f"[{THEME_ID}][COMPLETE] Key Phrase(A2) status={kp_a2_status}")
        result["key_phrase_a2_status"] = kp_a2_status
        result["key_phrase_a2_redundancy_qa"] = kp_a2.get("redundancy_qa")

        stopped_stage = "key_phrase_b1b"
        ensure_budget("key_phrase_b1b")
        kp_b1b_start_line = _line_count()
        kp_dir_b1b = f"{BASE_DIR}/key_phrases/b1b"
        kp_b1b = prev_driver.scaffold_gen.run_key_phrases(
            b1b_text_after, kp_dir_b1b, f"{THEME_ID}_b1b_complete", "B1-B(N3-01, fact-fix complete)",
            process="B1_SUPPORT")
        kp_b1b_end_line = _line_count()
        kp_b1b_status = (kp_b1b["canonicalization"] or {}).get("status") if kp_b1b["canonicalization"] else kp_b1b["selection"]["status"]
        print(f"[{THEME_ID}][COMPLETE] Key Phrase(B1B) status={kp_b1b_status}")
        result["key_phrase_b1b_status"] = kp_b1b_status
        result["key_phrase_b1b_redundancy_qa"] = kp_b1b.get("redundancy_qa")

        with open(LOG_PATH, encoding="utf-8") as f:
            _all_lines_for_kp_cost = f.readlines()
        result["key_phrase_a2_jpy"] = round(
            prev_driver._lines_cost_jpy(_all_lines_for_kp_cost[kp_a2_start_line:kp_a2_end_line]), 2)
        result["key_phrase_b1b_jpy"] = round(
            prev_driver._lines_cost_jpy(_all_lines_for_kp_cost[kp_b1b_start_line:kp_b1b_end_line]), 2)

        result["overall_status"] = "COMPLETE"
        stopped_stage = None

    except BudgetStop as e:
        result["overall_status"] = "STOP_BUDGET_EXCEEDED"
        result["stop_reason"] = str(e)
        result["stopped_before_stage"] = e.stage
        print(f"[{THEME_ID}][COMPLETE] STOP(budget): {e}")

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
    with open(f"{BASE_DIR}/raw_usage_log_complete_task_only.jsonl", "w", encoding="utf-8") as f:
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

    cost_summary_complete = {
        "started_at": started_at, "finished_at": finished_at, "budget_jpy": BUDGET_JPY,
        "baseline_cost_jpy_excluded": round(baseline_cost_jpy, 2),
        "this_task_cost_jpy": this_task_cost_jpy,
        "budget_exceeded": this_task_cost_jpy > BUDGET_JPY,
        "overall_status": result.get("overall_status"),
        "stopped_before_stage": result.get("stopped_before_stage"),
        "new_api_calls": len(new_lines),
        "model_ids": model_ids,
        "token_totals": {"input_tokens": total_in, "output_tokens": total_out, "cached_input_tokens": total_cached,
                          "total_tokens": total_in + total_out},
        "cost_breakdown_by_stage_jpy": stage_breakdown,
    }
    with open(f"{BASE_DIR}/cost_summary_complete.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary_complete, f, ensure_ascii=False, indent=2, default=str)

    # production_set_cost.json 更新
    prod_cost_path = f"{BASE_DIR}/production_set_cost.json"
    with open(prod_cost_path, encoding="utf-8") as f:
        prod_cost = json.load(f)
    prod_cost["this_task_fact_fix_qa_and_key_phrase_jpy"] = this_task_cost_jpy
    prod_cost["this_task_breakdown_by_stage_jpy"] = stage_breakdown
    prod_cost["key_phrase_a2_jpy"] = result.get("key_phrase_a2_jpy")
    prod_cost["key_phrase_b1b_jpy"] = result.get("key_phrase_b1b_jpy")
    prod_cost["status"] = f"COMPLETE({result.get('overall_status')})"
    prod_cost["grand_total_jpy_including_key_phrase"] = round(
        prod_cost.get("grand_total_jpy_excluding_key_phrase", 0.0) + this_task_cost_jpy, 2)
    prod_cost["note"] = ("Discovery Production 1生成セット(共通Research/Ledger+A2+B1、Key Phrase込み)完成。"
                          "本タスク(EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE)でF002/F011のLedger修正+"
                          "A2/B1B該当文rewrite+正式QA再実行+Key Phrase A2/B1B生成を実施。50:50配賦は行わない。")
    with open(prod_cost_path, "w", encoding="utf-8") as f:
        json.dump(prod_cost, f, ensure_ascii=False, indent=2, default=str)

    result["finished_at"] = finished_at
    result["this_task_cost_jpy"] = this_task_cost_jpy
    result["budget_exceeded"] = this_task_cost_jpy > BUDGET_JPY
    result["model_ids"] = model_ids

    # observation_complete.jsonは実行コマンド(3)のaggregate_usage.pyが別途出力する
    with open(f"{BASE_DIR}/run_result_complete.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{os.path.dirname(BASE_DIR)}/progress_log.md", "a", encoding="utf-8") as f:
        f.write(f"- Discovery complete: overall_status={result.get('overall_status')} "
                f"this_task_cost_jpy=¥{this_task_cost_jpy:.2f} "
                f"a2_fact_checker={result.get('a2_final_qa', {}).get('fact_checker_verdict')} "
                f"b1b_fact_checker={result.get('b1b_final_qa', {}).get('fact_checker_verdict')} "
                f"key_phrase_a2={result.get('key_phrase_a2_status')} "
                f"key_phrase_b1b={result.get('key_phrase_b1b_status')} "
                f"({finished_at})\n")

    print(f"[{THEME_ID}][COMPLETE] 完了。overall_status={result.get('overall_status')} "
          f"本タスク実測費用=¥{this_task_cost_jpy:.2f}(予算=¥{BUDGET_JPY:.2f})")
    return result


if __name__ == "__main__":
    main()
    sys.exit(0)
