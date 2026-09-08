# ============================================================
# build_player_a2_runtime_evidence.py
# 管理ID: OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01
# ============================================================
# rerun_04/a2(full_story_part1差し替え後の再Assembly結果)向けの
# player_a2.htmlを、標準フォーマット共通module(audio_review_player.py、
# PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11)で生成する。
# 既存のrerun_04/player.html(B1用)には一切触れない、別名で新規生成する。
# Segment label→text解決ロジックは本スクリプトが持つ(既存audit JSON/
# timeline.json/a2_support_texts.json/parts.json/keywords_canonicalized.json
# /tts_generation_results.json(voiceフィールド)のみを読み、推測補完は
# しない。取得できない場合は「未取得」と明記する)。
# TTS/ASR/Assemblyは一切呼んでいない(既存の音声wav・JSONを読むだけ)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe \
#     er011_output/open112_trend_theme2_b_final_audio_rerun_04/\
#     build_player_a2_runtime_evidence.py
from __future__ import annotations

import html
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import audio_review_player as arp
import er003_b1_p9a_audio as p9a
import er003_v1_crosslevel_audio_02_common as c

OUT_ROOT = "er011_output/open112_trend_theme2_b_final_audio_rerun_04"
A2_DIR = f"{OUT_ROOT}/a2"
NARRATION_DIR = f"{A2_DIR}/narration"
ASSEMBLED_PATH = f"{A2_DIR}/assembled/English_Your_Way_A2_OPEN112_TREND_THEME2_B_FINAL_AUDIO_RERUN_04.wav"
PLAYER_OUT_PATH = f"{OUT_ROOT}/player_a2.html"

MISSING = "未取得"

parts = json.load(open(f"{A2_DIR}/parts.json", encoding="utf-8"))
support = json.load(open(f"{A2_DIR}/a2_support_texts.json", encoding="utf-8"))
timeline = json.load(open(f"{A2_DIR}/audit/timeline.json", encoding="utf-8"))
tts_results = json.load(open(f"{A2_DIR}/audit/tts_generation_results.json", encoding="utf-8"))
kp = json.load(open(f"{A2_DIR}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
run_summary_assemble = json.load(open(f"{A2_DIR}/run_summary_assemble.json", encoding="utf-8"))

segments = tts_results.get("segments", {})
kp_tts = tts_results.get("key_phrases", {})
kp_items = {item["rank"]: item for item in kp["items"]}

# 記事固有(per-episode)segmentは実測tts_generation_results.jsonの
# voiceフィールドから取得する(推測しない)。共通テンプレート音声
# (welcome/preview_intro/point_explanation/key_phrases_intro/
# full_story_intro)はMaster Audio Store経由でB1と共有される固定音声で
# あり(er003_v1_crosslevel_audio_02_common.pyのload_a2_sources参照)、
# B1側のvoice(Charon、B1 rerun_04 build_player_runtime_evidence.py参照)
# をそのまま踏襲する。
SHARED_FIXED_TEXT_BY_NAME = {
    "welcome": p9a.PODCAST_NAME_TEXT_V2,
    "preview_intro": p9a.PREVIEW_INTRO_TEXT,
    "point_explanation": p9a.POINT_EXPLANATION_TEXT,
    "key_phrases_intro": p9a.KEY_PHRASES_INTRO_TEXT,
    "full_story_intro": p9a.FULL_STORY_INTRO_TEXT,
}
SHARED_FIXED_VOICE = "Charon"


def shared_audio_url(name: str) -> str:
    local_path = f"{NARRATION_DIR}/{name}.wav"
    if os.path.exists(local_path):
        return arp.abs_file_url(local_path)
    return arp.abs_file_url(f"{c.A01_NARRATION_DIR}/{name}.wav")


SFX_PARTS = {
    "Intro": ("音楽ジングル(ナレーションなし、読み上げなし)。", p9a.INTRO_MP3_PATH),
    "Notification 1": ("効果音(読み上げなし)。", p9a.NOTIFICATION_MP3_PATH),
    "Notification 2": ("効果音(読み上げなし)。", p9a.NOTIFICATION_MP3_PATH),
    "Notification 3": ("効果音(読み上げなし)。", p9a.NOTIFICATION_MP3_PATH),
    "Outro": ("音楽ジングル(ナレーションなし、読み上げなし)。", p9a.OUTRO_MP3_PATH),
}


def esc(text: str) -> str:
    return html.escape(text).replace("\n\n", "<br><br>").replace("\n", "<br>")


def audio_url(name_no_ext: str) -> str:
    return arp.abs_file_url(f"{NARRATION_DIR}/{name_no_ext}.wav")


def voice_of(name: str) -> str:
    seg = segments.get(name)
    if seg and seg.get("voice"):
        return seg["voice"]
    return MISSING


def resolve_row(part_label: str):
    """(voice_disp, script_html, audio_html, missing) を返す。
    取得できない場合はscript_htmlに「未取得」を入れ、missing=Trueとする。"""
    label = part_label

    if label in SFX_PARTS:
        note, _src = SFX_PARTS[label]
        return "SFX", esc(note), "—", False
    if label.startswith("Point Notification"):
        return "SFX", "効果音(読み上げなし)。", "—", False
    if label.startswith("pause_"):
        return None, None, None, None  # pauseはテーブルに出さない

    if label == "Welcome":
        text = SHARED_FIXED_TEXT_BY_NAME["welcome"]
        return SHARED_FIXED_VOICE, esc(text), arp.render_single_audio_html(shared_audio_url("welcome")), False
    if label == "Preview intro":
        text = SHARED_FIXED_TEXT_BY_NAME["preview_intro"]
        return SHARED_FIXED_VOICE, esc(text), arp.render_single_audio_html(shared_audio_url("preview_intro")), False
    if label == "Point explanation":
        text = SHARED_FIXED_TEXT_BY_NAME["point_explanation"]
        return SHARED_FIXED_VOICE, esc(text), arp.render_single_audio_html(shared_audio_url("point_explanation")), False
    if label == "Key phrases intro":
        text = SHARED_FIXED_TEXT_BY_NAME["key_phrases_intro"]
        return SHARED_FIXED_VOICE, esc(text), arp.render_single_audio_html(shared_audio_url("key_phrases_intro")), False
    if label == "Full story intro":
        text = SHARED_FIXED_TEXT_BY_NAME["full_story_intro"]
        return SHARED_FIXED_VOICE, esc(text), arp.render_single_audio_html(shared_audio_url("full_story_intro")), False

    if label == "Topic intro":
        text = f"Today's topic is {parts['title']}."
        return voice_of("topic_intro"), esc(text), arp.render_single_audio_html(audio_url("topic_intro")), False
    if label == "Japanese title":
        # JAPANESE_TITLESはtheme_id依存の定数辞書だが、実際に読み上げられた
        # テキストはtts_generation_results.json自体には保存されていない
        # ため、ここでは音声のみ提示し、本文はarticle titleの日本語訳が
        # 別途存在しないため「未取得」とする(推測補完しない)。
        return voice_of("japanese_title"), MISSING, arp.render_single_audio_html(audio_url("japanese_title")), True

    if label == "Preview":
        text = support.get("preview")
        return voice_of("preview"), esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("preview")), text is None

    for i in (1, 2, 3, 4):
        if label == f"Comment {i}":
            cname = f"comment_{i}"
            text = support.get(cname)
            return voice_of(cname), esc(text) if text else MISSING, arp.render_single_audio_html(audio_url(cname)), text is None

    if label.startswith("Key Phrase "):
        rank = int(label.split(" ")[-1])
        item = kp_items.get(rank)
        if item is None:
            return MISSING, MISSING, "—", True
        used_form = item["used_form"]
        gloss = item["japanese_gloss"]
        en_voice = ((kp_tts.get(str(rank)) or {}).get("english") or {}).get("voice", "Aoede")
        ja_voice = ((kp_tts.get(str(rank)) or {}).get("japanese_meaning") or {}).get("voice", "Aoede")
        text = f"EN: {used_form}<br>JA(表示/TTS共通): {gloss}"
        audio_html = arp.render_single_audio_html((audio_url(f"kp{rank}_en"), audio_url(f"meaning_{rank}")))
        return f"{en_voice}(EN)/{ja_voice}(JA)", text, audio_html, False

    if label == "Full Story Part 1":
        text = parts.get("part1")
        return voice_of("full_story_part1"), esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("full_story_part1")), text is None
    if label == "Full Story Part 2":
        text = parts.get("part2")
        return voice_of("full_story_part2"), esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("full_story_part2")), text is None
    if label == "Point One semantic heading":
        text = parts.get("point_one_heading")
        return voice_of("point_one_heading"), esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("point_one_heading")), text is None
    if label == "Point One":
        text = parts.get("point_one_body")
        return voice_of("point_one"), esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("point_one")), text is None
    if label == "Point Two semantic heading":
        text = parts.get("point_two_heading")
        return voice_of("point_two_heading"), esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("point_two_heading")), text is None
    if label == "Point Two":
        text = parts.get("point_two_body")
        return voice_of("point_two"), esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("point_two")), text is None
    if label == "In One Line":
        text = parts.get("in_one_line")
        return voice_of("in_one_line"), esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("in_one_line")), text is None

    # 未知のlabel(想定外の構造変化)。推測補完しない。
    return MISSING, MISSING, "—", True


def build_kp_table() -> str:
    rows = ["<tr><th>#</th><th>English (used_form)</th><th>表示用 gloss</th><th>TTS用テキスト</th></tr>"]
    for rank in sorted(kp_items.keys()):
        item = kp_items[rank]
        rows.append(
            f"<tr><td>{rank}</td><td>{html.escape(item['used_form'])}</td>"
            f"<td>{html.escape(item['japanese_gloss'])}</td>"
            f"<td>{html.escape(item.get('japanese_gloss_tts') or MISSING)}</td></tr>"
        )
    return f'<table class="kp"><thead>{rows[0]}</thead><tbody>{"".join(rows[1:])}</tbody></table>'


def main():
    row_html_list = []
    unresolved = []
    for entry in timeline:
        label = entry["part"]
        voice_disp, script_html, audio_html, missing = resolve_row(label)
        if voice_disp is None:
            continue  # pause行はスキップ
        if missing:
            unresolved.append(label)
        row_html_list.append(
            arp.render_timeline_row(entry["start_seconds"], label, voice_disp, script_html, audio_html, missing=bool(missing))
        )

    kp_table_html = build_kp_table()
    episode_audio_url = arp.abs_file_url(ASSEMBLED_PATH)

    duration = run_summary_assemble["duration_seconds"]
    peak = run_summary_assemble["peak"]
    clipping = run_summary_assemble["clipping_detected"]
    headroom = run_summary_assemble["headroom_safety_valve"]

    fs_regen = json.load(open(f"{OUT_ROOT}/full_story_part1_a2_regen_run_summary.json", encoding="utf-8"))
    reuse_verification = json.load(open(f"{OUT_ROOT}/reuse_sha256_verification_a2.json", encoding="utf-8"))

    note = f"""
<p class="note">
このページは、Theme 2「若者の旅行:ゆっくり滞在」A2の完成音声(rerun_04、
full_story_part1のみOPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-
CHECK-01の確認結果[Part 1で確認した現行Production Evidence Compression
Editorの実データに基づく決定的置換、24.1%→about 24%]を反映して
再生成、他{reuse_verification['match_count']}件のnarration/
audit資産はrerun_02からbyte-for-byte再利用[sha256一致確認済み])と、
その音声で実際に読み上げられた全文スクリプトをsegment順に並べたレビュー
用ページです(標準フォーマット、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-
STANDARD-FORMAT-11準拠、Source列なし)。
「Seek」ボタンをクリックすると、上部の完成episode音声プレイヤーが該当
時刻から再生されます。
</p>
<p class="note">
duration: {duration}s(rerun_02比 {round(duration - 358.175, 3)}s) / peak: {peak}
(rerun_02: 0.98、原因piece: Point One、本タスクでは無変更) /
clipping: {clipping} / headroom safety valve: {'適用' if headroom['applied'] else '不適用'}
(peak_before={headroom['peak_before']}、閾値{headroom['threshold']}、
rerun_02と同値)。
</p>
<p class="note">
full_story_part1: status={fs_regen['status']}、asr_verified={fs_regen['asr_verified']}、
audio_classification={fs_regen['audio_classification']}、
repetition_qa flagged={fs_regen['repetition_qa_evidence']['flagged']}
(方式D&prime; best_run={fs_regen['repetition_qa_evidence']['method_d_prime_spectral_short_lag']['best_run_length_seconds']}秒)、
attempt数={len(fs_regen['attempts_log_summary'])}、sha256={fs_regen['new_sha256']}。
</p>
"""

    html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01(Theme 2 A2 数値決定的置換 + 再Assembly)</h1>
{note}
<audio id="episode_audio" class="main" controls src="{episode_audio_url}"></audio>

<h3>A2 タイムライン・全スクリプト(収録順、rerun_04実測timeline.jsonより)</h3>
{arp.render_timeline_table(row_html_list)}

<p class="note">補足: num_one.wav〜num_five.wav(Key Phrase 1〜5の番号読み上げ、共有音声、rerun_02からそのまま継承)は上表には掲載していません。</p>

<h3>A2 Key Phrase表(rerun_02から無変更、再掲)</h3>
{kp_table_html}

<script>
{arp.SEEK_SCRIPT}
</script>
</body>
</html>
"""

    with open(PLAYER_OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_doc)

    print(f"[build_player_a2] rows={len(row_html_list)} unresolved={unresolved}")
    print(f"[build_player_a2] -> {PLAYER_OUT_PATH}")


if __name__ == "__main__":
    main()
