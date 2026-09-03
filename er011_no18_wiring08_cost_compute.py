from __future__ import annotations

import json

import er011_specfix_cost_compute_01 as cc

GEMINI_FLASH_BATCH_IN = cc.price_tiered("gemini", "gemini-3.1-flash-tts-preview", "input_tokens", "Batch")
GEMINI_FLASH_BATCH_OUT = cc.price_tiered("gemini", "gemini-3.1-flash-tts-preview", "output_tokens", "Batch")


def call_cost_usd(r: dict) -> float:
    # cc.call_cost_usd()はgemini_batch+flashモデル(A2の一部segmentで使用)の
    # Batch単価分岐が未実装のため、ここでのみ補完する(共有moduleは変更しない)。
    if r.get("provider") == "gemini_batch" and r.get("model_id") == "gemini-3.1-flash-tts-preview":
        it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
        return (it / 1e6) * GEMINI_FLASH_BATCH_IN + (ot / 1e6) * GEMINI_FLASH_BATCH_OUT
    return cc.call_cost_usd(r)


LOGS = [
    "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/raw_usage_log_wiring08_audio.jsonl",
    "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/raw_usage_log_wiring08_scoped_retry.jsonl",
]


def load_records():
    records = []
    for path in LOGS:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def main():
    records = load_records()
    total_usd = 0.0
    resolver_usd = 0.0
    resolver_calls = 0
    tts_asr_usd = 0.0
    for r in records:
        if not r.get("success", True):
            continue  # 課金対象外(APIエラー、費用ゼロ扱い)
        cost = call_cost_usd(r)
        total_usd += cost
        if r.get("api") == "responses.create":
            resolver_usd += cost
            resolver_calls += 1
        else:
            tts_asr_usd += cost

    result = {
        "total_calls": len(records),
        "total_usd": round(total_usd, 4),
        "total_jpy": round(total_usd * cc.USD_JPY, 2),
        "reading_resolver_calls": resolver_calls,
        "reading_resolver_usd": round(resolver_usd, 4),
        "reading_resolver_jpy": round(resolver_usd * cc.USD_JPY, 2),
        "tts_asr_usd": round(tts_asr_usd, 4),
        "tts_asr_jpy": round(tts_asr_usd * cc.USD_JPY, 2),
        "connected_speech_validator_cost_jpy": 0.0,
        "note": "Connected Speech Validatorはローカルpure Pythonロジックのため追加API呼び出し・追加費用は0円。"
                "Reading Resolverはresponses.create(gpt-5.6-luna)呼び出し分のみを分離集計。",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    with open("er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/cost_summary_wiring08.json",
              "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
