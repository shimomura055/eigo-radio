# ============================================================
# er003_v1_b1_p3z_generate.py
# ER-003-B1-P3Z: 英語前後の間・9パターン比較・生成
# ============================================================
# P3Yの既存3component(ja_before_marker.wav/en_shot_on_target_trimmed.wav/
# ja_after_marker.wav)を再利用し、新しいTTS生成・MFA再実行・原稿変更は
# 一切行わない。英語前後の実効的な間だけを9パターン(3×3)に調整する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p3z_generate.py

from __future__ import annotations

import hashlib
import json
import os

import numpy as np

import er002_common as common
import er003_b1_p3u_audio as p3u
import er003_b1_p3z_audio as p3z

OUT_DIR = "er003_output/b1_p3z/A01"


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _build_one_pattern(
    pattern: dict,
    ja_before_samples: "np.ndarray",
    en_samples: "np.ndarray",
    ja_after_samples: "np.ndarray",
    sr: int,
    ja_before_silence: dict,
    en_silence: dict,
    ja_after_silence: dict,
) -> dict:
    target_before = pattern["gap_before_seconds"]
    target_after = pattern["gap_after_seconds"]
    en_leading_seconds = en_silence["leading_silence_seconds"]
    en_trailing_seconds = en_silence["trailing_silence_seconds"]

    needed_ja_before_trailing = round(target_before - en_leading_seconds, 4)
    needed_ja_after_leading = round(target_after - en_trailing_seconds, 4)

    if needed_ja_before_trailing < 0 or needed_ja_after_leading < 0:
        return {
            **pattern,
            "status": "FAIL",
            "reason": (
                f"英語component自体の既存安全余白(前{en_leading_seconds}s/後{en_trailing_seconds}s)"
                f"だけで目標値を超えるため、発話を削らずには達成できません"
            ),
        }

    ja_before_adjusted, before_info = p3z.adjust_trailing_silence(
        ja_before_samples, sr, ja_before_silence["speech_end_sample"], needed_ja_before_trailing)
    ja_after_adjusted, after_info = p3z.adjust_leading_silence(
        ja_after_samples, sr, ja_after_silence["speech_start_sample"], needed_ja_after_leading)

    joined = np.concatenate([ja_before_adjusted, en_samples, ja_after_adjusted])

    # --- 実測(結合後の音声で、同一の無音検出条件により再測定) ---
    en_start_in_joined = len(ja_before_adjusted)
    en_end_in_joined = en_start_in_joined + len(en_samples)

    ja_before_speech_end_in_joined = ja_before_silence["speech_end_sample"]
    en_speech_start_in_joined = en_start_in_joined + en_silence["speech_start_sample"]
    measured_gap_before = (en_speech_start_in_joined - ja_before_speech_end_in_joined) / sr

    en_speech_end_in_joined = en_start_in_joined + en_silence["speech_end_sample"]
    ja_after_bounds = p3u.find_speech_bounds(ja_after_adjusted, sr)
    ja_after_speech_start_in_joined = en_end_in_joined + ja_after_bounds[0]
    measured_gap_after = (ja_after_speech_start_in_joined - en_speech_end_in_joined) / sr

    within_tolerance_before = abs(measured_gap_before - target_before) <= p3z.GAP_TOLERANCE_SECONDS
    within_tolerance_after = abs(measured_gap_after - target_after) <= p3z.GAP_TOLERANCE_SECONDS

    final_path = f"{OUT_DIR}/final/{pattern['filename']}"
    dynamics_result = common.apply_dynamics3_once(joined, sr)
    common.write_wav_float(final_path, dynamics_result.c1_samples, sr, 1)
    metrics_final = dynamics_result.metrics_c1

    return {
        **pattern,
        "status": "OK" if (within_tolerance_before and within_tolerance_after) else "FAIL",
        "measured_gap_before_seconds": round(measured_gap_before, 4),
        "measured_gap_after_seconds": round(measured_gap_after, 4),
        "within_tolerance_before": within_tolerance_before,
        "within_tolerance_after": within_tolerance_after,
        "final_path": final_path,
        "final_sha256": _sha256_file(final_path),
        "duration_seconds": metrics_final["duration_seconds"],
        "clipping_detected": metrics_final["clipping_detected"],
        "dynamics3_applied": dynamics_result.applied_once,
        "before_adjustment": before_info,
        "after_adjustment": after_info,
    }


def run() -> dict:
    os.makedirs(f"{OUT_DIR}/final", exist_ok=True)

    # --- 既存3componentの再利用確認(新規TTS/MFA生成しない) ---
    for path in (p3z.EXISTING_JA_BEFORE_PATH, p3z.EXISTING_EN_PATH, p3z.EXISTING_JA_AFTER_PATH):
        if not os.path.exists(path):
            return {"status": "STOPPED", "reason": f"既存componentが見つかりません: {path}"}

    ja_before_samples, sr, _, _ = common.read_wav_float(p3z.EXISTING_JA_BEFORE_PATH)
    en_samples, sr_en, _, _ = common.read_wav_float(p3z.EXISTING_EN_PATH)
    ja_after_samples, sr_ja_after, _, _ = common.read_wav_float(p3z.EXISTING_JA_AFTER_PATH)
    if not (sr == sr_en == sr_ja_after):
        return {"status": "STOPPED", "reason": f"サンプルレート不一致(ja_before={sr}, en={sr_en}, ja_after={sr_ja_after})"}

    source_files = {
        "ja_before_marker": {
            "path": p3z.EXISTING_JA_BEFORE_PATH,
            "sha256": _sha256_file(p3z.EXISTING_JA_BEFORE_PATH),
            "duration_seconds": round(len(ja_before_samples) / sr, 4),
        },
        "en_shot_on_target_trimmed": {
            "path": p3z.EXISTING_EN_PATH,
            "sha256": _sha256_file(p3z.EXISTING_EN_PATH),
            "duration_seconds": round(len(en_samples) / sr, 4),
        },
        "ja_after_marker": {
            "path": p3z.EXISTING_JA_AFTER_PATH,
            "sha256": _sha256_file(p3z.EXISTING_JA_AFTER_PATH),
            "duration_seconds": round(len(ja_after_samples) / sr, 4),
        },
    }

    # --- 既存component内の無音を計測(9パターン全てで同一の検出条件) ---
    ja_before_silence = p3z.measure_component_silence(ja_before_samples, sr)
    en_silence = p3z.measure_component_silence(en_samples, sr)
    ja_after_silence = p3z.measure_component_silence(ja_after_samples, sr)

    for name, sil in (
        ("ja_before_marker", ja_before_silence),
        ("en_shot_on_target_trimmed", en_silence),
        ("ja_after_marker", ja_after_silence),
    ):
        if sil["speech_start_sample"] is None:
            return {"status": "STOPPED", "reason": f"{name}で発話区間を検出できませんでした"}

    patterns = p3z.build_patterns()
    pattern_results = [
        _build_one_pattern(p, ja_before_samples, en_samples, ja_after_samples, sr,
                            ja_before_silence, en_silence, ja_after_silence)
        for p in patterns
    ]

    metadata = {
        "management_id": "ER-003-B1-P3Z",
        "article_id": "A01",
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "source_files": source_files,
        "silence_detection_method": "p3u.find_speech_bounds (window_ms=20.0, silence_rms_threshold=0.02), 9パターン全てで同一条件",
        "measured_existing_silence": {
            "ja_before_marker_trailing_seconds": ja_before_silence["trailing_silence_seconds"],
            "en_leading_seconds": en_silence["leading_silence_seconds"],
            "en_trailing_seconds": en_silence["trailing_silence_seconds"],
            "ja_after_marker_leading_seconds": ja_after_silence["leading_silence_seconds"],
        },
        "design_note": (
            "en_shot_on_target_trimmed.wav自体の前後安全余白(P3Uで設定済み、"
            "各0.08秒)は固定し、変更しない。目標の実効間隔は、ja_before_marker"
            "の末尾無音とja_after_markerの先頭無音だけを調整して達成する。"
        ),
        "gap_tolerance_seconds": p3z.GAP_TOLERANCE_SECONDS,
        "dynamics3_params": common.DYNAMICS3_PARAMS,
        "sample_rate": sr,
        "channels": 1,
        "patterns": pattern_results,
        "new_tts_calls_made": 0,
        "mfa_reruns_made": 0,
        "pattern_a_full_generated": False,
        "b1_body_generated": False,
    }

    with open(f"{OUT_DIR}/audio_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return {"status": "OK", "metadata": metadata}


if __name__ == "__main__":
    result = run()
    print(f"status={result['status']}")
    if result["status"] != "OK":
        print(result.get("reason"))
    else:
        for p in result["metadata"]["patterns"]:
            print(p["no"], p["status"], p.get("measured_gap_before_seconds"),
                  p.get("measured_gap_after_seconds"), p.get("duration_seconds"))
