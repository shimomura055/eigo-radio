# ============================================================
# er003_b1_p7a_audio.py
# ER-003-B1-P7A: Geminiモデル監査・3.1単一call限定検証
# ============================================================
# P4D・P6A・P6Bが実際に使用したTTSモデルIDを、コード(er002_common.
# MODEL_NAME)・呼び出し経路(er002_gemini_client.make_tts_call_fn)から
# 追跡して特定する(監査結果はer003_v1_b1_p7a_generate.pyのdocstring/
# 実行報告に記録、本モジュールでは再現しない)。
#
# 監査結果: P4D/P6A/P6Bはいずれも同一の呼び出し経路
#   er002_gemini_client.make_tts_call_fn(voice_name)
#     -> client.models.generate_content(model=er002_common.MODEL_NAME, ...)
#   MODEL_NAME = "gemini-2.5-pro-preview-tts"(er002_common.py:53、
#   コメントに「ER-001B-9/10・ER-002-S0の凍結仕様から変更しない」と明記)
# を経由しており、3.1未満のモデルを使用していたことが確認された。
#
# er002_common.MODEL_NAME/er002_gemini_client.pyは凍結仕様(ER-002本編が
# 依存)のため変更しない。本モジュールは、同じ呼び出し形状(response_
# modalities=["AUDIO"]、speech_config、http timeout)を維持したまま
# モデルIDだけをgemini-3.1-flash-tts-previewへ差し替えたtts_call_fnを
# 独立して提供する。
#
# 再利用するもの(再実装しない):
#   - er002_gemini_client.make_client/build_speech_config/TTS_TIMEOUT_MS
#   - er002_common._call_tts_with_retry/pcm_to_wav_bytes/read_wav_float/
#     measure_metrics/SAMPLE_RATE
#   - er003_b1_p4_audio.get_full_text_via_azure_stt_continuous
#   - er003_b1_p4b_audio.VOICE_NAME/JAPANESE_STYLE_PREFIX/build_tts_prompt

from __future__ import annotations

import difflib
import hashlib

from google import genai
from google.genai import types

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p4b_audio as p4b

ARTICLE_ID = "A01"
CANDIDATE_MODEL_NAME = "gemini-3.1-flash-tts-preview"
BASELINE_MODEL_NAME = common.MODEL_NAME  # "gemini-2.5-pro-preview-tts"(監査で確認済み)

VOICE_NAME = p4b.VOICE_NAME  # "Aoede"
JAPANESE_STYLE_PREFIX = p4b.JAPANESE_STYLE_PREFIX
build_tts_prompt = p4b.build_tts_prompt

MAX_TTS_TECHNICAL_RETRY = 0  # 指示section6「technical retryなし」

KEY_EXPRESSIONS = (
    "激しい接触",
    "枠内シュート",
    "選手を交代で下げる",
    "目印という決断で",
    "守備を固め",
    "わずかなリード",
    "最後の数分",
    "何が起きるのでしょうか",
)
MARKER_TOKEN = "目印"
EXPECTED_MARKER_COUNT = 5


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def model_is_available(model_name: str, client: "genai.Client" = None) -> bool:
    """genai.Client.models.list()の実結果に対象モデルIDが含まれるかを
    確認する(推測でモデルの存在を仮定しない)。"""
    client = client or gclient.make_client()
    full_name = f"models/{model_name}"
    return any(m.name == full_name for m in client.models.list())


def make_tts_call_fn_for_model(model_name: str, voice_name: str, client: "genai.Client" = None):
    """er002_gemini_client.make_tts_call_fnと同一の呼び出し形状
    (response_modalities=["AUDIO"]、speech_config、http timeout)を保ち、
    modelだけを引数で差し替え可能にした版。gclient.py本体は変更しない。"""
    client = client or gclient.make_client()
    speech_config = gclient.build_speech_config(voice_name)

    def tts_call_fn(prompt: str) -> bytes:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=speech_config,
                http_options=types.HttpOptions(timeout=gclient.TTS_TIMEOUT_MS),
            ),
        )
        parts = response.candidates[0].content.parts
        pcm = b"".join(p.inline_data.data for p in parts if p.inline_data and p.inline_data.data)
        if not pcm:
            raise RuntimeError(f"音声パーツが空でした(parts数: {len(parts)})")
        return pcm

    return tts_call_fn


def check_key_expressions(asr_text: str) -> dict:
    result = {}
    for expr in KEY_EXPRESSIONS:
        result[expr] = {"present": expr in asr_text, "count": asr_text.count(expr)}
    result["marker_count"] = asr_text.count(MARKER_TOKEN)
    result["marker_count_matches_expected"] = result["marker_count"] == EXPECTED_MARKER_COUNT
    result["all_key_expressions_present"] = all(v["present"] for k, v in result.items() if k in KEY_EXPRESSIONS)
    return result


def diff_input_vs_asr(input_text: str, asr_text: str) -> dict:
    """全文の疑わしい差分を、文字単位のSequenceMatcherで一覧化する
    (類似度スコアのみでの合否判定はしない、指示section8の明記通り)。"""
    matcher = difflib.SequenceMatcher(a=input_text, b=asr_text, autojunk=False)
    ratio = matcher.ratio()
    ops = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        ops.append({
            "tag": tag,
            "input_segment": input_text[i1:i2],
            "asr_segment": asr_text[j1:j2],
        })
    return {"similarity_ratio": ratio, "diff_ops": ops}
