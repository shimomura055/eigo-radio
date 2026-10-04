# 委任_07 作業1-4(¥0): rep28 residual_at_pass の remains_in_final_en=True の中身(目印部分文字列と、最終本文での周辺)を逐語表示。
import json, glob, sys, re
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
import er052_open233_self_recovery_flow_runner_01 as runner
for p in sorted(x.replace("\\", "/") for x in glob.glob("er052_output/open233_self_recovery_flow_runner_01_rep28/instances_s*/*.json")):
    d = json.load(open(p, encoding="utf-8"))
    for df in (d.get("residual_at_pass") or {}).get("defs", []):
        if df.get("remains_in_final_en"):
            print("=====", p.split("rep28/")[1], d.get("final_state"), df["sub_id"], df["related_fact_id"], "| substring:", df["text_substring"])
            print("  ever_blocking_flagged:", df["ever_blocking_flagged"], "same_fact:", df["ever_blocking_flagged_same_fact_id"], "pass_with_residual_unflagged:", df["pass_with_residual_unflagged"])
            c = d["cycles"][-1] if d.get("cycles") else {}
            fin = c.get("en_text_after_rewrite") or c.get("en_text_before_rewrite")
            print("  (final text source:", "en_text_after_rewrite" if c.get("en_text_after_rewrite") else "en_text_before_rewrite/none", ")")
            if fin:
                n = runner._norm_for_residual(fin); s = runner._norm_for_residual(df["text_substring"]); i = n.find(s)
                print("  CONTEXT:", n[max(0, i - 160): i + len(s) + 160])
