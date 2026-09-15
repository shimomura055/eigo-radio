# -*- coding: utf-8 -*-
"""USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-TREND-NAMING
Trend B1(内部id: b1b)playerの表示文字列のみを「B1-B」→「B1」へ置換する。

対象: er014_output/four_type_observation_01/trend/audio/b1b/player.html
- 音声ファイル・segment構成・パス(`trend/b1b/article.md`等の内部パス表記)は変更しない。
- 表示文字列(<title>/<h1>/<h2>見出し)のみ「B1-B」→「B1」に置換する。
- h1直後に「(internal id: b1b)」という小さい注記を残す(内部compatibility
  identifierであることをユーザー向け画面上にも記録しておく)。
- 冪等: 既に置換済み(「B1-B」が本文中に残っていない)の場合はNo-opで終了する。

このscriptはPlayer生成ロジック本体(run_trend_audio_completion.py の
build_player_and_web_delivery()、Production/Trialコード)を変更しない。
既に生成済みのplayer.htmlに対する表示文字列post-processのみを行う
Trial専用の補助scriptである。
"""
from __future__ import annotations

import re

PLAYER_PATH = "er014_output/four_type_observation_01/trend/audio/b1b/player.html"

# 置換対象は表示文字列4箇所のみ(<title>・<h1>・<h2>x2)。
# 内部パス表記(例: "trend/b1b/article.md")は "B1-B" という文字列を
# 含まないため、単純な文字列置換で誤爆しない。
REPLACEMENTS = [
    (
        "<title>USER-TEST-AUDIO-COMPLETION-01-TREND B1-B</title>",
        "<title>USER-TEST-AUDIO-COMPLETION-01-TREND B1</title>",
    ),
    (
        "<h1>USER-TEST-AUDIO-COMPLETION-01-TREND — Level: B1-B — 完成episode音声</h1>",
        "<h1>USER-TEST-AUDIO-COMPLETION-01-TREND — Level: B1 — 完成episode音声</h1>\n"
        "<p style=\"font-size:0.78em;color:#666;margin:2px 0 0 0;\">(internal id: b1b)</p>",
    ),
    (
        "<h2>B1-B タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h2>",
        "<h2>B1 タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h2>",
    ),
    (
        "<h2>B1-B 記事全文(article.md)</h2>",
        "<h2>B1 記事全文(article.md)</h2>",
    ),
]


def main() -> None:
    text = open(PLAYER_PATH, encoding="utf-8").read()

    if "B1-B" not in text:
        print(f"[SKIP] 既に置換済み(『B1-B』が見つかりません): {PLAYER_PATH}")
        return

    before_b1b_count = len(re.findall(r"B1-B", text))
    applied = 0
    for old, new in REPLACEMENTS:
        if old not in text:
            raise RuntimeError(
                f"想定した表示文字列が見つかりませんでした(player.html構造が変わった可能性): {old!r}"
            )
        if text.count(old) != 1:
            raise RuntimeError(f"置換対象文字列が1箇所ではありません(count={text.count(old)}): {old!r}")
        text = text.replace(old, new, 1)
        applied += 1

    after_b1b_count = len(re.findall(r"B1-B", text))
    internal_note_count = text.count("internal id: b1b")

    # 内部パス表記(trend/b1b/...)は変更していないことを確認するため、
    # 「b1b」自体は残っていてよい(表示用の「B1-B」だけが消えていればよい)。
    if after_b1b_count != 0:
        raise RuntimeError(f"置換後も『B1-B』が残っています(count={after_b1b_count})")

    open(PLAYER_PATH, "w", encoding="utf-8", newline="\n").write(text)

    print(
        f"[OK] {PLAYER_PATH}: 表示文字列『B1-B』{before_b1b_count}箇所→『B1』に置換"
        f"({applied}箇所)、internal id注記{internal_note_count}箇所を追加。"
    )
    print("[OK] 音声ファイル・segment構成・内部パス(trend/b1b/...)は無変更。")


if __name__ == "__main__":
    main()
