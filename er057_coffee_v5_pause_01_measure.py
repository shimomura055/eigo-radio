# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-V5-PAUSE-ROOT-CAUSE-01: 文末無音のオフライン測定(API呼出なし、local faster-whisper small)。
usage: python er057_coffee_v5_pause_01_measure.py"""
import os, sys, json, hashlib, re
import numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er057_output", "coffee_v5_pause_01")
os.makedirs(os.path.join(OUT, "words"), exist_ok=True)
THR_DB, MIN_RUN, FRAME = -40.0, 0.05, 0.01
V4S = "er057_output/coffee_final_v4/segments"; F5S = "er057_output/coffee_final_listening_tone_trial_01/part_final/segments"
PD8 = "er057_output/pace_trial_02/attempts"
V3S = "er057_output/coffee_final_audio_assembly_01/segments"
# set name -> (part -> path, slowdown_ratio_in_file)
SETS = {}
for lv in ("std", "adv"):
    pass
SETS["v5/v4 Adv FS (P8 new take)"] = ([f"{V4S}/adv_part{n}_raw.wav" for n in (1, 2, 3)], 1.0)
SETS["v5/v4 Std FS raw (P8, pre-slowdown)"] = ([f"{V4S}/std_part{n}_raw.wav" for n in (1, 2, 3)], 1.0)
SETS["v5/v4 Std FS slow6 (as heard)"] = ([f"{V4S}/std_part{n}_slow6.wav" for n in (1, 2, 3)], 1.06)
SETS["PD8 Trial take (=v3 Adv)"] = ([f"{PD8}/PD8_adv_part{n}.wav" for n in (1, 2, 3)], 1.0)
SETS["v3 Std FS slow6 (PD8+6%)"] = ([f"{V3S}/std_part{n}_slow6.wav" for n in (1, 2, 3)], 1.06)
SETS["F5 Adv FS (final_v2)"] = ([f"{F5S}/adv_part{n}_f5.wav" for n in (1, 2, 3)], 1.0)
SETS["F5 Std FS slow6 (final_v2)"] = ([f"{F5S}/std_part{n}_f5_slow6.wav" for n in (1, 2, 3)], 1.06)
ABBR = {"u.s.", "u.k.", "mr.", "mrs.", "dr.", "st.", "no.", "vs."}


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(p):
    x, sr = sf.read(os.path.join(ROOT, p), dtype="float32")
    if x.ndim > 1: x = x.mean(axis=1)
    return x, sr


def silent_runs(x, sr, thr=THR_DB):
    n = int(sr * FRAME); m = len(x) // n
    rms = np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(axis=1) + 1e-20)
    db = 20 * np.log10(rms + 1e-12)
    sil = db < thr
    runs, i = [], 0
    while i < m:
        if sil[i]:
            j = i
            while j < m and sil[j]: j += 1
            if (j - i) * FRAME >= MIN_RUN - 1e-9: runs.append((i * FRAME, j * FRAME))
            i = j
        else: i += 1
    return runs, m * FRAME


_model = None
def words_of(p):
    cache = os.path.join(OUT, "words", hashlib.sha1(p.encode()).hexdigest()[:10] + ".json")
    if os.path.exists(cache) and json.load(open(cache))["sha"] == sha(os.path.join(ROOT, p)): return json.load(open(cache))["words"]
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = _model.transcribe(os.path.join(ROOT, p), language="en", word_timestamps=True, beam_size=5, condition_on_previous_text=False)
    w = [{"w": a.word.strip(), "s": a.start, "e": a.end} for s in segs for a in s.words]
    json.dump({"path": p, "sha": sha(os.path.join(ROOT, p)), "words": w}, open(cache, "w"))
    return w


REF = json.load(open(os.path.join(OUT, "tts_input_texts.json"), encoding="utf-8"))
def norm(t): return re.sub(r"[^a-z0-9]", "", t.lower())
def ref_sents(job):
    t = REF[job]["text"].replace("U.S.", "U_S_")
    ss = re.split(r"(?<=[.?!])\s+(?=[A-Z\"'])", t)
    return [s.replace("U_S_", "U.S.") for s in ss]
def ref_end_to_asr(job, w):
    """reference文末tokenを、ASR word列へdifflib整列で写像(ASR句読点に依存しない)"""
    import difflib
    rt, ends = [], []
    for s in ref_sents(job):
        toks = [norm(x) for x in re.findall(r"\S+", s) if norm(x)]
        rt += toks; ends.append(len(rt) - 1)
    at = [norm(a["w"]) for a in w]
    m = difflib.SequenceMatcher(None, rt, at, autojunk=False)
    mp = {}
    for a, b, n in m.get_matching_blocks():
        for k in range(n): mp[a + k] = b + k
    out = []
    for e in ends[:-1]:
        k = e
        while k >= 0 and k not in mp: k -= 1
        if k >= 0 and mp[k] < len(w) - 1: out.append(mp[k] + (0 if k == e else 0))
        else: out.append(None)
    return out, len(ends), m.ratio()


def analyze(p, thr=THR_DB):
    x, sr = load(p); runs, dur = silent_runs(x, sr, thr); w = words_of(p)
    lead = runs[0][1] if runs and runs[0][0] < 0.005 else 0.0
    trail = dur - runs[-1][0] if runs and runs[-1][1] >= dur - 0.011 else 0.0
    job = ("std" if "std_" in p or "std" in os.path.basename(p) else "adv") + "_part" + re.search(r"part(\d)", p).group(1)
    ends, n_ref, ratio = ref_end_to_asr(job, w)
    ends = [i for i in ends if i is not None]
    pauses = []
    used = set()
    for i in ends:
        lo, hi = w[i]["e"] - 0.25, w[i + 1]["s"] + 0.25
        best, bo = None, 0
        for k, (a, b) in enumerate(runs):
            ov = min(b, hi) - max(a, lo)
            if ov > bo: best, bo = k, ov
        if best is not None: used.add(best)
        pauses.append({"after": w[i]["w"], "t": round(w[i]["e"], 2), "pause_ms": round((runs[best][1] - runs[best][0]) * 1000) if best is not None else 0})
    other = [round((b - a) * 1000) for k, (a, b) in enumerate(runs) if k not in used and a > 0.005 and b < dur - 0.011]
    return {"path": p, "sha12": sha(os.path.join(ROOT, p))[:12], "dur_s": round(dur, 3), "lead_ms": round(lead * 1000), "trail_ms": round(trail * 1000),
            "n_words": len(w), "n_sentences": n_ref, "n_boundaries_mapped": len(ends), "align_ratio": round(ratio, 3), "sentence_end_pauses": pauses, "other_internal_runs_ms": other}


BINS = [(0, 50), (50, 150), (150, 300), (300, 500), (500, 800), (800, 1200), (1200, 10 ** 9)]
def stats(vals):
    v = np.array(vals, float)
    h = {f"{a}-{b if b < 10**9 else 'inf'}": int(((v >= a) & (v < b)).sum()) for a, b in BINS}
    return {"n": len(v), "mean": round(float(v.mean())), "median": round(float(np.median(v))), "max": int(v.max()), "sum_ms": int(v.sum()), "hist": h} if len(v) else {"n": 0}


def main():
    res = {"threshold_dbfs": THR_DB, "min_run_s": MIN_RUN, "asr": "faster-whisper small (local, cost 0)", "sets": {}}
    for name, (paths, ratio) in SETS.items():
        parts = [analyze(p) for p in paths]
        allp = [q["pause_ms"] for pt in parts for q in pt["sentence_end_pauses"]]
        st = stats(allp); st2 = {k: (round(v / ratio) if k in ("mean", "median", "max", "sum_ms") else v) for k, v in st.items()} if ratio != 1.0 else None
        # sentence-end pauses excluding zero (no silent run found)
        nz = [a for a in allp if a > 0]
        res["sets"][name] = {"ratio_in_file": ratio, "parts": parts, "sentence_end_stats_ms": st, "pre_slowdown_equiv_ms": st2, "n_zero": len(allp) - len(nz),
                             "n_sentences_total": sum(pt["n_sentences"] for pt in parts), "total_dur_s": round(sum(pt["dur_s"] for pt in parts), 2),
                             "total_sentence_end_pause_s": round(sum(allp) / 1000, 2)}
        print(name, st["n"], "mean", st.get("mean"), "med", st.get("median"), "max", st.get("max"), "sum_s", res["sets"][name]["total_sentence_end_pause_s"], "dur", res["sets"][name]["total_dur_s"])
    # sensitivity -35/-45 for the key sets
    sens = {}
    for name in ("v5/v4 Adv FS (P8 new take)", "PD8 Trial take (=v3 Adv)", "F5 Adv FS (final_v2)"):
        for thr in (-35.0, -45.0):
            allp = [q["pause_ms"] for p in SETS[name][0] for q in analyze(p, thr)["sentence_end_pauses"]]
            sens[f"{name}@{thr}"] = {"mean": round(float(np.mean(allp))), "median": round(float(np.median(allp))), "max": int(max(allp))}
    res["sensitivity"] = sens
    json.dump(res, open(os.path.join(OUT, "sentence_end_pause_stats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
