# ============================================================
# er010_no9_function_word_reduction_production_wiring_27.py
# ER-010-NO9-FUNCTION-WORD-REDUCTION-PRODUCTION-WIRING-AND-A2-FINAL-27-R1
# ============================================================
# ユーザー正式決定(2026-09-02): Trial 26(ER-010-NO9-A2-KEYPHRASE-ARTICLE-
# REDUCTION-DIAGNOSTIC-AND-TRIAL-26)で検証したfunction-word/article
# reduction原則を、Key Phrase英語TTSの一般Production仕様として正式採用
# する(APPROVED_FOR_PRODUCTION → 本モジュールでPRODUCTION_WIREDへ)。
#
# er003_v1_repro01_main_generate.pyのKEY_PHRASE_MINIMAL_INSTRUCTION_
# PREFIX自体を書き換え済み(CORE_TEXT + FUNCTION_WORD_REDUCTION_SUFFIX)
# であり、KEY_PHRASE_ENGLISH_LOCK_INSTRUCTIONはこのPREFIXを起点に構築
# されるため、Primary(Minimal)・Fallback(English Lock)の両方へ自動的に
# 適用される(実装は既に完了、本モジュールはRuntime evidence取得・
# regression確認・No.9 A2への反映を担当)。
#
# 本モジュールは:
#   1. Dangling Reference Check(静的検証)
#   2. Runtime evidence: 実Production path(generate_key_phrase_
#      component_verified、Trial専用scriptではない)経由で「a catch」+
#      article/function-word fixture(a/an/the)+ 非function-word系の
#      既存Key Phrase(guilt tipping/push back/starting point)を隔離
#      probe dirで生成し、article弱化・非function-word系への悪影響
#      有無を実データで確認する
#   3. No.9 A2の`kp4_en.wav`(a catch)を、上記2で得た実Production生成
#      音声へ差し替え、tts_generation_results.jsonを更新する
#   4. No.9 A2 episodeを再Assemblyし、完成音声中の「a catch」区間を
#      実測ASRで再確認する
#
# `default`(kp2、OPEN-103)・他Key Phrase(guilt tipping/push back/
# starting point)のnarration本体は再生成・再splice**しない**
# (regression確認用のprobe音声は隔離dirのみに留め、実production asset
# には一切触れない)。

from __future__ import annotations

import hashlib
import json
import os
import shutil

import numpy as np

import er002_common as common
import er003_v1_n3_01_assemble as asm
import er003_v1_repro01_main_generate as repro01
import er006_asr_provider_routing_01 as routing
import er011_human_review_lock_01 as review_lock

MANAGEMENT_ID = "ER-010-NO9-FUNCTION-WORD-REDUCTION-PRODUCTION-WIRING-AND-A2-FINAL-27-R1"

OUT_DIR = "er010_output/no9_function_word_reduction_production_wiring_27"
RUNTIME_DIR = f"{OUT_DIR}/runtime_evidence"

THEME_ID = "pool_n9_tip_screens"
A2_OUT_DIR = f"er006_output/pool_pilot_01/{THEME_ID}"
A2_DIR = f"{A2_OUT_DIR}/a2"
NARRATION_DIR = f"{A2_DIR}/narration"
AUDIT_DIR = f"{A2_DIR}/audit"
TTS_RESULTS_PATH = f"{AUDIT_DIR}/tts_generation_results.json"
KP4_EN_PATH = f"{NARRATION_DIR}/kp4_en.wav"
KP4_EN_PRE_WIRING27_BACKUP_PATH = f"{NARRATION_DIR}/kp4_en_pre_wiring27_backup.wav"

# Article/function-word fixture(一般原則の対象、「a catch」固有ではない
# ことを確認するための汎用短句、No.9本文とは無関係の一般的English)。
ARTICLE_FIXTURES = {
    "a_chance": "a chance",
    "an_idea": "an idea",
    "the_answer": "the answer",
}
# No.9 A2の正式承認済みKey Phrase("a catch"本体)。
TARGET_KEY_PHRASE = {"a_catch": "a catch"}
# 非function-word系の既存Key Phrase(regression確認用、No.9 A2で実際に
# 使われている語)。
NON_FUNCTION_WORD_FIXTURES = {
    "guilt_tipping": "guilt tipping",
    "push_back": "push back",
    "starting_point": "starting point",
}
ALL_FIXTURES = {**TARGET_KEY_PHRASE, **ARTICLE_FIXTURES, **NON_FUNCTION_WORD_FIXTURES}


def _sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _measure_word_envelope(path: str) -> dict:
    """簡易envelope解析(10ms窓RMS、閾値=peakの8%)。Trial 26と同一の
    軽量な補助diagnostic(Production本体の判定には使わない、参考情報)。
    Trial専用モジュールをimportしない設計方針のため実装をここへ複製する。"""
    samples, sr, channels, _nframes = common.read_wav_float(path)
    if channels > 1:
        samples = samples.reshape(-1, channels)
        samples = samples[:, 0]
    win = max(1, int(sr * 0.01))
    n_win = len(samples) // win
    if n_win == 0:
        return {"runs": [], "note": "音声が短すぎてenvelope解析不可"}
    env = np.array([np.sqrt(np.mean(samples[i * win:(i + 1) * win] ** 2)) for i in range(n_win)])
    peak = float(env.max()) if len(env) else 0.0
    if peak <= 0:
        return {"runs": [], "note": "無音"}
    thresh = peak * 0.08
    speech = env > thresh
    runs = []
    in_run = False
    start = 0
    for i, s in enumerate(speech):
        if s and not in_run:
            start = i
            in_run = True
        if not s and in_run:
            runs.append((start, i))
            in_run = False
    if in_run:
        runs.append((start, len(speech)))
    run_info = []
    for r in runs:
        seg = env[r[0]:r[1]]
        run_info.append({
            "start_seconds": round(r[0] * 0.01, 3), "end_seconds": round(r[1] * 0.01, 3),
            "duration_seconds": round((r[1] - r[0]) * 0.01, 3),
            "peak_rms": round(float(seg.max()), 4), "mean_rms": round(float(seg.mean()), 4),
        })
    return {"runs": run_info, "peak_rms_overall": round(peak, 4), "num_runs": len(run_info)}


def step1_dangling_reference_check() -> dict:
    """function-word reductionが実際にPrimary/Fallback両方の実効
    instructionへ入っているか、Trial専用定義(er010_no9_a2_keyphrase_
    article_reduction_trial_26)をProduction本体が参照していないかを
    静的に確認する。"""
    checks = {}
    suffix = repro01.FUNCTION_WORD_REDUCTION_SUFFIX
    checks["suffix_in_minimal_prefix"] = suffix in repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX
    checks["suffix_in_english_lock_instruction"] = suffix in repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION
    checks["minimal_prefix_starts_with_core_text"] = repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX.startswith(
        repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_CORE_TEXT)
    checks["english_lock_starts_with_minimal_prefix"] = repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION.startswith(
        repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX)
    checks["core_safeguards_preserved"] = all(s in repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_CORE_TEXT for s in (
        "do not add explanations", "do not add, omit, or change any words",
        "not as separate words read one at a time", "not trailed off",
        "do not over-emphasize or exaggerate any single sound"))
    checks["suffix_is_general_not_hardcoded_to_a_catch"] = (
        "a catch" not in suffix and "articles" in suffix and '"a", "an", "the"' in suffix)
    with open("er003_v1_repro01_main_generate.py", "r", encoding="utf-8") as f:
        repro01_source = f.read()
    checks["production_module_does_not_import_trial_26_module"] = (
        "er010_no9_a2_keyphrase_article_reduction_trial_26" not in repro01_source)
    checks["all_passed"] = all(v is True for v in checks.values())
    return checks


def _generate_probe(key: str, text: str) -> dict:
    """実Production entry point(generate_key_phrase_component_verified、
    review_lock guarded)を、隔離probe dir配下でそのまま呼ぶ。Trial 26の
    ような手動でTTS/ASR/Validatorを再実装した簡易版ではなく、Primary→
    Fallback遷移・review_lock記録を含めた実際のProduction pathをそのまま
    発火させる(Runtime evidence)。"""
    theme_dir = f"{RUNTIME_DIR}/probe_{key}/a2"
    narration_dir = f"{theme_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    out_path = f"{narration_dir}/kp_probe_{key}.wav"

    result = repro01.generate_key_phrase_component_verified(text, out_path)

    level_out_dir = review_lock._level_out_dir_from_out_path(out_path)
    store = review_lock._load_store(level_out_dir)
    lock_entry = store.get(f"kp_probe_{key}")

    envelope = _measure_word_envelope(out_path) if os.path.exists(out_path) else None

    return {
        "key": key, "text": text, "status": result.get("status"),
        "verified": result.get("status") == "OK",
        "fallback_used": result.get("fallback_used"),
        "primary_instruction_type": result.get("primary_instruction_type"),
        "model": result.get("model"), "voice": result.get("voice"),
        "asr_text": result.get("asr_text"),
        "duration_seconds": result.get("duration_seconds"),
        "call_count": result.get("call_count"), "retry_count": result.get("retry_count"),
        "disfluency_checked": result.get("disfluency_checked"),
        "disfluency_evidence": result.get("disfluency_evidence"),
        "audio_classification": result.get("audio_classification"),
        "review_lock_state": lock_entry.get("state") if lock_entry else None,
        "instruction_full_text": result.get("instruction_full_text"),
        "audio_path": out_path if os.path.exists(out_path) else None,
        "sha256": _sha256(out_path) if os.path.exists(out_path) else None,
        "envelope_analysis": envelope,
        "reason": result.get("reason"),
    }


def step2_runtime_evidence_all_fixtures() -> dict:
    results = {}
    for key, text in ALL_FIXTURES.items():
        results[key] = _generate_probe(key, text)
    return results


def step3_splice_a_catch_into_a2(a_catch_probe: dict) -> dict:
    """probe生成済みの実Production「a catch」音声を、No.9 A2の
    kp4_en.wavへ差し替える(Attempt-4 one-off scriptと同じsplice
    パターン、旧ファイルはbackupとして保持)。"""
    if not a_catch_probe.get("verified"):
        raise RuntimeError(
            f"A_CATCH_PROBE_NOT_VERIFIED: 実Production pathでの生成がPASSしていません"
            f"(status={a_catch_probe.get('status')})。A2への反映を中止します。")

    os.makedirs(NARRATION_DIR, exist_ok=True)
    old_existed = os.path.exists(KP4_EN_PATH)
    old_sha256 = _sha256(KP4_EN_PATH) if old_existed else None
    if old_existed and not os.path.exists(KP4_EN_PRE_WIRING27_BACKUP_PATH):
        shutil.copyfile(KP4_EN_PATH, KP4_EN_PRE_WIRING27_BACKUP_PATH)
    shutil.copyfile(a_catch_probe["audio_path"], KP4_EN_PATH)
    new_sha256 = _sha256(KP4_EN_PATH)

    with open(TTS_RESULTS_PATH, "r", encoding="utf-8") as f:
        tts_results = json.load(f)
    kp4_english = tts_results["key_phrases"]["4"]["english"]
    kp4_english["status"] = "OK"
    kp4_english["path"] = KP4_EN_PATH
    kp4_english["reused"] = False
    kp4_english["master_audio_id"] = None
    kp4_english["cache_miss_reason"] = "function_word_reduction_instruction_changed"
    kp4_english["sha256"] = new_sha256
    kp4_english["asr_verified"] = True
    kp4_english["asr_text"] = a_catch_probe["asr_text"]
    kp4_english["disfluency_checked"] = a_catch_probe["disfluency_checked"]
    kp4_english["disfluency_evidence"] = a_catch_probe["disfluency_evidence"]
    kp4_english["function_word_reduction_wiring"] = {
        "management_id": MANAGEMENT_ID,
        "note": ("ER-010-NO9-A2-KEYPHRASE-ARTICLE-REDUCTION-DIAGNOSTIC-AND-TRIAL-26で検証・"
                 "ユーザー承認済みのfunction-word/article reduction原則を、KEY_PHRASE_MINIMAL_"
                 "INSTRUCTION_PREFIXへ正式追加した後の実Production path(Trial専用scriptでは"
                 "ない)から生成した音声。旧kp4_en.wavはbackupとして保持。"),
        "old_kp4_en_sha256": old_sha256,
        "old_kp4_en_backup_path": KP4_EN_PRE_WIRING27_BACKUP_PATH if old_existed else None,
        "primary_instruction_type": a_catch_probe["primary_instruction_type"],
        "fallback_used": a_catch_probe["fallback_used"],
        "model": a_catch_probe["model"], "voice": a_catch_probe["voice"],
        "duration_seconds": a_catch_probe["duration_seconds"],
        "call_count": a_catch_probe["call_count"],
        "envelope_analysis": a_catch_probe["envelope_analysis"],
    }
    with open(TTS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2, default=str)

    return {
        "old_kp4_en_existed": old_existed, "old_kp4_en_sha256": old_sha256,
        "new_kp4_en_sha256": new_sha256,
        "new_kp4_en_sha256_matches_probe": new_sha256 == a_catch_probe["sha256"],
    }


def step4_reassemble_a2() -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": A2_OUT_DIR}
    summary = asm.stage_assemble_a2(theme)
    return summary


def step5_verify_assembled(assemble_summary: dict) -> dict:
    timeline_path = f"{A2_DIR}/audit/timeline.json"
    with open(timeline_path, "r", encoding="utf-8") as f:
        timeline = json.load(f)

    kp4_entries = [t for t in timeline if t["part"] == "Key Phrase 4"]
    kp_labels = [t["part"] for t in timeline if t["part"].startswith("Key Phrase")]
    part_names = [t["part"] for t in timeline]
    exempt = {"Notification 1", "Notification 2", "Notification 3",
              "Point Notification (Point One cue)", "Point Notification (Point Two cue)"}
    duplicates = [p for p in set(part_names) if part_names.count(p) > 1
                  and not p.startswith("pause_") and p not in exempt]

    assembled_path = assemble_summary["out_path"]
    samples, sr, channels, _nframes = common.read_wav_float(assembled_path)
    if channels > 1:
        samples = samples.reshape(-1, channels)
    total_duration = len(samples) / sr

    result = {
        "assembled_path": assembled_path,
        "total_duration_seconds": round(total_duration, 3),
        "total_duration_from_summary": assemble_summary["duration_seconds"],
        "clipping_detected": assemble_summary["clipping_detected"],
        "sample_rate": assemble_summary["sample_rate"], "channels": assemble_summary["channels"],
        "kp_labels_present": kp_labels, "segment_count": len(timeline),
        "kp4_appears_exactly_once": len(kp4_entries) == 1,
        "kp4_timeline_entry": kp4_entries[0] if kp4_entries else None,
        "unexpected_duplicate_named_segments": duplicates,
    }

    if kp4_entries:
        entry = kp4_entries[0]
        start_idx = int(entry["start_seconds"] * sr)
        end_idx = int((entry["start_seconds"] + entry["duration_seconds"]) * sr)
        clip = samples[start_idx:end_idx, 0] if samples.ndim == 2 else samples[start_idx:end_idx]
        clip_path = f"{OUT_DIR}/assembled_kp4_a_catch_clip_check.wav"
        os.makedirs(OUT_DIR, exist_ok=True)
        common.write_wav_float(clip_path, clip, sr, 1)
        asr_text, asr_err = routing.transcribe(clip_path, language="en-US")
        result["assembled_kp4_clip_check_path"] = clip_path
        result["assembled_kp4_clip_asr_text"] = asr_text
        result["assembled_kp4_clip_asr_error"] = asr_err
        result["assembled_kp4_clip_envelope_analysis"] = _measure_word_envelope(clip_path)

    return result


def run_all() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    dangling = step1_dangling_reference_check()
    fixtures = step2_runtime_evidence_all_fixtures()
    splice = step3_splice_a_catch_into_a2(fixtures["a_catch"])
    assemble_summary = step4_reassemble_a2()
    verify = step5_verify_assembled(assemble_summary)

    result = {
        "management_id": MANAGEMENT_ID,
        "dangling_reference_check": dangling,
        "runtime_evidence_fixtures": fixtures,
        "a2_splice": splice,
        "assemble_summary": assemble_summary,
        "assembled_verify": verify,
    }
    with open(f"{OUT_DIR}/wiring27_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    return result


if __name__ == "__main__":
    run_all()
