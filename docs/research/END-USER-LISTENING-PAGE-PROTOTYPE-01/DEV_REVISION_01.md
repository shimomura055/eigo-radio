# END-USER-LISTENING-PAGE-DEV-REVISION-01 委任_01 記録(DEV試作・Production変更0・LLM/TTS API 0円)

状態: **ローカル検証=完了(176項目PASS/NG 0)。公開(GitHub Pages)検証=未確認**。理由: `git merge origin/main` が `user_test/dev_enduser_page_01/{app.js,data/ai_island.json,data/moon.json}` でconflict(origin/mainにChatGPT DEV commit 4件が追加で存在)→委任文どおり `--abort` して未push。公開URL・ビルドID=`rev01-b`(push後に live で一致確認予定)。

## 1. 復元の記録
- 復元元: commit `c8d0865bb`(Claude版 委任_02完了。コード内容は `a376afde4` と同一)。`git checkout c8d0865bb -- user_test/dev_enduser_page_01/` で app.js / index.html / style.css / data/ai_island.json / data/moon.json を復元(他パス不変。ChatGPT commitが追加した新規ファイル=なし、削除ファイル=なし)。
- 全面破棄したChatGPT commit(user_test/dev_enduser_page_01 を変更した shimomura055 名義、15件):
  - 取り込み済み11件: 01d54c182, 7348957c9, 6b681f037, 093803022, ab17bf652, 2a0c48b6e, 673cd5307, 1010bc9e5, 02525c119, 983f42e95, 51a5bf5fa
  - origin/mainにのみ存在する追加4件(未取込み。mergeでconflictの原因): 52a30890a, 4b5e9c009, be97724ac, c58bacda1(いずれも `DEV glossar*` 系。app.js/ai_island.json/moon.json)
- ChatGPTの日本語訳・実装は参照・採用していない(日本語訳は後述の承認済み原稿またはWorker作成DEV訳)。

## 2. 10項目(実装 file:line / ローカル / 公開)
検証script=`tools/verify_rev_01.py`(Playwright PC1280/モバイル390x844、結果=`verify_result_rev_local_01.json`、画像=`shots_rev/{pc,mobile}_01..10`+補助b画像)。公開列は未実施のため「未確認」。

| No | 内容 | 実装(file:line) | ローカル | 公開 |
|---|---|---|---|---|
| 1 | 全体再生をタブ直下へ・拡大 | index.html:19-20、style.css `.playall`(高68px/21px/全幅) | PASS(タブ下、PC高68px・フォント21px、クリックで全体mp3再生、タブ切替は不変) | 未確認 |
| 2 | KP/Word英語のみ | app.js `playKp`/`endKp`、data `kp[].en_audio`、tools/build_rev_01.py | PASS(9 KP全て: 英語区間開始±0.6s内で再生開始→終端+0.35s以内で停止・全体音声へ復帰。切出し区間のwhisper(small)=言語en・文字起こし=KP表現と一致 `kp_audio_check_01.json`) | 未確認 |
| 3 | 本文下の意味一覧+解説リンク | app.js `glossHtml`/`a.glink`ハンドラ、vocab `id=vi-<lv>-<n>` | PASS(下線対象+KP+Vocab全件を網羅、重複0、各リンククリックで該当表現のdetailsが開き位置へスクロール。モバイルはページ末尾項目のみ画面内移動に制限) | 未確認 |
| 4 | 2列・控えめ枠 | style.css `.gloss` | PASS(PC 2列/モバイル1列、背景#f7f8fa+枠1px、本文より小、日本語意味rgb(31,41,51)) | 未確認 |
| 5 | 日本語訳 | app.js `trHtml`、data `parts[].ja/ja_source` | PASS(英語ブロック全件に直後の訳、欠落0、空欄/ダミー0。内訳は§3) | 未確認 |
| 6 | 「▶ ここから再生」一本化 | app.js `btns`、`playFull(parts[i].start)` | PASS(「このパート」「通しで」DOM 0、各パート1ボタン。3記事で実時間のままパート境界を越え連続再生・ハイライトが次パートへ移動。シークバーで終端付近へ移動後も連続) | 未確認 |
| 7 | Full Story+In One Line連結 | app.js render `#fullstory`内 `.partblock.oneline` | PASS(In One Lineは独立カードなし、Comment 4直後、見出し維持、ハイライト・訳動作) | 未確認 |
| 8 | 文法あり/なし | app.js grammar描画、style.css `.gr` | PASS(月Adv: Vocab5件+Grammar表示(1項目・5欄)、AI島Std/Adv: Grammarカード0・文字列0) | 未確認 |
| 9 | 解説文字・色 | style.css `details.vi ...` | PASS(dd 17px/意味17px/見出し18px、意味・解説色rgb(16,24,40)。旧は16px・#667085。モバイルdd16.5px) | 未確認 |
| 10 | 下線凡例削除 | app.js(legend生成コード撤去) | PASS(凡例文字列0・`.legend`0、lk1/lk2/lk3のspan残存、太字+二重下線等の計算値維持) | 未確認 |

## 3. 日本語訳の出典
- Full Story Part 1〜3(3記事・計9ブロック、段落25): **承認済み日本語原稿 `revision2.md` の対応段落を再利用**(AI島 `er019_output/ai_island_temple/run_form_prod_01/ja_writer/revision2.md`、月 `er019_output/moon_shrinking/run_reselect_01/ja_writer/revision2.md`。sha=runtime_evidence.ja_text_sha256と一致を確認。英語は日本語原稿の段落対応翻案で、段落数が一致=AI島8/月9)。英語Part本文の文単位訳ではなく「対応段落の日本語原稿」。
- Std Comment 1〜4: 既に日本語本文のため訳不要(4ブロック、native_ja)。
- **DEV訳(未承認)11ブロック**: AI島Adv Comment 1〜4+In One Line(5)、AI島Std In One Line(1)、月Adv Comment 1〜4+In One Line(5)。承認済み日本語原稿に対応段落がなく、Workerが英文の意味・事実を保持して作成。データ(`ja_source=dev_translation_unapproved`)と画面(「DEV訳・未承認」ラベル)に明記。訳文は tools/build_rev_01.py `DEV_TR`。
- Vocab/意味一覧の日本語意味: 既存の承認済みVocab「本文中の意味」と Part別 `meanings` を再利用(新規作成0)。

## 4. KP英語のみ再生の方式
既存KP区間mp3は「番号→英語→日本語の意味(Advは英語の解説)→英語再掲」の構成(例: std_09発話ブロック0.24-0.65/1.72-2.45/3.47-4.24/5.13-5.86s、`narration`の個別wavと同形)。音声ファイルは変更せず、silencedetect(-40dB,0.2s)で2番目の発話ブロック(最初の英語)の開始-0.08s/終了+0.15sを `kp[].en_audio` に記録。ページはKP区間mp3の該当秒へシークして再生し、rAFで終端到達時に停止、全体音声(パート開始位置)へ復帰。AdvのKPも英語の語句のみ(英語解説は流さない)。

## 5. Regression(ローカル、AI島Std/Adv・月Advの全3ケース)
1文ハイライト精度(各記事約24文サンプルのシーク点灯=誤り許容1/20以内)、文クリック再生、シーク(50%)、再生/一時停止、レベル往復切替、横スクロールなし、console error 0、HTTP 4xx/5xx 0 = 全PASS。

## 6. 未完了・未確認一覧
1. **公開URL(GitHub Pages)での10項目再検証=未実施**(push不可: origin/main追加ChatGPT commit 4件とのconflict。委任文により `--abort`)。
2. DEV訳(未承認)11ブロックの訳文品質はユーザー未確認。
3. 聴感確認(KP英語区間の切れ目の自然さ)は自動検証(whisper・停止位置)のみ。
4. Fable独立受入評価=Fable側で実施。

## 7. commit
- 実装commit(ローカル、未push): `2246d0180`。docs commitは別途。

## 委任_02 統合push・公開検証(2026-10-29)

- 統合: `git merge --no-ff origin/main`、conflictは user_test/dev_enduser_page_01/{app.js,data/ai_island.json,data/moon.json} の3件のみ。ユーザー指示(ChatGPT改修は全面破棄・Claude版を復元)に基づき全て ours(Claude版rev01-b)で解決。ChatGPTのみが追加したファイルは無し(削除0)。`git diff HEAD -- user_test/dev_enduser_page_01/` 空を確認。merge commit e6c32caec、push成功(487eb2cb7..e6c32caec)。
- 公開反映: live index.html に build-id rev01-b を確認(11:55:30頃、cache無効取得)。取得・検証時刻=2026-10-29T11:59+0900。
- 公開検証(PC/スマホ、tools/verify_rev_01.py、cache無効): TOTAL 176 / NG 0。10項目すべてPASS(公開列: 全体再生移動/KP英語のみ/意味一覧+解説リンク/日本語訳/ここから再生/In One Line連結/解説拡大/凡例削除ほか)、Regression(ハイライト精度・文クリック再生・シーク・再生停止・レベル切替・横overflow無し・console error 0・4xx/5xx 0)PASS。未確認=実機iOS/Android。
- 証跡: shots_rev_live/{pc,mobile}_01..10、verify_result_rev_live_01.json。NG是正: 無し。
