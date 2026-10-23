# 組立後の通し音声QA(API 0): 長さ・順序・無音・peak/clip/NaN・旧(STALE)とのsequence_order一致。usage: qa_assembled_01.py
import json, os, sys
import numpy as np
import soundfile as sf
ROOT = "C:/Users/tensh/eigo-radio"; os.chdir(ROOT)
BASE = "er026_output/family_z_production_e2e_01"
RUNS = {"melos": (f"{BASE}/melos/run_e2e_06", "melos"), "open_window": (f"{BASE}/the_open_window/run_e2e_01", "the_open_window")}
out = {}
for story, (run, slug) in RUNS.items():
    for lv in ("a2", "b1b"):
        p = f"{run}/{lv}/assembly/Family_Z_{slug}_{lv}.wav"
        y, sr = sf.read(p, dtype="float32"); y = y if y.ndim == 1 else y.mean(axis=1)
        tl = json.load(open(f"{run}/{lv}/assembly/timeline.json", encoding="utf-8"))
        old = json.load(open(f"{run}/STALE_speed_v1_20261023/{lv}/assembly/timeline.json", encoding="utf-8"))
        # 無音: 1フレーム20msのRMS<1e-4が連続する最長区間
        fr = int(sr * 0.02); n = len(y) // fr
        rms = np.sqrt((y[: n * fr].reshape(n, fr) ** 2).mean(axis=1)); sil = rms < 1e-4
        longest = cur = 0
        for s in sil:
            cur = cur + 1 if s else 0; longest = max(longest, cur)
        rec = {"duration_seconds": round(len(y) / sr, 3), "old_duration_seconds": round(old["duration_seconds"], 3), "peak": round(float(np.abs(y).max()), 4),
               "clipped_samples(>=0.999)": int((np.abs(y) >= 0.999).sum()), "nan": bool(np.isnan(y).any()), "rms": round(float(np.sqrt((y ** 2).mean())), 4),
               "longest_silence_seconds": round(longest * 0.02, 2), "sequence_order_equal_old": tl["sequence_order"] == old["sequence_order"],
               "n_pieces": len(tl["sequence_order"]), "headroom_applied": tl["headroom"].get("applied")}
        out[f"{story}/{lv}"] = rec; print(story, lv, rec)
json.dump(out, open("er026_output/family_z_dialogue_speed_wiring_01/qa_assembled_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
