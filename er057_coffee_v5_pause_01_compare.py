# -*- coding: utf-8 -*-
"""take間比較(per-sentence): sentence_end_pause_stats.json から v5 Adv take vs PD8 take vs F5 take の文末無音を文単位で対応付け。"""
import json, os, numpy as np
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er057_output", "coffee_v5_pause_01")
d = json.load(open(os.path.join(OUT, "sentence_end_pause_stats.json"), encoding="utf-8"))
S = d["sets"]
def seq(name): return [q["pause_ms"] for pt in S[name]["parts"] for q in pt["sentence_end_pauses"]]
def ints(name): return [v for pt in S[name]["parts"] for v in pt["other_internal_runs_ms"]]
A, B, C = seq("v5/v4 Adv FS (P8 new take)"), seq("PD8 Trial take (=v3 Adv)"), seq("F5 Adv FS (final_v2)")
rows = {}
def cmp(x, y, nm):
    x, y = np.array(x), np.array(y); dlt = x - y
    return {"pair": nm, "n": len(x), "mean_diff_ms": round(float(dlt.mean())), "sd_diff_ms": round(float(dlt.std(ddof=1))), "mean_abs_diff_ms": round(float(np.abs(dlt).mean())), "max_abs_diff_ms": int(np.abs(dlt).max()),
            "corr": round(float(np.corrcoef(x, y)[0, 1]), 3), "n_sent_gt_200ms_diff": int((np.abs(dlt) > 200).sum())}
rows["adv"] = [cmp(A, B, "v5(P8 new take) - PD8 take"), cmp(A, C, "v5(P8) - F5"), cmp(B, C, "PD8 - F5")]
Sr, Sf = seq("v5/v4 Std FS raw (P8, pre-slowdown)"), seq("F5 Std FS slow6 (final_v2)")
S3 = seq("v3 Std FS slow6 (PD8+6%)")
Sv5 = seq("v5/v4 Std FS slow6 (as heard)")
rows["std"] = [cmp(Sv5, S3, "v5 Std(P8 new take+6%) - v3 Std(PD8 take+6%)"), cmp(Sv5, Sf, "v5 Std - F5 Std")]
rat = {k: {"pause_total_s": S[k]["total_sentence_end_pause_s"], "audio_s": S[k]["total_dur_s"], "pause_share_pct": round(100 * S[k]["total_sentence_end_pause_s"] / S[k]["total_dur_s"], 1),
           "internal_other_runs_n": len(ints(k)), "internal_other_runs_sum_s": round(sum(ints(k)) / 1000, 2), "internal_other_ge300": sum(1 for v in ints(k) if v >= 300)} for k in S}
print(json.dumps(rows, ensure_ascii=False, indent=1)); print(json.dumps(rat, ensure_ascii=False, indent=1))
print("per-sentence Adv v5/PD8/F5:", list(zip(A, B, C)))
json.dump({"pairwise": rows, "share": rat, "adv_per_sentence_v5_pd8_f5": list(zip(A, B, C)), "std_per_sentence_v5_v3_f5": list(zip(Sv5, S3, Sf))}, open(os.path.join(OUT, "take_variance_comparison.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
