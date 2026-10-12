# Phase D(委任_04) 集計スクリプト(API不使用、JPY0)。凍結planの正解表で shortlist(決定論)/抽出/最終選定を集計する。
import glob, json, os, sys
sys.path.insert(0, ".")
import er030_key_phrase_db_hybrid_core_01 as core
import er064_kp_idiom_trial_01_matcher as M
import er064_kp_idiom_trial_01_pipeline as P
import er064_kp_idiom_trial_01_phase_d_run as R

PD = R.PD
plan = json.load(open(f"{PD}/FROZEN_PLAN_02.json", encoding="utf-8"))
dbs = core.load_group1_dbs()
pats = M.build_pattern_index(dbs)
out = {"shortlist": {}, "extraction": {}, "final": {}}
arts = {a["id"]: a for a in plan["articles"]}
lines = []


def P_(s=""):
    lines.append(s)
    print(s)


# ---------- shortlist 比較(V0/V1+d/V2/V3) ----------
P_("## S. shortlist再現率(決定論、JPY0)  ex=exact件数/targets総数, ex|partial=exactまたはpartial件数")
for aid, a in arts.items():
    t = R.art_text(a)
    base = P.load_base(t)
    st = base["stage1"]
    pc = R.placeholder_cands(base, dbs, pats)
    rc = M.rule_possessive_pattern_candidates(st["sentence_units"], dbs, P._canon_set(st))
    v0 = P.build_variant_shortlist(base, "V0")
    v1 = P.build_variant_shortlist(base, "V1", placeholder_cands=pc)
    v3 = P.build_variant_shortlist(base, "V3", rule_cands=rc)
    res = {}

    def ev(info, tag):
        sl = [c["surface_form"] for c in info["shortlist_info"]["shortlist"]]
        e = R.eval_targets(a["targets"], sl, sl) if a["targets"] else {}
        res[tag] = {"n": len(sl), "exact": sum(v["exact"] for v in e.values()),
                    "partial_or_exact": sum(v["exact"] or v["partial"] for v in e.values()),
                    "total_targets": len(e), "per_target": e,
                    "reserved": [c["surface_form"] for c in info["reserved"]],
                    "overflow": [c["surface_form"] for c in info["reserved_overflow"]]}

    ev(v0, "V0")
    ev(v1, "V1+d")
    ev(v3, "V3")
    for k in range(1, a.get("extract_n", 0) + 1):
        ap = f"{R.extraction_dir(a, k)}/accepted_candidates.json"
        if os.path.exists(ap):
            acc = json.load(open(ap, encoding="utf-8"))["accepted_candidates"]
            ev(P.build_variant_shortlist(base, "V2", placeholder_cands=pc, llm_cands=acc), f"V2_run{k}")
    if a.get("extract_n", 0) == 0:
        ev(P.build_variant_shortlist(base, "V2", placeholder_cands=pc, llm_cands=[]), "V2_noLLM")
    out["shortlist"][aid] = res
    P_(f"- {aid} ({a['level']}, {a['role']}): " + " / ".join(
        f"{k}: ex {v['exact']}/{v['total_targets']} (ex|part {v['partial_or_exact']}), n={v['n']}, resv={v['reserved']}, ovf={v['overflow']}"
        for k, v in res.items()))

# ---------- 抽出 ----------
P_()
P_("## E. 抽出(extractor v3)")
for aid, a in arts.items():
    rs = []
    for k in range(1, a.get("extract_n", 0) + 1):
        p = f"{R.extraction_dir(a, k)}/extract_result.json"
        if os.path.exists(p):
            rs.append(json.load(open(p, encoding="utf-8")))
    if not rs:
        continue
    acc_n = [len(r["accepted"]) for r in rs]
    subj = [sum(1 for s in r["subject_included"] if s) for r in rs]
    out["extraction"][aid] = {
        "accepted_counts": acc_n, "accepted": [r["accepted"] for r in rs], "raw_counts": [r["raw_item_count"] for r in rs],
        "rejected_reasons": [[x["reason"] for x in r["rejected"]] for r in rs],
        "dup": [[x.get("canonical_form") for x in r["duplicate_of_existing"]] for r in rs],
        "containment": [r["containment_duplicates"] for r in rs], "subject_included": subj,
        "reserved_in_v2": [r["reserved_in_v2"] for r in rs], "reserved_overflow": [r["reserved_overflow"] for r in rs],
        "raw_items": [[(i.get("rank"), i["span"], i["transparency"]) for i in r["raw_items"]] for r in rs],
        "cost": sum(r["cost_jpy"] for r in rs)}
    P_(f"- {aid}: raw={[r['raw_item_count'] for r in rs]} accepted={acc_n} (mean {sum(acc_n) / len(acc_n):.2f}) subj={subj}")
    for r in rs:
        P_(f"    run{r['run']}: raw={[(i.get('rank'), i['span'], i['transparency']) for i in r['raw_items']]} -> acc={r['accepted']} "
           f"rej={[(x['reason'], x['span']) for x in r['rejected']]} dup={[x['canonical_form'] for x in r['duplicate_of_existing']]} "
           f"cont={r['containment_duplicates']} reserved={r['reserved_in_v2']} ovf={r['reserved_overflow']}")
nc = [aid for aid, a in arts.items() if a["role"] == "negative_control"]
tot = [n for aid in nc for n in out["extraction"][aid]["accepted_counts"]]
P_(f"- 陰性対照(N1/D6/D5/R3) accepted平均/回 = {sum(tot) / len(tot):.2f} (runs {len(tot)}, 基準<=1) / 記事別: " +
   ", ".join(f"{aid} {sum(out['extraction'][aid]['accepted_counts']) / len(out['extraction'][aid]['accepted_counts']):.2f}" for aid in nc))
out["negctl_extraction_mean"] = sum(tot) / len(tot)

# ---------- 最終選定 ----------
P_()
P_("## F. 最終選定(job単位)")
jobs = sorted(glob.glob(f"{PD}/final/*/*/job_result.json"))
jr = [json.load(open(j, encoding="utf-8")) for j in jobs]
for r in jr:
    aid, v, k = r["id"], r["variant"], r["run"]
    ft = r.get("final_targets", {})
    fx = sum(x["exact"] for x in ft.values())
    fp = sum(x["exact"] or x["partial"] for x in ft.values())
    inval = [s for a_ in r["attempts"] for s in (a_.get("canonicalization_attempt_statuses") or [])]
    out["final"][f"{aid}_{v}_run{k}"] = {
        "final_phrases": r["final_phrases"], "evidence": r["final_evidence"], "llm_ph": r["final_llm_or_placeholder_count"],
        "targets_exact": fx, "targets_partial_or_exact": fp, "n_targets": len(ft), "per_target": ft, "retry": r["retry_used"],
        "retry_cost": r["retry_cost_jpy"], "init_red": r["initial_redundancy_status"], "final_red": r["final_redundancy_status"],
        "canon_statuses": inval, "reserved_selected": r["reserved_selected_count"], "reserved_unselected": r["reserved_unselected_count"],
        "reserved": r["reserved_candidates"], "cost": r["cost_jpy"], "elapsed": r["elapsed_sec"], "stop": r["stop_reason"],
        "final_canon": r["final_canonicalization_status"],
        "src_missing": [a_.get("source_span_missing") for a_ in r["attempts"]]}
    P_(f"- {aid} {v} run{k}: {r['final_phrases']} ev={r['final_evidence']} tgt ex {fx}/{len(ft)} (ex|part {fp}) "
       f"llm/ph={r['final_llm_or_placeholder_count']} reserved={r['reserved_candidates']} "
       f"red={r['initial_redundancy_status']}->{r['final_redundancy_status']} canon={inval} "
       f"srcmiss={[a_.get('source_span_missing') for a_ in r['attempts']]} cost={r['cost_jpy']} t={r['elapsed_sec']}s")

# ---------- 受入判定 ----------
P_()
P_("## J. 受入基準の判定")


def fj(aid, v):
    return [out["final"][k] for k in sorted(out["final"]) if k.startswith(f"{aid}_{v}_run")]


neg = {}
for aid in ("N1", "D6", "D5", "R3"):
    for x in fj(aid, "V2"):
        neg.setdefault(aid, []).append(x["llm_ph"])
P_(f"- 陰性対照(最終5件のllm/placeholder由来件数、run単位): {neg} -> {'PASS' if all(c == 0 for v in neg.values() for c in v) else 'FAIL'}")
out["negctl_final"] = neg
d2s = out["shortlist"]["D2"]
P_(f"- D2 shortlist exact: V0 {d2s['V0']['exact']}/6, V1+d {d2s['V1+d']['exact']}/6, " +
   ", ".join(f"{k} {v['exact']}/6" for k, v in d2s.items() if k.startswith("V2")))
for aid, th in (("D2", 2), ("D3", 2), ("D4", 2)):
    P_(f"- {aid} final (>= {th}件, partial可): V2 " + str([x["targets_partial_or_exact"] for x in fj(aid, "V2")]) +
       " V0 " + str([x["targets_partial_or_exact"] for x in fj(aid, "V0")]))
d3 = out["shortlist"]["D3"]
b1only = {"d3_whisper", "d3_asleep", "d3_loan"}
for k, v in d3.items():
    if k.startswith("V2"):
        P_(f"- D3 shortlist {k}: b1only回復 {[t for t in sorted(b1only) if v['per_target'][t]['exact'] or v['per_target'][t]['partial']]}")
cd = [t["id"] for t in arts["D4"]["targets"] if t.get("cd")]
for tag in ("V0", "V2"):
    for x in fj("D4", tag):
        P_(f"- D4 {tag} CD件数 = {sum(1 for t in cd if x['per_target'][t]['exact'] or x['per_target'][t]['partial'])}")
json.dump(out, open(f"{PD}/analysis_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(f"{PD}/analysis_02.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
