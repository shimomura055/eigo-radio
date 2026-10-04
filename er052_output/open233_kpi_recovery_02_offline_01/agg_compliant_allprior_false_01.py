# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_08 作業3(¥0、Fable評価7): 全ログの「Recheck LEDGER_COMPLIANT ∧ all_prior_issues_resolved=False」の
# 全cycleについて、再確認(recheck_confirm)の最終結果を集計する。再確認でPASS以外(非COMPLIANT・all_prior未解消・deviationあり)に
# なった件数が0なら、件数一致バグによる「取りこぼし経路なし」と判断できる(Opus#13論点4の推奨集計)。
import json, glob, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
OUT = "er052_output/open233_kpi_recovery_02_offline_01"
rows = []
for p in sorted(x.replace("\\", "/") for x in glob.glob("er052_output/open233_self_recovery_flow_runner_01_*/instances*/*.json")):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    run = p.split("/")[1].replace("open233_self_recovery_flow_runner_01_", "")
    for c in d.get("cycles") or []:
        if c.get("recheck_overall_status") == "LEDGER_COMPLIANT" and c.get("recheck_all_prior_issues_resolved") is False:
            cs = c.get("recheck_confirm_overall_status")
            ca = c.get("recheck_confirm_all_prior_issues_resolved")
            cd = c.get("recheck_confirm_deviations")
            recorded = cs is not None
            if not recorded:
                final = "UNRECORDED"
            elif cs == "LEDGER_COMPLIANT" and ca is True and not (cd or []):
                final = "PASS"
            else:
                final = "NON_PASS"
            rows.append({"run": run, "instance": d.get("instance_id"), "cycle": c.get("cycle"),
                         "reconfirmed": c.get("recheck_reconfirmed"), "confirm_status": cs, "confirm_all_prior": ca,
                         "confirm_deviations_n": len(cd or []), "confirm_recorded": recorded, "confirm_final": final,
                         "instance_final_state": d.get("final_state"), "instance_stage4_reason": d.get("stage4_reason"),
                         "n_sent": c.get("recheck_prior_issues_sent_count"),
                         "items": c.get("recheck_prior_issues_resolved")})
cnt = collections.Counter(r["confirm_final"] for r in rows)
print("LEDGER_COMPLIANT∧all_prior=False cycles:", len(rows))
print("再確認の最終結果:", dict(cnt))
print("再確認が記録されている件数:", sum(1 for r in rows if r["confirm_recorded"]), " 未記録:", cnt.get("UNRECORDED", 0))
nonpass = [r for r in rows if r["confirm_final"] == "NON_PASS"]
unrec = [r for r in rows if r["confirm_final"] == "UNRECORDED"]
print("PASS以外(NON_PASS)の件数:", len(nonpass))
for r in nonpass:
    print("  NON_PASS", {k: r[k] for k in ("run", "instance", "cycle", "confirm_status", "confirm_all_prior", "confirm_deviations_n", "instance_final_state", "instance_stage4_reason")})
print("再確認が未記録の件:", len(unrec))
for r in unrec:
    print("  UNRECORDED", {k: r[k] for k in ("run", "instance", "cycle", "reconfirmed", "instance_final_state", "instance_stage4_reason")})
print("by run:", dict(collections.Counter(r["run"] for r in rows)))
json.dump(rows, open(f"{OUT}/agg_compliant_allprior_false_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
