# -*- coding: utf-8 -*-
"""OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01 委任_02a: trigger反実仮想replay(JPY0, LLM呼び出しなし)。
保存済みrun jsonのみを決定論的に集計する。語彙は検出用の近似であり設計の正本ではない。"""
import argparse, glob, json, os, re, collections

LEX = re.compile(
    r"\b(roll(?:ed|s|ing)? ?back|rollback|restor\w*|reinstat\w*|withdr[ae]\w*|withdrew|resum\w*|suspend\w*|"
    r"stop\w*|start\w*|halt\w*|paus\w*|increas\w*|decreas\w*|ris(?:e|es|en|ing)|rose|fall(?:s|ing|en)?|fell|"
    r"expand\w*|shrink\w*|shrank|allow\w*|ban|bans|banned|banning|prohibit\w*|approv\w*|reject\w*|"
    r"add|adds|added|adding|remov\w*|cancel\w*|reviv\w*|put back|bring back|brought back|return\w*|revers\w*|"
    r"not|no|never|nor|neither|without|cannot|none|nothing)\b|n't", re.I)

# runner SAFETY_CRITICAL_CLAIM_DEFS(L9817付近)の期待BLOCKING定義6件(転記)
SC_GOLD = [
    ("bgroup_B3", "B3", "flashy 20% plan", r"\b(so|because|therefore|as a result|led to)\b[^.]{0,40}flashy 20% plan"),
    ("safety_A2A3", "A2A3-0", "repay the money", None),
    ("safety_A4", "A4-0", "completed the exchanges with users", None),
    ("safety_A5", "A5-0", "temporarily put back the feature", None),
    ("bgroup_B4", "B4-a", "take over when AI alone has trouble", None),
    ("neg5_hormuz_div_a2", "B3-same@neg5", "flashy 20% plan",
     r"\b(so|because|therefore|as a result|led to)\b[^.]{0,40}flashy 20% plan"),
]

def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def load_runs(d):
    sub = os.path.join(d, "s1")
    if os.path.isdir(sub):
        d = sub
    return {os.path.splitext(os.path.basename(p))[0]: jload(p) for p in sorted(glob.glob(os.path.join(d, "*.json")))}

def records(runs):
    out = []
    for run, d in runs.items():
        for c in d.get("cycles", []):
            for x in c.get("stage2_results", []):
                s1 = (x.get("dev") or {}).get("stage1_coverage") or {}
                out.append({"run": run, "cycle": c["cycle"], "claim": x["claim_text"],
                            "fact": x.get("related_fact_id"), "sub": s1.get("sub_reasons", []),
                            "llm": x.get("llm_materiality"), "final": x.get("materiality"),
                            "floor": x.get("floor_reason")})
    return out

def trig(r):
    sub = r["sub"]
    nb = r["llm"] != "BLOCKING"
    det = any(s != "model" for s in sub)
    detonly = bool(sub) and all(s != "model" for s in sub)
    lex = bool(LEX.search(r["claim"]))
    return {"T-A": det and nb, "T-B": detonly and nb, "T-C": lex and nb}
SCHEMES = ["T-A", "T-B", "T-C"]

def per_run_table(recs, runs):
    t = {}
    for run, d in runs.items():
        rr = [r for r in recs if r["run"] == run]
        row = {"cycles": len(d.get("cycles", [])), "n_stage2": len(rr)}
        for s in SCHEMES:
            row[s] = sum(1 for r in rr if trig(r)[s])
        t[run] = row
    tot = {"cycles": sum(v["cycles"] for v in t.values()), "n_stage2": sum(v["n_stage2"] for v in t.values())}
    for s in SCHEMES:
        tot[s] = sum(v[s] for v in t.values())
        tot[s + "_per_run"] = round(tot[s] / max(1, len(runs)), 2)
        tot[s + "_per_cycle"] = round(tot[s] / max(1, tot["cycles"]), 2)
        tot[s + "_final_nonblock_basis"] = sum(1 for r in recs if _tf(r, s))
    return t, tot

def _tf(r, s):
    """参考: 最終materiality(floor反映後)が非BLOCKINGの基準"""
    r2 = dict(r); r2["llm"] = r["final"]
    return trig(r2)[s]

def key(run, cycle, claim):
    return "%s|%s|%s" % (run, cycle, claim)

def new_label_join(recs, labels):
    lab = {key(l["run"], l["cycle"], l.get("claim_text") or l["claim"]): l for l in labels["labels"]}
    for r in recs:
        l = lab.get(key(r["run"], r["cycle"], r["claim"]))
        r["sev"] = (l or {}).get("severity_eval") or "(blank)"
        r["crit"] = (l or {}).get("true_critical", "(none)")
        r["label_found"] = l is not None
    return sum(1 for r in recs if r["label_found"])

def breakdown(recs):
    res = {}
    for s in SCHEMES:
        c = collections.Counter()
        for r in recs:
            if trig(r)[s]:
                c["crit_Y" if r["crit"] == "Y" else "UNDECIDABLE" if r["crit"] == "UNDECIDABLE" else
                  "minor" if r["sev"] == "軽微" else "no_problem" if r["sev"] == "問題なし" else "other:" + r["sev"]] += 1
        res[s] = dict(c)
    return res
def old_join(recs, old):
    lab = {key(x["run"], x["cycle"], x["claim"]): x for x in old["rows"]}
    sel = []
    for r in recs:
        x = lab.get(key(r["run"], r["cycle"], r["claim"]))
        if x and r["final"] == "BLOCKING" and (r["floor"] or "").strip():
            r["old_label"] = x["label_RCA_suggested"]; r["old_no"] = x["no"]; r["old_floor"] = x["floor_reason"]
            sel.append(r)
    out = {}
    for lbl in ["正当", "不要", "判断不能"]:
        rr = [r for r in sel if r["old_label"] == lbl]
        out[lbl] = {"n": len(rr), **{s: sum(1 for r in rr if trig(r)[s]) for s in SCHEMES}}
    return len(sel), out, [{"no": r["old_no"], "label": r["old_label"], "claim": r["claim"][:90], "sub": r["sub"],
                            "llm": r["llm"], **trig(r)} for r in sel]

def stagea(d):
    rows = []
    for p in sorted(glob.glob(os.path.join(d, "runs", "*", "*.json"))):
        j = jload(p)
        a = j.get("audit") or {}
        if "union_candidates" not in a:
            continue
        for u in a["union_candidates"]:
            rows.append({"run": os.path.basename(p)[:-5], "stage": os.path.basename(os.path.dirname(p)),
                         "inst": j.get("instance_id"), "claim": u["claim_text"], "sub": u.get("sub_reasons", []),
                         "lex": bool(LEX.search(u["claim_text"])), "det": any(s != "model" for s in u.get("sub_reasons", []))})
    return rows

def sc_gold(rows):
    out = []
    for inst, sid, sub, pat in SC_GOLD:
        m = [r for r in rows if r["inst"] == inst and (sub in r["claim"] or (pat and re.search(pat, r["claim"], re.I)))]
        runs_all = {(r["stage"], r["run"]) for r in rows if r["inst"] == inst}
        out.append({"sub_id": sid, "instance": inst, "runs_with_instance": len(runs_all), "matched_candidates": len(m),
                    "T-C_lex_hit": sum(1 for r in m if r["lex"]), "det_candidate": sum(1 for r in m if r["det"]),
                    "sample": (m[0]["claim"][:100] if m else None)})
    return out
def md_table(head, rows):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]) + "\n"

def main():
    ap = argparse.ArgumentParser()
    for a in ["new-runs", "old-runs", "stagea", "labels", "old-labels", "out-dir"]:
        ap.add_argument("--" + a, required=True)
    a = ap.parse_args()
    nruns, oruns = load_runs(a.new_runs), load_runs(a.old_runs)
    nrec, orec = records(nruns), records(oruns)
    nlab = new_label_join(nrec, jload(a.labels))
    ntab, ntot = per_run_table(nrec, nruns)
    otab, otot = per_run_table(orec, oruns)
    brk = breakdown(nrec)
    hc = [r for r in nrec if r["fact"] == "MUSE-HC-012" and "restored the human concierge" in r["claim"]]
    gold4 = [{"run": r["run"], "cycle": r["cycle"], "fact": r["fact"], "claim": r["claim"][:80], "sub": r["sub"],
              "llm": r["llm"], "final": r["final"], **trig(r)} for r in nrec if r["crit"] == "Y"]
    n_old, old_sum, old_rows = old_join(orec, jload(a.old_labels))
    sa = stagea(a.stagea)
    sa_runs = {(r["stage"], r["run"]) for r in sa}
    sa_sum = {"n_runs": len(sa_runs), "n_candidates": len(sa), "T-C_lex_hit": sum(r["lex"] for r in sa),
              "det_candidates": sum(r["det"] for r in sa)}
    res = {"new": {"per_run": ntab, "total": ntot, "n_labeled_joined": nlab, "label_breakdown": brk},
           "old": {"per_run": otab, "total": otot}, "HC-012": [{**trig(r), "llm": r["llm"], "final": r["final"], "sub": r["sub"]} for r in hc],
           "new_gold4": gold4, "old35_join": {"n": n_old, "by_label": old_sum, "rows": old_rows},
           "stageA": {"summary": sa_sum, "sc_gold": sc_gold(sa)},
           "notes": ["非BLOCKING=llm_materiality!=BLOCKING(後段AI判定)。final(materiality)基準は参考列",
                     "T-B=sub_reasonsが全て決定論種別(model無し)=Stage1 AIはSUPPORTED判定と同値の近似",
                     "語彙は検出用近似で設計の正本ではない。Ledger fact本文は保存jsonに無く、claim_textのみに適用"]}
    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "trigger_replay_01.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    write_md(a.out_dir, res)

def write_md(od, res):
    L = ["# trigger_replay_01 (JPY0、保存データ決定論集計。考察なし)\n"]
    L += ["注記: " + n + "\n" for n in res["notes"]]
    for nm, k in [("(1a) 新9 run", "new"), ("(1b) 旧9 run", "old")]:
        d = res[k]; hd = ["run", "cycles", "stage2件数", "T-A", "T-B", "T-C"]
        rows = [[r, v["cycles"], v["n_stage2"], v["T-A"], v["T-B"], v["T-C"]] for r, v in d["per_run"].items()]
        t = d["total"]; rows.append(["合計", t["cycles"], t["n_stage2"], t["T-A"], t["T-B"], t["T-C"]])
        rows.append(["件/run", "", "", t["T-A_per_run"], t["T-B_per_run"], t["T-C_per_run"]])
        rows.append(["件/cycle", "", "", t["T-A_per_cycle"], t["T-B_per_cycle"], t["T-C_per_cycle"]])
        rows.append(["参考:final非BLOCKING基準", "", "", t["T-A_final_nonblock_basis"], t["T-B_final_nonblock_basis"], t["T-C_final_nonblock_basis"]])
        L += ["\n## " + nm + "\n", md_table(hd, rows)]
    s = res["stageA"]["summary"]
    L += ["\n## (1c) 段階A(Stage 1のみ、候補中の該当件数)\n", md_table(["run数", "候補数", "T-C語彙該当", "決定論由来候補"],
          [[s["n_runs"], s["n_candidates"], s["T-C_lex_hit"], s["det_candidates"]]])]
    b = res["new"]["label_breakdown"]
    L += ["\n## (2) 新9 runラベル済み(結合%d/123)の内訳\n" % res["new"]["n_labeled_joined"],
          md_table(["案", "trigger計", "真に重大Y", "軽微", "問題なし", "UNDECIDABLE", "その他"],
                   [[sc, sum(b[sc].values()), b[sc].get("crit_Y", 0), b[sc].get("minor", 0), b[sc].get("no_problem", 0),
                     b[sc].get("UNDECIDABLE", 0), sum(v for k, v in b[sc].items() if k.startswith("other"))] for sc in SCHEMES])]
    L += ["\n## (3) HC-012 (meta_run03_advanced cycle1)\n", md_table(["案", "triggered", "llm", "final", "sub_reasons"],
          [[sc, h[sc], h["llm"], h["final"], h["sub"]] for h in res["HC-012"] for sc in SCHEMES])]
    L += ["\n## (4a) 新9 run 重大4件\n", md_table(["run", "fact", "sub_reasons", "llm", "final", "T-A", "T-B", "T-C"],
          [[g["run"], g["fact"], g["sub"], g["llm"], g["final"], g["T-A"], g["T-B"], g["T-C"]] for g in res["new_gold4"]])]
    o = res["old35_join"]
    L += ["\n## (4b)(5) 旧35件(結合%d)のラベル別trigger件数\n" % o["n"], md_table(["旧ラベル", "n", "T-A", "T-B", "T-C"],
          [[k, v["n"], v["T-A"], v["T-B"], v["T-C"]] for k, v in o["by_label"].items()])]
    L += ["\n## (4c) 段階A SC gold 6件\n", md_table(["sub_id", "instance", "run数", "一致候補", "T-C語彙該当", "決定論候補", "例"],
          [[g["sub_id"], g["instance"], g["runs_with_instance"], g["matched_candidates"], g["T-C_lex_hit"], g["det_candidate"], g["sample"]]
           for g in res["stageA"]["sc_gold"]])]
    with open(os.path.join(od, "trigger_replay_01.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))

if __name__ == "__main__":
    main()

