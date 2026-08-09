# ============================================================
# er003_v1_a2_audio_01_generate.py
# ER-003-A2-AUDIO-01: A02 A2構造支援版 音声プロトタイプ
# ============================================================
# A01/B1専用モジュール(er003_b1_p9a_audio.py等)、A02のB1組み立てスクリプト
# (er003_v1_repro01_main_generate.py)は変更しない。それらの汎用関数・
# 既存音声資産(Intro/notification/Outro/サービス共通ナレーション/
# topic_intro/japanese_title/meaning_1-5/Key Phrase Components/
# 承認済みPreview)をそのまま再利用し、A2固有の新規部分(日本語Comment1〜4、
# 英語Full Story Part1/2・Point One・Point Two・In One Line)だけを
# このスクリプトで新規生成する。
#
# テキストのSource of Truth: ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md
# (ER-003-A2-STRUCT-05でIn One Lineへ補足2文を反映した最新版)。

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er002_ja_article_generation as article_gen
import er003_a2_article as a2
import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01

ARTICLE_ID = "A02"
OUT_DIR = f"er003_output/a2_audio_01/{ARTICLE_ID}"
B1_OUT_DIR = repro01.OUT_DIR  # er003_output/b1_p9a/A02(既存B1資産の参照元)
A2_SOURCE_TEXT_PATH = f"er003_output/a2_p1_r3/{ARTICLE_ID}/a2_article_raw.md"

generate_narration_snippet_verified_strict = repro01.generate_narration_snippet_verified_strict


# ============================================================
# ブロック1: A2固有テキスト
# ============================================================
# Full Story Part1/2・Point One/Twoは、手入力による文字化け(カーリー
# クォート等)を避けるため、A2-03本文ファイルからプログラムで直接抽出する
# (ER-003-A2-STRUCT-03/04で使ったsplit_article_sectionsと同じ方法)。
# In One Lineの中心1文も同ファイルから抽出し、ER-003-A2-STRUCT-05で
# 追加した補足2文だけをリテラルとして追記する(補足文はスマートクォートを
# 含まないため手入力の文字化けリスクがない)。
def _load_source_texts() -> dict:
    with open(A2_SOURCE_TEXT_PATH, encoding="utf-8") as f:
        original = f.read()
    sections = a2.split_article_sections(original)
    paras = [p.strip() for p in sections["full_story"].split("\n\n") if p.strip()]
    body_paras = paras[1:]  # [0]はタイトル

    full_story_part1 = "\n\n".join(body_paras[0:5])
    full_story_part2 = "\n\n".join(body_paras[5:7])

    points = sections["points"]
    idx = points.index("### Point Two")
    point_one = points[:idx].strip().replace("### ", "")
    point_two = points[idx:].strip().replace("### ", "")

    in_one_line_core = sections["in_one_line"].strip()

    return {
        "full_story_part1": full_story_part1,
        "full_story_part2": full_story_part2,
        "point_one": point_one,
        "point_two": point_two,
        "in_one_line_core": in_one_line_core,
    }


_SRC = _load_source_texts()

COMMENT_1_TEXT = "まずは、夜になるとSNSがどう変わるのかに注目して聞いてみましょう。"
COMMENT_2_TEXT = "ここまでで、深夜にはSNSのいくつかの機能が自動で止まる計画だと分かりました。では、利用者はこの設定を自分で変えられるのでしょうか。"
COMMENT_3_TEXT = "設定は自分で変えられるので、これは完全な禁止ではありません。それでも、最初から使えない状態にしておくだけで行動は変わるのでしょうか。ここからは、2つの実験を見ていきます。"
COMMENT_4_TEXT = "夜のルールだけですべて解決するわけではありません。でも、最初の設定を変えるだけで、人の行動が変わる可能性はありそうです。最後に、今日のニュースを英語一文でまとめます。"

FULL_STORY_PART1_TEXT = _SRC["full_story_part1"]
FULL_STORY_PART2_TEXT = _SRC["full_story_part2"]
POINT_ONE_TEXT = _SRC["point_one"]
POINT_TWO_TEXT = _SRC["point_two"]

# ER-003-A2-STRUCT-05で確定した補足2文(スマートクォートを含まないため
# リテラルのまま。中心1文はソースファイルからプログラムで取得)
IN_ONE_LINE_FOLLOWUP_1 = "This is not a full ban; teenagers can still turn it off."
IN_ONE_LINE_FOLLOWUP_2 = "But even a simple first setting can change what people do."
IN_ONE_LINE_TEXT = f"{_SRC['in_one_line_core']} {IN_ONE_LINE_FOLLOWUP_1} {IN_ONE_LINE_FOLLOWUP_2}"

# 各segmentのstrict ASR検証パラメータ(内容の一部を示す代表的な語句+
# 長さ上限の余裕。既存のtopic_intro/meaning_X/Key Phrase Componentと
# 同じ考え方: 全文一致ではなく代表語句+文字数上限でhallucinationを検知)
_SEGMENTS = [
    ("comment_1", COMMENT_1_TEXT, "ja", "夜になるとSNSがどう変わる", 40),
    ("comment_2", COMMENT_2_TEXT, "ja", "自分で変えられるのでしょうか", 50),
    ("comment_3", COMMENT_3_TEXT, "ja", "2つの実験", 60),
    ("comment_4", COMMENT_4_TEXT, "ja", "英語一文でまとめます", 60),
    ("full_story_part1", FULL_STORY_PART1_TEXT, "en", "digital switch-off period", 60),
    ("full_story_part2", FULL_STORY_PART2_TEXT, "en", "just one more", 60),
    ("point_one", POINT_ONE_TEXT, "en", "309 families", 60),
    ("point_two", POINT_TWO_TEXT, "en", "seven in ten children", 60),
    ("in_one_line", IN_ONE_LINE_TEXT, "en", "go to sleep", 60),
]


def stage_a2_generate_new_segments() -> dict:
    narration_dir = f"{OUT_DIR}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    results = {}
    for name, text, language, expected_substring, max_extra_chars in _SEGMENTS:
        out_path = f"{narration_dir}/{name}.wav"
        result = generate_narration_snippet_verified_strict(
            text, language, out_path, expected_substring, max_attempts=6, max_extra_chars=max_extra_chars)
        results[name] = result

    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    with open(f"{OUT_DIR}/audit/new_segments_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    all_ok = all(r.get("status") == "OK" for r in results.values())
    return {"status": "OK" if all_ok else "STOPPED", "results": results}


# ============================================================
# ブロック2: 全体組み立て
# ============================================================
SR = p9a.TARGET_SAMPLE_RATE


def load_all_sources() -> dict:
    """B1既存資産(Intro/notification/Outro/サービス共通ナレーション/
    topic_intro/japanese_title/meaning_1-5/Key Phrase Components/
    承認済みPreview)はrepro01.load_all_sourcesと全く同じ実体を再利用する
    (同じB1_OUT_DIRから読み込むため、A2側で新規生成しない)。新規segment
    (Comment1-4/Full Story Part1-2/Point One-Two/In One Line)だけを
    追加で読み込む。"""
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    preview_mono, preview_sr, _, _ = common.read_wav_float(repro01.PREVIEW_PATH)
    assert preview_sr == common.SAMPLE_RATE

    narration = {}
    for name in repro01.SERVICE_LEVEL_NARRATION_NAMES:
        mono, sr, _, _ = common.read_wav_float(f"{repro01.A01_NARRATION_DIR}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("topic_intro", "japanese_title", "meaning_1", "meaning_2", "meaning_3", "meaning_4", "meaning_5"):
        mono, sr, _, _ = common.read_wav_float(f"{B1_OUT_DIR}/narration/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono

    key_phrase_components = {}
    for kp in repro01.A02_KEY_PHRASES:
        mono, sr, _, _ = common.read_wav_float(kp["component_path"])
        key_phrase_components[kp["number"]] = p9a.p7c.tight_speech_only(mono, sr)

    a2_segments = {}
    for name, _text, _lang, _sub, _max in _SEGMENTS:
        mono, sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/{name}.wav")
        assert sr == common.SAMPLE_RATE
        a2_segments[name] = mono

    return {
        "intro": intro, "notification": notification, "outro": outro,
        "preview_mono": preview_mono, "narration": narration,
        "key_phrase_components": key_phrase_components,
        "a2_segments": a2_segments,
    }


def apply_gain_and_convert(sources: dict) -> dict:
    """B1(repro01.apply_gain_and_convert)と同じ考え方。Previewは無加工の
    まま基準の一部とする。target_rmsはPreviewとA2の新規本編相当(Full Story
    Part1)の平均とする(B1のPreview/Body平均と同じ考え方)。Intro/
    notification/新規ナレーション/A2新規segmentは平均RMSへ、Outroだけは
    Introの調整後RMSへ合わせる。"""
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
    result["outro"] = gain_to_rms(sources["outro"]["samples"], intro_final_rms, "outro")
    gain_report["outro"]["matched_to"] = "intro_post_gain_rms"
    gain_report["outro"]["intro_post_gain_rms"] = round(intro_final_rms, 5)

    result["preview"] = p9a.mono_24k_to_stereo_target(sources["preview_mono"])  # 無加工(ユーザー承認済み)

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

    gain_report["preview"] = {"gain": 1.0, "note": "無加工(ユーザー承認済み音声を保持)"}
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


# パート順・パート名(タイムライン報告用に名前を保持しながら組み立てる)
def build_pieces_with_timeline(parts: dict) -> "tuple[np.ndarray, list]":
    key_phrase_blocks = build_key_phrase_blocks(parts)
    a2 = parts["a2_segments"]

    # (name, samples) のリストとして構築する。silenceにも名前を付け、
    # タイムライン報告で「どのポーズか」を追跡できるようにする。
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
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Preview", parts["preview"]),
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
        # --- ここからA2固有(ER-003-A2-AUDIO-01) ---
        # EN→JA切替: 1.0秒。JA→EN切替: 0.8秒。同一言語(EN→EN)の
        # Point One→Point Two、In One Line→Outroは既存慣例の0.5秒。
        # 新規Transition効果音は追加しない(ポーズのみ)。
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
        ("Comment 4", a2["comment_4"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("In One Line", a2["in_one_line"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        # --- A2固有ここまで ---
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


def stage_a2_assemble() -> dict:
    os.makedirs(f"{OUT_DIR}/assembled", exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    sources = load_all_sources()
    parts = apply_gain_and_convert(sources)
    result = assemble_with_timeline(parts)
    assembled = result["assembled"]

    out_path = f"{OUT_DIR}/assembled/English_Your_Way_A2_A02.wav"
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
    r1 = stage_a2_generate_new_segments()
    print("stage_a2_generate_new_segments status:", r1["status"])
    if r1["status"] == "OK":
        r2 = stage_a2_assemble()
        print("stage_a2_assemble status:", r2["status"])
        print("duration:", r2["duration_seconds"], "peak:", r2["peak"], "clipping:", r2["clipping_detected"])
