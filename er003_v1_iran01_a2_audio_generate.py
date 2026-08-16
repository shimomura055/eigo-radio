# ============================================================
# er003_v1_iran01_a2_audio_generate.py
# ER-003-IRAN-A2-B1-01: IRAN01 A2 Full Audio(単一Aoede voice、
# 日本語Preview/Comment、英語News本文)
# ============================================================
# A2の既存確立済みアーキテクチャ(er003_v1_crosslevel_audio_02_common.py、
# ADD03/A01で確立)をそのまま再利用する。今回のB1 Voice Allocation
# (Charon/Aoede分割)はA2へ一切移植しない(ユーザー明示指示)。
# Shell共通文言(welcome/preview_intro/point_explanation/
# key_phrases_intro/full_story_intro/num_one〜five)は、記事非依存の
# サービス共通音声としてA01の既存ファイルをそのまま再利用し、新規TTSは
# 行わない。topic_intro/japanese_titleのみ記事固有のため新規生成する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_iran01_a2_audio_generate.py

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_crosslevel_audio_02_common as c
import er003_v1_iran01_articles_generate as gen

ARTICLE_ID = "IRAN01_A2"
OUT_DIR = f"{gen.OUT_DIR}/a2_audio"
NARRATION_DIR = f"{OUT_DIR}/narration"
SR = c.SR

with open(f"{gen.OUT_DIR}/a2/fixed_news_parts.json", encoding="utf-8") as f:
    A2_PARTS = json.load(f)
with open(f"{gen.OUT_DIR}/a2/support_texts_ja.json", encoding="utf-8") as f:
    A2_SUPPORT_JA = json.load(f)
with open(f"{gen.OUT_DIR}/a2/key_phrases/keywords_canonicalized.json", encoding="utf-8") as f:
    A2_KP = json.load(f)

ENGLISH_TITLE_TEXT = A2_PARTS["title"]
TOPIC_INTRO_TEXT = f"Today's topic is {ENGLISH_TITLE_TEXT}."
JAPANESE_TITLE_TEXT = "「海峡を我が領土に」という発言の裏で、イランとオマーンは静かに新しい航路の合意へ動いていた"

KEY_PHRASES = tuple(
    {"number": ("One", "Two", "Three", "Four", "Five")[item["rank"] - 1],
     "used_form": item["used_form"], "japanese_gloss": item["japanese_gloss"], "at_risk": False,
     "final_phoneme_note": "(A2 IRAN01、簡略トリアージにより試作は省略)"}
    for item in sorted(A2_KP["items"], key=lambda it: it["rank"])
)

_SEGMENTS = [
    ("topic_intro", TOPIC_INTRO_TEXT, "en", "Trump talks territory", 30),
    ("japanese_title", JAPANESE_TITLE_TEXT, "ja", "航路の合意", 30),
    ("preview", A2_SUPPORT_JA["preview"], "ja", "石油の流れ", 60),
    ("comment_1", A2_SUPPORT_JA["comment_1"], "ja", "事実なのか", 40),
    ("comment_2", A2_SUPPORT_JA["comment_2"], "ja", "領土になった", 40),
    ("comment_3", A2_SUPPORT_JA["comment_3"], "ja", "航路図", 40),
    ("comment_4", A2_SUPPORT_JA["comment_4"], "ja", "一文で確認", 40),
    ("full_story_part1", A2_PARTS["part1"], "en", "Strait of Hormuz", 60),
    ("full_story_part2", A2_PARTS["part2"], "en", "shipping route map", 60),
    ("point_one", A2_PARTS["point_one_body"], "en", "one-fifth", 60),
    ("point_two", A2_PARTS["point_two_body"], "en", "ship incidents", 60),
    ("in_one_line", A2_PARTS["in_one_line"], "en", "route map", 60),
]
for i, kp in enumerate(sorted(A2_KP["items"], key=lambda it: it["rank"]), start=1):
    gloss = kp["japanese_gloss"]
    _SEGMENTS.append((f"meaning_{i}", gloss, "ja", gloss[:4], 40))

CONFIG = {
    "article_id": ARTICLE_ID,
    "out_dir": OUT_DIR,
    "key_phrases": KEY_PHRASES,
    "segments": _SEGMENTS,
}


# ============================================================
# 組み立て(topic_intro/japanese_titleを記事固有narration_dirから
# 読み込む点のみ、共通モジュールのload_all_sources/build_pieces_with_
# timelineから差し替える。それ以外の値・順序・pauseはA2既存仕様どおり)
# ============================================================
def load_all_sources_local(config: dict) -> dict:
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    narration_dir = f"{config['out_dir']}/narration"
    preview_mono, preview_sr, _, _ = common.read_wav_float(f"{narration_dir}/preview.wav")
    assert preview_sr == common.SAMPLE_RATE

    narration = {}
    for name in c.SERVICE_LEVEL_NARRATION_NAMES:
        mono, sr, _, _ = common.read_wav_float(f"{c.A01_NARRATION_DIR}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("topic_intro", "japanese_title"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for i in range(1, len(config["key_phrases"]) + 1):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/meaning_{i}.wav")
        assert sr == common.SAMPLE_RATE
        narration[f"meaning_{i}"] = mono

    key_phrase_components = {}
    for kp in config["key_phrases"]:
        path = c._adopted_component_path(config, kp)
        mono, sr, _, _ = common.read_wav_float(path)
        key_phrase_components[kp["number"]] = p9a.p7c.tight_speech_only(mono, sr)

    a2_segments = {}
    for name, _text, _lang, _sub, _max in config["segments"]:
        if name in ("preview", "topic_intro", "japanese_title") or name.startswith("meaning_"):
            continue
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        a2_segments[name] = mono

    return {
        "intro": intro, "notification": notification, "outro": outro,
        "preview_mono": preview_mono, "narration": narration,
        "key_phrase_components": key_phrase_components,
        "a2_segments": a2_segments,
    }


def stage_assemble_local(config: dict) -> dict:
    os.makedirs(f"{config['out_dir']}/assembled", exist_ok=True)
    os.makedirs(f"{config['out_dir']}/audit", exist_ok=True)
    sources = load_all_sources_local(config)
    parts = c.apply_gain_and_convert(sources)
    result = c.assemble_with_timeline(config, parts)
    assembled = result["assembled"]

    out_path = f"{config['out_dir']}/assembled/English_Your_Way_A2_{config['article_id']}.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{config['out_dir']}/audit/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{config['out_dir']}/audit/timeline.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    return {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2,
    }


def main():
    r1 = c.generate_text_segments(CONFIG)
    print(f"[{ARTICLE_ID}] generate_text_segments status:", r1["status"])
    if r1["status"] != "OK":
        failed = [k for k, v in r1["results"].items() if v.get("status") != "OK"]
        print(f"[{ARTICLE_ID}] 失敗segment:", failed)
        return

    r2 = c.generate_key_phrase_components(CONFIG)
    print(f"[{ARTICLE_ID}] generate_key_phrase_components status:", r2["status"])
    if r2["status"] != "OK":
        return

    r3 = stage_assemble_local(CONFIG)
    print(f"[{ARTICLE_ID}] stage_assemble status:", r3["status"], "duration:", r3["duration_seconds"],
          "peak:", r3["peak"], "clipping:", r3["clipping_detected"])

    with open(f"{OUT_DIR}/run_summary_audio.json", "w", encoding="utf-8") as f:
        json.dump({"text_segments": r1["status"], "key_phrase_components": r2["status"], "assemble": r3},
                   f, ensure_ascii=False, indent=2, default=str)
    print(f"[{ARTICLE_ID}] 完了。")


if __name__ == "__main__":
    main()
