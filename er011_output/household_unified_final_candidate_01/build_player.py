# ============================================================
# er011_output/household_unified_final_candidate_01/build_player.py
# 管理ID: HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01
# ============================================================
# 完成したA2/B1B完成episode音声(本タスクで実際にAssembly・Gate opt-in ON
# 経路までPASSした音声)向けの試聴ページを、標準フォーマット共通module
# (audio_review_player.py、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-
# FORMAT-11、Source列なし、audio min-width 360px)で生成する。
# 参照テンプレート(読み取りのみ、ロジックを踏襲):
#   - er011_output/open138_household_fact03_b1b_minimal_fix_03/build_player_03.py(B1B行解決ロジック)
#   - er011_family_a_completion_a2_trend_end_to_end_01_a2_continuation_player_01.py(A2行構築ロジック)
# TTS/ASR/Assemblyは一切呼んでいない(既存の音声wav・JSONを読むだけ)。
from __future__ import annotations

import html
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import audio_review_player as arp
import er003_b1_p9a_audio as p9a

OUT_DIR = "er011_output/household_unified_final_candidate_01"
PLAYER_OUT_PATH = f"{OUT_DIR}/player.html"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def esc(text: str) -> str:
    if text is None:
        return ""
    return html.escape(str(text)).replace("\n\n", "<br><br>").replace("\n", "<br>")


def au(path: str) -> str:
    return arp.abs_file_url(path)


# ============================================================
# B1B行構築(build_player_03.pyのresolve_rowロジックを踏襲・簡略化)
# ============================================================
def build_b1b_rows() -> tuple:
    b1_dir = f"{OUT_DIR}/b1b"
    narration_dir = f"{b1_dir}/narration"
    parts = load_json(f"{b1_dir}/parts.json")
    support = load_json(f"{b1_dir}/b1_support_texts.json")
    timeline = load_json(f"{b1_dir}/audit/timeline.json")
    kp = load_json(f"{b1_dir}/key_phrases/keywords_canonicalized.json")
    kp_items = {item["rank"]: item for item in kp["items"]}

    def audio_url(name: str) -> str:
        return au(f"{narration_dir}/{name}.wav")

    fixed_text = {
        "welcome_charon": p9a.PODCAST_NAME_TEXT_V2,
        "preview_intro_charon": p9a.PREVIEW_INTRO_TEXT,
        "key_phrases_intro_charon": p9a.KEY_PHRASES_INTRO_TEXT,
        "full_story_intro_charon": p9a.FULL_STORY_INTRO_TEXT,
    }
    sfx_labels = {"Intro", "Notification 1", "Notification 2", "Notification 3", "Outro (Charon)",
                  "Point Notification (Point One cue)", "Point Notification (Point Two cue)"}

    def resolve_row(label: str):
        if label in sfx_labels:
            return "SFX", "効果音・音楽ジングル(読み上げなし、固定音源)。", "—"
        if label.startswith("pause_"):
            return None, None, None
        if label == "Welcome (Charon)":
            return "Charon", esc(fixed_text["welcome_charon"]), arp.render_single_audio_html(audio_url("welcome_charon"))
        if label == "Preview intro (Charon)":
            return "Charon", esc(fixed_text["preview_intro_charon"]), arp.render_single_audio_html(audio_url("preview_intro_charon"))
        if label == "Key phrases intro (Charon)":
            return "Charon", esc(fixed_text["key_phrases_intro_charon"]), arp.render_single_audio_html(audio_url("key_phrases_intro_charon"))
        if label == "Full story intro (Charon)":
            return "Charon", esc(fixed_text["full_story_intro_charon"]), arp.render_single_audio_html(audio_url("full_story_intro_charon"))
        if label == "Topic intro (Charon)":
            text = f"Today's topic is {parts['title']}."
            return "Charon", esc(text), arp.render_single_audio_html(audio_url("topic_intro"))
        if label == "Preview (Charon)":
            return "Charon", esc(support.get("preview")), arp.render_single_audio_html(audio_url("preview"))
        comment_map = {"Comment 1 (Charon)": 1, "Comment 2 (Charon)": 2,
                       "Comment 3 (Charon, Bridge)": 3, "Comment 4 (Charon)": 4}
        if label in comment_map:
            i = comment_map[label]
            return "Charon", esc(support.get(f"comment_{i}")), arp.render_single_audio_html(audio_url(f"comment_{i}"))
        if label.startswith("Key Phrase "):
            rank = int(label.split(" ")[-1])
            item = kp_items.get(rank)
            if item is None:
                return "Aoede/Charon", "未取得", "—"
            text = f"EN: {esc(item['used_form'])}<br>JA(表示/TTS共通): {esc(item['japanese_gloss'])}"
            audio_html = arp.render_single_audio_html((audio_url(f"kp{rank}_en"), audio_url(f"kp{rank}_ja_charon")))
            return "Aoede(EN)/Charon(JA)", text, audio_html
        if label == "Full Story Part 1 (Aoede)":
            return "Aoede", esc(parts.get("part1")), arp.render_single_audio_html(audio_url("full_story_part1"))
        if label == "Full Story Part 2 (Aoede)":
            return "Aoede", esc(parts.get("part2")), arp.render_single_audio_html(audio_url("full_story_part2"))
        if label == "Point One semantic heading (Aoede)":
            return "Aoede", esc(parts.get("point_one_heading")), arp.render_single_audio_html(audio_url("point_one_heading"))
        if label == "Point One (Aoede)":
            return "Aoede", esc(parts.get("point_one_body")), arp.render_single_audio_html(audio_url("point_one"))
        if label == "Point Two semantic heading (Aoede)":
            return "Aoede", esc(parts.get("point_two_heading")), arp.render_single_audio_html(audio_url("point_two_heading"))
        if label == "Point Two (Aoede)":
            return "Aoede", esc(parts.get("point_two_body")), arp.render_single_audio_html(audio_url("point_two"))
        if label == "In One Line (Aoede)":
            return "Aoede", esc(parts.get("in_one_line")), arp.render_single_audio_html(audio_url("in_one_line"))
        return "未取得", "未取得", "—"

    rows = []
    for entry in timeline:
        voice, script_html, audio_html = resolve_row(entry["part"])
        if voice is None:
            continue
        rows.append(arp.render_timeline_row(entry["start_seconds"], entry["part"], voice, script_html, audio_html,
                                             missing=False))

    kp_rows = ["<tr><th>#</th><th>English (used_form)</th><th>表示用 gloss</th><th>TTS用テキスト</th></tr>"]
    for rank in sorted(kp_items.keys()):
        item = kp_items[rank]
        kp_rows.append(f"<tr><td>{rank}</td><td>{esc(item['used_form'])}</td><td>{esc(item['japanese_gloss'])}</td>"
                        f"<td>{esc(item.get('japanese_gloss_tts') or item['japanese_gloss'])}</td></tr>")
    kp_table_html = f'<table class="kp"><thead>{kp_rows[0]}</thead><tbody>{"".join(kp_rows[1:])}</tbody></table>'

    return rows, kp_table_html, parts, support


# ============================================================
# A2行構築(a2_continuation_player_01.pyのadd()ロジックを踏襲)
# ============================================================
def build_a2_rows() -> tuple:
    a2_dir = f"{OUT_DIR}/a2"
    narration_dir = f"{a2_dir}/narration"
    parts = load_json(f"{a2_dir}/parts.json")
    support = load_json(f"{a2_dir}/a2_support_texts.json")
    timeline = load_json(f"{a2_dir}/audit/timeline.json")
    tts = load_json(f"{a2_dir}/audit/tts_generation_results.json")
    kp_canon = load_json(f"{a2_dir}/key_phrases/keywords_canonicalized.json")
    seg = tts["segments"]
    kp = tts["key_phrases"]
    kp_items_by_rank = {it["rank"]: it for it in kp_canon["items"]}
    start_by_part = {t["part"]: t["start_seconds"] for t in timeline}

    def seg_audio(name: str) -> str:
        return au(f"{narration_dir}/{name}.wav")

    rows = []

    def add(part_name: str, label: str, voice: str, script_html: str, audio_paths):
        sec = start_by_part[part_name]
        audio_html = arp.render_single_audio_html(audio_paths) if audio_paths else "—"
        rows.append(arp.render_timeline_row(sec, label, voice, script_html, audio_html, missing=(audio_paths is None)))

    add("Intro", "Intro", "—(SFX)", "音楽ジングル(ナレーションなし、読み上げなし、固定音源)", None)
    add("Welcome", "Welcome", "Charon(固定文言)", esc(p9a.PODCAST_NAME_TEXT_V2), None)
    add("Topic intro", "Topic intro", "Aoede(英語)", esc(seg["topic_intro"].get("text")), seg_audio("topic_intro"))
    ja_title = seg.get("japanese_title", {}).get("text", "")
    add("Japanese title", "Japanese title", "Aoede(日本語、既存Household完成版タイトルを流用)",
        esc(ja_title), seg_audio("japanese_title"))
    add("Notification 1", "Notification 1", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Preview intro", "Preview intro", "Charon(固定文言)", esc(p9a.PREVIEW_INTRO_TEXT), None)
    add("Point explanation", "Point explanation", "Charon(固定文言・日本語)", "ポイント解説", None)
    add("Preview", "Preview", "Aoede(日本語)", esc(support.get("preview")), seg_audio("preview"))
    add("Notification 2", "Notification 2", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Key phrases intro", "Key phrases intro", "Charon(固定文言)", esc(p9a.KEY_PHRASES_INTRO_TEXT), None)

    for rank in range(1, 6):
        item = kp_items_by_rank[rank]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        ja_gloss_tts = item.get("japanese_gloss_tts", ja_gloss)
        gloss_note = "" if ja_gloss_tts == ja_gloss else f"(TTS読み上げ用: {esc(ja_gloss_tts)})"
        add(f"Key Phrase {rank}", f"Key Phrase {rank}", "Aoede(英語+日本語)",
            f"英語: {esc(used_form)}<br>日本語gloss(表示用): {esc(ja_gloss)}{gloss_note}",
            [seg_audio(f"kp{rank}_en"), seg_audio(f"meaning_{rank}")])

    add("Notification 3", "Notification 3", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Full story intro", "Full story intro", "Charon(固定文言)", esc(p9a.FULL_STORY_INTRO_TEXT), None)
    add("Comment 1", "Comment 1", "Aoede(日本語)", esc(support.get("comment_1")), seg_audio("comment_1"))
    add("Full Story Part 1", "Full Story Part 1", "Aoede(英語・A2 6%減速)",
        esc(seg["full_story_part1"].get("text")), seg_audio("full_story_part1"))
    add("Comment 2", "Comment 2", "Aoede(日本語)", esc(support.get("comment_2")), seg_audio("comment_2"))
    add("Full Story Part 2", "Full Story Part 2", "Aoede(英語・A2 6%減速)",
        esc(seg["full_story_part2"].get("text")), seg_audio("full_story_part2"))
    add("Comment 3", "Comment 3", "Aoede(日本語)", esc(support.get("comment_3")), seg_audio("comment_3"))
    add("Point Notification (Point One cue)", "Point Notification(Point One)", "—(SFX)",
        "効果音(読み上げなし、固定音源)", None)
    add("Point One semantic heading", "Point One heading", "Aoede(英語・A2 6%減速)",
        esc(seg["point_one_heading"].get("text")), seg_audio("point_one_heading"))
    add("Point One", "Point One", "Aoede(英語・A2 6%減速)", esc(seg["point_one"].get("text")), seg_audio("point_one"))
    add("Point Notification (Point Two cue)", "Point Notification(Point Two)", "—(SFX)",
        "効果音(読み上げなし、固定音源)", None)
    add("Point Two semantic heading", "Point Two heading", "Aoede(英語・A2 6%減速)",
        esc(seg["point_two_heading"].get("text")), seg_audio("point_two_heading"))
    add("Point Two", "Point Two", "Aoede(英語・A2 6%減速)", esc(seg["point_two"].get("text")), seg_audio("point_two"))
    add("Comment 4", "Comment 4", "Aoede(日本語)", esc(support.get("comment_4")), seg_audio("comment_4"))
    add("In One Line", "In One Line", "Aoede(英語・A2 6%減速)", esc(seg["in_one_line"].get("text")), seg_audio("in_one_line"))
    add("Outro", "Outro", "—(SFX)", "音楽ジングル(ナレーションなし、読み上げなし、固定音源)", None)

    kp_rows = ["<tr><th>#</th><th>English (used_form)</th><th>表示用 gloss</th><th>TTS用テキスト</th></tr>"]
    for rank in sorted(kp_items_by_rank.keys()):
        item = kp_items_by_rank[rank]
        kp_rows.append(f"<tr><td>{rank}</td><td>{esc(item['used_form'])}</td><td>{esc(item['japanese_gloss'])}</td>"
                        f"<td>{esc(item.get('japanese_gloss_tts') or item['japanese_gloss'])}</td></tr>")
    kp_table_html = f'<table class="kp"><thead>{kp_rows[0]}</thead><tbody>{"".join(kp_rows[1:])}</tbody></table>'

    return rows, kp_table_html, parts, support


def main() -> None:
    a2_rows, a2_kp_table, a2_parts, a2_support = build_a2_rows()
    b1b_rows, b1b_kp_table, b1b_parts, b1b_support = build_b1b_rows()

    a2_assemble = load_json(f"{OUT_DIR}/a2/run_summary_assemble.json")
    b1b_assemble = load_json(f"{OUT_DIR}/b1b/run_summary_assemble.json")
    a2_audio_url = au(a2_assemble["out_path"])
    b1b_audio_url = au(b1b_assemble["out_path"])

    with open(f"{OUT_DIR}/a2/article.md", encoding="utf-8") as f:
        a2_article_md = f.read()
    with open(f"{OUT_DIR}/b1b/article.md", encoding="utf-8") as f:
        b1b_article_md = f.read()

    note = """
<p class="note">
このページはHOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01(Trial扱い、Production配線
なし)の試聴用ページです。A2/B1Bとも、Household Verified Fact Ledger v5
(既存正本、無変更)を用い、現行Discovery Focus Moduleへ最小のWriter表現制約
(FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10の
<code>cautionary_constrained</code>条件、Part B案1、未承認候補)を適用した
条件で、既存Production関数(Writer/Point Role Planning/Point Overlap QA
[Diagnostic Full Retry、Loop Budget 2]/Fact Checker/Ledger Deviation
Checker/Evidence Compression/Key Phrase選定[Redundancy QA込み]/TTS
[ASR検証]/Assembly[SFX込み]/Audio Validation Gate)を無変更で直接呼び、
新規に記事生成からAudio完成まで実行しました。両レベルともGate opt-in
ON経路(OPEN-129)までPASSし、HUMAN_REVIEW_REQUIRED/GATE_BLOCKEDの発動は
ありませんでした(Lock発動なし)。標準フォーマット(audio_review_player.py、
PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11、Source列なし)準拠。
</p>
<p class="note">
A2: duration={a2_dur}s / peak={a2_peak} / clipping={a2_clip}。日本語タイトルは
既存Household完成版のタイトルをそのまま流用(JAPANESE_TITLES辞書に本Trial
theme_id未登録のためのgap fill、新しい主張・数字は追加していない)。<br>
B1B: duration={b1b_dur}s / peak={b1b_peak} / clipping={b1b_clip}。
</p>
""".format(a2_dur=a2_assemble["duration_seconds"], a2_peak=a2_assemble["peak"], a2_clip=a2_assemble["clipping_detected"],
           b1b_dur=b1b_assemble["duration_seconds"], b1b_peak=b1b_assemble["peak"], b1b_clip=b1b_assemble["clipping_detected"])

    # 標準arp.SEEK_SCRIPTは単一id="episode_audio"を前提とする(1ページ1完成
    # episode音声の既存前例のみ)。本ページはA2/B1Bの2つの完成episode音声を
    # 1ページに並置するため、標準CSS/render_timeline_row/render_timeline_table
    # は無変更のまま使い、Seek対象の解決だけをdata-audio-target属性でscopeする
    # 独自スクリプトに置き換える(audio_review_player.py自体は無変更)。
    scoped_seek_script = """
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-audio-target]").forEach(function (container) {
    var audioId = container.getAttribute("data-audio-target");
    container.querySelectorAll("button.seek").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var a = document.getElementById(audioId);
        a.currentTime = parseFloat(btn.getAttribute("data-sec"));
        a.play();
      });
    });
  });
});
""".strip("\n")

    html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01 — Household 最終候補(A2/B1B、Discovery Focus Module cautionary_constrained条件)</h1>
{note}

<div data-audio-target="episode_audio_a2">
<h2>A2 — 「{esc(a2_parts.get('title'))}」</h2>
<audio id="episode_audio_a2" class="main" controls src="{a2_audio_url}"></audio>
<h3>A2 タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h3>
{arp.render_timeline_table(a2_rows)}
<h3>A2 Key Phrase表</h3>
{a2_kp_table}
<h3>A2 記事全文(article.md)</h3>
<pre class="article">{esc(a2_article_md)}</pre>
</div>

<hr>

<div data-audio-target="episode_audio_b1b">
<h2>B1B — 「{esc(b1b_parts.get('title'))}」</h2>
<audio id="episode_audio_b1b" class="main" controls src="{b1b_audio_url}"></audio>
<h3>B1B タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h3>
{arp.render_timeline_table(b1b_rows)}
<h3>B1B Key Phrase表</h3>
{b1b_kp_table}
<h3>B1B 記事全文(article.md)</h3>
<pre class="article">{esc(b1b_article_md)}</pre>
</div>

<script>
{scoped_seek_script}
</script>
</body>
</html>
"""

    with open(PLAYER_OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_doc)
    abs_path = os.path.abspath(PLAYER_OUT_PATH).replace("\\", "/")
    print(f"player.html 出力: {PLAYER_OUT_PATH}")
    print(f"file:///{abs_path}")


if __name__ == "__main__":
    main()
