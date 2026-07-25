# ============================================================
# er003_v1_b1_p4c_generate.py
# ER-003-B1-P4C: 「目印」マーカーでListening Preview完成版を再生成
# ============================================================
# P4Bはchunk05(stoppage time)で、ASRが「合図」を文字列完全一致で検出
# できず(表記が「会津」「アイズ」に揺れた)停止した。本ステージでは
# markerを「目印」へ変更し、ASRは診断用途にとどめて表記完全一致を
# 合否条件にしない(er003_b1_p4c_audio.check_chunk_content)。marker
# 区間の正式な特定はMFAで行う(P4Bと同じ設計)。
#
# オーケストレーション構造はer003_v1_b1_p4b_generate.pyと並行だが、
# 出力先(OUT_DIR)がP4Bの成果物を上書きしないよう別ディレクトリと
# なるため、per-stage生成scriptとして独立させている(このプロジェクトの
# 既存の慣習: p3z/p4/p4a/p4bも各stageごとに専用のgenerate scriptを持つ)。
# 深い共有ロジック(MFA・無音調整・trim・Dynamics3等)は、er003_b1_p4b_
# audio.py同様、既存モジュールをそのまま再利用し、再実装しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p4c_generate.py

from __future__ import annotations

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
import er003_b1_p4b_audio as p4b
import er003_b1_p4c_audio as p4c

OUT_DIR = "er003_output/b1_p4c/A01"

MAX_CONTENT_REGENERATION_ATTEMPTS = 2  # 同一chunkにつき、内容確認込みで最大2回
INTER_CHUNK_GAP_STOP_THRESHOLD_SECONDS = 1.0


def sleep_fn(seconds: float) -> None:
    time.sleep(seconds)


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _mkdirs() -> None:
    for sub in (
        "source", "preview/ja_chunks", "preview/alignment",
        "preview/en_components", "preview/replaced_chunks", "preview/final",
    ):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)


# ============================================================
# Step 1: source保存 + chunk分割(「目印」marker) + 静的検証
# ============================================================
def _step_build_and_verify_plan() -> dict:
    pattern_a_text = p4.load_pattern_a_text()

    with open(p4.PATTERN_A_SOURCE_PATH, encoding="utf-8") as f:
        pattern_a_raw_json_text = f.read()
    pattern_a_used_forms = json.loads(pattern_a_raw_json_text)
    used_forms = next(p for p in pattern_a_used_forms["patterns"] if p["pattern_id"] == "A")["used_forms"]

    chunk_plan = p4b.build_chunk_plan(pattern_a_text, used_forms, marker_token=p4c.MARKER_TOKEN)
    static_check = p4b.verify_chunk_plan_static(chunk_plan, pattern_a_text, marker_token=p4c.MARKER_TOKEN)

    with open(f"{OUT_DIR}/source/pattern_a_approved.md", "w", encoding="utf-8") as f:
        f.write(pattern_a_text)
    with open(f"{OUT_DIR}/source/chunk_plan.json", "w", encoding="utf-8") as f:
        json.dump(chunk_plan, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/source/static_check.json", "w", encoding="utf-8") as f:
        json.dump(static_check, f, ensure_ascii=False, indent=2)

    source_hashes = {
        "pattern_a_source_path": p4.PATTERN_A_SOURCE_PATH,
        "pattern_a_source_sha256": _sha256_file(p4.PATTERN_A_SOURCE_PATH),
        "pattern_a_text_sha256": _sha256_text(pattern_a_text),
    }
    with open(f"{OUT_DIR}/source/source_hashes.json", "w", encoding="utf-8") as f:
        json.dump(source_hashes, f, ensure_ascii=False, indent=2)

    return {
        "pattern_a_text": pattern_a_text,
        "used_forms": used_forms,
        "chunk_plan": chunk_plan,
        "static_check": static_check,
        "source_hashes": source_hashes,
    }


# ============================================================
# Step 2: chunkごとの生成 + 内容確認(表記揺れを許容するASR診断)
# ============================================================
def _generate_one_chunk_attempt(chunk: dict, tts_call_fn, sleep_function) -> dict:
    prompt = p4c.build_tts_prompt(chunk["tts_text"], p4c.JAPANESE_STYLE_PREFIX)
    pcm, retries, ok, err = common._call_tts_with_retry(
        tts_call_fn, prompt, max_retry=p4c.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not ok:
        return {"status": "TECHNICAL_FAILURE", "reason": err, "call_count": 1 + retries}

    wav_path = f"{OUT_DIR}/preview/ja_chunks/chunk{chunk['chunk_id']}_ja.wav"
    with open(wav_path, "wb") as f:
        f.write(common.pcm_to_wav_bytes(pcm, common.SAMPLE_RATE))
    samples, sr, ch, _ = common.read_wav_float(wav_path)
    metrics = common.measure_metrics(samples, sr)

    recognized, stt_err = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP")
    if recognized is None:
        return {"status": "STT_FAILURE", "reason": stt_err, "call_count": 1 + retries}

    content_check = p4c.check_chunk_content(recognized, chunk)

    return {
        "status": "OK", "wav_path": wav_path, "call_count": 1 + retries, "retry_count": retries,
        "sha256": _sha256_file(wav_path), "duration_seconds": metrics["duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "samples": samples, "sample_rate": sr,
        "content_check": content_check,
    }


def generate_chunk_with_content_gate(chunk: dict, tts_call_fn, sleep_function) -> dict:
    """技術的失敗はcommon._call_tts_with_retry内で1回まで自動再試行される。
    技術的には成功したが内容確認に失敗した場合は、同一payloadでこの
    関数のレベルでもう1回だけ生成をやり直す。2回連続で内容確認に失敗、
    または技術的失敗した場合は停止する(P4Bと同じ2回ルール)。"""
    attempts = []
    for attempt_number in range(1, MAX_CONTENT_REGENERATION_ATTEMPTS + 1):
        attempt = _generate_one_chunk_attempt(chunk, tts_call_fn, sleep_function)
        attempt["attempt_number"] = attempt_number
        attempts.append({k: v for k, v in attempt.items() if k != "samples"})
        if attempt["status"] == "OK" and attempt["content_check"]["passed"]:
            return {"status": "OK", "final_attempt": attempt, "attempts": attempts}
    return {"status": "STOPPED", "reason": f"chunk{chunk['chunk_id']}の内容確認が{MAX_CONTENT_REGENERATION_ATTEMPTS}回連続で失敗しました", "attempts": attempts}


def _step_generate_all_chunks(chunk_plan: list, tts_call_fn, sleep_function) -> dict:
    results = {}
    for chunk in chunk_plan:
        r = generate_chunk_with_content_gate(chunk, tts_call_fn, sleep_function)
        results[chunk["chunk_id"]] = r
        if r["status"] != "OK":
            return {"status": "STOPPED", "phase": "chunk_generation", "chunk_id": chunk["chunk_id"], "reason": r["reason"], "results": results}
    return {"status": "OK", "results": results}


# ============================================================
# Step 3: marker chunkごとのMFA alignment(「目印」の区間特定)
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
    marker_specs = [{"marker_id": f"chunk{chunk['chunk_id']}_目印", "token_sequence": p4c.MARKER_TOKEN_SEQUENCE}]
    spans, errors = p4.find_all_marker_spans(words, marker_specs)

    if errors or spans[0] is None:
        return {"status": "STOPPED", "reason": f"chunk{chunk['chunk_id']}: 「目印」区間を特定できませんでした: {errors}", "textgrid_path": dest_textgrid}

    span = spans[0]
    if not (span["start_seconds"] < span["end_seconds"]):
        return {"status": "STOPPED", "reason": f"chunk{chunk['chunk_id']}: 「目印」区間のstart>=endです", "span": span}

    return {"status": "OK", "textgrid_path": dest_textgrid, "span": span, "align_result": align_result}


def _step_mfa_align_all_marker_chunks(chunk_plan: list, chunk_results: dict) -> dict:
    results = {}
    for chunk in chunk_plan:
        if chunk["chunk_type"] != "marker":
            continue
        ja_wav_path = chunk_results[chunk["chunk_id"]]["final_attempt"]["wav_path"]
        r = _step_mfa_align_chunk(chunk, ja_wav_path)
        results[chunk["chunk_id"]] = r
        if r["status"] != "OK":
            return {"status": "STOPPED", "phase": "mfa_alignment", "chunk_id": chunk["chunk_id"], "reason": r["reason"], "results": results}
    # 各marker chunkは別々の音声file(別々のtimeline)としてMFAを実行して
    # いるため、chunk間でのstart/end秒の単調性比較は意味を持たない
    # (P4Bと同じ設計。単調性チェックはchunk単体内のstart<endのみ、
    # _step_mfa_align_chunk側で確認済み)。
    return {"status": "OK", "results": results}


# ============================================================
# Step 4: 英語Key Phrase生成(shot on targetは既存流用、他4件は新規生成)
# ============================================================
def _step_generate_key_phrases(chunk_plan: list, tts_call_fn, sleep_function) -> dict:
    results = {}
    for chunk in chunk_plan:
        if chunk["chunk_type"] != "marker":
            continue
        used_form = chunk["used_form"]
        out_path = f"{OUT_DIR}/preview/en_components/{chunk['chunk_id']}_{chunk['canonical_english'].replace(' ', '_')}.wav"

        if used_form == "shot on target":
            if not os.path.exists(p4c.EXISTING_SHOT_ON_TARGET_PATH):
                return {"status": "STOPPED", "reason": f"既存音声が見つかりません: {p4c.EXISTING_SHOT_ON_TARGET_PATH}"}
            shutil.copyfile(p4c.EXISTING_SHOT_ON_TARGET_PATH, out_path)
            samples, sr, ch, _ = common.read_wav_float(out_path)
            results[chunk["chunk_id"]] = {
                "used_form": used_form, "path": out_path, "reused": True,
                "source_path": p4c.EXISTING_SHOT_ON_TARGET_PATH, "sha256": _sha256_file(out_path),
                "call_count": 0, "retry_count": 0, "samples": samples, "sample_rate": sr,
                "duration_seconds": round(len(samples) / sr, 4),
            }
            continue

        prompt = p4c.build_tts_prompt(used_form, p4c.ENGLISH_STYLE_PREFIX)
        pcm, retries, ok, err = common._call_tts_with_retry(
            tts_call_fn, prompt, max_retry=p4c.MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
        if not ok:
            return {"status": "STOPPED", "reason": f"英語Key Phrase({used_form!r})のTTSが失敗: {err}"}

        samples_raw = common.pcm_bytes_to_float_mono(pcm)
        trimmed, trim_info = p3u.trim_english_keyword_silence(samples_raw, common.SAMPLE_RATE)
        if trimmed is None:
            return {"status": "STOPPED", "reason": f"英語Key Phrase({used_form!r})に発話区間を検出できませんでした"}

        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        results[chunk["chunk_id"]] = {
            "used_form": used_form, "path": out_path, "reused": False,
            "call_count": 1 + retries, "retry_count": retries, "sha256": _sha256_file(out_path),
            "trim_info": trim_info, "samples": trimmed, "sample_rate": common.SAMPLE_RATE,
            "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
        }

    return {"status": "OK", "key_phrases": results}


# ============================================================
# Step 5: marker chunkごとの置換(「目印」区間→英語Component)
# ============================================================
def _replace_marker_in_chunk(chunk: dict, ja_samples: "np.ndarray", sr: int, span: dict, en_samples: "np.ndarray") -> dict:
    marker_start_sample = int(round(span["start_seconds"] * sr))
    marker_end_sample = int(round(span["end_seconds"] * sr))
    before = ja_samples[:marker_start_sample].copy()
    after = ja_samples[marker_end_sample:].copy()

    needed_trailing = round(p4c.GAP_BEFORE_TARGET_SECONDS - p4c.EN_TRIM_SAFETY_MARGIN_SECONDS, 4)
    needed_leading = round(p4c.GAP_AFTER_TARGET_SECONDS - p4c.EN_TRIM_SAFETY_MARGIN_SECONDS, 4)

    before_bounds = p3u.find_speech_bounds(before, sr)
    after_bounds = p3u.find_speech_bounds(after, sr)
    if before_bounds is None or after_bounds is None:
        return {"status": "STOPPED", "reason": f"chunk{chunk['chunk_id']}: マーカー前後の発話区間を検出できませんでした"}

    before_adjusted, trail_info = p3z.adjust_trailing_silence(before, sr, before_bounds[1], needed_trailing)
    after_adjusted, lead_info = p3z.adjust_leading_silence(after, sr, after_bounds[0], needed_leading)

    joined = np.concatenate([before_adjusted, en_samples, after_adjusted])

    before_adj_bounds = p3u.find_speech_bounds(before_adjusted, sr)
    en_bounds = p3u.find_speech_bounds(en_samples, sr)
    after_adj_bounds = p3u.find_speech_bounds(after_adjusted, sr)

    cursor_after_before = len(before_adjusted)
    en_speech_start_in_joined = cursor_after_before + en_bounds[0]
    en_speech_end_in_joined = cursor_after_before + en_bounds[1]
    cursor_after_en = cursor_after_before + len(en_samples)
    after_speech_start_in_joined = cursor_after_en + after_adj_bounds[0]

    ja_before_speech_end_in_joined = before_adj_bounds[1]
    gap_before = (en_speech_start_in_joined - ja_before_speech_end_in_joined) / sr
    gap_after = (after_speech_start_in_joined - en_speech_end_in_joined) / sr

    return {
        "status": "OK", "joined": joined, "sample_rate": sr,
        "trailing_adjustment": trail_info, "leading_adjustment": lead_info,
        "measured_gap_before_seconds": round(gap_before, 4),
        "measured_gap_after_seconds": round(gap_after, 4),
        "within_tolerance_before": abs(gap_before - p4c.GAP_BEFORE_TARGET_SECONDS) <= p4c.GAP_TOLERANCE_SECONDS,
        "within_tolerance_after": abs(gap_after - p4c.GAP_AFTER_TARGET_SECONDS) <= p4c.GAP_TOLERANCE_SECONDS,
    }


def _step_replace_all_marker_chunks(chunk_plan: list, chunk_results: dict, mfa_results: dict, key_phrase_results: dict) -> dict:
    final_chunks = {}
    replacement_reports = {}
    for chunk in chunk_plan:
        cid = chunk["chunk_id"]
        if chunk["chunk_type"] != "marker":
            ja_samples = chunk_results[cid]["final_attempt"]["samples"]
            final_chunks[cid] = ja_samples
            continue

        ja_samples = chunk_results[cid]["final_attempt"]["samples"]
        sr = chunk_results[cid]["final_attempt"]["sample_rate"]
        span = mfa_results[cid]["span"]
        en_samples = key_phrase_results[cid]["samples"]

        r = _replace_marker_in_chunk(chunk, ja_samples, sr, span, en_samples)
        if r["status"] != "OK":
            return {"status": "STOPPED", "phase": "marker_replacement", "chunk_id": cid, "reason": r["reason"]}

        replaced_path = f"{OUT_DIR}/preview/replaced_chunks/chunk{cid}_replaced.wav"
        common.write_wav_float(replaced_path, r["joined"], r["sample_rate"], 1)
        r["replaced_path"] = replaced_path
        replacement_reports[cid] = {k: v for k, v in r.items() if k != "joined"}
        final_chunks[cid] = r["joined"]

    return {"status": "OK", "final_chunks": final_chunks, "replacement_reports": replacement_reports}


# ============================================================
# Step 6: 6chunkを追加無音なしで結合し、chunk間の実測無音を測定
# ============================================================
def _step_concatenate_chunks(chunk_plan: list, final_chunks: dict, sr: int) -> dict:
    ordered = [final_chunks[c["chunk_id"]] for c in chunk_plan]
    joined = np.concatenate(ordered)

    boundary_gaps = []
    for i in range(len(ordered) - 1):
        bounds_i = p3u.find_speech_bounds(ordered[i], sr)
        bounds_next = p3u.find_speech_bounds(ordered[i + 1], sr)
        trailing_silence = (len(ordered[i]) - bounds_i[1]) / sr
        leading_silence = bounds_next[0] / sr
        gap = trailing_silence + leading_silence
        boundary_gaps.append({
            "between_chunk": f"{chunk_plan[i]['chunk_id']}->{chunk_plan[i + 1]['chunk_id']}",
            "measured_gap_seconds": round(gap, 4),
            "exceeds_threshold": gap > INTER_CHUNK_GAP_STOP_THRESHOLD_SECONDS,
        })

    any_exceeds = any(b["exceeds_threshold"] for b in boundary_gaps)
    if any_exceeds:
        return {"status": "STOPPED", "reason": "chunk間の無音が1.0秒を超えました", "boundary_gaps": boundary_gaps}

    return {"status": "OK", "joined": joined, "sample_rate": sr, "boundary_gaps": boundary_gaps}


# ============================================================
# 実行本体
# ============================================================
def run(tts_call_fn=None, sleep_function=sleep_fn) -> dict:
    _mkdirs()
    call_fn = tts_call_fn or gclient.make_tts_call_fn(p4c.VOICE_NAME)

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

    kp = _step_generate_key_phrases(chunk_plan, call_fn, sleep_function)
    if kp["status"] != "OK":
        return {**kp, "plan_step": plan_step, "gen": gen, "mfa": mfa}

    replace = _step_replace_all_marker_chunks(chunk_plan, gen["results"], mfa["results"], kp["key_phrases"])
    if replace["status"] != "OK":
        return {**replace, "plan_step": plan_step, "gen": gen, "mfa": mfa, "kp": kp}

    sr = common.SAMPLE_RATE
    concat = _step_concatenate_chunks(chunk_plan, replace["final_chunks"], sr)
    if concat["status"] != "OK":
        return {**concat, "plan_step": plan_step, "gen": gen, "mfa": mfa, "kp": kp, "replace": replace}

    preview_raw_path = f"{OUT_DIR}/preview/final/A01_b1_listening_preview_raw.wav"
    common.write_wav_float(preview_raw_path, concat["joined"], sr, 1)

    dynamics_result = common.apply_dynamics3_once(concat["joined"], sr)
    preview_dynamics3_path = f"{OUT_DIR}/preview/final/A01_b1_listening_preview_dynamics3.wav"
    common.write_wav_float(preview_dynamics3_path, dynamics_result.c1_samples, sr, 1)

    return {
        "status": "OK",
        "plan_step": plan_step,
        "gen": gen,
        "mfa": mfa,
        "kp": kp,
        "replace": replace,
        "concat": concat,
        "preview_raw_path": preview_raw_path,
        "preview_dynamics3_path": preview_dynamics3_path,
        "dynamics3_metrics_c0": dynamics_result.metrics_c0,
        "dynamics3_metrics_c1": dynamics_result.metrics_c1,
        "dynamics3_loudness_matching": dynamics_result.loudness_matching,
    }


if __name__ == "__main__":
    result = run()
    print(f"status={result['status']}")
    if result["status"] != "OK":
        print(result.get("phase"), result.get("reason"))
    else:
        for cid, r in result["replace"]["replacement_reports"].items():
            print(cid, r["measured_gap_before_seconds"], r["measured_gap_after_seconds"],
                  r["within_tolerance_before"], r["within_tolerance_after"])
        for b in result["concat"]["boundary_gaps"]:
            print(b["between_chunk"], b["measured_gap_seconds"])
        print("preview_raw_path:", result["preview_raw_path"])
        print("preview_dynamics3_path:", result["preview_dynamics3_path"])
