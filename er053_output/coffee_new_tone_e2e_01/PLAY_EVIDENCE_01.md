# PLAY_EVIDENCE_01(FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_07 Step 4、Gate 7)

ページ: `user_test/coffee_new_tone_01/index.html`(+ `b1b/player.html`、`b1b/web/episode.mp3`、`b1b/web/segments/*.mp3`、`a2/web/segments/*.mp3`)。ビルド: `er053_output/coffee_new_tone_e2e_01/build_pages_01.py`(API課金0)。mp3は既存 `user_test/coffee_prices_l3_01/` と同じくgit管理。

## 公開URL(GitHub Pages)
`https://shimomura055.github.io/eigo-radio/user_test/coffee_new_tone_01/index.html`
**注意: GitHub Pagesはmain由来のため、本ブランチ(feature/coffee-new-tone-01)をmainへmergeするまで上記URLは404。ユーザー環境から開ける状態(Gate 7 (m))は未達=試聴依頼はmain merge+Pages deploy後(次委任)。** それまで「ユーザーへ提示した」とは扱わない。

## Playwright実再生evidence(`pages_play_evidence_01.json`、`play_verify_01.py`)
Headless Chromium(Playwright、`--autoplay-policy=no-user-gesture-required`)で、`user_test/coffee_new_tone_01` を **Range(206)対応のローカルhttp.server**(GitHub Pages同等の静的配信・seek可)から開き、全`<audio>`を実再生。
| 対象 | audio数 | 再生開始・進行 | duration | エラー | seek |
|---|---|---|---|---|---|
| index.html | 21(Advanced episode+segment、Standard合格segment 9本) | 21/21 PASS(2.5秒再生でcurrentTime進行) | episode 291.26s、segment 1.0〜51.6s | 0(console error 0、HTTP>=400 0) | episode・長尺segmentでseek PASS |
| b1b/player.html | 26(episode + 全segment + KP英語/解説) | 26/26 PASS | 同上 | 0 | PASS |
- Advanced完成音声(通し): `b1b/web/episode.mp3` 291.26s、再生開始・進行・seek OK。
- 表示フォーマット(Gate 7 (n)): `English:/EN:/英語:/日本語gloss` ラベル不在、`(A2)/(B1)/B1B` 非表示、Standard/Advanced表示、`file:///` 不在(いずれもDOM検査でfalse/true期待どおり)。
- 内容(Gate 7 (a)〜(l)): (a)完成episode=Advancedのみ(Standardは**未取得**と明記、HUMAN_REVIEW待ち) (b)Preview (c)Comment全件 (d)本文3 section (e)KP英語+解説 (f)固定shell(welcome等はepisode内、shell表で再利用状況を表示) (g)segment order・click-seek(player.html timeline) (h)各segment voice名 (i)Standard/Advanced分離 (j)未取得segmentは「未取得」明記 (k)TTS方式=Batch(Flash-Lite speech_metadata)明記 (l)再生ボタンとscript/style表同一行。各segment行に `style_source` と style_prefix全文を表示。
- **限界**: 実再生はローカル配信で検証(Pages公開は未達)。聴感(トーン品質)の主観評価は人間ユーザーの試聴が必要で、本evidenceは「再生可能・エラー無し」までを保証する。
