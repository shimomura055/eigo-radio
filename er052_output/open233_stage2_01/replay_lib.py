# -*- coding: utf-8 -*-
"""STAGE2-01 委任_02 replay共通ライブラリ(offline replay: Stage1候補は保存済みを固定、Stage2以降のみ新構成で再判定)。
Trial専用。Production経路・既存runの証跡は変更しない(出力は er052_output/open233_stage2_01/ 配下のみ)。"""
import glob
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("PYTHONUTF8", "1")
import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402
import er052_open233_checker_action_policy_stage2_01 as cap2  # noqa: E402

OUT = ROOT / "er052_output" / "open233_stage2_01"
RATE = json.loads((OUT / "precheck" / "stage1_candidate_rate.json").read_text(encoding="utf-8"))
SPLIT_PATH = ROOT / "er052_output/open233_stage0_01/reclass/split.json"


def dev_items(kind="dev"):
    if kind == "heldout":
        d = json.loads((OUT / "replay_heldout" / "heldout_items.json").read_text(encoding="utf-8"))
        return [i for i in d["items"] if not str(i["status"]).startswith("excluded")]
    return [i for i in RATE["items"] if not str(i["status"]).startswith("excluded")]


def dev_runs(kind="dev"):
    return sorted({i["run"] for i in dev_items(kind)})


def load_run(run_dir):
    d = ROOT / run_dir
    files = glob.glob(str(d / "checker/runs/*.json"))
    assert len(files) == 1, (run_dir, files)
    run = json.loads(pathlib.Path(files[0]).read_text(encoding="utf-8"))
    ledger = (d / "research_ledger/verified_fact_ledger.txt").read_text(encoding="utf-8")
    c1 = run["cycles"][0]
    art = c1.get("en_text_before_rewrite")
    if not art:
        art = (d / "b1b/article.md").read_text(encoding="utf-8")
    return run, ledger, art


def cycle1_claims(run):
    """保存済みcycle1のStage1候補(stage1_llm由来)を固定入力へ。precheck floor等(Stage2を通らない)は除く。"""
    out = []
    for sr in run["cycles"][0]["stage2_results"]:
        if sr.get("stage2_route") == "precheck_floor_bypass" or sr.get("detected_by", "stage1_llm") != "stage1_llm":
            continue
        out.append({"claim_text": sr["claim_text"], "origin": sr.get("origin"), "related_fact_id": sr.get("related_fact_id"),
                    "dev": sr["dev"], "detected_by": "stage1_llm", "_saved": {
                        k: sr.get(k) for k in ("materiality", "llm_materiality", "floor_reason", "basis", "section_type")}
                    | {"so_confirmed": (sr.get("second_opinion") or {}).get("confirmed_downgrade"),
                       "so_split": (sr.get("second_opinion") or {}).get("split")}})
    return out


def setup(budget_jpy, run_budget_jpy=6.0):
    runner.apply_open233_approved_flow_switches()
    runner.TOTAL_BUDGET_JPY = run_budget_jpy
    runner.save_budget_state = lambda s: None  # 既存の予算状態ファイルを汚染しない(費用は本スクリプトのcost.jsonで管理)
    import er003_v1_en_direct_vfl_01_generate as vfl01
    return vfl01.get_client()


def new_state():
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def stage2_replay(client, run_dir, label):
    """1 runのcycle1を再判定(Stage2+2nd opinion)。戻り値: dict(results, cost_jpy, calls)。"""
    run, ledger, art = load_run(run_dir)
    claims = cycle1_claims(run)
    fixture = {"ledger_text": ledger, "article_text": art, "source_article_text": None}
    state, ce, call_log = new_state(), [0], []
    feed = [{k: v for k, v in c.items() if k != "_saved"} for c in claims]
    if not feed:
        return {"run": run_dir, "results": [], "cost_jpy": 0.0, "n_calls": 0, "claims": []}
    results = runner.run_stage2(client, state, ce, call_log, label, fixture, feed)
    if runner.STAGE2_SECOND_OPINION:
        results, so_log = runner.apply_stage2_second_opinion(client, state, ce, call_log, label, fixture, results,
                                                             run.get("instance_id"), 1)
    else:
        so_log = []
    out = []
    for c, r in zip(claims, results):
        out.append({"claim_text": c["claim_text"], "related_fact_id": c.get("related_fact_id"), "saved": c["_saved"],
                    "new": {k: r.get(k) for k in ("materiality", "llm_materiality", "floor_reason", "basis", "section_type", "rewrite_kind", "rewrite_hint",
                                                  "guard_target", "guard_types", "reader_belief")}
                    | {"so": {k: (r.get("second_opinion") or {}).get(k) for k in (
                        "confirmed_downgrade", "split", "first_belief", "second_belief", "belief_only")}}})
    return {"run": run_dir, "results": out, "cost_jpy": round(state["cumulative_jpy"], 4), "n_calls": state["cumulative_calls"],
            "call_log": [{k: v for k, v in c.items() if k in ("label", "stage2_variant", "cost_jpy", "error")} for c in call_log]}
