# -*- coding: utf-8 -*-
"""H-speed Trial 測定(API呼出なし、費用0、faster-whisper small local)。8way測定を流用し3take化。"""
import os, sys, json, re, hashlib, statistics as st
import numpy as np
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_coffee_v5_pause_01_measure as M
import er057_audio_anomaly_detect_trial_01 as D
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_04", "round5")
os.makedirs(os.path.join(OUT, "words"), exist_ok=True); M.OUT = OUT
GL = [json.loads(l) for l in open(os.path.join(OUT, "generation_log_r5.jsonl"), encoding="utf-8")]
GL = {r["job"]: r for r in GL if r.get("status") == "OK"}
NW = {"std": 117, "adv": 131}
V5 = {"std": "er057_output/coffee_final_v4/segments/std_part1_slow6.wav", "adv": "er057_output/coffee_final_v4/segments/adv_part1_raw.wav"}
CS = [f"J{i:02d}" for i in range(1, 14)]
H0GL = {r["job"]: r for r in (json.loads(l) for l in open(os.path.join(ROOT, "er057_output/coffee_tts_style_h_speed_02/generation_log_02.jsonl"), encoding="utf-8")) if r.get("status") == "OK"}

def measure(p, lv, key):
    a = M.analyze(p); a["lv"] = lv
    x, sr = M.load(p); runs, dur = M.silent_runs(x, sr); w = M.words_of(p)
    end_p = [q["pause_ms"] for q in a["sentence_end_pauses"]]
    oth = a["other_internal_runs_ms"]
    long_sil = sum(b - c for c, b in runs if (b - c) > 0.5 and c > 0.005 and b < dur - 0.011)
    inner = [(c, b) for c, b in runs if c > 0.005 and b < dur - 0.011]
    longpos = []
    for c, b in inner:
        if (b - c) >= 0.8:
            prev = [q for q in w if q["e"] <= c + 0.15]; nxt = [q for q in w if q["s"] >= b - 0.15]
            longpos.append({"t": round(c, 2), "ms": round((b - c) * 1000), "prev": prev[-1]["w"] if prev else None, "next": nxt[0]["w"] if nxt else None})
    ref = M.REF[f"{lv}_part1"]["text"]; rt = [M.norm(t) for t in re.findall(r"\S+", ref) if M.norm(t)]
    at = [M.norm(q["w"]) for q in w if M.norm(q["w"])]
    tail_ok = rt[-3:] == at[-3:]
    rms = float(np.sqrt((x ** 2).mean())); peak = float(np.abs(x).max())
    anom, _ = D.analyze(x.astype("float64"), sr, key, True)
    anom_s = [{"symptom": e["symptom"], "conf": e["confidence"], "t": round(float(e["t"]), 2)} for e in anom]
    last = w[-1] if w else None
    return {"path": p, "sha12": a["sha12"], "dur_s": a["dur_s"], "words_ref": NW[lv], "wpm": round(NW[lv] / dur * 60, 1),
            "speech_wpm500": round(NW[lv] / (dur - long_sil) * 60, 1),
            "end_pause_ms": {"n": len(end_p), **{k: v for k, v in M.stats(end_p).items() if k in ("mean", "median", "max", "hist")}} if end_p else None,
            "mid": {"n": len(oth), "total_s": round(sum(oth) / 1000, 2), "n300": sum(1 for v in oth if v >= 300)},
            "long800": longpos, "tail_last3_match": tail_ok, "align_ratio": a["align_ratio"], "asr_words": len(w),
            "last_word": last["w"] if last else None, "last_word_dur_ms": round((last["e"] - last["s"]) * 1000) if last else None,
            "rms_dbfs": round(20 * np.log10(rms + 1e-12), 1), "peak_dbfs": round(20 * np.log10(peak + 1e-12), 1),
            "anomalies": anom_s, "anomaly_medium_plus": sum(1 for e in anom_s if str(e["conf"]).lower() in ("medium", "high"))}


def pitch_dyn(p):
    x, sr = M.load(p); x = np.asarray(x, dtype="float64")
    fl = int(0.04 * sr); hop = int(0.01 * sr); lo = int(sr / 400); hi = int(sr / 75)
    f0s = []; db = []
    for i in range(0, len(x) - fl, hop):
        fr = x[i:i + fl]; r = np.sqrt((fr ** 2).mean()); d = 20 * np.log10(r + 1e-12)
        if d < -40: continue
        db.append(d); fr = fr - fr.mean(); ac = np.correlate(fr, fr, "full")[fl - 1:]
        if ac[0] <= 0: continue
        seg = ac[lo:hi]; k = int(np.argmax(seg)); 
        if seg[k] / ac[0] > 0.5: f0s.append(sr / (lo + k))
    f0s = np.array(f0s); db = np.array(db)
    return {"pitch_p10_p90_semitones": round(float(12 * np.log2(np.percentile(f0s, 90) / np.percentile(f0s, 10))), 2) if len(f0s) > 50 else None,
            "pitch_median_hz": round(float(np.median(f0s)), 1) if len(f0s) else None, "voiced_frames": int(len(f0s)),
            "dyn_p10_p90_db": round(float(np.percentile(db, 90) - np.percentile(db, 10)), 1)}

def main():
    res = {"method": "faster-whisper small local, -40dBFS silence, min 50ms, same as TRIAL-02; Std measured as heard (slow6 applied); pitch=autocorr 40ms frames voiced>0.5, dyn=frame RMS p10-p90 (参考値)", "takes": {}, "v5": {}}
    jobs = {j: r for j, r in GL.items()}
    for jid, r in sorted(jobs.items()):
        m = measure(r["final_wav"], r["level"], jid); m.update(pitch_dyn(r["final_wav"]))
        m.update(cand=r["cand"], level=r["level"], primary_asr=r["classification"], asr_verified=r["verified"], duration_anomaly=r.get("duration_anomaly"), raw_sha256=r["raw_sha256"],
                 final_sha256=r["final_sha256"], tts_input_sha256=r["tts_input_sha256"], model_version=r["model_version"])
        res["takes"][jid] = m; print(jid, m["wpm"], m["end_pause_ms"] and m["end_pause_ms"]["mean"], m["mid"], m["pitch_p10_p90_semitones"], m["dyn_p10_p90_db"], flush=True)
    for lv in ("std", "adv"):
        r = H0GL[f"H0_{lv}_part1_t1"]; m = measure(r["final_wav"], lv, f"H0_{lv}"); m.update(pitch_dyn(r["final_wav"])); m["primary_asr"] = r["classification"]; res.setdefault("H0_t1", {})[lv] = m
        m = measure(V5[lv], lv, f"v5_{lv}"); m.update(pitch_dyn(V5[lv])); res["v5"][lv] = m
    json.dump(res, open(os.path.join(OUT, "measurements_r5.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
if __name__ == "__main__": main()
