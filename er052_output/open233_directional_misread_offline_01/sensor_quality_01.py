# -*- coding: utf-8 -*-
"""OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01 委任_02d: 決定論センサー当たりの質(JPY0、LLM呼出なし、checker関数をimportして呼ぶのみ)。"""
import sys, re, json, glob, os, collections
sys.path.insert(0, ".")
import er052_open233_self_recovery_flow_runner_01 as R
import er052_open233_stage1_coverage_checker_01 as cov

OUT = "er052_output/open233_directional_misread_offline_01"
NEW = "er052_output/open233_prod_e2e_02/runs"
OLD = "er052_output/open233_e2e_acceptance_01/runs/s1"
LABELS = "er052_output/open233_prod_e2e_02/labels/labels_merged.json"
INS = {i["instance_id"]: i for i in R.build_target_instances()}
DET = ("number_not_in_fact", "causal_not_in_fact", "negation_polarity_mismatch")


def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def blocks_of(iid):
    return cov.ledger_fact_blocks(INS[iid]["fixture"]["ledger_text"])


def fact_markers(block):
    """fact側のclaim行(1行目)で否定として数えられた語(legacy / 是正案a)。"""
    line = block.split(chr(10))[0]
    leg = [m for m in cov.NEGATION_MARKERS_JA if m in line]
    s = cov.BENIGN_JA_RE.sub("", line)
    a = [m for m in cov.NEGATION_MARKERS_JA + cov.NEGATION_EXTRA_JA if m in s]
    en = [m.group(0) for m in cov.NEGATION_EN_RE.finditer(line)] if not cov._KANA_RE.search(line[:80]) else []
    return {"legacy": leg, "a": a + en}


def unit_markers(text):
    t = cov.NOT_ONLY_RE.sub(" ", text or "")
    return [m.group(0) for m in cov.NEGATION_EN_RE.finditer(t)] + [m.group(0) for m in cov.UNIT_EN_EXTRA_RE.finditer(t)]


def sense(claim, block):
    """1文×1factブロックに決定論センサーを直接適用。戻り=発火理由と使われたマーカー。"""
    u = {"type": "sentence", "text": claim}
    return {
        "negation_legacy": cov.negation_mismatch(u, [block]),
        "negation_a": cov.negation_mismatch_a(u, [block]),
        "number_not_in_fact": bool(cov.numbers_not_in_facts(claim, block)),
        "causal_not_in_fact": bool(cov.unit_has_causal(u) and not cov.facts_have_causal([block])),
        "unit_neg_markers": unit_markers(claim), "fact_neg_markers": fact_markers(block),
    }

def load_runs(d):
    return {os.path.splitext(os.path.basename(p))[0]: jload(p) for p in sorted(glob.glob(os.path.join(d, "*.json")))}


def records(runs, tag):
    out = []
    for run, d in runs.items():
        for c in d.get("cycles", []):
            for x in c.get("stage2_results", []):
                s1 = (x.get("dev") or {}).get("stage1_coverage") or {}
                out.append({"set": tag, "run": run, "cycle": c["cycle"], "claim": x["claim_text"], "fact": x.get("related_fact_id"),
                            "sub": s1.get("sub_reasons", []), "llm": x.get("llm_materiality"), "final": x.get("materiality"),
                            "floor": x.get("floor_reason"), "dev": x.get("dev") or {}})
    return out


def part_A(new_recs):
    hc = [r for r in new_recs if r["fact"] == "MUSE-HC-012"]
    rows = []
    for r in hc:
        b = blocks_of(r["run"])["MUSE-HC-012"]
        s = sense(r["claim"], b)
        rows.append({"run": r["run"], "cycle": r["cycle"], "claim": r["claim"][:90], "recorded_sub": r["sub"], "llm": r["llm"], **s})
    blk = next(iter([blocks_of("meta_run03_advanced")["MUSE-HC-012"]]))
    ctl = {
        "faithful_rollback": "The company rolled back the human concierge feature for now.",
        "reversed_expanded": "The company expanded the human concierge feature to all users.",
        "reversed_restored": "The company also restored the human concierge feature to the way it had been before, at least for now.",
        "negative_faithful": "The company did not disclose that contractors were making the calls.",
    }
    controls = {k: sense(v, blk) for k, v in ctl.items()}
    return {"hc012_fact_line": blk.split(chr(10))[0], "hc012_records": rows, "controls": controls}


def ledger_has_neg(iid, fid):
    try:
        b = blocks_of(iid).get(fid)
    except KeyError:
        return None
    if b is None:
        return None
    m = fact_markers(b)
    return {"legacy": bool(m["legacy"]), "a": bool(m["a"]), "markers_a": m["a"]}


def part_B(recs, labels):
    lab = {"%s|%s|%s" % (l["run"], l["cycle"], l.get("claim_text") or l["claim"]): l for l in labels["labels"]}
    agg = collections.defaultdict(lambda: {"n_claims": 0, "react": collections.Counter(), "label": collections.Counter()})
    tot = collections.Counter()
    for r in recs:
        k = (r["set"], r["fact"])
        agg[k]["n_claims"] += 1
        for s in r["sub"]:
            if s in DET:
                agg[k]["react"][s] += 1
                tot[(r["set"], s)] += 1
        if any(s in DET for s in r["sub"]) and r["set"] == "new":
            l = lab.get("%s|%s|%s" % (r["run"], r["cycle"], r["claim"]))
            agg[k]["label"][((l or {}).get("severity_eval") or "(blank)") + ("/crit" if (l or {}).get("true_critical") == "Y" else "")] += 1
    rows = []
    for (st, fid), v in agg.items():
        if not v["react"]:
            continue
        inst = next((r["run"] for r in recs if r["set"] == st and r["fact"] == fid), None)
        rows.append({"set": st, "fact": fid, "n_claims": v["n_claims"], "react": dict(v["react"]), "label": dict(v["label"]),
                     "fact_neg": ledger_has_neg(inst, fid) if inst in INS else None})
    rows.sort(key=lambda x: -sum(x["react"].values()))
    return rows, {f"{a}:{b}": n for (a, b), n in tot.items()}

def find_sentence(sub):
    for iid, i in INS.items():
        t = i["fixture"]["article_text"]
        for x in re.split(r"(?<=[.!?])\s+|\n+", t):
            if sub in x:
                return iid, x.strip()
    return None, None


def part_C():
    cases = []
    def add(name, iid, sent, fid, ledger_iid):
        b = blocks_of(ledger_iid).get(fid)
        if b is None or sent is None:
            cases.append({"case": name, "status": "unavailable", "inst": iid, "fact": fid})
            return
        cases.append({"case": name, "inst": iid, "fact": fid, "claim": sent, "fact_line": b.split(chr(10))[0][:110],
                      "comparison_sensor": "none_exists", **sense(sent, b)})
    i, s = find_sentence("temporarily put back the feature")
    add("A5-0 state-change reversal", i, s, "MUSE-HC-012", i)
    i, s = find_sentence("restored the human concierge")
    add("HC-012 restored (new E2E miss)", i, s, "MUSE-HC-012", i)
    i, s = find_sentence("Just after the charge plan disappeared")
    add("K19 transition (HF-009)", i, s, "HF-009", "hormuz_run03_standard")
    i, s = find_sentence("The fee plan left the stage")
    add("K16 transition (HF-009)", i, s, "HF-009", "hormuz_run03_standard")
    add("D61 comparison reversal (synthetic from delegation_60)", "synthetic", "After the plan was withdrawn, oil prices fell.", "HF-009", "hormuz_run03_standard")
    i, s = find_sentence("flashy 20% plan left the stage")
    add("B3 causal (HF-007)", i, s, "HF-007", "hormuz_run03_standard")
    return cases


def part_D(new_recs):
    hits = [r for r in new_recs if "number_not_in_fact" in r["sub"]]
    rows = [{"run": r["run"], "cycle": r["cycle"], "claim": r["claim"][:80], "sub": r["sub"], "changed_number": bool(r["dev"].get("changed_number")),
             "floor": r["floor"], "llm": r["llm"], "final": r["final"]} for r in hits]
    return {"n_new_records": len(new_recs), "n_number_not_in_fact": len(hits),
            "n_changed_number_true": sum(1 for x in rows if x["changed_number"]),
            "n_floor_deterministic": sum(1 for x in rows if x["floor"]), "rows": rows}


def per_record_neg_split(recs):
    """negation_polarity_mismatch反応を『fact行に否定語(是正案a)あり/なし』で分ける。"""
    c = collections.Counter()
    for r in recs:
        if "negation_polarity_mismatch" not in r["sub"] or r["run"] not in INS:
            continue
        b = blocks_of(r["run"]).get(r["fact"])
        if b is None:
            c[(r["set"], "fact_unknown")] += 1
            continue
        m = fact_markers(b)
        c[(r["set"], "fact_neg_a=" + str(bool(m["a"])) + ",legacy=" + str(bool(m["legacy"])) + ",unit_neg_a=" + str(bool(cov._unit_neg_a(r["claim"]))))] += 1
    return {f"{a}|{b}": n for (a, b), n in c.items()}


def main():
    nr, orr = load_runs(NEW), load_runs(OLD)
    recs = records(nr, "new") + records(orr, "old")
    newr = [r for r in recs if r["set"] == "new"]
    B, tot = part_B(recs, jload(LABELS))
    res = {"A": part_A(newr), "B": {"rows": B, "totals": tot, "neg_split": per_record_neg_split(recs)},
           "C": part_C(), "D": part_D(newr), "n_runs": {"new": len(nr), "old": len(orr)}}
    with open(os.path.join(OUT, "sensor_quality_01.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: res[k] for k in ("B", "D")}, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    main()
