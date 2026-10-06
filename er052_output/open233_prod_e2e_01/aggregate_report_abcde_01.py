# -*- coding: utf-8 -*-
"""OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 委任_02: 報告A〜E集計script。
標準ライブラリのみ。API呼び出しなし(0円)。保存run jsonと任意のラベルjsonだけを読む(read-only)。
旧9 run(frozen)に適用した結果は『比較基準値』であり、新仕様のEvidenceではない。
欠損フィールドはMISSINGとして扱い、推測ラベルは新規に付けない(ラベルは--labelsの外部jsonのみ、無ければUNLABELED)。"""
import argparse, csv, glob, json, os, re, sys, unicodedata
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser()
ap.add_argument("--runs-dir", required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--labels", default=None)
ap.add_argument("--aggregate-json", default=None, help="旧e2e_aggregate.json(safety欄の参照用、省略時はruns-dir/../e2e_aggregate.json)")
ap.add_argument("--spec-note", default="旧仕様9 run(frozen)・比較基準値・新仕様のEvidenceではない")
args = ap.parse_args()
UNL = "UNLABELED"
LEDGERS = {"meta": "er019_output/family_x_refresh_e2e_01/meta/run_03/ledger/verified_fact_ledger.txt",
           "hormuz": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_01/research_ledger/verified_fact_ledger.txt"}
# 費用stage分類(call_logのrecovery_stage)。新仕様のstage1_reclassifyはCheckerへ含める
STAGE_GROUP = {"stage1_initial": "checker", "stage1_reclassify": "checker", "stage2_second_judge": "downstream",
               "floor_verify": "downstream", "stage3_rewrite": "rewrite", "stage1_recheck": "rewrite", "stage1_exit_check": "rewrite"}


def norm(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", s)).strip()


def fam(inst):
    i = inst.lower()
    if "meta" in i or "safety_a4" in i or "safety_a5" in i or "bgroup_b4" in i:
        return "meta"
    if "hormuz" in i or "a2a3" in i or "bgroup_b3" in i:
        return "hormuz"
    return None


_L = {}


def ledger_text(inst, fid):
    f = fam(inst)
    if not f or not fid or not os.path.exists(LEDGERS[f]):
        return ""
    if f not in _L:
        b, cur = {}, None
        for ln in open(LEDGERS[f], encoding="utf-8").read().splitlines():
            m = re.match(r"^\[(?:VERIFIED\] )?([A-Z]+-[A-Z0-9-]+)[\]:]", ln)
            if m:
                cur = m.group(1)
                b[cur] = [ln]
            elif cur:
                b[cur].append(ln)
        _L[f] = {k: "\n".join(v) for k, v in b.items()}
    return _L[f].get(fid, "")[:600]
def load_runs(d):
    out = {}
    for p in sorted(glob.glob(os.path.join(d, "**", "*.json"), recursive=True)):
        if "_aborted" in p:
            continue
        j = json.load(open(p, encoding="utf-8"))
        if isinstance(j, dict) and "cycles" in j and "call_log" in j:
            out[os.path.splitext(os.path.basename(p))[0]] = j
    return out


LAB = defaultdict(list)
LABEL_SRC = Counter()
if args.labels:
    for e in json.load(open(args.labels, encoding="utf-8"))["labels"]:
        LAB[(e["run"], norm(e["claim"]))].append(e)


def get_label(run, cyc, claim, field):
    es = LAB.get((run, norm(claim)), [])
    for e in es:
        if e.get("cycle") in (cyc, None) and e.get(field) not in (None, ""):
            LABEL_SRC[e.get("label_source", "?")] += 1
            return e[field]
    return UNL


def cand_classes(d):
    """union_candidatesをclaim単位(norm)で集約し AI/機械 を判定。AI=model_r3/model_r5由来、機械=deterministic/coverage_gap/precheck。"""
    cl = {}
    cov = d.get("stage1_coverage") or {}
    for u in cov.get("union_candidates", []):
        k = norm(u["claim_text"])
        e = cl.setdefault(k, {"claim": u["claim_text"], "ai": False, "mach": False, "mach_kinds": set(), "fids": set(), "flags": set()})
        srcs = u.get("sources", [])
        subs = u.get("sub_reasons", [])
        if any(s.startswith("model") for s in srcs):
            e["ai"] = True
        for s in srcs + subs:
            if s == "deterministic" or "coverage_gap" in s or "precheck" in s or s.endswith("_mismatch") or s == "quote_not_in_ledger":
                e["mach"] = True
                e["mach_kinds"].add(s)
        e["fids"] |= set(u.get("related_fact_ids") or [])
        e["flags"] |= {f for f, v in (u.get("flags") or {}).items() if v}
        for kk in u:
            if "reclass" in kk.lower():
                e["reclass_field"] = u[kk]
    return cl, cov
def floor_kinds(fr):
    if not fr:
        return []
    if fr.startswith("deterministic_floor:"):
        return fr.split(":", 1)[1].split(",")
    return [fr]


def lab_count(vals):
    c = Counter(vals)
    return {"Y": c.get("Y", 0), "N": c.get("N", 0), "UNDECIDABLE": c.get("UNDECIDABLE", 0), UNL: c.get(UNL, 0)}


runs = load_runs(args.runs_dir)
RUN_A, S2, SHEET, RW, HR, COST = {}, [], [], [], [], {}
for run, d in runs.items():
    cl, cov = cand_classes(d)
    ai = {k for k, e in cl.items() if e["ai"]}
    mc = {k for k, e in cl.items() if e["mach"]}
    RUN_A[run] = {"n_union_passed_downstream": len(cl), "ai": len(ai), "machine": len(mc), "ai_only": len(ai - mc), "machine_only": len(mc - ai),
                  "both": len(ai & mc), "total_before_dedup": len(ai) + len(mc), "total_after_dedup": len(ai | mc),
                  "ai_true_problem": lab_count([get_label(run, 1, cl[k]["claim"], "true_problem") for k in ai]),
                  "machine_true_problem": lab_count([get_label(run, 1, cl[k]["claim"], "true_problem") for k in mc]),
                  "mach_kinds": dict(Counter(x for k in mc for x in cl[k]["mach_kinds"])),
                  "reclass_fields_present": sorted({kk for k in cov for kk in [k] if "reclass" in k.lower()} | {"candidate:" + str(e["reclass_field"])[:40] for e in cl.values() if "reclass_field" in e}),
                  "n_union_by_stage1_coverage": cov.get("n_union_candidates", "MISSING")}
    for c in d["cycles"]:
        for r in c.get("stage2_results", []):
            fr = r.get("floor_reason")
            fk = floor_kinds(fr)
            k = norm(r["claim_text"])
            tc = get_label(run, c["cycle"], r["claim_text"], "true_critical")
            S2.append({"run": run, "cycle": c["cycle"], "claim": r["claim_text"], "fact_id": r.get("related_fact_id"), "llm": r.get("llm_materiality"),
                       "final": r.get("materiality"), "floor_reason": fr, "floor_kinds": fk, "floor_fired": bool(fk) and r.get("materiality") == "BLOCKING",
                       "tier0": r.get("tier0"), "basis": r.get("basis"), "ai_cand": cl.get(k, {}).get("ai"), "mach_cand": cl.get(k, {}).get("mach"),
                       "true_critical": tc, "true_problem": get_label(run, 1, r["claim_text"], "true_problem"),
                       "issue": (r.get("dev") or {}).get("issue", "")})
for run, d in runs.items():
    cyc = d["cycles"]
    cl, _ = cand_classes(d)
    for i, c in enumerate(cyc):
        nxt = cyc[i + 1] if i + 1 < len(cyc) else None
        nxt_block = {r.get("related_fact_id") for r in (nxt or {}).get("stage2_results", []) if r.get("materiality") == "BLOCKING"}
        for w in c.get("rewrite_records", []):
            ident = w.get("claim_identity", "")
            fid = ident.split(":", 1)[1] if ident.startswith("fact:") else None
            ctext = (w.get("handoff") or {}).get("checker_claim_text", "")
            RW.append({"run": run, "cycle": c["cycle"], "claim_identity": ident, "claim": ctext, "guard_ok": w.get("guard_ok"), "method": w.get("method"),
                       "ladder_level_used": w.get("ladder_level_used"), "had_next_cycle": nxt is not None,
                       "needs_refix": (fid in nxt_block) if (nxt is not None and fid) else (None if nxt is None else "UNKNOWN_ID"),
                       "rewrite_needed": get_label(run, c["cycle"], ctext, "rewrite_needed"),
                       "rewrite_summary": ((w.get("handoff") or {}).get("level_attempts") or [{}])[-1].get("before_after", "MISSING") if (w.get("handoff") or {}).get("level_attempts") else "MISSING"})
    fs = d.get("final_state", "")
    if fs.startswith("STAGE4") or d.get("stage4_reason"):
        last = cyc[-1]
        rw_last = {w.get("claim_identity"): w for w in last.get("rewrite_records", [])}
        for r in last.get("stage2_results", []):
            if r.get("materiality") != "BLOCKING":
                continue
            fid = r.get("related_fact_id")
            ck = cl.get(norm(r["claim_text"]), {})
            w = rw_last.get("fact:" + str(fid))
            HR.append({"run": run, "final_state": fs, "stage4_reason": d.get("stage4_reason"), "cycle": last["cycle"], "claim_en": r["claim_text"],
                       "ledger_fact_id": fid, "ledger_fact_text": ledger_text(run, fid) or "MISSING(ledger未取得)",
                       "checker_ai": "候補(model)" if ck.get("ai") else ("非候補" if ck else "MISSING"),
                       "checker_machine": ("候補(%s)" % ",".join(sorted(ck.get("mach_kinds", [])))) if ck.get("mach") else ("非候補" if ck else "MISSING"),
                       "downstream_ai_llm_materiality": r.get("llm_materiality"), "downstream_machine_floor": r.get("floor_reason") or "なし",
                       "rewrite": ({"method": w.get("method"), "guard_ok": w.get("guard_ok"), "ladder": w.get("ladder_level_used")} if w else "同cycleにRewrite記録なし"),
                       "recheck": {"overall": last.get("recheck_overall_status", "MISSING"), "all_prior_resolved": last.get("recheck_all_prior_issues_resolved", "MISSING"),
                                   "resolved_by_index": last.get("recheck_prior_issues_resolved_by_index", "MISSING")},
                       "stage4_allowlist_decisions": (d.get("stage4_allowlist") or {}).get("decisions", "MISSING"), "issue": (r.get("dev") or {}).get("issue", "")})
    g = Counter()
    for x in d["call_log"]:
        g[STAGE_GROUP.get(x.get("recovery_stage"), "other")] += x.get("cost_jpy") or 0
    COST[run] = {"total_cost_jpy": d.get("total_cost_jpy"), "call_log_sum": round(sum(g.values()), 4), "n_calls": len(d["call_log"]),
                 "by_group": {k: round(g.get(k, 0), 4) for k in ["checker", "downstream", "rewrite", "other"]},
                 "by_stage": dict(Counter({x.get("recovery_stage", "?"): 0 for x in d["call_log"]}))}
    for x in d["call_log"]:
        COST[run]["by_stage"][x.get("recovery_stage", "?")] = round(COST[run]["by_stage"][x.get("recovery_stage", "?")] + (x.get("cost_jpy") or 0), 4)
def sum_a(key):
    return sum(v[key] for v in RUN_A.values())


def lab_sum(key):
    t = Counter()
    for v in RUN_A.values():
        t.update(v[key])
    return dict(t)


def b_stats(rows):
    ai = Counter(r["llm"] for r in rows)
    fl = [r for r in rows if r["floor_fired"]]
    ai_b = [r for r in rows if r["llm"] == "BLOCKING"]
    kinds = Counter(k for r in fl for k in r["floor_kinds"])
    return {"n_claim_judgments": len(rows),
            "downstream_ai": {"重大(BLOCKING)": ai.get("BLOCKING", 0), "軽微(QUALITY)": ai.get("QUALITY", 0), "問題なし(ACCEPTABLE)": ai.get("ACCEPTABLE", 0)},
            "downstream_ai_posteval": {"真に重大だった(AI重大&Y)": sum(r["true_critical"] == "Y" for r in ai_b), "不要に重大判定(AI重大&N)": sum(r["true_critical"] == "N" for r in ai_b),
                                        "AI重大の判断不能": sum(r["true_critical"] == "UNDECIDABLE" for r in ai_b), "AI重大のUNLABELED": sum(r["true_critical"] == UNL for r in ai_b),
                                        "真に重大だったのに軽微/問題なし(Y&AI非重大)": sum(r["true_critical"] == "Y" and r["llm"] != "BLOCKING" for r in rows)},
            "downstream_machine_floor": {"発火件数": len(fl), "種別内訳": dict(kinds), "AI判定との重複(AIもBLOCKING)": sum(r["llm"] == "BLOCKING" for r in fl),
                                         "機械のみで重大化": sum(r["llm"] != "BLOCKING" for r in fl), "真に重大だった(Y)": sum(r["true_critical"] == "Y" for r in fl),
                                         "不要に重大化(N)": sum(r["true_critical"] == "N" for r in fl), "判断不能": sum(r["true_critical"] == "UNDECIDABLE" for r in fl),
                                         "UNLABELED": sum(r["true_critical"] == UNL for r in fl)}}


A = {"per_run": RUN_A, "total": {"AI候補(claim)": sum_a("ai"), "機械候補(claim)": sum_a("machine"), "AIのみ": sum_a("ai_only"), "機械のみ": sum_a("machine_only"),
     "AIと機械の重複": sum_a("both"), "重複除外前の延べ": sum_a("total_before_dedup"), "重複除外後のChecker総候補(=後段へ渡した件数)": sum_a("total_after_dedup"),
     "AI候補 true_problem": lab_sum("ai_true_problem"), "機械候補 true_problem": lab_sum("machine_true_problem"),
     "機械候補の内訳": lab_sum("mach_kinds"), "再分類前後フィールド": sorted({x for v in RUN_A.values() for x in v["reclass_fields_present"]}) or "MISSING(旧仕様に無し)"}}
B = {"cycle1": b_stats([r for r in S2 if r["cycle"] == 1]), "all_cycles": b_stats(S2)}
n_rw = len(RW)
C = {"Rewrite発生件数(rewrite_records)": n_rw, "guard_ok件数": sum(bool(r["guard_ok"]) for r in RW), "Rewrite発生run数": len({r["run"] for r in RW}), "run総数": len(runs),
     "必要だった": sum(r["rewrite_needed"] == "Y" for r in RW), "不要だった": sum(r["rewrite_needed"] == "N" for r in RW), "判断不能": sum(r["rewrite_needed"] == "UNDECIDABLE" for r in RW),
     "ラベルUNLABELED": sum(r["rewrite_needed"] == UNL for r in RW), "Rewrite後に再修正が必要(同fact次cycleもBLOCKING)": sum(r["needs_refix"] is True for r in RW),
     "再修正判定不能(次cycleなし/ID無)": sum(r["needs_refix"] in (None, "UNKNOWN_ID") for r in RW), "per_run": dict(Counter(r["run"] for r in RW)), "rows": RW}
D = {"human_review_runs": sorted({h["run"] for h in HR}), "n_runs": len({h["run"] for h in HR}), "n_blocking_claims_at_exit": len(HR), "目標": 0, "rows": HR}
agg_p = args.aggregate_json or os.path.join(os.path.dirname(args.runs_dir.rstrip("/\\")), "e2e_aggregate.json")
SAFE = {"source": "MISSING(旧e2e_aggregate.json無し)"}
if os.path.exists(agg_p):
    sf = json.load(open(agg_p, encoding="utf-8")).get("safety", {})
    SAFE = {"source": agg_p, "真の重大Fact見逃し件数(出口)": len(sf.get("critical_miss_at_exit", [])), "重大Fact検出件数(Stage1 M)": sf.get("stage1_detect_M"),
            "n_gold_checks": sf.get("n_gold_checks"), "note": "gold(既知重大)行のみ。gold以外の真重大はラベル無しのため算出不能"}
tot = round(sum(c["total_cost_jpy"] or 0 for c in COST.values()), 4)
grp = {g: round(sum(c["by_group"][g] for c in COST.values()), 4) for g in ["checker", "downstream", "rewrite", "other"]}
E = {"safety": SAFE, "per_run_cost": COST, "total_jpy": tot, "mean_per_run_jpy": round(tot / max(len(COST), 1), 4),
     "group_totals_jpy": {"Checker関連(Stage1初回+再分類)": grp["checker"], "後段判定関連(Stage2+S1+floor_verify)": grp["downstream"],
                          "Rewrite関連(Rewrite+regen+Recheck+出口)": grp["rewrite"], "分離不能(other)": grp["other"]}}
os.makedirs(args.out_dir, exist_ok=True)
REP = {"spec_note": args.spec_note, "n_runs": len(runs), "runs": sorted(runs), "labels_file": args.labels, "label_sources_used": dict(LABEL_SRC),
       "A": A, "B": B, "C": C, "D": D, "E": E}
json.dump(REP, open(os.path.join(args.out_dir, "report_abcde.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=list)
with open(os.path.join(args.out_dir, "label_sheet.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["run", "cycle", "claim_text", "fact_id", "ledger_excerpt", "checker_ai", "checker_machine", "llm_materiality", "floor_reason", "final_materiality",
                "true_problem", "true_critical", "rewrite_needed_fact_level", "label_source", "note_fill_Y_N_UNDECIDABLE"])
    rwk = {(r["run"], r["cycle"], r["claim_identity"]): r["rewrite_needed"] for r in RW}
    for r in S2:
        rn = rwk.get((r["run"], r["cycle"], "fact:" + str(r["fact_id"])), "")
        es = LAB.get((r["run"], norm(r["claim"])), [])
        w.writerow([r["run"], r["cycle"], r["claim"], r["fact_id"], ledger_text(r["run"], r["fact_id"]).replace("\n", " / "), r["ai_cand"], r["mach_cand"], r["llm"],
                    r["floor_reason"] or "", r["final"], r["true_problem"], r["true_critical"], rn, es[0].get("label_source", "") if es else "", ""])


def tbl(rows, hdr):
    return ["| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)] + ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]


def flat(d):
    return [(k, json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in d.items()]


L = ["# 報告A〜E集計(委任_02 / 比較基準値)", "", "**%s**。ラベルは `--labels` の外部jsonのみ(推測ラベルの新規付与なし)。UNLABELEDは未ラベル件数。" % args.spec_note,
     "対象run: %d (%s)" % (len(runs), ", ".join(sorted(runs))), "", "## A. Checker(初回候補、重複はclaim単位=norm)"]
L += tbl(flat(A["total"]), ["項目", "値"]) + ["", "run別:"]
L += tbl([(r, v["ai"], v["machine"], v["ai_only"], v["machine_only"], v["both"], v["total_before_dedup"], v["total_after_dedup"]) for r, v in RUN_A.items()],
         ["run", "AI", "機械", "AIのみ", "機械のみ", "重複", "延べ", "除外後(後段へ)"])
L += ["", "## B. 後段判定(cycle1)"] + tbl([(k, json.dumps(v, ensure_ascii=False)) for k, v in B["cycle1"].items()], ["項目", "値"])
L += ["", "## B. 後段判定(全cycle合算)"] + tbl([(k, json.dumps(v, ensure_ascii=False)) for k, v in B["all_cycles"].items()], ["項目", "値"])
L += ["", "## C. Rewrite"] + tbl(flat({k: v for k, v in C.items() if k != "rows"}), ["項目", "値"])
L += ["", "## D. Human Review(目標0件)", "到達run: %s、出口BLOCKING claim %d件" % (D["human_review_runs"], D["n_blocking_claims_at_exit"]), ""]
for h in HR:
    L += ["- [%s] `%s` fact=%s | Checker AI=%s / 機械=%s | 後段AI=%s / 機械=%s | Rewrite=%s | Recheck=%s | 直接原因=%s" % (h["run"], h["claim_en"][:90], h["ledger_fact_id"], h["checker_ai"], h["checker_machine"],
          h["downstream_ai_llm_materiality"], h["downstream_machine_floor"], json.dumps(h["rewrite"], ensure_ascii=False), json.dumps(h["recheck"], ensure_ascii=False)[:120], h["stage4_reason"])]
L += ["", "## E. Safety・Cost", "Safety: " + json.dumps(SAFE, ensure_ascii=False), ""]
L += tbl([(r, c["total_cost_jpy"], c["call_log_sum"], c["by_group"]["checker"], c["by_group"]["downstream"], c["by_group"]["rewrite"], c["by_group"]["other"]) for r, c in COST.items()],
         ["run", "total_cost_jpy", "call_log合計", "Checker", "後段判定", "Rewrite関連", "other"])
L += ["", "合計 %.3f円 / 1run平均 %.3f円" % (tot, E["mean_per_run_jpy"]), json.dumps(E["group_totals_jpy"], ensure_ascii=False)]
open(os.path.join(args.out_dir, "report_abcde.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("OK", len(runs), "runs; S2 rows", len(S2), "; rewrite", n_rw, "; HR", len(HR), "; total", tot)
