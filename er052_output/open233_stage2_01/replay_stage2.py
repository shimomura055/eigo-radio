# -*- coding: utf-8 -*-
"""STAGE2-01 委任_02 replayドライバ(Trial専用、有料API)。使い方:
  python er052_output/open233_stage2_01/replay_stage2.py --stage dev --tag v1 --belief 1 --budget-jpy 180 --max-workers 4
stage: w1w2 / dev / stability / a5 / rewrite / heldout。単層ThreadPool(最大4)。費用は cost.json に追記(累計>=--budget-jpyで残りをskip)。"""
import argparse
import concurrent.futures as cf
import json
import os
import pathlib
import random
import threading
import time

import replay_lib as L

runner, cap2, OUT = L.runner, L.cap2, L.OUT
COST = OUT / "cost.json"
lock = threading.Lock()


def cost_total():
    if not COST.exists():
        return 0.0
    return round(sum(e["cost_jpy"] for e in json.loads(COST.read_text(encoding="utf-8"))["entries"]), 4)


def add_cost(stage, tag, name, cost, n_calls):
    with lock:
        d = json.loads(COST.read_text(encoding="utf-8")) if COST.exists() else {"entries": []}
        d["entries"].append({"stage": stage, "tag": tag, "name": name, "cost_jpy": round(cost, 4), "n_calls": n_calls,
                             "t": time.strftime("%Y-%m-%d %H:%M:%S")})
        d["total_jpy"] = round(sum(e["cost_jpy"] for e in d["entries"]), 4)
        COST.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def set_env(a):
    os.environ[cap2.SW_READER_BELIEF] = "1" if a.belief else "0"
    os.environ[cap2.SW_STRUCT_RULES] = "1" if a.struct else "0"
    os.environ["OPEN233_FIX_W1_TITLE_MARKUP"] = "1" if a.struct else "0"
    os.environ["OPEN233_FIX_W2_STRUCTURAL_RECHECK"] = "1" if a.struct else "0"
    os.environ[cap2.SW_SAVE_R3] = "1"
    os.environ[cap2.RUBRIC_VERSION_ENV] = a.rubric


def slug(run_dir):
    return run_dir.replace("er052_output/", "").replace("/runs/", "__").replace("/", "_")


def do_dev(a, client, runs, outdir):
    outdir.mkdir(parents=True, exist_ok=True)

    def work(run_dir):
        f = outdir / (slug(run_dir) + ".json")
        if f.exists():
            return json.loads(f.read_text(encoding="utf-8"))
        if cost_total() >= a.budget_jpy:
            return {"run": run_dir, "skipped": "budget"}
        try:
            r = L.stage2_replay(client, run_dir, f"rp_{a.tag}_{slug(run_dir)[:40]}")
        except Exception as e:  # noqa: BLE001
            return {"run": run_dir, "error": f"{type(e).__name__}: {e}"}
        f.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        add_cost(a.stage, a.tag, run_dir, r["cost_jpy"], r["n_calls"])
        return r
    with cf.ThreadPoolExecutor(max_workers=a.max_workers) as ex:
        return list(ex.map(work, runs))



def do_w1w2(a, client):
    """(1) W1/W2回帰replay: qvqc rep2 cycle1のタイトル書換え(保存済み)を、W1/W2 ON(構造要素規則はOFF=バグ修正のみ)で再生し、
    ladderの決定論部分(LLMはAPI無しの固定応答)→Recheckを実API 1回。タイトルがT単位としてRecheck対象になることを確認する。"""
    import unittest.mock as mock
    os.environ[cap2.SW_STRUCT_RULES] = "0"
    os.environ["OPEN233_FIX_W1_TITLE_MARKUP"] = "1"
    os.environ["OPEN233_FIX_W2_STRUCTURAL_RECHECK"] = "1"
    fxd = L.ROOT / "er052_output/open233_stage2_01/precheck/fixtures"
    before = (fxd / "qvqc_rep2_before.md").read_text(encoding="utf-8")
    att = json.loads((fxd / "qvqc_rep2_cycle1_title_attempt.json").read_text(encoding="utf-8"))
    rd = "er052_output/open233_control_checker_polysemy_trial_01/runs/meta/nb/rep2"
    run, ledger, _ = L.load_run(rd)
    c1 = run["cycles"][0]
    fixture = {"ledger_text": ledger, "article_text": before}
    claim_rec = {"claim_text": att["targets"][0], "rewrite_kind": "delete", "materiality": "BLOCKING", "basis": "ledger_claim",
                 "rewrite_hint": "h", "dev": {"issue": "x"}}
    state, ce, call_log = L.new_state(), [0], []
    with mock.patch.object(runner, "STRUCTURAL_ELEMENT_REWRITE", True), \
            mock.patch.object(runner, "simple_llm_call",
                              side_effect=lambda *x, **k: json.dumps({"revised_ranges": [att["revised"][0]]})):
        res = runner.rewrite_ranges_ladder(None, state, ce, call_log, "w1w2", fixture, "article_text", claim_rec)
    pair = res["handoff"].get("structural_pair")
    after = res["updated_text"]
    prior = [{"claim_in_article": r["claim_text"]} for r in c1["stage2_results"] if r.get("materiality") == "BLOCKING"]
    rc = runner.run_recheck_coverage(client, state, ce, call_log, "w1w2_recheck", {"ledger_text": ledger, "article_text": after},
                                     after, prior, before, structural_pairs=[{"before": pair["before"], "after": pair["after"]}])
    audit = rc.get("recheck_coverage_audit") or {}
    saved = c1.get("recheck_coverage") or {}
    out = {"title_after": runner._en_title_line(after), "w1_title_markup_restored": res["handoff"].get("w1_title_markup_restored"),
           "structural_pair": pair, "recheck_scope_ids_new": audit.get("scope_ids"), "recheck_changed_ids_new": audit.get("changed_ids"),
           "recheck_scope_ids_saved_off": saved.get("scope_ids"), "recheck_changed_ids_saved_off": saved.get("changed_ids"),
           "T_in_scope_new": "T" in (audit.get("scope_ids") or []), "T_in_scope_saved": "T" in (saved.get("scope_ids") or []),
           "overall_status": rc.get("overall_status"), "n_calls": audit.get("n_calls"), "cost_jpy": round(state["cumulative_jpy"], 4)}
    (OUT / "replay_dev").mkdir(exist_ok=True, parents=True)
    (OUT / "replay_dev" / "w1w2_regression.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    add_cost("w1w2", "w1w2", rd, state["cumulative_jpy"], state["cumulative_calls"])
    print(json.dumps(out, ensure_ascii=False, indent=1))


def do_stability(a, client):
    """測定: belief_vs_ledgerの3回一致率(同一claim x 3回)。devのguard_target候補から無作為10件(seed固定)、run単位でbatch化して3回再判定
    (2nd opinionは使わない=1回目callのbelief_vs_ledgerのみ)。"""
    src = OUT / "replay_dev" / a.tag
    pool = []
    for f in sorted(src.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for x in d.get("results", []):
            if x["new"].get("guard_target") and (x["new"].get("reader_belief") or {}).get("belief_vs_ledger"):
                pool.append((d["run"], x["claim_text"]))
    rng = random.Random(20261007)
    pick = rng.sample(pool, min(10, len(pool)))
    by_run = {}
    for run, ct in pick:
        by_run.setdefault(run, []).append(ct)
    res = {}  # (run, claim) -> [beliefs]
    lock2 = threading.Lock()

    def work(job):
        run_dir, rep = job
        if cost_total() >= a.budget_jpy:
            return
        run, ledger, art = L.load_run(run_dir)
        claims = [c for c in L.cycle1_claims(run) if c["claim_text"] in by_run[run_dir]]
        feed = [{k: v for k, v in c.items() if k != "_saved"} for c in claims]
        state, ce, cl = L.new_state(), [0], []
        out = runner.run_stage2(client, state, ce, cl, f"stab{rep}_{slug(run_dir)[:30]}",
                                {"ledger_text": ledger, "article_text": art, "source_article_text": None}, feed)
        add_cost("stability", a.tag, f"{run_dir}#{rep}", state["cumulative_jpy"], state["cumulative_calls"])
        with lock2:
            for c, r in zip(claims, out):
                res.setdefault((run_dir, c["claim_text"]), []).append(
                    {"belief": (r.get("reader_belief") or {}).get("belief_vs_ledger"), "materiality": r["materiality"],
                     "llm_materiality": r.get("llm_materiality"), "reasked": (r.get("reader_belief") or {}).get("reasked")})
    jobs = [(rd, rep) for rd in by_run for rep in (1, 2, 3)]
    with cf.ThreadPoolExecutor(max_workers=a.max_workers) as ex:
        list(ex.map(work, jobs))
    rows = []
    for (run, ct), v in res.items():
        bl = [x["belief"] for x in v]
        rows.append({"run": run, "claim": ct[:120], "beliefs": bl, "materiality": [x["materiality"] for x in v],
                     "agree3": len(bl) == 3 and len(set(bl)) == 1, "material_agree3": len({x["materiality"] for x in v}) == 1})
    n = len(rows)
    out = {"tag": a.tag, "n_pool": len(pool), "n_picked": len(pick), "n_claims": n, "n_agree3": sum(r["agree3"] for r in rows),
           "agree_rate": round(sum(r["agree3"] for r in rows) / n, 3) if n else None,
           "materiality_agree_rate": round(sum(r["material_agree3"] for r in rows) / n, 3) if n else None,
           "pass_ge_0.8": bool(n) and sum(r["agree3"] for r in rows) / n >= 0.8, "rows": rows}
    (OUT / "eval").mkdir(exist_ok=True, parents=True)
    (OUT / "eval" / f"stability_{a.tag}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, ensure_ascii=False, indent=1))


def do_a5(a, client):
    """ライン3(A5-0): Safety-criticalのA5群(A5-0=ロールバック方向の誤読BLOCKING、A5-1)を現行/新構成でn=3判定。"""
    import er052_open233_element_trial_safety_control_02 as sc02
    g = {x["group_id"]: x for x in sc02.safety_critical_groups()}["A5"]
    fx = g["fixture"]
    claims = [{"claim_text": c["claim_text"], "origin": c.get("origin"), "related_fact_id": c.get("related_fact_id"),
               "dev": {"severity": "MAJOR", "related_fact_id": c.get("related_fact_id"), "unsupported_new_claim": bool(c.get("unsupported_new_claim"))},
               "detected_by": "stage1_llm"} for c in g["claims"]]
    fixture = {"ledger_text": fx["ledger_text"], "article_text": fx["article_text"], "source_article_text": fx.get("source_article_text")}
    rows = []

    def work(rep):
        state, ce, cl = L.new_state(), [0], []
        out = runner.run_stage2(client, state, ce, cl, f"a5_{a.tag}_{rep}", fixture, [dict(c) for c in claims])
        if runner.STAGE2_SECOND_OPINION:
            out, _ = runner.apply_stage2_second_opinion(client, state, ce, cl, f"a5_{a.tag}_{rep}", fixture, out, "A5", 1)
        add_cost("a5", a.tag, f"rep{rep}", state["cumulative_jpy"], state["cumulative_calls"])
        return [{"rep": rep, "sub_id": g["claims"][i]["sub_id"], "correct": g["claims"][i]["correct_label"], "materiality": r["materiality"],
                 "llm_materiality": r.get("llm_materiality"), "floor_reason": r.get("floor_reason"),
                 "belief": (r.get("reader_belief") or {}).get("belief_vs_ledger"), "guard_target": r.get("guard_target")}
                for i, r in enumerate(out)]
    with cf.ThreadPoolExecutor(max_workers=a.max_workers) as ex:
        for part in ex.map(work, [1, 2, 3]):
            rows += part
    a50 = [r for r in rows if r["sub_id"] == "A5-0"]
    out = {"tag": a.tag, "A5-0_blocking": sum(1 for r in a50 if r["materiality"] == "BLOCKING"), "A5-0_n": len(a50),
           "A5-1_blocking": sum(1 for r in rows if r["sub_id"] == "A5-1" and r["materiality"] == "BLOCKING"), "rows": rows}
    (OUT / "eval").mkdir(exist_ok=True, parents=True)
    (OUT / "eval" / f"a5_{a.tag}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--tag", default="v1")
    ap.add_argument("--belief", type=int, default=1)
    ap.add_argument("--struct", type=int, default=1)
    ap.add_argument("--rubric", default="v1")
    ap.add_argument("--budget-jpy", type=float, default=180.0)
    ap.add_argument("--max-workers", type=int, default=4)
    ap.add_argument("--runs", default="")
    a = ap.parse_args()
    set_env(a)
    client = L.setup(a.budget_jpy)
    print("cost_before", cost_total())
    if a.stage in ("dev", "heldout"):
        runs = L.dev_runs("heldout" if a.stage == "heldout" else "dev") if not a.runs else a.runs.split(",")
        res = do_dev(a, client, runs, OUT / ("replay_heldout" if a.stage == "heldout" else "replay_dev") / a.tag)
        print(json.dumps([{k: r.get(k) for k in ("run", "cost_jpy", "n_calls", "error", "skipped")} for r in res], ensure_ascii=False))
    if a.stage == "w1w2":
        do_w1w2(a, client)
    if a.stage == "stability":
        do_stability(a, client)
    if a.stage == "a5":
        do_a5(a, client)
    print("cost_after", cost_total())


if __name__ == "__main__":
    main()
