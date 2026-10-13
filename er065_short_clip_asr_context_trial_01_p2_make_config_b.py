# -*- coding: utf-8 -*-
"""委任_03 B: 「長さ vs s+s融合」分離用の既存音声切出し(オフライン無料)とbuild用config生成。
既存Melos clip(a2/b1b)から、Melosの後ろがs始まりでない語(called/turned/had/listened/fell)を
word timestamp(local whisper small)で2語に切り出した短尺clip と、それを含む元clip全体をtargetにする。
加えて『1文単位』検証として、Melos said. 全7 take を直前の台詞clip(Rpre/Rboth相当)と短gap(80ms)で結合したconfigも作る。"""
import json, os, sys, re
sys.path.insert(0, ".")
import er065_short_clip_asr_context_trial_01_lib as L
import er065_short_clip_asr_context_trial_01_p2_phon as P
OUT = "er065_output/short_clip_asr_context_trial_01/phase2"
SRC = "er065_output/short_clip_asr_context_trial_01/audio_src/"
VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
os.makedirs(OUT + "/b_cuts" + ("" if VER == "v1" else "_" + VER), exist_ok=True)
L.install_write_guard([OUT])

def clip_path(level, cid):
    base = SRC + f"{level}_narration/{cid}"
    return base + "_original.wav" if os.path.exists(base + "_original.wav") else base + ".wav"

# (id, clip, word index range [w0,w1] inclusive, canonical)  ※word indexはトークン(P.tokens)基準
CUTS = [
    ("called2", "full_story_part1_c1", (0, 1), "Melos called."),
    ("turned2", "full_story_part1_c9", (0, 1), "Melos turned."),
    ("had2", "full_story_part1_c9", None, "Melos had."),     # 2文目 'Melos had' (最初の 'had' 直前のMelos)
    ("listened2", "full_story_part1_c11", None, "Melos listened."),
    ("fell2", "full_story_part3_c3", None, "Melos fell."),
]
WHOLE = [("c1whole", "full_story_part1_c1", "Melos called across the hall,"),
         ("p3c3whole", "full_story_part3_c3", "His friend turned around, and Melos fell against him.")]
targets = []
meta = []
for level in ("a2", "b1b"):
    plan = json.load(open(SRC + f"segment_plan_{level}.json", encoding="utf-8"))
    texts = {c["id"]: c["text"].replace("“", "").replace("”", "").replace('"', "").strip() for c in plan["clips"]}
    voice_model = {"a2": ("Aoede", "gemini-3.8-flash-lite-tts"), "b1b": ("Aoede", "gemini-3.8-flash-lite-tts")}[level]
    for tid, cid, rng, canon in CUTS:
        p = clip_path(level, cid)
        r = L.whisper_asr(p, "small")
        ws = [w for w in r["words"] if P.tokens(w["w"])]
        toks = [" ".join(P.tokens(w["w"])) for w in ws]
        ct = P.tokens(texts[cid])
        if len(toks) != len(ct):
            meta.append({"level": level, "cut": tid, "skipped": "word_mismatch", "asr": toks, "text": ct}); continue
        if rng is None:
            nxt = canon.lower().strip(".").split()[1]
            idx = [i for i in range(len(ct) - 1) if ct[i] == "melos" and ct[i + 1] == nxt]
            if not idx: meta.append({"level": level, "cut": tid, "skipped": "pair_not_found"}); continue
            rng = (idx[0], idx[0] + 1)
        a, b = rng
        if ct[b] != canon.lower().strip(".").split()[1]:
            meta.append({"level": level, "cut": tid, "skipped": "second_word_differs_in_this_level", "text_words": [ct[a], ct[b]]}); continue
        if VER == "v1":
            t0 = max(0.0, ws[a]["start"] - 0.03); t1 = ws[b]["end"] + 0.06
        else:
            # v2: 語末(-edなど)の切れを避けるため、終端は次語の開始直前(無ければ語末+0.25秒)、始端は前語の終端直後
            t0 = max(ws[a - 1]["end"] if a > 0 else 0.0, ws[a]["start"] - 0.05)
            t1 = (ws[b + 1]["start"] - 0.005) if b + 1 < len(ws) else ws[b]["end"] + 0.25
        x = L.read_wav_mono(p, 24000)
        seg = x[int(t0 * 24000):int(t1 * 24000)]
        outp = f"{OUT}/b_cuts{'' if VER == 'v1' else '_' + VER}/{level}_{tid}.wav"
        L.write_wav(outp, seg)
        targets.append({"id": f"{level}_{tid}", "path": outp, "pool": "x", "canonical": canon, "focus_word": "Melos",
                        "voice": voice_model[0], "model": voice_model[1], "note": f"cut {cid} words {a}-{b} of '{texts[cid][:40]}'",
                        "category": "length_vs_ss_cut"})
        meta.append({"level": level, "cut": tid, "src": cid, "words": [toks[a], toks[b]], "t0": round(t0, 3), "t1": round(t1, 3),
                     "dur": round(t1 - t0, 3)})
    for tid, cid, canon in (WHOLE if VER == "v1" else []):
        p = clip_path(level, cid)
        canon = texts[cid]
        targets.append({"id": f"{level}_{tid}", "path": p, "pool": "x", "canonical": canon, "focus_word": "Melos",
                        "voice": voice_model[0], "model": voice_model[1], "note": f"whole {cid}", "category": "length_vs_ss_whole"})
        meta.append({"level": level, "cut": tid, "src": cid, "whole": True, "dur": round(L.wav_duration(p), 3)})
cfg = {"work_id": "family_z_melos_run_e2e_02", "group": "p2_len" if VER == "v1" else "p2_len_" + VER, "focus_word": "Melos", "target_canonical": "Melos called.",
       "gap_ms": 300, "pools": {"x": {"slots": {}, "clips": {}}}, "targets": targets,
       "recipes": [{"id": "R00_alone", "pre": [], "post": [], "kind": "alone"}], "targets_recipes": {}}
json.dump(cfg, open(OUT + ("/config_len_02.json" if VER == "v1" else f"/config_len_{VER}_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(meta, open(OUT + ("/b_cuts_meta_02.json" if VER == "v1" else f"/b_cuts_meta_{VER}_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 1文単位(短gap): 直前の台詞clip(c4)+target / target+c6 / c4+target+c6 を80ms gapで結合
old = json.load(open("er065_output/short_clip_asr_context_trial_01/config_melos_01.json", encoding="utf-8"))
cfg2 = dict(old)
cfg2["group"] = "p2_sentence80"
cfg2["gap_ms"] = 80
cfg2["recipes"] = [r for r in old["recipes"] if r["id"] in ("Rpre", "Rpost", "Rboth")]
if VER == "v1": json.dump(cfg2, open(OUT + "/config_sentence80_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(meta, ensure_ascii=False)[:2500])
print(len(targets), "targets; blocked(tmp only expected):", len(L.write_guard_report()["blocked_write_attempts"]))
