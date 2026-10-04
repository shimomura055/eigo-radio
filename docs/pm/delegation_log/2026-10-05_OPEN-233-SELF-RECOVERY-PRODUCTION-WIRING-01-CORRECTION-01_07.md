# 委任_07 OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-01(全文保存)

## 管理ID
`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-01`(委任_07、親 `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`)。並行タスクなし。

## 性質/禁止事項
- 性質: ¥0・Status記録のみ(コード変更なし、有料APIなし)。委任_06の確定事実(rep30のStage 1は fresh 3 call[4 run]/frozen再利用31 run[gpt-6-luna、2026-09-29/30生成、V4A prompt+related_fact_id、列挙instruction・schema追加・重大誤解原則なし(原則なしは推測)]/V0差替え3 run[gpt-5.6-luna]。V0が検出していた6 claimのうち候補構成のfreshで検出されたのは0/6。B4 4件はfrozen由来、B2_hormuz 1件はV0差替え由来、A2A3 HF-009はrep30でも非検出)に基づき、ユーザー是正指示§5「rep30自体がその6件についてfresh Stage 1 Checkerを検証しておらず、reuseデータに依存していたため、Productionで使うStage 1 Checkerの正式仕様が未検証」=**Yes**と判定し、Production wiringの未充足事項としてSTOP、FableはユーザーへUSER_DECISION_REQUIREDで報告する。
- Fable判断(逐語記録): 「rep30でVALIDATEDされたのは『Stage 1出力を所与とした後段(Stage 2〜許可リスト出口)』であり、Stage 1 Checkerについては、Production初回pathで必ず発生するfresh実行の正式構成がrep30内で検証されていない(fresh 3 call、Safety群・B群・負例群では0件)。したがって『rep30構成の忠実なProduction再現』はStage 1に関して定義不能であり、Fable/Claudeが独自にChecker仕様を決めてProductionへ入れることは禁止されているため、ユーザー判断を求める。後段(Stage 2以降)の配線設計(Opus#15・Fable評価)はStage 1の決定後に有効。委任_05の比較(¥20.10)は是正指示後に停止しきれず完走した分を含み、Regression参考値として保存のみ、採否には使わない。」
- 禁止: コード変更禁止。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`PM_GOVERNANCE.md`は編集しない。`git add -A`/`stash`/`amend`禁止。既存M差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。1回の書き込みは2,500文字以下。
- T-0: 委任ログ(本ファイル)に本委任文を全文保存(分割)、check実行・結果記録。
- 固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## 作業
1. T-0。
2. `docs/pm/ACTIVE_TASK.md`: 固定ヘッダStatusを`USER_DECISION_REQUIRED`に。Fable判断(上記逐語)、ユーザー判断事項: (1)Production初回pathのStage 1 Checker構成をどう定めるか — 選択肢A: frozen生成構成(V4A prompt+related_fact_id、原則・列挙なし、gpt-6-luna)を正式仕様としてfresh検証Trialを限定実施(Safety-critical+B群+負例、約5〜8円)/選択肢B: 現行Production Checker V0(vfl01、gpt-5.6-luna)をStage 1とし、rep30後段を配線(組合せ未検証、限定確認約10〜15円)/選択肢C: 候補構成(V4A+原則+列挙)を正式仕様とする(Phase 1でB4 0/2のためFableは推奨しない)/選択肢D: 他(ユーザー指定)。(2)K7モデルrouting(選択肢(1)に従属)。(3)委任_05費用20.10円の扱い(記録のみ)。addしない。
3. `OPEN_ITEMS.md`: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`行Status→「USER_DECISION_REQUIRED(CORRECTION-01: rep30のStage 1はreuse主体でfresh正式構成が未検証=未充足。Stage 1構成のユーザー判断待ち。後段配線設計はOpus#15・Gap文書7節で準備済み)」。`REPORT_LEDGER.md`1行。
4. commit/push(明示add: `OPEN_ITEMS.md`、`REPORT_LEDGER.md`、委任ログ+check.json)。メッセージ: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-01: rep30 Stage 1のfresh正式構成が未検証(reuse 31/38・V0差替え3)=Production wiring未充足としてUSER_DECISION_REQUIREDでSTOP(委任_07、¥0)`

## 事前指定Grep/更新位置
ACTIVE_TASK.md固定ヘッダStatus行。OPEN_ITEMS.md Grep `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`の該当行Status欄。REPORT_LEDGER.md(docs/pm/)末尾1行。

## 報告(5行以内)
更新内容、T-0、commit hash、push、raw URL(OPEN_ITEMS)。

## 事前指定Read一覧
なし(Read対象は上記Grep/更新位置のみ)。

## SSOT追記先
OPEN_ITEMS.md(該当行Status)、docs/pm/REPORT_LEDGER.md末尾1行。CURRENT_SPEC/DECISION_LOG/PM_GOVERNANCEは編集しない。

## 実行コマンド全文
T-0 check:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-01_07.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-01_07.md_check.json

## Git(明示add対象・コミットメッセージ・trailer)
git status --porcelain -> 明示add(OPEN_ITEMS.md, docs/pm/REPORT_LEDGER.md, 委任ログ+check.json) -> commit(上記メッセージ+Co-Authored-By trailer) -> git push origin main -> git log --oneline -1
