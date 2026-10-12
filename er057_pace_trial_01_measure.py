# -*- coding: utf-8 -*-
"""委任_02 WPM実測(測定ロジックは measure_wpm_01.py の関数群をそのままexecして再利用。API費用0)。
使い方: python er057_pace_trial_01_measure.py PC1 PC2 ... (候補単位でjson出力)"""
import os, sys, json
ROOT = "C:/Users/tensh/eigo-radio"; sys.path.insert(0, ROOT)
src = open(f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01/wpm_measurement_01/measure_wpm_01.py", encoding="utf-8").read()
assert src.rstrip().endswith("\nmain()")
src = src.rstrip()[:-len("main()")]
ns = {"__name__": "m"}; exec(compile(src, "measure_wpm_01.py", "exec"), ns)
import numpy as np, soundfile as sf
OUT = f"{ROOT}/er057_output/pace_trial_01"
def measure(path, raw, safe):
    x, sr = sf.read(path, dtype="float32")
    if x.ndim > 1: x = x.mean(axis=1)
    dur = len(x) / sr
    wc = ns["count_primary"](safe)
    d = {"wav": os.path.relpath(path, ROOT).replace("\\", "/"), "sha256": ns["sha"](path), "duration_s": round(dur, 3), "words_adopted": wc,
         "wpm_overall": round(wc / dur * 60, 1), "pause_sens": {}}
    db = ns["frame_rms_db"](x, sr)
    aw = {m: ns["asr"](path, m) for m in ("medium", "small")}
    d["asr"] = {m: ns["diff_report"](ns["norm_words"](safe), aw[m]) for m in aw}
    for mp in ns["MIN_PAUSE_MS"]:
        ps = ns["find_pauses"](db, mp, dur)
        mid = [p for p in ps if p["edge"] == "mid"]; tot = sum(p["dur"] for p in ps); sp = dur - tot
        d["pause_sens"][str(mp)] = {"n_all": len(ps), "n_mid": len(mid), "total_all_s": round(tot, 3), "total_mid_s": round(sum(p["dur"] for p in mid), 3),
            "mean_mid_s": round(float(np.mean([p["dur"] for p in mid])), 3) if mid else 0, "speech_s": round(sp, 3), "wpm_speech": round(wc / sp * 60, 1)}
    d["windows10s"] = ns["window_wpm"](aw["medium"], ns["find_pauses"](db, 300, dur), dur)
    d["sentences"] = [{"t0": s[0]["s"], "t1": s[-1]["e"], "n": len(s), "wpm": round(len(s) / (s[-1]["e"] - s[0]["s"]) * 60, 1), "text": " ".join(w["w"] for w in s)}
                      for s in ns["sentences"](aw["medium"]) if s[-1]["e"] - s[0]["s"] > 0.5]
    return d
if __name__ == "__main__":
    import er057_tone_trial_final_build_03 as B
    jobs = {j["id"]: j for j in B.jobs_def() if j["level"] == "adv"}
    for c in sys.argv[1:]:
        R = {}
        for n in (1, 2, 3):
            j = jobs[f"adv_part{n}"]
            R[str(n)] = measure(f"{ROOT}/er057_output/pace_trial_01/attempts/{c}_adv_part{n}.wav", j["manuscript"], j["tts_input"])
            print(c, n, R[str(n)]["duration_s"], R[str(n)]["wpm_overall"], flush=True)
        json.dump(R, open(f"{OUT}/wpm/{c}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
