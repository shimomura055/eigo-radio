# ============================================================
# er003_b1_p9a_audio.py
# ER-003-B1-P9A: 「English Your Way」Podcast完成版組み立て
# ============================================================
# 完成済みのPreview(P7C)・本編(P8A)音声はそのまま再利用し、新規に
# 読み上げ直さない。新規に生成するのは、番組名・記事タイトル(英語+
# 日本語)・セクション案内2件の計5点の短いナレーションのみ。Intro・
# 効果音・Outroは指定された外部mp3をそのまま使用する。
#
# ナレーターは既存プロジェクトの確立済み経路をそのまま再利用する
# (新しいinstruction/styleは作らない)。
#   - 英語の短いナレーション(番組名/英語タイトル/セクション案内2件):
#     `er003_b1_p4c_audio.ENGLISH_STYLE_PREFIX`(=common.build_style_
#     prefix()、英語Key Phrase Componentと同一のinstruction)+Aoede+
#     `gemini-2.5-pro-preview-tts`(英語Component生成で既に採用済みの
#     経路、er002_gemini_client.make_tts_call_fn)
#   - 日本語タイトル: `er003_b1_p7a_audio.JAPANESE_STYLE_PREFIX`(P7A/
#     Previewと同一instruction)+Aoede+`gemini-3.1-flash-tts-preview`
#     (Previewで採用済みのモデル。この新規ナレーションはPreview導入部の
#     一部として聞かれるため、直後に続くPreviewと同じ話者設定に揃える)
#
# 外部音源(Intro/notification/outro、mp3)はsoundfile(libsndfile)で
# デコードし、内容・速度・ピッチを変えないrational resampling
# (scipy.signal.resample_poly)のみで48000Hz/stereoへ統一する。TTSで
# 生成した24000Hz/monoの音声も同じ48000Hz/stereoへ変換して結合する
# (mono->stereoはL=Rの複製のみ、crossfade等の加工はしない)。
#
# 音量差(指示の「共通ルール」)は、区間ごとのスカラーgain調整のみで
# 対応する(ダイナミックレンジ圧縮=Dynamics3は今回一切使わない、
# Preview/本編には触れない)。
#
# 再利用するもの(再実装しない):
#   - er002_common.SAMPLE_RATE/pcm_bytes_to_float_mono/read_wav_float/
#     write_wav_float/measure_metrics/_call_tts_with_retry
#   - er002_gemini_client.make_client
#   - er003_b1_p3u_audio.find_speech_bounds/trim_english_keyword_silence
#   - er003_b1_p4c_audio.ENGLISH_STYLE_PREFIX/VOICE_NAME/
#     MAX_TTS_TECHNICAL_RETRY/build_tts_prompt
#   - er003_b1_p7a_audio.JAPANESE_STYLE_PREFIX/CANDIDATE_MODEL_NAME/
#     sha256_file
#   - er003_b1_p7c_audio.tight_speech_only

from __future__ import annotations

import os

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p7a_audio as p7a
import er003_b1_p7c_audio as p7c

ARTICLE_ID = "A01"
TARGET_SAMPLE_RATE = 48000

# ------------------------------------------------------------
# 固定入力(すでに完成・ユーザー試聴確認中の既存音声。今回は無変更で再利用)
# ------------------------------------------------------------
PREVIEW_PATH = p7c.INPUT_WAV_PATH.replace(
    "b1_p7a/A01/raw/A01_p7a_gemini31_single_call.wav",
    "b1_p7c/A01/A01_p7c_gemini31_english_replaced_dynamics3.wav",
)
BODY_PATH = "er003_output/b1_p8a/A01/body_raw/A01_b1_body_dynamics3.wav"

INTRO_MP3_PATH = "C:/Users/tensh/sound/Intro.mp3"
NOTIFICATION_MP3_PATH = "C:/Users/tensh/sound/notification.mp3"
OUTRO_MP3_PATH = "C:/Users/tensh/sound/outro.mp3"

# ------------------------------------------------------------
# 新規ナレーション原稿(内容は一切変更しない、指示された文言そのまま)
# ------------------------------------------------------------
PODCAST_NAME_TEXT = "English Your Way."
ENGLISH_TITLE_TEXT = "Five Minutes from the Final—Then the Champions Struck"
# 既存承認済み日本語マスター(er003_output/b1_p1/A01/master_ja_approved.md)
# のタイトル行をそのまま使用(指示「既存データにある場合はそのまま使用」)。
JAPANESE_TITLE_TEXT = "あと5分で決勝だった。だが、王者は時計まで味方につけた"
JAPANESE_TITLE_SOURCE_PATH = "er003_output/b1_p1/A01/master_ja_approved.md"
PREVIEW_INTRO_TEXT = "Here's a quick preview."
FULL_STORY_INTRO_TEXT = "Now, the full story."

# ------------------------------------------------------------
# 話者設定(既存経路の再利用。新規style/instructionは作らない)
# ------------------------------------------------------------
VOICE_NAME = p4c.VOICE_NAME  # "Aoede"
ENGLISH_STYLE_PREFIX = p4c.ENGLISH_STYLE_PREFIX
ENGLISH_MODEL_NAME = common.MODEL_NAME  # "gemini-2.5-pro-preview-tts"(英語Component方式)
JAPANESE_STYLE_PREFIX = p7a.JAPANESE_STYLE_PREFIX
JAPANESE_MODEL_NAME = p7a.CANDIDATE_MODEL_NAME  # "gemini-3.1-flash-tts-preview"(Preview方式)
MAX_TTS_TECHNICAL_RETRY = p4c.MAX_TTS_TECHNICAL_RETRY

# ------------------------------------------------------------
# 指定ポーズ(指示の秒数レンジの中央付近で固定値化。全て根拠を報告する)
# ------------------------------------------------------------
PAUSE_AFTER_INTRO_SECONDS = 0.0  # Introの余韻をそのまま使う、追加無音なし
PAUSE_AFTER_PODCAST_NAME_SECONDS = 0.5
PAUSE_BETWEEN_TITLES_SECONDS = 0.65  # 指示レンジ0.5〜0.8秒の中央
PAUSE_AFTER_JAPANESE_TITLE_SECONDS = 0.5
PAUSE_AFTER_NOTIFICATION_SECONDS = 0.4  # 指示レンジ0.3〜0.5秒の中央
PAUSE_AFTER_PREVIEW_INTRO_SECONDS = 0.5
PAUSE_AFTER_PREVIEW_SECONDS = 0.5
PAUSE_AFTER_FULL_STORY_INTRO_SECONDS = 0.7
PAUSE_AFTER_FULL_STORY_SECONDS = 0.5
PAUSE_AFTER_OUTRO_SECONDS = 0.0  # Outroの余韻をそのまま使う、追加無音なし


def sha256_file(path: str) -> str:
    return p7a.sha256_file(path)


# ============================================================
# 外部mp3の読み込み・リサンプリング(内容・速度・ピッチは変えない)
# ============================================================
def load_and_resample_to_target(path: str, target_sr: int = TARGET_SAMPLE_RATE) -> dict:
    data, sr = sf.read(path, always_2d=True)  # shape: (n, channels)
    if sr != target_sr:
        from math import gcd
        g = gcd(sr, target_sr)
        up, down = target_sr // g, sr // g
        resampled = np.stack([resample_poly(data[:, ch], up, down) for ch in range(data.shape[1])], axis=-1)
    else:
        resampled = data
    if resampled.shape[1] == 1:
        resampled = np.repeat(resampled, 2, axis=1)
    return {
        "samples": resampled, "original_sample_rate": sr, "original_channels": data.shape[1],
        "original_duration_seconds": round(len(data) / sr, 4),
        "resampled_duration_seconds": round(len(resampled) / target_sr, 4),
    }


def mono_24k_to_stereo_target(samples_24k_mono: "np.ndarray", target_sr: int = TARGET_SAMPLE_RATE) -> "np.ndarray":
    from math import gcd
    g = gcd(common.SAMPLE_RATE, target_sr)
    up, down = target_sr // g, common.SAMPLE_RATE // g
    resampled = resample_poly(samples_24k_mono, up, down)
    return np.stack([resampled, resampled], axis=-1)


# ============================================================
# 新規ナレーション生成(5点)
# ============================================================
def _make_english_call_fn(client=None):
    return gclient.make_tts_call_fn(VOICE_NAME, client=client)


def _make_japanese_call_fn(client=None):
    return p7a.make_tts_call_fn_for_model(JAPANESE_MODEL_NAME, VOICE_NAME, client=client)


def generate_narration_snippet(text: str, language: str, out_path: str,
                                tts_call_fn=None, sleep_function=None) -> dict:
    """language: 'en' または 'ja'。既存の確立済みinstruction/モデル/voiceを
    そのまま使う(新規styleは作らない)。"""
    if language == "en":
        style_prefix, model_name = ENGLISH_STYLE_PREFIX, ENGLISH_MODEL_NAME
        call_fn = tts_call_fn or _make_english_call_fn()
        prompt = p4c.build_tts_prompt(text, style_prefix)
    elif language == "ja":
        style_prefix, model_name = JAPANESE_STYLE_PREFIX, JAPANESE_MODEL_NAME
        call_fn = tts_call_fn or _make_japanese_call_fn()
        prompt = style_prefix + text
    else:
        raise ValueError(f"unsupported language: {language}")

    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=MAX_TTS_TECHNICAL_RETRY, sleep_fn=sleep_function)
    if not ok:
        return {"status": "STOPPED", "reason": f"ナレーション({text!r})のTTSが失敗: {err}"}

    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(samples_raw, common.SAMPLE_RATE)
    if trimmed is None:
        return {"status": "STOPPED", "reason": f"ナレーション({text!r})に発話区間を検出できませんでした"}

    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
    return {
        "status": "OK", "text": text, "language": language, "path": out_path,
        "model": model_name, "voice": VOICE_NAME, "call_count": 1 + retries, "retry_count": retries,
        "sha256": sha256_file(out_path), "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
        "trim_info": trim_info, "clipping_detected": metrics["clipping_detected"],
    }


# ============================================================
# 音量診断・gain調整(scalar gain。Dynamics3・compressorは使わない)
# ============================================================
def rms(samples: "np.ndarray") -> float:
    return float(np.sqrt(np.mean(samples.astype(np.float64) ** 2))) if len(samples) else 0.0


def peak(samples: "np.ndarray") -> float:
    return float(np.max(np.abs(samples))) if len(samples) else 0.0


def compute_gain_for_target_rms(samples: "np.ndarray", target_rms: float, max_peak: float = 0.95) -> float:
    """samplesのRMSをtarget_rmsへ近づけるスカラーgainを返す。ピークが
    max_peakを超えないよう上限をかける(内容・速度・ピッチは変えない、
    振幅の一律スケーリングのみ)。"""
    current_rms = rms(samples)
    if current_rms <= 1e-9:
        return 1.0
    gain = target_rms / current_rms
    current_peak = peak(samples)
    if current_peak > 0:
        max_gain_for_peak = max_peak / current_peak
        gain = min(gain, max_gain_for_peak)
    return gain


def silence_stereo(seconds: float, sr: int = TARGET_SAMPLE_RATE) -> "np.ndarray":
    return np.zeros((int(round(seconds * sr)), 2), dtype=np.float64)
