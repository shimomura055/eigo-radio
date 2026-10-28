# JA-ASR-FALSE-NG-ROOT-FIX-02 委任_02B (ii)実測: N3 30wav を OpenAI(Production Primary, gpt-4o-mini-transcribe) で各4 draw 再転写。
# 1起動のみ・自動再試行なし・エラー時は途中結果を保存して即停止(再起動しない)。上限¥3、見積≈¥0.65(BUDGET_PLAN_02.md)。TTS/Azure 0。
# 実行: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/n3_redraw_02.py
import hashlib, json, sys, time
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
import er005_cost_logger as cl
OUT = "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/"
cl.install(OUT + "n3_redraw_02.cost_log.jsonl")
import er006_asr_provider_routing_01 as routing
CLIPS = json.load(open("docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/n3_clips_01.json", encoding="utf8"))
N_DRAW = 4
MODEL = routing.require_asr_route("ja-JP")["model"]
res, stopped = [], None
try:
    for c in CLIPS:
        wav = f"docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/phase3_run/n3/{c['id']}.wav"
        sha = hashlib.sha256(open(wav, "rb").read()).hexdigest()
        for d in range(1, N_DRAW + 1):
            t0 = time.time()
            t, e = routing.transcribe(wav, language="ja-JP")
            rec = {"id": c["id"], "wav": wav, "wav_sha256": sha, "draw": d, "model": MODEL, "text": t, "error": e, "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "elapsed_s": round(time.time() - t0, 2)}
            res.append(rec)
            if e or not t:
                stopped = rec
                raise SystemExit(f"[STOP] {c['id']}#{d} error: {e}")
finally:
    json.dump({"managed_id": "JA-ASR-FALSE-NG-ROOT-FIX-02", "model": MODEL, "n_calls": len(res), "stopped": stopped, "draws": res}, open(OUT + "n3_redraw_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("calls", len(res), "stopped", bool(stopped))
