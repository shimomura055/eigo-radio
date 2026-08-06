# ============================================================
# er003_b1_p8a_audio.py
# ER-003-B1-P8A: Preview＋本編 通し試聴版生成
# ============================================================
# P7Cでユーザー合格済みのPreview完成版を固定し、A01 B1本編(承認済み
# 原稿、ER-002以来の凍結仕様)の音声を生成(未生成のため新規)して、
# Preview→本編の順で接続する。Preview/本編とも再加工しない(crossfade・
# time stretch・pitch変更・自動音量補正は行わない)。
#
# 調査で確認した事実(推測ではない):
#   - A01 B1本編の音声は、このリポジトリの全履歴を通じて一度も生成
#     されていない(P3R/P4のaudio_metadata.jsonはb1_article source
#     のsha256を記録するのみで、TTS call数は常に0)
#   - 承認済み原稿: er003_output/b1_p1/A01/b1_article_raw.md
#     (ER-003-B1-P1自身はPROTOTYPE/NOT_APPROVEDと自己申告しているが、
#     後続のP2/P3Rのcommitメッセージでは「承認済みA01 B1本文」と
#     一貫して呼ばれている。ファイルとしての明示的な承認記録は
#     存在しないため、本ステージ実行前にユーザーへ直接確認し、
#     使用してよいと回答を得た)
#
# 再利用するもの(再実装しない):
#   - er002_common.build_style_prefix/build_narration_plan/
#     run_tts_content_attempts/assemble_audio/pcm_to_wav_bytes/
#     pcm_bytes_to_float_mono/read_wav_float/write_wav_float/
#     measure_metrics/apply_dynamics3_once/MODEL_NAME/QA_MODEL_NAME/
#     SECTION_JOIN_PAUSE_SECONDS
#   - er002_gemini_client.make_tts_call_fn/make_qa_call_fn
#   - er003_b1_p3r_audio.B1_ARTICLE_SOURCE_PATH/VOICE_NAME/
#     load_b1_article_text/parse_b1_markdown_to_script
#   - er003_b1_p3u_audio.find_speech_bounds(音量診断の発話区間検出のみ、
#     marker除去等の判断には使わない)
#   - er003_b1_p3z_audio.adjust_trailing_silence/adjust_leading_silence
#   - er003_b1_p7a_audio.sha256_file/sha256_text
#   - er003_b1_p7c_audio.tight_speech_only(区間検出のみ再利用)

from __future__ import annotations

import numpy as np

import er002_common as common
import er003_b1_p3r_audio as p3r
import er003_b1_p3u_audio as p3u
import er003_b1_p3z_audio as p3z
import er003_b1_p7a_audio as p7a
import er003_b1_p7c_audio as p7c

ARTICLE_ID = "A01"

PREVIEW_PATH = "er003_output/b1_p7c/A01/A01_p7c_gemini31_english_replaced_dynamics3.wav"
# 2026-08-06: P7Cの無音間隔バグ修正後の値(旧: cf12636c...)。
PREVIEW_EXPECTED_SHA256 = "111788d635637be7d4edb38d2c45784a5d929144cbf7e68e5e1e3b31c0671168"

B1_ARTICLE_SOURCE_PATH = p3r.B1_ARTICLE_SOURCE_PATH  # er003_output/b1_p1/A01/b1_article_raw.md
VOICE_NAME = p3r.VOICE_NAME  # "Aoede"(Previewと同一話者、本編は別モデルだがvoice名は共通)

PREVIEW_MODEL_NAME = p7a.CANDIDATE_MODEL_NAME  # "gemini-3.1-flash-tts-preview"
ARTICLE_BODY_MODEL_NAME = common.MODEL_NAME  # "gemini-2.5-pro-preview-tts"(凍結仕様、変更しない)

TRANSITION_PAUSE_SECONDS = 0.80  # 指示section9、本編セクション境界と同一値


def sha256_file(path: str) -> str:
    return p7a.sha256_file(path)


def verify_preview_unchanged(path: str = PREVIEW_PATH, expected_sha256: str = PREVIEW_EXPECTED_SHA256) -> dict:
    actual = sha256_file(path)
    return {"path": path, "expected_sha256": expected_sha256, "actual_sha256": actual, "matches": actual == expected_sha256}


def load_and_build_narration_plan(path: str = B1_ARTICLE_SOURCE_PATH) -> "common.NarrationPlan":
    text = p3r.load_b1_article_text(path)
    script = p3r.parse_b1_markdown_to_script(text)
    plan = common.build_narration_plan(script)
    return plan, text, script


# ============================================================
# 本編音声生成(未生成の場合のみ、凍結仕様のまま)
# ============================================================
def generate_article_body_audio(plan: "common.NarrationPlan", tts_call_fn=None, qa_call_fn=None, sleep_function=None) -> dict:
    import er002_gemini_client as gclient
    call_fn = tts_call_fn or gclient.make_tts_call_fn(VOICE_NAME)
    qa_fn = qa_call_fn or gclient.make_qa_call_fn()
    style_prefix = common.build_style_prefix()

    result = common.run_tts_content_attempts(plan, style_prefix, call_fn, qa_fn)
    if result.status != "OK":
        return {"status": "STOPPED", "reason": "本編TTSが全試行不合格でした", "result": result}

    samples = common.pcm_bytes_to_float_mono(result.accepted_audio)
    dyn = common.apply_dynamics3_once(samples, common.SAMPLE_RATE)

    return {
        "status": "OK", "accepted_attempt": result.accepted_attempt,
        "attempts_count": len(result.attempts),
        "pre_dynamics3_samples": samples, "post_dynamics3_samples": dyn.c1_samples,
        "model": ARTICLE_BODY_MODEL_NAME, "voice": VOICE_NAME, "style_prefix": style_prefix,
        "sample_rate": common.SAMPLE_RATE,
        "num_chunks": len(plan.chunks),
    }


# ============================================================
# 接続(Preview → 0.8秒 → 本編)、実効間隔ベース、crossfade等なし
# ============================================================
def concatenate_preview_and_body(preview_samples: "np.ndarray", body_samples: "np.ndarray", sample_rate: int,
                                  pause_seconds: float = TRANSITION_PAUSE_SECONDS) -> dict:
    """PreviewとPreview末尾の可聴音・本編先頭の可聴音を検出し(RMSは診断・
    パディング計算のみに使用、内容の削除には使わない)、可聴音間の実効
    間隔がpause_secondsになるよう、Preview側に末尾無音を追加/削減し、
    本編側の先頭無音はそのまま維持した上で不足分を追加する。両者の
    発話内容は一切変更しない。"""
    preview_bounds = p3u.find_speech_bounds(preview_samples, sample_rate)
    body_bounds = p3u.find_speech_bounds(body_samples, sample_rate)
    if preview_bounds is None or body_bounds is None:
        raise ValueError("PreviewまたはB1本編の発話区間を検出できません")

    preview_speech_end = preview_bounds[1]
    body_speech_start = body_bounds[0]

    preview_adjusted, preview_info = p3z.adjust_trailing_silence(
        preview_samples, sample_rate, preview_speech_end, pause_seconds)
    body_adjusted, body_info = p3z.adjust_leading_silence(
        body_samples, sample_rate, body_speech_start, 0.0)

    combined = np.concatenate([preview_adjusted, body_adjusted]).astype(preview_samples.dtype)

    return {
        "combined": combined,
        "preview_trailing_adjustment": preview_info,
        "body_leading_adjustment": body_info,
        "preview_length_samples": len(preview_adjusted),
        "body_start_sample_in_combined": len(preview_adjusted),
        "effective_gap_seconds": preview_info["achieved_trailing_seconds"],
    }


# ============================================================
# 音量診断
# ============================================================
def loudness_diagnostics(samples: "np.ndarray", sample_rate: int, label: str) -> dict:
    metrics = common.measure_metrics(samples, sample_rate)
    peak = float(np.max(np.abs(samples))) if len(samples) else 0.0
    rms = float(np.sqrt(np.mean(samples.astype(np.float64) ** 2))) if len(samples) else 0.0
    bounds = p3u.find_speech_bounds(samples, sample_rate)
    tail_seconds = 3.0
    head_seconds = 3.0
    tail_slice = samples[max(0, len(samples) - int(tail_seconds * sample_rate)):]
    head_slice = samples[:int(head_seconds * sample_rate)]
    tail_rms = float(np.sqrt(np.mean(tail_slice.astype(np.float64) ** 2))) if len(tail_slice) else 0.0
    head_rms = float(np.sqrt(np.mean(head_slice.astype(np.float64) ** 2))) if len(head_slice) else 0.0

    return {
        "label": label, "duration_seconds": metrics["duration_seconds"],
        "peak": round(peak, 5), "rms": round(rms, 5), "clipping_detected": metrics["clipping_detected"],
        "speech_bounds_seconds": None if bounds is None else [round(bounds[0] / sample_rate, 4), round(bounds[1] / sample_rate, 4)],
        f"last_{tail_seconds:.0f}s_rms": round(tail_rms, 5),
        f"first_{head_seconds:.0f}s_rms": round(head_rms, 5),
    }


def extract_transition_clip(combined: "np.ndarray", sample_rate: int, body_start_sample: int,
                             preview_tail_seconds: float = 10.0, body_head_seconds: float = 15.0) -> "np.ndarray":
    start = max(0, body_start_sample - int(preview_tail_seconds * sample_rate))
    end = min(len(combined), body_start_sample + int(body_head_seconds * sample_rate))
    return combined[start:end]


def check_model_isolation() -> dict:
    return {
        "preview_model": PREVIEW_MODEL_NAME,
        "article_body_model": ARTICLE_BODY_MODEL_NAME,
        "isolated": PREVIEW_MODEL_NAME != ARTICLE_BODY_MODEL_NAME,
        "article_body_model_is_frozen_spec": ARTICLE_BODY_MODEL_NAME == "gemini-2.5-pro-preview-tts",
    }
