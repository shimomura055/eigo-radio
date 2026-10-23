# -*- coding: utf-8 -*-
"""FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01 build (Trial専用、API 0、Production run dirは読み取りのみ)。
A = 現行(全story clip 6%減速)。B = dialogue clipだけ `_original.wav`(減速前原音)に差替え。それ以外は同一ファイル。
A_rebuild(未変更narrationを再組立)がProduction assembled wavとsha一致することで、B側の組立経路が同一であることを担保する。
usage: python build_ab_01.py <story: melos|open_window>
"""
import hashlib, json, os, shutil, subprocess, sys

ROOT = "C:/Users/tensh/eigo-radio"
os.chdir(ROOT)
sys.path.insert(0, ROOT)
BASE = "er026_output/family_z_production_e2e_01"
SRC = {"melos": f"{BASE}/melos/run_e2e_06", "open_window": f"{BASE}/the_open_window/run_e2e_01"}
SLUG = {"melos": "melos", "open_window": "the_open_window"}
OUT = "er026_output/family_z_std_dialogue_speed_ab_01"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rj(p):
    return json.load(open(p, encoding="utf-8"))


def prep(story, variant):
    src = SRC[story]
    dst = f"{OUT}/{story}/{variant}"
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(f"{dst}/a2/narration"); os.makedirs(f"{dst}/a2/audit")
    for fn in os.listdir(f"{src}/a2/narration"):
        if fn.endswith(".wav") and not fn.endswith("_original.wav"):
            shutil.copyfile(f"{src}/a2/narration/{fn}", f"{dst}/a2/narration/{fn}")
    shutil.copyfile(f"{src}/a2/audit/tts_generation_results.json", f"{dst}/a2/audit/tts_generation_results.json")
    return src, dst


def main(story):
    import er063_family_z_audio_01 as a63
    src = SRC[story]
    plan = rj(f"{src}/segment_plan_a2.json")
    clips = plan["clips"]
    res = rj(f"{src}/a2/audit/tts_generation_results.json")["segments"]
    kp_path = f"{src}/a2/key_phrases/keywords_canonicalized.json"
    if not os.path.exists(kp_path):
        kp_path = f"{src}/key_phrases/a2/keywords_canonicalized.json"
    kp = rj(kp_path)
    kp_items = [{"rank": it["rank"], "used_form": it["used_form"], "japanese_gloss": it.get("japanese_gloss", ""),
                 "display_phrase": it["display_phrase"]} for it in sorted(kp["items"], key=lambda x: x["rank"])]
    report = {"story": story, "source_run": src, "dialogue_clips": [], "narrator_clips": []}
    # A_rebuild
    _, dA = prep(story, "A_rebuild")
    tlA = a63.run_assembly(dA, "a2", clips, kp_items, story_key=SLUG[story], kp_third="japanese")
    prod_wav = f"{src}/a2/assembly/Family_Z_{SLUG[story]}_a2.wav"
    report["prod_wav_sha"] = sha(prod_wav)
    report["A_rebuild_wav_sha"] = sha(tlA["wav"])
    report["A_rebuild_equals_production"] = report["prod_wav_sha"] == report["A_rebuild_wav_sha"]
    # B
    _, dB = prep(story, "B")
    nA, nB = f"{dA}/a2/narration", f"{dB}/a2/narration"
    for c in clips:
        cid = c["id"]
        kind = (res.get(cid) or {}).get("clip_kind")
        if kind == "dialogue":
            orig = f"{src}/a2/narration/{cid}_original.wav"
            if not os.path.exists(orig):
                raise SystemExit(f"NO_ORIGINAL: {cid}")
            shutil.copyfile(orig, f"{nB}/{cid}.wav")
            report["dialogue_clips"].append({"id": cid, "voice": res[cid].get("voice"), "speaker": c.get("speaker"),
                                              "A_sha": sha(f"{nA}/{cid}.wav"), "B_sha": sha(f"{nB}/{cid}.wav"),
                                              "orig_sha_src": sha(orig)})
        else:
            report["narrator_clips"].append({"id": cid, "kind": kind, "A_sha": sha(f"{nA}/{cid}.wav"), "B_sha": sha(f"{nB}/{cid}.wav")})
    tlB = a63.run_assembly(dB, "a2", clips, kp_items, story_key=SLUG[story], kp_third="japanese")
    report["B_wav"] = tlB["wav"]; report["B_wav_sha"] = sha(tlB["wav"])
    report["A_duration"] = tlA["duration_seconds"]; report["B_duration"] = tlB["duration_seconds"]
    report["sequence_order_equal"] = tlA["sequence_order"] == tlB["sequence_order"]
    report["headroom_A"] = tlA["headroom"]; report["headroom_B"] = tlB["headroom"]
    json.dump(report, open(f"{OUT}/{story}/build_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in report.items() if not isinstance(v, (list, dict))}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
