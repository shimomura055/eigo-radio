# ============================================================
# er011_wake_before_alarm_trial12_std_player_01.py
# 管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12
#         -STANDARD-PLAYER-01
# ============================================================
# 目的: Trial-11の標準player生成部品(er011_towels_trial11_std_player_01.py
# と同一ロジック)を再利用し、GitHub raw URLで配布できる標準player
# (player_std/index.html)を作る。
#
# B1B: 記事生成→Support/KP→TTS(全segment検証PASS)→Assembly(Gate OFF/ON
# 両方PASS)まで完了しているため、Trial-11と同一の完成episode audio付き
# セクションを生成する。
#
# A2: TTS segment `full_story_part1`が既存Human Review Lock機構により
# 3回連続NG→STOPPED(cool-down 20分観測の4回目も無人でNG、review_lock_
# state.json参照)となり、Assembly(Gate OFF経路)がBLOCKEDのまま。本Trial
# harnessは自動retry・Production側承認代行を行わない(委任文の制約どおり)
# ため、A2は「未承認テイクを一切公開しない」部分player(完成episode audio
# なし、full_story_part1のみ音声リンク省略・PENDING HUMAN REVIEWと明記、
# 他の検証PASS済みsegmentの個別音声は参照可能)として出力する。
#
# 制約: 音声再生成なし。TTS/ASR/API呼び出し一切なし(¥0)。既存
# `{a2,b1b}/narration/`・`review_lock_state.json`等は読み取りのみ。
# 書き込みは新規ディレクトリ`player_std/`配下のみ。個別segment音声は
# wav→mp3変換(単純soundfile変換、TTS再生成ではない)。音声参照URLは
# GitHub raw絶対URL(pushは別タスク)。
from __future__ import annotations

import json
import os
import time

import soundfile as sf

import audio_review_player as arp
import er011_discovery_generalization_wake_before_alarm_trial_12_audio_run as run

THEME_ID = "discovery_generalization_wake_before_alarm_trial_12"
OUT_DIR = f"er011_output/{THEME_ID}"
PLAYER_STD_DIR = f"{OUT_DIR}/player_std"
MP3_DIR = f"{PLAYER_STD_DIR}/audio_mp3"

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/shimomura055/eigo-radio/main/"
RAW_HACK_BASE = "https://raw.githack.com/shimomura055/eigo-radio/main/"


def raw_url(repo_rel_path: str) -> str:
    return GITHUB_RAW_BASE + repo_rel_path.replace("\\", "/")


def esc(text) -> str:
    return run.esc(text)


# ------------------------------------------------------------
# B1B(完全PASS、Trial-11と同一手順)
# ------------------------------------------------------------
def collect_source_wav_paths(level: str) -> set:
    collected = set()
    original_au = run.au

    def recorder(path: str) -> str:
        collected.add(path)
        return "PLACEHOLDER"

    run.au = recorder
    try:
        if level == "b1b":
            run.build_b1b_rows()
        else:
            raise ValueError(level)
    finally:
        run.au = original_au
    return collected


def convert_wav_to_mp3(src_wav_path: str, level: str) -> str:
    basename = os.path.splitext(os.path.basename(src_wav_path))[0]
    out_dir = f"{MP3_DIR}/{level}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/{basename}.mp3"
    if not os.path.exists(out_path):
        data, sr = sf.read(src_wav_path)
        sf.write(out_path, data, sr, format="MP3")
    return out_path


def build_wav_to_mp3_url_map(level: str) -> dict:
    src_paths = collect_source_wav_paths(level)
    mapping = {}
    for src in sorted(src_paths):
        mp3_path = convert_wav_to_mp3(src, level)
        mapping[src] = raw_url(mp3_path)
    return mapping


def render_b1b_rows_with_raw_urls() -> tuple:
    url_map = build_wav_to_mp3_url_map("b1b")
    original_au = run.au

    def au_to_raw_mp3(path: str) -> str:
        if path not in url_map:
            raise KeyError(f"未変換のnarration wavパス: {path}")
        return url_map[path]

    run.au = au_to_raw_mp3
    try:
        result = run.build_b1b_rows()
    finally:
        run.au = original_au
    return result


def build_b1b_episode_audio_url() -> tuple:
    assemble = run.load_json(f"{OUT_DIR}/b1b/run_summary_assemble.json")
    wav_path = assemble["out_path"]
    mp3_path = f"{MP3_DIR}/b1b_episode.mp3"
    if not os.path.exists(mp3_path):
        t0 = time.time()
        data, sr = sf.read(wav_path)
        sf.write(mp3_path, data, sr, format="MP3")
        print(f"[episode mp3変換] b1b: {time.time() - t0:.1f}s")
    return raw_url(mp3_path), assemble


def build_b1b_section() -> str:
    rows, kp_table, parts, support = render_b1b_rows_with_raw_urls()
    episode_url, assemble = build_b1b_episode_audio_url()
    with open(f"{OUT_DIR}/b1b/article.md", encoding="utf-8") as f:
        article_md = f.read()
    audio_id = "episode_audio_b1b"
    return f"""
<div data-audio-target="{audio_id}">
<h2>B1B — 「{esc(parts.get('title'))}」(完成、Assembly PASS)</h2>
<p class="note">
duration={assemble['duration_seconds']}s / peak={assemble['peak']} /
clipping={assemble['clipping_detected']}。TTS_EXECUTION_MODE=STANDARD
(同期呼び出し)。全segment ASR検証PASS、Human Review Lock発火なし
(locked_or_review_required_segments=[])。Gate OFF/opt-in ON経路とも
PASS。
</p>
<audio id="{audio_id}" class="main" controls preload="none" src="{episode_url}"></audio>
<h3>B1B タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h3>
{arp.render_timeline_table(rows)}
<h3>B1B Key Phrase表</h3>
{kp_table}
<h3>B1B 記事全文(article.md)</h3>
<pre class="article">{esc(article_md)}</pre>
</div>
"""


# ------------------------------------------------------------
# A2(部分完成。full_story_part1がHuman Review Lock中のため、Assembly
# BLOCKED。未承認テイクは一切公開しない)
# ------------------------------------------------------------
A2_SEGMENT_ORDER = [
    ("topic_intro", "Topic intro", "Aoede(英語)"),
    ("japanese_title", "Japanese title", "Aoede(日本語、ユーザー提示タイトル)"),
    ("preview", "Preview", "Aoede(日本語)"),
    ("comment_1", "Comment 1", "Aoede(日本語)"),
    ("full_story_part1", "Full Story Part 1", "Aoede(英語・A2 6%減速)"),
    ("comment_2", "Comment 2", "Aoede(日本語)"),
    ("full_story_part2", "Full Story Part 2", "Aoede(英語・A2 6%減速)"),
    ("comment_3", "Comment 3", "Aoede(日本語)"),
    ("point_one_heading", "Point One heading", "Aoede(英語・A2 6%減速)"),
    ("point_one", "Point One", "Aoede(英語・A2 6%減速)"),
    ("point_two_heading", "Point Two heading", "Aoede(英語・A2 6%減速)"),
    ("point_two", "Point Two", "Aoede(英語・A2 6%減速)"),
    ("comment_4", "Comment 4", "Aoede(日本語)"),
    ("in_one_line", "In One Line", "Aoede(英語・A2 6%減速)"),
]

LOCKED_SEGMENT_IDS = {"full_story_part1"}  # review_lock_state.jsonから確認済み(HUMAN_REVIEW_REQUIRED)


def a2_text_for(segment_id: str, parts: dict, support: dict) -> str:
    mapping = {
        "topic_intro": f"Today's topic is {parts.get('title')}.",
        "japanese_title": run.WAKE_JAPANESE_TITLE,
        "preview": support.get("preview"),
        "comment_1": support.get("comment_1"),
        "comment_2": support.get("comment_2"),
        "comment_3": support.get("comment_3"),
        "comment_4": support.get("comment_4"),
        "full_story_part1": parts.get("part1"),
        "full_story_part2": parts.get("part2"),
        "point_one_heading": parts.get("point_one_heading"),
        "point_one": parts.get("point_one_body"),
        "point_two_heading": parts.get("point_two_heading"),
        "point_two": parts.get("point_two_body"),
        "in_one_line": parts.get("in_one_line"),
    }
    return mapping.get(segment_id, "")


def a2_kp_table_html(kp_canon: dict) -> str:
    kp_rows = ["<tr><th>#</th><th>English (used_form)</th><th>表示用 gloss</th></tr>"]
    for item in sorted(kp_canon["items"], key=lambda x: x["rank"]):
        kp_rows.append(f"<tr><td>{item['rank']}</td><td>{esc(item['used_form'])}</td>"
                        f"<td>{esc(item['japanese_gloss'])}</td></tr>")
    return f'<table class="kp"><thead>{kp_rows[0]}</thead><tbody>{"".join(kp_rows[1:])}</tbody></table>'


def build_a2_section() -> str:
    a2_dir = f"{OUT_DIR}/a2"
    narration_dir = f"{a2_dir}/narration"
    parts = run.load_json(f"{a2_dir}/parts.json")
    support = run.load_json(f"{a2_dir}/a2_support_texts.json")
    kp_canon = run.load_json(f"{a2_dir}/key_phrases/keywords_canonicalized.json")
    tts = run.load_json(f"{a2_dir}/audit/tts_generation_results.json")
    seg_status = {sid: (v.get("status") if isinstance(v, dict) else None)
                  for sid, v in tts.get("segments", {}).items()}

    rows_html = []
    for segment_id, label, voice in A2_SEGMENT_ORDER:
        text = esc(a2_text_for(segment_id, parts, support))
        status = seg_status.get(segment_id)
        if segment_id in LOCKED_SEGMENT_IDS or status != "OK":
            audio_html = ("<span class=\"missing\">PENDING HUMAN REVIEW"
                           "(既存Human Review Lock、3回NG+cool-down 4回目もNG。"
                           "未承認テイクにつき音声は非公開。詳細:"
                           " a2/audit/review_lock_state.json / "
                           "a2/audit/tts_cooldown_observation_stage_summary.json)</span>")
            rows_html.append(
                f'<tr class="missing"><td>個別再生のみ(episode未完成)</td>'
                f'<td><b>{label}</b><br><small>voice={voice}</small></td>'
                f'<td class="txt">{text}</td><td>{audio_html}</td></tr>')
            continue
        mp3_path = convert_wav_to_mp3(f"{narration_dir}/{segment_id}.wav", "a2")
        audio_html = arp.render_single_audio_html(raw_url(mp3_path))
        rows_html.append(
            f'<tr><td>個別再生のみ(episode未完成)</td>'
            f'<td><b>{label}</b><br><small>voice={voice}</small></td>'
            f'<td class="txt">{text}</td><td>{audio_html}</td></tr>')

    # Key Phrase(全5件、TTS OK)
    for rank in range(1, 6):
        item = next(it for it in kp_canon["items"] if it["rank"] == rank)
        en_mp3 = convert_wav_to_mp3(f"{narration_dir}/kp{rank}_en.wav", "a2")
        ja_mp3 = convert_wav_to_mp3(f"{narration_dir}/meaning_{rank}.wav", "a2")
        audio_html = arp.render_single_audio_html([raw_url(en_mp3), raw_url(ja_mp3)])
        text = f"英語: {esc(item['used_form'])}<br>日本語gloss: {esc(item['japanese_gloss'])}"
        rows_html.append(
            f'<tr><td>個別再生のみ(episode未完成)</td>'
            f'<td><b>Key Phrase {rank}</b><br><small>voice=Aoede(EN)/Aoede(JA)</small></td>'
            f'<td class="txt">{text}</td><td>{audio_html}</td></tr>')

    with open(f"{a2_dir}/article.md", encoding="utf-8") as f:
        article_md = f.read()

    return f"""
<div>
<h2>A2 — 「{esc(parts.get('title'))}」(部分完成。<span class="missing">完成episode音声なし
・Assembly BLOCKED</span>)</h2>
<p class="note">
既存Human Review Lock機構(TTS Retry Cascade)が、segment
<code>full_story_part1</code>で3回連続NG(Repetition QA: 記事本文に
正当に2回出現する句"24-hour day"をrepetitionと判定、既知の安全側
false-positiveの可能性、Production Repetition QAロジックは本Trialでは
一切変更していない)を検出し、review_lock_state.json上でHUMAN_REVIEW_
REQUIRED(final_status=STOPPED)に遷移した。cool-down 20分観測フック
(TTS-RETRY-COOLDOWN-20MIN-OBSERVATION-TRIAL-01)による無人4回目試行も
NGだった(観測記録のみ、Production側は変更していない・自動採用していない)。
本Trial harnessは自動retry・Human Review承認代行を行わないため、
Assembly(Gate OFF経路)はBLOCKEDのまま。<b>full_story_part1およびepisode
全体の完成音声は本playerに一切含めていない(未承認テイクを公開しない)。</b>
他segment(TTS/ASR検証PASS済み)の個別音声のみ参照可能。
</p>
<table class="timeline"><thead>{arp.TIMELINE_TABLE_HEADER}</thead>
<tbody>{''.join(rows_html)}</tbody></table>
<h3>A2 Key Phrase表</h3>
{a2_kp_table_html(kp_canon)}
<h3>A2 記事全文(article.md)</h3>
<pre class="article">{esc(article_md)}</pre>
</div>
"""


def build_index_html() -> str:
    note = """
<p class="note">
管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12
-STANDARD-PLAYER-01。標準フォーマット(audio_review_player.py、
PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11、Source列なし、
個別音声最低幅360px)準拠。音声再生成なし、既存採用済み(検証PASS)音声の
みをそのまま使用。個別segment音声はmp3変換済み(player_std/audio_mp3/
配下、新規変換・元wav/narrationは無変更)。B1Bの完成episode音声はmp3
(新規変換、TTS再生成ではない)。全リンクはGitHub raw絶対URL
(https://raw.githubusercontent.com/shimomura055/eigo-radio/main/...)。
</p>
<p class="note">
<b>Focus ModuleのProduction採用判断はこのTrialでは行っていません。
ユーザー試聴待ちです。A2はHuman Review Lock中のsegmentがあるため
部分完成(下記参照)。</b>
</p>
"""
    a2_section = build_a2_section()
    b1b_section = build_b1b_section()
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12-STANDARD-PLAYER-01</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12 —
「なぜ目覚ましが鳴る直前に目が覚めることがあるのか?」テーマ 標準player
(A2/B1B、Discovery Focus Module Part A単独)</h1>
{note}
{a2_section}
<hr>
{b1b_section}
</body>
</html>
"""


def main() -> None:
    os.makedirs(f"{MP3_DIR}/a2", exist_ok=True)
    os.makedirs(f"{MP3_DIR}/b1b", exist_ok=True)
    html = build_index_html()
    out_path = f"{PLAYER_STD_DIR}/index.html"
    os.makedirs(PLAYER_STD_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"標準player出力: {out_path}")
    print(f"GitHub raw URL(push後): {raw_url(out_path)}")
    print(f"raw.githack URL(push後): {RAW_HACK_BASE}{out_path.replace(chr(92), '/')}")


if __name__ == "__main__":
    main()
