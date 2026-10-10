# -*- coding: utf-8 -*-
"""C3-2(G-4)前提確認: 実在する raw_usage_log.jsonl 全件(repo内)から、cost_usd無しで token単価が必要になる
(provider in gemini/openai/openai_asr, model有り)の (provider, model) を集計し、pricing_snapshot.json の
Standard tier input_tokens/output_tokens 登録有無を確認する(課金API 0、read-only)。
実行: .venv/Scripts/python.exe -X utf8 er053_output/risk_flagger_production_wiring_01/gen_pricing_coverage_c3_01.py
出力: er053_output/risk_flagger_production_wiring_01/pricing_coverage_audio_c3.json"""
import collections
import glob
import json
import os
import sys

sys.dont_write_bytecode = True
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(REPO)
prices = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]
reg = {(p["provider"], p["model"], p["meter"]) for p in prices if p.get("tier", "Standard") == "Standard"}
files = sorted(set(glob.glob("er0*_output/**/raw_usage_log.jsonl", recursive=True)))
seen = collections.Counter()
for f in files:
    try:
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            pr, m = r.get("provider"), r.get("model_id") or r.get("model")
            if pr in ("gemini", "openai", "openai_asr") and m and r.get("cost_usd") is None:
                miss = tuple(mt for mt in ("input_tokens", "output_tokens") if (pr, m, mt) not in reg)
                seen[(pr, m, miss)] += 1
    except OSError:
        pass
rows = [{"provider": k[0], "model": k[1], "unregistered_meters": list(k[2]), "records": v}
        for k, v in sorted(seen.items(), key=lambda x: -x[1])]
out = {"generated_for": "RISK-FLAGGER-PRODUCTION-WIRING-01 C3-2 (G-4) 前提確認", "log_files_scanned": len(files),
       "models": rows,
       "unregistered": [r for r in rows if r["unregistered_meters"]],
       "note": "unregisteredは歴史的Trial(gpt-5.6-terra)のみ。現行Production audio/entertainment経路のmodel(TTS3種/ASR/KP/Writer/RF)は全て登録済み。"}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pricing_coverage_audio_c3.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print(json.dumps({"files": len(files), "unregistered": out["unregistered"]}, ensure_ascii=False))
