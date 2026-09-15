# ============================================================
# er014_output/four_type_observation_01/discovery/run_discovery_b1b_part2_split_ut06.py
# 管理ID: USER-TEST-FINAL-AUDIO-BATCH-06 (D) / FOLLOWUP-01 item4
# ============================================================
# 目的: Discovery B1(discovery/audio/b1b) full_story_part2 segmentが
# 3回試行(cumulative_tts_attempts=6、state=HUMAN_REVIEW_REQUIRED)しても
# 「a study of about 2,500 college students in 11 countries ... phone use.」
# を含む段落がまるごと欠落する(TRUE_CONTENT_MISMATCH、delete block)ため、
# ユーザー判断(USER-TEST-FINAL-AUDIO-BATCH-06-FOLLOWUP-01 item4、
# 2026-09-15)により、canonical本文(parts.json part2)の**既存の段落境界**
# (\n\n区切り、意味を一切変更しない)で2segmentへ分割してTTSする。
#
# 分割点: parts.json "part2"は3段落から成る。
#   P1: "At the same time, silence can also bring calm. ..."
#   P2: "Research on the body shows the same mixed picture. ..."
#   P3: "People also differ across studies and cultures. In a study of
#        about 2,500 college students in 11 countries, ... phone use. ..."
# 問題の段落(2,500人/11か国)はP3の先頭にある。P3をそのまま独立した短い
# segment(2b)にすることで、「長segment後半でblock omissionが起きる」既知の
# 失敗モードを避ける。2a = P1+P2, 2b = P3。canonical文字列は一切変更せず、
# 2a + "\n\n" + 2b が元のpart2と完全一致することをpythonで検証する。
#
# 分割はTTS入力の分割のみ(本記事b1bの個別対応)。共通Assembly関数
# (er003_v1_n3_01_assemble.stage_assemble_b1、無変更)はnarration/
# full_story_part2.wavという単一ファイルを読む前提のままなので、
# 2a.wav+2b.wavをPASS後に音声レベルで連結し、既存のfull_story_part2.wav
# パスへ書き込む(Assembly側のコード変更は一切行わない)。
#
# Human Review Lock: 新segment名(full_story_part2a/full_story_part2b)は
# 既存storeに存在しないため技術的にはcheck_before_generationがそのまま
# proceed=Trueを返すが、既存Lock機構を迂回した扱いにしないため、ユーザー
# 承認(FOLLOWUP-01 item4)を理由としてapprove_regenerate()を2a/2bそれぞれ
# 1回ずつ明示的に呼ぶ(委任文の指示通り)。各segmentの既存cascade
# (標準2+fallback1)内の呼び出しは許容、それを超える自動retryはしない。
#
# 実行方法:
#   .venv/Scripts/python.exe er014_output/four_type_observation_01/discovery/run_discovery_b1b_part2_split_ut06.py
from __future__ import annotations

import json
import os
import shutil
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

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402

import er003_v1_n3_01_tts_generate as tts_gen  # noqa: E402
import er003_v1_sing01_news_tail_fix as news_tail_fix  # noqa: E402
import er005_cost_logger as cl  # noqa: E402
import er011_human_review_lock_01 as review_lock  # noqa: E402
import run_discovery_audio_completion as base  # noqa: E402 (既存driver、TTS/Assembly/Gate/Web、無変更で再利用)

TASK_ID = "USER-TEST-FINAL-AUDIO-BATCH-06"
DISCOVERY_DIR = base.DISCOVERY_DIR
B1B_AUDIO_DIR = f"{base.OUT_DIR}/b1b"
NARRATION_DIR = f"{B1B_AUDIO_DIR}/narration"
WAV_PART2 = f"{NARRATION_DIR}/full_story_part2.wav"
WAV_PART2A = f"{NARRATION_DIR}/full_story_part2a.wav"
WAV_PART2B = f"{NARRATION_DIR}/full_story_part2b.wav"
BACKUP_WAV = f"{NARRATION_DIR}/full_story_part2_pre_split_ut06d_backup.wav"
RESULTS_PATH = f"{B1B_AUDIO_DIR}/audit/tts_generation_results.json"
SUMMARY_PATH = f"{B1B_AUDIO_DIR}/run_summary_tts.json"
TRANSFORMS_PATH = f"{base.OUT_DIR}/tts_reading_transforms.json"
PARTS_PATH = f"{B1B_AUDIO_DIR}/parts.json"
OUTCOME_PATH = f"{B1B_AUDIO_DIR}/audit/ut06d_part2_split_result.json"
HUMAN_REVIEW_PLAYER_PATH = f"{B1B_AUDIO_DIR}/human_review_player.html"

APPROVED_BY = ("user (USER-TEST-FINAL-AUDIO-BATCH-06-FOLLOWUP-01 item4, 2026-09-15 explicit "
               "approval to split full_story_part2 into 2 segments at an existing paragraph "
               "boundary; canonical text unchanged, no new permanent Assembly spec)")

REQUIRED_2B_KEYWORDS = ["2,500", "2500", "two thousand five hundred"]
REQUIRED_2B_COUNTRY_KEYWORDS = ["11 countries", "eleven countries"]
REQUIRED_2B_TAIL_KEYWORD = "phone use"


def keyword_present(text: str, candidates: list[str]) -> bool:
    low = text.lower()
    return any(c.lower() in low for c in candidates)


def main() -> None:
    cl.install(base.LOG_PATH)
    baseline_cost = base.cost_so_far_jpy()
    print(f"[UT06-D][BUDGET] task開始前の全累積コスト(audio_completion log)={baseline_cost:.2f} JPY")

    transforms_record = base.load_json(TRANSFORMS_PATH)
    original_text = transforms_record["original_text"]
    transformed_text = transforms_record["transformed_text"]

    parts = base.load_json(PARTS_PATH)
    assert parts["part2"] == original_text, (
        "[UT06-D] STOP: parts.json part2 と tts_reading_transforms.json original_text が不一致。"
        "本文が変更されている可能性があるため実行を中止します。")

    orig_paragraphs = original_text.split("\n\n")
    trans_paragraphs = transformed_text.split("\n\n")
    assert len(orig_paragraphs) == 3 and len(trans_paragraphs) == 3, (
        f"[UT06-D] STOP: 想定外の段落数(original={len(orig_paragraphs)}, transformed={len(trans_paragraphs)})。"
        "自然な段落境界での分割前提が崩れているため中止します。")

    part2a_original = orig_paragraphs[0] + "\n\n" + orig_paragraphs[1]
    part2b_original = orig_paragraphs[2]
    split_concat_equal = (part2a_original + "\n\n" + part2b_original) == original_text
    print(f"[UT06-D] SPLIT_CONCAT_EQUAL={split_concat_equal}")
    assert split_concat_equal, "[UT06-D] STOP: 2a+2b連結が元のpart2と一致しません。"

    part2a_transformed = trans_paragraphs[0] + "\n\n" + trans_paragraphs[1]
    part2b_transformed = trans_paragraphs[2]
    transformed_split_concat_equal = (part2a_transformed + "\n\n" + part2b_transformed) == transformed_text
    print(f"[UT06-D] TRANSFORMED_SPLIT_CONCAT_EQUAL={transformed_split_concat_equal}")
    assert transformed_split_concat_equal, "[UT06-D] STOP: 読み整形後テキストの2a+2b連結が不一致です。"

    print("[UT06-D] 分割点: P1+P2(2a) / P3(2b、2,500人/11か国段落を含む)")
    print(f"[UT06-D] 2a冒頭: {part2a_original[:60]!r}")
    print(f"[UT06-D] 2b冒頭: {part2b_original[:60]!r}")

    tts_input_2a = tts_gen.tts_safe_news_en(part2a_transformed)
    tts_input_2b = tts_gen.tts_safe_news_en(part2b_transformed)

    if os.path.exists(WAV_PART2) and not os.path.exists(BACKUP_WAV):
        shutil.copy2(WAV_PART2, BACKUP_WAV)
        print(f"[UT06-D] 既存full_story_part2.wavを退避: {BACKUP_WAV}")

    print(f"[UT06-D] Human Review Lock解除(approve_regenerate, full_story_part2a、1回限り)。"
          f"approved_by={APPROVED_BY}")
    approve_a = review_lock.approve_regenerate(WAV_PART2A, tts_input_2a, approved_by=APPROVED_BY)
    print(f"[UT06-D] approve_regenerate(2a)結果: state={approve_a.get('state')}")

    print(f"[UT06-D] Human Review Lock解除(approve_regenerate, full_story_part2b、1回限り)。"
          f"approved_by={APPROVED_BY}")
    approve_b = review_lock.approve_regenerate(WAV_PART2B, tts_input_2b, approved_by=APPROVED_BY)
    print(f"[UT06-D] approve_regenerate(2b)結果: state={approve_b.get('state')}")

    print("[UT06-D] full_story_part2a 生成(既存Production関数、無変更)...")
    with cl.logging_context(base.THEME_ID, "tts_b1b_ut06d_part2a"):
        result_2a = news_tail_fix.generate_news_narration_wide_margin(
            tts_input_2a, WAV_PART2A,
            disfluency_qa=False,
            enable_connected_speech_equivalence_layer=True,
            enable_repetition_qa=True,
        )
    result_2a["canonical_text"] = part2a_original
    result_2a["tts_input_text"] = tts_input_2a
    result_2a["task_id"] = TASK_ID
    result_2a["fix_label"] = "ut06d_split_part2a"

    print("[UT06-D] full_story_part2b 生成(既存Production関数、無変更)...")
    with cl.logging_context(base.THEME_ID, "tts_b1b_ut06d_part2b"):
        result_2b = news_tail_fix.generate_news_narration_wide_margin(
            tts_input_2b, WAV_PART2B,
            disfluency_qa=False,
            enable_connected_speech_equivalence_layer=True,
            enable_repetition_qa=True,
        )
    result_2b["canonical_text"] = part2b_original
    result_2b["tts_input_text"] = tts_input_2b
    result_2b["task_id"] = TASK_ID
    result_2b["fix_label"] = "ut06d_split_part2b"

    status_a = result_2a.get("status")
    verified_a = result_2a.get("asr_verified")
    status_b = result_2b.get("status")
    verified_b = result_2b.get("asr_verified")
    print(f"[UT06-D] full_story_part2a status={status_a} asr_verified={verified_a}")
    for a in (result_2a.get("attempts_log") or []):
        print(f"  [2a] attempt={a.get('attempt')} audio_classification={a.get('audio_classification')} "
              f"verified={a.get('verified')}")
        print(f"    asr_text={a.get('asr_text')!r}")
    print(f"[UT06-D] full_story_part2b status={status_b} asr_verified={verified_b}")
    for a in (result_2b.get("attempts_log") or []):
        print(f"  [2b] attempt={a.get('attempt')} audio_classification={a.get('audio_classification')} "
              f"verified={a.get('verified')}")
        print(f"    asr_text={a.get('asr_text')!r}")

    # 監査記録(RESOLVED/HUMAN_REVIEW_REQUIRE状態に関わらず、成功/失敗どちらでも保存)
    data = base.load_json(RESULTS_PATH)
    data["segments"]["full_story_part2a"] = result_2a
    data["segments"]["full_story_part2b"] = result_2b
    base.save_json(RESULTS_PATH, data)

    both_pass = (status_a == "OK" and verified_a and status_b == "OK" and verified_b)

    content_checks = {}
    if both_pass:
        asr_2b = ""
        attempts_2b = result_2b.get("attempts_log") or []
        if attempts_2b:
            asr_2b = attempts_2b[-1].get("asr_text") or ""
        content_checks = {
            "asr_2b_text": asr_2b,
            "has_2500_number": keyword_present(asr_2b, REQUIRED_2B_KEYWORDS),
            "has_11_countries": keyword_present(asr_2b, REQUIRED_2B_COUNTRY_KEYWORDS),
            "has_phone_use_tail": REQUIRED_2B_TAIL_KEYWORD in asr_2b.lower(),
        }
        print(f"[UT06-D] content_checks(2b)={content_checks}")

    outcome = {
        "task_id": TASK_ID,
        "split_concat_equal": split_concat_equal,
        "transformed_split_concat_equal": transformed_split_concat_equal,
        "part2a_original": part2a_original,
        "part2b_original": part2b_original,
        "status_2a": status_a,
        "asr_verified_2a": verified_a,
        "attempts_log_2a": result_2a.get("attempts_log"),
        "status_2b": status_b,
        "asr_verified_2b": verified_b,
        "attempts_log_2b": result_2b.get("attempts_log"),
        "content_checks_2b": content_checks,
        "both_pass": both_pass,
        "cost_before_jpy": baseline_cost,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if not both_pass:
        outcome["cost_after_jpy"] = base.cost_so_far_jpy()
        outcome["incremental_cost_jpy"] = round(outcome["cost_after_jpy"] - baseline_cost, 2)
        base.save_json(OUTCOME_PATH, outcome)
        print("===== [UT06-D] STOP: 分割後も2a/2bのいずれかがASR検証に合格しませんでした。"
              "Assembly以降には進みません。個別対応候補は別途RESULT_PACKETへ記載します。 =====")
        return

    print("[UT06-D] 2a/2b両方PASS。full_story_part2.wavへ音声連結します。")
    data_a, sr_a = sf.read(WAV_PART2A)
    data_b, sr_b = sf.read(WAV_PART2B)
    assert sr_a == sr_b, f"[UT06-D] STOP: サンプルレート不一致(2a={sr_a}, 2b={sr_b})。"
    combined = np.concatenate([data_a, data_b], axis=0)
    sf.write(WAV_PART2, combined, sr_a, subtype="PCM_16")
    combined_duration = round(len(combined) / sr_a, 3)
    print(f"[UT06-D] 連結後full_story_part2.wav duration={combined_duration}s "
          f"(2a={round(len(data_a)/sr_a,3)}s + 2b={round(len(data_b)/sr_a,3)}s)")

    # tts_generation_results.jsonの既存"full_story_part2"キー(canonical_text_of()等が
    # 参照する)を、分割合成であることを明記したうえで更新する(下流コードは無変更で動く)。
    composite = {
        "status": "OK",
        "asr_verified": True,
        "canonical_text": original_text,
        "tts_input_text": transformed_text,
        "task_id": TASK_ID,
        "fix_label": "ut06d_split_composite_part2a_plus_part2b",
        "split_from": ["full_story_part2a", "full_story_part2b"],
        "duration_seconds": combined_duration,
        "note": ("USER-TEST-FINAL-AUDIO-BATCH-06(D)/FOLLOWUP-01 item4: 個別対応として、"
                 "既存段落境界でfull_story_part2a(P1+P2)/full_story_part2b(P3、2,500人/11か国"
                 "段落を含む)へ分割しTTS。各segment個別にASR検証PASS後、音声レベルで連結して"
                 "本キーのwav(full_story_part2.wav)を更新。canonical_text/本文は無変更。"),
    }
    data = base.load_json(RESULTS_PATH)
    data["segments"]["full_story_part2"] = composite
    base.save_json(RESULTS_PATH, data)
    summary = base.load_json(SUMMARY_PATH)
    summary["segment_status"]["full_story_part2"] = "OK"
    summary["segment_status"]["full_story_part2a"] = status_a
    summary["segment_status"]["full_story_part2b"] = status_b
    base.save_json(SUMMARY_PATH, summary)

    print("[UT06-D] Assembly/Gate/Consistency/Web playerへ進みます(既存Production関数、無変更)。")
    assemble_result = base.run_assembly("b1b")
    if assemble_result.get("gate_off_result") != "PASS":
        outcome["assembly_error"] = assemble_result
        base.save_json(OUTCOME_PATH, outcome)
        raise RuntimeError(f"[UT06-D] Assembly(Gate OFF経路)がPASSしませんでした、STOP: {assemble_result}")
    gate_on = base.run_gate_opt_in_check("b1b")
    consistency = base.build_consistency_check("b1b")
    web = base.build_player_and_web_delivery("b1b", assemble_result)

    level_result = {
        "level": "b1b", "assemble_result": assemble_result, "gate_opt_in_result": gate_on,
        "consistency": consistency, "web": web,
        "cost_breakdown_jpy": base.cost_breakdown_by_stage(),
    }
    base.update_shared_outputs("b1b", level_result)
    base.append_progress_log("b1b", level_result)
    base.save_json(f"{B1B_AUDIO_DIR}/run_result_ut06d_split.json", level_result)

    cost_after = base.cost_so_far_jpy()
    outcome["cost_after_jpy"] = cost_after
    outcome["incremental_cost_jpy"] = round(cost_after - baseline_cost, 2)
    outcome["assemble_result"] = {
        "gate_off_result": assemble_result.get("gate_off_result"),
        "duration_seconds": assemble_result.get("duration_seconds"),
    }
    outcome["gate_opt_in_result"] = gate_on
    outcome["consistency_all_pass"] = consistency.get("all_pass")
    outcome["web"] = web
    base.save_json(OUTCOME_PATH, outcome)

    # human_review_player.htmlへ「attempt5(分割版、採用)」の追記(既存tabウィジェットの
    # 構造は変更せず、末尾<script>直前に静的な追記セクションを挿入するのみ)。
    if os.path.exists(HUMAN_REVIEW_PLAYER_PATH):
        with open(HUMAN_REVIEW_PLAYER_PATH, encoding="utf-8") as f:
            html = f.read()
        addendum = f"""
<div class="attempt-block" id="attempt-block-5-split" style="display:block;border-top:2px solid #333;margin-top:16px;padding-top:12px;">
  <h3>Attempt 5(分割版、採用。USER-TEST-FINAL-AUDIO-BATCH-06(D)/FOLLOWUP-01 item4)</h3>
  <p>full_story_part2をP1+P2(full_story_part2a)/P3(full_story_part2b、2,500人/11か国段落を含む)
  へ既存段落境界で分割し個別TTS。両segmentともASR検証PASS
  (2a: audio_classification={(result_2a.get('attempts_log') or [{}])[-1].get('audio_classification')},
  2b: audio_classification={(result_2b.get('attempts_log') or [{}])[-1].get('audio_classification')})。
  音声レベルで連結してfull_story_part2.wav({combined_duration}秒)として採用。canonical本文は無変更。</p>
  <audio controls preload="none" src="web/segments/full_story_part2a.mp3"></audio>
  <audio controls preload="none" src="web/segments/full_story_part2b.mp3"></audio>
  <p>2b ASR transcript: {content_checks.get('asr_2b_text', '')}</p>
  <p>content_checks: has_2500_number={content_checks.get('has_2500_number')},
  has_11_countries={content_checks.get('has_11_countries')},
  has_phone_use_tail={content_checks.get('has_phone_use_tail')}</p>
</div>
"""
        html = html.replace("\n<script>", addendum + "\n<script>", 1)
        with open(HUMAN_REVIEW_PLAYER_PATH, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[UT06-D] human_review_player.htmlへattempt5追記完了: {HUMAN_REVIEW_PLAYER_PATH}")

    print(f"[UT06-D][BUDGET] task完了後の全累積コスト={cost_after:.2f} JPY "
          f"(本タスク差分=¥{cost_after - baseline_cost:.2f})")
    print(f"[UT06-D] Assembly完了: gate_off=PASS gate_on={gate_on.get('gate_on_result')} "
          f"duration={assemble_result.get('duration_seconds')}s "
          f"consistency_all_pass={consistency.get('all_pass')}")
    print("===== [UT06-D] Part1(B1) PASS =====")


if __name__ == "__main__":
    main()
