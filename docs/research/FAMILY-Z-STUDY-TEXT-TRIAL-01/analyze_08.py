# Trial-08 オフライン分析(API 0)。PREREGISTERED_CRITERIA_08.md の許容集合(Trial-07登録の継承+Tier区分)・基準1〜6を機械的に当てはめる。
#   py analyze_08.py          -> analysis_08.json
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_trial_07 as t7, run_trial_04 as t4, run_trial_08 as t8, analyze_07 as a7
BASE = t8.BASE
INV_REG = {"open_window": {"P21"}, "gift": {"P22", "P30"}, "paw": {"P24"}, "tth": {"P8", "P15"}}      # 登録済み許容集合のうち倒置(INV)のもの(PREREG_08 §2)
def key_para(k): return k.rstrip("b")
def reg_entries(w):
    out = []
    for kind, tab in (("core", a7.CORE[w]), ("either", a7.EITHER[w])):
        for k, key in tab.items():
            out.append(dict(id=k, para=key_para(k), phrase=key, kind=kind, inv=(key_para(k) in INV_REG.get(w, set()))))
    return out
def kind_of(w, rec): return a7.kind_of(w, rec)
def match_reg(w, rec):
    for e in reg_entries(w):
        if e["para"] == rec["para"] and t4._qn(e["phrase"]) in t4._qn(rec["sentence"]): return e
    return None
def reg_fate(w, F):
    """登録済みTier1許容文(非INV)が、この標本のfeaturesに現れたか/適格か/不適格理由"""
    tab = t8.tier_table(F); out = {}
    for e in reg_entries(w):
        if e["inv"]: continue
        hit = [r for r in tab if r["para"] == e["para"] and t4._qn(e["phrase"]) in t4._qn(r["sentence"] or "")]
        out[e["id"]] = dict(kind=e["kind"], present=bool(hit), cls=[r["cls"] for r in hit], eligible=any(r["eligible"] for r in hit), why_not=[r["why_not"] for r in hit])
    return out
def load_new(w):
    n = t8.REEXTRACT.get(w, 0); out = []
    for i in range(1, n + 1):
        p = os.path.join(BASE, f"OUTPUT_08_{w}_r{i}_STEPA_DEV.json")
        out.append(json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None)
    return out
def sample_row(w, run, j, src):
    F = j["features"]; sel, tier = t8.select_tiered(F); old = t7.select_one(F)
    recs = [t8.rec8(f, tier) for f in sel]
    for r in recs:
        m = match_reg(w, r); r["registered"] = (m["id"] if m else None); r["reg_kind"] = (m["kind"] if m else "outside"); r["reg_inv"] = bool(m and m["inv"])
    t1_elig = [f for f in F if t7.eligible7(f) and not t8.is_inv(f)]; t2_elig = [f for f in F if t7.eligible7(f) and t8.is_inv(f)]
    return dict(run=run, src=src, n_features=len(F), tier=tier, selected=recs, n_selected=len(recs), single_span_ok=all(r.get("single_span_ok") for r in recs),
                trial07_rule_selected=[dict(para=f["para"], cls=t7._cls(f)) for f in old], n_t1_eligible=len(t1_elig), n_t2_eligible=len(t2_elig),
                t1_eligible=[dict(para=f["para"], cls=t7._cls(f), sentence=f["sentence"][:80]) for f in sorted(t1_elig, key=t7._order_key)],
                inv_eligible=[dict(para=f["para"], sentence=f["sentence"][:80]) for f in t2_elig],
                reg_fate=reg_fate(w, F), parse_error=bool(j.get("parse_error")), cross_para=sum(1 for f in F if f.get("cross_para_flag")),
                cost=(j.get("usage") or {}).get("cost_jpy_at_160") if src == "new" else None, table=t8.tier_table(F))
def analyze():
    out = {}
    for w in t8.WORKS8:
        rows = [sample_row(w, f"r{i}", j, "old") for i, j in enumerate(t8.load07(w), 1)]
        new = [sample_row(w, f"r{i}", j, "new") for i, j in enumerate(load_new(w), 1) if j]
        r = dict(old=rows, new=new, expected_new=t8.REEXTRACT.get(w, 0))
        allrows = new if new else rows            # 判定用: 再抽出した作品は新抽出、それ以外は既存抽出(順位変更のみの効果)
        r["judged_src"] = "new" if new else "old"
        has_core = bool(a7.CORE[w])
        c1 = all(not (s["n_t1_eligible"] > 0 and any(x["feature_class"] == "INV" for x in s["selected"])) for s in allrows)
        c2 =all(all(x["reg_kind"] != "outside" for x in s["selected"]) for s in allrows)
        r["c1_priority_ok"] = c1
        r["c2_no_forced_selection"] = c2 if w != "melos" else None
        r["c2_melos_inherited_outside"] = [dict(run=s["run"], sel=[(x["para"], x["sentence"][:50]) for x in s["selected"]]) for s in allrows if w == "melos" and s["selected"]]
        inv_sel = [s for s in allrows if any(x["feature_class"] == "INV" for x in s["selected"])]
        r["c3_inv_retained"] = [dict(run=s["run"], para=[x["para"] for x in s["selected"]], reg_inv_ok=all(x["reg_inv"] for x in s["selected"]),
                                     reg_tier1_fate={k: (v["present"], v["eligible"], v["why_not"]) for k, v in s["reg_fate"].items()}) for s in inv_sel]
        r["c3_ok"] = all(all(x["reg_inv"] for x in s["selected"]) and not s["n_t1_eligible"] for s in inv_sel)
        r["c4a_zero_with_core"] = [s["run"] for s in allrows if has_core and not s["selected"] and w != "melos"]
        core_nonInv = [e for e in reg_entries(w) if e["kind"] == "core" and not e["inv"]]
        r["c4b_core_nonInv_present"] = {e["id"]: dict(old=sum(1 for s in rows if s["reg_fate"][e["id"]]["present"]), old_n=len(rows), new=sum(1 for s in new if s["reg_fate"][e["id"]]["present"]), new_n=len(new)) for e in core_nonInv}
        r["c5_max1"] = all(s["n_selected"] <= 1 for s in allrows)
        r["c6_single_span"] = all(s["single_span_ok"] for s in allrows)
        r["parse_errors"] = sum(1 for s in allrows if s["parse_error"])
        r["n_ok"] = (len(new) == r["expected_new"]) if r["expected_new"] else True
        r["cost"] = round(sum((s["cost"] or 0) for s in new), 4)
        r["rule_pass"] = bool(c1 and (c2 if w != "melos" else True) and r["c5_max1"] and r["c6_single_span"] and not r["c4a_zero_with_core"] and r["parse_errors"] == 0 and r["n_ok"] and r["c3_ok"])
        out[w] = r
    out["_all_pass"] = all(out[w]["rule_pass"] for w in t8.WORKS8)
    out["_total_cost"] = round(sum(out[w]["cost"] for w in t8.WORKS8), 4)
    json.dump(out, open(os.path.join(BASE, "analysis_08.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out
if __name__ == "__main__":
    o = analyze()
    for w in t8.WORKS8:
        r = o[w]; print("==", w, "judged", r["judged_src"], "pass", r["rule_pass"], "c1", r["c1_priority_ok"], "c2", r["c2_no_forced_selection"], "c3", r["c3_ok"], "c4a", r["c4a_zero_with_core"], "c4b", r["c4b_core_nonInv_present"])
        for s in r["old"] + r["new"]:
            print("  ", s["src"], s["run"], s["tier"], [(x["para"], x["feature_class"], x["reg_kind"]) for x in s["selected"]], "T1elig", s["n_t1_eligible"], "T2elig", s["n_t2_eligible"], "07rule", s["trial07_rule_selected"])
    print("ALL_PASS", o["_all_pass"], "COST", o["_total_cost"])
