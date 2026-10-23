# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_02: Trial結果の機械集計(API 0)とJudge入力の構築。DEV専用。
入力=er112_output/kp_gm_trial_01/runs/<arm>/rep*/<unit>/result.json、inputs/units.json。出力=標準出力 or summary json。"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "er112_output" / "kp_gm_trial_01"
UNITS = json.loads((OUT / "inputs" / "units.json").read_text(encoding="utf-8"))
HARD = set(UNITS["hard_display"])
UBY = {u["unit_id"]: u for u in UNITS["units"]}

FIXED_THAT = ("that said", "at that point", "in that case", "this time", "like that", "all that", "not that bad", "that much", "so that", "between you and me",
              "cost that much", "take that advice")


def load_results(include_v1=False):
    """runs/(現行=v2以降) + 任意でruns_v1/(A-1初版、arm名に`v1_`を付けて区別)。"""
    res = {}
    for f in sorted((OUT / "runs").glob("*/rep*/*/result.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        res[(r["arm"], r["rep"], r["unit_id"])] = r
    if include_v1:
        for f in sorted((OUT / "runs_v1").glob("*/rep*/*/result.json")):
            r = json.loads(f.read_text(encoding="utf-8"))
            r["arm"] = "v1_" + r["arm"]
            res[(r["arm"], r["rep"], r["unit_id"])] = r
    return res


def toks(s):
    return re.findall(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*", s or "")


def residual_flags(key: str, disp: str) -> list:
    """一般化の取りこぼし(機械flag)。固定表現・合成negativeは対象外にするため、display側にも同じ語が実在しkeyに残るものだけ。"""
    t = [w.lower() for w in toks(key)]
    f = []
    k = (key or "").lower()
    if any(x in t for x in ("that", "this")) and not any(fx in k for fx in FIXED_THAT):
        f.append("dem")
    if any(x in t for x in ("him", "me", "us")):
        f.append("obj")
    if "her" in t:
        i = t.index("her")
        if i + 1 >= len(t) or t[i + 1] in ("the", "a", "an", "to", "for", "with", "up", "down", "off", "out", "over", "away", "back"):
            f.append("obj_her")
    return f


def items_table(res):
    rows = []
    for (arm, rep, uid), r in res.items():
        u = UBY.get(uid)
        if not u:
            continue
        pr = u.get("production") or {}
        for it in r.get("items") or []:
            e = (r.get("expl") or {}).get(str(it["rank"])) or {}
            prod = pr.get(str(it["rank"])) or {}
            rows.append(dict(arm=arm, rep=rep, unit=uid, family=u["family"], level=u["level"], synthetic=u["synthetic"], rank=it["rank"],
                             display=it["display_phrase"], key=it["key_phrase"], reason=it.get("reason"), gloss=it.get("gloss"), expl=e.get("text"),
                             expl_status=e.get("status"), sentence=it.get("source_sentence"), hard=it["display_phrase"].lower() in HARD,
                             prod_key=prod.get("key_phrase"), exp=(u.get("expected") or {}).get(str(it["rank"])),
                             words=len(toks(it["key_phrase"])), flags=residual_flags(it["key_phrase"], it["display_phrase"])))
    return rows


def summarize(res, rows):
    arms = sorted({k[0] for k in res})
    print("== unit-level (canon status / retry / HR / error) ==")
    for arm in arms:
        rs = [r for k, r in res.items() if k[0] == arm]
        st = Counter(r.get("canon_status") for r in rs)
        retry = sum(1 for r in rs if len(r.get("canon_attempts") or []) > 1)
        hr = sum(1 for r in rs if (r.get("gloss_alignment_status") or "").startswith(("ALIGN_PARTIAL", "ALIGN_FAILED")))
        err = sum(1 for r in rs if r.get("error") or r.get("expl_error"))
        print(f"{arm:7s} units={len(rs):3d} canon={dict(st)} canon_retry_units={retry} gloss_HR_units={hr} errors={err}")
    print("== item-level ==")
    for arm in arms:
        rr = [x for x in rows if x["arm"] == arm and not x["synthetic"]]
        if not rr:
            continue
        over5 = sum(1 for x in rr if x["words"] > 5)
        resid_h = sum(1 for x in rr if x["hard"] and x["flags"])
        same_n = [x for x in rr if not x["hard"] and x["prod_key"]]
        same = sum(1 for x in same_n if x["key"].lower() == x["prod_key"].lower())
        print(f"{arm:7s} items={len(rr):3d} over5={over5} hard_residual={resid_h} normal_key_same_as_prod={same}/{len(same_n)}")
    print("== synthetic expected ==")
    for arm in arms:
        rr = [x for x in rows if x["arm"] == arm and x["synthetic"]]
        if not rr:
            continue
        ok = 0
        for x in rr:
            if x["key"].lower() in [a.lower() for a in x["exp"]["accept"]]:
                ok += 1
        P = [x for x in rr if x["exp"]["kind"] == "P"]
        N = [x for x in rr if x["exp"]["kind"] == "N"]
        pok = sum(1 for x in P if x["key"].lower() in [a.lower() for a in x["exp"]["accept"]])
        nok = sum(1 for x in N if x["key"].lower() in [a.lower() for a in x["exp"]["accept"]])
        print(f"{arm:7s} syn_items={len(rr)} pos_ok={pok}/{len(P)} neg_kept={nok}/{len(N)}")


def show_hard(rows):
    by = defaultdict(lambda: defaultdict(list))
    for x in rows:
        if x["hard"] or x["synthetic"]:
            by[(x["display"], x["unit"][:24])][x["arm"]].append(x)
    for (disp, u), d in sorted(by.items()):
        print(f"--- {disp}  [{u}]")
        for arm in sorted(d):
            for x in d[arm]:
                print(f"   {arm:6s} r{x['rep']} key={x['key']!r} reason={x['reason']} | {x['gloss']} | {x['expl']}")


if __name__ == "__main__":
    res = load_results(include_v1="v1" in sys.argv)
    rows = items_table(res)
    summarize(res, rows)
    if len(sys.argv) > 1 and sys.argv[1] == "hard":
        show_hard(rows)
