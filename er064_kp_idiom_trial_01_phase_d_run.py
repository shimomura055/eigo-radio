# ============================================================
# er064_kp_idiom_trial_01_phase_d_run.py
# FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 / Phase D 実行(有料段、Trial専用、手動で1段ずつ起動)
# 使い方: PYTHONPATH=. .venv/Scripts/python.exe er064_kp_idiom_trial_01_phase_d_run.py --stage m1|extract|final|v1d [--group N1,D6]
# - 凍結(phase_d/FROZEN_PLAN_01.json)のshaと現在のファイルが一致しないと実行しない。
# - 自動再試行・監督ループなし。各段は1回だけ起動する。残予算超過見込みなら新規callをせず終了(陰性対照を削って収めない)。
# - 正解表(gold)は凍結planのJSON内にあり、Trial実装(matcher/pipeline/extractor/select)には渡さない。
# ============================================================
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import hashlib
import json
import os
import re
import sys
import threading
import time

import er030_key_phrase_db_hybrid_core_01 as core
import er064_kp_idiom_trial_01_extractor as X
import er064_kp_idiom_trial_01_matcher as M
import er064_kp_idiom_trial_01_pipeline as P
import er064_kp_idiom_trial_01_select as S

ROOT = "er064_output/kp_idiom_trial_01"
PD = f"{ROOT}/phase_d"
PLAN_PATH = f"{PD}/FROZEN_PLAN_02.json"  # 委任_04: extractor v3で再凍結(01は履歴として保持)
BUDGET_LIMIT = 34.28           # 本件専用残予算(JPY)。本件上限50 - (Phase C 14.4411 + 委任_03 M1 1.2792)。委任_04の費用は cost_02.json に記録
JOB_EST = 1.4                  # 1 job(選定+正規化+QA)の保守的見積(JPY)
EXTRACT_EST = 0.25
DETS = {"the", "a", "an", "your", "my", "his", "her", "its", "their", "our", "this", "that", "these", "those"}
AUX = {"is", "are", "was", "were"}


def sha_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def stop_files_present() -> list:
    # 本件の有料run判定は本件用STOP(+本件名のSTOP_NOTICE)のみ(Fable指示 委任_04。Family ZのSTOP_ALLは別案件のtest由来で対象外)。
    # Family Z STOP_ALLの存在は参考として stage 開始時にログ出力する。
    return glob.glob("docs/pm/delegation_log/*KP-IDIOM*STOP*") + glob.glob(f"{ROOT}/STOP") + glob.glob(f"{PD}/STOP")


def load_plan() -> dict:
    if not os.path.exists(PLAN_PATH):
        sys.exit("FROZEN_PLAN_02.json missing: not frozen")
    plan = json.load(open(PLAN_PATH, encoding="utf-8"))
    for f, h in plan["file_sha256"].items():
        if sha_file(f) != h:
            sys.exit(f"frozen file changed after freeze: {f}")
    if time.time() < plan["frozen_at_epoch"]:
        sys.exit("clock before frozen_at")
    return plan


# ----------------------------------------------------------------- cost / budget
class Budget:
    def __init__(self):
        self.lock = threading.Lock()
        self.cost_path = f"{PD}/cost_02.json"
        if os.path.exists(self.cost_path):
            self.cost = json.load(open(self.cost_path, encoding="utf-8"))
        else:
            self.cost = {"budget_limit_jpy": BUDGET_LIMIT, "model": S.MODEL, "calls": [], "cumulative_jpy": 0.0}
        self.reserved = 0.0

    @property
    def spent(self) -> float:
        return round(sum(c["cost_jpy"] for c in self.cost["calls"]), 4)

    def reserve(self, est: float) -> bool:
        with self.lock:
            if self.spent + self.reserved + est > BUDGET_LIMIT:
                return False
            self.reserved += est
            return True

    def settle(self, est: float, stage: str, tag: str, client: S.UsageClient) -> None:
        with self.lock:
            self.reserved = max(0.0, self.reserved - est)
            for c in client.log:
                self.cost["calls"].append({"stage": stage, "tag": tag, **c})
            self.cost["cumulative_jpy"] = self.spent
            json.dump(self.cost, open(self.cost_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


# ----------------------------------------------------------------- 評価(gold)
def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower().replace("’", "'")).strip()


def eval_targets(targets: list, exact_texts: list, partial_texts: list) -> dict:
    ex_set = [norm(t) for t in exact_texts]
    pt = [norm(t) for t in partial_texts]
    res = {}
    for t in targets:
        forms = {norm(e) for e in t["exact"]}
        res[t["id"]] = {"exact": any(x in forms for x in ex_set),
                        "partial": any(all(norm(p) in x for p in t["partial_all"]) for x in pt)}
    return res


def subject_included(span: str, narrowed_from: str | None = None) -> bool:
    """近似ヒューリスティック(凍結planに記載): 限定詞/所有格で始まり、後続に動詞らしい語(-s/-ed/-ing語尾でssでない語、be動詞)を含む
    =主語名詞込みの述語スパンとみなす。LLMがcore_spanで縮約した(=raw spanは主語込み)場合もTrue。"""
    if narrowed_from:
        return True
    toks = norm(span).split()
    if len(toks) < 3 or toks[0] not in DETS:
        return False
    for t in toks[2:]:
        if t in AUX or (t.endswith(("ed", "es", "ing")) or (t.endswith("s") and not t.endswith("ss"))):
            return True
    return False


# ----------------------------------------------------------------- 記事・基盤
def art_path(a: dict) -> str:
    return f"{PD}/inputs/{a['file']}" if not a["file"].startswith("er064_output") else a["file"]


def art_text(a: dict) -> str:
    return open(art_path(a), encoding="utf-8").read()


def placeholder_cands(base: dict, dbs, pats) -> list:
    st = base["stage1"]
    return M.placeholder_candidates(st["sentence_units"], pats, dbs, P._canon_set(st))


def extraction_dir(a: dict, k: int, root: str = None) -> str:
    return f"{root or PD + '/extraction'}/{a['id']}/run{k}"


# ----------------------------------------------------------------- 抽出(有料)
def extract_one(a: dict, k: int, budget: Budget, root: str = None, stage: str = "extract") -> dict:
    d = extraction_dir(a, k, root)
    os.makedirs(d, exist_ok=True)
    if stop_files_present():
        raise RuntimeError("STOP file present")
    client = S.UsageClient(label=f"{stage}_{a['id']}_{k}")
    est = EXTRACT_EST
    try:
        t = art_text(a)
        r = X.call_extractor(t, a["level"], S.MODEL, client=client)
    finally:
        budget.settle(est, stage, f"{a['id']}_run{k}", client)
    json.dump(r, open(f"{d}/extractor_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    base = P.load_base(t)
    built = X.build_llm_candidates(r["parsed"], base["stage1"]["sentence_units"], P._canon_set(base["stage1"]))
    dbs = core.load_group1_dbs()
    pats = M.build_pattern_index(dbs)
    pc = placeholder_cands(base, dbs, pats)
    v2 = P.build_variant_shortlist(base, "V2", placeholder_cands=pc, llm_cands=built["accepted"])
    sl = [c["surface_form"] for c in v2["shortlist_info"]["shortlist"]]
    acc_spans = [c["surface_form"] for c in built["accepted"]]
    res = {"id": a["id"], "level": a["level"], "run": k, "raw_item_count": built["raw_item_count"],
           "raw_items": r["parsed"].get("items", []),
           "accepted": acc_spans, "rejected": built["rejected"], "duplicate_of_existing": built["duplicate_of_existing"],
           "containment_duplicates": [x for x in built["duplicate_of_existing"] if x.get("contains_existing")],
           "subject_included": [subject_included(c["surface_form"], c["llm_raw_span"] if c.get("core_span_narrowed") else None)
                                for c in built["accepted"]],
           "reserved_in_v2": [c["surface_form"] for c in v2["reserved"]],
           "reserved_overflow": [c["surface_form"] for c in v2["reserved_overflow"]],
           "v2_shortlist_total": len(sl),
           "usage_calls": client.log, "cost_jpy": client.total_cost(), "prompt_sha256": r["prompt_sha256"],
           "elapsed_sec": r["elapsed_sec"]}
    tg = a.get("targets")
    if tg:
        res["accepted_targets"] = eval_targets(tg, acc_spans, acc_spans)
        res["raw_targets"] = eval_targets(tg, [i["span"] for i in res["raw_items"]], [i["span"] for i in res["raw_items"]])
        res["v2_shortlist_targets"] = eval_targets(tg, sl, sl)
    json.dump(res, open(f"{d}/extract_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"accepted_candidates": built["accepted"]}, open(f"{d}/accepted_candidates.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    return res


# ----------------------------------------------------------------- 最終選定(有料)
def final_texts(items: list) -> tuple:
    ex, pt = [], []
    for i in items:
        for k in ("display_phrase", "key_phrase"):
            if i.get(k):
                ex.append(i[k])
        pt.append((i.get("display_phrase") or "") + " | " + (i.get("source_span") or ""))
    return ex, pt


def run_variant_job(a: dict, variant: str, k: int, budget: Budget, out_root: str = None, allow_retry: bool = True) -> dict:
    """variant: V0(Production現行shortlist+Production guidance) / V1d(V0+placeholder+d guidance) / V2(a+b1+c+d)。"""
    tag = f"{a['id']}_{variant}_run{k}"
    d = f"{out_root or PD + '/final'}/{a['id']}/{variant}_run{k}"
    os.makedirs(d, exist_ok=True)
    res = {"id": a["id"], "level": a["level"], "variant": variant, "run": k, "tag": tag, "attempts": []}
    t0 = time.time()
    t = art_text(a)
    base = P.load_base(t)
    dbs = core.load_group1_dbs()
    pats = M.build_pattern_index(dbs)
    pc = placeholder_cands(base, dbs, pats)
    if variant == "V0":
        sl_info = P.build_variant_shortlist(base, "V0")
        guidance = S.prod_guidance()
    elif variant == "V1d":
        sl_info = P.build_variant_shortlist(base, "V1", placeholder_cands=pc)
        guidance = S.trial_guidance(a["level"])
    elif variant == "V2":
        acc = json.load(open(f"{extraction_dir(a, k)}/accepted_candidates.json", encoding="utf-8"))["accepted_candidates"]
        sl_info = P.build_variant_shortlist(base, "V2", placeholder_cands=pc, llm_cands=acc)
        guidance = S.trial_guidance(a["level"])
    else:
        raise ValueError(variant)
    info = sl_info["shortlist_info"]
    reserved_forms = [c["surface_form"] for c in sl_info["reserved"]]
    res["reserved_candidates"] = reserved_forms
    res["shortlist_forms"] = [c["surface_form"] for c in info["shortlist"]]
    note = None
    stop_reason = None
    for attempt in range(0, 2 if (allow_retry and variant != "V0") else 1):
        if stop_files_present():
            stop_reason = "STOP_FILE_PRESENT"
            break
        if not budget.reserve(JOB_EST):
            stop_reason = "BUDGET_STOP_before_attempt"
            break
        client = S.UsageClient(label=f"final_{tag}_a{attempt}")
        ta = time.time()
        try:
            sel = S.run_selection(t, info, guidance, client, article_id=f"kp_d_{tag}_a{attempt}",
                                  out_dir=f"{d}/attempt{attempt}", diagnostic_note=note)
            rec = {"attempt": attempt, "selection_status": sel["status"], "prompt_sha256": sel["prompt_sha256"],
                   "source_span_missing": sel.get("source_span_missing"), "validation_reasons": sel.get("validation_reasons")}
            if sel["status"] == "KEY_WORDS_STRUCTURE_PASS":
                items = sel["original_items"]
                id2 = {c["candidate_id"]: c for c in sel["candidates"]}
                rec["selected_items"] = [
                    {"rank": i.get("rank"), "role": i.get("key_phrase_role"), "display_phrase": i.get("display_phrase"),
                     "source_span": i.get("source_span"), "source_candidate_id": i.get("source_candidate_id"),
                     "evidence": (id2.get(i.get("source_candidate_id")) or {}).get("evidence"),
                     "unit_type": (id2.get(i.get("source_candidate_id")) or {}).get("unit_type")} for i in items]
                qa = S.run_canonicalization_and_qa(t, items, client)
                rec["canonicalization_status"] = qa.get("canonicalization_status")
                rec["canonicalization_attempt_statuses"] = [x.get("status") for x in qa.get("canonicalization_attempts", [])]
                rec["canonicalization_item_reasons"] = [x.get("item_reasons") for x in qa.get("canonicalization_attempts", [])]
                rec["redundancy_status"] = qa.get("redundancy_status")
                rec["redundancy_duplicate_pairs"] = qa.get("redundancy_duplicate_pairs")
                if qa.get("merged"):
                    rec["canonicalized"] = [{"rank": i["rank"], "key_phrase": i["key_phrase"], "display_phrase": i["display_phrase"],
                                             "normalization_reason": i["normalization_reason"], "qa_overall_status": i["qa_overall_status"]}
                                            for i in qa["merged"]["items"]]
                    rec["merged_overall_status"] = qa["merged"]["overall_status"]
        finally:
            budget.settle(JOB_EST, "final", f"{tag}_a{attempt}", client)
        rec["cost_jpy"] = client.total_cost()
        rec["elapsed_sec"] = round(time.time() - ta, 2)
        res["attempts"].append(rec)
        if rec.get("redundancy_status") == "REDUNDANCY_NG" and variant != "V0" and allow_retry and attempt == 0:
            import er011_key_phrase_set_redundancy_qa_01 as rq
            by_rank = {c["rank"]: c for c in rec.get("canonicalized", [])}
            if by_rank:
                note = rq.build_redundancy_diagnostic_note(rec["redundancy_duplicate_pairs"], by_rank)
                continue
        break
    res["stop_reason"] = stop_reason
    last = res["attempts"][-1] if res["attempts"] else {}
    first = res["attempts"][0] if res["attempts"] else {}
    fin_items = last.get("selected_items", [])
    ex, pt = final_texts(fin_items + [{"display_phrase": c["display_phrase"], "key_phrase": c["key_phrase"]}
                                      for c in last.get("canonicalized", [])])
    ex0, pt0 = final_texts(first.get("selected_items", []))
    if a.get("targets"):
        res["final_targets"] = eval_targets(a["targets"], ex, pt)
        res["first_attempt_targets"] = eval_targets(a["targets"], ex0, pt0)
    res["final_phrases"] = [i["display_phrase"] for i in fin_items]
    res["final_evidence"] = [i["evidence"] for i in fin_items]
    res["final_llm_or_placeholder_count"] = sum(1 for i in fin_items if i.get("evidence") in ("llm_noncompositional", "placeholder_title"))
    res["final_llm_or_placeholder_items"] = [i["display_phrase"] for i in fin_items if i.get("evidence") in ("llm_noncompositional", "placeholder_title")]
    res["reserved_selected_count"] = res["final_llm_or_placeholder_count"]
    res["reserved_unselected_count"] = len(reserved_forms) - res["final_llm_or_placeholder_count"]
    res["retry_used"] = len(res["attempts"]) > 1
    res["retry_cost_jpy"] = round(sum(x["cost_jpy"] for x in res["attempts"][1:]), 4)
    res["cost_jpy"] = round(sum(x["cost_jpy"] for x in res["attempts"]), 4)
    res["elapsed_sec"] = round(time.time() - t0, 2)
    res["initial_redundancy_status"] = first.get("redundancy_status")
    res["final_redundancy_status"] = last.get("redundancy_status")
    res["initial_canonicalization_status"] = first.get("canonicalization_status")
    res["final_canonicalization_status"] = last.get("canonicalization_status")
    json.dump(res, open(f"{d}/job_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return res


# ----------------------------------------------------------------- stages
def pool_run(fn_jobs: list, workers: int = 6) -> tuple:
    results, errors = [], []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(*j[1:]): j[0] for j in fn_jobs}
        for f in cf.as_completed(futs):
            try:
                results.append(f.result())
            except Exception as e:  # 失敗は記録して終了(再起動しない)
                errors.append({"job": futs[f], "error": f"{type(e).__name__}: {e}"})
    return results, errors


def get_art(plan: dict, aid: str) -> dict:
    for sec in ("m1", "articles"):
        for a in plan[sec]:
            if a["id"] == aid:
                return a
    sys.exit(f"unknown article {aid}")


def stage_m1(plan: dict, budget: Budget) -> None:
    jobs = []
    if budget.spent + 6 * EXTRACT_EST > BUDGET_LIMIT:
        sys.exit("budget stop")
    for a in plan["m1"]:
        for k in (1, 2, 3):
            jobs.append(((a["id"], k), extract_one, a, k, budget, f"{PD}/m1_recheck_02", "m1"))
    res, err = pool_run(jobs)
    res = sorted(res, key=lambda r: (r["id"], r["run"]))
    json.dump({"runs": res, "errors": err, "cumulative_jpy": budget.spent}, open(f"{PD}/m1_summary_02.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    for r in res:
        print(r["id"], r["run"], "raw", r["raw_item_count"], "acc", r["accepted"], "tgt_acc", r["accepted_targets"], "tgt_sl", r["v2_shortlist_targets"],
              "subj", r["subject_included"], "cost", r["cost_jpy"])
    print("errors", err, "cum", budget.spent)


def stage_extract(plan: dict, budget: Budget) -> None:
    jobs = []
    for a in plan["articles"]:
        if a.get("extract_n", 0) <= 0:
            continue
        for k in range(1, a["extract_n"] + 1):
            jobs.append(((a["id"], k), extract_one, a, k, budget, None, "extract"))
    est = len(jobs) * EXTRACT_EST
    if budget.spent + est > BUDGET_LIMIT:
        sys.exit(f"budget stop: spent {budget.spent} + est {est} > {BUDGET_LIMIT}")
    res, err = pool_run(jobs)
    res = sorted(res, key=lambda r: (r["id"], r["run"]))
    json.dump({"runs": res, "errors": err, "cumulative_jpy": budget.spent}, open(f"{PD}/extract_summary_02.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    for r in res:
        print(r["id"], r["run"], "raw", r["raw_item_count"], "acc", r["accepted"], "rej", [x["reason"] for x in r["rejected"]], "cost", r["cost_jpy"])
    print("errors", err, "cum", budget.spent)


def stage_final(plan: dict, budget: Budget, group: list) -> None:
    jobs = []
    for aid in group:
        a = get_art(plan, aid)
        for variant, ks in a["final_runs"].items():
            for k in ks:
                jobs.append(((aid, variant, k), run_variant_job, a, variant, k, budget))
    res, err = pool_run(jobs)
    res = sorted(res, key=lambda r: (r["id"], r["variant"], r["run"]))
    path = f"{PD}/final_summary_02_{'_'.join(group)}.json"
    json.dump({"runs": res, "errors": err, "cumulative_jpy": budget.spent}, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for r in res:
        print(r["id"], r["variant"], r["run"], r["stop_reason"], r["final_phrases"], "llm/ph", r["final_llm_or_placeholder_count"],
              r["final_redundancy_status"], "retry" if r["retry_used"] else "-", r["cost_jpy"])
    print("errors", err, "cum", budget.spent)


def stage_v1d(plan: dict, budget: Budget) -> None:
    """任意: Coffee Adv V1+d n=2(効果分離)。必須分完了後・残額>=3のときのみ手動起動。"""
    if BUDGET_LIMIT - budget.spent < 3.0:
        sys.exit(f"budget remaining {BUDGET_LIMIT - budget.spent:.2f} < 3.0: skip")
    a = get_art(plan, "coffee_adv")
    jobs = [(("coffee_adv", "V1d", k), run_variant_job, a, "V1d", k, budget) for k in (1, 2)]
    res, err = pool_run(jobs)
    res = sorted(res, key=lambda r: r["run"])
    json.dump({"runs": res, "errors": err, "cumulative_jpy": budget.spent}, open(f"{PD}/v1d_summary_02.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    for r in res:
        print(r["id"], r["variant"], r["run"], r["stop_reason"], r["final_phrases"], r.get("final_targets"), r["cost_jpy"])
    print("errors", err, "cum", budget.spent)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["m1", "extract", "final", "v1d"])
    ap.add_argument("--group", default="")
    a = ap.parse_args()
    print("family_z_STOP_ALL_present(参考のみ):", bool(glob.glob("er026_output/family_z_production_e2e_01/STOP_ALL")))
    sf = stop_files_present()
    if sf:
        sys.exit(f"STOP files present: {sf}")
    plan = load_plan()
    os.makedirs(PD, exist_ok=True)
    budget = Budget()
    if a.stage == "m1":
        stage_m1(plan, budget)
    elif a.stage == "extract":
        stage_extract(plan, budget)
    elif a.stage == "v1d":
        stage_v1d(plan, budget)
    else:
        stage_final(plan, budget, [x for x in a.group.split(",") if x])
