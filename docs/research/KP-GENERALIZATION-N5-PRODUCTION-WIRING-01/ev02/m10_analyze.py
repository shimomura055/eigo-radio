"""M10集計(実行後)。usage: python m10_analyze.py <case_id>...  Trial生存候補とProduction出力をspanで突合し、基準(m10_thresholds_fixed.md)で分類する。"""
import sys, os, json
ROOT = os.path.abspath(os.getcwd())
EV = os.path.join(ROOT, "docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/ev02")
fx = json.load(open(f"{ROOT}/docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/fixtures/n5_trial_replay_fixture_01.json", encoding="utf-8"))
def norm(s): return " ".join((s or "").lower().replace(chr(0x2019), chr(39)).split())
tot = {"trial": 0, "kept": 0, "n5_dropped": 0, "gate_lost": 0, "not_seen": 0}
out = {}
for cid in sys.argv[1:]:
    r = json.load(open(f"{EV}/m10/{cid}/result.json", encoding="utf-8"))
    d = r["doc"]
    cands = {}
    for c in d["candidates"]:
        it = c.get("item") or {}
        cands[norm(it.get("source_span") or c.get("selection_phrase"))] = c
    drops = {}
    for x in d["dropped"]:
        drops.setdefault(norm(x.get("phrase")), []).append(x)
    g = d["generalization"]
    pool_rej = {}
    for a in g["attempts"]:
        for l1 in a["l1"]:
            for x in l1.get("pool_rejected") or []:
                pool_rej.setdefault(norm(x.get("span")), []).append(x)
    rows = []
    for it in fx["cases"][cid]["trial_items"]:
        sp = norm(it["source_span"]); tot["trial"] += 1
        if sp in cands:
            c = cands[sp]; tot["kept"] += 1
            rows.append((it["source_span"], "KEPT", it["display_form"], c["used_form"], c["item"]["gloss_alignment_status"]))
        elif sp in drops:
            st = [x["stage"] for x in drops[sp]]
            if all(s.startswith("n5_") for s in st):
                tot["n5_dropped"] += 1; rows.append((it["source_span"], "N5_DROPPED", st, [x["reasons"] for x in drops[sp]][:1], ""))
            else:
                tot["gate_lost"] += 1; rows.append((it["source_span"], "GATE_LOST", st, [x["reasons"] for x in drops[sp]][:1], ""))
        elif sp in pool_rej:
            rows.append((it["source_span"], "POOL_DUP(n5_pool)", [x["stage"] for x in pool_rej[sp]], [x["reasons"] for x in pool_rej[sp]][:1], "")); tot["not_seen"] += 1
        else:
            tot["not_seen"] += 1; rows.append((it["source_span"], "NOT_SEEN(未再現)", "", "", ""))
    extra = [k for k in cands if k not in {norm(i["source_span"]) for i in fx["cases"][cid]["trial_items"]}]
    out[cid] = {"rows": rows, "production_only": extra, "n_candidates": len(d["candidates"]), "dropped_by_stage": {}}
    for x in d["dropped"]:
        out[cid]["dropped_by_stage"][x["stage"]] = out[cid]["dropped_by_stage"].get(x["stage"], 0) + 1
    print("==", cid, "Production候補", len(d["candidates"]), "drops", out[cid]["dropped_by_stage"], "backfill", (d.get("backfill") or {}).get("status"))
    for row in rows: print("  ", row)
    print("   production_only:", extra)
print("TOTAL", tot, "gate_lost_rate=%.3f" % (tot["gate_lost"] / max(1, tot["trial"])))
json.dump({"cases": out, "total": tot}, open(f"{EV}/m10/analysis.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
