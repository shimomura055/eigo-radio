# -*- coding: utf-8 -*-
"""Phase 2 集計(決定論、API無し)。runs/<model>/<theme>/rep<n>/ を GT・反復間・モデル間で評価し eval_results_01.json を出力。"""
import sys, os, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import annot_eval as ev
from annot_driver import FORMAL9, THEMES, paths
rd = lambda p: open(p, encoding="utf-8", newline="").read()
js = lambda p: json.load(open(p, encoding="utf-8"))
inv = {r["theme"]: r for r in js(os.path.join(HERE, "gt_inventory.json"))}
led = [json.loads(l) for l in open(os.path.join(HERE, "cost_ledger_annot_01.jsonl"), encoding="utf-8") if l.strip()]
lg = {(r["model_key"], r["theme"], r["rep"]): r for r in led}

def rundir(m, t, r): return os.path.join(HERE, "runs", m, t, "rep%d" % r)

def load(m, t, r):
    d = rundir(m, t, r)
    if not os.path.exists(os.path.join(d, "annotated.md")): return None
    return dict(md=rd(os.path.join(d, "annotated.md")), side=js(os.path.join(d, "annotation.json")))

def check_info(m, t, r):
    d = rundir(m, t, r); cp = os.path.join(d, "check.json")
    L = lg.get((m, t, r), {})
    if not os.path.exists(cp): return dict(verdict=L.get("check", "NO_OUTPUT"), fails=[], problems=[])
    c = js(cp); fails, probs = [], []
    for k, v in c.items():
        if isinstance(v, dict) and v.get("status") == "FAIL":
            fails.append(k); probs += [k + ": " + str(p)[:200] for p in (v.get("problems") or v.get("notes") or [])]
    return dict(verdict=c["verdict"], fails=fails, problems=probs)

def tagcounts(brief, md):
    e, _ = ev.events(brief, md)
    if e is None: return None
    return dict(fact=sum(1 for _, k in e if k == "fact"), core=sum(1 for _, k in e if k == "core"), peripheral=sum(1 for _, k in e if k == "peripheral"))

def pairdiff(brief, A, B):
    """A,B = load()結果。完全一致、タグ位置/種別差分を種別ごとに数える(中立: どちらも正解ではない)。"""
    ea, _ = ev.events(brief, A["md"]); eb, _ = ev.events(brief, B["md"])
    if ea is None or eb is None: return dict(comparable=False)
    da, db = {}, {}
    for o, k in ea: da.setdefault(o, []).append(k)
    for o, k in eb: db.setdefault(o, []).append(k)
    kinds = dict(fact_only_a=0, fact_only_b=0, num_only_a=0, num_only_b=0, class_swap=0)
    for o in set(da) | set(db):
        a, b = da.get(o, []), db.get(o, [])
        fa, fb = "fact" in a, "fact" in b
        na, nb = [k for k in a if k != "fact"], [k for k in b if k != "fact"]
        if fa and not fb: kinds["fact_only_a"] += 1
        if fb and not fa: kinds["fact_only_b"] += 1
        if na and not nb: kinds["num_only_a"] += 1
        if nb and not na: kinds["num_only_b"] += 1
        if na and nb and na != nb: kinds["class_swap"] += 1
    # ledger_ids差(位置が一致した事実どうし)
    def fm(X, e):
        offs = [o for o, k in e if k == "fact"]; ids = [set(f.get("ledger_ids", [])) for f in X["side"].get("facts", [])]
        return {o: ids[i] for i, o in enumerate(offs) if i < len(ids)}
    ma, mb = fm(A, ea), fm(B, eb); both = set(ma) & set(mb)
    kinds["ledger_id_diff"] = sum(ma[o] != mb[o] for o in both)
    return dict(comparable=True, exact_md_equal=A["md"] == B["md"], diff_total=sum(v for k, v in kinds.items() if k != "ledger_id_diff") + kinds["ledger_id_diff"], **kinds)

out = dict(runs=[], reps=[], cross=[])
for m in ("luna", "sonnet55"):
    for t in THEMES:
        p = paths(t); brief, ledger = rd(p["brief"]), rd(p["ledger"])
        gt = inv.get(t); gtmd = rd(os.path.join(REPO, gt["final"])) if gt and gt.get("final") else None
        gts = js(os.path.join(REPO, gt["final_sidecar"])) if gt and gt.get("final_sidecar") else None
        R = {}
        for r in (1, 2):
            X = load(m, t, r); R[r] = X; L = lg.get((m, t, r), {})
            row = dict(model=m, theme=t, rep=r, formal=t in FORMAL9, ran=bool(L), model_id_returned=L.get("model_id_returned"), cost_jpy=L.get("cost_jpy"), latency_s=L.get("latency_s"),
                       usage=L.get("usage"), **check_info(m, t, r))
            if X:
                row["tags"] = tagcounts(brief, X["md"])
                if gtmd: row["vs_gt"] = ev.compare(brief, gtmd, X["md"], gts, X["side"])
            out["runs"].append(row)
        if R[1] and R[2]:
            out["reps"].append(dict(model=m, theme=t, formal=t in FORMAL9, **pairdiff(brief, R[1], R[2])))
for t in THEMES:
    p = paths(t); brief = rd(p["brief"])
    for r in (1, 2):
        A, B = load("luna", t, r), load("sonnet55", t, r)
        if A and B: out["cross"].append(dict(theme=t, rep=r, formal=t in FORMAL9, **pairdiff(brief, A, B)))
json.dump(out, open(os.path.join(HERE, "eval_results_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 集計(正式9のみ)
def agg(m):
    rs = [x for x in out["runs"] if x["model"] == m and x["formal"] and x["ran"]]
    s = dict(model=m, n=len(rs), check_pass=sum(x["verdict"] == "PASS" for x in rs), body_unmod=sum(1 for x in rs if x.get("vs_gt", {}).get("cand_body_unmodified")),
             cost_per_article_mean=sum(x["cost_jpy"] for x in rs) / max(1, len(rs)), latency_mean=sum(x["latency_s"] for x in rs) / max(1, len(rs)))
    for t in ("fact", "core", "peripheral"):
        tp = fp = fn = 0
        for x in rs:
            c = x.get("vs_gt", {}).get(t)
            if c: tp += c["tp"]; fp += c["fp"]; fn += c["fn"]
        P = tp / (tp + fp) if tp + fp else None; Rr = tp / (tp + fn) if tp + fn else None
        s[t] = dict(tp=tp, fp=fp, fn=fn, P=P, R=Rr, F1=(2 * P * Rr / (P + Rr) if P and Rr else None))
    ag = [x["vs_gt"]["core_peripheral_class_agreement"] for x in rs if x.get("vs_gt", {}).get("core_peripheral_class_agreement") is not None]
    s["class_agreement_mean"] = sum(ag) / len(ag) if ag else None
    fi = [x["vs_gt"]["fact_ledger_id_exact_match"] for x in rs if x.get("vs_gt", {}).get("fact_ledger_id_exact_match") is not None]
    s["fact_id_match_mean"] = sum(fi) / len(fi) if fi else None
    rp = [x for x in out["reps"] if x["model"] == m and x["formal"] and x.get("comparable")]
    s["rep_exact_equal"] = "%d/%d" % (sum(x["exact_md_equal"] for x in rp), len(rp)); s["rep_diff_total"] = sum(x["diff_total"] for x in rp)
    s["cost_total_all10"] = sum(x["cost_jpy"] or 0 for x in out["runs"] if x["model"] == m)
    return s
summ = [agg("luna"), agg("sonnet55")]
json.dump(summ, open(os.path.join(HERE, "eval_summary_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(summ, ensure_ascii=False, indent=1))
