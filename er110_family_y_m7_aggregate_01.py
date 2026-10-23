# -*- coding: utf-8 -*-
"""M7校正結果の集計(読取りのみ、API 0)。"""
import glob
import json
import sys

OUT = "er110_output/family_y_trial_01/m7_calibration"


def load(tag):
    res = {}
    for p in sorted(glob.glob(f"{OUT}/*_judge_{tag}.json")):
        d = json.load(open(p, encoding="utf-8"))
        res[d["id"]] = d
    return res


def agg(tag):
    res = load(tag)
    rows, a = [], {"tp": 0, "fn": 0, "fp": 0, "tn": 0}
    s = {"tp": 0, "fn": 0, "fp": 0, "tn": 0}
    for iid, d in res.items():
        lab = d["label"]
        new_secs = {f["section"]: f["fail_fields"] for f in d["check"]["flagged_items"]}
        old_secs = {k: v for k, v in d["old_labels"].items() if v}
        pred = d["check"]["any_flagged"]
        if lab == "NG":
            a["tp" if pred else "fn"] += 1
        else:
            a["fp" if pred else "tn"] += 1
        for sec in ("voice_1", "voice_2", "voice_3", "tension"):
            o, n = sec in old_secs, sec in new_secs
            s["tp" if o and n else "fn" if o and not n else "fp" if n and not o else "tn"] += 1
        rows.append((iid, lab, {k: v for k, v in old_secs.items()}, new_secs, d["check"]["n_fail_fields"]))
    return a, s, rows


if __name__ == "__main__":
    for tag in sys.argv[1:]:
        a, s, rows = agg(tag)
        print(f"== {tag}: article-level {a}  section-level {s}")
        for r in rows:
            print(r[0], r[1], "old=", {k: len(v) for k, v in r[2].items()}, "new=", {k: len(v) for k, v in r[3].items()}, "nFail=", r[4])
