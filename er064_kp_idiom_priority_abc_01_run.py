# ============================================================
# er064_kp_idiom_priority_abc_01_run.py
# FAMILY-X-KP-IDIOM-PRIORITY-ABC-TRIAL-01 (Trial専用、Production未配線)
# 固定候補リスト(Phase D M1 extractor v3 run1のaccepted_candidates)で、選定Promptの優先順位記述(template 11行目)のみA/B/Cで差し替え。
# 抽出(extractor)は再実行しない。TTS無し。timeout/監督ループ無し。各stageは1回だけ手動起動。
# 使い方: PYTHONPATH=. .venv/Scripts/python.exe er064_kp_idiom_priority_abc_01_run.py --stage prep|final [--n 3]
# ============================================================
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import hashlib
import json
import os
import sys
import threading
import time

import er003_b1_p2_keywords as bk
import er030_key_phrase_db_hybrid_core_01 as core
import er030_key_phrase_db_hybrid_selector_01 as selector01
import er064_kp_idiom_trial_01_matcher as M
import er064_kp_idiom_trial_01_pipeline as P
import er064_kp_idiom_trial_01_select as S

OUT = "er064_output/kp_idiom_priority_abc_01"
SRC = "er064_output/kp_idiom_trial_01"
BUDGET = 20.0
LEVELS = ("std", "adv")
VERSIONS = ("A", "B", "C")
PRIO = {
    "A": "初回音声での処理困難、未知の可能性、瞬時の推測困難、本文の事実・感情・面白さへの影響、記事内重要度、汎用性",
    "B": "未知の可能性、初回音声での処理困難、瞬時の推測困難、本文の事実・感情・面白さへの影響、記事内重要度、汎用性",
    "C": "未知の可能性、汎用性、初回音声での処理困難、瞬時の推測困難、本文の事実・感情・面白さへの影響、記事内重要度",
}
LINE_A = "優先順位は、" + PRIO["A"] + "の順です。"
CAND_FROM = {lv: f"{SRC}/phase_d/m1_recheck_02/coffee_{lv}/run1/accepted_candidates.json" for lv in LEVELS}
ART = {lv: f"{SRC}/phase_a/inputs/v4_{lv}_article.md" for lv in LEVELS}

_tl = threading.local()
_orig_static = selector01.extract_static_instructions


def _patched_static(template):
    s = _orig_static(template)
    v = getattr(_tl, "version", None)
    if v is None:
        return s
    assert s.count(LINE_A) == 1, "優先順位行がProduction templateと逐語一致しない"
    return s.replace(LINE_A, "優先順位は、" + PRIO[v] + "の順です。")


selector01.extract_static_instructions = _patched_static


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def stop_present():
    return glob.glob(f"{OUT}/STOP") + glob.glob("docs/pm/delegation_log/*KP-IDIOM*STOP*")


def build_fixed(lv):
    t = open(ART[lv], encoding="utf-8").read()
    base = P.load_base(t)
    dbs = core.load_group1_dbs()
    pats = M.build_pattern_index(dbs)
    st = base["stage1"]
    pc = M.placeholder_candidates(st["sentence_units"], pats, dbs, P._canon_set(st))
    acc = json.load(open(CAND_FROM[lv], encoding="utf-8"))["accepted_candidates"]
    return t, P.build_variant_shortlist(base, "V2", placeholder_cands=pc, llm_cands=acc)


class Cost:
    lock = threading.Lock()
    path = f"{OUT}/cost_01.json"

    @classmethod
    def load(cls):
        return json.load(open(cls.path, encoding="utf-8")) if os.path.exists(cls.path) else {"budget_jpy": BUDGET, "model": S.MODEL, "calls": []}

    @classmethod
    def spent(cls):
        return round(sum(c["cost_jpy"] for c in cls.load()["calls"]), 4)

    @classmethod
    def add(cls, stage, tag, client):
        with cls.lock:
            c = cls.load()
            for x in client.log:
                c["calls"].append({"stage": stage, "tag": tag, **x})
            c["cumulative_jpy"] = round(sum(x["cost_jpy"] for x in c["calls"]), 4)
            json.dump(c, open(cls.path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def job(lv, ver, k, shortlists):
    if stop_present():
        raise RuntimeError("STOP present")
    t, sl = shortlists[lv]
    tag = f"{lv}_{ver}_run{k}"
    d = f"{OUT}/runs/{tag}"
    os.makedirs(d, exist_ok=True)
    _tl.version = ver
    client = S.UsageClient(label=tag)
    res = {"level": lv, "version": ver, "run": k, "tag": tag}
    t0 = time.time()
    try:
        sel = S.run_selection(t, sl["shortlist_info"], S.prod_guidance(), client, article_id=f"kp_abc_{tag}", out_dir=d)
        res.update(selection_status=sel["status"], prompt_sha256=sel["prompt_sha256"],
                   validation_reasons=sel.get("validation_reasons"), source_span_missing=sel.get("source_span_missing"))
        if sel["status"] == "KEY_WORDS_STRUCTURE_PASS":
            items = sel["original_items"]
            id2 = {c["candidate_id"]: c for c in sel["candidates"]}
            res["raw_selected_items"] = items
            res["selected_items"] = [{"rank": i.get("rank"), "role": i.get("key_phrase_role"), "display_phrase": i.get("display_phrase"),
                                      "source_span": i.get("source_span"), "source_candidate_id": i.get("source_candidate_id"),
                                      "evidence": (id2.get(i.get("source_candidate_id")) or {}).get("evidence"),
                                      "candidate_surface": (id2.get(i.get("source_candidate_id")) or {}).get("surface_form")} for i in items]
            res["backup_item"] = sel["parsed"].get("backup_item")
            qa = S.run_canonicalization_and_qa(t, items, client)
            res["canonicalization_status"] = qa.get("canonicalization_status")
            res["canonicalization_item_reasons"] = [x.get("item_reasons") for x in qa.get("canonicalization_attempts", [])]
            res["canonicalization_attempt_statuses"] = [x.get("status") for x in qa.get("canonicalization_attempts", [])]
            res["redundancy_status"] = qa.get("redundancy_status")
            res["redundancy_duplicate_pairs"] = qa.get("redundancy_duplicate_pairs")
            if qa.get("merged"):
                res["canonicalized"] = [{"rank": i["rank"], "key_phrase": i["key_phrase"], "display_phrase": i["display_phrase"],
                                         "normalization_reason": i["normalization_reason"], "qa_overall_status": i["qa_overall_status"]}
                                        for i in qa["merged"]["items"]]
                res["merged_overall_status"] = qa["merged"]["overall_status"]
    finally:
        Cost.add("final", tag, client)
    res["cost_jpy"] = client.total_cost()
    res["elapsed_sec"] = round(time.time() - t0, 2)
    json.dump(res, open(f"{d}/job_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return res


def stage_prep(n):
    os.makedirs(OUT, exist_ok=True)
    info = {}
    for lv in LEVELS:
        t, sl = build_fixed(lv)
        forms = [c["surface_form"] for c in sl["shortlist_info"]["shortlist"]]
        info[lv] = {"candidate_source_file": CAND_FROM[lv], "candidate_source_sha256": sha_file(CAND_FROM[lv]),
                    "article_file": ART[lv], "article_sha256": sha_file(ART[lv]),
                    "accepted_llm_candidates": [c["surface_form"] for c in json.load(open(CAND_FROM[lv], encoding="utf-8"))["accepted_candidates"]],
                    "reserved": [c["surface_form"] for c in sl["reserved"]], "shortlist_forms": forms,
                    "shortlist_sha256": hashlib.sha256(json.dumps(forms).encode()).hexdigest()}
    json.dump(info, open(f"{OUT}/fixed_candidates_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    est = len(LEVELS) * len(VERSIONS) * n * 0.91
    if not os.path.exists(Cost.path):
        json.dump({"budget_jpy": BUDGET, "model": S.MODEL, "calls": [],
                   "pre_estimate": {"versions": 3, "levels": 2, "n": n, "per_job_jpy_phaseD_avg": 0.91, "estimate_jpy": round(est, 2)}},
                  open(Cost.path, "w", encoding="utf-8"), indent=2)
    print(json.dumps({lv: {k: v for k, v in x.items() if k != "shortlist_forms"} for lv, x in info.items()}, ensure_ascii=False, indent=1))
    print("estimate", est)


def stage_final(n):
    if stop_present():
        sys.exit(f"STOP present {stop_present()}")
    if Cost.spent() + len(LEVELS) * len(VERSIONS) * n * 0.91 > BUDGET:
        sys.exit("budget guard: reduce n")
    shortlists = {lv: build_fixed(lv) for lv in LEVELS}
    jobs = [(lv, v, k) for lv in LEVELS for v in VERSIONS for k in range(1, n + 1)]
    res, err = [], []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(job, lv, v, k, shortlists): (lv, v, k) for lv, v, k in jobs}
        for f in cf.as_completed(futs):
            try:
                res.append(f.result())
            except Exception as e:
                err.append({"job": futs[f], "error": f"{type(e).__name__}: {e}"})
    res.sort(key=lambda r: (r["level"], r["version"], r["run"]))
    json.dump({"runs": res, "errors": err, "cumulative_jpy": Cost.spent()}, open(f"{OUT}/final_summary_01.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    for r in res:
        print(r["tag"], r["selection_status"], r.get("canonicalization_status"), r.get("redundancy_status"),
              [i["display_phrase"] for i in r.get("selected_items", [])], r["cost_jpy"])
    print("errors", err, "cum", Cost.spent())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["prep", "final"])
    ap.add_argument("--n", type=int, default=3)
    a = ap.parse_args()
    if a.stage == "prep":
        stage_prep(a.n)
    else:
        stage_final(a.n)
