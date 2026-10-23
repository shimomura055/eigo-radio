# FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01: Production正式経路の再処理結果 vs Trial B / 旧Production(STALE)の比較(API 0、読み取りのみ)。
# usage: compare_trial_b_01.py <melos|open_window> -> er026_output/family_z_dialogue_speed_wiring_01/compare_<story>.json
import hashlib, json, os, sys, wave
ROOT = "C:/Users/tensh/eigo-radio"; os.chdir(ROOT)
story = sys.argv[1]
BASE = "er026_output/family_z_production_e2e_01"
RUN = {"melos": f"{BASE}/melos/run_e2e_06", "open_window": f"{BASE}/the_open_window/run_e2e_01"}[story]
SLUG = {"melos": "melos", "open_window": "the_open_window"}[story]
TB = {"a2": f"er026_output/family_z_std_dialogue_speed_ab_01/{story}/B/a2/narration", "b1b": f"er026_output/family_z_std_dialogue_speed_ab_01/adv/{story}/B/b1b/narration"}
TB_WAV = {lv: json.load(open(f"er026_output/family_z_std_dialogue_speed_ab_01/{'adv/' if lv=='b1b' else ''}{story}/build_report.json", encoding="utf-8"))["B_wav_sha"] for lv in ("a2", "b1b")}
def sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()
def dur(p):
    with wave.open(p, "rb") as w: return w.getnframes() / w.getframerate()
out = {"story": story, "run": RUN}
for lv in ("a2", "b1b"):
    new = f"{RUN}/{lv}/narration"; old_assembly = f"{RUN}/STALE_speed_v1_20261023/{lv}/assembly"
    res = json.load(open(f"{RUN}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]
    old_res = json.load(open(f"{RUN}/STALE_speed_v1_20261023/{lv}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]
    rows = []; same_tb = 0; tb_total = 0; narr_unchanged = 0; narr_total = 0
    for cid, e in sorted(res.items()):
        kind = e.get("clip_kind"); p = f"{new}/{cid}.wav"
        if not os.path.exists(p): continue
        r = {"id": cid, "kind": kind, "new_sha": sha(p), "old_sha(STALE results)": (old_res.get(cid) or {}).get("sha256"), "speed_profile": (e.get("speed_profile") or {}).get("profile")}
        tbp = f"{TB[lv]}/{cid}.wav"
        if os.path.exists(tbp) and kind in ("dialogue",):
            tb_total += 1; r["trial_b_sha"] = sha(tbp); r["equals_trial_b"] = r["trial_b_sha"] == r["new_sha"]; same_tb += r["equals_trial_b"]
            r["dur_new"] = round(dur(p), 3); r["dur_trial_b"] = round(dur(tbp), 3)
        if kind in ("narrator",) or kind not in ("dialogue",):
            narr_total += 1; ok = r["old_sha(STALE results)"] == r["new_sha"]; r["unchanged_vs_old"] = ok; narr_unchanged += ok
        rows.append(r)
    out[lv] = {"dialogue_equal_trial_b": f"{same_tb}/{tb_total}", "non_dialogue_unchanged_vs_old": f"{narr_unchanged}/{narr_total}",
               "non_dialogue_changed": [r["id"] for r in rows if r.get("unchanged_vs_old") is False], "clips": rows}
    asm = f"{RUN}/{lv}/assembly/Family_Z_{SLUG}_{lv}.wav"
    out[lv]["assembled_wav"] = asm; out[lv]["assembled_sha"] = sha(asm); out[lv]["assembled_duration"] = round(dur(asm), 4)
    out[lv]["trial_b_assembled_sha"] = TB_WAV[lv]; out[lv]["assembled_equals_trial_b"] = out[lv]["assembled_sha"] == TB_WAV[lv]
    oa = f"{old_assembly}/Family_Z_{SLUG}_{lv}.wav"
    out[lv]["old_assembled_duration"] = round(dur(oa), 4) if os.path.exists(oa) else None
json.dump(out, open(f"er026_output/family_z_dialogue_speed_wiring_01/compare_{story}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for lv in ("a2", "b1b"):
    o = out[lv]; print(lv, "dialogue==TrialB", o["dialogue_equal_trial_b"], "| nondialogue unchanged", o["non_dialogue_unchanged_vs_old"], o["non_dialogue_changed"], "| asm==TrialB", o["assembled_equals_trial_b"], "dur", o["old_assembled_duration"], "->", o["assembled_duration"])
