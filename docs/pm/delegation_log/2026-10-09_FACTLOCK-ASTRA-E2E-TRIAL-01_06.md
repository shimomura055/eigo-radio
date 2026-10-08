# 委任_06 FACTLOCK-ASTRA-E2E-TRIAL-01 Stage R(委任文全文)

管理ID: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_06(Stage R: 新6テーマのresearch→台帳→B3生成、旧4テーマの凍結台帳からのB3再生成、台帳スキーマ点検。API支出あり: **上限¥130**[見積: 新6 research+台帳+B3 約¥100、旧4 B3 約¥2、余裕込み]。超えそうなら残りを止めて報告)。日付 2026-10-09。並行して委任_05(runner実装、¥0)が走っている。**委任_05のファイル(`er052_factlock_astra_e2e_runner_01*.py`、`g0_dryrun/`、`pricing_snapshot.json`、routing contract)には触らない。** git commit時にindex.lockで失敗したら10秒待って最大5回再試行。

## ユーザー決定(2026-10-09)
- 新6テーマ(確定): (1) BYDが18万台超をリコール、ブレーキペダル部品の欠陥が原因 (2) USA TodayなどがOpenAIを著作権侵害で提訴 (3) 中央銀行の金利判断と住宅ローンへの影響 (4) 訪日外国人数が過去最高水準に (5) 動画配信サービスの値上げが続く (6) 半導体大手の決算とAI需要の行方。補欠: 第1 コーヒー価格の高騰、第2 最低賃金の引き上げ(台帳が育たないテーマの入替用。入替は「VERIFIED fact が3件未満」または research失敗の場合のみ、入替した事実を記録)。
- 旧4テーマ(META/ホルムズ/宇宙兵器/ミニバッグ)は凍結台帳を再利用し、B3だけ新規生成(D案)。researchは呼ばない。
- 全10記事のB3は、後続の注記(仕様v2)の入力になる。注記は本委任では行わない。

## 事前指定Read
DESIGN_E2E_01.md(v2 §2・§5・凍結入力)、B3_ANNOTATION_SPEC_v2.md §8、b3_annotation_check_01.py、er019 runner(L92 research分岐、出力形式)、gpt6_wiring_e2e_01/E2E_EVIDENCE.md・run_02起動コマンド、凍結台帳の所在(sha256照合)。

## 作業
1. topic文の起案(新6): 前回形式の英語topic文6本。BYD(183,211台・対象車種・製造期間・欠陥原因・安全リスク具体化)/USA Today(提訴段階、主体・主張・裁判ステータス)。`stage_r/TOPICS.md`に記録。
2. 新6のresearch→台帳→B3: Production経路(全段gpt-6-luna、web_search込み)、直列または最大2並列。出力 `stage_r/<slug>/`。費用記録。VERIFIED fact 3件未満なら補欠へ入替(第1→第2)。
3. 旧4のB3再生成: 凍結台帳(sha256照合)からB3段のみ。research非実行をログで確認(呼ばれたら即停止・報告)。旧B3との差分を簡潔に記録。
4. 台帳スキーマ点検(仕様v2 §8): 全10台帳でnumeric_value/date_or_period欄の有無、量を示す語があるのに欄が無い記録、VERIFIED件数を表に(`stage_r/LEDGER_SCHEMA_CHECK.md`)。欄が無い台帳は代替規則の適用対象として明記。
5. 凍結: 全10テーマの台帳・B3 md・JSONのsha256(LF正規化後)を `stage_r/FROZEN_INPUTS_SHA256.json`。
6. 費用集計: テーマ別・段別(登録単価×実測トークン、web_search call課金込み)を `stage_r/COST_STAGE_R.md`。

## 禁止事項
Astra呼び出し禁止。Writer段以降は実行しない。注記は行わない。既存コード・Prompt・SSOT本体(CURRENT_SPEC.md/OPEN_ITEMS.md)の編集禁止。上限¥130超過禁止。1テーマで¥30超なら当該テーマを止めて報告。未確認数値を確定値として書かない。

## 記録・Git
委任文全文を本ファイル、check結果、最終報告を `_06_result.md`(RESULT_PACKET.mdは使わない)。DECISION_LOG.mdには触らない。docs/pm/REPORT_LEDGER.md 1行。commitはstage_r/配下と委任記録だけを明示的にgit add、push、hash+raw URL報告。

## 報告形式(result.md)
1 テーマ別結果表 / 2 旧4のB3再生成結果 / 3 台帳スキーマ点検要約 / 4 凍結sha256ファイルパス / 5 費用合計と所要時間 / 6 未確認・Fable判断要
