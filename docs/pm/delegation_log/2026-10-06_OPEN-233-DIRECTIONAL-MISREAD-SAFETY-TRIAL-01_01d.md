## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01(委任_01d: ACTIVE_TASK更新+副産物2件の別管理ID起票)。並列委任_01a/01b/01cが`er052_output/open233_directional_misread_trial_01/`と新規scriptを作成中。**書込先は`docs/pm/ACTIVE_TASK.md`、`OPEN_ITEMS.md`(2項目追加+1項目進捗)、`docs/pm/RESULT_PACKET_TRIAL_01D.md`、`docs/pm/delegation_log/`のみ。git操作なし。**
作業方式: Editは1回30行以内、Bash heredoc不使用、説明最小。T-0は委任文をWrite+Edit追記で逐語保存。時間目安15分。

## 性質/到達上限Status/禁止事項
性質: SSOT起票・一時ファイル更新(¥0)。禁止: 有料API/残11 run/Production変更/コード変更/「決定」の創作。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_01d.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、逐語)
> 管理ID: OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01。目的: ユーザー承認済みの設計案について、Production変更は行わず、限定Trialで有効性を確認する。残り11 E2Eは引き続き停止する。
> まず¥0で実施(Ledger全Fact数/状態変化Fact数/記事側確認件数/1 runあたり追加処理件数/コスト見込み)。費用: 限定Trial費用上限は¥15。¥0再集計後に、見積が¥15を超える場合のみSTOPして報告する。¥15以内なら追加承認を待たずTrialまで進めてよい。
> 比較: 同一model構成/Ledger側と記事側でmodelを分ける構成/blind分離あり・なし。モデル変更自体をProduction採用する判断は今回行わない。
> Production変更禁止: Production Checker変更/Production後段AI変更/既存floor復活/残11 E2E再開/KPI変更/gold変更/Human Reviewへの振替/Trial結果を根拠に自動でProduction採用。
> 副産物の不具合: 今回見つかった以下は本Trialと混ぜない。1. 数字floorの配線漏れ 2. 現在OFFのtwo_of_two系潜在不具合。それぞれ別管理IDで是正・Open Item管理する。承認済み仕様どおりに直すだけの実装不具合は通常是正として進めてよいが、本Trialの結果と混同しないこと。
> Trial終了時のStatus: VALIDATED/REJECTED/USER_DECISION_REQUIRED。VALIDATEDでもProduction採用ではない。残11 E2Eは、ユーザーが明示的に再開承認するまで開始しないこと。

## 作業内容
1. `docs/pm/ACTIVE_TASK.md` 全面更新(一時ファイル): 管理ID=OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01(進行中)/DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(設計=ユーザー承認済み・限定Trialへ)/CHECKER-FLOOR-PRODUCTION-E2E-01(9/20停止・残11待機・PRODUCTION_WIRED未)。Status=TRIAL進行中(Phase 0 ¥0)。予算上限¥15(超過見込み時STOP)。到達上限=VALIDATED/REJECTED/USER_DECISION_REQUIRED(Production採用不可)。禁止事項(上記逐語の要点)。UDR-blocking=残11 run再開はユーザー明示待ち。UDR-deferred=U2/U3/STAGE4(既存)。次アクション=Phase 0(01a母集団/01b対象セット/01c script)→見積→Trial実行→集計→SSOT→Closeout報告(11項目)。
2. `OPEN_ITEMS.md`: Grep `OPEN-233-DIRECTIONAL-MISREAD` →該当行へ進捗追記「2026-10-06 ユーザーが設計案(案E': Ledger側事前抽出→記事側blind抽出→機械比較)の限定Trialを承認(TRIAL-01、上限¥15、Production変更なし)」(表セル内、短く)。
3. `OPEN_ITEMS.md` 新規2項目(既存の行書式に合わせ、OPEN-233関連の直後に追加。ID番号は既存の最大番号+1、+2を採番。Grep `^\| OPEN-\d+` で最大番号を確認):
   - (a) 「数字floor配線漏れ: `number_not_in_fact`(checker L554-555)が候補flagsへ`changed_number`として反映されず(L640-643)、承認構成`FLOOR_MODE=number_only`の数字floorが発火しない。新9 runで実害0(`sensor_quality_01.md` D)。承認済み仕様どおりの配線是正(新floorではない)。是正時は¥0 replayで挙動差を確認し、TRIAL-01の結果と混同しない。Status: OPEN(未着手)。出典: 設計doc §13 #9、Opus OF-057」
   - (b) 「`apply_stage2_two_of_two`潜在不具合: `claim_identity`=`fact:<id>`(runner L1424-1429)をキーにするため同一factの兄弟文が上書きし合い、対象外BLOCKING claimまで降格し得る(L4106-4122)。現在`STAGE2_NORMAL_TWO_OF_TWO=False`(L430)で影響なし。再有効化の前提条件として修正要。Status: OPEN(再有効化前に是正)。出典: 設計doc §13 #8、Opus OF-056/057」
   行の文字数は各500文字以内。
4. `docs/pm/RESULT_PACKET_TRIAL_01D.md`: 変更箇所(行番号)、採番したID、T-0結果。

## 事前指定Read/Grep一覧
`docs/pm/ACTIVE_TASK.md` 全文(15行)。`OPEN_ITEMS.md`: Grep `OPEN-233-DIRECTIONAL-MISREAD|^\| OPEN-\d+` →該当行と最大番号行のみRead(全文Read禁止)。書式確認のため直近追加行1行をRead。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_01d.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_01d.md_check.json`

## SSOT追記文
上記2・3。

## Git
なし(Fableが後でまとめてcommit)。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_TRIAL_01D.md`。最終報告5行以内。
