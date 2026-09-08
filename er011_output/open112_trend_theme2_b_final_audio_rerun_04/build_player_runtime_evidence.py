# ============================================================
# build_player_runtime_evidence.py
# 管理ID: OPEN-112-THEME2-B1-NUMERIC-PRECISION-MINIMAL-FIX-RERUN-04
# ============================================================
# rerun_04(point_one/point_two差し替え後の再Assembly結果)向けのplayer.html
# を、標準フォーマット共通module(audio_review_player.py、PM-GOVERNANCE-
# AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11)で生成する。Segment label→text
# 解決ロジックは本スクリプトが持つ(既存audit JSON/timeline.json/
# b1_support_texts.json/parts.json/keywords_canonicalized.jsonのみを読み、
# 推測補完はしない。取得できない場合は「未取得」と明記する)。
# TTS/ASR/Assemblyは一切呼んでいない(既存の音声wav・JSONを読むだけ)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe \
#     er011_output/open112_trend_theme2_b_final_audio_rerun_04/\
#     build_player_runtime_evidence.py
from __future__ import annotations

import html
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import audio_review_player as arp
import er003_b1_p9a_audio as p9a

OUT_ROOT = "er011_output/open112_trend_theme2_b_final_audio_rerun_04"
B1_DIR = f"{OUT_ROOT}/b1b"
NARRATION_DIR = f"{B1_DIR}/narration"
ASSEMBLED_PATH = f"{B1_DIR}/assembled/English_Your_Way_B1B_OPEN112_TREND_THEME2_B_FINAL_AUDIO_RERUN_04.wav"
PLAYER_OUT_PATH = f"{OUT_ROOT}/player.html"

MISSING = "未取得"

parts = json.load(open(f"{B1_DIR}/parts.json", encoding="utf-8"))
support = json.load(open(f"{B1_DIR}/b1_support_texts.json", encoding="utf-8"))
timeline = json.load(open(f"{B1_DIR}/audit/timeline.json", encoding="utf-8"))
tts_results = json.load(open(f"{B1_DIR}/audit/tts_generation_results.json", encoding="utf-8"))
kp = json.load(open(f"{B1_DIR}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
run_summary_assemble = json.load(open(f"{B1_DIR}/run_summary_assemble.json", encoding="utf-8"))

segments = tts_results.get("segments", {})
kp_items = {item["rank"]: item for item in kp["items"]}

# Segment名(narration/{name}.wav)への解決。固定テンプレート音声(Master
# Audio Store経由でTTS結果recordを持たない)はp9a定数から取得する(推測ではなく
# 実コード定数)。
FIXED_TEXT_BY_NAME = {
    "welcome_charon": p9a.PODCAST_NAME_TEXT_V2,
    "preview_intro_charon": p9a.PREVIEW_INTRO_TEXT,
    "key_phrases_intro_charon": p9a.KEY_PHRASES_INTRO_TEXT,
    "full_story_intro_charon": p9a.FULL_STORY_INTRO_TEXT,
}

SFX_PARTS = {
    "Intro": ("音楽ジングル(ナレーションなし、読み上げなし)。10.736秒のIntro音楽をそのまま再生。", p9a.INTRO_MP3_PATH),
    "Notification 1": ("効果音(読み上げなし)。", p9a.NOTIFICATION_MP3_PATH),
    "Notification 2": ("効果音(読み上げなし)。", p9a.NOTIFICATION_MP3_PATH),
    "Notification 3": ("効果音(読み上げなし)。", p9a.NOTIFICATION_MP3_PATH),
    "Outro (Charon)": ("音楽ジングル(ナレーションなし、読み上げなし)。6.144秒のOutro音楽をそのまま再生。", p9a.OUTRO_MP3_PATH),
}
# Point Notification(専用効果音、asm.POINT_NOTIFICATION_MP3_PATHと同一)。
POINT_NOTIFICATION_PATH = "C:/Users/tensh/eigo-radio/notification/universfield-new-notification-07-210334.mp3"


def esc(text: str) -> str:
    return html.escape(text).replace("\n\n", "<br><br>").replace("\n", "<br>")


def audio_url(name_no_ext: str) -> str:
    return arp.abs_file_url(f"{NARRATION_DIR}/{name_no_ext}.wav")


def resolve_row(part_label: str, start_sec: float):
    """(voice_disp, script_html, audio_html, missing) を返す。
    取得できない場合はscript_htmlに「未取得」を入れ、missing=Trueとする。"""
    label = part_label

    if label in SFX_PARTS:
        note, _src = SFX_PARTS[label]
        return "SFX", esc(note), "—", False
    if label == "Point Notification (Point One cue)" or label == "Point Notification (Point Two cue)":
        return "SFX", "効果音(読み上げなし)。", "—", False
    if label.startswith("pause_"):
        return None, None, None, None  # pauseはテーブルに出さない(呼び出し側でスキップ)

    if label == "Welcome (Charon)":
        return "Charon", esc(FIXED_TEXT_BY_NAME["welcome_charon"]), arp.render_single_audio_html(audio_url("welcome_charon")), False
    if label == "Preview intro (Charon)":
        return "Charon", esc(FIXED_TEXT_BY_NAME["preview_intro_charon"]), arp.render_single_audio_html(audio_url("preview_intro_charon")), False
    if label == "Key phrases intro (Charon)":
        return "Charon", esc(FIXED_TEXT_BY_NAME["key_phrases_intro_charon"]), arp.render_single_audio_html(audio_url("key_phrases_intro_charon")), False
    if label == "Full story intro (Charon)":
        return "Charon", esc(FIXED_TEXT_BY_NAME["full_story_intro_charon"]), arp.render_single_audio_html(audio_url("full_story_intro_charon")), False

    if label == "Topic intro (Charon)":
        text = f"Today's topic is {parts['title']}."
        return "Charon", esc(text), arp.render_single_audio_html(audio_url("topic_intro")), False

    if label == "Preview (Charon)":
        text = support.get("preview")
        return "Charon", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("preview")), text is None

    for i in (1, 2, 3, 4):
        cname = f"comment_{i}"
        label_prefixes = {
            1: "Comment 1 (Charon)", 2: "Comment 2 (Charon)",
            3: "Comment 3 (Charon, Bridge)", 4: "Comment 4 (Charon)",
        }
        if label == label_prefixes[i]:
            text = support.get(cname)
            return "Charon", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url(cname)), text is None

    if label.startswith("Key Phrase "):
        rank = int(label.split(" ")[-1])
        item = kp_items.get(rank)
        if item is None:
            return "Aoede/Charon", MISSING, "—", True
        used_form = item["used_form"]
        gloss = item["japanese_gloss"]
        text = f"EN: {used_form}<br>JA(表示/TTS共通): {gloss}"
        audio_html = arp.render_single_audio_html((audio_url(f"kp{rank}_en"), audio_url(f"kp{rank}_ja_charon")))
        return "Aoede(EN)/Charon(JA)", text, audio_html, False

    if label == "Full Story Part 1 (Aoede)":
        text = parts.get("part1")
        return "Aoede", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("full_story_part1")), text is None
    if label == "Full Story Part 2 (Aoede)":
        text = parts.get("part2")
        return "Aoede", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("full_story_part2")), text is None
    if label == "Point One semantic heading (Aoede)":
        text = parts.get("point_one_heading")
        return "Aoede", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("point_one_heading")), text is None
    if label == "Point One (Aoede)":
        text = parts.get("point_one_body")
        return "Aoede", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("point_one")), text is None
    if label == "Point Two semantic heading (Aoede)":
        text = parts.get("point_two_heading")
        return "Aoede", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("point_two_heading")), text is None
    if label == "Point Two (Aoede)":
        text = parts.get("point_two_body")
        return "Aoede", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("point_two")), text is None
    if label == "In One Line (Aoede)":
        text = parts.get("in_one_line")
        return "Aoede", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("in_one_line")), text is None

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
        start_sec = entry["start_seconds"]
        voice_disp, script_html, audio_html, missing = resolve_row(label, start_sec)
        if voice_disp is None:
            continue  # pause行はスキップ
        if missing:
            unresolved.append(label)
        row_html_list.append(
            arp.render_timeline_row(start_sec, label, voice_disp, script_html, audio_html, missing=bool(missing))
        )

    kp_table_html = build_kp_table()
    episode_audio_url = arp.abs_file_url(ASSEMBLED_PATH)

    duration = run_summary_assemble["duration_seconds"]
    peak = run_summary_assemble["peak"]
    clipping = run_summary_assemble["clipping_detected"]
    headroom = run_summary_assemble["headroom_safety_valve"]

    point_one_regen = json.load(open(f"{OUT_ROOT}/point_one_two_regen_run_summary.json", encoding="utf-8"))
    reuse_verification = json.load(open(f"{OUT_ROOT}/reuse_sha256_verification.json", encoding="utf-8"))

    note = f"""
<p class="note">
このページは、Theme 2「若者の旅行:ゆっくり滞在」B1の完成音声(rerun_04、
point_one/point_twoの2segmentのみOPEN-112-THEME2-B1-NUMERIC-PRECISION-
WIRING-AUDIT-01のユーザー決定[選択肢A: 決定的置換、25.2%→about 25%・
44.7%→about 45%]を反映して再生成、他{len(reuse_verification['matches'])}件の
narration/audit資産はrerun_03からbyte-for-byte再利用[sha256一致確認済み])
と、その音声で実際に読み上げられた全文スクリプトをsegment順に並べた
レビュー用ページです(標準フォーマット、PM-GOVERNANCE-AUDIO-REVIEW-
PLAYER-STANDARD-FORMAT-11準拠、Source列なし)。
「Seek」ボタンをクリックすると、上部の完成episode音声プレイヤーが該当
時刻から再生されます。
</p>
<p class="note">
duration: {duration}s(rerun_03比 {round(duration - 343.044, 3)}s) / peak: {peak}
(rerun_03: 0.75511、原因piece: Full Story Part 1、本タスクでは無変更) /
clipping: {clipping} / headroom safety valve: {'適用' if headroom['applied'] else '不適用'}
(peak_before={headroom['peak_before']}、閾値{headroom['threshold']}未満)。
</p>
<p class="note">
point_one: status={point_one_regen['point_one']['status']}、
asr_verified={point_one_regen['point_one']['asr_verified']}、
audio_classification={point_one_regen['point_one']['audio_classification']}、
repetition_qa flagged={point_one_regen['point_one']['repetition_qa_evidence']['flagged']}
(方式D&prime; best_run={point_one_regen['point_one']['repetition_qa_evidence']['method_d_prime_spectral_short_lag']['best_run_length_seconds']}秒)、
attempt数={len(point_one_regen['point_one']['attempts_log_summary'])}、
sha256={point_one_regen['point_one']['new_sha256']}。<br>
point_two: status={point_one_regen['point_two']['status']}、
asr_verified={point_one_regen['point_two']['asr_verified']}、
audio_classification={point_one_regen['point_two']['audio_classification']}、
repetition_qa flagged={point_one_regen['point_two']['repetition_qa_evidence']['flagged']}
(方式D&prime; best_run={point_one_regen['point_two']['repetition_qa_evidence']['method_d_prime_spectral_short_lag']['best_run_length_seconds']}秒)、
attempt数={len(point_one_regen['point_two']['attempts_log_summary'])}、
sha256={point_one_regen['point_two']['new_sha256']}。
</p>
"""

    html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>OPEN-112-THEME2-B1-NUMERIC-PRECISION-MINIMAL-FIX-RERUN-04</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>OPEN-112-THEME2-B1-NUMERIC-PRECISION-MINIMAL-FIX-RERUN-04(Theme 2 B1 数値決定的置換 + 再Assembly)</h1>
{note}
<audio id="episode_audio" class="main" controls src="{episode_audio_url}"></audio>

<h3>B1 タイムライン・全スクリプト(収録順、rerun_04実測timeline.jsonより)</h3>
{arp.render_timeline_table(row_html_list)}

<p class="note">補足: num_one_charon.wav〜num_five_charon.wav(Key Phrase 1〜5の番号読み上げ、Charon、rerun_03からそのまま継承)は上表には掲載していません(rerun_03player.htmlと同じ扱い)。</p>

<h3>B1 Key Phrase表(rerun_03から無変更、再掲)</h3>
{kp_table_html}

<script>
{arp.SEEK_SCRIPT}
</script>
</body>
</html>
"""

    with open(PLAYER_OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_doc)

    print(f"[build_player] rows={len(row_html_list)} unresolved={unresolved}")
    print(f"[build_player] -> {PLAYER_OUT_PATH}")


if __name__ == "__main__":
    main()
