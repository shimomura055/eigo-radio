# -*- coding: utf-8 -*-
"""er083_b3_background_fact_trial_01_writer_probe.py
下流テキスト検証用の最小wrapper(Trial専用)。Production W-1 JA Writer(`er053_family_x_factlock_ja_writer_01.run_w1_writer`)を
**そのまま**、候補の一時out-dir(er083_output配下)に対して呼ぶ。入力=その候補のannotated B3(契約検証V1-V10は課金前にProduction側で実行)、
出力=`<cand_dir>/ja_writer/revision2.md`。Production runner・run_mey_01配下には触れない。

  python er083_b3_background_fact_trial_01_writer_probe.py --cand-dir <dir> --out-root <dir> --budget-jpy N [--dry-run]

予算: W-1 chain(R0+R1+R2)見込み EST_W1_CHAIN_JPY(≒14.6)。呼出ごとのguardは budget_check コールバック(R0前/R1前/R2前…)で
「これまでの実費 + 1call見込み(chain/3) <= budget」を判定する。
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from types import SimpleNamespace

import er083_b3_background_fact_trial_01_lib as lib
import er053_family_x_factlock_ja_writer_01 as w1


class StubWriterClient:
    """W-1のR0/R1/R2呼出用stub(API 0)。タグ付きR0文を返し、R1/R2は入力本文を素通しする。合成であり実LLM出力ではない。"""

    def __init__(self, log_path: str):
        self.log, self.n = log_path, 0
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.n += 1
        user = kw["input"][-1]["content"]
        text = "合成テスト本文です。【事実1】に基づく一文。" if self.n == 1 else "合成の改稿本文です。"
        lib.append_jsonl(self.log, {"theme": w1.THEME_TAG, "stage": "dry_run_stub_w1", "provider": "openai",
                                    "model_id": kw["model"], "success": True, "usage_source": "SYNTHETIC_DRYRUN_STUB",
                                    "input_tokens": len(user) // 2, "output_tokens": 800, "dry_run_stub": True,
                                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()})
        return SimpleNamespace(output_text=text, model=kw["model"], id=f"stub_w1_{self.n}",
                               usage=SimpleNamespace(input_tokens=len(user) // 2, output_tokens=800))


def run_probe(cand_dir: str, out_root: str, budget_jpy: float, dry_run: bool, client=None, cost_log: str | None = None) -> dict:
    lib.assert_under_out_root(cand_dir, out_root)
    cost_log = cost_log or os.path.join(out_root, "cost_log_dryrun.jsonl" if dry_run else "cost_log.jsonl")
    guard = lib.BudgetGuard(cost_log, budget_jpy, lib.EST_W1_CHAIN_JPY / 3.0, dry_run)
    if client is None:
        if dry_run:
            client = StubWriterClient(cost_log)
        else:
            lib.cl.install(cost_log)
            client = lib.vfl01.get_client()
    calls = {"n": 0}

    def budget_check():
        calls["n"] += 1
        guard.check(f"w1_probe#{calls['n']}")

    res = w1.run_w1_writer(cand_dir, client=client, budget_check=budget_check)
    out = {"cand_dir": cand_dir, "ja_chars": len(res["ja_text"]), "title": res["title"], "revision2": res["paths"]["revision2"],
           "dry_run": dry_run, "cost": lib.cost_summary(cost_log)}
    lib.write_json(os.path.join(cand_dir, "writer_probe_summary.json"), out)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand-dir", required=True)
    ap.add_argument("--out-root", default=lib.OUT_ROOT)
    ap.add_argument("--budget-jpy", type=float, required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    for sentinel in ("STOP", "STOP_ALL"):
        if os.path.exists(os.path.join(os.path.abspath(a.out_root), sentinel)):
            print(f"[STOP] {sentinel} センチネルあり。開始しません。")
            return 3
    if not a.dry_run and a.budget_jpy < lib.EST_W1_CHAIN_JPY:
        print(f"[STOP] budget {a.budget_jpy} < W-1 chain見込み {lib.EST_W1_CHAIN_JPY}")
        return 4
    print(json.dumps(run_probe(a.cand_dir, a.out_root, a.budget_jpy, a.dry_run), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
