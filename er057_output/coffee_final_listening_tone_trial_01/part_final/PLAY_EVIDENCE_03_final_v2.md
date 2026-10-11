# PLAY_EVIDENCE_03_final_v2(委任_03、公開GitHub Pages上のPlaywright実再生、有料APIなし)

URL(ユーザー向け、GitHub Pages): 
- 両Level一覧(通し全編+全script+KP): https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/final_v2/index.html
- Standard単独: https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/final_v2/standard/index.html
- Advanced単独: https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/final_v2/advanced/index.html
生データ: `pages_play_evidence_03.json`、実行script `play_verify_03.py`(Chromium 153.0.8010.12 headless、muted実再生)。commit 9e0837f9(静的ファイルのみ)、Pages deploy後に200確認。

| ページ | HTTP | audio要素 実再生OK/総数 | 長尺seek | ジャンプ(全編位置へ) | HTTP>=400 | console error |
|---|---|---|---|---|---|---|
| index.html | 200 | 52/52 | 全OK | 10/10 OK | 0 | 0 |
| standard/index.html | 200 | 27/27 | 全OK | 5/5 OK | 0 | 0 |
| advanced/index.html | 200 | 25/25 | 全OK | 5/5 OK | 0 | 0 |
episode mp3: Standard 4,729,772 B / Advanced 4,616,108 B / 旧topic_intro参考 65,420 B いずれもHTTP 200。

## Gate 7 (a)〜(n) 確認
(a) 完成episode音声(両Level通し全編、Standard 295.6秒/Advanced 288.5秒、実episode構造)=OK。(b) Preview=OK(行あり)。(c) Comment 1〜4全件=OK。(d) 本文Full Story Part1〜3+In One Line=OK。(e) Key Phrase 5件の英語+日本語gloss(表示用)=OK(`table.kp` 左=英語/右=日本語の2列、各Level5件)。(f) Intro/Outro/通知音は「固定音源(TTSなし)・読み上げなし」と明記=OK。(g) segment order・開始秒・click-seek=OK(全編位置へジャンプ、timeline順)。(h) 各segmentのvoice名=OK(Charon/Aoede)。(i) Standard/Advancedの分離=OK(別セクション・別ページ)。(j) 未取得segmentなし(全script取得済み、日本語原稿は`a2_support_texts.json`、英語は`parts.json`等)。(k) TTS方式=「Gemini gemini-3.8-flash-lite-tts・speech_metadata方式・Standard同期(試聴用DEV、Production既定=Batch)」と明記=OK。(l) 各音声の再生ボタンとscript/由来/Style/Voiceが同一行=OK。(m) `file:///`・`C:\`混入なし(HTML全文検査、`file_scheme_in_html=False`)、GitHub Pages公開で開ける=OK。(n) KP表示に`English:`/`日本語:`等のラベル文字列なし(`EN_JA_gloss_label_present=False`)、(A2)/(B1)/B1Bラベルなし(`A2_B1_level_label_visible=False`)=OK。
追加表示: 再生成/再利用の別、適用Style名(A5/B5/E1/F5/K2/M2/P2/既存承認)、Standard 6%減速適用(処理前後秒数と実測%)、Advanced K2未適用の明記、STD-24の旧take併載。
