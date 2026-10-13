# KP-OPT-01 委任_03 費用/トークン/所要時間の条件別集計(API呼出なし)。出力 phase2/agg_cost_03.json
import glob, json, collections
OUT = "er064_output/kp_extraction_selection_opt_01/phase2"
runs = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(f"{OUT}/runs/*/job_result.json"))]
G = collections.defaultdict(list)
for r in runs:
    G[(r["cond"],)].append(r); G[(r["cond"], r["level"])].append(r); G[("ALL",)].append(r); G[(r["cond"], r["article"])].append(r)
res = {}
for k, rs in sorted(G.items()):
    def s(ph, f): return sum((u["usage"].get(f) or 0) for r in rs for u in r["usage"][ph])
    n = len(rs)
    sel_cost = sum(u["cost_jpy"] for r in rs for u in r["usage"]["selection"]); qa_cost = sum(u["cost_jpy"] for r in rs for u in r["usage"]["canon_qa"])
    res["/".join(k)] = {"n": n, "cost_per_job": round((sel_cost + qa_cost) / n, 4), "sel_cost_per_job": round(sel_cost / n, 4), "canon_qa_cost_per_job": round(qa_cost / n, 4),
        "sel_calls_per_job": round(sum(len(r["usage"]["selection"]) for r in rs) / n, 2), "qa_calls_per_job": round(sum(len(r["usage"]["canon_qa"]) for r in rs) / n, 2),
        "sel_in_tok": round(s("selection", "input_tokens") / n), "sel_out_tok": round(s("selection", "output_tokens") / n), "sel_reason_tok": round(s("selection", "reasoning_tokens") / n),
        "qa_in_tok": round(s("canon_qa", "input_tokens") / n), "qa_out_tok": round(s("canon_qa", "output_tokens") / n), "qa_reason_tok": round(s("canon_qa", "reasoning_tokens") / n),
        "sel_api_sec_per_job": round(sum(u["elapsed_sec"] for r in rs for u in r["usage"]["selection"]) / n, 1),
        "qa_api_sec_per_job": round(sum(u["elapsed_sec"] for r in rs for u in r["usage"]["canon_qa"]) / n, 1),
        "job_sec": round(sum(r["elapsed_sec"] for r in rs) / n, 1),
        "sel_invalid": sum(1 for r in rs if r["selection_status"] != "KEY_WORDS_STRUCTURE_PASS"),
        "canon_invalid": sum(1 for r in rs if r.get("canonicalization_status") not in (None, "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED")),
        "red_ng": sum(1 for r in rs if r.get("redundancy_status") not in (None, "REDUNDANCY_PASS"))}
json.dump(res, open(f"{OUT}/agg_cost_03.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in res.items(): print(k, v)
