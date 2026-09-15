# ============================================================
# er014_output/four_type_observation_01/discovery/run_discovery_a2_ut06_regen.py
# 管理ID: USER-TEST-FINAL-AUDIO-BATCH-06 (A) item2 / (D) FOLLOWUP-01 item5
# ============================================================
# 追記(D、2026-09-15): --only-segments引数を追加。委任Aで16segment中14件
# OK・2件(full_story_part1: silence->pause、point_two: 2,557->2,527)が
# NGだった状態(Assembly未実施)から、ユーザー承認(FOLLOWUP-01 item5)により
# NGの2segmentだけを個別retryする。本文・Support・Key Phraseは無変更、
# 他14segmentのTTS/ASRは再実行しない(既存wavをそのまま再利用)。
# 目的: discovery/a2/article.md(530語版、ユーザー採用済み、本文は再生成
# しない)を固定入力として、既存Production関数のみ(er003_v1_n3_01_
# scaffold_generate.run_a2_scaffold/run_key_phrases、er003_v1_n3_01_
# tts_generate.generate_a2_segments、er003_v1_n3_01_assemble.
# stage_assemble_a2/verify_episode_audio_validation_gate、いずれも無変更)
# で、Key Phrase再選定(Canonicalization+Redundancy QA込み)/Support
# (Preview/Comment)生成/TTS/Assembly/Audio Validation/Web playerまで
# 完走させる。旧604語版由来のaudio/key_phrase artifactは事前に
# discovery/audio/a2_before_regeneration_604w/・discovery/key_phrases/
# a2_before_regeneration_604w/へ退避済み(本スクリプト実行前に完了)。
#
# 既存run_discovery_audio_completion.pyのprepare_key_phrases()は
# 「既存出力をそのままコピー再利用」する設計(A2/B1Bとも過去に既に
# 完成済みだったため)だが、本文が530語版へ変更されているため、まず
# discovery/key_phrases/a2/へ新規Key Phrase選定を行ってから同関数で
# audio/a2/側へコピーする(既存関数は無変更、投入するsource側のみ更新)。
#
# 実行方法:
#   .venv/Scripts/python.exe er014_output/four_type_observation_01/discovery/run_discovery_a2_ut06_regen.py
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_THIS_DIR = os.path.dirname(__file__)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import er003_v1_n3_01_scaffold_generate as sc  # noqa: E402
import er003_v1_n3_01_tts_generate as tts_gen  # noqa: E402
import er005_cost_logger as cl  # noqa: E402
import er011_human_review_lock_01 as review_lock  # noqa: E402
import run_discovery_audio_completion as base  # noqa: E402 (既存driver、無変更で再利用)

TASK_ID = "USER-TEST-FINAL-AUDIO-BATCH-06"
BUDGET_JPY = 80.0
LEVEL = "a2"

# --only-segments用: segment名 -> parts.jsonのキー(canonical本文の参照元)
TARGETABLE_SEGMENTS = {
    "full_story_part1": "part1",
    "point_two": "point_two_body",
}

APPROVE_REASON_DEFAULT = ("user (USER-TEST-FINAL-AUDIO-BATCH-06-FOLLOWUP-01 item5, 2026-09-15 "
                           "explicit approval for individual retry of NG segments "
                           "full_story_part1/point_two only; canonical text/Support/Key Phrase "
                           "unchanged, other 14 segments reused as-is)")


def sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_targeted_retry(only_segments: list[str], approve_reason: str, budget_jpy: float) -> None:
    """委任D: NGだった2segment(full_story_part1/point_two)のみを個別retryする。
    本文・Support・Key Phraseは再生成しない(既存article.md/key_phrasesを
    そのまま使用)。他segmentのTTS/ASRは一切呼ばない(sha256不変を確認)。"""
    level_out_dir = f"{base.OUT_DIR}/{LEVEL}"
    narration_dir = f"{level_out_dir}/narration"
    results_path = f"{level_out_dir}/audit/tts_generation_results.json"
    summary_path = f"{level_out_dir}/run_summary_tts.json"

    cl.install(base.LOG_PATH)
    baseline_cost = base.cost_so_far_jpy()
    print(f"[UT06-D][A2][BUDGET] task開始前の全累積コスト={baseline_cost:.2f} JPY "
          f"(本Part上限=¥{budget_jpy}はこのdriverの新規発生分のみに適用)")

    def check_part_budget(note: str) -> None:
        now = base.cost_so_far_jpy()
        delta = now - baseline_cost
        print(f"[UT06-D][A2][BUDGET] 累積差分={delta:.2f} JPY / 上限={budget_jpy} JPY (次段階: {note})")
        if delta >= budget_jpy:
            raise RuntimeError(
                f"[UT06-D][A2] Part2費用上限到達のためSTOP: 差分={delta:.2f} JPY >= {budget_jpy} JPY "
                f"(次段階「{note}」を実行せず停止)")

    parts = base.load_json(f"{level_out_dir}/parts.json")

    # 他14 segmentのsha256(不変確認用ベースライン)
    all_content_names = list(base.A2_CONTENT_SEGMENT_NAMES)
    kp_names = [f"kp{r}_en" for r in range(1, 6)] + [f"meaning_{r}" for r in range(1, 6)]
    unaffected_names = [n for n in all_content_names if n not in only_segments] + kp_names
    sha_before = {}
    for n in unaffected_names:
        p = f"{narration_dir}/{n}.wav"
        if os.path.exists(p):
            sha_before[n] = sha256_of(p)

    data = base.load_json(results_path)

    retry_results = {}
    try:
        for name in only_segments:
            parts_key = TARGETABLE_SEGMENTS[name]
            text = parts[parts_key]
            if name in ("point_one", "point_two"):
                sc.assert_no_point_number_label(text, name)
            tts_input = tts_gen.tts_safe_news_en(text)
            out_path = f"{narration_dir}/{name}.wav"
            sub = tts_gen.first_words(text)

            check_part_budget(f"approve_regenerate({name})")
            print(f"[UT06-D][A2] Human Review Lock解除(approve_regenerate, {name}、1回限り)。"
                  f"approved_by={approve_reason}")
            approve_entry = review_lock.approve_regenerate(out_path, tts_input, approved_by=approve_reason)
            print(f"[UT06-D][A2] approve_regenerate({name})結果: state={approve_entry.get('state')}")

            check_part_budget(f"TTS retry({name})")
            print(f"[UT06-D][A2] {name} 個別retry(既存Production関数generate_a2_segment_with_slowdown、無変更)...")
            with cl.logging_context(base.THEME_ID, f"tts_a2_ut06d_{name}"):
                result = tts_gen.generate_a2_segment_with_slowdown(
                    tts_input, out_path, sub,
                    style_prefix_override=tts_gen.A2_ENGLISH_STYLE_PREFIX_SLOWER,
                    disfluency_qa=False,
                    enable_connected_speech_equivalence_layer=True,
                    enable_repetition_qa=True,
                )
            result["canonical_text"] = text
            result["task_id"] = TASK_ID
            result["fix_label"] = f"ut06d_a2_individual_retry_{name}"
            retry_results[name] = result

            status = result.get("status")
            verified = result.get("asr_verified")
            print(f"[UT06-D][A2] {name} status={status} asr_verified={verified}")
            for a in (result.get("attempts_log") or []):
                print(f"  [{name}] attempt={a.get('attempt')} audio_classification={a.get('audio_classification')} "
                      f"verified={a.get('verified')}")
                print(f"    asr_text={a.get('asr_text')!r}")

            data["segments"][name] = result
    finally:
        # 予算超過等でloop途中の例外が発生しても、ここまでの結果は必ず保存する
        # (監査証跡の欠落防止。委任Dの実行で判明したgap、2026-09-15)。
        base.save_json(results_path, data)

    all_pass = all(
        (retry_results[n].get("status") == "OK" and retry_results[n].get("asr_verified"))
        for n in only_segments
    )

    # 他14(+kp10)segmentのsha256不変確認
    sha_after = {}
    unchanged_count = 0
    for n, before in sha_before.items():
        p = f"{narration_dir}/{n}.wav"
        after = sha256_of(p) if os.path.exists(p) else "MISSING"
        sha_after[n] = after
        if after == before:
            unchanged_count += 1
    print(f"[UT06-D][A2] 他segment sha256不変確認: {unchanged_count}/{len(sha_before)} 件不変")

    outcome = {
        "task_id": TASK_ID,
        "only_segments": only_segments,
        "retry_results": {n: {"status": r.get("status"), "asr_verified": r.get("asr_verified"),
                               "attempts_log": r.get("attempts_log")} for n, r in retry_results.items()},
        "all_pass": all_pass,
        "unaffected_segment_count": len(sha_before),
        "unaffected_segment_unchanged_count": unchanged_count,
        "unaffected_segment_sha_before": sha_before,
        "unaffected_segment_sha_after": sha_after,
        "cost_before_jpy": baseline_cost,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if not all_pass:
        outcome["cost_after_jpy"] = base.cost_so_far_jpy()
        outcome["incremental_cost_jpy"] = round(outcome["cost_after_jpy"] - baseline_cost, 2)
        base.save_json(f"{level_out_dir}/audit/ut06d_a2_targeted_retry_result.json", outcome)
        print("===== [UT06-D][A2] STOP: 個別retryでもいずれかのsegmentがASR検証に合格しませんでした。"
              "Assembly以降には進みません。 =====")
        return

    summary = base.load_json(summary_path)
    for n in only_segments:
        summary["segment_status"][n] = "OK"
    base.save_json(summary_path, summary)

    check_part_budget("Assembly")
    assemble_result = base.run_assembly(LEVEL)
    if assemble_result.get("gate_off_result") != "PASS":
        outcome["assembly_error"] = assemble_result
        base.save_json(f"{level_out_dir}/audit/ut06d_a2_targeted_retry_result.json", outcome)
        raise RuntimeError(f"[UT06-D][A2] Assembly(Gate OFF経路)がPASSしませんでした、STOP: {assemble_result}")

    check_part_budget("Gate ON / Consistency / Web player")
    gate_on = base.run_gate_opt_in_check(LEVEL)
    consistency = base.build_consistency_check(LEVEL)
    web = base.build_player_and_web_delivery(LEVEL, assemble_result)

    cost_after = base.cost_so_far_jpy()
    level_result = {
        "level": LEVEL, "assemble_result": assemble_result, "gate_opt_in_result": gate_on,
        "consistency": consistency, "web": web,
        "cost_breakdown_jpy": base.cost_breakdown_by_stage(),
    }
    base.update_shared_outputs(LEVEL, level_result)
    base.append_progress_log(LEVEL, level_result)
    base.save_json(f"{level_out_dir}/run_result_ut06d_targeted_retry.json", level_result)

    outcome["cost_after_jpy"] = cost_after
    outcome["incremental_cost_jpy"] = round(cost_after - baseline_cost, 2)
    outcome["assemble_result"] = {
        "gate_off_result": assemble_result.get("gate_off_result"),
        "duration_seconds": assemble_result.get("duration_seconds"),
    }
    outcome["gate_opt_in_result"] = gate_on
    outcome["consistency_all_pass"] = consistency.get("all_pass")
    outcome["web"] = web
    base.save_json(f"{level_out_dir}/audit/ut06d_a2_targeted_retry_result.json", outcome)

    print(f"[UT06-D][A2][BUDGET] task完了後の全累積コスト={cost_after:.2f} JPY "
          f"(本Part差分=¥{cost_after - baseline_cost:.2f})")
    print(f"[UT06-D][A2] 完了: gate_off=PASS gate_on={gate_on.get('gate_on_result')} "
          f"duration={assemble_result.get('duration_seconds')}s "
          f"consistency_all_pass={consistency.get('all_pass')}")
    print("===== [UT06-D][A2] Part2(A2) PASS =====")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only-segments", type=str, default=None,
                         help="comma-separated segment names for individual retry (D, FOLLOWUP-01 item5)")
    parser.add_argument("--approve-reason", type=str, default=APPROVE_REASON_DEFAULT)
    parser.add_argument("--budget-jpy", type=float, default=None)
    args = parser.parse_args()

    if args.only_segments:
        only_segments = [s.strip() for s in args.only_segments.split(",") if s.strip()]
        for s in only_segments:
            if s not in TARGETABLE_SEGMENTS:
                raise ValueError(f"[UT06-D][A2] --only-segmentsに未対応のsegment名: {s!r} "
                                  f"(対応: {list(TARGETABLE_SEGMENTS)})")
        budget = args.budget_jpy if args.budget_jpy is not None else 15.0
        run_targeted_retry(only_segments, args.approve_reason, budget)
        return

    cl.install(base.LOG_PATH)
    baseline_cost = base.cost_so_far_jpy()
    print(f"[UT06-A][A2][BUDGET] task開始前の全累積コスト={baseline_cost:.2f} JPY "
          f"(本タスクPart3上限=¥{BUDGET_JPY}はこのdriverの新規発生分のみに適用)")

    def check_part_budget(note: str) -> None:
        now = base.cost_so_far_jpy()
        delta = now - baseline_cost
        print(f"[UT06-A][A2][BUDGET] 累積差分={delta:.2f} JPY / 上限={BUDGET_JPY} JPY (次段階: {note})")
        if delta >= BUDGET_JPY:
            raise RuntimeError(
                f"[UT06-A][A2] Part3費用上限到達のためSTOP: 差分={delta:.2f} JPY >= {BUDGET_JPY} JPY "
                f"(次段階「{note}」を実行せず停止)")

    article_text = base.prepare_article(LEVEL)
    word_count_split = len(article_text.split())
    print(f"[UT06-A][A2] article.md word_count(split()による簡易カウント)={word_count_split}")

    check_part_budget("scaffold(Preview/Comment)")
    parts = base.run_scaffold(LEVEL, article_text)

    check_part_budget("key phrase reselection(Canonicalization+Redundancy QA)")
    kp_dir_a2 = f"{base.DISCOVERY_DIR}/key_phrases/a2"
    kp_result = sc.run_key_phrases(
        article_text, kp_dir_a2, f"{base.THEME_ID}_a2_ut06a",
        "A2(N3-01, Discovery Focus S2, UT06A 530-word version)", process="A2_SUPPORT")
    sel_status = kp_result["selection"]["status"]
    canon_status = (kp_result.get("canonicalization") or {}).get("status")
    redundancy_status = (kp_result.get("redundancy_qa") or {}).get("status")
    print(f"[UT06-A][A2] Key Phrase再選定: selection={sel_status} canonicalization={canon_status} "
          f"redundancy_qa={redundancy_status}")
    if sel_status != "KEY_WORDS_STRUCTURE_PASS" or canon_status not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED") or redundancy_status == "REDUNDANCY_NG":
        base.save_json(f"{base.OUT_DIR}/{LEVEL}/audit/ut06a_key_phrase_stop.json", kp_result)
        print("===== [UT06-A][A2] STOP: Key Phrase再選定がPASSしませんでした。TTS以降には進みません。 =====")
        return

    check_part_budget("Key Phrase reuse-copy into audio/a2")
    kp = base.prepare_key_phrases(LEVEL, article_text)

    check_part_budget("TTS(generate_a2_segments)")
    tts_result = base.run_tts(LEVEL)
    print(f"[UT06-A][A2] TTS完了。segment_status={ {k: v.get('status') if isinstance(v, dict) else v for k, v in (tts_result or {}).items()} if isinstance(tts_result, dict) else tts_result }")

    check_part_budget("Assembly")
    assemble_result = base.run_assembly(LEVEL)
    if assemble_result.get("gate_off_result") != "PASS":
        base.save_json(f"{base.OUT_DIR}/{LEVEL}/audit/ut06a_assembly_stop.json", assemble_result)
        print(f"===== [UT06-A][A2] STOP: Assembly(Gate OFF経路)がPASSしませんでした: {assemble_result} =====")
        return

    check_part_budget("Gate ON / Consistency / Web player")
    gate_on = base.run_gate_opt_in_check(LEVEL)
    consistency = base.build_consistency_check(LEVEL)
    web = base.build_player_and_web_delivery(LEVEL, assemble_result)

    cost_after = base.cost_so_far_jpy()
    level_result = {
        "level": LEVEL, "task_id": TASK_ID,
        "word_count_split": word_count_split,
        "kp_result_status": {"selection": sel_status, "canonicalization": canon_status,
                              "redundancy_qa": redundancy_status},
        "assemble_result": assemble_result, "gate_opt_in_result": gate_on,
        "consistency": consistency, "web": web,
        "cost_breakdown_jpy": base.cost_breakdown_by_stage(),
        "cost_before_jpy": baseline_cost, "cost_after_jpy": cost_after,
        "incremental_cost_jpy": round(cost_after - baseline_cost, 2),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    base.save_json(f"{base.OUT_DIR}/{LEVEL}/run_result_ut06a_regen.json", level_result)
    print(f"[UT06-A][A2] 完了: gate_off=PASS gate_on={gate_on.get('gate_on_result')} "
          f"duration={assemble_result.get('duration_seconds')}s "
          f"consistency_all_pass={consistency.get('all_pass')} "
          f"incremental_cost_jpy={level_result['incremental_cost_jpy']}")


if __name__ == "__main__":
    main()
