# ============================================================
# er011_output/discovery_s2_production_runtime_evidence_02/run_happy_path_a2.py
# 管理ID: FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01
# ============================================================
# 目的: Production正式関数`er003_discovery_focus_staged_production_01.
# run_one_pattern_staged_discovery_focus()`を、通常Verified Fact Ledger
# (`er011_output/discovery_generalization_wake_before_alarm_trial_12/
# research/`、read-only再利用、無改変)でA2レベル1本、実APIで正常完走させる
# ためだけの薄いdriver。Production関数のmonkeypatch・再実装は一切なし
# (importしてそのまま1回呼ぶだけ)。費用集計ロジックは`er011_discovery_
# generalization_wake_before_alarm_trial_12_run.py`のread-only転記
# (無変更)。
#
# 費用guard: 実行中、API call 1回ごとにer005_cost_logger.record()を
# ラップして累積JPYを再計算し、単独上限(BUDGET_JPY_CAP=60円)を超えたら
# その場でRuntimeErrorを送出して停止する(Production関数自体のロジックは
# 変更しない。record()という計測フックのみを外側から包む安全装置)。
#
# 実行方法: .venv/Scripts/python.exe er011_output/discovery_s2_production_
# runtime_evidence_02/run_happy_path_a2.py
from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI

import er003_discovery_focus_staged_production_01 as s2prod
import er005_cost_logger as cl

THEME_ID = "discovery_s2_production_runtime_evidence_02"
OUT_DIR = f"er011_output/{THEME_ID}"
RAW_LEDGER_DIR = "er011_output/discovery_generalization_wake_before_alarm_trial_12/research"
LEDGER_PATH = f"{RAW_LEDGER_DIR}/verified_fact_ledger.txt"
TOPIC_PATH = f"{RAW_LEDGER_DIR}/writer_topic.json"
VFL_PATH = f"{RAW_LEDGER_DIR}/stage_b3_vfl.json"
BUDGET_JPY_CAP = 60.0
USD_JPY = 160.0

_PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def _price(provider, model, meter, tier="Standard"):
    for p in _PRICING:
        if p["provider"] == provider and p["model"] == model and p["meter"] == meter and p.get("tier", "Standard") == tier:
            return p["price"]
    raise KeyError((provider, model, meter, tier))


def _call_cost_usd(r: dict) -> tuple:
    provider = r.get("provider")
    model = r.get("model_id") or r.get("model")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    try:
        if provider == "openai":
            billable_in = max(it - ct, 0)
            cost = (billable_in / 1e6) * _price("openai", model, "input_tokens") \
                + (ct / 1e6) * _price("openai", model, "cached_input_tokens") \
                + (ot / 1e6) * _price("openai", model, "output_tokens")
            wsc = r.get("web_search_call_count") or 0
            cost += (wsc / 1000) * _price("openai", "N/A (tool, all models)", "web_search_call")
            return cost, False
        return 0.0, True
    except KeyError:
        return 0.0, True


def _sum_log_jpy(log_path: str) -> dict:
    if not os.path.exists(log_path):
        return {"total_jpy": 0.0, "by_provider_jpy": {}, "unpriced_records": 0, "total_records": 0}
    total_usd, by_provider, unpriced, n = 0.0, {}, 0, 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            cost, up = _call_cost_usd(rec)
            total_usd += cost
            by_provider[rec.get("provider")] = by_provider.get(rec.get("provider"), 0.0) + cost
            unpriced += int(up)
            n += 1
    return {
        "total_jpy": round(total_usd * USD_JPY, 2),
        "by_provider_jpy": {k: round(v * USD_JPY, 2) for k, v in by_provider.items()},
        "unpriced_records": unpriced, "total_records": n,
    }


RAW_LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"
_original_record = cl.record


def _record_with_budget_guard(entry: dict) -> None:
    _original_record(entry)
    summary = _sum_log_jpy(RAW_LOG_PATH)
    if summary["total_jpy"] > BUDGET_JPY_CAP:
        raise RuntimeError(
            f"費用上限超過(実測{summary['total_jpy']}円 > 単独上限{BUDGET_JPY_CAP}円)。STOP。"
            f"(driver側budget guard、Production関数のロジックは無変更)")


def main() -> None:
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.init_logger(RAW_LOG_PATH)
    cl.install(RAW_LOG_PATH)
    cl.record = _record_with_budget_guard  # driver側の安全装置(budget guard)のみ。record()の呼び出し箇所[er005_cost_logger.py内]はモジュールグローバル参照のため、この差し替えで全record呼び出しに適用される。

    with open(LEDGER_PATH, encoding="utf-8") as f:
        verified_ledger_text = f.read()
    with open(TOPIC_PATH, encoding="utf-8") as f:
        topic_ja = json.load(f)["topic_ja"]

    client = OpenAI()

    result = s2prod.run_one_pattern_staged_discovery_focus(
        client=client,
        level="a2",
        topic_ja=topic_ja,
        verified_ledger_text=verified_ledger_text,
        out_dir=OUT_DIR,
        theme_tag=THEME_ID,
        vfl_path=VFL_PATH,
    )

    article_text = result.pop("article_text", None)
    if article_text:
        with open(f"{OUT_DIR}/reader_facing_article.txt", "w", encoding="utf-8") as f:
            f.write(article_text)

    with open(f"{OUT_DIR}/e2e_run_summary_a2.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    cost_summary = _sum_log_jpy(RAW_LOG_PATH)
    with open(f"{OUT_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary, f, ensure_ascii=False, indent=2)

    print(f"[{THEME_ID}] status={result.get('status')} cost_jpy={cost_summary['total_jpy']}")


if __name__ == "__main__":
    main()
