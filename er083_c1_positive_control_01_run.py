# -*- coding: utf-8 -*-
"""er083_c1_positive_control_01_run.py
C1陽性対照Trial(FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_02で準備、実走は委任_03でFable照合後)のB3実行CLI。
Trial専用(DEV path)。Production runner・producer・契約・Writer・B3 moduleは変更しない。既存 er083_b3_background_fact_trial_01_lib を
**import再利用**(Productionの run_storyline_b3_selection をそのまま呼ぶ。候補文C1は user入力末尾への追記のみ。baselineは追記なし=Production同一Prompt)。

  python er083_c1_positive_control_01_run.py --design docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/c1_posctrl_matrix_01.json \
      --out er083_output/c1_positive_control_01 --dry-run
  # 有料実走(委任_03、Fable照合後のみ): --budget-jpy N --paid-run-approved-by-fable [--cells PC1_hormuz:C1:1 ...](セル単位で並列プロセス起動可)

--dry-run: StubB3Client(API 0)。出力は <out>/_dryrun/<ledger_id>/<cond>/s<N>/ 。実runは <out>/<ledger_id>/<cond>/s<N>/ (cost_log.jsonlも同dir)。
env変数・隠しswitchなし。STOP/STOP_ALL が out にあれば開始しない。費用集計のTHEME_TAG=C1_POSCTRL_01。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import er083_b3_background_fact_trial_01_lib as lib

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(ROOT, "er083_output", "c1_positive_control_01")


def load_design(path: str) -> dict:
    d = json.loads(lib.read_text(path))
    for c in d["conditions"]:
        if c not in lib.CANDIDATE_NAMES:
            raise ValueError(f"unknown condition {c}")
    return d


def all_cells(design: dict) -> list:
    return [(L["id"], c, s) for L in design["ledgers"] for c in design["conditions"] for s in design["samples"]]


def parse_cells(specs, design: dict) -> list:
    if not specs:
        return all_cells(design)
    valid = set(all_cells(design))
    out = []
    for sp in specs:
        lid, cond, s = sp.split(":")
        cell = (lid, cond, int(s))
        if cell not in valid:
            raise ValueError(f"cell not in design: {sp}")
        out.append(cell)
    return out


def _abs(p: str) -> str:
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def ledger_by_id(design: dict, lid: str) -> dict:
    return [L for L in design["ledgers"] if L["id"] == lid][0]


def stub_evidence_for(L: dict) -> dict:
    """dry-run用: 既存Production選定の保存evidenceを土台にする(合成応答。実LLM結果ではない)。test Ledgerの追加Factは除外行を合成。"""
    if L.get("is_test_ledger"):
        ev_path = os.path.join(lib.PRODUCTION_MEY_RUN, "storyline_b3", "fact_selection_evidence.json")
    else:
        ev_path = os.path.join(os.path.dirname(os.path.dirname(_abs(L["ledger_path"]))), "storyline_b3", "fact_selection_evidence.json")
    ev = json.loads(lib.read_text(ev_path))
    ledger_ids = lib.b3.extract_fact_ids_from_ledger(lib.read_text(_abs(L["ledger_path"])))
    have = {ft["fact_id"] for ft in ev["fact_tests"]}
    for fid in ledger_ids:
        if fid not in have:
            ev["fact_tests"].append({"fact_id": fid, "test1_answer": "NO", "test2_answer": "NO", "test3_answer": "NO", "test4_answer": "NO",
                                     "decision": "excluded", "reason": "[stub合成] 追加Factの除外行(dry-run用)"})
    return ev


def run_cell(design: dict, cell: tuple, out_root: str, budget_jpy: float, dry_run: bool) -> dict:
    lid, cond, sample = cell
    L = ledger_by_id(design, lid)
    lib.THEME_TAG = design["theme_tag"]       # Trial専用のcost theme(C1_POSCTRL_01)。Production B3内部のlogging_context上書きは cost_summary が全行を数えるため無関係
    cand_dir = os.path.join(out_root, "_dryrun" if dry_run else "", lid, cond, f"s{sample}")
    cost_log = os.path.join(out_root, "cost_log_dryrun.jsonl") if dry_run else os.path.join(cand_dir, "cost_log.jsonl")
    ledger_text = lib.read_text(_abs(L["ledger_path"]))
    if dry_run:
        supp = (L["expected_core"][0] if (L["role"] == "positive" and L["expected_core"]) else None)
        client = lib.StubB3Client(stub_evidence_for(L), cost_log, synthetic_supplement_id=supp)
    else:
        lib.cl.install(cost_log)
        client = lib.vfl01.get_client()
    meta = lib.run_candidate(client, candidate=cond, topic=L["topic"], ledger_text=ledger_text, cand_dir=cand_dir, out_root=out_root,
                             baseline_ids=L["prior_baseline_selection"], budget_jpy=budget_jpy, cost_log=cost_log, dry_run=dry_run)
    meta_extra = {"ledger_id": lid, "role": L["role"], "sample": sample, "expected_core": L["expected_core"], "expected_ok": L["expected_ok"],
                  "is_test_ledger": L["is_test_ledger"], "theme_tag": design["theme_tag"]}
    meta.update(meta_extra)
    lib.write_json(os.path.join(cand_dir, "trial_meta.json"), meta)
    return meta


def plan(design: dict, cells: list) -> dict:
    est = design["est_b3_call_jpy"]
    n = len(cells)
    return {"n_b3_calls": n, "est_jpy_lib": round(n * est["lib_estimate"], 1), "est_jpy_prev_actual_mean": round(n * est["previous_trial_actual_mean"], 1),
            "writer_probe_max_chains": 4, "est_w1_jpy_max": round(4 * design["est_w1_chain_jpy"]["previous_trial_actual"][0], 1)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--cells", nargs="*", default=None, help="ledger_id:condition:sample (省略=全セル)")
    ap.add_argument("--budget-jpy", type=float, default=None, help="1セルあたりのbudget guard(実runで必須)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--paid-run-approved-by-fable", action="store_true", help="有料実走の明示確認(委任_03でFableが承認後のみ)")
    a = ap.parse_args(argv)

    out_root = os.path.abspath(a.out)
    for sentinel in ("STOP", "STOP_ALL"):
        if os.path.exists(os.path.join(out_root, sentinel)):
            print(f"[STOP] {sentinel} センチネルが {out_root} にあります。開始しません。")
            return 3
    design = load_design(a.design)
    cells = parse_cells(a.cells, design)
    if not a.dry_run:
        if not a.paid_run_approved_by_fable:
            print("[STOP] 有料実走には --paid-run-approved-by-fable が必要(委任_03、Fable照合後)。--dry-run を使ってください。")
            return 4
        if a.budget_jpy is None or a.budget_jpy < lib.EST_B3_CALL_JPY:
            print(f"[STOP] --budget-jpy は1call見込み {lib.EST_B3_CALL_JPY} 以上が必要")
            return 4
    budget = a.budget_jpy if a.budget_jpy is not None else 1e9
    results = []
    for cell in cells:
        try:
            meta = run_cell(design, cell, out_root, budget, a.dry_run)
            an = meta.get("analysis") or {}
            results.append({"cell": ":".join(map(str, cell)), "status": meta["status"], "selected": an.get("selected_fact_ids"),
                            "supplement": an.get("supplement_fact_ids"), "n_calls": len(meta["calls"]),
                            "rules_sha256": (meta.get("producer") or {}).get("rules_sha256")})
        except Exception as e:                      # dry-runで経路不備を可視化(実runでは中断して報告)
            results.append({"cell": ":".join(map(str, cell)), "status": "ERROR", "error": f"{type(e).__name__}: {e}"})
            if not a.dry_run:
                break
    summary = {"dry_run": a.dry_run, "plan": plan(design, cells), "results": results,
               "cost": lib.cost_summary_tree(out_root) if not a.dry_run else lib.cost_summary(os.path.join(out_root, "cost_log_dryrun.jsonl")),
               "production_prompt_shas": lib.prod_prompt_shas(), "note": "dry-runの応答は合成(StubB3Client)であり実LLMの挙動の根拠ではない" if a.dry_run else ""}
    lib.write_json(os.path.join(out_root, "_dryrun" if a.dry_run else "", "run_summary.json"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if all(r["status"] != "ERROR" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
