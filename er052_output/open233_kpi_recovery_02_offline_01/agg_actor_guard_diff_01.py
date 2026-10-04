# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_08 作業3(¥0): 新guard(ag1_strict)の差分0確認。
# 全ログ(er052_output/open233_self_recovery_flow_runner_01_*/instances*/*.json)の level_attempts のうち、
#  (A) 結果が許容(success系)だったRewrite試行全件に新guardを適用 -> 許容->拒否 に変わる件数(0必須)
#  (B) actor_guard_rejected だった試行(7試行)に新guardを適用 -> 拒否->許容 の件数
# 関連factは stage2_results のBLOCKING claim(rewrite_records[i]に対応)の related_fact_id、issueは dev.issue+explanation。
import json, os, glob, collections, sys
sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
import er052_open233_self_recovery_flow_runner_01 as runner

OUT = "er052_output/open233_kpi_recovery_02_offline_01"
fx = {i["instance_id"]: i["fixture"]["ledger_text"] for i in runner.build_target_instances()}
runner.ACTOR_GUARD_MODE = "ag1_strict"

accepted_rows, rejected_rows = [], []
n_files = n_attempts = ledger_missing = 0
for p in sorted(x.replace("\\", "/") for x in glob.glob("er052_output/open233_self_recovery_flow_runner_01_*/instances*/*.json")):
    run = p.split("/")[1].replace("open233_self_recovery_flow_runner_01_", "")
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    if "cycles" not in d:
        continue
    n_files += 1
    iid = d.get("instance_id")
    led = fx.get(iid)
    for c in d.get("cycles") or []:
        blk = [s for s in (c.get("stage2_results") or []) if s.get("materiality") == "BLOCKING"]
        for i, r in enumerate(c.get("rewrite_records") or []):
            h = r.get("handoff") or {}
            cl = blk[i] if i < len(blk) else {}
            dev = cl.get("dev") or {}
            fid = cl.get("related_fact_id") or dev.get("related_fact_id") or ""
            issue = " ".join(str(x) for x in (dev.get("issue"), dev.get("explanation")) if x)
            for a in h.get("level_attempts") or []:
                res = a.get("result")
                targets, revised = a.get("targets") or [], a.get("revised") or []
                if res not in ("success", "actor_guard_rejected") or not targets or len(targets) != len(revised):
                    continue
                n_attempts += 1
                if led is None:
                    ledger_missing += 1
                    continue
                new_ok = True
                dets = []
                for t, rv in zip(targets, revised):
                    dec = runner.actor_rewrite_guard_decision(t or "", rv or "", led, fid, issue)
                    dets.append(dec)
                    new_ok = new_ok and dec["ok"]
                has_new_actor = any(dd["new_classes"] for dd in dets)
                row = {"run": run, "instance": iid, "cycle": c.get("cycle"), "rec_idx": i, "level": a.get("level"),
                       "related_fact_id": fid, "result_in_log": res, "new_guard_ok": new_ok, "has_new_actor_class": has_new_actor,
                       "decisions": [dd["new_classes"] for dd in dets if dd["new_classes"]],
                       "before": " ".join(targets)[:200], "after": " ".join(revised)[:200]}
                (accepted_rows if res == "success" else rejected_rows).append(row)

acc_to_rej = [r for r in accepted_rows if not r["new_guard_ok"]]
rej_to_acc = [r for r in rejected_rows if r["new_guard_ok"]]
print("files:", n_files, " attempts(success/actor_guard_rejected):", n_attempts, " ledger_missing(skipped):", ledger_missing)
print("(A) 許容済みRewrite試行:", len(accepted_rows), " うち新主体クラスを含む:", sum(1 for r in accepted_rows if r["has_new_actor_class"]),
      " 許容->拒否:", len(acc_to_rej))
for r in acc_to_rej:
    print("   !! 許容->拒否", r)
print("(B) 拒否済み(actor_guard_rejected)試行:", len(rejected_rows), " 拒否->許容:", len(rej_to_acc))
for r in rejected_rows:
    print("   ", r["run"], r["instance"], "c", r["cycle"], r["level"], "fid", r["related_fact_id"], "new_guard_ok", r["new_guard_ok"],
          [(p["class"], p["basis"]) for ds in r["decisions"] for p in ds])
by_inst = collections.Counter((r["instance"]) for r in accepted_rows if r["has_new_actor_class"])
print("(A内) 新主体クラスを含む許容試行の内訳:", dict(by_inst))
json.dump({"files": n_files, "attempts": n_attempts, "ledger_missing": ledger_missing,
           "accepted_total": len(accepted_rows), "accepted_with_new_actor": sum(1 for r in accepted_rows if r["has_new_actor_class"]),
           "accepted_to_rejected": acc_to_rej, "rejected_total": len(rejected_rows), "rejected_to_accepted": len(rej_to_acc),
           "rejected_rows": rejected_rows, "accepted_with_new_actor_rows": [r for r in accepted_rows if r["has_new_actor_class"]]},
          open(f"{OUT}/agg_actor_guard_diff_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
