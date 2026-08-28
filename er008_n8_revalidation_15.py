# ============================================================
# er008_n8_revalidation_15.py
# ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part M:
# No.8 Human Review 3件の再validation(新規TTS/ASR呼び出しなし)
# ============================================================
# 既存音声を再TTSせず、既に記録済みのASR文字起こし(human_review_queue.
# jsonl)を、新しいValidator/Cascadeロジックへそのまま再投入して再評価
# する。ASR呼び出しはモックで「その時点の実際の記録済み文字列」を順番に
# 返すだけで、新規のASR API呼び出しは一切発生しない。
#
# wait/weightのみ例外: Part L監査で判明した通り、Human Review Lock
# 発動時にattempts_logが空配列で上書きされる実装だったため、リポジトリ
# 内に生のASR文字列が残っていない。ユーザーの元タスク記述にある
# 「ASR: weight」を既知の事実として使い、6回とも"weight"だったと仮定して
# 再評価する(この制約は結果に明記する)。
from __future__ import annotations

import json

from dotenv import load_dotenv
load_dotenv()

import er005_cost_logger as cl
cl.init_logger("er008_output/n8_revalidation_15/cost_log.jsonl")

import er003_b1_p4_audio as p4
import er006_asr_provider_routing_01 as routing
import er006_secondary_asr_01 as secondary
import er007_ja_secondary_asr_01 as ja_secondary

RESULTS_PATH = "er008_output/n8_revalidation_15/results.json"


def _replay_english(canonical_text: str, wav_path: str, step_texts: dict) -> dict:
    """step_texts: {"primary_1":..., "primary_2":..., "secondary_1":..., "secondary_2":...}
    実際に記録済みの文字列を、その順番通りに返すだけのモック。新規ASR呼び出しは発生しない。"""
    orig_transcribe = routing.transcribe
    orig_azure = secondary.get_full_text_via_azure_stt_with_phrase_list
    azure_calls = {"n": 0}

    def fake_transcribe(*a, **k):
        return step_texts["primary_2"], None

    def fake_azure(*a, **k):
        azure_calls["n"] += 1
        key = "secondary_1" if azure_calls["n"] == 1 else "secondary_2"
        return step_texts[key], None

    routing.transcribe = fake_transcribe
    secondary.get_full_text_via_azure_stt_with_phrase_list = fake_azure
    try:
        detail = secondary.evaluate_attempt_with_cascade_detail(
            canonical_text, step_texts["primary_1"], [], wav_path, language="en-US", cascade_enabled=True)
    finally:
        routing.transcribe = orig_transcribe
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_azure
    return detail


def _replay_japanese(canonical_text: str, wav_path: str, step_texts: dict) -> dict:
    orig_openai = routing._transcribe_openai_mini
    orig_azure = p4.get_full_text_via_azure_stt_continuous
    azure_calls = {"n": 0}

    def fake_openai(*a, **k):
        return step_texts["primary_2"], None

    def fake_azure(*a, **k):
        azure_calls["n"] += 1
        key = "secondary_1" if azure_calls["n"] == 1 else "secondary_2"
        return step_texts[key], None

    routing._transcribe_openai_mini = fake_openai
    p4.get_full_text_via_azure_stt_continuous = fake_azure
    try:
        detail = ja_secondary.evaluate_attempt_ja_with_cascade_detail(
            canonical_text, step_texts["primary_1"], wav_path, cascade_enabled=True)
    finally:
        routing._transcribe_openai_mini = orig_openai
        p4.get_full_text_via_azure_stt_continuous = orig_azure
    return detail


def revalidate_kristie_tse() -> dict:
    canonical_text = (
        "Kristie Tse links the behavior to anxiety and a wish to feel in control. The overhead bins add "
        "another worry: people may fear being last and having to check a bag. Once a few passengers form "
        "a line, others may copy them. Social pressure can make waiting feel safer."
    )
    wav_path = "er006_output/pool_pilot_01/pool_n8_airport_line/b1b/narration/point_two.wav"
    # 実際にhuman_review_queue.jsonlへ記録された5回分のCascade試行(2026-08-27実施)。
    with open("er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]
    kristie_entries = [e for e in entries if e["wav_path"] == wav_path]

    attempts = []
    for entry in kristie_entries:
        step_texts = {s["step"]: s["text"] for s in entry["steps"]}
        detail = _replay_english(canonical_text, wav_path, step_texts)
        attempts.append({
            "recorded_timestamp": entry["timestamp"],
            "recorded_primary_1_text": step_texts["primary_1"],
            "new_verified": detail["verified"],
            "new_final_status": detail["final_status"],
            "new_human_review_required": detail["human_review_required"],
            "new_pronunciation_lookups": detail.get("pronunciation_lookups", {}),
        })
    any_verified = any(a["new_verified"] for a in attempts)
    return {
        "case": "Kristie Tse (B1 point_two)",
        "canonical_text": canonical_text,
        "attempts_replayed": len(attempts),
        "attempts": attempts,
        "overall_result": "VALIDATED" if any_verified else "HUMAN_REVIEW",
        "note": "5回のCascade試行のうち、いずれか1回でも新ロジックでverified=Trueになれば"
                "VALIDATEDとする(実運用でも最初にverifiedになった時点でPASSするため)。",
    }


def revalidate_koro_kore() -> dict:
    canonical_text = (
        "今回は、空港の搭乗口で、搭乗が始まる前からできる列についてのニュースです。まだ呼ばれていない"
        "乗客が立つことで、搭乗口ではどんな課題が生まれるのでしょうか。このニュースでは、乗客の行動と"
        "空港の仕組みに注目します。聞き終えるころには、この早い列がなぜ空港の話題になり、搭乗口でどんな"
        "変化が始まっているのかが分かります。"
    )
    wav_path = "er006_output/pool_pilot_01/pool_n8_airport_line/a2/narration/preview.wav"
    with open("er007_output/ja_asr_cascade_01/human_review_queue.jsonl", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]
    matching = [e for e in entries if e["wav_path"] == wav_path]

    attempts = []
    for entry in matching:
        step_texts = {s["step"]: s["text"] for s in entry["steps"]}
        detail = _replay_japanese(canonical_text, wav_path, step_texts)
        attempts.append({
            "recorded_timestamp": entry["timestamp"],
            "new_verified": detail["verified"],
            "new_final_status": detail["final_status"],
            "new_human_review_required": detail["human_review_required"],
        })
    any_verified = any(a["new_verified"] for a in attempts)
    return {
        "case": "ころ/頃 (A2 preview)",
        "canonical_text": canonical_text,
        "attempts_replayed": len(attempts),
        "attempts": attempts,
        "overall_result": "VALIDATED" if any_verified else "HUMAN_REVIEW",
        "note": "わかります/分かりますは元々content_diffsに現れないため、この再validationの対象外"
                "(既に自動吸収済み)。",
    }


def revalidate_wait_weight() -> dict:
    canonical_text = "A small wait can protect against a big fear."
    wav_path = "er006_output/pool_pilot_01/pool_n8_airport_line/a2/narration/point_one_heading.wav"
    # Part L監査で判明した通り、Human Review Lock発動によりattempts_logが
    # 空配列で上書きされており、リポジトリ内に生のASR文字列が残っていない。
    # 元タスク記述の「ASR: weightだけであれば」を既知事実として、6回とも
    # "weight"だったと仮定して再評価する。
    synthetic_asr_text = "A small weight can protect against a big fear."
    step_texts = {"primary_1": synthetic_asr_text, "primary_2": synthetic_asr_text,
                  "secondary_1": synthetic_asr_text, "secondary_2": synthetic_asr_text}
    detail = _replay_english(canonical_text, wav_path, step_texts)
    return {
        "case": "wait/weight (A2 point_one_heading)",
        "canonical_text": canonical_text,
        "caveat": "リポジトリに生ASR文字列が保存されていない(Part L監査で発見した記録欠落そのもの)。"
                  "ユーザーの元タスク記述にある「ASR: weight」を既知事実として、6回とも\"weight\"だった"
                  "と仮定した合成データで再評価している。実際の生ログでの裏付けは取れていない。",
        "synthetic_asr_text_used": synthetic_asr_text,
        "new_verified": detail["verified"],
        "new_final_status": detail["final_status"],
        "new_human_review_required": detail["human_review_required"],
        "overall_result": "VALIDATED" if detail["verified"] else "HUMAN_REVIEW",
    }


def main() -> dict:
    results = {
        "kristie_tse": revalidate_kristie_tse(),
        "koro_kore": revalidate_koro_kore(),
        "wait_weight": revalidate_wait_weight(),
    }
    import os
    os.makedirs("er008_output/n8_revalidation_15", exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    for key, r in results.items():
        print(f"[{r['overall_result']}] {r['case']}")
    return results


if __name__ == "__main__":
    main()
