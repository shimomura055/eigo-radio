# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_01 RCA(¥0、既存instance JSONの走査のみ、API呼び出しなし)
import json, sys, statistics, collections
sys.path.insert(0, ".")
import er052_open233_stage2_b3_misdowngrade_diag_01 as diag
import er052_open233_self_recovery_flow_runner_01 as runner
OUT = "er052_output/open233_kpi_recovery_02_offline_01"

def call_for(d, cyc, route):
    suf = f"_c{cyc}_stage2_stage2_{route}"
    for c in d.get("call_log", []):
        if c.get("label", "").endswith(suf):
            return c
    return None

rows = []   # 全Checker MAJOR claim(Stage 2通過)
for f, dname, d in diag._iter_instances():
    rub = diag._rubric_of_dir(dname)
    defs = runner._safety_critical_defs(d["instance_id"])
    for c in d["cycles"]:
        cyc = c.get("cycle", 1)
        srs = c.get("stage2_results") or []
        for idx, e in enumerate(srs):
            dev = e.get("dev") or {}
            if dev.get("severity") != "MAJOR":
                continue
            route = e.get("stage2_route")
            call = call_for(d, cyc, route) if route else None
            n_batch = sum(1 for x in srs if x.get("stage2_route") == route and (x.get("dev") or {}).get("severity") == "MAJOR")
            sc = None
            for df in defs:
                if df["related_fact_id"] == (e.get("related_fact_id") or "").strip() and df["text_substring"] in (e.get("claim_text") or ""):
                    sc = df["sub_id"]
            flags = [k for k, v in dev.items() if k.startswith("changed_") or k == "unsupported_new_claim" if v is True]
            rows.append({"file": f, "dir": dname, "rubric": rub, "instance_id": d["instance_id"], "final_state": d.get("final_state"),
                "cycle": cyc, "idx": idx, "n_major_in_route": n_batch, "route": route, "sub_id": sc,
                "materiality": e["materiality"], "llm_materiality": e.get("llm_materiality"), "basis": e.get("basis"),
                "rewrite_kind": e.get("rewrite_kind"), "hint_empty": not (e.get("rewrite_hint") or "").strip(),
                "flags": flags, "claim": e.get("claim_text"), "issue": dev.get("issue"), "fid": e.get("related_fact_id"),
                "reasoning": (call or {}).get("usage", {}).get("reasoning_tokens"),
                "out_tokens": (call or {}).get("usage", {}).get("output_tokens"),
                "stage1_sub": d.get("stage1_recall_miss_substituted"), "stage1_called": d.get("stage1_call_used"),
                "floor_reason": e.get("floor_reason"), "two_of_two": bool(e.get("two_of_two_downgraded"))})
json.dump(rows, open(f"{OUT}/rca_major_rows_01.json", "w", encoding="utf-8"), ensure_ascii=False)
print("rows", len(rows))
# A) Safety-critical非BLOCKING(最終)
leaks = [r for r in rows if r["sub_id"] and r["materiality"] != "BLOCKING" and r["cycle"] >= 1]
print("SC non-blocking rows", len(leaks))
for r in leaks:
    print(r["dir"][-14:], r["instance_id"], r["sub_id"], "cyc", r["cycle"], r["rubric"], r["llm_materiality"], r["materiality"], r["basis"],
          "hint_empty" if r["hint_empty"] else "hint", r["flags"], "reason", r["reasoning"], "n", r["n_major_in_route"], r["route"], r["final_state"], "s1sub", r["stage1_sub"], "s1call", r["stage1_called"], r["floor_reason"])
