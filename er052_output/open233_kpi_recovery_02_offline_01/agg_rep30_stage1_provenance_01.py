# -*- coding: utf-8 -*-
# 委任_06 (CORRECTION-01): rep30 38 instance-runのStage 1区分/model/prompt/schema/Stage2へ渡した件数を集計(API呼び出しなし、read-only)
import json, os, sys, hashlib, datetime
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import er052_open233_self_recovery_flow_runner_01 as runner

D = "er052_output/open233_self_recovery_flow_runner_01_rep30"
OUT = "er052_output/open233_kpi_recovery_02_offline_01/agg_rep30_stage1_provenance_01.json"
insts = {i["instance_id"]: i for i in runner.build_target_instances()}
rows = []
src_cache = {}
for s in (1, 2):
    for fn in sorted(os.listdir(f"{D}/instances_s{s}")):
        r = json.load(open(f"{D}/instances_s{s}/{fn}", encoding="utf-8"))
        iid = r["instance_id"]
        inst = insts[iid]
        mode = inst["stage1_mode"]
        src = inst.get("stage1_source")
        row = {"sample": s, "instance_id": iid, "group": r["group"], "stage1_mode_built": mode,
               "stage1_call_used": r["stage1_call_used"], "substituted": r["stage1_recall_miss_substituted"],
               "s1u_screen_used": r["s1u_screen_used"], "final_state": r["final_state"]}
        if r["stage1_recall_miss_substituted"]:
            row["category"] = "V0-substitute"
        elif mode == "reuse":
            row["category"] = "frozen-reuse"
        else:
            row["category"] = "fresh" if r["stage1_call_used"] else "fresh(cache-shared from s1, 0 call)"
        if mode == "reuse":
            m = json.load(open(src, encoding="utf-8"))
            row["source_path"] = src
            row["source_model"] = m.get("model"); row["source_model_returned"] = m.get("model_returned")
            row["source_variant"] = m.get("variant"); row["source_prompt_sha256"] = m.get("prompt_sha256")
            row["source_mtime"] = datetime.datetime.fromtimestamp(os.path.getmtime(src)).isoformat(timespec="seconds")
            row["source_has_same_fact_id_locations_field"] = any("same_fact_id_locations" in (d or {}) for d in (m.get("raw_parsed", {}).get("deviations") or []))
            row["source_raw_has_enum_schema"] = "same_fact_id_locations" in json.dumps(m.get("raw_parsed", {}), ensure_ascii=False)
            row["source_keys"] = sorted(m.keys())
        else:
            row["model"] = runner.MODEL
            cl = [c for c in r["call_log"] if c.get("recovery_stage") == "stage1_initial"]
            row["fresh_prompt_sha256"] = cl[0].get("prompt_sha256") if cl else None
        if r["stage1_recall_miss_substituted"]:
            fx = inst["fixture"]
            row["substitute_fixture_keys"] = sorted(fx.keys())
            row["substitute_source_hint"] = {k: fx[k] for k in fx if k in ("source", "baseline_source", "audit_path", "origin_path", "note", "path") and isinstance(fx[k], str)}
        raw = r["all_deviations_raw"]["stage1"]
        row["stage1_raw_n"] = len(raw)
        row["stage1_raw_major_n"] = sum(1 for d in raw if d["severity"] == "MAJOR")
        row["stage1_raw_minor_n"] = sum(1 for d in raw if d["severity"] != "MAJOR")
        cyc = r["cycles"][0] if r["cycles"] else None
        if cyc:
            sr = cyc["stage2_results"]
            row["stage2_cycle1_n"] = len(sr)
            row["stage2_cycle1_by_detected_by"] = {}
            for x in sr:
                k = x.get("detected_by") or "?"
                row["stage2_cycle1_by_detected_by"][k] = row["stage2_cycle1_by_detected_by"].get(k, 0) + 1
            row["stage2_cycle1_dev_severity"] = {}
            for x in sr:
                k = (x["dev"] or {}).get("severity")
                row["stage2_cycle1_dev_severity"][str(k)] = row["stage2_cycle1_dev_severity"].get(str(k), 0) + 1
            row["stage2_cycle1_enum_added_n"] = sum(1 for x in sr if (x["dev"] or {}).get("detected_by_enumeration"))
            row["stage2_cycle1_dev_has_severity_final"] = sum(1 for x in sr if "severity_final" in (x["dev"] or {}))
        else:
            row["stage2_cycle1_n"] = 0
        row["claims_stage1_raw"] = [d["claim_in_article"] for d in raw]
        row["claims_stage1_raw_fact"] = [d["related_fact_id"] for d in raw]
        row["claims_stage1_raw_sev"] = [d["severity"] for d in raw]
        row["claims_stage2_cycle1"] = [x["claim_text"] for x in (cyc["stage2_results"] if cyc else [])]
        rows.append(row)

SIX = [("bgroup_B4", "A person can take over when AI alone has trouble"),
       ("bgroup_B4", "People feel differently when they think they are speaking to a machine"),
       ("bgroup_B4", "Names, plans, and private matters are easier to share"),
       ("bgroup_B4", "As AI makes calls and reservations, useful features make people want to know"),
       ("safety_A2A3", "Just after the charge plan disappeared, prices began to fall"),
       ("bgroup_B2_hormuz", "The disappearance of the fee plan did not lead to a large, lasting fall")]
six_out = []
for iid, frag in SIX:
    for r in rows:
        if r["instance_id"] != iid: continue
        in_s1 = [(c, sev, f) for c, sev, f in zip(r["claims_stage1_raw"], r["claims_stage1_raw_sev"], r["claims_stage1_raw_fact"]) if frag.lower().replace("’","'") in c.lower().replace("’","'")]
        in_s2 = [c for c in r["claims_stage2_cycle1"] if frag.lower() in c.lower()]
        six_out.append({"instance_id": iid, "sample": r["sample"], "claim_fragment": frag, "category": r["category"],
                        "source_model": r.get("source_model"), "source_path": r.get("source_path"),
                        "in_stage1_raw": [list(x) for x in in_s1], "in_stage2_cycle1": in_s2})
cnt = {}
for r in rows:
    cnt[r["category"]] = cnt.get(r["category"], 0) + 1
frozen = [r for r in rows if r["category"] == "frozen-reuse"]
fz = {}
for r in frozen:
    k = (r["source_model"], r["source_variant"], r["source_mtime"][:10], r["source_raw_has_enum_schema"])
    fz[str(k)] = fz.get(str(k), 0) + 1
out = {"n_runs": len(rows), "category_counts": cnt, "frozen_by_model_variant_date_enumschema": fz,
       "fresh_runs_with_candidate_config": [(r["sample"], r["instance_id"], r["category"]) for r in rows if r["category"].startswith("fresh")],
       "runner_MODEL": runner.MODEL, "six_claims": six_out, "rows": rows}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ("n_runs", "category_counts", "frozen_by_model_variant_date_enumschema", "fresh_runs_with_candidate_config", "runner_MODEL")}, ensure_ascii=False, indent=1))
for s in six_out: print(json.dumps(s, ensure_ascii=False))

# --- prompt sha再計算(frozen reuseのpromptが「V4A+related_fact_id(+origin)のみ、列挙instruction無し」と一致するか、freshは「+列挙」と一致するか) ---
import er051_open233_checker_trial_variant_01 as trial
import er003_v1_en_direct_vfl_01_generate as vfl01
import hashlib as _h
def _sha(t): return _h.sha256(t.encode("utf-8")).hexdigest()
def _prompt(fx, enum):
    p = trial.build_trial_prompt_template("V4A").format(verified_ledger_text=fx["ledger_text"], article_text=fx["article_text"])
    p += vfl01.RELATED_FACT_ID_INSTRUCTION
    if fx.get("source_article_text") is not None:
        p += vfl01.ORIGIN_INSTRUCTION_TEMPLATE.format(source_article_text=fx["source_article_text"])
    if enum: p += runner.SAME_FACT_ID_ENUMERATION_INSTRUCTION
    return p
chk = []
for r in rows:
    fx = insts[r["instance_id"]]["fixture"]
    if r["stage1_mode_built"] == "reuse":
        a = r["source_prompt_sha256"]
        chk.append({"s": r["sample"], "id": r["instance_id"], "kind": "reuse", "match_no_enum": a == _sha(_prompt(fx, False)), "match_with_enum": a == _sha(_prompt(fx, True))})
    elif r["category"] == "fresh":
        a = r["fresh_prompt_sha256"]
        chk.append({"s": r["sample"], "id": r["instance_id"], "kind": "fresh", "match_no_enum": a == _sha(_prompt(fx, False)), "match_with_enum": a == _sha(_prompt(fx, True))})
out["prompt_sha_check"] = chk
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter((c["kind"], c["match_no_enum"], c["match_with_enum"]) for c in chk))
print([c for c in chk if c["kind"]=="reuse" and not c["match_no_enum"]][:12])
