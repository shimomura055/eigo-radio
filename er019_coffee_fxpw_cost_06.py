# -*- coding: utf-8 -*-
"""FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_06: 音声run費用の工程別集計+Batch換算(有料APIなし、read-only集計)。
単価=er005_output/cost_baseline_01/pricing_snapshot.json。Batch換算は同snapshotに正式Batch単価があるGemini TTSのみ(token量に適用)。
ASR/OpenAI LLM/Azureはsnapshotに正式Batch単価がないため実測のまま(manual_substitution=計算値)。"""
import json, collections, sys
sys.path.insert(0, ".")
USD_JPY = 160.0
RUN = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01"
TEXT = "er019_output/coffee_prices/run_fxpw_01/cost.json"
S8_END_UTC = "2026-10-16T08:37:45"   # S8(b1b tts)終了(/tmp/s8.log mtime 17:37:44 JST)
S7_END_UTC = "2026-10-16T08:33:23"   # S7(scaffold)終了

snap = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def p(provider, model, tier, meter):
    for x in snap:
        if x["provider"] == provider and x["model"] == model and x["tier"] == tier and x["meter"] == meter:
            return x["price"]
    return None


def cost_usd(rec, batch=False):
    if rec.get("cost_usd") is not None:
        return rec["cost_usd"]
    prov, model = rec.get("provider"), rec.get("model_id") or rec.get("model")
    if prov == "azure":
        import er006_cost_log as cl  # noqa
        raise SystemExit("azure cost via runner function")
    tier = "Batch" if (batch and prov == "gemini") else "Standard"
    return (rec.get("input_tokens") or 0) * p(prov, model, tier, "input_tokens") / 1e6 + (rec.get("output_tokens") or 0) * p(prov, model, tier, "output_tokens") / 1e6


import er019_family_x_audio_production_runner_01 as R  # noqa: E402

price = R._load_pricing()
cl = R.cl
rows = [json.loads(l) for l in open(f"{RUN}/raw_usage_log.jsonl", encoding="utf-8") if l.strip()]
agg = collections.defaultdict(lambda: {"std_usd": 0.0, "batch_usd": 0.0, "calls": 0})
for r in rows:
    ts = r["timestamp"][:19]
    if r["stage"] == "scaffold":
        phase = "S7_scaffold(KP LLM/gloss/explanation/support text)"
    else:
        phase = "S8_tts_adv(b1b)" if ts <= S8_END_UTC else "S9_tts_std(a2)"
    if r["provider"] == "azure":
        usd = cl.azure_stt_cost_usd(r, price)
        bus = usd
    else:
        usd = cost_usd(r, False)
        bus = cost_usd(r, True)
    kind = {"gemini": "TTS(gemini)", "openai_asr": "ASR(openai)", "azure": "ASR(azure secondary)", "openai": "LLM(openai luna)"}[r["provider"]]
    k = (phase, kind)
    agg[k]["std_usd"] += usd
    agg[k]["batch_usd"] += bus
    agg[k]["calls"] += 1
out = {"usd_jpy": USD_JPY, "audio_stages": {}, "audio_total_jpy": 0.0, "audio_total_batch_equiv_jpy": 0.0}
for (phase, kind), v in sorted(agg.items()):
    out["audio_stages"][f"{phase} | {kind}"] = {"jpy": round(v["std_usd"] * USD_JPY, 3), "batch_equiv_jpy": round(v["batch_usd"] * USD_JPY, 3), "calls": v["calls"]}
    out["audio_total_jpy"] += v["std_usd"] * USD_JPY
    out["audio_total_batch_equiv_jpy"] += v["batch_usd"] * USD_JPY
text = json.load(open(TEXT, encoding="utf-8"))
out["text_total_jpy"] = text["total_jpy"]
out["text_by_stage_jpy"] = text["by_stage_jpy"]
out["audio_total_jpy"] = round(out["audio_total_jpy"], 3)
out["audio_total_batch_equiv_jpy"] = round(out["audio_total_batch_equiv_jpy"], 3)
out["e2e_total_jpy"] = round(text["total_jpy"] + out["audio_total_jpy"], 3)
out["e2e_total_batch_equiv_jpy"] = round(text["total_jpy"] + out["audio_total_batch_equiv_jpy"], 3)
out["approved_cap_jpy"] = 205
out["remaining_vs_cap_jpy"] = round(205 - out["e2e_total_jpy"], 3)
out["batch_basis"] = "Gemini TTS token量 x pricing_snapshot.json Batch tier(gemini-3.8-flash-lite-tts input 0.25/output 3.0 USD per Mtok, Standard比50%)。ASR/OpenAI LLM/Azure/Research等は正式Batch単価なし=実測のまま。manual_substitution(計算値)"
json.dump(out, open(f"{RUN}/audit/cost_by_stage_e2e_06.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
