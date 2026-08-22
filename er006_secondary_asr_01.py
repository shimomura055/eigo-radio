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

import json
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
# ER-006-AUDIO-RETRY-CASCADE-PROD-01: Production Cascade
# Gemini TTS(1回) -> Primary#1 -> Primary#2 -> Secondary#1(+Phrase List)
# -> Secondary#2(+Phrase List) -> Human Review
# 同一音声に対して複数回ASRだけをやり直す(TTSは再生成しない)。
# ============================================================
import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val

FEATURE_FLAG_SECONDARY_ASR_ENABLED = False  # Production defaultはOFF(タスク仕様§15)

# SSOT: Cascadeの試行回数上限・Phrase List設定(タスク仕様§11-12)
CASCADE_CONFIG = {
    "max_primary_attempts": 2,
    "max_secondary_attempts": 2,
    "phrase_list_weight": None,  # AzureのPhraseListGrammarはper-phrase重み設定APIを
                                  # 現行SDKでは公開していないため、既定(均等)を使う。
                                  # 将来SDKが対応した場合はここへ重み値を設定する。
}

# Cost Guard(タスク仕様§13): 1 segmentあたりの累積コストがこれを超えたら
# Fail-closedでCascadeを打ち切り、Human Reviewへ送る(異常な費用膨張防止)。
COST_GUARD_MAX_USD_PER_SEGMENT = 0.05


def is_entity_like_mismatch(result: "val.ClassificationResult") -> bool:
    """classify_asr_matchの結果が、固有名詞らしき語のみの音訳差による
    ASR_VALIDATION_UNCERTAINかどうかを判定する。数字・否定・通常の内容語
    差は対象外(それらはprotected_checkで既にTRUE_CONTENT_MISMATCHになる
    ため、ここへは到達しない)。"""
    if result.classification != "ASR_VALIDATION_UNCERTAIN":
        return False
    diffs = result.protected.content_word_diffs
    return bool(diffs) and all(d["entity_like"] for d in diffs)


HUMAN_REVIEW_LOG_PATH = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"


def _log_human_review(detail: dict) -> None:
    os.makedirs(os.path.dirname(HUMAN_REVIEW_LOG_PATH), exist_ok=True)
    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "canonical_text": detail["canonical_text"],
        "wav_path": detail["wav_path"],
        "steps": detail["steps"],
        "cost_guard_triggered": detail["cost_guard_triggered"],
        "final_status": detail["final_status"],
    }
    with open(HUMAN_REVIEW_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def evaluate_attempt_with_cascade(
    canonical_text: str, asr_text: Optional[str], prior_results: list,
    wav_path: str, language: str = "en-US", ledger_phrases: Optional[list[str]] = None,
    max_same_signature: int = 3, cascade_enabled: bool = FEATURE_FLAG_SECONDARY_ASR_ENABLED,
) -> tuple[bool, bool, "val.ClassificationResult"]:
    """Production retry loop向けのdrop-in互換ラッパー。val.evaluate_attempt()
    と同じ(verified, stop_retrying, classification)のタプルを返す
    (既存呼び出し元のコードをほぼ変更せずに差し替えられる)。
    Cascadeが起動してHuman Review行きになった場合、詳細(§14の一覧項目)を
    HUMAN_REVIEW_LOG_PATHへ追記する。"""
    detail = evaluate_attempt_with_cascade_detail(
        canonical_text, asr_text, prior_results, wav_path, language=language,
        ledger_phrases=ledger_phrases, max_same_signature=max_same_signature,
        cascade_enabled=cascade_enabled)
    if detail["human_review_required"]:
        _log_human_review(detail)
    return detail["verified"], detail["stop_retrying"], detail["classification"]


def evaluate_attempt_with_cascade_detail(
    canonical_text: str, asr_text: Optional[str], prior_results: list,
    wav_path: str, language: str = "en-US", ledger_phrases: Optional[list[str]] = None,
    max_same_signature: int = 3, cascade_enabled: bool = FEATURE_FLAG_SECONDARY_ASR_ENABLED,
) -> dict:
    """既存のval.evaluate_attempt()(Primary ASR 1回分の判定)をラップし、
    その結果が「固有名詞由来のASR_VALIDATION_UNCERTAIN」であれば、TTSを
    再生成せず同じ音声に対してCascade(Primary#2 -> Secondary#1 ->
    Secondary#2)を追加実行する。cascade_enabled=Falseなら既存のval.
    evaluate_attempt()と完全に同じ挙動(後方互換、Production既定)。

    戻り値のdictには、Human Review用に全stepのtranscriptを保持する
    (canonical_text/TTS audioパス/Primary#1-2/Secondary#1-2の書き起こし)。
    """
    verified, stop_retrying, cls = val.evaluate_attempt(
        canonical_text, asr_text, prior_results, max_same_signature=max_same_signature)

    steps = [{"step": "primary_1", "provider": "openai_asr", "text": asr_text,
              "classification": cls.classification}]
    cumulative_cost_usd = 0.0

    result = {
        "verified": verified, "stop_retrying": stop_retrying, "classification": cls,
        "cascade_invoked": False, "steps": steps, "final_status": cls.classification,
        "human_review_required": False, "canonical_text": canonical_text, "wav_path": wav_path,
        "cost_guard_triggered": False,
    }

    if verified or not cascade_enabled or not is_entity_like_mismatch(cls):
        # 固有名詞由来でない不一致(数字・否定・通常内容語の差等)は、既存の
        # blind TTS retryへ委ねる(Cascadeの対象外、§8の限定条件を守る)。
        return result

    result["cascade_invoked"] = True

    # --- Primary #2(同じ音声、TTSは再生成しない) ---
    text_p2, err_p2 = routing.transcribe(wav_path, language=language)
    cost_guess = 0.000002  # OpenAI mini ASRの概算単価(1呼び出しあたり数十秒の音声で1円未満)
    cumulative_cost_usd += cost_guess
    cls_p2 = val.classify_asr_match(canonical_text, text_p2) if text_p2 is not None else None
    steps.append({"step": "primary_2", "provider": "openai_asr", "text": text_p2,
                   "classification": cls_p2.classification if cls_p2 else "TTS_FAILURE"})
    if cls_p2 is not None and cls_p2.should_pass:
        result["verified"] = True
        result["stop_retrying"] = False
        result["final_status"] = cls_p2.classification
        result["classification"] = cls_p2
        return result

    if cumulative_cost_usd > COST_GUARD_MAX_USD_PER_SEGMENT:
        result["cost_guard_triggered"] = True
        result["human_review_required"] = True
        result["final_status"] = "ASR_VALIDATION_UNCERTAIN"
        return result

    # --- Secondary #1(Azure + Phrase List) ---
    text_s1, err_s1 = get_full_text_via_azure_stt_with_phrase_list(
        wav_path, language=language, phrases=ledger_phrases)
    cumulative_cost_usd += 0.00001  # Azure概算単価(1秒あたり約$0.00028、数十秒想定)
    cls_s1 = val.classify_asr_match(canonical_text, text_s1) if text_s1 is not None else None
    steps.append({"step": "secondary_1", "provider": "azure", "text": text_s1,
                   "classification": cls_s1.classification if cls_s1 else "TTS_FAILURE",
                   "phrase_list_used": bool(ledger_phrases)})
    if cls_s1 is not None and cls_s1.should_pass:
        result["verified"] = True
        result["stop_retrying"] = False
        result["final_status"] = cls_s1.classification
        result["classification"] = cls_s1
        return result

    if cumulative_cost_usd > COST_GUARD_MAX_USD_PER_SEGMENT:
        result["cost_guard_triggered"] = True
        result["human_review_required"] = True
        result["final_status"] = "ASR_VALIDATION_UNCERTAIN"
        return result

    # --- Secondary #2(Azure + Phrase List、同じ音声を再度) ---
    text_s2, err_s2 = get_full_text_via_azure_stt_with_phrase_list(
        wav_path, language=language, phrases=ledger_phrases)
    cumulative_cost_usd += 0.00001
    cls_s2 = val.classify_asr_match(canonical_text, text_s2) if text_s2 is not None else None
    steps.append({"step": "secondary_2", "provider": "azure", "text": text_s2,
                   "classification": cls_s2.classification if cls_s2 else "TTS_FAILURE",
                   "phrase_list_used": bool(ledger_phrases)})
    if cls_s2 is not None and cls_s2.should_pass:
        result["verified"] = True
        result["stop_retrying"] = False
        result["final_status"] = cls_s2.classification
        result["classification"] = cls_s2
        return result

    # --- 4 step全て不一致 -> Human Review(TTSは再生成しない、§9の通り
    # 固有名詞だけの表記差ではretryしない) ---
    result["human_review_required"] = True
    result["stop_retrying"] = True
    result["final_status"] = "ASR_VALIDATION_UNCERTAIN"
    return result
