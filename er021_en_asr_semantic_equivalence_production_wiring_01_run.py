# ============================================================
# er021_en_asr_semantic_equivalence_production_wiring_01_run.py
# 管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(Phase A+B)
# ============================================================
# Runtime evidence(実API)取得用オーケストレーションスクリプト。
# 正式generate関数(B1 voice01.generate_charon_english、A2
# crosslevel_audio_02_common.generate_english_segment_with_fallback)を
# 実際にそのまま呼び出す(判定層だけを個別に呼ぶのではない)。
#   - TTS_EXECUTION_MODE=STANDARD
#   - 専用out-dir(er021_output/en_asr_semantic_equivalence_production_
#     wiring_01/probes/...、既存記事artifactは一切触れない)
#   - cost logger必須(er005_cost_logger.install)
#   - 各probeはmax_attempts=1に固定し、Tier1が発火しない不測の事態でも
#     過剰なTTS/ASR再試行・cool-down・Local Rewriteが発生しないようにする
#     (enable_connected_speech_equivalence_layerも既定Falseのまま)。

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

import er005_cost_logger as cost_logger
import er011_human_review_lock_01 as review_lock
import er003_v1_sing01_voice01_generate as voice01
import er003_v1_crosslevel_audio_02_common as crosslevel
import er006_preprod_hardening_01_validation as val

OUT_DIR = "er021_output/en_asr_semantic_equivalence_production_wiring_01"
PROBE_DIR = f"{OUT_DIR}/probes"
RESULTS_PATH = f"{OUT_DIR}/runtime_evidence_results.json"
COST_LOG_PATH = f"{OUT_DIR}/audit/raw_usage_log.jsonl"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 30.0

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
# B1 probe(voice01.generate_charon_english、Charon英語、正式generate関数)
# ============================================================
B1_THEME, B1_LEVEL = "semantic_equivalence_probe", "b1_dev"
B1_PROBES = [
    {"segment_id": "comment_1",
     "canonical": "Company profits reached four point seven billion dollars this quarter."},
    {"segment_id": "in_one_line",
     "canonical": "The new policy officially took effect in twenty twenty-six."},
    {"segment_id": "topic_intro",
     "canonical": "Growth came in at two point five percent this month."},
    {"segment_id": "preview",
     "canonical": "The device now costs one hundred twenty five dollars."},
    # role非適用の対照probe(Key Phrase/Heading同様、role gate自体が
    # Falseになることを確認する。out_pathのsegment名をpoint_one_heading
    # にすることで、resolve_narrative_role()がHEADING_READOUTを返す)。
    {"segment_id": "point_one_heading",
     "canonical": "Company profits reached four point seven billion dollars this quarter."},
]


def run_b1_probes():
    log("\n=== B1 probe(voice01.generate_charon_english、実TTS+実ASR) ===")
    results = []
    for item in B1_PROBES:
        seg = item["segment_id"]
        out_path = f"{PROBE_DIR}/{B1_THEME}/{B1_LEVEL}/narration/{seg}.wav"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        log(f"\n--- B1 segment_id={seg} ---\n  canonical: {item['canonical']!r}")
        result = voice01.generate_charon_english(item["canonical"], out_path, max_attempts=1)
        assert_budget_ok(f"after B1 {seg}")
        attempts_log = result.get("attempts_log") or []
        last_attempt = attempts_log[-1] if attempts_log else {}
        row = {
            "segment_id": seg, "canonical": item["canonical"],
            "status": result.get("status"),
            "asr_text": result.get("asr_text") or last_attempt.get("asr_text"),
            "audio_classification": result.get("audio_classification") or last_attempt.get("audio_classification"),
            "semantic_equivalence": last_attempt.get("semantic_equivalence"),
        }
        results.append(row)
        log(f"  status={row['status']} asr_text={row['asr_text']!r}")
        log(f"  audio_classification={row['audio_classification']} "
            f"semantic_equivalence={row['semantic_equivalence']}")
    return results


# ============================================================
# A2 probe(crosslevel.generate_english_segment_with_fallback、正式
# generate関数)+ er003_v1_n3_01_tts_generate.apply_a2_slowdown_postprocess
# と同じ再判定パターン(実際に配線した1行、segment_id=name)を、実際に
# 得られたASR逐語で再現する。
# ============================================================
A2_THEME, A2_LEVEL = "semantic_equivalence_probe", "a2_dev"
A2_PROBE = {"segment_id": "full_story_part1",
            "canonical": "The company reported profits of three point one billion dollars last year."}


def run_a2_probe():
    log("\n=== A2 probe(crosslevel_audio_02_common.generate_english_segment_with_fallback、実TTS+実ASR) ===")
    seg = A2_PROBE["segment_id"]
    canonical = A2_PROBE["canonical"]
    out_path = f"{PROBE_DIR}/{A2_THEME}/{A2_LEVEL}/narration/{seg}.wav"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    log(f"\n--- A2 segment_id={seg} ---\n  canonical: {canonical!r}")
    result = crosslevel.generate_english_segment_with_fallback(
        canonical, out_path, expected_substring=canonical[:10], max_attempts=1, standard_attempts=1)
    assert_budget_ok("after A2 standard path")
    attempts_log = result.get("attempts_log") or []
    last_attempt = attempts_log[-1] if attempts_log else {}
    asr_text = result.get("asr_text") or last_attempt.get("asr_text")
    row_standard = {
        "segment_id": seg, "canonical": canonical, "status": result.get("status"),
        "asr_text": asr_text,
        "audio_classification": result.get("audio_classification") or last_attempt.get("audio_classification"),
    }
    log(f"  [standard path, unowned repro01経由のためsegment_id非配線] status={row_standard['status']} "
        f"asr_text={asr_text!r} classification={row_standard['audio_classification']}")

    # er003_v1_n3_01_tts_generate.apply_a2_slowdown_postprocess()で実際に
    # 配線した1行(classify_asr_match(..., segment_id=name))を、上記で
    # 実際に得られたASR逐語を使って再現する(新規TTS/ASR呼び出しなし、¥0)。
    reclass_with_gate = val.classify_asr_match(canonical, asr_text, segment_id=seg) if asr_text else None
    reclass_without_gate = val.classify_asr_match(canonical, asr_text) if asr_text else None
    row_standard["post_slowdown_style_reclassification_with_segment_id"] = (
        reclass_with_gate.classification if reclass_with_gate else None)
    row_standard["post_slowdown_style_reclassification_without_segment_id"] = (
        reclass_without_gate.classification if reclass_without_gate else None)
    row_standard["semantic_equivalence_with_gate"] = (
        getattr(reclass_with_gate, "semantic_equivalence_info", None) if reclass_with_gate else None)
    log(f"  [apply_a2_slowdown_postprocess同型の再判定、¥0] "
        f"segment_id有={row_standard['post_slowdown_style_reclassification_with_segment_id']} / "
        f"segment_id無={row_standard['post_slowdown_style_reclassification_without_segment_id']}")
    return row_standard


def main():
    cost_logger.install(COST_LOG_PATH)
    b1_results = run_b1_probes()
    a2_result = run_a2_probe()
    jpy_final, by_provider = compute_cost_jpy_so_far()
    output = {"b1_probes": b1_results, "a2_probe": a2_result,
              "cost_jpy_final": round(jpy_final, 2), "cost_by_provider_jpy": by_provider}
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    log(f"\n=== 完了。実測費用: {jpy_final:.2f} JPY {by_provider} ===")
    log(f"結果: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
