# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-KP-EN-EXPLANATION-STYLE-TRIAL-01 測定lib(measure_wpm_01.py方式を再実装、-40dBFS/20ms frame/10ms hop。元scriptは import時に全処理が走るため再利用不可)。"""
import re, numpy as np, soundfile as sf
FRAME_MS, HOP_MS, THRESH_DB = 20, 10, -40.0
def load(p):
    x, sr = sf.read(p, dtype="float64"); return (x if x.ndim == 1 else x[:, 0]), sr
def frame_db(x, sr):
    f, h = int(sr*FRAME_MS/1000), int(sr*HOP_MS/1000)
    n = max(0, (len(x)-f)//h+1)
    if n == 0: return np.array([])
    idx = np.arange(f)[None, :] + h*np.arange(n)[:, None]
    r = np.sqrt(np.mean(x[idx]**2, axis=1))
    return 20*np.log10(np.maximum(r, 1e-10))
def pauses(db, min_ms, dur):
    sil = db < THRESH_DB; res = []; i = 0; n = len(sil)
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]: j += 1
            s, e = i*HOP_MS/1000, min(dur, (j-1)*HOP_MS/1000+FRAME_MS/1000)
            if (e-s)*1000 >= min_ms:
                res.append({"start": round(s, 3), "end": round(e, 3), "dur": round(e-s, 3), "edge": "head" if i == 0 else ("tail" if j >= n else "mid")})
            i = j
        else: i += 1
    return res
def count_words(t): return sum(1 for w in t.split() if re.search(r"[A-Za-z0-9]", w))
def measure(path, words):
    x, sr = load(path); dur = len(x)/sr; db = frame_db(x, sr)
    p500 = pauses(db, 500, dur); p300 = pauses(db, 300, dur)
    sp500 = dur - sum(q["dur"] for q in p500)
    mid300 = [q for q in p300 if q["edge"] == "mid"]
    p150 = pauses(db, 150, dur); mid150 = [q for q in p150 if q["edge"] == "mid"]
    head = next((q["dur"] for q in p150 if q["edge"] == "head"), 0.0); tail = next((q["dur"] for q in p150 if q["edge"] == "tail"), 0.0)
    core_span = round(dur - head - tail, 3); core_speech = round(core_span - sum(q["dur"] for q in mid150), 3)
    pk = float(np.max(np.abs(x)))
    return {"duration_s": round(dur, 3), "words": words, "wpm_total": round(words/dur*60, 1),
            "speech_wpm500": round(words/sp500*60, 1) if sp500 > 0 else None, "speech_s500": round(sp500, 3),
            "pauses500": p500, "n_pause500": len(p500), "pause500_total_s": round(sum(q["dur"] for q in p500), 3),
            "pauses300": p300, "n_pause300": len(p300), "pause300_total_s": round(sum(q["dur"] for q in p300), 3),
            "mid300_n": len(mid300), "mid300_total_s": round(sum(q["dur"] for q in mid300), 3),
            "mid300_max_s": round(max([q["dur"] for q in mid300], default=0), 3),
            "head_s": round(next((q["dur"] for q in p300 if q["edge"] == "head"), 0), 3),
            "tail_s": round(next((q["dur"] for q in p300 if q["edge"] == "tail"), 0), 3),
            "core_span_s": core_span, "mid150_n": len(mid150), "mid150_total_s": round(sum(q["dur"] for q in mid150), 3), "mid150": mid150,
            "core_speech_s": core_speech, "speech_wpm_core": round(words/core_speech*60, 1) if core_speech > 0 else None,
            "peak": round(pk, 4), "peak_dbfs": round(20*np.log10(max(pk, 1e-10)), 2), "headroom_ok": pk < 0.98}
