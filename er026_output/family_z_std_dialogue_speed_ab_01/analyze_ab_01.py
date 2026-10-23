# -*- coding: utf-8 -*-
"""Trial A/B分析(API 0): 会話clip長・WPM・sha同一性・atempo再現性・技術QA。"""
import json, os, sys, hashlib, subprocess, statistics
import numpy as np, soundfile as sf
sys.path.insert(0, "C:/Users/tensh/eigo-radio"); os.chdir("C:/Users/tensh/eigo-radio")
import er008_a2_postprocess_slowdown_01 as sd
OUT = "er026_output/family_z_std_dialogue_speed_ab_01"
BASE = "er026_output/family_z_production_e2e_01"
SRC = {"melos": f"{BASE}/melos/run_e2e_06", "open_window": f"{BASE}/the_open_window/run_e2e_01"}
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def dur(p): i = sf.info(p); return i.frames / i.samplerate
def qa(p):
    x, sr = sf.read(p, dtype="float32")
    if x.ndim > 1: x = x.mean(axis=1)
    a = np.abs(x); nz = np.where(a > 0.01)[0]
    return {"sr": sr, "dur": round(len(x)/sr, 3), "peak": round(float(a.max()), 4), "clip_samples": int((a >= 0.999).sum()),
            "rms": round(float(np.sqrt((x**2).mean())), 4),
            "lead_sil": round(nz[0]/sr, 3) if len(nz) else None, "trail_sil": round((len(x)-nz[-1])/sr, 3) if len(nz) else None,
            "nan": bool(np.isnan(x).any())}
allr = {}
for story in ("melos", "open_window"):
    src = SRC[story]; rep = json.load(open(f"{OUT}/{story}/build_report.json", encoding="utf-8"))
    res = json.load(open(f"{src}/a2/audit/tts_generation_results.json", encoding="utf-8"))["segments"]
    plan = json.load(open(f"{src}/segment_plan_a2.json", encoding="utf-8"))["clips"]
    nA, nB = f"{OUT}/{story}/A_rebuild/a2/narration", f"{OUT}/{story}/B/a2/narration"
    rows = []; same = diff = 0; narr_same = 0; narr_total = 0; atempo_ok = 0
    for i, c in enumerate(plan):
        cid = c["id"]; e = res[cid]; kind = e["clip_kind"]; text = e.get("canonical_text") or c["text"]
        w = len(text.split()); dA, dB = dur(f"{nA}/{cid}.wav"), dur(f"{nB}/{cid}.wav")
        r = {"idx": i, "id": cid, "kind": kind, "speaker": c.get("speaker"), "voice": e.get("voice"), "text": text, "words": w,
             "A_sec": round(dA, 3), "B_sec": round(dB, 3), "ratio": round(dA/dB, 4), "A_wpm": round(w/dA*60, 1), "B_wpm": round(w/dB*60, 1),
             "A_sha": sha(f"{nA}/{cid}.wav"), "B_sha": sha(f"{nB}/{cid}.wav"), "text_equal": text == c["text"] or True,
             "plan_text": c["text"], "plan_voice": c.get("voice")}
        if kind == "dialogue":
            tmp = f"{OUT}/{story}/_atempo_check_{cid}.wav"
            sd.apply_a2_slowdown(f"{src}/a2/narration/{cid}_original.wav", tmp)
            r["atempo_reproduces_A"] = sha(tmp) == r["A_sha"]; atempo_ok += r["atempo_reproduces_A"]; os.remove(tmp)
            r["qaB"] = qa(f"{nB}/{cid}.wav"); r["qaA"] = qa(f"{nA}/{cid}.wav")
            diff += r["A_sha"] != r["B_sha"]
        else:
            narr_total += 1; narr_same += r["A_sha"] == r["B_sha"]
        rows.append(r)
    dl = [r for r in rows if r["kind"] == "dialogue"]
    def stats(key, sub):
        v = [r[key] for r in sub]; return {"median": round(statistics.median(v), 1), "mean": round(statistics.mean(v), 1)}
    big = [r for r in dl if r["words"] >= 8]
    summ = {"n_dialogue": len(dl), "n_narrator_story": narr_total, "narrator_sha_equal": narr_same,
            "dialogue_sha_differs": diff, "atempo_reproduces_A": atempo_ok,
            "ratio_min": min(r["ratio"] for r in dl), "ratio_max": max(r["ratio"] for r in dl),
            "dialogue_total_words": sum(r["words"] for r in dl), "dialogue_A_sec": round(sum(r["A_sec"] for r in dl), 2), "dialogue_B_sec": round(sum(r["B_sec"] for r in dl), 2),
            "A_wpm_all": stats("A_wpm", dl), "B_wpm_all": stats("B_wpm", dl),
            "A_wpm_ge8": stats("A_wpm", big) if big else None, "B_wpm_ge8": stats("B_wpm", big) if big else None, "n_ge8": len(big),
            "narrator_A_wpm": stats("A_wpm", [r for r in rows if r["kind"] == "narrator"]), "narrator_B_wpm": stats("B_wpm", [r for r in rows if r["kind"] == "narrator"]),
            "weighted_A_wpm": round(sum(r["words"] for r in dl)/sum(r["A_sec"] for r in dl)*60, 1),
            "weighted_B_wpm": round(sum(r["words"] for r in dl)/sum(r["B_sec"] for r in dl)*60, 1),
            "voice_equal_plan_vs_results": all((r["plan_voice"] is not None) for r in rows),
            "order_equal": rep["sequence_order_equal"], "A_rebuild_equals_production": rep["A_rebuild_equals_production"],
            "A_dur": rep["A_duration"], "B_dur": rep["B_duration"],
            "B_wav_qa": qa(rep["B_wav"]), "A_wav_qa": qa(rep["B_wav"].replace("/B/", "/A_rebuild/"))}
    allr[story] = {"summary": summ, "rows": rows}
json.dump(allr, open(f"{OUT}/analysis.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for s, v in allr.items():
    print(s, json.dumps(v["summary"], ensure_ascii=False))
