# ============================================================
# er021_en_asr_semantic_equivalence_production_wiring_01_fix1_run.py
# 管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(Fable差し戻し
# 修正1回目)
# ============================================================
# 修正1回目のruntime evidence(実API)取得用オーケストレーションスクリプト。
# 既知Gapだった「A2標準経路(crosslevel_audio_02_common.
# generate_english_segment_with_fallback()の標準呼び出し)にsegment_idが
# 未配線」を解消したことを、実際の正式generate関数をそのまま呼び出して
# 確認する(判定層だけを個別に呼ぶのではない)。
#   - TTS_EXECUTION_MODE=STANDARD
#   - 専用out-dir(er021_output/en_asr_semantic_equivalence_production_
#     wiring_01/probes_fix1/、既存記事artifactは一切触れない)
#   - cost logger必須(er005_cost_logger.install)
#   - 各probeはmax_attempts=1・standard_attempts=1に固定する。これにより
#     「attempt1(標準経路の初回攻撃)だけでNUMERIC_EQUIVALENCE_MATCHとして
#     PASSする」ことを実データで直接証明する(もし修正が効いていなければ、
#     attempt1のTRUE_CONTENT_MISMATCHのままfallback予算0で即STOPPEDになる
#     はずであり、両者は明確に区別できる)。

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

import er005_cost_logger as cost_logger
import er003_v1_crosslevel_audio_02_common as crosslevel

OUT_DIR = "er021_output/en_asr_semantic_equivalence_production_wiring_01"
PROBE_DIR = f"{OUT_DIR}/probes_fix1"
RESULTS_PATH = f"{OUT_DIR}/runtime_evidence_results_fix1.json"
COST_LOG_PATH = f"{OUT_DIR}/audit/raw_usage_log_fix1.jsonl"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 15.0  # Guardrail(委任文の目安予算¥5に対し、安全側の上限)

os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)


def log(msg):
    print(msg, flush=True)


def _load_pricing():
    prices = json.load(open(PRICING_SNAPSHOT_PATH, encoding="utf-8"))["prices"]

    def price(provider, model, meter, tier="Standard"):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                    and p.get("tier", "Standard") == tier)
    return price


def compute_cost_jpy_so_far():
    if not os.path.exists(COST_LOG_PATH):
        return 0.0, {}
    price = _load_pricing()
    total_usd, by_provider = 0.0, {}
    with open(COST_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            usd = 0.0
            try:
                if provider == "openai_asr" and model:
                    in_tok, out_tok = rec.get("input_tokens") or 0, rec.get("output_tokens") or 0
                    usd = in_tok * price("openai_asr", model, "input_tokens") / 1e6 \
                        + out_tok * price("openai_asr", model, "output_tokens") / 1e6
                elif provider == "azure":
                    dur_s = rec.get("audio_duration_submitted_seconds") or 0.0
                    usd = (dur_s / 3600.0) * price(
                        "azure", "real-time transcription (S0/S1 standard tier)", "audio_hour")
                elif provider in ("gemini", "gemini_batch") and model:
                    tier = "Batch" if provider == "gemini_batch" else "Standard"
                    in_tok, out_tok = rec.get("input_tokens") or 0, rec.get("output_tokens") or 0
                    usd = in_tok * price("gemini", model, "input_tokens", tier) / 1e6 \
                        + out_tok * price("gemini", model, "output_tokens", tier) / 1e6
            except StopIteration:
                usd = 0.0
            total_usd += usd
            by_provider[provider] = by_provider.get(provider, 0.0) + usd
    return total_usd * USD_JPY, {k: round(v * USD_JPY, 2) for k, v in by_provider.items()}


def assert_budget_ok(note=""):
    jpy, by = compute_cost_jpy_so_far()
    log(f"  [budget] so far {jpy:.2f} JPY (cap {BUDGET_JPY_CAP}) breakdown={by} ({note})")
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.1f} JPY > cap {BUDGET_JPY_CAP} JPY. Stopping ({note}).")
    return jpy


# ============================================================
# A2標準経路probe(crosslevel.generate_english_segment_with_fallback、
# 正式generate関数。max_attempts=1・standard_attempts=1固定=fallback
# 予算0、標準経路attempt1のみで合否が決まる)。
# ============================================================
A2_THEME, A2_LEVEL = "semantic_equivalence_probe_fix1", "a2_dev"
A2_PROBES = [
    {"segment_id": "full_story_part1",
     "canonical": "The company reported profits of four point seven billion dollars last year."},
    {"segment_id": "topic_intro",
     "canonical": "The forecast now covers the period through twenty twenty-six."},
]


def run_a2_probes():
    log("\n=== A2標準経路probe(crosslevel_audio_02_common."
        "generate_english_segment_with_fallback、standard_attempts=1、実TTS+実ASR) ===")
    results = []
    for item in A2_PROBES:
        seg = item["segment_id"]
        canonical = item["canonical"]
        out_path = f"{PROBE_DIR}/{A2_THEME}/{A2_LEVEL}/narration/{seg}.wav"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        log(f"\n--- A2 segment_id={seg} ---\n  canonical: {canonical!r}")
        result = crosslevel.generate_english_segment_with_fallback(
            canonical, out_path, expected_substring=canonical[:15], max_attempts=1, standard_attempts=1)
        assert_budget_ok(f"after A2 {seg}")
        attempts_log = result.get("attempts_log") or []
        row = {
            "segment_id": seg, "canonical": canonical, "status": result.get("status"),
            "asr_text": result.get("asr_text"),
            "audio_classification": result.get("audio_classification"),
            "attempts_log_len": len(attempts_log),
            "fallback_used": result.get("fallback_used"),
            "cooldown_events_present": "cooldown_events" in result,
        }
        results.append(row)
        log(f"  status={row['status']} asr_text={row['asr_text']!r}")
        log(f"  audio_classification={row['audio_classification']} "
            f"attempts_log_len={row['attempts_log_len']} fallback_used={row['fallback_used']} "
            f"cooldown_events_present={row['cooldown_events_present']}")
    return results


def main():
    cost_logger.install(COST_LOG_PATH)
    a2_results = run_a2_probes()
    jpy_final, by_provider = compute_cost_jpy_so_far()
    output = {"a2_standard_path_fix1_probes": a2_results,
              "cost_jpy_final": round(jpy_final, 2), "cost_by_provider_jpy": by_provider}
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    log(f"\n=== 完了。実測費用: {jpy_final:.2f} JPY {by_provider} ===")
    log(f"結果: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
