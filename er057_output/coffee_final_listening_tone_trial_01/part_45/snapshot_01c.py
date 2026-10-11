# -*- coding: utf-8 -*-
"""委任_01C: worktree(read-only)のCoffee Standard/Advanced音声・audit JSONをsha256付きでsnapshotへコピー。API呼出なし。"""
import hashlib, json, os, shutil, glob
W = r"C:\Users\tensh\eigo-radio-tone\er019_output\family_x_audio_production_wiring_01\coffee_prices__run_e_tone_01"
OUT = r"C:\Users\tensh\eigo-radio\er057_output\coffee_final_listening_tone_trial_01\part_45\evidence_snapshot"
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
man = []
def cp(src, rel):
    dst = os.path.join(OUT, rel); os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    man.append({"rel": rel.replace("\\", "/"), "src": src, "bytes": os.path.getsize(dst), "sha256": sha(dst), "sha256_src": sha(src)})
for lv in ("a2", "b1b"):
    for f in sorted(glob.glob(f"{W}/{lv}/narration/*.wav")): cp(f, f"{lv}/narration/{os.path.basename(f)}")
    for f in sorted(glob.glob(f"{W}/{lv}/assembled/*.wav")): cp(f, f"{lv}/assembled/{os.path.basename(f)}")
    for n in ("timeline.json", "gain_report.json", "headroom_report.json", "tts_generation_results.json", "human_approved_segments.json", "review_lock_state.json"):
        p = f"{W}/{lv}/audit/{n}"
        if os.path.exists(p): cp(p, f"{lv}/audit/{n}")
    p = f"{W}/{lv}/parts.json"
    if os.path.exists(p): cp(p, f"{lv}/parts.json")
for f in sorted(glob.glob(f"{W}/a2/narration/attempts/full_story_part2_*")): cp(f, f"a2/attempts/{os.path.basename(f)}")
for p, rel in ((r"C:\Users\tensh\eigo-radio-tone\er011_output\local_rewrite_recovery\coffee_prices__run_e_tone_01\a2\local_rewrite_recovery_full_story_part2.json", "a2/local_rewrite_recovery_full_story_part2.json"),
               (r"C:\Users\tensh\eigo-radio-tone\er053_output\coffee_new_tone_e2e_01\phase09\tts_generation_results.pre_adopt_backup.json", "a2/tts_generation_results.pre_adopt_backup.json"),
               (r"C:\Users\tensh\eigo-radio-tone\er053_output\coffee_new_tone_e2e_01\phase09\part2_attempt4_adoption_record_09.json", "a2/part2_attempt4_adoption_record_09.json")):
    cp(p, rel)
assert all(m["sha256"] == m["sha256_src"] for m in man)
json.dump(man, open(os.path.join(OUT, "SNAPSHOT_MANIFEST.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(man), "files", sum(m["bytes"] for m in man) // 1048576, "MB")
