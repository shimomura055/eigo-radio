# HANDOFF_DESIGN_01 送信・コピー改善の設計(委任_06、到達=DESIGN_READY。実装は委任_07)

前提: `HANDOFF_SURVEY_01.md`(推奨=(b)+(c))、`COPY_FORMAT_01.md`、`RESTORE_TOOL_SPEC_01.md`。ユーザー原文=`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER_03.md`。Status=APPROVED_FOR_PRODUCTION(ユーザー正式決定)。

## 1. フォーム側の動作(委任_07で`form_logic.js`/`index.html`を変更)

### 「ChatGPTへ送信」(1クリック)
1. `text = PREFACE_NEW + buildReadable(d, st)`(人間可読+照合コード1行。`COPY_FORMAT_01.md`)。
2. **クリック処理の同一tickで**クリップボード書込みを開始(`navigator.clipboard.writeText`のPromiseを保持。失敗時は`execCommand('copy')`、それも失敗なら読取専用textareaに全文表示して手動コピー案内)→ 続けて`window.open`。※`writeText`はページにフォーカスがある間に開始する必要があり、`window.open`より先に呼ぶ。`window.open`はユーザー操作と同期(ポップアップブロック回避)。
3. `url = 'https://chatgpt.com/?q=' + encodeURIComponent(text)`が`URL_MAX`以内 → そのURLで開く。超過 → `https://chatgpt.com/`(`q`なし)を開く。`URL_MAX`は現行6000を維持(ユーザー実測で引き上げ可。SURVEY §5)。JSON同梱は**廃止**(降格順は「URL本文入り → 貼付案内」の2段のみ)。
4. 状態表示(`#status`、警告色ではなく通常色):
   - URL内蔵: 「選定結果をコピーし、ChatGPTを開きました。入力欄に内容が入っていればそのまま送信、空ならCtrl+V / ⌘V で貼り付けて送信してください。」
   - 貼付方式: 「選定結果をコピーしました(内容が長いため貼り付け方式です)。開いたChatGPTの入力欄にCtrl+V / ⌘V で貼り付けて送信してください。」
   - コピー失敗: 「自動コピーできませんでした。下の枠のテキストを手動でコピーしてください。」(状態は保持)
5. 選定状態(localStorage、記事×レベル別。現行`save()`)は送信・コピーのどの結果でも**変更・消去しない**(現行と同じ。testで固定)。

### 「選定結果をコピー」
`buildReadable(d, st)`(PREFACEなし)のみコピー。JSON・candidate_id一覧・SHA全文・`candidates_all`・`ai_reference`は表示/コピーしない。成功時「選定結果をコピーしました。」

### 任意の補助(推奨・小): 「技術情報付きでコピー(通常は不要)」
`<details>`内の小ボタンで従来の`buildCopyText`(テキスト+JSON、`candidates_all`付き)を維持。直接`er128 confirm --from-form`に渡せる**逃げ道**(復元toolの障害時・data版が履歴から取れない場合)で、ユーザーのJSON手編集は不要(ファイルへ貼るのはClaude)。表示の主導線には出さない。分類=B(承認範囲内の自己解決。ユーザー原文§4「内部情報は表示から分離」に整合: 既定で見えない)。委任_07で採否を再確認。

## 2. 「ChatGPT側で取得できない方式は不可」との関係(論証)
- ChatGPTが受け取るもの=人間可読の確定内容そのもの(記事・①②③の英語と日本語訳・文法名と解説全文・自由コメント)+照合コード1行。**ChatGPTは外部取得を一切しない**(URL/ブラウザ保存データ参照なし)。欠落が起き得るのは「URLに載らない長さ」のみで、その場合は同じ全文をクリップボード経由(貼付)で渡す。
- candidate_id・本文sha・候補集合shaは、**公開データJSON(`user_test/selection_form_v3/data/<stem>.json`。リポジトリ=GitHub Pagesと同一ファイル)**に既にあり、ChatGPTを経由しない。復元はClaude側(ローカルrepo)が照合コードで行う。照合コードには データ版`d6`/候補集合sha`c8`/本文sha`t8`/選択集合`s10`/文法集合`g10`/コメント`m8`/チェック`k4`が入り、選定の欠落・改変・取り違えは検出される(prototype実測: `proto06_output_01.txt`)。
- ChatGPTを経由しない直接貼付(方式(h))でも同一の手順で復元可能。

## 3. ChatGPT応答の扱い(PREFACEの簡素化・推奨)
現行PREFACE(「選定内容を整理し…Claude Code向け指示案を作成してください」)は、ChatGPTに**内容を書き換えさせる余地**を与える(原文条件5「送信途中で意図せず内容が変更されないこと」と緊張)。推奨:
```
以下はeigo-radioの学習項目選定結果です。内容(英語・日本語訳・区分・文法解説・自由コメント・照合コード)を一切変更・要約・翻訳せず、下の「選定結果」をそのままコードブロックで返してください。修正してほしい点があればコードブロックの外に書いてください。
```
- ChatGPTには**中継・整形ではなく原文再掲**をさせる。コードブロックで返させる理由=ChatGPT画面でMarkdownが描画されると`**強調**`・リスト記号が変わるため、コピーボタン(コードブロック)で逐語コピーさせる。
- 変更があっても復元tool側で検出(fail-closed)するため、PREFACEが守られなくても誤確定はしない(安全はPREFACEに依存しない)。
- 「Claude Code向け指示案を作成」を残したいかはユーザー運用判断(既存の使い方)。残す場合も「選定結果ブロックは逐語で別掲」を条件にする。**判断区分=B**(承認範囲内: 原文§3-5「途中で内容が変更されない」を満たす最小変更。文言は委任_07/Fable受入で確認)。

## 4. 既存Production Wiringとの整合(原文§5)
| 項目 | 整合 |
|---|---|
| 文法Top1/Top2提示・最大1件(GPG委任_05A) | コピー形式は文法0〜N件を扱う(Nは`form_logic.js`の`GRAMMAR_MAX`/er128の`GRAMMAR_MAX`)。復元payloadの`grammar[]`は選択された分のみ(<=1) |
| 文法解説全文の事前生成 | 文法の解説全文は**公開データJSONの`grammar[].body`**(事前生成物と一致する値)をコピーに含め、復元で逐語照合。er128 `_validate_form_grammar`(L1390-)の`explanation_full==explanation_md`検査は復元payloadにdata値を入れるため従来どおり働く(data更新時は不一致→ISSUE) |
| ユーザー確定内容の保護(er128 `confirm --from-form`、L1297-) | 復元toolは**同じpayload v2(`schema_minor:1`)**を生成して既存`cmd_from_form`に渡す。`cmd_from_form`が読むのは`schema_version/article/selection/comment`のみ(L1302-1382)。`ai_reference`・`candidates_all`・`limits`は読まない=コピーから外しても確定処理に影響しない |
| KP/KW①②③分類・上限(3/5/12) | 復元は上限を検査しない(フォーム時点で担保)が、er128 `op_select`が従来どおり検査 |
| X/Y/Z共通フォーム | 照合コードの`stem`(`<slug>__<level>[__prod]`)でデータを特定。Family非依存 |

## 5. 作業分担(競合回避)
| 作業 | 担当 | 競合 |
|---|---|---|
| `form_logic.js`/`index.html`: `buildReadable`/`buildCode`/送信・コピー動作 | 委任_07(フォーム実装)。AI-ISLAND 委任_02完了後 | AI-ISLAND委任_02が`user_test/selection_form_v3/**`編集中 → 委任_07は同委任のマージ後に着手 |
| 復元tool `er128_form_readable_restore_01.py`(新規ファイル)+CLI `confirm --from-readable` | GPG委任_05A完了後の小委任(er128/CLI/exporter編集権あり)。**新規ファイル+薄いCLI追加のみ**で既存関数は変更しない | GPG 05Aが`er128`/CLI編集中 → 本設計の入力(`RESTORE_TOOL_SPEC_01.md`)だけ先に渡す |
| `export_form_data_01.py` | **変更不要**(`d6`は出力ファイルのsha、他は既存フィールドを使用) | なし |
| 並列化 | フォーム側(JS)と復元tool(Python)は**契約=`COPY_FORMAT_01.md`+コード仕様**のみで独立。2者を並列実装でき、契約testで一致(`TEST_PLAN_06.md` T-C) | — |

## 6. Opus独立レビュー要否(条件A)
**不要と判断(根拠を明記)**: 新規バックエンド・外部サービス・保存先を採らない。新規の「識別子方式」は、既存の公開データJSON(固定sha)と既存の`candidate_id`/`candidates_sha256`を**参照するだけの検査用短縮コード**で、保存・取得系の新構造を含まない(復元はローカルrepo読取のみ)。変更は表示形式+クリップボード動作+Claude側read-only復元。判断はFableが覆してよい(Fableがコード方式を新構造と見なす場合は`OPUS_REVIEW_REQUEST_02.md`を起こす)。`OPUS_REVIEW_REQUEST_02.md`は作成しない。

## 7. リスクと緩和
| リスク | 緩和 |
|---|---|
| ChatGPTがブロックを改変 | 照合コード+逐語検査で検出→fail-closed(再コピーを案内。ユーザー編集不要) |
| クリップボード不可(権限/Safari) | textarea表示の手動コピー(現行実装維持)。選定状態は保持 |
| 選定後にdata JSONが更新 | `d6`で選定時版をgit履歴から取得(取得不可なら選び直し案内) |
| `?q=`が効かない/落ちる | 常にクリップボードにも入っているため貼付で完了(正常動作として案内) |
| 照合コードを人が誤編集 | チェックk4で検出 |
