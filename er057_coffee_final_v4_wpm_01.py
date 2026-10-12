# -*- coding: utf-8 -*-
"""委任_01A: v3/v4 Full Story WPM(measure_wpm_01.py の count_primary/frame_rms_db/find_pauses を再利用、無料)。語数=Full Story tts_input語数。発話WPM=500ms以上ポーズ全除外。"""
import sys, json, importlib.util
ROOT = "C:/Users/tensh/eigo-radio"; sys.path.insert(0, ROOT)
spec = importlib.util.spec_from_file_location("mw", f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01/wpm_measurement_01/measure_wpm_01.py")
mw = importlib.util.module_from_spec(spec); spec.loader.exec_module(mw)
import soundfile as sf
import er057_tone_trial_final_build_03 as B
J = {j["id"]: j for j in B.jobs_def()}
V3 = "er057_output/coffee_final_audio_assembly_01/segments"; V4 = "er057_output/coffee_final_v4/segments"
P3 = {"adv": "er057_output/pace_trial_02/attempts/PD8_adv_part%d.wav", "std": V3 + "/std_part%d_slow6.wav"}
P4 = {"adv": V4 + "/adv_part%d_raw.wav", "std": V4 + "/std_part%d_slow6.wav"}
def meas(p, words):
    x, sr = sf.read(p, dtype="float64"); x = x if x.ndim == 1 else x[:, 0]
    dur = len(x) / sr; db = mw.frame_rms_db(x, sr); ps = mw.find_pauses(db, 500, dur)
    sp = dur - sum(q["dur"] for q in ps)
    return {"dur": round(dur, 2), "wpm": round(words / dur * 60, 1), "speech_wpm500": round(words / sp * 60, 1), "n_pause500": len(ps)}
res = {}
for lv in ("std", "adv"):
    for ver, P in (("v3", P3), ("v4", P4)):
        rows = []; W = D = S = 0
        for n in (1, 2, 3):
            w = mw.count_primary(J[f"{lv}_part{n}"]["tts_input"]); m = meas(P[lv] % n, w); m["words"] = w; rows.append(m)
            W += w; D += m["dur"]; S += w / m["speech_wpm500"] * 60
        res[f"{lv}_{ver}"] = {"parts": rows, "total_wpm": round(W / D * 60, 1), "total_speech_wpm500": round(W / S * 60, 1), "total_dur": round(D, 2), "words": W}
for lv in ("std", "adv"):
    a, b = res[f"{lv}_v3"], res[f"{lv}_v4"]
    res[f"{lv}_diff_pct"] = {"total_wpm": round((b["total_wpm"] / a["total_wpm"] - 1) * 100, 1), "speech_wpm500": round((b["total_speech_wpm500"] / a["total_speech_wpm500"] - 1) * 100, 1),
                              "dur": round((b["total_dur"] / a["total_dur"] - 1) * 100, 1)}
json.dump(res, open("er057_output/coffee_final_v4/wpm_v4_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
