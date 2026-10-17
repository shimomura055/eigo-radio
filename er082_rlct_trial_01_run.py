# ============================================================
# er082_rlct_trial_01_run.py
# FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_04 (CP1): Trial専用runner(Production非接続)
# ============================================================
# 使い方(dry-run=API 0):
#   .venv\Scripts\python.exe er082_rlct_trial_01_run.py --dry-run --all-articles --all-methods --out er082_output/rlct_trial_01/_dryrun
# 有料run(次委任以降、Fable確認後のみ。PAID_CONFIRM_TOKEN必須):
#   .venv\Scripts\python.exe er082_rlct_trial_01_run.py --paid-confirm <TOKEN> --plan 1a --out er082_output/rlct_trial_01
# ============================================================
from __future__ import annotations

import argparse
import datetime
import os
import shutil
import subprocess
import sys

import er082_rlct_trial_01_lib as lib
from er082_rlct_trial_01_lib import (ARTICLES, METHODS, OUT_ROOT, Budget, BudgetStop, load_json, save_json)

STOP_SENTINEL_PATHS = ["er026_output/family_z_production_e2e_01/STOP_ALL"]
MANAGED_ID = "FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01"


def _scenario(data: dict) -> dict:
    rej = [fid for fid, v in data["m0_verdicts"].items() if v["verdict"] == "REJECTED"]
    return {
        "m0_verdicts": data["m0_verdicts"], "m0_evidence": data["m0_evidence"],
        "n_facts_all": len(data["draft"]["facts"]),
        "m0_total_ws_calls": (data["m0_verification_record"].get("search_usage") or {}).get("web_search_call_count", 14),
        "b3_initial_extra_ids": rej[:1],      # REJECTEDを持つ記事では初回B3がそれを選ぶ状況を模擬(再選定loopを動かす)
    }


def _selection_from_stored(data: dict) -> dict:
    ev = data["m0_evidence"]
    parsed = {"selected_storyline": ev["selected_storyline"], "fact_tests": ev["fact_tests"],
              "selected_fact_ids": ev["selected_fact_ids"], "selected_fact_brief": ev["selected_fact_brief_text"],
              "recheck_note": ev.get("recheck_note")}
    return {"parsed": parsed, "model": data["b3_runtime"].get("model_id_actual"),
            "response_id": data["b3_runtime"].get("response_id"), "attempts": 1, "retried": False,
            "soft_warnings": ev.get("soft_warnings", []), "attempts_log": [], "reused_existing_b3": True}


def _ws_stats(work: str) -> dict:
    rows = lib.read_jsonl(f"{work}/web_search_calls.jsonl")
    by_type = lib._count_by(rows, "action_type")
    return {"web_search_call_rows": len(rows), "by_action_type": by_type,
            "query_count": sum(len(r["queries"]) for r in rows)}


def _cost_for(usage_log: str, prefix: str) -> dict:
    allc = lib.cost_by_stage_tag(usage_log, theme=lib.THEME_TAG)
    sel = {k: v for k, v in allc.items() if k.startswith(prefix + "|")}
    tot = {"llm_jpy": 0.0, "web_search_jpy": 0.0, "total_jpy": 0.0, "calls": 0, "web_search_calls": 0}
    for v in sel.values():
        for k in tot:
            tot[k] += v[k]
    tot = {k: round(v, 3) if isinstance(v, float) else v for k, v in tot.items()}
    return {"by_step": {k.split("|", 3)[3]: v for k, v in sel.items()}, "total": tot}


def run_method(article: str, method: str, stage: str, client, budget: Budget, out_root: str, usage_log: str,
               dry_run: bool) -> dict:
    inputs_dir = lib.copy_inputs(article, out_root)
    data = lib.load_article_inputs(inputs_dir)
    topic, draft = data["topic"], data["draft"]
    all_ids = [f["fact_id"] for f in draft["facts"]]
    mdir = f"{out_root}/{article}/{method}"
    work = f"{mdir}/_work"
    lib.assert_under_out_root(mdir, out_root)
    if os.path.exists(mdir):
        if not dry_run:
            raise RuntimeError(f"[STOP] {mdir} は既に存在する(有料runの二重実行防止)。")
        shutil.rmtree(mdir)
    os.makedirs(work, exist_ok=True)
    prefix = f"{stage}|{article}|{method}"
    res = {"article": article, "method": method, "stage": stage, "dry_run": dry_run,
           "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "usage_basis":
           "SYNTHETIC_DRYRUN_STUB" if dry_run else "OFFICIAL_API_RESPONSE"}
    models = {}
    final_verdicts, selection, ledger_text, m0_reused = {}, None, None, False
    verify_records = []

    if method == "M0":
        if ARTICLES[article]["b3_reusable"]:
            selection, ledger_text, m0_reused = _selection_from_stored(data), data["m0_ledger_text"], True
        else:
            selection = lib.select_b3_trial(client, topic, data["m0_ledger_text"], work_dir=work, label="m0",
                                            stage_tag=f"{prefix}|b3", budget=budget)
            ledger_text = data["m0_ledger_text"]
        final_verdicts = dict(data["m0_verdicts"])
    elif method == "M0b":
        selection = lib.select_b3_trial(client, topic, data["m0_ledger_text"], work_dir=work, label="m0b",
                                        stage_tag=f"{prefix}|b3", budget=budget)
        ledger_text, final_verdicts = data["m0_ledger_text"], dict(data["m0_verdicts"])
    elif method in ("M0p", "M1"):
        cap = method == "M1"
        v = lib.verify_facts_trial(client, topic, draft, all_ids, cap=cap, work_dir=work, label="full",
                                   stage_tag=f"{prefix}|ledger", budget=budget, est_jpy=lib.EST_VERIFY_FULL_JPY)
        verify_records.append(v["record"])
        final_verdicts = {x["fact_id"]: x for x in v["parsed"]["verifications"]}
        ledger_text, counts, _kept = lib.vfl01.build_verified_ledger_text(draft, v["parsed"])
        res["verdict_counts"] = counts
        if method == "M1":
            selection = lib.select_b3_trial(client, topic, ledger_text, work_dir=work, label="m1",
                                            stage_tag=f"{prefix}|b3", budget=budget)
        else:
            # M0p: Ledger再検証のみ(B3なし)。台帳完全性だけ確認
            lib.save_text(f"{mdir}/research_ledger/verified_fact_ledger.txt", ledger_text)
    elif method in ("M2", "M3"):
        shared = None
        if method == "M3":
            p = f"{out_root}/{article}/M2/_work/initial_b3.json"
            if not os.path.isfile(p):
                raise RuntimeError(f"[STOP] M3はM2の初回B3選定を共有する(設計4-1)。先にM2を実行: {p}")
            shared = load_json(p)
        sv = lib.select_then_verify(client, topic, draft, work_dir=work, stage_prefix=prefix, budget=budget,
                                    cap=(method == "M3"), shared_initial=shared)
        res["reselect"] = {"status": sv["status"], "rounds": sv["rounds"],
                           "reselect_count": sv.get("reselect_count", len(sv["rounds"]) - 1)}
        for r in sv["rounds"]:
            if r.get("verify_record"):
                verify_records.append(r["verify_record"])
        if sv["status"] != "COMPLETED":
            # 未成立: 確定ファイル(research_ledger/storyline_b3)を出さない(設計4-3)
            res.update({"status": "UNRESOLVED", "unresolved": {k: sv[k] for k in sv if k not in ("rounds",)},
                        "selected_fact_ids": None})
            return _finish(res, mdir, work, usage_log, prefix, verify_records, models, article, data, None, {})
        selection, ledger_text = sv["selection"], sv["ledger_text"]
        final_verdicts = sv["verdicts"]
        res["shared_initial_b3_from"] = (f"{stage}|{article}|M2|b3_initial" if shared is not None else None)
    else:
        raise ValueError(method)

    contract = None
    if selection is not None:
        lib.write_run_layout(mdir, topic, ledger_text, selection,
                             {"method": method, "reused_existing_b3": m0_reused})
        contract = lib.contract_check(mdir, out_root)
    elif method == "M0p":
        contract = {"ledger_complete": lib.contract_check_ledger_only(mdir)}
    res["status"] = "COMPLETED"
    return _finish(res, mdir, work, usage_log, prefix, verify_records, models, article, data, selection,
                   final_verdicts, contract)


def _finish(res, mdir, work, usage_log, prefix, verify_records, models, article, data, selection, final_verdicts,
            contract=None) -> dict:
    sel_ids = selection["parsed"]["selected_fact_ids"] if selection else res.get("selected_fact_ids")
    res["selected_fact_ids"] = sel_ids
    if selection:
        res["selected_storyline"] = selection["parsed"]["selected_storyline"]
        res["b3_model"] = selection.get("model")
        res["b3_attempts"] = selection.get("attempts")
        res["ambiguous_central"] = lib.ambiguous_central_assertions(
            selection["parsed"]["selected_storyline"], data["draft"], final_verdicts)
    if sel_ids and final_verdicts:
        res["known_defect_status"] = lib.known_defect_status(article, sel_ids, final_verdicts)
    if final_verdicts:
        res["verdict_transitions"] = lib.verdict_transitions(data["m0_verdicts"], final_verdicts)
        res["final_verdicts"] = {k: {"verdict": v["verdict"]} for k, v in final_verdicts.items()}
    m0_model = (data["ledger_runtime"].get("ledger_verification") or {}).get("model_id_actual")
    res["verifier_models"] = sorted({r["model"] for r in verify_records})
    res["verifier_model_matches_m0"] = all(r["model"] == m0_model for r in verify_records) if verify_records else None
    res["m0_verifier_model"] = m0_model
    res["web_search_calls"] = _ws_stats(work)
    res["verify_requests"] = verify_records
    res["cost"] = _cost_for(usage_log, prefix)
    res["contract"] = contract
    res["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_json(f"{mdir}/result.json", res)
    return res


def jobs_from_args(a) -> list:
    if a.plan:
        return [(art, m, a.plan) for art, m in lib.PLAN[a.plan]]
    arts = list(ARTICLES) if a.all_articles else [x for x in (a.article or "").split(",") if x]
    meths = METHODS if a.all_methods else [x for x in (a.method or "").split(",") if x]
    if not arts or not meths:
        raise SystemExit("--article/--method (または --all-articles/--all-methods/--plan) が必要")
    jobs = []
    for art in arts:
        if art not in ARTICLES:
            raise SystemExit(f"unknown article {art}")
        for m in METHODS:
            if m in meths:
                jobs.append((art, m, a.stage or ARTICLES[art]["stage"]))
    return jobs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--paid-confirm", default=None)
    ap.add_argument("--article")
    ap.add_argument("--all-articles", action="store_true")
    ap.add_argument("--method")
    ap.add_argument("--all-methods", action="store_true")
    ap.add_argument("--stage", choices=list(lib.STAGE_CAPS_JPY))
    ap.add_argument("--plan", choices=["1a", "1b"])
    ap.add_argument("--out", default=OUT_ROOT)
    ap.add_argument("--other-spend-today-jpy", type=float, default=0.0)
    a = ap.parse_args(argv)
    if a.dry_run == bool(a.paid_confirm):
        raise SystemExit("--dry-run か --paid-confirm のどちらか一方だけ指定する")
    if a.paid_confirm and a.paid_confirm != lib.PAID_CONFIRM_TOKEN:
        raise SystemExit("--paid-confirm トークン不一致。有料runはFable確認後の次委任のみ")
    jobs = jobs_from_args(a)
    out = a.out
    os.makedirs(out, exist_ok=True)
    # STOP確認(有料時はhelperも実行。rc=3で停止)
    for p in [f"{out}/STOP"] + STOP_SENTINEL_PATHS:
        if os.path.exists(p):
            print(f"[STOP] sentinel {p}")
            return 3
    if a.paid_confirm:
        rc = subprocess.call([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MANAGED_ID,
                              "--run-dir", out, "--out", f"{out}/stop_check.json"])
        if rc == 3:
            print("[STOP] stop_scope_check rc=3")
            return 3
    arts = sorted({j[0] for j in jobs})
    before = lib.integrity_snapshot(arts)
    save_json(f"{out}/integrity_before.json", before)
    real_log = f"{out}/raw_usage_log.jsonl"
    lib.ensure_cost_logger(real_log)             # R-02: プロセス開始時に必ず実行
    stub_log = f"{out}/stub_usage_log.jsonl"
    if a.dry_run:
        if os.path.exists(stub_log):
            os.remove(stub_log)
        usage_log = stub_log
    else:
        usage_log = real_log
    budgets, clients, results, rc = {}, {}, [], 0
    try:
        for art, m, stage in jobs:
            if stage not in budgets:
                budgets[stage] = Budget(usage_log, stage, out_root=out, other_spend_today_jpy=a.other_spend_today_jpy)
            if a.dry_run:
                if art not in clients:
                    inputs_dir = lib.copy_inputs(art, out)
                    clients[art] = lib.StubClient(_scenario(lib.load_article_inputs(inputs_dir)), stub_log)
                client = clients[art]
            else:
                client = clients.setdefault("real", lib.vfl01.get_client())
            print(f"[RLCT] {'DRYRUN' if a.dry_run else 'PAID'} stage={stage} {art} {m}")
            r = run_method(art, m, stage, client, budgets[stage], out, usage_log, a.dry_run)
            results.append({"article": art, "method": m, "status": r["status"],
                            "total_jpy": r["cost"]["total"]["total_jpy"],
                            "selected": r.get("selected_fact_ids")})
    except BudgetStop as exc:
        print(str(exc))
        rc = 4
    after = lib.integrity_snapshot(arts)
    cmp_ = lib.compare_snapshots(before, after)
    save_json(f"{out}/integrity_after.json", after)
    save_json(f"{out}/integrity_check.json", cmp_)
    summary = {"dry_run": a.dry_run, "jobs": len(jobs), "completed": results, "integrity_identical": cmp_["identical"],
               "real_usage_log_rows": len(lib.read_jsonl(real_log)),
               "stub_usage_rows": len(lib.read_jsonl(stub_log)) if a.dry_run else None,
               "stub_calls_total": sum(c.calls for c in clients.values() if hasattr(c, "calls")) if a.dry_run else None,
               "guard_constants": {"stage_caps": lib.STAGE_CAPS_JPY, "cum_cap": lib.CUM_CAP_JPY,
                                   "expected_total": lib.EXPECTED_TOTAL_JPY},
               "spent_by_stage": {s: b.spent() for s, b in budgets.items()}}
    save_json(f"{out}/{'dryrun_summary' if a.dry_run else 'run_summary'}.json", summary)
    if not cmp_["identical"]:
        print("[STOP] integrity mismatch", cmp_["diffs"][:5])
        return 5
    return rc


if __name__ == "__main__":
    sys.exit(main())
