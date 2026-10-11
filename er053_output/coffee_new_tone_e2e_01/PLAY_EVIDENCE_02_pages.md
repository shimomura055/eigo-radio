# PLAY_EVIDENCE_02_pages(FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_08、Gate 7)

API課金0(静的ページ取得のみ)。main commit `f8e63c8b`(`user_test/coffee_new_tone_01/` の html+mp3 のみ、39ファイル)をpush後、GitHub Pagesが約2分で配信開始(200確認)。

## 公開URL(HTTP 200確認済み)
- 通しページ: https://shimomura055.github.io/eigo-radio/user_test/coffee_new_tone_01/index.html
- part2 Human Reviewページ: https://shimomura055.github.io/eigo-radio/user_test/coffee_new_tone_01/part2_review/index.html
- (参考)Advanced個別player: https://shimomura055.github.io/eigo-radio/user_test/coffee_new_tone_01/b1b/player.html

## Playwright実再生(公開URL上、headless Chromium、`play_verify_02_pages.py`、結果 `pages_play_evidence_02.json`)
| ページ | HTTP | audio数 | 再生開始・進行 | HTTP>=400 | console error | seek(長尺) |
|---|---|---|---|---|---|---|
| index.html | 200 | 21(Advanced episode 291.26s + Advanced 10 segment + Standard合格9 segment) | 21/21 PASS | 0 | 0 | PASS |
| part2_review/index.html | 200 | 5(参考1+attempt 1〜4) | 5/5 PASS(47.72〜52.6s) | 0 | 0 | 5/5 PASS |
| b1b/player.html | 200 | 26 | 26/26 PASS | 0 | 0 | PASS |
各audioで `loadedmetadata`→`play()`→2.5秒後に `currentTime` が進行、`error=null`、duration>0 を確認(muted再生)。

## Gate 7 (a)〜(n)
- (a) 完成episode=Advancedのみ(`b1b/web/episode.mp3`)。Standardは通し**未取得**とindex.htmlに明記(推測補完なし) / (b) Preview / (c) Comment 1〜4: segment表・player.htmlに存在 / (d) 本文3 section(part1/2/3) / (e) Key Phrase(英語+解説、player.html、ラベル文字列なし) / (f) 固定shellは表で再利用状況を表示(episode内) / (g) player.htmlのsegment order・click-seek / (h) 各segmentにvoice名 / (i) Standard/Advanced分離 / (j) `full_story_part2`は「未取得」明記+part2_reviewへリンク / (k) TTS方式 Batch(Flash-Lite speech_metadata)明記 / (l) 各segment行にplayer+style_source+style_prefix同一行。part2_reviewは各attemptカード内にplayer・種別・style_source・ASR転写・判定理由を同一ブロック配置。
- (m) 公開URLはGitHub Pages(HTTP 200、`file:///`・`C:\` 不在をDOM検査: 3ページとも false)。
- (n) `English:/EN:/英語:/日本語gloss` ラベル不在、`(A2)/(B1)/B1B` 非表示(3ページ全てDOM検査で false)、index/part2_reviewにStandard/Advanced表示。

## 限界
聴感(読み違いの有無・tone品質)は人間ユーザーの試聴が必要。本evidenceは「公開URLで再生可能・エラー無し」までを保証する。
