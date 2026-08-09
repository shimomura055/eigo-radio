# ============================================================
# er003_v1_a2_audio_02_generate.py
# ER-003-CROSSLEVEL-AUDIO-01: A02再試作
# (Preview刷新/Comment4修正/Key Phrase語末音素試作/ポーズ+0.2秒/Outro減衰)
# ============================================================
# ER-003-A2-AUDIO-01(er003_v1_a2_audio_01_generate.py、以下audio01)を
# ベースとし、そこで変更しないと明示された部分(Comment1-3・Full Story
# Part1/2・Point One/Two・In One Line英語3文・英語本編TTS速度・
# Comment前後のポーズ・新規効果音なし方針)はaudio01の生成済み資産を
# そのまま再利用する。audio01自体・B1既存資産・共有凍結モジュールは
# 変更しない。

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_b1_p3u_audio as p3u
import er003_b1_p9a_audio as p9a
import er003_v1_a2_audio_01_generate as audio01
import er003_v1_repro01_main_generate as repro01

ARTICLE_ID = "A02"
OUT_DIR = f"er003_output/a2_audio_02/{ARTICLE_ID}"

generate_narration_snippet_verified_strict = repro01.generate_narration_snippet_verified_strict

# ============================================================
# ブロック1: 変更するテキスト
# ============================================================
# 共通変更①: Previewは後続本文の具体回答を先に言いすぎない
# (16/17歳・深夜0-6時・通知停止・おすすめ停止・opt-out可能、いずれも
# 具体的には触れない。テーマ・問題意識・問いのみ)
PREVIEW_TEXT_V2 = (
    "英国政府が、10代の若者とSNSの使い方をめぐる新しい計画を発表しました。"
    "夜のSNS利用を見直すことで、若者の睡眠を守ろうという狙いです。"
    "この仕組みは、本当に行動を変えられるのでしょうか。"
)

# A2固有変更②: Comment4末尾を「英語一文で」→「ポイントを英語で」へ
# (In One Lineが中心1文+補足2文の計3文のため)。最初の2文は変更しない。
COMMENT_4_TEXT_V2 = (
    "夜のルールだけですべて解決するわけではありません。"
    "でも、最初の設定を変えるだけで、人の行動が変わる可能性はありそうです。"
    "最後に、今日のニュースのポイントを英語で聞いてみましょう。"
)

# 共通変更③: Key Phrase語末音素試作(personalized feedの/d/)
KEY_PHRASE_4_TEXT = "personalized feed"
# ENGLISH_STYLE_PREFIX(標準経路)・MINIMAL_INSTRUCTION_PREFIX(既存
# フォールバック)のいずれも変更せず、今回の試作専用の新規instructionを
# 別途定義する(既存2経路への影響なし)。狙いは語末子音の不自然な強調
# ではなく、「言い切る」ことの明示のみ。
TRIAL_CLARITY_INSTRUCTION_PREFIX = (
    "Speak the following short phrase aloud naturally and clearly, in a warm podcast "
    "announcer voice. Pronounce it as a complete, natural phrase and make sure the very "
    "last sound of the phrase is actually spoken, not trailed off into silence. Do not "
    "add, omit, or change any words, and do not over-emphasize or exaggerate any single "
    "sound.\n\n"
)
# 既存のtrim安全マージン(0.08秒)より広めに取り、末尾の弱い破裂音・
# 気息音を安全側で残す(trim_english_keyword_silence自体は変更せず、
# 引数で余白だけ広げる)。
TRIAL_TRIM_SAFETY_MARGIN_SECONDS = 0.15


def generate_key_phrase_trial_clarity(text: str, out_path: str) -> dict:
    prompt = TRIAL_CLARITY_INSTRUCTION_PREFIX + text
    call_fn = p9a._make_english_call_fn()
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"status": "STOPPED", "reason": f"TTS失敗: {err}"}
    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=TRIAL_TRIM_SAFETY_MARGIN_SECONDS)
    if trimmed is None:
        return {"status": "STOPPED", "reason": "発話区間を検出できませんでした"}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
    return {
        "status": "OK", "text": text, "path": out_path, "model": p9a.ENGLISH_MODEL_NAME,
        "voice": p9a.VOICE_NAME, "call_count": 1 + retries, "retry_count": retries,
        "sha256": repro01.p8a.sha256_file(out_path), "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
        "trim_info": trim_info, "clipping_detected": metrics["clipping_detected"],
        "instruction": "trial_clarity (not ENGLISH_STYLE_PREFIX, not MINIMAL_INSTRUCTION_PREFIX)",
        "trim_safety_margin_seconds": TRIAL_TRIM_SAFETY_MARGIN_SECONDS,
    }


def _tail_energy_profile(path: str, window_ms: float = 20.0, tail_ms: float = 300.0) -> list:
    samples, sr, _, _ = common.read_wav_float(path)
    win = int(sr * window_ms / 1000)
    tail = samples[-int(sr * tail_ms / 1000):]
    profile = []
    offset = len(samples) - len(tail)
    for i in range(0, len(tail), win):
        chunk = tail[i:i + win]
        if len(chunk) == 0:
            continue
        rms = float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2)))
        t = (offset + i) / sr
        profile.append({"t": round(t, 3), "rms": round(rms, 4)})
    return profile


_SEGMENTS_V2 = [
    ("preview_v2", PREVIEW_TEXT_V2, "ja", "睡眠を守ろう", 60),
    ("comment_4_v2", COMMENT_4_TEXT_V2, "ja", "ポイントを英語で聞いて", 60),
]


def stage_generate_v2_segments() -> dict:
    narration_dir = f"{OUT_DIR}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    results = {}
    for name, text, language, expected_substring, max_extra_chars in _SEGMENTS_V2:
        out_path = f"{narration_dir}/{name}.wav"
        result = generate_narration_snippet_verified_strict(
            text, language, out_path, expected_substring, max_attempts=6, max_extra_chars=max_extra_chars)
        results[name] = result

    # Key Phrase 4語末音素の試作
    kp4_out = f"{narration_dir}/key_phrase_4_feed_trial.wav"
    kp4_result = generate_key_phrase_trial_clarity(KEY_PHRASE_4_TEXT, kp4_out)
    results["key_phrase_4_feed_trial"] = kp4_result

    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    # 語末エネルギー比較(旧kp_4 vs 新trial)
    old_kp4_path = repro01.A02_KEY_PHRASES[3]["component_path"]
    tail_comparison = {
        "old": {"path": old_kp4_path, "profile": _tail_energy_profile(old_kp4_path)},
    }
    if kp4_result.get("status") == "OK":
        tail_comparison["new_trial"] = {"path": kp4_out, "profile": _tail_energy_profile(kp4_out)}
    with open(f"{OUT_DIR}/audit/key_phrase_4_tail_energy_comparison.json", "w", encoding="utf-8") as f:
        json.dump(tail_comparison, f, ensure_ascii=False, indent=2)

    with open(f"{OUT_DIR}/audit/v2_segments_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    all_ok = all(r.get("status") == "OK" for r in results.values())
    return {"status": "OK" if all_ok else "STOPPED", "results": results, "tail_comparison": tail_comparison}


# ============================================================
# ブロック2: 全体組み立て(audio01の資産を最大限再利用)
# ============================================================
SR = p9a.TARGET_SAMPLE_RATE

# Outro減衰: 人間聴覚上「約4/5(80%)」を狙う。心理音響の一般的な目安
# (10dBの増減で知覚音量がおよそ2倍/半分になる、という経験則)に基づき、
# 20%減の知覚を得るための減衰量を dB = 10*log2(0.8) ≈ -3.22dB とし、
# 振幅倍率 = 10^(dB/20) ≈ 0.693 を、既存のIntro基準RMS一致ゲインの上に
# 追加で乗じる(amplitudeを単純に0.8倍にはしない)。
OUTRO_PERCEIVED_LOUDNESS_TARGET = 0.8
OUTRO_EXTRA_GAIN_DB = 10 * np.log2(OUTRO_PERCEIVED_LOUDNESS_TARGET)  # ≈ -3.22
OUTRO_EXTRA_GAIN_LINEAR = 10 ** (OUTRO_EXTRA_GAIN_DB / 20)  # ≈ 0.693

# 「ポイント解説」後のポーズ: 0.5秒→0.7秒(+0.2秒)。他のポーズ値は変更しない。
POINT_EXPLANATION_PAUSE_SECONDS = 0.7


def load_all_sources_v2() -> dict:
    """audio01のload_all_sourcesと同じB1既存資産(Intro/notification/
    Outro/サービス共通ナレーション/topic_intro/japanese_title/
    meaning_1-5/Key Phrase Component1-3・5)を再利用し、Preview・
    Comment4・Key Phrase Component4だけを新版へ差し替える。
    Comment1-3・Full Story Part1/2・Point One/Two・In One Lineは
    audio01で既に生成済みのwavファイルをそのまま再利用する(再生成しない)。"""
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    # 新Preview(V2)
    preview_mono, preview_sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/preview_v2.wav")
    assert preview_sr == common.SAMPLE_RATE

    narration = {}
    for name in repro01.SERVICE_LEVEL_NARRATION_NAMES:
        mono, sr, _, _ = common.read_wav_float(f"{repro01.A01_NARRATION_DIR}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("topic_intro", "japanese_title", "meaning_1", "meaning_2", "meaning_3", "meaning_4", "meaning_5"):
        mono, sr, _, _ = common.read_wav_float(f"{repro01.OUT_DIR}/narration/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono

    key_phrase_components = {}
    for kp in repro01.A02_KEY_PHRASES:
        if kp["number"] == "Four":
            mono, sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/key_phrase_4_feed_trial.wav")
        else:
            mono, sr, _, _ = common.read_wav_float(kp["component_path"])
        key_phrase_components[kp["number"]] = p9a.p7c.tight_speech_only(mono, sr)

    # Comment1-3・Full Story Part1/2・Point One/Two・In One LineはA2-AUDIO-01の
    # 既存生成物をそのまま再利用(再生成しない)
    a2_segments = {}
    for name in ("comment_1", "comment_2", "comment_3", "full_story_part1", "full_story_part2",
                 "point_one", "point_two", "in_one_line"):
        mono, sr, _, _ = common.read_wav_float(f"{audio01.OUT_DIR}/narration/{name}.wav")
        assert sr == common.SAMPLE_RATE
        a2_segments[name] = mono
    # Comment4だけ新版
    mono, sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/comment_4_v2.wav")
    assert sr == common.SAMPLE_RATE
    a2_segments["comment_4"] = mono

    return {
        "intro": intro, "notification": notification, "outro": outro,
        "preview_mono": preview_mono, "narration": narration,
        "key_phrase_components": key_phrase_components,
        "a2_segments": a2_segments,
    }


def apply_gain_and_convert_v2(sources: dict) -> dict:
    target_rms = (p9a.rms(sources["preview_mono"]) + p9a.rms(sources["a2_segments"]["full_story_part1"])) / 2
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
    outro_final = outro_matched * OUTRO_EXTRA_GAIN_LINEAR
    result["outro"] = outro_final
    gain_report["outro"] = {
        "matched_to": "intro_post_gain_rms", "intro_post_gain_rms": round(intro_final_rms, 5),
        "rms_after_match": round(p9a.rms(outro_matched), 5),
        "extra_perceived_loudness_target": OUTRO_PERCEIVED_LOUDNESS_TARGET,
        "extra_gain_db": round(float(OUTRO_EXTRA_GAIN_DB), 3),
        "extra_gain_linear": round(float(OUTRO_EXTRA_GAIN_LINEAR), 4),
        "rms_final": round(p9a.rms(outro_final), 5), "peak_final": round(p9a.peak(outro_final), 5),
    }

    result["preview"] = p9a.mono_24k_to_stereo_target(sources["preview_mono"])

    for name, mono in sources["narration"].items():
        gained = gain_to_rms(mono, target_rms, name)
        result[name] = p9a.mono_24k_to_stereo_target(gained)

    key_phrase_stereo = {}
    for number, mono in sources["key_phrase_components"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_en_{number}")
        key_phrase_stereo[number] = p9a.mono_24k_to_stereo_target(gained)
    result["key_phrase_components"] = key_phrase_stereo

    a2_stereo = {}
    for name, mono in sources["a2_segments"].items():
        gained = gain_to_rms(mono, target_rms, f"a2_{name}")
        a2_stereo[name] = p9a.mono_24k_to_stereo_target(gained)
    result["a2_segments"] = a2_stereo

    gain_report["preview"] = {"gain": 1.0, "note": "無加工(新Preview V2音声を保持)"}
    result["gain_report"] = gain_report
    return result


def build_key_phrase_blocks(parts: dict) -> list:
    blocks = []
    for kp in repro01.A02_KEY_PHRASES:
        num_key = f"num_{kp['number'].lower()}"
        meaning_key = f"meaning_{repro01.A02_KEY_PHRASES.index(kp) + 1}"
        block = p9a.build_key_phrase_block(
            parts[num_key], parts["key_phrase_components"][kp["number"]], parts[meaning_key], SR)
        blocks.append(block)
    return blocks


def build_pieces_with_timeline(parts: dict) -> list:
    key_phrase_blocks = build_key_phrase_blocks(parts)
    a2 = parts["a2_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Japanese title", parts["japanese_title"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Point explanation", parts["point_explanation"]),
        # 共通変更④: 0.5秒→0.7秒(+0.2秒)。他のポーズは変更しない。
        ("pause_0.7_point_explanation", p9a.silence_stereo(POINT_EXPLANATION_PAUSE_SECONDS)),
        ("Preview", parts["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = ("Key Phrase 1", "Key Phrase 2", "Key Phrase 3", "Key Phrase 4 (trial)", "Key Phrase 5")
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro", parts["full_story_intro"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 1", a2["comment_1"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Full Story Part 1", a2["full_story_part1"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 2", a2["comment_2"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Full Story Part 2", a2["full_story_part2"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 3", a2["comment_3"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Point One", a2["point_one"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Point Two", a2["point_two"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 4 (v2)", a2["comment_4"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("In One Line", a2["in_one_line"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
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


def stage_assemble() -> dict:
    os.makedirs(f"{OUT_DIR}/assembled", exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    sources = load_all_sources_v2()
    parts = apply_gain_and_convert_v2(sources)
    result = assemble_with_timeline(parts)
    assembled = result["assembled"]

    out_path = f"{OUT_DIR}/assembled/English_Your_Way_A2_A02_v2.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{OUT_DIR}/audit/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/timeline.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    return {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2, "timeline": result["timeline"],
    }


if __name__ == "__main__":
    r1 = stage_generate_v2_segments()
    print("stage_generate_v2_segments status:", r1["status"])
    if r1["status"] == "OK":
        r2 = stage_assemble()
        print("stage_assemble status:", r2["status"])
        print("duration:", r2["duration_seconds"], "peak:", r2["peak"], "clipping:", r2["clipping_detected"])
