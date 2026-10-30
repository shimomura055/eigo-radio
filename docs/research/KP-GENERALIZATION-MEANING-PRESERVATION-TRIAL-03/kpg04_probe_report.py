# -*- coding: utf-8 -*-
"""probe結果の集計(API 0)。種別×構成のPASS/FAIL/KEPT/REVIEW、FAIL一覧、繰り返し(SALT違い)の一致、主基準(AP/SS/SO種別の『全回FAIL 0』)を出す。
使い方: python kpg04_probe_report.py [--cfgs P0,P1,P2,P4] [--reviews kpg04_work/probe_results/reviews.json]
reviews.json: {"<cfg>|<suffix>|<probe_id>": "PASS|FAIL|KEPT", ...} Sonnet実読でREVIEWを確定した結果(未記入のREVIEWは未確定として別掲)。"""
import os, sys, json, glob, argparse, collections
HERE = os.path.dirname(os.path.abspath(__file__))
PR = os.path.join(HERE, "kpg04_work", "probe_results")
CRIT_TYPES = ("ARG_PERSON_THING", "SENSE_SHIFT", "SLOT_SENSE")      # 主基準: 3回ともFAIL 0
ALLOW_TYPES = ("MODIFIER_DROPPABLE", "ALREADY_CORRECT")            # 壊さない: 全PASS(or KEPT可否は別集計)


def load(cfg):
    runs = {}
    for p in sorted(glob.glob(os.path.join(PR, f"probes__{cfg}*.json"))):
        name = os.path.basename(p)[len("probes__"):-5]
        if name == cfg or (name.startswith(cfg + "_") and not name[len(cfg) + 1:].startswith("i")):
            runs["" if name == cfg else name[len(cfg) + 1:]] = json.load(open(p, encoding="utf-8"))
    return runs


def verdict(it, reviews, cfg, suf):
    s = it["score"]
    if s == "REVIEW":
        return reviews.get(f"{cfg}|{suf}|{it['probe_id']}", "REVIEW")
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfgs", default="P0,P1,P2,P4,P4d")
    ap.add_argument("--reviews", default=os.path.join(PR, "reviews.json"))
    a = ap.parse_args()
    probes = {p["id"]: p for p in json.load(open(os.path.join(HERE, "kpg04_probes.json"), encoding="utf-8")) if p["type"] != "FREE_COMBINATION"}
    reviews = json.load(open(a.reviews, encoding="utf-8")) if os.path.exists(a.reviews) else {}
    types = list(dict.fromkeys(p["type"] for p in probes.values()))
    print("## 構成別・種別別 (PASS/FAIL/KEPT/REVIEW未確定/欠落)。各構成の全run合算")
    summary = {}
    for cfg in a.cfgs.split(","):
        runs = load(cfg)
        if not runs:
            continue
        print(f"\n### {cfg} (runs: {','.join(r or 'r1' for r in runs)})")
        print("| 種別 | " + " | ".join(r or "r1" for r in runs) + " |")
        print("|---|" + "---|" * len(runs))
        per = {}
        for t in types:
            row = []
            for suf, r in runs.items():
                c = collections.Counter()
                got = set()
                for it in r["items"]:
                    if probes[it["probe_id"]]["type"] != t:
                        continue
                    c[verdict(it, reviews, cfg, suf)] += 1; got.add(it["probe_id"])
                miss = sum(1 for p in probes.values() if p["type"] == t) - len(got)
                row.append(f"P{c['PASS']}/F{c['FAIL']}/K{c['KEPT']}/R{c['REVIEW']}/欠{miss}")
                per.setdefault(suf, {})[t] = c
            print(f"| {t} | " + " | ".join(row) + " |")
        tf = {suf: sum(per[suf][t]["FAIL"] for t in types) for suf in per}
        print("FAIL合計:", tf)
        summary[cfg] = dict(fail=tf, runs=list(runs))
        fails = []
        for suf, r in runs.items():
            for it in r["items"]:
                v = verdict(it, reviews, cfg, suf)
                if v in ("FAIL", "REVIEW"):
                    fails.append((suf or "r1", it["probe_id"], v, it["source_span"], it["display_form"], it["gloss_ja"], "rev" if it.get("reverted") else ""))
        for f in fails:
            print("  -", *f)
        # 主基準: 重要種別で全runのFAIL=0
        crit = {}
        for t in CRIT_TYPES:
            crit[t] = sum(per[suf][t]["FAIL"] for suf in per)
        print("主基準(AP/SS/SO種別 全run合算FAIL):", crit)
    print("\n## 同一probe×構成での run間一致(形)")
    for cfg in a.cfgs.split(","):
        runs = load(cfg)
        if len(runs) < 2:
            continue
        diff = []
        for pid in probes:
            forms = set()
            for suf, r in runs.items():
                for it in r["items"]:
                    if it["probe_id"] == pid:
                        forms.add(it["display_form"])
            if len(forms) > 1:
                diff.append((pid, sorted(forms)))
        print(f"- {cfg}: 形が割れたprobe {len(diff)}/{len(probes)}", diff[:20])


if __name__ == "__main__":
    main()
