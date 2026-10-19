# -*- coding: utf-8 -*-
"""FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 (Trial専用) lib。

Production moduleは読取/関数呼出のみ。Production ASR設定(er006_secondary_asr_01.py)は変更しない。
Azure転写はProduction `get_full_text_via_azure_stt_with_phrase_list`と同じ連続認識方式
(en-US / SpeechConfig既定 / AudioConfig(filename) / start_continuous_recognition)で、差分は
(1) PhraseListGrammar.setWeight(weight)の呼出(weight!=Noneのときのみ)
(2) Speech_LogFilename診断ログ(重み反映の証拠)
(3) 各recognizedイベントのresult.json保存、のみ。キー・リージョンは出力に含めない。
"""
import hashlib
import json
import os
import re
import time
import wave

import er005_cost_logger as cl

TRIAL_ID = "FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01"
THEME_TAG = "PLW_TRIAL_01"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.join(ROOT, "er084_output", "azure_phraselist_weight_trial_01")
USD_PER_HOUR, JPY_PER_USD = 1.0, 160.0  # er005_output/cost_baseline_01/pricing_snapshot.json (azure audio_hour USD1.0)
TARGET = "Melos"
# 「Melosの正認識」とみなす綴り、および誤認識として数える綴り(事前固定)
RE_MELOS = re.compile(r"\bmelos\b", re.I)
WRONG_VARIANTS = ("mellows", "mello", "melo", "mellow", "mellos", "malos")

COND_NAMES = ("no_pl", "pl_unspecified", "pl_w1.0", "pl_w1.5", "pl_w2.0")

_COND = {
    "no_pl": {"use_pl": False, "weight": None},
    "pl_unspecified": {"use_pl": True, "weight": None},
    "pl_w1.0": {"use_pl": True, "weight": 1.0},
    "pl_w1.5": {"use_pl": True, "weight": 1.5},
    "pl_w2.0": {"use_pl": True, "weight": 2.0},
}


def cond_spec(name: str) -> dict:
    """条件名 -> {use_pl, weight(Noneで未指定)}。"""
    return dict(_COND[name])


def wav_info(path: str) -> dict:
    with wave.open(path, "rb") as w:
        dur = w.getnframes() / float(w.getframerate())
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()
    return {"duration_s": round(dur, 3), "sha256": h}


def est_jpy(seconds: float) -> float:
    return seconds / 3600.0 * USD_PER_HOUR * JPY_PER_USD


def classify_melos(text):
    """転写1件を Melos正認識 / 誤認識variant に分類(事前固定のregex)。"""
    t = text or ""
    low = t.lower()
    return {
        "melos": bool(RE_MELOS.search(t)),
        "wrong": [v for v in WRONG_VARIANTS if re.search(r"\b" + v + r"\b", low)],
    }


def extract_weight_evidence(log_path: str, max_lines: int = 12) -> dict:
    """SDK診断ログから、PhraseList/weight/dgi/phraseDetection関連行(抜粋、秘密情報除外)を返す。"""
    if not os.path.exists(log_path):
        return {"log_exists": False}
    hits, total = [], 0
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            total += 1
            if re.search(r"weight|dgi|phraseDetection|Phrases|speech\.context", line, re.I):
                line = re.sub(r"(Ocp-Apim-Subscription-Key|X-ConnectionId|Authorization)[^,;\s]*", r"\1=<redacted>", line)
                hits.append(line.strip()[:700])
    text = open(log_path, "r", encoding="utf-8", errors="replace").read()
    # 実機で確認した証拠行: 'SPEECH-PhraseListWeight' property と speech.context JSONの dgi.bias(wireに載る値)
    prop_weight = sorted(set(re.findall(r"PhraseListWeight'; value='([^']*)'", text)))
    wire_bias = sorted(set(re.findall(r'"bias":\s*([-0-9.eE]+)', text)))
    has_dgi = '"dgi"' in text
    return {"log_exists": True, "log_lines": total, "n_hits": len(hits), "prop_weight": prop_weight,
            "wire_bias": wire_bias, "wire_has_dgi": has_dgi, "hits_head": hits[:max_lines]}


def azure_transcribe(wav_path, phrases, weight, sdk_log_path=None, language="en-US",
                     timeout_seconds=90.0, speechsdk=None) -> dict:
    """1回のAzure連続認識。phrases=None/[]ならPhraseList無。weight=NoneならsetWeightを呼ばない(=現行設定)。"""
    from dotenv import load_dotenv
    if speechsdk is None:
        import azure.cognitiveservices.speech as speechsdk
    load_dotenv()
    key, region = os.getenv("SPEECH_KEY"), os.getenv("SPEECH_REGION")
    if not key or not region:
        return {"text": None, "err": "SPEECH_KEY/SPEECH_REGION未設定", "segments_json": [], "elapsed_s": 0.0,
                "weight_call": None, "phrases": phrases, "sdk_log_path": sdk_log_path}
    cfg = speechsdk.SpeechConfig(subscription=key, region=region)
    cfg.speech_recognition_language = language
    if sdk_log_path:
        os.makedirs(os.path.dirname(sdk_log_path), exist_ok=True)
        if os.path.exists(sdk_log_path):
            os.remove(sdk_log_path)
        cfg.set_property(speechsdk.PropertyId.Speech_LogFilename, sdk_log_path)
    audio = speechsdk.audio.AudioConfig(filename=wav_path)
    rec = speechsdk.SpeechRecognizer(speech_config=cfg, audio_config=audio)
    weight_call = None
    if phrases:
        g = speechsdk.PhraseListGrammar.from_recognizer(rec)
        for p in phrases:
            g.addPhrase(p)
        if weight is not None:
            g.setWeight(float(weight))
            weight_call = float(weight)
    segs, seg_json = [], []
    done = {"flag": False, "err": None}

    def on_rec(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            segs.append(evt.result.text)
            try:
                seg_json.append(json.loads(evt.result.json))
            except Exception:  # noqa: BLE001
                seg_json.append({"raw": str(evt.result.json)[:500]})

    def on_stop(evt):
        done["flag"] = True

    def on_cancel(evt):
        try:
            d = evt.cancellation_details
            if d.reason == speechsdk.CancellationReason.Error:
                done["err"] = f"CancellationReason.Error: {getattr(d, 'error_details', None)}"
        except Exception as exc:  # noqa: BLE001
            done["err"] = f"canceled(詳細取得不能): {exc}"
        done["flag"] = True

    rec.recognized.connect(on_rec)
    rec.session_stopped.connect(on_stop)
    rec.canceled.connect(on_cancel)
    t0 = time.time()
    rec.start_continuous_recognition()
    while not done["flag"] and (time.time() - t0) < timeout_seconds:
        time.sleep(0.2)
    rec.stop_continuous_recognition()
    el = round(time.time() - t0, 3)
    err = done["err"] or (None if done["flag"] else f"timeout({timeout_seconds}s)")
    del rec  # ログfileを閉じる
    return {"text": None if err else "".join(segs), "err": err, "segments_json": seg_json, "elapsed_s": el,
            "weight_call": weight_call, "phrases": list(phrases) if phrases else None, "sdk_log_path": sdk_log_path}


def append_raw(raw_path: str, row: dict) -> None:
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    with open(raw_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_raw(raw_path: str) -> list:
    if not os.path.exists(raw_path):
        return []
    return [json.loads(line) for line in open(raw_path, encoding="utf-8") if line.strip()]


def record_cost(phase: str, wav: dict, ok: bool, elapsed: float, cond: str) -> float:
    """er005_cost_loggerへTrial専用THEME_TAGで記録(Productionのcost_logを汚さないTrial専用ファイル、cl.install不使用)。"""
    jpy = est_jpy(wav["duration_s"])
    with cl.logging_context(THEME_TAG, f"phase_{phase}"):
        cl.record({"provider": "azure", "api": "plw_trial_azure_transcribe", "model_id": "azure-speech-stt",
                   "locale": "en-US", "attempt_number": 1, "success": ok, "elapsed_seconds": elapsed,
                   "usage_source": "LOCAL_WAV_HEADER_EXACT", "audio_duration_submitted_seconds": wav["duration_s"],
                   "condition": cond, "est_jpy": round(jpy, 4)})
    return jpy
