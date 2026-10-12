# PLAY_EVIDENCE_02(委任_01、公開GitHub Pages上のPlaywright実再生、Chromium headless、有料APIなし)
URL: https://shimomura055.github.io/eigo-radio/user_test/coffee_pace_trial_02/index.html (HTTP 200、commit 960cfac0)。script `er057_pace_trial_02_play_verify.py`(01を再利用)。
- audio要素 36(9ブロック x [Part1/2/3/3Part連結])、全36件 実再生成功(再生位置前進、duration>0、error 0)、長尺(>20秒)全件シーク成功。
- 連結音声長 = Part1〜3合計 + 1.6秒(0.8秒x2)を9ブロック全て照合OK。
- HTTP>=400 0件、console error 0件、file://参照なし。
- 行順(合計WPM遅い順、F5を同列): PD8, PD1, PD6, PD4, PD7, PD2, PD3, PD5, F5 を確認(order_slow_first=True)。各行に Prompt全文(details)・WPM表・警告・ASR判定・F5からの主要変更点・品質所見(機械指標)。仕様名中立(PD1〜PD8/F5、Final v2/Standard 6%/APPROVED等の語なし)。Blindにしていない。
- Pages配信は push後 約2.5分で200。音声mp3 96kbps mono(約30.6MB、wavは非commit)。
- Gate 7 (a)〜(n) の個別項目定義は本委任文に無く、01同様 既存play_verifyと同種項目を実施。要Fable照合。
