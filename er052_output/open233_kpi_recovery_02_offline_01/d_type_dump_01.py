# -*- coding: utf-8 -*-
# 委任_01 作業3(¥0): (d)型5件の入力一式(Checker出力・記事・Ledger fact・P-strict-closedの棄却箇所)を吐き出す。
import importlib.util, json, os, sys, re
sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
HERE = "er052_output/open233_span_restore_offline_01"
spec = importlib.util.spec_from_file_location("replay_01_x", f"{HERE}/replay_01.py")
rep = importlib.util.module_from_spec(spec); sys.modules["replay_01_x"] = rep; spec.loader.exec_module(rep)
runner = rep.runner
import glob
OUT = "er052_output/open233_kpi_recovery_02_offline_01"
rows = rep.collect()
uniq = {}
for r in rows:
    k = (r["claim"], r["en"])
    u = uniq.setdefault(k, dict(r, occ=[]))
    u["occ"].append(f"{r['file']}:{r['instance']}:c{r['cycle']}")
fx = {i["instance_id"]: i["fixture"] for i in runner.build_target_instances()}
dump = []
for (claim, en), u in uniq.items():
    base = runner._resolve_claim_string(claim, en, None)
    if base["status"] == "resolved":
        continue
    l6 = rep.l6_restore(claim, en)
    t = rep.classify_unresolved(claim, {"reason": base.get("reason")}, l6, u.get("detected_by"))
    if not t.startswith("d_"):
        continue
    # related_fact_idをinstance JSONから取得
    iid = u["instance"]
    fid = None
    for f in glob.glob("er052_output/open233_self_recovery_flow_runner_01*/instances*/%s.json" % iid):
        d = json.load(open(f, encoding="utf-8"))
        for c in d.get("cycles", []):
            for sr in c.get("stage2_results", []):
                if (sr.get("claim_text") or "") == claim:
                    fid = sr.get("related_fact_id")
                    dev = sr.get("dev") or {}
    ledger = fx[iid]["ledger_text"]
    fact = None
    if fid:
        m = re.search(r"(?ms)^\[VERIFIED\] %s:.*?(?=^\[VERIFIED\]|\Z)" % re.escape(fid), ledger)
        fact = m.group(0).strip() if m else None
    es = base.get("explain_split") or {}
    dump.append({"claim": claim, "issue": u.get("issue"), "related_fact_id": fid, "instance": iid, "occ": u["occ"],
                 "type": t, "p_reason": es.get("reason"), "fragments": es.get("fragments"), "dropped_remainders": es.get("dropped_remainders"),
                 "l6_status": l6.get("status") if isinstance(l6, dict) else None, "l6_reason": (l6 or {}).get("reason"),
                 "fact": fact, "flags": {k: v for k, v in (dev or {}).items() if k.startswith("changed_") or k == "unsupported_new_claim"} , "article": en})
json.dump(dump, open(f"{OUT}/d_type_dump_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(dump))
for i, r in enumerate(dump, 1):
    print("=" * 30, i, r["instance"], r["occ"][:2], r["p_reason"], r["l6_status"], r["l6_reason"])
    print("claim:", r["claim"]); print("issue:", r["issue"]); print("fid:", r["related_fact_id"])
    print("fragments:", r["fragments"]); print("remainders:", r["dropped_remainders"])
    print("fact:", (r["fact"] or "")[:700])
