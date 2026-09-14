# ============================================================
# er014_output/four_type_observation_01/voices/run_voices_2v_b1_v2.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-
# WIRING-02(OPEN-151完成)
# ============================================================
# 目的: 5-1(Comment Contract配線)+5-2(Fact Safetyゲート2V/3V一般化)適用後の
# clean 2V runtime evidence取得。run_voices_2v_b1.py(-01タスク版、Research→
# Writerのみ)とは異なり、実際の2V正式Production経路そのもの
# (er012_b_family_production_runner_01.main_b1_2v()、write_new_theme stage)を
# argv経由で呼び出す(Comment Contract配線・Fact Safetyゲート一般化が実際の
# Production入口から効くことのevidenceとするため)。
#
# --reuse-ledger: 既存research/verified_fact_ledger.txt(-01タスクで取得済み、
#   VERIFIED 18件)をそのまま再利用し、Research/Verificationを再実行しない
#   (Research再実行禁止、Ledger再利用)。
# --out-subdir: 出力先サブディレクトリ名(既定"run2_clean")。
# --budget-jpy: 本runの新規スペンド(Writer/Comment/QA/Gate/retry)の予算上限
#   (既定150.0)。write_new_theme stage自体は既存Production側で途中budget
#   checkpointを持たないため、事後(実行後)にログから実測しPASS/OVER判定する
#   (新しいGate・新しい強制停止機構は追加しない、報告のみ)。
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import er005_cost_logger as cl
import er012_b_family_production_runner_01 as runner

BASE_DIR = "er014_output/four_type_observation_01/voices"
LEDGER_PATH = f"{BASE_DIR}/research/verified_fact_ledger.txt"
THEME_MODULE_NAME = "voices_theme_personalized_news_01"

PRICING_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0

# -01タスクのresearch(Research+Verification)実測費用(run1_partial/へ退避済み
# raw_usage_log.jsonlの実測値、既存記録の転記のみ・再計算しない)。
RESEARCH_LEDGER_COST_JPY = 46.98


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse-ledger", action="store_true",
                         help="既存research/verified_fact_ledger.txtを再利用し、Researchを再実行しない")
    parser.add_argument("--out-subdir", default="run2_clean")
    parser.add_argument("--budget-jpy", type=float, default=150.0)
    args = parser.parse_args()

    if not args.reuse_ledger:
        raise SystemExit("本v2driverは--reuse-ledger必須です(Research再実行はrun_voices_2v_b1.pyのphase1_research()を"
                          "別途手動実行してください、本タスクではLedger再利用のみサポート)。")
    if not os.path.exists(LEDGER_PATH):
        raise SystemExit(f"Ledgerが見つかりません: {LEDGER_PATH}")

    out_dir_subdir = f"{BASE_DIR}/{args.out_subdir}"
    out_dir_base = f"{out_dir_subdir}/b1_2v_new_theme"
    os.makedirs(out_dir_subdir, exist_ok=True)
    log_path = f"{out_dir_subdir}/raw_usage_log.jsonl"
    cl.install(log_path)

    print(f"[run_voices_2v_b1_v2] 正式Production経路(er012_b_family_production_runner_01.main_b1_2v()、"
          f"write_new_theme stage)を呼び出します。out_dir_base={out_dir_base} budget_jpy={args.budget_jpy}")

    old_argv = sys.argv
    sys.argv = ["er012_b_family_production_runner_01.py", "write_new_theme", "b1_2v",
                THEME_MODULE_NAME, out_dir_base]
    try:
        runner.main_b1_2v()
    finally:
        sys.argv = old_argv

    # 既知の表示バグ(-01タスクREPORT 6節と同一原因): run_writer_stage_generic()
    # 内部で`cl.install(f"{out_dir_base}/raw_usage_log_writer.jsonl")`が
    # ログ出力先を切り替えるため(既存3V/2V共通の既存実装、本タスクでの変更
    # ではない)、driver側で最初にinstallしたlog_pathには記録が残らない。
    # 実際の記録先(Writer+Comment Contract分含む、Comment生成はWriter完了後の
    # 呼び出しだがcl.install()の切替が持続するため同一ファイルに記録される)を
    # 明示的に参照して実測する。
    writer_log_path = f"{out_dir_base}/raw_usage_log_writer.jsonl"
    base_spend_jpy, base_tok = _cost_from_log(log_path)
    writer_spend_jpy, writer_tok = _cost_from_log(writer_log_path)
    new_spend_jpy = base_spend_jpy + writer_spend_jpy
    token_summary = {
        "driver_log": {"path": log_path, "cost_jpy": round(base_spend_jpy, 2), **base_tok},
        "writer_log_incl_comment_contract": {"path": writer_log_path, "cost_jpy": round(writer_spend_jpy, 2), **writer_tok},
    }
    total_jpy = RESEARCH_LEDGER_COST_JPY + new_spend_jpy
    budget_status = "PASS" if new_spend_jpy <= args.budget_jpy else "OVER_BUDGET_REPORTED_ONLY"

    summary_json = _load_json_if_exists(f"{out_dir_base}/summary.json") or {}
    comment_contract_summary = _load_json_if_exists(f"{out_dir_base}/audit/new_theme_comment_contract_summary.json")
    support_texts = _load_json_if_exists(f"{out_dir_base}/b1_support_texts.json")
    support_ledger_deviation = _load_json_if_exists(f"{out_dir_base}/audit/support_ledger_deviation.json")

    cost_summary = {
        "research_ledger_cost_jpy_reused": RESEARCH_LEDGER_COST_JPY,
        "new_spend_jpy_writer_comment_qa_gate": round(new_spend_jpy, 2),
        "new_spend_token_summary": token_summary,
        "voices_production_set_total_cost_jpy": round(total_jpy, 2),
        "budget_jpy_new_spend_only": args.budget_jpy,
        "budget_status": budget_status,
    }
    with open(f"{out_dir_subdir}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir_subdir}/production_set_cost.json", "w", encoding="utf-8") as f:
        json.dump({
            "note": ("Voices Production 1生成セット総原価= "
                     "Research/Ledger(既存、run1_partial流用・再計算なし) + "
                     "Writer/Comment/QA/Gate/retry(本run実測)"),
            **cost_summary,
        }, f, ensure_ascii=False, indent=2)

    run_result = {
        "writer_status": summary_json.get("final_result", {}) if isinstance(summary_json, dict) else None,
        "total_attempts": summary_json.get("total_attempts") if isinstance(summary_json, dict) else None,
        "comment_contract_summary": comment_contract_summary,
        "support_texts_present": bool(support_texts),
        "support_ledger_deviation_overall_status": (support_ledger_deviation or {}).get("overall_status"),
        "cost_summary": cost_summary,
    }
    with open(f"{out_dir_subdir}/run_result.json", "w", encoding="utf-8") as f:
        json.dump(run_result, f, ensure_ascii=False, indent=2, default=str)

    print(f"[run_voices_2v_b1_v2] 完了。新規spend実測=¥{new_spend_jpy:.2f}(budget_status={budget_status})、"
          f"Voices Production 1生成セット総原価(累積)=¥{total_jpy:.2f}")
    print(f"[run_voices_2v_b1_v2] comment_contract_summary={comment_contract_summary}")


if __name__ == "__main__":
    main()
