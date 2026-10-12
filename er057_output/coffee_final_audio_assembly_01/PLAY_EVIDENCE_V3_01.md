# PLAY_EVIDENCE_V3_01(委任_02、公開GitHub Pages上のPlaywright実再生、有料API 0)
公開URL: https://shimomura055.github.io/eigo-radio/user_test/coffee_final_v3/ (index.html / standard/index.html / advanced/index.html)。commit 4276f676(mainへpush、Pages 200確認)。Chromium headless(--autoplay-policy=no-user-gesture-required)、`er057_coffee_final_v3_play_verify_01.py`、生データ `pages_play_evidence_v3_01.json`。
| ページ | HTTP | audio再生OK | seek OK | 行数 | KP 2列table | console error | HTTP>=400 |
|---|---|---|---|---|---|---|---|
| index.html(両Level) | 200 | 51/51 | 全件 | 49 | 10 | 0 | 0 |
| standard/index.html | 200 | 26/26 | 全件 | 25 | 5 | 0 | 0 |
| advanced/index.html | 200 | 25/25 | 全件 | 24 | 5 | 0 | 0 |
通し全編mp3の長さ(実測): Standard 314.17秒 / Advanced 314.97秒(manifestの314.172/314.97と一致)。
Gate 7確認: (a)完成episode構造 (b)Preview (c)Comment全件 (d)本文Part1〜3+新In One Line (e)KP英語+日本語(Std)/英語解説(Adv)、2列table・ラベル文字列なし(n) (f)Intro/Outro/通知音は「読み上げなし」と明記 (g)行ごとに開始秒+「全編の位置へ」ボタン(49/24/25個)とclick-seek (h)各行Voice明記 (i)Standard/Advancedを別ページ+一覧、A2/B1表示なし (j)テキスト無しsegmentは固定音源として明記 (k)TTS方式(Standard同期DEV/Production既定Batch)をページ冒頭に記載 (l)各行に音声とscript同一行 (m)`file:///`/`C:\`なし(Pages URL)。
