# -*- coding: utf-8 -*-
"""名前別/効果別の補助解析(API呼出なし)。python ... > per_name_analysis_01.txt"""
import json, sys, os, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from er069_attribution_clip_split_trial_01_summarize import fisher_p

D = "er069_output/attribution_clip_split_trial_01"
R = json.load(open(f"{D}/results_01.json", encoding="utf8"))
rows = R["rows"]


def c(sel, k):
    v = [r for r in rows if sel(r)]
    return sum(r[k] for r in v), len(v)


out = []
for nm in ["Melos", "Brontes", "Pelias", "Kallis", "NONMELOS_OOV(Brontes+Pelias)", "ALL_OOV"]:
    if nm == "NONMELOS_OOV(Brontes+Pelias)":
        f = lambda r: r["name"] in ("Brontes", "Pelias")
    elif nm == "ALL_OOV":
        f = lambda r: r["name"] != "Kallis"
    else:
        f = lambda r, nm=nm: r["name"] == nm
    for k in ["openai_verified", "azure_pass", "or_pass", "spell_openai", "spell_azure", "spell_whisper"]:
        a, n1 = c(lambda r: f(r) and r["boundary"] == "nss", k)
        b, n2 = c(lambda r: f(r) and r["boundary"] == "ss", k)
        out.append(f"{nm:30s} {k:16s} s+s-avoid(nss) {a}/{n1} vs ss {b}/{n2}  p={fisher_p(a, n1 - a, b, n2 - b):.4f}")
        a, n1 = c(lambda r: f(r) and r["length"] == "L7", k)
        b, n2 = c(lambda r: f(r) and r["length"] == "L2", k)
        e, n3 = c(lambda r: f(r) and r["length"] == "L4", k)
        out.append(f"{nm:30s} {k:16s}   length L7 {a}/{n1} vs L4 {e}/{n3} vs L2 {b}/{n2}  (L7vsL2 p={fisher_p(a, n1 - a, b, n2 - b):.4f})")
for L in ("L2", "L4", "L7"):
    d = [r["duration_s"] for r in rows if r["length"] == L and r["target"] == "raw"]
    out.append(f"dur {L}: mean {statistics.mean(d):.2f}s min {min(d):.2f} max {max(d):.2f}")
cost = json.load(open(f"{D}/cost_01.json", encoding="utf8"))
oi = sum(x["openai_tokens"][0] or 0 for x in cost["asr_calls"])
oo = sum(x["openai_tokens"][1] or 0 for x in cost["asr_calls"])
az = sum(x["azure_seconds"] or 0 for x in cost["asr_calls"])
out.append(f"openai tokens in/out {oi}/{oo}; azure sec {az:.1f}; totals {cost['totals']}; models {cost['tts_model_versions_observed']}")
s = "\n".join(out)
print(s)
