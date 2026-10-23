# -*- coding: utf-8 -*-
"""FZSPAB 委任_02 Advanced: 会話clipのみ atempo=1.06(ピッチ保持、er008 apply_a2_slowdownを係数のみ変えて再利用)。API 0。
A_rebuild(b1b未変更clipの再組立)==Production b1b wav sha一致でB側組立経路の同一性を担保。usage: build_adv_01.py <melos|open_window>"""
import hashlib, json, os, shutil, sys
ROOT = "C:/Users/tensh/eigo-radio"; os.chdir(ROOT); sys.path.insert(0, ROOT)
BASE = "er026_output/family_z_production_e2e_01"
SRC = {"melos": f"{BASE}/melos/run_e2e_06", "open_window": f"{BASE}/the_open_window/run_e2e_01"}
SLUG = {"melos": "melos", "open_window": "the_open_window"}
OUT = "er026_output/family_z_std_dialogue_speed_ab_01/adv"
SPEEDUP = 1.06
SLOWDOWN_PCT = (1.0 / SPEEDUP - 1.0) * 100.0   # 負値 -> er008のtempo=1/(1+pct/100)=1.06
def sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()
def rj(p): return json.load(open(p, encoding="utf-8"))
def prep(story, variant):
    src = SRC[story]; dst = f"{OUT}/{story}/{variant}"
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(f"{dst}/b1b/narration"); os.makedirs(f"{dst}/b1b/audit")
    for fn in os.listdir(f"{src}/b1b/narration"):
        if fn.endswith(".wav"): shutil.copyfile(f"{src}/b1b/narration/{fn}", f"{dst}/b1b/narration/{fn}")
    return dst
def main(story):
    import er063_family_z_audio_01 as a63, er008_a2_postprocess_slowdown_01 as sd
    src = SRC[story]
    clips = rj(f"{src}/segment_plan_b1b.json")["clips"]
    res = rj(f"{src}/b1b/audit/tts_generation_results.json")["segments"]
    kp = rj(f"{src}/b1b/key_phrases/keywords_canonicalized.json")
    kp_items = [{"rank": it["rank"], "used_form": it["used_form"], "japanese_gloss": it.get("japanese_gloss", ""), "display_phrase": it["display_phrase"]} for it in sorted(kp["items"], key=lambda x: x["rank"])]
    rep = {"story": story, "source_run": src, "slowdown_pct_arg": SLOWDOWN_PCT, "dialogue": [], "non_dialogue_equal": 0, "non_dialogue_total": 0}
    dA = prep(story, "A_rebuild")
    tlA = a63.run_assembly(dA, "b1b", clips, kp_items, story_key=SLUG[story], kp_third="explanation")
    prod = f"{src}/b1b/assembly/Family_Z_{SLUG[story]}_b1b.wav"
    rep["prod_wav_sha"] = sha(prod); rep["A_rebuild_wav_sha"] = sha(tlA["wav"]); rep["A_rebuild_equals_production"] = rep["prod_wav_sha"] == rep["A_rebuild_wav_sha"]
    dB = prep(story, "B")
    nA, nB = f"{dA}/b1b/narration", f"{dB}/b1b/narration"
    for c in clips:
        cid = c["id"]; kind = (res.get(cid) or {}).get("clip_kind")
        if kind == "dialogue":
            info = sd.apply_a2_slowdown(f"{nA}/{cid}.wav", f"{nB}/{cid}.wav", SLOWDOWN_PCT)
            rep["dialogue"].append({"id": cid, "A_sha": sha(f"{nA}/{cid}.wav"), "B_sha": sha(f"{nB}/{cid}.wav"), "src_sec": info["src_duration_seconds"], "dst_sec": info["dst_duration_seconds"]})
    for fn in sorted(os.listdir(nA)):
        cid = fn[:-4]
        if cid in {d["id"] for d in rep["dialogue"]}: continue
        rep["non_dialogue_total"] += 1; rep["non_dialogue_equal"] += sha(f"{nA}/{fn}") == sha(f"{nB}/{fn}")
    tlB = a63.run_assembly(dB, "b1b", clips, kp_items, story_key=SLUG[story], kp_third="explanation")
    rep["B_wav"] = tlB["wav"]; rep["B_wav_sha"] = sha(tlB["wav"]); rep["A_duration"] = tlA["duration_seconds"]; rep["B_duration"] = tlB["duration_seconds"]
    rep["sequence_order_equal"] = tlA["sequence_order"] == tlB["sequence_order"]; rep["headroom_A"] = tlA["headroom"]; rep["headroom_B"] = tlB["headroom"]
    json.dump(rep, open(f"{OUT}/{story}/build_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in rep.items() if not isinstance(v, (list, dict))}, ensure_ascii=False, indent=1), len(rep["dialogue"]))
if __name__ == "__main__": main(sys.argv[1])
