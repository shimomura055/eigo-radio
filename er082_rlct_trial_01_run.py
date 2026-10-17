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
import glob
import os
import re
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
        res["reselect"] = _reselect_summary(sv)
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


CORRECTABLE = {"M2": "M2c", "M3": "M3c"}      # --correct-from → 出力method名(委任_07 D6)


def _restore_source(src_root: str, article: str, method: str) -> dict:
    """補正元method(読み取り専用)から、最終sel・検証結果(notes込み)・初回B3を復元する。
    復元できなければSTOP(推測で補わない)。"""
    sdir = f"{src_root}/{article}/{method}"
    rp = f"{sdir}/result.json"
    if not os.path.isfile(rp):
        raise RuntimeError(f"[STOP] 補正元のresult.jsonが無い: {rp}")
    src = load_json(rp)
    if src.get("status") != "COMPLETED":
        raise RuntimeError(f"[STOP] 補正元がCOMPLETEDでない({src.get('status')}): {rp}")
    rounds = src["reselect"]["rounds"]
    # 検証結果: _work/verify_r*.json の parsed から notes ごと復元(round はファイル名の番号)
    verdicts = {}
    files = sorted(glob.glob(f"{sdir}/_work/verify_r*.json"), key=lambda p: int(re.search(r"verify_r(\d+)\.json$", p).group(1)))
    for p in files:
        rnum = int(re.search(r"verify_r(\d+)\.json$", p).group(1))
        for v in load_json(p)["parsed"]["verifications"]:
            verdicts[v["fact_id"]] = {"verdict": v["verdict"], "verification_notes": v["verification_notes"], "round": rnum}
    # 欠落(検証結果なし=安全側AMBIGUOUS)はrounds[*].missing_verificationに記録済み → その旨でnotesを再現
    for rd in rounds:
        for i in rd.get("missing_verification", []):
            verdicts.setdefault(i, {"verdict": "AMBIGUOUS", "verification_notes": "(検証結果なし、安全側でAMBIGUOUS扱い)",
                                    "round": rd["round"]})
    fv = {k: v["verdict"] for k, v in src["final_verdicts"].items()}
    got = {k: v["verdict"] for k, v in verdicts.items()}
    if fv != got:
        raise RuntimeError(f"[STOP] verify_*.jsonから復元した判定がresult.jsonのfinal_verdictsと一致しない: {fv} vs {got}")
    r_last = len(rounds) - 1
    # 最終selを生成したB3呼出の保存物
    init_p = f"{src_root}/{article}/M2/_work/initial_b3.json"      # M3もM2の初回B3を共有(設計4-1)
    if r_last == 0:
        sel_p, sel_label = init_p, "initial"
    else:
        sel_label = rounds[-1].get("b3_label") or f"reselect{r_last}"
        sel_p = f"{sdir}/_work/b3_{sel_label}.json"
    for p in (init_p, sel_p):
        if not os.path.isfile(p):
            raise RuntimeError(f"[STOP] 補正元のB3保存物が無い: {p}")
    sel = load_json(sel_p)
    if list(sel["parsed"]["selected_fact_ids"]) != list(src["selected_fact_ids"]):
        raise RuntimeError(f"[STOP] 復元したselと補正元result.jsonの選定Factが一致しない: {sel_p}")
    sel_visible = {i: v for i, v in verdicts.items() if v["round"] < r_last}   # sel生成B3呼出の候補Ledgerに見えていた判定
    brief_p = f"{sdir}/storyline_b3/selected_brief.md"
    return {"src": src, "sdir": sdir, "verdicts": verdicts, "sel": sel, "sel_label": sel_label,
            "sel_visible": sel_visible, "b3_used": r_last, "init_path": init_p,
            "init_sha256": lib.sha256_file(init_p),
            "brief_sha256": lib.sha256_file(brief_p) if os.path.isfile(brief_p) else None}


def run_correction(article: str, from_method: str, stage: str, client, budget: Budget, out_root: str,
                   usage_log: str, dry_run: bool, src_root: str) -> dict:
    """委任_07 D6: 既存M2/M3を変更せず、<method>c を新規作成して最終B3確認パスだけを実行する。"""
    if from_method not in CORRECTABLE:
        raise SystemExit(f"--correct-from は {sorted(CORRECTABLE)} のみ")
    method = CORRECTABLE[from_method]
    inputs_dir = lib.copy_inputs(article, out_root)
    data = lib.load_article_inputs(inputs_dir)
    topic, draft = data["topic"], data["draft"]
    mdir = f"{out_root}/{article}/{method}"
    work = f"{mdir}/_work"
    lib.assert_under_out_root(mdir, out_root)
    if os.path.abspath(mdir).startswith(os.path.abspath(f"{src_root}/{article}/{from_method}") + os.sep) \
            or os.path.abspath(mdir) == os.path.abspath(f"{src_root}/{article}/{from_method}"):
        raise RuntimeError("[STOP] 補正出力先が補正元と重なる")
    if os.path.exists(mdir):
        if not dry_run:
            raise RuntimeError(f"[STOP] {mdir} は既に存在する(有料runの二重実行防止)。")
        shutil.rmtree(mdir)
    os.makedirs(work, exist_ok=True)
    rs = _restore_source(src_root, article, from_method)
    prefix = f"{stage}|{article}|{method}"
    src = rs["src"]
    res = {"article": article, "method": method, "stage": stage, "dry_run": dry_run,
           "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "usage_basis": "SYNTHETIC_DRYRUN_STUB" if dry_run else "OFFICIAL_API_RESPONSE",
           "corrected_from": from_method, "correct_source_root": src_root,
           "reused_initial_b3_sha256": rs["init_sha256"], "reused_verdict_ids": sorted(rs["verdicts"]),
           "pre_correction_selected_fact_ids": src.get("selected_fact_ids"),
           "pre_correction_storyline_sha256": lib.sha256_bytes((src.get("selected_storyline") or "").encode("utf-8")),
           "pre_correction_brief_sha256": rs["brief_sha256"],
           "pre_correction_cost_total_jpy": src["cost"]["total"]["total_jpy"],
           "pre_correction_basis": src.get("usage_basis")}
    verify_records = []
    resume = {"sel": rs["sel"], "verdicts": rs["verdicts"], "sel_visible": rs["sel_visible"],
              "sel_label": rs["sel_label"], "b3_used": rs["b3_used"]}
    sv = lib.select_then_verify(client, topic, draft, work_dir=work, stage_prefix=prefix, budget=budget,
                                cap=(from_method == "M3"), resume=resume,
                                shared_initial=(load_json(rs["init_path"]) if from_method == "M3" else None))
    res["reselect"] = _reselect_summary(sv)
    for r in sv["rounds"]:
        if r.get("verify_record"):
            verify_records.append(r["verify_record"])
    if sv["status"] != "COMPLETED":
        res.update({"status": "UNRESOLVED", "unresolved": {k: sv[k] for k in sv if k not in ("rounds",)},
                    "selected_fact_ids": None})
        out = _finish(res, mdir, work, usage_log, prefix, verify_records, {}, article, data, None, {})
    else:
        selection, ledger_text, final_verdicts = sv["selection"], sv["ledger_text"], sv["verdicts"]
        res["shared_initial_b3_from"] = f"{stage}|{article}|M2|b3_initial" if from_method == "M3" else None
        lib.write_run_layout(mdir, topic, ledger_text, selection, {"method": method, "corrected_from": from_method})
        contract = lib.contract_check(mdir, out_root)
        res["status"] = "COMPLETED"
        out = _finish(res, mdir, work, usage_log, prefix, verify_records, {}, article, data, selection,
                      final_verdicts, contract)
    corr = out["cost"]["total"]
    out["cost_correction_only"] = corr
    out["cost_production_equivalent"] = {
        "source_method_total_jpy": src["cost"]["total"]["total_jpy"], "correction_total_jpy": corr["total_jpy"],
        "total_jpy": round(src["cost"]["total"]["total_jpy"] + corr["total_jpy"], 3),
        "note": "補正元method実測(Trial費用)+補正費用。共有初回B3(M3c)の帰属はaggregateで加算"}
    out["brief_changed_vs_pre_correction"] = (
        (lib.sha256_file(f"{mdir}/storyline_b3/selected_brief.md") != rs["brief_sha256"])
        if out["status"] == "COMPLETED" and rs["brief_sha256"] else None)
    save_json(f"{mdir}/result.json", out)
    return out


def _reselect_summary(sv: dict) -> dict:
    return {"status": sv["status"], "rounds": sv["rounds"], "reselect_count": sv.get("reselect_count", 0),
            "confirm_pass_count": sv.get("confirm_pass_count", 0),
            "b3_calls_after_initial": sv.get("b3_calls_after_initial", 0),
            "b3_calls_before_this_run": sv.get("b3_calls_before_this_run", 0),
            "final_confirm_pass": sv.get("final_confirm_pass"), "unmet": sv.get("unmet")}


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
    if a.correct_from:
        arts = [x for x in (a.article or "").split(",") if x]
        meths = [x for x in a.correct_from.split(",") if x]
        if not arts:
            raise SystemExit("--correct-from には --article が必要")
        for m in meths:
            if m not in CORRECTABLE:
                raise SystemExit(f"--correct-from は {sorted(CORRECTABLE)} のみ")
        for art in arts:
            if art not in ARTICLES:
                raise SystemExit(f"unknown article {art}")
        return [(art, CORRECTABLE[m], a.stage or "1a") for art in arts for m in meths]     # Budget stage=1a
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
    ap.add_argument("--correct-from", default=None, help="M2 / M3 / M2,M3: 最終B3確認パスのみ追加実行し M2c/M3c を新規作成")
    ap.add_argument("--correct-source-root", default=None, help="補正元(既存M2/M3)のroot。読み取り専用。既定=--out")
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
            if a.correct_from:
                src_from = [k for k, v in CORRECTABLE.items() if v == m][0]
                r = run_correction(art, src_from, stage, client, budgets[stage], out, usage_log, a.dry_run,
                                   a.correct_source_root or out)
            else:
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
