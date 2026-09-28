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

# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(2026-09-28、
# ユーザー確定仕様C): Family Xでは共有narration(固定shell+Key Phrase)も
# 含めFlash-Liteへ原則統一する。MasterAudioKey.tts_model_idにこの値を
# 使うことで、既存Structured Separation資産(TTS_MODEL_EN/JA)とは自動的に
# 別のmaster_audio_idになり、既存entryを無効化せずbackward compatibleに
# 共存する(既存entry無変更、Flash-Lite分は別キーで新規生成・保存)。
TTS_MODEL_FLASH_LITE = "gemini-3.8-flash-lite-tts"


def _resolve_shared_narration_model(language: str, tts_backend: str) -> str:
    if tts_backend == "speech_metadata_flash_lite":
        return TTS_MODEL_FLASH_LITE
    return TTS_MODEL_EN if language == "en" else TTS_MODEL_JA

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



# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(修正3回目、
# 2026-09-28、Opus L2所見BL-1是正): shell固定英語segment(welcome/
# preview_intro/key_phrases_intro/full_story_intro/num_one〜five)は、
# tts_backend="speech_metadata_flash_lite"のときstyle_prefix_overrideを
# 渡していなかったため、モデルだけFlash-Liteへ切り替わりstyle層は
# p9a.ENGLISH_STYLE_PREFIX(約2,000字・記事本文向けの長い指示)のまま
# 単語1つ("Two."等)に適用され、num_two実測失敗(ASR="Ту"、
# TRUE_CONTENT_MISMATCH)の最有力原因になっていた。新規style文言は
# 考案せず、既にTrial実測済みのer033_tts_flash_lite_family_x_styles_01.
# FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]("natural, clear, conversational")を
# 流用する(ユーザー承認2026-09-28「shell用styleは、報告案どおり既存の
# FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]を流用してよい」)。既定backend
# ("structured_separation")では従来どおりstyle_prefix_override=None
# のまま(byte-identical)。
SHELL_ENGLISH_FLASH_LITE_STYLE_INSTRUCTION_VERSION = "v2_flash_lite_short_style"

# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W2、2026-09-29): ユーザーが
# TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02(er043)/TTS-FIXED-SHELL-NUMBER-
# THREE-FIVE-RETRIAL-01(er047)で正式決定したChampion(固定phraseごとに
# 勝者candidate/takeが異なる、B系統とC系統が混在)をProduction Master
# Storeへ配線する。welcomeのみ現行Master(v2_flash_lite_short_style、
# FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]="natural, clear, conversational")を
# 継続reuseし、新規登録しない(ユーザー決定「welcome=A」)。welcome以外の
# 8 English phraseは、phraseごとに異なるChampion style文言(B/C系統)を
# 使うため、単一のFAMILY_X_ROLE_STYLE_EN_FALLBACK[0]一律適用では表現
# できず、phrase別style mapが必要になった(旧v2版の「shell全体に単一
# style」という設計からの変更点)。
#
# 新styleを適用するには、旧v2_flash_lite_short_style時代に生成済みの
# master(9件、Championとは異なるstyleで生成された資産)が黙ってcache
# hitし続けないよう、style_instruction_versionを必ずbumpする(BL-1で
# 踏んだ同型の罠、上のコメント参照)。旧v2資産は削除せず残置する
# (以後のreuseは新versionのkeyのみが参照する)。
SHELL_CHAMPION_STYLE_INSTRUCTION_VERSION = "v3_champion_2026_09_29"

# er043_output/tts_fixed_shell_master_champion_trial_02/
# champion_trial_results.json の各candidateの"style_prefix_used"から
# 逐語転記(welcomeを除く8 English phrase。num_three/num_fiveは
# er047_output/tts_fixed_shell_number_three_five_retrial_01/
# retrial_results.jsonのstyleB take1の"style_prefix_used"から逐語転記、
# num_two/num_threeが同じstyleB系統・num_one/num_fourが同じstyleC系統の
# 文言であることをsource JSON上で確認済み)。新しいstyle文言の考案は
# 一切していない。
SHELL_CHAMPION_STYLE_BY_PHRASE_EN = {
    "preview_intro": "natural, clear, conversational",
    "key_phrases_intro": "natural, clear, conversational",
    "full_story_intro": (
        "natural, clear, conversational, unhurried pace, "
        "with a brief pause before continuing"),
    "num_one": (
        "measured, matter-of-fact delivery, consistent energy and tempo "
        "for every word, plain falling pitch at the end, spoken as a flat "
        "statement, not a question"),
    "num_two": (
        "calm, steady, declarative tone, even volume and pace across the "
        "set, ending each word with a clear falling pitch, stated plainly, "
        "never rising like a question"),
    "num_three": (
        "calm, steady, declarative tone, even volume and pace across the "
        "set, ending each word with a clear falling pitch, stated plainly, "
        "never rising like a question"),
    "num_four": (
        "measured, matter-of-fact delivery, consistent energy and tempo "
        "for every word, plain falling pitch at the end, spoken as a flat "
        "statement, not a question"),
    "num_five": (
        "calm, steady, declarative tone, even volume and pace across the "
        "set, ending each word with a clear falling pitch, stated plainly, "
        "never rising like a question"),
}

# point_explanation(JA、A2専用)のChampion(candidate B)。
# er043_output/.../champion_trial_results.jsonのcandidates.B.
# point_explanation.style_prefix_usedから逐語転記。下位の
# voice01.generate_charon_japaneseにはstyle_prefix_override引数が無く
# (EN側generate_charon_englishとは非対称、BL-1所見時点からの既知の
# 制約・本タスクのスコープ外)、cache hit経路(登録済みChampion音声の
# reuse)でのみこの文言が実際の音声と対応する。cache miss(登録済み
# 音声が万一失われた場合のfallback再生成)時はこの文言が音声生成には
# 反映されない既知の制約として記録する(REPORT参照)。
SHELL_CHAMPION_STYLE_JA_POINT_EXPLANATION_B = "自然な抑揚をつけて、はっきりと落ち着いた調子で話す"


def _resolve_shell_english_style_prefix_override(name: str, tts_backend: str) -> str | None:
    if tts_backend != "speech_metadata_flash_lite":
        return None
    if name == "welcome":
        import er033_tts_flash_lite_family_x_styles_01 as fl_styles
        return fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]
    return SHELL_CHAMPION_STYLE_BY_PHRASE_EN[name]


def _make_english_key(name: str, text: str, tts_backend: str = "structured_separation") -> store.MasterAudioKey:
    # BL-1是正: Flash-Lite backend時のみstyle_instruction_versionをbump
    # する。さもないと長prefixで生成済みのFlash-Lite shell masterが
    # 黙ってcache hitし続け、上記のstyle override修正が効かない
    # (shared_narration.py内KEY_PHRASE_TRIM_POLICY_VERSIONで過去に
    # 踏んだ同型の罠、Opus所見BL-1参照)。既定backendのkeyは無変更
    # ("v1"のまま、既存Structured Separation資産のcache維持)。
    #
    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W2、2026-09-29):
    # welcomeは現行Master(v2)を継続。welcome以外はChampion版
    # (SHELL_CHAMPION_STYLE_INSTRUCTION_VERSION)へ切り替える。
    if tts_backend != "speech_metadata_flash_lite":
        version = "v1"
    elif name == "welcome":
        version = SHELL_ENGLISH_FLASH_LITE_STYLE_INSTRUCTION_VERSION
    else:
        version = SHELL_CHAMPION_STYLE_INSTRUCTION_VERSION
    return store.MasterAudioKey(
        language="en", speaker_voice="Charon",
        tts_model_id=_resolve_shared_narration_model("en", tts_backend),
        canonical_text=text, level=None,
        style_instruction_id="charon_english_fixed_shell", style_instruction_version=version,
    )


def _make_japanese_key(text: str, tts_backend: str = "structured_separation") -> store.MasterAudioKey:
    # BL-1所見はensure_fixed_japanese_segment(point_explanation、A2のみ)
    # にも触れているが、下位のvoice01.generate_charon_japanese自体に
    # style_prefix_override引数が無く(EN側のgenerate_charon_englishとは
    # 非対称)。JA側のstyle override機構自体の新設(generate_charon_japanese
    # への引数追加)は本タスクでも引き続きスコープ外(SHELL_CHAMPION_STYLE_
    # JA_POINT_EXPLANATION_B参照のコメント)。
    #
    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W2、2026-09-29): ただし
    # point_explanationはChampion(candidate B)としてProduction Master
    # Storeへ新規登録するため、Flash-Lite backend時のみversionをbumpし、
    # 旧v1資産(Champion決定前のstyleで生成された既存entry)が新keyの
    # 参照先として黙ってcache hitしないようにする(現在JA固定phraseは
    # point_explanationの1種類のみのため、phrase別mapは不要、一律bump
    # で足りる)。
    version = (SHELL_CHAMPION_STYLE_INSTRUCTION_VERSION
               if tts_backend == "speech_metadata_flash_lite" else "v1")
    return store.MasterAudioKey(
        language="ja", speaker_voice="Charon",
        tts_model_id=_resolve_shared_narration_model("ja", tts_backend),
        canonical_text=text, level=None,
        style_instruction_id="charon_japanese_fixed_shell", style_instruction_version=version,
    )


def ensure_fixed_english_segment(name: str, narration_dir: str, filename_suffix: str = "",
                                  # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02
                                  # (2026-09-28、既定"structured_separation"で既存挙動と
                                  # byte-identical、既存MasterAudioKeyはtts_model_idが同じ
                                  # ため無変更): Family X runnerのみが明示的に
                                  # "speech_metadata_flash_lite"を渡す。
                                  tts_backend: str = "structured_separation") -> dict:
    text = FIXED_ENGLISH_TEXTS[name]
    out_path = f"{narration_dir}/{name}{filename_suffix}.wav"
    key = _make_english_key(name, text, tts_backend)
    style_prefix_override = _resolve_shell_english_style_prefix_override(name, tts_backend)
    return store.get_or_generate(
        key, out_path, lambda p: voice01.generate_charon_english(
            text, p, style_prefix_override=style_prefix_override, tts_backend=tts_backend))


def ensure_fixed_japanese_segment(name: str, narration_dir: str,
                                   tts_backend: str = "structured_separation") -> dict:
    text = FIXED_JAPANESE_TEXTS_A2_ONLY[name]
    out_path = f"{narration_dir}/{name}.wav"
    key = _make_japanese_key(text, tts_backend)
    return store.get_or_generate(
        key, out_path,
        lambda p: voice01.generate_charon_japanese(text, p, text, max_attempts=6, tts_backend=tts_backend))


def ensure_key_phrase_english_component(used_form_tts_safe: str, out_path: str,
                                        tts_backend: str = "structured_separation") -> dict:
    """Key Phrase英語Component(voice=Aoede)をMaster Audio Store経由で
    取得する。同一トピックのB1/A2で同じKey Phraseテキスト(tts_safe_kp_en
    正規化後の同一文字列)・同じvoice/model/styleの場合のみreuseされる
    (level=Noneで揃えている)。文字列が少しでも異なれば別のmaster_audio_id
    になり、reuseされない(ER-006-AUDIO-COST-OPTIMIZATION-01 §2.3で
    確認済みの4件の重複Key Phraseが対象)。

    TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(2026-09-28、
    ユーザー確定仕様C): tts_backend="speech_metadata_flash_lite"の場合、
    tts_model_idがFlash-Liteになるため既存Structured Separation資産とは
    別キーになり(既存entry無変更)、Flash-Liteで新規生成・保存される。"""
    key = store.MasterAudioKey(
        language="en", speaker_voice="Aoede",
        tts_model_id=_resolve_shared_narration_model("en", tts_backend),
        canonical_text=used_form_tts_safe, level=None,
        style_instruction_id="key_phrase_english_component",
        style_instruction_version=KEY_PHRASE_TRIM_POLICY_VERSION,
    )
    return store.get_or_generate(
        key, out_path,
        lambda p: repro01.generate_key_phrase_component_verified(used_form_tts_safe, p, tts_backend=tts_backend))


def ensure_all_shared_narration_b1(narration_dir: str, tts_backend: str = "structured_separation") -> dict:
    """B1向け: Master Audio Store経由でwelcome/preview_intro/key_phrases_
    intro/full_story_intro/num_one〜fiveを取得する。ファイル名は既存の
    er003_v1_n3_01_assemble.py::load_b1_sources()が期待する"_charon"
    suffix付きで書き出す(assemble.py側は無変更のまま、copy_b1_shared_
    assets()が「既にファイルが存在すればコピーしない」設計のため、この
    関数を先に呼んでおけば自動的にStore経由の音声が優先される)。"""
    os.makedirs(narration_dir, exist_ok=True)
    results = {}
    for name in FIXED_ENGLISH_TEXTS:
        results[name] = ensure_fixed_english_segment(name, narration_dir, filename_suffix="_charon",
                                                       tts_backend=tts_backend)
    return results


def ensure_all_shared_narration_a2(narration_dir: str, tts_backend: str = "structured_separation") -> dict:
    """A2向け: 上記に加えpoint_explanation(日本語)も取得する。
    Key(level=None)はB1と完全に同一のため、B1側で既にMasterが存在すれば
    ここではTTSを一切呼ばずreuseする。"""
    os.makedirs(narration_dir, exist_ok=True)
    results = {}
    for name in FIXED_ENGLISH_TEXTS:
        results[name] = ensure_fixed_english_segment(name, narration_dir, tts_backend=tts_backend)
    for name in FIXED_JAPANESE_TEXTS_A2_ONLY:
        results[name] = ensure_fixed_japanese_segment(name, narration_dir, tts_backend=tts_backend)
    return results
