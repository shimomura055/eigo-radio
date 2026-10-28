# JA-ASR-FALSE-NG-ROOT-FIX-02 委任_03 正例拡張4wav(pos_ext_03.json)を OpenAI(Production Primary, gpt-4o-mini-transcribe) で各4 draw 再転写(計16呼出)。
# 1起動のみ・自動再試行なし・エラー時は途中結果を保存して即停止(再起動しない)。見積≈¥1.9、上限¥15(BUDGET_PLAN_03.md)。TTS/Azure 0。
# 実行: PYTHONUTF8=1 .venv/Scripts/python.exe -X utf8 docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/redraw_03.py
import hashlib, json, sys, time
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
import er005_cost_logger as cl
OUT = "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/"
cl.install(OUT + "redraw_03.cost_log.jsonl")
import er006_asr_provider_routing_01 as routing
ITEMS = json.load(open(OUT + "pos_ext_03.json", encoding="utf8"))["items"]
N_DRAW = 4
MODEL = routing.require_asr_route("ja-JP")["model"]
res, stopped = [], None
try:
    for it in ITEMS:
        sha = hashlib.sha256(open(it["wav"], "rb").read()).hexdigest()
        assert sha == it["sha256"]
        for d in range(1, N_DRAW + 1):
            t0 = time.time()
            t, e = routing.transcribe(it["wav"], language="ja-JP")
            rec = {"run": it["run"], "seg": it["seg"], "wav": it["wav"], "wav_sha256": sha, "draw": d, "model": MODEL, "text": t, "error": e,
                   "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "elapsed_s": round(time.time() - t0, 2)}
            res.append(rec)
            if e or not t:
                stopped = rec
                raise SystemExit(f"[STOP] {it['run']}/{it['seg']}#{d} error: {e}")
finally:
    json.dump({"managed_id": "JA-ASR-FALSE-NG-ROOT-FIX-02", "model": MODEL, "n_calls": len(res), "stopped": stopped, "draws": res}, open(OUT + "redraw_03.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("calls", len(res), "stopped", bool(stopped))
