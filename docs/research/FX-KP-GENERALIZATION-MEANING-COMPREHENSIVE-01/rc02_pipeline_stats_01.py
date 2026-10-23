# ROOT_CAUSE_02 (d): 現行path 15 run(census_items_01.json の run)のgloss/canonicalization/外側retry実績を集計(API 0)
import json, os, collections, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\tensh\eigo-radio"
census = json.load(open(ROOT + r"\docs\research\FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01\census_items_01.json", encoding="utf-8"))
runs = sorted({(c["run"], c["level"]) for c in census})
tot = collections.Counter(); reasons = collections.Counter(); ex = []
for run, lv in runs:
    kd = os.path.join(ROOT, run, lv, "key_phrases")
    gm = os.path.join(kd, "gloss_alignment_runtime_metadata.json")
    cm = os.path.join(kd, "canonicalization_runtime_metadata.json")
    ol = os.path.join(kd, "outer_retry_log.json")
    tot["unit"] += 1
    if os.path.exists(gm):
        g = json.load(open(gm, encoding="utf-8"))
        tot["gloss_units"] += 1
        na = len(g.get("attempts_detail") or [])
        tot["gloss_attempts_total"] += na
        if na > 1: tot["gloss_retry_units"] += 1
        tot["gloss_status_" + str(g.get("final_status"))] += 1
        for k, lst in (g.get("item_log") or {}).items():
            for rec in lst:
                tot["gloss_item_attempts"] += 1
                if rec.get("verdict") != "VALID":
                    tot["gloss_item_invalid"] += 1
                    for r in rec.get("reasons") or []: reasons[r[:60]] += 1
                    ex.append((run.split("/")[-1], lv, k, rec.get("proposed_gloss"), rec.get("reasons")))
                if rec.get("qa") != "PASS": tot["gloss_qa_not_pass"] += 1
                mc = rec.get("machine_check") or {}
                if mc and not mc.get("pass", True): tot["gloss_machine_check_fail_recordonly"] += 1
    if os.path.exists(ol):
        o = json.load(open(ol, encoding="utf-8"))
        n = len(o.get("attempts") or [])
        tot["outer_attempts_total"] += n
        if n > 1: tot["outer_retry_units"] += 1
        for a in o.get("attempts") or []:
            for ca in a.get("canonicalization_attempts") or []:
                tot["canon_attempts_total"] += 1
                if ca.get("status") != "CANONICALIZATION_PASS": tot["canon_attempt_nonpass"] += 1
print(dict(tot)); print(reasons.most_common(10))
for e in ex: print(e)
