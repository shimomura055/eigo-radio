# ============================================================
# er011_towels_trial11_std_player_01.py
# 管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-STANDARD-PLAYER-01
# ============================================================
# 目的: PM_GOVERNANCE.md Gate 7 補足(音声artifact受入チェックリスト、
# 2節 (a)〜(m))を満たす標準player(audio_review_player.py、
# PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11)を、A2/B1B
# それぞれについてユーザー環境から実際に開けるURL(GitHub raw)で
# 配布できる形で生成する。
#
# 制約(本タスクの委任文どおり):
# - 音声再生成なし。TTS/ASR/API呼び出し一切なし(¥0)。
# - `{a2,b1b}/assembled/`配下は読み取りのみ(並列でCONSOLIDATION-84が
#   Git使用中のため)。書き込みは新規ディレクトリ`player_std/`配下のみ。
# - 既存の標準player生成関数(audio_review_player.py、および
#   er011_discovery_generalization_towels_trial_11_audio_run.py の
#   build_a2_rows()/build_b1b_rows())を再利用する。新フォーマットは作らない。
# - 個別segment音声はwav→mp3変換したものを参照する(委任文の指示どおり)。
#   変換はProduction関数を呼ばない単純なsoundfile読み込み→MP3書き出し
#   (既存前例: er011_discovery_generalization_towels_trial_11_audio_03_
#   b1b_individual_approval_and_assemble_01.py の step6_export_mp3と同じ
#   sf.write(path, data, sr, format="MP3")パターン)。
# - 音声参照URLはGitHub raw絶対URLとする(pushは別タスク[次のconsolidation]
#   が行う。本タスクはURL設計のみ)。
from __future__ import annotations

import os
import time

import soundfile as sf

import audio_review_player as arp
import er011_discovery_generalization_towels_trial_11_audio_run as run

THEME_ID = "discovery_generalization_towels_trial_11"
OUT_DIR = f"er011_output/{THEME_ID}"
PLAYER_STD_DIR = f"{OUT_DIR}/player_std"
MP3_DIR = f"{PLAYER_STD_DIR}/audio_mp3"

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/shimomura055/eigo-radio/main/"
RAW_HACK_BASE = "https://raw.githack.com/shimomura055/eigo-radio/main/"


def raw_url(repo_rel_path: str) -> str:
    return GITHUB_RAW_BASE + repo_rel_path.replace("\\", "/")


def collect_source_wav_paths(level: str) -> set:
    """build_a2_rows()/build_b1b_rows()がau()へ渡す元wavパスを、実際に
    Production関数を呼ばずに収集する(run.auを一時的に記録用へ差し替え)。"""
    collected = set()
    original_au = run.au

    def recorder(path: str) -> str:
        collected.add(path)
        return "PLACEHOLDER"

    run.au = recorder
    try:
        if level == "a2":
            run.build_a2_rows()
        elif level == "b1b":
            run.build_b1b_rows()
        else:
            raise ValueError(level)
    finally:
        run.au = original_au
    return collected


def convert_wav_to_mp3(src_wav_path: str, level: str) -> str:
    """narration wavを1つmp3へ変換し、player_std/audio_mp3/<level>/配下へ
    出力する(新規ディレクトリのみ書き込み、narration/元wavは無変更)。
    戻り値: 変換後mp3の repo相対パス。"""
    basename = os.path.splitext(os.path.basename(src_wav_path))[0]
    out_dir = f"{MP3_DIR}/{level}"
    out_path = f"{out_dir}/{basename}.mp3"
    if not os.path.exists(out_path):
        data, sr = sf.read(src_wav_path)
        sf.write(out_path, data, sr, format="MP3")
    return out_path


def build_wav_to_mp3_url_map(level: str) -> dict:
    """元wavの絶対/相対パス文字列 -> 変換後mp3のGitHub raw URL、のマップを作る。"""
    src_paths = collect_source_wav_paths(level)
    mapping = {}
    for src in sorted(src_paths):
        mp3_path = convert_wav_to_mp3(src, level)
        mapping[src] = raw_url(mp3_path)
    return mapping


def render_rows_with_raw_urls(level: str) -> tuple:
    """build_a2_rows()/build_b1b_rows()を、run.au()の戻り値を
    「変換済みmp3のGitHub raw URL」へ差し替えた状態で実行し、
    (rows, kp_table_html, parts, support)を返す。"""
    url_map = build_wav_to_mp3_url_map(level)
    original_au = run.au

    def au_to_raw_mp3(path: str) -> str:
        if path not in url_map:
            raise KeyError(f"未変換のnarration wavパス: {path}")
        return url_map[path]

    run.au = au_to_raw_mp3
    try:
        if level == "a2":
            result = run.build_a2_rows()
        else:
            result = run.build_b1b_rows()
    finally:
        run.au = original_au
    return result


def build_episode_audio_url(level: str) -> tuple:
    """完成episode音声のGitHub raw URL(既存assembled/配下は読み取りのみ、
    書き込みなし)。B1Bは既存mp3(assembled/内、既に生成済み)をそのまま
    参照する。A2はmp3が未生成のため、player_std/配下へ新規変換する
    (assembled/wav自体は無変更、読み取りのみ)。"""
    assemble = run.load_json(f"{OUT_DIR}/{level}/run_summary_assemble.json")
    wav_path = assemble["out_path"]
    if level == "b1b":
        mp3_path = wav_path.rsplit(".", 1)[0] + ".mp3"
        if not os.path.exists(mp3_path):
            raise FileNotFoundError(
                f"想定していたB1B既存mp3が見つからない(読み取り専用のため生成しない): {mp3_path}"
            )
    else:
        mp3_path = f"{MP3_DIR}/{level}_episode.mp3"
        if not os.path.exists(mp3_path):
            t0 = time.time()
            data, sr = sf.read(wav_path)
            sf.write(mp3_path, data, sr, format="MP3")
            print(f"[episode mp3変換] {level}: {time.time() - t0:.1f}s")
    return raw_url(mp3_path), assemble


def esc(text) -> str:
    return run.esc(text)


SCOPED_SEEK_SCRIPT = """
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


def build_level_section(level: str, section_title: str) -> str:
    rows, kp_table, parts, support = render_rows_with_raw_urls(level)
    episode_url, assemble = build_episode_audio_url(level)
    with open(f"{OUT_DIR}/{level}/article.md", encoding="utf-8") as f:
        article_md = f.read()
    audio_id = f"episode_audio_{level}"
    return f"""
<div data-audio-target="{audio_id}">
<h2>{section_title} — 「{esc(parts.get('title'))}」</h2>
<p class="note">
duration={assemble['duration_seconds']}s / peak={assemble['peak']} /
clipping={assemble['clipping_detected']}。TTS方式: 実行記録(raw_usage_log)
確認の結果、本Trialの音声生成は全segment Batch API(provider=gemini_batch)
で実行されている(Standard同期呼び出しは0件)。レベル: {level.upper()}
(A2/B1B分離、他レベルの音声・スクリプトは含まない)。
</p>
<audio id="{audio_id}" class="main" controls preload="none" src="{episode_url}"></audio>
<h3>{section_title} タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h3>
{arp.render_timeline_table(rows)}
<h3>{section_title} Key Phrase表(英語+日本語gloss)</h3>
{kp_table}
<h3>{section_title} 記事全文(article.md)</h3>
<pre class="article">{esc(article_md)}</pre>
</div>
"""


def build_index_html() -> str:
    note = """
<p class="note">
管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-STANDARD-PLAYER-01。
標準フォーマット(audio_review_player.py、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-
STANDARD-FORMAT-11、Source列なし、個別音声最低幅360px)準拠。Gate 7 (a)〜(m)
(docs/pm/PM_GOVERNANCE.md 2節)必須要素(完成episode音声・Preview・Comment
全件・本文全section・Key Phrase英語+日本語gloss・Intro/Outro/SFX・segment
order・開始秒・click-seek・voice名・A2/B1分離・TTS方式・ユーザー環境から
開けるURL)を満たすことを目的とする。音声再生成なし、既存採用済み音声を
そのまま使用。個別segment音声はmp3変換済み(player_std/audio_mp3/配下、
新規変換・元wav/narrationは無変更)、完成episode音声もmp3(B1Bは既存
assembled/内の既生成mp3をそのまま参照、A2は本タスクで新規変換
[player_std/audio_mp3/a2_episode.mp3]、いずれもwavから単純変換のみで
TTS再生成ではない)。全リンクはGitHub raw絶対URL
(https://raw.githubusercontent.com/shimomura055/eigo-radio/main/...)であり、
配布方法の詳細はplayer_std/DISTRIBUTION.md参照。
</p>
<p class="note">
<b>Focus ModuleのProduction採用判断はこのTrialでは行っていません。
ユーザー試聴待ちです。</b>
</p>
"""
    a2_section = build_level_section("a2", "A2")
    b1b_section = build_level_section("b1b", "B1B")
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-STANDARD-PLAYER-01</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11 — タオル臭テーマ
標準player(A2/B1B、Discovery Focus Module Part A単独)</h1>
{note}
{a2_section}
<hr>
{b1b_section}
<script>
{SCOPED_SEEK_SCRIPT}
</script>
</body>
</html>
"""


def main() -> None:
    os.makedirs(f"{MP3_DIR}/a2", exist_ok=True)
    os.makedirs(f"{MP3_DIR}/b1b", exist_ok=True)
    html = build_index_html()
    out_path = f"{PLAYER_STD_DIR}/index.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"標準player出力: {out_path}")
    print(f"GitHub raw URL(push後): {raw_url(out_path)}")
    print(f"raw.githack URL(push後): {RAW_HACK_BASE}{out_path.replace(chr(92), '/')}")


if __name__ == "__main__":
    main()
