# formant_01.py -- 保存wav(8 attempt)で 'gacha' 第1母音が /ɑ/(AA, gotcha型)か /æ/(AE, gatcha型)かを、同一音声内の既知語(AA/AEの基準語)とのF1/F2比較で推定する。
# 証拠の種類=間接(LPC推定のF2。AIは耳確認不可)。API 0。 基準語は CMU の第1強勢母音で選ぶ。
import json, sys, numpy as np, soundfile as sf
sys.path.insert(0, ".")
from scipy.signal import resample_poly, lfilter
from scipy.linalg import solve_toeplitz
from faster_whisper import WhisperModel
import pronouncing
base = "er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/b1b/narration/attempts/"
model = WhisperModel("small", device="cpu", compute_type="int8")
def formants(frame, sr, order=14):
    x = frame * np.hamming(len(frame)); x = lfilter([1, -0.97], 1, x)
    r = np.correlate(x, x, "full")[len(x) - 1:len(x) + order]
    if r[0] < 1e-9: return None
    a = solve_toeplitz(r[:order], -r[1:order + 1]); a = np.concatenate(([1], a))
    roots = [z for z in np.roots(a) if np.imag(z) > 0.01]
    fr = sorted(np.angle(z) * sr / (2 * np.pi) for z in roots if -np.log(abs(z)) * sr / np.pi < 400)
    fr = [f for f in fr if 200 < f < 3500]
    return fr[:3] if len(fr) >= 2 else None
def vowel_f(y, sr, t0, t1):
    out = []
    for t in np.arange(t0, t1 - 0.025, 0.01):
        fr = formants(y[int(t * sr):int((t + 0.03) * sr)], sr)
        if fr: out.append(fr[:2])
    return np.median(np.array(out), axis=0) if len(out) >= 3 else None
def first_vowel(w):
    ph = pronouncing.phones_for_word(w.lower())
    if not ph: return None
    for p in ph[0].split():
        if p[-1].isdigit() and p[-1] in "12": return p[:-1]
    return None
res = {}
for n in range(1, 9):
    p = base + f"full_story_part3_attempt{n}_englishstyleprefixwidemargin.wav"
    y, sr = sf.read(p); y = y[:, 0] if y.ndim > 1 else y
    y16 = resample_poly(y, 16000, sr) if sr != 16000 else y
    segs, _ = model.transcribe(p, language="en", word_timestamps=True)
    words = [(w.word.strip().strip(".,?!\"'").lower(), w.start, w.end) for s in segs for w in s.words]
    cls = {"AA": [], "AE": [], "AO": [], "EH": []}; g = None
    for w, s, e in words:
        if w in ("gotcha", "gacha"): g = vowel_f(y16, 16000, s + 0.05, min(e, s + 0.22)); continue
        v = first_vowel(w)
        if v in cls and e - s > 0.2:
            f = vowel_f(y16, 16000, s + 0.04, min(e, s + 0.25))
            if f is not None: cls[v].append(f)
    cen = {k: (np.median(np.array(v), axis=0).round(0).tolist(), len(v)) for k, v in cls.items() if v}
    res[n] = {"gacha_F1F2": None if g is None else g.round(0).tolist(), "ref": cen}
    print(n, "gacha F1,F2 =", res[n]["gacha_F1F2"], "| refs (median F1,F2; n):", cen)
json.dump(res, open("docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/work/formant_01.json", "w"), indent=1)
