# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICES-DESIGN-01 委任_05 Phase 3: 音声QA・Voice別実測(F0/話速)・長さ・費用の集計(API 0、DEV/Trial専用)。
入力: er110_output/family_y_trial_01/audio/<cand>/{b1b,a2}/ の audit・narration。出力: audio_qa_summary.json(同dir)。
F0は自己相関法(70〜330Hz、有声フレームのみ)の簡易推定で、Voice間の相対差(聞き分け可能性の数値材料)として使う。"""
from __future__ import annotations

import json
import os
import re
import sys

import numpy as np
import soundfile as sf

import er110_family_y_audio_trial_01 as y

BASE = y.OUT_ROOT


def _load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def f0_stats(x: np.ndarray, sr: int) -> dict:
    """自己相関F0。24kHz mono想定。フレーム40ms/hop10ms、有声判定=正規化自己相関ピーク>0.45かつエネルギー閾値超。"""
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float64)
    fl, hop = int(0.04 * sr), int(0.01 * sr)
    lo, hi = int(sr / 330), int(sr / 70)
    thr = 0.1 * np.sqrt(np.mean(x ** 2) + 1e-12)
    f0s, cents = [], []
    for s in range(0, len(x) - fl - hi, hop):
        fr = x[s:s + fl]
        if np.sqrt(np.mean(fr ** 2)) < thr:
            continue
        fr = fr - fr.mean()
        ac = np.correlate(fr, fr, mode="full")[fl - 1:]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        seg = ac[lo:hi]
        k = int(np.argmax(seg))
        if seg[k] > 0.45:
            f0s.append(sr / (lo + k))
    if len(f0s) < 20:
        return {"voiced_frames": len(f0s)}
    a = np.array(f0s)
    q = np.percentile(a, [10, 25, 50, 75, 90])
    # スペクトル重心(明るさの目安)
    spec = np.abs(np.fft.rfft(x[: min(len(x), sr * 30)]))
    freqs = np.fft.rfftfreq(min(len(x), sr * 30), 1 / sr)
    centroid = float((spec * freqs).sum() / (spec.sum() + 1e-12))
    return {"voiced_frames": len(f0s), "f0_median_hz": round(float(q[2]), 1), "f0_p10_hz": round(float(q[0]), 1),
            "f0_p90_hz": round(float(q[4]), 1), "f0_iqr_hz": round(float(q[3] - q[1]), 1),
            "f0_range_semitones_p10_p90": round(float(12 * np.log2(q[4] / q[0])), 2), "spectral_centroid_hz": round(centroid, 0)}


def seg_audio_metrics(theme: str, level: str, name: str, text: str, original: bool = False) -> dict:
    p = f"{theme}/{level}/narration/{name}{'_original' if original else ''}.wav"
    if not os.path.exists(p):
        return {"missing": p}
    x, sr = sf.read(p, dtype="float32")
    dur = len(x) / sr
    words = len(text.split())
    d = {"duration_s": round(dur, 2), "words": words, "wpm": round(words / dur * 60, 1) if dur else None}
    d.update(f0_stats(x, sr))
    return d


def asr_summary(theme: str, level: str) -> dict:
    res = _load(f"{theme}/{level}/audit/tts_generation_results.json")
    rows = {}
    for name, e in (res.get("segments") or {}).items():
        aj = e.get("asr_judgement") or e.get("asr_judgement_inherited") or {}
        rows[name] = {
            "status": e.get("status"), "asr_judgement": (aj.get("state") if isinstance(aj, dict) else aj) or (aj if isinstance(aj, str) else None),
            "attempts": len(e.get("attempts_log") or []), "tts_generations_used": e.get("tts_generations_used"),
            "instruction_type": e.get("instruction_type"), "fallback_used": e.get("fallback_used"),
            "slowdown_applied": e.get("slowdown_applied"), "reused_from_previous_run": e.get("reused_from_previous_run", False),
            "human_review": bool(e.get("human_review_required") or e.get("status") in ("HUMAN_REVIEW_LOCKED", "STOPPED")),
            "voice_requested": e.get("y_tts_voice_requested"), "asr_text_head": (e.get("asr_text") or "")[:80]}
    kp = {}
    for rank, d in (res.get("key_phrases") or {}).items():
        kp[rank] = {k: (v or {}).get("status") for k, v in d.items()}
    return {"segments": rows, "key_phrases": kp, "style_version": res.get("style_version")}


def voice_used_evidence(theme: str, level: str) -> dict:
    """各Y本文segmentで実際にTTSへ渡されたvoice名(attempt metadata json / raw_usage_log由来)を照合する。"""
    out = {}
    res = _load(f"{theme}/{level}/audit/tts_generation_results.json")
    for name in y.Y_BODY_IDS:
        e = (res.get("segments") or {}).get(name) or {}
        voices = set()
        for att in e.get("attempts_log") or []:
            p = att.get("attempt_audio_path")
            if p:
                mp = os.path.splitext(p)[0] + ".json"
                for cand in (mp, p + ".json"):
                    if os.path.exists(cand):
                        try:
                            m = _load(cand)
                            if m.get("voice"):
                                voices.add(m["voice"])
                        except Exception:
                            pass
        out[name] = {"requested": y.Y_VOICE_OF[name], "observed_in_attempt_metadata": sorted(voices)}
    return out


def build(cand: str) -> dict:
    theme = f"{BASE}/{cand}"
    summary = {"cand": cand, "levels": {}}
    for level in ("b1b", "a2"):
        lv = {}
        parts = _load(f"{theme}/{level}/parts.json")
        texts = {s: parts[f"part{i}"] for i, s in enumerate(y.Y_BODY_IDS, start=1)}
        texts["in_one_line"] = parts["in_one_line"]
        metrics = {}
        for s in (*y.Y_BODY_IDS, "in_one_line"):
            metrics[s] = seg_audio_metrics(theme, level, s, texts[s])
            if level == "a2":
                metrics[s]["original_pre_slowdown"] = seg_audio_metrics(theme, level, s, texts[s], original=True)
        lv["segment_metrics"] = metrics
        lv["asr"] = asr_summary(theme, level)
        try:
            lv["voice_evidence"] = voice_used_evidence(theme, level)
        except Exception as exc:   # noqa: BLE001
            lv["voice_evidence"] = {"error": str(exc)}
        for fn in ("run_summary_assemble.json", "run_summary_assemble_voice_noslow.json"):
            p = f"{theme}/{level}/{fn}"
            if os.path.exists(p):
                lv[fn.replace(".json", "")] = {k: v for k, v in _load(p).items() if k in ("status", "duration_seconds", "clipping_detected", "peak")}
        pw = f"{theme}/{level}/audit/pass_with_warning_listening_list.json"
        lv["pass_with_warning"] = _load(pw) if os.path.exists(pw) else {"count": 0, "entries": []}
        sg = f"{theme}/{level}/audit/y_style_profile_gate.json"
        lv["y_style_gate"] = {k: _load(sg).get(k) for k in ("status", "y_body_blocked", "x_gate_blocked_after_filter")} if os.path.exists(sg) else None
        summary["levels"][level] = lv
    log = f"{theme}/raw_usage_log.jsonl"
    if os.path.exists(log):
        import er019_family_x_audio_production_runner_01 as xr
        jpy, by = xr.compute_cost_jpy_so_far(log)
        summary["cost_jpy"] = round(jpy, 2)
        summary["cost_by_provider"] = {k: round(v, 2) for k, v in by.items()}
    with open(f"{theme}/audio_qa_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def voice_table(summary: dict) -> list:
    rows = []
    for level, lv in summary["levels"].items():
        for s in (*y.Y_BODY_IDS, "in_one_line"):
            m = lv["segment_metrics"][s]
            rows.append((summary["cand"], level, s, y.Y_ROLE_OF.get(s, "in_one_line"), y.Y_VOICE_OF.get(s, "Aoede"),
                         m.get("duration_s"), m.get("words"), m.get("wpm"), m.get("f0_median_hz"), m.get("f0_range_semitones_p10_p90"),
                         m.get("spectral_centroid_hz")))
    return rows


if __name__ == "__main__":
    for c in sys.argv[1:] or ["r2", "r0"]:
        if os.path.isdir(f"{BASE}/{c}/b1b/narration"):
            s = build(c)
            print(c, "cost", s.get("cost_jpy"))
            for r in voice_table(s):
                print(r)
