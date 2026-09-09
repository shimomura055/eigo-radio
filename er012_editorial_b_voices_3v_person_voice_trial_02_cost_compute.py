# ============================================================
# er012_editorial_b_voices_3v_person_voice_trial_02_cost_compute.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-02(補助)
# ============================================================
# Trial-02のraw_usage_log*.jsonl(writer stage + qa stage、cl.install()に
# よる全API call実測)を、既存の公式pricing snapshot(er005_output/
# cost_baseline_01/pricing_snapshot.json)で集計する。他Trial(例:
# er011_no18_cost_compute_01.py)と同一のprice()パターンを踏襲。
# 推測priceは使わない。web_search自体の課金はpricing_snapshotに含まれず、
# 4V/3V Trial-01と同様に本集計ではtoken usageのみを計上する(web_search
# call自体の課金は既存Trialでも計上していない、無変更のまま踏襲)。
from __future__ import annotations

import json

pricing = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def price(provider, model, meter):
    return next(p["price"] for p in pricing if p["provider"] == provider and p["model"] == model and p["meter"] == meter)


LUNA_IN = price("openai", "gpt-5.6-luna", "input_tokens")
LUNA_CACHED = price("openai", "gpt-5.6-luna", "cached_input_tokens")
LUNA_OUT = price("openai", "gpt-5.6-luna", "output_tokens")
USD_JPY = 155.0  # 4V Trial-02・3V Trial-01の¥93.63等、既存Trial実績と同水準のレートを採用


def call_cost_usd(r: dict) -> float:
    provider, model = r["provider"], r.get("model_id")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    if provider == "openai":
        billable_in = max(it - ct, 0)
        return (billable_in / 1e6) * LUNA_IN + (ct / 1e6) * LUNA_CACHED + (ot / 1e6) * LUNA_OUT
    raise ValueError(f"unpriced provider: {provider}")


OUT_DIR = "er012_output/editorial_b_voices_3v_person_voice_trial_02"
LOG_PATHS = {
    "writer": f"{OUT_DIR}/b1b_run01/raw_usage_log_3v_writer.jsonl",
    "qa": f"{OUT_DIR}/raw_usage_log_3v_qa_stage.jsonl",
}


def main():
    grand_total_usd = 0.0
    per_stage = {}
    for stage, path in LOG_PATHS.items():
        try:
            records = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        except FileNotFoundError:
            per_stage[stage] = {"path": path, "found": False, "call_count": 0, "cost_usd": 0.0, "cost_jpy": 0.0}
            continue
        for r in records:
            r["_cost_usd"] = call_cost_usd(r)
        total_usd = sum(r["_cost_usd"] for r in records)
        grand_total_usd += total_usd
        per_stage[stage] = {
            "path": path, "found": True, "call_count": len(records),
            "cost_usd": round(total_usd, 4), "cost_jpy": round(total_usd * USD_JPY, 2),
            "web_search_call_count_total": sum(r.get("web_search_call_count") or 0 for r in records),
        }
    result = {
        "usd_jpy_rate": USD_JPY,
        "per_stage": per_stage,
        "grand_total_usd": round(grand_total_usd, 4),
        "grand_total_jpy": round(grand_total_usd * USD_JPY, 2),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    with open(f"{OUT_DIR}/cost_compute_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
