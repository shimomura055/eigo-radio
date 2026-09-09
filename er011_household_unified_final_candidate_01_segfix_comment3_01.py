# ============================================================
# er011_household_unified_final_candidate_01_segfix_comment3_01.py
# 管理ID: PM-CLOSEOUT-CONSOLIDATION-64
#   (サブID: HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01-SEGFIX-01)
# ============================================================
# 背景: HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01をユーザーが試聴し、A2/B1B
# とも全体として良好=OKだが、B1B comment_3の"prevent"の発音に違和感が
# あるとの指摘があった(2026-09-10)。
#
# 機械的確認(本スクリプト実行前、読み取りのみ):
#   er011_output/household_unified_final_candidate_01/b1b/audit/
#   tts_generation_results.json の segments.comment_3.disfluency_evidence
#   .transcript(method="faster_whisper_small_local_verbatim"、disfluency
#   QA用の独立ローカルASR)が、canonical_textの"prevent"の位置で
#   "perfect"と誤認識していた(NORMALIZED_MATCH判定に使う主ASR側の
#   asr_textは"prevent"一致だったが、独立した別のローカルASRが該当語の
#   みを誤認識、ユーザー指摘箇所と一致)。これを「機械的に異常が確認
#   できる場合」と判定し、既存segment再生成経路でcomment_3のみ再生成
#   する。Prompt/本文/Support文言(b1_support_texts.json)は一切変更
#   しない。他segment・A2は無変更。
#
# 再生成経路(既存Production関数を無変更のまま呼ぶだけ):
#   - er011_human_review_lock_01.approve_regenerate() (state=RESOLVED
#     からの明示的再生成承認、既存API)
#   - er003_v1_sing01_voice01_generate.generate_charon_english()
#     (comment_3を元々生成したのと同一関数・同一引数
#     [style_prefix_override=B1_PREVIEW_STYLE_PREFIX_CALM,
#     disfluency_qa=True]、er003_v1_n3_01_tts_generate.
#     generate_b1_segments()内のcomment_3呼び出しと同一)
#   - Human Review Lock(review_lock.guarded_generate、max_attempts=3)・
#     Audio QA・ASR・disfluency QAは既存どおり内部で適用される
#     (本スクリプトは独自の判定ロジックを追加していない)。
#   - 旧comment_3.wavは comment_3_original.wav として narration_dir に
#     残す(上書き消去しない、既存慣行)。
#   - 再生成後、er011_household_unified_final_candidate_01_run.py の
#     assembly_stage("b1b")(無変更)でB1Bを再Assembly + Gate opt-in ON
#     を再確認する。
from __future__ import annotations

import json
import os
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er011_household_unified_final_candidate_01_run as driver
import er011_human_review_lock_01 as review_lock

THEME_ID = driver.THEME_ID
OUT_DIR = driver.OUT_DIR
LEVEL_OUT_DIR = f"{OUT_DIR}/b1b"
NARRATION_DIR = f"{LEVEL_OUT_DIR}/narration"
TARGET = "comment_3"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def step1_diagnose() -> dict:
    """再生成前の機械的異常確認(読み取りのみ、再度ログとして保存)。"""
    results = load_json(f"{LEVEL_OUT_DIR}/audit/tts_generation_results.json")
    entry = results["segments"][TARGET]
    primary_asr_text = entry.get("asr_text", "")
    disfluency_transcript = (entry.get("disfluency_evidence") or {}).get("transcript", "")
    canonical_text = entry.get("canonical_text", "")

    finding = {
        "target": TARGET,
        "canonical_text": canonical_text,
        "primary_asr_text_NORMALIZED_MATCH_basis": primary_asr_text,
        "disfluency_qa_independent_local_asr_transcript": disfluency_transcript,
        "primary_asr_contains_prevent": "prevent" in primary_asr_text.lower(),
        "disfluency_asr_contains_prevent": "prevent" in disfluency_transcript.lower(),
        "disfluency_asr_contains_perfect_misrecognition": "perfect" in disfluency_transcript.lower(),
        "audio_classification": entry.get("audio_classification"),
        "disfluency_flagged": (entry.get("disfluency_evidence") or {}).get("flagged"),
    }
    print(f"[{THEME_ID}][diagnose] {json.dumps(finding, ensure_ascii=False)}")
    assert (finding["disfluency_asr_contains_perfect_misrecognition"]
            and not finding["disfluency_asr_contains_prevent"]), (
        "想定していた誤認識パターン(独立ローカルASRが'prevent'を'perfect'と誤認識)と"
        "異なります。再確認してください。")
    return finding


def step2_backup_original() -> str:
    out_path = f"{NARRATION_DIR}/{TARGET}.wav"
    backup_path = f"{NARRATION_DIR}/{TARGET}_original.wav"
    assert os.path.exists(out_path), f"対象wavが見つかりません: {out_path}"
    if not os.path.exists(backup_path):
        shutil.copyfile(out_path, backup_path)
        print(f"[{THEME_ID}] b1b {TARGET}: 旧音声を {backup_path} へ退避しました。")
    else:
        print(f"[{THEME_ID}] b1b {TARGET}: 退避先 {backup_path} は既に存在します(再実行のため上書きしません)。")
    return backup_path


def step3_regenerate() -> dict:
    support = load_json(f"{LEVEL_OUT_DIR}/b1_support_texts.json")
    results_path = f"{LEVEL_OUT_DIR}/audit/tts_generation_results.json"
    summary_path = f"{LEVEL_OUT_DIR}/run_summary_tts.json"
    all_results = load_json(results_path)
    all_summary = load_json(summary_path)
    old_entry = all_results["segments"][TARGET]

    text = support[TARGET]
    out_path = f"{NARRATION_DIR}/{TARGET}.wav"
    safe_text = tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text))

    review_lock.approve_regenerate(
        out_path, safe_text, approved_by="claude_code_operator_pm_closeout_consolidation_64")
    print(f"[{THEME_ID}] b1b {TARGET}: REGENERATE_APPROVED付与。既存segment再生成経路"
          "(voice01.generate_charon_english、元のcomment_3呼び出しと同一引数)で再生成開始...")

    with cl.logging_context(THEME_ID, "tts_comment3_segfix_pm_closeout_consolidation_64"), \
         cl.segment_context(TARGET):
        r = voice01.generate_charon_english(
            safe_text, out_path,
            style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM,
            disfluency_qa=True)
    r["canonical_text"] = text
    print(f"[{THEME_ID}] b1b {TARGET}: 再生成結果 status={r.get('status')} asr_text={r.get('asr_text')!r}")
    disfl = r.get("disfluency_evidence") or {}
    print(f"[{THEME_ID}] b1b {TARGET}: disfluency_evidence.transcript(独立ローカルASR)="
          f"{disfl.get('transcript')!r}")

    all_results["segments"][TARGET] = r
    save_json(results_path, all_results)

    all_status = {k: v.get("status") for k, v in all_results["segments"].items()}
    all_summary["segment_status"] = all_status
    save_json(summary_path, all_summary)

    save_json(
        f"{LEVEL_OUT_DIR}/audit/segfix_comment3_prevent_pronunciation_pm_closeout_consolidation_64.json",
        {
            "management_id": "PM-CLOSEOUT-CONSOLIDATION-64",
            "sub_id": "HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01-SEGFIX-01",
            "target": TARGET,
            "reason": (
                "ユーザー試聴でcomment_3の'prevent'発音に違和感の指摘(2026-09-10)。"
                "既存QA記録を確認したところ、disfluency QA用の独立ローカルASR"
                "(faster_whisper_small_local_verbatim)が'prevent'を'perfect'と"
                "誤認識していた機械的証拠を確認した(NORMALIZED_MATCH判定に使う"
                "主ASR[asr_text]は'prevent'と一致していたが、別の独立ローカルASR"
                "が該当語のみ誤認識、ユーザー指摘箇所と一致)。これを機械的異常と"
                "判定し、既存segment再生成経路(review_lock.approve_regenerate + "
                "voice01.generate_charon_english、元のcomment_3呼び出しと同一引数"
                "[style_prefix_override=B1_PREVIEW_STYLE_PREFIX_CALM, "
                "disfluency_qa=True])でcomment_3のみ再生成した。Prompt/本文/"
                "Support文言は無変更。旧音声はcomment_3_original.wavとして退避。"
            ),
            "old_entry": old_entry,
            "new_entry": r,
        },
    )
    print(f"[{THEME_ID}] b1b comment_3 再生成・記録更新完了。status={all_status[TARGET]}")
    return r


def step4_reassemble_and_gate() -> dict:
    result = driver.assembly_stage("b1b")
    print(f"[{THEME_ID}] b1b 再Assembly + Gate opt-in ON結果: "
          f"gate_off={result.get('gate_off_result')} gate_on={result.get('gate_opt_in_result', {}).get('gate_on_result')}")
    return result


def step5_cost() -> dict:
    return driver.cost_stage()


def main() -> dict:
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    diagnosis = step1_diagnose()
    step2_backup_original()
    regen_result = step3_regenerate()
    assembly_result = step4_reassemble_and_gate()
    cost_result = step5_cost()

    summary = {
        "diagnosis": diagnosis,
        "regen_result": regen_result,
        "assembly_result": assembly_result,
        "cost_result": cost_result,
    }
    save_json(f"{OUT_DIR}/segfix_comment3_pm_closeout_consolidation_64_summary.json", summary)
    print(f"[{THEME_ID}] SEGFIX-01 完了。")
    return summary


if __name__ == "__main__":
    main()
