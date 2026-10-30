"""J2監査(API 0): Trial 03の19ケース記録で、包含dedupeに落とされたB1候補と、その包含相手(Trial P7 base)のSEL判定を列挙する。
usage: <python> j2_trial_blocker_audit.py (cwd=repo root)。fixture応答のreplayのみ。"""
import sys, json, os
sys.path.insert(0, os.getcwd())
from unittest import mock
import er138_kp_n5_generalization_01_test_01 as T
n5 = T.n5
rows = []
for cid, case in T.FX["cases"].items():
    send = T.ReplaySend()
    ctx = n5.N5Ctx("A2_SUPPORT", sleep_fn=lambda s: None)
    with mock.patch.object(n5, "_send", send), mock.patch.object(n5, "preflight", lambda: None):
        o, m = n5.call_llm("b1", n5.prompt_B1(case["text"]), n5.B1_SCHEMA, ctx, label="B1")
        defer = []
        pool, rej = n5.collect_pool(case["text"], case["base"], o["candidates"], defer_out=defer)
        log = n5.new_log("audit")
        judged = n5.select(case["text"], pool, log, ctx)
    base_spans = {b["span"] for b in case["base"]}
    jm = {c["span"]: c for c in judged}
    for d in defer:
        bl = d["blocked_by"]
        bj = jm.get(bl)
        rows.append({"case": cid, "superset_B1": d["cand"]["span"], "blocker": bl, "blocker_is_trial_P7_base": bl in base_spans,
                     "blocker_sel_keep": (bj or {}).get("keep"), "blocker_cls": (bj or {}).get("cls"), "blocker_in_trial_final_items": bl in {i["source_span"] for i in case["trial_items"]}})
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "j2_trial_blocker_audit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
n = len(rows); nb = sum(1 for r in rows if r["blocker_is_trial_P7_base"]); nf = sum(1 for r in rows if r["blocker_is_trial_P7_base"] and r["blocker_sel_keep"] is False)
print(f"dedupe-dropped B1 candidates in Trial 19 cases: {n}; blocker is Trial P7 base: {nb}; of which blocker SEL non-keep (=the J2 mechanism present in Trial): {nf}")
for r in rows: print(r["case"], "|", r["superset_B1"], "<- blocked by", r["blocker"], "| P7base", r["blocker_is_trial_P7_base"], "keep", r["blocker_sel_keep"], r["blocker_cls"])
