# -*- coding: utf-8 -*-
"""委任_03 Phase 2 集計(API 0)。Control/After(Luna丸め)を同一記事・同一条件で比較する。
出力: er090_output/b3_core_number_rounding_trial_02/evidence/phase2_summary.json
  - 決定論数値監査(Trial専用): JA R2 / Advanced / Standard の全数値トークン分類
  - 現行Production相当: Writer STOP/再生成retry、Risk Flagger flag数(Human Review増分)、丸め数値を含む文へのflag
  - 旧LDC(Trial専用の追加参考)
  - 費用/時間(実測raw_usage_log)
"""
from __future__ import annotations

import json
import os
import re

import er053_cost_aggregate_01 as ca
import er090_b3_core_number_rounding_trial_02_audit as au
import er090_b3_core_number_rounding_trial_02_p2 as p2
import er090_b3_core_number_rounding_trial_02_run as r2

ROOT = r2.ROOT


def jl(p):
    return r2.load_json(p) if os.path.exists(p) else None


def rd(p):
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None


def arm_eval(aid, arm):
    d = p2.p2_dir(aid, arm)
    res = jl(os.path.join(d, "arm_result.json"))
    if not res:
        return None
    side = jl(os.path.join(d, "storyline_b3", "annotation.json"))
    overlay = jl(os.path.join(d, "overlay_used.json")) if arm == "after" else None
    allowed = au.build_allowed(side, overlay)
    out = {"article": aid, "arm": arm, "stop": res["stop"], "events": res["events"], "writer": res.get("writer"),
           "stages": res["stages"], "audit": {}}
    texts = {"ja_r2": rd(os.path.join(d, "ja_writer", "revision2.md")), "advanced": rd(os.path.join(d, "b1b", "article.md")),
             "standard": rd(os.path.join(d, "a2", "article.md"))}
    jset = au.ja_value_set(texts["ja_r2"]) if texts["ja_r2"] else None
    for k, t in texts.items():
        if t is None:
            continue
        c = au.classify(t, allowed, "ja" if k == "ja_r2" else "en", jset if k != "ja_r2" else None)
        out["audit"][k] = c
        out["audit"][k]["leak_concept_tag"] = bool(re.search(r"概数表記|中核数値|周辺数値|【事実", t))
    if overlay and texts["ja_r2"]:
        out["designated_ja"] = au.designated_surface_check(texts["ja_r2"], overlay)
    out["rf"] = {}
    for lvl in ("b1b", "a2"):
        r = jl(os.path.join(d, f"rf_{lvl}.json"))
        if r:
            out["rf"][lvl] = {"status": r["status"], "n_issues": len(r["issues"]),
                              "issues": [{"sid": i["sentence_id"], "text": i["sentence_text"][:200], "conf": i["confidence"], "facts": i["related_fact_ids"],
                                          "question": [f["question"][:160] for f in i["flag_reasons"]][:2]} for i in r["issues"]]}
    out["ldc"] = {}
    for k in ("ja", "b1b", "a2"):
        r = jl(os.path.join(d, f"ldc_{k}.json"))
        if r:
            devs = r["parsed"].get("deviations", [])
            out["ldc"][k] = {"overall": r["parsed"].get("overall_status"), "n": len(devs), "changed_number": sum(1 for x in devs if x.get("changed_number")),
                             "devs": [{"claim": x["claim_in_article"][:140], "sev": x["severity"], "flags": [f for f in ("changed_number", "changed_scope", "changed_comparison", "changed_fact", "changed_certainty", "changed_causality") if x.get(f)]} for x in devs]}
    lg = os.path.join(d, "raw_usage_log.jsonl")
    cb = ca.compute_stage_cost_breakdown_multi(lg)
    out["cost_jpy_total"] = cb["total_jpy"]
    out["cost_by_stage_jpy"] = cb["by_stage_jpy"]
    out["sec_total"] = round(sum(v.get("sec", 0) for v in res["stages"].values()), 1)
    return out


def main():
    summary = {"arms": {}}
    for aid in p2.P2_ARTICLES:
        for arm in ("control", "control2", "after"):
            e = arm_eval(aid, arm)
            if e:
                summary["arms"][f"{aid}:{arm}"] = e
    r2.save_json(os.path.join(ROOT, "evidence", "phase2_summary.json"), summary)
    for k, e in summary["arms"].items():
        a = e["audit"]
        print(k, "stop=", e["stop"] and e["stop"]["type"], "cost=", e["cost_jpy_total"], "sec=", e["sec_total"],
              {lv: (a[lv]["n_tokens"], a[lv]["violations"], len(a[lv]["DESIGNATED_APPROX"]), a[lv]["leak_concept_tag"]) for lv in a},
              "RF=", {lv: v["n_issues"] for lv, v in e["rf"].items()}, "LDC=", {lv: (v["overall"], v["n"], v["changed_number"]) for lv, v in e["ldc"].items()})


if __name__ == "__main__":
    main()
