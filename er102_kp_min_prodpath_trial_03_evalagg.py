# -*- coding: utf-8 -*-
"""KPMP3 評価集計(API 0)。eval/{span,final}/*.json + blind_map.json + validation.json -> eval_summary.json"""
import json, statistics, sys
from pathlib import Path
OUT = Path(__file__).resolve().parent / "er102_output" / "kp_min_prodpath_trial_03"
DIMS = ["V", "E", "N", "C", "U", "S", "X"]
def main():
    bmap = json.loads((OUT / "eval" / "blind_map.json").read_text(encoding="utf-8"))
    val = json.loads((OUT / "validation.json").read_text(encoding="utf-8"))
    rows = []; sets = []
    for kind in ("span", "final"):
        for rp in sorted((OUT / "eval" / kind).glob("*.json")):
            d = json.loads(rp.read_text(encoding="utf-8")); uid = d["unit_id"]
            if not d.get("parsed"): sets.append(dict(kind=kind, unit=uid, error="parse")); continue
            for s in d["parsed"]["sets"]:
                arm = bmap[uid + ":" + kind][s["set_id"]]
                phr = val["units"][uid][arm]["rows"]
                sets.append(dict(kind=kind, unit=uid, arm=arm, padding=s.get("padding"), n=len(s["candidates"])))
                for c in s["candidates"]:
                    r = phr[c["idx"] - 1]
                    rows.append(dict(kind=kind, unit=uid, arm=arm, rank=c["idx"], phrase=r["source_span"] if kind == "span" else r["key_phrase"], **{k: c.get(k) for k in DIMS}, note=c.get("note", ""), words=len(((r["source_span"] if kind == "span" else r["key_phrase"]) or "").split())))
    S = {}
    for kind in ("span", "final"):
        S[kind] = {}
        for arm in ("A", "B"):
            rr = [r for r in rows if r["kind"] == kind and r["arm"] == arm]
            S[kind][arm] = dict(n=len(rr), **{k: round(statistics.mean(r[k] for r in rr), 3) for k in DIMS},
                                low=dict(**{k: sum(1 for r in rr if r[k] == 0) for k in DIMS}),
                                padding_sets=sum(1 for s in sets if s.get("kind") == kind and s.get("arm") == arm and s.get("padding")),
                                not_in_text=sum(1 for r in rr if r["note"] == "not_in_text"),
                                sum_VEN=round(statistics.mean(r["V"] + r["E"] + r["N"] for r in rr), 3), sum_CUSX=round(statistics.mean(r["C"] + r["U"] + r["S"] + r["X"] for r in rr), 3))
        # paired by unit (set means)
        wins = {k: [0, 0, 0] for k in DIMS}
        for uid in {r["unit"] for r in rows}:
            for k in DIMS:
                a = [r[k] for r in rows if r["kind"] == kind and r["unit"] == uid and r["arm"] == "A"]; b = [r[k] for r in rows if r["kind"] == kind and r["unit"] == uid and r["arm"] == "B"]
                if a and b:
                    ma, mb = statistics.mean(a), statistics.mean(b); wins[k][0 if mb > ma else (1 if mb < ma else 2)] += 1
        S[kind]["unit_paired_B_gt_A__B_lt_A__tie"] = wins
    out = dict(summary=S, rows=rows, sets=sets)
    (OUT / "eval_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(S, ensure_ascii=False, indent=1)); print("errors", [s for s in sets if s.get("error")])
if __name__ == "__main__": sys.exit(main())
