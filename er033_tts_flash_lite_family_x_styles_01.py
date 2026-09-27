# ============================================================
# er033_tts_flash_lite_family_x_styles_01.py
# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01 Phase 1
# ============================================================
# 性質: 定数辞書のみで構成する(副作用・API呼び出し・importによる挙動変化
# 一切なし)。設計書§(d)のDangling Reference Check方針に従い、Family
# A/B/C(legacy)の呼び出し元コードはこのモジュールを一切importしない
# (importするのは、tts_backend="speech_metadata_flash_lite"を明示的に
# 選択するFamily Xランナー[er019_family_x_audio_production_runner_01.py]
# のみを想定する。共有TTS関数[p9a/voice01/repro01/crosslevel/n3等]自身は
# このモジュールを参照しない — role別style値は呼び出し側[Family X
# ランナー]がstyle_prefix_overrideとして明示的に渡す設計のため)。
#
# 値の根拠: TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01 Stage 3
# (er022_tts_gemini_3_8_flash_lite_next_trial_01_stage3.py、
# ROLE_ATTEMPT1_STYLE/FALLBACK_STYLES)で実測済みの、Family X Hormuz B1B
# 1記事12segment(英語のみ)の役割別最小style文字列をそのまま転記した
# (新しい値をここで新規に考案してはいない)。plan_role文字列
# ("TOPIC_INTRO"/"PREVIEW"/"COMMENT"/"FULL_STORY"/"HEADING_READOUT"/
# "IN_ONE_LINE")は、既存Production概念(er019_family_x_audio_plan_01.
# FAMILY_X_B1_SEGMENT_ORDER/FAMILY_X_A2_SEGMENT_ORDER)と一致する
# (設計書§(d)で確認済み)。
from __future__ import annotations

# ------------------------------------------------------------
# Model
# ------------------------------------------------------------
# 設計書§(g): 専用定数として保持し、call_fn生成時にactual model_idを
# 明示的に結果へ記録する(既存result["model"]フィールドと同じパターン)。
FAMILY_X_FLASH_LITE_MODEL_NAME = "gemini-3.8-flash-lite-tts"

# ------------------------------------------------------------
# 英語6-role style(Trial実測値、attempt1専用。Stage3
# ROLE_ATTEMPT1_STYLEをそのまま転記)
# ------------------------------------------------------------
FAMILY_X_ROLE_STYLE_EN = {
    "TOPIC_INTRO": "brief, clear, engaging news topic introduction",
    "PREVIEW": "calm, conversational",
    "COMMENT": "calm, conversational",
    "FULL_STORY": "calm, steady news narration",
    "HEADING_READOUT": "brief and clear",
    "IN_ONE_LINE": "concise, clear",
}

# Trial Stage3のattempt2/3 fallback style(FALLBACK_STYLESをそのまま転記)。
# Production側は「標準経路(同一style使用、既定2回)+fallback経路(minimal
# instruction、既定1回)」という構造のため、Trialの3段階(attempt別に
# 異なるstyle)とは1:1に対応しない。Production配線では、fallback
# (minimal instruction)発動時の speech_metadata.style として
# FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]("natural, clear, conversational")を
# 採用する(Trial attempt2相当、既存のMINIMAL_INSTRUCTION系プレフィックス
# より簡潔だが「自然に読む」という意図は共通)。この対応関係は実測に基づく
# ものではなくPhase 1時点の技術判断であり、Phase 2の実TTS/ASR結果を見て
# Opus L2レビュー・Fableが妥当性を再確認すること。
FAMILY_X_ROLE_STYLE_EN_FALLBACK = ["natural, clear, conversational", "clear"]

# ------------------------------------------------------------
# 日本語style(Trial未実測、設計書§(c-2)の判断を踏まえた技術決定)
# ------------------------------------------------------------
# Trial(Stage1-3)はFamily X Hormuz B1Bの英語12segmentのみを対象とし、
# 日本語segment(A2 preview/comment/japanese_title/KP meaning等)は一度も
# 実際にspeech_metadata方式で生成・ASR検証されていない。設計書§(c-2)は
# 「日本語側の発音解決はtext自体の書き換えであり、speech_metadata方式の
# styleフィールドとは無関係な層のため、追加設計・変更は不要」と判断して
# いるが、これは「JAのtext処理は無変更でよい」という結論であり、
# speech_metadata.styleへ何を渡すべきかは実測データが無いままである。
# 以下の値は、既存Structured Separation方式で使っているinstruction文字列
# (p9a.JAPANESE_STYLE_PREFIX等)をそのまま流用する設計方針(Production
# 共有関数側の実装、Dangling Reference Check維持のためこのモジュール内には
# 転記しない)を補助する短い代替表現として用意したが、**Phase 1時点では
# Family Xランナーからは参照しない**(JA側はstyle_prefix_overrideを渡さず、
# 各共有関数が保持する既存JAPANESE_STYLE_PREFIX/MINIMAL_INSTRUCTION_
# PREFIX_JA等のテキストをそのままspeech_metadata.styleへ転用する)。
# Phase 2でJA実音声evidenceが揃うまでUSER_DECISION_REQUIREDではなく
# 「Trial未検証」の状態として明示するための記録として残す。
FAMILY_X_JA_STYLE_NOTE = (
    "TRIAL_UNVALIDATED: JA speech_metadata.style content is not yet "
    "evidence-based; Phase 1 reuses each shared function's existing "
    "JAPANESE_STYLE_PREFIX / minimal-instruction text verbatim as the "
    "style field (no new short JA style invented here)."
)
