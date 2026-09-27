# ============================================================
# er022_tts_gemini_3_8_flash_lite_next_trial_01_stage1.py
# TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01 (Stage 1: 実TTS呼び出し1件)
# ============================================================
# 性質: Trial限定(最大到達Status=VALIDATED、Production採用しない、
# Production挙動は無変更)。実行は `.venv_trial_genai225`
# (google-genai==2.25.0、Production .venv/.venv-ci/requirements*.txtは
# 無変更)からのみ行う。
#
# 前提: 本Trialの前段(Phase 0、TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01
# _REPORT.md §0-§13)で、google-genai==2.14.0では公式ドキュメントが要求
# する`speech_metadata`(GenerateContent APIのPart.speechMetadata、REST
# リファレンス`ai.google.dev/api/generate-content`に定義済み)がSDK型
# レベルで欠落していたことを確認しSTOPした。同REPORT §12補足調査で、
# CHANGELOG(2.25.0, 2026-09-22公開)に「Expose SpeechMetadata...in public
# GenAI SDKs」という該当記述を発見し、REST定義とも整合することを確認
# した(いずれもネットワーク呼び出し0件、¥0)。本ファイルはその続き
# ——2.25.0を実際にTrial venvへ導入した上での実機検証(Stage 1)。
#
# 呼び出し形状: 現行Production(er003_b1_p7a_audio.make_tts_call_fn_for_
# model)が使う「Structured Separation」(本文内delimiterでstyle指示を
# 混ぜる単一文字列prompt)は使わない。代わりに、公式ドキュメントが要求する
# 構造: contents = Content(parts=[Part(text=<verbatim canonical text>,
# speech_metadata=SpeechMetadata(style=<style>))])。本文(text)は
# parts.json の tension_body をそのまま使う(一切変更しない、ER-005の
# 「内容は変えず区切り方だけ変える」原則を踏襲)。
#
# 変えないもの(計画doc§4):
#   - ASR検証: er006_asr_provider_routing_01.transcribe(既存Primary ASR
#     routing、Production非変更)+
#     er006_preprod_hardening_01_validation.classify_asr_match(英語6分類
#     Validator、Production非変更)をそのままimportして使う。
#   - retry上限: 標準2回+fallback1回=合計3回
#     (er011_human_review_lock_01.PRODUCTION_MAX_TTS_ATTEMPTS/
#     PRODUCTION_STANDARD_TTS_ATTEMPTSの値をそのまま参照するが、呼び出し
#     形状自体が変わるため独立したorchestrationループを本ファイル内に
#     新設する。計画doc§4の想定通り——Production関数の中身は一切変更
#     しない)。
#   - 異常長検知: er003_audio_tts_asr_safety.detect_duration_anomaly
#     (Production非変更)。
#   - Production本体ファイル(er003_*/er006_*/er011_*/er012_*等): import
#     して利用するのみ、一切変更しない。
#
# Cost Guard: er011_connected_speech_equivalence_layer_trial_02.py と
# 同型のcompute_cost_jpy_so_far()/assert_budget_ok()をTrial専用で実装
# (Cap=500円、呼び出し前の事前ガード)。
#
# 実行方法:
#   .venv_trial_genai225/Scripts/python.exe \
#     er022_tts_gemini_3_8_flash_lite_next_trial_01_stage1.py
from __future__ import annotations

import difflib
import io
import json
import os
import re
import time
import wave

import numpy as np
import soundfile as sf

import er002_common as common
import er003_audio_tts_asr_safety as safety
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as en_validator
import er011_human_review_lock_01 as review_lock

SOURCE_A_DIR = "er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/a2"
OUT_DIR = "er022_output/tts_gemini_3_8_flash_lite_next_trial_01/stage1"
NARR_DIR = f"{OUT_DIR}/narration"
AUDIT_DIR = f"{OUT_DIR}/audit"
COST_LOG_PATH = f"{AUDIT_DIR}/raw_usage_log.jsonl"
RESULT_PATH = f"{AUDIT_DIR}/stage1_result.json"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"

MODEL_B = "gemini-3.8-flash-lite-tts"
VOICE_NAME = "Aoede"
SEGMENT_NAME = "tension_reflection"
LANGUAGE = "en"
USD_JPY = 160.0

# TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01(委任文§13-4/5): 事前ガード用
# worst-case(output token上限16,384付近まで暴走した場合)の1 attempt
# あたり見積り(計画doc§10、pricing_snapshot.json登録値そのまま)。
BUDGET_JPY_CAP = 500.0
WORST_CASE_OUTPUT_TOKENS_PER_ATTEMPT = 16384

# 標準2回+fallback1回=合計3回(既存PRODUCTION_MAX_TTS_ATTEMPTS/
# PRODUCTION_STANDARD_TTS_ATTEMPTSの値をそのまま参照、値自体は変更しない)。
STANDARD_ATTEMPTS = review_lock.PRODUCTION_STANDARD_TTS_ATTEMPTS
TOTAL_ATTEMPTS = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS

# 計画doc§6の段階的方針(Step A: style空/Step B: 簡潔style)+
# レポート§11の想定(fallback=単純な差)に基づく、本Trial限定のstyle系列
# (ユーザー方針: theatrical/明示的ペース指示は含めない、既存Production
# instructionの詳細移植はしない)。
ATTEMPT_STYLES = [
    "",  # attempt 1(標準#1): 公式推奨"Test plain TTS first"(Step A)
    "natural, clear, conversational",  # attempt 2(標準#2): Step B(簡潔style)
    "clear",  # attempt 3(fallback): さらに単純な最小指示(標準2回とは異なる構成)
]

os.makedirs(NARR_DIR, exist_ok=True)
os.makedirs(AUDIT_DIR, exist_ok=True)


def log(msg: str) -> None:
    print(msg, flush=True)


# ============================================================
# Part 0: Cost Guard(er011_connected_speech_equivalence_layer_trial_02.py
# と同型、Trial専用の独立実装。既存pricing_snapshot.json[Phase 0で
# gemini-3.8-flash-lite-tts Standard/Batch単価を追加登録済み]を参照する)
# ============================================================
def _load_pricing() -> list:
    return json.load(open(PRICING_SNAPSHOT_PATH, encoding="utf-8"))["prices"]


def _price(prices: list, provider: str, model: str, meter: str, tier: str = "Standard") -> float:
    return next(p["price"] for p in prices
                if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                and p.get("tier", "Standard") == tier)


def compute_cost_jpy_so_far() -> tuple[float, dict]:
    if not os.path.exists(COST_LOG_PATH):
        return 0.0, {}
    prices = _load_pricing()
    total_usd = 0.0
    by_provider: dict = {}
    with open(COST_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            usd = 0.0
            try:
                if provider == "gemini" and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = (in_tok * _price(prices, "gemini", model, "input_tokens", "Standard") / 1e6
                           + out_tok * _price(prices, "gemini", model, "output_tokens", "Standard") / 1e6)
                elif provider == "openai_asr" and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = (in_tok * _price(prices, "openai_asr", model, "input_tokens", "Standard") / 1e6
                           + out_tok * _price(prices, "openai_asr", model, "output_tokens", "Standard") / 1e6)
            except StopIteration:
                usd = 0.0
            total_usd += usd
            by_provider[provider] = by_provider.get(provider, 0.0) + usd
    jpy = total_usd * USD_JPY
    return jpy, {k: round(v * USD_JPY, 2) for k, v in by_provider.items()}


def worst_case_next_call_jpy() -> float:
    prices = _load_pricing()
    rate_out = _price(prices, "gemini", MODEL_B, "output_tokens", "Standard")
    usd = WORST_CASE_OUTPUT_TOKENS_PER_ATTEMPT * rate_out / 1e6
    return usd * USD_JPY


def assert_budget_ok(note: str = "") -> float:
    """次の1回のTTS呼び出しを行う直前に呼ぶ、事前ガード方式
    (委任文§13-4: 実行後ではなく実行前に判定)。"""
    jpy_so_far, by_provider = compute_cost_jpy_so_far()
    projected = jpy_so_far + worst_case_next_call_jpy()
    log(f"  [budget] so_far={jpy_so_far:.2f} JPY, projected(worst-case next call)={projected:.2f} JPY, "
        f"cap={BUDGET_JPY_CAP} JPY, by_provider={by_provider} ({note})")
    if projected > BUDGET_JPY_CAP:
        raise RuntimeError(
            f"[BUDGET_GUARD] projected cost {projected:.1f} JPY (so_far={jpy_so_far:.1f}"
            f" + worst_case_next_call={projected - jpy_so_far:.1f}) > cap {BUDGET_JPY_CAP} JPY. "
            f"Stopping before the call ({note}).")
    if jpy_so_far > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] actual cost so far {jpy_so_far:.1f} JPY > cap {BUDGET_JPY_CAP} JPY ({note}).")
    return jpy_so_far


# ============================================================
# Part 1: TTS呼び出し(speech_metadataを使う新経路、Production
# build_tts_promptは一切使わない)
# ============================================================
def make_tts_call_fn(model_name: str, voice_name: str):
    """GenerateContent API経由、Part.speech_metadataでstyleを渡す。
    本文(text)はverbatim(delimiterなし)。gclient.make_client()と同じ
    client構築方法(APIキーは環境変数のみ)を使う(er002_gemini_client.py
    は無変更、importして関数だけ再利用)。"""
    import er002_gemini_client as gclient
    from google.genai import types

    client = gclient.make_client()

    def tts_call_fn(text: str, style: str) -> bytes:
        parts_kwargs = {"text": text}
        if style:
            parts_kwargs["speech_metadata"] = types.SpeechMetadata(style=style)
        content = types.Content(parts=[types.Part(**parts_kwargs)], role="user")
        response = client.models.generate_content(
            model=model_name,
            contents=content,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
                    )
                ),
            ),
        )
        parts = response.candidates[0].content.parts
        raw = b"".join(p.inline_data.data for p in parts if p.inline_data and p.inline_data.data)
        if not raw:
            raise RuntimeError(f"音声パーツが空でした(parts数: {len(parts)})")
        return raw

    return tts_call_fn


def decode_audio_bytes_defensive(raw: bytes) -> tuple[np.ndarray, int, bool]:
    """計画doc§1-3(Gemini 3.8系はデフォルトでWAVヘッダ付き音声を返す)への
    対応。先頭がRIFFマジックバイトかどうかを検出し、WAVならwaveモジュール
    で正しくデコードする(ヘッダ誤読を防ぐ)。ヘッダが無ければ既存
    Production同様、ヘッダ無し16bit生PCM/24kHz/monoと仮定する
    (er002_common.pcm_bytes_to_float_mono と同じ前提)。"""
    if raw[:4] == b"RIFF" and raw[8:12] == b"WAVE":
        with wave.open(io.BytesIO(raw), "rb") as w:
            channels = w.getnchannels()
            sampwidth = w.getsampwidth()
            framerate = w.getframerate()
            nframes = w.getnframes()
            frames = w.readframes(nframes)
        assert sampwidth == 2, f"想定外のsample width: {sampwidth}"
        samples = np.frombuffer(frames, dtype=np.int16).astype(np.float64) / 32768.0
        if channels > 1:
            samples = samples.reshape(-1, channels).mean(axis=1)
        return samples, framerate, True
    samples = common.pcm_bytes_to_float_mono(raw)
    return samples, common.SAMPLE_RATE, False


# ============================================================
# Part 2: 本文外発話(off-script speech)検知(計画doc§7、既存分類の
# 解釈強化。新規実装ではなく既存TRUE_CONTENT_MISMATCH分類への追加解釈)
# ============================================================
_WORD_RE = re.compile(r"[a-zA-Z']+")


def canonical_word_overlap_fraction(canonical_text: str, asr_text: str) -> float:
    canon_words = {w.lower() for w in _WORD_RE.findall(canonical_text) if len(w) >= 4}
    asr_words = {w.lower() for w in _WORD_RE.findall(asr_text or "")}
    if not canon_words:
        return 1.0
    return len(canon_words & asr_words) / len(canon_words)


def retry_checkpoint_analysis(canonical_text: str, attempts_so_far: list, style_words: list) -> dict:
    """委任文§13-3: 「同一segmentでretryが2回発生した時点(3回目に入る
    前)で、原因を一度立ち止まって確認する」を、機械的な診断ログとして
    実装する(前回のように3回終わるまで気づかない運用を避ける)。"""
    findings = []
    for a in attempts_so_far:
        asr_text = (a.get("asr_text") or "").lower()
        leaked_style_words = [w for w in style_words if w and w.lower() in asr_text]
        similarity = difflib.SequenceMatcher(a=canonical_text.lower(), b=asr_text, autojunk=False).ratio()
        findings.append({
            "attempt": a.get("attempt"), "classification": a.get("classification"),
            "leaked_style_words_detected": leaked_style_words,
            "text_similarity_ratio": round(similarity, 3),
            "canonical_word_overlap_fraction": round(canonical_word_overlap_fraction(canonical_text, a.get("asr_text") or ""), 3),
        })
    return {"checkpoint": "after_attempt_2_before_attempt_3", "per_attempt_findings": findings}


# ============================================================
# Part 3: Stage 1 orchestration(独立実装。Production
# generate_english_segment_with_fallback は使わない——理由は計画doc§4:
# 呼び出し形状[part単位でspeech_metadataを渡す]自体が変わるため)
# ============================================================
def run_stage1() -> dict:
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    cl.install(COST_LOG_PATH)

    parts = json.load(open(f"{SOURCE_A_DIR}/parts.json", encoding="utf-8"))
    canonical_text = parts["tension_body"]
    out_path = f"{NARR_DIR}/{SEGMENT_NAME}.wav"

    tts_call_fn = make_tts_call_fn(MODEL_B, VOICE_NAME)

    attempts_log = []
    early_stop = None
    final_status = "ASR_VALIDATION_UNCERTAIN"
    final_asr_text = None
    final_duration = None

    for attempt in range(1, TOTAL_ATTEMPTS + 1):
        style = ATTEMPT_STYLES[attempt - 1]
        note = f"{SEGMENT_NAME} attempt {attempt}/{TOTAL_ATTEMPTS} (style={style!r})"

        if attempt == STANDARD_ATTEMPTS + 1:
            # 委任文§13-3: fallback(3回目)へ入る前に立ち止まって確認する。
            checkpoint = retry_checkpoint_analysis(canonical_text, attempts_log, ATTEMPT_STYLES)
            log(f"  [retry_checkpoint] {json.dumps(checkpoint, ensure_ascii=False)}")
            attempts_log.append({"attempt": "checkpoint", **checkpoint})

        try:
            assert_budget_ok(note)
        except RuntimeError as e:
            early_stop = {"reason": "BUDGET_GUARD_STOP", "detail": str(e)}
            log(f"  [STOP] {early_stop}")
            break

        t0 = time.time()
        with cl.segment_context(SEGMENT_NAME):
            try:
                raw = tts_call_fn(canonical_text, style)
            except Exception as e:
                elapsed = round(time.time() - t0, 3)
                attempts_log.append({"attempt": attempt, "style": style, "status": "TTS_CALL_FAILED",
                                      "error": str(e)[:500], "elapsed_seconds": elapsed})
                continue
        elapsed = round(time.time() - t0, 3)

        samples, framerate, wav_header_detected = decode_audio_bytes_defensive(raw)
        raw_duration = round(len(samples) / framerate, 4)

        anomaly = safety.detect_duration_anomaly(raw_duration, canonical_text, LANGUAGE)
        if anomaly["is_anomaly"]:
            attempts_log.append({
                "attempt": attempt, "style": style, "status": "STOPPED_DURATION_ANOMALY",
                "elapsed_seconds": elapsed, "wav_header_detected": wav_header_detected,
                "duration_seconds": raw_duration, "anomaly": anomaly,
            })
            if attempt == TOTAL_ATTEMPTS:
                early_stop = {"reason": "DURATION_ANOMALY_ON_FINAL_ATTEMPT", "detail": anomaly}
            continue

        common.write_wav_float(out_path, samples, framerate, 1)
        asr_text, asr_err = routing.transcribe(out_path, "en-US")
        if asr_err or asr_text is None:
            attempts_log.append({"attempt": attempt, "style": style, "status": "ASR_ERROR",
                                  "asr_error": asr_err, "elapsed_seconds": elapsed,
                                  "wav_header_detected": wav_header_detected, "duration_seconds": raw_duration})
            continue

        cls = en_validator.classify_asr_match(canonical_text, asr_text)
        metrics = common.measure_metrics(samples, framerate)
        entry = {
            "attempt": attempt, "style": style, "status": "OK_ASR_RAN",
            "asr_text": asr_text, "classification": cls.classification,
            "should_pass": cls.should_pass, "should_retry": cls.should_retry,
            "reason": cls.reason, "elapsed_seconds": elapsed,
            "wav_header_detected": wav_header_detected, "duration_seconds": raw_duration,
            "clipping_detected": metrics.get("clipping_detected"),
        }

        if cls.should_pass:
            entry["final_status"] = "OK"
            attempts_log.append(entry)
            final_status = "OK"
            final_asr_text = asr_text
            final_duration = raw_duration
            break

        # 計画doc§7: 本文外発話(TRUE_CONTENT_MISMATCH かつ canonical主要語が
        # ほぼ含まれない)は既存retry上限を待たず即座にTrial全体を停止する。
        if cls.classification == "TRUE_CONTENT_MISMATCH":
            overlap = canonical_word_overlap_fraction(canonical_text, asr_text)
            entry["canonical_word_overlap_fraction"] = round(overlap, 3)
            if overlap < 0.2:
                attempts_log.append(entry)
                early_stop = {
                    "reason": "OFF_SCRIPT_SPEECH_DETECTED",
                    "detail": f"canonical_word_overlap_fraction={overlap:.3f} (<0.2しきい値)、"
                               f"ASRテキストがcanonical本文とほぼ無関係と判定",
                    "attempt": attempt,
                }
                log(f"  [STOP] {early_stop}")
                break

        attempts_log.append(entry)

    result = {
        "management_id": "TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01",
        "stage": "Stage 1 (1 segment)",
        "segment": SEGMENT_NAME, "language": LANGUAGE, "voice": VOICE_NAME, "model": MODEL_B,
        "canonical_text_char_count": len(canonical_text),
        "attempts_log": attempts_log,
        "final_status": final_status if early_stop is None else "STOPPED",
        "early_stop": early_stop,
        "final_asr_text": final_asr_text,
        "final_duration_seconds": final_duration,
        "standard_attempts_budget": STANDARD_ATTEMPTS, "total_attempts_budget": TOTAL_ATTEMPTS,
        "attempt_styles_used": ATTEMPT_STYLES,
        "out_path": out_path if final_status == "OK" else (out_path if os.path.exists(out_path) else None),
    }
    jpy_final, by_provider_final = compute_cost_jpy_so_far()
    result["cost_jpy_total"] = round(jpy_final, 2)
    result["cost_jpy_by_provider"] = by_provider_final
    result["budget_cap_jpy"] = BUDGET_JPY_CAP

    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


if __name__ == "__main__":
    r = run_stage1()
    print(json.dumps({k: v for k, v in r.items() if k != "attempts_log"}, ensure_ascii=False, indent=2))
    print(f"\n[written] {RESULT_PATH}")
