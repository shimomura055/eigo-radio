# ja_title_reasr_01.out.json の12 OpenAI再転写(+同wavのAzure転写)に、現行Production / v2 Primary層(未採用) / β composite(未採用)を当てる what-if(API 0)。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_whatif_fresh_01.py
import json, sys, hashlib
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import b_light_proto_02 as B
CANON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
D = "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01/a2/narration/attempts/"
R = json.load(open("docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_reasr_01.out.json", encoding="utf-8"))
E.api0_guard_on(); out = []; cnt = {"n": 0, "cur_pass": 0, "v2_pass": 0, "beta_pass": 0, "v2_or_beta_pass": 0}
for r in R:
    sha = hashlib.sha256(open(D + r["wav"], "rb").read()).hexdigest(); az = r["azure"]["text"]
    for o in r["openai"]:
        p = o["text"]; cur = E.primary_stage(CANON, p, False); v2 = E.primary_stage(CANON, p, True)
        b = B.composite_judge(CANON, p, az, {"engine": "azure", "wav_sha256": sha, "model_id": "azure-speech-stt"})
        row = {"wav": r["wav"][:24], "primary": p, "azure": az, "current": cur["state"], "v2_primary_layer": v2["state"], "beta": bool(b.equal), "beta_blocked_by": b.blocked_by}
        out.append(row); cnt["n"] += 1; cnt["cur_pass"] += cur["state"] in E.uj.PASSING_STATES; cnt["v2_pass"] += v2["state"] in E.uj.PASSING_STATES; cnt["beta_pass"] += bool(b.equal)
        cnt["v2_or_beta_pass"] += (v2["state"] in E.uj.PASSING_STATES) or bool(b.equal)
        print(json.dumps(row, ensure_ascii=False))
E.api0_guard_off(); print(cnt)
json.dump({"rows": out, "counts": cnt}, open("docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_whatif_fresh_01.out.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
