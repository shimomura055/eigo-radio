# PLAY_EVIDENCE_01C(委任_01C、Gate 7)

API課金0(静的ページ取得・ブラウザ再生のみ)。main commit `92bf1abe`(`user_test/coffee_tone_trial_01/anomaly/` html+mp3 62本+spectrogram PNG 62枚、及びpart_45の調査成果物・スクリプト)をpush後、GitHub Pages配信開始(約3分、HTTP 200確認)。

## 公開URL(HTTP 200)
- 異音候補 人間確認ページ: https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/anomaly/index.html
- 参照(全編音声。既存の完成版ページと同一ファイル): `../../coffee_new_tone_01/a2/web/episode.mp3`(Standard 298.655秒)、`../../coffee_new_tone_01/b1b/web/episode.mp3`(Advanced 291.26秒)

## Playwright実再生(公開URL上、headless Chromium、`play_verify_01c.py`、結果 `pages_play_evidence_01c.json`)
| 項目 | 結果 |
|---|---|
| HTTP | 200 |
| audio要素 | 64(全編2本 + 候補クリップ62本=FOCUS 2 + Standard 30 + Advanced 30) |
| 再生開始・進行 | **64/64 PASS**(`loadedmetadata`→`play()`→2秒後に `currentTime` 進行、`error=null`、duration>0、muted再生) |
| 長尺seek | 全編2本とも seek PASS(120秒位置へ) |
| ジャンプボタン(全編の該当位置へ) | 13本をクリック検証、13/13 PASS(`currentTime` が目標+約1.5秒) |
| 画像(spectrogram PNG) | 62枚すべて HTTP 200(HEAD全件確認)。`loading=lazy` のため初期DOMでの読込済みは25枚(スクロールで残りも読込) |
| mp3 62本 | 全件 HTTP 200 |
| HTTP>=400 / console error | 0 / 0 |
| `file:///`・`C:\` の混入 | なし(DOM検査) |
| `English:/EN:/英語:/日本語gloss` ラベル、`(A2)/(B1)/B1B` | 不在(DOM検査) |

## Gate 7 (a)〜(n)(本ページは「異音候補確認ページ」であり完成版playerではないため、該当しない項目は理由を記載)
- (a) 完成episode: Standard/Advanced の完成episode.mp3(上記)を頁上部に固定表示(再生・seek PASS)。部品sampleではなく実episode構造 / (b) Preview: 全編timelineに Preview の開始秒+seekボタン / (c) Comment 1〜4: 同上(全4件) / (d) 本文3 section(Full Story Part 1〜3、In One Line): 同上 + 候補rowの `segment` 列で位置を特定
- (e) Key Phrase: 全編timelineに Key Phrase 1〜5 の開始秒。英語+日本語gloss表示は完成版playerに存在(`../../coffee_new_tone_01/{a2,b1b}/player.html`)。本ページは候補のsegment名(Key Phrase N 英語/日本語意味/英語解説)と近傍の語を表示 / (f) Intro/Outro/Notification(SFX): timeline上に開始秒・長さを表示、読み上げなし(固定音源) / (g) segment order・開始秒・click-seek: timelineの全行にseekボタン、候補rowに「全編 N秒 から」ボタン(13本検証PASS)
- (h) 各segmentの使用voice: 候補rowに `tts_generation_results.json` 記録のvoiceを表示(本文=Aoede、StandardのKP等は audit上Aoede、固定shellは「固定shell/共通音声(Master Store)」)。委任_09で既知の通り、完成版player上のvoice表示ラベルには不整合がある(本ページの表示は audit由来) / (i) Standard/Advancedの明確な分離: 候補表は2つのh2に分割、ID接頭辞 STD-/ADV-、timelineも別表
- (j) テキスト未取得segment: 候補rowの「近傍の語」はlocal whisper転写(日本語/英語)で、完成版の原稿全文ではない(全スクリプトは完成版playerを参照)。原稿が存在しないsegment(num_*等)は一覧から除外している。 / (k) TTS方式: 頁冒頭に「Gemini 3.8 Flash-Lite TTS(Batch、既存run音声の再解析のみ)」と明記
- (l) 再生ボタンとscript(近傍の語)を同一行: 候補rowに audio(360px以上)+spectrogram+近傍の語+判断欄を同一行配置。完成版の完全scriptは完成版playerに存在(本ページは確認用)
- (m) 公開URLはGitHub Pages(HTTP 200)。`file:///`・`C:\` 不在をDOM検査で確認(上表)
- (n) `English:/EN:/英語:/日本語gloss` ラベル不在、`(A2)/(B1)/B1B` 非表示、Standard/Advanced表示(上表)

## 既知の限界
- 聴感・異音の有無の判断は人間ユーザーの試聴が必要。本evidenceは「公開URLで再生可能・エラー無し」までを保証する。
- 全編timelineはStandard/Advancedの完成episode(委任_09時点)に基づく。
