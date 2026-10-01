# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_element_trial_meta_hook_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_28 Part2 Meta要素Trial B[Hook許容
# 基準] + Part3 Trial C[未確認actor置換の抑止])
# ============================================================
# 目的:
# Trial B: Hook専用Stage2 rubric(HOOK_RUBRIC_WITH_MISCONCEPTION_
#   PRINCIPLE_V2、委任_28 Part0-3のtie-break明文化)+ Stage1(V4A、重大
#   誤解原則配線)が、Meta Muse記事の実際のHook段落(neg1 cycle1、disclosure
#   doc`docs/pm/open233_evidence_disclosure_neg1_neg3_hormuz_01.md`§1逐語
#   引用)の許容群(5)・境界群(1、演出強め)・NG群(4、未確認の人物/行動/
#   数字/事実反転)を正しく分けるかを実測する。
# Trial C: neg1 cycle2(MUSE-HC-012、実データ、同disclosure doc)で実際に
#   Stage1 floorを発火させた"The test began without clearly telling users
#   that contract workers would make the calls."が、Stage1(V4A)へ重大
#   誤解原則を配線した後も同じ結果になるか(§1「社内テスト誤読」仮説の
#   検証)、およびBLOCKING維持と仮定した場合にStage3主体置換ガード
#   (`actor_rewrite_guard_ok`、委任_27 Part1-3)が実際にどう動くかを実測
#   する。NG対照(VP→CEOの主体入替、真の誤認)も併せて確認する。
#
# 重要な設計制約・事故是正(委任_28中にPart1で発生した事故の教訓を踏襲):
# - `er052_open233_self_recovery_flow_runner_01`(以下runner)の
#   `record_call`/`save_budget_state`は、呼び出し元が渡すstate dictの
#   中身に関わらずrunner自身の固定`BUDGET_STATE_PATH`(他delegationの
#   既存証跡)へ書き込む副作用を持つ。本ファイルがrunnerのAPI呼び出し
#   ヘルパー(`single_text_rewrite`/`run_local_qa`)を再利用する箇所では、
#   `unittest.mock.patch.object(runner, "save_budget_state", lambda s: None)`
#   で必ずこの副作用を遮断する(costの記録自体は渡したstate dictへ
#   正しく蓄積されるため、計測は失われない)。Stage1 fresh呼び出しは
#   runnerの関数を使わず、本ファイル専用の自己完結ラッパーを使う。
# - Production code(er003/er009/er010/er012/er019)は一切変更しない。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
# - 保存jsonにはprompt本体ではなくsha256のみ記録。
# - claim_textは全て実データ逐語引用、または委任文が明示したNG例文
#   そのもの(捏造Ledger factは無い)。
from __future__ import annotations

import argparse
import json
import os
import time
from unittest import mock

import er003_v1_en_direct_vfl_01_generate as vfl01
import er050_gpt6_checker_comparison_trial_01 as g6
import er051_open233_checker_trial_variant_01 as trial
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_stage2_hook_01 as s2h
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_element_trial_meta_hook_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233ae.json"
TOTAL_BUDGET_JPY = 15.0  # 委任_28 Part2(≤¥10)+Part3(≤¥5)の合算Guardrail
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3

TITLE = "# We Thought It Was AI—But There Was a Person Inside Meta's Muse"
IN_ONE_LINE = "## In one line\nMeta ran a test about AI phone calls.\n"


class TrialAbort(RuntimeError):
    pass


def load_budget_state() -> dict:
    if os.path.exists(BUDGET_STATE_PATH):
        with open(BUDGET_STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def save_budget_state(state: dict) -> None:
    os.makedirs(os.path.dirname(BUDGET_STATE_PATH), exist_ok=True)
    with open(BUDGET_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_budget(state: dict) -> None:
    if state["cumulative_jpy"] >= TOTAL_BUDGET_JPY:
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.4f}が委任_28 Part2+3 Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def record(state: dict, consecutive_errors: list, label: str, cost: float, ok: bool) -> None:
    state["cumulative_calls"] += 1
    if ok:
        state["cumulative_jpy"] += cost
        state["history"].append({"label": label, "cost_jpy": cost})
        consecutive_errors[0] = 0
    else:
        state["cumulative_errors"] += 1
        consecutive_errors[0] += 1
    save_budget_state(state)
    if consecutive_errors[0] >= MAX_CONSECUTIVE_ERRORS:
        raise TrialAbort(f"API errorが{MAX_CONSECUTIVE_ERRORS}call連続(STOP条件)")


def stage1_fresh_misconception_local(client, state, consecutive_errors, label, fixture) -> dict:
    """事故是正済み自己完結版Stage1 fresh呼び出し(上記冒頭コメント・
    er052_open233_element_trial_safety_control_01.pyと同一方式)。"""
    check_budget(state)
    last_err = None
    result = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = trial.run_trial_deviation_check(
                client, fixture["ledger_text"], fixture["article_text"], s2p.MODEL, "V4A",
                include_related_fact_id=True, source_article_text=fixture.get("source_article_text"),
                developer_message_override=trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE,
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    if result is not None:
        cost = round(s2p.official_cost_jpy(result["usage"]), 4)
        record(state, consecutive_errors, label, cost, True)
        return result["parsed"]
    record(state, consecutive_errors, label, 0.0, False)
    return {"overall_status": "LEDGER_DEVIATION", "deviations": [], "_stage1_api_failure": True,
            "_error": last_err}


# ------------------------------------------------------------
# Trial B(Part2): Hook claim variants
# ------------------------------------------------------------
NEG1_ORIGINAL_HOOK = (
    "A call seemed to come from an AI agent. But as the conversation went on, the voice "
    "was not AI at all. It was a person. Meta had run a test that caused exactly this surprise."
)

HOOK_CLAIMS = [
    {"group": "accept", "sub_id": "accept-1-original-hook", "claim_text": NEG1_ORIGINAL_HOOK, "n_runs": 3},
    {"group": "accept", "sub_id": "accept-2-experience-para-1",
     "claim_text": "You pick up. The voice sounds human—because it is.", "n_runs": 2},
    {"group": "accept", "sub_id": "accept-3-experience-para-2",
     "claim_text": "The person on the other end of the line was real, not artificial—even though "
                   "the call began just like any other call through Muse.", "n_runs": 2},
    {"group": "accept", "sub_id": "accept-4-scene-depiction",
     "claim_text": "Ring, ring. The phone connects, and for a moment neither side lets on who is "
                   "really speaking.", "n_runs": 2},
    {"group": "accept", "sub_id": "accept-5-conversational-restatement",
     "claim_text": "Imagine getting a call from Muse and finding a real person on the line.",
     "n_runs": 2},
    {"group": "boundary", "sub_id": "boundary-1-dramatization",
     "claim_text": "The surprise came halfway through the call.", "n_runs": 2},
    {"group": "ng", "sub_id": "ng-1-unconfirmed-person",
     "claim_text": "Mark Zuckerberg himself made some of the calls.", "n_runs": 2},
    {"group": "ng", "sub_id": "ng-2-unconfirmed-action",
     "claim_text": "Workers read from a secret script to hide that they were human.", "n_runs": 2},
    {"group": "ng", "sub_id": "ng-3-unconfirmed-number",
     "claim_text": "About 40% of Muse calls were made by humans.", "n_runs": 2},
    {"group": "ng", "sub_id": "ng-4-fact-reversal",
     "claim_text": "Meta said every call was fully AI.", "n_runs": 2},
]


def build_hook_article(claim_text: str) -> str:
    return f"{TITLE}\n\n{claim_text}\n\n{IN_ONE_LINE}"


def run_trial_b(client, state, consecutive_errors, meta_fixture) -> dict:
    max_n = max(c["n_runs"] for c in HOOK_CLAIMS)
    articles = {c["sub_id"]: build_hook_article(c["claim_text"]) for c in HOOK_CLAIMS}

    # --- Stage1 fresh(claim毎に専用の短い合成記事、n=claimごとのn_runs) ---
    stage1_rows = []
    for c in HOOK_CLAIMS:
        fixture = {"ledger_text": meta_fixture["ledger_text"], "article_text": articles[c["sub_id"]],
                   "source_article_text": meta_fixture.get("source_article_text")}
        run_records = []
        for run_idx in range(1, c["n_runs"] + 1):
            label = f"partB_stage1fresh_{c['sub_id']}_run{run_idx}"
            save_path = f"{OUT_DIR}/trialB_stage1/{c['sub_id']}/run_{run_idx}.json"
            parsed = stage1_fresh_misconception_local(client, state, consecutive_errors, label, fixture)
            save_json(save_path, parsed)
            devs = parsed.get("deviations", [])
            match = next((d for d in devs if c["claim_text"].strip()[:40] in (d.get("claim_in_article") or "")
                          or (d.get("claim_in_article") or "").strip()[:40] in c["claim_text"]), None)
            run_records.append({
                "run": run_idx, "overall_status": parsed.get("overall_status"), "n_deviations": len(devs),
                "matched_own_claim_blocking": bool(match and match.get("severity_final") == "BLOCKING"),
                "any_blocking_in_article": any(d.get("severity_final") == "BLOCKING" for d in devs),
                "match_explanation": match.get("explanation") if match else None,
            })
        stage1_rows.append({"sub_id": c["sub_id"], "group": c["group"], "runs": run_records})

    # --- Hook Stage2(全claimを1 batchにまとめ、run数=max_n) ---
    batch_claims = [{"claim_text": c["claim_text"], "origin": "translation",
                      "related_fact_id": "MUSE-HC-006"} for c in HOOK_CLAIMS]
    title_hook_text = f"{TITLE}\n\n{NEG1_ORIGINAL_HOOK}"
    hook_runs = []
    for run_idx in range(1, max_n + 1):
        check_budget(state)
        label = f"partB_hookstage2_run{run_idx}"
        save_path = f"{OUT_DIR}/trialB_hookstage2/run_{run_idx}.json"
        last_err = None
        result = None
        for _ in range(1 + MAX_RETRIES_PER_CALL):
            try:
                result = s2h.run_stage2_hook_batch(
                    client, meta_fixture["ledger_text"], meta_fixture.get("source_article_text"),
                    title_hook_text, batch_claims, model=s2p.MODEL,
                    hook_rubric_text=s2h.HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V2)
                break
            except Exception as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {e}"
                time.sleep(1.0)
        if result is not None:
            record(state, consecutive_errors, label, result["cost_jpy"], True)
            save_json(save_path, result)
            hook_runs.append(result)
        else:
            record(state, consecutive_errors, label, 0.0, False)
            save_json(save_path, {"error": last_err})

    hook_rows = []
    for idx, c in enumerate(HOOK_CLAIMS):
        labels = []
        for run_idx, res in enumerate(hook_runs, start=1):
            if run_idx > c["n_runs"]:
                continue
            judgments = res["parsed"].get("judgments", [])
            match = next((j for j in judgments if j.get("claim_index") == idx), None)
            if match is not None:
                labels.append({"materiality": match["materiality"], "basis": match.get("basis")})
        observed = [lb["materiality"] for lb in labels]
        if c["group"] == "ng":
            wrong = [m for m in observed if m == "BLOCKING"]
            correct_count = len(observed) - len(wrong)
        else:
            wrong = [m for m in observed if m != "BLOCKING"]
            correct_count = len(wrong)
        hook_rows.append({
            "sub_id": c["sub_id"], "group": c["group"], "claim_text": c["claim_text"],
            "hook_stage2_labels": labels, "expected_non_blocking": c["group"] != "ng",
            "false_block_count": (len(wrong) if c["group"] != "ng" else 0),
            "false_pass_count": (len(wrong) if c["group"] == "ng" else 0),
            "variance_across_runs": len(set(observed)) > 1 if observed else False,
        })

    return {
        "stage1_rows": stage1_rows, "hook_stage2_rows": hook_rows,
        "false_block_total": sum(r["false_block_count"] for r in hook_rows),
        "false_pass_total": sum(r["false_pass_count"] for r in hook_rows),
    }


# ------------------------------------------------------------
# Trial C(Part3): 未確認actor置換の抑止(neg1 cycle2実データ)
# ------------------------------------------------------------
# 実データ(er052_output/open233_self_recovery_flow_runner_01_iter7/
# instances_s1/neg1_meta_b3prod_a2.json、cycles[1]["en_text_before_
# rewrite"]、既存証跡、読み取りのみ・本ファイルからは変更しない)。
IT7_S1_PATH = "er052_output/open233_self_recovery_flow_runner_01_iter7/instances_s1/neg1_meta_b3prod_a2.json"

ACTOR_CLAIM_TEXT = "The test began without clearly telling users that contract workers would make the calls."
NG_ACTOR_SENTENCE_ORIGINAL = "A Meta executive admitted the mistake. The test had begun without clearly telling users."
NG_ACTOR_SENTENCE_SWAPPED = "Meta's CEO admitted the mistake. The test had begun without clearly telling users."


def load_neg1_cycle2_article() -> str:
    with open(IT7_S1_PATH, encoding="utf-8") as f:
        d = json.load(f)
    return d["cycles"][1]["en_text_before_rewrite"]


def run_trial_c(client, state, consecutive_errors, meta_fixture) -> dict:
    cycle2_article = load_neg1_cycle2_article()
    ng_article = cycle2_article.replace(NG_ACTOR_SENTENCE_ORIGINAL, NG_ACTOR_SENTENCE_SWAPPED, 1)
    assert ng_article != cycle2_article, "NG対照記事の置換が反映されていない"

    fixture_main = {"ledger_text": meta_fixture["ledger_text"], "article_text": cycle2_article,
                     "source_article_text": meta_fixture.get("source_article_text")}
    fixture_ng = {"ledger_text": meta_fixture["ledger_text"], "article_text": ng_article,
                  "source_article_text": meta_fixture.get("source_article_text")}

    def _run_stage1(fixture, label_prefix, n_runs, needle):
        rows = []
        for run_idx in range(1, n_runs + 1):
            label = f"{label_prefix}_run{run_idx}"
            save_path = f"{OUT_DIR}/trialC_stage1/{label}.json"
            parsed = stage1_fresh_misconception_local(client, state, consecutive_errors, label, fixture)
            save_json(save_path, parsed)
            devs = parsed.get("deviations", [])
            match = next((d for d in devs if needle in (d.get("claim_in_article") or "")), None)
            rows.append({
                "run": run_idx, "overall_status": parsed.get("overall_status"),
                "matched": match is not None,
                "matched_severity_final": match.get("severity_final") if match else None,
                "matched_dev": match,
            })
        return rows

    actor_claim_rows = _run_stage1(fixture_main, "partC_actorclaim", 2, "contract workers would make the calls")
    ng_rows = _run_stage1(fixture_ng, "partC_ngcontrol", 2, "admitted the mistake")

    still_blocking_runs = [r for r in actor_claim_rows if r["matched"] and r["matched_severity_final"] == "BLOCKING"]

    stage3_result = None
    local_qa_result = None
    if still_blocking_runs:
        dev = still_blocking_runs[0]["matched_dev"]
        claim_rec = {
            "claim_text": ACTOR_CLAIM_TEXT, "rewrite_kind": "replace_with_ledger_value",
            "dev": dev, "materiality": "BLOCKING", "basis": dev.get("basis") or "ledger_fact",
            "rewrite_hint": "",
        }
        check_budget(state)
        call_log: list = []
        # 事故是正(本ファイル冒頭コメント参照): runner.single_text_rewrite
        # 自体は変更せず、cost計上の副作用(check_budget/save_budget_state、
        # いずれもrunner自身の固定TOTAL_BUDGET_JPY/BUDGET_STATE_PATHを参照
        # する)のみをこの呼び出しの間だけ無害化する。stateへのcumulative_jpy
        # 加算自体(record_call内)は維持されるため測定値は失われない。
        with mock.patch.object(runner, "save_budget_state", lambda s: None), \
             mock.patch.object(runner, "check_budget", lambda s: None):
            stage3_result = runner.single_text_rewrite(
                client, state, consecutive_errors, call_log, "partC_rewrite", fixture_main,
                "article_text", claim_rec)
        save_json(f"{OUT_DIR}/trialC_stage3_rewrite.json",
                   {"result": stage3_result, "call_log": call_log})
        save_budget_state(state)

        if stage3_result.get("guard_ok") and stage3_result.get("after_fragment"):
            # run_local_qa_fastpathと同一方式: before_ctx/after_ctxは
            # Rewrite後の全文中でafter_fragmentの前後1文を検索して得る
            # (¥0、決定論)。
            before_ctx, located_sentence, after_ctx = runner.find_sentence_context(
                stage3_result["updated_text"], stage3_result["after_fragment"])
            check_budget(state)
            qa_call_log: list = []
            with mock.patch.object(runner, "save_budget_state", lambda s: None), \
                 mock.patch.object(runner, "check_budget", lambda s: None):
                local_qa_result = runner.run_local_qa(
                    client, state, consecutive_errors, qa_call_log, "partC_local_qa",
                    meta_fixture["ledger_text"], dev.get("issue") or dev.get("explanation") or "",
                    before_ctx or "", located_sentence or stage3_result["after_fragment"], after_ctx or "")
            save_json(f"{OUT_DIR}/trialC_local_qa.json",
                       {"result": local_qa_result, "call_log": qa_call_log,
                        "before_ctx": before_ctx, "located_sentence": located_sentence, "after_ctx": after_ctx})
            save_budget_state(state)

    return {
        "actor_claim_rows": actor_claim_rows, "ng_control_rows": ng_rows,
        "still_blocking_run_count": len(still_blocking_runs),
        "stage3_rewrite_result": stage3_result, "local_qa_result": local_qa_result,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip_b", action="store_true")
    parser.add_argument("--skip_c", action="store_true")
    args = parser.parse_args()

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]
    meta_fixture = next(f for f in g6.step2_fixtures() if f["id"] == "Meta_run03_standard")

    stopped, stop_reason = False, None
    trial_b = {}
    trial_c = {}
    try:
        if not args.skip_b:
            trial_b = run_trial_b(client, state, consecutive_errors, meta_fixture)
        if not args.skip_c:
            trial_c = run_trial_c(client, state, consecutive_errors, meta_fixture)
    except TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "trial_b_false_block_total": trial_b.get("false_block_total"),
        "trial_b_false_pass_total": trial_b.get("false_pass_total"),
        "trial_c_still_blocking_run_count": trial_c.get("still_blocking_run_count"),
    }
    save_json(f"{OUT_DIR}/summary_meta_hook.json", {
        "summary": summary, "trial_b": trial_b, "trial_c": trial_c,
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
