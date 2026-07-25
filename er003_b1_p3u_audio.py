# ============================================================
# er003_b1_p3u_audio.py
# ER-003-B1-P3U: 正確な語句境界への英語Key Phrase差し込み再検証
# ============================================================
# ER-003-B1-P3Tでは、日本語通し音声内の「最長無音区間」を差し込み位置と
# みなした結果、実際の語句境界(「枠内シュート」と「を」の間)より
# 約2.19秒早い位置に英語Key Phraseが挿入されていた(ユーザー指摘により
# 判明)。本ステージでは、無音長による推測を廃止し、原稿と音声の対応
# (forced alignment)から境界時刻を直接特定する。
#
# 新しいTTS生成は行わない。ER-003-B1-P3Tで既に生成済みの
#   - er003_output/b1_p3t/A01/raw/ja_full_sentence.wav
#   - er003_output/b1_p3t/A01/raw/en_shot_on_target.wav
# を再利用する。
#
# alignment手段: Azure Cognitive Services Speech SDK
# (azure-cognitiveservices-speech、この環境に既存インストール済み・
# .envにSPEECH_KEY/SPEECH_REGION設定済み。tts_test_azure.pyで同SDKの
# 利用実績あり)のSpeech-to-Text(単語レベルタイムスタンプ付き)を使い、
# 既存の日本語通し音声を解析して「シュート」と「を」の単語境界時刻を
# 直接特定する。新規の大規模基盤構築は行わず、既存依存関係を優先する。
#
# 再利用するもの(再実装しない):
#   - er002_common.SAMPLE_RATE/read_wav_float/write_wav_float/
#     pcm_bytes_to_float_mono/measure_metrics/apply_dynamics3_once
#   - er003_b1_p3t_audio.SOURCE_JAPANESE_FULL_SENTENCE/
#     SOURCE_ENGLISH_KEYWORD(原稿定数、そのまま再利用)
#
# 新規に追加するのは、(1) 既存音声に対するAzure STT単語タイムスタンプ
# 取得、(2) その結果から「シュート|を」境界を特定するロジック、
# (3) 英語Key Phrase音声の前後無音トリム、(4) 境界での日本語分割と
# 0.12秒固定ポーズでの結合、の4つのみ。

from __future__ import annotations

import json
import os
from typing import Optional

import numpy as np

import er003_b1_p3t_audio as p3t

ARTICLE_ID = "A01"

EXISTING_JA_PATH = "er003_output/b1_p3t/A01/raw/ja_full_sentence.wav"
EXISTING_EN_PATH = "er003_output/b1_p3t/A01/raw/en_shot_on_target.wav"

SOURCE_JAPANESE_FULL_SENTENCE = p3t.SOURCE_JAPANESE_FULL_SENTENCE
SOURCE_ENGLISH_KEYWORD = p3t.SOURCE_ENGLISH_KEYWORD  # "shot on target"

# P3S/P3T(0.2秒)とは異なる、本ステージ専用の固定境界ポーズ値。
# 今回はこの1値のみ検証し、複数候補の比較は行わない。
BOUNDARY_PAUSE_SECONDS = 0.12

# 英語Key Phrase前後の無音トリム時に残す安全マージン(指示section 7の
# 50-100ms範囲内の固定値)。
EN_TRIM_SAFETY_MARGIN_SECONDS = 0.08

_SPEECH_WINDOW_MS = 20.0
_SPEECH_SILENCE_RMS_THRESHOLD = 0.02

# 「シュート」を構成する文字列。Azure STTの単語配列内で「を」の直前に
# この並びが連続して見つかることを、境界特定の根拠とする。
_SHUUTO_CHARS = ("シ", "ュ", "ー", "ト")
_WO_CHAR = "を"


def get_word_timestamps_via_azure_stt(wav_path: str, language: str = "ja-JP") -> tuple[Optional[list[dict]], Optional[str]]:
    """既存の音声ファイルに対してAzure Speech-to-Text(単語レベルタイム
    スタンプ付き)を実行する。新しいTTS呼び出しではなく、既存音声の
    解析のみを行う。戻り値は(words, error)で、失敗時はwordsがNoneに
    なりerrorに理由が入る。"""
    if not os.path.exists(wav_path):
        return None, f"音声ファイルが見つかりません: {wav_path}"

    try:
        from dotenv import load_dotenv
        import azure.cognitiveservices.speech as speechsdk
    except ImportError as exc:
        return None, f"Azure Speech SDKの読み込みに失敗しました: {exc}"

    load_dotenv()
    speech_key = os.getenv("SPEECH_KEY")
    speech_region = os.getenv("SPEECH_REGION")
    if not speech_key or not speech_region:
        return None, "SPEECH_KEY/SPEECH_REGIONが.envに設定されていません"

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language = language
    speech_config.output_format = speechsdk.OutputFormat.Detailed
    speech_config.request_word_level_timestamps()
    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    result = recognizer.recognize_once()

    if result.reason != speechsdk.ResultReason.RecognizedSpeech:
        return None, f"Azure STTが音声を認識できませんでした(reason={result.reason})"

    raw_json = result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
    if not raw_json:
        return None, "Azure STTの詳細JSON結果が取得できませんでした"

    data = json.loads(raw_json)
    nbest = data.get("NBest")
    if not nbest:
        return None, "Azure STT結果にNBestが含まれていません"

    words_raw = nbest[0].get("Words")
    if not words_raw:
        return None, "Azure STT結果に単語レベルタイムスタンプが含まれていません"

    words = []
    for w in words_raw:
        offset = w["Offset"]
        duration = w["Duration"]
        words.append({
            "word": w["Word"],
            "start_seconds": offset / 10_000_000,
            "end_seconds": (offset + duration) / 10_000_000,
            "confidence": w.get("Confidence"),
        })
    return words, None


def find_keyword_boundary(words: list[dict]) -> tuple[Optional[dict], Optional[str]]:
    """Azure STTの単語タイムスタンプ列から、「枠内シュート」の末尾と
    「を記録できないまま」の先頭の境界を特定する。無音長は一切使わず、
    文字列としての「シ→ュ→ー→ト→を」の連続一致のみを根拠にする。
    「を」が原稿内にちょうど1回しか出現しないこと、かつその直前に
    「シュート」が連続して現れることを条件とし、満たさない場合は
    (None, 理由)を返して呼び出し側で停止させる。"""
    wo_indices = [i for i, w in enumerate(words) if w["word"] == _WO_CHAR]
    if len(wo_indices) != 1:
        return None, f"「を」の出現数が1ではありません(検出数: {len(wo_indices)})"
    wo_idx = wo_indices[0]

    n = len(_SHUUTO_CHARS)
    if wo_idx < n:
        return None, "「を」の直前に「シュート」4文字分の単語が存在しません"

    for offset, expected_char in enumerate(reversed(_SHUUTO_CHARS)):
        pos = wo_idx - 1 - offset
        if words[pos]["word"] != expected_char:
            return None, (
                f"「シュート」の文字列が単語列内で連続して見つかりません"
                f"(位置{pos}: 期待='{expected_char}', 実際='{words[pos]['word']}')"
            )

    shi_idx = wo_idx - n
    to_idx = wo_idx - 1  # 「ト」(シュートの末尾)
    wo_word = words[wo_idx]
    to_word = words[to_idx]
    shi_word = words[shi_idx]

    shuuto_end_seconds = to_word["end_seconds"]
    wo_start_seconds = wo_word["start_seconds"]
    gap_seconds = wo_start_seconds - shuuto_end_seconds
    boundary_seconds = (shuuto_end_seconds + wo_start_seconds) / 2.0

    return {
        "shuuto_start_seconds": shi_word["start_seconds"],
        "shuuto_end_seconds": shuuto_end_seconds,
        "wo_start_seconds": wo_start_seconds,
        "gap_seconds": round(gap_seconds, 4),
        "boundary_seconds": round(boundary_seconds, 4),
        "to_confidence": to_word["confidence"],
        "wo_confidence": wo_word["confidence"],
    }, None


def find_speech_bounds(
    samples: "np.ndarray",
    sample_rate: int,
    window_ms: float = _SPEECH_WINDOW_MS,
    silence_rms_threshold: float = _SPEECH_SILENCE_RMS_THRESHOLD,
) -> Optional[tuple[int, int]]:
    """samples内の先頭・末尾の無音を除いた、実際の発話区間(サンプル
    位置)を返す。無音のみで発話が全く検出できない場合はNoneを返す。"""
    window_size = max(1, int(sample_rate * window_ms / 1000))
    n = len(samples)

    def _rms(chunk: "np.ndarray") -> float:
        if len(chunk) == 0:
            return 1.0
        return float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2)))

    speech_start = None
    for pos in range(0, n, window_size):
        chunk = samples[pos:pos + window_size]
        if _rms(chunk) > silence_rms_threshold:
            speech_start = pos
            break
    if speech_start is None:
        return None

    speech_end = None
    for pos in range(n - window_size, -window_size, -window_size):
        start = max(0, pos)
        chunk = samples[start:start + window_size]
        if _rms(chunk) > silence_rms_threshold:
            speech_end = start + len(chunk)
            break
    if speech_end is None:
        return None

    return speech_start, speech_end


def trim_english_keyword_silence(
    samples: "np.ndarray",
    sample_rate: int,
    safety_margin_seconds: float = EN_TRIM_SAFETY_MARGIN_SECONDS,
) -> tuple[Optional["np.ndarray"], Optional[dict]]:
    """英語Key Phrase音声の前後の余分な無音をトリムする。実際の発話を
    絶対に削らないよう、発話区間の前後にsafety_margin_secondsの安全
    マージンを残す。発話区間が検出できない場合は(None, None)を返す。"""
    bounds = find_speech_bounds(samples, sample_rate)
    if bounds is None:
        return None, None
    speech_start, speech_end = bounds

    margin_samples = int(round(safety_margin_seconds * sample_rate))
    trim_start = max(0, speech_start - margin_samples)
    trim_end = min(len(samples), speech_end + margin_samples)
    trimmed = samples[trim_start:trim_end]

    info = {
        "raw_duration_seconds": round(len(samples) / sample_rate, 4),
        "raw_leading_silence_seconds": round(speech_start / sample_rate, 4),
        "raw_trailing_silence_seconds": round((len(samples) - speech_end) / sample_rate, 4),
        "trimmed_duration_seconds": round(len(trimmed) / sample_rate, 4),
        "leading_margin_retained_seconds": round((speech_start - trim_start) / sample_rate, 4),
        "trailing_margin_retained_seconds": round((trim_end - speech_end) / sample_rate, 4),
    }
    return trimmed, info


def split_japanese_at_boundary(
    ja_samples: "np.ndarray",
    sample_rate: int,
    boundary_seconds: float,
) -> tuple["np.ndarray", "np.ndarray"]:
    """ja_samplesを、alignmentで特定した境界時刻(単一の切断点)で
    2つに分割する。無音区間の探索は行わない(境界時刻をそのまま
    サンプル位置へ変換して切断するのみ)。"""
    boundary_sample = int(round(boundary_seconds * sample_rate))
    boundary_sample = max(0, min(len(ja_samples), boundary_sample))
    return ja_samples[:boundary_sample], ja_samples[boundary_sample:]


def join_with_boundary_pauses(
    ja_before: "np.ndarray",
    en_trimmed: "np.ndarray",
    ja_after: "np.ndarray",
    sample_rate: int,
    boundary_pause_seconds: float = BOUNDARY_PAUSE_SECONDS,
) -> "np.ndarray":
    """日本語(前)→0.12秒無音→トリム済み英語Key Phrase→0.12秒無音→
    日本語(後)の順で結合する。"""
    pause = np.zeros(int(round(sample_rate * boundary_pause_seconds)), dtype=ja_before.dtype)
    return np.concatenate([ja_before, pause, en_trimmed, pause, ja_after])
