# ============================================================
# er006_secondary_asr_01.py
# ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01: Secondary ASR + Phrase List
# ============================================================
# Primary ASR(OpenAI gpt-4o-mini-transcribe、既存のer006_asr_provider_
# routing_01.py)がFAIL/UNCERTAINを返したsegmentだけを対象に、Azure
# Speech STTをSecondaryとして呼ぶ。Azure呼び出し時、Pronunciation
# Ledgerに登録済みの固有名詞をPhrase Listとして渡せるようにする
# (canonical spellingをヒントとして渡すだけで、それ以外は変更しない)。
#
# 既存の本番Azure呼び出し(er003_b1_p4_audio.get_full_text_via_azure_
# stt_continuous)は変更しない。本モジュールはPhrase List対応の新規
# 関数を追加するのみ(最小Blast Radius)。

from __future__ import annotations

import os
import time
import wave
from typing import Optional

import er005_cost_logger as cl


def _wav_duration_seconds(wav_path: str) -> Optional[float]:
    try:
        with wave.open(wav_path, "rb") as wf:
            return round(wf.getnframes() / float(wf.getframerate()), 3)
    except Exception:
        return None


def get_full_text_via_azure_stt_with_phrase_list(
    wav_path: str, language: str = "en-US", phrases: Optional[list[str]] = None,
    timeout_seconds: float = 90.0,
) -> tuple[str | None, str | None]:
    """er003_b1_p4_audio.get_full_text_via_azure_stt_continuous()と同じ
    連続認識方式に、Azure PhraseListGrammarを追加したもの。phrasesに
    Pronunciation LedgerのcanonicaL spellingを渡すと、Azureがその語を
    認識しやすくなる(重み付けのみ、認識結果を強制はしない)。"""
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
    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    if phrases:
        phrase_list = speechsdk.PhraseListGrammar.from_recognizer(recognizer)
        for phrase in phrases:
            phrase_list.addPhrase(phrase)

    segments = []
    done = {"flag": False, "reason": None}

    def on_recognized(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            segments.append(evt.result.text)

    def on_stopped(evt):
        done["flag"] = True
        done["reason"] = str(evt)

    recognizer.recognized.connect(on_recognized)
    recognizer.session_stopped.connect(on_stopped)
    recognizer.canceled.connect(on_stopped)

    t0 = time.time()
    recognizer.start_continuous_recognition()
    start = time.time()
    while not done["flag"] and (time.time() - start) < timeout_seconds:
        time.sleep(0.5)
    recognizer.stop_continuous_recognition()
    elapsed = round(time.time() - t0, 3)
    duration = _wav_duration_seconds(wav_path)

    if not done["flag"]:
        cl.record({
            "provider": "azure", "api": "get_full_text_via_azure_stt_with_phrase_list",
            "model_id": "azure-speech-stt", "locale": language, "attempt_number": 1,
            "success": False, "elapsed_seconds": elapsed, "usage_source": "LOCAL_WAV_HEADER_EXACT",
            "audio_duration_submitted_seconds": duration, "phrase_list_size": len(phrases or []),
        })
        return None, f"連続認識がtimeout({timeout_seconds}秒)内に完了しませんでした"

    cl.record({
        "provider": "azure", "api": "get_full_text_via_azure_stt_with_phrase_list",
        "model_id": "azure-speech-stt", "locale": language, "attempt_number": 1,
        "success": True, "elapsed_seconds": elapsed, "usage_source": "LOCAL_WAV_HEADER_EXACT",
        "audio_duration_submitted_seconds": duration, "phrase_list_size": len(phrases or []),
    })
    return "".join(segments), None


# ============================================================
# Retry Architecture: Primary(OpenAI mini) -> Secondary(Azure+Phrase
# List) -> それでも不一致の場合のみTTS retry候補
# ============================================================
import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val

FEATURE_FLAG_SECONDARY_ASR_ENABLED = False  # Production defaultはOFF(タスク仕様§18)


def evaluate_with_secondary_cascade(
    canonical_text: str, wav_path: str, language: str = "en-US",
    ledger_phrases: Optional[list[str]] = None, prior_results: Optional[list] = None,
    secondary_enabled: bool = FEATURE_FLAG_SECONDARY_ASR_ENABLED,
) -> dict:
    """§12-13のRetry Architectureを実装する。
    1. Primary(OpenAI mini経由のrouting.transcribe)を実行
    2. PASS/NORMALIZED_MATCHなら即終了
    3. UNCERTAIN/MISMATCHならSecondary(Azure+Phrase List)を実行
       (secondary_enabled=Falseならここで打ち切り、Primary結果のみ返す)
    4. 両者が同じ内容差を示す場合のみretry_recommended=True
       (どちらか一方だけの不一致では原則retryしない、固有名詞だけの
       表記差はASR_UNCERTAIN/Human Reviewへ)
    """
    prior_results = prior_results if prior_results is not None else []

    primary_text, primary_err = routing.transcribe(wav_path, language=language)
    primary_cls = val.classify_asr_match(canonical_text, primary_text) if primary_text is not None else None

    result = {
        "primary": {"provider": "openai_asr", "text": primary_text, "error": primary_err,
                     "classification": primary_cls.classification if primary_cls else "TTS_FAILURE"},
        "secondary": None,
        "final_status": None,
        "retry_recommended": False,
        "reason": "",
    }

    if primary_cls is not None and primary_cls.should_pass:
        result["final_status"] = primary_cls.classification
        result["reason"] = "Primary ASRでPASS、Secondaryは呼ばない"
        return result

    if not secondary_enabled:
        result["final_status"] = primary_cls.classification if primary_cls else "TTS_FAILURE"
        result["retry_recommended"] = primary_cls.should_retry if primary_cls else True
        result["reason"] = "Secondary ASR機能フラグOFFのため、Primary結果のみで判定(既存の単一ASR retry方針を維持)"
        return result

    # Secondaryを実行(Phrase List付き、Ledger登録語のcanonical spellingを渡す)
    import er003_b1_p4_audio as p4
    lang_secondary = language if language.startswith("en") else language  # 同じlanguageで呼ぶ
    secondary_text, secondary_err = get_full_text_via_azure_stt_with_phrase_list(
        wav_path, language=lang_secondary, phrases=ledger_phrases)
    secondary_cls = val.classify_asr_match(canonical_text, secondary_text) if secondary_text is not None else None
    result["secondary"] = {"provider": "azure", "text": secondary_text, "error": secondary_err,
                             "classification": secondary_cls.classification if secondary_cls else "TTS_FAILURE",
                             "phrase_list_used": bool(ledger_phrases)}

    if secondary_cls is not None and secondary_cls.should_pass:
        result["final_status"] = secondary_cls.classification
        result["reason"] = "PrimaryはFAIL/UNCERTAINだったが、Secondary(Azure)でPASS"
        return result

    # 両方ともPASSしなかった場合: 同じ内容差(同じsignature)かどうかで判断
    primary_sig = val.signature(canonical_text, primary_text) if primary_text else None
    secondary_sig = val.signature(canonical_text, secondary_text) if secondary_text else None
    same_signature = primary_sig is not None and primary_sig == secondary_sig

    if same_signature and primary_cls.classification == "TRUE_CONTENT_MISMATCH":
        result["final_status"] = "TRUE_CONTENT_MISMATCH"
        result["retry_recommended"] = True
        result["reason"] = "両ASRが同じ内容差を一貫して示しており、TTS自体の発話が疑わしいためretry候補"
    else:
        result["final_status"] = "ASR_VALIDATION_UNCERTAIN"
        result["retry_recommended"] = False
        result["reason"] = ("両ASRの結果が一致しない、または固有名詞のtransliteration差にとどまるため、"
                             "TTS再生成はせずHuman Review対象とする")
    return result
