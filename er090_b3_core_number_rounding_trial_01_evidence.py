# -*- coding: utf-8 -*-
"""FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 証跡集計(API 0)。
出力: er090_output/b3_core_number_rounding_trial_01/evidence/{structural_diff_evidence.json, judge_table.json, cost_by_stage.json}
実行: .venv/Scripts/python.exe er090_b3_core_number_rounding_trial_01_evidence.py
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import sys

import er053_b3_annotation_contract_01 as contract
import er053_b3_deterministic_producer_01 as prod
import er053_cost_aggregate_01 as ca
import er053_family_x_factlock_ja_writer_01 as w1
import er090_b3_core_number_rounding_trial_01_overlay as ov
import er090_b3_core_number_rounding_trial_01_run as run

ROOT, RUN_A = run.ROOT, run.RUN_A
EVD = os.path.join(ROOT, "evidence")


def sha_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def structural():
    a = contract.validate_annotated_b3(RUN_A)
    d_after = os.path.join(ROOT, "after")
    a2 = contract.validate_annotated_b3(d_after)           # 契約検証(sha整合)が通ること自体が『注記/sidecar/manifest無改変』の証拠
    story, _ = w1.parse_brief_md(a.annotated_md_text)
    overlay = json.load(open(os.path.join(ROOT, "judge", "A_rep1", "overlay.json"), encoding="utf-8"))
    after_news = ov.apply_to_news_field(a.facts_text, a.constraints_text, overlay, prod.CONS_HEADING, prod.compose_news_field)
    bp = w1.build_r0_prompt(story, a.news_field_text)
    ap = ov.apply_rule8(w1.build_r0_prompt(story, after_news), overlay)
    udiff = [l for l in difflib.unified_diff(bp.split("\n"), ap.split("\n"), "before_r0_prompt", "after_r0_prompt", lineterm="", n=0)]
    added = [l[1:] for l in udiff if l.startswith("+") and not l.startswith("+++")]
    removed = [l[1:] for l in udiff if l.startswith("-") and not l.startswith("---")]
    sel_a = json.load(open(os.path.join(RUN_A, "storyline_b3", "fact_selection_evidence.json"), encoding="utf-8"))
    sel_b = json.load(open(os.path.join(d_after, "storyline_b3", "fact_selection_evidence.json"), encoding="utf-8"))
    files = {}
    for sub in ("research_ledger", "storyline_b3"):
        for dp, _d, fns in os.walk(os.path.join(RUN_A, sub)):
            for fn in fns:
                p = os.path.join(dp, fn)
                rel = os.path.relpath(p, RUN_A).replace("\\", "/")
                q = os.path.join(d_after, rel)
                files[rel] = {"before_sha": run.sha_file(p), "after_sha": run.sha_file(q), "equal": run.sha_file(p) == run.sha_file(q)}
    ev = {
        "selected_fact_ids_before": sel_a.get("selected_fact_ids"), "selected_fact_ids_after": sel_b.get("selected_fact_ids"),
        "selected_fact_ids_equal": sel_a.get("selected_fact_ids") == sel_b.get("selected_fact_ids"),
        "sidecar_numbers_equal": a.sidecar["numbers"] == a2.sidecar["numbers"],
        "sidecar_facts_equal": a.sidecar["facts"] == a2.sidecar["facts"],
        "core_concepts_before": [(c["concept"], c["surfaces"]) for c in ov.core_concepts(a.sidecar)],
        "core_concepts_after": [(c["concept"], c["surfaces"]) for c in ov.core_concepts(a2.sidecar)],
        "annotated_md_sha_equal": a.annotated_md_sha256 == a2.annotated_md_sha256,
        "producer_rule_version": a.manifest.get("rule_version"),
        "storyline_and_facts_text_equal": (a.facts_text == a2.facts_text and a.storyline == a2.storyline),
        "constraints_text_before_after_overlay": [a.constraints_text, ov.apply_to_constraints(a.constraints_text, overlay, prod.CONS_HEADING)],
        "r0_prompt_before_sha": sha_text(bp), "r0_prompt_after_sha": sha_text(ap),
        "r0_prompt_diff_added_lines": added, "r0_prompt_diff_removed_lines": removed,
        "r0_prompt_diff_removed_count": len(removed),
        "r0_prompt_diff_limited_to_overlay_and_rule8": (not removed) and all(
            (l in ov.constraint_lines(overlay)) or (l in ov.RULE8_TEXT.split("\n")) or l == "" for l in added),
        "r0_prompt_actually_used_after_sha": json.load(open(os.path.join(d_after, "ja_writer", "factlock", "r0_meta.json"), encoding="utf-8"))["r0_prompt_sha256"],
        "r0_prompt_actually_used_control_sha": json.load(open(os.path.join(ROOT, "control", "ja_writer", "factlock", "r0_meta.json"), encoding="utf-8"))["r0_prompt_sha256"],
        "r0_prompt_production_before_sha": json.load(open(os.path.join(RUN_A, "ja_writer", "factlock", "r0_meta.json"), encoding="utf-8"))["r0_prompt_sha256"],
        "files": files, "all_b3_ledger_files_equal": all(v["equal"] for v in files.values()),
        "production_modules_sha_unchanged_note": {"w1": run.sha_file(w1.__file__), "w1_recorded_in_production_entry_point": json.load(open(os.path.join(RUN_A, "entry_point.json"), encoding="utf-8"))["ja_writer_module_sha256"]},
    }
    ev["r1_r2_prompt_unchanged_note"] = "R1/R2はR0本文だけを入力にUSER_TMPLを使う(w1 USER_TMPL無改変)。r1/r2のuser_message_sha256はafter/control/Productionで同一構造(本文依存のためshaは異なる)。"
    ev["after_vs_control_r0_prompt_equal"] = ev["r0_prompt_actually_used_after_sha"] == ev["r0_prompt_actually_used_control_sha"]
    ev["control_equals_production_before_prompt"] = ev["r0_prompt_actually_used_control_sha"] == ev["r0_prompt_production_before_sha"]
    os.makedirs(EVD, exist_ok=True)
    run.save_json(os.path.join(EVD, "structural_diff_evidence.json"), ev)
    return ev


def judge_table():
    rows = []
    for tag in ("A_rep1", "A_med", "coffee", "boredom", "semi"):
        o = json.load(open(os.path.join(ROOT, "judge", tag, "overlay.json"), encoding="utf-8"))
        r = json.load(open(os.path.join(ROOT, "judge", tag, "response.json"), encoding="utf-8")) if os.path.exists(os.path.join(ROOT, "judge", tag, "response.json")) else None
        src = o["source"]
        resp = {d["concept"]: d for d in (r["parsed"]["decisions"] if r else [])}
        for e in o["entries"]:
            primary = e["surfaces"][-1]["surface"] if e["surfaces"] else None
            exp = None
            for s in e["surfaces"]:
                exp = exp or run.EXPECTED.get((src, s["surface"]))
            approx = [s["approx"] for s in e["surfaces"]] if e["final_decision"] == ov.DECISION_APPROX else None
            llm_approx = [x.get("approx_surface") for x in resp.get(e["concept"], {}).get("surfaces", [])] if resp else None
            rows.append({"run": tag, "source": src, "concept": e["concept"], "surfaces": [s["surface"] for s in e["surfaces"]], "expected": exp,
                         "llm_decision": e["llm_decision"], "final_decision": e["final_decision"], "downgrade": e["downgrade_reasons"],
                         "final_approx": approx, "llm_approx": llm_approx,
                         "match_expected_final": (exp == e["final_decision"]) if exp else None,
                         "match_expected_llm": (exp == e["llm_decision"]) if exp else None,
                         "boundary": any((src, s["surface"]) in run.BOUNDARY for s in e["surfaces"]),
                         "reason": e["reason"]})
    # v1(format iteration)のA判断(安定性参考)
    v1 = []
    for tag in ("A_rep1", "A_rep2"):
        p = os.path.join(ROOT, "judge_v1_format_iteration", tag, "response.json")
        if os.path.exists(p):
            r = json.load(open(p, encoding="utf-8"))
            v1.append({"run": "v1_" + tag, "decisions": {d["concept"]: d["decision"] for d in r["parsed"]["decisions"]}})
    run.save_json(os.path.join(EVD, "judge_table.json"), {"rows": rows, "v1_prompt_A_decisions": v1})
    return rows


def cost():
    out = {}
    tot = 0.0
    for dp, _d, fns in os.walk(ROOT):
        if "raw_usage_log.jsonl" in fns:
            b = ca.compute_stage_cost_breakdown_multi(os.path.join(dp, "raw_usage_log.jsonl"))
            rel = os.path.relpath(dp, ROOT).replace("\\", "/")
            out[rel] = {"total_jpy": b["total_jpy"], "by_stage_jpy": b["by_stage_jpy"]}
            tot += b["total_jpy"]
    out["_TOTAL_jpy"] = round(tot, 3)
    run.save_json(os.path.join(EVD, "cost_by_stage.json"), out)
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ev = structural()
    print(json.dumps({k: ev[k] for k in ev if k not in ("files", "constraints_text_before_after_overlay")}, ensure_ascii=False, indent=1))
    rows = judge_table()
    for r in rows:
        print(r["run"], r["concept"], r["surfaces"], "exp=", r["expected"], "llm=", r["llm_decision"], "final=", r["final_decision"], r["final_approx"], r["downgrade"][:1])
    c = cost()
    print(json.dumps(c, ensure_ascii=False, indent=1)[:2500])
