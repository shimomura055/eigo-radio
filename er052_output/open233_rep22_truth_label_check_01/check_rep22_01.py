# -*- coding: utf-8 -*-
"""OPEN-233-SELF-RECOVERY-TRIAL-01 委任_47: rep22(限定Trial)の記録と正解ラベルの照合(read-only集計)。

LLM/API/TTS/Web Search/Trial再実行は一切なし。標準ライブラリのみ。既存モジュールはimportしない。
出力: 同ディレクトリの results_01.json と cases_01.csv。
照合ロジック(完全一致=空白正規化のみ、sentence-levelのBLOCKING判定=正規化文字列の包含関係)は
委任_46の check_01.py と同一定義。
"""
import csv
import glob
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
ER = os.path.join(ROOT, "er052_output")
P = "open233_self_recovery_flow_runner_01_"
REP22 = os.path.join(ER, P + "rep22")
TARGET = "Also, some calls needed user information to continue."
RESOLVED = ("RESOLVED_REWRITE", "RESOLVED_REWRITE_THEN_DOWNGRADE", "RESOLVED_STAGE2_DOWNGRADE", "ACCEPTABLE_STAGE1")
# runner の SAFETY_CRITICAL_CLAIM_DEFS["meta_run03_standard"] を逐語で転記(runner 5676-5681行)
META_DEFS = [{"sub_id": "Meta-1", "related_fact_id": "MUSE-HC-010", "text_substring": "needed user information to continue"},
             {"sub_id": "Meta-2", "related_fact_id": "MUSE-HC-012", "text_substring": "needed user information to continue"}]
CURLY = {"’": "'", "‘": "'", "“": '"', "”": '"'}
FLAGS = ["changed_fact", "changed_scope", "changed_causality", "changed_certainty", "changed_number", "changed_actor",
         "changed_negation", "changed_comparison", "changed_time", "unsupported_new_claim", "auto_downgraded"]


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def strip_q(s):
    s = (s or "").strip()
    if len(s) >= 2 and ((s[0] == "“" and s[-1] == "”") or (s[0] == '"' and s[-1] == '"')):
        return s[1:-1].strip()
    return s


def nl(s):
    return "".join(CURLY.get(c, c) for c in ws(strip_q(s))).lower()


def sentences(text):
    out = []
    for para in re.split(r"\n\s*\n", text):
        p = para.strip()
        if not p:
            continue
        if p.startswith("#"):
            out.append(p)
        else:
            out.extend(x for x in re.split(r"(?<=[.!?])\s+", p) if x)
    return out


def load(p):
    return json.load(open(p, encoding="utf-8"))


def final_en(d, orig):
    for c in reversed(d["cycles"]):
        if c.get("en_text_after_rewrite") is not None:
            return c["en_text_after_rewrite"]
    return orig


def related(claim, target_n):
    cn = nl(claim)
    return len(cn) >= 12 and (cn in target_n or target_n in cn)


def meta_row(label, path, d, is_new):
    cy = d["cycles"]
    orig = cy[0]["en_text_before_rewrite"] if cy and cy[0].get("en_text_before_rewrite") is not None else None
    ft = final_en(d, orig)
    present = TARGET in ws(ft) if ft else None
    present_in_orig = TARGET in ws(orig) if orig else None
    tn = nl(TARGET)
    sent_block, sent_nonblock, fact_block, defs_eval = [], [], [], []
    for c in cy:
        for s in c["stage2_results"]:
            cl = s["dev"].get("claim_in_article", "") or ""
            frs = [nl(cl)] + [nl(m) for m in re.findall(r"“([^”]+)”", cl)]
            rel = any(related(x, tn) for x in frs)
            if rel:
                (sent_block if s["materiality"] == "BLOCKING" else sent_nonblock).append((c["cycle"], s.get("related_fact_id"), s["materiality"]))
            if s.get("related_fact_id") == "MUSE-HC-010" and s["materiality"] == "BLOCKING":
                fact_block.append(c["cycle"])
            for df in META_DEFS:  # runner detect_safety_critical_misdowngrades と同じ照合(claim_text 部分一致+fact id)
                if df["related_fact_id"] == (s.get("related_fact_id") or "").strip() and df["text_substring"] in (s.get("claim_text") or ""):
                    defs_eval.append({"sub_id": df["sub_id"], "cycle": c["cycle"], "materiality": s["materiality"]})
    final_sent = [x for x in sentences(ft or "") if "user information" in x] if not present else [TARGET]
    resolved = d["final_state"] in RESOLVED
    return {"label": label, "path": path, "is_rep22": is_new, "final_state": d["final_state"], "stage4_reason": d.get("stage4_reason"),
            "n_cycles": len(cy), "total_calls": d.get("total_calls"), "total_cost_jpy": d.get("total_cost_jpy"),
            "sentence_in_original_article": present_in_orig, "sentence_in_final_verbatim": present,
            "final_sentences_with_user_information": final_sent,
            "HC010_BLOCKING_cycles": fact_block, "sentence_level_BLOCKING_cycles": sorted({c for c, _, _ in sent_block}),
            "sentence_level_BLOCKING_detail": sent_block, "sentence_level_nonblocking_detail": sent_nonblock,
            "safety_defs_eval_Meta1_Meta2": defs_eval,
            "target_pattern(原文残存&未指摘&解消)": bool(present and not sent_block and resolved),
            "target_pattern_if_HC010_fact_basis_only": bool(present and not fact_block and resolved)}


def ladder_counts(d):
    cnt = Counter()
    for c in d["cycles"]:
        for r in c.get("rewrite_records", []):
            cnt[r.get("ladder_level_used") or "none"] += 1
    return dict(cnt)


def main():
    out = {}
    # ---------------- 旧方式(固定入力7実行): check_01 の frozen 判定を再現
    fx = load(os.path.join(ER, P + "rep19", "stage1_fixtures", "meta_run03_standard_iter8_cycle1_frozen.json"))
    fx_claims = sorted(nl(x["claim_in_article"]) for x in fx["deviations"])
    old = []
    for dd in sorted(glob.glob(os.path.join(ER, P + "*"))):
        name = os.path.basename(dd).split("_01_", 1)[1]
        if not re.match(r"(iter[5-8]|rep(7|8|9|1\d|2[01]))$", name):
            continue
        for f in sorted(glob.glob(os.path.join(dd, "instances_*", "meta_run03_standard.json"))):
            d = load(f)
            cy = d.get("cycles") or []
            if not cy:
                continue
            c1 = sorted(nl(s["dev"]["claim_in_article"]) for s in cy[0]["stage2_results"]
                        if s.get("detected_by") != "precheck" and not s["dev"].get("enumeration_source_claim"))
            if c1 == fx_claims:
                old.append((name + "/" + os.path.basename(os.path.dirname(f)), f, d))
    # ---------------- 新方式 T1
    new_t1 = [("rep22/" + s, os.path.join(REP22, f"instances_{s}", "meta_run03_standard.json")) for s in ("s1", "s2", "s3", "s4")]
    t1 = []
    for lab, f in new_t1:
        d = load(f)
        t1.append((lab, f, d))
    rows_new = [meta_row(l, os.path.relpath(f, ROOT), d, True) for l, f, d in t1]
    rows_old = [meta_row(l, os.path.relpath(f, ROOT), d, False) for l, f, d in old]
    for r, (_, _, d) in zip(rows_new + rows_old, t1 + old):
        r["ladder_level_used_counts"] = ladder_counts(d)
        r["elapsed_seconds"] = d.get("elapsed_seconds")
    out["Q1_T1_new"] = rows_new
    out["Q1_old_fixed_input"] = rows_old
    out["Q1_5_counts"] = {
        "new_T1_n": len(rows_new), "new_T1_target_pattern": sum(r["target_pattern(原文残存&未指摘&解消)"] for r in rows_new),
        "old_n": len(rows_old), "old_target_pattern": sum(r["target_pattern(原文残存&未指摘&解消)"] for r in rows_old),
        "new_T1_sentence_remains_verbatim": sum(bool(r["sentence_in_final_verbatim"]) for r in rows_new),
        "old_sentence_remains_verbatim": sum(bool(r["sentence_in_final_verbatim"]) for r in rows_old),
        "new_T1_BLOCKING_flagged_sentence_level": sum(bool(r["sentence_level_BLOCKING_cycles"]) for r in rows_new),
        "old_BLOCKING_flagged_sentence_level": sum(bool(r["sentence_level_BLOCKING_cycles"]) for r in rows_old),
        "new_T1_final_state_Stage4": sum(r["final_state"] == "STAGE4_ESCALATION" for r in rows_new),
        "old_final_state_Stage4": sum(r["final_state"] == "STAGE4_ESCALATION" for r in rows_old),
        "new_T1_sentence_remains_and_unflagged_regardless_of_final_state": sum(bool(r["sentence_in_final_verbatim"]) and not r["sentence_level_BLOCKING_cycles"] for r in rows_new),
        "old_sentence_remains_and_unflagged_regardless_of_final_state": sum(bool(r["sentence_in_final_verbatim"]) and not r["sentence_level_BLOCKING_cycles"] for r in rows_old),
    }
    # check_01 の results_01.json と突合(旧方式の値)
    r01 = load(os.path.join(ER, "open233_missed_detection_truth_check_01", "results_01.json"))
    prev = {x["run"].replace("\\", "/"): x for x in r01["A5_table"]}
    cmp = []
    for r in rows_old + rows_new:
        key = next((k for k in prev if k.endswith(r["path"].split("open233_self_recovery_flow_runner_01_")[-1].replace("\\", "/"))), None)
        pv = prev.get(key) if key else None
        cmp.append({"label": r["label"], "in_results_01": bool(pv),
                    "match_present": (pv["sentence_in_final_article_verbatim"] == r["sentence_in_final_verbatim"]) if pv else None,
                    "match_flag": (bool(pv["BLOCKING_flag_cycles_sentence_level"]) == bool(r["sentence_level_BLOCKING_cycles"])) if pv else None,
                    "match_state": (pv["final_state"] == r["final_state"]) if pv else None,
                    "match_target_pattern": (pv["target_pattern(原文残存&未指摘&解消)"] == r["target_pattern(原文残存&未指摘&解消)"]) if pv else None})
    out["Q1_crosscheck_with_results_01"] = cmp

    # ---------------- T2
    t2 = []
    for s in ("s1", "s2"):
        f = os.path.join(REP22, f"instances_t2_{s}", "meta_run03_standard_cycle2_repro.json")
        d = load(f)
        en_before, en_after = d["en_text_before"], d["en_text_after"]
        rec = d["rewrite_records"][0]
        la = rec["handoff"]["level_attempts"]
        t2.append({"label": "T2_" + s, "final_state": d["final_state"], "stage4_reason": d["stage4_reason"],
                   "total_calls": d["total_calls"], "total_cost_jpy": d["total_cost_jpy"],
                   "sentence_in_en_before": TARGET in ws(en_before), "sentence_in_en_after_rewrite": TARGET in ws(en_after),
                   "HC010_flagged_in_recheck_en": [x for x in d["recheck_en"]["deviations"] if x.get("related_fact_id") == "MUSE-HC-010"],
                   "recheck_en_status": d["recheck_en"]["overall_status"], "recheck_ja_status": d["recheck_ja"]["overall_status"],
                   "recheck_en_deviations": d["recheck_en"]["deviations"], "recheck_ja_deviations": d["recheck_ja"]["deviations"],
                   "ladder_attempts": [{k: a.get(k) for k in ("level", "targets", "revised", "result")} for a in la],
                   "confirmed_ranges": rec["handoff"]["resolution"]["ranges"],
                   "paragraph_before": [p for p in en_before.split("\n\n") if "They did not realize it" in p],
                   "paragraph_after_rewrite": [p for p in en_after.split("\n\n") if "Meta later" in p or "People could ask" in p]})
    # T2の主体置換ガード検証(runner 423-441行と同じ正規表現・同じ判定)
    pat = re.compile(r"\b(users?|employees?|workers?|staff|contractors?|agents?|executives?|customers?|clients?|spokespeople|spokesperson|engineers?|managers?|officials?|residents?|drivers?|passengers?|patients?|students?|teachers?|analysts?|traders?|investors?|shareholders?)\b", re.I)
    nouns = lambda t: {m.group(0).lower() for m in pat.finditer(t or "")}
    for x in t2:
        a3 = next(a for a in x["ladder_attempts"] if a["level"] == "3_sentence")
        before_target = " ".join(a3["targets"])
        after_target = " ".join(a3["revised"])
        new_words = sorted(nouns(after_target) - nouns(before_target))
        para = x["paragraph_before"][0]
        x["guard_replay"] = {"before_target_actor_nouns": sorted(nouns(before_target)), "after_revised_actor_nouns": sorted(nouns(after_target)),
                              "new_actor_nouns": new_words,
                              "new_words_present_in_same_paragraph_before_rewrite": {w: (w in nouns(para)) for w in new_words},
                              "new_words_inside_confirmed_ranges": {w: any(w in nouns(r) for r in x["confirmed_ranges"]) for w in new_words},
                              "new_words_in_paragraph_but_outside_confirmed_ranges": {w: (w in nouns(para) and not any(w in nouns(r) for r in x["confirmed_ranges"])) for w in new_words},
                              "ledger_text_is_JA_only_so_no_English_actor_noun_in_it(確認はrunner import探索で実施、本スクリプトでは未再検証)": True}
    out["Q4_2_T2"] = t2

    # ---------------- T3
    d3 = load(os.path.join(REP22, "instances_safety_a", "safety_er009_changed_number.json"))
    d3b = load(os.path.join(REP22, "instances_safety_a_run1_before_carry_forward_fix", "safety_er009_changed_number.json"))
    c3 = d3["cycles"][0]
    orig3 = c3["en_text_before_rewrite"]
    fin3 = final_en(d3, orig3)
    out["Q1_T3"] = {"final_state": d3["final_state"], "stage4_reason": d3["stage4_reason"], "n_cycles": len(d3["cycles"]),
                    "instance_in_SAFETY_CRITICAL_CLAIM_DEFS": False,
                    "label_source": "設計書7-1/7-0-iter4: er009_changed_number=BLOCKING(deterministic floor、改竄数値「more than 30 million」、Ledger値F-002「1,300万件超」)",
                    "tampered_phrase_in_original": "more than 30 million" in orig3, "tampered_phrase_in_final": "more than 30 million" in fin3,
                    "final_article": fin3, "original_article": orig3,
                    "BLOCKING_cycles_for_tampered_claim": [c["cycle"] for c in d3["cycles"] for s in c["stage2_results"]
                                                           if "30 million" in (s["dev"].get("claim_in_article") or "") and s["materiality"] == "BLOCKING"],
                    "recheck": [c3.get("recheck_overall_status"), c3.get("recheck_all_prior_issues_resolved")],
                    "total_calls": d3["total_calls"], "total_cost_jpy": d3["total_cost_jpy"],
                    "run1_before_fix": {"final_state": d3b["final_state"], "stage4_reason": d3b["stage4_reason"],
                                        "total_calls": d3b["total_calls"], "total_cost_jpy": d3b["total_cost_jpy"]}}
    s2r = c3["stage2_results"]
    out["Q4_3_carry_forward"] = {
        "preceding": {"claim_identity": c3["rewrite_records"][0]["claim_identity"], "origin": s2r[0].get("detected_by"),
                      "related_fact_id": s2r[0].get("related_fact_id"), "claim_in_article": s2r[0]["dev"]["claim_in_article"],
                      "issue": s2r[0]["dev"]["issue"], "rewrite_hint": s2r[0].get("rewrite_hint"), "materiality": s2r[0]["materiality"], "floor_reason": s2r[0]["floor_reason"]},
        "following": {"claim_identity": c3["rewrite_records"][1]["claim_identity"], "origin": s2r[1].get("detected_by"),
                      "related_fact_id": s2r[1].get("related_fact_id"), "claim_in_article": s2r[1]["dev"]["claim_in_article"],
                      "issue": s2r[1]["dev"]["issue"], "rewrite_hint": s2r[1].get("rewrite_hint"), "materiality": s2r[1]["materiality"], "floor_reason": s2r[1]["floor_reason"]},
        "same_claim_text": s2r[0]["dev"]["claim_in_article"] == s2r[1]["dev"]["claim_in_article"],
        "preceding_rewrite_before_after": c3["rewrite_records"][0]["handoff"]["level_attempts"][0]["before_after"],
        "following_rewrite_method": c3["rewrite_records"][1]["method"],
        "following_level_attempts_count(=Rewrite LLM call数)": len(c3["rewrite_records"][1]["handoff"]["level_attempts"]),
        "following_carry_forward_covered": c3["rewrite_records"][1]["handoff"].get("carry_forward_covered"),
        "recheck_after": [c3.get("recheck_overall_status"), c3.get("recheck_all_prior_issues_resolved")],
        "final_article": fin3}

    # ---------------- Q2: 最終周回のRecheck指摘(s1,s3,s4) + HC-012「They enjoyed AI's convenience」の揺れ
    q2 = []
    for lab, f, d in t1:
        if d["final_state"] != "RESOLVED_REWRITE_THEN_DOWNGRADE":
            continue
        lc = d["cycles"][-1]
        items = []
        for s in lc["stage2_results"]:
            dv = s["dev"]
            items.append({"run": lab, "cycle": lc["cycle"], "related_fact_id": s.get("related_fact_id"), "claim_in_article": dv.get("claim_in_article"),
                          "issue": dv.get("issue"), "checker_severity": dv.get("severity"), "true_flags": [k for k in FLAGS if dv.get(k) is True],
                          "stage2_llm_materiality": s.get("llm_materiality"), "final_materiality": s["materiality"], "floor_reason": s.get("floor_reason"),
                          "floor_cited_materiality": s.get("floor_cited_materiality"), "floor_cited_reason": s.get("floor_cited_reason"),
                          "stage2_route": s.get("stage2_route"), "detected_by": s.get("detected_by"),
                          "llm_BLOCKING_downgraded_by_rule": bool(s.get("llm_materiality") == "BLOCKING" and s["materiality"] != "BLOCKING")})
        q2.append({"run": lab, "final_cycle": lc["cycle"], "recheck_overall_status_of_previous_cycle": d["cycles"][-2].get("recheck_overall_status") if len(d["cycles"]) > 1 else None,
                   "items": items})
    out["Q2_final_cycle_items"] = q2
    out["Q2_n_llm_BLOCKING_downgraded_in_final_cycles"] = sum(i["llm_BLOCKING_downgraded_by_rule"] for r in q2 for i in r["items"])
    # 揺れ: 最終周回の各claim(正規化)が、全meta固定入力実行(旧7+新4)で各cycleにどの重大度だったか
    fluct = {}
    allruns = [(l, d) for l, _, d in t1] + [(l, d) for l, _, d in old]
    keys = sorted({nl(i["claim_in_article"]) for r in q2 for i in r["items"]})
    for k in keys:
        rows = []
        for lab, d in allruns:
            for c in d["cycles"]:
                for s in c["stage2_results"]:
                    cn = nl(s["dev"].get("claim_in_article", "") or "")
                    if cn == k or (len(cn) >= 12 and (cn in k or k in cn)):
                        rows.append({"run": lab, "cycle": c["cycle"], "fact": s.get("related_fact_id"), "materiality": s["materiality"],
                                     "llm": s.get("llm_materiality"), "floor": s.get("floor_reason")})
        fluct[k] = rows
    out["Q2_fluctuation_by_claim"] = fluct

    # ---------------- Q4-1
    q41 = {}
    ana = load(os.path.join(REP22, "analysis_rep22.json"))
    for k, v in ana["rep22"].items():
        q41["rep22/" + k] = {x: v[x] for x in ("final_state", "stage4_reason", "n_cycles", "total_calls", "total_cost_jpy", "ladder_level_used_counts", "first_attempted_levels")}
    q41_old = {}
    for r in rows_old:
        q41_old[r["label"]] = {"final_state": r["final_state"], "stage4_reason": r["stage4_reason"], "n_cycles": r["n_cycles"], "total_calls": r["total_calls"],
                               "total_cost_jpy": r["total_cost_jpy"], "ladder_level_used_counts": r["ladder_level_used_counts"]}
    out["Q4_1_new"] = q41
    out["Q4_1_old"] = q41_old
    out["Q4_1_analysis_rep22_old_method_block"] = ana["old_method_same_fixed_input"]
    out["Q4_1_analysis_totals"] = {"t1_totals": ana["t1_totals"], "rep22_totals": ana["rep22_totals"]}
    out["summary_rep22_safety_critical_misdowngrade_rows"] = load(os.path.join(REP22, "summary_rep22.json"))["parts"]["t1_two_sentence_miss"]["safety_critical_misdowngrade_rows"]

    with open(os.path.join(OUT_DIR, "results_01.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
    cols = ["method", "run", "final_state", "stage4_reason", "n_cycles", "sentence_in_final_verbatim", "HC010_BLOCKING_cycles",
            "sentence_level_BLOCKING_cycles", "target_pattern", "calls", "cost_jpy"]
    with open(os.path.join(OUT_DIR, "cases_01.csv"), "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for meth, rs in (("new_rep22_T1", rows_new), ("old_fixed_input", rows_old)):
            for r in rs:
                w.writerow({"method": meth, "run": r["label"], "final_state": r["final_state"], "stage4_reason": r["stage4_reason"], "n_cycles": r["n_cycles"],
                            "sentence_in_final_verbatim": r["sentence_in_final_verbatim"], "HC010_BLOCKING_cycles": r["HC010_BLOCKING_cycles"],
                            "sentence_level_BLOCKING_cycles": r["sentence_level_BLOCKING_cycles"], "target_pattern": r["target_pattern(原文残存&未指摘&解消)"],
                            "calls": r["total_calls"], "cost_jpy": r["total_cost_jpy"]})
    print(json.dumps({"Q1_5": out["Q1_5_counts"], "n_old": len(rows_old), "Q2_downgraded": out["Q2_n_llm_BLOCKING_downgraded_in_final_cycles"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
