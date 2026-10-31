"""Trial専用。TRIAL_PLAN_02 §1の全アームを1反復ずつ実行(抽出3+E5+SEL5プール+rerank2、GEN/VER/CHKはしない)。
usage: python n5r_run_02.py <proc_label> <case> <rep_from> <rep_to>   (非対話・逐次。結果=ev02/rep_<case>_<n>.json。既存fileはskip)"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n5r_lib_02 as L
n5 = L.n5

PROC, CASE, R0_, R1_ = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
MODE = sys.argv[5] if len(sys.argv) > 5 else "full"      # full=Phase1(全アーム)/ p3=Phase3(A0とE2プールのみ+Phase3アーム)
L.install_log(PROC)
n5.preflight()
fx = L.fixture(); case = fx["cases"][CASE]; text = case["text"]
units = L.core.build_sentence_units(text)
base = L.base_from_fixture(case)


def spans_of(lst):
    return [{"span": c["span"], "difficulty": c.get("difficulty"), "chunk_type": c.get("chunk_type"), "n5_origin": c.get("n5_origin"), "cls": c.get("cls")} for c in lst]


for rep in range(R0_, R1_ + 1):
    fn = f"{L.EV}/rep_{CASE}_{rep}.json"
    if os.path.exists(fn):
        print("skip", fn); continue
    t_rep = time.time()
    ctx = L.make_ctx(CASE, PROC, f"n5r2_{CASE}_{rep}")
    log = n5.new_log(f"N5R2_{CASE}_{rep}")
    out = {"case": CASE, "rep": rep, "proc": PROC, "ext": {}, "pools": {}, "picks": {}, "rr": {}, "sens": {}}
    cand = {}
    for kind in (("A0", "E1", "E2") if MODE == "full" else ("A0", "E2")):
        try:
            cand[kind], info = L.run_extract(kind, text, ctx, f"{CASE}_{rep}_{kind}")
            info["fallback"] = None
        except n5.N5TechnicalFailure as e:
            if kind == "A0":
                raise
            cand[kind] = list(cand["A0"]); info = {"fallback": "B1へフォールバック: " + str(e)[:160], "cost_jpy": 0, "sec": 0}
        info["n_cands"] = len(cand[kind]); info["spans"] = [c["span"] for c in cand[kind]]
        out["ext"][kind] = info
        print(CASE, rep, kind, len(cand[kind]), "cost", info.get("cost_jpy"), "sec", info.get("sec"), "spent", round(L.spent(), 2)); sys.stdout.flush()
    e5 = [dict(span=s, sentence="") for s in L.e5_find(text)] if MODE == "full" else []
    out["ext"]["E5"] = {"n_cands": len(e5), "spans": [c["span"] for c in e5], "cost_jpy": 0, "sec": 0}
    e2spans = [c["span"] for c in cand["E2"]]
    e5diff = [c for c in e5 if not any(n5._contains(c["span"], s) for s in e2spans)]
    out["ext"]["E5diff"] = {"n_cands": len(e5diff), "spans": [c["span"] for c in e5diff]}
    pool_in = ({"A0": cand["A0"], "E1": cand["E1"], "E2": cand["E2"], "E5": e5, "E6": cand["E2"] + e5diff} if MODE == "full" else {"A0": cand["A0"], "E2": cand["E2"]})
    J = {}
    for pn, cs in pool_in.items():
        judged, pool, info = L.pool_and_judge(text, base, cs, units, ctx, f"{CASE}_{rep}_SEL_{pn}", log)
        J[pn] = judged
        out["pools"][pn] = {"info": info, "judged": [L.slim(c) for c in judged]}
        print(CASE, rep, "SEL", pn, "pool", info["n_pool"], "keep", info["n_keep"], "cost", info["cost_jpy"], "trunc", info["truncated"], "sec", info["sec"], "spent", round(L.spent(), 2)); sys.stdout.flush()
    P = {}
    P["A0"] = L.pick_R0(J["A0"]); P["A2"] = L.pick_R0(J["E2"])
    P["A2d"] = L.pick_R0d(J["E2"], text); P["A4"] = L.pick_R1(J["E2"]); P["A4d"] = L.pick_R1d(J["E2"], text)
    if MODE != "p4":
        P["A8"] = L.pick_R5(J["E2"], text, k=2); P["A3ref"] = L.pick_A3(J["E2"], text)
    if MODE == "full":
        P["A1"] = L.pick_R0(J["E1"]); P["A5"] = L.pick_R0(J["E5"])
        out["sens"]["R5_k1"] = [c["span"] for c in L.pick_R5(J["E2"], text, k=1)]
        out["sens"]["R5_k3"] = [c["span"] for c in L.pick_R5(J["E2"], text, k=3)]
    P["A7p"], out["rr"]["E2"] = L.run_rerank(text, J["E2"], ctx, f"{CASE}_{rep}_RR_E2")
    if MODE == "full":
        P["A6p"], out["rr"]["E6"] = L.run_rerank(text, J["E6"], ctx, f"{CASE}_{rep}_RR_E6")
    elif MODE == "p3":
        P["A9"], out["rr"]["SLATE"] = L.run_slate(text, J["E2"], ctx, f"{CASE}_{rep}_SLATE")
        P["A10"] = L.pick_A10(J["E2"], text); P["A12"] = L.pick_A12(J["E2"], text)
        out["sens"]["A11_caps"] = {str(cp): [c["span"] for c in L.pick_R1d(J["E2"], text, cp)] for cp in (8, 9, 10)}
    else:   # p4: A13 RRF(R1d順 x rerank順)
        P["A13"] = L.pick_RRF(J["E2"], text, out["rr"]["E2"].get("order_spans"))
    for a, lst in P.items():
        out["picks"][a] = spans_of(lst)
    for a, lst in P.items():
        h = L.hits([c["span"] for c in lst])
        print(CASE, rep, a, "both" if (h["put_away"] and h["in_the_way"]) else "-", "pa", int(h["put_away"]), "itw", int(h["in_the_way"]))
    out["body_recur"] = {c["span"]: {"trial": L.body_recur_trial(c["span"], text), "strict": L.body_recur_strict(c["span"], text)} for c in J["E2"] if c["keep"]}
    out["total_calls"] = len(ctx.metas); out["total_cost_jpy"] = round(sum(m.get("cost_jpy") or 0 for m in ctx.metas), 4)
    out["all_metas"] = [{k: m.get(k) for k in ("stage", "label", "attempt", "json_ok", "cost_jpy", "sec", "out", "max_out")} for m in ctx.metas]
    out["rep_wall_sec"] = round(time.time() - t_rep, 1)
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("DONE", fn, "cost", out["total_cost_jpy"], "wall", out["rep_wall_sec"], "spent", round(L.spent(), 2)); sys.stdout.flush()
