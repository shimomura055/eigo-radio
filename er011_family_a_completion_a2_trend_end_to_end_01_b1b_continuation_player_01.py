# ============================================================
# er011_family_a_completion_a2_trend_end_to_end_01_b1b_continuation_player_01.py
# 管理ID: FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01(継続、B1B level)
# ============================================================
# 目的: B1B継続run(er011_family_a_completion_a2_trend_end_to_end_01_run.py
# run_b1b_continuation())で完成したB1B完成episode音声を、docs/pm/
# PM_GOVERNANCE.md Gate 7 (a)〜(l)・標準フォーマット(audio_review_player.py、
# PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11)に沿った試聴ページ
# として出力する。読み取り専用(音声・Assembly結果は一切変更しない)。
from __future__ import annotations

import json

import audio_review_player as arp
import er006_audio_cost_pilot_02_shared_narration as shared_narration

OUT_DIR = "er011_output/family_a_completion_a2_trend_end_to_end_01"
B1_DIR = f"{OUT_DIR}/b1b"
CONT_DIR = f"{B1_DIR}/kp5_regen_and_completion_01"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    timeline = load_json(f"{B1_DIR}/audit/timeline.json")
    tts = load_json(f"{B1_DIR}/audit/tts_generation_results.json")
    kp_canon = load_json(f"{B1_DIR}/key_phrases/keywords_canonicalized.json")
    assemble_summary = load_json(f"{B1_DIR}/run_summary_assemble.json")
    parts = load_json(f"{B1_DIR}/parts.json")
    support_texts = load_json(f"{B1_DIR}/b1_support_texts.json")
    kp5_replacement = None
    kp5_regen = None
    try:
        kp5_replacement = load_json(f"{CONT_DIR}/audit/kp5_replacement_result.json")
    except FileNotFoundError:
        pass
    try:
        kp5_regen = load_json(f"{CONT_DIR}/audit/kp5_regen_01_result.json")
    except FileNotFoundError:
        pass

    seg = tts["segments"]
    kp = tts["key_phrases"]
    kp_items_by_rank = {it["rank"]: it for it in kp_canon["items"]}

    start_by_part = {t["part"]: t["start_seconds"] for t in timeline}

    def au(path: str) -> str:
        return arp.abs_file_url(path)

    def seg_audio(name: str) -> str:
        return au(f"{B1_DIR}/narration/{name}.wav")

    rows = []

    def add(part_name: str, label: str, voice: str, script_html: str, audio_html):
        sec = start_by_part[part_name]
        rows.append(arp.render_timeline_row(sec, label, voice, script_html,
                                             arp.render_single_audio_html(audio_html) if audio_html else "—",
                                             missing=(audio_html is None)))

    add("Intro", "Intro", "—(SFX)", "音楽ジングル(ナレーションなし、読み上げなし、記事非依存の固定音源)", None)
    add("Welcome (Charon)", "Welcome (Charon)", "Charon(固定文言)",
        shared_narration.FIXED_ENGLISH_TEXTS["welcome"], seg_audio("welcome_charon"))
    add("Topic intro (Charon)", "Topic intro (Charon)", "Charon(英語)",
        seg["topic_intro"].get("canonical_text", ""), seg_audio("topic_intro"))
    add("Notification 1", "Notification 1", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Preview intro (Charon)", "Preview intro (Charon)", "Charon(固定文言)",
        shared_narration.FIXED_ENGLISH_TEXTS["preview_intro"], seg_audio("preview_intro_charon"))
    add("Preview (Charon)", "Preview (Charon)", "Charon(英語)",
        seg["preview"].get("canonical_text", ""), seg_audio("preview"))
    add("Notification 2", "Notification 2", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Key phrases intro (Charon)", "Key phrases intro (Charon)", "Charon(固定文言)",
        shared_narration.FIXED_ENGLISH_TEXTS["key_phrases_intro"], seg_audio("key_phrases_intro_charon"))

    for rank in range(1, 6):
        item = kp_items_by_rank[rank]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        ja_gloss_tts = item.get("japanese_gloss_tts", ja_gloss)
        gloss_note = "" if ja_gloss_tts == ja_gloss else f"(TTS読み上げ用: {ja_gloss_tts})"
        replaced_note = " ※本継続runでrank5を差し替え(旧候補'take shape'→新候補、下記note参照)" \
            if rank == 5 and kp5_replacement else ""
        add(f"Key Phrase {rank}", f"Key Phrase {rank}", "Aoede(英語)/Charon(日本語)",
            f"英語: {used_form}<br>日本語gloss(表示用): {ja_gloss}{gloss_note}{replaced_note}",
            [seg_audio(f"kp{rank}_en"), seg_audio(f"kp{rank}_ja_charon")])

    add("Notification 3", "Notification 3", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Full story intro (Charon)", "Full story intro (Charon)", "Charon(固定文言)",
        shared_narration.FIXED_ENGLISH_TEXTS["full_story_intro"], seg_audio("full_story_intro_charon"))
    add("Comment 1 (Charon)", "Comment 1 (Charon)", "Charon(英語)",
        seg["comment_1"].get("canonical_text", ""), seg_audio("comment_1"))
    add("Full Story Part 1 (Aoede)", "Full Story Part 1 (Aoede)", "Aoede(英語)",
        seg["full_story_part1"].get("canonical_text", "").replace("\n", "<br>"), seg_audio("full_story_part1"))
    add("Comment 2 (Charon)", "Comment 2 (Charon)", "Charon(英語)",
        seg["comment_2"].get("canonical_text", ""), seg_audio("comment_2"))
    add("Full Story Part 2 (Aoede)", "Full Story Part 2 (Aoede)", "Aoede(英語)",
        seg["full_story_part2"].get("canonical_text", "").replace("\n", "<br>"), seg_audio("full_story_part2"))
    add("Comment 3 (Charon, Bridge)", "Comment 3 (Charon, Bridge)", "Charon(英語)",
        seg["comment_3"].get("canonical_text", ""), seg_audio("comment_3"))
    add("Point Notification (Point One cue)", "Point Notification(Point One)", "—(SFX)",
        "効果音(読み上げなし、固定音源)", None)
    add("Point One semantic heading (Aoede)", "Point One heading (Aoede)", "Aoede(英語)",
        seg["point_one_heading"].get("canonical_text", ""), seg_audio("point_one_heading"))
    add("Point One (Aoede)", "Point One (Aoede)", "Aoede(英語)",
        seg["point_one"].get("canonical_text", ""), seg_audio("point_one"))
    add("Point Notification (Point Two cue)", "Point Notification(Point Two)", "—(SFX)",
        "効果音(読み上げなし、固定音源)", None)
    add("Point Two semantic heading (Aoede)", "Point Two heading (Aoede)", "Aoede(英語)",
        seg["point_two_heading"].get("canonical_text", ""), seg_audio("point_two_heading"))
    add("Point Two (Aoede)", "Point Two (Aoede)", "Aoede(英語)",
        seg["point_two"].get("canonical_text", ""), seg_audio("point_two"))
    add("Comment 4 (Charon)", "Comment 4 (Charon)", "Charon(英語)",
        seg["comment_4"].get("canonical_text", ""), seg_audio("comment_4"))
    add("In One Line (Aoede)", "In One Line (Aoede)", "Aoede(英語)",
        seg["in_one_line"].get("canonical_text", ""), seg_audio("in_one_line"))
    add("Outro (Charon)", "Outro (Charon)", "—(SFX)",
        "音楽ジングル(ナレーションなし、読み上げなし、固定音源。ラベルに(Charon)とあるが実際はTTS読み上げではない固定音源ジングル)", None)

    episode_audio_url = au(assemble_summary["out_path"])

    kp5_note = ""
    if kp5_replacement:
        kp5_note = (
            f"<p class='note'>Key Phrase 5差し替え(本継続run): 承認済み再生成(review_lock."
            f"approve_regenerate()、1回限り)が再度NG(status="
            f"{kp5_regen.get('generate_result_status') if kp5_regen else 'N/A'})だったため、"
            "ユーザー決定(2026-09-09、A2-UDR-1(a))に従い同一文言での追加retryはせず、"
            "既存Key Phrase選定経路(Selection→Canonicalization→Redundancy QA)で新候補"
            f"'{kp5_replacement['new_candidate']['used_form']}'へ差し替えた"
            f"(旧候補'{kp5_replacement['old_candidate']['used_form']}'、旧rank1-4との最終"
            f"Redundancy QA={kp5_replacement['final_merged_redundancy_qa_status']})。"
            "詳細: kp5_regen_and_completion_01/audit/kp5_replacement_candidate_and_reason.json。</p>"
        )

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01 B1B継続(kp5_regen_and_completion_01)</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01(継続) — B1B 完成episode音声(kp5_regen_and_completion_01)</h1>
<p class="note">
記事: 「{parts['title']}」(Trend Synthesis、Wiring後正式経路のOK版article.mdをそのまま使用、記事は再生成していない)。
TTS方式: <code>TTS_EXECUTION_MODE=STANDARD</code>(正式リリース前のStandard同期、Batch API不使用)。
duration={assemble_summary['duration_seconds']}s / peak={assemble_summary['peak']} / clipping={assemble_summary['clipping_detected']}。
Audio Validation Gate: 既定OFF経路(Assembly内蔵)=PASS、opt-in ON経路(OPEN-129 required_structure)=PASS(いずれもb1b_continuation_summary.jsonに記録)。
「Seek」ボタンで上部の完成episode音声player(id=episode_audio)がその開始秒から再生されます。
</p>
{kp5_note}

<audio id="episode_audio" class="main" controls src="{episode_audio_url}"></audio>

<h2>B1B タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h2>
{arp.render_timeline_table(rows)}

<script>
{arp.SEEK_SCRIPT}
</script>
</body>
</html>
"""

    out_path = f"{CONT_DIR}/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"player.html 出力: {out_path}")
    print(f"file:///{'/'.join(__import__('os').path.abspath(out_path).split(chr(92)))}")


if __name__ == "__main__":
    main()
