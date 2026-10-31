"""Trial専用。TRIAL_PLAN_02 §3-C 追加対照。
mode ext : 2x2抽出対照(untidi_b1b 各3回、SELなし)。X1=網羅列挙文面@14 / X2=価値中立L1文面@40 / X3=網羅列挙@40+重複回避文 / X4=L1@30-重複回避文
mode sel : 同一プールSEL反復(untidi_b1b rep1のA0プール・E2プールにSELを追加2回=計3回)。cls/keep/difficulty一致率を算出
usage: python n5r_ctl_02.py <proc_label> ext|sel"""
import sys, os, json, time, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n5r_lib_02 as L
n5 = L.n5
PROC, MODE = sys.argv[1], sys.argv[2]
L.install_log(PROC)
n5.preflight()
CASE = "untidi_b1b"
fx = L.fixture(); text = fx["cases"][CASE]["text"]
ctx = L.make_ctx(CASE, PROC, f"n5r2_ctl_{MODE}")
if MODE == "ext":
    V = {"X1_enum@14": lambda: L.p_L3(text, 14, dup=False), "X2_neutralL1@40": lambda: L.p_L1(text, 40, dup=True),
         "X3_enum@40+dup": lambda: L.p_L3(text, 40, dup=True), "X4_L1@30-dup": lambda: L.p_L1(text, 30, dup=False)}
    out = {"case": CASE, "runs": {}}
    for v, f in V.items():
        out["runs"][v] = []
        for i in range(3):
            L.guard(0.6); k0 = len(ctx.metas); t0 = time.time()
            with L.cl.logging_context("N5R2", f"ctl_{v}_{i+1}"):
                o, m = n5.call_llm("b1", f(), n5.B1_SCHEMA, ctx, label=f"N5R2_ctl_{v}")
            sp = [c["span"] for c in o["candidates"]]
            info = L.calls_info(ctx, k0, time.time() - t0)
            out["runs"][v].append({"sample": i + 1, "n": len(sp), "hits": L.hits(sp), "spans": sp, "cost_jpy": info["cost_jpy"], "sec": info["sec"], "truncated": info["truncated"]})
            print(v, i + 1, len(sp), {k: int(b) for k, b in L.hits(sp).items()}, "spent", round(L.spent(), 2)); sys.stdout.flush()
    json.dump(out, open(f"{L.EV}/ctl_ext_{CASE}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
else:
    rep = json.load(open(f"{L.EV}/rep_{CASE}_1.json", encoding="utf-8"))
    out = {"case": CASE, "pools": {}}
    for pn in ("A0", "E2"):
        orig = rep["pools"][pn]["judged"]
        cands = [dict(span=c["span"], sentence=c["sentence"], n5_origin=c["n5_origin"], p7_rank=c.get("p7_rank")) for c in orig
                 if True]
        # 元の主SELに渡した候補のみ(SEL_DEFERREDで追加判定されたものは除く): poolサイズ=info.n_pool
        npool = rep["pools"][pn]["info"]["n_pool"]
        cands = cands[:npool]
        runs = [{c["span"]: (c["cls"], bool(c["keep"]), c["difficulty"]) for c in orig[:npool]}]
        sels = []
        for r in range(2):
            L.guard(0.8); log = n5.new_log(f"ctl_sel_{pn}_{r}"); k0 = len(ctx.metas); t0 = time.time()
            with L.cl.logging_context("N5R2", f"ctl_sel_{pn}_{r+1}"):
                j = n5.select(text, [dict(c) for c in cands], log, ctx, label="SEL_CTL")
            info = L.calls_info(ctx, k0, time.time() - t0); sels.append(info)
            runs.append({c["span"]: (c["cls"], bool(c["keep"]), c["difficulty"]) for c in j})
            print(pn, r + 1, "keep", sum(1 for c in j if c["keep"]), "cost", info["cost_jpy"], "trunc", info["truncated"], "spent", round(L.spent(), 2)); sys.stdout.flush()
        def agree(a, b, what):
            ks = [k for k in a if k in b]
            if what == "clskeep": return sum(1 for k in ks if a[k][0] == b[k][0] and a[k][1] == b[k][1]) / max(1, len(ks))
            if what == "keep": return sum(1 for k in ks if a[k][1] == b[k][1]) / max(1, len(ks))
            if what == "diff_keep": return sum(1 for k in ks if a[k][1] and b[k][1] and a[k][2] == b[k][2]) / max(1, sum(1 for k in ks if a[k][1] and b[k][1]))
            return sum(1 for k in ks if a[k][2] == b[k][2]) / max(1, len(ks))
        res = {}
        for what in ("clskeep", "keep", "difficulty", "diff_keep"):
            vals = [agree(runs[i], runs[j], what) for i, j in itertools.combinations(range(3), 2)]
            res[what] = {"pairs": [round(v, 4) for v in vals], "mean": round(sum(vals) / len(vals), 4)}
        out["pools"][pn] = {"n_pool": npool, "runs": runs, "agreement": res, "sel_infos": sels}
    json.dump(out, open(f"{L.EV}/ctl_sel_{CASE}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({pn: v["agreement"] for pn, v in out["pools"].items()}, ensure_ascii=False))
