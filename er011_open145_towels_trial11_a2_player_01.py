# ============================================================
# er011_open145_towels_trial11_a2_player_01.py
# OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01
# ============================================================
# タスク項目5: comment_2/meaning_4のresync後にstage_assemble_a2相当
# (Audio Validation Gate込み)を実行しPASSしたA2完成episode音声の試聴
# ページを、既存標準フォーマット(audio_review_player.py、PM-GOVERNANCE-
# AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11、Source列なし)で出力する。
# 読み取り専用(音声・Assembly結果は一切変更しない)。B1B側には一切
# 触れない(別タスクが処理中のため、A2のみの単一track player)。
#
# 構成はer011_family_a_completion_a2_trend_end_to_end_01_a2_continuation_
# player_01.py(既存前例、A2単独player)と同じパターンを踏襲する。
from __future__ import annotations

import json

import audio_review_player as arp

THEME_ID = "discovery_generalization_towels_trial_11"
OUT_DIR = f"er011_output/{THEME_ID}"
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

    add("Intro", "Intro", "—(SFX)", "音楽ジングル(ナレーションなし、読み上げなし、記事非依存の固定音源)", None)
    add("Welcome", "Welcome", "Charon(固定文言)", "Welcome to English Your Way.", None)
    add("Topic intro", "Topic intro", "Aoede(英語)",
        seg["topic_intro"].get("canonical_text", ""), seg_audio("topic_intro"))
    add("Japanese title", "Japanese title", "Aoede(日本語)",
        "洗濯したのに、なぜタオルは臭うことがあるのか(JAPANESE_TITLES辞書への人手供給、"
        "原文タイトルの直訳、新しい主張・数字は追加していない、OPEN-137既知gapの継続)",
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
        note4 = ""
        if rank == 4:
            note4 = ("<br><i>(OPEN-145: japanese_meaningはtts_generation_results.json側の記録"
                     "同期漏れ[pre-existing sync gap、review_lock_state.jsonでは既にRESOLVED/OK]を"
                     "本タスクで是正。音声そのもの・TTS/ASR判定は無変更)</i>")
        add(f"Key Phrase {rank}", f"Key Phrase {rank}", "Aoede(英語+日本語)",
            f"英語: {used_form}<br>日本語gloss(表示用): {ja_gloss}{gloss_note}{note4}",
            [seg_audio(f"kp{rank}_en"), seg_audio(f"meaning_{rank}")])

    add("Notification 3", "Notification 3", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
    add("Full story intro", "Full story intro", "Charon(固定文言)", "Now, the full story.", None)
    add("Comment 1", "Comment 1", "Aoede(日本語)", seg["comment_1"].get("canonical_text", ""), seg_audio("comment_1"))
    add("Full Story Part 1", "Full Story Part 1", "Aoede(英語・A2 6%減速)",
        seg["full_story_part1"].get("canonical_text", "").replace("\n", "<br>"), seg_audio("full_story_part1"))
    add("Comment 2", "Comment 2", "Aoede(日本語)",
        seg["comment_2"].get("canonical_text", "") +
        "<br><i>(OPEN-145: 既存採用済み音声を配線後のProduction Validatorでoffline再判定しPASS"
        f"[{seg['comment_2'].get('audio_classification')}]、既存採用規則によりこの音声をそのまま採用。"
        "TTS再生成・新規ASR呼び出しなし)</i>",
        seg_audio("comment_2"))
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
<title>OPEN-145 タオルTrial-11 A2 完成episode(comment_2/meaning_4 resync後)</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11 — A2 完成episode音声
(OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01 resync後)</h1>
<p class="note">
記事: 「{parts['title']}」(既存article.md、本タスクでは変更していない)。
comment_2はHuman Review Lock(HUMAN_REVIEW_REQUIRED)で止まっていたが、JA ASR表記ゆれ
一般化Variant Layer(Candidate B、形態素解析ベース読みエンジン、fugashi+unidic-lite)を
配線したProduction Validator(er007_ja_asr_validator_01.classify_ja_asr_match)で
既存の6 take(offline、既存ASR書き起こしの再判定のみ、新規ASR/TTS呼び出しなし)を再判定した
結果、既に採用済みの音声がPHONETIC_MATCHでPASSしたためそのまま採用した(TTS再生成なし)。
meaning_4(Key Phrase 4 japanese_meaning)は別件のpre-existing記録同期漏れ(review_lock_state.jsonでは
既にRESOLVED/OKだったが、tts_generation_results.json側が未同期だった)を同時に是正した
(音声そのもの・TTS/ASR判定は無変更)。Level: A2のみ(B1BはSSOT記載どおり別タスクが処理中の
ため本ページには含めない)。
duration={assemble_summary['duration_seconds']}s / peak={assemble_summary['peak']} /
clipping={assemble_summary['clipping_detected']}。
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

    out_path = f"{A2_DIR}/assembled/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"player.html 出力: {out_path}")
    import os
    print(f"file:///{'/'.join(os.path.abspath(out_path).split(chr(92)))}")


if __name__ == "__main__":
    main()
