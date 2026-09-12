# ============================================================
# er011_family_a_trend_synthesis_ai_manufacturing_production_run_01_b1b_player.py
# 管理ID: FAMILY-A-TREND-SYNTHESIS-AI-MANUFACTURING-PRODUCTION-RUN-01
# ============================================================
# 目的: 完成したB1B(Assembly PASS・Audio Validation Gate opt-in ON PASS)を、
# docs/pm/PM_GOVERNANCE.md Gate 7 (a)〜(l)・標準フォーマット
# (audio_review_player.py、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-
# FORMAT-11)に沿った標準player(音声参照はGitHub raw絶対URL、
# er011_towels_trial11_std_player_01.pyと同一部品)として出力する。
# 読み取り専用(音声・Assembly結果は一切変更しない、mp3変換のみ新規
# ディレクトリplayer_std/へ書き込む)。commit/pushは本タスクでは行わない
# (Fable統合時)。A2は日本語Foreign Token Gate(ER-009)によりHuman Review
# 待ちで未完成のため、本player生成対象はB1Bのみ。
from __future__ import annotations

import html as html_mod
import json
import os

import soundfile as sf

import audio_review_player as arp
import er006_audio_cost_pilot_02_shared_narration as shared_narration

THEME_ID = "family_a_trend_ai_manufacturing_prod_run_01"
OUT_DIR = f"er011_output/{THEME_ID}"
B1_DIR = f"{OUT_DIR}/b1b"
PLAYER_STD_DIR = f"{OUT_DIR}/player_std"
MP3_DIR = f"{PLAYER_STD_DIR}/audio_mp3/b1b"

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/shimomura055/eigo-radio/main/"


def raw_url(repo_rel_path: str) -> str:
    return GITHUB_RAW_BASE + repo_rel_path.replace("\\", "/")


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def wav_to_mp3_url(src_wav_path: str) -> str:
    basename = os.path.splitext(os.path.basename(src_wav_path))[0]
    out_path = f"{MP3_DIR}/{basename}.mp3"
    if not os.path.exists(out_path):
        data, sr = sf.read(src_wav_path)
        sf.write(out_path, data, sr, format="MP3")
    return raw_url(out_path)


def episode_mp3_url(wav_path: str) -> str:
    out_path = f"{MP3_DIR}/b1b_episode.mp3"
    if not os.path.exists(out_path):
        data, sr = sf.read(wav_path)
        sf.write(out_path, data, sr, format="MP3")
    return raw_url(out_path)


def main() -> None:
    os.makedirs(MP3_DIR, exist_ok=True)

    timeline = load_json(f"{B1_DIR}/audit/timeline.json")
    tts = load_json(f"{B1_DIR}/audit/tts_generation_results.json")
    kp_canon = load_json(f"{B1_DIR}/key_phrases/keywords_canonicalized.json")
    assemble_summary = load_json(f"{B1_DIR}/run_summary_assemble.json")
    parts = load_json(f"{B1_DIR}/parts.json")

    seg = tts["segments"]
    kp = tts["key_phrases"]
    kp_items_by_rank = {it["rank"]: it for it in kp_canon["items"]}
    start_by_part = {t["part"]: t["start_seconds"] for t in timeline}

    def seg_audio(name: str) -> str:
        return wav_to_mp3_url(f"{B1_DIR}/narration/{name}.wav")

    rows = []

    def add(part_name: str, label: str, voice: str, script_html: str, audio_urls):
        sec = start_by_part[part_name]
        rows.append(arp.render_timeline_row(
            sec, label, voice, script_html,
            arp.render_single_audio_html(audio_urls) if audio_urls else "—",
            missing=(audio_urls is None)))

    add("Intro", "Intro", "—(SFX)", "音楽ジングル(ナレーションなし、読み上げなし、記事非依存の固定音源)", None)
    add("Welcome (Charon)", "Welcome (Charon)", "Charon(固定文言)",
        shared_narration.FIXED_ENGLISH_TEXTS["welcome"], seg_audio("welcome_charon"))
    add("Topic intro (Charon)", "Topic intro (Charon)", "Charon(英語)",
        seg["topic_intro"].get("canonical_text") or seg["topic_intro"].get("text", ""),
        seg_audio("topic_intro"))
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
        add(f"Key Phrase {rank}", f"Key Phrase {rank}", "Aoede(英語)/Charon(日本語)",
            f"英語: {used_form}<br>日本語gloss(表示用): {ja_gloss}{gloss_note}",
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
        "音楽ジングル(ナレーションなし、読み上げなし、固定音源)", None)

    episode_url = episode_mp3_url(assemble_summary["out_path"])

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>FAMILY-A-TREND-SYNTHESIS-AI-MANUFACTURING-PRODUCTION-RUN-01 B1B</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>FAMILY-A-TREND-SYNTHESIS-AI-MANUFACTURING-PRODUCTION-RUN-01 — B1B 完成episode音声</h1>
<p class="note">
記事: 「{parts.get('title')}」(Trend Synthesis、editorial_mode="trend_synthesis"、
Production Writer正式初回経路[er006_pool_pilot_01_writer.run_writer_for_theme ->
er003_v1_n3_01_articles_generate.run_one_pattern]で新規生成)。
TTS方式: <code>TTS_EXECUTION_MODE=STANDARD</code>(正式リリース前のStandard同期、Batch API不使用)。
duration={assemble_summary['duration_seconds']}s / peak={assemble_summary['peak']} /
clipping={assemble_summary['clipping_detected']}。
Audio Validation Gate: 既定OFF経路(Assembly内蔵)=PASS、opt-in ON経路
(OPEN-129 required_structure)=PASS(audio_run_summary.jsonに記録)。
Fact Checker verdict=REVIEW_REQUIRED(non-blocking advisory、blockingではない)、
Ledger Deviation overall_status=LEDGER_COMPLIANT(MINOR 1件のみ、MAJOR無し)。
音声はmp3変換のみ(TTS再生成ではない、player_std/audio_mp3/b1b/配下へ新規変換)。
リンクはGitHub raw絶対URL(push後に有効。本player生成時点では未pushのため
Fable統合時のcommit/push後に開けるようになる)。
</p>
<p class="note">
<b>A2は日本語Foreign Token Gate(ER-009-JA-FOREIGN-TOKEN-GATE-01)によりHuman
Review待ちで未完成のため、本playerはB1Bのみを対象とする(詳細はREPORT参照)。</b>
</p>

<audio id="episode_audio" class="main" controls preload="none" src="{episode_url}"></audio>

<h2>B1B タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h2>
{arp.render_timeline_table(rows)}

<h2>B1B 記事全文(article.md)</h2>
<pre class="article">{html_mod.escape(open(f"{B1_DIR}/article.md", encoding="utf-8").read())}</pre>

<script>
{arp.SEEK_SCRIPT}
</script>
</body>
</html>
"""

    out_path = f"{PLAYER_STD_DIR}/index.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"標準player出力: {out_path}")
    print(f"GitHub raw URL(push後): {raw_url(out_path)}")


if __name__ == "__main__":
    main()
