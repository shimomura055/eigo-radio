# ============================================================
# er019_family_x_pointless_tts_01.py
# NEWS-FAMILY-X-POINTLESS-TRIAL-01 Phase B
# ============================================================
# Family X(Point構造廃止)向けB1 segment TTS生成。低レベル生成関数
# (voice01.generate_charon_english / news_tail_fix.generate_news_
# narration_wide_margin / er006_audio_cost_pilot_02_shared_narration.
# ensure_fixed_english_segment、disfluency QA/Connected Speech
# Equivalence Layer/Repetition QA/Human Review Lockを内包)は、
# 既存Family Aモジュールからそのままimportして呼ぶ(モジュール自体は
# 無変更)。Point前提の上位ループ(generate_b1_segments、
# point_one/two_heading・point_one/two・Key Phrase 5件を含む)は
# コピーせず、Family X専用のsegment集合(topic_intro/preview/
# comment_1-4/full_story_part1-3/in_one_line)のみを新規に組み立てる。
#
# Key Phraseは生成しない(構造比較に不要、Fable指示どおり)。

from __future__ import annotations

import json
import os

import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration

# Family X front-half(Intro/Welcome/Topic intro/Notification/Preview
# intro/Full story intro)は、Key Phrase blockを持たないため、既存
# ensure_all_shared_narration_b1()(welcome/preview_intro/key_phrases_
# intro/full_story_intro/num_one〜five の7件を一括取得)は呼ばず、
# 実際に使う3件(welcome/preview_intro/full_story_intro)のみを
# Master Audio Store経由で取得する(低レベルヘルパーensure_fixed_
# english_segment自体は無変更のまま個別に呼ぶ)。
_FAMILY_X_SHARED_NARRATION_NAMES = ("welcome", "preview_intro", "full_story_intro")

# full_story_part3はfull_story_part1/2と同種(B1英語本文segment)のため、
# OPEN-121/OPEN-122で承認済みのConnected Speech Equivalence Layer/
# Repetition QAの対象範囲をfull_story_part3にも一般化して適用する
# (Sonnet判断、既存Production対象の拡大ではなくFamily X Trial限定。
# 新しい検証ロジックの追加ではなく、既存の承認済みQAをこのTrialの
# 同種segmentへも及ぼすだけであり、判定基準自体は無変更)。
_BODY_PART_NAMES = ("full_story_part1", "full_story_part2", "full_story_part3")


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def ensure_family_x_shared_narration_b1(narration_dir: str) -> dict:
    os.makedirs(narration_dir, exist_ok=True)
    results = {}
    for name in _FAMILY_X_SHARED_NARRATION_NAMES:
        results[name] = shared_narration.ensure_fixed_english_segment(name, narration_dir, filename_suffix="_charon")
    return results


def generate_family_x_b1_segments(theme: dict) -> dict:
    theme_id = theme["theme_id"]
    out_dir = f"{theme['out_dir']}/b1b"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)

    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/b1_support_texts.json")

    ensure_family_x_shared_narration_b1(narration_dir)

    results = {}

    topic_intro_text = f"Today's topic is {parts['title']}."
    print(f"[FAMILY-X-TTS][{theme_id}/b1b] topic_intro生成(Charon)...")
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = voice01.generate_charon_english(
            n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_intro_text)), f"{narration_dir}/topic_intro.wav")
    results["topic_intro"]["canonical_text"] = topic_intro_text

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        print(f"[FAMILY-X-TTS][{theme_id}/b1b] {name}生成(Charon)...")
        with cl.segment_context(name):
            results[name] = voice01.generate_charon_english(
                n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(text)), f"{narration_dir}/{name}.wav",
                style_prefix_override=n3_tts.B1_PREVIEW_STYLE_PREFIX_CALM,
                disfluency_qa=True)
        results[name]["canonical_text"] = text

    for name, text in (
        ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
        ("full_story_part3", parts["part3"]), ("in_one_line", parts["in_one_line"]),
    ):
        print(f"[FAMILY-X-TTS][{theme_id}/b1b] {name}生成(Aoede、News本文)...")
        with cl.segment_context(name):
            results[name] = news_tail_fix.generate_news_narration_wide_margin(
                n3_tts.tts_safe_news_en(text), f"{narration_dir}/{name}.wav",
                disfluency_qa=(name == "in_one_line"),
                enable_connected_speech_equivalence_layer=(name in _BODY_PART_NAMES),
                enable_repetition_qa=(name in _BODY_PART_NAMES))
        results[name]["canonical_text"] = text

    all_status = {k: v.get("status") for k, v in results.items()}
    with open(f"{out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump({"segments": results, "key_phrases": {}}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/run_summary_tts.json", "w", encoding="utf-8") as f:
        json.dump({"segment_status": all_status, "key_phrase_status": {}}, f, ensure_ascii=False, indent=2)
    print(f"[FAMILY-X-TTS][{theme_id}/b1b] 完了。segment_status={all_status}")
    return {"segment_status": all_status, "key_phrase_status": {}}


_COMMENT_GROUP_NAMES = ("preview", "comment_1", "comment_2", "comment_3", "comment_4")
_BODY_GROUP_TEXT_KEYS = {"full_story_part1": "part1", "full_story_part2": "part2",
                          "full_story_part3": "part3", "in_one_line": "in_one_line"}


def regenerate_family_x_b1_segment(theme: dict, name: str) -> dict:
    """既存のASR retry(voice01.generate_charon_english/news_tail_fix.
    generate_news_narration_wide_margin内部、最大review_lock.PRODUCTION_
    MAX_TTS_ATTEMPTS回)を尽くしてもASR_VALIDATION_UNCERTAIN/STOPPEDだった
    segment 1件のみを、独立した新しいtop-level attemptとして再生成する
    (Gate自体を回避・無効化するものではない。既存Family Aの「Human
    Reviewで人間が実際に聴取判断する」運用フローに進む前段の、通常の
    再試行操作)。tts_generation_results.jsonの当該entryのみを差し替える。"""
    theme_id = theme["theme_id"]
    out_dir = f"{theme['out_dir']}/b1b"
    narration_dir = f"{out_dir}/narration"

    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/b1_support_texts.json")
    all_results = load_json(f"{out_dir}/audit/tts_generation_results.json")

    if name in _COMMENT_GROUP_NAMES:
        text = support[name]
        print(f"[FAMILY-X-TTS][{theme_id}/b1b] {name} 再生成(Charon)...")
        with cl.segment_context(name):
            entry = voice01.generate_charon_english(
                n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(text)), f"{narration_dir}/{name}.wav",
                style_prefix_override=n3_tts.B1_PREVIEW_STYLE_PREFIX_CALM,
                disfluency_qa=True)
    elif name in _BODY_GROUP_TEXT_KEYS:
        text = parts[_BODY_GROUP_TEXT_KEYS[name]]
        print(f"[FAMILY-X-TTS][{theme_id}/b1b] {name} 再生成(Aoede、News本文)...")
        with cl.segment_context(name):
            entry = news_tail_fix.generate_news_narration_wide_margin(
                n3_tts.tts_safe_news_en(text), f"{narration_dir}/{name}.wav",
                disfluency_qa=(name == "in_one_line"),
                enable_connected_speech_equivalence_layer=(name in _BODY_PART_NAMES),
                enable_repetition_qa=(name in _BODY_PART_NAMES))
    else:
        raise ValueError(f"regenerate_family_x_b1_segment: 未対応のsegment名です: {name!r}")

    entry["canonical_text"] = text
    all_results["segments"][name] = entry
    with open(f"{out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    run_summary = load_json(f"{out_dir}/run_summary_tts.json")
    run_summary["segment_status"][name] = entry.get("status")
    with open(f"{out_dir}/run_summary_tts.json", "w", encoding="utf-8") as f:
        json.dump(run_summary, f, ensure_ascii=False, indent=2)
    print(f"[FAMILY-X-TTS][{theme_id}/b1b] {name} 再生成完了: status={entry.get('status')}")
    return entry
