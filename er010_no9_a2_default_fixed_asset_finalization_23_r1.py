# ============================================================
# er010_no9_a2_default_fixed_asset_finalization_23_r1.py
# ER-010-NO9-A2-DEFAULT-FIXED-ASSET-FINALIZATION-23-R1
# ============================================================
# OPEN-103の"default"個別対応。新規TTS Trialは行わず、リポジトリ内の
# 既存承認済み音声から正しい英語発音の"default"を探索する。
#
# 探索範囲(実施済み、このモジュールはその再現用):
#   1. 既存kp2_en.wav(er006_output/pool_pilot_01/pool_n9_tip_screens/
#      a2/narration/kp2_en.wav)を実際にASRで再確認する。
#   2. No.9 A2/B1BのFull Story本文(parts.json)に"default"という単語が
#      地の文として登場する箇所が無いか確認する(Key Phrase一覧とは別)。
#   3. 該当segmentが既にreview_lock上RESOLVED(=ASR content-match検証
#      PASS済み)であることを確認し、faster-whisper(ローカル無料、
#      追加API課金なし)のword-level timestampで"default"の位置を特定、
#      単語単位で切り出す。
#   4. 切り出した音声をProduction ASR(実API、小額課金)・ローカル
#      faster-whisperの両方で再検証する。
#
# 明確な禁止(このタスクの明示的指示): Trial 21のEnglish Lock Attempt
# 3/4を今回の固定assetとして使わない、新規TTS Trialを行わない。
# 本モジュールもいずれも行っていない(既存音声の再ASR・単語切り出しのみ)。
#
# Claude Codeはこの候補群を勝手に正式採用しない。ユーザー提示専用。

from __future__ import annotations

import json
import os

import er002_common as common
import er006_asr_provider_routing_01 as routing
import er008_disfluency_qa_18 as dq18

OUT_DIR = "er010_output/no9_a2_default_fixed_asset_finalization_23_r1"
CANDIDATES_DIR = f"{OUT_DIR}/candidates"

EXISTING_KP2_PATH = "er006_output/pool_pilot_01/pool_n9_tip_screens/a2/narration/kp2_en.wav"

# faster-whisperで特定した、本文ナレーション中の"default"の実際の位置
# (word-level timestamp、秒)。この定数はwiring-22時点の正式Production
# 完成音声[full_story_part1/full_story_part2/full_story_part2_original]
# に対する実測値であり、これらのsegmentが将来別テキストで再生成された
# 場合は再特定が必要(このモジュールは今回の一回限りの調査用)。
WORD_EXTRACTION_MARGIN_SECONDS = 0.06
CANDIDATE_SOURCES = {
    "b1b_full_story_part1": {
        "source_path": "er006_output/pool_pilot_01/pool_n9_tip_screens/b1b/narration/full_story_part1.wav",
        "word_start": 35.72, "word_end": 36.26,
        "context": "...At fares just below and just above that price, passengers saw different "
                   "default tip menus.",
    },
    "a2_full_story_part2": {
        "source_path": "er006_output/pool_pilot_01/pool_n9_tip_screens/a2/narration/full_story_part2.wav",
        "word_start": 27.70, "word_end": 28.26,
        "context": "...So, a high default can raise the tip from some customers. But it can "
                   "also push other customers away...",
    },
    "a2_full_story_part2_original": {
        "source_path": "er006_output/pool_pilot_01/pool_n9_tip_screens/a2/narration/"
                        "full_story_part2_original.wav",
        "word_start": 26.16, "word_end": 26.70,
        "context": "...So, a high default can raise the tip from some customers. But it can "
                   "also push other customers away...",
    },
}


def reverify_existing_kp2_en() -> dict:
    """既存kp2_en.wavを実際にASRで再確認する(前回セッションの「異常発生前
    の古い生成物」という評価を、実データで再検証する)。"""
    samples, sr, channels, _meta = common.read_wav_float(EXISTING_KP2_PATH)
    duration = len(samples) / sr
    asr_text, err = routing.transcribe(EXISTING_KP2_PATH, language="en-US")
    return {
        "path": EXISTING_KP2_PATH, "duration_seconds": round(duration, 4),
        "sample_rate": sr, "channels": channels,
        "asr_text": asr_text, "asr_error": err,
        "is_default": bool(asr_text and "default" in asr_text.lower()),
    }


def extract_and_verify_candidate(name: str) -> dict:
    """本文ナレーション中の"default"をword-level timestampで切り出し、
    Production ASR(実API)・ローカルfaster-whisperの両方で再検証する。"""
    spec = CANDIDATE_SOURCES[name]
    os.makedirs(CANDIDATES_DIR, exist_ok=True)
    samples, sr, _channels, _meta = common.read_wav_float(spec["source_path"])
    margin = WORD_EXTRACTION_MARGIN_SECONDS
    s_idx = max(0, int((spec["word_start"] - margin) * sr))
    e_idx = min(len(samples), int((spec["word_end"] + margin) * sr))
    clip = samples[s_idx:e_idx]
    out_path = f"{CANDIDATES_DIR}/{name}_extracted_default.wav"
    common.write_wav_float(out_path, clip, sr, 1)
    duration = len(clip) / sr

    production_asr_text, production_asr_err = routing.transcribe(out_path, language="en-US")
    local_words = dq18.transcribe_verbatim(out_path, language="en")

    return {
        "name": name, "source_path": spec["source_path"], "context": spec["context"],
        "word_start": spec["word_start"], "word_end": spec["word_end"], "margin": margin,
        "extracted_path": out_path, "duration_seconds": round(duration, 4),
        "production_asr_text": production_asr_text, "production_asr_error": production_asr_err,
        "local_whisper_words": local_words,
    }


def run_search() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    result = {
        "existing_kp2_en": reverify_existing_kp2_en(),
        "candidates": {name: extract_and_verify_candidate(name) for name in CANDIDATE_SOURCES},
    }
    with open(f"{OUT_DIR}/search_and_extraction_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    return result


if __name__ == "__main__":
    run_search()
