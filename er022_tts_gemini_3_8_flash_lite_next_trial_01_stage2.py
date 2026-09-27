# ============================================================
# er022_tts_gemini_3_8_flash_lite_next_trial_01_stage2.py
# TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01 (Stage 2: 2〜3 segment、
# 異なるVoice/固有名詞+数値segmentを追加)
# ============================================================
# 性質: Trial限定(最大到達Status=VALIDATED、Production採用しない、
# Production挙動は無変更)。実行は `.venv_trial_genai225`
# (google-genai==2.25.0)からのみ行う。Stage 1 script
# (er022_..._stage1.py)は本タスクで一切変更していない
# (新規ファイルとしてStage 2ロジックを追加しただけ)。
#
# 呼び出し形状: Stage 1と同じ(Structured Separationは使わず、
# GenerateContent APIのPart.speech_metadataでstyleを渡す。本文[text]は
# verbatim、既存canonical本文を一切変更しない)。Stage 1との違いは
# segmentを1件から2〜3件へ拡張し、各segmentごとに独立したbudget guard
# (segment単位¥500・Stage2合計¥1500)を適用する点。
#
# 対象segment(委任文Stage2内容1、選定理由は各SEGMENTS辞書のrationale参照):
#   1. hormuz_full_story_part1: Family X Hormuz B1B `full_story_part1`
#      (数値+固有名詞を含む必須segment)。
#   2. ai_hiring_point_two_body: ai_hiring A2 `point_two_body`
#      (Narrator以外のVoice=Erinome、必須segment)。
#   3. ai_hiring_full_story_part1: ai_hiring A2 `full_story_part1`
#      (任意・予算内、Voice=Aoede)。
#
# 変えないもの(計画doc§4、Stage1と同一):
#   - ASR検証: er006_asr_provider_routing_01.transcribe(既存Primary ASR
#     routing、Production非変更、共有storeへの書き込み無し[確認済み])。
#   - retry上限: 標準2回+fallback1回=合計3回。
#   - 異常長検知: er003_audio_tts_asr_safety.detect_duration_anomaly。
#   - Production本体ファイル: import して利用するのみ、一切変更しない。
#
# Cost Guard: segment単位上限¥500、Stage2合計上限¥1500(委任文の指示、
# Stage1と同型のcompute_cost_jpy_so_far()/assert_budget_ok()を、
# segment単位フィルタと合計の両方でチェックするよう拡張)。
#
# 実行方法:
#   .venv_trial_genai225/Scripts/python.exe \
#     er022_tts_gemini_3_8_flash_lite_next_trial_01_stage2.py
from __future__ import annotations

import io
import json
import os
import re
import time
import wave

import numpy as np

import er002_common as common
import er003_audio_tts_asr_safety as safety
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as en_validator
import er011_human_review_lock_01 as review_lock

OUT_DIR = "er022_output/tts_gemini_3_8_flash_lite_next_trial_01/stage2"
NARR_DIR = f"{OUT_DIR}/narration"
AUDIT_DIR = f"{OUT_DIR}/audit"
COST_LOG_PATH = f"{AUDIT_DIR}/raw_usage_log.jsonl"
RESULT_PATH = f"{AUDIT_DIR}/stage2_result.json"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"

MODEL_B = "gemini-3.8-flash-lite-tts"
USD_JPY = 160.0

# 委任文Stage2内容(費用): segment単位上限¥500、Stage2合計上限¥1500。
BUDGET_JPY_CAP_PER_SEGMENT = 500.0
BUDGET_JPY_CAP_TOTAL = 1500.0
WORST_CASE_OUTPUT_TOKENS_PER_ATTEMPT = 16384

STANDARD_ATTEMPTS = review_lock.PRODUCTION_STANDARD_TTS_ATTEMPTS
TOTAL_ATTEMPTS = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS

# Stage1と同じstyle系列(委任文「Stage 1と同じstyle方針(簡潔style)で
# 再現性を優先」、ペース調整[pace指示]は今回行わない)。
ATTEMPT_STYLES = [
    "",  # attempt 1(標準#1): 公式推奨"Test plain TTS first"
    "natural, clear, conversational",  # attempt 2(標準#2)
    "clear",  # attempt 3(fallback)
]

os.makedirs(NARR_DIR, exist_ok=True)
os.makedirs(AUDIT_DIR, exist_ok=True)


def log(msg: str) -> None:
    print(msg, flush=True)


# ============================================================
# Part 0: segment候補の定義(既存Production artifactから読み取り専用で
# canonical text・A側参照音声メタデータを取得する。既存artifactは一切
# 変更しない)。
# ============================================================
def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_segment_configs() -> list[dict]:
    segments = []

    # --- 1. hormuz_full_story_part1(必須、数値+固有名詞) ---
    hormuz_dir = ("er019_output/family_x_audio_production_wiring_01/"
                  "family_x_b3_diversity_trial_01/hormuz__run_02/b1b")
    hormuz_results = _load_json(f"{hormuz_dir}/audit/tts_generation_results.json")
    hormuz_seg = hormuz_results["segments"]["full_story_part1"]
    # 委任文/計画doc の「内容は変えず区切り方だけ変える」原則(ER-005)に
    # 従い、raw parts.json ではなく、Productionが実際にTTSへ送信した
    # 正規化済みtext(TTS-SYMBOL-NORMALIZATION適用後、"20%"/"Act 2"等の
    # digit表記)を使う。A側音声もこのtextから生成されたものであるため、
    # A/B比較の公平性を保つにはこちらが正しい(raw parts.json側は
    # 「Act Two」等の綴り文字表記かつ全角引用符付きで、A音声の実際の
    # 入力とは異なる)。
    canonical_text = hormuz_seg["text"]
    segments.append({
        "segment_id": "hormuz_full_story_part1",
        "language": "en",
        "voice": "Aoede",
        "canonical_text": canonical_text,
        "a_wav_path": f"{hormuz_dir}/narration/full_story_part1.wav",
        "a_duration_seconds": hormuz_seg["trim_info"]["trimmed_duration_seconds"],
        "a_model": "gemini-2.5-pro-preview-tts",
        "a_voice": "Aoede",
        "a_instruction_type": hormuz_seg.get("instruction_type"),
        "rationale": ("数値[3 acts/20%/2/3/July 13/10:16 a.m.]と固有名詞"
                      "[Trump/Strait of Hormuz/United States/US]を含む必須segment。"
                      "Family X Hormuz B1B記事の既存OK音声・textが確認できたため、"
                      "計画doc§5第1候補[代替]は使わずこちらを採用。"),
        "required": True,
    })

    # --- 2. ai_hiring_point_two_body(必須、Narrator以外のVoice) ---
    a2_dir = "er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/a2"
    a2_results = _load_json(f"{a2_dir}/audit/tts_generation_results.json")
    a2_parts = _load_json(f"{a2_dir}/parts.json")
    point_two_seg = a2_results["segments"]["point_two"]
    segments.append({
        "segment_id": "ai_hiring_point_two_body",
        "language": "en",
        "voice": "Erinome",
        # Stage1の前例(parts.jsonのtension_bodyをそのまま使用)を踏襲。
        # このsegmentには数字が無いため(計画doc§5確認済み)、
        # symbol正規化による内容差分は無い(production "text" フィールドは
        # 段落区切りが単一スペースへ結合されているだけで語彙は同一)。
        "canonical_text": a2_parts["point_two_body"],
        "a_wav_path": f"{a2_dir}/narration/point_two.wav",
        "a_duration_seconds": point_two_seg["trim_info"]["trimmed_duration_seconds"],
        "a_model": point_two_seg.get("model") or "gemini-2.5-pro-preview-tts",
        "a_voice": "Erinome",
        "a_instruction_type": point_two_seg.get("instruction_type"),
        "rationale": ("Narrator(Aoede)以外のVoice[Erinome]を使う必須segment。"
                      "3 Voices記事のキャラクター読み上げの代表。"),
        "required": True,
    })

    # --- 3. ai_hiring_full_story_part1(任意、予算内) ---
    full_story_seg = a2_results["segments"]["full_story_part1"]
    segments.append({
        "segment_id": "ai_hiring_full_story_part1",
        "language": "en",
        "voice": "Aoede",
        "canonical_text": a2_parts["part1"],
        "a_wav_path": f"{a2_dir}/narration/full_story_part1.wav",
        "a_duration_seconds": full_story_seg["trim_info"]["trimmed_duration_seconds"],
        "a_model": full_story_seg.get("model") or "gemini-2.5-pro-preview-tts",
        "a_voice": "Aoede",
        "a_instruction_type": full_story_seg.get("instruction_type"),
        "rationale": ("任意candidate。「Full Story」名称のNarrator通常品質の基準点。"
                      "予算内であれば実行する(委任文Stage2内容1)。"),
        "required": False,
    })

    return segments


# ============================================================
# Part 1: Cost Guard(segment単位¥500 + Stage2合計¥1500の二重ガード)
# ============================================================
def _load_pricing() -> list:
    return json.load(open(PRICING_SNAPSHOT_PATH, encoding="utf-8"))["prices"]


def _price(prices: list, provider: str, model: str, meter: str, tier: str = "Standard") -> float:
    return next(p["price"] for p in prices
                if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                and p.get("tier", "Standard") == tier)


def _iter_cost_records():
    if not os.path.exists(COST_LOG_PATH):
        return
    with open(COST_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def _record_cost_jpy(rec: dict, prices: list) -> float:
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
    return usd * USD_JPY


def compute_cost_jpy_so_far(segment_id: str | None = None) -> tuple[float, dict]:
    prices = _load_pricing()
    total_jpy = 0.0
    by_provider: dict = {}
    for rec in _iter_cost_records():
        if segment_id is not None and rec.get("segment") != segment_id:
            continue
        jpy = _record_cost_jpy(rec, prices)
        total_jpy += jpy
        by_provider[rec.get("provider")] = by_provider.get(rec.get("provider"), 0.0) + jpy
    return total_jpy, {k: round(v, 2) for k, v in by_provider.items()}


def worst_case_next_call_jpy() -> float:
    prices = _load_pricing()
    rate_out = _price(prices, "gemini", MODEL_B, "output_tokens", "Standard")
    usd = WORST_CASE_OUTPUT_TOKENS_PER_ATTEMPT * rate_out / 1e6
    return usd * USD_JPY


def assert_budget_ok(segment_id: str, note: str = "") -> float:
    """次の1回のTTS呼び出しを行う直前に呼ぶ、事前ガード方式。
    segment単位¥500、Stage2合計¥1500の両方をチェックする
    (委任文Stage2内容: 「segment単位上限¥500、Stage 2合計上限¥1,500」)。"""
    seg_jpy, seg_by_provider = compute_cost_jpy_so_far(segment_id)
    total_jpy, total_by_provider = compute_cost_jpy_so_far(None)
    worst = worst_case_next_call_jpy()
    seg_projected = seg_jpy + worst
    total_projected = total_jpy + worst
    log(f"  [budget] segment={segment_id} seg_so_far={seg_jpy:.2f} JPY "
        f"seg_projected={seg_projected:.2f}/{BUDGET_JPY_CAP_PER_SEGMENT} JPY, "
        f"total_so_far={total_jpy:.2f} total_projected={total_projected:.2f}/{BUDGET_JPY_CAP_TOTAL} JPY "
        f"({note})")
    if seg_projected > BUDGET_JPY_CAP_PER_SEGMENT:
        raise RuntimeError(
            f"[BUDGET_GUARD_SEGMENT] projected segment cost {seg_projected:.1f} JPY > "
            f"per-segment cap {BUDGET_JPY_CAP_PER_SEGMENT} JPY. Stopping before the call ({note}).")
    if total_projected > BUDGET_JPY_CAP_TOTAL:
        raise RuntimeError(
            f"[BUDGET_GUARD_TOTAL] projected total cost {total_projected:.1f} JPY > "
            f"Stage2 cap {BUDGET_JPY_CAP_TOTAL} JPY. Stopping before the call ({note}).")
    return seg_jpy


# ============================================================
# Part 2: TTS呼び出し(Stage1と同一形状、speech_metadataでstyleを渡す)
# ============================================================
def make_tts_call_fn(model_name: str, voice_name: str):
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
    対応。Stage1と同一実装。"""
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
# Part 3: 本文外発話・指示文漏れ検知(委任文Stage2内容3の早期STOP条件)
# ============================================================
_WORD_RE = re.compile(r"[a-zA-Z']+")


def canonical_word_overlap_fraction(canonical_text: str, asr_text: str) -> float:
    canon_words = {w.lower() for w in _WORD_RE.findall(canonical_text) if len(w) >= 4}
    asr_words = {w.lower() for w in _WORD_RE.findall(asr_text or "")}
    if not canon_words:
        return 1.0
    return len(canon_words & asr_words) / len(canon_words)


def detect_leaked_style_words(canonical_text: str, asr_text: str, style: str) -> list[str]:
    """委任文Stage2内容3「指示文の読み上げ」の検知。styleの各単語がASR結果に
    含まれ、かつcanonical本文自体には元々含まれない単語のみを漏れとみなす
    (canonical本文中に偶然同じ単語が存在するケースの誤検知を避ける)。"""
    if not style:
        return []
    canon_lower = canonical_text.lower()
    asr_lower = (asr_text or "").lower()
    leaked = []
    for raw_word in style.split(","):
        w = raw_word.strip().lower()
        if not w:
            continue
        if w in asr_lower and w not in canon_lower:
            leaked.append(w)
    return leaked


# ============================================================
# Part 4: segment単位のorchestration(Stage1と同一retryロジック、
# segment横断の早期STOPを追加)
# ============================================================
def run_segment(seg_cfg: dict) -> dict:
    segment_id = seg_cfg["segment_id"]
    canonical_text = seg_cfg["canonical_text"]
    out_path = f"{NARR_DIR}/{segment_id}.wav"
    tts_call_fn = make_tts_call_fn(MODEL_B, seg_cfg["voice"])

    attempts_log = []
    early_stop = None
    final_status = "ASR_VALIDATION_UNCERTAIN"
    final_asr_text = None
    final_duration = None

    for attempt in range(1, TOTAL_ATTEMPTS + 1):
        style = ATTEMPT_STYLES[attempt - 1]
        note = f"{segment_id} attempt {attempt}/{TOTAL_ATTEMPTS} (style={style!r})"

        try:
            assert_budget_ok(segment_id, note)
        except RuntimeError as e:
            early_stop = {"reason": "BUDGET_GUARD_STOP", "detail": str(e)}
            log(f"  [STOP] {early_stop}")
            break

        t0 = time.time()
        with cl.segment_context(segment_id):
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

        anomaly = safety.detect_duration_anomaly(raw_duration, canonical_text, seg_cfg["language"])
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
        asr_text, asr_err = routing.transcribe(out_path, f"{seg_cfg['language']}-US"
                                                if seg_cfg["language"] == "en" else seg_cfg["language"])
        if asr_err or asr_text is None:
            attempts_log.append({"attempt": attempt, "style": style, "status": "ASR_ERROR",
                                  "asr_error": asr_err, "elapsed_seconds": elapsed,
                                  "wav_header_detected": wav_header_detected, "duration_seconds": raw_duration})
            continue

        cls = en_validator.classify_asr_match(canonical_text, asr_text)
        metrics = common.measure_metrics(samples, framerate)
        leaked_style_words = detect_leaked_style_words(canonical_text, asr_text, style)
        entry = {
            "attempt": attempt, "style": style, "status": "OK_ASR_RAN",
            "asr_text": asr_text, "classification": cls.classification,
            "should_pass": cls.should_pass, "should_retry": cls.should_retry,
            "reason": cls.reason, "elapsed_seconds": elapsed,
            "wav_header_detected": wav_header_detected, "duration_seconds": raw_duration,
            "clipping_detected": metrics.get("clipping_detected"),
            "leaked_style_words": leaked_style_words,
        }

        if leaked_style_words:
            attempts_log.append(entry)
            early_stop = {
                "reason": "INSTRUCTION_TEXT_LEAKED",
                "detail": f"leaked_style_words={leaked_style_words}",
                "attempt": attempt,
            }
            log(f"  [STOP] {early_stop}")
            break

        if cls.should_pass:
            entry["final_status"] = "OK"
            attempts_log.append(entry)
            final_status = "OK"
            final_asr_text = asr_text
            final_duration = raw_duration
            break

        if cls.classification == "TRUE_CONTENT_MISMATCH":
            overlap = canonical_word_overlap_fraction(canonical_text, asr_text)
            entry["canonical_word_overlap_fraction"] = round(overlap, 3)
            if overlap < 0.2:
                attempts_log.append(entry)
                early_stop = {
                    "reason": "OFF_SCRIPT_SPEECH_DETECTED",
                    "detail": f"canonical_word_overlap_fraction={overlap:.3f} (<0.2しきい値)",
                    "attempt": attempt,
                }
                log(f"  [STOP] {early_stop}")
                break

        attempts_log.append(entry)

    if early_stop is None and final_status != "OK" and len(
            [a for a in attempts_log if a.get("attempt") in (1, 2, 3)]) >= TOTAL_ATTEMPTS:
        early_stop = {"reason": "ALL_ATTEMPTS_EXHAUSTED_WITHOUT_PASS", "detail": "3回とも成功しなかった"}

    seg_jpy, seg_by_provider = compute_cost_jpy_so_far(segment_id)
    return {
        "segment_id": segment_id,
        "language": seg_cfg["language"], "voice": seg_cfg["voice"], "model": MODEL_B,
        "canonical_text_char_count": len(canonical_text),
        "a_reference": {
            "wav_path": seg_cfg["a_wav_path"],
            "duration_seconds": seg_cfg["a_duration_seconds"],
            "model": seg_cfg["a_model"], "voice": seg_cfg["a_voice"],
            "instruction_type": seg_cfg["a_instruction_type"],
        },
        "rationale": seg_cfg["rationale"],
        "attempts_log": attempts_log,
        "final_status": final_status if early_stop is None else "STOPPED",
        "early_stop": early_stop,
        "final_asr_text": final_asr_text,
        "final_duration_seconds": final_duration,
        "out_path": out_path if os.path.exists(out_path) else None,
        "cost_jpy_segment_total": round(seg_jpy, 2),
        "cost_jpy_segment_by_provider": seg_by_provider,
    }


# ============================================================
# Part 5: Stage 2 orchestration(segment横断の早期STOP)
# ============================================================
def run_stage2() -> dict:
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    cl.install(COST_LOG_PATH)

    segment_configs = build_segment_configs()
    results = []
    trial_early_stop = None

    for seg_cfg in segment_configs:
        if trial_early_stop is not None:
            results.append({
                "segment_id": seg_cfg["segment_id"], "final_status": "NOT_ATTEMPTED_DUE_TO_EARLY_STOP",
                "rationale": seg_cfg["rationale"], "required": seg_cfg["required"],
            })
            continue

        log(f"=== segment: {seg_cfg['segment_id']} (required={seg_cfg['required']}) ===")
        seg_result = run_segment(seg_cfg)
        seg_result["required"] = seg_cfg["required"]
        results.append(seg_result)

        stop = seg_result.get("early_stop")
        if stop and stop.get("reason") in (
                "OFF_SCRIPT_SPEECH_DETECTED", "INSTRUCTION_TEXT_LEAKED",
                "ALL_ATTEMPTS_EXHAUSTED_WITHOUT_PASS"):
            trial_early_stop = {
                "stopped_at_segment": seg_cfg["segment_id"],
                "reason": stop.get("reason"), "detail": stop.get("detail"),
            }
            log(f"  [TRIAL STOP] {trial_early_stop}")

    total_jpy, total_by_provider = compute_cost_jpy_so_far(None)
    result = {
        "management_id": "TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01",
        "stage": "Stage 2 (2-3 segments)",
        "segments": results,
        "trial_early_stop": trial_early_stop,
        "standard_attempts_budget": STANDARD_ATTEMPTS, "total_attempts_budget": TOTAL_ATTEMPTS,
        "attempt_styles_used": ATTEMPT_STYLES,
        "cost_jpy_total": round(total_jpy, 2),
        "cost_jpy_by_provider": total_by_provider,
        "budget_cap_jpy_per_segment": BUDGET_JPY_CAP_PER_SEGMENT,
        "budget_cap_jpy_total": BUDGET_JPY_CAP_TOTAL,
    }

    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


if __name__ == "__main__":
    r = run_stage2()
    printable = {k: v for k, v in r.items() if k != "segments"}
    printable["segments_summary"] = [
        {k2: v2 for k2, v2 in s.items() if k2 != "attempts_log"} for s in r["segments"]
    ]
    print(json.dumps(printable, ensure_ascii=False, indent=2))
    print(f"\n[written] {RESULT_PATH}")
