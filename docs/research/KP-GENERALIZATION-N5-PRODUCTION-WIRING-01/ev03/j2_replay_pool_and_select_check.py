import sys, json
sys.path.insert(0, ".")
from unittest import mock
import er138_kp_n5_generalization_01_test_01 as T
n5 = T.n5
out = {}
orig_select = n5.select
rec = []
def sel_wrap(text, cands, log, ctx, *, label="SEL"):
    rec.append((label, [c["span"] for c in cands]))
    return orig_select(text, cands, log, ctx, label=label)
n5.select = sel_wrap
for cid, case in T.FX["cases"].items():
    items = [{"display_phrase": b["span"], "source_sentence": b.get("sentence") or "", "item": {"display_phrase": b["span"]}} for b in case["base"]]
    rec.clear()
    send = T.ReplaySend()
    ctx = n5.N5Ctx("A2_SUPPORT", sleep_fn=lambda s: None)
    # Trial等価(collect, defer無し) の kept
    gate = lambda units, screen=None: (lambda c: (dict(c, n5_origin="B1", item={"display_phrase": c["span"], "reason_ja": ""}), []))
    with mock.patch.object(n5, "_send", send), mock.patch.object(n5, "preflight", lambda: None), mock.patch.object(n5, "make_b1_gate", gate):
        try:
            r = n5.pool_and_select(case["text"], items, ctx, include_b1=True, units=[])
            status = "OK"
            deferred = r["record"]["deferred_rejudged"]
        except (AssertionError, n5.N5TechnicalFailure) as e:
            status = "CACHE_MISS(second SEL needed)"
            deferred = None
            r = None
    # Trial側のkept: run_trial_equivalent
    t_items, tr, _, _ = T.run_case(cid)
    trial_spans = [i["source_span"] for i in t_items]
    prod_spans = [p["item"]["display_phrase"] for p in r["picked"]] if r else None
    out[cid] = {"status": status, "deferred": deferred, "n_trial_items": len(trial_spans), "deferred_sel_input": [x for x in rec if x[0]=="SEL_DEFERRED"],
                "pick_same_as_trial": (sorted(prod_spans) == sorted(trial_spans)) if r else None}
for k, v in out.items(): print(k, v)
print("cases", len(out), "OK", sum(1 for v in out.values() if v["status"]=="OK"), "miss", sum(1 for v in out.values() if v["status"]!="OK"))
json.dump(out, open("../j2_replay_result.json","w"), ensure_ascii=False, indent=1)
