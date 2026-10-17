# 委任文(DELEGATION_STANDARD_TEMPLATE準拠)

## 管理ID
FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01 委任_01(略称BAPE。新規Family X記事「退屈と攻撃性」正式Production E2Eの**事前準備のみ**: ユーザー指示原文保存、開始条件・流用禁止の確認、実行計画、工程別費用見積、当日残額。**JPY0・有料実行なし・git書込みなし**)。本日=2026-10-17(JST)。

## 性質/到達上限Status/禁止事項
- 性質: read-only調査+計画書作成(新規ファイルの作成は可、git add/commit/pushは不可)。
- 到達上限Status: `E2E_PLAN_READY_PENDING_S3_WIRED_AND_COST_APPROVAL`。
- 禁止: 有料API(Research/Writer/TTS/ASR等)一切/Production code・Prompt変更/SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`REPORT_LEDGER.md`/`USER_DECISION_REGISTER_01.md`)編集/`docs/pm/ACTIVE_TASK.md`編集/git書込み(並行中のS3W 委任_03がcommit予定。「commitを伴う作業は同時に1件のみ」)/S3W・RLCT関連pathへの書込み/テーマの変更・具体化(研究結果・因果関係を事実として固定しない)/Research/Ledgerコスト改善方式(検索上限・Select-then-Verify)の適用。
- 費用: JPY0。
- 並行タスク: S3W 委任_03(Production配線・実走・commit中。`er019_family_x_style_profile_01.py`・runner・test・`er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3prod/`・`user_test/coffee_fxpw_e2e_01_s3prod/`・SSOTを編集中)。これらは**読取のみ可(編集不可)**。style profileの読取は「現時点の値」であり、S3W完了後に再確認が必要と計画書に明記。
- Opus Gate(11-3): 非該当(既存正式経路の実走計画)。
- 時間見込み: 45分、単独。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1/D-1/G-1/F-1: 同一task内再読禁止、Grep→範囲Read、git出力最小化、transcript退避不要。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し`check_delegation_prompt.py`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。
T-2: TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示(本委任は計画のみ。計画書内の全TTSコマンドに明示する)。
T-3: 本委任は費用上限JPY0のためCap定型は該当なし(計画書内に後続委任用のCap定型を記載する)。
T-0補足(厳守): (a)本委任文は全文を本ファイルへ保存。(b)「ユーザー指示(原文)」節を`..._USER.md`へ一字一句保存し、文字数・sha256を記録。`python`shimは壊れている(rc=49)ので `.venv\Scripts\python.exe` を使う。

(注: 本ファイルは委任文の要点節を保存。ユーザー指示原文は`2026-10-17_FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01_USER.md`に全文あり。以下の節は委任文原本から転記。)

## ユーザー指示(原文)
→ `2026-10-17_FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01_USER.md`(全文・逐語)

## KPI provenance欄(24節)
見積: `manual_substitution`(Coffee run_fxpw_01 実測の転用)。E2E自己確認: 該当なし(計画のみ)。

## Opus台帳更新
該当なし。

## 事前指定Read一覧
1. `docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/COFFEE_E2E_PLAN_01.md` §2と「§実行直前チェック」「§実走記録(委任_06)」。BAPEの工程・コマンドの雛形。
2. `er019_output/coffee_prices/run_fxpw_01/cost.json` と `.../coffee_prices__run_fxpw_01/audit/cost_by_stage_e2e_06.json`(工程別実測)。
3. `er019_output/coffee_prices/run_l3_01/entry_point.json`(Grep `theme`)→ `--theme`書式。
4. 既存の「退屈と攻撃性」関連: Grep `退屈|boredom|Boredom|aggression` を `OPEN_ITEMS.md`・`DECISION_LOG.md`・`docs/pm/USER_DECISION_REGISTER_01.md`・`er019_output/**/entry_point.json` → 原文引用、過去run/Trial成果の有無(流用禁止対象)。
5. `docs/pm/PM_GOVERNANCE.md` Grep `7-7|7-9|13-|^## 13`(今回はユーザー指定テーマ=選定不要であることを記録)。
6. `er019_family_x_style_profile_01.py` Grep `DEFAULT_NEW_RUN_PROFILE|PROFILE_FX_2026`(読取のみ。S3W完了後の値を実走前に再確認する旨を明記)。
7. 本日費用: `er057_output/ja_support_calm_style_trial_04/cost_actual_01.json`、`.../coffee_prices__run_fxpw_01_s3_support_01/cost_actual_01.json`、S3W 委任_03の新run `.../coffee_prices__run_fxpw_01_s3prod/cost.json`(存在すれば読取のみ)。

## 計画書(新規): `docs/research/FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01/E2E_PLAN_01.md`
1.開始条件チェックリスト(§2の7項目) 2.テーマ文字列案・slug `boredom_aggression`・out-dir `er019_output/boredom_aggression/run_bape_01`・既存dir非存在確認 3.工程表S0〜S11(Coffee計画転用、run-label `BAPE-E2E-01`、全TTSに`TTS_EXECUTION_MODE=STANDARD`、Mandatory STOP明記、`--tts-backend`省略) 4.仕様照合表(§5の11行、S3は`audit/style_profile.json`のSUPPORT_JA sha `060c08fd…`) 5.流用禁止担保 6.費用見積(上限JPY165案、text `--budget-jpy 110`/audio `--budget-jpy 70`、7-7判定=ユーザー個別費用承認要、Coffee 205枠流用不可) 7.本日使用済み・残額 8.STOP条件・CP-A〜F 9.報告様式。

## 実行コマンド全文
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <本ファイル> --json-out <本ファイル>_check.json`
- 既存dir確認、STOP確認(`tools/stop_scope_check_01.py --managed-id FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01 --run-dir er019_output/boredom_aggression/run_bape_01`)。
- 有料コマンドは実行しない。git書込みなし。

## SSOT追記文
(編集権なし。文案のみ: DECISION_LOG/OPEN_ITEMS(新規候補 BAPE Status=PENDING_S3_WIRED_AND_COST_APPROVAL)/REGISTER(#106 BAPE費用承認: 上限165案)/REPORT_LEDGER行/ACTIVE_TASK行。)

## Git
本委任ではgit書込みを行わない。RESULT_PACKETにcommit対象一覧とcommit message案を記載。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_BAPE1.md`(15行程度): T-0 2行/開始条件の現状/テーマ文字列案・slug・out-dir・既存dir非存在/過去記録(原文引用)と流用禁止対象/工程別見積表と7-7判定・承認案/本日使用済み・残額/仕様照合表要点/commit対象一覧・SSOT文案/4行/`判定整合:`行/判断候補(#106 費用承認のみ、D区分)。
