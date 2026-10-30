# DESIGN_03 — 選定UI是正設計(委任_03、API 0、実装は次委任)

根拠: GAP_ANALYSIS_03.md(実装はbatch付与で動作=28チェックPASS。未達の主因=公開にbatch無し/供給経路未運用/単一グローバルbatch+機能のbatch限定)。原文=再開原文§3①〜④・§4・§5・§6。**選定基準・選定数・候補生成仕様・Production Prompt・Vocabulary音声・記事Production経路は変更しない**(再開原文§5)。

## 1. 設計方針(最小変更で未達を構造的に解消)
既存のform_logic.js(Done署名・①ちょうど3件・残り全選択・buildBatchReadable)と一括コピー形式(BATCH1/SET区切り、er128.restore_batch互換)は**そのまま再利用**する。変更は「対象セットの決め方」「状態の分離」「機能のbatch限定の撤廃」「供給+公開確認の工程化」の4点。

### 1-1 報告(batch)の定義と供給
- 新設 `user_test/selection_form_v3/data/batches/<batch_id>.json` = `{schema:"eigo_radio_batch_v1", id, date, report_ref, members:[<data stem>...], created}`。1報告=1ファイル(複数報告が並存・上書きしない)。membersは現行どおりdata stem(例 `moon_shrinking__b1b__prod`)。
- URL: **`index.html?batch=<id>`**(報告ごとの固定URL)。`articles.json`に新キー`batch_latest:"<id>"`を1つだけ追加(記事配列は触れない)。パラメータ無しの安定URLは`batch_latest`のbatchを開く(ユーザーは従来URLを開くだけ)。既存の`articles.json.batch`(02B契約)は後方互換で読む(新旧同時に有る場合は`?batch`>`batch_latest`>旧`batch`)。
- **batchが特定できない場合は記事を一切出さず**「対象の報告が指定されていません」+既知batch一覧のリンクのみ表示(全35枠フォールバックを廃止=再開原文§3①「過去記事を混在させない」。A既判断)。開発/テスト用の全枠表示は`?dev=all`のみ(リンクしない・赤い「開発用・報告対象外」帯を常時表示・テスト専用)。
- 画面に`batch.id`・日付・「対象N記事/Mセット」を常時表示(古い報告を誤って開いていることに気づけるようにする)。

### 1-2 状態の報告単位分離
localStorageキーを`eigo-kp-form-v3:b:<batch_id>`へ(旧`eigo-kp-form-v3`は読まず残置=別報告・旧テスト状態と混ざらない。移行なし=新報告は空から開始が正)。`loadAllState/saveSet/resetAll`の`STORE_KEY`を`storeKey(batchId)`へ置換(index.html:34,38,42,267,271)。Done署名(doneSig)は不変。リセットは「このbatchの全セット」のみに作用。

### 1-3 機能のbatch限定撤廃
batch画面=唯一の画面になるため、コメント欄(フレーズ/単語、`boxPhrase/boxWord`)・Done・残り全選択・一括コピーは**常に表示**(index.html:76,84,95,96のBSゲートが実質消える)。単体の「ChatGPTへ送信」「選定結果をコピー」「技術情報付きコピー」は一括画面に出さない現状を維持(`?dev=all`のみ従来動作、既存のform1 test/回帰互換)。

### 1-4 Done・進捗・移動・保持(既存実装を維持、不足のみ追加)
- Done=①ちょうど3件+文法決定+データ検証(doneErrors:411)、署名一致でDone/不一致=「要再確認」で自動解除(doneStatus:423)、コメントは任意で空でもDone可。維持。
- 進捗`対象記事N/セットM/Done n/M/バー`・記事行チップ(未完了/Done/要再確認)・「次の未完了セットへ」・未完了コピー拒否時の未完了一覧(記事名+レベル+該当セットへ移動ボタン)を維持。
- 追加(モバイル視認性、再開原文§4): 画面下部に**固定フッタ**(`Done n/M`・次の未完了へ・一括コピー)。一覧は折畳み。フォームは長い(mobileでword commentまで約2500px)ため、選択数カウンタ(stats)をsticky化。
- 記事/レベル切替での入力保持=edit()が即時localStorage保存(維持)。リロード耐性=維持。

### 1-5 コメント(再開原文§3③)
フレーズ欄直下・単語欄直下の独立欄+全体欄(`追加指示(全体)`)を維持。コピー内は各SETの「自由コメント：」に`【フレーズ】…`/`【単語】…`/`【追加指示(全体)】…`を行分けで格納(SETヘッダに記事名|レベル+照合コードのstemが付くため記事・レベル・区分が判別可能。AIF1 m8互換のため合成文字列形式は変更しない=Claude受領形式互換を維持)。区切り注入対策(sanitizeComment:383)維持。

### 1-6 一括コピー(再開原文§3④)
ロジック(buildBatchReadable:475・batchCopyErrors:456)は無変更。対象=batchの全セット、全Done時のみ有効、1クリックで1データ。形式=`BATCH_PREFACE`+`一括ヘッダ`(件数/生成/バッチid)+`════ SET i/N ｜ <stem> ════`×N+`════ END 合計N件 / BATCH1-N-<sha10> ════`(現行)。コピー成功の明確な表示(緑バナー)維持。クリップボード失敗時の手動コピー用textarea維持。

### 1-7 Claude側受領(er128、追加のみ)
`restore_batch`/`confirm-batch`に**batchファイル解決**を追加: 貼付ヘッダの`バッチ=<id>`から`data/batches/<id>.json`を読みmembers完全一致を検査(従来の`--articles-json`+`batch`キー経路も維持)。ファイル無し/id不一致/members不一致=fail-closed(何も確定しない)。既存`restore`/`cmd_from_readable`・単体経路は無変更(差分grepで確認)。

### 1-8 供給と公開の工程化(再発防止の核)
- 新設 `tools/publish_selection_batch_01.py`(新ファイル): `--id --date --report-ref --members stem,...`→(1)全membersのdata存在・`validateArticle`相当検査・重複/空拒否 (2)batchファイル書出し+`articles.json`の`batch_latest`のみ更新(CRLF保持・他キー不変、原子的書換) (3)`--push`で対象ファイルのみadd/commit/push (4)**live smoke(必須・失敗=URLを提示不可)**: 公開URL(`?batch=<id>`)が200になるまでpollし、Playwrightで「チップ数==members数/コメント欄2種可視/全枠35件が出ていない/pageerror 0/(任意でfixtureでなく実データの全Done→一括コピー→restore_batch受入)」を検査。結果JSON+URLを出力。
- 既存`export_form_data_01.py --set-batch`は互換維持(旧`batch`キー書出し)。新規はpublish toolを正規入口とする。
- 運用規則(Fableが採否判断・PM_GOVERNANCE/委任テンプレへ): ①HR依頼書・報告でユーザーへ出す選定URLは**必ず`?batch=<id>`のbatch URL**(`?a=`単体URLの提示禁止) ②選定UI関連の完了/受入は**公開URLでのlive smoke結果+実操作スクショ(PC/mobile)**を必須証拠とする(コード・fixture testのみでACCEPTEDにしない) ③`gen_hr*.py`等タスク別ツールがURLを組む場合はpublish toolの出力を使う。

## 2. 変更ファイル(実装委任の編集範囲)
| 区分 | ファイル | 内容 |
|---|---|---|
| UI | `user_test/selection_form_v3/index.html`、`form_logic.js` | batch解決(`resolveBatch(idx,params,batchDoc)`)、storeKey(batchId)、BSゲート撤廃、no-batch画面、sticky footer、`?dev=all` |
| data | `user_test/selection_form_v3/data/batches/*.json`(新)、`data/articles.json`(`batch_latest`キー追加のみ) | 並行Workerのarticles.json記事追記とは別キーで衝突最小 |
| 受領 | `er128_form_readable_restore_01.py`(追加のみ) | batchファイル解決 |
| 工程 | `tools/publish_selection_batch_01.py`(新)、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`(互換のみ・読取+必要最小の追加) | 本委任では読み取りのみだった。実装委任で編集 |
| test | `selection_form_logic_test_01.js`(追記)、新`sub03_verify.py`(Playwright E2E)、新`selection_form_live_smoke_01.py`、er128 batch-file test | 下記3 |
競合: ECH(er135/enduser_page_assets/user_test/*/enduser)・KPN5(er119/er138/routing)とは非重複。実装着手時に`git status`で再確認。

## 3. Regression(同一根本原因の再発防止)
1. **form_logicノードtest**(既存70件に追記): resolveBatch(優先順位・batch無し→sets 0=全枠フォールバック無し・不明id→エラー)、storeKey名前空間(別batchで同一stemの状態が混ざらない)、旧`batch`キー互換、BSゲート撤廃後のDone/コメント不変(既存70件が緑のまま)。
2. **Playwright E2E `sub03_verify.py`**(fixture+ローカル、PC1280/mobile390 touch): シナリオA(9記事×2=18セット: 18のみ表示・全セットDone→一括コピー1回で18 SET+全コメント・Done進捗・切替保持)、B(3記事・計5セット: 5のみ表示/集計/コピー)、C(未完了で一括拒否と未完了列挙+移動、Done後選定変更=自動解除、コメント編集=要再確認、記事・レベル切替保持、リロード保持、コピーの欠落・重複なし=SET番号連番・各コメントが1回のみ、別batch切替で状態分離)。
3. **公開live smoke `selection_form_live_smoke_01.py`**(publish toolが自動実行、単独でも実行可): 公開URLで上記の要点を実測(今回のgap03_probe群を恒久化)。**これが今回の見落とし(公開実操作)への直接の再発防止**。
4. **ガードtest**: (a) articles.jsonに`batch_latest`無し/不明id=記事選択UIが0件(py/Playwright) (b) HR依頼書・RESULT_PACKETテンプレにbatch URL欄 (c) er128 batchファイル経路の正常系/id不一致/members欠落・余剰/ファイル無し。
5. 既存回帰: form1_selection_form_v3_test_01(既存4件FAILは不変=OPEN-613)・er128 76件・node70件が悪化しないこと。Vocabulary音声/記事Production経路は編集範囲外(差分grepで0行を確認)。

## 4. 公開受入手順(実装委任の完了条件、再開原文§6)
(1)publish toolでシナリオA相当の実batch(今ある27実データ stem から14〜18セット)を公開→live smoke PASS (2)公開URLをPC/mobileでPlaywright実操作(全Done→一括コピー→クリップボード→er128 confirm-batch dry受入)、スクショ保存 (3)`?batch=<別id>`で別報告が混ざらないこと (4)Fable独立受入=公開URLを自分で開く。**ここまでをユーザー最終URL提示の前提**。テスト用batchは「テスト」と明記し、本番報告のbatch_latestを汚さない(検証後に実報告batchで`batch_latest`を更新、または検証用idは`batch_latest`に設定しない)。

## 5. 実装見込み
Sonnet 1委任(UI/logic 1.5h、publish tool+er128 0.5〜1h、test/E2E/live smoke 1.5h、並列化で約3〜3.5h)。**API費用0・追加量産単価0**。構造変更(batchファイル+名前空間+入口tool)を含むため、PM_GOVERNANCE 11-3条件A(新しい構造・処理フロー設計)に該当し得る=Opus独立レビュー推奨(Fable判断)。

## 6. 判断候補の整理(27-3)
| 事項 | 区分 | 根拠 |
|---|---|---|
| batch無し=記事を出さない(全枠フォールバック廃止) | **A既判断** | 再開原文§3①「過去記事を混在させない」 |
| 報告ごとのbatchファイル+`?batch=`+状態名前空間 | **B承認範囲内** | 再開原文§3①「対象範囲は報告単位で管理・別報告の選定状態と混同しない設計」 |
| パラメータ無し安定URL=`batch_latest` | B | 当初設計「ユーザーはURLを開くだけ」(DESIGN_01.md:17) |
| `?dev=all`(テスト専用全枠表示) | B | 既存回帰/QA維持。ユーザー導線に出さない |
| 規則(batch URL必須・live smoke受入必須)のSSOT化 | **Fable所管**(PM_GOVERNANCE/委任テンプレ)。ユーザー判断ではない | 受入側不備の是正 |
→ **D(真に新しい判断)なし。ユーザー判断候補なし。**
