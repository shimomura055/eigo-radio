# ============================================================
# er012_personalized_news_b1_rebuild_01_writer.py
# 管理ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01
# ============================================================
# 目的: 新Ledger(er012_output/personalized_news_b1_rebuild_01/research/
# verified_fact_ledger.txt)を使い、正式Production経路
# (er012_b_family_production_runner_01.main_b1_2v()、write_new_theme stage)で
# B1(2V)を再生成する。呼び出し規約はrun_voices_2v_b1_v2.py(OPEN-151-02)と
# 同一(argv経由でrunner.main_b1_2v()を呼ぶ)。
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.abspath("er012_output/personalized_news_b1_rebuild_01"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import er005_cost_logger as cl
import er012_b_family_production_runner_01 as runner

BASE_DIR = "er012_output/personalized_news_b1_rebuild_01"
THEME_MODULE_NAME = "voices_theme_personalized_news_b1_rebuild_01"

PRICING_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0


def _load_pricing():
    with open(PRICING_PATH, encoding="utf-8") as f:
        return json.load(f)["prices"]


PRICING = _load_pricing()


def _price(provider, model, meter, tier="Standard"):
    return next(p["price"] for p in PRICING if p["provider"] == provider and p["model"] == model
                and p["meter"] == meter and p.get("tier", "Standard") == tier)


def _call_cost_usd(rec: dict) -> float:
    provider, model = rec.get("provider"), rec.get("model_id")
    if provider != "openai":
        return 0.0
    it, ot = rec.get("input_tokens") or 0, rec.get("output_tokens") or 0
    ct = rec.get("cached_input_tokens") or 0
    billable_in = max(it - ct, 0)
    in_price = _price("openai", model, "input_tokens")
    cached_price = _price("openai", model, "cached_input_tokens")
    out_price = _price("openai", model, "output_tokens")
    cost = (billable_in / 1e6) * in_price + (ct / 1e6) * cached_price + (ot / 1e6) * out_price
    web_search_calls = rec.get("web_search_call_count") or 0
    web_search_price = _price("openai", "N/A (tool, all models)", "web_search_call")
    cost += (web_search_calls / 1000) * web_search_price
    return cost


def _cost_from_log(log_path: str) -> tuple[float, dict]:
    if not os.path.exists(log_path):
        return 0.0, {}
    total_usd = 0.0
    input_tok = output_tok = cached_tok = 0
    calls = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("success") is False:
                continue
            total_usd += _call_cost_usd(rec)
            input_tok += rec.get("input_tokens") or 0
            output_tok += rec.get("output_tokens") or 0
            cached_tok += rec.get("cached_input_tokens") or 0
            calls += 1
    return total_usd * USD_JPY, {"calls": calls, "input_tokens": input_tok,
                                  "output_tokens": output_tok, "cached_input_tokens": cached_tok}


def _load_json_if_exists(path: str):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-tag", default="", help="出力サブディレクトリsuffix(再試行時の衝突回避用)")
    args = parser.parse_args()

    out_dir_subdir = BASE_DIR
    out_dir_base = f"{out_dir_subdir}/b1_2v_new_theme{args.run_tag}"
    os.makedirs(out_dir_subdir, exist_ok=True)
    log_path = f"{out_dir_subdir}/raw_usage_log_writer_driver{args.run_tag}.jsonl"
    cl.install(log_path)

    print(f"[PN-B1-REBUILD-01][writer] 正式Production経路(main_b1_2v()、write_new_theme stage)を"
          f"呼び出します。out_dir_base={out_dir_base}")

    old_argv = sys.argv
    sys.argv = ["er012_b_family_production_runner_01.py", "write_new_theme", "b1_2v",
                THEME_MODULE_NAME, out_dir_base]
    try:
        runner.main_b1_2v()
    finally:
        sys.argv = old_argv

    writer_log_path = f"{out_dir_base}/raw_usage_log_writer.jsonl"
    base_spend_jpy, base_tok = _cost_from_log(log_path)
    writer_spend_jpy, writer_tok = _cost_from_log(writer_log_path)
    new_spend_jpy = base_spend_jpy + writer_spend_jpy

    summary_json = _load_json_if_exists(f"{out_dir_base}/summary.json") or {}
    comment_contract_summary = _load_json_if_exists(f"{out_dir_base}/audit/new_theme_comment_contract_summary.json")

    cost_summary = {
        "new_spend_jpy_writer_comment_qa_gate": round(new_spend_jpy, 2),
        "driver_log": {"path": log_path, "cost_jpy": round(base_spend_jpy, 2), **base_tok},
        "writer_log_incl_comment_contract": {"path": writer_log_path, "cost_jpy": round(writer_spend_jpy, 2), **writer_tok},
    }
    with open(f"{out_dir_subdir}/cost_summary_writer{args.run_tag}.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary, f, ensure_ascii=False, indent=2)

    run_result = {
        "writer_status": summary_json.get("final_result", {}) if isinstance(summary_json, dict) else None,
        "total_attempts": summary_json.get("total_attempts") if isinstance(summary_json, dict) else None,
        "comment_contract_summary": comment_contract_summary,
        "cost_summary": cost_summary,
    }
    with open(f"{out_dir_subdir}/run_result_writer{args.run_tag}.json", "w", encoding="utf-8") as f:
        json.dump(run_result, f, ensure_ascii=False, indent=2, default=str)

    print(f"[PN-B1-REBUILD-01][writer] 完了。新規spend実測=¥{new_spend_jpy:.2f}")
    print(f"[PN-B1-REBUILD-01][writer] comment_contract_summary={comment_contract_summary}")


if __name__ == "__main__":
    main()
