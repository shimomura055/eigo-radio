"""委任_03: run_voice_fenrir_01のnarrator clip(Fenrir keyで記録されたがAoede送信だった音声)を、再利用されないよう
audit/legacy_voice_mislabel/<level>/ へ退避(上書き・削除しない)。results.jsonの旧版も丸ごと保存し、narrator entryだけ除去する。
dialogue(old_man=Algieba)・topic_intro等の他clipは対象外。API 0。"""
import json, os, shutil, hashlib, sys
RUN = sys.argv[1]
NARR = ["full_story_part1_c1", "full_story_part1_c2", "full_story_part1_c4", "full_story_part2_c1", "full_story_part2_c1_k1",
        "full_story_part2_c1_k2", "full_story_part3_c1", "full_story_part3_c1_k1", "full_story_part3_c1_k2"]
manifest = []
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
for lv in ("a2", "b1b"):
    dst = f"{RUN}/{lv}/audit/legacy_voice_mislabel"
    os.makedirs(f"{dst}/narration/attempts", exist_ok=True)
    os.makedirs(f"{dst}/tts_block_progress", exist_ok=True)
    rp = f"{RUN}/{lv}/audit/tts_generation_results.json"
    shutil.copyfile(rp, f"{dst}/tts_generation_results.before.json")
    d = json.load(open(rp, encoding="utf-8"))
    for cid in NARR:
        e = d["segments"].pop(cid, None)
        manifest.append({"level": lv, "clip": cid, "entry_voice_recorded": (e or {}).get("voice"), "entry_sha256": (e or {}).get("sha256")})
        for suffix in ("", "_original"):
            f = f"{RUN}/{lv}/narration/{cid}{suffix}.wav"
            if os.path.exists(f):
                manifest.append({"level": lv, "file": f"narration/{cid}{suffix}.wav", "sha256": sha(f)})
                shutil.move(f, f"{dst}/narration/{cid}{suffix}.wav")
        adir = f"{RUN}/{lv}/narration/attempts"
        for fn in sorted(os.listdir(adir)):
            if fn.startswith(cid + "_attempt"):
                manifest.append({"level": lv, "file": f"narration/attempts/{fn}", "sha256": sha(f"{adir}/{fn}")})
                shutil.move(f"{adir}/{fn}", f"{dst}/narration/attempts/{fn}")
        pf = f"{RUN}/{lv}/audit/tts_block_progress/{cid}.json"
        if os.path.exists(pf):
            shutil.move(pf, f"{dst}/tts_block_progress/{cid}.json")
    json.dump(d, open(rp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(manifest, open(f"{RUN}/a2/audit/legacy_voice_mislabel/MANIFEST.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(manifest), "items retired")
