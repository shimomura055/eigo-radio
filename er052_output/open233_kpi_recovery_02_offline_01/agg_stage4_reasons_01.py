# -*- coding: utf-8 -*-
# 委任_05 作業2/3: 既存ログ全体(er052_output/open233_self_recovery_flow_runner_01*/ の instance JSON)で、STAGE4_ESCALATIONの
# stage4_reason別の件数と、unconfirmed_after_reverifyの詳細(再確認結果の型)を集計する。API call 0、JPY0。
import collections, glob, json, os, re

rows = []
for f in sorted(glob.glob("er052_output/open233_self_recovery_flow_runner_01*/**/*.json", recursive=True)):
    if os.sep + "instances" not in f.replace("/", os.sep):
        continue
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(d, dict) or "instance_id" not in d or "final_state" not in d:
        continue
    run = f.replace("\\", "/").split("/")[1].replace("open233_self_recovery_flow_runner_01", "") or "base"
    rows.append((run, f, d))
print("instance files:", len(rows))
by_reason = collections.Counter()
by_run_reason = collections.defaultdict(collections.Counter)
uar = []
for run, f, d in rows:
    fs = d.get("final_state")
    r = d.get("stage4_reason")
    if fs == "STAGE4_ESCALATION":
        by_reason[r] += 1
        by_run_reason[run][r] += 1
    if r == "unconfirmed_after_reverify":
        cyc = d.get("cycles") or []
        last = cyc[-1] if cyc else {}
        uar.append({"run": run, "instance_id": d["instance_id"], "file": f.replace("\\", "/"),
                    "n_cycles": len(cyc), "recheck_overall_status": last.get("recheck_overall_status"),
                    "recheck_all_prior": last.get("recheck_all_prior_issues_resolved"),
                    "confirm_overall_status": last.get("recheck_confirm_overall_status"),
                    "confirm_all_prior": last.get("recheck_confirm_all_prior_issues_resolved"),
                    "confirm_released": last.get("recheck_confirm_cite_or_release_released_count"),
                    "confirm_deviations_recorded": ("recheck_confirm_deviations" in last),
                    "confirm_deviation_count": (len(last.get("recheck_confirm_deviations") or []) if "recheck_confirm_deviations" in last else None),
                    "prior_issue_text_sources": last.get("prior_issue_text_sources"),
                    "recheck_deviations_in_raw": [len(x.get("deviations") or []) for x in (d.get("all_deviations_raw") or {}).get("rechecks", [])] if isinstance(d.get("all_deviations_raw"), dict) else None})
print("STAGE4 reasons (all instance files):", dict(by_reason))
for run, c in by_run_reason.items():
    print(" ", run, dict(c))
print("unconfirmed_after_reverify:", len(uar))
for u in uar:
    print(" ", u["run"], u["instance_id"], "cycles", u["n_cycles"], "recheck", u["recheck_overall_status"], u["recheck_all_prior"],
          "| confirm", u["confirm_overall_status"], u["confirm_all_prior"], "released", u["confirm_released"],
          "| confirm_deviations_recorded", u["confirm_deviations_recorded"], "| recheck_devs", u["recheck_deviations_in_raw"])
json.dump({"n_files": len(rows), "by_reason": dict(by_reason), "by_run_reason": {k: dict(v) for k, v in by_run_reason.items()}, "unconfirmed_after_reverify": uar},
          open("er052_output/open233_kpi_recovery_02_offline_01/agg_stage4_reasons_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
