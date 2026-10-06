"""TRIAL-03 vs TRIAL-02(blind) 前回比。事実のみ(判定はFable)。"""


def rep0(r):
    c = [x.get("compare") for x in r.get("repeats", [])]
    return r.get("final_compare_rep0") or (c or [None])[0]


def compare(cur_rows, cur_it, cur_cost, prev_rows, prev_sum):
    pit = prev_sum["items"]
    pg, cg = pit.get("gold", {}), cur_it.get("gold", {})
    gold = {g: {"prev_k": (pg.get(g) or {}).get("k"), "cur_k": (cg.get(g) or {}).get("k"),
                "n": (cg.get(g) or {}).get("n")} for g in sorted(set(pg) | set(cg))}
    pr = {r["id"]: rep0(r) for r in prev_rows}
    cr = {r["id"]: rep0(r) for r in cur_rows}
    changed = {i: [pr[i], cr[i]] for i in cr if i in pr and pr[i] != cr[i]}
    new_ids = [i for i in cr if i not in pr]
    cn = cur_it.get("normal_pool") or cur_it.get("normal", {})
    pn = pit.get("normal", {})
    cu = sum(1 for i in cr if cr[i] == "UNCLEAR")
    return {"gold": gold,
            "false_reversal": {"prev": pn.get("false_reversal"), "cur": cn.get("false_reversal"),
                               "prev_ids": pn.get("false_reversal_ids"), "cur_ids": cn.get("false_reversal_ids")},
            "unclear_total": {"prev": pit.get("unclear_total"), "cur": cu},
            "cost_jpy": {"prev": prev_sum.get("cost_jpy"), "cur": cur_cost,
                         "diff": None if prev_sum.get("cost_jpy") is None else round(cur_cost - prev_sum["cost_jpy"], 4)},
            "n_items": {"prev": len(pr), "cur": len(cr), "new_ids_not_in_prev": new_ids},
            "changed_rep0": changed,
            "to_REVERSED": [i for i, v in changed.items() if v[1] == "REVERSED"],
            "from_REVERSED": [i for i, v in changed.items() if v[0] == "REVERSED"]}


def to_md(g):
    m = ["| 項目 | 前回(TRIAL-02) | 今回 |", "|---|---|---|"]
    for k, v in g["gold"].items():
        m.append(f"| {k} 検出k/{v['n']} | {v['prev_k']} | {v['cur_k']} |")
    f = g["false_reversal"]
    m.append(f"| 正常文 誤REVERSED(rep0) | {f['prev']} {f['prev_ids']} | {f['cur']} {f['cur_ids']} |")
    m.append(f"| UNCLEAR(rep0) | {g['unclear_total']['prev']} | {g['unclear_total']['cur']} |")
    c = g["cost_jpy"]
    m.append(f"| 実費(円) | {c['prev']} | {c['cur']} (差 {c['diff']}) |")
    m += ["", f"項目数 前回{g['n_items']['prev']} / 今回{g['n_items']['cur']}、今回のみのid: {g['n_items']['new_ids_not_in_prev']}",
          f"REVERSEDになった: {g['to_REVERSED']}", f"REVERSEDでなくなった: {g['from_REVERSED']}", "", "rep0変化id一覧:"]
    m += [f"- {i}: {a} -> {b}" for i, (a, b) in g["changed_rep0"].items()] or ["- なし"]
    return m
