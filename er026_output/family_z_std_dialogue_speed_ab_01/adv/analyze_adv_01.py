# -*- coding: utf-8 -*-
"""FZSPAB 委任_02 Advanced分析+mp3+manifest(API 0)。ASRはローカルfaster-whisper。"""
import json, os, sys, hashlib, statistics, re, difflib
import numpy as np, soundfile as sf, lameenc
sys.path.insert(0, "C:/Users/tensh/eigo-radio"); os.chdir("C:/Users/tensh/eigo-radio")
OUT = "er026_output/family_z_std_dialogue_speed_ab_01/adv"; BASE = "er026_output/family_z_production_e2e_01"
SRC = {"melos": f"{BASE}/melos/run_e2e_06", "open_window": f"{BASE}/the_open_window/run_e2e_01"}
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def dur(p): i = sf.info(p); return i.frames / i.samplerate
def qa(p):
    x, sr = sf.read(p, dtype="float32")
    if x.ndim > 1: x = x.mean(axis=1)
    a = np.abs(x); nz = np.where(a > 0.01)[0]
    return {"sr": sr, "dur": round(len(x)/sr, 3), "peak": round(float(a.max()), 4), "clip_samples": int((a >= 0.999).sum()), "rms": round(float(np.sqrt((x**2).mean())), 4),
            "lead_sil": round(nz[0]/sr, 3) if len(nz) else None, "trail_sil": round((len(x)-nz[-1])/sr, 3) if len(nz) else None, "nan": bool(np.isnan(x).any())}
def mp3(path, x, sr):
    if x.ndim == 1: x = x[:, None]
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    e = lameenc.Encoder(); e.set_bit_rate(128); e.set_in_sample_rate(sr); e.set_channels(pcm.shape[1]); e.set_quality(2)
    open(path, "wb").write(e.encode(pcm.tobytes()) + e.flush())
def norm(s): return re.sub(r"[^a-z0-9' ]", " ", s.lower().replace("’", "'")).split()
from faster_whisper import WhisperModel
wm = WhisperModel("small.en", device="cpu", compute_type="int8")
def asr(p):
    segs, _ = wm.transcribe(p, language="en", beam_size=5, condition_on_previous_text=False)
    return " ".join(s.text.strip() for s in segs)
allr = {}; manifest = {"trial": "FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01", "delegation": "02_ADV", "level": "advanced(b1b)", "process": "ffmpeg atempo=1.06 (er008 apply_a2_slowdown reuse, pitch-preserving)", "stories": {}}
for story in ("melos", "open_window"):
    src = SRC[story]; rep = json.load(open(f"{OUT}/{story}/build_report.json", encoding="utf-8"))
    res = json.load(open(f"{src}/b1b/audit/tts_generation_results.json", encoding="utf-8"))["segments"]
    plan = json.load(open(f"{src}/segment_plan_b1b.json", encoding="utf-8"))["clips"]
    nA, nB = f"{OUT}/{story}/A_rebuild/b1b/narration", f"{OUT}/{story}/B/b1b/narration"
    md = f"{OUT}/{story}/mp3"; os.makedirs(md, exist_ok=True)
    rows = []; n = 0
    for i, c in enumerate(plan):
        cid = c["id"]; e = res[cid]; kind = e["clip_kind"]; text = e.get("canonical_text") or c["text"]; w = len(text.split())
        dA, dB = dur(f"{nA}/{cid}.wav"), dur(f"{nB}/{cid}.wav")
        r = {"idx": i, "id": cid, "kind": kind, "speaker": c.get("speaker"), "voice": e.get("voice") or c.get("voice"), "text": text, "plan_text": c["text"], "words": w,
             "A_sec": round(dA, 3), "B_sec": round(dB, 3), "ratio_B_over_A": round(dB/dA, 4), "A_wpm": round(w/dA*60, 1), "B_wpm": round(w/dB*60, 1),
             "A_sha": sha(f"{nA}/{cid}.wav"), "B_sha": sha(f"{nB}/{cid}.wav")}
        if kind == "dialogue":
            n += 1; r["qaA"] = qa(f"{nA}/{cid}.wav"); r["qaB"] = qa(f"{nB}/{cid}.wav")
            e_, a_ = norm(text), norm(asr(f"{nB}/{cid}.wav")); r["asr_B"] = " ".join(a_)
            r["asr_exact_norm"] = e_ == a_; r["asr_similarity"] = round(difflib.SequenceMatcher(None, e_, a_).ratio(), 3)
            r["asr_A_stored"] = e.get("asr_text")
            for v, nd in (("A", nA), ("B", nB)):
                x, sr = sf.read(f"{nd}/{cid}.wav", dtype="float32"); mp3(f"{md}/d{n:02d}_{v}.mp3", x, sr)
            r["mp3_A"] = f"{md}/d{n:02d}_A.mp3"; r["mp3_B"] = f"{md}/d{n:02d}_B.mp3"
            print(story, cid, r["asr_exact_norm"], r["asr_similarity"], r["ratio_B_over_A"], flush=True)
        rows.append(r)
    for v, w in (("A", rep["prod_wav_sha"] and f"{OUT}/{story}/A_rebuild/b1b/assembly/Family_Z_{'melos' if story=='melos' else 'the_open_window'}_b1b.wav"), ("B", rep["B_wav"])):
        x, sr = sf.read(w, dtype="float32"); mp3(f"{md}/full_{v}.mp3", x, sr)
    dl = [r for r in rows if r["kind"] == "dialogue"]; nr = [r for r in rows if r["kind"] == "narrator"]; big = [r for r in dl if r["words"] >= 8]
    med = lambda k, s: round(statistics.median([r[k] for r in s]), 1)
    wt = lambda k, s: round(sum(r["words"] for r in s)/sum(r[k] for r in s)*60, 1)
    summ = {"n_dialogue": len(dl), "n_narrator": len(nr), "nondialogue_clip_sha_equal": rep["non_dialogue_equal"], "nondialogue_clip_total": rep["non_dialogue_total"],
            "ratio_min": min(r["ratio_B_over_A"] for r in dl), "ratio_max": max(r["ratio_B_over_A"] for r in dl),
            "narr_wpm_median": med("A_wpm", nr), "narr_wpm_weighted": wt("A_sec", nr), "narr_n_ge8": len([r for r in nr if r["words"]>=8]),
            "dlg_A_wpm_median": med("A_wpm", dl), "dlg_B_wpm_median": med("B_wpm", dl), "dlg_A_wpm_ge8": med("A_wpm", big), "dlg_B_wpm_ge8": med("B_wpm", big), "n_ge8": len(big),
            "dlg_A_wpm_weighted": wt("A_sec", dl), "dlg_B_wpm_weighted": wt("B_sec", dl),
            "narr_wpm_ge8_median": med("A_wpm", [r for r in nr if r["words"]>=8]),
            "A_dur": rep["A_duration"], "B_dur": rep["B_duration"], "order_equal": rep["sequence_order_equal"], "A_rebuild_equals_production": rep["A_rebuild_equals_production"],
            "asr_exact_norm": sum(r["asr_exact_norm"] for r in dl), "asr_sim_lt_0_9": [r["id"] for r in dl if r["asr_similarity"] < 0.9],
            "B_full_qa": qa(rep["B_wav"]), "A_full_qa": qa(f"{OUT}/{story}/A_rebuild/b1b/assembly/Family_Z_{'melos' if story=='melos' else 'the_open_window'}_b1b.wav"),
            "plan_text_equal_results": all(r["text"].strip()==r["plan_text"].strip() for r in rows)}
    allr[story] = {"summary": summ, "rows": rows}
    manifest["stories"][story] = {"source_run": src, "full": {"A": f"{md}/full_A.mp3", "B": f"{md}/full_B.mp3", "A_sec": rep["A_duration"], "B_sec": rep["B_duration"], "A_wav_sha": rep["prod_wav_sha"], "B_wav_sha": rep["B_wav_sha"]},
        "wpm_summary": {k: summ[k] for k in summ if "wpm" in k or k=="n_ge8"},
        "clips": [{"clip_id": r["id"], "speaker": r["speaker"], "voice": r["voice"], "text": r["text"], "words": r["words"], "A_mp3": r["mp3_A"], "B_mp3": r["mp3_B"], "A_sec": r["A_sec"], "B_sec": r["B_sec"],
                   "A_wpm": r["A_wpm"], "B_wpm": r["B_wpm"], "tempo_factor": 1.06, "A_sha": r["A_sha"], "B_sha": r["B_sha"]} for r in dl],
        "narrator_unchanged_clips": [{"clip_id": r["id"], "sha_equal": r["A_sha"]==r["B_sha"], "sha": r["A_sha"]} for r in nr]}
json.dump(allr, open(f"{OUT}/analysis_adv.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(manifest, open(f"{OUT}/manifest_adv.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for s, v in allr.items(): print(s, json.dumps(v["summary"], ensure_ascii=False))
