# 委任_10: 診断のみ。run_e2e_04 attempt1-3 wavへ既存の6%減速(er008_a2_postprocess_slowdown_01.apply_a2_slowdown, ローカルffmpeg)を
# scratchコピーに適用し、既存ASR経路(OpenAI, prompt無し)で各2回転写。Production出力・review_lock_state・既存wavは不変。新規TTS 0 / Azure 0 / LLM 0。
import sys, os, json, re, shutil
sys.path.insert(0, os.getcwd())
import er008_a2_postprocess_slowdown_01 as sd
import er006_asr_provider_routing_01 as routing
SCR = sys.argv[1]
B = "er026_output/family_z_production_e2e_01/melos/run_e2e_04/a2/narration/attempts"
W = {"att1": f"{B}/full_story_part3_c1_attempt1_customa3c4625e.wav", "att2": f"{B}/full_story_part3_c1_attempt2_customa3c4625e.wav",
     "att3": f"{B}/full_story_part3_c1_attempt3_minimalfallback.wav"}
out = {}
for k, p in W.items():
    dst = os.path.join(SCR, f"{k}_slowed.wav")
    info = sd.apply_a2_slowdown(p, dst)
    rows = []
    for i in range(2):
        t, err = routing.transcribe(dst, language="en-US")
        m = re.search(r"rock\.\s*(.{0,28})", t or "")
        rows.append({"err": err, "name_window": m.group(1) if m else None, "text": t})
    out[k] = {"stretch": {kk: info.get(kk) for kk in ("src_duration_seconds", "dst_duration_seconds")}, "results": rows}
    print(k, [r["name_window"] for r in rows])
json.dump(out, open("docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/asr_reeval_slowed_part3c1_10_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
