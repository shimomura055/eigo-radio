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
NOTIFICATION2_WAV_PATH = "C:/Users/tensh/sound/notification2.wav"

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
# 2026-08-07 修正版(v2)で変更・追加された原稿
# ------------------------------------------------------------
PODCAST_NAME_TEXT_V2 = "Welcome to English Your Way."
TOPIC_INTRO_TEXT_V2 = f"Today's topic is {ENGLISH_TITLE_TEXT}."
POINT_EXPLANATION_TEXT = "ポイント解説"
KEY_PHRASES_INTRO_TEXT = "Here are today's key phrases."
NUMBER_WORDS = ("One.", "Two.", "Three.", "Four.", "Five.")

# 日本語のみPreview(英語Key Phraseを含まない、既存Preview原稿から
# 英語挿入部分を除いた自然な日本語の流れ)。既存の日本語のみPreview
# 音声はこのプロジェクトのどこにも存在しなかったため新規作成した
# (調査結果はER-003-B1-P9A-R1報告書参照)。
JAPANESE_ONLY_PREVIEW_TEXT = (
    "前半は激しい接触と緊張が続き、両チームとも枠内シュートを記録できないまま、"
    "静かな均衡が保たれます。後半に試合が動くと、イングランドは選手を交代で下げる"
    "という決断で守備を固め、わずかなリードを守ろうとします。アルゼンチンの決勝への"
    "道を閉ざすことが現実になりそうなその時、メッシが流れを変え、ついにアディショナル"
    "タイムへ。最後の数分、歓喜と痛みの境目で何が起きるのでしょうか。"
)

# 5つのKey Phrase(番号→英語→日本語→英語)。英語音声は既存のP7C
# Componentをそのまま再利用する(新規TTSなし)。日本語は意味の要約
# (Pattern A本文で既に使われている表現と同一、新規の訳語は作らない)。
KEY_PHRASES = (
    {"number": "One", "english": "shot on target", "japanese": "枠内シュート",
     "english_component_path": "er003_output/b1_p3u/A01/components/en_shot_on_target_trimmed.wav"},
    {"number": "Two", "english": "take players off", "japanese": "選手を交代で下げる",
     "english_component_path": "er003_output/b1_p4c/A01/preview/en_components/02_take_a_player_off.wav"},
    {"number": "Three", "english": "a narrow lead", "japanese": "わずかなリード",
     "english_component_path": "er003_output/b1_p4c/A01/preview/en_components/03_narrow_lead.wav"},
    {"number": "Four", "english": "close the door to the final", "japanese": "決勝への道を閉ざす",
     "english_component_path": "er003_output/b1_p7c/A01/components/new_close_the_door_to_the_final.wav"},
    {"number": "Five", "english": "stoppage time", "japanese": "アディショナルタイム",
     "english_component_path": "er003_output/b1_p4c/A01/preview/en_components/05_stoppage_time.wav"},
)

# Key Phrasesセクション専用のポーズ(指示section6、Preview/本文より短め、
# ただし区切りが明確に聞き取れる程度)。
KEY_PHRASE_INTERNAL_PAUSE_SECONDS = 0.4  # 番号→英語→日本語→英語、各区切り
KEY_PHRASE_BLOCK_END_PAUSE_SECONDS = 0.8  # 各キーフレーズの最後(2回目の英語)の後

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
# ASR検証付き生成(2026-08-07: "Now, the full story."/"ポイント解説"で
# 実際に発生した、TTSが指定テキストと無関係な内容を返す現象への対策。
# 生成のたびにASRで内容を確認し、一致するまで再試行する。RMS/波形の
# 診断とは別に、内容そのものの検証として使う)。
# ============================================================
def generate_narration_snippet_verified(text: str, language: str, out_path: str,
                                         expected_substring: str, max_attempts: int = 6) -> dict:
    import er003_b1_p4_audio as p4
    asr_language = "en-US" if language == "en" else "ja-JP"
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        r = generate_narration_snippet(text, language, out_path)
        if r.get("status") != "OK":
            attempts_log.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason")})
            continue
        asr_text, err = p4.get_full_text_via_azure_stt_continuous(out_path, language=asr_language)
        verified = asr_text is not None and expected_substring.lower() in asr_text.lower()
        attempts_log.append({"attempt": attempt, "status": "OK", "duration_seconds": r["duration_seconds"],
                              "asr_text": asr_text, "verified": verified})
        if verified:
            return {**r, "asr_verified": True, "asr_text": asr_text, "attempts_log": attempts_log}
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log}


# ============================================================
# Full Story冒頭のタイトル除去(MFA境界のみを根拠にする。RMSは使わない)
# ============================================================
def trim_title_from_body(body_samples: "np.ndarray", sample_rate: int, first_word_start_seconds: float,
                          natural_leading_seconds: float) -> dict:
    """本編音声先頭のタイトル部分を、本文第1文の最初の単語の開始時刻
    (MFAで特定済み)を基準に除去する。本文の内容は一切変更しない
    (adjust_leading_silenceのspeech_content_unchangedで保証)。"""
    import er003_b1_p3z_audio as p3z
    speech_start_sample = int(round(first_word_start_seconds * sample_rate))
    trimmed, info = p3z.adjust_leading_silence(body_samples, sample_rate, speech_start_sample, natural_leading_seconds)
    return {"trimmed": trimmed, "info": info}


# ============================================================
# 本編内部の異常に長い無音区間の短縮(MFA境界のみを根拠にする)
# ============================================================
def trim_internal_gap(body_samples: "np.ndarray", sample_rate: int, gap_end_seconds: float,
                       gap_start_seconds: float, target_gap_seconds: float) -> dict:
    """本編音声の途中(先頭・末尾ではない)にある無音区間を、その直前の
    単語の終了時刻(gap_end_seconds)と直後の単語の開始時刻
    (gap_start_seconds、いずれもMFAで特定済み)を基準に、
    target_gap_secondsへ短縮する。前後の発話内容は一切変更しない。"""
    before_end_sample = int(round(gap_end_seconds * sample_rate))
    after_start_sample = int(round(gap_start_seconds * sample_rate))
    before_part = body_samples[:before_end_sample]
    after_part = body_samples[after_start_sample:]
    new_gap = np.zeros(int(round(target_gap_seconds * sample_rate)), dtype=body_samples.dtype)
    trimmed = np.concatenate([before_part, new_gap, after_part])
    original_gap_seconds = gap_start_seconds - gap_end_seconds
    return {
        "trimmed": trimmed,
        "info": {
            "original_gap_seconds": round(original_gap_seconds, 4),
            "target_gap_seconds": target_gap_seconds,
            "before_content_unchanged": bool(np.array_equal(trimmed[:before_end_sample], before_part)),
            "after_content_unchanged": bool(np.array_equal(
                trimmed[before_end_sample + len(new_gap):], after_part)),
        },
    }


# ============================================================
# 外部音源をbody(mono, 24kHz)の音声内部の指定位置へ挿入する
# (MFA境界のみを根拠にする。前後の発話内容は変更しない)
# ============================================================
def load_mono_at_rate(path: str, target_sr: int) -> "np.ndarray":
    """外部音源(mp3/wav)を、bodyと同じmono・sample_rateへ変換して
    読み込む(top-level partsで使うstereo/48kHz変換とは別の、本編内部
    への挿入専用の読み込み経路)。"""
    data, sr = sf.read(path, always_2d=True)
    mono = data.mean(axis=1)
    if sr != target_sr:
        from math import gcd
        g = gcd(sr, target_sr)
        up, down = target_sr // g, sr // g
        mono = resample_poly(mono, up, down)
    return mono


def insert_sound_at_internal_gap(body_samples: "np.ndarray", sample_rate: int, gap_end_seconds: float,
                                  gap_start_seconds: float, sound_samples: "np.ndarray",
                                  pause_before_seconds: float, pause_after_seconds: float) -> dict:
    """本編音声の途中(MFAで特定済みの単語境界の間)に、外部音源
    (sound_samples、既にbodyと同じsample_rate/monoへ変換済みのもの)を
    挿入する。前後の発話内容は一切変更しない。挿入する音源自体の内容・
    長さは変更しない(gainやtrimは行わない、そのまま使う)。"""
    before_end_sample = int(round(gap_end_seconds * sample_rate))
    after_start_sample = int(round(gap_start_seconds * sample_rate))
    before_part = body_samples[:before_end_sample]
    after_part = body_samples[after_start_sample:]
    pause_before = np.zeros(int(round(pause_before_seconds * sample_rate)), dtype=body_samples.dtype)
    pause_after = np.zeros(int(round(pause_after_seconds * sample_rate)), dtype=body_samples.dtype)
    sound = sound_samples.astype(body_samples.dtype)

    result = np.concatenate([before_part, pause_before, sound, pause_after, after_part])
    inserted_len = len(pause_before) + len(sound) + len(pause_after)
    return {
        "result": result,
        "info": {
            "gap_end_seconds": gap_end_seconds, "gap_start_seconds": gap_start_seconds,
            "original_gap_seconds": round(gap_start_seconds - gap_end_seconds, 4),
            "pause_before_seconds": pause_before_seconds, "pause_after_seconds": pause_after_seconds,
            "sound_duration_seconds": round(len(sound) / sample_rate, 4),
            "before_content_unchanged": bool(np.array_equal(result[:before_end_sample], before_part)),
            "after_content_unchanged": bool(np.array_equal(result[before_end_sample + inserted_len:], after_part)),
        },
    }


# ============================================================
# Key Phrasesブロック組み立て(番号→英語→日本語→英語)
# ============================================================
def build_key_phrase_block(number_word_samples: "np.ndarray", english_component_samples: "np.ndarray",
                            japanese_meaning_samples: "np.ndarray", sample_rate: int) -> "np.ndarray":
    """英語Componentは`tight_speech_only`で見かけ上の無音を除去済みの
    ものを渡す想定(1回目・2回目とも同じ音声を再利用する)。入力は
    (n, 2)のstereo配列を想定し、無音もstereo形状で作る。"""
    pause = silence_stereo(KEY_PHRASE_INTERNAL_PAUSE_SECONDS, sample_rate)
    block_end_pause = silence_stereo(KEY_PHRASE_BLOCK_END_PAUSE_SECONDS, sample_rate)
    return np.concatenate([
        number_word_samples, pause,
        english_component_samples, pause,
        japanese_meaning_samples, pause,
        english_component_samples, block_end_pause,
    ])


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
