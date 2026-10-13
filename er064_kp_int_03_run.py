# ============================================================
# er064_kp_int_03_run.py (FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01 Round3 / 有料Trial runner、Trial専用・Production非接続)
# 使い方: PYTHONPATH=. .venv/Scripts/python.exe er064_kp_int_03_run.py --stage prep0|0|prep1|1
#  Stage0 = (b1)抽出のみ(選定なし、18呼出) / Stage1 = Go時の選定(38 job以内)。各Stageは1回だけ起動。
# retry/監督ループ/timeoutラッパなし。外部停止後の再起動禁止。Go判定は事前登録規則(plan_r3.md)を機械適用するだけ。
# ============================================================
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import er064_kp_int_01_run as RUN  # noqa: E402
import er064_kp_int_01_machine as MC  # noqa: E402
import er064_kp_int_01_eval as EV  # noqa: E402  (Go判定の評価専用。builder側は参照しない)
import er064_kp_idiom_trial_01_extractor as EX  # noqa: E402
import er064_kp_idiom_trial_01_select as S  # noqa: E402
import er064_kp_int_03_b1 as B  # noqa: E402
import er064_kp_opt_01_phase2_run_03 as R  # noqa: E402

OUT = B.OUT
R1 = "er064_output/kp_integrated_opt_01/round1"
R2 = "er064_output/kp_integrated_opt_01/round2"
BUDGET_R3, HARD_STOP_R3 = 60.0, 65.0
TRIAL_PRIOR = 99.00           # Round1 80.7198 + Round2 18.2794 (cost_r1/cost_r2.json)
TRIAL_CAP = 164.0             # 99.00 + 65
STAGE0_CAP = 8.0
EST0_PER_CALL = 0.25          # 設計書L176 / Phase D M1実測(JPY0.25/回/level)
NONVERBATIM_STOP = 0.50
EVAL_KEYS = MC.ARTICLE_KEYS
COFFEE_EXTRA = ("coffee_std", "coffee_adv")   # 揺れ測定: run1(事前登録)に加えrun2,3
RUN.OUT = OUT
RUN.COST_PATH = f"{OUT}/cost_r3.json"
RUN.HARD_STOP = HARD_STOP_R3
RUN.EST = {"std": 1.30, "adv": 1.10}   # P5相当(Round2実績Std~1.0-1.3, Adv~0.9-1.0)を含む保守見積
RUN.COMBOS["M2P5"] = ("M2", "P5")
RUN.COMBOS["M2BP0"] = ("M2B", "P0")
RUN.COMBOS["M2BP5"] = ("M2B", "P5")


def stop_present():
    return (glob.glob(f"{OUT}/STOP") + glob.glob("er026_output/family_z_production_e2e_01/STOP_ALL")
            + glob.glob("docs/pm/delegation_log/*STOP_NOTICE*KP-INTEGRATED*"))
RUN.stop_present = stop_present


def stop_notice_scan():
    return {"all_STOP_NOTICE_files": sorted(glob.glob("docs/pm/delegation_log/*STOP_NOTICE*")), "OUT_STOP": glob.glob(f"{OUT}/STOP"),
            "STOP_ALL": glob.glob("er026_output/family_z_production_e2e_01/STOP_ALL"), "blocking_for_KP": stop_present()}


def guard(label):
    p = f"{OUT}/state_guard_r3.json"
    g = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    g[label] = RUN.state_hashes()
    if "before" in g and label != "before":
        g[f"unchanged_{label}"] = g[label] == g["before"]
    json.dump(g, open(p, "w", encoding="utf-8"), indent=1)


def init_cost():
    if not os.path.exists(RUN.COST_PATH):
        json.dump({"budget_round3_jpy": BUDGET_R3, "hard_stop_jpy": HARD_STOP_R3, "trial_prior_cumulative_jpy": TRIAL_PRIOR, "trial_cap_jpy": TRIAL_CAP,
                   "job_cap_jpy": RUN.JOB_CAP, "model": S.MODEL, "usd_jpy": RUN.pricing.USD_TO_JPY,
                   "pricing_source": "er005_output/cost_baseline_01/pricing_snapshot.json (via er009 PRICING_USD_PER_M)", "calls": []},
                  open(RUN.COST_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# ---------------- Stage 0 ----------------
def stage0_specs():
    s = [(k, 1) for k in EVAL_KEYS] + [(k, n) for k in COFFEE_EXTRA for n in (2, 3)] + [(a, 1) for a in B.NEG_CONTROLS]
    return s


_PRE = {}


def existing_for_any(aid):
    """スレッド外(main)で事前計算した結果を返す(U.patched等のグローバルpatchはスレッド安全でないため)。"""
    return _PRE[aid]


def prewarm(aids):
    import er064_kp_idiom_trial_01_pipeline as P
    R._init()
    for aid in aids:
        if aid in B.NEG_CONTROLS:
            st0 = R.core.run_stage1_for_article(B.article_text(aid), R._dbs)
            _PRE[aid] = (st0, P._canon_set(st0))
        else:
            base, st0, ex = B.existing_for(aid)
            B.build_pattern_m2b(aid, [])
            _PRE[aid] = (st0, ex)


def extract_one(spec):
    aid, k = spec
    if RUN.STOP_EVT.is_set() or stop_present():
        raise RuntimeError("STOP present / stop event")
    if RUN.spent() >= HARD_STOP_R3:
        RUN.STOP_EVT.set()
        raise RuntimeError("hard stop")
    d = f"{B.B1DIR}/{aid}"
    os.makedirs(d, exist_ok=True)
    t = B.article_text(aid)
    lv = B.level_of_id(aid)
    client = RUN.Client2(f"{aid}_b1_run{k}", "b1_extract")
    r = EX.call_extractor(t, lv, S.MODEL, client=client)
    cost = round(client.total_cost(), 4)
    st0, ex = existing_for_any(aid)
    built = B.build_b1(r["parsed"], st0["sentence_units"], ex, t)
    rec = {"id": aid, "level": lv, "run": k, "prompt_sha256": r["prompt_sha256"], "model": r["model"], "response_id": r["response_id"], "usage": r["usage"],
           "elapsed_sec": r["elapsed_sec"], "cost_jpy": cost, "parsed": r["parsed"], "built": built,
           "reasoning_tokens": (client.log[-1]["usage"].get("reasoning_tokens") if client.log else None)}
    if aid not in B.NEG_CONTROLS:
        pat = B.build_pattern_m2b(aid, built["accepted"])
        rec["tier_h_deleted_existing"], rec["tier_h_deleted_b1"] = pat["tier_h_deleted_existing"], pat["tier_h_deleted_b1"]
        rec["tier_h_recompute_base"] = pat["tier_h_recompute_base"]
        rec["b1_added_final"], rec["rows_sha256"] = pat["b1_added"], RUN.sha(pat["rows_text"])
        rec["noop_vs_M2"] = pat["noop_vs_M2"]
    json.dump(rec, open(f"{d}/run{k}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return rec


def go_decision(recs):
    nv_total = nv_bad = zero_calls = 0
    for r in recs:
        v = r["built"]["verbatim"]
        if not v:
            zero_calls += 1
            continue
        nv_total += len(v)
        nv_bad += sum(1 for x in v if not x["verbatim"])
    rate = (nv_bad / nv_total) if nv_total else 0.0
    stops = []
    if rate > NONVERBATIM_STOP:
        stops.append(f"non-verbatim rate {rate:.2f} > {NONVERBATIM_STOP}")
    c = next((r for r in recs if r["id"] == "coffee_adv" and r["run"] == 1), None)
    hit = []
    if c:
        hit = [s for s in c.get("b1_added_final", []) if 2 in EV.anchor_hits(s, "full")]
    go = bool(hit) and not stops
    return {"go": go, "rule": "Coffee Adv 事前登録run1のb1予約(Tier H後)に`behind price increases`系(anchor rank2 full一致)が入り、かつSTOP条件なし",
            "coffee_adv_run1_b1_added_final": (c or {}).get("b1_added_final"), "anchor2_hit": hit, "stops": stops,
            "nonverbatim": {"outputs_total_in_calls_with_output": nv_total, "nonverbatim": nv_bad, "rate": round(rate, 4), "zero_output_calls": zero_calls}}


def stage0(prep_only):
    os.makedirs(OUT, exist_ok=True)
    stops = stop_notice_scan()
    if stops["blocking_for_KP"]:
        sys.exit(f"STOP present {stops}")
    specs = stage0_specs()
    est = round(len(specs) * EST0_PER_CALL, 3)
    init_cost()
    if not os.path.exists(f"{OUT}/state_guard_r3.json"):
        guard("before")
    sp = RUN.spent()
    assert sp + est <= STAGE0_CAP and TRIAL_PRIOR + sp + est <= TRIAL_CAP, f"budget guard {sp}+{est}"
    info = {"stage": 0, "n_calls": len(specs), "est_jpy": est,
            "est_basis": "18呼出 x JPY0.25(設計書L176)=4.5。Phase D実測は0.116/呼出(2.09/18=約2.1)。Stage0上限8で停止", "spent": sp,
            "stage0_cap": STAGE0_CAP, "stop_scan": stops, "calls": [list(s) for s in specs], "prompt_sha256": EX.prompt_sha()}
    json.dump(info, open(f"{OUT}/prep_stage0_r3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: info[k] for k in ("n_calls", "est_jpy", "spent", "prompt_sha256")}), flush=True)
    if prep_only:
        return
    recs, err = [], []
    prewarm(sorted({s[0] for s in specs}))
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(extract_one, s): s for s in specs}
        for f in cf.as_completed(futs):
            try:
                recs.append(f.result())
            except Exception as e:
                err.append({"call": list(futs[f]), "error": f"{type(e).__name__}: {e}"})
    recs.sort(key=lambda r: (r["id"], r["run"]))
    go = go_decision([r for r in recs if r["id"] not in B.NEG_CONTROLS])
    json.dump({"stage": 0, "n_ok": len(recs), "errors": err, "cumulative_round3_jpy": RUN.spent(), "go": go},
              open(f"{OUT}/stage0_summary_r3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for r in recs:
        print(r["id"], r["run"], "raw", r["built"]["raw_item_count"], "acc", [c["surface_form"] for c in r["built"]["accepted"]], r["cost_jpy"])
    print("errors", err, "cum", RUN.spent())
    print("GO", json.dumps(go, ensure_ascii=False))
    guard("after_stage0")


# ---------------- Stage 1 ----------------
_cache = {}
_orig_bp = MC.build_pattern


def load_run1(key):
    return json.load(open(f"{B.B1DIR}/{key}/run1.json", encoding="utf-8"))


def bp(key, pat):
    if pat == "M2B":
        if key not in _cache:
            rec = load_run1(key)
            out = B.build_pattern_m2b(key, rec["built"]["accepted"])
            out["secs"] = 0
            _cache[key] = out
        return _cache[key]
    return _orig_bp(key, pat)
MC.build_pattern = bp


def stage1_specs():
    s = []
    for k in range(1, 6):
        s += [("coffee", "adv", "M2BP0", k), ("coffee", "adv", "M2BP5", k), ("coffee", "std", "M2BP0", k)]
    for k in range(1, 4):
        s.append(("coffee", "std", "M2BP5", k))
    for lv in RUN.LEVELS:
        s += [("coffee", lv, "M2P0", k) for k in (4, 5)]
        s += [("meta", lv, "M2P0", k) for k in (3, 4)] + [("meta", lv, "M2P5", k) for k in (3, 4)]
    for a in ("meta", "hormuz"):
        for lv in RUN.LEVELS:
            s += [(a, lv, "M2BP0", k) for k in (1, 2)]
    return s


def noop_cells(specs):
    """b1が何も追加しない(shortlistがM2と同一)セルのM2B jobは実行しない(M2P0 runと同一Promptになるため)。"""
    noop = {}
    for (a, lv, cn, k) in specs:
        if cn.startswith("M2B"):
            key = f"{a}_{lv}"
            noop[key] = bool(bp(key, "M2B").get("noop_vs_M2"))
    return noop


def stage1(prep_only):
    os.makedirs(OUT, exist_ok=True)
    stops = stop_notice_scan()
    if stops["blocking_for_KP"]:
        sys.exit(f"STOP present {stops}")
    g = json.load(open(f"{OUT}/stage0_summary_r3.json", encoding="utf-8"))["go"]
    if not g["go"]:
        sys.exit(f"No-Go (事前登録): {g}")
    specs = stage1_specs()
    noop = noop_cells(specs)
    specs = [s for s in specs if not (s[2].startswith("M2B") and noop.get(f"{s[0]}_{s[1]}"))]
    ctx = {}
    for a in sorted({s[0] for s in specs}):
        combos = sorted({s[2] for s in specs if s[0] == a})
        ctx.update(RUN.build_ctx(a, combos))
    est = RUN.est_cost(specs)
    sp = RUN.spent()
    assert sp + est <= BUDGET_R3 and TRIAL_PRIOR + sp + est <= TRIAL_CAP, f"budget guard {sp}+{est}"
    info = {"stage": 1, "n_jobs": len(specs), "est_cost_jpy": est, "spent_round3_jpy": sp, "trial_cumulative_if_est": round(TRIAL_PRIOR + sp + est, 2),
            "noop_cells": noop, "stop_scan": stops,
            "prompts": {f"{a}_{lv}_{cn}": {"msg_sha256": c["prompt_sha256"], "rows_sha256": c["rows_sha256"], "n_candidates": c["n_candidates"]} for (a, lv, cn), c in ctx.items()},
            "jobs": [list(s) for s in specs]}
    json.dump(info, open(f"{OUT}/prep_stage1_r3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: info[k] for k in ("n_jobs", "est_cost_jpy", "spent_round3_jpy", "trial_cumulative_if_est", "noop_cells")}), flush=True)
    if prep_only:
        return
    res, err = [], []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(RUN.job, s, ctx): s for s in specs}
        for f in cf.as_completed(futs):
            try:
                res.append(f.result())
            except Exception as e:
                err.append({"job": list(futs[f]), "error": f"{type(e).__name__}: {e}"})
    res.sort(key=lambda r: (r["article"], r["level"], r["combo"], r["run"]))
    json.dump({"stage": 1, "runs": res, "errors": err, "cumulative_round3_jpy": RUN.spent()},
              open(f"{OUT}/stage1_summary_r3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for r in res:
        print(r["tag"], r["selection_status"], r.get("canonicalization_status"), r.get("redundancy_status"),
              [i["display_phrase"] for i in r.get("selected_items", [])], r["cost_jpy"], r["elapsed_sec"])
    print("errors", err, "cum_round3", RUN.spent())
    guard("after_stage1")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["prep0", "0", "prep1", "1"])
    a = ap.parse_args()
    (stage0 if a.stage.endswith("0") else stage1)(a.stage.startswith("prep"))
