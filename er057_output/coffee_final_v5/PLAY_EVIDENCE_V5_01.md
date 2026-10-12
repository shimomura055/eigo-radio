# PLAY_EVIDENCE_V5_01 (Gate 7、Playwright実再生。公開Pages上、有料APIなし)

- Base: https://shimomura055.github.io/eigo-radio/user_test/coffee_final_v5/ (commit 9cdf2c20 push後)。生データ: `pages_play_evidence_v5_01.json`、script `er057_coffee_final_v5_play_verify_01.py`(headless Chromium、autoplay許可)。
- HTTP 200: index.html / standard/index.html / advanced/index.html / audio/Coffee_Advanced_final_v5.mp3(全て200)。
- 実再生: index 51/51 audio、standard 26/26、advanced 25/25(全てcurrentTime前進>0.5s)。全編mp3のシーク(終端-5s)OK。
- 全編duration: Standard 316.6s(manifest 316.603)、Advanced 315.71s(manifest 315.71)。
- HTTP>=400 0件、console error 0件、file:///・C:\ 混入なし、(A2)/(B1)/B1Bラベル表示なし、KP 2列表(index 10/std 5/adv 5)、Voiceラベル・開始秒・ジャンプボタン各行あり。
- v4差分(Comment 4 v4→v5新文76字、Std R2、Adv P3、変更/不変role)はページ上部に掲載(has_R2/P3/trial03 =True)。
- 注: 音声品質の合否判断はユーザー試聴(R2/P3の採否は決定済み)。
