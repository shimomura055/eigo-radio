# -*- coding: utf-8 -*-
"""STAGE2-01 委任_02 ②replay devの事前登録ライン判定(ライン2/3/4/5/8)。
使い方: python eval_dev.py --tag v1 [--control control_off]
入力: replay_dev/<tag>/*.json(replay_lib.stage2_replay出力)、precheck/stage1_candidate_rate.json(dev項目)。出力: eval/dev_eval_<tag>.json"""
import argparse
import glob
import json
import pathlib

import replay_lib as L

OUT = L.OUT
GUARD_TYPES = ("主体", "全称", "否定・不在", "数値", "方向・極性")


def load_tag(tag, kind="dev"):
    res = {}
    for f in sorted(glob.glob(str(OUT / ("replay_heldout" if kind == "heldout" else "replay_dev") / tag / "*.json"))):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        if "results" in d:
            res[d["run"]] = d
    return res


def norm(s):
    return " ".join((s or "").split())


def saved_stage2_cost(run_dir):
    run, _, _ = L.load_run(run_dir)
    return round(sum(c.get("cost_jpy") or 0 for c in run["call_log"]
                     if "_c1_stage2_" in (c.get("label") or "") or "_c1_s1_" in (c.get("label") or "")), 4)


def evaluate(tag, control=None, kind="dev"):
    new = load_tag(tag, kind)
    ctrl = load_tag(control, kind) if control else {}
    items = [i for i in L.dev_items(kind) if i.get("matched_claim")]
    rows = []
    for it in items:
        r = new.get(it["run"])
        if not r:
            continue
        hit = next((x for x in r["results"] if norm(x["claim_text"]) == norm(it["matched_claim"])), None)
        if not hit:
            continue
        c_hit = None
        if it["run"] in ctrl:
            c_hit = next((x for x in ctrl[it["run"]]["results"] if norm(x["claim_text"]) == norm(it["matched_claim"])), None)
        rows.append({"item_id": it["item_id"], "guard_type": it["guard_type"], "status": it["status"], "fact_id": it.get("fact_id"),
                     "run": it["run"], "cur": hit["saved"]["materiality"], "new": hit["new"]["materiality"],
                     "ctrl": ((c_hit or {}).get("new") or {}).get("materiality") if c_hit else None,
                     "new_guard_target": hit["new"].get("guard_target"), "claim": it["matched_claim"][:100]})
    out = {"tag": tag, "n_runs_replayed": len(new), "n_items_matched": len(rows)}
    # ライン2: 現行BLOCKINGの既知NGが新構成で非BLOCKING(退行)
    cur_b = [r for r in rows if r["cur"] == "BLOCKING"]
    reg = [r for r in cur_b if r["new"] != "BLOCKING"]
    out["line2"] = {"n_cur_blocking_known_ng": len(cur_b), "n_regressions": len(reg), "regressions": reg,
                    "sentence_level_only": {"n": len([r for r in cur_b if r["status"] == "candidate_sentence_level"]),
                                            "regressions": len([r for r in reg if r["status"] == "candidate_sentence_level"])},
                    "pass": len(reg) == 0}
    # ライン3(HC-012部分。A5-0は別stage)
    hc = [r for r in rows if r["fact_id"] and "HC-012" in r["fact_id"]]
    hc_nb_cur = len([r for r in hc if r["cur"] != "BLOCKING"])
    hc_nb_new = len([r for r in hc if r["new"] != "BLOCKING"])
    hc_worse = [r for r in hc if r["cur"] == "BLOCKING" and r["new"] != "BLOCKING"]
    out["line3_hc012"] = {"n": len(hc), "nonblocking_cur": hc_nb_cur, "nonblocking_new": hc_nb_new, "worse_items": hc_worse,
                          "pass_hc012": (not hc_worse) and hc_nb_new <= hc_nb_cur, "rows": hc}
    # ライン4
    g = [r for r in rows if r["guard_type"] in GUARD_TYPES and r["cur"] != "BLOCKING"]
    g_not = [r for r in g if r["new"] == "BLOCKING"]
    g_sent = [r for r in g if r["status"] == "candidate_sentence_level"]
    g_sent_not = [r for r in g_sent if r["new"] == "BLOCKING"]
    out["line4"] = {"n_denominator": len(g), "n_downgrade_not_established": len(g_not),
                    "ratio": round(len(g_not) / len(g), 3) if g else None,
                    "sentence_level_only": {"n": len(g_sent), "not_established": len(g_sent_not)},
                    "pass": bool(g) and len(g_not) / len(g) >= 0.5, "rows": g}
    # ライン5: 既知NGでない候補の新規BLOCKING
    matched_by_run = {}
    for it in L.dev_items(kind):
        if it.get("matched_claim"):
            matched_by_run.setdefault(it["run"], set()).add(norm(it["matched_claim"]))
    per = []
    for run, d in new.items():
        nonng = [x for x in d["results"] if norm(x["claim_text"]) not in matched_by_run.get(run, set())]
        sb = sum(1 for x in nonng if x["saved"]["materiality"] == "BLOCKING")
        nb = sum(1 for x in nonng if x["new"]["materiality"] == "BLOCKING")
        cb = None
        if run in ctrl:
            cb = sum(1 for x in ctrl[run]["results"] if norm(x["claim_text"]) not in matched_by_run.get(run, set())
                     and x["new"]["materiality"] == "BLOCKING")
        per.append({"run": run, "n_nonng": len(nonng), "saved_blocking": sb, "new_blocking": nb, "control_blocking": cb})
    n = len(per)
    sb_t, nb_t = sum(p["saved_blocking"] for p in per), sum(p["new_blocking"] for p in per)
    cb_t = sum(p["control_blocking"] for p in per if p["control_blocking"] is not None) if ctrl else None
    delta = (nb_t - sb_t) / n if n else None
    rel = (nb_t - sb_t) / sb_t if sb_t else None
    out["line5"] = {"n_articles": n, "saved_blocking_nonng": sb_t, "new_blocking_nonng": nb_t,
                    "delta_per_article": round(delta, 3) if delta is not None else None,
                    "relative": round(rel, 3) if rel is not None else None, "control_off_blocking_nonng": cb_t,
                    "control_delta_per_article_vs_saved": round((cb_t - sb_t) / n, 3) if (ctrl and n) else None,
                    "pass": (delta is not None and delta <= 0.3 and (rel is None or rel <= 0.15)), "per_run": per}
    # ライン8: 費用
    cost_rows = []
    for run, d in new.items():
        cost_rows.append({"run": run, "new": d["cost_jpy"], "saved": saved_stage2_cost(run)})
    dc = sum(c["new"] - c["saved"] for c in cost_rows) / len(cost_rows) if cost_rows else None
    out["line8"] = {"mean_delta_jpy_per_article": round(dc, 4) if dc is not None else None,
                    "mean_new": round(sum(c["new"] for c in cost_rows) / len(cost_rows), 4) if cost_rows else None,
                    "mean_saved": round(sum(c["saved"] for c in cost_rows) / len(cost_rows), 4) if cost_rows else None,
                    "pass": dc is not None and dc <= 1.0}
    allc = [x for d in new.values() for x in d["results"]]
    forced = [x for x in allc if (x["new"].get("reader_belief") or {}).get("forced_blocking")]
    out["belief_stats"] = {
        "n_claims": len(allc), "n_guard_target": sum(1 for x in allc if x["new"].get("guard_target")),
        "belief_dist": {k: sum(1 for x in allc if (x["new"].get("reader_belief") or {}).get("belief_vs_ledger") == k)
                        for k in ("consistent", "contradicts", "unsupported_new_claim", "unclear")},
        "reasked": sum(1 for x in allc if (x["new"].get("reader_belief") or {}).get("reasked")),
        "forced_blocking": len(forced),
        "forced_reasons": {str(k): sum(1 for x in forced if x["new"]["reader_belief"].get("forced_reason") == k)
                           for k in {x["new"]["reader_belief"].get("forced_reason") for x in forced}},
        "so_split_belief_only": sum(1 for x in allc if (x["new"]["so"] or {}).get("belief_only") and (x["new"]["so"] or {}).get("split")),
        "saved_blocking": sum(1 for x in allc if x["saved"]["materiality"] == "BLOCKING"),
        "new_blocking": sum(1 for x in allc if x["new"]["materiality"] == "BLOCKING"),
        "flips_blocking_to_nonblocking": sum(1 for x in allc if x["saved"]["materiality"] == "BLOCKING" and x["new"]["materiality"] != "BLOCKING"),
        "flips_nonblocking_to_blocking": sum(1 for x in allc if x["saved"]["materiality"] != "BLOCKING" and x["new"]["materiality"] == "BLOCKING"),
    }
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--control", default=None)
    ap.add_argument("--kind", default="dev")
    a = ap.parse_args()
    o = evaluate(a.tag, a.control, a.kind)
    (OUT / "eval").mkdir(exist_ok=True, parents=True)
    (OUT / "eval" / f"{a.kind}_eval_{a.tag}.json").write_text(json.dumps(o, ensure_ascii=False, indent=1), encoding="utf-8")
    brief = {k: ({kk: vv for kk, vv in v.items() if kk not in ("rows", "per_run", "regressions", "worse_items")}
                 if isinstance(v, dict) else v) for k, v in o.items()}
    print(json.dumps(brief, ensure_ascii=False, indent=1))
