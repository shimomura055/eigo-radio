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

## § 追加4項目(rev01-c、委任_03、2026-10-29)
URL=https://shimomura055.github.io/eigo-radio/user_test/dev_enduser_page_01/index.html (build-id `rev01-c`、live反映確認、cache無効取得)。原文=delegation_log/2026-10-29_END-USER-LISTENING-PAGE-DEV-REVISION-01_USER_02.md。API 0・Production変更0。
- 実装: ①見出し=`app.js` glossHtml(`覚えておきたい表現`、全箇所) ②順序=app.js Full Story描画の `sentHtml+glossHtml+trHtml`(2箇所、内容・リンクは不変) ③停止=app.js btns()に`■ 停止`(`.seek.stop`、data-act=stop)追加+content clickハンドラで`A.pause()`、style.css末尾`.seek.stop` ④文法仮表示=app.js render()の`grammar_source==='placeholder_for_layout_check'`分岐で`.phnote`(「【仮データ・表示確認用】他記事(月のしわ Advanced)の文法解説を流用しています。…」、橙破線枠)+ラベル`GRAMMAR(仮)`。
- 仮データ: 出典=`data/moon.json` levels.adv.grammar[0](月のしわAdv実データ)をdata/ai_island.json の std/adv へコピー。マーカー`grammar_source=placeholder_for_layout_check`・`grammar_placeholder_origin`をdataに付与。月Advの実データ(マーカー無し・注記無し)は不変。表示経路はDEVページ(user_test/dev_enduser_page_01)のみ。公開記事ページ・Production・生成物には未接続。
- 公開検証(Playwright、PC1280/スマホ390x844、公開URL): 216チェック NG 0。①見出し文字列PASS ②DOM順(script→gloss→tr)・視覚順・「日本語訳」タグ・解説リンク維持PASS ③停止ボタンが各「ここから再生」の隣(11/10/10個)、停止で再生停止(currentTime固定)、パート境界を跨ぐ連続再生中の停止、停止後の再開(ここから再生/固定バー)・シーク・1文ハイライト、KP再生中の停止 PASS ④AI島Std/Advに仮コーナー+明示文言+data marker、横溢れなし、月Advは実データ表示のまま PASS。既存Regression(rev01-b 176チェック相当: KP英語のみ/意味一覧/リンク/日本語訳/連続再生/Full Story連結/ハイライト精度/シーク/タブ/overflow/console error 0/4xx 0)全PASS。
- 検証スクリプト=tools/verify_rev_c_01.py(verify_rev_01.pyから順序・ボタン構成・仮文法に合わせ期待値を更新)。結果=verify_result_rev_c_live_01.json、shots_rev_c_live/。ローカル初回は期待値側の誤り6件(仮文法dt数を4と誤指定・月Advにリンク0件)のみNG→期待値修正し、公開で全件再実行しPASS(ローカル再実行は未実施)。
- 未確認: 実機iOS/Androidの実機操作、ローカル再実行(修正後)。

## § 追加5項目(rev01-d、委任_04、2026-10-29)
原文=`docs/pm/delegation_log/2026-10-29_END-USER-LISTENING-PAGE-DEV-REVISION-01_USER_03.md`。ビルドID rev01-d。変更=`user_test/dev_enduser_page_01/`のみ(Production・API 0)。
1. 上部「DEV試作」バー・フッターの「DEV試作…」を削除(`<title>`は`[DEV]`のみ)。同期状態表示`#syncState`は検証用に非表示(hidden)で保持。
2. 記事切替UI(select・見出し)削除。`?a=`/`?lv=`による記事・レベル指定は維持(既定=AI島)。Std/Advタブは維持。
3. 「■ 停止」を赤系→濃グレー黒系(#2f343d地・白字)。文言・機能不変。
4. 学習ブロックを枠線+淡背景: Vocabulary=黄(#fffbea/#e6c84a)・Grammar=青(#f1f6ff/#8fb2ee)・ニュアンス解説=緑(#f1faf3/#86c795)。添付イメージ未受領のため淡色背景+同系細枠で統一。
5. ニュアンス解説仮表示: AI島Std/Adv・月Advに「ニュアンス解説」コーナー(文法の後)。出典=02C証拠`NUANCE-EXPLANATION-PRODUCTION-WIRING-01/evidence/X_nxm1_..._standard__nuance_fragment.html`(Std)・`X_nxm2_..._advanced__nuance_fragment.html`(Adv)の採用1件。dataに`nuance_source=placeholder_for_layout_check`、画面に「【仮データ・表示確認用】他記事のニュアンス解説を流用。記事本文とは内容が対応しません。」。生成: `tools/build_rev_d_01.py`。DEV data以外に接続なし。
注記: 日本語訳ラベル「(DEV訳・未承認)」は既存の維持対象(日本語訳)のためそのまま。
検証: `tools/verify_rev_d_01.py`(rev_c全項目継承+D1-D5)。ローカル274チェック中NG6=「DEV文字列なし」判定が`(DEV訳・未承認)`に反応した検査側の過剰判定(正規表現を修正済み)。結果は公開検証`verify_result_rev_d_live_01.json`。
