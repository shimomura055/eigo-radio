# -*- coding: utf-8 -*-
"""JA-GLOSS-QUALITY-ALARM-TRIAL-01 委任_02B 最終評価(API 0)。凍結構成の final run(rep群)を TRIAL_PLAN_02 §1 の母集団で集計する。
使い方: jaq02b_final.py <frozen_config.json> <outjson>  (frozen_config: method, rule, runs[final run名...], ...)
"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jaq02b_score as S

J = S.J


def per_rep(U, cfg, run):
    res, cost, be = S.load_run(run, U)
    if cfg["method"] == "M5all" or cfg["method"] == "M5lim":
        raise NotImplementedError
    m = cfg["method"]; rule = cfg["rule"]
    P = S.pops(U)
    out = {"run": run, "cost_jpy": round(cost, 3), "mean_batch_s": round(sum(be) / len(be), 1) if be else None, "n_batches": len(be)}
    # 母集団
    pa = S.evaluate(res, U, P["pool_all"], rule, m)
    pap = S.evaluate(res, U, P["pool_prime"], rule, m)
    pc = S.evaluate(res, U, P["real_held_out"], rule, m)
    out["P_a"] = pa; out["P_a_prime"] = pap; out["P_c"] = pc
    # P-c' (P-a'と同一内容を除く)= held-out realのうち、対応するpool項目がP-a'に含まれないもの
    prime_ids = {u["uid"] for u in P["pool_prime"]}
    pcp = [u for u in P["real_held_out"] if not (u.get("pool_uid") in prime_ids)]
    out["P_c_prime_items"] = len(pcp)
    out["pooled"] = {"TP": pap["TP"] + S.evaluate(res, U, pcp, rule, m)["TP"], "warn": pap["warn"] + S.evaluate(res, U, pcp, rule, m)["warn"]}
    out["guardA_held_out"] = S.rate(res, U, P["guardA_held_out"], rule, m)
    out["guardB_held_out"] = S.rate(res, U, P["guardB_held_out"], rule, m)
    out["t3_held_out"] = S.rate(res, U, P["t3_held_out"], rule, m)
    out["t3p_held_out"] = S.rate(res, U, P["t3p_held_out"], rule, m)
    # 運用Recall: 凍結ラベルのproblem 12件(プール)
    pool_prob = [u for u in P["pool_all"] if u["label"] == "problem"]
    out["op_recall"] = S.rate(res, U, pool_prob, rule, m)
    # 類型別Recall(real problem=pool 12件はfrozen category、T3'=category)
    cat = collections.defaultdict(lambda: [0, 0])
    for u in pool_prob + [x for x in U.values() if x["kind"] == "eval" and x["split"] == "held_out" and x["tier"] == "T3P"]:
        b = S.lookup(res, U, u)
        c = u["category"]
        cat[str(c)][1] += 1
        if b and b.get("res") and S.rule_warn(b["res"], rule, m): cat[str(c)][0] += 1
    out["recall_by_category"] = {k: v for k, v in sorted(cat.items())}
    # 警告件数/level batch(自然batch、確認負担)
    nb = collections.defaultdict(lambda: [0, 0])
    for u in P["pool_all"]:
        b = S.lookup(res, U, u)
        if not b or not b.get("res"): continue
        k = (u["slug"], u["level"]); nb[k][1] += 1
        if S.rule_warn(b["res"], rule, m): nb[k][0] += 1
    out["warn_per_level_mean"] = round(sum(v[0] for v in nb.values()) / len(nb), 2)
    out["warn_per_level_max"] = max(v[0] for v in nb.values())
    # Family別/level別 (P-a)
    fam = collections.defaultdict(lambda: collections.Counter())
    for u in P["pool_all"]:
        b = S.lookup(res, U, u)
        if not b or not b.get("res"): fam[(u["family"], u["level"])]["unchecked"] += 1; continue
        w = S.rule_warn(b["res"], rule, m); pos = u["label"] == "problem"
        fam[(u["family"], u["level"])]["n"] += 1
        if w and pos: fam[(u["family"], u["level"])]["TP"] += 1
        if w and not pos: fam[(u["family"], u["level"])]["FP"] += 1
        if (not w) and pos: fam[(u["family"], u["level"])]["FN"] += 1
        if pos: fam[(u["family"], u["level"])]["problem"] += 1
    out["by_family_level"] = {f"{k[0]}|{k[1]}": dict(v) for k, v in sorted(fam.items())}
    # 警告された項目の詳細(誤警告一覧・見逃し一覧に使う)
    det = []
    for u in P["pool_all"] + [x for x in U.values() if x["kind"] == "eval" and x["split"] == "held_out" and (x["tier"] in ("T3", "T3P") or not x.get("pool_uid"))]:
        b = S.lookup(res, U, u)
        r = b["res"] if b and b.get("res") else None
        det.append({"uid": u["uid"], "tier": u.get("tier"), "label": u["label"], "sev": u["severity"], "cat": u["category"], "family": u["family"], "level": u["level"],
                    "expr": u["expression"], "ja": u["current_ja"], "in_dev": u.get("in_dev_set"), "borderline": u.get("borderline_normal"), "unchecked": r is None,
                    "warn_rule": (S.rule_warn(r, rule, m) if r else None), "raw": r})
    out["detail"] = det
    # 未検査・費用
    out["unchecked_total"] = sum(1 for d in det if d["unchecked"])
    return out


def main():
    cfg = J(sys.argv[1]); outp = sys.argv[2]
    U = J(os.path.join(S.TRIAL, "units.json"))
    reps = [per_rep(U, cfg, r) for r in cfg["runs"]]
    def agg(key, sub):
        vals = [r[key][sub] for r in reps if r[key].get(sub) is not None]
        return {"values": vals, "mean": round(sum(vals) / len(vals), 1) if vals else None, "min": min(vals) if vals else None}
    summ = {"P_a_prime_precision": agg("P_a_prime", "precision"), "P_a_precision": agg("P_a", "precision"), "P_c_precision": agg("P_c", "precision"),
            "P_a_prime_recall": agg("P_a_prime", "recall"), "op_recall": agg("op_recall", "pct"), "guardA_held_out": agg("guardA_held_out", "pct"),
            "guardB_held_out": agg("guardB_held_out", "pct"), "t3_held_out": agg("t3_held_out", "pct")}
    json.dump({"cfg": cfg, "summary": summ, "reps": reps}, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    for r in reps:
        print(r["run"], "cost", r["cost_jpy"], "P-a'", r["P_a_prime"]["TP"], "/", r["P_a_prime"]["warn"], "FP", r["P_a_prime"]["FP"], "unchecked", r["unchecked_total"],
              "guardA", r["guardA_held_out"]["k"], "/", r["guardA_held_out"]["n"], "warn/level", r["warn_per_level_mean"])


if __name__ == "__main__":
    main()
