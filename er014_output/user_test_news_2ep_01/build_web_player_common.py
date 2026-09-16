# ============================================================
# er014_output/user_test_news_2ep_01/build_web_player_common.py
# 管理ID: USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-02
#
# 目的: Space Weapons/AI Controlの各A2/B1完成episodeについて、
# 既存標準player形式(audio_review_player.py、PM-GOVERNANCE-AUDIO-
# REVIEW-PLAYER-STANDARD-FORMAT-11)を使い、rawcdn.githack等のCDN経由で
# 参照できるplayer.html(相対パス+mp3、local file:// URL不使用)を作る。
# 行解決ロジックは er011_output/household_unified_final_candidate_01/
# build_player.py(A2)・er011_output/open138_household_fact03_b1b_
# minimal_fix_03/build_player_03.py系(B1B)を踏襲(新規ロジック発明では
# ない)。Key Phrase表はユーザー向け画面のため英語+日本語意味のみ
# (TTS用/表示用の区別・voice名・QA結果等の内部情報は出さない、Fable
# 指示に基づく変更点)。mp3変換は既存前例(er012_b_voices_3v_a2_user_
# test_01.py::wav_to_mp3、soundfile使用)と同一方式。
# TTS/ASR/Assemblyは一切呼ばない(既存の完成wav/JSONを読むだけ)。
# ============================================================
from __future__ import annotations

import html
import json
import os

import audio_review_player as arp
import er003_b1_p9a_audio as p9a


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def esc(text) -> str:
    if text is None:
        return ""
    return html.escape(str(text)).replace("\n\n", "<br><br>").replace("\n", "<br>")


def wav_to_mp3(src_wav_path: str, out_path: str) -> None:
    import soundfile as sf
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    data, sr = sf.read(src_wav_path)
    sf.write(out_path, data, sr, format="MP3")


def build_web_delivery(out_dir: str, level_dir: str, narration_dir: str, episode_wav_path: str,
                        segment_names: list) -> dict:
    """out_dir直下にweb/episode.mp3・web/segments/*.mp3を作り、
    web_delivery.jsonを保存する(player.htmlからの相対参照用)。"""
    web_dir = f"{level_dir}/web"
    seg_dir = f"{web_dir}/segments"
    os.makedirs(seg_dir, exist_ok=True)

    episode_mp3 = f"{web_dir}/episode.mp3"
    wav_to_mp3(episode_wav_path, episode_mp3)

    for name in segment_names:
        src = f"{narration_dir}/{name}.wav"
        if os.path.exists(src):
            wav_to_mp3(src, f"{seg_dir}/{name}.mp3")

    mp3_paths = [episode_mp3] + [f"{seg_dir}/{fn}" for fn in os.listdir(seg_dir)]
    manifest, over_50mb = [], []
    for p in mp3_paths:
        size_bytes = os.path.getsize(p)
        rel = os.path.relpath(p, out_dir).replace("\\", "/")
        manifest.append({"path": rel, "size_bytes": size_bytes})
        if size_bytes > 50 * 1024 * 1024:
            over_50mb.append(rel)

    web_delivery = {
        "episode_mp3": os.path.relpath(episode_mp3, out_dir).replace("\\", "/"),
        "mp3_files": manifest, "all_under_50mb": not over_50mb,
    }
    save_path = f"{level_dir}/web_delivery.json"
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(web_delivery, f, ensure_ascii=False, indent=2)
    return web_delivery


def _kp_table_html(kp_items: dict) -> str:
    rows = ['<tr><th>#</th><th>English</th><th>日本語の意味</th></tr>']
    for rank in sorted(kp_items.keys()):
        item = kp_items[rank]
        rows.append(f"<tr><td>{rank}</td><td>{esc(item['used_form'])}</td>"
                    f"<td>{esc(item['japanese_gloss'])}</td></tr>")
    return f'<table class="kp"><thead>{rows[0]}</thead><tbody>{"".join(rows[1:])}</tbody></table>'


# ============================================================
# A2行構築(household build_a2_rows()と同一構造、音声pathのみ相対mp3化)
# ============================================================
def build_a2_rows(level_dir: str, seg_rel_prefix: str):
    narration_dir = f"{level_dir}/narration"
    parts = load_json(f"{level_dir}/parts.json")
    support = load_json(f"{level_dir}/a2_support_texts.json")
    timeline = load_json(f"{level_dir}/audit/timeline.json")
    tts = load_json(f"{level_dir}/audit/tts_generation_results.json")
    kp_canon = load_json(f"{level_dir}/key_phrases/keywords_canonicalized.json")
    seg = tts["segments"]
    kp_items_by_rank = {it["rank"]: it for it in kp_canon["items"]}
    start_by_part = {t["part"]: t["start_seconds"] for t in timeline}

    def seg_url(name: str) -> str:
        return f"{seg_rel_prefix}/{name}.mp3"

    rows = []

    def add(part_name, label, voice, script_html, audio_names):
        sec = start_by_part[part_name]
        audio_html = arp.render_single_audio_html(
            tuple(seg_url(n) for n in audio_names) if len(audio_names) > 1
            else seg_url(audio_names[0])) if audio_names else "—"
        rows.append(arp.render_timeline_row(sec, label, voice, script_html, audio_html, missing=False))

    add("Intro", "Intro", "—(SFX)", "音楽ジングル(読み上げなし、固定音源)", [])
    add("Welcome", "Welcome", "Charon(固定文言)", esc(p9a.PODCAST_NAME_TEXT_V2), [])
    add("Topic intro", "Topic intro", "Aoede(英語)", esc(seg["topic_intro"].get("text")), ["topic_intro"])
    ja_title = seg.get("japanese_title", {}).get("text", "")
    add("Japanese title", "Japanese title", "Aoede(日本語)", esc(ja_title), ["japanese_title"])
    add("Notification 1", "Notification 1", "—(SFX)", "効果音(読み上げなし)", [])
    add("Preview intro", "Preview intro", "Charon(固定文言)", esc(p9a.PREVIEW_INTRO_TEXT), [])
    add("Point explanation", "Point explanation", "Charon(固定文言・日本語)", "ポイント解説", [])
    add("Preview", "Preview", "Aoede(日本語)", esc(support.get("preview")), ["preview"])
    add("Notification 2", "Notification 2", "—(SFX)", "効果音(読み上げなし)", [])
    add("Key phrases intro", "Key phrases intro", "Charon(固定文言)", esc(p9a.KEY_PHRASES_INTRO_TEXT), [])

    for rank in range(1, 6):
        item = kp_items_by_rank[rank]
        add(f"Key Phrase {rank}", f"Key Phrase {rank}", "Aoede(英語+日本語)",
            f"English: {esc(item['used_form'])}<br>日本語: {esc(item['japanese_gloss'])}",
            [f"kp{rank}_en", f"meaning_{rank}"])

    add("Notification 3", "Notification 3", "—(SFX)", "効果音(読み上げなし)", [])
    add("Full story intro", "Full story intro", "Charon(固定文言)", esc(p9a.FULL_STORY_INTRO_TEXT), [])
    add("Comment 1", "Comment 1", "Aoede(日本語)", esc(support.get("comment_1")), ["comment_1"])
    add("Full Story Part 1", "Full Story Part 1", "Aoede(英語・A2 6%減速)",
        esc(seg["full_story_part1"].get("text")), ["full_story_part1"])
    add("Comment 2", "Comment 2", "Aoede(日本語)", esc(support.get("comment_2")), ["comment_2"])
    add("Full Story Part 2", "Full Story Part 2", "Aoede(英語・A2 6%減速)",
        esc(seg["full_story_part2"].get("text")), ["full_story_part2"])
    add("Comment 3", "Comment 3", "Aoede(日本語)", esc(support.get("comment_3")), ["comment_3"])
    add("Point Notification (Point One cue)", "Point Notification(Point One)", "—(SFX)", "効果音", [])
    add("Point One semantic heading", "Point One heading", "Aoede(英語・A2 6%減速)",
        esc(seg["point_one_heading"].get("text")), ["point_one_heading"])
    add("Point One", "Point One", "Aoede(英語・A2 6%減速)", esc(seg["point_one"].get("text")), ["point_one"])
    add("Point Notification (Point Two cue)", "Point Notification(Point Two)", "—(SFX)", "効果音", [])
    add("Point Two semantic heading", "Point Two heading", "Aoede(英語・A2 6%減速)",
        esc(seg["point_two_heading"].get("text")), ["point_two_heading"])
    add("Point Two", "Point Two", "Aoede(英語・A2 6%減速)", esc(seg["point_two"].get("text")), ["point_two"])
    add("Comment 4", "Comment 4", "Aoede(日本語)", esc(support.get("comment_4")), ["comment_4"])
    add("In One Line", "In One Line", "Aoede(英語・A2 6%減速)", esc(seg["in_one_line"].get("text")), ["in_one_line"])
    add("Outro", "Outro", "—(SFX)", "音楽ジングル(読み上げなし)", [])

    kp_table_html = _kp_table_html(kp_items_by_rank)
    return rows, kp_table_html, parts


# ============================================================
# B1B行構築(household build_b1b_rows()と同一構造)
# ============================================================
def build_b1b_rows(level_dir: str, seg_rel_prefix: str):
    parts = load_json(f"{level_dir}/parts.json")
    support = load_json(f"{level_dir}/b1_support_texts.json")
    timeline = load_json(f"{level_dir}/audit/timeline.json")
    kp = load_json(f"{level_dir}/key_phrases/keywords_canonicalized.json")
    kp_items = {item["rank"]: item for item in kp["items"]}

    def seg_url(name: str) -> str:
        return f"{seg_rel_prefix}/{name}.mp3"

    fixed_text = {
        "welcome_charon": p9a.PODCAST_NAME_TEXT_V2,
        "preview_intro_charon": p9a.PREVIEW_INTRO_TEXT,
        "key_phrases_intro_charon": p9a.KEY_PHRASES_INTRO_TEXT,
        "full_story_intro_charon": p9a.FULL_STORY_INTRO_TEXT,
    }
    sfx_labels = {"Intro", "Notification 1", "Notification 2", "Notification 3", "Outro (Charon)", "Outro",
                  "Point Notification (Point One cue)", "Point Notification (Point Two cue)"}

    def resolve_row(label: str):
        if label in sfx_labels:
            return "SFX", "効果音・音楽ジングル(読み上げなし)。", "—"
        if label.startswith("pause_"):
            return None, None, None
        if label == "Welcome (Charon)":
            return "Charon", esc(fixed_text["welcome_charon"]), arp.render_single_audio_html(seg_url("welcome_charon"))
        if label == "Preview intro (Charon)":
            return "Charon", esc(fixed_text["preview_intro_charon"]), arp.render_single_audio_html(seg_url("preview_intro_charon"))
        if label == "Key phrases intro (Charon)":
            return "Charon", esc(fixed_text["key_phrases_intro_charon"]), arp.render_single_audio_html(seg_url("key_phrases_intro_charon"))
        if label == "Full story intro (Charon)":
            return "Charon", esc(fixed_text["full_story_intro_charon"]), arp.render_single_audio_html(seg_url("full_story_intro_charon"))
        if label == "Topic intro (Charon)":
            text = f"Today's topic is {parts['title']}."
            return "Charon", esc(text), arp.render_single_audio_html(seg_url("topic_intro"))
        if label == "Preview (Charon)":
            return "Charon", esc(support.get("preview")), arp.render_single_audio_html(seg_url("preview"))
        comment_map = {"Comment 1 (Charon)": 1, "Comment 2 (Charon)": 2,
                       "Comment 3 (Charon, Bridge)": 3, "Comment 4 (Charon)": 4}
        if label in comment_map:
            i = comment_map[label]
            return "Charon", esc(support.get(f"comment_{i}")), arp.render_single_audio_html(seg_url(f"comment_{i}"))
        if label.startswith("Key Phrase "):
            rank = int(label.split(" ")[-1])
            item = kp_items.get(rank)
            if item is None:
                return "Aoede/Charon", "未取得", "—"
            text = f"English: {esc(item['used_form'])}<br>日本語: {esc(item['japanese_gloss'])}"
            audio_html = arp.render_single_audio_html((seg_url(f"kp{rank}_en"), seg_url(f"kp{rank}_ja_charon")))
            return "Aoede(EN)/Charon(JA)", text, audio_html
        if label == "Full Story Part 1 (Aoede)":
            return "Aoede", esc(parts.get("part1")), arp.render_single_audio_html(seg_url("full_story_part1"))
        if label == "Full Story Part 2 (Aoede)":
            return "Aoede", esc(parts.get("part2")), arp.render_single_audio_html(seg_url("full_story_part2"))
        if label == "Point One semantic heading (Aoede)":
            return "Aoede", esc(parts.get("point_one_heading")), arp.render_single_audio_html(seg_url("point_one_heading"))
        if label == "Point One (Aoede)":
            return "Aoede", esc(parts.get("point_one_body")), arp.render_single_audio_html(seg_url("point_one"))
        if label == "Point Two semantic heading (Aoede)":
            return "Aoede", esc(parts.get("point_two_heading")), arp.render_single_audio_html(seg_url("point_two_heading"))
        if label == "Point Two (Aoede)":
            return "Aoede", esc(parts.get("point_two_body")), arp.render_single_audio_html(seg_url("point_two"))
        if label == "In One Line (Aoede)":
            return "Aoede", esc(parts.get("in_one_line")), arp.render_single_audio_html(seg_url("in_one_line"))
        return "未取得", "未取得", "—"

    rows = []
    for entry in timeline:
        voice, script_html, audio_html = resolve_row(entry["part"])
        if voice is None:
            continue
        rows.append(arp.render_timeline_row(entry["start_seconds"], entry["part"], voice, script_html, audio_html,
                                             missing=False))

    kp_table_html = _kp_table_html(kp_items)
    return rows, kp_table_html, parts


def render_player_page(title: str, note_html: str, episode_audio_url: str, duration_seconds, peak, clipping,
                        timeline_rows: list, kp_table_html: str, out_path: str) -> str:
    timeline_table = arp.render_timeline_table(timeline_rows)
    html_out = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{esc(title)}</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
<script>
{arp.SEEK_SCRIPT}
</script>
</head><body>
<h1>{esc(title)}</h1>
<p class="note">{note_html} duration={duration_seconds}s peak={peak} clipping={clipping}</p>

<h2>Episode audio</h2>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_audio_url}"></audio>

<h2>タイムライン・全スクリプト</h2>
{timeline_table}

<h2>Key Phrases</h2>
{kp_table_html}

</body></html>
"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    return out_path
