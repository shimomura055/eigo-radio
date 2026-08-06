# ============================================================
# er003_v1_b1_p7c_generate.py
# ER-003-B1-P7C: Gemini 3.1 Preview英語Component差し替え検証
# ============================================================
# P7Aで合格した日本語marker入りraw音声を固定し、5箇所の「目印」を
# 承認済み英語used formへ差し替えて完成版候補を生成する。日本語TTSは
# 新たに呼び出さない。不足している英語Component(close the door to the
# final)のみ、既に採用済みの方式で1回だけ新規生成する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p7c_generate.py

from __future__ import annotations

import json
import os

import er002_common as common
import er003_b1_p4_audio as p4
import er003_b1_p7c_audio as p7c

OUT_DIR = "er003_output/b1_p7c/A01"
INPUT_TEXT_PATH = "er003_output/b1_p7a/A01/source/input_text.txt"


def _mkdirs() -> None:
    for sub in ("source", "mfa", "components", "assembled", "asr", "audit", "clips"):
        os.makedirs(f"{OUT_DIR}/{sub}", exist_ok=True)


def step1_verify_input() -> dict:
    check = p7c.verify_input_wav_unchanged()
    samples, sr, ch, nframes = common.read_wav_float(p7c.INPUT_WAV_PATH)
    with open(INPUT_TEXT_PATH, encoding="utf-8") as f:
        tts_text = f.read()
    info = {
        **check, "sample_rate": sr, "channels": ch, "nframes": nframes,
        "duration_seconds": round(nframes / sr, 4),
        "tts_text_path": INPUT_TEXT_PATH, "tts_text_sha256": p7c.p7a.sha256_text(tts_text),
        "p7a_model": p7c.p7a.CANDIDATE_MODEL_NAME, "p7a_voice": p7c.p7a.VOICE_NAME,
        "p7a_call_count": 1,
    }
    with open(f"{OUT_DIR}/audit/input_fixed_metadata.json", "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    return {**info, "samples": samples, "tts_text": tts_text}


def step2_mfa_align(samples, sr, tts_text: str) -> dict:
    mfa_result = p7c.run_mfa_on_full_audio(p7c.INPUT_WAV_PATH, tts_text, f"{OUT_DIR}/mfa")
    if mfa_result["status"] != "OK":
        return mfa_result
    span_result = p7c.find_five_marker_spans(mfa_result["words"])
    with open(f"{OUT_DIR}/mfa/marker_spans.json", "w", encoding="utf-8") as f:
        json.dump({"status": span_result["status"],
                    "spans": span_result.get("spans"),
                    "overlap_check": span_result.get("overlap_check")}, f, ensure_ascii=False, indent=2, default=str)
    if span_result["status"] != "OK":
        return span_result
    return {"status": "OK", "mfa_result": mfa_result, "spans": span_result["spans"], "overlap_check": span_result["overlap_check"]}


def step3_components(tts_call_fn=None, sleep_function=None) -> dict:
    provenance = p7c.collect_existing_component_provenance()

    for missing_form in p7c.MISSING_USED_FORMS:
        out_path = f"{OUT_DIR}/components/new_{missing_form.replace(' ', '_')}.wav"
        if os.path.exists(out_path):
            # 指示section7「2回目以降の候補生成」を避けるため、この
            # P7Cステージ内で既に生成済みの不足Componentがあれば再生成
            # しない(1回の成功結果を確定候補として扱い続ける)。
            samples, sr, ch, _ = common.read_wav_float(out_path)
            metrics = common.measure_metrics(samples, sr)
            provenance[missing_form] = {
                "status": "generated_new_reused_from_this_stage", "used_form": missing_form, "path": out_path,
                "model": common.MODEL_NAME, "voice": p7c.VOICE_NAME,
                "sha256": p7c.sha256_file(out_path), "duration_seconds": round(len(samples) / sr, 4),
                "clipping_detected": metrics["clipping_detected"],
            }
            continue
        gen = p7c.generate_missing_component(missing_form, out_path, tts_call_fn=tts_call_fn, sleep_function=sleep_function)
        if gen["status"] != "OK":
            return {"status": "STOPPED", "reason": gen["reason"], "provenance": provenance}
        provenance[missing_form] = {**gen, "status": "generated_new"}

    with open(f"{OUT_DIR}/audit/component_provenance.json", "w", encoding="utf-8") as f:
        json.dump(provenance, f, ensure_ascii=False, indent=2)

    ordered_samples = []
    ordered_durations = []
    for used_form in p7c.USED_FORMS_IN_ORDER:
        entry = provenance[used_form]
        path = entry["path"]
        samples, sr, ch, _ = common.read_wav_float(path)
        tight = p7c.tight_speech_only(samples, sr)
        ordered_samples.append(tight)
        ordered_durations.append(len(tight) / sr)

    return {"status": "OK", "provenance": provenance, "ordered_samples": ordered_samples, "ordered_durations": ordered_durations}


def step4_splice(ja_samples, sr, spans, ordered_samples, ordered_durations) -> dict:
    result = p7c.remove_markers_and_insert_components(ja_samples, sr, spans, ordered_samples)
    gaps = p7c.measure_effective_gaps(spans, result["silence_adjustments"], ordered_durations)

    with open(f"{OUT_DIR}/audit/silence_adjustments.json", "w", encoding="utf-8") as f:
        json.dump(result["silence_adjustments"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/effective_gaps.json", "w", encoding="utf-8") as f:
        json.dump(gaps, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/component_positions.json", "w", encoding="utf-8") as f:
        json.dump(result["component_positions"], f, ensure_ascii=False, indent=2)

    pre_dynamics3_path = f"{OUT_DIR}/assembled/A01_p7c_pre_dynamics3.wav"
    common.write_wav_float(pre_dynamics3_path, result["assembled"], sr, 1)

    return {"status": "OK", "assembled": result["assembled"], "component_positions": result["component_positions"],
            "gaps": gaps, "pre_dynamics3_path": pre_dynamics3_path}


def step5_dynamics3_and_clips(assembled, sr, component_positions) -> dict:
    dyn_result = common.apply_dynamics3_once(assembled, sr)
    final_path = f"{OUT_DIR}/A01_p7c_gemini31_english_replaced_dynamics3.wav"
    common.write_wav_float(final_path, dyn_result.c1_samples, sr, 1)
    metrics = common.measure_metrics(dyn_result.c1_samples, sr)

    clip_paths = []
    for pos in component_positions:
        clip = p7c.extract_boundary_clip(assembled, sr, pos)
        clip_name = f"{OUT_DIR}/clips/{pos['marker_id']}_{pos['used_form'].replace(' ', '_')}.wav"
        common.write_wav_float(clip_name, clip, sr, 1)
        clip_paths.append({"marker_id": pos["marker_id"], "used_form": pos["used_form"], "path": clip_name,
                            "duration_seconds": round(len(clip) / sr, 4)})

    return {"status": "OK", "final_path": final_path, "clipping_detected": metrics["clipping_detected"],
            "duration_seconds": metrics["duration_seconds"], "clip_paths": clip_paths}


def step6_asr_and_qa(final_path: str) -> dict:
    recognized, err = p4.get_full_text_via_azure_stt_continuous(final_path, language="ja-JP")
    if recognized is None:
        return {"status": "ERROR", "reason": err}
    with open(f"{OUT_DIR}/asr/asr_transcript.txt", "w", encoding="utf-8") as f:
        f.write(recognized)

    ja_fidelity = p7c.check_japanese_fidelity(recognized)
    en_check = p7c.check_english_used_forms(recognized)
    with open(f"{OUT_DIR}/asr/japanese_fidelity.json", "w", encoding="utf-8") as f:
        json.dump(ja_fidelity, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/asr/english_used_forms.json", "w", encoding="utf-8") as f:
        json.dump(en_check, f, ensure_ascii=False, indent=2)

    return {"status": "OK", "recognized_text": recognized, "japanese_fidelity": ja_fidelity, "english_check": en_check}


def run(tts_call_fn=None, sleep_function=None) -> dict:
    _mkdirs()

    inp = step1_verify_input()
    if not inp["matches"]:
        return {"status": "STOPPED", "phase": "input_verification", "reason": "P7A rawのsha256が一致しません", "inp": inp}

    align = step2_mfa_align(inp["samples"], inp["sample_rate"], inp["tts_text"])
    if align["status"] != "OK":
        return {"status": "STOPPED", "phase": "mfa_alignment", "reason": align.get("reason"), "align": align}

    comp = step3_components(tts_call_fn=tts_call_fn, sleep_function=sleep_function)
    if comp["status"] != "OK":
        return {"status": "STOPPED", "phase": "component_provenance", "reason": comp.get("reason"), "comp": comp}

    splice = step4_splice(inp["samples"], inp["sample_rate"], align["spans"], comp["ordered_samples"], comp["ordered_durations"])
    dyn = step5_dynamics3_and_clips(splice["assembled"], inp["sample_rate"], splice["component_positions"])
    asr = step6_asr_and_qa(dyn["final_path"])

    return {"status": "OK", "inp": inp, "align": align, "comp": comp, "splice": splice, "dyn": dyn, "asr": asr}


if __name__ == "__main__":
    result = run()
    print("status:", result["status"])
    if result["status"] != "OK":
        print(result.get("phase"), result.get("reason"))
    else:
        print("final_path:", result["dyn"]["final_path"])
        print("duration_seconds:", result["dyn"]["duration_seconds"])
        print("clipping_detected:", result["dyn"]["clipping_detected"])
        print("gaps:", result["splice"]["gaps"])
        print("japanese_fidelity_ok:", result["asr"]["japanese_fidelity"]["ok"])
        print("english_all_present:", result["asr"]["english_check"]["all_present_at_least_once"])
