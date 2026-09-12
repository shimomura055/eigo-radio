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
# A2: TTS segment `full_story_part1`は当初、既存Human Review Lock機構により
# 3回連続NG→STOPPED(cool-down 20分観測の4回目も無人でNG)となっていたが、
# OPEN-121対称正規化のProduction配線(2026-09-12、ハイフン境界+数詞0-999
# 拡張)適用後の遡及再判定で"24-hour day"の誤flagが解消され、Human Review
# Lockが既存機構どおりRESOLVED(採用: standard attempt1)へ遷移、A2必須6%
# slowdown post-process適用・post-slowdown ASR再検証PASSまで完了した
# (PM-CLOSEOUT-CONSOLIDATION-95/96)。これによりA2もAssembly(Gate OFF/
# opt-in ON両方)PASSとなり、B1Bと同じ完成episode audio付きセクションを
# 生成する。
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
        elif level == "a2":
            run.build_a2_rows()
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


def render_a2_rows_with_raw_urls() -> tuple:
    """A2タイムラインの行生成は、既存のローカルreview player生成関数
    `run.build_a2_rows()`(Intro/Welcome/Notification/固定文言Charon台詞・
    Point explanation・実際のtimeline.json start_secondsによるSeekボタンを
    全て含む、B1Bと同じ完全な行データを返す既存関数)をそのまま再利用する。
    新しいSeekロジック・新しい行定義は作らず、`run.au`(file://絶対パス
    解決)だけをGitHub raw mp3 URL解決に差し替える(B1Bと同一パターン)。
    """
    url_map = build_wav_to_mp3_url_map("a2")
    original_au = run.au

    def au_to_raw_mp3(path: str) -> str:
        if path not in url_map:
            raise KeyError(f"未変換のnarration wavパス: {path}")
        return url_map[path]

    run.au = au_to_raw_mp3
    try:
        result = run.build_a2_rows()
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
# A2(完成、Assembly PASS。PM-CLOSEOUT-CONSOLIDATION-96でfull_story_part1
# のHuman Review Lock RESOLVED+A2必須6% slowdown post-process適用完了)
#
# 2026-09-12是正(PM-CLOSEOUT-CONSOLIDATION-97-ARTICLE-CLOSE-REQUIRES-
# USER-LISTENING-AND-STANDARD-PLAYER-AUDIT): 旧実装はA2完成前(Human
# Review待ちでSTOPPED)時点のまま「個別再生のみ(episode未完成)」の
# 固定文字列をSeek列に出し続けており、A2完成後もIntro/Welcome/
# Notification/Preview intro/Point explanation/Key phrases intro/
# Full story intro/Outro等の固定文言行が欠落し、Seekボタンの
# クリック動作用<script>も出力されていなかった(標準player必須要素
# (7)固定文言/(8)順序・start sec・seekが欠落)。既存のローカルreview
# player生成関数`run.build_a2_rows()`(B1Bの`run.build_b1b_rows()`と
# 対になる、`timeline.json`のstart_secondsに基づく完全な行データを
# 返す既存関数、新規ロジックではない)をそのまま再利用し、`run.au`の
# 解決先だけをGitHub raw mp3 URLへ差し替えることで是正する。
# ------------------------------------------------------------


def build_a2_episode_audio_url() -> tuple:
    assemble = run.load_json(f"{OUT_DIR}/a2/audit/assembly_and_gate_summary_audio_01.json")
    wav_path = assemble["out_path"]
    mp3_path = f"{MP3_DIR}/a2_episode.mp3"
    if not os.path.exists(mp3_path):
        t0 = time.time()
        data, sr = sf.read(wav_path)
        sf.write(mp3_path, data, sr, format="MP3")
        print(f"[episode mp3変換] a2: {time.time() - t0:.1f}s")
    return raw_url(mp3_path), assemble


def build_a2_section() -> str:
    a2_dir = f"{OUT_DIR}/a2"
    parts = run.load_json(f"{a2_dir}/parts.json")

    rows, kp_table, _parts, _support = render_a2_rows_with_raw_urls()

    with open(f"{a2_dir}/article.md", encoding="utf-8") as f:
        article_md = f.read()

    episode_url, assemble = build_a2_episode_audio_url()
    audio_id = "episode_audio_a2"
    return f"""
<div data-audio-target="{audio_id}">
<h2>A2 — 「{esc(parts.get('title'))}」(完成、Assembly PASS)</h2>
<p class="note">
duration={assemble['duration_seconds']}s / peak={assemble['peak']} /
clipping={assemble['clipping_detected']}。segment<code>full_story_part1</code>
は当初、既存Human Review Lock機構(TTS Retry Cascade)が記事本文に正当に
2回出現する句"24-hour day"をrepetitionと誤判定(3回連続NG、cool-down
4回目も無人でNG)しHUMAN_REVIEW_REQUIREDへ遷移していたが、OPEN-121対称
正規化のProduction配線(2026-09-12、ハイフン境界+数詞0-999拡張)適用後の
遡及再判定で誤flagが解消され、既存機構どおりRESOLVED(採用: standard
attempt1)へ遷移した。その後A2必須6% time-stretch post-process
(apply_a2_slowdown_postprocess、既存Production関数・無変更)を適用し、
内蔵Primary ASR再検証PASS(NORMALIZED_MATCH)、post-slowdown音声への
OPEN-121対称正規化repetition_qa再判定もflagged=falseを確認済み。Gate
OFF/opt-in ON経路とも PASS。
</p>
<audio id="{audio_id}" class="main" controls preload="none" src="{episode_url}"></audio>
<h3>A2 タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h3>
{arp.render_timeline_table(rows)}
<h3>A2 Key Phrase表</h3>
{kp_table}
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
ユーザー試聴待ちです。A2/B1Bともに完成(Assembly PASS、下記参照)。</b>
</p>
"""
    a2_section = build_a2_section()
    b1b_section = build_b1b_section()
    # 2026-09-12是正(PM-CLOSEOUT-CONSOLIDATION-97): 標準arp.SEEK_SCRIPTは
    # 単一id="episode_audio"を前提とするが、本ページはA2/B1Bの2つの完成
    # episode音声を1ページに並置するため、Seek対象の解決を各セクションの
    # data-audio-target属性でscopeする(既存ローカルreview player生成
    # `run.player_stage()`のscoped_seek_scriptと同一パターン、新規ロジック
    # ではない)。旧実装は本<script>自体が欠落しており、B1Bのseekボタンも
    # クリック無反応だった。
    scoped_seek_script = """
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-audio-target]").forEach(function (container) {
    var audioId = container.getAttribute("data-audio-target");
    container.querySelectorAll("button.seek").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var a = document.getElementById(audioId);
        if (!a) return;
        a.currentTime = parseFloat(btn.getAttribute("data-sec"));
        a.play();
      });
    });
  });
});
""".strip("\n")
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
<script>
{scoped_seek_script}
</script>
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
