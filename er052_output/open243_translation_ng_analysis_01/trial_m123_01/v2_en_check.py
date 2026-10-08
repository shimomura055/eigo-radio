# -*- coding: utf-8 -*-
"""V2(M2): 保存済み英語記事に対し run_deviation_check だけを旧/新(OPEN243_M2)で再実行し、混同行列を作る。

fixture:
  - 59 一意EN記事(ANALYSIS_01 _stats.py と同じ解決: MAP.json -> run_dir/b1b/article.md)
  - 53 事象(_events.json): 翻訳由来/増幅 26(陽性) + JA由来 27
  - ユーザー許容文(S0_USER_CHECK 確認1-3): STOPした世代の最終本文(rejected_advanced_attempt2.md)5記事(G02/G06/G09 必須、G07/G12 同型)
実行: v2_en_check.py --arm old|new [--scope all|events|tolerance] [--threads 4]
  --arm new は OPEN243_M2=1 を設定。結果は v2/<arm>/<key>.json に保存(promptと生応答含む)。既存ファイルはスキップ(再開可)。
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

BS = chr(92)
V2 = f"{C.TRIAL}/v2"
TOL = [  # (key, gen, run_dir, 許容とされた型)
    ("TOL_G02_users", "G02", "er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b2__all6__r2", "users"),
    ("TOL_G09_so", "G09", "er052_output/factlock_writer_trial_01/runs/meta/control/b4__factlock__r1", "so"),
    ("TOL_G06_oil", "G06", "er052_output/factlock_writer_trial_01/runs/hormuz/control/b1__factlock__r2", "oil prices"),
    ("TOLX_G07_users", "G07", "er052_output/factlock_writer_trial_01/runs/meta/control/b1__factlock__r1", "users(同型)"),
    ("TOLX_G12_users", "G12", "er052_output/factlock_writer_trial_01/sweep_01/runs/meta/control/b2__S3__r1", "users(同型)"),
]


def articles59():
    arts = {}
    for t in ["all6_writer_redesign_necessity_01", "factlock_writer_trial_01"]:
        m = json.load(open(f"er052_output/{t}/eval/_private/MAP.json", encoding="utf8"))["articles"]
        judged = {os.path.basename(f)[:-5] for f in glob.glob(f"er052_output/{t}/eval/judgments/*.json")}
        for k, v in m.items():
            if v["code"] not in judged:
                continue
            run = v["run_dir"].replace(BS, "/")
            ens = run + "/b1b/article.md"
            if not os.path.exists(ens):
                continue
            arts.setdefault(run, {"run": run, "en_path": ens})
    return arts


def build_fixtures():
    arts = articles59()
    events = json.load(open(f"{C.OUT}/_events.json", encoding="utf-8"))
    ev_by_run = {}
    for e in events:
        ev_by_run.setdefault(e["run_dir"].replace(BS, "/"), []).append(e)
    fx = []
    for run, a in sorted(arts.items()):
        key = "ART_" + run.replace("er052_output/", "").replace("/", "__")
        fx.append({"key": key, "kind": "article", "run": run, "en_path": a["en_path"],
                   "ledger_path": f"{run}/research_ledger/verified_fact_ledger.txt",
                   "ja_path": f"{run}/ja_writer/revision2.md",
                   "events": [{k: e[k] for k in ("event_id", "origin", "type", "severity", "sentence", "position")} for e in ev_by_run.get(run, [])]})
    for key, gen, run, typ in TOL:
        fx.append({"key": key, "kind": "tolerance", "gen": gen, "tolerated_type": typ, "run": run,
                   "en_path": f"{run}/b1b/audit/rejected_advanced_attempt2.md",
                   "ledger_path": f"{run}/research_ledger/verified_fact_ledger.txt",
                   "ja_path": f"{run}/ja_writer/revision2.md", "events": []})
    missing = [(f["key"], p) for f in fx for p in (f["en_path"], f["ledger_path"], f["ja_path"]) if not os.path.exists(p)]
    return fx, missing, set(ev_by_run) - set(arts)


def run_one(client, f, arm):
    out_path = f"{V2}/{arm}/{f['key']}.json"
    if os.path.exists(out_path):
        return "skip"
    en = open(f["en_path"], encoding="utf-8").read()
    led = open(f["ledger_path"], encoding="utf-8").read()
    ja = open(f["ja_path"], encoding="utf-8").read()
    r = C.checked_deviation(client, led, en, ja, f"v2.{arm}.{f['key']}")
    C.jdump(out_path, {"key": f["key"], "arm": arm, "model": r["model"], "usage": r["usage"], "cost_jpy": r["cost_jpy"],
                       "prompt": r["prompt"], "raw_text": r["raw_text"], "parsed": r["parsed"]})
    return "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["old", "new"], required=True)
    ap.add_argument("--scope", choices=["all", "events", "posevents", "tolerance", "sample_rest"], default="all")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    fx, missing, ev_runs_missing = build_fixtures()
    if args.list:
        print(len(fx), "fixtures; missing files:", missing, "event runs without article:", ev_runs_missing)
        print("with events:", sum(1 for f in fx if f["events"]))
        return
    if missing:
        raise SystemExit(f"missing files: {missing}")
    if args.arm == "new":
        os.environ["OPEN243_M2"] = "1"
    else:
        os.environ.pop("OPEN243_M2", None)
    sel = [f for f in fx if args.scope == "all" or (args.scope == "events" and f["events"]) or (args.scope == "posevents" and any(e["origin"] in ("translation", "amplified") for e in f["events"])) or
           (args.scope == "tolerance" and f["kind"] == "tolerance")]
    if args.scope == "sample_rest":  # 残り38記事のうち1つおき(19記事)。予算上限のため全件は再実行しない
        rest = [f for f in fx if f["kind"] == "article" and not any(e["origin"] in ("translation", "amplified") for e in f["events"])]
        sel = rest[::2]
    client = C.vfl01.get_client()
    with cf.ThreadPoolExecutor(max_workers=args.threads) as ex:
        futs = {ex.submit(run_one, client, f, args.arm): f["key"] for f in sel}
        for fu in cf.as_completed(futs):
            try:
                print(futs[fu], fu.result(), "spend", round(C.total_spend(), 3), flush=True)
            except Exception as e:  # noqa: BLE001
                print("ERROR", futs[fu], type(e).__name__, e, flush=True)
    print("TOTAL SPEND JPY", round(C.total_spend(), 3))


if __name__ == "__main__":
    main()
