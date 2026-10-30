# SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_02A EVIDENCE(一括選定UI=V3拡張、2026-10-30、API 0)

設計=DESIGN_01.md + Opus条件A反映(M1-M5)。実装=`user_test/selection_form_v3/form_logic.js`(純ロジック追加)・`index.html`(一括画面)。本番`data/*.json`・`articles.json`・er128・export_form_data_01.pyは無変更(02Bの実装は読取のみ)。

## 実装(file:line、form_logic.js)
KP_EXACT=3(:8付近)/ normalizeState / sanitizeComment(M4) / composeComment・singleComment(e) / doneSig(M1、SIG_VER=sig1、sha256Hex流用) / doneErrors(①ちょうど3・文法・validateArticle・候補>=3) / doneStatus(done|stale|todo) / selectRemaining(M5、allowed()経由・純関数) / batchSets(batchキー無し=null=M3) / batchCopyErrors / buildBatchReadable(fail-closed)。buildReadable は `opts.comment` 追加のみ(未指定=従来)。`Grep "function doneSig|function selectRemaining|function buildBatchReadable" form_logic.js` で行番号確認。
index.html: 進捗(#progress)/一覧(#list, chip)/選択中バー(#curbar)/①②③(フレーズ/単語を分割し直下にコメント欄)/残り全選択(#selRest)/Done(#doneBox)/一括コピー(#batchBox)/リセット(#resetBox)。M2: `edit()`=セット単位キーの読み直し→変更→書込、`storage`イベントで再描画、一括コピー直前に`loadAllState()`。ChatGPT送信・技術情報付きコピーは一括画面で非表示(関数残置)。batchキー無し=従来の単体画面(M3)。

## コピー形式(02Bと同一契約。02Bの restore_batch/BATCH_*_RE に合わせて確定)
```
以下はeigo-radioの学習項目選定結果(一括)です。…(PREFACE準拠)
▼選定結果
一括ヘッダ:
件数=N / 生成=<ISO> / バッチ=<id>
(空行)
════ SET i/N ｜ <データファイルstem> ════      ← stem=照合コードのstem(例 moon_shrinking__b1b__prod)
<buildReadable出力そのまま。コメントのみ【フレーズ】/【単語】/【追加指示(全体)】の合成>
════ END 合計N件 / BATCH1-N-<sha256(各AIF1コードをSET順に区切り無し連結)[:10]> ════
```
DESIGN_01の記述との差(02B実装と整合させるため): (a) 「一括ヘッダ:」と`件数=…`は2行に分離(02Bの正規表現が行頭`件数=`を要求)、(b) SET区切り名は`<slug>__<level>`ではなくデータ`stem`(02Bが照合コードのstemとの一致を検査)。articles.json `batch.members`もデータstem(slug/slug__levelも許容)。

## test
- node `LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/selection_form_logic_test_01.js`: 58→**70件PASS**(新規12: 3件必須/候補不足/残り全選択純関数+上限防御/署名無効化(選択・文法・各コメント・d6・リロード)/normalizeState互換/コメント合成/区切り注入/一括形式/未完了拒否/単体互換)。既存の陳腐化2箇所(data増加で`==9`/`==10`固定。:22,:263,:435)を`>=`へ修正(本件の変更ではなくdata追加Workerによる既存不整合)。
- Playwright `sub02a_verify.py`: **70チェック全PASS**(`sub02a_verify_result.json`)。1/4/9/10記事×2レベル、Done/解除/再編集、2件Done拒否、3件OK、4件目不可、残り全選択(上限/無効条件)、kp_confirmed、候補不足、未完了コピー拒否(クリップボード不変)、全Doneコピー成功、コメント保存・リロード・切替保持・コピー反映、区切り注入、2タブ同時編集(storageイベント・セット単位書込・後勝ち・コピー直前再検証)、batchキー無し=従来画面、本番articles.json現状(batch無し)=従来表示、`?a=`互換、PC/mobile(チップ>=44px・横スクロール無し)。
- 受入互換: `sub02a_er128_parity.py`=各SETブロックを既存`er128.restore`(無変更)で復元 48/48 OK、END/BATCH1コード一致。`sub02a_er128_batch_accept.py`/一時検証=02B `restore_batch`が1/4/9/10記事サンプル(2/8/18/20セット)を全件受入(origin/main版er128で実行)。
- 既存`form1_selection_form_v3_test_01.py`: 3FAIL+1ERROR(candidate_id件数・kp75 path・placeholder文法・roundtrip)はHEADクリーンworktreeでも同名が失敗する既存不整合(OPEN-613系=data増加・経路変更)で、本件で増減なし(HEAD:6FAIL+2ERROR、作業ツリー:3FAIL+1ERROR)。

## サンプル・スクリーンショット
`sub02a_batch_sample_{1,4,9,10}articles.txt`(02B受入test用)、`sub02a_shots/`(pc/mobile: 一覧・全Done・拒否表示・全体)。fixture=`user_test/selection_form_v3/test_fixtures/`(`sub02a_make_fixtures.py`で再生成可、データはLF正規化=公開Pagesと同一d6)。

## 既知事項・注意
- m8変化: 旧「自由コメント」のみのstateを一括出力すると`【追加指示(全体)】`ラベル付きになりAIF1のm8(コメントsha8)が従来と異なる(設計(e)で承認済みの既知事項)。単体コピーは従来形式を維持(フレーズ/単語コメントが空なら自由コメントそのまま)。
- Chromium/Windowsはクリップボード経由でLF→CRLF化する(テストで吸収。er128はCRLFを吸収する)。
- 本番`articles.json`に`batch`が無いため、公開URLは現状従来表示(fail-closed)。Fableが`export_form_data_01.py --set-batch`(02B)で対象バッチを書出すと一括画面が有効化。
