# ============================================================
# er021_en_asr_semantic_equivalence_production_wiring_01_fix2_run.py
# 管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(Fable差し戻し
# 修正2回目)
# ============================================================
# 修正2回目のruntime evidence(実API)取得用オーケストレーションスクリプト。
# 既知Gapだった「B1本文(er003_v1_sing01_news_tail_fix.py::
# generate_news_narration_wide_margin、Full Story/Point/In One Line生成の
# 主経路)にsegment_idが未配線」を解消したことを、実際の正式generate関数を
# そのまま呼び出して確認する(判定層だけを個別に呼ぶのではない)。
#   - TTS_EXECUTION_MODE=STANDARD
#   - 専用out-dir(er021_output/en_asr_semantic_equivalence_production_
#     wiring_01/probes_fix2/、既存記事artifactは一切触れない)
#   - cost logger必須(er005_cost_logger.install)
#   - max_attempts=1に固定する。これにより「attempt1(唯一の試行)だけで
#     NUMERIC_EQUIVALENCE_MATCHとしてPASSする」ことを実データで直接証明
#     する(もし修正が効いていなければ、attempt1のTRUE_CONTENT_MISMATCHの
#     まま即STOPPEDになるはずであり、両者は明確に区別できる)。
#   - telemetry.jsonl(observability、role適用かつTier1不一致の場合のみ
#     追記される設計)の行数を実行前後で比較する。今回のprobeはTier1で
#     PASSする想定のため、この設計上、新規telemetry行は追加されない
#     (Tier1で救済された場合はobservability対象外という既存設計、
#     Phase A実装時からの仕様どおり)。telemetry機構自体が生きていることは
#     既存test(Tier1ProductionCorpusTest等、role適用NEGATIVE corpusを
#     実ロジック経由)で既に確認済み。

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

import er005_cost_logger as cost_logger
import er003_v1_sing01_news_tail_fix as news_tail_fix

OUT_DIR = "er021_output/en_asr_semantic_equivalence_production_wiring_01"
PROBE_DIR = f"{OUT_DIR}/probes_fix2"
RESULTS_PATH = f"{OUT_DIR}/runtime_evidence_results_fix2.json"
COST_LOG_PATH = f"{OUT_DIR}/audit/raw_usage_log_fix2.jsonl"
TELEMETRY_PATH = f"{OUT_DIR}/telemetry.jsonl"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 10.0  # Guardrail(委任文の目安予算¥3に対し、安全側の上限)

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


def _telemetry_line_count():
    if not os.path.exists(TELEMETRY_PATH):
        return 0
    with open(TELEMETRY_PATH, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


# ============================================================
# B1本文probe(news_tail_fix.generate_news_narration_wide_margin、正式
# generate関数。max_attempts=1固定=唯一の試行のみで合否が決まる)。
# ============================================================
THEME, LEVEL = "semantic_equivalence_probe_fix2", "b1b_dev"
SEGMENT_ID = "full_story_part1"
CANONICAL = "The company reported profits of four point seven billion dollars last year."


def main():
    cost_logger.install(COST_LOG_PATH)
    telemetry_before = _telemetry_line_count()

    out_path = f"{PROBE_DIR}/{THEME}/{LEVEL}/narration/{SEGMENT_ID}.wav"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    log(f"\n=== B1本文probe(news_tail_fix.generate_news_narration_wide_margin、"
        f"segment_id={SEGMENT_ID}、max_attempts=1、実TTS+実ASR) ===")
    log(f"  canonical: {CANONICAL!r}")
    result = news_tail_fix.generate_news_narration_wide_margin(CANONICAL, out_path, max_attempts=1)
    assert_budget_ok(f"after B1 {SEGMENT_ID}")
    telemetry_after = _telemetry_line_count()

    attempts_log = result.get("attempts_log") or []
    row = {
        "segment_id": SEGMENT_ID, "canonical": CANONICAL, "status": result.get("status"),
        "asr_text": result.get("asr_text"),
        "audio_classification": result.get("audio_classification"),
        "attempts_log": attempts_log,
        "attempts_log_len": len(attempts_log),
        "cooldown_events_present": "cooldown_events" in result,
        "cooldown_events": result.get("cooldown_events"),
        "telemetry_line_count_before": telemetry_before,
        "telemetry_line_count_after": telemetry_after,
    }
    log(f"  status={row['status']} asr_text={row['asr_text']!r}")
    log(f"  audio_classification={row['audio_classification']} "
        f"attempts_log_len={row['attempts_log_len']} cooldown_events={row['cooldown_events']}")
    log(f"  telemetry.jsonl line count: before={telemetry_before} after={telemetry_after} "
        f"(Tier1 PASS時は既存設計により新規行なし。telemetry機構自体はunittest側の"
        f"実ロジック経由テストで別途確認済み)")

    jpy_final, by_provider = compute_cost_jpy_so_far()
    output = {"b1_full_story_part1_probe": row,
              "cost_jpy_final": round(jpy_final, 2), "cost_by_provider_jpy": by_provider}
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    log(f"\n=== 完了。実測費用: {jpy_final:.2f} JPY {by_provider} ===")
    log(f"結果: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
