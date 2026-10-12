# PLAY_EVIDENCE_V4_01(委任_01A、公開GitHub Pages上のPlaywright実再生、有料API 0)
公開URL: https://shimomura055.github.io/eigo-radio/user_test/coffee_final_v4/ (index.html / standard/index.html / advanced/index.html)。commit 776c6b92(main push、Pages 200確認)。Chromium headless、`er057_coffee_final_v4_play_verify_01.py`、生データ `pages_play_evidence_v4_01.json`。
| ページ | HTTP | audio再生OK | seek OK | 行数 | KP 2列table | console error | HTTP>=400 |
|---|---|---|---|---|---|---|---|
| index.html(両Level) | 200 | 51/51 | 全件 | 49 | 10 | 0 | 0 |
| standard/index.html | 200 | 26/26 | 全件 | 25 | 5 | 0 | 0 |
| advanced/index.html | 200 | 25/25 | 全件 | 24 | 5 | 0 | 0 |
通し全編mp3の長さ(実測): Standard 317.68秒 / Advanced 317.07秒(manifestの317.683/317.07と一致)。
Gate 7確認(v3と同構成): (a)完成episode構造 (b)Preview (c)Comment全件 (d)本文Part1〜3+In One Line (e)KP英語+日本語(Std)/英語解説(Adv)、2列table・ラベル文字列なし(n) (f)Intro/Outro/通知音は読み上げなしと明記 (g)行ごと開始秒+「全編の位置へ」ボタン(49/25/24)とclick-seek (h)各行Voice明記 (i)Std/Adv別ページ+一覧、(A2)/(B1)表示なし (j)テキスト無しsegmentは固定音源と明記 (k)TTS方式(DEV Trial)を冒頭に記載 (l)各行に音声とscript同一行 (m)file:///・C:\なし(Pages URL)。
注: 自動再生・seek成立の確認であり、音声品質の合否ではない(ユーザー試聴待ち)。
