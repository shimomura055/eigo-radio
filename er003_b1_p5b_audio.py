# ============================================================
# er003_b1_p5b_audio.py
# ER-003-B1-P5B: Google Cloud TTS／Amazon Polly比較検証
# ============================================================
# P5AではAzure Speech(ja-JP-NanamiNeural)のみ実行できた。本ステージでは
# Google Cloud Text-to-SpeechとAmazon Polly Neuralの利用可否を、実際の
# APIクライアント呼び出し(読み取り専用、課金の生じない操作)で確認する。
# いずれの認証情報も本実行環境には一切存在しないため(後述)、音声合成
# 呼び出し自体は実行していない。合成用コードは、実際の応答形式(特に
# Google Cloud TTSのLINEAR16レスポンスにWAVヘッダーが含まれるか等)を
# 実機で検証していない状態で書くと、この project 全体の「常に実証済みの
# 事実にのみ基づく」という方針に反するため、認証情報が用意された時点で
# 実装・検証する。
#
# 再利用するもの(再実装しない):
#   - er003_b1_p5a_audio.load_p4d_input/load_p4d_marked_text/
#     asr_reading_normalize
#   - er003_b1_p4d_audio.check_full_text_content
#   - er003_b1_p4_audio.get_full_text_via_azure_stt_continuous
#   - er002_common.SAMPLE_RATE/measure_metrics/read_wav_float

from __future__ import annotations

import er003_b1_p5a_audio as p5a

ARTICLE_ID = "A01"

GOOGLE_VOICE_NAME = "ja-JP-Neural2-B"
GOOGLE_LANGUAGE_CODE = "ja-JP"

AWS_POLLY_VOICE_ID = "Kazuha"
AWS_POLLY_ENGINE = "neural"
AWS_POLLY_LANGUAGE_CODE = "ja-JP"
AWS_POLLY_DEFAULT_REGION = "ap-northeast-1"

# P5Aの5対象句に、Azure Speechが不合格となった「なにがおきる」を追加。
TARGET_PHRASES = p5a.TARGET_PHRASES + ("なにがおきる",)

_NANI_GA_OKIRU_CORRECT = "なにがおきる"
_NANI_GA_OKIRU_WRONG = "なんがおきる"


def check_google_cloud_tts_availability(voice_name: str = GOOGLE_VOICE_NAME, language_code: str = GOOGLE_LANGUAGE_CODE) -> dict:
    """Google Cloud TTSクライアントの実利用可否を、読み取り専用の
    list_voices呼び出し(音声合成は行わず課金は生じない)で確認する。
    パッケージ未インストール・認証情報なしのいずれも、実際の例外を
    捕捉して報告する(推測しない)。"""
    try:
        from google.cloud import texttospeech
    except ImportError as e:
        return {
            "available": False, "package_installed": False,
            "error_type": "ImportError", "error_message": str(e),
            "reason": "google-cloud-texttospeechパッケージが未インストールです。`pip install google-cloud-texttospeech`が必要です。",
        }

    try:
        client = texttospeech.TextToSpeechClient()
        response = client.list_voices(language_code=language_code)
        voice_names = [v.name for v in response.voices]
        return {
            "available": True, "package_installed": True,
            "voice_requested": voice_name, "voice_available": voice_name in voice_names,
            "available_voices_for_language": voice_names,
        }
    except Exception as e:
        return {
            "available": False, "package_installed": True,
            "error_type": type(e).__name__, "error_message": str(e),
            "reason": (
                "Application Default Credentials(ADC)が見つかりません。利用するには、"
                "(1) GCPサービスアカウントキー(JSON)を発行し環境変数GOOGLE_APPLICATION_CREDENTIALSに"
                "そのファイルパスを設定する、または(2) `gcloud auth application-default login`でADCを"
                "設定する、(3) 対象GCPプロジェクトでCloud Text-to-Speech APIを有効化する、のいずれかが必要です。"
            ),
        }


def check_aws_polly_availability(voice_id: str = AWS_POLLY_VOICE_ID, region_name: str = AWS_POLLY_DEFAULT_REGION) -> dict:
    """Amazon Pollyクライアントの実利用可否を、読み取り専用のdescribe_voices
    呼び出し(音声合成は行わない)で確認する。"""
    try:
        import boto3
    except ImportError as e:
        return {
            "available": False, "package_installed": False,
            "error_type": "ImportError", "error_message": str(e),
            "reason": "boto3パッケージが未インストールです。`pip install boto3`が必要です。",
        }

    try:
        client = boto3.client("polly", region_name=region_name)
        response = client.describe_voices(LanguageCode=AWS_POLLY_LANGUAGE_CODE)
        voice_ids = [v["Id"] for v in response["Voices"]]
        return {
            "available": True, "package_installed": True,
            "voice_requested": voice_id, "voice_available": voice_id in voice_ids,
            "available_voices_for_language": voice_ids, "region": region_name,
        }
    except Exception as e:
        return {
            "available": False, "package_installed": True,
            "error_type": type(e).__name__, "error_message": str(e),
            "reason": (
                "AWS認証情報が見つかりません。利用するには、(1) AWS IAMユーザー(または既存ロール)を用意し、"
                "polly:SynthesizeSpeech(および利用可否確認用のpolly:DescribeVoices)権限を付与する、"
                "(2) アクセスキーを発行して環境変数AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEYへ設定する"
                "(または~/.aws/credentialsにprofileを設定する)、(3) Kazuha(neural engine)が利用可能な"
                "リージョン(例: ap-northeast-1)を指定する、のいずれも必要です。"
            ),
        }


def check_nani_ga_okiru(hiragana_normalized_text: str) -> dict:
    """指示section8で明示された「なにがおきる」/「なんがおきる」の
    どちらとして認識されたかを記録する(Azure Speechの不合格理由の
    再発有無を確認するための専用チェック)。"""
    return {
        "correct_present": _NANI_GA_OKIRU_CORRECT in hiragana_normalized_text,
        "wrong_present": _NANI_GA_OKIRU_WRONG in hiragana_normalized_text,
    }


def check_target_phrases(hiragana_normalized_text: str) -> dict:
    return {phrase: (phrase in hiragana_normalized_text) for phrase in TARGET_PHRASES}
