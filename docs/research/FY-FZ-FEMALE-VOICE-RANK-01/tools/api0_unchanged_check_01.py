# -*- coding: utf-8 -*-
"""FY-FZ-FEMALE-VOICE-RANK-01 API 0 evidence: 既存run(完了/制作中)のVoice割当が女性順位変更後も不変であること、新規run(記録なし)は新順位になること。
Y: 各run dirの voice_assignment.json 記録値 == ya.segment_voice_map(run_dir, level)(runner resume/regen/guard/assembleが使う関数)。runnerの記録更新(voice_assignment_record)も既存記録を保持。
Z: 各既存runの voice_assignment.json の女性/男性話者Voice == 現行 derive_dialogue_voice_tts_names(story)(runnerの送信Voice決定元)。"""
import glob
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "netblock_harness_01"))
import er062_family_z_structure_01 as z  # noqa: E402
import er121_family_y_audio_01 as ya  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402

out = {"Y": [], "Z": [], "fail": []}
for p in sorted(glob.glob("er121_output/family_y_production_01/*/*/voice_assignment.json")):
    d = os.path.dirname(p)
    rec = json.load(open(p, encoding="utf-8"))
    rec_slots = rec["y_fixed_slots"]
    row = {"run": d.replace("\\", "/"), "recorded_slots": rec_slots}
    for lv in ("a2", "b1b"):
        vm = ya.segment_voice_map(d, lv)
        row[lv] = {k: vm[k] for k in ("y_voice_1", "y_voice_2", "y_voice_3")}
        # 女性slot=記録値(不変)。男性slot=現行既定(男性は今回不変。旧記録のAlgiebaは従来どおり現行既定Puckへ解決され、記録値では上書きしない)
        want = {"y_voice_1": ys.FIXED_VOICE_SLOTS["voice_1"], "y_voice_2": rec_slots["voice_2"], "y_voice_3": ys.FIXED_VOICE_SLOTS["voice_3"]}
        if row[lv] != want:
            out["fail"].append((d, lv, row[lv], want))
    row["record_preserved_on_rerun"] = ys.voice_assignment_record(d) == rec
    if not row["record_preserved_on_rerun"]:
        out["fail"].append((d, "record_not_preserved"))
    out["Y"].append(row)
for p in sorted(glob.glob("er026_output/family_z_production_e2e_01/*/*/voice_assignment.json")):
    if "melos/er026_output" in p.replace("\\", "/"):
        continue
    rec = json.load(open(p, encoding="utf-8"))
    story = rec["story_key"]
    cur = z.derive_dialogue_voice_tts_names(story)
    rec_v = {r["speaker"]: r["voice"] for r in rec["speakers"]}
    diff = {k: (v, cur.get(k)) for k, v in rec_v.items() if cur.get(k) != v}
    out["Z"].append({"run": os.path.dirname(p).replace("\\", "/"), "story": story, "recorded": rec_v, "current": {k: cur[k] for k in rec_v}, "diff": diff})
    if diff:
        out["fail"].append((p, diff))
out["new_run_default_Y"] = ys.resolve_voice_slots(None)
print(json.dumps({"Y_runs": len(out["Y"]), "Z_runs": len(out["Z"]), "fail": out["fail"], "new_run_default_Y": out["new_run_default_Y"]}, ensure_ascii=False, indent=1))
json.dump(out, open("docs/research/FY-FZ-FEMALE-VOICE-RANK-01/evidence/api0_unchanged_check_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
