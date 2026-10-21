# er088_kp_asr_dual_pass_summarize_01.py: results.jsonl -> summary.json + table.md (集計のみ、API 0)
import collections
import json

OUT = "er088_output/kp_asr_dual_pass_trial_01"
rows = [json.loads(l) for l in open(f"{OUT}/results.jsonl", encoding="utf-8")]
timing = json.load(open(f"{OUT}/timing.json", encoding="utf-8"))
lines = ["| 回 | Primary転写／判定 | Azure転写／判定 | Whisper転写／判定 | 両方PASS方式 |", "|---|---|---|---|---|"]
pp = sp = dual = wp = 0
prim_t, az_t, wh_t = collections.Counter(), collections.Counter(), collections.Counter()
oa_in = oa_out = 0
oa_jpy = az_ceil = az_exact = 0.0
for d in rows:
    r, w = d["primary_and_secondary"], d["whisper"]
    j = r["judge"]
    P, S = bool(j["primary_passed"]), bool(j["secondary_accepted"])
    pp += P
    sp += S
    dual += bool(j["dual_verified_production_force_secondary"])
    wp += bool(w["pass_equivalent"])
    prim_t[j["primary_text"]] += 1
    az_t[j["secondary_text"]] += 1
    wh_t[w["text"]] += 1
    resp = r["primary_call"]["response"] or {}
    oa_in += resp.get("input_tokens") or 0
    oa_out += resp.get("output_tokens") or 0
    oa_jpy += r["cost_jpy"]["primary_openai"]
    az_ceil += r["cost_jpy"]["azure_est_ceil_seconds"]
    az_exact += r["cost_jpy"]["azure_exact_seconds"]
    lines.append(f"| {d['trial']} | 「{j['primary_text']}」/ {j['primary_label']} → {'PASS' if P else 'NG'} | "
                 f"「{j['secondary_text']}」/ {j['secondary_label']} → {'PASS' if S else 'NG'} | "
                 f"「{w['text']}」/ {w['label']} → {'PASS相当' if w['pass_equivalent'] else 'NG相当'} | "
                 f"{'OK' if j['dual_verified_production_force_secondary'] else 'NG'}({j['state']}) |")
summary = {
    "n": len(rows), "primary_pass": pp, "secondary_pass": sp, "dual_pass": dual, "dual_ng_detected": len(rows) - dual,
    "whisper_pass_equivalent": wp,
    "dual_by_definition_equals_production_verified": all(
        d["primary_and_secondary"]["dual_ok_by_definition"] == d["primary_and_secondary"]["judge"]["dual_verified_production_force_secondary"] for d in rows),
    "primary_transcripts": dict(prim_t), "azure_transcripts": dict(az_t), "whisper_transcripts": dict(wh_t),
    "primary_unique_request_ids": len({(d["primary_and_secondary"]["primary_call"]["response"] or {}).get("request_id") for d in rows}),
    "azure_real_calls_per_audit_total": sum(d["primary_and_secondary"]["judge"]["azure_real_calls"] or 0 for d in rows),
    "cost_jpy": {"openai_input_tokens": oa_in, "openai_output_tokens": oa_out, "openai_total_jpy": round(oa_jpy, 4),
                 "azure_est_production_ceil_seconds_jpy": round(az_ceil, 4), "azure_exact_seconds_jpy": round(az_exact, 4),
                 "total_jpy_production_formula": round(oa_jpy + az_ceil, 4), "whisper_jpy": 0.0,
                 "per_trial_primary_jpy": round(oa_jpy / len(rows), 5), "per_trial_azure_jpy_ceil": round(az_ceil / len(rows), 5)},
    "timing": timing,
    "per_trial_wall_s": [d["primary_and_secondary"]["trial_wall_s"] for d in rows],
    "primary_call_wall_s": [d["primary_and_secondary"]["primary_call"]["wall_s"] for d in rows],
    "azure_secondary_ms": [d["primary_and_secondary"]["judge"]["timing"]["secondary_ms"] for d in rows],
    "whisper_wall_s": [d["whisper"]["wall_s"] for d in rows],
    "whisper_word_probabilities_trial1": rows[0]["whisper"]["words"],
}
json.dump(summary, open(f"{OUT}/summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(f"{OUT}/table.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
print(json.dumps({k: v for k, v in summary.items() if k != "whisper_word_probabilities_trial1"}, ensure_ascii=False, indent=1))
print(summary["whisper_word_probabilities_trial1"])
