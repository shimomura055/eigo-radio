# ============================================================
# er022_tts_gemini_3_8_flash_lite_next_trial_01_stage3.py
# TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01 (Stage 3: 1記事全segment、
# Family X Hormuz B1B、role別speech_metadata styleでの記事全体安定性検証)
# ============================================================
# 性質: Trial限定(最大到達Status=VALIDATED、Production採用しない、
# Production挙動は無変更)。実行は `.venv_trial_genai225`
# (google-genai==2.25.0)からのみ行う。Stage 1/2 script
# (er022_..._stage1.py/_stage2.py)は本タスクで一切変更していない
# (新規ファイルとしてStage 3ロジックを追加しただけ)。
#
# 呼び出し形状: Stage 1/2と同じ(GenerateContent APIのPart.speech_metadata
# でstyleを渡す。本文[text]はverbatim、既存canonical本文を一切変更しない)。
# Stage 1/2との違い:
#   1. 対象segmentをFamily X Hormuz B1B 1記事全体(12segment)へ拡張。
#   2. attempt1のstyleを空文字列ではなく、role別の必要最小限style
#      (委任文Stage3内容2の例に対応。Full Story=calm steady news
#      narration、Comment/Preview=calm conversational、Heading=brief and
#      clear、In One Line=concise clear、Topic Intro=brief clear engaging)
#      とする。attempt2/3のfallback styleはStage1/2と同一
#      ("natural, clear, conversational" / "clear")。
#   3. Stage 2で発見したscript bug(ASR呼び出しがsegment_context外で
#      raw usage logのsegment=Noneになる)を修正: TTS呼び出しとASR呼び出し
#      の両方を同じcl.segment_context(segment_id)ブロック内で行う。
#
# 対象segment(Family X Hormuz B1B、hormuz__run_02/b1b、Production正規化
# 済みtext・voice割当・style prefixをread-onlyで読み取る):
#   topic_intro(Charon) / preview(Charon) / comment_1-4(Charon) /
#   full_story_part1(Aoede) / full_story_part2_heading(Aoede) /
#   full_story_part2(Aoede、既存OK音声なし=時刻コロンGate STOPPED中だが
#   Production正規化済みtextは存在するためTrialでは実行対象とする) /
#   full_story_part3_heading(Aoede) / full_story_part3(Aoede) /
#   in_one_line(Aoede)。計12segment。
#
# 現行Production側のrole/pacing実態(read-onlyでコード確認済み、
# er019_family_x_audio_production_runner_01.generate_family_x_b1_segments・
# er003_v1_n3_01_tts_generate.py):
#   - topic_intro: voice01.generate_charon_english(style override無し
#     =p9a.ENGLISH_STYLE_PREFIX素のまま、Level2 animated)。
#   - preview/comment_1-4: voice01.generate_charon_english(
#     style_prefix_override=B1_PREVIEW_STYLE_PREFIX_CALM
#     =ENGLISH_STYLE_PREFIX+"Speak this in a calm, clear, unhurried
#     tone..."、ユーザー正式承認済みcalm instruction)。
#   - full_story_part1/2/3, in_one_line: news_tail_fix.
#     generate_news_narration_wide_margin(style override無し
#     =ENGLISH_STYLE_PREFIX素のまま、Level2 animated、末尾trim margin
#     のみ広い。pace指示は無し)。
#   - full_story_part2_heading/3_heading: point_headings.generate(
#     ENGLISH_STYLE_PREFIX、fallback時のみMINIMAL_INSTRUCTION)。
#   - A2 6% slowdown post-process(er008_a2_postprocess_slowdown_01)は
#     A2レベル専用(A2_SLOWDOWN_TARGET_SEGMENTS)であり、B1B側の本記事
#     segmentには一切適用されていない(read-only確認済み、Production
#     非変更)。
#
# Cost Guard: 委任文Stage3内容(費用)の指示通り、segment単位上限¥100、
# Stage3合計上限¥600(事前ガード方式、Stage1/2と同型のcompute_cost_jpy_
# so_far()/assert_budget_ok()をsegment単位フィルタと合計の両方で拡張)。
#
# 実行方法:
#   .venv_trial_genai225/Scripts/python.exe \
#     er022_tts_gemini_3_8_flash_lite_next_trial_01_stage3.py
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

OUT_DIR = "er022_output/tts_gemini_3_8_flash_lite_next_trial_01/stage3"
NARR_DIR = f"{OUT_DIR}/narration"
AUDIT_DIR = f"{OUT_DIR}/audit"
COST_LOG_PATH = f"{AUDIT_DIR}/raw_usage_log.jsonl"
RESULT_PATH = f"{AUDIT_DIR}/stage3_result.json"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"

HORMUZ_B1B_DIR = ("er019_output/family_x_audio_production_wiring_01/"
                   "family_x_b3_diversity_trial_01/hormuz__run_02/b1b")

MODEL_B = "gemini-3.8-flash-lite-tts"
USD_JPY = 160.0

# 委任文Stage3内容(費用): segment単位上限¥100、Stage3合計上限¥600。
BUDGET_JPY_CAP_PER_SEGMENT = 100.0
BUDGET_JPY_CAP_TOTAL = 600.0
WORST_CASE_OUTPUT_TOKENS_PER_ATTEMPT = 16384

STANDARD_ATTEMPTS = review_lock.PRODUCTION_STANDARD_TTS_ATTEMPTS
TOTAL_ATTEMPTS = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS

# 記事内の役割順序(Family X Hormuz B1B segment_plan.json通り)。
# voice割当・roleはer019_family_x_audio_production_runner_01.
# generate_family_x_b1_segments()のコード読み取りに基づく(read-only、
# Production非変更)。
ARTICLE_ORDER = [
    "topic_intro", "preview", "comment_1", "full_story_part1", "comment_2",
    "full_story_part2_heading", "full_story_part2", "comment_3",
    "full_story_part3_heading", "full_story_part3", "comment_4", "in_one_line",
]

SEGMENT_ROLE = {
    "topic_intro": "TOPIC_INTRO",
    "preview": "PREVIEW",
    "comment_1": "COMMENT", "comment_2": "COMMENT",
    "comment_3": "COMMENT", "comment_4": "COMMENT",
    "full_story_part1": "FULL_STORY", "full_story_part2": "FULL_STORY",
    "full_story_part3": "FULL_STORY",
    "full_story_part2_heading": "HEADING_READOUT",
    "full_story_part3_heading": "HEADING_READOUT",
    "in_one_line": "IN_ONE_LINE",
}

SEGMENT_VOICE = {
    "topic_intro": "Charon", "preview": "Charon",
    "comment_1": "Charon", "comment_2": "Charon",
    "comment_3": "Charon", "comment_4": "Charon",
    "full_story_part1": "Aoede", "full_story_part2": "Aoede",
    "full_story_part3": "Aoede",
    "full_story_part2_heading": "Aoede", "full_story_part3_heading": "Aoede",
    "in_one_line": "Aoede",
}

# 現行Production側のrole/pacing意図(read-only確認結果、REPORT参照)。
PRODUCTION_STYLE_NOTE = {
    "TOPIC_INTRO": "voice01.generate_charon_english、override無し=ENGLISH_STYLE_PREFIX素のまま(Level2 animated)。pace指示無し。",
    "PREVIEW": "voice01.generate_charon_english、style_prefix_override=B1_PREVIEW_STYLE_PREFIX_CALM(ENGLISH_STYLE_PREFIX+\"calm, clear, unhurried tone\"、ユーザー正式承認済み)。",
    "COMMENT": "voice01.generate_charon_english、style_prefix_override=B1_PREVIEW_STYLE_PREFIX_CALM(同上、Comment1-4にも適用対象拡大済み)。",
    "FULL_STORY": "news_tail_fix.generate_news_narration_wide_margin、override無し=ENGLISH_STYLE_PREFIX素のまま(Level2 animated)。pace指示無し。末尾trim marginのみ0.35秒(通常0.08秒より広い、音声の演技指示ではない)。",
    "HEADING_READOUT": "point_headings.generate、ENGLISH_STYLE_PREFIX(fallback時のみMINIMAL_INSTRUCTION)。pace指示無し。",
    "IN_ONE_LINE": "news_tail_fix.generate_news_narration_wide_margin、override無し=ENGLISH_STYLE_PREFIX素のまま(Level2 animated)。pace指示無し。",
}

# Trial側 role別最小styleの3段attempt(委任文Stage3内容2の例に対応)。
# attempt1=role別最小style、attempt2/3はStage1/2と同一fallback。
ROLE_ATTEMPT1_STYLE = {
    "TOPIC_INTRO": "brief, clear, engaging news topic introduction",
    "PREVIEW": "calm, conversational",
    "COMMENT": "calm, conversational",
    "FULL_STORY": "calm, steady news narration",
    "HEADING_READOUT": "brief and clear",
    "IN_ONE_LINE": "concise, clear",
}
FALLBACK_STYLES = ["natural, clear, conversational", "clear"]

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


def _wav_duration_seconds(path: str) -> float | None:
    """既存Production audit JSONにtrim_info(duration)が無いsegment
    (Heading Readout等)向けに、実wavファイルから長さを読み取るだけの
    read-onlyヘルパー(既存artifactは一切書き換えない)。"""
    if not path or not os.path.exists(path):
        return None
    with wave.open(path, "rb") as w:
        return round(w.getnframes() / w.getframerate(), 4)


def build_segment_configs() -> list[dict]:
    results = _load_json(f"{HORMUZ_B1B_DIR}/audit/tts_generation_results.json")["segments"]
    segments = []
    for segment_id in ARTICLE_ORDER:
        rec = results[segment_id]
        role = SEGMENT_ROLE[segment_id]
        voice = SEGMENT_VOICE[segment_id]
        canonical_text = rec["canonical_text"]
        has_existing_audio = rec.get("status") == "OK" and rec.get("path")
        cfg = {
            "segment_id": segment_id,
            "language": "en",
            "role": role,
            "voice": voice,
            "canonical_text": canonical_text,
            "production_style_note": PRODUCTION_STYLE_NOTE[role],
            "attempt_styles": [ROLE_ATTEMPT1_STYLE[role]] + FALLBACK_STYLES,
        }
        if has_existing_audio:
            cfg["a_wav_path"] = rec["path"]
            a_dur = rec.get("trim_info", {}).get("trimmed_duration_seconds")
            if a_dur is None:
                a_dur = _wav_duration_seconds(rec["path"])
            cfg["a_duration_seconds"] = a_dur
            cfg["a_model"] = "gemini-2.5-pro-preview-tts"
            cfg["a_voice"] = voice
            cfg["a_instruction_type"] = rec.get("instruction_type")
            cfg["a_existing_audio"] = True
        else:
            cfg["a_wav_path"] = None
            cfg["a_duration_seconds"] = None
            cfg["a_model"] = None
            cfg["a_voice"] = None
            cfg["a_instruction_type"] = None
            cfg["a_existing_audio"] = False
            cfg["a_missing_reason"] = rec.get("reason", "既存Production OK音声なし")
        segments.append(cfg)
    return segments


# ============================================================
# Part 1: Cost Guard(segment単位¥100 + Stage3合計¥600の二重ガード)
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
    segment単位¥100、Stage3合計¥600の両方をチェックする
    (委任文Stage3内容: 「segment単位上限¥100、Stage 3合計上限¥600」)。"""
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
            f"Stage3 cap {BUDGET_JPY_CAP_TOTAL} JPY. Stopping before the call ({note}).")
    return seg_jpy


# ============================================================
# Part 2: TTS呼び出し(Stage1/2と同一形状、speech_metadataでstyleを渡す)
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
    対応。Stage1/2と同一実装。"""
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
# Part 3: 本文外発話・指示文漏れ検知(Stage1/2と同一)
# ============================================================
_WORD_RE = re.compile(r"[a-zA-Z']+")


def canonical_word_overlap_fraction(canonical_text: str, asr_text: str) -> float:
    canon_words = {w.lower() for w in _WORD_RE.findall(canonical_text) if len(w) >= 4}
    asr_words = {w.lower() for w in _WORD_RE.findall(asr_text or "")}
    if not canon_words:
        return 1.0
    return len(canon_words & asr_words) / len(canon_words)


def detect_leaked_style_words(canonical_text: str, asr_text: str, style: str) -> list[str]:
    """指示文の読み上げ検知。styleの各単語がASR結果に含まれ、かつ
    canonical本文自体には元々含まれない単語のみを漏れとみなす(canonical
    本文中に偶然同じ単語が存在するケースの誤検知を避ける)。"""
    if not style:
        return []
    canon_lower = canonical_text.lower()
    asr_lower = (asr_text or "").lower()
    leaked = []
    for raw_word in re.split(r"[,\s]+", style):
        w = raw_word.strip().lower()
        if not w or len(w) < 4:
            continue
        if w in asr_lower and w not in canon_lower:
            leaked.append(w)
    return leaked


# ============================================================
# Part 4: segment単位のorchestration(Stage2 script bug修正版:
# TTS呼び出し+ASR呼び出しの両方を同じsegment_contextブロック内で行う)
# ============================================================
def run_segment(seg_cfg: dict) -> dict:
    segment_id = seg_cfg["segment_id"]
    canonical_text = seg_cfg["canonical_text"]
    out_path = f"{NARR_DIR}/{segment_id}.wav"
    tts_call_fn = make_tts_call_fn(MODEL_B, seg_cfg["voice"])
    attempt_styles = seg_cfg["attempt_styles"]

    attempts_log = []
    early_stop = None
    final_status = "ASR_VALIDATION_UNCERTAIN"
    final_asr_text = None
    final_duration = None

    for attempt in range(1, TOTAL_ATTEMPTS + 1):
        style = attempt_styles[attempt - 1]
        note = f"{segment_id} attempt {attempt}/{TOTAL_ATTEMPTS} (style={style!r})"

        try:
            assert_budget_ok(segment_id, note)
        except RuntimeError as e:
            early_stop = {"reason": "BUDGET_GUARD_STOP", "detail": str(e)}
            log(f"  [STOP] {early_stop}")
            break

        # Stage2で発見したbug修正: TTS呼び出し+ASR呼び出しの両方を同じ
        # segment_contextブロック内で行う(raw usage logのsegment付与漏れ防止)。
        with cl.segment_context(segment_id):
            t0 = time.time()
            try:
                raw = tts_call_fn(canonical_text, style)
            except Exception as e:
                tts_elapsed = round(time.time() - t0, 3)
                attempts_log.append({"attempt": attempt, "style": style, "status": "TTS_CALL_FAILED",
                                      "error": str(e)[:500], "tts_latency_seconds": tts_elapsed})
                continue
            tts_elapsed = round(time.time() - t0, 3)

            samples, framerate, wav_header_detected = decode_audio_bytes_defensive(raw)
            raw_duration = round(len(samples) / framerate, 4)

            anomaly = safety.detect_duration_anomaly(raw_duration, canonical_text, seg_cfg["language"])
            if anomaly["is_anomaly"]:
                attempts_log.append({
                    "attempt": attempt, "style": style, "status": "STOPPED_DURATION_ANOMALY",
                    "tts_latency_seconds": tts_elapsed, "wav_header_detected": wav_header_detected,
                    "duration_seconds": raw_duration, "anomaly": anomaly,
                })
                if attempt == TOTAL_ATTEMPTS:
                    early_stop = {"reason": "DURATION_ANOMALY_ON_FINAL_ATTEMPT", "detail": anomaly}
                continue

            common.write_wav_float(out_path, samples, framerate, 1)
            t1 = time.time()
            asr_text, asr_err = routing.transcribe(
                out_path, f"{seg_cfg['language']}-US" if seg_cfg["language"] == "en" else seg_cfg["language"])
            asr_elapsed = round(time.time() - t1, 3)

        if asr_err or asr_text is None:
            attempts_log.append({"attempt": attempt, "style": style, "status": "ASR_ERROR",
                                  "asr_error": asr_err, "tts_latency_seconds": tts_elapsed,
                                  "asr_latency_seconds": asr_elapsed,
                                  "wav_header_detected": wav_header_detected, "duration_seconds": raw_duration})
            continue

        # 実行中に発見し取りやめた変更(REPORTへ経緯を記録): Production
        # (er003_v1_n3_01_tts_generate等)はsegment_id=nameを渡してTier 1
        # 数値等価role gate(Full Story/Comment/Preview/Topic intro/
        # In One Line、er006_preprod_hardening_01_validation.
        # _resolve_semantic_equivalence_role)を有効化している。一度
        # segment_id=segment_idを渡す変更を試したが、この呼び出し経路は
        # 不合格判定時に共有store
        # (er021_output/en_asr_semantic_equivalence_production_wiring_01/
        # telemetry.jsonl)へ副作用として書き込みを行うことが判明し
        # (委任文で明示的に書き込み禁止と指定された共有store)、かつ本Trialの
        # 実データではTier1が一度も救済に寄与しなかった(segment_id有無で
        # 分類結果が完全一致することを検証済み)ため、Stage1/2と同じく
        # segment_idを渡さない形に戻した(Gate自体の変更ではない、単に
        # 共有store書き込みを避けるための不使用)。
        cls = en_validator.classify_asr_match(canonical_text, asr_text)
        metrics = common.measure_metrics(samples, framerate)
        leaked_style_words = detect_leaked_style_words(canonical_text, asr_text, style)
        entry = {
            "attempt": attempt, "style": style, "status": "OK_ASR_RAN",
            "asr_text": asr_text, "classification": cls.classification,
            "should_pass": cls.should_pass, "should_retry": cls.should_retry,
            "reason": cls.reason, "tts_latency_seconds": tts_elapsed,
            "asr_latency_seconds": asr_elapsed,
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
        "segment_id": segment_id, "role": seg_cfg["role"],
        "language": seg_cfg["language"], "voice": seg_cfg["voice"], "model": MODEL_B,
        "canonical_text_char_count": len(canonical_text),
        "production_style_note": seg_cfg["production_style_note"],
        "attempt_styles": attempt_styles,
        "a_reference": {
            "wav_path": seg_cfg["a_wav_path"],
            "duration_seconds": seg_cfg["a_duration_seconds"],
            "model": seg_cfg["a_model"], "voice": seg_cfg["a_voice"],
            "instruction_type": seg_cfg["a_instruction_type"],
            "existing_audio": seg_cfg["a_existing_audio"],
            "missing_reason": seg_cfg.get("a_missing_reason"),
        },
        "attempts_log": attempts_log,
        "attempt_count": len(attempts_log),
        "final_status": final_status if early_stop is None else "STOPPED",
        "early_stop": early_stop,
        "final_asr_text": final_asr_text,
        "final_duration_seconds": final_duration,
        "out_path": out_path if os.path.exists(out_path) else None,
        "cost_jpy_segment_total": round(seg_jpy, 2),
        "cost_jpy_segment_by_provider": seg_by_provider,
    }


# ============================================================
# Part 5: Stage 3 orchestration(記事全体、segment横断の早期STOP)
# ============================================================
def run_stage3() -> dict:
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    cl.install(COST_LOG_PATH)

    segment_configs = build_segment_configs()
    results = []
    trial_early_stop = None

    for seg_cfg in segment_configs:
        if trial_early_stop is not None:
            results.append({
                "segment_id": seg_cfg["segment_id"], "role": seg_cfg["role"],
                "final_status": "NOT_ATTEMPTED_DUE_TO_EARLY_STOP",
            })
            continue

        log(f"=== segment: {seg_cfg['segment_id']} (role={seg_cfg['role']}, voice={seg_cfg['voice']}) ===")
        seg_result = run_segment(seg_cfg)
        results.append(seg_result)

        stop = seg_result.get("early_stop")
        # 実行中に発見・修正した設計判断(委任文原文には明記が無いため、
        # 実装時の判断としてREPORTへ明記しFableへ報告する): 委任文の
        # 「3回失敗」早期STOPは、Production実物の挙動
        # (er019_family_x_audio_production_runner_01.
        # generate_family_x_b1_segments、read-only確認済み)に合わせ、
        # segment単位のSTOP(この1segmentのみ音声化断念、final_status=
        # STOPPEDのまま記録)として扱い、記事全体の残りsegment生成は
        # 継続する。根拠: 実際のProduction run(hormuz__run_02/b1b)でも
        # full_story_part2が時刻コロンGateでSTOPPEDのまま、
        # full_story_part3・in_one_line等の他segmentは同じrunでOKになって
        # おり、1segmentの失敗が記事全体の生成を止める設計にはなっていない
        # (tts_generation_results.json実物で確認)。一方、無関係内容の
        # 読み上げ(OFF_SCRIPT_SPEECH_DETECTED)・指示文の読み上げ
        # (INSTRUCTION_TEXT_LEAKED)・予算上限到達(BUDGET_GUARD_STOP)は、
        # 個別segmentの内容問題ではなくモデル/実行環境側の異常を示唆する
        # ため、委任文通り記事全体の早期STOP(残りsegment未実行)を維持する。
        if stop and stop.get("reason") in (
                "OFF_SCRIPT_SPEECH_DETECTED", "INSTRUCTION_TEXT_LEAKED", "BUDGET_GUARD_STOP"):
            trial_early_stop = {
                "stopped_at_segment": seg_cfg["segment_id"],
                "reason": stop.get("reason"), "detail": stop.get("detail"),
            }
            log(f"  [TRIAL STOP] {trial_early_stop}")

    total_jpy, total_by_provider = compute_cost_jpy_so_far(None)
    result = {
        "management_id": "TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01",
        "stage": "Stage 3 (1 article, 12 segments, Family X Hormuz B1B)",
        "article_dir": HORMUZ_B1B_DIR,
        "article_order": ARTICLE_ORDER,
        "segments": results,
        "trial_early_stop": trial_early_stop,
        "standard_attempts_budget": STANDARD_ATTEMPTS, "total_attempts_budget": TOTAL_ATTEMPTS,
        "role_attempt1_style": ROLE_ATTEMPT1_STYLE, "fallback_styles": FALLBACK_STYLES,
        "cost_jpy_total": round(total_jpy, 2),
        "cost_jpy_by_provider": total_by_provider,
        "budget_cap_jpy_per_segment": BUDGET_JPY_CAP_PER_SEGMENT,
        "budget_cap_jpy_total": BUDGET_JPY_CAP_TOTAL,
    }

    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


if __name__ == "__main__":
    r = run_stage3()
    printable = {k: v for k, v in r.items() if k != "segments"}
    printable["segments_summary"] = [
        {k2: v2 for k2, v2 in s.items() if k2 != "attempts_log"} for s in r["segments"]
    ]
    print(json.dumps(printable, ensure_ascii=False, indent=2))
    print(f"\n[written] {RESULT_PATH}")
