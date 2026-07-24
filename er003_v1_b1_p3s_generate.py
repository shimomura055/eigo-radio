# ============================================================
# er003_v1_b1_p3s_generate.py
# ER-003-B1-P3S: 日英分離TTS・短尺結合サンプル生成
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p3s_generate.py

from __future__ import annotations

import hashlib
import json
import os
import time

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p3s_audio as p3s

OUT_DIR = "er003_output/b1_p3s/A01"

SPAN_ORDER = ("span_01_ja_before", "span_02_en_keyword", "span_03_ja_after")


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _save_wav(path: str, pcm_bytes: bytes) -> None:
    with open(path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm_bytes, common.SAMPLE_RATE))


def _build_selected_excerpt_markdown(excerpt: dict) -> str:
    return (
        f"# ER-003-B1-P3S 選択箇所\n\n"
        f"## Key Phrase\n\n{excerpt['key_phrase']}\n\n"
        f"## span 1: 日本語(前)\n\n{excerpt['ja_before']}\n\n"
        f"## span 2: 英語Key Phrase\n\n{excerpt['en_keyword']}\n\n"
        f"## span 3: 日本語(後)\n\n{excerpt['ja_after']}\n\n"
        f"## 結合結果(原文の該当範囲と一致することを確認済み)\n\n{excerpt['reconstructed']}\n\n"
        f"## 句読点調整\n\n{'あり' if excerpt['punctuation_adjusted'] else 'なし'}\n"
    )


def run(tts_call_fn=None, sleep_function=sleep_fn, key_phrase: str = p3s.DEFAULT_KEY_PHRASE) -> dict:
    for sub in ("source", "raw", "final"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)

    pattern_a_text = p3s.load_pattern_a_text()
    pattern_a_sha256_before = p3s.sha256_text(pattern_a_text)
    excerpt = p3s.select_excerpt(pattern_a_text, key_phrase=key_phrase)

    with open(f"{OUT_DIR}/source/pattern_a_source.md", "w", encoding="utf-8") as f:
        f.write(pattern_a_text)
    with open(f"{OUT_DIR}/source/selected_excerpt.md", "w", encoding="utf-8") as f:
        f.write(_build_selected_excerpt_markdown(excerpt))
    with open(f"{OUT_DIR}/source/span_01_ja_before.txt", "w", encoding="utf-8") as f:
        f.write(excerpt["ja_before"])
    with open(f"{OUT_DIR}/source/span_02_en_keyword.txt", "w", encoding="utf-8") as f:
        f.write(excerpt["en_keyword"])
    with open(f"{OUT_DIR}/source/span_03_ja_after.txt", "w", encoding="utf-8") as f:
        f.write(excerpt["ja_after"])

    style_prefix = p3s.build_style_prefix()
    if tts_call_fn is None:
        tts_call_fn = gclient.make_tts_call_fn(p3s.VOICE_NAME)

    span_texts = {
        "span_01_ja_before": excerpt["ja_before"],
        "span_02_en_keyword": excerpt["en_keyword"],
        "span_03_ja_after": excerpt["ja_after"],
    }

    span_pcms = {}
    span_call_counts = {}
    span_retry_counts = {}
    span_durations = {}

    for label in SPAN_ORDER:
        text = span_texts[label]
        prompt = p3s.build_tts_prompt(text, style_prefix)
        pcm, retries, ok, err = common._call_tts_with_retry(
            tts_call_fn, prompt, max_retry=p3s.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
        span_retry_counts[label] = retries
        span_call_counts[label] = 1 + retries
        if not ok:
            return {
                "status": "STOPPED",
                "reason": f"{label} TTS failed after retry: {err}",
                "failed_span": label,
                "span_call_counts": span_call_counts,
                "span_retry_counts": span_retry_counts,
                "succeeded_spans": list(span_pcms.keys()),
            }
        span_pcms[label] = pcm
        span_durations[label] = round(len(pcm) / 2 / common.SAMPLE_RATE, 3)
        _save_wav(f"{OUT_DIR}/raw/{label}.wav", pcm)

    # --- 全span成功 -> 短尺結合(0.2秒無音×2) ---
    ordered_pcms = [span_pcms[label] for label in SPAN_ORDER]
    joined_pcm, pause_offsets = common.assemble_audio(
        ordered_pcms, sample_rate=common.SAMPLE_RATE, pause_seconds=p3s.JOIN_PAUSE_SECONDS)

    raw_join_path = f"{OUT_DIR}/final/A01_b1_ja_en_ja_join_sample_raw.wav"
    _save_wav(raw_join_path, joined_pcm)

    c0_mono = common.pcm_bytes_to_float_mono(joined_pcm)
    dynamics_result = common.apply_dynamics3_once(c0_mono, common.SAMPLE_RATE)

    # MP3エンコーダ(ffmpeg/pydub等)がこの環境に存在しないため、final成果物は
    # WAVのまま保存する(ER-003-B1-P3Rと同一の判断、新しい音声変換基盤は追加しない)。
    final_path = f"{OUT_DIR}/final/A01_b1_ja_en_ja_join_sample_dynamics3.wav"
    common.write_wav_float(final_path, dynamics_result.c1_samples, common.SAMPLE_RATE, 1)

    pattern_a_sha256_after = p3s.sha256_text(p3s.load_pattern_a_text())

    metrics_raw = common.measure_metrics(c0_mono, common.SAMPLE_RATE)
    metrics_final = dynamics_result.metrics_c1
    pause_offsets_seconds = [offset / 2 / common.SAMPLE_RATE for offset in pause_offsets]

    metadata = {
        "management_id": "ER-003-B1-P3S",
        "article_id": p3s.ARTICLE_ID,
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "pattern_a_source_path": p3s.PATTERN_A_SOURCE_PATH,
        "pattern_a_source_sha256_before": pattern_a_sha256_before,
        "pattern_a_source_sha256_after": pattern_a_sha256_after,
        "source_unchanged": pattern_a_sha256_before == pattern_a_sha256_after,
        "selected_key_phrase": excerpt["key_phrase"],
        "span_texts": span_texts,
        "punctuation_adjusted": excerpt["punctuation_adjusted"],
        "tts_model": common.MODEL_NAME,
        "voice": p3s.VOICE_NAME,
        "tts_instruction_used": style_prefix,
        "span_call_counts": span_call_counts,
        "span_retry_counts": span_retry_counts,
        "max_technical_retry_per_span": p3s.MAX_TTS_TECHNICAL_RETRY,
        "span_durations_seconds": span_durations,
        "join_order": list(SPAN_ORDER),
        "join_pause_seconds": p3s.JOIN_PAUSE_SECONDS,
        "join_pause_count": 2,
        "join_pause_offsets_seconds": pause_offsets_seconds,
        "dynamics3_applied": dynamics_result.applied_once,
        "dynamics3_params": dynamics_result.dynamics_params,
        "loudness_matching": dynamics_result.loudness_matching,
        "raw_join_path": raw_join_path,
        "final_path": final_path,
        "final_path_format_note": (
            "MP3エンコーダ(ffmpeg/pydub)がこの環境に存在しないため、"
            "指示のdynamics3.mp3ではなくWAVとして保存した(ER-003-B1-P3Rと同一の判断)。"
        ),
        "sample_rate": common.SAMPLE_RATE,
        "channels": 1,
        "metrics_raw": metrics_raw,
        "metrics_final": metrics_final,
        "final_duration_seconds": metrics_final["duration_seconds"],
        "final_sha256": hashlib.sha256(open(final_path, "rb").read()).hexdigest(),
        "execution_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }

    with open(f"{OUT_DIR}/audio_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return {"status": "OK", "metadata": metadata}


if __name__ == "__main__":
    result = run()
    print(f"status={result['status']}")
    if result["status"] != "OK":
        print(result.get("reason"))
        print("succeeded_spans:", result.get("succeeded_spans"))
    else:
        print(f"final_duration_seconds={result['metadata']['final_duration_seconds']}")
        print(f"source_unchanged={result['metadata']['source_unchanged']}")
