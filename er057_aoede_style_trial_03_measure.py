# -*- coding: utf-8 -*-
"""全9本(P0含む)を同一scriptで測定。WPM測定ロジックは measure_wpm_01.py の関数群をexec再利用(-40dBFS/300,500ms)。API費用0。使い方: python ... P0 P1 ..."""
import os, sys, json
ROOT = "C:/Users/tensh/eigo-radio"; sys.path.insert(0, ROOT)
src = open(f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01/wpm_measurement_01/measure_wpm_01.py", encoding="utf-8").read()
src = src.rstrip()[:-len("main()")]
ns = {"__name__": "m"}; exec(compile(src, "measure_wpm_01.py", "exec"), ns)
import numpy as np, soundfile as sf
import er057_tone_trial_final_build_03 as B
OUT = f"{ROOT}/er057_output/aoede_style_trial_03"
safe = [j for j in B.jobs_def() if j["id"] == "adv_part1"][0]["tts_input"]
def measure(path):
    x, sr = sf.read(path, dtype="float32")
    if x.ndim > 1: x = x.mean(axis=1)
    dur = len(x) / sr; wc = ns["count_primary"](safe)
    d = {"wav": os.path.relpath(path, ROOT).replace("\\", "/"), "sha256": ns["sha"](path), "duration_s": round(dur, 3), "words": wc, "wpm_overall": round(wc / dur * 60, 1), "pause": {}}
    db = ns["frame_rms_db"](x, sr)
    for mp in ns["MIN_PAUSE_MS"]:
        ps = ns["find_pauses"](db, mp, dur); mid = [p for p in ps if p["edge"] == "mid"]; tot = sum(p["dur"] for p in ps)
        d["pause"][str(mp)] = {"n_all": len(ps), "n_mid": len(mid), "total_all_s": round(tot, 3), "total_mid_s": round(sum(p["dur"] for p in mid), 3),
                               "max_mid_s": round(max([p["dur"] for p in mid], default=0), 3), "speech_s": round(dur - tot, 3), "wpm_speech": round(wc / (dur - tot) * 60, 1)}
    pk = float(np.max(np.abs(x))); d["audio_qa"] = {"peak_abs": round(pk, 4), "peak_dbfs": round(20 * np.log10(pk), 2), "headroom_db": round(-20 * np.log10(pk), 2),
        "clip_samples_ge_0.999": int(np.sum(np.abs(x) >= 0.999)), "rms_dbfs": round(float(20 * np.log10(np.sqrt(np.mean(x.astype(np.float64) ** 2)))), 2)}
    aw = ns["asr"](path, "medium"); d["local_whisper_medium_diff"] = ns["diff_report"](ns["norm_words"](safe), aw)
    return d
if __name__ == "__main__":
    for c in sys.argv[1:]:
        r = measure(f"{OUT}/audio/{c}.wav"); json.dump(r, open(f"{OUT}/m/{c}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1); print(c, r["duration_s"], r["wpm_overall"], r["pause"]["500"]["wpm_speech"], flush=True)
