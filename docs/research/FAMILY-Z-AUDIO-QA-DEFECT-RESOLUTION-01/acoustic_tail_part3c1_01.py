# 委任_01(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01): 既存wavの「Melos」語末区間の簡易音響指標(API 0、ローカルfaster-whisper=無料、numpy/scipy既存)。
# 目的: 語末に歯擦音(s/z)エネルギーが存在するか、有声性(z的な低域周期性)があるかをattempt間・run_03 PASS版と比較する。
# 実行: .venv\Scripts\python.exe -X utf8 <this file> --out <json>   (cwd=repo root)
import sys, os, json, argparse, re
sys.path.insert(0, os.getcwd())
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt
import er008_disfluency_qa_18 as dq

B = "er026_output/family_z_production_e2e_01/melos"
WAVS = {
 "run04_att1": f"{B}/run_e2e_04/a2/narration/attempts/full_story_part3_c1_attempt1_customa3c4625e.wav",
 "run04_att2": f"{B}/run_e2e_04/a2/narration/attempts/full_story_part3_c1_attempt2_customa3c4625e.wav",
 "run04_att3": f"{B}/run_e2e_04/a2/narration/attempts/full_story_part3_c1_attempt3_minimalfallback.wav",
 "run03_att1_PASS_pre_slowdown": f"{B}/run_e2e_03/a2/narration/attempts/full_story_part3_c1_attempt1_customa3c4625e.wav",
 "run03_final_PASS_post_slowdown": f"{B}/run_e2e_03/a2/narration/full_story_part3_c1.wav",
}
def band(x, sr, lo, hi):
    hi = min(hi, sr / 2 * 0.98)
    sos = butter(4, [lo, hi], btype="band", fs=sr, output="sos")
    return sosfiltfilt(sos, x)
def rms(x):
    return float(np.sqrt(np.mean(np.square(x)) + 1e-12))
def db(x):
    return float(20 * np.log10(x + 1e-9))
def seg_metrics(x, sr):
    if len(x) < int(0.01 * sr):
        return None
    hf = rms(band(x, sr, 4000, 10000)); lf = rms(band(x, sr, 80, 500)); full = rms(x)
    # 有声性: 自己相関ピーク(80-400Hzのlag範囲)の正規化値
    y = x - np.mean(x); ac = np.correlate(y, y, "full")[len(y) - 1:]
    ac = ac / (ac[0] + 1e-12)
    lo, hi = int(sr / 400), min(int(sr / 80), len(ac) - 1)
    per = float(np.max(ac[lo:hi])) if hi > lo else None
    return {"dur_ms": round(1000 * len(x) / sr, 1), "rms_db": round(db(full), 1), "hf4_10k_db": round(db(hf), 1),
            "lf80_500_db": round(db(lf), 1), "hf_minus_lf_db": round(db(hf) - db(lf), 1), "autocorr_periodicity": None if per is None else round(per, 3)}

def fricative_runs(x, sr, t0, t1, hop=0.01, win=0.025):
    """[t0,t1]秒を10ms刻みで走査し、歯擦音様フレーム(4-10kHz > 80-500Hz かつ自己相関周期性<0.4=無声)の連続区間と、
    有声性の近似(同区間の低域80-500Hz rmsの対全帯域比)を返す。簡易指標=診断用で、合否根拠にしない。"""
    hfs = band(x, sr, 4000, 10000); lfs = band(x, sr, 80, 500)
    frames = []
    t = t0
    while t + win <= t1:
        a, b = int(t * sr), int((t + win) * sr)
        f = x[a:b]; h = rms(hfs[a:b]); l = rms(lfs[a:b]); fr = rms(f)
        y = f - np.mean(f); ac = np.correlate(y, y, "full")[len(y) - 1:]; ac = ac / (ac[0] + 1e-12)
        lo, hi = int(sr / 400), min(int(sr / 80), len(ac) - 1)
        per = float(np.max(ac[lo:hi])) if hi > lo else 0.0
        frames.append((round(t, 3), db(fr), db(h), db(l), per, (db(h) - db(l)) > 0 and per < 0.4 and db(h) > -45))
        t += hop
    runs, cur = [], []
    for fm in frames + [(None, 0, 0, 0, 0, False)]:
        if fm[5]: cur.append(fm)
        else:
            if cur: runs.append(cur); cur = []
    res = []
    for r in runs:
        res.append({"start": r[0][0], "end": round(r[-1][0] + win, 3), "dur_ms": round(1000 * (r[-1][0] + win - r[0][0]), 0),
                    "mean_hf_db": round(float(np.mean([q[2] for q in r])), 1), "mean_lf_db": round(float(np.mean([q[3] for q in r])), 1),
                    "mean_periodicity": round(float(np.mean([q[4] for q in r])), 3)})
    return res

def find_name_word(words):
    """'rock' の次の語(Melos相当)とその次語(drank相当)"""
    toks = [re.sub(r"[^a-z]", "", w["text"].lower()) for w in words]
    for i, t in enumerate(toks):
        if t == "rock" and i + 2 < len(words):
            return i + 1, i + 2
    return None, None
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
out = {"engine": "faster-whisper small local (free), word_timestamps; numpy/scipy DSP", "wavs": {}}
for k, p in WAVS.items():
    x, sr = sf.read(p, dtype="float32")
    if x.ndim > 1: x = x.mean(axis=1)
    words = dq.transcribe_verbatim(p, language="en")
    i, j = find_name_word(words)
    rec = {"path": p, "sr": sr, "words_around": [(w["text"], round(w["start"], 2), round(w["end"], 2)) for w in words[max(0, (i or 5) - 2):(j or 8) + 3]]}
    if i is not None:
        w1, w2 = words[i], words[j]
        s, e = int(w1["start"] * sr), int(w1["end"] * sr)
        word = x[s:e]
        tail = x[max(s, e - int(0.12 * sr)):e]
        gap = x[e:int(w2["start"] * sr)] if w2["start"] > w1["end"] else x[e:e]
        vowel = x[s + int(0.35 * (e - s)):s + int(0.6 * (e - s))]
        rec.update({"name_word_whisper": w1["text"], "name_word_start_end": [round(w1["start"], 3), round(w1["end"], 3)], "next_word": w2["text"],
                    "whole_word": seg_metrics(word, sr), "last120ms": seg_metrics(tail, sr), "mid_vowel_ref": seg_metrics(vowel, sr),
                    "gap_to_next": seg_metrics(gap, sr),
                    "fricative_runs_name_to_next_end": fricative_runs(x, sr, w1["start"], w2["end"] + 0.15)})
    out["wavs"][k] = rec
    print(k, rec.get("name_word_whisper"), rec.get("last120ms"))
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
