# -*- coding: utf-8 -*-
"""STAGE2-01 委任_02 測定(4)の準備: held-out項目(split.json heldout)をdevと同じ機械近似でrun・候補へ対応付ける(API無し)。
**測定(2)(3)の最終構成が確定するまで実行しない**(事前登録: held-outは手順(4)まで開かない)。1回のみ実行。
出力: replay_heldout/heldout_items.json(stage1_candidate_rate.jsonのitems形式)。"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
src = (HERE / "precheck" / "stage1_candidate_rate.py").read_text(encoding="utf-8")
head = src.split("eligible = [r for r in res if not r[\"status\"].startswith(\"excluded\")]")[0]
head = head.replace('dev = set(split["dev"])', 'dev = set(split["heldout"])').replace("assert len(items) == 100", "pass")
head = head.replace("ROOT = pathlib.Path(__file__).resolve().parents[3]", "ROOT = pathlib.Path(__file__).resolve().parents[2]")
head = head.replace("OUT = pathlib.Path(__file__).parent", "OUT = pathlib.Path(__file__).parent / 'replay_heldout'")
ns = {"__file__": str(HERE / "heldout_prep.py"), "__name__": "heldout_prep_exec"}
exec(compile(head, "heldout_prep_exec", "exec"), ns)
res = ns["res"]
(HERE / "replay_heldout").mkdir(exist_ok=True)
(HERE / "replay_heldout" / "heldout_items.json").write_text(json.dumps({"n_items": len(res), "excluded": dict(ns["excluded"]), "items": res},
                                                                       ensure_ascii=False, indent=1), encoding="utf-8")
print("n_items", len(res), "excluded", dict(ns["excluded"]))
print("eligible", sum(1 for r in res if not r["status"].startswith("excluded")), "runs",
      len({r["run"] for r in res if not r["status"].startswith("excluded")}))
