# ============================================================
# er064_kp_int_01_run.py  (FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01 Round1 / 有料Trial runner、Trial専用・Production非接続)
# 選定/gate/canonicalization/Redundancy QAはProduction関数(er064_kp_opt_01_phase2_run_03 / er064_kp_idiom_trial_01_select経由)。retryなし。
# 使い方: PYTHONPATH=. .venv/Scripts/python.exe er064_kp_int_01_run.py --stage prep|1|2|3
# timeout/監督ループ/自動retryなし。各stageは1回だけ手動起動。外部停止後の再起動禁止。
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

sys.path.insert(0, os.getcwd())
import er009_n1_routing_governance_10_actual_model_cost as pricing  # noqa: E402
import er030_key_phrase_db_hybrid_selector_01 as selector01  # noqa: E402
import er030_key_phrase_db_hybrid_source_reference_contract_01 as src_ref  # noqa: E402
import er064_kp_idiom_trial_01_select as S  # noqa: E402
import er064_kp_int_01_machine as MC  # noqa: E402
import er064_kp_int_01_prompts as PR  # noqa: E402
import er064_kp_opt_01_phase2_run_03 as R  # noqa: E402

OUT = MC.OUT
HARD_STOP = 95.0
JOB_CAP = 2.5
N = {"coffee": 3, "other": 2}
EST = {"std": 1.185, "adv": 0.938}  # 委任文の1 job実測(保守見積)
LEVELS = ("std", "adv")
COMBOS = {  # 名前 -> (M, P)
    "M0P0": ("M0", "P0"), "M1P0": ("M1", "P0"), "M2P0": ("M2", "P0"), "M0P2": ("M0", "P2"), "M2P2": ("M2", "P2"), "M3P4": ("M3", "P4"),
    "M0P1": ("M0", "P1"), "M0P3": ("M0", "P3"), "M0P4": ("M0", "P4"), "M2P4": ("M2", "P4"),
    "M1P2": ("M1", "P2"), "M1P4": ("M1", "P4"), "M3P2": ("M3", "P2"), "M2P1": ("M2", "P1"), "M2P3": ("M2", "P3"), "M3P1": ("M3", "P1"), "M3P3": ("M3", "P3"),
}
STAGES = {1: ("coffee", ["M0P0", "M1P0", "M2P0", "M0P2", "M2P2", "M3P4"]), 2: ("coffee", ["M0P1", "M0P3", "M0P4", "M2P1", "M2P3", "M2P4"])}
STOP_EVT = threading.Event()
cost_lock = threading.Lock()
COST_PATH = f"{OUT}/cost_r1.json"


def stop_present():
    return (glob.glob(f"{OUT}/STOP") + glob.glob("er026_output/family_z_production_e2e_01/STOP_ALL")
            + glob.glob("docs/pm/delegation_log/*STOP_NOTICE*KP-INTEGRATED*"))


def cost_load():
    if os.path.exists(COST_PATH):
        return json.load(open(COST_PATH, encoding="utf-8"))
    return {"budget_round1_jpy": 100.0, "hard_stop_jpy": HARD_STOP, "job_cap_jpy": JOB_CAP, "model": S.MODEL, "usd_jpy": pricing.USD_TO_JPY,
            "pricing_source": "er005_output/cost_baseline_01/pricing_snapshot.json (via er009 PRICING_USD_PER_M)", "calls": []}


def spent():
    return round(sum(c["cost_jpy"] for c in cost_load()["calls"]), 4)


def cost_append(rec):
    with cost_lock:
        c = cost_load()
        c["calls"].append(rec)
        c["cumulative_jpy"] = round(sum(x["cost_jpy"] for x in c["calls"]), 4)
        json.dump(c, open(COST_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


class Client2(S.UsageClient):
    """UsageClient + reasoning token分離 + 呼出ごとにcost_r1.jsonへ即時追記(model_id/入力/出力/reasoning token)。"""

    def __init__(self, tag, phase):
        super().__init__(label=tag)
        outer = self

        class _Resp:
            def create(self, **kw):
                t0 = time.time()
                started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
                r = outer._real.responses.create(**kw)
                u = getattr(r, "usage", None)
                usage = {}
                if u is not None:
                    usage = {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None),
                             "reasoning_tokens": getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", 0) or 0,
                             "cached_input_tokens": getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0}
                rec = {"tag": tag, "phase": phase, "started_at": started, "model": r.model, "response_id": r.id, "usage": usage,
                       "elapsed_sec": round(time.time() - t0, 3),
                       "cost_jpy": pricing.cost_jpy_for_call("openai", r.model, usage.get("input_tokens"), usage.get("cached_input_tokens"), usage.get("output_tokens"))}
                outer.log.append(dict(rec, output_text=(getattr(r, "output_text", None) if phase == "selection" else None)))  # Stage2以降: backup_item等の生出力を保存
                cost_append(rec)
                return r
        self.responses = _Resp()


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def build_ctx(article, combos, levels=LEVELS):
    """(article, level, combo) -> job context。有料呼出なし。"""
    ctx = {}
    for lv in levels:
        key = f"{article}_{lv}"
        from er064_kp_opt_01_upstream_core import read_article
        t = read_article(key)
        for cname in combos:
            m, p = COMBOS[cname]
            b = MC.build_pattern(key, m)
            ids = src_ref.assign_candidate_ids(b["shortlist"])
            corr = src_ref.correct_shortlist_source_span_consistency(ids["shortlist_with_ids"], b["sentence_reference"])
            assert not corr["excluded"], f"span consistency除外あり {key} {cname}: {corr['excluded']}"
            msg = PR.render(p, lv, R.cand_block(b["rows_text"]))
            ctx[(article, lv, cname)] = {"article_text": t, "msg": msg, "id2c": corr["id_to_candidate"], "cids": corr["candidate_ids"],
                                         "sentence_reference": b["sentence_reference"], "rows_sha256": sha(b["rows_text"]),
                                         "n_candidates": len(b["shortlist"]), "prompt_sha256": sha(msg)}
    return ctx


def job(spec, ctx):
    article, level, cname, k = spec
    tag = f"{article}_{level}_{cname}_run{k}"
    if STOP_EVT.is_set() or stop_present():
        raise RuntimeError("STOP present / stop event")
    if spent() >= HARD_STOP:
        STOP_EVT.set()
        raise RuntimeError(f"cumulative >= {HARD_STOP}: stop before job")
    d = f"{OUT}/runs/{tag}"
    os.makedirs(d, exist_ok=True)
    c = ctx[(article, level, cname)]
    t = c["article_text"]
    c_sel, c_qa = Client2(tag, "selection"), Client2(tag, "canon_qa")
    res = {"article": article, "level": level, "combo": cname, "M": COMBOS[cname][0], "P": COMBOS[cname][1], "run": k, "tag": tag,
           "msg_sha256": c["prompt_sha256"], "rows_sha256": c["rows_sha256"], "n_candidates": c["n_candidates"], "model": S.MODEL}
    t0 = time.time()
    gate, viol = R.run_gate(c["msg"], t, c["id2c"], c["cids"], c["sentence_reference"], c_sel, d, tag)
    res.update(selection_status=gate["status"], validation_reasons=gate.get("validation_reasons"), item_reasons=gate.get("item_reasons"),
               topic_slot_filled_by_backup=gate.get("topic_slot_filled_by_backup"), contract_violation=viol)
    parsed = gate.get("parsed") or {}
    res["backup_item"] = parsed.get("backup_item")
    if gate["status"] == "KEY_WORDS_STRUCTURE_PASS":
        items = parsed["items"]
        id2 = c["id2c"]
        res["source_span_missing"] = selector01._verify_source_spans_against_raw_article(items, t)
        res["raw_selected_items"] = items
        res["selected_items"] = [{"rank": i.get("rank"), "role": i.get("key_phrase_role"), "display_phrase": i.get("display_phrase"),
                                  "source_span": i.get("source_span"), "source_candidate_id": i.get("source_candidate_id"),
                                  "ja_gloss": i.get("ja_gloss"), "phrase_type": i.get("phrase_type"),
                                  "evidence": (id2.get(i.get("source_candidate_id")) or {}).get("evidence"),
                                  "candidate_surface": (id2.get(i.get("source_candidate_id")) or {}).get("surface_form")} for i in items]
        qa = S.run_canonicalization_and_qa(t, items, c_qa)
        res["canonicalization_status"] = qa.get("canonicalization_status")
        res["canonicalization_item_reasons"] = [x.get("item_reasons") for x in qa.get("canonicalization_attempts", [])]
        res["canonicalization_attempt_statuses"] = [x.get("status") for x in qa.get("canonicalization_attempts", [])]
        res["redundancy_status"] = qa.get("redundancy_status")
        res["redundancy_duplicate_pairs"] = qa.get("redundancy_duplicate_pairs")
        if qa.get("merged"):
            res["canonicalized"] = [{"rank": i["rank"], "key_phrase": i["key_phrase"], "display_phrase": i["display_phrase"], "ja_gloss": i.get("ja_gloss"),
                                     "normalization_reason": i["normalization_reason"], "qa_overall_status": i["qa_overall_status"]} for i in qa["merged"]["items"]]
            res["merged_overall_status"] = qa["merged"]["overall_status"]
    res["usage"] = {"selection": c_sel.log, "canon_qa": c_qa.log}
    res["cost_jpy"] = round(c_sel.total_cost() + c_qa.total_cost(), 4)
    res["elapsed_sec"] = round(time.time() - t0, 2)
    if res["cost_jpy"] > JOB_CAP:
        STOP_EVT.set()
        res["job_cap_exceeded"] = True
    json.dump(res, open(f"{d}/job_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return res


def state_hashes():
    return {f: (R.sha_file(f) if os.path.exists(f) else None) for f in R.STATE_FILES}


def update_guard(label):
    p = f"{OUT}/state_guard_r1.json"
    g = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    g[label] = state_hashes()
    if "before" in g and label != "before":
        g[f"unchanged_{label}"] = g[label] == g["before"]
    json.dump(g, open(p, "w", encoding="utf-8"), indent=1)
    return g


def fidelity(ctx):
    """M0P0のバイト一致: Production実run Prompt(coffee/meta)、およびPhase2のC0/C1と同一Prompt(sha)。"""
    rep = {}
    p2 = "er064_output/kp_extraction_selection_opt_01/phase2"
    for (art, lv, cname), c in ctx.items():
        key = f"{art}_{lv}"
        if cname == "M0P0" and key in R.PROD_PROMPT:
            rep[f"{key}_M0P0_vs_production_run"] = (open(R.PROD_PROMPT[key], encoding="utf-8").read() == c["msg"])
        for pf in sorted(glob.glob(f"{p2}/prep_stage*_03.json")):
            info = json.load(open(pf, encoding="utf-8"))["info"]
            for cond, cn in (("C0", "M0P0"), ("C1", "M1P0")):
                if cname == cn and f"{key}_{cond}" in info:
                    rep[f"{key}_{cname}_vs_phase2_{cond}"] = (info[f"{key}_{cond}"]["msg_sha256"] == c["prompt_sha256"])
    return rep


def specs_for(article, combos, n):
    return [(article, lv, cn, k) for lv in LEVELS for cn in combos for k in range(1, n + 1)]


def stage_plan(stage):
    if stage in STAGES:
        art, combos = STAGES[stage]
        return art, combos, N["coffee"], list(LEVELS)
    plan = json.load(open(f"{OUT}/stage3_plan_r1.json", encoding="utf-8"))
    return None, plan["combos"], N["other"], plan


def est_cost(specs):
    return round(sum(EST[s[1]] for s in specs), 3)


def stage_prep(stage):
    os.makedirs(OUT, exist_ok=True)
    assert not stop_present(), stop_present()
    if not os.path.exists(f"{OUT}/state_guard_r1.json"):
        update_guard("before")
    ctxs, specs = {}, []
    if stage in STAGES:
        art, combos = STAGES[stage]
        ctxs = build_ctx(art, combos)
        specs = specs_for(art, combos, N["coffee"])
    else:
        plan = json.load(open(f"{OUT}/stage3_plan_r1.json", encoding="utf-8"))
        for art in plan["articles"]:
            ctxs.update(build_ctx(art, plan["combos"]))
            specs += specs_for(art, plan["combos"], N["other"])
    fid = fidelity(ctxs)
    out = {"stage": stage, "n_jobs": len(specs), "est_cost_jpy": est_cost(specs), "spent_jpy": spent(), "fidelity": fid,
           "prompts": {f"{a}_{lv}_{cn}": {"msg_sha256": c["prompt_sha256"], "rows_sha256": c["rows_sha256"], "n_candidates": c["n_candidates"],
                                          "input_tokens_approx": PR.tokens(c["msg"])} for (a, lv, cn), c in ctxs.items()},
           "jobs": [list(s) for s in specs]}
    json.dump(out, open(f"{OUT}/prep_stage{stage}_r1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"jobs": len(specs), "est": out["est_cost_jpy"], "spent": out["spent_jpy"], "fidelity": fid}, ensure_ascii=False, indent=1))


def stage_run(stage):
    os.makedirs(OUT, exist_ok=True)
    if stop_present():
        sys.exit(f"STOP present {stop_present()}")
    ctxs, specs = {}, []
    if stage in STAGES:
        art, combos = STAGES[stage]
        ctxs = build_ctx(art, combos)
        specs = specs_for(art, combos, N["coffee"])
    else:
        plan = json.load(open(f"{OUT}/stage3_plan_r1.json", encoding="utf-8"))
        for art in plan["articles"]:
            ctxs.update(build_ctx(art, plan["combos"]))
            specs += specs_for(art, plan["combos"], N["other"])
    sp, est = spent(), est_cost(specs)
    if sp + est > HARD_STOP:
        sys.exit(f"budget guard: spent {sp} + est {est} > {HARD_STOP}")
    fid = fidelity(ctxs)
    assert all(fid.values()), f"fidelity NG {fid}"
    print("fidelity", fid, "jobs", len(specs), "spent_before", sp, "est", est, flush=True)
    res, err = [], []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(job, s, ctxs): s for s in specs}
        for f in cf.as_completed(futs):
            try:
                res.append(f.result())
            except Exception as e:
                err.append({"job": list(futs[f]), "error": f"{type(e).__name__}: {e}"})
    res.sort(key=lambda r: (r["article"], r["level"], r["combo"], r["run"]))
    json.dump({"stage": stage, "runs": res, "errors": err, "cumulative_jpy": spent(), "fidelity": fid},
              open(f"{OUT}/stage{stage}_summary_r1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for r in res:
        print(r["tag"], r["selection_status"], r.get("canonicalization_status"), r.get("redundancy_status"),
              [i["display_phrase"] for i in r.get("selected_items", [])], r["cost_jpy"], r["elapsed_sec"])
    print("errors", err, "cum", spent())
    update_guard(f"after_stage{stage}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["prep1", "prep2", "prep3", "1", "2", "3"])
    a = ap.parse_args()
    if a.stage.startswith("prep"):
        stage_prep(int(a.stage[-1]))
    else:
        stage_run(int(a.stage))
