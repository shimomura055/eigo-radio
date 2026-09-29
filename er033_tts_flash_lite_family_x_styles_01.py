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
# TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B、2026-09-28):
# TOPIC_INTRO/FULL_STORY/IN_ONE_LINEの3値を、TTS-VARIABLE-SPOKEN-ROLE-
# STYLE-TRIAL-02でユーザーが正式決定・APPROVED_FOR_PRODUCTIONとした
# E2実測値へ更新(逐語転記、新規style考案なし)。PREVIEW/COMMENT/
# HEADING_READOUTはE2未検証のため不変(E0のまま)。
FAMILY_X_ROLE_STYLE_EN = {
    "TOPIC_INTRO": "brief, clear, engaging news topic introduction with natural emphasis on the topic; "
                   "not dramatic.",
    "PREVIEW": "calm, conversational",
    "COMMENT": "calm, conversational",
    "FULL_STORY": "calm, steady news narration with natural emphasis at key points and turns; not dramatic.",
    "HEADING_READOUT": "brief and clear",
    "IN_ONE_LINE": "concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.",
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
# 日本語style(Phase 1: Trial未実測、Phase 2: TRIAL-02実測・ユーザー
# 承認済みのJ3を採用)
# ------------------------------------------------------------
# Trial(Stage1-3、Phase 1時点)はFamily X Hormuz B1Bの英語12segmentのみを
# 対象とし、日本語segment(A2 preview/comment/japanese_title/KP meaning等)
# は一度もspeech_metadata方式で生成・ASR検証されていなかった。設計書
# §(c-2)は「日本語側の発音解決はtext自体の書き換えであり、speech_metadata
# 方式のstyleフィールドとは無関係な層のため、追加設計・変更は不要」と
# 判断していたが、これは「JAのtext処理は無変更でよい」という結論であり、
# speech_metadata.styleへ何を渡すべきかは実測データが無いままだった。
# **Phase 1時点では**以下のFAMILY_X_JA_STYLE_NOTEの方針どおりFamily X
# ランナーからは参照せず、各共有関数が保持する既存JAPANESE_STYLE_PREFIX/
# MINIMAL_INSTRUCTION_PREFIX_JA等のテキストをそのままspeech_metadata.style
# へ転用していた。
FAMILY_X_JA_STYLE_NOTE = (
    "TRIAL_UNVALIDATED: JA speech_metadata.style content is not yet "
    "evidence-based; Phase 1 reuses each shared function's existing "
    "JAPANESE_STYLE_PREFIX / minimal-instruction text verbatim as the "
    "style field (no new short JA style invented here)."
)

# TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B、2026-09-28):
# TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02(er044.J_PATTERN_STYLES["J3"])で
# 実測・ASR検証・ユーザー正式決定(APPROVED_FOR_PRODUCTION)されたJ3を、
# 新規style考案なしで逐語転記する。日本語はEN側のようなrole別辞書ではなく、
# role非依存の単一style文字列(Family X Standard[A2]のJA preview/
# comment_1〜4へ一律適用、japanese_title・Key Phraseは対象外)。
# `speech_metadata_flash_lite` backend明示時のみ参照される(EN 6-roleと
# 同じbackendゲート、既定backendでは`er019._role_style_ja()`がNoneを返し
# JAPANESE_STYLE_PREFIXのまま無変更)。
FAMILY_X_ROLE_STYLE_JA = (
    "落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。"
    "演技がかった話し方は避けてください。"
)

# ------------------------------------------------------------
# Advanced(B1B)Key Phrase 英語解説(explanation_en)style
# ------------------------------------------------------------
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W4、2026-09-29): Key Phrase
# 音声構造(Standard/Advanced共通骨格、CURRENT_SPEC.md「Key Phrase 音声
# 構造」節)のAdvanced中間segment(英語解説)専用style。KEY-PHRASE-ADVANCED-
# ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04(er046)で比較した中間3案
# (A/B/C)のうちVariant B「clear, precise, at a measured pace, without
# dragging」をユーザーが2026-09-29に正式採用(逐語転記、新規style考案
# なし)。このKey Phrase解説roleは本Wiring以前は存在しなかった全く新しい
# roleのため(既存の6-role style辞書のような「既定backend=None、
# flash-lite backendのみ適用」というgatingは適用しない)、tts_backend
# の値によらず常にこのstyleをstyle_prefix_overrideとして使う
# (n3_tts.generate_key_phrase_explanation_en_verified経由、Family X
# runnerのみが参照する)。
KEY_PHRASE_EXPLANATION_EN = "clear, precise, at a measured pace, without dragging"
