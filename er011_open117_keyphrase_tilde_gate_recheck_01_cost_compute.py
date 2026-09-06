# ============================================================
# er011_open117_keyphrase_tilde_gate_recheck_01_cost_compute.py
# OPEN-117-KEYPHRASE-TILDE-GATE-RECHECK-01の実費計算
# ============================================================
# er011_specfix_cost_compute_01.call_cost_usd()はgemini_batch+
# gemini-3.1-flash-tts-preview(Batch単価)のモデルpriceテーブルが
# 未整備のため、既存ER-011他Trialスクリプト(例:
# er011_no18_wiring08_cost_compute.py)と同じ補完パターンをここでも
# 踏襲する(共有moduleは変更しない)。
from __future__ import annotations

import json

import er011_specfix_cost_compute_01 as cc

GEMINI_FLASH_BATCH_IN = cc.price_tiered("gemini", "gemini-3.1-flash-tts-preview", "input_tokens", "Batch")
GEMINI_FLASH_BATCH_OUT = cc.price_tiered("gemini", "gemini-3.1-flash-tts-preview", "output_tokens", "Batch")

LOG_PATH = "er011_output/open117_keyphrase_tilde_gate_recheck_01/raw_usage_log_open117.jsonl"
OUT_PATH = "er011_output/open117_keyphrase_tilde_gate_recheck_01/cost_summary_open117.json"


def call_cost_usd(r: dict) -> float:
    if r.get("provider") == "gemini_batch" and r.get("model_id") == "gemini-3.1-flash-tts-preview":
        it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
        return (it / 1e6) * GEMINI_FLASH_BATCH_IN + (ot / 1e6) * GEMINI_FLASH_BATCH_OUT
    return cc.call_cost_usd(r)


def main():
    records = []
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    total_usd = 0.0
    by_api: dict[tuple, float] = {}
    for r in records:
        if not r.get("success", True):
            continue
        cost = call_cost_usd(r)
        total_usd += cost
        key = (r.get("provider"), r.get("api"))
        by_api[key] = by_api.get(key, 0.0) + cost

    result = {
        "total_calls": len(records),
        "total_usd": round(total_usd, 5),
        "total_jpy": round(total_usd * cc.USD_JPY, 2),
        "by_provider_api_usd": {f"{k[0]}::{k[1]}": round(v, 5) for k, v in by_api.items()},
        "note": "Production標準のGemini TTS Batch API(gemini-3.1-flash-tts-preview, voice=Charon)"
                "+OpenAI ASR(gpt-4o-mini-transcribe)+ASR Cascade(openai responses.create)経路の実費。"
                "4入力(a/b/c/d)×最大3回(標準2+fallback1)のTTS/ASR呼び出し実費。",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
