# ============================================================
# er003_v1_b1_p3r_generate.py
# ER-003-B1-P3R: A01 Listening Preview + B1本文 通し音声プロトタイプ生成
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p3r_generate.py

from __future__ import annotations

import hashlib
import json
import os
import time

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p3r_audio as p3r

OUT_DIR = "er003_output/b1_p3r/A01"


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _save_wav(path: str, pcm_bytes: bytes) -> None:
    with open(path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm_bytes, common.SAMPLE_RATE))


def run(tts_call_fn=None, sleep_function=sleep_fn) -> dict:
    for sub in ("source", "raw", "components"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)

    pattern_a_text = p3r.load_pattern_a_text()
    b1_article_text = p3r.load_b1_article_text()
    pattern_a_sha256_before = p3r.sha256_text(pattern_a_text)
    b1_article_sha256_before = p3r.sha256_text(b1_article_text)

    with open(f"{OUT_DIR}/source/pattern_a_source.md", "w", encoding="utf-8") as f:
        f.write(pattern_a_text)
    with open(f"{OUT_DIR}/source/b1_article_source.md", "w", encoding="utf-8") as f:
        f.write(b1_article_text)

    script = p3r.parse_b1_markdown_to_script(b1_article_text)
    plan = common.build_narration_plan(script)
    style_prefix = p3r.build_style_prefix()

    if tts_call_fn is None:
        tts_call_fn = gclient.make_tts_call_fn(p3r.VOICE_NAME)

    # --- Preview(1生成単位) ---
    preview_prompt = p3r.build_tts_prompt(pattern_a_text, style_prefix)
    preview_pcm, preview_retries, preview_ok, preview_err = common._call_tts_with_retry(
        tts_call_fn, preview_prompt, max_retry=p3r.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not preview_ok:
        return {"status": "STOPPED", "reason": f"Preview TTS failed after retry: {preview_err}"}

    # --- B1本文(既存採用済み3チャンク) ---
    body_pcms = []
    body_retries_total = 0
    for label, text in plan.chunks:
        prompt = p3r.build_tts_prompt(text, style_prefix)
        pcm, retries, ok, err = common._call_tts_with_retry(
            tts_call_fn, prompt, max_retry=p3r.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
        body_retries_total += retries
        if not ok:
            return {"status": "STOPPED", "reason": f"B1 body chunk '{label}' TTS failed after retry: {err}"}
        body_pcms.append(pcm)

    # --- component保存 ---
    _save_wav(f"{OUT_DIR}/components/01_listening_preview.wav", preview_pcm)
    body_combined_pcm, body_pause_offsets = common.assemble_audio(
        body_pcms, sample_rate=common.SAMPLE_RATE, pause_seconds=common.SECTION_JOIN_PAUSE_SECONDS)
    _save_wav(f"{OUT_DIR}/components/02_b1_article.wav", body_combined_pcm)

    # --- raw(本文個別チャンク) ---
    _save_wav(f"{OUT_DIR}/raw/listening_preview_chunk.wav", preview_pcm)
    for i, pcm in enumerate(body_pcms, start=1):
        _save_wav(f"{OUT_DIR}/raw/b1_article_chunk_{i}.wav", pcm)

    # --- 全体結合(Preview + 0.8秒 + B1本文) ---
    final_raw_pcm, top_pause_offsets = common.assemble_audio(
        [preview_pcm, body_combined_pcm], sample_rate=common.SAMPLE_RATE,
        pause_seconds=common.SECTION_JOIN_PAUSE_SECONDS)

    raw_wav_path = f"{OUT_DIR}/A01_b1_full_experience_raw.wav"
    _save_wav(raw_wav_path, final_raw_pcm)

    # --- Dynamics3を一度だけ適用 ---
    c0_mono = common.pcm_bytes_to_float_mono(final_raw_pcm)
    dynamics_result = common.apply_dynamics3_once(c0_mono, common.SAMPLE_RATE)

    # MP3エンコーダ(ffmpeg/pydub等)がこの環境に存在しないため、final成果物は
    # WAVのまま保存する(新しい音声変換基盤の追加はスコープ外のため導入しない)。
    final_wav_path = f"{OUT_DIR}/A01_b1_full_experience_final.wav"
    common.write_wav_float(final_wav_path, dynamics_result.c1_samples, common.SAMPLE_RATE, 1)

    pattern_a_sha256_after = p3r.sha256_text(p3r.load_pattern_a_text())
    b1_article_sha256_after = p3r.sha256_text(p3r.load_b1_article_text())

    metrics_raw = common.measure_metrics(c0_mono, common.SAMPLE_RATE)
    metrics_final = dynamics_result.metrics_c1

    # 無音位置をサンプル単位からPCMバイトオフセット→秒へ変換(top_pause_offsetsは
    # int16 PCMバイト列内のバイトオフセット)。
    top_pause_seconds = [offset / 2 / common.SAMPLE_RATE for offset in top_pause_offsets]
    body_pause_seconds = [offset / 2 / common.SAMPLE_RATE for offset in body_pause_offsets]

    metadata = {
        "management_id": "ER-003-B1-P3R",
        "article_id": p3r.ARTICLE_ID,
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "pattern_a_source_path": p3r.PATTERN_A_SOURCE_PATH,
        "pattern_a_source_sha256_before": pattern_a_sha256_before,
        "pattern_a_source_sha256_after": pattern_a_sha256_after,
        "b1_article_source_path": p3r.B1_ARTICLE_SOURCE_PATH,
        "b1_article_source_sha256_before": b1_article_sha256_before,
        "b1_article_source_sha256_after": b1_article_sha256_after,
        "source_unchanged": (
            pattern_a_sha256_before == pattern_a_sha256_after
            and b1_article_sha256_before == b1_article_sha256_after
        ),
        "tts_model": common.MODEL_NAME,
        "voice": p3r.VOICE_NAME,
        "tts_instruction_used": style_prefix,
        "preview_tts_call_count": 1 + preview_retries,
        "b1_article_tts_call_count": len(plan.chunks) + body_retries_total,
        "preview_retry_count": preview_retries,
        "b1_article_retry_count_total": body_retries_total,
        "max_technical_retry": p3r.MAX_TTS_TECHNICAL_RETRY,
        "b1_article_chunk_labels": [label for label, _ in plan.chunks],
        "section_join_pause_seconds": common.SECTION_JOIN_PAUSE_SECONDS,
        "top_level_pause_offsets_seconds": top_pause_seconds,
        "body_internal_pause_offsets_seconds": body_pause_seconds,
        "dynamics3_applied": dynamics_result.applied_once,
        "dynamics3_params": dynamics_result.dynamics_params,
        "loudness_matching": dynamics_result.loudness_matching,
        "component_paths": {
            "listening_preview": f"{OUT_DIR}/components/01_listening_preview.wav",
            "b1_article": f"{OUT_DIR}/components/02_b1_article.wav",
        },
        "component_durations_seconds": {
            "listening_preview": round(len(preview_pcm) / 2 / common.SAMPLE_RATE, 3),
            "b1_article": round(len(body_combined_pcm) / 2 / common.SAMPLE_RATE, 3),
        },
        "final_raw_path": raw_wav_path,
        "final_path": final_wav_path,
        "final_path_format_note": (
            "MP3エンコーダ(ffmpeg/pydub)がこの環境に存在しないため、"
            "指示のfinal.mp3ではなくWAV(final.wav)として保存した。"
            "新しい音声変換基盤の追加は本ステージのスコープ外と判断したため。"
        ),
        "sample_rate": common.SAMPLE_RATE,
        "channels": 1,
        "metrics_raw": metrics_raw,
        "metrics_final": metrics_final,
        "final_duration_seconds": metrics_final["duration_seconds"],
        "final_sha256": hashlib.sha256(open(final_wav_path, "rb").read()).hexdigest(),
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
        print(f"final_duration_seconds={result['metadata']['final_duration_seconds']}")
        print(f"source_unchanged={result['metadata']['source_unchanged']}")
