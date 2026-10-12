# ============================================================
# er064_kp_idiom_trial_01_phase_c_run.py
# FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 / Phase C 実行(有料段、Trial専用、1段ずつ手動起動)
# 使い方: PYTHONPATH=. .venv/Scripts/python.exe er064_kp_idiom_trial_01_phase_c_run.py --stage c1|c2|c3
# - 自動再試行・監督ループなし。各段は1回だけ起動する。失敗callは記録して終了(再起動は行わない)。
# - 評価fixture(TARGETS)は『評価用ラベル』であり、Trial実装(matcher/pipeline/extractor/select)には入っていない。
# - 累計費用は phase_c/cost.json に追記。上限超過見込みなら新規callをしない。
# ============================================================
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import json
import os
import sys
import time

import er030_key_phrase_db_hybrid_core_01 as core
import er064_kp_idiom_trial_01_extractor as X
import er064_kp_idiom_trial_01_matcher as M
import er064_kp_idiom_trial_01_pipeline as P
import er064_kp_idiom_trial_01_select as S

ROOT = "er064_output/kp_idiom_trial_01"
PC = f"{ROOT}/phase_c"
INPUTS = f"{ROOT}/phase_a/inputs"
BUDGET_JPY = 20.0
LEVELS = ("std", "adv")
RUNS = (1, 2, 3)
# 評価fixture(ラベル判定用のみ。実装側には渡さない)
TARGETS = {"pumps_its_fist": lambda s: ("pump" in s.lower() and "fist" in s.lower()),
           "mark_the_date": lambda s: "mark the date" in s.lower()}


def stop_files_present() -> list:
    found = glob.glob("docs/pm/delegation_log/*KP-IDIOM*STOP*") + glob.glob(f"{ROOT}/STOP") + \
        glob.glob("er026_output/family_z_production_e2e_01/STOP_ALL") + glob.glob(f"{PC}/STOP")
    return found


def load_cost() -> dict:
    p = f"{PC}/cost.json"
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return {"budget_jpy": BUDGET_JPY, "model": S.MODEL, "calls": [], "cumulative_jpy": 0.0}


def save_cost(cost: dict) -> None:
    cost["cumulative_jpy"] = round(sum(c["cost_jpy"] for c in cost["calls"]), 4)
    json.dump(cost, open(f"{PC}/cost.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def article(lv: str) -> str:
    return open(f"{INPUTS}/v4_{lv}_article.md", encoding="utf-8").read()


def target_flags(texts: list) -> dict:
    return {k: any(f(t) for t in texts) for k, f in TARGETS.items()}


def v2_shortlist(lv: str, llm_cands: list):
    t = article(lv)
    base = P.load_base(t)
    dbs = core.load_group1_dbs()
    pats = M.build_pattern_index(dbs)
    st = base["stage1"]
    pc = M.placeholder_candidates(st["sentence_units"], pats, dbs, P._canon_set(st))
    return base, P.build_variant_shortlist(base, "V2", placeholder_cands=pc, llm_cands=llm_cands)


# ---------------------------------------------------------------- C1
def c1_one(lv: str, k: int) -> dict:
    d = f"{PC}/c1_extraction/{lv}_run{k}"
    os.makedirs(d, exist_ok=True)
    client = S.UsageClient(label=f"c1_{lv}_{k}")
    t = article(lv)
    r = X.call_extractor(t, lv, S.MODEL, client=client)
    json.dump({k2: v for k2, v in r.items()}, open(f"{d}/extractor_raw.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    base = P.load_base(t)
    units = base["stage1"]["sentence_units"]
    built = X.build_llm_candidates(r["parsed"], units, P._canon_set(base["stage1"]))
    base2, v2 = v2_shortlist(lv, built["accepted"])
    sl_keys = P.shortlist_keys(v2["shortlist_info"])
    raw_spans = [i["span"] for i in r["parsed"].get("items", [])]
    res = {"level": lv, "run": k, "raw_item_count": len(raw_spans), "raw_spans": raw_spans,
           "accepted": [c["surface_form"] for c in built["accepted"]],
           "rejected": built["rejected"], "duplicate_of_existing": built["duplicate_of_existing"],
           "reserved_in_v2": [c["surface_form"] for c in v2["reserved"]],
           "reserved_overflow": [c["surface_form"] for c in v2["reserved_overflow"]],
           "v2_shortlist_total": len(sl_keys),
           "extracted_targets_raw": target_flags(raw_spans),
           "accepted_targets": target_flags([c["surface_form"] for c in built["accepted"]]),
           "shortlist_targets": target_flags(sl_keys),
           "usage_calls": client.log, "cost_jpy": client.total_cost(), "prompt_sha256": r["prompt_sha256"]}
    json.dump(res, open(f"{d}/c1_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"accepted_candidates": built["accepted"]}, open(f"{d}/accepted_candidates.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    return res


def stage_c1() -> None:
    cost = load_cost()
    if cost["cumulative_jpy"] + 2.0 > BUDGET_JPY:
        sys.exit("budget guard")
    jobs = [(lv, k) for lv in LEVELS for k in RUNS]
    results, errors = [], []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(c1_one, lv, k): (lv, k) for lv, k in jobs}
        for f in cf.as_completed(futs):
            try:
                results.append(f.result())
            except Exception as e:  # 失敗は記録して終了(再起動しない)
                errors.append({"job": futs[f], "error": f"{type(e).__name__}: {e}"})
    for r in sorted(results, key=lambda x: (x["level"], x["run"])):
        for c in r["usage_calls"]:
            cost["calls"].append({"stage": "c1", **c})
    save_cost(cost)
    summ = {"errors": errors, "runs": sorted(results, key=lambda x: (x["level"], x["run"])),
            "cost_jpy_stage": round(sum(r["cost_jpy"] for r in results), 4), "cumulative_jpy": cost["cumulative_jpy"]}
    json.dump(summ, open(f"{PC}/c1_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for r in summ["runs"]:
        print(r["level"], r["run"], "raw", r["raw_item_count"], "acc", len(r["accepted"]), "tgt_raw", r["extracted_targets_raw"],
              "tgt_sl", r["shortlist_targets"], "cost", r["cost_jpy"])
    print("errors", errors, "stage_cost", summ["cost_jpy_stage"], "cum", cost["cumulative_jpy"])


# ---------------------------------------------------------------- C2
def c2_one(lv: str, k: int) -> dict:
    d = f"{PC}/c2_vl/{lv}_run{k}"
    os.makedirs(d, exist_ok=True)
    client = S.UsageClient(label=f"c2_{lv}_{k}")
    r = S.run_vl(article(lv), client, article_id=f"kp_idiom_vl_{lv}_{k}")
    items = (r["parsed"] or {}).get("items", []) if r["parsed"] else []
    res = {"level": lv, "run": k, "status": r["status"], "attempts": r["attempts"],
           "items": [{"rank": i.get("rank"), "role": i.get("key_phrase_role"), "display_phrase": i.get("display_phrase"),
                      "source_span": i.get("source_span")} for i in items],
           "targets_selected": target_flags([i.get("display_phrase", "") + " | " + i.get("source_span", "") for i in items]),
           "usage_calls": client.log, "cost_jpy": client.total_cost(), "prompt_sha256": r["prompt_sha256"]}
    json.dump(res, open(f"{d}/c2_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return res


def stage_c2() -> None:
    cost = load_cost()
    if cost["cumulative_jpy"] + 3.0 > BUDGET_JPY:
        sys.exit("budget guard")
    jobs = [(lv, k) for lv in LEVELS for k in RUNS]
    results, errors = [], []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(c2_one, lv, k): (lv, k) for lv, k in jobs}
        for f in cf.as_completed(futs):
            try:
                results.append(f.result())
            except Exception as e:
                errors.append({"job": futs[f], "error": f"{type(e).__name__}: {e}"})
    for r in results:
        for c in r["usage_calls"]:
            cost["calls"].append({"stage": "c2", **c})
    save_cost(cost)
    summ = {"errors": errors, "runs": sorted(results, key=lambda x: (x["level"], x["run"])),
            "cost_jpy_stage": round(sum(r["cost_jpy"] for r in results), 4), "cumulative_jpy": cost["cumulative_jpy"]}
    json.dump(summ, open(f"{PC}/c2_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for r in summ["runs"]:
        print(r["level"], r["run"], r["status"], [i["display_phrase"] for i in r["items"]], r["targets_selected"], r["cost_jpy"])
    print("errors", errors, "stage_cost", summ["cost_jpy_stage"], "cum", cost["cumulative_jpy"])


# ---------------------------------------------------------------- C3
def c3_one(lv: str, k: int) -> dict:
    d = f"{PC}/c3_v2/{lv}_run{k}"
    os.makedirs(d, exist_ok=True)
    client = S.UsageClient(label=f"c3_{lv}_{k}")
    t = article(lv)
    acc = json.load(open(f"{PC}/c1_extraction/{lv}_run{k}/accepted_candidates.json", encoding="utf-8"))["accepted_candidates"]
    base, v2 = v2_shortlist(lv, acc)
    sel = S.run_selection(t, v2["shortlist_info"], S.trial_guidance(lv), client, article_id=f"kp_idiom_v2_{lv}_{k}", out_dir=d)
    res = {"level": lv, "run": k, "selection_status": sel["status"], "prompt_sha256": sel["prompt_sha256"],
           "candidates": sel["candidates"], "source_span_missing": sel.get("source_span_missing"),
           "validation_reasons": sel.get("validation_reasons"), "item_reasons": sel.get("item_reasons")}
    items = []
    if sel["status"] == "KEY_WORDS_STRUCTURE_PASS":
        items = sel["original_items"]
        res["selected_items"] = [{"rank": i.get("rank"), "role": i.get("key_phrase_role"), "display_phrase": i.get("display_phrase"),
                                  "source_span": i.get("source_span"), "source_candidate_id": i.get("source_candidate_id"),
                                  "ja_gloss": i.get("ja_gloss") or i.get("japanese_gloss")} for i in items]
        id2 = {c["candidate_id"]: c for c in sel["candidates"]}
        for si in res["selected_items"]:
            si["candidate_evidence"] = (id2.get(si["source_candidate_id"]) or {}).get("evidence")
        qa = S.run_canonicalization_and_qa(t, items, client)
        res["canonicalization_status"] = qa.get("canonicalization_status")
        res["canonicalization_item_reasons"] = [a.get("item_reasons") for a in qa.get("canonicalization_attempts", [])]
        res["canonicalization_attempt_statuses"] = [a.get("status") for a in qa.get("canonicalization_attempts", [])]
        res["redundancy_status"] = qa.get("redundancy_status")
        res["redundancy_duplicate_pairs"] = qa.get("redundancy_duplicate_pairs")
        if qa.get("merged"):
            res["canonicalized"] = [{"rank": i["rank"], "key_phrase": i["key_phrase"], "display_phrase": i["display_phrase"],
                                     "normalization_reason": i["normalization_reason"], "qa_overall_status": i["qa_overall_status"]}
                                    for i in qa["merged"]["items"]]
            res["merged_overall_status"] = qa["merged"]["overall_status"]
    res["targets_selected"] = target_flags([(i.get("display_phrase") or "") + " | " + (i.get("source_span") or "") for i in items])
    res["usage_calls"] = client.log
    res["cost_jpy"] = client.total_cost()
    json.dump(res, open(f"{d}/c3_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return res


def stage_c3() -> None:
    cost = load_cost()
    if cost["cumulative_jpy"] + 10.0 > BUDGET_JPY:
        sys.exit(f"budget guard: cumulative {cost['cumulative_jpy']} + est 10 > {BUDGET_JPY}")
    jobs = [(lv, k) for lv in LEVELS for k in RUNS]
    results, errors = [], []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(c3_one, lv, k): (lv, k) for lv, k in jobs}
        for f in cf.as_completed(futs):
            try:
                results.append(f.result())
            except Exception as e:
                errors.append({"job": futs[f], "error": f"{type(e).__name__}: {e}"})
    for r in results:
        for c in r["usage_calls"]:
            cost["calls"].append({"stage": "c3", **c})
    save_cost(cost)
    summ = {"errors": errors, "runs": sorted(results, key=lambda x: (x["level"], x["run"])),
            "cost_jpy_stage": round(sum(r["cost_jpy"] for r in results), 4), "cumulative_jpy": cost["cumulative_jpy"]}
    json.dump(summ, open(f"{PC}/c3_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for r in summ["runs"]:
        print(r["level"], r["run"], r["selection_status"], r.get("canonicalization_status"), r.get("redundancy_status"),
              [i["display_phrase"] for i in r.get("selected_items", [])], r["targets_selected"], r["cost_jpy"])
    print("errors", errors, "stage_cost", summ["cost_jpy_stage"], "cum", cost["cumulative_jpy"])


# ---------------------------------------------------------------- C3R (Production redundancy retryとの整合確認)
def c3r_one(lv: str, k: int) -> dict:
    """C3でREDUNDANCY_NGだった実行について、Productionのretry方式(診断メモをprompt末尾へ追記して選定からやり直し、
    canonicalization+Redundancy QAを再実行)を1回だけ再現する。Production上限(POINT_OVERLAP_ARTICLE_RETRY_MAX=2)の
    うち1回分のみ。"""
    import er011_key_phrase_set_redundancy_qa_01 as rq
    prev = json.load(open(f"{PC}/c3_v2/{lv}_run{k}/c3_result.json", encoding="utf-8"))
    d = f"{PC}/c3_v2/{lv}_run{k}_retry1"
    os.makedirs(d, exist_ok=True)
    client = S.UsageClient(label=f"c3r_{lv}_{k}")
    t = article(lv)
    acc = json.load(open(f"{PC}/c1_extraction/{lv}_run{k}/accepted_candidates.json", encoding="utf-8"))["accepted_candidates"]
    base, v2 = v2_shortlist(lv, acc)
    items_by_rank = {c["rank"]: c for c in prev["canonicalized"]}
    note = rq.build_redundancy_diagnostic_note(prev["redundancy_duplicate_pairs"], items_by_rank)
    sel = S.run_selection(t, v2["shortlist_info"], S.trial_guidance(lv), client, article_id=f"kp_idiom_v2r_{lv}_{k}",
                          out_dir=d, diagnostic_note=note)
    res = {"level": lv, "run": k, "retry": 1, "diagnostic_note": note, "selection_status": sel["status"],
           "source_span_missing": sel.get("source_span_missing")}
    items = []
    if sel["status"] == "KEY_WORDS_STRUCTURE_PASS":
        items = sel["original_items"]
        res["selected_items"] = [{"rank": i.get("rank"), "role": i.get("key_phrase_role"), "display_phrase": i.get("display_phrase"),
                                  "source_span": i.get("source_span"), "source_candidate_id": i.get("source_candidate_id")} for i in items]
        qa = S.run_canonicalization_and_qa(t, items, client)
        res["canonicalization_status"] = qa.get("canonicalization_status")
        res["canonicalization_attempt_statuses"] = [a.get("status") for a in qa.get("canonicalization_attempts", [])]
        res["redundancy_status"] = qa.get("redundancy_status")
        res["redundancy_duplicate_pairs"] = qa.get("redundancy_duplicate_pairs")
        if qa.get("merged"):
            res["canonicalized"] = [{"rank": i["rank"], "key_phrase": i["key_phrase"], "display_phrase": i["display_phrase"],
                                     "normalization_reason": i["normalization_reason"], "qa_overall_status": i["qa_overall_status"]}
                                    for i in qa["merged"]["items"]]
    res["targets_selected"] = target_flags([(i.get("display_phrase") or "") + " | " + (i.get("source_span") or "") for i in items])
    res["usage_calls"] = client.log
    res["cost_jpy"] = client.total_cost()
    json.dump(res, open(f"{d}/c3r_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return res


def stage_c3r() -> None:
    cost = load_cost()
    if cost["cumulative_jpy"] + 4.5 > BUDGET_JPY:
        sys.exit("budget guard")
    jobs = []
    for lv in LEVELS:
        for k in RUNS:
            prev = json.load(open(f"{PC}/c3_v2/{lv}_run{k}/c3_result.json", encoding="utf-8"))
            if prev.get("redundancy_status") == "REDUNDANCY_NG":
                jobs.append((lv, k))
    results, errors = [], []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(c3r_one, lv, k): (lv, k) for lv, k in jobs}
        for f in cf.as_completed(futs):
            try:
                results.append(f.result())
            except Exception as e:
                errors.append({"job": futs[f], "error": f"{type(e).__name__}: {e}"})
    for r in results:
        for c in r["usage_calls"]:
            cost["calls"].append({"stage": "c3r", **c})
    save_cost(cost)
    summ = {"errors": errors, "runs": sorted(results, key=lambda x: (x["level"], x["run"])),
            "cost_jpy_stage": round(sum(r["cost_jpy"] for r in results), 4), "cumulative_jpy": cost["cumulative_jpy"]}
    json.dump(summ, open(f"{PC}/c3r_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for r in summ["runs"]:
        print(r["level"], r["run"], r["selection_status"], r.get("canonicalization_status"), r.get("redundancy_status"),
              [i["display_phrase"] for i in r.get("selected_items", [])], r["targets_selected"], r["cost_jpy"])
    print("errors", errors, "stage_cost", summ["cost_jpy_stage"], "cum", cost["cumulative_jpy"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["c1", "c2", "c3", "c3r"])
    a = ap.parse_args()
    sf = stop_files_present()
    if sf:
        sys.exit(f"STOP files present: {sf}")
    os.makedirs(PC, exist_ok=True)
    {"c1": stage_c1, "c2": stage_c2, "c3": stage_c3, "c3r": stage_c3r}[a.stage]()
