# ============================================================
# er011_output/open138_household_fact03_b1b_minimal_fix_03/
#   build_player_03.py
# 管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03(OPEN-138、
# A-FACT03-4=(a))
# ============================================================
# topic_intro HUMAN_APPROVED記録後、stage_assemble_b1()で実際に完成した
# `fact03_fix_02/b1b/assembled/English_Your_Way_B1B_HOUSEHOLD.wav`向けの
# player.htmlを、標準フォーマット共通module(audio_review_player.py、
# PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11)で生成する。
# er011_output/open112_trend_theme2_b_final_audio_rerun_04/
#   build_player_runtime_evidence.pyのSegment解決ロジックをそのまま踏襲
# (既存audit JSON/timeline.json/b1_support_texts.json/parts.json/
# keywords_canonicalized.jsonのみを読み、推測補完はしない)。
# TTS/ASR/Assemblyは一切呼んでいない(既存の音声wav・JSONを読むだけ)。
#
# 実行方法(root直下から):
#   PYTHONPATH=. .venv/Scripts/python.exe \
#     er011_output/open138_household_fact03_b1b_minimal_fix_03/\
#     build_player_03.py
from __future__ import annotations

import html
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import audio_review_player as arp
import er003_b1_p9a_audio as p9a

OUT_ROOT = "er003_output/n3_01/household/fact03_fix_02"
B1_DIR = f"{OUT_ROOT}/b1b"
NARRATION_DIR = f"{B1_DIR}/narration"
ASSEMBLED_PATH = f"{B1_DIR}/assembled/English_Your_Way_B1B_HOUSEHOLD.wav"
PLAYER_OUT_PATH = ("er011_output/open138_household_fact03_b1b_minimal_fix_03/"
                    "player.html")

MISSING = "未取得"

parts = json.load(open(f"{B1_DIR}/parts.json", encoding="utf-8"))
support = json.load(open(f"{B1_DIR}/b1_support_texts.json", encoding="utf-8"))
timeline = json.load(open(f"{B1_DIR}/audit/timeline.json", encoding="utf-8"))
tts_results = json.load(open(f"{B1_DIR}/audit/tts_generation_results.json", encoding="utf-8"))
kp = json.load(open(f"{B1_DIR}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
run_summary_assemble = json.load(open(f"{B1_DIR}/run_summary_assemble.json", encoding="utf-8"))
human_approved = json.load(open(f"{B1_DIR}/audit/human_approved_segments.json", encoding="utf-8"))

segments = tts_results.get("segments", {})
kp_items = {item["rank"]: item for item in kp["items"]}

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


def esc(text: str) -> str:
    return html.escape(text).replace("\n\n", "<br><br>").replace("\n", "<br>")


def audio_url(name_no_ext: str) -> str:
    return arp.abs_file_url(f"{NARRATION_DIR}/{name_no_ext}.wav")


def resolve_row(part_label: str, start_sec: float):
    label = part_label

    if label in SFX_PARTS:
        note, _src = SFX_PARTS[label]
        return "SFX", esc(note), "—", False
    if label in ("Point Notification (Point One cue)", "Point Notification (Point Two cue)"):
        return "SFX", "効果音(読み上げなし)。", "—", False
    if label.startswith("pause_"):
        return None, None, None, None

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
        note = (" <span class=\"missing\">[HUMAN_APPROVED: 2026-08-17当時ASR 6回試行"
                "FAIL(status=STOPPEDのまま不変)、現行ASR cascadeで事後再照合"
                "NORMALIZED_MATCH、2026-09-09ユーザー判断A-FACT03-4(a)で人間承認済み"
                "(音声byte不変、TTS再生成なし)]</span>")
        return "Charon", esc(text) + note, arp.render_single_audio_html(audio_url("topic_intro")), False

    if label == "Preview (Charon)":
        text = support.get("preview")
        return "Charon", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("preview")), text is None

    label_prefixes = {
        1: "Comment 1 (Charon)", 2: "Comment 2 (Charon)",
        3: "Comment 3 (Charon, Bridge)", 4: "Comment 4 (Charon)",
    }
    for i in (1, 2, 3, 4):
        if label == label_prefixes[i]:
            cname = f"comment_{i}"
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
        if rank == 2:
            text += (" <span class=\"missing\">[HUMAN_APPROVED: 英語部分(kp2_english)は"
                      "ASR同音異義('crisper'/'CRISPR')でFAIL、2026-09-09ユーザー試聴承認"
                      "(FIX-02継続3、A-FACT03-2(a))で人間承認済み。日本語部分は元々検証"
                      "PASS]</span>")
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
        note = " <span class=\"missing\">[revision3a、FACT-03修正文。他segmentと異なりnarration wavはoriginalとbyte不一致]</span>"
        return "Aoede", (esc(text) + note) if text else MISSING, arp.render_single_audio_html(audio_url("point_one")), text is None
    if label == "Point Two semantic heading (Aoede)":
        text = parts.get("point_two_heading")
        return "Aoede", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("point_two_heading")), text is None
    if label == "Point Two (Aoede)":
        text = parts.get("point_two_body")
        return "Aoede", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("point_two")), text is None
    if label == "In One Line (Aoede)":
        text = parts.get("in_one_line")
        return "Aoede", esc(text) if text else MISSING, arp.render_single_audio_html(audio_url("in_one_line")), text is None

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
            continue
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

    approval = human_approved.get("topic_intro", {})

    note = f"""
<p class="note">
このページは、HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03(OPEN-138、
A-FACT03-4=(a))で、topic_intro(既存承認済み音声、8月生成時ASR FAIL x6、
現行ASR cascadeによる事後再照合PASS)を既存の人間承認経路
(record_human_approval())でHUMAN_APPROVEDとして記録した上でAssemblyした
完成episode音声(`fact03_fix_02/b1b/assembled/English_Your_Way_B1B_
HOUSEHOLD.wav`)と、その音声で実際に読み上げられた全文スクリプトをsegment順に
並べたレビュー用ページです(標準フォーマット、PM-GOVERNANCE-AUDIO-REVIEW-
PLAYER-STANDARD-FORMAT-11準拠、Source列なし)。narration wav 32件中、
point_one.wav(FIX-02継続1、revision3a)のみoriginal(2026-08-17承認版)と
byte不一致、topic_introを含む他31件はoriginalとbyte完全一致(TTS再生成
なし)です。「Seek」ボタンをクリックすると、上部の完成episode音声プレイヤーが
該当時刻から再生されます。
</p>
<p class="note">
duration: {duration}s / peak: {peak} / clipping: {clipping} / headroom
safety valve: {'適用' if headroom['applied'] else '不適用'}
(peak_before={headroom['peak_before']}、閾値{headroom['threshold']}未満、
cause_piece={headroom['cause_piece']})。
</p>
<p class="note">
topic_intro HUMAN_APPROVED記録: approved_at={approval.get('approved_at')} /
approved_by={approval.get('approved_by')} / note={html.escape(approval.get('note', ''))}
</p>
<p class="note">
レベル: B1(A2は本タスク無変更、既存承認済み`er003_output/n3_01/household/a2/`
を引き続き参照)。TTS方式: 既存Production標準経路(Standard、非Batch、
`generate_news_narration_wide_margin`等の1segmentずつ逐次生成関数、
`TTS_EXECUTION_MODE=STANDARD`)。narration wav 32件は全て2026-08-17
(topic_intro等31件)または本タスク系継続1(point_one、revision3a)時点で
この経路により生成済みで、本タスクでは新規TTS呼び出しを一切行っていない。
</p>
"""

    html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03(topic_intro HUMAN_APPROVED + B1 Assembly)</h1>
{note}
<audio id="episode_audio" class="main" controls src="{episode_audio_url}"></audio>

<h3>B1 タイムライン・全スクリプト(収録順、本タスク実測timeline.jsonより)</h3>
{arp.render_timeline_table(row_html_list)}

<p class="note">補足: num_one_charon.wav〜num_five_charon.wav(Key Phrase 1〜5の番号読み上げ、Charon)は上表には掲載していません(既存標準の扱い)。</p>

<h3>B1 Key Phrase表</h3>
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
