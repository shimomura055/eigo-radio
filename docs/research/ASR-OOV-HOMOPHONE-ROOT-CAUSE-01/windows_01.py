# windows_01.py -- 保存wav(Adv full_story_part3 の8 attempt)から gacha/gotcha 発話窓を切り出す(ローカルfaster-whisper small、API 0)。
import json, os, sys, wave
sys.path.insert(0, ".")
import numpy as np, soundfile as sf
from faster_whisper import WhisperModel
base = "er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/b1b/narration/attempts/"
out_dir = "docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/work/windows"; os.makedirs(out_dir, exist_ok=True)
model = WhisperModel("small", device="cpu", compute_type="int8")
res = {}
for n in range(1, 9):
    p = base + f"full_story_part3_attempt{n}_englishstyleprefixwidemargin.wav"
    segs, _ = model.transcribe(p, language="en", word_timestamps=True, beam_size=5)
    words = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
    hit = [w for w in words if w[0].lower().strip(".,?!'\"") in ("gotcha", "gacha", "gotta", "gatcha", "gocha")]
    full = " ".join(w[0] for w in words)
    res[n] = {"hit": hit, "snippet": " ".join(w[0] for w in words if hit and hit[0][1] - 4 < w[1] < hit[0][2] + 3)}
    print(n, hit, "|", res[n]["snippet"])
    if hit:
        y, sr = sf.read(p)
        if y.ndim > 1: y = y[:, 0]
        t0 = max(0, hit[0][1] - 3.5); t1 = min(len(y) / sr, hit[0][2] + 2.5)
        sf.write(os.path.join(out_dir, f"att{n}_win.wav"), y[int(t0 * sr):int(t1 * sr)], sr)
        res[n]["win"] = [round(t0, 2), round(t1, 2)]
json.dump(res, open("docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/work/windows_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
