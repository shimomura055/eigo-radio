# ============================================================
# er011_open117_keyphrase_display_tts_separation_trial_02_cost_compute.py
# OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02の実費計算
# ============================================================
# Trial-01(er011_open117_keyphrase_display_tts_separation_trial_01_cost_
# compute.py)と同じ補完パターン(gemini_batch::gemini-3.1-flash-tts-previewの
# Batch tier単価を追加)を踏襲する(共有module er011_specfix_cost_compute_01は
# 変更しない)。本Trialは選定/canonicalization/redundancy QA(openai、
# gpt-5.6-luna)・Key Phrase日本語TTS(gemini_batch、B1=flash-tts-preview
# [Charon]/A2=gemini-2.5-pro-preview-tts[Aoede])・OpenAI ASRを含む。
from __future__ import annotations

import json

import er011_specfix_cost_compute_01 as cc

GEMINI_FLASH_BATCH_IN = cc.price_tiered("gemini", "gemini-3.1-flash-tts-preview", "input_tokens", "Batch")
GEMINI_FLASH_BATCH_OUT = cc.price_tiered("gemini", "gemini-3.1-flash-tts-preview", "output_tokens", "Batch")

LOG_PATH = "er011_output/open117_keyphrase_display_tts_separation_trial_02/raw_usage_log_open117_trial02.jsonl"
OUT_PATH = "er011_output/open117_keyphrase_display_tts_separation_trial_02/cost_summary_open117_trial02.json"


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
        "note": "Production標準経路(選定/canonicalization/redundancy QA[openai gpt-5.6-luna]、"
                "Key Phrase日本語TTS[gemini_batch、B1=Charon flash-tts-preview/A2=Aoede "
                "gemini-2.5-pro-preview-tts]、OpenAI ASR[gpt-4o-mini-transcribe])の実費。"
                "本文13/14 segmentは再利用のためTTS/ASR課金なし(0 API call)。"
                "Key Phrase英語ComponentはMaster Audio Store経由でTTS課金がgemini_batch::"
                "gemini-2.5-pro-preview-tts側に混在する。",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
