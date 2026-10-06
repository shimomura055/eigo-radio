"""前回(TRIAL-01)比。事実の差分表のみ(判定なし)。standalone: regression_vs_trial01.py --cur trial_summary_02.json --prev trial_summary_01.json [--cfg same_blind]"""
import argparse
import json


def compare(cur, prev_cfg):
    pg = prev_cfg.get("gold", {})
    rows = []
    for gid, nm in (("G-01", "HC-012"), ("G-02", "A5-0"), ("G-03", "D61")):
        pv = pg.get("per_item", {}).get(gid)
        cv = cur["gold"].get(gid)
        rows.append((f"{nm}({gid}) k/n", f"{sum(x == 'REVERSED' for x in pv)}/{len(pv)}" if pv else "-", f"{cv['k']}/{cv['n']}" if cv else "-"))
    rows.append(("gold repeat計", f"{pg.get('detected_repeats')}/{pg.get('total_repeats')}",
                 f"{sum(v['k'] for v in cur['gold'].values())}/{sum(v['n'] for v in cur['gold'].values())}"))
    pn = prev_cfg.get("normal", {})
    rows.append(("正常文誤重大 件(rate)", f"{pn.get('false_reversal')}({pn.get('rate')})", f"{cur['normal']['false_reversal']}({cur['normal']['rate_rep0']})"))
    rows.append(("正常文誤重大 ids", pn.get("false_reversal_ids"), cur["normal"]["false_reversal_ids"]))
    rows.append(("UNCLEAR全体", prev_cfg.get("unclear_total"), cur["unclear_total"]))
    ps = prev_cfg.get("synthetic", {})
    rows.append(("人工反転 検出", f"{ps.get('all_detected')}/{ps.get('n')}", f"{cur['synthetic']['detected']}/{cur['synthetic']['n']}"))
    for lvl, v in cur["per_run"]["levels"].items():
        p = prev_cfg.get("per_run", {}).get(lvl, {})
        rows.append((f"{lvl} 追加円/run", p.get("added_jpy"), v["added_jpy"]))
        rows.append((f"{lvl} 不要Rewrite/run", p.get("unneeded_rewrite_per_run"), v["unneeded_rewrite_per_run"]))
    return [{"item": a, "trial01": b, "trial02": c} for a, b, c in rows]


def to_md(rows):
    return ["| 項目 | TRIAL-01 | TRIAL-02 |", "|---|---|---|"] + [f"| {r['item']} | {r['trial01']} | {r['trial02']} |" for r in rows]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cur", required=True)
    ap.add_argument("--prev", required=True)
    ap.add_argument("--cfg", default="same_blind")
    a = ap.parse_args()
    print("\n".join(to_md(compare(json.load(open(a.cur, encoding="utf-8")), json.load(open(a.prev, encoding="utf-8"))["configs"][a.cfg]))))
