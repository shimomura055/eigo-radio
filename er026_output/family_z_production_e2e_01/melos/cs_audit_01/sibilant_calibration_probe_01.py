"""CS audit: sibilant境界の持続時間キャリブレーション(offline、無料、read-only、API 0)。
run_e2e_02の既存narration wav(canonical既知)から、語境界を (A) 's'終わり語+'s'始まり語 (geminate候補) と
(B) 非's'終わり語+'s'始まり語 (単独/s/対照) に分け、境界付近の最長摩擦区間(ms)の分布を比べる。
Melos said.の測定値が、(A)の分布に近いか(B)に近いかを見る。粗い研究用指標(Productionでは使わない)。
語境界はlocal faster-whisper small(word timestamp)。ASR語数==canonical語数のclipのみ採用(index対応)。"""
import json, sys, os, re, glob, wave
import numpy as np
sys.path.insert(0, ".")
import er008_disfluency_qa_18 as dq
R = "er026_output/family_z_production_e2e_01/melos/run_e2e_02"
def load(p):
    w = wave.open(p); sr = w.getframerate(); n = w.getnframes(); ch = w.getnchannels()
    x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1: x = x.reshape(-1, ch).mean(1)
    return x, sr
def frames(x, sr, hop=0.005, win=0.02):
    H = int(sr * hop); W = int(sr * win); out = []
    hann = np.hanning(W); f = np.fft.rfftfreq(W, 1 / sr)
    for i in range(0, len(x) - W, H):
        seg = x[i:i + W] * hann; sp = np.abs(np.fft.rfft(seg)) ** 2
        out.append((sp[f >= 4000].sum() / (sp.sum() + 1e-12), np.sqrt((seg ** 2).mean())))
    return np.array(out), H / sr
def longest_run(fr, hop, t0, t1, mx):
    fric = (fr[:, 0] > 0.5) & (fr[:, 1] > 0.05 * mx)
    best = cur = 0
    for i in range(max(0, int(t0 / hop)), min(len(fric), int(t1 / hop))):
        cur = cur + 1 if fric[i] else 0
        best = max(best, cur)
    return best * hop * 1000
def toks(t): return re.findall(r"[A-Za-z']+", t)
rows = []
for lv, sfx in (("a2", "_original"), ("b1b", "")):
    plan = json.load(open(f"{R}/segment_plan_{lv}.json", encoding="utf-8"))
    clips = [c for v in plan.values() if isinstance(v, list) for c in v if isinstance(c, dict) and c.get("id", "").startswith("full_story_part")]
    for c in clips:
        wav = f"{R}/{lv}/narration/{c['id']}{sfx}.wav"
        if not os.path.exists(wav): continue
        ct = toks(c["text"])
        if len(ct) < 3: continue
        # 候補境界が無ければASRを回さない
        pairs = [(i, i + 1) for i in range(len(ct) - 1) if ct[i + 1].lower().startswith("s") and not ct[i + 1].lower().startswith(("sh",))]
        if not pairs: continue
        ws = dq.transcribe_verbatim(wav, language="en", model_size="small")
        wt = [re.sub(r"[^a-z']", "", w["text"].lower()) for w in ws]
        if len(wt) != len(ct) or any(a != b.lower() for a, b in zip(wt, ct)):
            # canonicalと完全一致しないclipは境界位置が不確実なので除外
            if len(wt) != len(ct): continue
        x, sr = load(wav); fr, hop = frames(x, sr); mx = fr[:, 1].max()
        for i, j in pairs:
            end_i, st_j = ws[i]["end"], ws[j]["start"]
            kind = "A_s_then_s" if ct[i].lower().endswith("s") and not ct[i].lower().endswith("ss") or ct[i].lower().endswith("ss") else "B_nons_then_s"
            kind = "A_s_then_s" if ct[i].lower().endswith("s") else "B_nons_then_s"
            run = longest_run(fr, hop, end_i - 0.15, st_j + 0.35, mx)
            rows.append({"lv": lv, "clip": c["id"], "w1": ct[i], "w2": ct[j], "kind": kind, "run_ms": round(run), "w1_end": round(end_i, 2), "w2_start": round(st_j, 2)})
            print(rows[-1], flush=True)
json.dump(rows, open(os.path.join(os.path.dirname(__file__), "sibilant_calibration_probe_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k in ("A_s_then_s", "B_nons_then_s"):
    v = [r["run_ms"] for r in rows if r["kind"] == k]
    if v: print(k, "n=%d mean=%.0f median=%.0f min=%d max=%d" % (len(v), np.mean(v), np.median(v), min(v), max(v)))
