# ============================================================
# er011_no18_evidence_compression_a_precision_21r_audio_stage.py
# ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R
# ============================================================
# er011_no18_evidence_compression_a_precision_21r_production_regen.pyで
# 生成したNo.18 A2/B1新article(Pattern A + Precision反映)から、既存の
# 再利用可能な音声パーツ(Support/Key Phrase/変更のないEnglish segment)は
# 一切再TTSせずそのままコピーし、テキストが実際に変わったsegmentだけを
# 正式Production TTS関数で再生成する(§6)。
#
# 対象segment(A2/B1共通、parts.jsonの7フィールドから機械的に導出):
#   topic_intro(title依存) / full_story_part1 / full_story_part2 /
#   point_one / point_two / point_one_heading / point_two_heading /
#   in_one_line
# Support(preview/comment_1-4)・Key Phrase(kp{rank}_en/meaning_i/kp_ja)は
# 今回Scaffold自体を再実行しない(再実行するとLLMが新しい日本語文言を
# 生成し、Evidence Compressionと無関係な箇所まで書き変わってしまうため)。
# 常に既存specfix_v2のSupport/Key Phrase成果物をそのまま再利用する。
#
# A2の最終候補Assemblyのみ、ユーザー承認済みのTrial-15条件(tight_speech_
# only()の一時的な恒等関数化)を適用する。Production正式コード
# (er003_v1_n3_01_assemble.py)は一切変更しない
# (er011_no18_tight_speech_only_removal_trial_15.pyと同じcontextmanager
# 手法を再利用、runが終わったら必ず元へ戻す)。B1には適用しない。

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_crosslevel_audio_02_common as c
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er011_no18_evidence_compression_a_precision_21r_production_regen as regen

OLD_OUT_DIR = regen.OLD_OUT_DIR
NEW_OUT_DIR = regen.NEW_OUT_DIR
NEW_THEME_ID = regen.NEW_THEME_ID

DIFF_FIELDS = {
    # parts.jsonのフィールド名 -> narration segment名
    "part1": "full_story_part1", "part2": "full_story_part2",
    "point_one_body": "point_one", "point_two_body": "point_two",
    "point_one_heading": "point_one_heading", "point_two_heading": "point_two_heading",
    "in_one_line": "in_one_line",
}


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


# ------------------------------------------------------------
# §1: 既存specfix_v2のnarration/key_phrases/tts_generation_resultsを
#     新theme dirへ丸ごとコピー(TTS再生成なしの既定状態を作る)
# ------------------------------------------------------------
def prepare_reused_assets(level: str) -> dict:
    old_level_dir = f"{OLD_OUT_DIR}/{level}"
    new_level_dir = f"{NEW_OUT_DIR}/{level}"

    new_narration_dir = f"{new_level_dir}/narration"
    if os.path.exists(new_narration_dir):
        shutil.rmtree(new_narration_dir)
    shutil.copytree(f"{old_level_dir}/narration", new_narration_dir)

    new_kp_dir = f"{new_level_dir}/key_phrases"
    if os.path.exists(new_kp_dir):
        shutil.rmtree(new_kp_dir)
    shutil.copytree(f"{old_level_dir}/key_phrases", new_kp_dir)

    support_filename = "a2_support_texts.json" if level == "a2" else "b1_support_texts.json"
    shutil.copyfile(f"{old_level_dir}/{support_filename}", f"{new_level_dir}/{support_filename}")

    os.makedirs(f"{new_level_dir}/audit", exist_ok=True)
    shutil.copyfile(f"{old_level_dir}/audit/tts_generation_results.json",
                     f"{new_level_dir}/audit/tts_generation_results.json")
    old_approvals = f"{old_level_dir}/audit/human_approved_segments.json"
    if os.path.exists(old_approvals):
        shutil.copyfile(old_approvals, f"{new_level_dir}/audit/human_approved_segments.json")

    print(f"[21R-AUDIO] {level}: narration/key_phrases/support/tts_generation_resultsを"
          f"{old_level_dir}から丸ごとコピーしました(この時点では全segment未変更として扱う)。")
    return {"narration_dir": new_narration_dir, "level_dir": new_level_dir}


# ------------------------------------------------------------
# §2: parts.jsonを新articleから機械的に再構築し、旧parts.jsonとの
#     フィールド単位diffでsegment単位の再TTS要否を判定する
# ------------------------------------------------------------
def compute_parts_diff(level: str) -> dict:
    new_level_dir = f"{NEW_OUT_DIR}/{level}"
    with open(f"{new_level_dir}/article.md", encoding="utf-8") as f:
        new_article_text = f.read()
    new_parts = sc.split_article_text(new_article_text)
    with open(f"{new_level_dir}/parts.json", "w", encoding="utf-8") as f:
        json.dump(new_parts, f, ensure_ascii=False, indent=2)

    with open(f"{OLD_OUT_DIR}/{level}/parts.json", encoding="utf-8") as f:
        old_parts = json.load(f)

    title_changed = new_parts["title"] != old_parts["title"]
    changed_segments = {"topic_intro": title_changed, "japanese_title": False}
    for field, seg_name in DIFF_FIELDS.items():
        changed_segments[seg_name] = new_parts[field] != old_parts[field]

    return {"new_parts": new_parts, "old_parts": old_parts,
            "title_changed": title_changed, "changed_segments": changed_segments}


# ------------------------------------------------------------
# §3: 変更されたsegmentだけを正式Production TTS関数で再生成する
#     (generate_a2_segments/generate_b1_segmentsと同一の呼び出し方)
# ------------------------------------------------------------
def regenerate_changed_segments_a2(diff: dict) -> dict:
    level_dir = f"{NEW_OUT_DIR}/a2"
    narration_dir = f"{level_dir}/narration"
    parts = diff["new_parts"]
    changed = diff["changed_segments"]
    results_path = f"{level_dir}/audit/tts_generation_results.json"
    with open(results_path, encoding="utf-8") as f:
        results_data = json.load(f)
    segments = results_data["segments"]
    regenerated = []

    if changed["topic_intro"]:
        topic_intro_text = f"Today's topic is {parts['title']}."
        print(f"[21R-AUDIO][a2] topic_intro再生成(title変更あり)...")
        r = c.generate_english_segment_with_fallback(
            tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(topic_intro_text)),
            f"{narration_dir}/topic_intro.wav", tts_gen.first_words(parts["title"], 3), max_extra_chars=30)
        r["canonical_text"] = topic_intro_text
        segments["topic_intro"] = r
        regenerated.append("topic_intro")

    for name in ("point_one_heading", "point_two_heading"):
        if not changed[name]:
            continue
        text = parts["point_one_heading"] if name == "point_one_heading" else parts["point_two_heading"]
        sc.assert_no_point_number_label(text, name)
        tts_input = tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text))
        print(f"[21R-AUDIO][a2] {name}再生成(text変更あり)...")
        r = tts_gen.generate_a2_segment_with_slowdown(
            tts_input, f"{narration_dir}/{name}.wav", tts_gen.first_words(text, 3), max_extra_chars=20,
            style_prefix_override=tts_gen.A2_ENGLISH_STYLE_PREFIX_SLOWER, disfluency_qa=True)
        r["canonical_text"] = text
        segments[name] = r
        regenerated.append(name)

    field_map = {
        "full_story_part1": parts["part1"], "full_story_part2": parts["part2"],
        "point_one": parts["point_one_body"], "point_two": parts["point_two_body"],
        "in_one_line": parts["in_one_line"],
    }
    for name, text in field_map.items():
        if not changed[name]:
            continue
        if name in ("point_one", "point_two"):
            sc.assert_no_point_number_label(text, name)
        tts_input = tts_gen.tts_safe_news_en(text)
        sub = tts_gen.first_words(text)
        print(f"[21R-AUDIO][a2] {name}再生成(text変更あり)...")
        r = tts_gen.generate_a2_segment_with_slowdown(
            tts_input, f"{narration_dir}/{name}.wav", sub,
            style_prefix_override=tts_gen.A2_ENGLISH_STYLE_PREFIX_SLOWER,
            disfluency_qa=(name == "in_one_line"))
        r["canonical_text"] = text
        segments[name] = r
        regenerated.append(name)

    results_data["segments"] = segments
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2, default=str)
    all_status = {k: v.get("status") for k, v in segments.items()}
    with open(f"{level_dir}/run_summary_tts.json", "w", encoding="utf-8") as f:
        json.dump({"segment_status": all_status,
                    "key_phrase_status": results_data.get("key_phrases", {})},
                   f, ensure_ascii=False, indent=2, default=str)
    print(f"[21R-AUDIO][a2] 再TTS対象: {regenerated}")
    return {"regenerated_segments": regenerated, "segment_status": all_status}


def regenerate_changed_segments_b1(diff: dict) -> dict:
    level_dir = f"{NEW_OUT_DIR}/b1b"
    narration_dir = f"{level_dir}/narration"
    parts = diff["new_parts"]
    changed = diff["changed_segments"]
    results_path = f"{level_dir}/audit/tts_generation_results.json"
    with open(results_path, encoding="utf-8") as f:
        results_data = json.load(f)
    segments = results_data["segments"]
    regenerated = []

    if changed["topic_intro"]:
        topic_intro_text = f"Today's topic is {parts['title']}."
        print(f"[21R-AUDIO][b1b] topic_intro再生成(title変更あり)...")
        r = voice01.generate_charon_english(
            tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(topic_intro_text)),
            f"{narration_dir}/topic_intro.wav")
        r["canonical_text"] = topic_intro_text
        segments["topic_intro"] = r
        regenerated.append("topic_intro")

    for name in ("point_one_heading", "point_two_heading"):
        if not changed[name]:
            continue
        text = parts["point_one_heading"] if name == "point_one_heading" else parts["point_two_heading"]
        sc.assert_no_point_number_label(text, name)
        print(f"[21R-AUDIO][b1b] {name}再生成(text変更あり)...")
        r = point_headings.generate(
            tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text)), f"{narration_dir}/{name}.wav")
        r["canonical_text"] = text
        segments[name] = r
        regenerated.append(name)

    field_map = {
        "full_story_part1": parts["part1"], "full_story_part2": parts["part2"],
        "point_one": parts["point_one_body"], "point_two": parts["point_two_body"],
        "in_one_line": parts["in_one_line"],
    }
    for name, text in field_map.items():
        if not changed[name]:
            continue
        if name in ("point_one", "point_two"):
            sc.assert_no_point_number_label(text, name)
        print(f"[21R-AUDIO][b1b] {name}再生成(text変更あり)...")
        r = news_tail_fix.generate_news_narration_wide_margin(
            tts_gen.tts_safe_news_en(text), f"{narration_dir}/{name}.wav",
            disfluency_qa=(name == "in_one_line"))
        r["canonical_text"] = text
        segments[name] = r
        regenerated.append(name)

    results_data["segments"] = segments
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2, default=str)
    all_status = {k: v.get("status") for k, v in segments.items()}
    with open(f"{level_dir}/run_summary_tts.json", "w", encoding="utf-8") as f:
        json.dump({"segment_status": all_status,
                    "key_phrase_status": results_data.get("key_phrases", {})},
                   f, ensure_ascii=False, indent=2, default=str)
    print(f"[21R-AUDIO][b1b] 再TTS対象: {regenerated}")
    return {"regenerated_segments": regenerated, "segment_status": all_status}


# ------------------------------------------------------------
# §4: A2最終候補Assemblyのみ、tight_speech_only()をTrial-15と同じ手法で
#     一時的に恒等関数化する(Production正式コードは変更しない)
# ------------------------------------------------------------
_CALL_LOG = {"identity_calls": 0}


@contextlib.contextmanager
def tight_speech_only_disabled():
    original = asm.p9a.p7c.tight_speech_only
    _CALL_LOG["identity_calls"] = 0

    def _identity(samples, sample_rate):
        _CALL_LOG["identity_calls"] += 1
        return samples

    asm.p9a.p7c.tight_speech_only = _identity
    try:
        yield
    finally:
        asm.p9a.p7c.tight_speech_only = original


# ------------------------------------------------------------
# §5: Assembly実行(実Production関数、theme['out_dir']だけ新theme dirへ)
# ------------------------------------------------------------
def run_assembly() -> dict:
    theme = {"theme_id": NEW_THEME_ID, "out_dir": NEW_OUT_DIR}

    print("[21R-AUDIO] B1 Assembly(通常経路、tight_speech_only無関係)開始...")
    b1_summary = asm.stage_assemble_b1(theme)

    print("[21R-AUDIO] A2 Assembly(Trial-15条件: tight_speech_only一時的に恒等関数化)開始...")
    with tight_speech_only_disabled():
        a2_summary = asm.stage_assemble_a2(theme)
    a2_summary["tight_speech_only_identity_calls"] = _CALL_LOG["identity_calls"]
    a2_summary["tight_speech_only_removal_trial_condition"] = True

    return {"b1b": b1_summary, "a2": a2_summary}


def main() -> dict:
    cl.install(f"{NEW_OUT_DIR}/raw_usage_log_21r_audio.jsonl")
    summary = {}
    for level in ("a2", "b1b"):
        prepare_reused_assets(level)
        diff = compute_parts_diff(level)
        with open(f"{NEW_OUT_DIR}/{level}/audit/parts_diff_21r.json", "w", encoding="utf-8") as f:
            json.dump({"changed_segments": diff["changed_segments"]}, f, ensure_ascii=False, indent=2)
        if level == "a2":
            tts_result = regenerate_changed_segments_a2(diff)
        else:
            tts_result = regenerate_changed_segments_b1(diff)
        summary[level] = {"changed_segments": diff["changed_segments"], "tts_result": tts_result}

    assemble_result = run_assembly()
    summary["assemble"] = assemble_result
    with open(f"{NEW_OUT_DIR}/audio_stage_21r_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[21R-AUDIO] 完了。summary -> {NEW_OUT_DIR}/audio_stage_21r_summary.json")
    return summary


if __name__ == "__main__":
    main()
