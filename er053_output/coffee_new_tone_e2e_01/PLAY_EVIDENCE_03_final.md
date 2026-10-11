# PLAY_EVIDENCE_03_final(FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_09、Gate 7)

API課金0(静的ページ取得のみ)。main commit `c93c10ea`(`user_test/coffee_new_tone_01/` の html+mp3 のみ、15ファイル)をpush後、GitHub Pages配信開始(約2.5分、200確認)。

## 公開URL(HTTP 200)
- 通しページ(Standard/Advanced両完成版): https://shimomura055.github.io/eigo-radio/user_test/coffee_new_tone_01/index.html
- Standard player(通し再生+全スクリプト+Key Phrases): https://shimomura055.github.io/eigo-radio/user_test/coffee_new_tone_01/a2/player.html
- Advanced player(同): https://shimomura055.github.io/eigo-radio/user_test/coffee_new_tone_01/b1b/player.html
- part2_review(採用済み表示): https://shimomura055.github.io/eigo-radio/user_test/coffee_new_tone_01/part2_review/index.html

## Playwright実再生(公開URL上、headless Chromium 153.0.8010.12、`play_verify_03_final.py`、結果 `pages_play_evidence_03.json`)
| ページ | HTTP | audio数 | 再生開始・進行 | HTTP>=400 | console error | seek(長尺) |
|---|---|---|---|---|---|---|
| index.html | 200 | 23(Advanced episode 291.3s + Standard episode 298.7s + 各segment) | 23/23 PASS | 0 | 0 | 8/8 PASS |
| part2_review/index.html | 200 | 5 | 5/5 PASS | 0 | 0 | 5/5 PASS |
| a2/player.html (Standard) | 200 | 22(episode 298.7s + segment/KP) | 22/22 PASS | 0 | 0 | 4/4 PASS |
| b1b/player.html (Advanced) | 200 | 26(episode 291.3s + segment/KP) | 26/26 PASS | 0 | 0 | 4/4 PASS |
各audioで `loadedmetadata`→`play()`→2.5秒後に `currentTime` 進行、`error=null`、duration>0(muted再生)。

## Gate 7 (a)〜(n)
- (a) 完成episode: Standard(`a2/web/episode.mp3` 298.655s)・Advanced(`b1b/web/episode.mp3` 291.26s)とも通し再生PASS / (b) Preview / (c) Comment 1〜4 / (d) 本文3 section(part1/2/3、両player): 両playerの行に存在 / (e) Key Phrase: Standardは「英語Phrase / 日本語意味」、Advancedは「Phrase / 英語解説」をplayer行で確認可(個別音声付き、ラベル文字列なし) / (f) 固定shell: 両levelとも再利用(index表、Advancedと同一sha256: `phase09/shell_sha_compare_09.txt`) / (g) player.htmlのsegment order・click-seek / (h) 各行にvoice名 / (i) Standard/Advanced分離 / (j) full_story_part2: Standard player行に「採用音声=Attempt 4(Local Rewrite後)、ユーザー試聴PASS 2026-10-11、個別Human Approval、記事全体の品質承認ではない」と明記、読まれた文面の差分も併記、part2_reviewへリンク / (k) TTS方式 Batch(Flash-Lite speech_metadata)明記 / (l) 各segment行にplayer+style_source+style_prefix(全文)同一行(index表)。
- (m) 公開URLはGitHub Pages(HTTP 200)。`file:///`・`C:\` 不在をDOM検査: 4ページとも false。
- (n) `English:/EN:/英語:/日本語gloss` ラベル不在、`(A2)/(B1)/B1B` 非表示(4ページとも DOM検査 false)、index/part2_reviewにStandard/Advanced表示。

## 既知の限界・観察
- 聴感(tone品質・読み違い有無)は人間ユーザーの最終試聴が必要。本evidenceは「公開URLで再生可能・エラー無し」までを保証する。
- Standard/Advancedのplayer.html内の行ラベル(例: Standardの固定shell行が `voice=Aoede` 表記、Advancedは `Charon`/`Aoede` 混在)はランナーplayer(`build_player_html`)由来の表示で、実際のshell音声はMaster Store key上 Charon(両levelで同一sha256)。表示ラベルの不整合はOPEN候補(音声自体の問題ではない)。
