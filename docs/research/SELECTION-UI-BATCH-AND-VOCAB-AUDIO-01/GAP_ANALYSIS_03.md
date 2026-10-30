# GAP_ANALYSIS_03 — OPEN-620 選定UI未達の照合調査(委任_03、API 0、公開物の変更なし)

基点: origin/main ff84fdb7d。再取得: `gap03_probe.py`(公開・無改変)/`gap03_probe2.py`/`gap03_probe_batch.py`(公開JS・dataをそのまま使い`articles.json`だけroute差替でbatch付与)/`gap03_er128_accept.py`。証跡: `gap03_result*.json`、`gap03_batch_copy_{pc,mobile}.txt`、`gap03_shots/`。ユーザー原文: `docs/pm/delegation_log/2026-10-30_SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01_USER_02_REOPEN.md`(以下「再開原文」)、当初=`..._USER.md`(以下「当初原文」)。

## 1. 結論(一言)
実装(form_logic.js/index.html/er128 restore_batch)は**ほぼ当初要求どおり作られ、batchキーを与えれば14セットで全機能が動く**(下記5)。しかし**公開データ(articles.json)にbatchキーが一度も入らず**、公開ページは従来の単体画面(全35枠・Done/コメント欄/一括コピー無し)のままだった。02Aは「batch無し=従来画面(fail-closed)」を**合格**と記録し、公開で一括機能が使えないことを未達と扱わなかった。Fable受入はWorker報告の照合のみで、公開URLの実操作を欠いた。

## 2. 当初要求(当初原文)の項目化
| ID | 要求 | 当初原文 |
|---|---|---|
| R1 | 対象記事数に応じ動的表示(9固定でない) | :51-57 |
| R2 | 全体進捗/記事・レベル一覧(Done/未完了識別・クリックで切替・未完了へ移動)/選択中1セットのみ編集 | :62-84 |
| R3 | セット別Done(条件充足時のみ・具体エラー・変更で自動解除・切替で保持・リロードで失わない) | :86-98 |
| R4 | 全Done時のみ一括コピー1回で全セット(記事/レベル識別・①②③・文法・フレーズ/単語コメント)を1データに。未完了=コピーせずエラー(未完了の記事名・レベル、直接移動)。成功表示。既存Claude受入形式互換 | :100-126 |
| R5 | フレーズ欄直下/単語欄直下に独立コメント欄(任意・空欄でDone可・区分判別可・既存コメント意味維持) | :128-139 |
| R6 | ①ちょうど3件/残りすべて選択 | :143-185 |
| R7 | PC/スマホ・公開ページでの実操作検証(再開原文§4/§6) | 再開原文:§4,§6 |
再開原文§3①「過去記事を混在させない・報告単位で管理」は当初原文に**明文なし**(当初は「対象バッチ」=DESIGN_01.md:17で『Fableが書出し時に指定』と設計)。ただし当初原文:51-57の「実際の対象記事数に応じ動的」は対象絞込みを前提にしており、**同趣旨の要求**。

## 3. 実装(origin/main)
- form_logic.js: KP_EXACT=3(:6)、SIG_VER(:371)、sanitizeComment(:383)、composeComment(:390)、doneSig(:402)、doneErrors(:411)、doneStatus(:423)、selectRemaining(:431)、batchSets(:447)=**`articles.json`の任意キー`batch`が無いと`null`**、batchCopyErrors(:456)、buildBatchReadable(:475)。
- index.html: 一括UI(batchTop :16、コメント欄`boxPhrase/boxWord` :19-20、doneBox :23、batchBox :25)は**すべて`BS`(=batch有)でのみ表示**(:95 `hidden=!BS||!d`、:96、:76 `if(!BS){doneBox.hidden=true}`、:84 `if(!BS){restRow.hidden=true}`、:277 `BS=FL.batchSets(IDX)`)。batch無しの画面=従来の全記事セレクト+「選定結果をコピー」(1セット)。
- 一括の出力: `export_form_data_01.py --set-batch`(`write_batch_key`:304、articles.jsonの`batch`だけ書換)。受入: er128 `restore_batch`(:661)/`confirm-batch`(:833)。
- **公開データ**: `git show origin/main:user_test/selection_form_v3/data/articles.json` に`batch`キーなし(キー=schema,note_ja,default,articles。`git log -S'"batch"'`の履歴は一時表示用エントリの別件のみ=本機能で書かれたことが一度もない)。`default`=`monkeys_paw__b1b`(旧記事)。

## 4. 公開ページ実操作(Playwright、`https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/index.html`、PC1280x900/mobile390x844 touch。`gap03_result.json`/`gap03_result2.json`)
| 観測 | PC | mobile |
|---|---|---|
| 記事セレクトの選択肢数 | **35**(旧記事・未登録枠・ui_checkダミー含む、重複名なし) | 35 |
| `BS`(batch)/`IDX.batch` | null / false | null / false |
| 進捗・記事一覧・次の未完了・Doneボタン・一括コピー欄(batchTop/batchBox/doneBox) | **すべて非表示** | 非表示 |
| フレーズ/単語コメント欄(boxPhrase/boxWord) | **非表示** | 非表示 |
| 残りをすべて選択 | 非表示 | 非表示 |
| 「選定結果をコピー」 | 表示。対象=**選択中の1セットだけ**(単体コピー、AIF1コード1個) | 同(未選択時は「選定結果がありません」) |
| 初期表示 | `monkeys_paw__b1b`(旧記事) | 同 |
| 切替で入力保持 | 単体画面でもlocalStorage保持(`eigo-kp-form-v3`、PASS) | 同 |
| `?batch=`パラメータ | **未対応**(batch指定はarticles.jsonのみ) | 同 |
スクリーンショット: `gap03_shots/live_{pc,mobile}_{top,full}.png`、`live_pc_classic_after.png`。→ ユーザーの観察(過去全記事が表示/一括・Done・コメント欄・一括コピーが無い)と**完全一致**。

## 5. 「batch付与時の同じ公開コードの挙動」(実装の実在証明、`gap03_probe_batch.py`、28チェック全PASS)
公開JS/HTML/dataは無改変・articles.jsonのみroute差替でbatch(7記事×2=14セット)付与。PC/mobile各: 一覧14チップ(対象外セット非表示)・進捗`Done n/14`・コメント欄が`candPhrase→boxPhrase→candWord→boxWord→全体コメント→Done→一括コピー`の順(y座標昇順)・全14セットを3KP+文法+コメントでDone・切替でコメント保持・未Doneでの一括コピー拒否(未完了列挙)・全Done後1回で14セット(`════ SET i/14`×14、END行`BATCH1-14-<sha10>`)・フレーズ/単語コメントがセット別に重複なく含まれる・Done後編集で自動解除+再コピー拒否・pageerror 0。`gap03_batch_copy_{pc,mobile}.txt`を`er128.restore_batch`へ → **14セット全件受入**(`gap03_er128_accept.py`)。スクショ `gap03_shots/inject_{pc,mobile}_{top,full}.png`。

## 6. 不一致表(分類と原因)
| 要求 | 分類 | 原因(file:line) | 02A/02B/Fable受入が見落とした理由 |
|---|---|---|---|
| R1 対象絞込み(再開①) | **実装済みだが未公開**(絞込みロジックはbatchSets :447に存在)+**仕様解釈の誤り**(batch無し時を全35枠フォールバック=過去記事混在を許容した) | articles.jsonにbatch未設定(`data/articles.json`)。index.html:277,282-284、form_logic.js:446-447のコメント「無ければnull…全35枠フォールバック」 | 02A RESULT_PACKET「公開: batchキーが無いため従来の単体画面(fail-closed)」と記録し合格扱い。DESIGN_01.md:17は「無ければdata有り全セットからダミー等除外」と書いたが実装は全35枠。公開状態=受入条件と見なさなかった |
| R2 一覧/進捗/Done | **実装済みだが未公開**(batch有で動作=5) | 同上、BSゲート index.html:16,76,95-96 | sub02a_verify_result_live.json は「batch absent→classic」をPASSとして記録。公開で機能が見えないことを未達としなかった |
| R3 Done管理 | **実装済みだが未公開** | 同上 | 同上 |
| R4 一括コピー | **実装済みだが未公開**(コード+er128受入は完成・5で全PASS)。公開では「選定結果をコピー」(1セット)のみ | 同上。さらに**batch供給経路が未運用**: `--set-batch`(export_form_data_01.py:344)を呼ぶ工程がPM_GOVERNANCE/各HR依頼手順(gen_hr.py等のタスク別ツール)に無く、02A/02B後のHR配信(FX4/雪女等)も`?a=`単体URLで提示 | 設計(DESIGN_01.md:17)は「Fableが書出し時に指定」としたが、Fableの運用手順・SSOT・Workerの委任文に落ちていなかった(grep: `set-batch`は02A/02Bの2 RESULT_PACKETのみ)。受入=Worker報告の照合のみで公開実操作を欠いた |
| R5 コメント直下 | **実装済みだが未公開**(BS時のみ表示、index.html:95)+**仕様解釈の誤り**(新機能をbatch限定に閉じ込めた。当初原文:128-139はフォーム全般への要求で、batch有無の条件は無い) | index.html:95 `$('boxPhrase').hidden=!BS||!d` | 同上。単体画面で出ないことを「M3 fail-closed」の副作用として受容した |
| R6 ①3件/残り全選択 | 一部**実装済みだが未公開**。①ちょうど3件はDone/一括コピー条件のみで単体画面の「選定結果をコピー」では強制されない(0件でもコピー可)。残り全選択はBS限定(:84) | index.html:84、form_logic.js:411-421 | 同上 |
| 報告単位の状態分離(再開①) | **未実装** | localStorageキー`eigo-kp-form-v3`(index.html:34)・状態キー`slug__level`(form_logic.js:74)が**全報告共通**。同じ記事が別報告に出ると状態・Doneが混ざる。batchは単一グローバルキー(1度に1報告、別報告の上書き) | DESIGN_01.md「対象バッチ」は単一キー前提。複数日・複数報告の並存を設計時に検討していない |
| 公開URL/URLパラメータ | **未実装** | `?batch=<id>`が無く、報告ごとのURLを提示できない(`?a=`のみ) | 同上 |
| R7 公開実操作検証 | **未実施**(受入側の不備) | sub02a_verify.py は fixture(route差替)で70チェック。公開は3チェック(HTTP200/batch無し=従来/JSエラー無)のみ | Fable受入基準に「公開ページでユーザーが操作できること」の実操作が無かった |
| Claude受領形式互換 | 実装済み・公開と無関係に**OK** | er128 restore_batch(:661)。5で14セット受入 | — |

## 7. 根本原因(3点)
1. **公開状態を受入条件にしなかった**: 「batch無し=従来画面」を安全側の合格として扱い、ユーザーが使う公開URLで機能が使えるかを確認しなかった(02A RESULT_PACKET 公開行、sub02a_verify_result_live.json 3チェック)。
2. **batch供給が運用に接続されていない**: 対象セット指定(`--set-batch`)→公開→報告URL提示という手順の責任者・工程・点検がどのSSOT/委任にも無い。報告ごとのHR依頼書生成も各タスク別ツールで、共通入口が無い。
3. **設計が「単一グローバルbatch+機能のbatch限定」**: 報告単位の分離(状態名前空間・複数batch並存・URL指定)が設計に無く、新機能(コメント直下・Done・残り全選択)を非batch画面に出さない構造だったため、batch未設定=すべて使えなくなる単一障害点になった。

## 8. 11-8線引き
本不一致は「承認済み要求(当初原文)と実装/公開の矛盾」=不具合(PM_GOVERNANCE 11-8)であり、新仕様ではない。是正は委任範囲内。新仕様候補なし(再開原文は当初要求の再確認)。
