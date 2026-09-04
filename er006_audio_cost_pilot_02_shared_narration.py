# ============================================================
# er006_audio_cost_pilot_02_shared_narration.py
# ER-006-MASTER-AUDIO-STORE-01: 完全固定segment(Welcome等)を
# Master Audio Store経由で取得するPilot用wiring
# ============================================================
# 既存のcopy_b1_shared_assets()(B1、er003_v1_n3_01_assemble.py)と
# A01_NARRATION_DIR直接参照(A2、er003_v1_crosslevel_audio_02_common.py)
# は、この2つが完全に別々のコピー元であるためdriftしうる(ER-006-AUDIO-
# COST-OPTIMIZATION-01 §2.2で実際にwelcome.wavの長さが2.111s/2.561sと
# 21%ズレていることを確認済み)。
#
# 本モジュールは、B1/A2どちらの生成でも同じMasterAudioKey(level=None=
# レベル非依存)を使ってer006_master_audio_store_01経由で取得する新しい
# 経路を提供する。既存のcopy_b1_shared_assets()・A01_NARRATION_DIR自体は
# 変更しない(他テーマ・他パイプラインへの影響を避けるため、この
# Pilotでの新規生成分のみ本経路を使う、最小Blast Radius)。

from __future__ import annotations

import os

import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_voice01_generate as voice01
import er006_master_audio_store_01 as store

TTS_MODEL_EN = "gemini-2.5-pro-preview-tts"
TTS_MODEL_JA = "gemini-3.1-flash-tts-preview"

# ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23:
# Key Phrase英語ComponentのMasterAudioKeyにtrim policyのversionを含める。
# MasterAudioKey.EQUALITY_FIELDS(er006_master_audio_store_01.py)は
# 生成時に使ったsafety marginそのものを識別子に含まないため、
# repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDSを0.20→0.30秒へ変更
# した後も、0.20秒時代に生成済みのMaster資産(2026-08-17〜09-02に
# 生成された99件、いずれもaudio_processing_version="v1")が同一
# style_instruction_id/version・同一テキストの新規リクエストに対して
# そのままcache hitしてしまい、「現行仕様は0.30秒」という前提が
# 静かに破られる恐れがあった(実際に全99件がこの状態だったことを本
# タスクで確認)。style_instruction_versionへtrim policyのversionを
# 含めることで、旧margin時代の資産とは異なるmaster_audio_idになり、
# 自然にcache missとなって現行margin(0.30秒)で再生成される。
# KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDSを今後変更する場合は、この
# versionも必ず更新すること(さもないと同じ問題が再発する)。
KEY_PHRASE_TRIM_POLICY_VERSION = "v2_margin030"

# er003_v1_sing01_voice01_generate.py::jobs_english および
# er003_v1_repro01_main_generate.py::SERVICE_LEVEL_NARRATION_NAMESの
# コメントと完全一致させる(内容は無変更、既存確定文言をそのまま使う)。
FIXED_ENGLISH_TEXTS = {
    "welcome": "Welcome to English Your Way.",
    "preview_intro": "Here's a quick preview.",
    "key_phrases_intro": "Here are today's key phrases.",
    "full_story_intro": "Now, the full story.",
    "num_one": "One.", "num_two": "Two.", "num_three": "Three.",
    "num_four": "Four.", "num_five": "Five.",
}
# A2のみで使う固定日本語segment。
FIXED_JAPANESE_TEXTS_A2_ONLY = {
    "point_explanation": "ポイント解説",
}


def _make_english_key(text: str) -> store.MasterAudioKey:
    return store.MasterAudioKey(
        language="en", speaker_voice="Charon", tts_model_id=TTS_MODEL_EN,
        canonical_text=text, level=None,
        style_instruction_id="charon_english_fixed_shell", style_instruction_version="v1",
    )


def _make_japanese_key(text: str) -> store.MasterAudioKey:
    return store.MasterAudioKey(
        language="ja", speaker_voice="Charon", tts_model_id=TTS_MODEL_JA,
        canonical_text=text, level=None,
        style_instruction_id="charon_japanese_fixed_shell", style_instruction_version="v1",
    )


def ensure_fixed_english_segment(name: str, narration_dir: str, filename_suffix: str = "") -> dict:
    text = FIXED_ENGLISH_TEXTS[name]
    out_path = f"{narration_dir}/{name}{filename_suffix}.wav"
    key = _make_english_key(text)
    return store.get_or_generate(key, out_path, lambda p: voice01.generate_charon_english(text, p))


def ensure_fixed_japanese_segment(name: str, narration_dir: str) -> dict:
    text = FIXED_JAPANESE_TEXTS_A2_ONLY[name]
    out_path = f"{narration_dir}/{name}.wav"
    key = _make_japanese_key(text)
    return store.get_or_generate(
        key, out_path,
        lambda p: voice01.generate_charon_japanese(text, p, text, max_attempts=6))


def ensure_key_phrase_english_component(used_form_tts_safe: str, out_path: str) -> dict:
    """Key Phrase英語Component(voice=Aoede)をMaster Audio Store経由で
    取得する。同一トピックのB1/A2で同じKey Phraseテキスト(tts_safe_kp_en
    正規化後の同一文字列)・同じvoice/model/styleの場合のみreuseされる
    (level=Noneで揃えている)。文字列が少しでも異なれば別のmaster_audio_id
    になり、reuseされない(ER-006-AUDIO-COST-OPTIMIZATION-01 §2.3で
    確認済みの4件の重複Key Phraseが対象)。"""
    key = store.MasterAudioKey(
        language="en", speaker_voice="Aoede", tts_model_id=TTS_MODEL_EN,
        canonical_text=used_form_tts_safe, level=None,
        style_instruction_id="key_phrase_english_component",
        style_instruction_version=KEY_PHRASE_TRIM_POLICY_VERSION,
    )
    return store.get_or_generate(
        key, out_path,
        lambda p: repro01.generate_key_phrase_component_verified(used_form_tts_safe, p))


def ensure_all_shared_narration_b1(narration_dir: str) -> dict:
    """B1向け: Master Audio Store経由でwelcome/preview_intro/key_phrases_
    intro/full_story_intro/num_one〜fiveを取得する。ファイル名は既存の
    er003_v1_n3_01_assemble.py::load_b1_sources()が期待する"_charon"
    suffix付きで書き出す(assemble.py側は無変更のまま、copy_b1_shared_
    assets()が「既にファイルが存在すればコピーしない」設計のため、この
    関数を先に呼んでおけば自動的にStore経由の音声が優先される)。"""
    os.makedirs(narration_dir, exist_ok=True)
    results = {}
    for name in FIXED_ENGLISH_TEXTS:
        results[name] = ensure_fixed_english_segment(name, narration_dir, filename_suffix="_charon")
    return results


def ensure_all_shared_narration_a2(narration_dir: str) -> dict:
    """A2向け: 上記に加えpoint_explanation(日本語)も取得する。
    Key(level=None)はB1と完全に同一のため、B1側で既にMasterが存在すれば
    ここではTTSを一切呼ばずreuseする。"""
    os.makedirs(narration_dir, exist_ok=True)
    results = {}
    for name in FIXED_ENGLISH_TEXTS:
        results[name] = ensure_fixed_english_segment(name, narration_dir)
    for name in FIXED_JAPANESE_TEXTS_A2_ONLY:
        results[name] = ensure_fixed_japanese_segment(name, narration_dir)
    return results
