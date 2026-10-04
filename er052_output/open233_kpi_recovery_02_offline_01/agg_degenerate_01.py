# -*- coding: utf-8 -*-
# 委任_07 作業1-2(¥0): degenerate_rewrite_output全件(全ログ)と、delete選択の内訳。
import json, glob, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
n = 0
for p in sorted(x.replace("\\", "/") for x in glob.glob("er052_output/open233_self_recovery_flow_runner_01_*/instances*/*.json")):
    try: d = json.load(open(p, encoding="utf-8"))
    except Exception: continue
    if d.get("stage4_reason") != "degenerate_rewrite_output": continue
    n += 1
    run = p.split("/")[1].replace("open233_self_recovery_flow_runner_01_", "")
    print("=====", run, d.get("instance_id"), "final", d.get("final_state"))
    c = d["cycles"][-1]
    for i, r in enumerate(c.get("rewrite_records") or []):
        print("  rec", i, r.get("rewrite_kind"), r.get("mechanism"), "|", r.get("method"), "| section", r.get("section_type"), "| level", r.get("ladder_level_used"),
              "| before:", str(r.get("before_fragment"))[:140], "| after:", str(r.get("after_fragment"))[:100])
    sr = c.get("section_role_violation_after_regen") or c.get("section_role_violation") or {}
    print("  section_role:", {k: v for k, v in sr.items() if "degenerate" in k})
    if c.get("en_text_before_rewrite"):
        print("  BEFORE head:", c["en_text_before_rewrite"][:160].replace("\n", "\n"))
        print("  AFTER  head:", (c.get("en_text_after_rewrite") or "")[:160].replace("\n", "\n"))
print("degenerate_rewrite_output instances:", n)
