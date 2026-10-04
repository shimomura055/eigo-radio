"""OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_11 第二段階案の¥0集計(Opus#14論点6、Fable評価11)。

案: 同fact_idの兄弟箇所(決定論列挙`deterministic_same_fact_id_location_fallback`)を、cycle 1のStage 2 batchへ前倒し(Rewriteへは渡さない)。
  ① 後cycle(2以降)の「新規」BLOCKING(前cycleまでの置換範囲と重ならない箇所)のうち、cycle 1の列挙で覆えた割合
  ② NORMAL群で、列挙により増えるcycle 1のStage 2判定件数(と、記録上BLOCKINGになった件数=不要Rewrite候補)
採用条件(事前固定): ①>0。LLM callなし。対象: rep27/28/29全run(記録済み出力)。
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er052_open233_self_recovery_flow_runner_01 as R  # noqa: E402

R.apply_kpi_trial_switches()
OUT = os.path.join("er052_output", "open233_kpi_recovery_02_offline_01", "agg_sibling_locations_cycle1_01.json")
REPS = {27: "open233_self_recovery_flow_runner_01_rep27", 28: "open233_self_recovery_flow_runner_01_rep28",
        29: "open233_self_recovery_flow_runner_01_rep29"}
INSTANCES = {i["instance_id"]: i for i in R.build_target_instances()}


def nrm(s: str) -> str:
    return R._norm_for_residual(s or "").casefold()


def main() -> None:
    rows, tot = [], Counter()
    for rep, dn in REPS.items():
        for f in sorted(glob.glob(os.path.join("er052_output", dn, "instances_s*", "*.json"))):
            d = json.load(open(f, encoding="utf-8"))
            iid = d["instance_id"]
            text0 = INSTANCES[iid]["fixture"]["article_text"]
            if not d["cycles"]:
                continue
            c1 = d["cycles"][0]
            devs = [s["dev"] for s in c1["stage2_results"] if s.get("dev")]
            c1_claims = {nrm(s["claim_text"]) for s in c1["stage2_results"]}
            enum_locs: list = []
            for dev in devs:
                en = R.deterministic_same_fact_id_location_fallback([dict(dev, same_fact_id_locations=None)], text0)[0]
                for loc in en.get("same_fact_id_locations") or []:
                    ls = (loc or "").strip()
                    if ls and ls in text0 and nrm(ls) not in c1_claims and ls not in enum_locs:
                        enum_locs.append(ls)
            # ① 後cycleの新規BLOCKING
            texts, cur = [], text0
            for c in d["cycles"]:
                texts.append(cur)
                cur = c.get("en_text_after_rewrite", cur)
            regions: list = []
            seen_claims = set(c1_claims)
            new_major, covered = [], []
            for k, c in enumerate(d["cycles"]):
                if k >= 1:
                    for sr in c["stage2_results"]:
                        if sr["materiality"] != "BLOCKING":
                            continue
                        lv, n = R.location_prior_levels(regions, sr, texts[k])
                        txt = sr.get("claim_span_text") or sr["claim_text"]
                        if n == 0 and nrm(sr["claim_text"]) not in seen_claims:
                            new_major.append({"cycle": c["cycle"], "fact": sr["dev"].get("related_fact_id"), "claim": txt[:90]})
                            cn = nrm(txt)
                            if any(len(nrm(l)) >= 15 and (nrm(l) in cn or cn in nrm(l)) for l in enum_locs):
                                covered.append(new_major[-1])
                        seen_claims.add(nrm(sr["claim_text"]))
                if texts[k + 1 if k + 1 < len(texts) else k] != texts[k]:
                    pass
                nxt = c.get("en_text_after_rewrite")
                if nxt and nxt != texts[k]:
                    regions = R.update_regions_after_rewrite(regions, texts[k], c.get("rewrite_records", []), c["cycle"])
            is_normal = iid in R.NORMAL_GROUP_INSTANCE_IDS
            # ② NORMAL群の追加Stage 2判定件数(列挙で増える分)と、記録上BLOCKINGになった件数
            later_block_texts = {nrm(s["claim_text"]) for c in d["cycles"][1:] for s in c["stage2_results"] if s["materiality"] == "BLOCKING"}
            blocked = [l for l in enum_locs if any(nrm(l) in t or t in nrm(l) for t in later_block_texts if t)]
            row = {"rep": rep, "instance_id": iid, "sample": os.path.basename(os.path.dirname(f)), "normal_group": is_normal,
                   "cycle1_stage2_claims": len(c1["stage2_results"]), "enumerated_extra_locations": len(enum_locs),
                   "later_new_major": len(new_major), "later_new_major_covered": len(covered),
                   "extra_locations_observed_blocking": len(blocked), "new_major_detail": new_major, "covered_detail": covered}
            rows.append(row)
            tot["runs"] += 1
            tot["later_new_major"] += len(new_major)
            tot["later_new_major_covered"] += len(covered)
            if is_normal:
                tot["normal_runs"] += 1
                tot["normal_cycle1_stage2_claims"] += len(c1["stage2_results"])
                tot["normal_extra_stage2_judgments"] += len(enum_locs)
                tot["normal_extra_observed_blocking"] += len(blocked)
    ratio = (tot["later_new_major_covered"] / tot["later_new_major"]) if tot["later_new_major"] else None
    out = {"totals": dict(tot), "item1_covered_ratio": ratio,
           "adoption_condition": "①>0(事前固定)", "adoption_condition_met": bool(tot["later_new_major_covered"] > 0),
           "note": ("②のBLOCKING化件数は記録上観測できた分のみ(列挙した箇所が後cycleのBLOCKINGに現れた件数)。列挙した箇所をStage 2へ通した結果の"
                    "実測ではない=不要Rewrite候補の上限推定にはならない(call必要)。"),
           "rows": rows}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"totals": out["totals"], "item1_covered_ratio": ratio,
                      "adoption_condition_met": out["adoption_condition_met"]}, ensure_ascii=False))
    for r in rows:
        if r["later_new_major"] or (r["normal_group"] and r["enumerated_extra_locations"]):
            print(r["rep"], r["sample"], r["instance_id"], "newMAJOR", r["later_new_major"], "covered", r["later_new_major_covered"],
                  "extra", r["enumerated_extra_locations"], "normal" if r["normal_group"] else "")


if __name__ == "__main__":
    main()
