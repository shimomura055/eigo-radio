# ============================================================
# er003_b1_p7c_audio.py
# ER-003-B1-P7C: Gemini 3.1 Preview英語Component差し替え検証
# ============================================================
# P7Aでユーザーが合格と判断した日本語marker入りraw音声
# (er003_output/b1_p7a/A01/raw/A01_p7a_gemini31_single_call.wav)を固定し、
# 5箇所の「目印」を承認済み英語used formへ差し替える。日本語TTSは新たに
# 呼び出さない。
#
# 用途別モデル隔離(指示section3): Previewは3.1(P7Aで既に使用済み、本
# モジュールは日本語TTSを再呼び出ししない)。英語Componentの生成は、
# 既に採用済みの方式(er002_gemini_client.make_tts_call_fn経由、
# er002_common.MODEL_NAME="gemini-2.5-pro-preview-tts")をそのまま使う
# (指示section8「既に採用済みの英語Component生成方式を使用」に従う)。
# er002_common.py/er002_gemini_client.pyは変更しない。
#
# 境界決定はMFA区間のみを根拠にする(RMSは英語Component自身の内部無音
# トリムにのみ使用し、日本語marker隣接tokenの判定には使わない、指示
# section7の明記通り)。
#
# 再利用するもの(再実装しない):
#   - er002_common.SAMPLE_RATE/pcm_bytes_to_float_mono/read_wav_float/
#     write_wav_float/measure_metrics/apply_dynamics3_once/
#     _call_tts_with_retry/MODEL_NAME
#   - er002_gemini_client.make_tts_call_fn/make_client
#   - er003_b1_p3w_audio.run_mfa_align/parse_textgrid_words_tier/MFA_*
#   - er003_b1_p3u_audio.find_speech_bounds/trim_english_keyword_silence
#   - er003_b1_p3z_audio.adjust_trailing_silence/adjust_leading_silence
#   - er003_b1_p4_audio.find_all_marker_spans/spans_are_monotonic_non_overlapping
#   - er003_b1_p4c_audio.MARKER_TOKEN/MARKER_TOKEN_SEQUENCE/VOICE_NAME/
#     ENGLISH_STYLE_PREFIX/MAX_TTS_TECHNICAL_RETRY/build_tts_prompt
#   - er003_b1_p6a_audio.GAP_BEFORE_TARGET_SECONDS/GAP_AFTER_TARGET_SECONDS/
#     GAP_TOLERANCE_SECONDS/KANJI_TARGET_PHRASES
#   - er003_b1_p6b_audio.mfa_anchor_sample/verify_spans_no_overlap_with_adjacent_tokens
#   - er003_b1_p7a_audio.CANDIDATE_MODEL_NAME/BASELINE_MODEL_NAME/sha256_file/sha256_text

from __future__ import annotations

import hashlib
import os
import shutil

import numpy as np

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p3u_audio as p3u
import er003_b1_p3w_audio as p3w
import er003_b1_p3z_audio as p3z
import er003_b1_p4_audio as p4
import er003_b1_p4c_audio as p4c
import er003_b1_p6a_audio as p6a
import er003_b1_p6b_audio as p6b
import er003_b1_p7a_audio as p7a

ARTICLE_ID = "A01"

INPUT_WAV_PATH = "er003_output/b1_p7a/A01/raw/A01_p7a_gemini31_single_call.wav"
INPUT_EXPECTED_SHA256 = "30162196543087ce2a0a5e15e1f0e12b8caf65f57f51345128e2a06beab1d22b"

USED_FORMS_IN_ORDER = (
    "shot on target",
    "take players off",
    "a narrow lead",
    "close the door to the final",
    "stoppage time",
)

MARKER_TOKEN = p4c.MARKER_TOKEN  # "目印"
MARKER_TOKEN_SEQUENCE = p4c.MARKER_TOKEN_SEQUENCE  # ("目印",)
EXPECTED_MARKER_COUNT = 5

GAP_BEFORE_TARGET_SECONDS = p6a.GAP_BEFORE_TARGET_SECONDS  # 0.40
GAP_AFTER_TARGET_SECONDS = p6a.GAP_AFTER_TARGET_SECONDS  # 0.30
GAP_TOLERANCE_SECONDS = p6a.GAP_TOLERANCE_SECONDS  # 0.03
KANJI_TARGET_PHRASES = p6a.KANJI_TARGET_PHRASES

# 英語Componentは「既に採用済みの生成方式」(P4C)をそのまま使う。
VOICE_NAME = p4c.VOICE_NAME  # "Aoede"
ENGLISH_STYLE_PREFIX = p4c.ENGLISH_STYLE_PREFIX
MAX_TTS_TECHNICAL_RETRY = p4c.MAX_TTS_TECHNICAL_RETRY
build_tts_prompt = p4c.build_tts_prompt

# ------------------------------------------------------------
# 既存英語Componentの由来(指示section8で確認済み。04のみP4Cで
# 「不自然に分断された」とユーザーから明示された既知の不採用品のため
# 再利用しない → 不足として新規生成する)。
# ------------------------------------------------------------
EXISTING_COMPONENT_PATHS = {
    "shot on target": "er003_output/b1_p3u/A01/components/en_shot_on_target_trimmed.wav",
    "take players off": "er003_output/b1_p4c/A01/preview/en_components/02_take_a_player_off.wav",
    "a narrow lead": "er003_output/b1_p4c/A01/preview/en_components/03_narrow_lead.wav",
    "stoppage time": "er003_output/b1_p4c/A01/preview/en_components/05_stoppage_time.wav",
}
REJECTED_COMPONENT_PATHS = {
    "close the door to the final": "er003_output/b1_p4c/A01/preview/en_components/04_close_the_door_to.wav",
}
MISSING_USED_FORMS = ("close the door to the final",)


def sha256_file(path: str) -> str:
    return p7a.sha256_file(path)


def verify_input_wav_unchanged(path: str = INPUT_WAV_PATH, expected_sha256: str = INPUT_EXPECTED_SHA256) -> dict:
    actual = sha256_file(path)
    return {"path": path, "expected_sha256": expected_sha256, "actual_sha256": actual, "matches": actual == expected_sha256}


# ============================================================
# MFAアラインメント(P7A raw全体、5箇所の「目印」)
# ============================================================
def run_mfa_on_full_audio(wav_path: str, tts_text: str, work_dir: str) -> dict:
    corpus_dir = f"{work_dir}/_mfa_corpus"
    output_dir = f"{work_dir}/_mfa_output"
    os.makedirs(corpus_dir, exist_ok=True)
    stem = "A01_p7a_full"
    shutil.copyfile(wav_path, f"{corpus_dir}/{stem}.wav")
    with open(f"{corpus_dir}/{stem}.lab", "w", encoding="utf-8") as f:
        f.write(tts_text)

    align_result = p3w.run_mfa_align(corpus_dir, output_dir)
    if not align_result["success"]:
        return {"status": "STOPPED", "reason": "MFA alignmentが失敗しました", "align_result": align_result}

    textgrid_path = f"{output_dir}/{stem}.TextGrid"
    if not os.path.exists(textgrid_path):
        return {"status": "STOPPED", "reason": f"TextGridが生成されませんでした: {textgrid_path}"}

    dest_textgrid = f"{work_dir}/{stem}.TextGrid"
    shutil.copyfile(textgrid_path, dest_textgrid)
    shutil.rmtree(output_dir, ignore_errors=True)
    shutil.rmtree(corpus_dir, ignore_errors=True)

    words = p3w.parse_textgrid_words_tier(dest_textgrid)
    return {"status": "OK", "textgrid_path": dest_textgrid, "words": words, "align_result": align_result}


def find_five_marker_spans(words: list[dict]) -> dict:
    marker_specs = [{"marker_id": f"marker_{i + 1}", "token_sequence": MARKER_TOKEN_SEQUENCE} for i in range(EXPECTED_MARKER_COUNT)]
    spans, errors = p4.find_all_marker_spans(words, marker_specs)

    if errors or any(s is None for s in spans):
        return {"status": "STOPPED", "reason": f"5件のmarker区間を特定できませんでした: {errors}", "spans": spans, "errors": errors}
    if len(spans) != EXPECTED_MARKER_COUNT:
        return {"status": "STOPPED", "reason": f"marker数が{len(spans)}件(期待{EXPECTED_MARKER_COUNT}件)", "spans": spans}
    if not p4.spans_are_monotonic_non_overlapping(spans):
        return {"status": "STOPPED", "reason": "marker区間が単調増加・非重複ではありません", "spans": spans}

    overlap_check = p6b.verify_spans_no_overlap_with_adjacent_tokens(spans)
    if not overlap_check["all_passed"]:
        return {"status": "STOPPED", "reason": "marker区間が隣接日本語tokenと重なっています", "spans": spans, "overlap_check": overlap_check}

    return {"status": "OK", "spans": spans, "overlap_check": overlap_check}


# ============================================================
# 英語Component: 由来確認・不足分の新規生成
# ============================================================
def collect_existing_component_provenance() -> dict:
    provenance = {}
    for used_form, path in EXISTING_COMPONENT_PATHS.items():
        exists = os.path.exists(path)
        entry = {"used_form": used_form, "path": path, "exists": exists, "status": "reused_existing"}
        if exists:
            samples, sr, ch, _ = common.read_wav_float(path)
            metrics = common.measure_metrics(samples, sr)
            entry.update({
                "sha256": sha256_file(path), "duration_seconds": round(len(samples) / sr, 4),
                "sample_rate": sr, "channels": ch, "clipping_detected": metrics["clipping_detected"],
            })
        provenance[used_form] = entry
    for used_form, path in REJECTED_COMPONENT_PATHS.items():
        provenance[used_form] = {
            "used_form": used_form, "path": path, "status": "excluded_rejected_by_user",
            "reason": "P4Cで不自然に分断されたComponentとしてユーザーから明示的に再利用禁止と指示された",
        }
    return provenance


def generate_missing_component(used_form: str, out_path: str, tts_call_fn=None, sleep_function=None) -> dict:
    call_fn = tts_call_fn or gclient.make_tts_call_fn(VOICE_NAME)
    prompt = build_tts_prompt(used_form, ENGLISH_STYLE_PREFIX)

    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not ok:
        return {"status": "STOPPED", "reason": f"英語Component({used_form!r})のTTSが失敗: {err}"}

    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(samples_raw, common.SAMPLE_RATE)
    if trimmed is None:
        return {"status": "STOPPED", "reason": f"英語Component({used_form!r})に発話区間を検出できませんでした"}

    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
    return {
        "status": "OK", "used_form": used_form, "path": out_path, "model": common.MODEL_NAME, "voice": VOICE_NAME,
        "call_count": 1 + retries, "retry_count": retries, "sha256": sha256_file(out_path),
        "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4), "trim_info": trim_info,
        "clipping_detected": metrics["clipping_detected"],
    }


def tight_speech_only(samples: "np.ndarray", sample_rate: int) -> "np.ndarray":
    """英語Componentの見かけ上の前後無音(保存時のsafety margin含む)を
    含めず、実際の可聴音区間だけを取り出す(指示section9: 見かけ上の
    配置時刻ではなく可聴音同士の間隔で仕様を満たすため)。"""
    bounds = p3u.find_speech_bounds(samples, sample_rate)
    if bounds is None:
        raise ValueError("英語Componentの発話区間を検出できません")
    start, end = bounds
    return samples[start:end]


# ============================================================
# marker除去+英語Component挿入(MFA境界のみ使用)
# ============================================================
def remove_markers_and_insert_components(
    ja_samples: "np.ndarray", sample_rate: int, spans: list[dict], component_samples: list["np.ndarray"],
) -> dict:
    """spansはfind_five_marker_spansで得たMFA由来の5区間(出現順)。
    component_samplesはtight_speech_only済みの5つの英語Component
    (出現順)。markerを除去する処理と、英語前後の無音を作る処理を分離し、
    無音確保のために日本語側の除去範囲を広げない(指示section7)。"""
    n = len(spans)
    assert len(component_samples) == n, "spansとcomponent_samplesの件数が一致しません"

    # Step 1: markerだけを除去し、6つの日本語segmentへ分割する。
    segments = []
    seg_start_sample = 0
    for span in spans:
        marker_start_sample = int(round(span["start_seconds"] * sample_rate))
        segments.append({"samples": ja_samples[seg_start_sample:marker_start_sample].copy(),
                          "abs_start_seconds": seg_start_sample / sample_rate})
        seg_start_sample = int(round(span["end_seconds"] * sample_rate))
    segments.append({"samples": ja_samples[seg_start_sample:].copy(),
                      "abs_start_seconds": seg_start_sample / sample_rate})

    # Step 2: 各segmentへ、MFA由来の隣接token境界を基準に前後無音を調整する。
    silence_adjustments = []
    for i, span in enumerate(spans):
        seg_before = segments[i]
        speech_end_sample = p6b.mfa_anchor_sample(span["preceding_end_seconds"], seg_before["abs_start_seconds"], sample_rate)
        adjusted, info = p3z.adjust_trailing_silence(seg_before["samples"], sample_rate, speech_end_sample, GAP_BEFORE_TARGET_SECONDS)
        seg_before["samples"] = adjusted
        silence_adjustments.append({"marker_id": span["marker_id"], "side": "trailing_before_english",
                                     "segment_index": i, "speech_end_sample": speech_end_sample, **info})

        seg_after = segments[i + 1]
        speech_start_sample = p6b.mfa_anchor_sample(span["following_start_seconds"], seg_after["abs_start_seconds"], sample_rate)
        adjusted, info = p3z.adjust_leading_silence(seg_after["samples"], sample_rate, speech_start_sample, GAP_AFTER_TARGET_SECONDS)
        seg_after["samples"] = adjusted
        silence_adjustments.append({"marker_id": span["marker_id"], "side": "leading_after_english",
                                     "segment_index": i + 1, "speech_start_sample": speech_start_sample, **info})

    # Step 3: segmentと英語Componentを順番に連結する。連結中に各
    # Componentの完成音声内での絶対サンプル位置を記録する(境界確認
    # clip抽出用。指示section11「保存する試聴成果物」)。
    pieces = [segments[0]["samples"]]
    cursor = len(segments[0]["samples"])
    component_positions = []
    for i in range(n):
        en_start = cursor
        pieces.append(component_samples[i])
        cursor += len(component_samples[i])
        en_end = cursor
        component_positions.append({
            "marker_id": spans[i]["marker_id"], "used_form": USED_FORMS_IN_ORDER[i],
            "assembled_start_sample": en_start, "assembled_end_sample": en_end,
        })
        pieces.append(segments[i + 1]["samples"])
        cursor += len(segments[i + 1]["samples"])
    assembled = np.concatenate(pieces).astype(ja_samples.dtype)

    return {
        "assembled": assembled, "segments": segments, "silence_adjustments": silence_adjustments,
        "component_positions": component_positions,
    }


def extract_boundary_clip(assembled: "np.ndarray", sample_rate: int, position: dict,
                           context_seconds: float = 1.2) -> "np.ndarray":
    """英語Component前後の日本語を含む短い試聴clipを、完成音声内の
    記録済み絶対サンプル位置から切り出す(指示section11: 英語直前の
    日本語・英語Component全体・英語直後の日本語を聞き取れる長さ)。"""
    context_samples = int(round(context_seconds * sample_rate))
    start = max(0, position["assembled_start_sample"] - context_samples)
    end = min(len(assembled), position["assembled_end_sample"] + context_samples)
    return assembled[start:end]


def measure_effective_gaps(spans: list[dict], silence_adjustments: list[dict],
                            component_durations_seconds: list[float]) -> list[dict]:
    """各markerについて、p3z.adjust_trailing_silence/adjust_leading_silence
    が実際に達成したachieved_*_secondsから、英語Component前後の実効
    間隔(可聴音同士、指示section9の定義通り)を報告する。英語Component
    自身はtight_speech_onlyで見かけ上の無音を除去済みのため、
    achieved値がそのまま可聴音間の実効間隔になる(RMSでの再検出は
    行わない。値はp3z側のサンプル数計算による厳密値)。"""
    by_marker = {}
    for adj in silence_adjustments:
        by_marker.setdefault(adj["marker_id"], {})[adj["side"]] = adj

    results = []
    for i, span in enumerate(spans):
        entry = by_marker[span["marker_id"]]
        before = entry["trailing_before_english"]
        after = entry["leading_after_english"]
        gap_before = before["achieved_trailing_seconds"]
        gap_after = after["achieved_leading_seconds"]
        results.append({
            "marker_id": span["marker_id"],
            "used_form": USED_FORMS_IN_ORDER[i],
            "gap_before_seconds": gap_before,
            "gap_after_seconds": gap_after,
            "component_duration_seconds": round(component_durations_seconds[i], 4),
            "within_tolerance_before": abs(gap_before - GAP_BEFORE_TARGET_SECONDS) <= GAP_TOLERANCE_SECONDS,
            "within_tolerance_after": abs(gap_after - GAP_AFTER_TARGET_SECONDS) <= GAP_TOLERANCE_SECONDS,
            "before_speech_content_unchanged": before["speech_content_unchanged"],
            "after_speech_content_unchanged": after["speech_content_unchanged"],
        })
    return results


# ============================================================
# 原稿忠実性QA(指示section12、置換後の日本語)
# ============================================================
# marker除去後に隣接して残っているべき日本語(指示section6の各期待構造
# +section12の確認リストを合わせたもの)。「守備を固める」への変化検出
# も含む(禁止形)。
JAPANESE_FIDELITY_PHRASES = (
    "激しい接触",
    "枠内シュート",
    "を記録",
    "選手を交代で下げる",
    "という決断で",
    "守備を固め",
    "を守ろう",
    "が現実",
    "へ。最後の数分",
    "何が起きるのでしょうか",
)
JAPANESE_FORBIDDEN_FORM = "守備を固める"  # 「守備を固め」への変化(section12)


def check_japanese_fidelity(text: str) -> dict:
    result = {phrase: (phrase in text) for phrase in JAPANESE_FIDELITY_PHRASES}
    result["forbidden_form_present"] = JAPANESE_FORBIDDEN_FORM in text
    result["marker_residue_count"] = text.count(MARKER_TOKEN)
    result["all_present"] = all(result[p] for p in JAPANESE_FIDELITY_PHRASES)
    result["ok"] = result["all_present"] and not result["forbidden_form_present"] and result["marker_residue_count"] == 0
    return result


def check_english_used_forms(text: str) -> dict:
    lowered = text.lower()
    result = {}
    for form in USED_FORMS_IN_ORDER:
        count = lowered.count(form.lower())
        result[form] = {"present": count >= 1, "count": count}
    result["all_present_at_least_once"] = all(v["present"] for v in result.values() if isinstance(v, dict))
    return result


# ============================================================
# 用途別モデル隔離の確認(指示section3)
# ============================================================
def check_model_isolation() -> dict:
    """Preview(本モジュールが英語Component新規生成に使うTTS呼び出し経路
    を含め、日本語Preview自体はP7Aで既に3.1を使用済み)と、本文
    (er002_common.MODEL_NAME)が別モデルのまま分離されていることを、
    実際にimport済みのモジュール状態から確認する。er002_common.py/
    er002_gemini_client.pyは本ステージで一切変更していない。"""
    return {
        "preview_model_used_in_p7a": p7a.CANDIDATE_MODEL_NAME,
        "article_body_model_common_module": common.MODEL_NAME,
        "isolated": p7a.CANDIDATE_MODEL_NAME != common.MODEL_NAME,
        "article_body_model_is_frozen_spec": common.MODEL_NAME == "gemini-2.5-pro-preview-tts",
        "english_component_generation_uses_common_model_name": True,
    }
