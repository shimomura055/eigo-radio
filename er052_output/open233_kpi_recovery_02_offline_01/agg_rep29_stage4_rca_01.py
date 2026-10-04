# -*- coding: utf-8 -*-
# 委任_10 (OPEN-233-KPI-RECOVERY-REDESIGN-02) 作業1/2の¥0オフライン集計・replay(LLM callなし、runnerは読み込みのみ=編集なし)。
# 実行: .venv/Scripts/python.exe er052_output/open233_kpi_recovery_02_offline_01/agg_rep29_stage4_rca_01.py  (cwd=repo root, PYTHONUTF8=1)
# 出力: agg_rep29_stage4_rca_01.json / agg_rep29_stage4_rca_01_stdout.txt
import json, os, re, sys, glob, collections
sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
import er052_open233_self_recovery_flow_runner_01 as runner

R29 = "er052_output/open233_self_recovery_flow_runner_01_rep29"
out = {}
def load(p): return json.load(open(p, encoding="utf-8"))

# ---------- (1) rep29 3件のspan再解決replay(決定論) ----------
s1 = load(f"{R29}/instances_s1/meta_run03_advanced.json")
s2 = load(f"{R29}/instances_s2/meta_run03_advanced.json")
a4 = load(f"{R29}/instances_s1/safety_A4.json")
rp = {}
# s1 cycle3: STAGE4直前のHC-006 claim(=cycle2のnormal_gap由来の古い文言)を、cycle3開始時点の記事(=cycle2のRewrite後)で解決できるか
c2 = s1["cycles"][1]; c3 = s1["cycles"][2]
claim_s1c3 = [x for x in c3["stage2_results"] if x["related_fact_id"] == "MUSE-HC-006"][0]["claim_text"]
art_s1c3 = c2["en_text_after_rewrite"]
res = runner.resolve_violation_spans(claim_s1c3, art_s1c3, None)
rp["s1_c3_HC006_claim_vs_cycle3_start_article"] = {
    "claim": claim_s1c3, "status": res.get("status"), "reason": res.get("reason"), "level": res.get("level"), "ranges": res.get("ranges"),
    "claim_text_literally_in_article": claim_s1c3.strip("“”") in art_s1c3,
    "stale_phrases_present": {p: (p in art_s1c3) for p in ["had no way to know", "on the other end of the call", "had little way to know", "a human on the call"]}}
# s2 cycle3: composite claim
c2b = s2["cycles"][1]; c3b = s2["cycles"][2]
claim_s2c3 = c3b["stage2_results"][0]["claim_text"]
art_s2c3 = c2b["en_text_after_rewrite"]
res2 = runner.resolve_violation_spans(claim_s2c3, art_s2c3, None)
frags = re.findall(r"“([^”]+)”", claim_s2c3)
frag_res = []
for f in frags:
    rr = runner.resolve_violation_spans(f, art_s2c3, None)
    frag_res.append({"fragment": f, "status": rr.get("status"), "reason": rr.get("reason"), "level": rr.get("level"), "ranges": rr.get("ranges")})
rp["s2_c3_HC006_claim_vs_cycle3_start_article"] = {
    "claim": claim_s2c3, "status": res2.get("status"), "reason": res2.get("reason"),
    "quote_fragments": frag_res,
    "article_equals_original_before_cycle1": s2["cycles"][0]["en_text_before_rewrite"] == art_s2c3}
out["span_replay"] = rp

# ---------- (2) safety_A4 s1 費用内訳 ----------
by_cycle = collections.defaultdict(lambda: collections.defaultdict(float)); n_calls = collections.defaultdict(lambda: collections.Counter())
for cl in a4["call_log"]:
    m = re.search(r"_c(\d)_", cl["label"]); cyc = int(m.group(1)) if m else 0
    stage = cl["recovery_stage"]
    if stage == "stage2_second_judge" and "_s1_" in cl["label"]: stage = "s1_second_opinion"
    if stage == "stage3_rewrite" and "_regen_" in cl["label"]: stage = "stage3_regen(quality_regen)"
    by_cycle[cyc][stage] += cl["cost_jpy"]; n_calls[cyc][stage] += 1
a4cost = {str(k): {s: round(v, 4) for s, v in d.items()} for k, d in by_cycle.items()}
for k in a4cost: a4cost[k]["_cycle_total"] = round(sum(by_cycle[int(k)].values()), 4); a4cost[k]["_n_calls"] = dict(n_calls[int(k)])
tot_stage = collections.defaultdict(float)
for d in by_cycle.values():
    for s, v in d.items(): tot_stage[s] += v
out["a4_cost"] = {"by_cycle": a4cost, "by_stage": {s: round(v, 4) for s, v in tot_stage.items()},
                  "sum_from_call_log": round(sum(c["cost_jpy"] for c in a4["call_log"]), 4), "total_cost_jpy_field": a4["total_cost_jpy"], "n_calls": len(a4["call_log"])}

# ---------- (3) rep27-29 全instance: ladder成功判定とissue解消の乖離、STAGE4理由 ----------
rows = []
stage4 = []
for run in ("rep27", "rep28", "rep29"):
    for p in sorted(glob.glob(f"er052_output/open233_self_recovery_flow_runner_01_{run}/instances_s*/*.json")):
        d = load(p); samp = "s1" if "instances_s1" in p.replace("\\", "/") else "s2"
        if d.get("final_state") == "STAGE4_ESCALATION":
            lv = []
            for c in d["cycles"]:
                for rr in c.get("rewrite_records", []):
                    lv.append((c["cycle"], rr.get("claim_identity"), rr.get("ladder_level_used"), (rr.get("handoff") or {}).get("problem_kind")))
            stage4.append({"run": run, "sample": samp, "instance": d["instance_id"], "reason": d["stage4_reason"], "n_cycles": len(d["cycles"]),
                           "rewrite_levels": lv, "cost": d["total_cost_jpy"]})
        for c in d.get("cycles", []):
            recs = [r for r in c.get("rewrite_records", []) if r.get("guard_ok")]
            sent = c.get("recheck_prior_issues_sent_count")
            res_l = c.get("recheck_prior_issues_resolved") or []
            if len(recs) == 1 and sent == 1 and len(res_l) >= 1 and "recheck_prior_issues_resolved" in c:
                r0 = recs[0]
                rows.append({"run": run, "sample": samp, "instance": d["instance_id"], "cycle": c["cycle"],
                             "level": r0.get("ladder_level_used"), "kind": (r0.get("handoff") or {}).get("problem_kind"),
                             "resolved": bool(res_l[0].get("resolved"))})
tab = collections.defaultdict(lambda: [0, 0])
for r in rows:
    key = (r["level"], r["kind"]); tab[key][0] += 1; tab[key][1] += int(r["resolved"])
tab_level = collections.defaultdict(lambda: [0, 0])
for r in rows:
    tab_level[r["level"]][0] += 1; tab_level[r["level"]][1] += int(r["resolved"])
out["single_rewrite_cycles"] = {"n": len(rows),
    "by_level": {str(k): {"n": v[0], "resolved": v[1]} for k, v in tab_level.items()},
    "by_level_kind": {f"{k[0]}|{k[1]}": {"n": v[0], "resolved": v[1]} for k, v in tab.items()},
    "note": "recheck_prior_issues_sent_count==1かつ当cycleのguard_ok Rewrite==1件のcycleのみ(index 0=その1件に一意対応)。対象=rep27-29の全instance"}
out["stage4_rows_rep27_29"] = stage4
reason_cnt = collections.Counter((r["run"], r["reason"]) for r in stage4)
out["stage4_reason_by_run"] = {f"{k[0]}|{k[1]}": v for k, v in sorted(reason_cnt.items())}

# ---------- (4) escalated_to_paragraph記録と実ladderの不一致(STAGE4 same_claim_fact_id_reblocked) ----------
mis = []
for r in stage4:
    if r["reason"] == "same_claim_fact_id_reblocked":
        max_lvl = max([{"1_word_connective": 1, "3_sentence": 3, "4_paragraph": 4}.get(x[2], 0) for x in r["rewrite_levels"]] or [0])
        mis.append({"run": r["run"], "sample": r["sample"], "instance": r["instance"], "max_ladder_level_actually_used": max_lvl,
                    "ladder_actually_exhausted_to_level4": max_lvl >= 4})
out["same_claim_reblocked_vs_actual_ladder"] = mis

# ---------- (5) A提案(焦点要素の決定論チェック)の裏取り: level 1成功のbefore/afterに主体語が残存/入替しているか(rep29の3件) ----------
def actor_nouns(t): return sorted(runner.extract_actor_nouns(t))
chk = []
for name, d in (("s1_meta", s1), ("s2_meta", s2), ("s1_A4", a4)):
    for c in d["cycles"]:
        for rr in c.get("rewrite_records", []):
            for la in (rr.get("handoff") or {}).get("level_attempts", []):
                if la.get("result") == "success" and la.get("before_after"):
                    for ba in la["before_after"]:
                        b, a = actor_nouns(ba["before"]), actor_nouns(ba["after"])
                        chk.append({"inst": name, "cycle": c["cycle"], "claim": rr["claim_identity"], "level": la["level"],
                                    "before_actor_nouns": b, "after_actor_nouns": a,
                                    "actor_noun_retained": bool(set(b) & set(a)), "actor_noun_swapped": bool(b) and not (set(b) & set(a)) and bool(a)})
out["actor_focus_check_rep29"] = chk

# ---------- (6) s1 cycle2のprior issue文(L2221のnewline判定)の確認 ----------
rec2 = s1["cycles"][1]["rewrite_records"][0]
own2 = runner.collect_replaced_units(rec2, rec2["claim_identity"])
cur2, src2 = runner.resolve_prior_issue_text("orig", rec2, own2, s1["cycles"][1]["en_text_after_rewrite"], None)
out["s1_c2_prior_issue_text"] = {"cur": cur2, "source": src2, "contains_newline": chr(10) in cur2,
    "l2221_replacement_skipped": chr(10) in cur2, "n_after_units": len(own2[0]["after_units"]) if own2 else 0}
json.dump(out, open("er052_output/open233_kpi_recovery_02_offline_01/agg_rep29_stage4_rca_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
