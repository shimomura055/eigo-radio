# ============================================================
# audio_review_player.py
# 管理ID: PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11
# ============================================================
# 背景(ユーザー決定 2026-09-08、正式):
# EDITORIAL-B-FAMILY-VOICES-TRIAL-09で作成したplayer形式
# (er012_output/editorial_b_voices_trial_09_audio/player.html、
# Gate 7 (a)〜(l)準拠、各行にSeekボタン+voice名+scriptを同一行配置)を、
# 今後の完成音声/Trial音声レビューの標準フォーマットとして採用する。
# 毎回フォーマットを変えない(docs/pm/PM_GOVERNANCE.md Gate 7 (l)参照)。
#
# 本モジュールは、上記標準フォーマットのHTML生成部分(CSS・タイムライン
# テーブル行・Seek用JavaScript)を1箇所に集約した共通関数群である。
# ユーザー決定に基づき、以下3点をTrial-09時点の形式から修正している:
#   1. Source列を削除する(個別音声の出典・根拠が必要な場合は、呼び出し側が
#      note欄やSegment名内に短く記載する。標準テーブルの列としては持たない)
#   2. その分、Script列の幅を広げる(固定幅の列をSeek/Segment/個別音声の
#      3列だけに絞り、Script列は残り幅を自動的に使う)
#   3. 個別音声<audio controls>要素の幅を広げ、再生ボタンが常時見えるように
#      する(最低幅 AUDIO_MIN_WIDTH_PX、「…」オーバーフローメニュー化や
#      長いスクロールなしで、再生ボタン/Segment・Voice/Script/個別再生が
#      同一行で確認できることを目安とする)
#
# 既存Gate 7 (a)〜(l)(docs/pm/PM_GOVERNANCE.md 2節)の必須要素
# (完成episode player・Seekボタン・Segment名+voice・実際に読み上げられた
# script・個別音声再生)は維持する。新しい項目番号・新しいルールは増やさない
# (既存(l)の実装を1箇所に集約するだけ)。
#
# 呼び出し側(各Trial/Productionのplayer生成スクリプト)は、タイムラインの
# 各行に必要な情報(Segment labelからscript textやaudio pathへの解決ロジック)
# を引き続き自前で持つ(記事・Trialごとに解決ロジックが異なるため。本モジュール
# は「解決済みの行データ」をどう描画するかだけを共通化する)。
from __future__ import annotations

import os

# --- 標準player: 幅の目安(px) -------------------------------------------
# Chrome/Edge系ブラウザの<audio controls>は、幅が概ね260px程度以下になると
# 再生ボタン等が「…」(overflow)メニューに畳み込まれることを確認したため、
# 常時ボタンが見える最低幅として360pxを標準値とする。
AUDIO_MIN_WIDTH_PX = 360
# 個別音声セル(<td>)自体の幅(audio本体+セルpadding分の余白を含む)。
AUDIO_COLUMN_WIDTH_PX = 400
# Seek列・Segment/voice列は固定幅、残り(Script列)を自動的に広げる。
SEEK_COLUMN_WIDTH_PX = 100
SEGMENT_COLUMN_WIDTH_PX = 190

# タイムラインテーブルのヘッダー(Gate 7 (l)必須列のみ。Source列は標準から削除)。
TIMELINE_TABLE_HEADER = (
    "<tr><th>Seek(同一行)</th><th>Segment / voice(同一行)</th>"
    "<th>Script(同一行)</th><th>個別音声</th></tr>"
)

PLAYER_STANDARD_CSS = f"""
body {{ font-family: "Meiryo","Hiragino Kaku Gothic ProN",sans-serif; max-width: 1080px; margin: 2em auto; line-height:1.55; color:#111; }}
h1 {{ font-size: 1.3em; }}
h2 {{ border-bottom: 2px solid #333; padding-bottom:4px; margin-top:1.8em; }}
h3 {{ margin-top:1.6em; border-left:6px solid #888; padding-left:8px; }}
table.timeline {{ border-collapse: collapse; width: 100%; margin: 10px 0 22px 0; font-size: 0.9em; }}
table.timeline th, table.timeline td {{ border: 1px solid #ccc; padding: 6px 8px; vertical-align: top; text-align:left; }}
table.timeline th {{ background:#f0f0f0; }}
table.timeline th:nth-child(1), table.timeline td:nth-child(1) {{ width: {SEEK_COLUMN_WIDTH_PX}px; }}
table.timeline th:nth-child(2), table.timeline td:nth-child(2) {{ width: {SEGMENT_COLUMN_WIDTH_PX}px; }}
table.timeline th:nth-child(4), table.timeline td:nth-child(4) {{ width: {AUDIO_COLUMN_WIDTH_PX}px; }}
table.timeline td.txt {{ white-space: pre-wrap; }}
button.seek {{ cursor:pointer; font-family:monospace; font-size:0.92em; padding:2px 6px; }}
table.timeline audio {{ width: 100%; min-width: {AUDIO_MIN_WIDTH_PX}px; height: 32px; }}
.missing {{ color:#a33; font-style:italic; }}
.note {{ background:#fffbe6; border:1px solid #e0d080; padding:8px 12px; font-size:0.88em; margin:10px 0; }}
audio.main {{ width:100%; max-width:640px; display:block; margin:8px 0; }}
table.kp {{ border-collapse: collapse; width: 100%; margin: 10px 0 22px 0; font-size: 0.9em; }}
table.kp th, table.kp td {{ border: 1px solid #ccc; padding: 6px 8px; vertical-align: top; text-align:left; }}
table.kp th {{ background:#f0f0f0; }}
""".strip("\n")

# Seekボタン(同一行のSeekボタン)クリックで、上部の完成episode音声player
# (id="episode_audio")をその開始秒へ移動して再生する共通JavaScript。
SEEK_SCRIPT = """
function seekMain(sec) {
  var a = document.getElementById('episode_audio');
  a.currentTime = parseFloat(sec);
  a.play();
}
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("button.seek").forEach(function (btn) {
    btn.addEventListener("click", function () { seekMain(btn.getAttribute("data-sec")); });
  });
});
""".strip("\n")


def abs_file_url(path: str) -> str:
    """ローカルファイルパスを file:/// URLへ変換する(絶対パス化)。"""
    return "file:///" + os.path.abspath(path).replace("\\", "/")


def render_single_audio_html(audio_url_or_urls) -> str:
    """個別音声セルのHTML断片を組み立てる。SFX等で音声が無い場合は
    呼び出し側が"—"等を直接渡す想定(本関数はaudio要素の組み立てのみ)。"""
    if isinstance(audio_url_or_urls, (tuple, list)):
        return "".join(
            f'<audio controls preload="none" src="{u}"></audio>' for u in audio_url_or_urls
        )
    return f'<audio controls preload="none" src="{audio_url_or_urls}"></audio>'


def render_timeline_row(seek_sec: float, label: str, voice_disp: str, script_html: str,
                         audio_html: str, missing: bool = False) -> str:
    """Gate 7 (a)〜(l)標準の1行(Source列なし)。
    seek_sec: 完成episode音声内の開始秒(Seekボタンのdata-sec)。
    label: Segment名。voice_disp: voice名("—"/"SFX"等も可)。
    script_html: 実際に読み上げられたscript(SFXは"効果音(読み上げなし)"等)。
    audio_html: render_single_audio_htmlの戻り値、または"—"。
    """
    row_class = ' class="missing"' if missing else ""
    seek_btn = f'<button class="seek" data-sec="{seek_sec}">&#9654; {seek_sec:.2f}s</button>'
    return (
        f'<tr{row_class}><td>{seek_btn}</td>'
        f'<td><b>{label}</b><br><small>voice={voice_disp}</small></td>'
        f'<td class="txt">{script_html}</td>'
        f'<td>{audio_html}</td></tr>'
    )


def render_timeline_table(row_html_list: list[str]) -> str:
    """タイムラインテーブル全体(標準ヘッダー+行)を組み立てる。"""
    return (
        f'<table class="timeline"><thead>{TIMELINE_TABLE_HEADER}</thead>'
        f'<tbody>{"".join(row_html_list)}</tbody></table>'
    )
