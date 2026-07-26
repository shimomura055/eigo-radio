# ============================================================
# er003_v1_b1_p6a_generate.py
# ER-003-B1-P6A: 本編分割・接続方式のPreview適用検証
# ============================================================
# 本編監査(er003_b1_p6a_audio.pyのdocstring参照)の結果に基づき、
# Pattern Aを原文の4文(読点でのさらなる分割なし)へ分割し、本編と
# 同じ設計(独立TTS call、chunk間0.8秒無音、結合後にDynamics3を1回)を
# 適用してListening Previewを生成する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p6a_generate.py

from __future__ import annotations

import difflib
import hashlib
import json
import os
import shutil
import time

import numpy as np

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p3u_audio as p3u
import er003_b1_p3w_audio as p3w
import er003_b1_p3z_audio as p3z
import er003_b1_p4_audio as p4
import er003_b1_p6a_audio as p6a

OUT_DIR = "er003_output/b1_p6a/A01"
MANAGEMENT_ID = "ER-003-B1-P6A"

# 指示section9: 新規英語生成は行わず、既存の技術検証済み英語Componentを
# そのまま流用する(shot on targetはP3U、他4件はP4Cで生成済み)。
EXISTING_EN_COMPONENT_PATHS = {
    "shot on target": p6a.EXISTING_SHOT_ON_TARGET_PATH,
    "take players off": "er003_output/b1_p4c/A01/preview/en_components/02_take_a_player_off.wav",
    "a narrow lead": "er003_output/b1_p4c/A01/preview/en_components/03_narrow_lead.wav",
    "close the door to the final": "er003_output/b1_p4c/A01/preview/en_components/04_close_the_door_to.wav",
    "stoppage time": "er003_output/b1_p4c/A01/preview/en_components/05_stoppage_time.wav",
}


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _mkdirs() -> None:
    for sub in ("source", "preview/ja_chunks", "preview/alignment", "preview/replaced_chunks", "preview/final", "instruction"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)


def _float_to_pcm_bytes(samples: "np.ndarray") -> bytes:
    clipped = np.clip(samples, -1.0, 1.0)
    return (clipped * 32767.0).astype(np.int16).tobytes()


# ============================================================
# Step 1: source保存 + chunk分割(本編と同じ思想: 文境界のみ) + 静的検証
# ============================================================
def _step_build_and_verify_plan() -> dict:
    pattern_a_text = p4.load_pattern_a_text()
    with open(p4.PATTERN_A_SOURCE_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    used_forms = next(p for p in raw["patterns"] if p["pattern_id"] == "A")["used_forms"]

    chunk_plan = p6a.build_chunk_plan(pattern_a_text, used_forms)
    static_check = p6a.verify_chunk_plan_static(chunk_plan, pattern_a_text)

    with open(f"{OUT_DIR}/source/pattern_a_approved.md", "w", encoding="utf-8") as f:
        f.write(pattern_a_text)
    with open(f"{OUT_DIR}/source/chunk_plan.json", "w", encoding="utf-8") as f:
        json.dump(chunk_plan, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/source/static_check.json", "w", encoding="utf-8") as f:
        json.dump(static_check, f, ensure_ascii=False, indent=2)

    return {"pattern_a_text": pattern_a_text, "used_forms": used_forms, "chunk_plan": chunk_plan, "static_check": static_check}


# ============================================================
# Step 2: chunkごとのTTS生成(本編と同じ: 独立call、technical retryのみ)
# ============================================================
def check_chunk_content(recognized_text: str, chunk: dict) -> dict:
    """P4Cのcheck_chunk_content(marker最大1件を前提)を、1chunkに0〜2件
    のmarkerを許容するよう一般化したもの(新規、P4Cの関数はそのままでは
    使えないため)。ASR結果は診断情報として扱い、単独で合否を決定しない。"""
    stripped = p4._strip_punctuation(recognized_text)
    ja_char_count = sum(
        1 for ch in recognized_text
        if ("぀" <= ch <= "ゟ") or ("゠" <= ch <= "ヿ") or ("一" <= ch <= "鿿")
    )
    ja_char_ratio = ja_char_count / len(recognized_text) if recognized_text else 0.0
    is_japanese = ja_char_ratio >= 0.5
    ascii_letter_count = len(p6a._ASCII_LETTER_PATTERN.findall(recognized_text))
    marker_count_in_recognized = stripped.count(p6a.MARKER_TOKEN)
    expected_marker_count = len(chunk["used_forms"])
    marker_ok = marker_count_in_recognized == expected_marker_count
    ref_stripped = p4._strip_punctuation(chunk["tts_text"])
    similarity_ratio = difflib.SequenceMatcher(None, ref_stripped, stripped).ratio()
    similarity_ok = similarity_ratio >= 0.5
    passed = is_japanese and ascii_letter_count == 0 and marker_ok and similarity_ok
    return {
        "recognized_text_ja_JP": recognized_text, "ja_char_ratio": round(ja_char_ratio, 4),
        "is_japanese": is_japanese, "ascii_letter_count": ascii_letter_count,
        "marker_count_in_recognized": marker_count_in_recognized, "expected_marker_count": expected_marker_count,
        "marker_ok": marker_ok, "content_similarity_ratio": round(similarity_ratio, 4),
        "similarity_ok": similarity_ok, "passed": passed,
    }


def _step_generate_all_chunks(chunk_plan: list, tts_call_fn, sleep_function) -> dict:
    """本編(run_tts_content_attempts)と同じく、chunkごとに独立して1回
    TTS呼び出しする(technical失敗時のみ1回retry)。品質理由での自動
    再生成は行わない。ASR診断は結果を保存するのみで、生成の可否には
    使わない(指示section10: ASR結果だけで合否を判断しない)。"""
    results = {}
    for chunk in chunk_plan:
        prompt = p6a.build_tts_prompt(chunk["tts_text"], p6a.JAPANESE_STYLE_PREFIX)
        pcm, retries, ok, err = common._call_tts_with_retry(
            tts_call_fn, prompt, max_retry=p6a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
        if not ok:
            return {"status": "STOPPED", "phase": "chunk_generation", "chunk_id": chunk["chunk_id"], "reason": f"TTSが失敗: {err}", "results": results}

        wav_path = f"{OUT_DIR}/preview/ja_chunks/chunk{chunk['chunk_id']}_ja.wav"
        with open(wav_path, "wb") as f:
            f.write(common.pcm_to_wav_bytes(pcm, common.SAMPLE_RATE))
        samples, sr, ch, _ = common.read_wav_float(wav_path)
        metrics = common.measure_metrics(samples, sr)

        recognized, stt_err = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP")
        content_check = check_chunk_content(recognized, chunk) if recognized is not None else {"status": "ERROR", "reason": stt_err}

        results[chunk["chunk_id"]] = {
            "status": "OK", "wav_path": wav_path, "call_count": 1 + retries, "retry_count": retries,
            "sha256": _sha256_file(wav_path), "duration_seconds": metrics["duration_seconds"],
            "clipping_detected": metrics["clipping_detected"], "samples": samples, "sample_rate": sr,
            "content_check": content_check,
        }
    return {"status": "OK", "results": results}


# ============================================================
# Step 3: marker chunkごとのMFA alignment(1chunkに0〜2件の「目印」)
# ============================================================
def _step_mfa_align_chunk(chunk: dict, ja_wav_path: str) -> dict:
    align_corpus_dir = f"{OUT_DIR}/preview/_mfa_corpus_{chunk['chunk_id']}"
    align_output_dir = f"{OUT_DIR}/preview/alignment/_mfa_raw_output_{chunk['chunk_id']}"
    os.makedirs(align_corpus_dir, exist_ok=True)
    stem = f"chunk{chunk['chunk_id']}_ja"
    shutil.copyfile(ja_wav_path, f"{align_corpus_dir}/{stem}.wav")
    with open(f"{align_corpus_dir}/{stem}.lab", "w", encoding="utf-8") as f:
        f.write(chunk["tts_text"])

    align_result = p3w.run_mfa_align(align_corpus_dir, align_output_dir)
    if not align_result["success"]:
        return {"status": "STOPPED", "reason": f"chunk{chunk['chunk_id']}: MFA alignmentが失敗しました", "align_result": align_result}

    textgrid_path = f"{align_output_dir}/{stem}.TextGrid"
    if not os.path.exists(textgrid_path):
        return {"status": "STOPPED", "reason": f"chunk{chunk['chunk_id']}: TextGridが生成されませんでした: {textgrid_path}"}

    dest_textgrid = f"{OUT_DIR}/preview/alignment/{stem}.TextGrid"
    shutil.copyfile(textgrid_path, dest_textgrid)
    shutil.rmtree(align_output_dir, ignore_errors=True)
    shutil.rmtree(align_corpus_dir, ignore_errors=True)

    words = p3w.parse_textgrid_words_tier(dest_textgrid)
    n = len(chunk["used_forms"])
    marker_specs = [{"marker_id": f"chunk{chunk['chunk_id']}_m{i + 1}", "token_sequence": p6a.MARKER_TOKEN_SEQUENCE} for i in range(n)]
    spans, errors = p4.find_all_marker_spans(words, marker_specs)

    if errors or any(s is None for s in spans):
        return {"status": "STOPPED", "reason": f"chunk{chunk['chunk_id']}: 「目印」区間を特定できませんでした: {errors}", "textgrid_path": dest_textgrid}
    if not p4.spans_are_monotonic_non_overlapping(spans):
        return {"status": "STOPPED", "reason": f"chunk{chunk['chunk_id']}: marker区間の順序が単調増加でないか、重複しています", "spans": spans}

    return {"status": "OK", "textgrid_path": dest_textgrid, "spans": spans, "align_result": align_result}


def _step_mfa_align_all_marker_chunks(chunk_plan: list, chunk_results: dict) -> dict:
    results = {}
    for chunk in chunk_plan:
        if chunk["chunk_type"] != "marker":
            continue
        ja_wav_path = chunk_results[chunk["chunk_id"]]["wav_path"]
        r = _step_mfa_align_chunk(chunk, ja_wav_path)
        results[chunk["chunk_id"]] = r
        if r["status"] != "OK":
            return {"status": "STOPPED", "phase": "mfa_alignment", "chunk_id": chunk["chunk_id"], "reason": r["reason"], "results": results}
    return {"status": "OK", "results": results}


# ============================================================
# Step 4: chunkごとのmarker置換(0〜2件の「目印」→既存英語Component)
# ============================================================
def _splice_markers_in_chunk(chunk: dict, ja_samples: "np.ndarray", sr: int, spans: list, en_samples_list: list) -> dict:
    """P4Bの_splice_five_markersと同一アルゴリズムを、1chunk内の
    0〜2件のmarkerへ一般化したもの(新規: 対象がPreview全体ではなく
    1chunk、marker件数が可変のため既存関数をそのまま呼べない)。"""
    n = len(spans)
    boundaries = [(0.0 if i == 0 else spans[i - 1]["end_seconds"],
                   spans[i]["start_seconds"] if i < n else len(ja_samples) / sr)
                  for i in range(n + 1)]
    segments = []
    for (start_s, end_s) in boundaries:
        start_sample = int(round(start_s * sr))
        end_sample = int(round(end_s * sr))
        segments.append(ja_samples[start_sample:end_sample].copy())

    needed_trailing = round(p6a.GAP_BEFORE_TARGET_SECONDS - p6a.EN_TRIM_SAFETY_MARGIN_SECONDS, 4)
    needed_leading = round(p6a.GAP_AFTER_TARGET_SECONDS - p6a.EN_TRIM_SAFETY_MARGIN_SECONDS, 4)

    adjusted_segments = []
    segment_infos = []
    for i, seg in enumerate(segments):
        bounds = p3u.find_speech_bounds(seg, sr)
        if bounds is None:
            return {"status": "STOPPED", "reason": f"chunk{chunk['chunk_id']} segment{i}: 発話区間を検出できませんでした"}
        speech_start, speech_end = bounds
        info = {"segment_index": i, "raw_duration_seconds": round(len(seg) / sr, 4)}
        result_seg = seg
        if i < n:
            result_seg, trail_info = p3z.adjust_trailing_silence(result_seg, sr, speech_end, needed_trailing)
            info["trailing_adjustment"] = trail_info
        if i > 0:
            result_seg, lead_info = p3z.adjust_leading_silence(result_seg, sr, speech_start, needed_leading)
            info["leading_adjustment"] = lead_info
        adjusted_segments.append(result_seg)
        info["adjusted_duration_seconds"] = round(len(result_seg) / sr, 4)
        segment_infos.append(info)

    parts = [adjusted_segments[0]]
    for i in range(n):
        parts.append(en_samples_list[i])
        parts.append(adjusted_segments[i + 1])
    joined = np.concatenate(parts)

    measured = []
    cursor = 0
    for i in range(n):
        seg_before_len = len(adjusted_segments[i])
        seg_before_bounds = p3u.find_speech_bounds(adjusted_segments[i], sr)
        ja_before_speech_end = cursor + seg_before_bounds[1]
        cursor += seg_before_len

        en_len = len(en_samples_list[i])
        en_bounds = p3u.find_speech_bounds(en_samples_list[i], sr)
        en_speech_start = cursor + en_bounds[0]
        en_speech_end = cursor + en_bounds[1]
        cursor += en_len

        seg_after_bounds = p3u.find_speech_bounds(adjusted_segments[i + 1], sr)
        ja_after_speech_start = cursor + seg_after_bounds[0]

        gap_before = (en_speech_start - ja_before_speech_end) / sr
        gap_after = (ja_after_speech_start - en_speech_end) / sr
        measured.append({
            "marker_index": i, "used_form": chunk["used_forms"][i],
            "measured_gap_before_seconds": round(gap_before, 4),
            "measured_gap_after_seconds": round(gap_after, 4),
            "within_tolerance_before": abs(gap_before - p6a.GAP_BEFORE_TARGET_SECONDS) <= p6a.GAP_TOLERANCE_SECONDS,
            "within_tolerance_after": abs(gap_after - p6a.GAP_AFTER_TARGET_SECONDS) <= p6a.GAP_TOLERANCE_SECONDS,
        })

    return {"status": "OK", "joined": joined, "sample_rate": sr, "measured": measured, "segment_infos": segment_infos}


def _step_replace_all_marker_chunks(chunk_plan: list, chunk_results: dict, mfa_results: dict) -> dict:
    final_chunks = {}
    replacement_reports = {}
    for chunk in chunk_plan:
        cid = chunk["chunk_id"]
        if chunk["chunk_type"] != "marker":
            final_chunks[cid] = chunk_results[cid]["samples"]
            continue

        ja_samples = chunk_results[cid]["samples"]
        sr = chunk_results[cid]["sample_rate"]
        spans = mfa_results[cid]["spans"]

        en_samples_list = []
        for used_form in chunk["used_forms"]:
            en_path = EXISTING_EN_COMPONENT_PATHS[used_form]
            en_samples, en_sr, _, _ = common.read_wav_float(en_path)
            en_samples_list.append(en_samples)

        r = _splice_markers_in_chunk(chunk, ja_samples, sr, spans, en_samples_list)
        if r["status"] != "OK":
            return {"status": "STOPPED", "phase": "marker_replacement", "chunk_id": cid, "reason": r["reason"]}

        replaced_path = f"{OUT_DIR}/preview/replaced_chunks/chunk{cid}_replaced.wav"
        common.write_wav_float(replaced_path, r["joined"], sr, 1)
        replacement_reports[cid] = {"measured": r["measured"], "segment_infos": r["segment_infos"], "replaced_path": replaced_path}
        final_chunks[cid] = r["joined"]

    return {"status": "OK", "final_chunks": final_chunks, "replacement_reports": replacement_reports}


# ============================================================
# Step 5: 4chunkを本編と同じ0.8秒無音で結合し、Dynamics3を1回適用
# ============================================================
def _step_assemble_and_finalize(chunk_plan: list, final_chunks: dict, sr: int) -> dict:
    pcm_chunks = [_float_to_pcm_bytes(final_chunks[c["chunk_id"]]) for c in chunk_plan]
    combined_pcm, pause_positions = common.assemble_audio(pcm_chunks, sample_rate=sr, pause_seconds=p6a.JA_CHUNK_JOIN_PAUSE_SECONDS)
    combined_samples = common.pcm_bytes_to_float_mono(combined_pcm)

    raw_path = f"{OUT_DIR}/preview/final/A01_b1_listening_preview_raw.wav"
    common.write_wav_float(raw_path, combined_samples, sr, 1)

    dynamics_result = common.apply_dynamics3_once(combined_samples, sr)
    dynamics3_path = f"{OUT_DIR}/preview/final/A01_b1_listening_preview_dynamics3.wav"
    common.write_wav_float(dynamics3_path, dynamics_result.c1_samples, sr, 1)

    return {
        "status": "OK", "raw_path": raw_path, "dynamics3_path": dynamics3_path,
        "pause_positions": pause_positions, "pause_count": len(pause_positions),
        "metrics_c0": dynamics_result.metrics_c0, "metrics_c1": dynamics_result.metrics_c1,
        "loudness_matching": dynamics_result.loudness_matching,
    }


# ============================================================
# 実行本体
# ============================================================
def run(tts_call_fn=None, sleep_function=sleep_fn) -> dict:
    _mkdirs()
    call_fn = tts_call_fn or gclient.make_tts_call_fn(p6a.VOICE_NAME)

    plan_step = _step_build_and_verify_plan()
    if not plan_step["static_check"]["all_passed"]:
        return {"status": "STOPPED", "phase": "static_check", "reason": "chunk計画の静的検証に不合格のため、TTSを呼び出さず停止", "plan_step": plan_step}

    chunk_plan = plan_step["chunk_plan"]

    gen = _step_generate_all_chunks(chunk_plan, call_fn, sleep_function)
    if gen["status"] != "OK":
        return {**gen, "plan_step": plan_step}

    mfa = _step_mfa_align_all_marker_chunks(chunk_plan, gen["results"])
    if mfa["status"] != "OK":
        return {**mfa, "plan_step": plan_step, "gen": gen}

    replace = _step_replace_all_marker_chunks(chunk_plan, gen["results"], mfa["results"])
    if replace["status"] != "OK":
        return {**replace, "plan_step": plan_step, "gen": gen, "mfa": mfa}

    sr = common.SAMPLE_RATE
    final = _step_assemble_and_finalize(chunk_plan, replace["final_chunks"], sr)

    recognized, stt_err = p4.get_full_text_via_azure_stt_continuous(final["dynamics3_path"], language="ja-JP")
    final_asr = None
    if recognized is not None:
        with open(f"{OUT_DIR}/preview/final/asr_transcript.txt", "w", encoding="utf-8") as f:
            f.write(recognized)
        final_asr = {"recognized_text_ja_JP": recognized, "kanji_target_phrase_results": p6a.check_kanji_target_phrases(recognized)}
    else:
        final_asr = {"status": "ERROR", "reason": stt_err}

    return {
        "status": "OK", "plan_step": plan_step, "gen": gen, "mfa": mfa, "replace": replace,
        "final": final, "final_asr": final_asr,
    }


if __name__ == "__main__":
    result = run()
    print(f"status={result['status']}")
    if result["status"] != "OK":
        print(result.get("phase"), result.get("reason"))
    else:
        for cid, r in result["replace"]["replacement_reports"].items():
            for m in r["measured"]:
                print(cid, m["used_form"], m["measured_gap_before_seconds"], m["measured_gap_after_seconds"],
                      m["within_tolerance_before"], m["within_tolerance_after"])
        print("raw_path:", result["final"]["raw_path"])
        print("dynamics3_path:", result["final"]["dynamics3_path"])
        if "kanji_target_phrase_results" in result["final_asr"]:
            print("kanji_target_phrase_results:", result["final_asr"]["kanji_target_phrase_results"])
