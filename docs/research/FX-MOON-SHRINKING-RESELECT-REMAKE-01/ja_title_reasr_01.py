# 月Std日本語題の保存wav(今回3 attempt)を OpenAI(Production Primary, gpt-4o-mini-transcribe)×N と Azure×1 で再転写し、ASR非決定性と判定を調べる(TTS 0・見積≈¥1・Cap ¥5)。
# FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_03 調査2B。再実行しない(1起動)。各転写を現行Production判定(adapter、Secondary=その場のAzure転写)へ通す。
# 実行: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_reasr_01.py
import json, os, sys, time
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
from dotenv import load_dotenv
load_dotenv()
import er005_cost_logger as cl
OUT = "docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01"
cl.install(f"{OUT}/ja_title_reasr_01.cost_log.jsonl")
import er006_asr_provider_routing_01 as routing
import er007_ja_secondary_asr_01 as sec
import eval_common_02 as E
CANON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
D = "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01/a2/narration/attempts/"
FILES = ["japanese_title_attempt1_customb8f0ff16.wav", "japanese_title_attempt2_customb8f0ff16.wav", "japanese_title_attempt3_minimalfallback.wav"]
N_OPENAI = 4
res = []
for f in FILES:
    row = {"wav": f, "openai": [], "azure": None}
    for i in range(N_OPENAI):
        t, err = routing.transcribe(D + f, language="ja-JP")
        row["openai"].append({"text": t, "error": err})
    az, aerr = sec._azure_stt_strict(D + f, language="ja-JP")
    row["azure"] = {"text": az, "error": aerr}
    # 判定: 各OpenAI転写 x 今回のAzure転写(Secondary stub)を現行Production adapterへ
    judged = []
    for o in row["openai"]:
        if not o["text"]: continue
        orig = sec._azure_stt_strict
        sec._azure_stt_strict = (lambda p, language="ja-JP", timeout_seconds=90, _a=az: (_a, None))
        try:
            r = sec.evaluate_attempt_ja_with_cascade_detail(CANON, o["text"], D + f, cascade_enabled=True, attempt_ctx={"max_len": 400})
        finally:
            sec._azure_stt_strict = orig
        j = r["asr_judgement"]
        judged.append({"primary": o["text"], "state": j.get("state"), "reason": j.get("reason_code")})
    row["judged_with_this_azure"] = judged
    res.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
json.dump(res, open(f"{OUT}/ja_title_reasr_01.out.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
