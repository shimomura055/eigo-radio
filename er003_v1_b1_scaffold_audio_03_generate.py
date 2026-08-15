# ============================================================
# er003_v1_b1_scaffold_audio_03_generate.py
# ER-003-B1-SCAFFOLD-AUDIO-03: B1 Audio Language/Voice Separation 修正版
# ============================================================
# AUDIO-02完成版候補のユーザー試聴で見つかった3件の問題を修正する:
#   1. A2から継承したAudio Shellに残っていた日本語ナレーション
#      (Japanese title / Point explanation)をB1では廃止・英語化する
#      (Key Phrasesの日本語訳のみが許可される唯一の日本語領域)
#   2. Preview末尾"prove"の音切れ(語尾フリケイティブの途中でtrimが
#      cutしていたバグ)を、trim安全マージンを広げて修正する
#   3. B2 NewsとB1 Commentが同一voice(Aoede)だったため、Comment1-4のみ
#      Charon voiceへ変更し、聴覚的な役割の区別を作る(Prototype)
#
# Production本体・記事本文(Support/News)のテキスト自体は変更しない。
# B2共通News本文・Key Phrasesは無変更(音声も再利用、再生成しない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_scaffold_audio_03_generate.py

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er002_gemini_client as gclient
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4_audio as p4
import er003_b1_p9a_audio as p9a
import er003_v1_a2_audio_02_generate as audio02
import er003_v1_b1_scaffold_01_generate as scaffold
import er003_v1_b1_scaffold_audio_01_generate as audio01b
import er003_v1_b1_scaffold_audio_02_generate as audio02b
import er003_v1_repro01_main_generate as repro01

ARTICLE_ID = "A02"
OUT_DIR = "er003_output/b1_scaffold_audio_03/A02"
NARRATION_DIR = f"{OUT_DIR}/narration"
SR = p9a.TARGET_SAMPLE_RATE

B1_NARRATION_DIR_V1 = "er003_output/b1_scaffold_audio_01/A02/narration"  # AUDIO-01生成、Full Story等はここから無変更で再利用

# ------------------------------------------------------------
# Shell定数(AUDIO-02から無変更で継承。新しい値は作らない)
# ------------------------------------------------------------
POINT_EXPLANATION_PAUSE_SECONDS = audio02.POINT_EXPLANATION_PAUSE_SECONDS  # 0.7
OUTRO_EXTRA_GAIN_LINEAR = audio02.OUTRO_EXTRA_GAIN_LINEAR
OUTRO_FURTHER_EXTRA_GAIN_LINEAR = audio02.OUTRO_EXTRA_GAIN_LINEAR
POINT1_TO_POINT2_PAUSE_SECONDS = 0.8
IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS = 0.8
COMMENT_EN_TO_JA_PAUSE_SECONDS = 0.8  # 名称はA2由来だがB1ではEN→EN間(AUDIO-02 F節を継承)
COMMENT_JA_TO_EN_PAUSE_SECONDS = 0.8

KEY_PHRASES = audio01b.KEY_PHRASES  # 無変更(section 13)

# 新規B1英語Shellナレーション(C節: 役割は維持、言語のみ英語化)
POINT_EXPLANATION_EN_TEXT = "Here's the point."
# Japanese titleは廃止(読み上げない)。代替の英語再読み上げは行わない
# (Topic introが既に英語でタイトルを読み上げ済みのため、二重読み上げに
# しない、というB節の判断)。

COMMENT_VOICE_NAME = "Charon"  # 過去記録上ナレーター実績のある男性voice(11節)
NEWS_VOICE_NAME = p9a.VOICE_NAME  # "Aoede"、News/Preview/Shellは無変更(10節)

# Preview語尾切れ対策: Key Phrase単語向けの既定マージン(0.08秒、
# p3u.EN_TRIM_SAFETY_MARGIN_SECONDS)は、長文の語尾フリケイティブ/decay
# には不足していたため(C節根本原因)、長文専用に広げたマージンを使う。
# p3u.trim_english_keyword_silence自体は変更せず、呼び出し時の引数のみ
# 変える(Production非変更)。
LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS = 0.35


# ============================================================
# Step 1: 新規B1英語Shellナレーション(Point explanation英語版)
# ============================================================
def _point_explanation_primary(text: str, out_path: str) -> dict:
    return p9a.generate_narration_snippet(text, "en", out_path)


def _point_explanation_fallback(text: str, out_path: str) -> dict:
    return repro01.generate_english_component_minimal_instruction(text, out_path)


def generate_point_explanation_en(text: str, out_path: str, max_attempts: int = 6) -> dict:
    """既存service-level narration(preview_intro/full_story_intro等)と
    同じENGLISH_STYLE_PREFIX経路を主経路にし、失敗時のみMINIMAL_
    INSTRUCTION経路へfallbackする(er003_audio_tts_asr_safety.
    generate_tts_with_fallbackを再利用、HARDENING-01の成果をAUDIO-03へ
    再利用する、というユーザー指示section 17に対応)。"""
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        r = safety.generate_tts_with_fallback(text, out_path, _point_explanation_primary, _point_explanation_fallback)
        if r.get("status") != "OK":
            attempts_log.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason")})
            continue
        asr_text, asr_err = p4.get_full_text_via_azure_stt_continuous(out_path, language="en-US")
        match = safety.validate_asr_match(text, asr_text, asr_error=asr_err)
        attempts_log.append({"attempt": attempt, "status": "OK", "instruction_type": r.get("instruction_type"),
                              "asr_text": asr_text, "asr_verdict": match["verdict"], "verified": match["passed"]})
        if match["passed"]:
            r["asr_verified"] = True
            r["asr_text"] = asr_text
            r["asr_match"] = match
            r["attempts_log"] = attempts_log
            return r
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log}


# ============================================================
# Step 2: 長文Support(Preview/Comment)音声 — trim安全マージン修正版
# ============================================================
def generate_long_form_narration_verified(text: str, out_path: str, voice_name: str,
                                           max_attempts: int = 6, max_extra_chars: int = 15,
                                           safety_margin_seconds: float = LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS) -> dict:
    """AUDIO-01のgenerate_support_narration_verifiedと同じMINIMAL_
    INSTRUCTION経路+ASR検証を使うが、以下2点を修正する:
      1. trim安全マージンを0.08秒(Key Phrase単語向けの既定値)ではなく
         0.35秒(長文の語尾decay向け)にする(C節: Preview"prove"語尾
         切れの根本原因への対策)
      2. voice_nameを指定可能にする(Comment 1-4のCharon化に対応)
    ASR検証はer003_audio_tts_asr_safety.validate_asr_match(HARDENING-01
    の共通モジュール)を使う。"""
    max_len = len(text) + max_extra_chars
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        call_fn = gclient.make_tts_call_fn(voice_name)
        prompt = repro01.MINIMAL_INSTRUCTION_PREFIX + text
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        if not ok:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": str(err)})
            continue
        samples_raw = common.pcm_bytes_to_float_mono(pcm)
        trimmed, trim_info = p3u.trim_english_keyword_silence(
            samples_raw, common.SAMPLE_RATE, safety_margin_seconds=safety_margin_seconds)
        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": "発話区間を検出できませんでした"})
            continue
        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, asr_err = p4.get_full_text_via_azure_stt_continuous(out_path, language="en-US")
        match = safety.validate_asr_match(text, asr_text, n=6, asr_error=asr_err)
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified = match["passed"] and length_ok
        attempts_log.append({
            "attempt": attempt, "status": "OK", "asr_text": asr_text, "asr_verdict": match["verdict"],
            "length_ok": length_ok, "verified": verified, "trim_info": trim_info,
        })
        if verified:
            metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
            return {
                "status": "OK", "text": text, "path": out_path, "voice": voice_name,
                "asr_verified": True, "asr_text": asr_text, "attempts_log": attempts_log,
                "trim_info": trim_info, "safety_margin_seconds": safety_margin_seconds,
                "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
                "clipping_detected": metrics["clipping_detected"],
            }
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log}


def tail_rms_envelope(path: str, window_ms: float = 10.0, n_windows: int = 10) -> list:
    """診断用: wav末尾を10msごとのRMSに分解する(自然な減衰か、hard cutか
    を目視確認するため。C節の原因調査・修正後確認の両方で使う)。"""
    samples, sr, _, _ = common.read_wav_float(path)
    chunk = int(sr * window_ms / 1000)
    out = []
    for i in range(n_windows, 0, -1):
        seg = samples[-(i) * chunk: -(i - 1) * chunk if i > 1 else None]
        rms = float(np.sqrt(np.mean(seg.astype(np.float64) ** 2))) if len(seg) else 0.0
        out.append({"ms_from_end": (i - 1) * int(window_ms), "rms": round(rms, 5)})
    return out


# ============================================================
# Step 3: 音源読み込み・gain調整・組み立て(AUDIO-02のShellロジックを継承)
# ============================================================
def load_all_sources(new_point_explanation_path: str, new_preview_path: str,
                      comment_paths: dict) -> dict:
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    narration = {}
    # article/level非依存のservice-level narration。ただしpoint_explanation
    # だけは今回生成した英語版に差し替える(日本語版は使わない)。
    # japanese_titleはB1では読み上げないため、そもそも読み込まない。
    for name in repro01.SERVICE_LEVEL_NARRATION_NAMES:
        if name == "point_explanation":
            mono, sr, _, _ = common.read_wav_float(new_point_explanation_path)
        else:
            mono, sr, _, _ = common.read_wav_float(f"{repro01.A01_NARRATION_DIR}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    # topic_introのみ継続利用(英語、旧タイトル文言の件はAUDIO-02 A節で
    # 既に報告済み・今回の言語問題とは無関係のため据え置き)。
    mono, sr, _, _ = common.read_wav_float(f"{repro01.OUT_DIR}/narration/topic_intro.wav")
    assert sr == common.SAMPLE_RATE
    narration["topic_intro"] = mono
    # japanese_titleはnarration dictに含めない(Shellから除去)

    b1_segments = {}
    mono, sr, _, _ = common.read_wav_float(new_preview_path)
    assert sr == common.SAMPLE_RATE
    b1_segments["preview"] = mono
    for name in ("comment_1", "comment_2", "comment_3", "comment_4"):
        mono, sr, _, _ = common.read_wav_float(comment_paths[name])
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono
    for name in ("full_story_part1", "full_story_part2", "point_one", "point_two", "in_one_line"):
        mono, sr, _, _ = common.read_wav_float(f"{B1_NARRATION_DIR_V1}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono

    key_phrase_components = {}
    key_phrase_meanings = {}
    for kp in KEY_PHRASES:
        rank = kp["rank"]
        mono, sr, _, _ = common.read_wav_float(f"{B1_NARRATION_DIR_V1}/kp{rank}_en.wav")
        key_phrase_components[rank] = mono
        mono, sr, _, _ = common.read_wav_float(f"{B1_NARRATION_DIR_V1}/kp{rank}_ja.wav")
        key_phrase_meanings[rank] = mono

    return {"intro": intro, "notification": notification, "outro": outro,
            "narration": narration, "b1_segments": b1_segments,
            "key_phrase_components": key_phrase_components, "key_phrase_meanings": key_phrase_meanings}


def apply_gain_and_convert(sources: dict) -> dict:
    """AUDIO-02(=A2最終承認script)と同一方式: target_rms = Preview と
    Full Story Part1のRMS平均。Previewは無加工のアンカー。Outroは
    post-gain IntroへマッチのうえA2と同じ二段減衰。"""
    preview_mono = sources["b1_segments"]["preview"]
    full_story_part1_mono = sources["b1_segments"]["full_story_part1"]
    target_rms = (p9a.rms(preview_mono) + p9a.rms(full_story_part1_mono)) / 2
    gain_report = {"target_rms": round(target_rms, 5)}

    def gain_to_rms(data, target, label):
        gain = p9a.compute_gain_for_target_rms(data, target)
        gained = data * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(data), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return gained

    result = {}
    result["intro"] = gain_to_rms(sources["intro"]["samples"], target_rms, "intro")
    result["notification"] = gain_to_rms(sources["notification"]["samples"], target_rms, "notification")

    intro_final_rms = p9a.rms(result["intro"])
    outro_matched = sources["outro"]["samples"] * p9a.compute_gain_for_target_rms(
        sources["outro"]["samples"], intro_final_rms)
    outro_v2 = outro_matched * OUTRO_EXTRA_GAIN_LINEAR
    outro_v3 = outro_v2 * OUTRO_FURTHER_EXTRA_GAIN_LINEAR
    result["outro"] = outro_v3
    gain_report["outro"] = {
        "matched_to": "intro_post_gain_rms", "intro_post_gain_rms": round(intro_final_rms, 5),
        "rms_after_match": round(p9a.rms(outro_matched), 5),
        "v2_extra_gain_linear": round(float(OUTRO_EXTRA_GAIN_LINEAR), 4),
        "v3_further_extra_gain_linear": round(float(OUTRO_FURTHER_EXTRA_GAIN_LINEAR), 4),
        "rms_final": round(p9a.rms(outro_v3), 5), "peak_final": round(p9a.peak(outro_v3), 5),
    }

    result["preview"] = p9a.mono_24k_to_stereo_target(preview_mono)
    gain_report["preview"] = {"gain": 1.0, "note": "無加工(RMSアンカー、AUDIO-02と同じ)"}

    for name, mono in sources["narration"].items():
        gained = gain_to_rms(mono, target_rms, name)
        result[name] = p9a.mono_24k_to_stereo_target(gained)

    key_phrase_stereo, key_phrase_meaning_stereo = {}, {}
    for rank, mono in sources["key_phrase_components"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_en_{rank}")
        key_phrase_stereo[rank] = p9a.mono_24k_to_stereo_target(gained)
    for rank, mono in sources["key_phrase_meanings"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_ja_{rank}")
        key_phrase_meaning_stereo[rank] = p9a.mono_24k_to_stereo_target(gained)
    result["key_phrase_components"] = key_phrase_stereo
    result["key_phrase_meanings"] = key_phrase_meaning_stereo

    b1_stereo = {}
    for name, mono in sources["b1_segments"].items():
        if name == "preview":
            continue
        gained = gain_to_rms(mono, target_rms, f"b1_{name}")
        b1_stereo[name] = p9a.mono_24k_to_stereo_target(gained)
    b1_stereo["preview"] = result["preview"]
    result["b1_segments"] = b1_stereo

    result["gain_report"] = gain_report
    return result


def build_key_phrase_blocks(parts: dict) -> list:
    num_names = ["num_one", "num_two", "num_three", "num_four", "num_five"]
    blocks = []
    for kp in KEY_PHRASES:
        rank = kp["rank"]
        num_key = num_names[rank - 1]
        block = p9a.build_key_phrase_block(
            parts[num_key], parts["key_phrase_components"][rank], parts["key_phrase_meanings"][rank], SR)
        blocks.append(block)
    return blocks


def build_pieces_with_timeline(parts: dict) -> list:
    """AUDIO-02のtimelineから以下2点のみ変更する:
      - "Japanese title"ノードとその専用pauseを削除(B節: B1では日本語
        タイトルを読み上げない。Topic introの直後にpause_0.65を1つだけ
        残し、Notification 1へ続ける。新しいpause秒数は作らない)
      - "Point explanation"は同じ位置・同じ前後pauseのまま、英語版音声に
        差し替え
    それ以外の並び・pause値はAUDIO-02(=A2最終承認script)と同一。"""
    key_phrase_blocks = build_key_phrase_blocks(parts)
    b1 = parts["b1_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        # "Japanese title"は削除(B節)。直前のpause_0.65を残したまま
        # Notification 1へ続く。
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Point explanation (EN)", parts["point_explanation"]),
        ("pause_0.7_point_explanation", p9a.silence_stereo(POINT_EXPLANATION_PAUSE_SECONDS)),
        ("Preview", b1["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = ("Key Phrase 1", "Key Phrase 2", "Key Phrase 3", "Key Phrase 4", "Key Phrase 5")
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro", parts["full_story_intro"]),
        ("pause_1.0", p9a.silence_stereo(COMMENT_EN_TO_JA_PAUSE_SECONDS)),
        ("Comment 1 (Charon)", b1["comment_1"]),
        ("pause_0.8", p9a.silence_stereo(COMMENT_JA_TO_EN_PAUSE_SECONDS)),
        ("Full Story Part 1", b1["full_story_part1"]),
        ("pause_1.0", p9a.silence_stereo(COMMENT_EN_TO_JA_PAUSE_SECONDS)),
        ("Comment 2 (Charon)", b1["comment_2"]),
        ("pause_0.8", p9a.silence_stereo(COMMENT_JA_TO_EN_PAUSE_SECONDS)),
        ("Full Story Part 2", b1["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(COMMENT_EN_TO_JA_PAUSE_SECONDS)),
        ("Comment 3 (Charon)", b1["comment_3"]),
        ("pause_0.8", p9a.silence_stereo(COMMENT_JA_TO_EN_PAUSE_SECONDS)),
        ("Point One", b1["point_one"]),
        ("pause_0.8_point1_to_point2", p9a.silence_stereo(POINT1_TO_POINT2_PAUSE_SECONDS)),
        ("Point Two", b1["point_two"]),
        ("pause_1.0", p9a.silence_stereo(COMMENT_EN_TO_JA_PAUSE_SECONDS)),
        ("Comment 4 (Charon)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(COMMENT_JA_TO_EN_PAUSE_SECONDS)),
        ("In One Line", b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro", parts["outro"]),
    ]
    return seq


def assemble_with_timeline(parts: dict) -> dict:
    seq = build_pieces_with_timeline(parts)
    pieces = [samples for _, samples in seq]
    assembled = np.ascontiguousarray(np.concatenate(pieces, axis=0))

    timeline = []
    t = 0.0
    for name, samples in seq:
        dur = len(samples) / SR
        timeline.append({"part": name, "start_seconds": round(t, 3), "duration_seconds": round(dur, 3)})
        t += dur

    return {"assembled": assembled, "timeline": timeline, "total_duration_seconds": round(t, 3)}


def verify_b2_text_sha() -> dict:
    return audio02b.verify_b2_text_sha()


# ============================================================
# 日本語残存Audit(最終assembleのtimelineラベルから機械判定)
# ============================================================
_KEY_PHRASE_JAPANESE_LABEL_PREFIX = "Key Phrase"


def audit_japanese_residual(timeline: list, segment_texts: dict) -> list:
    """timeline上の各セクションについて、そのセクションの発話テキストに
    日本語文字(ひらがな/カタカナ/漢字)が含まれるかを機械的に判定する。
    Key Phraseブロックのみ日本語(meaning部分)を含むことを期待値とする。"""
    import re
    ja_pattern = re.compile(r"[ぁ-んァ-ヶ一-龠]")
    rows = []
    for entry in timeline:
        part = entry["part"]
        if part.startswith("pause") or part in ("Intro", "Outro", "Notification 1", "Notification 2", "Notification 3"):
            continue
        text = segment_texts.get(part, "")
        has_ja = bool(ja_pattern.search(text)) if text else None
        expected = part.startswith(_KEY_PHRASE_JAPANESE_LABEL_PREFIX)
        rows.append({
            "section": part, "japanese_present": has_ja, "expected": expected,
            "result": "OK" if (has_ja == expected or text == "") else "UNEXPECTED_JAPANESE" if has_ja else "OK",
        })
    return rows


def main():
    os.makedirs(NARRATION_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/assembled", exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    sha_check = verify_b2_text_sha()
    print("[AUDIO-03] B2本文SHA一致確認:", sha_check["match"])
    with open(f"{OUT_DIR}/audit/b2_text_sha_check.json", "w", encoding="utf-8") as f:
        json.dump(sha_check, f, ensure_ascii=False, indent=2)
    if not sha_check["match"]:
        print("[AUDIO-03] SHA不一致のため中断します。")
        return

    # --- Step 1: Point explanation英語版 ---
    print("[AUDIO-03] Point explanation(英語版)生成...")
    pe_path = f"{NARRATION_DIR}/point_explanation_en.wav"
    pe_result = generate_point_explanation_en(POINT_EXPLANATION_EN_TEXT, pe_path)
    print(f"[AUDIO-03] point_explanation_en: status={pe_result.get('status')}")
    with open(f"{OUT_DIR}/audit/point_explanation_en_result.json", "w", encoding="utf-8") as f:
        json.dump(pe_result, f, ensure_ascii=False, indent=2, default=str)
    if pe_result.get("status") != "OK":
        print("[AUDIO-03] point_explanation_en生成失敗、中断します。")
        return

    # --- Step 2: Preview再生成(tail安全マージン修正版、voiceはAoede無変更) ---
    support_texts = audio01b.build_fixed_support_texts()
    print("[AUDIO-03] Preview再生成(trim安全マージン修正)...")
    preview_path = f"{NARRATION_DIR}/preview.wav"
    preview_tail_before = tail_rms_envelope(f"{B1_NARRATION_DIR_V1}/preview.wav")
    preview_result = generate_long_form_narration_verified(
        support_texts["preview"], preview_path, voice_name=NEWS_VOICE_NAME)
    print(f"[AUDIO-03] preview: status={preview_result.get('status')}")
    if preview_result.get("status") == "OK":
        preview_tail_after = tail_rms_envelope(preview_path)
        preview_result["tail_rms_before_fix"] = preview_tail_before
        preview_result["tail_rms_after_fix"] = preview_tail_after
    with open(f"{OUT_DIR}/audit/preview_regeneration_result.json", "w", encoding="utf-8") as f:
        json.dump(preview_result, f, ensure_ascii=False, indent=2, default=str)
    if preview_result.get("status") != "OK":
        print("[AUDIO-03] Preview再生成失敗、中断します。")
        return

    # --- Step 3: Comment 1-4をCharonで再生成(同じtrim安全マージン修正を適用) ---
    comment_results = {}
    comment_paths = {}
    for name in ("comment_1", "comment_2", "comment_3", "comment_4"):
        print(f"[AUDIO-03] {name}をCharonで再生成...")
        out_path = f"{NARRATION_DIR}/{name}_charon.wav"
        r = generate_long_form_narration_verified(support_texts[name], out_path, voice_name=COMMENT_VOICE_NAME)
        comment_results[name] = r
        comment_paths[name] = out_path
        print(f"[AUDIO-03] {name}: status={r.get('status')}")
    with open(f"{OUT_DIR}/audit/comment_charon_results.json", "w", encoding="utf-8") as f:
        json.dump(comment_results, f, ensure_ascii=False, indent=2, default=str)
    if any(r.get("status") != "OK" for r in comment_results.values()):
        print("[AUDIO-03] Comment Charon生成に失敗があり、中断します。")
        return

    # --- Step 4: 組み立て ---
    print("[AUDIO-03] 音源読み込み・組み立て開始...")
    sources = load_all_sources(pe_path, preview_path, comment_paths)
    parts = apply_gain_and_convert(sources)
    result = assemble_with_timeline(parts)
    assembled = result["assembled"]

    out_path = f"{OUT_DIR}/assembled/English_Your_Way_B1_A02_v3.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{OUT_DIR}/audit/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/timeline.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    # --- Step 5: 日本語残存Audit ---
    segment_texts = {
        "Welcome": "Welcome to English Your Way.",
        "Topic intro": repro01.TOPIC_INTRO_TEXT,
        "Preview intro": "Here's a quick preview.",
        "Point explanation (EN)": POINT_EXPLANATION_EN_TEXT,
        "Preview": support_texts["preview"],
        "Key phrases intro": "Here are today's key phrases.",
        "Key Phrase 1": "One. by default. 初期設定で. by default.",
        "Key Phrase 2": "Two. curfew. 利用禁止時間. curfew.",
        "Key Phrase 3": "Three. cross the finish line. 完了する、成立に至る. cross the finish line.",
        "Key Phrase 4": "Four. pilot. 試験的な調査. pilot.",
        "Key Phrase 5": "Five. personalised feeds. 個人向けに選ばれた投稿欄. personalised feeds.",
        "Full story intro": "Now, the full story.",
        "Comment 1 (Charon)": support_texts["comment_1"],
        "Full Story Part 1": "(B2共通ニュース本文、英語)",
        "Comment 2 (Charon)": support_texts["comment_2"],
        "Full Story Part 2": "(B2共通ニュース本文、英語)",
        "Comment 3 (Charon)": support_texts["comment_3"],
        "Point One": "(B2共通ニュース本文、英語)",
        "Point Two": "(B2共通ニュース本文、英語)",
        "Comment 4 (Charon)": support_texts["comment_4"],
        "In One Line": "(B2共通ニュース本文、英語)",
    }
    ja_audit = audit_japanese_residual(result["timeline"], segment_texts)
    with open(f"{OUT_DIR}/audit/japanese_residual_audit.json", "w", encoding="utf-8") as f:
        json.dump(ja_audit, f, ensure_ascii=False, indent=2)
    unexpected = [r for r in ja_audit if r["result"] == "UNEXPECTED_JAPANESE"]
    print(f"[AUDIO-03] 日本語残存Audit: 想定外の日本語 {len(unexpected)}件")

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2, "b2_text_sha_match": sha_check["match"],
        "japanese_residual_unexpected_count": len(unexpected),
        "comment_voice": COMMENT_VOICE_NAME, "news_voice": NEWS_VOICE_NAME,
    }
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[AUDIO-03] 完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
