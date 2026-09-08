# ============================================================
# er012_b_family_voices_production_01.py
# 管理ID: EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01
# ============================================================
# Voices Family(B-Family)専用のProduction機能を1箇所へ集約する:
#   - 5区切り構造parser(split_five_voice_sections)
#   - Voice可用性チェック + fallback解決
#   - Voice A/B本文(Algieba/Erinome想定)専用TTS
#     (Production共有TTS primitiveをvoice指定でラップする形。設計案
#     [EDITORIAL-B-FAMILY-PRODUCTION-PATH-DESIGN-01_REPORT.md 第2-1節]は
#     「既存er003_v1_sing01_news_tail_fix.pyへ新関数追加」を代替案として
#     挙げていたが、実際にコード確認したところ、その関数が内部で使う
#     全primitive(er002_common._call_tts_with_retry・
#     er006_batch_tts_wiring_01.make_batch_tts_call_fn・
#     er003_b1_p4c_audio.build_tts_prompt・
#     er003_b1_p3u_audio.trim_english_keyword_silence・
#     er003_audio_tts_asr_safety.detect_duration_anomaly・
#     er006_secondary_asr_01.evaluate_attempt_with_cascade・
#     er008_disfluency_qa_18.apply_disfluency_gate・
#     er011_human_review_lock_01.save_tts_attempt_audio)はすでにvoice_name
#     を明示引数として受け取れる(hardcodeされているのは呼び出し側が
#     p9a.VOICE_NAME/CHARONを渡している箇所だけ)。したがって
#     「共有primitiveをvoice指定でラップする」だけで新規Voice A/B関数が
#     完成し、er003_v1_sing01_news_tail_fix.py自体には一切触れる必要が
#     ない(既存関数・定数を無変更のまま温存)。この判断はGate 3
#     チェックリストに基づきReportへ明記する。
#   - B-Family専用Assembly timeline builder(Tension slot対応、既存
#     er003_v1_n3_01_assemble.build_b1_timeline()は無変更のまま、
#     本ファイルへ新規関数として追加)
#
# 既存Production関数(er003_v1_n3_01_assemble.py [asm]・
# er003_v1_sing01_point_headings_aoede.py [point_headings]・
# er003_v1_sing01_news_tail_fix.py [news_tail_fix]・
# er003_v1_sing01_voice01_generate.py [voice01])は一切変更しない。
#
# Phase 2保留: 一人称"I"の機械的強制なし(er012_b_family_editorial_type_
# registry_01.PHASE2_PENDING_NOTES参照)。
#
# 修正指示1回目(Fable、初回Report §8-1指摘への対応): Voice A/B本文
# (generate_voice_body_wide_margin、point_one/point_two相当)へ、
# A-Family既存Production(er003_v1_n3_01_tts_generate.py 745-754行目)と
# 同一規約でOPEN-121(repetition QA)・OPEN-122(connected speech
# equivalence layer)を配線した(既定True)。詳細は
# EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01_REPORT.md
# 「修正指示1回目への対応」章を参照。
from __future__ import annotations

import re

import er002_common as common
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er006_asr_provider_routing_01 as asr_routing
import er006_batch_tts_wiring_01 as batch_wiring
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_secondary_asr_01 as secondary_asr
import er008_disfluency_qa_18 as dq18
import er011_human_review_lock_01 as review_lock
import er011_open121_repetition_qa_production_01 as repetition_qa
import er012_b_family_editorial_type_registry_01 as registry

EXTRA_SEGMENT_NAME = registry.EXTRA_SEGMENT_NAME  # "tension_reflection"

# ============================================================
# 5区切り構造parser(Trial-08/09由来、正式Production化)
# ============================================================
_HEADING_RE = re.compile(r"^(#{2,3})[ \t]+(.+?)\s*$", re.MULTILINE)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")

SECTION_LABEL_ORDER = ("hook", "voice_a", "voice_b", "tension", "closing")


def split_five_voice_sections(article_text: str) -> dict | None:
    """記事本文(# タイトル + 5つの##/### 見出し)を、B-Family Voices構造
    (hook/voice_a/voice_b/tension/closing)へ分解する。想定外の見出し数
    (5以外)の場合はNoneを返す(ガード、単体テスト対象)。"""
    title_match = re.match(r"^#[ \t]+.+?\s*\n", article_text)
    if not title_match:
        return None
    body = article_text[title_match.end():]
    matches = list(_HEADING_RE.finditer(body))
    if len(matches) != 5:
        return None
    result = {}
    for i, label in enumerate(SECTION_LABEL_ORDER):
        heading_text = matches[i].group(2).strip()
        content_start = matches[i].end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        result[f"{label}_heading"] = heading_text
        result[f"{label}_body"] = body[content_start:content_end].strip()
    result["unexpected_preamble_before_first_heading"] = body[:matches[0].start()].strip()
    return result


def extract_title(article_text: str) -> str:
    m = re.match(r"^#\s+(.+?)\s*\n", article_text)
    if not m:
        raise RuntimeError("記事タイトル(# 見出し)が見つかりません")
    return m.group(1).strip()


def ensure_period(s: str) -> str:
    s = s.strip()
    return s if s.endswith((".", "!", "?")) else s + "."


def split_two_balanced_by_sentence(text: str) -> tuple:
    """Hookを2つのTTS segmentへ均等に近い形で分割する(Assembly側で小さい
    pauseで連続再生し、聞こえ方は単一のHookブロックになる)。"""
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
    if len(sentences) < 2:
        raise RuntimeError(f"Hookの文数が2未満です(検出数: {len(sentences)})")
    word_counts = [len(re.findall(r"[A-Za-z']+", s)) for s in sentences]
    total = sum(word_counts)
    running = 0
    best_diff = None
    split_idx = 1
    for i in range(1, len(sentences)):
        running += word_counts[i - 1]
        diff = abs(running - (total - running))
        if best_diff is None or diff < best_diff:
            best_diff = diff
            split_idx = i
    part1 = " ".join(sentences[:split_idx])
    part2 = " ".join(sentences[split_idx:])
    return part1, part2


def first_n_sentences(text: str, n: int) -> str:
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
    return " ".join(sentences[:n])


def build_parts(article_text: str) -> dict:
    sections = split_five_voice_sections(article_text)
    if sections is None:
        raise RuntimeError("5区切り構造の検出に失敗しました(想定と異なる見出し構成)")
    title = extract_title(article_text)
    hook_part1, hook_part2 = split_two_balanced_by_sentence(sections["hook_body"])
    return {
        "title": title,
        "part1": hook_part1, "part2": hook_part2,
        "point_one_heading": ensure_period(sc.clean_heading(sections["voice_a_heading"])),
        "point_one_body": sections["voice_a_body"],
        "point_two_heading": ensure_period(sc.clean_heading(sections["voice_b_heading"])),
        "point_two_body": sections["voice_b_body"],
        "in_one_line": sections["closing_body"],
        "tension_heading": sections["tension_heading"],
        "tension_body": sections["tension_body"],
        "_five_section_headings": {k: sections[k] for k in
                                    ("hook_heading", "voice_a_heading", "voice_b_heading",
                                     "tension_heading", "closing_heading")},
    }


# ============================================================
# Voice可用性チェック + fallback解決
# ============================================================
def generate_voice_sample_single_take(text: str, out_path: str, voice_name: str) -> dict:
    """比較sample専用の単発生成(ASR検証・retry cascadeは行わない、可用性
    確認のみ)。既存p4c.build_tts_prompt+batch_wiring.make_batch_tts_call_fn
    +p3u.trim_english_keyword_silenceはProductionと同じ呼び出しパターン。"""
    import os
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    call_fn = batch_wiring.make_batch_tts_call_fn(p9a.ENGLISH_MODEL_NAME, voice_name, output_path=out_path)
    prompt = p4c.build_tts_prompt(text, p9a.ENGLISH_STYLE_PREFIX)
    try:
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    except Exception as e:
        return {"status": "ERROR", "voice": voice_name, "text": text, "error": f"{type(e).__name__}: {e}"}
    if not ok:
        return {"status": "ERROR", "voice": voice_name, "text": text, "error": str(err)}
    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(samples_raw, common.SAMPLE_RATE, safety_margin_seconds=0.35)
    if trimmed is None:
        return {"status": "ERROR", "voice": voice_name, "text": text, "error": "発話区間検出失敗"}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    return {"status": "OK", "voice": voice_name, "text": text, "path": out_path,
            "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4)}


def run_voice_availability_check(sample_text: str, sample_dir: str,
                                  voice_names: tuple = None) -> dict:
    voice_names = voice_names or (registry.VOICE_ASSIGNMENT["voice_a"], registry.VOICE_ASSIGNMENT["voice_b"])
    results = {}
    for voice_name in voice_names:
        path = f"{sample_dir}/sample_{voice_name.lower()}.wav"
        print(f"[B-FAMILY-VOICES-PROD][voice-check] {voice_name} sample生成...")
        r = generate_voice_sample_single_take(sample_text, path, voice_name)
        results[voice_name] = r
        print(f"[B-FAMILY-VOICES-PROD][voice-check] {voice_name}: status={r.get('status')}")
    return results


def resolve_voice_names(sample_results: dict) -> tuple:
    """registryのvoice_assignment/voice_fallbackに基づき、実際に使う
    Voice A/Bの声名を決定する(technical availabilityに基づくfallbackのみ、
    editorialな理由での切替はしない)。単体テスト対象。"""
    reasons = {}
    voice_a_candidate = registry.VOICE_ASSIGNMENT["voice_a"]
    voice_b_candidate = registry.VOICE_ASSIGNMENT["voice_b"]
    voice_a_fallback = registry.VOICE_FALLBACK["voice_a"]
    voice_b_fallback = registry.VOICE_FALLBACK["voice_b"]
    voice_a = voice_a_candidate
    voice_b = voice_b_candidate
    if sample_results.get(voice_a_candidate, {}).get("status") != "OK":
        voice_a = voice_a_fallback
        reasons["voice_a"] = (f"{voice_a_candidate}が技術的に利用不可("
                               f"{sample_results.get(voice_a_candidate, {}).get('error')})のため"
                               f"{voice_a_fallback}へ変更")
    if sample_results.get(voice_b_candidate, {}).get("status") != "OK":
        voice_b = voice_b_fallback
        reasons["voice_b"] = (f"{voice_b_candidate}が技術的に利用不可("
                               f"{sample_results.get(voice_b_candidate, {}).get('error')})のため"
                               f"{voice_b_fallback}へ変更")
    return voice_a, voice_b, reasons


# ============================================================
# Voice A/B本文専用TTS(共有Production primitiveをvoice指定でラップ)
# ============================================================
@review_lock.guarded_generate("en")
def generate_voice_body_minimal_fallback(
        text: str, out_path: str, voice_name: str,
        safety_margin_seconds: float = p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS) -> dict:
    """MINIMAL_INSTRUCTION経路(声のみ変更、他ロジックは
    repro01.generate_english_component_minimal_instruction()と同一パターン)。
    Voice A/B fallback専用。"""
    prompt = p4c.build_tts_prompt(text, repro01.MINIMAL_INSTRUCTION_PREFIX)
    call_fn = batch_wiring.make_batch_tts_call_fn(p9a.ENGLISH_MODEL_NAME, voice_name, output_path=out_path)
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"status": "STOPPED", "reason": f"minimal instructionでもTTS失敗: {err}"}
    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=safety_margin_seconds)
    if trimmed is None:
        return {"status": "STOPPED", "reason": "発話区間を検出できませんでした"}
    anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
    if anomaly["is_anomaly"]:
        return {"status": "STOPPED", "reason": anomaly["reason"], "duration_anomaly": anomaly}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
    return {
        "status": "OK", "text": text, "path": out_path, "model": p9a.ENGLISH_MODEL_NAME,
        "voice": voice_name, "call_count": 1 + retries, "retry_count": retries,
        "sha256": p9a.sha256_file(out_path), "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
        "trim_info": trim_info, "clipping_detected": metrics["clipping_detected"],
        "instruction": "minimal (not ENGLISH_STYLE_PREFIX)",
    }


@review_lock.guarded_generate("en")
def generate_voice_body_wide_margin(text: str, out_path: str, voice_name: str,
                                     max_attempts: int = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS,
                                     max_extra_chars: int = 15,
                                     # EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01
                                     # 修正指示1回目: Voice A/B本文(point_one/point_two相当)は
                                     # A-Family既存Production(er003_v1_n3_01_tts_generate.py
                                     # 745-754行目)がfull_story_part1/2・point_one・point_two
                                     # 4segment全てで有効化しているOPEN-122/OPEN-121と同じ
                                     # 規約対象のため、既定Trueとする(Voice A/B呼び出しは
                                     # 常にこの4segment集合の一員であり、A-Familyと同一挙動)。
                                     enable_connected_speech_equivalence_layer: bool = True,
                                     enable_repetition_qa: bool = True) -> dict:
    """Voice A/B本文専用の正式Production TTS関数。既存
    news_tail_fix.generate_news_narration_wide_margin()と同一のASR検証・
    Cascade・disfluency gate・repetition QA・connected speech equivalence
    layer・attempt保存ロジックを、共有primitiveから直接組み立てる
    (voice_nameのみ呼び出し側で指定可能にする)。news_tail_fix.py自体は
    無変更のまま。"""
    max_len = len(text) + max_extra_chars
    attempts_log = []
    classification_history = []
    for attempt in range(1, max_attempts + 1):
        call_fn = batch_wiring.make_batch_tts_call_fn(p9a.ENGLISH_MODEL_NAME, voice_name, output_path=out_path)
        prompt = p4c.build_tts_prompt(text, p9a.ENGLISH_STYLE_PREFIX)
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        instruction_type = "english_style_prefix_wide_margin"
        if ok:
            samples_raw = common.pcm_bytes_to_float_mono(pcm)
            trimmed, trim_info = p3u.trim_english_keyword_silence(
                samples_raw, common.SAMPLE_RATE,
                safety_margin_seconds=news_tail_fix.LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS)
            if trimmed is not None:
                anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
                if anomaly["is_anomaly"]:
                    trimmed = None
                    err = anomaly["reason"]
        else:
            trimmed, trim_info = None, None

        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED",
                                  "reason": str(err) if not ok else "発話区間検出失敗",
                                  "instruction_type": instruction_type})
            r = generate_voice_body_minimal_fallback(text, out_path, voice_name)
            instruction_type = "minimal_fallback"
            if r.get("status") != "OK":
                attempts_log.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason"),
                                      "instruction_type": instruction_type})
                continue
        else:
            common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)

        asr_text, asr_err = asr_routing.transcribe(out_path, language="en-US")
        length_ok = asr_text is not None and len(asr_text) <= max_len
        ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(text, min_confidence="low")]
        verified_content, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
            text, asr_text, classification_history, out_path, language="en-US",
            ledger_phrases=ledger_phrases, cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED,
            enable_connected_speech_equivalence_layer=enable_connected_speech_equivalence_layer)
        verified = verified_content and length_ok
        gate = dq18.apply_disfluency_gate(verified, out_path, language="en", enabled=False)
        verified = gate["verified"]
        # OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01: 既存disfluency
        # gateと同一のANDゲートパターン(er003_v1_sing01_news_tail_fix.py
        # 118-124行目と同一規約)。
        rep_gate = repetition_qa.apply_repetition_qa_gate(
            verified, out_path, text, language="en", enabled=enable_repetition_qa)
        verified = rep_gate["verified"]
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "instruction_type": instruction_type, "audio_classification": cls.classification,
                              "connected_speech_info": getattr(cls, "connected_speech_info", None),
                              "length_ok": length_ok, "verified": verified,
                              "trim_info": trim_info, "disfluency_checked": gate["disfluency_checked"],
                              "disfluency_evidence": gate.get("disfluency_evidence"),
                              "repetition_qa_checked": rep_gate["repetition_qa_checked"],
                              "repetition_qa_evidence": rep_gate.get("repetition_qa_evidence")})
        _attempt_audio_path = review_lock.save_tts_attempt_audio(out_path, instruction_type, {
            "loop_attempt_index": attempt, "max_attempts": max_attempts, "language": "en",
            "model": p9a.ENGLISH_MODEL_NAME, "voice": voice_name,
            "tts_execution_mode": batch_wiring.resolve_tts_execution_mode(),
            "asr_text": asr_text, "audio_classification": cls.classification,
            "length_ok": length_ok, "verified": verified,
            "disfluency_checked": gate["disfluency_checked"],
            "disfluency_evidence": gate.get("disfluency_evidence"),
            "repetition_qa_checked": rep_gate["repetition_qa_checked"],
            "repetition_qa_evidence": rep_gate.get("repetition_qa_evidence"),
        })
        attempts_log[-1]["attempt_audio_path"] = _attempt_audio_path
        if verified:
            metrics = common.measure_metrics(common.read_wav_float(out_path)[0], common.SAMPLE_RATE)
            return {"status": "OK", "text": text, "path": out_path, "voice": voice_name, "asr_verified": True,
                    "asr_text": asr_text, "attempts_log": attempts_log, "instruction_type": instruction_type,
                    "trim_info": trim_info, "safety_margin_seconds": news_tail_fix.LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS,
                    "clipping_detected": metrics["clipping_detected"], "audio_classification": cls.classification,
                    "connected_speech_info": getattr(cls, "connected_speech_info", None),
                    "disfluency_checked": gate["disfluency_checked"], "disfluency_evidence": gate.get("disfluency_evidence"),
                    "repetition_qa_checked": rep_gate["repetition_qa_checked"],
                    "repetition_qa_evidence": rep_gate.get("repetition_qa_evidence")}
        if stop_retrying:
            metrics = common.measure_metrics(common.read_wav_float(out_path)[0], common.SAMPLE_RATE)
            return {"status": "ASR_VALIDATION_UNCERTAIN", "text": text, "path": out_path, "voice": voice_name,
                    "asr_verified": False, "asr_text": asr_text, "attempts_log": attempts_log,
                    "instruction_type": instruction_type, "trim_info": trim_info,
                    "safety_margin_seconds": news_tail_fix.LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS,
                    "clipping_detected": metrics["clipping_detected"],
                    "reason": f"同一ASR mismatch signatureが連続し、retryでの改善が見込めないため打ち切り"
                              f"(最終classification={cls.classification})"}
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log, "voice": voice_name}


# ============================================================
# B-Family専用Assembly timeline builder(Tension slot対応)
# 既存asm.build_b1_timeline()(11-part固定)は無変更のまま、新規関数として
# 追加する。既存Production primitive(asm.build_b1_key_phrase_blocks・
# p9a.silence_stereo・asm.AOEDE_TO_CHARON_PAUSE_SECONDS等の共有pause定数)は
# 無変更のまま呼ぶ。
# ============================================================
def build_b1_voices_timeline(parts: dict, voice_a: str, voice_b: str) -> list:
    """Hook/Comment1/One Voice(heading+body)/Comment2/Another Voice
    (heading+body)/Comment3/Tension/Comment4/Closingという、B-Family
    Voices構造(5区切り)のtimelineを構築する。Key Phrase位置は既存B1構造
    どおりPreview直後(2026-09-08ユーザー承認: 現状維持)。"""
    key_phrase_blocks = asm.build_b1_key_phrase_blocks(parts)
    b1 = parts["b1_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome (Charon)", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro (Charon)", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro (Charon)", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Preview (Charon)", b1["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro (Charon)", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = tuple(f"Key Phrase {i}" for i in range(1, len(key_phrase_blocks) + 1))
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro (Charon)", parts["full_story_intro"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 1 (Charon)", b1["comment_1"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Hook Part 1: The Question (Aoede, no heading)", b1["full_story_part1"]),
        ("pause_0.25_hook_internal", p9a.silence_stereo(0.25)),
        ("Hook Part 2: The Question (Aoede, no heading)", b1["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 2 (Charon, bridge to Voices)", b1["comment_2"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice A cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: One Voice heading (Aoede)", b1["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice A body ({voice_a})", b1["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice B cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: Another Voice heading (Aoede)", b1["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice B body ({voice_b})", b1["point_two"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 3 (Charon)", b1["comment_3"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Tension: Where the Difference Comes From (Aoede, no heading)", b1[EXTRA_SEGMENT_NAME]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Charon)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Closing: What the Seat Really Means (Aoede, no heading, In One Line)", b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(asm.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon)", parts["outro"]),
    ]
    return seq
