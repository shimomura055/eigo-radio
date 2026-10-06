"""critical_trace.md生成(委任_07、¥0)。true_critical=Yの各claimについて Stage1→再分類→Stage2→S1→Rewrite→次cycle→出口 を抽出。"""
import json
import os
import unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
labs = json.load(open(os.path.join(BASE, "labels", "labels_merged.json"), encoding="utf-8"))["labels"]


def norm(s):
    return unicodedata.normalize("NFKC", s or "").lower().strip()


out = ["# critical_trace(true_critical=Y、委任_07)", ""]
for e in labs:
    if e["true_critical"] != "Y":
        continue
    run = e["run"]
    d = json.load(open(os.path.join(BASE, "runs", run + ".json"), encoding="utf-8"))
    n = norm(e["claim"])
    out += ["## %s cycle%s fact=%s label_source=%s" % (run, e["cycle"], e.get("fact_id"), e.get("label_source")), "- claim: %s" % e["claim"], "- label reason: %s" % e["reason"],
            "- run final_state=%s、cycles=%d、stage4_reason=%s" % (d["final_state"], len(d["cycles"]), d.get("stage4_reason"))]
    verd = [v for v in (d.get("stage1_coverage", {}).get("candidate_filter", {}).get("verdicts") or []) if norm(v.get("claim")) == n]
    for v in verd:
        out.append("- Stage1再分類(初回): verdict=%s excluded=%s failclosed=%s reason=%s" % (v.get("verdict"), v.get("excluded"), v.get("failclosed"), (v.get("reason") or "")[:120]))
    if not verd:
        out.append("- Stage1再分類(初回): 該当verdictなし(初回filter非対象 or claim文字列不一致)")
    for c in d["cycles"]:
        for r in c["stage2_results"]:
            if norm(r["claim_text"]) == n:
                so = r.get("second_opinion") or {}
                out.append("- cycle%d Stage2: detected_by=%s sub_reasons=%s | llm=%s final=%s floor_reason=%s basis=%s kind=%s | S1: second=%s confirmed_downgrade=%s" % (
                    c["cycle"], r.get("detected_by"), (r.get("dev") or {}).get("stage1_coverage", {}).get("sub_reasons"), r.get("llm_materiality"), r.get("materiality"),
                    r.get("floor_reason"), r.get("basis"), r.get("rewrite_kind"), so.get("second_materiality"), so.get("confirmed_downgrade")))
        for w in c.get("rewrite_records", []):
            if norm((w.get("handoff") or {}).get("checker_claim_text")) == n:
                la = ((w.get("handoff") or {}).get("level_attempts") or [{}])[-1]
                out.append("- cycle%d Rewrite: identity=%s guard_ok=%s method=%s ladder=%s before_after=%s" % (c["cycle"], w.get("claim_identity"), w.get("guard_ok"), w.get("method"), w.get("ladder_level_used"), str(la.get("before_after"))[:300]))
    fid = e.get("fact_id")
    later = [(c["cycle"], r["claim_text"], r.get("materiality")) for c in d["cycles"] if c["cycle"] > e["cycle"] for r in c["stage2_results"] if r.get("related_fact_id") == fid]
    for cy, t, m in later:
        out.append("- 後続cycle%d 同fact: \"%s\" -> %s" % (cy, t, m))
    rx = d.get("recheck_exit_check")
    out.append("- recheck_exit_check: %s" % json.dumps(rx, ensure_ascii=False)[:400])
    out.append("")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "critical_trace.md"), "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
