"""CS audit: 「X said」境界のsibilant(摩擦音)連続区間長の音響プローブ(offline・無料・read-only)。
目的: 'Melos said'のsibilant融合(geminate /s s/)が音声に実在するか、対照('he said ...')より長い摩擦区間があるかを見る。
高域(>=4kHz)エネルギー比が高いフレームを摩擦音フレームとし、'said'語頭付近の最長連続区間を測る。
注意: 研究用の粗い指標。Production判定には使わない。"""
import json, sys, wave, os
import numpy as np
base = "er026_output/family_z_production_e2e_01/melos/run_e2e_02"
cases = [
 ("a2_part1_c5_final(slowed)", "a2/narration/full_story_part1_c5.wav", "said"),
 ("a2_part1_c5_original", "a2/narration/full_story_part1_c5_original.wav", "said"),
 ("a2_part1_c5_att1", "a2/narration/attempts/full_story_part1_c5_attempt1_customadfcf33f.wav", "said"),
 ("a2_part1_c5_att2", "a2/narration/attempts/full_story_part1_c5_attempt2_customadfcf33f.wav", "said"),
 ("a2_part1_c5_att3_minfb", "a2/narration/attempts/full_story_part1_c5_attempt3_minimalfallback.wav", "said"),
 ("b1b_part1_c5", "b1b/narration/full_story_part1_c5.wav", "said"),
 ("CTRL a2_part3_c5 'he said softly.'", "a2/narration/full_story_part3_c5.wav", "said"),
 ("CTRL b1b_part3_c9 'he said at last.'", "b1b/narration/full_story_part3_c9.wav", "said"),
]
sys.path.insert(0, ".")
import er008_disfluency_qa_18 as dq
def load(p):
    w = wave.open(p); sr = w.getframerate(); n = w.getnframes(); ch = w.getnchannels()
    x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1: x = x.reshape(-1, ch).mean(1)
    return x, sr
def hf_ratio(x, sr, hop=0.005, win=0.02):
    H = int(sr * hop); W = int(sr * win); fr = []
    for i in range(0, len(x) - W, H):
        seg = x[i:i + W] * np.hanning(W)
        sp = np.abs(np.fft.rfft(seg)) ** 2; f = np.fft.rfftfreq(W, 1 / sr)
        tot = sp.sum() + 1e-12
        fr.append((sp[f >= 4000].sum() / tot, np.sqrt((seg ** 2).mean())))
    return np.array(fr), H / sr
out = []
for name, rel, target in cases:
    p = f"{base}/{rel}"
    if not os.path.exists(p): out.append({"case": name, "missing": True}); continue
    x, sr = load(p)
    words = dq.transcribe_verbatim(p, language="en", model_size="small")
    tw = [w for w in words if w["text"].strip().lower().strip(".,") == target]
    fr, hop = hf_ratio(x, sr)
    mx = fr[:, 1].max()
    fric = (fr[:, 0] > 0.5) & (fr[:, 1] > 0.05 * mx)
    ws = float(tw[0]["start"]) if tw else None
    lo = max(0, int(((ws or 0) - 0.25) / hop)); hi = int(((ws or 0) + 0.45) / hop)
    best = (0, None); cur = 0; st = None
    for i in range(lo, min(hi, len(fric))):
        if fric[i]:
            if cur == 0: st = i
            cur += 1
            if cur > best[0]: best = (cur, st)
        else: cur = 0
    out.append({"case": name, "sr": sr, "dur_s": round(len(x) / sr, 2), "said_start_s": ws,
                "longest_fricative_run_ms_near_said": round(best[0] * hop * 1000), "run_start_s": round(best[1] * hop, 3) if best[1] is not None else None})
    print(out[-1], flush=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "sibilant_duration_probe_01.json"), "w"), ensure_ascii=False, indent=1)
