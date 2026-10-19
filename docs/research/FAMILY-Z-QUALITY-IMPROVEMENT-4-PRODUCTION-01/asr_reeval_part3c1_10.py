# 委任_10: 既存wavに対する既存ASR経路(er006_asr_provider_routing_01.transcribe, OpenAI gpt-4o-mini-transcribe, 既定設定=prompt無し)
# のみの再評価。新規TTS 0 / LLM 0 / Azure 0。各wavを3回(ASR出力の揺れ=B側証拠、wav間比較=A側証拠)。1回起動のみ。
# 実行: .venv\Scripts\python.exe -I -X utf8 <this file>   (cwd=repo root)
import sys, os, json, hashlib, time
sys.path.insert(0, os.getcwd())
import er006_asr_provider_routing_01 as routing
B = "er026_output/family_z_production_e2e_01/melos"
WAVS = {
 "run04_att1_flash_lite": f"{B}/run_e2e_04/a2/narration/attempts/full_story_part3_c1_attempt1_customa3c4625e.wav",
 "run04_att2_flash_lite": f"{B}/run_e2e_04/a2/narration/attempts/full_story_part3_c1_attempt2_customa3c4625e.wav",
 "run04_att3_minimal_fallback": f"{B}/run_e2e_04/a2/narration/attempts/full_story_part3_c1_attempt3_minimalfallback.wav",
 "run04_LR_rewritten_original(He drank text)": f"{B}/run_e2e_04/a2/narration/full_story_part3_c1_original.wav",
 "run03_att1_pre_slowdown(PASS)": f"{B}/run_e2e_03/a2/narration/attempts/full_story_part3_c1_attempt1_customa3c4625e.wav",
 "run03_final_post_slowdown(PASS)": f"{B}/run_e2e_03/a2/narration/full_story_part3_c1.wav",
}
REPEAT = 3
out = {"engine": "openai_asr gpt-4o-mini-transcribe via er006_asr_provider_routing_01.transcribe(lang=en-US), prompt=None", "runs": {}}
import re
def name_window(t):
    m = re.search(r"rock\.\s*(.{0,28})", t or "")
    return m.group(1) if m else None
n_calls = 0
for label, p in WAVS.items():
    sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
    rows = []
    for i in range(REPEAT):
        t, err = routing.transcribe(p, language="en-US")
        n_calls += 1
        rows.append({"i": i + 1, "err": err, "name_window": name_window(t), "text": t})
    out["runs"][label] = {"path": p, "sha256": sha, "results": rows}
out["n_calls"] = n_calls
out["cost_note"] = "OpenAI ASR 1 call per ~25s wav; official unit price ~USD0.003/min => ~JPY0.2/call (estimate, not metered here)"
rp = "docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/asr_reeval_part3c1_10_result.json"
json.dump(out, open(rp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in out["runs"].items():
    print(k, [r["name_window"] for r in v["results"]])
print("calls", n_calls)
