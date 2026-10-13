# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02: Coffee Full Story(N01、Production runner生成)の速度・ポーズ実測(API呼出なし、local faster-whisper small)。
既存測定手順を踏襲: WPM = measure_wpm_01.py(count_primary/frame_rms_db/find_pauses)、文末無音 = er057_coffee_v5_pause_01_measure.py
(silent_runs[-40dBFS,50ms]+ASR語タイムスタンプ+reference文末のdifflib整列)。新しいGateは作らない(Trial参照値は参考値として併記)。
usage: PYTHONUTF8=1 .venv/Scripts/python.exe er071_coffee_m2p0_n01_measure_01.py <out_dir> <evidence_dir>
出力: <evidence_dir>/speed_pause_02.json(words/キャッシュは<evidence_dir>/words、commit対象外)"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

ROOT = os.getcwd()
sys.path.insert(0, ROOT)
import er057_coffee_v5_pause_01_measure as PM  # noqa: E402  (既存測定関数の再利用。import時にmain実行はしない)

_spec = importlib.util.spec_from_file_location(
    "mw", f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01/wpm_measurement_01/measure_wpm_01.py")
mw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mw)

# Trial参照値(参考。Productionの自動化された速度・ポーズ基準ではない。EVIDENCE_PLAN/委任文 Opus必須8)
TRIAL_REF = {"std_wpm_post_slowdown": [157, 6], "adv_wpm": [167, 6], "sentence_end_mean_ms_max": {"std": 498, "adv": 593},
             "long_silence_ge_800ms_max": 1}
_model = None


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def words_of2(path, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    cache = os.path.join(cache_dir, hashlib.sha1(path.encode()).hexdigest()[:10] + ".json")
    if os.path.exists(cache) and json.load(open(cache))["sha"] == sha(path):
        return json.load(open(cache))["words"]
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = _model.transcribe(path, language="en", word_timestamps=True, beam_size=5, condition_on_previous_text=False)
    w = [{"w": a.word.strip(), "s": a.start, "e": a.end} for s in segs for a in s.words]
    json.dump({"path": path, "sha": sha(path), "words": w}, open(cache, "w"))
    return w


def analyze_part(path, job, text, cache_dir):
    PM.REF[job] = {"text": text}
    x, sr = sf.read(path, dtype="float32")
    if x.ndim > 1:
        x = x.mean(axis=1)
    runs, dur = PM.silent_runs(x, sr, PM.THR_DB)
    w = words_of2(path, cache_dir)
    ends, n_ref, ratio = PM.ref_end_to_asr(job, w)
    ends = [i for i in ends if i is not None]
    pauses, used = [], set()
    for i in ends:
        lo, hi = w[i]["e"] - 0.25, w[i + 1]["s"] + 0.25
        best, bo = None, 0
        for k, (a, b) in enumerate(runs):
            ov = min(b, hi) - max(a, lo)
            if ov > bo:
                best, bo = k, ov
        if best is not None:
            used.add(best)
        pauses.append({"after": w[i]["w"], "pause_ms": round((runs[best][1] - runs[best][0]) * 1000) if best is not None else 0})
    other = [round((b - a) * 1000) for k, (a, b) in enumerate(runs) if k not in used and a > 0.005 and b < dur - 0.011]
    db = mw.frame_rms_db(x.astype("float64"), sr)
    long_sil = [q for q in mw.find_pauses(db, 800, dur)]
    words = mw.count_primary(text)
    ps = mw.find_pauses(db, 500, dur)
    speech = dur - sum(q["dur"] for q in ps)
    return {"path": path, "sha256": sha(path), "dur_s": round(dur, 3), "words": words, "wpm": round(words / dur * 60, 1),
            "speech_wpm500": round(words / speech * 60, 1), "n_pause500": len(ps), "n_long_silence_ge_800ms": len(long_sil),
            "sentence_end_pauses_ms": [q["pause_ms"] for q in pauses], "n_sentences": n_ref, "align_ratio": round(ratio, 3),
            "other_internal_runs_ms": other}


def main(out_dir, ev_dir):
    res = {"threshold_dbfs": PM.THR_DB, "trial_reference_values_NOT_a_production_gate": TRIAL_REF,
           "production_criteria_note": ("Production側に自動化された速度/ポーズ合否基準は無い。CURRENT_SPEC: A2(Std)英語ナレーション速度は約135WPMを"
                                         "『目安』(hard constraintではない、2026-08-12 DECIDED)、B1/B2(Adv)は現行の自然な速度を維持し明示的なWPM targetは新設しない。"
                                         "文末ポーズ・長無音の自動基準はCURRENT_SPECに無い。よって新Gateは作らず、Trial参照値を参考として実測を併記する。"),
           "levels": {}}
    for level, d in (("std", "a2"), ("adv", "b1b")):
        results = json.load(open(f"{out_dir}/{d}/audit/tts_generation_results.json", encoding="utf-8"))
        parts = []
        for n in (1, 2, 3):
            e = results["segments"][f"full_story_part{n}"]
            path = e["path"].replace("\\", "/")
            text = e.get("canonical_text") or e.get("text")
            parts.append(analyze_part(path, f"m2n01_{level}_part{n}", text, os.path.join(ev_dir, "words")))
        W = sum(p["words"] for p in parts)
        D = sum(p["dur_s"] for p in parts)
        allp = [m for p in parts for m in p["sentence_end_pauses_ms"]]
        res["levels"][level] = {"parts": parts, "total_words": W, "total_dur_s": round(D, 2), "total_wpm": round(W / D * 60, 1),
                                "sentence_end_pause_mean_ms": round(float(np.mean(allp))) if allp else None,
                                "sentence_end_pause_max_ms": max(allp) if allp else None, "n_sentence_end_pauses": len(allp),
                                # 800ms以上の無音(find_pauses、-40dBFS基準): 文末・内部を区別せず各part全体で数える
                                "n_long_silence_ge_800ms_total": sum(p["n_long_silence_ge_800ms"] for p in parts)}}
        lv = res["levels"][level]
        ref_w = TRIAL_REF["std_wpm_post_slowdown"] if level == "std" else TRIAL_REF["adv_wpm"]
        lv["reference_comparison"] = {
            "wpm_within_trial_reference": abs(lv["total_wpm"] - ref_w[0]) <= ref_w[1],
            "sentence_end_mean_le_trial_ref": (lv["sentence_end_pause_mean_ms"] or 0) <= TRIAL_REF["sentence_end_mean_ms_max"][level],
            "long_silence_le_trial_ref": lv["n_long_silence_ge_800ms_total"] <= TRIAL_REF["long_silence_ge_800ms_max"]}
    json.dump(res, open(f"{ev_dir}/speed_pause_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "parts"} for k, v in res["levels"].items()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
