# ============================================================
# er003_v1_b1_p4_generate.py
# ER-003-B1-P4: Pattern A全文＋B1本文・通し試聴版生成
# ============================================================
# Part A: Listening Preview全文(5マーカー・MFA・英語Key Phrase置換)
# Part B: B1本文(既存3チャンク方式)
# Part C: 結合 + Dynamics3(全体へ1回のみ)
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p4_generate.py

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time

import numpy as np

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p3r_audio as p3r
import er003_b1_p3u_audio as p3u
import er003_b1_p3w_audio as p3w
import er003_b1_p3z_audio as p3z
import er003_b1_p4_audio as p4

OUT_DIR = "er003_output/b1_p4/A01"


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _save_wav_pcm(path: str, pcm_bytes: bytes) -> None:
    with open(path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm_bytes, common.SAMPLE_RATE))


def _mkdirs() -> None:
    for sub in (
        "source", "preview/raw", "preview/alignment", "preview/keywords",
        "preview/final", "body/raw", "body/final", "full",
    ):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)


# ============================================================
# Part A: Listening Preview
# ============================================================
def _step_save_sources() -> dict:
    pattern_a_text = p4.load_pattern_a_text()
    b1_article_text = p4.load_b1_article_text()
    keywords_data = p4.load_keywords_selected()

    with open(p4.PATTERN_A_SOURCE_PATH, encoding="utf-8") as f:
        pattern_a_raw_json_text = f.read()
    pattern_a_used_forms = json.loads(pattern_a_raw_json_text)
    used_forms = next(p for p in pattern_a_used_forms["patterns"] if p["pattern_id"] == "A")["used_forms"]

    marker_map = p4.build_marker_map(pattern_a_text, used_forms)
    tts_script = p4.build_tts_script_with_markers(pattern_a_text, marker_map)

    with open(f"{OUT_DIR}/source/pattern_a_approved.md", "w", encoding="utf-8") as f:
        f.write(pattern_a_text)
    with open(f"{OUT_DIR}/source/pattern_a_tts_with_katakana_markers.txt", "w", encoding="utf-8") as f:
        f.write(tts_script)
    with open(f"{OUT_DIR}/source/marker_map.json", "w", encoding="utf-8") as f:
        json.dump(marker_map, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/source/b1_body_approved.md", "w", encoding="utf-8") as f:
        f.write(b1_article_text)

    source_hashes = {
        "pattern_a_source_path": p4.PATTERN_A_SOURCE_PATH,
        "pattern_a_source_sha256": _sha256_file(p4.PATTERN_A_SOURCE_PATH),
        "b1_article_source_path": p4.B1_ARTICLE_SOURCE_PATH,
        "b1_article_source_sha256": _sha256_file(p4.B1_ARTICLE_SOURCE_PATH),
        "keywords_source_path": p4.KEYWORDS_SOURCE_PATH,
        "keywords_source_sha256": _sha256_file(p4.KEYWORDS_SOURCE_PATH),
        "pattern_a_text_sha256": _sha256_text(pattern_a_text),
        "b1_article_text_sha256": _sha256_text(b1_article_text),
    }
    with open(f"{OUT_DIR}/source/source_hashes.json", "w", encoding="utf-8") as f:
        json.dump(source_hashes, f, ensure_ascii=False, indent=2)

    return {
        "pattern_a_text": pattern_a_text,
        "b1_article_text": b1_article_text,
        "marker_map": marker_map,
        "tts_script": tts_script,
        "source_hashes": source_hashes,
    }


def _step_generate_preview_ja(tts_script: str, tts_call_fn, sleep_function) -> dict:
    prompt = p4.build_tts_prompt(tts_script, p4.JAPANESE_STYLE_PREFIX)
    pcm, retries, ok, err = common._call_tts_with_retry(
        tts_call_fn, prompt, max_retry=p4.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not ok:
        return {"status": "STOPPED", "phase": "Step7", "reason": f"日本語Preview TTSが失敗: {err}"}

    wav_path = f"{OUT_DIR}/preview/raw/preview_ja_with_5_markers.wav"
    _save_wav_pcm(wav_path, pcm)
    call_count = 1 + retries
    samples, sr, ch, _ = common.read_wav_float(wav_path)
    metrics = common.measure_metrics(samples, sr)
    return {
        "status": "OK", "wav_path": wav_path, "call_count": call_count, "retry_count": retries,
        "sha256": _sha256_file(wav_path), "duration_seconds": metrics["duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "samples": samples, "sample_rate": sr,
    }


def _step_check_preview_content(wav_path: str, marker_map: list) -> dict:
    """recognize_once()は複数文の長尺音声では最初の1文しか認識しない
    ため(実機で確認済み)、連続認識版を使う。"""
    recognized, err = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP")
    if recognized is None:
        return {"status": "ERROR", "reason": err}
    check = p4.check_ja_content(recognized, marker_map)
    check["recognized_text_ja_JP"] = recognized
    check["status"] = "OK"
    return check


def _step_mfa_align_preview(tts_script: str, ja_wav_path: str, marker_map: list) -> dict:
    align_corpus_dir = f"{OUT_DIR}/preview/_mfa_corpus"
    align_output_dir = f"{OUT_DIR}/preview/alignment/_mfa_raw_output"
    os.makedirs(align_corpus_dir, exist_ok=True)
    shutil.copyfile(ja_wav_path, f"{align_corpus_dir}/preview_ja_with_5_markers.wav")
    with open(f"{align_corpus_dir}/preview_ja_with_5_markers.lab", "w", encoding="utf-8") as f:
        f.write(tts_script)

    align_result = p3w.run_mfa_align(align_corpus_dir, align_output_dir)
    if not align_result["success"]:
        return {"status": "STOPPED", "phase": "Step8", "reason": "MFA alignmentが失敗しました", "align_result": align_result}

    textgrid_path = f"{align_output_dir}/preview_ja_with_5_markers.TextGrid"
    if not os.path.exists(textgrid_path):
        return {"status": "STOPPED", "phase": "Step8", "reason": f"TextGridが生成されませんでした: {textgrid_path}"}

    dest_textgrid = f"{OUT_DIR}/preview/alignment/preview_ja_with_5_markers.TextGrid"
    shutil.copyfile(textgrid_path, dest_textgrid)
    shutil.rmtree(align_output_dir, ignore_errors=True)
    shutil.rmtree(align_corpus_dir, ignore_errors=True)

    words = p3w.parse_textgrid_words_tier(dest_textgrid)
    marker_specs = p4.marker_specs_from_marker_map(marker_map)
    spans, errors = p4.find_all_marker_spans(words, marker_specs)

    if errors or any(s is None for s in spans):
        return {
            "status": "STOPPED", "phase": "Step8",
            "reason": f"マーカー区間を特定できませんでした: {errors}",
            "textgrid_path": dest_textgrid, "spans": spans, "errors": errors,
        }

    if not p4.spans_are_monotonic_non_overlapping(spans):
        return {
            "status": "STOPPED", "phase": "Step8",
            "reason": "マーカー区間の順序が単調増加でないか、重複しています",
            "spans": spans,
        }

    return {"status": "OK", "textgrid_path": dest_textgrid, "spans": spans, "align_result": align_result}


def _step_generate_key_phrases(marker_map: list, tts_call_fn, sleep_function) -> dict:
    """rank3(shot on target)は既存P3U成果物を再利用。残り4件を新規生成。"""
    results = {}
    for e in marker_map:
        used_form = e["used_form"]
        rank = e["rank"]
        slug = e["canonical_english"].replace(" ", "_")
        filename = f"{e['appearance_order']:02d}_{slug}.wav"
        out_path = f"{OUT_DIR}/preview/keywords/{filename}"

        if used_form == "shot on target":
            if not os.path.exists(p4.EXISTING_SHOT_ON_TARGET_PATH):
                return {"status": "STOPPED", "phase": "Step9", "reason": f"既存音声が見つかりません: {p4.EXISTING_SHOT_ON_TARGET_PATH}"}
            shutil.copyfile(p4.EXISTING_SHOT_ON_TARGET_PATH, out_path)
            samples, sr, ch, _ = common.read_wav_float(out_path)
            results[used_form] = {
                "path": out_path, "reused": True, "source_path": p4.EXISTING_SHOT_ON_TARGET_PATH,
                "sha256": _sha256_file(out_path), "call_count": 0, "retry_count": 0,
                "samples": samples, "sample_rate": sr,
                "duration_seconds": round(len(samples) / sr, 4),
            }
            continue

        prompt = p4.build_tts_prompt(used_form, p4.ENGLISH_STYLE_PREFIX)
        pcm, retries, ok, err = common._call_tts_with_retry(
            tts_call_fn, prompt, max_retry=p4.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
        if not ok:
            return {"status": "STOPPED", "phase": "Step9", "reason": f"英語Key Phrase({used_form!r})のTTSが失敗: {err}"}

        raw_samples_bytes = pcm
        samples_raw = common.pcm_bytes_to_float_mono(raw_samples_bytes)
        trimmed, trim_info = p3u.trim_english_keyword_silence(samples_raw, common.SAMPLE_RATE)
        if trimmed is None:
            return {"status": "STOPPED", "phase": "Step9", "reason": f"英語Key Phrase({used_form!r})に発話区間を検出できませんでした"}

        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        results[used_form] = {
            "path": out_path, "reused": False, "call_count": 1 + retries, "retry_count": retries,
            "sha256": _sha256_file(out_path), "trim_info": trim_info,
            "samples": trimmed, "sample_rate": common.SAMPLE_RATE,
            "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
        }

    return {"status": "OK", "key_phrases": results}


def _splice_five_markers(ja_samples: "np.ndarray", sr: int, spans: list, key_phrase_results: dict, marker_map: list) -> dict:
    """元のraw Preview音声から、marker境界(元音声時刻基準)で6segmentへ
    一括分割し、各segmentの前後無音を調整して0.40秒/0.30秒の目標間隔を
    達成する。後方からの逐次置換ではなく、一括再構築方式(前の置換による
    時刻ずれを防ぐ)。"""
    n = len(spans)
    boundaries = [(0.0 if i == 0 else spans[i - 1]["end_seconds"],
                   spans[i]["start_seconds"] if i < n else len(ja_samples) / sr)
                  for i in range(n + 1)]
    # boundaries[i] = (segment_start_seconds, segment_end_seconds) for segment i (0..n)
    segments = []
    for (start_s, end_s) in boundaries:
        start_sample = int(round(start_s * sr))
        end_sample = int(round(end_s * sr))
        segments.append(ja_samples[start_sample:end_sample].copy())

    needed_trailing = round(p4.GAP_BEFORE_TARGET_SECONDS - p4.EN_TRIM_SAFETY_MARGIN_SECONDS, 4)
    needed_leading = round(p4.GAP_AFTER_TARGET_SECONDS - p4.EN_TRIM_SAFETY_MARGIN_SECONDS, 4)

    adjusted_segments = []
    segment_infos = []
    for i, seg in enumerate(segments):
        bounds = p3u.find_speech_bounds(seg, sr)
        if bounds is None:
            return {"status": "STOPPED", "phase": "Step10", "reason": f"segment{i}で発話区間を検出できませんでした"}
        speech_start, speech_end = bounds

        info = {"segment_index": i, "raw_duration_seconds": round(len(seg) / sr, 4)}
        result_seg = seg

        if i < n:  # このsegmentの後に英語markerが続く→末尾を調整
            result_seg, trail_info = p3z.adjust_trailing_silence(result_seg, sr, speech_end, needed_trailing)
            info["trailing_adjustment"] = trail_info
        if i > 0:  # このsegmentの前に英語markerがある→先頭を調整
            # 末尾調整で長さが変わっている場合があるためspeech_startはそのまま
            # (adjust_trailing_silenceは末尾のみ変更し先頭側indexは不変)
            result_seg, lead_info = p3z.adjust_leading_silence(result_seg, sr, speech_start, needed_leading)
            info["leading_adjustment"] = lead_info

        adjusted_segments.append(result_seg)
        info["adjusted_duration_seconds"] = round(len(result_seg) / sr, 4)
        segment_infos.append(info)

    # marker_mapの出現順どおりに、対応する英語Key Phrase音声を挟み込む
    parts = [adjusted_segments[0]]
    en_infos = []
    for i, e in enumerate(marker_map):
        kp = key_phrase_results[e["used_form"]]
        parts.append(kp["samples"])
        en_infos.append({"used_form": e["used_form"], "duration_seconds": kp["duration_seconds"]})
        parts.append(adjusted_segments[i + 1])

    joined = np.concatenate(parts)

    # --- 実測(結合後の音声で、同一の無音検出条件により5境界を再測定) ---
    measured = []
    cursor = 0
    for i, e in enumerate(marker_map):
        seg_before_len = len(adjusted_segments[i])
        seg_before_bounds = p3u.find_speech_bounds(adjusted_segments[i], sr)
        ja_before_speech_end_in_joined = cursor + seg_before_bounds[1]
        cursor += seg_before_len

        en_len = len(key_phrase_results[e["used_form"]]["samples"])
        en_bounds = p3u.find_speech_bounds(key_phrase_results[e["used_form"]]["samples"], sr)
        en_speech_start_in_joined = cursor + en_bounds[0]
        en_speech_end_in_joined = cursor + en_bounds[1]
        cursor += en_len

        seg_after = adjusted_segments[i + 1]
        seg_after_bounds = p3u.find_speech_bounds(seg_after, sr)
        ja_after_speech_start_in_joined = cursor + seg_after_bounds[0]

        gap_before = (en_speech_start_in_joined - ja_before_speech_end_in_joined) / sr
        gap_after = (ja_after_speech_start_in_joined - en_speech_end_in_joined) / sr

        measured.append({
            "marker_id": e["canonical_english"],
            "used_form": e["used_form"],
            "measured_gap_before_seconds": round(gap_before, 4),
            "measured_gap_after_seconds": round(gap_after, 4),
            "within_tolerance_before": abs(gap_before - p4.GAP_BEFORE_TARGET_SECONDS) <= p4.GAP_TOLERANCE_SECONDS,
            "within_tolerance_after": abs(gap_after - p4.GAP_AFTER_TARGET_SECONDS) <= p4.GAP_TOLERANCE_SECONDS,
        })
        # cursorはここで既にadjusted_segments[i+1]の開始位置を指しており、
        # 次イテレーションのseg_before_lenがそのままadjusted_segments[i+1]の
        # 長さを加算するため、次のjoined内位置計算にそのまま使える。

    return {
        "status": "OK",
        "joined": joined,
        "sample_rate": sr,
        "segment_infos": segment_infos,
        "measured_boundaries": measured,
        "needed_trailing_seconds": needed_trailing,
        "needed_leading_seconds": needed_leading,
    }


def run_part_a(tts_call_fn=None, sleep_function=sleep_fn) -> dict:
    _mkdirs()
    sources = _step_save_sources()

    gen = _step_generate_preview_ja(sources["tts_script"], tts_call_fn or gclient.make_tts_call_fn(p4.VOICE_NAME), sleep_function)
    if gen["status"] != "OK":
        return {**gen, "sources": sources}

    content_check = _step_check_preview_content(gen["wav_path"], sources["marker_map"])
    if content_check.get("status") != "OK" or not content_check.get("is_japanese") or not content_check.get("all_markers_present_once"):
        return {
            "status": "STOPPED", "phase": "Step7-content-check",
            "reason": "raw Preview音声が日本語であること・5マーカーの存在を確認できませんでした",
            "content_check": content_check, "gen": {k: v for k, v in gen.items() if k != "samples"},
        }

    mfa = _step_mfa_align_preview(sources["tts_script"], gen["wav_path"], sources["marker_map"])
    if mfa["status"] != "OK":
        return {**mfa, "content_check": content_check, "gen": {k: v for k, v in gen.items() if k != "samples"}}

    kp = _step_generate_key_phrases(sources["marker_map"], tts_call_fn or gclient.make_tts_call_fn(p4.VOICE_NAME), sleep_function)
    if kp["status"] != "OK":
        return {**kp, "mfa": mfa}

    splice = _splice_five_markers(gen["samples"], gen["sample_rate"], mfa["spans"], kp["key_phrases"], sources["marker_map"])
    if splice["status"] != "OK":
        return {**splice, "kp": kp, "mfa": mfa}

    preview_raw_path = f"{OUT_DIR}/preview/final/A01_b1_listening_preview_raw.wav"
    common.write_wav_float(preview_raw_path, splice["joined"], splice["sample_rate"], 1)

    return {
        "status": "OK",
        "sources": sources,
        "gen": {k: v for k, v in gen.items() if k != "samples"},
        "content_check": content_check,
        "mfa": mfa,
        "key_phrases": kp["key_phrases"],
        "splice": splice,
        "preview_raw_path": preview_raw_path,
    }


if __name__ == "__main__":
    result = run_part_a()
    print(f"status={result['status']}")
    if result["status"] != "OK":
        print(result.get("phase"), result.get("reason"))
    else:
        for b in result["splice"]["measured_boundaries"]:
            print(b["marker_id"], b["measured_gap_before_seconds"], b["measured_gap_after_seconds"],
                  b["within_tolerance_before"], b["within_tolerance_after"])
        print("preview_raw_path:", result["preview_raw_path"])
