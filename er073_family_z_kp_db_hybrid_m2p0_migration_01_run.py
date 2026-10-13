# er073_family_z_kp_db_hybrid_m2p0_migration_01_run.py
# FAMILY-Z-KP-DB-HYBRID-M2P0-MIGRATION-TRIAL-01 委任_01 Phase 2 Trial隔離runner (Production無変更・未採用)
# Production module(er003/er030/er062)はimportのみ。telemetry書込(scaffold._log_kp_backend_telemetry)はno-op化。
# 出力は --out-dir 配下のみ(Melos run_e2e_02/Master Store/HR/attempt_history/telemetryへ書かない)。
# 1 processは1 text_id(n runs)を担当。監督ループ/自動再起動なし。
from __future__ import annotations
import argparse, glob, hashlib, json, os, sys, time

STOP_GLOBS = ["docs/pm/delegation_log/*STOP_NOTICE*"]
STOP_RUN_FILES = ["er026_output/family_z_production_e2e_01/melos/run_e2e_02/STOP",
                  "er026_output/family_z_production_e2e_01/STOP_ALL"]
OLD_STOP_NOTICE_KEY = "FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01"  # 2026-10-12 run_e2e_01事故の旧通知(委任文により非適用)
PROD_PY = ["er003_v1_n3_01_scaffold_generate.py", "er003_key_words_canonicalization.py", "er003_key_words_production.py",
           "er030_key_phrase_db_hybrid_selector_01.py", "er030_key_phrase_db_hybrid_core_01.py",
           "er030_key_phrase_db_hybrid_m2_supply_01.py", "er030_key_phrase_db_hybrid_source_reference_contract_01.py",
           "er062_family_z_writer_01.py", "er062_family_z_structure_01.py", "er026_family_z_fiction_production_runner_01.py"]
TELEMETRY_FILES = ["er030_output/kp_backend_telemetry_01/telemetry.jsonl", "er011_output/attempt_history.jsonl",
                   "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
                   "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
                   "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl"]
RUN_E2E_02 = "er026_output/family_z_production_e2e_01/melos/run_e2e_02"


class BudgetExceeded(RuntimeError):
    pass


class StopSentinel(RuntimeError):
    pass


def check_stop() -> list:
    found = []
    for g in STOP_GLOBS:
        found += [p for p in glob.glob(g) if OLD_STOP_NOTICE_KEY not in p]
    found += [p for p in STOP_RUN_FILES if os.path.exists(p)]
    return found


def sha_file(p: str) -> str:
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def line_count(p: str):
    if not os.path.exists(p):
        return None
    with open(p, "rb") as f:
        return sum(1 for _ in f)


def state_snapshot() -> dict:
    run = {}
    for root, _d, files in os.walk(RUN_E2E_02):
        for fn in files:
            p = os.path.join(root, fn).replace("\\", "/")
            run[p] = [os.path.getsize(p), os.path.getmtime(p)]
    return {"prod_py_sha256": {p: sha_file(p) for p in PROD_PY if os.path.exists(p)},
            "telemetry_lines": {p: line_count(p) for p in TELEMETRY_FILES},
            "run_e2e_02_files": len(run),
            "run_e2e_02_digest": hashlib.sha256(json.dumps(run, sort_keys=True).encode()).hexdigest()}


def jaccard(a, b) -> float:
    a, b = set(a), set(b)
    return 1.0 if not (a | b) else len(a & b) / len(a | b)


def norm_phrase(s: str) -> str:
    return " ".join((s or "").lower().split())


def read_cost_rows(path: str) -> list:
    if not os.path.exists(path):
        return []
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def row_cost(r: dict) -> float:
    import er009_n1_routing_governance_10_actual_model_cost as pricing
    if not r.get("success", True) or not r.get("model_id"):
        return 0.0
    return pricing.cost_jpy_for_call("openai", r["model_id"], r.get("input_tokens"), r.get("cached_input_tokens"),
                                     r.get("output_tokens"))


def total_spend(out_dir: str) -> float:
    return sum(row_cost(r) for p in glob.glob(os.path.join(out_dir, "**", "cost_log.jsonl"), recursive=True)
               for r in read_cost_rows(p))


def make_guard(out_dir: str, budget_jpy: float, soft_jpy: float, events: list):
    def guard(label: str):
        stops = check_stop()
        if stops:
            raise StopSentinel(f"STOP sentinel: {stops}")
        s = total_spend(out_dir)
        if s >= budget_jpy:
            raise BudgetExceeded(f"{label}: 合算実費JPY{s:.3f} >= 上限JPY{budget_jpy}")
        if s >= soft_jpy and not any(e.get("soft") for e in events):
            events.append({"soft": True, "label": label, "spend": round(s, 3)})
    return guard


def load_text(spec: dict, with_title: bool = True) -> tuple:
    """Z現行 `canonical_article_text`(タイトル除去本文)を再現。with_title=Trueで`# 見出し`を前置
    (Family X入力と同形。shortlistは不変[Phase1実測]、Topic行にだけ題名が入る)。"""
    import er062_family_z_structure_01 as st
    raw = open(spec["path"], encoding="utf-8").read()
    title, body_raw = st.split_title_body(raw)
    heading_in_body = not title
    if not title:
        title = next((ln.lstrip("#").strip() for ln in raw.splitlines() if ln.strip().startswith("#")), "")
    body = "\n\n".join(st.clean_body_paragraphs(body_raw))
    if with_title and not heading_in_body:
        return "# " + title + chr(10) + chr(10) + body, title
    return body, title


def summarize_run(res: dict, kp_dir: str) -> dict:
    sel = res.get("selection") or {}
    canon = res.get("canonicalization") or {}
    red = res.get("redundancy_qa") or {}
    merged = ((canon.get("merged") or {}).get("items")) or []
    olog = res.get("outer_retry_log") or []
    ok_canon = canon.get("status") in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED")
    out = {
        "stage_status": res.get("status") or ("PASS" if ok_canon and red.get("status") != "REDUNDANCY_NG" else "NOT_PASSED"),
        "selection_status": sel.get("status"), "kp_backend_used": sel.get("kp_backend_used"),
        "fallback_reason_code": sel.get("kp_backend_fallback_reason_code"),
        "canonicalization_status": canon.get("status"), "redundancy_status": red.get("status"),
        "outer_attempts": len(olog),
        "outer_attempt_detail": [{k: a.get(k) for k in ("outer_attempt", "selection_status", "canonicalization_status",
                                                        "redundancy_status")} for a in olog],
        "selection_phrases_per_attempt": [a.get("selection_phrases") for a in olog],
        "final_kp": [{"rank": it.get("rank"), "key_phrase": it.get("key_phrase") or it.get("display_phrase"),
                      "role": it.get("key_phrase_role"), "source_span": it.get("source_span"),
                      "japanese_gloss": it.get("japanese_gloss") or it.get("ja_gloss")} for it in merged],
        "redundancy_retry_attempts": res.get("redundancy_retry_attempts"),
    }
    n_rule7 = 0
    for a in olog:
        for d in (a.get("canonicalization_attempts") or []):
            for ir in (d.get("item_reasons") or []):
                n_rule7 += sum("Rule7" in x for x in (ir.get("reasons") or []))
    out["rule7_item_violations"] = n_rule7
    out["canon_invalid_attempts"] = sum(1 for a in olog if a.get("canonicalization_status") not in
                                        (None, "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"))
    m2p = os.path.join(kp_dir, "key_phrases_db_hybrid", "m2_supply_report.json")
    if os.path.exists(m2p):
        m2r = json.load(open(m2p, encoding="utf-8"))
        meta = m2r.get("m2_meta") or {}
        out["m2"] = {"reserved": meta.get("reserved"), "n_candidates": meta.get("n_candidates"),
                     "m2_total_seconds": meta.get("m2_total_seconds"),
                     "selected_reserved": m2r.get("selected_reserved_slot_candidates"),
                     "selected_fragment_risk": m2r.get("selected_fragment_risk_candidates"),
                     "selected_rows": m2r.get("selected_rows")}
    return out


def run_one(text_id: str, spec: dict, arm: str, idx: int, out_dir: str, budget: float, soft: float, events: list,
            *, select_base=None, canon_fn=None, red_fn=None) -> dict:
    import er003_v1_n3_01_scaffold_generate as sc
    import er005_cost_logger as cl
    import er062_family_z_writer_01 as w62
    run_dir = os.path.join(out_dir, text_id, f"{arm}_run{idx}")
    kp_dir = os.path.join(run_dir, "key_phrases")
    os.makedirs(kp_dir, exist_ok=True)
    cl.init_logger(os.path.join(run_dir, "cost_log.jsonl"))
    guard = make_guard(out_dir, budget, soft, events)
    guard(f"{text_id}/{arm}/{idx} start")
    article, title = load_text(spec, with_title=True)
    cache: dict = {}
    base = select_base or sc.run_key_phrase_selection

    def select_fn(text, kdir, aid, source_level, process=None, diagnostic_note=None, **_):
        guard("selection")
        if arm == "dbh_m2p0":
            return base(text, kdir, aid, source_level, process=process, diagnostic_note=diagnostic_note,
                        kp_backend="db_hybrid", shortlist_cache=cache)
        return base(text, kdir, aid, source_level, process=process, diagnostic_note=diagnostic_note)

    def canon_w(text, items, kdir, aid, process=None, **kw):
        guard("canonicalization")
        return (canon_fn or sc.run_key_phrase_canonicalization)(text, items, kdir, aid, process=process, **kw)

    def red_w(text, items, kdir, aid, process=None, **kw):
        guard("redundancy_qa")
        return (red_fn or sc.run_key_phrase_redundancy_qa)(text, items, kdir, aid, process=process, **kw)

    t0 = time.time()
    err = None
    res = {}
    try:
        with cl.logging_context("FZKP_MIGRATION_TRIAL_01", "kp"):
            res = w62.run_kp_with_outer_retry(article, kp_dir, f"family_z_trial73_{text_id}_{arm}_run{idx}",
                                              spec["source_level"], process=spec["process"], select_fn=select_fn,
                                              canon_fn=canon_w, redundancy_fn=red_w)
    except (BudgetExceeded, StopSentinel):
        raise
    except Exception as e:  # 握りつぶさず記録し、当該runのみ終了(再試行しない)
        err = f"{type(e).__name__}: {e}"
    elapsed = round(time.time() - t0, 1)
    rows = read_cost_rows(os.path.join(run_dir, "cost_log.jsonl"))
    cost = round(sum(row_cost(r) for r in rows), 4)
    summ = summarize_run(res, kp_dir) if res else {"stage_status": "EXCEPTION"}
    summ.update({"text_id": text_id, "arm": arm, "run": idx, "title_passed": title, "error": err,
                 "elapsed_sec": elapsed, "cost_jpy": cost, "n_calls": len(rows),
                 "model_ids": sorted({r.get("model_id") for r in rows if r.get("model_id")}),
                 "llm_elapsed_sec": round(sum(r.get("elapsed_seconds") or 0 for r in rows), 1)})
    with open(os.path.join(run_dir, "run_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summ, f, ensure_ascii=False, indent=2)
    return summ


def aggregate(out_dir: str) -> dict:
    runs = [json.load(open(p, encoding="utf-8"))
            for p in sorted(glob.glob(os.path.join(out_dir, "*", "*_run*", "run_summary.json")))]
    by = {}
    for r in runs:
        by.setdefault((r["text_id"], r["arm"]), []).append(r)
    table = {}
    for (t, a), rs in by.items():
        sets = [[norm_phrase(it["key_phrase"]) for it in r.get("final_kp", [])] for r in rs]
        pairs = [jaccard(sets[i], sets[j]) for i in range(len(sets)) for j in range(i + 1, len(sets))]
        table[f"{t}/{a}"] = {
            "n": len(rs), "pass": sum(1 for r in rs if r["stage_status"] == "PASS"),
            "fallback": sum(1 for r in rs if r.get("kp_backend_used") == "strategy_l_fallback"),
            "cost_jpy": round(sum(r["cost_jpy"] for r in rs), 4), "elapsed_sec": [r["elapsed_sec"] for r in rs],
            "outer_attempts": [r.get("outer_attempts") for r in rs],
            "canon_invalid_attempts": sum(r.get("canon_invalid_attempts", 0) for r in rs),
            "rule7_item_violations": sum(r.get("rule7_item_violations", 0) for r in rs),
            "jaccard_pairs": [round(x, 3) for x in pairs],
            "jaccard_mean": round(sum(pairs) / len(pairs), 3) if pairs else None,
            "final_kp": [[it["key_phrase"] for it in r.get("final_kp", [])] for r in rs]}
    out = {"total_cost_jpy": round(sum(r["cost_jpy"] for r in runs), 4), "n_runs": len(runs), "table": table}
    with open(os.path.join(out_dir, "aggregate.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--budget-jpy", type=float, default=50.0)
    ap.add_argument("--soft-jpy", type=float, default=35.0)
    ap.add_argument("--no-telemetry", action="store_true", help="telemetry書込をno-op化(必須)")
    ap.add_argument("--text-id", default=None, help="1 processが担当するtext_id")
    ap.add_argument("--arm", default="dbh_m2p0", choices=["dbh_m2p0", "strategy_l"])
    ap.add_argument("--runs", type=int, default=None)
    ap.add_argument("--aggregate-only", action="store_true")
    ap.add_argument("--state-snapshot", default=None, help="state_guard snapshotの保存先")
    a = ap.parse_args()
    if a.state_snapshot:
        with open(a.state_snapshot, "w", encoding="utf-8") as f:
            json.dump(state_snapshot(), f, indent=1)
        print("snapshot saved", a.state_snapshot)
        return
    if a.aggregate_only:
        print(json.dumps(aggregate(a.out_dir), ensure_ascii=False, indent=1))
        return
    if not a.no_telemetry:
        sys.exit("--no-telemetry 必須(Production telemetryへ書かない)")
    stops = check_stop()
    if stops:
        sys.exit(f"STOP sentinel検出、新規API呼出なし: {stops}")
    plan = json.load(open(a.plan, encoding="utf-8"))
    import er003_v1_n3_01_scaffold_generate as sc
    import er005_cost_logger as cl
    sc._log_kp_backend_telemetry = lambda *x, **k: None  # no-op化(Production telemetry不変)
    os.makedirs(os.path.join(a.out_dir, a.text_id), exist_ok=True)
    cl.install(os.path.join(a.out_dir, a.text_id, "cost_log_init.jsonl"))
    spec = plan["texts"][a.text_id]
    n = a.runs if a.runs is not None else plan["n"]
    events: list = []
    for i in range(1, n + 1):
        try:
            r = run_one(a.text_id, spec, a.arm, i, a.out_dir, a.budget_jpy, a.soft_jpy, events)
        except (BudgetExceeded, StopSentinel) as e:
            print("STOP:", e)
            break
        print(json.dumps({k: r.get(k) for k in ("text_id", "arm", "run", "stage_status", "kp_backend_used",
                                                  "cost_jpy", "elapsed_sec", "outer_attempts", "error")},
                         ensure_ascii=False), flush=True)
    with open(os.path.join(a.out_dir, a.text_id, f"events_{a.arm}.json"), "w") as f:
        json.dump({"events": events}, f, indent=1)


if __name__ == "__main__":
    main()
