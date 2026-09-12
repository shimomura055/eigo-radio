# ============================================================
# er011_family_a_trend_synthesis_ai_manufacturing_production_run_01_a2_player.py
# 管理ID: ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01
# ============================================================
# 目的: ER-009で辞書拡張+TTS再開+Assembly完了したA2を、
# er011_family_a_trend_synthesis_ai_manufacturing_production_run_01_
# b1b_player.py(標準フォーマット、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-
# STANDARD-FORMAT-11)を雛形として、同一部品(audio_review_player.py)で
# 出力する。音声参照はGitHub raw絶対URL。読み取り専用(音声・Assembly
# 結果は一切変更しない、mp3変換のみ新規ディレクトリplayer_std/audio_mp3/
# a2/へ書き込む)。commit/pushは本タスクでは行わない(Fable統合時)。
from __future__ import annotations

import html as html_mod
import json
import os

import soundfile as sf

import audio_review_player as arp
import er006_audio_cost_pilot_02_shared_narration as shared_narration

THEME_ID = "family_a_trend_ai_manufacturing_prod_run_01"
OUT_DIR = f"er011_output/{THEME_ID}"
A2_DIR = f"{OUT_DIR}/a2"
PLAYER_STD_DIR = f"{OUT_DIR}/player_std"
MP3_DIR = f"{PLAYER_STD_DIR}/audio_mp3/a2"

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
    out_path = f"{MP3_DIR}/a2_episode.mp3"
    if not os.path.exists(out_path):
        data, sr = sf.read(wav_path)
        sf.write(out_path, data, sr, format="MP3")
    return raw_url(out_path)


def canonical_text_of(seg: dict) -> str:
    # ER-009: canonical_textが無い旧artifactでも表示できるよう、
    # text fieldへのfallbackを引き継ぐ(b1b_player.pyのtopic_intro行と同型)。
    return seg.get("canonical_text") or seg.get("text", "")


def main() -> None:
    os.makedirs(MP3_DIR, exist_ok=True)

    timeline = load_json(f"{A2_DIR}/audit/timeline.json")
    tts = load_json(f"{A2_DIR}/audit/tts_generation_results.json")
    kp_canon = load_json(f"{A2_DIR}/key_phrases/keywords_canonicalized.json")
    assemble_summary = load_json(f"{A2_DIR}/run_summary_assemble.json")
    parts = load_json(f"{A2_DIR}/parts.json")

    seg = tts["segments"]
    kp_items_by_rank = {it["rank"]: it for it in kp_canon["items"]}
    start_by_part = {t["part"]: t["start_seconds"] for t in timeline}

    def seg_audio(name: str) -> str:
        return wav_to_mp3_url(f"{A2_DIR}/narration/{name}.wav")

    rows = []

    def add(part_name: str, label: str, voice: str, script_html: str, audio_urls):
        sec = start_by_part[part_name]
        rows.append(arp.render_timeline_row(
            sec, label, voice, script_html,
            arp.render_single_audio_html(audio_urls) if audio_urls else "—",
            missing=(audio_urls is None)))

    add("Intro", "Intro", "—(SFX)", "音楽ジングル(ナレーションなし、読み上げなし、記事非依存の固定音源)", None)
    add("Welcome", "Welcome", "Charon(固定文言、B1/A2共通Master)",
        shared_narration.FIXED_ENGLISH_TEXTS["welcome"], seg_audio("welcome"))
    add("Topic intro", "Topic intro", "Aoede(英語、A2単一Voice)",
        canonical_text_of(seg["topic_intro"]), seg_audio("topic_intro"))
    add("Japanese title", "Japanese title", "Aoede(日本語、A2単一Voice)",
        canonical_text_of(seg["japanese_title"]), seg_audio("japanese_title"))
    add("Notification 1", "Notification 1", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Preview intro", "Preview intro", "Charon(固定文言、B1/A2共通Master)",
        shared_narration.FIXED_ENGLISH_TEXTS["preview_intro"], seg_audio("preview_intro"))
    add("Point explanation", "Point explanation", "Charon(固定文言、A2専用Master、日本語)",
        shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY["point_explanation"], seg_audio("point_explanation"))
    add("Preview", "Preview", "Aoede(日本語、A2単一Voice)",
        canonical_text_of(seg["preview"]), seg_audio("preview"))
    add("Notification 2", "Notification 2", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Key phrases intro", "Key phrases intro", "Charon(固定文言、B1/A2共通Master)",
        shared_narration.FIXED_ENGLISH_TEXTS["key_phrases_intro"], seg_audio("key_phrases_intro"))

    for rank in range(1, 6):
        item = kp_items_by_rank[rank]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        ja_gloss_tts = item.get("japanese_gloss_tts", ja_gloss)
        gloss_note = "" if ja_gloss_tts == ja_gloss else f"(TTS読み上げ用: {ja_gloss_tts})"
        add(f"Key Phrase {rank}", f"Key Phrase {rank}", "Aoede(英語+日本語、A2単一Voice)",
            f"英語: {used_form}<br>日本語gloss(表示用): {ja_gloss}{gloss_note}",
            [seg_audio(f"kp{rank}_en"), seg_audio(f"meaning_{rank}")])

    add("Notification 3", "Notification 3", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Full story intro", "Full story intro", "Charon(固定文言、B1/A2共通Master)",
        shared_narration.FIXED_ENGLISH_TEXTS["full_story_intro"], seg_audio("full_story_intro"))
    add("Comment 1", "Comment 1", "Aoede(日本語、A2単一Voice)",
        canonical_text_of(seg["comment_1"]), seg_audio("comment_1"))
    add("Full Story Part 1", "Full Story Part 1", "Aoede(英語)",
        canonical_text_of(seg["full_story_part1"]).replace("\n", "<br>"), seg_audio("full_story_part1"))
    add("Comment 2", "Comment 2", "Aoede(日本語、A2単一Voice)",
        canonical_text_of(seg["comment_2"]), seg_audio("comment_2"))
    add("Full Story Part 2", "Full Story Part 2", "Aoede(英語)",
        canonical_text_of(seg["full_story_part2"]).replace("\n", "<br>"), seg_audio("full_story_part2"))
    add("Comment 3", "Comment 3", "Aoede(日本語、A2単一Voice)",
        canonical_text_of(seg["comment_3"]), seg_audio("comment_3"))
    add("Point Notification (Point One cue)", "Point Notification(Point One)", "—(SFX)",
        "効果音(読み上げなし、固定音源)", None)
    add("Point One semantic heading", "Point One heading", "Aoede(英語、わずかに減速)",
        canonical_text_of(seg["point_one_heading"]), seg_audio("point_one_heading"))
    add("Point One", "Point One", "Aoede(英語、わずかに減速)",
        canonical_text_of(seg["point_one"]), seg_audio("point_one"))
    add("Point Notification (Point Two cue)", "Point Notification(Point Two)", "—(SFX)",
        "効果音(読み上げなし、固定音源)", None)
    add("Point Two semantic heading", "Point Two heading", "Aoede(英語、わずかに減速)",
        canonical_text_of(seg["point_two_heading"]), seg_audio("point_two_heading"))
    add("Point Two", "Point Two", "Aoede(英語、わずかに減速)",
        canonical_text_of(seg["point_two"]), seg_audio("point_two"))
    add("Comment 4", "Comment 4", "Aoede(日本語、A2単一Voice)",
        canonical_text_of(seg["comment_4"]), seg_audio("comment_4"))
    add("In One Line", "In One Line", "Aoede(英語、わずかに減速)",
        canonical_text_of(seg["in_one_line"]), seg_audio("in_one_line"))
    add("Outro", "Outro", "—(SFX)",
        "音楽ジングル(ナレーションなし、読み上げなし、固定音源)", None)

    episode_url = episode_mp3_url(assemble_summary["out_path"])

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>FAMILY-A-TREND-SYNTHESIS-AI-MANUFACTURING-PRODUCTION-RUN-01 A2</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>FAMILY-A-TREND-SYNTHESIS-AI-MANUFACTURING-PRODUCTION-RUN-01 — A2 完成episode音声</h1>
<p class="note">
記事: 「{parts.get('title')}」(Trend Synthesis、editorial_mode="trend_synthesis"、
Production Writer正式初回経路[er006_pool_pilot_01_writer.run_writer_for_theme ->
er003_v1_n3_01_articles_generate.run_one_pattern]で新規生成。本文は再生成していない)。
TTS方式: <code>TTS_EXECUTION_MODE=STANDARD</code>(正式リリース前のStandard同期、Batch API不使用)。
duration={assemble_summary['duration_seconds']}s / peak={assemble_summary['peak']} /
clipping={assemble_summary['clipping_detected']}。
Audio Validation Gate: 既定OFF経路(Assembly内蔵)=PASS、opt-in ON経路
(OPEN-129 required_structure)=PASS。
音声はmp3変換のみ(player_std/audio_mp3/a2/配下へ新規変換)。
リンクはGitHub raw絶対URL(push後に有効)。
</p>
<p class="note">
<b>ER-009-JA-READING-DICTIONARY-ACRONYM-EXPANSION-AND-TREND-A2-RESUME-01
(2026-09-12、ユーザー承認)により、日本語Foreign Token Gate(ER-009-JA-FOREIGN-
TOKEN-GATE-01)でHuman Review待ちだった7 segment(japanese_title/preview/
comment_1〜4/Key Phrase 5日本語gloss、いずれも"AI"という単語がGate未登録
だったことが原因)を、辞書へ"AI"を含む15略語を追加登録したうえで再生成し、
本A2を完成させた(詳細はER-009_REPORT.md参照)。Gateロジック自体・retry/
Human Review Lock機構は無変更。</b>
</p>

<audio id="episode_audio" class="main" controls preload="none" src="{episode_url}"></audio>

<h2>A2 タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h2>
{arp.render_timeline_table(rows)}

<h2>A2 記事全文(article.md)</h2>
<pre class="article">{html_mod.escape(open(f"{A2_DIR}/article.md", encoding="utf-8").read())}</pre>

<script>
{arp.SEEK_SCRIPT}
</script>
</body>
</html>
"""

    out_path = f"{PLAYER_STD_DIR}/a2_index.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"標準player出力: {out_path}")
    print(f"GitHub raw URL(push後): {raw_url(out_path)}")


if __name__ == "__main__":
    main()
