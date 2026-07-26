# ============================================================
# er003_b1_p5a_audio.py
# ER-003-B1-P5A: 日本語TTS原稿忠実性スクリーニング
# ============================================================
# ER-003-B1-P4D-AUDITで、Gemini TTSが完全な入力の一部を音声生成段階で
# 省略していたことが確認された(前処理には欠落なし)。本ステージでは
# Gemini TTSへの局所修正は行わず、P4Dで実際に使用したのと完全に同一の
# 全文ひらがな入力を、複数の日本語TTSエンジンで生成し、原稿忠実性
# (省略・追加がないか)を比較する。第一評価軸は自然さではなく忠実性。
#
# 再利用するもの(再実装しない):
#   - er003_b1_p4d_audio.sudachi_tokenize/build_reading_map/
#     build_full_hiragana_script/check_full_text_content/MARKER_HIRAGANA
#   - er003_b1_p4_audio.get_full_text_via_azure_stt_continuous/
#     _strip_punctuation
#   - er002_common.SAMPLE_RATE/pcm_to_wav_bytes/read_wav_float/
#     write_wav_float/measure_metrics/_call_tts_with_retry
#
# 新規に追加するのは、(1) 3候補TTSエンジンの利用可否判定、(2) Azure
# Speech用tts_call_fn(このプロジェクトでAzure Speechを「生成」に使う
# のは初めてのため)、(3) 5つの対象句のASR診断チェック、の3つのみ。

from __future__ import annotations

import hashlib
import os

import er003_b1_p4_audio as p4
import er003_b1_p4d_audio as p4d

ARTICLE_ID = "A01"

# P4Dが実際にTTSへ渡した入力そのもの(変更禁止、指示section4)。
P4D_HIRAGANA_SCRIPT_PATH = "er003_output/b1_p4d/A01/source/pattern_a_full_hiragana.txt"
P4D_MARKED_TEXT_PATH = "er003_output/b1_p4d/A01/source/pattern_a_with_markers.txt"
# P4D完了時にsource_hashes.jsonへ記録済みの値(P4D audio_metadata.jsonと
# 一致することを確認済み)。ここに再掲し、読み込み時の改変検知に使う。
P4D_EXPECTED_HIRAGANA_SHA256 = "fb9ea8c9ef6740fd83fe905199d987609b2eba9e8ec79b6c3437dee17493bd5b"

MAX_TTS_TECHNICAL_RETRY = 1

AZURE_VOICE_NAME = "ja-JP-NanamiNeural"
GOOGLE_CLOUD_VOICE_NAME = "ja-JP-Neural2-B"
AMAZON_POLLY_VOICE_NAME = "Kazuha"

# 指示section7で明示された5つの対象句(全文ひらがな読み正規化後の
# 表記)。P4D-AUDITで欠落が確認された箇所を含む。
TARGET_PHRASES = (
    "せんしゅをこうたいでさげる",
    "めじるしというけつだんで",
    "しゅびをかため",
    "わずかなりーど",
    "さいごのすうふん",
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_p4d_input(
    hiragana_path: str = P4D_HIRAGANA_SCRIPT_PATH,
    expected_sha256: str = P4D_EXPECTED_HIRAGANA_SHA256,
) -> dict:
    """P4Dが実際に使用した全文ひらがなscriptを、変更せず読み込む。
    P4D完了時に記録済みのsha256と一致しない場合は例外を送出する
    (指示section4の「入力ファイルを変更しない」を機械的に保証する)。"""
    if not os.path.exists(hiragana_path):
        raise FileNotFoundError(f"P4D入力ファイルが見つかりません: {hiragana_path}")
    with open(hiragana_path, encoding="utf-8") as f:
        text = f.read()
    actual_sha256 = _sha256_text(text)
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"P4D入力ファイルのsha256が記録値と一致しません(改変の可能性): "
            f"expected={expected_sha256}, actual={actual_sha256}"
        )
    return {"text": text, "path": hiragana_path, "sha256": actual_sha256}


def load_p4d_marked_text(path: str = P4D_MARKED_TEXT_PATH) -> str:
    """ASR類似度比較の基準として、P4Dのmarker置換後(ひらがな化前)
    原文を読み込む(p4d.check_full_text_contentの比較対象と同じ役割)。"""
    with open(path, encoding="utf-8") as f:
        return f.read()


def check_engine_availability() -> dict:
    """3候補TTSエンジンの利用可否を判定する。認証情報の取得・パッケージ
    の新規インストールは行わず、現状で利用可能かどうかのみを報告する
    (指示section3: 利用できない候補を勝手な代替へ差し替えない)。"""
    from dotenv import load_dotenv
    load_dotenv()

    results = {}

    try:
        import google.cloud.texttospeech  # noqa: F401
        google_pkg_available = True
    except ImportError:
        google_pkg_available = False
    google_creds_present = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    results["google_cloud_tts"] = {
        "available": google_pkg_available and google_creds_present,
        "package_installed": google_pkg_available,
        "credentials_present": google_creds_present,
        "reason": None if (google_pkg_available and google_creds_present) else (
            "google-cloud-texttospeechパッケージが未インストール、かつGOOGLE_APPLICATION_CREDENTIALSが.envに未設定です。"
            "利用するには、(1) `pip install google-cloud-texttospeech`、(2) GCPサービスアカウントキー(JSON)の発行と"
            "GOOGLE_APPLICATION_CREDENTIALSへのパス設定、(3) Text-to-Speech APIの有効化が必要です。"
        ),
    }

    try:
        import azure.cognitiveservices.speech  # noqa: F401
        azure_pkg_available = True
    except ImportError:
        azure_pkg_available = False
    azure_creds_present = bool(os.getenv("SPEECH_KEY")) and bool(os.getenv("SPEECH_REGION"))
    results["azure_speech"] = {
        "available": azure_pkg_available and azure_creds_present,
        "package_installed": azure_pkg_available,
        "credentials_present": azure_creds_present,
        "reason": None if (azure_pkg_available and azure_creds_present) else "azure-cognitiveservices-speech未インストール、またはSPEECH_KEY/SPEECH_REGION未設定です。",
    }

    try:
        import boto3  # noqa: F401
        boto3_available = True
    except ImportError:
        boto3_available = False
    aws_creds_present = bool(os.getenv("AWS_ACCESS_KEY_ID")) and bool(os.getenv("AWS_SECRET_ACCESS_KEY"))
    results["amazon_polly"] = {
        "available": boto3_available and aws_creds_present,
        "package_installed": boto3_available,
        "credentials_present": aws_creds_present,
        "reason": None if (boto3_available and aws_creds_present) else (
            "boto3パッケージが未インストール、かつAWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEYが.envに未設定です。"
            "利用するには、(1) `pip install boto3`、(2) AWS IAMユーザーの発行とアクセスキー設定、"
            "(3) Amazon Polly(neural engine, Kazuha voice対応リージョン)への権限付与が必要です。"
        ),
    }

    return results


def make_azure_tts_call_fn(voice_name: str = AZURE_VOICE_NAME):
    """tts_call_fn(text)->bytes(生PCM、24kHz/16bit/mono)を返す。
    common._call_tts_with_retryへそのまま渡せるよう、Gemini用tts_call_fn
    (er002_gemini_client.make_tts_call_fn)と同一のインターフェースにする。
    SSML・スタイル指定は使わず、plain textをそのまま合成する
    (指示section5: SSMLによる発音修正・スタイル指定は行わない)。"""
    from dotenv import load_dotenv
    import azure.cognitiveservices.speech as speechsdk

    load_dotenv()
    speech_key = os.getenv("SPEECH_KEY")
    speech_region = os.getenv("SPEECH_REGION")

    def tts_call_fn(text: str) -> bytes:
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        speech_config.speech_synthesis_voice_name = voice_name
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Raw24Khz16BitMonoPcm)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            raise RuntimeError(f"Azure Speech合成が中断されました: {cancellation.reason}, {cancellation.error_details}")
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            raise RuntimeError(f"Azure Speech合成が失敗しました: {result.reason}")
        if not result.audio_data:
            raise RuntimeError("Azure Speech合成結果が空でした")

        tts_call_fn.last_result_metadata = {
            "result_id": result.result_id,
            "reason": str(result.reason),
            "audio_duration_reported": str(result.audio_duration),
            "voice_name": voice_name,
        }
        return result.audio_data

    tts_call_fn.last_result_metadata = None
    return tts_call_fn


def check_target_phrases(hiragana_normalized_text: str) -> dict:
    """指示section7の5対象句が、読み正規化後のASRテキストに含まれるかを
    確認する(境界決定・合否確定には使わず、診断情報として扱う)。"""
    return {phrase: (phrase in hiragana_normalized_text) for phrase in TARGET_PHRASES}


def asr_reading_normalize(recognized_text: str, work_dir: str) -> str:
    """P4Dで確立済みの読み正規化処理(sudachi tokenize→ひらがな化)を、
    ASR認識結果にもそのまま適用する(P4Dのasr_reading_normalizedと同じ
    設計。単一の類似度スコアだけに頼らず、対象句を直接照合するため)。"""
    morphemes = p4d.sudachi_tokenize(recognized_text, work_dir=work_dir)
    reading_map = p4d.build_reading_map(morphemes)
    return p4d.build_full_hiragana_script(reading_map)
