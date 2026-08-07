# ============================================================
# er003_v1_b1_p9a_r1_generate.py
# ER-003-B1-P9A-R1: 「English Your Way」Podcast完成版 修正版組み立て
# ============================================================
# ユーザー指示による修正:
#   1. Podcast Name: "Welcome to English Your Way."
#   2. タイトル: "Today's topic is [英語タイトル]." + 日本語タイトル
#   3. Preview Introduction: "Here's a quick preview." + 「ポイント解説」
#   4. Preview: 英語Key Phraseなし、日本語のみ(新規作成)
#   5. Key Phrasesセクション新設(番号→英語→日本語→英語 ×5)
#   6. Full Story Introduction: "Now, the full story."の異常音声を修正
#   7. Full Story冒頭のタイトルをMFA境界で除去(RMSは使わない)
#   8. Outro音量をIntroに合わせる
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p9a_r1_generate.py

from __future__ import annotations

import json

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a

OUT_DIR = "er003_output/b1_p9a/A01"
SR = p9a.TARGET_SAMPLE_RATE


def load_all_sources_v2() -> dict:
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    # Full Story: 既存のbody_dynamics3.wavから (1) "In One Line"内の異常に
    # 長い無音(約2.18秒、"...through the gap."と"Argentina will now..."
    # の間)を短縮し、(2) タイトルを除去した版を使用する。
    #
    # 順序が重要: どちらの処理も元のbody_dynamics3.wav上の絶対時刻
    # (MFA特定済み)を基準にするため、時系列で後ろにある編集(2.18秒の
    # 無音短縮、約139秒地点)を先に行い、その後で前方の編集(タイトル
    # 除去、約4.86秒地点)を行う。逆順だとタイトル除去でインデックスが
    # 前方にずれ、後段の絶対時刻指定が無効になる。
    body_full, body_sr, _, _ = common.read_wav_float(p9a.BODY_PATH)

    gap_fix_result = p9a.trim_internal_gap(
        body_full, body_sr, gap_end_seconds=138.949997, gap_start_seconds=141.130005,
        target_gap_seconds=0.68)  # 0.68秒は同一音声内の他の段落区切り(half./neither間)の実測値
    body_gap_fixed = gap_fix_result["trimmed"]

    trim_result = p9a.trim_title_from_body(body_gap_fixed, body_sr, first_word_start_seconds=4.86,
                                            natural_leading_seconds=0.17)
    body_mono = trim_result["trimmed"]

    preview_mono, preview_sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/preview_japanese_only.wav")
    assert preview_sr == common.SAMPLE_RATE and body_sr == common.SAMPLE_RATE

    narration_names = ("welcome", "topic_intro", "japanese_title", "preview_intro", "point_explanation",
                        "key_phrases_intro", "full_story_intro",
                        "num_one", "num_two", "num_three", "num_four", "num_five",
                        "meaning_1", "meaning_2", "meaning_3", "meaning_4", "meaning_5")
    narration = {}
    for name in narration_names:
        mono, sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono

    key_phrase_components = {}
    for kp in p9a.KEY_PHRASES:
        mono, sr, _, _ = common.read_wav_float(kp["english_component_path"])
        key_phrase_components[kp["number"]] = p9a.p7c.tight_speech_only(mono, sr)

    return {
        "intro": intro, "notification": notification, "outro": outro,
        "preview_mono": preview_mono, "body_mono": body_mono, "narration": narration,
        "key_phrase_components": key_phrase_components, "body_title_trim_info": trim_result["info"],
        "body_gap_fix_info": gap_fix_result["info"],
    }


def apply_gain_and_convert_v2(sources: dict) -> dict:
    """PreviewとBody(本編)は無加工のまま基準とする。Intro/notification/
    新規ナレーションは平均RMSへ。Outroだけは特別に、Introの調整後RMSへ
    合わせる(指示「Outro音量をIntroと聴感上ほぼ同程度に」)。"""
    target_rms = (p9a.rms(sources["preview_mono"]) + p9a.rms(sources["body_mono"])) / 2
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
    result["outro"] = gain_to_rms(sources["outro"]["samples"], intro_final_rms, "outro")
    gain_report["outro"]["matched_to"] = "intro_post_gain_rms"
    gain_report["outro"]["intro_post_gain_rms"] = round(intro_final_rms, 5)

    # ユーザーからの追加指示: Introと合わせた後も「まだ大きい」との指摘。
    # 「人間の聴覚的に2/3くらいまで下げたい」に対応するため、聴感上の
    # 音量(ラウドネス)がおよそ2/3になる追加のgainを適用する。目安として
    # 広く使われる経験則(10dBの変化で聴感上のラウドネスがおよそ2倍/半分
    # になる)に基づき、2/3のラウドネス比に相当する-5.85dB
    # (線形gain換算で約0.510倍)をIntro基準の音量へさらに掛け合わせる。
    perceptual_two_thirds_gain = 0.5099396125390767  # 10*log2(2/3) dB ≒ -5.85dB
    result["outro"] = result["outro"] * perceptual_two_thirds_gain
    gain_report["outro"]["perceptual_two_thirds_additional_gain"] = perceptual_two_thirds_gain
    gain_report["outro"]["perceptual_two_thirds_additional_db"] = -5.8496
    gain_report["outro"]["rms_after_perceptual_adjust"] = round(p9a.rms(result["outro"]), 5)
    gain_report["outro"]["peak_after_perceptual_adjust"] = round(p9a.peak(result["outro"]), 5)

    result["preview"] = p9a.mono_24k_to_stereo_target(sources["preview_mono"])  # 無加工
    result["body"] = p9a.mono_24k_to_stereo_target(sources["body_mono"])  # タイトル除去のみ、内容は無加工

    for name, mono in sources["narration"].items():
        gained = gain_to_rms(mono, target_rms, name)
        result[name] = p9a.mono_24k_to_stereo_target(gained)

    key_phrase_stereo = {}
    for number, mono in sources["key_phrase_components"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_en_{number}")
        key_phrase_stereo[number] = p9a.mono_24k_to_stereo_target(gained)
    result["key_phrase_components"] = key_phrase_stereo

    gain_report["preview"] = {"gain": 1.0, "note": "無加工(既存承認済み音声を保持)"}
    gain_report["body"] = {"gain": 1.0, "note": "タイトル除去のみ、本文の内容・gainは無加工"}
    result["gain_report"] = gain_report
    return result


def build_key_phrase_blocks(parts: dict) -> list:
    blocks = []
    for kp in p9a.KEY_PHRASES:
        num_key = f"num_{kp['number'].lower()}"
        meaning_key = f"meaning_{p9a.KEY_PHRASES.index(kp) + 1}"
        block = p9a.build_key_phrase_block(
            parts[num_key], parts["key_phrase_components"][kp["number"]], parts[meaning_key], SR)
        blocks.append(block)
    return blocks


def assemble_v2(parts: dict) -> "np.ndarray":
    key_phrase_blocks = build_key_phrase_blocks(parts)

    pieces = [
        parts["intro"],
        p9a.silence_stereo(0.0),
        parts["welcome"],
        p9a.silence_stereo(0.5),
        parts["topic_intro"],
        p9a.silence_stereo(0.65),
        parts["japanese_title"],
        p9a.silence_stereo(0.5),
        parts["notification"],
        p9a.silence_stereo(0.4),
        parts["preview_intro"],
        p9a.silence_stereo(0.65),
        parts["point_explanation"],
        p9a.silence_stereo(0.5),
        parts["preview"],
        p9a.silence_stereo(0.5),
        parts["notification"],
        p9a.silence_stereo(0.4),
        parts["key_phrases_intro"],
        p9a.silence_stereo(0.5),
    ]
    for block in key_phrase_blocks:
        pieces.append(block)
    pieces += [
        parts["notification"],
        p9a.silence_stereo(0.4),
        parts["full_story_intro"],
        p9a.silence_stereo(0.7),
        parts["body"],
        p9a.silence_stereo(0.5),
        parts["outro"],
    ]
    return np.ascontiguousarray(np.concatenate(pieces, axis=0))


def run() -> dict:
    sources = load_all_sources_v2()
    parts = apply_gain_and_convert_v2(sources)
    assembled = assemble_v2(parts)

    out_path = f"{OUT_DIR}/assembled/English_Your_Way_A01_r1.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{OUT_DIR}/audit/gain_report_r1.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/body_gap_fix_info.json", "w", encoding="utf-8") as f:
        json.dump(sources["body_gap_fix_info"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/body_title_trim_info.json", "w", encoding="utf-8") as f:
        json.dump(sources["body_title_trim_info"], f, ensure_ascii=False, indent=2)

    return {
        "status": "OK", "out_path": out_path, "duration_seconds": round(len(assembled) / SR, 4),
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2,
    }


if __name__ == "__main__":
    result = run()
    print("status:", result["status"])
    print("out_path:", result["out_path"])
    print("duration_seconds:", result["duration_seconds"])
    print("clipping_detected:", result["clipping_detected"])
    print("peak:", result["peak"])
