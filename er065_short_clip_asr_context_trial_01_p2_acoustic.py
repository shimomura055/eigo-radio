# -*- coding: utf-8 -*-
"""委任_03 C/D: 歯擦音境界の摩擦区間長の較正(Trial専用の補助的な独立証拠候補、Productionでは使わない)。
既存Production音声(canonical既知)を local faster-whisper small(無料CPU)で語境界推定し、
A=S/Z終わり+S/Z始まり(geminate/融合候補) / B=非歯擦音終わり+S始まり(語頭単独s) / C=S/Z終わり+非歯擦音始まり(語末単独s)
の境界を横切る連続摩擦区間(高域比>0.5 & 振幅>0.05*max、5msフレーム)の長さ(ms)を測る。ASR API呼出なし(費用0)。
出力は inventory(acoustic_ss_clip_inventory_02.json)を読み、incremental JSONL に追記する(再開可)。"""
import json, os, sys, random, wave, time
import numpy as np
sys.path.insert(0, ".")
import er065_short_clip_asr_context_trial_01_lib as L
import er065_short_clip_asr_context_trial_01_p2_phon as P

OUT = "er065_output/short_clip_asr_context_trial_01/phase2"
RES = OUT + "/acoustic_ss_probe_02b.jsonl"
MAXCLIPS = int(sys.argv[1]) if len(sys.argv) > 1 else 220

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

def run_across(fr, hop, t0, t1, mx, th=0.5):
    """[t0,t1]に重なる連続摩擦区間のうち最長のもの(区間全体の長さ、窓外へ延びる分も含む)"""
    fric = (fr[:, 0] > th) & (fr[:, 1] > 0.03 * mx)
    a, b = max(0, int(t0 / hop)), min(len(fric), int(t1 / hop))
    best = 0
    i = 0
    n = len(fric)
    while i < n:
        if fric[i]:
            j = i
            while j < n and fric[j]: j += 1
            if j > a and i < b: best = max(best, j - i)
            i = j
        else:
            i += 1
    return best * hop * 1000

def main():
    inv = json.load(open(OUT + "/acoustic_ss_clip_inventory_02.json", encoding="utf-8"))
    done = set()
    if os.path.exists(RES):
        for l in open(RES, encoding="utf-8"):
            try: done.add(json.loads(l)["wav"])
            except Exception: pass
    cands = []
    for p, d in inv.items():
        with wave.open(p) as w: dur = w.getnframes() / w.getframerate()
        if dur <= 45: cands.append((p, d, dur))
    random.Random(7).shuffle(cands)
    cands = cands[:MAXCLIPS]
    print("clips", len(cands), flush=True)
    t0 = time.time()
    for ci, (p, d, dur) in enumerate(cands):
        if p in done: continue
        if os.path.exists(OUT + "/STOP"): print("STOP sentinel"); break
        ct = P.tokens(d["text"])
        r = L.whisper_asr(p, "small")
        wt = [" ".join(P.tokens(w["w"])) for w in r["words"]]
        wt = [w for w in wt if w]
        rec = {"wav": p, "text": d["text"], "dur": round(dur, 2), "n_words_asr": len(wt), "n_words_text": len(ct), "rows": []}
        import difflib
        ws = [w for w in r["words"] if P.tokens(w["w"])]
        # whisper語(各語は1トークン想定、複数トークン語は結合)と text トークンを difflib で整列し、equalブロックの語だけ使う
        wtok = []
        for w in ws:
            tk = P.tokens(w["w"])
            wtok.append("".join(tk))
        ctj = ct
        sm = difflib.SequenceMatcher(a=ctj, b=wtok, autojunk=False)
        mp = {}
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for dd in range(i2 - i1): mp[i1 + dd] = j1 + dd
        rec["n_equal_words"] = len(mp)
        rec["words"] = [{"w": w["w"], "start": round(w["start"], 3), "end": round(w["end"], 3)} for w in ws]
        x, sr = load(p); fr, hop = frames(x, sr); mx = fr[:, 1].max()
        for k in range(len(ct) - 1):
            if k not in mp or (k + 1) not in mp or mp[k + 1] != mp[k] + 1: continue
            a = P.phones_all(ct[k]); b = P.phones_all(ct[k + 1])
            if not a or not b: continue
            f, i = a[0][0][-1], b[0][0][0]
            if f in P.SIBILANT_ALV and i in P.SIBILANT_ALV: kind = "A_ss"
            elif f not in P.SIBILANT_ALV and f not in P.SIBILANT_PAL and i == "S" and ct[k + 1].startswith("s"): kind = "B_single_initial_s"
            elif f in P.SIBILANT_ALV and i not in P.SIBILANT_ALV and i not in P.SIBILANT_PAL and ct[k].endswith("s"): kind = "C_single_final_s"
            else: continue
            e, s_ = ws[mp[k]]["end"], ws[mp[k + 1]]["start"]
            runs = {str(th): round(run_across(fr, hop, e - 0.04, s_ + 0.04, mx, th)) for th in (0.3, 0.4, 0.5)}
            rec["rows"].append({"k": k, "w1": ct[k], "w2": ct[k + 1], "kind": kind, "f": f, "i": i, "run_ms": runs["0.5"], "runs": runs,
                                "gap_ms": round((s_ - e) * 1000), "w1_dur_ms": round((ws[mp[k]]["end"] - ws[mp[k]]["start"]) * 1000),
                                "w2_dur_ms": round((ws[mp[k + 1]]["end"] - ws[mp[k + 1]]["start"]) * 1000)})
        with open(RES, "a", encoding="utf-8") as fh: fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(ci, os.path.basename(p), len(rec["rows"]), rec.get("skipped"), round(time.time() - t0), flush=True)

if __name__ == "__main__":
    main()
