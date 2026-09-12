# ============================================================
# er011_tts_cooldown_observation_harness_helpers_01.py
# 管理ID: PM-CLOSEOUT-CONSOLIDATION-84-OPEN145-OPEN146-WIRING-AND-A2-DISTRIBUTION
# ============================================================
# 目的: `TTS-RETRY-COOLDOWN-20MIN-OBSERVATION-TRIAL-01_REPORT.md`2節の配線
# 指示書に基づき、A-Family Discovery Trial(タオルTrial-11)・News Trial
# (`er011_news_stage3_new_theme_ledger_trial_09_b1b_full_pipeline.py`)が
# 共通で使う`er003_v1_n3_01_tts_generate.generate_a2_segments()`/
# `generate_b1_segments()`が生成するsegment_id別に、cooldown観測フック
# (`er011_tts_cooldown_observation_01.observe_after_three_consecutive_ng()`)
# へ渡す`single_attempt_fn`(Review Lockデコレータの外側=`.__wrapped__`)・
# `single_attempt_kwargs`を組み立てる。
#
# 安全性:
#   - Production関数(`generate_a2_segments`/`generate_b1_segments`、および
#     それらが呼ぶ`repro01.generate_narration_snippet_verified_strict`/
#     `voice01.generate_charon_english`/`news_tail_fix.
#     generate_news_narration_wide_margin`/`point_headings.generate`)は
#     一切変更しない(read-onlyでimportし`.__wrapped__`を取得するのみ)。
#   - out_pathは常にTrial専用の観測パス
#     (`{narration_dir}/_cooldown_observation_01/{segment_id}.wav`)を使う。
#     Production成果物(`{narration_dir}/{segment_id}.wav`)には一切
#     書き込まない。
#   - `max_attempts=1`を明示指定し、4回目1回だけを実行する(cooldown観測
#     module側の契約どおり)。
#   - Key Phrase英語Component(Master Audio Store経由の`shared_narration.
#     ensure_key_phrase_english_component`)は対象外(Storeの再利用ロジック
#     との相性を本タスクでは検証していないため、スコープ外として明示する)。
#
# 本モジュールは`TTS_COOLDOWN_OBSERVATION`が"1"の場合のみ呼び出し側から
# 実際に使われる(既定OFF、呼び出し側のno-op分岐は各harness側で行う)。
from __future__ import annotations

import os

import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01

# Review Lockデコレータの外側の生関数(1.3節: デコレータ付きのまま呼ぶと
# 3回連続NG後は既にHUMAN_REVIEW_REQUIREDのためcheck_before_generation()が
# 即ブロックし観測不能になる)。
RAW_NARRATION_SNIPPET = repro01.generate_narration_snippet_verified_strict.__wrapped__
RAW_CHARON_ENGLISH = voice01.generate_charon_english.__wrapped__
RAW_NEWS_WIDE_MARGIN = news_tail_fix.generate_news_narration_wide_margin.__wrapped__
RAW_POINT_HEADING = point_headings.generate.__wrapped__

A2_JA_SIMPLE_SEGMENTS = ("preview", "comment_1", "comment_2", "comment_3", "comment_4")
A2_EN_HEADING_SEGMENTS = ("point_one_heading", "point_two_heading")
A2_EN_BODY_SEGMENTS = ("full_story_part1", "full_story_part2", "point_one", "point_two")

B1_CHARON_SEGMENTS = ("preview", "comment_1", "comment_2", "comment_3", "comment_4")
B1_HEADING_SEGMENTS = ("point_one_heading", "point_two_heading")
B1_NEWS_BODY_SEGMENTS = ("full_story_part1", "full_story_part2", "point_one", "point_two", "in_one_line")

# segment_id(またはprefix)がこの集合に含まれる場合は対象外(Key Phrase
# 英語Component、Master Audio Store経由)。
OUT_OF_SCOPE_PREFIXES = ("kp",)


def observation_out_path(narration_dir: str, segment_id: str) -> str:
    d = f"{narration_dir}/_cooldown_observation_01"
    os.makedirs(d, exist_ok=True)
    return f"{d}/{segment_id}.wav"


def is_in_scope(segment_id: str) -> bool:
    return not any(segment_id.startswith(p) for p in OUT_OF_SCOPE_PREFIXES)


def build_a2_single_attempt_binding(segment_id: str, canonical_text: str, narration_dir: str):
    """A2 segment_id -> (raw_fn, args=(), kwargs)。未対応segment_idは
    Noneを返す(呼び出し側はNoneならその場でskipする)。"""
    if not is_in_scope(segment_id):
        return None
    out_path = observation_out_path(narration_dir, segment_id)

    if segment_id == "topic_intro":
        return RAW_NARRATION_SNIPPET, (), dict(
            text=tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(canonical_text)),
            language="en", out_path=out_path,
            expected_substring=tts_gen.first_words(canonical_text, 3), max_attempts=1, max_extra_chars=30)

    if segment_id == "japanese_title":
        return RAW_NARRATION_SNIPPET, (), dict(
            text=canonical_text, language="ja", out_path=out_path,
            expected_substring=tts_gen.expected_substring_ja(canonical_text), max_attempts=1, max_extra_chars=30)

    if segment_id in A2_JA_SIMPLE_SEGMENTS:
        return RAW_NARRATION_SNIPPET, (), dict(
            text=canonical_text, language="ja", out_path=out_path,
            expected_substring=tts_gen.expected_substring_ja(canonical_text), max_attempts=1)

    if segment_id.startswith("meaning_"):
        return RAW_NARRATION_SNIPPET, (), dict(
            text=canonical_text, language="ja", out_path=out_path,
            expected_substring=tts_gen.expected_substring_ja(canonical_text), max_attempts=1, max_extra_chars=30)

    if segment_id in A2_EN_HEADING_SEGMENTS:
        return RAW_NARRATION_SNIPPET, (), dict(
            text=tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(canonical_text)),
            language="en", out_path=out_path,
            expected_substring=tts_gen.first_words(canonical_text, 3), max_attempts=1, max_extra_chars=20,
            style_prefix_override=tts_gen.A2_ENGLISH_STYLE_PREFIX_SLOWER, disfluency_qa=True)

    if segment_id in A2_EN_BODY_SEGMENTS:
        return RAW_NARRATION_SNIPPET, (), dict(
            text=tts_gen.tts_safe_news_en(canonical_text), language="en", out_path=out_path,
            expected_substring=tts_gen.first_words(canonical_text), max_attempts=1,
            style_prefix_override=tts_gen.A2_ENGLISH_STYLE_PREFIX_SLOWER,
            enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True)

    return None


def build_b1_single_attempt_binding(segment_id: str, canonical_text: str, narration_dir: str):
    """B1(B1B)segment_id -> (raw_fn, args=(), kwargs)。未対応segment_idは
    Noneを返す。"""
    if not is_in_scope(segment_id):
        return None
    out_path = observation_out_path(narration_dir, segment_id)

    if segment_id == "topic_intro":
        return RAW_CHARON_ENGLISH, (), dict(
            text=tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(canonical_text)),
            out_path=out_path, max_attempts=1)

    if segment_id in B1_CHARON_SEGMENTS:
        return RAW_CHARON_ENGLISH, (), dict(
            text=tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(canonical_text)),
            out_path=out_path, max_attempts=1,
            style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True)

    if segment_id in B1_HEADING_SEGMENTS:
        return RAW_POINT_HEADING, (), dict(
            text=tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(canonical_text)),
            out_path=out_path, max_attempts=1)

    if segment_id in B1_NEWS_BODY_SEGMENTS:
        return RAW_NEWS_WIDE_MARGIN, (), dict(
            text=tts_gen.tts_safe_news_en(canonical_text), out_path=out_path, max_attempts=1,
            disfluency_qa=(segment_id == "in_one_line"),
            enable_connected_speech_equivalence_layer=(segment_id != "in_one_line"),
            enable_repetition_qa=(segment_id != "in_one_line"))

    return None


def load_three_attempt_records(narration_dir: str, segment_id: str) -> list:
    """`{narration_dir}/attempts/{segment_id}_attempt*.json`から
    attempt_number降順で直近3件を読み込む(既存の`er011_human_review_lock_01.
    save_tts_attempt_audio()`が書き出すスキーマをそのまま読む、read-only)。
    3件未満、または3件とも`verified=False`でない場合は空listを返す
    (呼び出し側は空listならcooldown観測を呼ばない)。"""
    import glob
    import json

    pattern = f"{narration_dir}/attempts/{segment_id}_attempt*.json"
    paths = [p for p in glob.glob(pattern) if p.endswith(".json")]
    records = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            records.append(json.load(f))
    records.sort(key=lambda r: r.get("attempt_number", 0))
    last_three = records[-3:]
    if len(last_three) != 3:
        return []
    if any(r.get("verified") is not False for r in last_three):
        return []
    return last_three
