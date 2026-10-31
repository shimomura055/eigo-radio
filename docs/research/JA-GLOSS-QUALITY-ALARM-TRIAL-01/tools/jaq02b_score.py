# -*- coding: utf-8 -*-
"""JA-GLOSS-QUALITY-ALARM-TRIAL-01 委任_02B 採点(API 0)。警告規則 R_strict/R_default/R_loose は DESIGN_OPTIONS_01 §3、母集団は TRIAL_PLAN_02 §1。
ラベルは凍結済み(labels_frozen_01.json / items.json)。結果を見てラベル・規則・基準を変えない。"""
import json, os, sys, math, glob, collections
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE); TRIAL = os.path.join(BASE, "trial")
J = lambda p: json.load(open(p, encoding="utf-8"))
CATS4 = {"meaning_mismatch", "too_generic", "lost_nuance", "established_term_replaced"}
RULES = ["R_strict", "R_default", "R_loose"]


def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0, c - h) * 100, 1), round(min(1, c + h) * 100, 1))


def rule_warn(r, rule, method=""):
    """r: dict(warn, severity, confidence, category, [fidelity]). 未検査は呼ぶ前に除外。"""
    if not r.get("warn"): return False
    if rule == "R_loose": return True
    if method.startswith("M3") and r.get("fidelity") == "faithful": return False
    if rule == "R_strict": return r["severity"] == "major" and r["confidence"] in ("mid", "high")
    if rule == "R_default":
        return r["severity"] == "major" or (r["severity"] == "minor" and r["confidence"] == "high" and r["category"] in CATS4)
    raise ValueError(rule)


def load_run(run, U):
    """-> dict uid -> {res: {...} or None(unchecked), reason}, cost, elapsed, calls"""
    d = os.path.join(TRIAL, "out", run)
    out = {}; cost = 0.0; elapsed = 0.0; failed = []
    for fn in sorted(glob.glob(os.path.join(d, "*.json"))):
        if os.path.basename(fn).startswith("_"): continue
        rec = J(fn); m = rec["method"]; idmap = rec["idmap"]
        for sname, st in rec["stages"].items():
            cost += st.get("cost", 0.0); elapsed = max(elapsed, 0) + 0.0
        # elapsed: batch内のstage合計(並列実行なので批次ごと)
        out.setdefault("_batch_elapsed", []).append(sum(st.get("elapsed", 0.0) for st in rec["stages"].values()))
        s1 = rec["stages"].get("s1")
        if m in ("M1", "M2", "M3", "R6", "M3v2", "R6v2"):
            got = {}
            if s1 and s1.get("output"):
                got = {x["id"]: x for x in s1["output"]["results"]}
            for cid, uid in idmap.items():
                if cid in got and (s1.get("ok") or m == "M1"): out[uid] = {"res": got[cid], "bid": rec["bid"], "method": m}
                else:
                    if m == "M1" and uid not in rec["scored"]: continue
                    out[uid] = {"res": None, "bid": rec["bid"], "method": m, "err": (s1 or {}).get("error") or (s1 or {}).get("errors")}
        elif m == "M6":
            skipped = set(rec.get("m6_skipped_equal", []))
            s2 = rec["stages"].get("s2")
            got2 = {x["id"]: x for x in s2["output"]["results"]} if s2 and s2.get("ok") else {}
            for cid, uid in idmap.items():
                if not (s1 and s1.get("ok")): out[uid] = {"res": None, "bid": rec["bid"], "method": m, "err": (s1 or {}).get("error")}
                elif cid in skipped: out[uid] = {"res": {"warn": False, "severity": "none", "confidence": "high", "category": "none", "reason_ja": "", "suggestion": "", "m6_equal_string": True}, "bid": rec["bid"], "method": m}
                elif cid in got2: out[uid] = {"res": got2[cid], "bid": rec["bid"], "method": m}
                else: out[uid] = {"res": None, "bid": rec["bid"], "method": m, "err": (s2 or {}).get("error", "no s2")}
        elif m == "M5":
            # base結果に段2を適用。ここでは M5all / M5lim の両方を後段 apply_m5 で作る。段2生情報を保持。
            s2 = rec["stages"].get("s2") or {}
            for cid, uid in idmap.items():
                out[uid] = {"bid": rec["bid"], "method": m, "choice": None, "s2ok": s2.get("ok", False)}
            if s2.get("ok"):
                for x in s2["output"]["results"]:
                    out[idmap[x["id"]]]["choice"] = x["choice"]; out[idmap[x["id"]]]["side"] = rec["m5_current_side"][x["id"]]
                    out[idmap[x["id"]]]["s2reason"] = x["reason_ja"]
    be = out.pop("_batch_elapsed", [])
    return out, cost, be


def apply_m5(base, m5, mode):
    """mode 'all': 段2を全警告(suggestionあり)に適用。'lim': 確信highでないまたはminorの警告のみに適用。"""
    out = {}
    for uid, b in base.items():
        r = b["res"]
        if r is None: out[uid] = b; continue
        r = dict(r); nb = dict(b); nb["res"] = r
        c = m5.get(uid)
        if c and c.get("choice") is not None and r["warn"]:
            apply = (mode == "all") or (r["confidence"] != "high" or r["severity"] == "minor")
            if apply and (c["choice"] == "equal" or c["choice"] == c["side"]):
                r["warn"] = False; r["m5_cancelled"] = True
        out[uid] = nb
    return out


def label_of(u):
    return u["label"]


def pops(U):
    ev = [u for u in U.values() if u["kind"] == "eval"]
    d = {}
    for sp in ("dev", "held_out"):
        real = [u for u in ev if u["split"] == sp and u["tier"] in ("T1", "T2", "T4")]
        d[f"real_{sp}"] = real
        d[f"guardA_{sp}"] = [u for u in ev if u["split"] == sp and ((u["tier"] == "T1" and u["severity"] == "major") or (u["tier"] == "T3P" and u["severity"] == "major"))]
        d[f"guardB_{sp}"] = [u for u in ev if u["split"] == sp and u["tier"] in ("T1", "T3P")]
        d[f"t3_{sp}"] = [u for u in ev if u["split"] == sp and u["tier"] == "T3"]
        d[f"t3p_{sp}"] = [u for u in ev if u["split"] == sp and u["tier"] == "T3P"]
    pool = [u for u in U.values() if u["kind"] == "pool"]
    d["pool_all"] = pool
    d["pool_prime"] = [u for u in pool if not u["in_dev_set"]]
    return d


def lookup(res, U, u):
    """eval項目でpool対応があり、自分のE-batch結果が無い場合は自然batchのpool結果を使う。"""
    if u["uid"] in res: return res[u["uid"]]
    if u["kind"] == "eval" and u.get("pool_uid") and u["pool_uid"] in res: return res[u["pool_uid"]]
    return None


def evaluate(res, U, popu, rule, method):
    """popu: 項目リスト。returns metrics dict。"""
    warned = []; TP = FP = FN = TN = 0; unchecked = []; fps = []; misses = []; tps = []; bn = []
    for u in popu:
        b = lookup(res, U, u)
        if b is None or b.get("res") is None:
            unchecked.append(u["uid"]); continue
        w = rule_warn(b["res"], rule, method)
        pos = u["label"] == "problem"
        if w and pos: TP += 1; tps.append(u["uid"])
        elif w and not pos:
            FP += 1; fps.append(u["uid"])
            if u.get("borderline_normal"): bn.append(u["uid"])
        elif (not w) and pos: FN += 1; misses.append(u["uid"])
        else: TN += 1
    nw = TP + FP
    return {"n": len(popu), "unchecked": len(unchecked), "warn": nw, "TP": TP, "FP": FP, "FN": FN, "TN": TN, "precision": (round(TP / nw * 100, 1) if nw else None),
            "precision_ci": wilson(TP, nw), "recall": (round(TP / (TP + FN) * 100, 1) if (TP + FN) else None), "fps": fps, "misses": misses, "tps": tps,
            "borderline_fp": bn, "unchecked_ids": unchecked}


def rate(res, U, popu, rule, method):
    """検出率(警告された/対象) -- ガード・T3用"""
    k = 0; n = 0; miss = []; unc = 0
    for u in popu:
        b = lookup(res, U, u)
        if b is None or b.get("res") is None: unc += 1; n += 1; miss.append(u["uid"]); continue
        n += 1
        if rule_warn(b["res"], rule, method): k += 1
        else: miss.append(u["uid"])
    return {"k": k, "n": n, "pct": round(k / n * 100, 1) if n else None, "ci": wilson(k, n), "miss": miss, "unchecked": unc}


def dev_table(run, U, method=None, base_res=None):
    res, cost, be = load_run(run, U)
    meth = method or next((v["method"] for v in res.values() if isinstance(v, dict) and "method" in v), "?")
    P = pops(U)
    out = {"run": run, "method": meth, "cost_jpy": round(cost, 3), "mean_batch_s": round(sum(be) / len(be), 1) if be else None, "n_batches": len(be), "rules": {}}
    for rule in RULES:
        ev = evaluate(res, U, P["real_dev"], rule, meth)
        gA = rate(res, U, P["guardA_dev"], rule, meth); gB = rate(res, U, P["guardB_dev"], rule, meth); t3 = rate(res, U, P["t3_dev"], rule, meth)
        out["rules"][rule] = {"real": {k: ev[k] for k in ("n", "unchecked", "warn", "TP", "FP", "FN", "precision", "recall", "fps", "misses")}, "guardA": gA, "guardB": gB, "t3": t3}
    return out, res


def fmt(t):
    L = [f"run={t['run']} method={t['method']} cost=¥{t['cost_jpy']} batches={t['n_batches']} mean_batch_s={t['mean_batch_s']}"]
    for r, v in t["rules"].items():
        re_ = v["real"]
        L.append(f"  {r}: P-dev {re_['TP']}/{re_['warn']} (P={re_['precision']}) FN={re_['FN']} FP={re_['FP']} unchk={re_['unchecked']} | guardA {v['guardA']['k']}/{v['guardA']['n']} guardB {v['guardB']['k']}/{v['guardB']['n']} T3 {v['t3']['k']}/{v['t3']['n']}")
    return "\n".join(L)


if __name__ == "__main__":
    U = J(os.path.join(TRIAL, "units.json"))
    for run in sys.argv[1:]:
        t, _ = dev_table(run, U)
        print(fmt(t))
