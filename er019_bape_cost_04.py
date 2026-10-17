# -*- coding: utf-8 -*-
"""FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01 委任_04: 音声工程+E2E総額の工程別費用集計(有料APIなし、read-only)。
er019_coffee_fxpw_cost_06.py(音声)+er019_bape_cost_03.py出力(text: cost_by_stage_text_03.json)を結合。Batch換算=Gemini TTS token量のみ(pricing_snapshot Batch単価、manual_substitution)。"""
import argparse, collections, json, sys
sys.path.insert(0, ".")
ap = argparse.ArgumentParser()
ap.add_argument("--run-dir", required=True); ap.add_argument("--audio-dir", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
USD_JPY = 160.0
S7_END = "2026-10-17T07:32:19"; S8_END = "2026-10-17T07:37:12"   # S7/S8 log mtime(UTC)。S8 logmtime 16:37:11 JST
snap = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]
def p(prov, model, tier, meter):
    for x in snap:
        if x["provider"] == prov and x["model"] == model and x["tier"] == tier and x["meter"] == meter: return x["price"]
def cost_usd(rec, batch=False):
    if rec.get("cost_usd") is not None: return rec["cost_usd"]
    prov, model = rec.get("provider"), rec.get("model_id") or rec.get("model")
    tier = "Batch" if (batch and prov == "gemini") else "Standard"
    return (rec.get("input_tokens") or 0) * p(prov, model, tier, "input_tokens") / 1e6 + (rec.get("output_tokens") or 0) * p(prov, model, tier, "output_tokens") / 1e6
import er019_family_x_audio_production_runner_01 as R  # noqa
price = R._load_pricing(); cl = R.cl
rows = [json.loads(l) for l in open(f"{a.audio_dir}/raw_usage_log.jsonl", encoding="utf-8") if l.strip()]
agg = collections.defaultdict(lambda: {"std": 0.0, "batch": 0.0, "calls": 0, "ws": 0})
for r in rows:
    ts = r["timestamp"][:19]
    phase = "S7_scaffold(KP選定/正規化/redundancy QA/gloss/Comment・Preview text)" if r["stage"] == "scaffold" else ("S8_tts_adv(b1b)" if ts <= S8_END else "S9_tts_std(a2)")
    if r["provider"] == "azure": usd = bus = cl.azure_stt_cost_usd(r, price)
    else: usd = cost_usd(r); bus = cost_usd(r, True)
    kind = {"gemini": "TTS(gemini)", "openai_asr": "ASR(openai)", "azure": "ASR(azure secondary)", "openai": "LLM(openai luna)"}[r["provider"]]
    k = (phase, kind); agg[k]["std"] += usd; agg[k]["batch"] += bus; agg[k]["calls"] += 1; agg[k]["ws"] += r.get("web_search_call_count") or 0
out = {"usd_jpy": USD_JPY, "audio_stages": {}}
at = ab = 0.0
for (ph, kd), v in sorted(agg.items()):
    out["audio_stages"][f"{ph} | {kd}"] = {"jpy": round(v["std"] * USD_JPY, 3), "batch_equiv_jpy": round(v["batch"] * USD_JPY, 3), "calls": v["calls"], "web_search_calls": v["ws"], "basis": "実測(usage OFFICIAL_API_RESPONSE x pricing_snapshot単価の計算値)"}
    at += v["std"] * USD_JPY; ab += v["batch"] * USD_JPY
text = json.load(open(f"{a.run_dir}/audit/cost_by_stage_text_03.json", encoding="utf-8"))
tt = json.load(open(f"{a.run_dir}/cost.json", encoding="utf-8"))["total_jpy"]
out["text_total_jpy"] = tt; out["text_stage_rows"] = text["text_stage_rows"]
out["text_research_ledger_web_search_jpy"] = text["research_ledger_web_search_jpy"]; out["text_research_ledger_llm_jpy"] = text["research_ledger_llm_jpy"]
out["audio_total_jpy"] = round(at, 3); out["audio_total_batch_equiv_jpy"] = round(ab, 3)
out["runner_reported_audio_cumulative_jpy"] = 23.22
out["e2e_total_jpy"] = round(tt + at, 3); out["e2e_total_batch_equiv_jpy"] = round(tt + ab, 3)
out["approved_cap_e2e_jpy"] = 180; out["remaining_vs_cap_jpy"] = round(180 - out["e2e_total_jpy"], 3)
out["audio_guardrail_jpy"] = 70
out["gap_vs_70jpy_target_actual_jpy"] = round(out["e2e_total_jpy"] - 70, 3); out["gap_vs_70jpy_target_batch_equiv_jpy"] = round(out["e2e_total_batch_equiv_jpy"] - 70, 3)
out["retry_fallback"] = "Adv comment_4 segment内TTS再生成1回(TRUE_CONTENT_MISMATCH→attempt2 CONNECTED_SPEECH_EQUIVALENCE_ACCEPT、既存segment retry機構、費用は上記Gemini/ASRに含む)。K2 fallback 0、run再起動0。web_search(音声工程)=0回"
out["batch_basis"] = "Gemini TTS token量 x pricing_snapshot Batch tier。ASR/OpenAI LLM/Azure/Research/Ledger等は正式Batch単価なし=実測のまま(manual_substitution)"
out["provenance"] = "production_formal_path(fresh)。Master Audio Store固定shell再利用=Std kp2_english 1件(同run内Adv生成の共用)のみ"
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("text_stage_rows",)}, ensure_ascii=False, indent=1))
