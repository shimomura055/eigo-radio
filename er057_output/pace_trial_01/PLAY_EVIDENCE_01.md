# PLAY_EVIDENCE_01(委任_02、公開GitHub Pages上のPlaywright実再生、Chromium headless、有料APIなし)
URL: https://shimomura055.github.io/eigo-radio/user_test/coffee_pace_trial_01/index.html (HTTP 200)。生データ `pages_play_evidence_01.json`、script `er057_pace_trial_01_play_verify.py`。
- audio要素 36(9ブロック x [Part1/2/3/3Part連結])、**全36件 実再生成功**(再生位置前進、duration>0、error 0)、長尺(>20秒)全件シーク成功。
- 連結音声長 = Part1〜3合計 + 1.6秒(0.8秒x2)を9ブロック全て照合OK(許容0.5秒)。
- HTTP>=400 0件、console error 0件、file://参照なし。
- 行順: 基準F5 -> PASS(合計WPM順 PC4, PC1, PC8) -> 参考(範囲外 PC6, PC2, PC7, PC3, PC5)。各行に説明・Prompt(details)・WPM表・警告・ASR判定。仕様名中立(Final v2/Standard 6%/APPROVED等の語なし)を確認(初版の「Final v2」表記を修正し再検証済み)。
- Pages配信遅延は約1〜2分。音声はmp3 96kbps mono(wavはgitignoreのため非commit、元wavは `attempts/` ローカル)。
- Gate 7 (a)〜(n) の個別項目の定義文は本委任文に無く、PM_GOVERNANCEの項目名と一対一照合はしていない(上記は既存 play_verify_04.py と同種の確認項目を実施)。要Fable照合。
