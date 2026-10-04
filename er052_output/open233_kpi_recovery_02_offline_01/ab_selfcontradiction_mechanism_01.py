# -*- coding: utf-8 -*-
# 委任_06 A/B(rep28a)の自己矛盾の機序確認(¥0、記録済みJSONの読み取りのみ)。
# `all_prior_issues_resolved`はTrial `run_recheck`(er003 vfl01と同一式)で `len(resolved)==len(prior_issues) and all(resolved)`。
# 一方 `run_recheck_confirm`(cite-or-release後)は `len>0 and all(resolved)`(件数一致を問わない)。
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
D = "er052_output/open233_self_recovery_flow_runner_01_rep28a"
rows = []
for cfg in "AB":
    for s in (1, 2):
        d = json.load(open(f"{D}/instances_{cfg}_s{s}/neg3_hormuz_prodrunner_b1b.json", encoding="utf-8"))
        c = d["cycles"][0]
        rs = c.get("recheck_prior_issues_resolved") or []
        cs = c.get("recheck_confirm_prior_issues_resolved") or []
        row = {"config": cfg, "sample": s, "prior_issues_sent": c.get("recheck_prior_issues_sent_count"),
               "recheck_returned_items": len(rs), "recheck_indexes": [x.get("index") for x in rs],
               "recheck_resolved_flags": [x.get("resolved") for x in rs],
               "recheck_all_prior": c.get("recheck_all_prior_issues_resolved"),
               "confirm_returned_items": len(cs), "confirm_resolved_flags": [x.get("resolved") for x in cs],
               "confirm_all_prior": c.get("recheck_confirm_all_prior_issues_resolved"),
               "length_mismatch_only": (len(rs) != c.get("recheck_prior_issues_sent_count")) and all(x.get("resolved") for x in rs)}
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))
print("length_mismatch_only count:", sum(1 for r in rows if r["length_mismatch_only"]), "/", len(rows))
json.dump(rows, open(f"{D}/selfcontradiction_mechanism_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
