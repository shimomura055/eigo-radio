# ============================================================
# er003_b1_p3v_capability.py
# ER-003-B1-P3V Phase 1: TTS API機能確認(Break / Mark / Timestamp)
# ============================================================
# 現在このプロジェクトが使っているTTS実装(er002_gemini_client.py、
# Gemini TTS、google-genai SDK)が、以下のいずれかに対応しているかを、
# 推測ではなく実装コードとインストール済みSDKの型定義を調べて判定する。
#
#   優先順位1: ネイティブBreak(SpeechConfig等の専用フィールド)
#   優先順位2: SSML <break>(contentsへSSML文字列を渡して解釈させる機構)
#   優先順位3: Mark / Bookmark / Timepoint(挿入位置に印を置きoffsetを
#              受け取る機構)
#   優先順位4: TTS生成時に返される文字・単語レベルのTimestamp、または
#              SDKが返すaudio offset metadata
#
# 判定はgoogle-genai SDKの実際の型定義(SpeechConfig/Part/Modalityの
# フィールド一覧)を直接調べることで行う。ドキュメントは、コード調査で
# 判定できない場合にのみ補助的に参照する。

from __future__ import annotations

import er002_common as common

# TTS呼び出しに実際に使われているモデル・SDK呼び出し形(er002_gemini_client.py
# のmake_tts_call_fnをそのまま引用。推測ではなく実装コードから転記)。
REQUEST_FORM = (
    "client.models.generate_content(model=common.MODEL_NAME, "
    "contents=<plain text prompt>, "
    "config=types.GenerateContentConfig("
    "response_modalities=['AUDIO'], "
    "speech_config=types.SpeechConfig(language_code=..., "
    "voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=...)))))"
)
RESPONSE_FORM = (
    "response.candidates[0].content.parts[*].inline_data.data "
    "(生PCMバイト列のみ。テキスト・タイムスタンプ・オフセット等は含まない)"
)


def check_tts_capability() -> dict:
    """インストール済みgoogle-genai SDKの型定義を直接調べ、Break/SSML/
    Mark・Timepoint/Timestamp・offsetメタデータのいずれかに対応する
    フィールドが存在するかを機械的に判定する。"""
    import google.genai as genai_pkg
    from google.genai import types

    sdk_version = getattr(genai_pkg, "__version__", "unknown")

    speech_config_fields = sorted(types.SpeechConfig.model_fields.keys())
    part_fields = sorted(types.Part.model_fields.keys())
    modality_values = [m.value for m in types.Modality]

    # SpeechConfigは voice_config / language_code / multi_speaker_voice_config
    # の3フィールドのみで、break・pause・silence等の専用フィールドは存在しない。
    _break_keywords = ("break", "pause", "silence", "mark", "bookmark", "timepoint")
    native_break_fields = [f for f in speech_config_fields if any(k in f.lower() for k in _break_keywords)]
    native_break_supported = len(native_break_fields) > 0

    # contentsはplain textのpromptであり、SSMLをパースする専用パラメータや
    # モードは存在しない(GenerateContentConfigにSSML関連フィールドはない)。
    ssml_break_supported = False

    mark_timepoint_fields = [f for f in speech_config_fields if any(k in f.lower() for k in ("mark", "bookmark", "timepoint"))]
    mark_timepoint_supported = len(mark_timepoint_fields) > 0

    # Partが持つフィールドの中に、文字・単語レベルのtimestamp/offsetを
    # 表すものがあるかを確認する。part_metadataはSDK利用者が任意の値を
    # 設定できる汎用dictであり、Gemini TTSのレスポンスとして自動的に
    # タイミング情報が入るフィールドではない(サーバー側から時刻情報が
    # 返される仕組みではない)。
    _timestamp_keywords = ("timestamp", "offset", "timepoint")
    timestamp_like_fields = [f for f in part_fields if any(k in f.lower() for k in _timestamp_keywords)]
    tts_timestamp_supported = len(timestamp_like_fields) > 0

    any_capability_available = any([
        native_break_supported, ssml_break_supported, mark_timepoint_supported, tts_timestamp_supported,
    ])

    return {
        "tts_model": common.MODEL_NAME,
        "sdk_name": "google-genai",
        "sdk_version": sdk_version,
        "request_form": REQUEST_FORM,
        "response_form": RESPONSE_FORM,
        "speech_config_fields": speech_config_fields,
        "part_fields": part_fields,
        "modality_values": modality_values,
        "native_break_supported": native_break_supported,
        "native_break_candidate_fields": native_break_fields,
        "ssml_break_supported": ssml_break_supported,
        "ssml_break_note": (
            "contentsはSSMLをパースするAPIパラメータを持たないplain textの"
            "promptであり、<break>等のタグを埋め込んでもマークアップとして"
            "解釈される機構が存在しない(過去のER-003-B1-P3Rで、この方式の"
            "Gemini TTSに日英混在テキストを渡した際、テキストとして誤読され"
            "400エラーになった実績があり、任意のタグ埋め込みが安全に無視・"
            "解釈される保証もない)。"
        ),
        "mark_timepoint_supported": mark_timepoint_supported,
        "mark_timepoint_candidate_fields": mark_timepoint_fields,
        "tts_timestamp_supported": tts_timestamp_supported,
        "tts_timestamp_candidate_fields": timestamp_like_fields,
        "part_metadata_note": (
            "Part.part_metadataはSDK利用者側が任意の値を設定できる汎用dict"
            "フィールドであり、Gemini TTSのレスポンスとして音声タイミング情報"
            "が自動的に格納される仕組みではない(公式説明: 'Custom metadata "
            "associated with the Part')。"
        ),
        "sdk_offset_metadata_supported": tts_timestamp_supported,
        "any_capability_available": any_capability_available,
    }
