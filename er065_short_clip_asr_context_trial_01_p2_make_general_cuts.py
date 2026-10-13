# -*- coding: utf-8 -*-
"""委任_03 B/D: 『一般語』の語境界(子音連続の型別)を既存Production音声から2語窓で切り出す(オフライン無料)。
Melos(OOV固有名詞)と一般語で、s+s等の融合境界が2語短尺でどれだけASR誤認(不一致)を起こすかを、対照(非融合境界)と並べるため。
型: SS(s/z+s/z) / TT(t+t) / DD(d+d) / NN(n+n) / YOD(t,d,s,z + y) / SHS(s,z + sh/ch/jh) / CTRL(融合しない子音+子音 or 子音+母音)。"""
import glob, json, os, random, sys, wave, difflib
sys.path.insert(0, ".")
import er065_short_clip_asr_context_trial_01_lib as L
import er065_short_clip_asr_context_trial_01_p2_phon as P
OUT = "er065_output/short_clip_asr_context_trial_01/phase2"
CUTD = OUT + "/g_cuts"
os.makedirs(CUTD, exist_ok=True)
L.install_write_guard([OUT])
N_PER = 8
items = {}
def walk(d):
    if isinstance(d, dict):
        if isinstance(d.get("text"), str) and isinstance(d.get("path"), str) and d["path"].endswith(".wav"):
            items.setdefault(d["path"], d["text"]); return
        for v in d.values(): walk(v)
    elif isinstance(d, list):
        for v in d: walk(v)
for f in glob.glob("**/tts_generation_results.json", recursive=True):
    if ".venv" in f: continue
    try: walk(json.load(open(f, encoding="utf-8")))
    except Exception: pass
def typ(f, i, w1, w2):
    if f in ("S", "Z") and i in ("S", "Z"): return "SS"
    if f == "T" and i == "T": return "TT"
    if f == "D" and i == "D": return "DD"
    if f == "N" and i == "N": return "NN"
    if f in ("T", "D", "S", "Z") and i == "Y": return "YOD"
    if (f in ("S", "Z") and i in P.SIBILANT_PAL) or (f in P.SIBILANT_PAL and i in ("S", "Z")): return "SHS"
    if f not in P.VOWELS and i not in P.VOWELS and f != i and P.boundary_type(f, i) is None and f not in ("S", "Z", "T", "D", "N") and i not in ("S", "Z", "T", "D", "N", "Y"): return "CTRL"
    return None
cands = {}
rng = random.Random(11)
paths = [p for p in items if os.path.exists(p)]
rng.shuffle(paths)
for p in paths:
    t = items[p]
    if any(ord(c) > 0x3000 for c in t): continue
    with wave.open(p) as w: dur = w.getnframes() / w.getframerate()
    if dur > 25 or dur < 2: continue
    tk = P.tokens(t)
    for k in range(len(tk) - 1):
        a = P.phones_all(tk[k]); b = P.phones_all(tk[k + 1])
        if not a or not b: continue
        ty = typ(a[0][0][-1], b[0][0][0], tk[k], tk[k + 1])
        if ty and len(tk[k]) >= 2 and len(tk[k + 1]) >= 2:
            cands.setdefault(ty, []).append((p, k))
sel = {}
used_clips = set()
for ty in ("SS", "TT", "DD", "NN", "YOD", "SHS", "CTRL"):
    lst = cands.get(ty, [])
    rng.shuffle(lst)
    sel[ty] = []
    for p, k in lst:
        if p in used_clips: continue
        sel[ty].append((p, k)); used_clips.add(p)
        if len(sel[ty]) >= N_PER + 5: break
print({t: (len(cands.get(t, [])), len(sel[t])) for t in sel})
import difflib
targets, meta = [], []
cache = {}
for ty in sel:
    got = 0
    for p, k in sel[ty]:
        if got >= N_PER: break
        t = items[p]; ct = P.tokens(t)
        r = L.whisper_asr(p, "small")
        ws = [w for w in r["words"] if P.tokens(w["w"])]
        wtok = ["".join(P.tokens(w["w"])) for w in ws]
        sm = difflib.SequenceMatcher(a=ct, b=wtok, autojunk=False)
        mp = {}
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for dd in range(i2 - i1): mp[i1 + dd] = j1 + dd
        if k not in mp or (k + 1) not in mp or mp[k + 1] != mp[k] + 1: continue
        a, b = mp[k], mp[k + 1]
        t0 = max(ws[a - 1]["end"] if a > 0 else 0.0, ws[a]["start"] - 0.05)
        t1 = (ws[b + 1]["start"] - 0.005) if b + 1 < len(ws) else ws[b]["end"] + 0.25
        if t1 - t0 < 0.3: continue
        x = L.read_wav_mono(p, 24000)
        seg = x[int(t0 * 24000):int(t1 * 24000)]
        cid = f"g_{ty}_{got:02d}"
        outp = f"{CUTD}/{cid}.wav"
        L.write_wav(outp, seg)
        cased = [w for w in __import__("re").findall(r"[A-Za-z0-9']+", t.replace("’", "'"))]
        canon = f"{cased[k]} {cased[k + 1]}" if len(cased) == len(ct) else f"{ct[k]} {ct[k+1]}"
        targets.append({"id": cid, "path": outp, "pool": "x", "canonical": canon, "focus_word": ct[k], "voice": None, "model": None,
                        "note": f"{ty} {os.path.basename(os.path.dirname(os.path.dirname(p)))[-30:]}", "category": ty})
        meta.append({"id": cid, "type": ty, "src_wav": p, "k": k, "canonical": canon, "dur": round(t1 - t0, 3), "words_asr": [ws[a]["w"], ws[b]["w"]]})
        got += 1
cfg = {"work_id": "general_words_prod_audio", "group": "p2_general", "focus_word": "", "target_canonical": "", "gap_ms": 300,
       "pools": {"x": {"slots": {}, "clips": {}}}, "targets": targets,
       "recipes": [{"id": "R00_alone", "pre": [], "post": [], "kind": "alone"}], "targets_recipes": {}}
json.dump(cfg, open(OUT + "/config_general_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(meta, open(OUT + "/g_cuts_meta_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import collections
print(collections.Counter(m["type"] for m in meta), len(targets))
