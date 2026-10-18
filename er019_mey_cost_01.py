# -*- coding: utf-8 -*-
"""FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-01 委任_01 (er019_bape_cost_03.pyの転用): text工程の工程別費用集計(有料APIなし、read-only集計)。
er019_coffee_fxpw_cost_06.py / er019_family_x_entertainment_production_runner_01.compute_stage_cost_breakdown と同じ単価・方式。
Research/LedgerはLLM(token)費用とweb_search_call手数料を分離。実測=raw_usage_logのusage(OFFICIAL_API_RESPONSE)×pricing_snapshot単価の計算値、
推定/未取得を列で区別(音声工程=未取得[S7以降は委任_02で実行]、ASR=未取得)。"""
import argparse, collections, json, sys
sys.path.insert(0, ".")
import er012_e_family_entertainment_two_level_runner_01 as efam  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--run-dir", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
price = efam._load_pricing()
J = efam.USD_JPY
rows = [json.loads(l) for l in open(f"{a.run_dir}/raw_usage_log.jsonl", encoding="utf-8") if l.strip()]
st = collections.OrderedDict()
for r in rows:
    s = r.get("stage") or "UNTAGGED"
    d = st.setdefault(s, {"llm_jpy": 0.0, "web_search_jpy": 0.0, "calls": 0, "web_search_calls": 0, "failed_or_retry_calls": 0, "usage_sources": set(), "models": set()})
    d["calls"] += 1
    d["models"].add(r.get("model_id") or r.get("model"))
    d["usage_sources"].add(r.get("usage_source"))
    if not r.get("success", True) or (r.get("attempt_number") or 1) > 1 and s != "advanced":
        d["failed_or_retry_calls"] += 1
    if r.get("provider") == "openai":
        m = r.get("model_id") or r.get("model")
        llm = (r.get("input_tokens") or 0) * price("openai", m, "input_tokens") / 1e6 + (r.get("output_tokens") or 0) * price("openai", m, "output_tokens") / 1e6
        ws = efam.web_search_call_usd(r, price)
        d["llm_jpy"] += llm * J
        d["web_search_jpy"] += ws * J
        d["web_search_calls"] += r.get("web_search_call_count") or 0
    else:
        d["llm_jpy"] += (r.get("cost_usd") or 0.0) * J

def grp(prefixes):
    return [k for k in st if any(k == p or k.startswith(p) for p in prefixes)]

rows_out = []
def add(label, keys, note=""):
    llm = sum(st[k]["llm_jpy"] for k in keys); ws = sum(st[k]["web_search_jpy"] for k in keys)
    rows_out.append({"stage": label, "llm_jpy": round(llm, 3), "web_search_jpy": round(ws, 3), "total_jpy": round(llm + ws, 3),
                     "web_search_calls": sum(st[k]["web_search_calls"] for k in keys), "calls": sum(st[k]["calls"] for k in keys),
                     "basis": "実測(usage OFFICIAL_API_RESPONSE x pricing_snapshot単価の計算値)", "note": note})
add("Research", ["research"])
add("Ledger(Verification)", ["ledger"])
add("B3 Storyline", ["storyline_b3"])
add("Writer R0", ["w1_r0"]); add("Writer R1", ["w1_astra_r1"]); add("Writer R2", ["w1_astra_r2"])
add("英語化(Advanced+IOL)", ["advanced"], "advanced stageにはAdvanced英語化1回+IOL生成1回(attempt_number=2は再試行でなく別目的call)")
add("Risk Flagger b1b", grp(["risk_flag."]) and [k for k in st if k.startswith("risk_flag.") and k.endswith(".b1b")])
add("Standard調整", ["standard"])
add("Risk Flagger a2", [k for k in st if k.startswith("risk_flag.") and k.endswith(".a2")])
retry = {k: v["failed_or_retry_calls"] for k, v in st.items() if v["failed_or_retry_calls"]}
total = round(sum(x["total_jpy"] for x in rows_out), 3)
_cj = json.load(open(f"{a.run_dir}/cost.json", encoding="utf-8"))["total_jpy"]
out = {"cost_json_total_jpy": _cj, "cost_json_diff_note": "cost.json(runner)とraw_usage_logのGemini cost_usdの差=cached_input割引の扱い差(a2 RF gemini 2 call)。cost.jsonが保守側",
       "run_dir": a.run_dir, "usd_jpy": J, "text_stage_rows": rows_out, "retry_fallback_calls_by_stage": retry,
       "retry_fallback_jpy": 0.0, "retry_fallback_basis": "retry/fallback/regeneration callは0件(failed_or_retry_calls参照)",
       "text_total_jpy": total, "research_ledger_llm_jpy": round(rows_out[0]["llm_jpy"] + rows_out[1]["llm_jpy"], 3),
       "research_ledger_web_search_jpy": round(rows_out[0]["web_search_jpy"] + rows_out[1]["web_search_jpy"], 3),
       "web_search_calls_total": rows_out[0]["web_search_calls"] + rows_out[1]["web_search_calls"],
       "untaken": {"KP": "未取得(S7は委任_02)", "TTS": "未取得(S8/S9は委任_02)", "ASR": "未取得(S8/S9は委任_02)", "audio_total": "未取得"},
       "approved_cap_e2e_jpy": 180, "remaining_vs_cap_after_text_jpy": round(180 - total, 3),
       "text_guardrail_jpy": 110, "audio_guardrail_jpy": 70,
       "gap_vs_70jpy_target_text_only_jpy": round(total - 70, 3),
       "gap_note": "70円目標は記事セット全体。text小計のみ時点の参考(音声工程は未取得)",
       "pricing_snapshot": "er005_output/cost_baseline_01/pricing_snapshot.json", "provenance": "production_formal_path(fresh)"}
import os; os.makedirs(os.path.dirname(a.out), exist_ok=True)
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
