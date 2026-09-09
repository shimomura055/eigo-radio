# ============================================================
# er011_family_a_completion_a2_trend_end_to_end_01_a2_continuation_player_01.py
# 管理ID: FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01(継続、A2 level)
# ============================================================
# 目的: A2継続run(er011_family_a_completion_a2_trend_end_to_end_01_run.py
# run_a2_continuation())で完成したA2完成episode音声(rerun_01)を、
# docs/pm/PM_GOVERNANCE.md Gate 7 (a)〜(l)・標準フォーマット(audio_review_
# player.py、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11)に沿った
# 試聴ページとして出力する。読み取り専用(音声・Assembly結果は一切変更しない)。
from __future__ import annotations

import json

import audio_review_player as arp

OUT_DIR = "er011_output/family_a_completion_a2_trend_end_to_end_01/a2/rerun_01"
A2_DIR = f"{OUT_DIR}/a2"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    timeline = load_json(f"{A2_DIR}/audit/timeline.json")
    tts = load_json(f"{A2_DIR}/audit/tts_generation_results.json")
    kp_canon = load_json(f"{A2_DIR}/key_phrases/keywords_canonicalized.json")
    assemble_summary = load_json(f"{A2_DIR}/run_summary_assemble.json")
    parts = load_json(f"{A2_DIR}/parts.json")

    seg = tts["segments"]
    kp = tts["key_phrases"]
    kp_items_by_rank = {it["rank"]: it for it in kp_canon["items"]}

    start_by_part = {t["part"]: t["start_seconds"] for t in timeline}

    def au(path: str) -> str:
        return arp.abs_file_url(path)

    def seg_audio(name: str) -> str:
        return au(f"{A2_DIR}/narration/{name}.wav")

    rows = []

    def add(part_name: str, label: str, voice: str, script_html: str, audio_html):
        sec = start_by_part[part_name]
        rows.append(arp.render_timeline_row(sec, label, voice, script_html,
                                             arp.render_single_audio_html(audio_html) if audio_html else "—",
                                             missing=(audio_html is None)))

    # --- Intro / Notification / Point Notification / Outro: SFX固定音源、読み上げなし ---
    add("Intro", "Intro", "—(SFX)", "音楽ジングル(ナレーションなし、読み上げなし、記事非依存の固定音源)", None)
    add("Welcome", "Welcome", "Charon(固定文言)", "Welcome to English Your Way.", None)
    add("Topic intro", "Topic intro", "Aoede(英語)",
        seg["topic_intro"].get("canonical_text", ""), seg_audio("topic_intro"))
    add("Japanese title", "Japanese title", "Aoede(日本語)",
        "自分のペースで旅行したい若い旅行者たち――でも滞在日数はまだ短いまま"
        "(人手供給・原文タイトルの直訳、FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01継続)",
        seg_audio("japanese_title"))
    add("Notification 1", "Notification 1", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Preview intro", "Preview intro", "Charon(固定文言)", "Here's a quick preview.", None)
    add("Point explanation", "Point explanation", "Charon(固定文言・日本語)", "ポイント解説", None)
    add("Preview", "Preview", "Aoede(日本語)", seg["preview"].get("canonical_text", ""), seg_audio("preview"))
    add("Notification 2", "Notification 2", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Key phrases intro", "Key phrases intro", "Charon(固定文言)", "Here are today's key phrases.", None)

    for rank in range(1, 6):
        item = kp_items_by_rank[rank]
        kpr = kp[str(rank)]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        ja_gloss_tts = item.get("japanese_gloss_tts", ja_gloss)
        gloss_note = "" if ja_gloss_tts == ja_gloss else f"(TTS読み上げ用: {ja_gloss_tts})"
        add(f"Key Phrase {rank}", f"Key Phrase {rank}", "Aoede(英語+日本語)",
            f"英語: {used_form}<br>日本語gloss(表示用): {ja_gloss}{gloss_note}",
            [seg_audio(f"kp{rank}_en"), seg_audio(f"meaning_{rank}")])

    add("Notification 3", "Notification 3", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Full story intro", "Full story intro", "Charon(固定文言)", "Now, the full story.", None)
    add("Comment 1", "Comment 1", "Aoede(日本語)", seg["comment_1"].get("canonical_text", ""), seg_audio("comment_1"))
    add("Full Story Part 1", "Full Story Part 1", "Aoede(英語・A2 6%減速)",
        seg["full_story_part1"].get("canonical_text", "").replace("\n", "<br>"), seg_audio("full_story_part1"))
    add("Comment 2", "Comment 2", "Aoede(日本語)", seg["comment_2"].get("canonical_text", ""), seg_audio("comment_2"))
    add("Full Story Part 2", "Full Story Part 2", "Aoede(英語・A2 6%減速)",
        seg["full_story_part2"].get("canonical_text", "").replace("\n", "<br>"), seg_audio("full_story_part2"))
    add("Comment 3", "Comment 3", "Aoede(日本語)", seg["comment_3"].get("canonical_text", ""), seg_audio("comment_3"))
    add("Point Notification (Point One cue)", "Point Notification(Point One)", "—(SFX)",
        "効果音(読み上げなし、固定音源)", None)
    add("Point One semantic heading", "Point One heading", "Aoede(英語・A2 6%減速)",
        seg["point_one_heading"].get("canonical_text", ""), seg_audio("point_one_heading"))
    add("Point One", "Point One", "Aoede(英語・A2 6%減速)",
        seg["point_one"].get("canonical_text", ""), seg_audio("point_one"))
    add("Point Notification (Point Two cue)", "Point Notification(Point Two)", "—(SFX)",
        "効果音(読み上げなし、固定音源)", None)
    add("Point Two semantic heading", "Point Two heading", "Aoede(英語・A2 6%減速)",
        seg["point_two_heading"].get("canonical_text", ""), seg_audio("point_two_heading"))
    add("Point Two", "Point Two", "Aoede(英語・A2 6%減速)",
        seg["point_two"].get("canonical_text", ""), seg_audio("point_two"))
    add("Comment 4", "Comment 4", "Aoede(日本語)", seg["comment_4"].get("canonical_text", ""), seg_audio("comment_4"))
    add("In One Line", "In One Line", "Aoede(英語・A2 6%減速)",
        seg["in_one_line"].get("canonical_text", ""), seg_audio("in_one_line"))
    add("Outro", "Outro", "—(SFX)", "音楽ジングル(ナレーションなし、読み上げなし、固定音源)", None)

    episode_audio_url = au(assemble_summary["out_path"])

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01 A2継続(rerun_01)</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01(継続) — A2 完成episode音声(rerun_01)</h1>
<p class="note">
記事: 「{parts['title']}」(Trend Synthesis, Wiring後正式経路a2_rerun_02のOK版article.mdをそのまま使用、記事は再生成していない)。
TTS方式: <code>TTS_EXECUTION_MODE=STANDARD</code>(正式リリース前のStandard同期、Batch API不使用)。
日本語タイトルは本継続runで人手供給した直訳(原文タイトルの直訳、新しい主張・数字を追加しない。
既存前例<code>er011_open112_trend_theme2_b_full_audio_trial_13.py</code>/
<code>EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03_REPORT.md</code> B-2と同一規約)。
Level: A2のみ(B1BはKey Phrase 5日本語音声のHuman Review Lock/再生成可否がユーザー判断待ちのため、本ページには含めない)。
duration={assemble_summary['duration_seconds']}s / peak={assemble_summary['peak']} / clipping={assemble_summary['clipping_detected']}。
「Seek」ボタンで上部の完成episode音声player(id=episode_audio)がその開始秒から再生されます。
</p>

<audio id="episode_audio" class="main" controls src="{episode_audio_url}"></audio>

<h2>A2 タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h2>
{arp.render_timeline_table(rows)}

<script>
{arp.SEEK_SCRIPT}
</script>
</body>
</html>
"""

    out_path = f"{OUT_DIR}/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"player.html 出力: {out_path}")
    print(f"file:///{'/'.join(__import__('os').path.abspath(out_path).split(chr(92)))}")


if __name__ == "__main__":
    main()
