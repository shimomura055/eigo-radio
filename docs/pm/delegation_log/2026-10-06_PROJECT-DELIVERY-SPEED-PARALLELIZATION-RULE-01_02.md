## 管理ID

PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01(委任_02: Fable判定「PRODUCTION_WIRED」の記入のみ。¥0)。並行タスク: OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 委任_05b(E2E実行中、`er052_output/open233_prod_e2e_0*/`・`OPEN_ITEMS.md`・`ACTIVE_TASK.md`・`RESULT_PACKET.md`を編集・commit予定)。本委任はそれらを編集しない・addしない。`git commit`でindex.lock競合時は5秒待って最大3回再試行。

**作業方式**: `Edit`で小分け、Bash heredoc不使用。T-0の委任文保存はWriteで逐語保存(短いので1回)。

## 性質/到達上限Status/禁止事項

- 性質: 記録のみ。Status: **PRODUCTION_WIRED**(Fable判定2026-10-06。根拠: 受入条件9項目充足、正本PM_GOVERNANCE 8-X-7〜12、逐語原文DECISION_LOG、CLAUDE.md/PM_BRIEF/テンプレート反映、commit 103e80f4 push済み、Dangling Referenceなし、参照可能)。
- 禁止: 上記以外の変更/`git add -A`・`stash`・`amend`/`ACTIVE_TASK.md`・`RESULT_PACKET*.md`のadd。
- 費用: ¥0。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力は`--porcelain`/`--short`で最小化。F-1: transcript退避不要。T-1: 事前指定Read/Grep一覧に従う(一覧外は理由を記録)。T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2(2026-09-25): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`明示。本委任はTTSなし。T-2追記(2026-09-25、7-5): TTS実行前4点確認。本委任はTTSなし。T-3(2026-09-26): ¥0のため適用対象外。

## ユーザー指示(原文)

> 今回の作業で、SSOT反映/Decision Log反映/必要な運用文書更新/Git commit/push/実際に次の開発指示/運用で参照可能な状態、まで確認して、初めてPRODUCTION_WIREDとする。

## KPI provenance欄

該当なし。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

1. `DECISION_LOG.md`: Grep `PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01` →該当エントリの「Fable判断」欄の位置(±5行)。
2. `docs/pm/REPORT_LEDGER.md`: Grep `PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01` →該当行。
3. `docs/pm/PM_GOVERNANCE.md`: Grep `^\*\*8-X\.` →見出し行のみ(Status注記の追記位置)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `DECISION_LOG.md`該当エントリの「Fable判断」欄へ記入: 「Fable判断(2026-10-06): PRODUCTION_WIRED。根拠: 受入条件9項目充足(正式ルール記録=PM_GOVERNANCE 8-X-7〜8-X-12/開始時の時間見積・並列化検討必須=8-X-7・22節項目4・D-2・テンプレート性質欄/独立作業の原則並列化=8-X-8/直列化理由の明示=8-X-9/Quality・Safety・PM Gate不緩和=8-X-10/Decision Log更新済み/commit 103e80f4 push済み/Dangling Referenceなし[4項目OK]/CLAUDE.md・PM_BRIEF・テンプレートから8-Xへ到達可能)。既存2026-09-27並列実行原則を拡張統合、重複文書なし、重大矛盾なし。8-X-8〜10は要旨、逐語原文は本エントリ。」
- `docs/pm/REPORT_LEDGER.md`該当行の「Fable判定: [記入]」を「Fable判定: PRODUCTION_WIRED(2026-10-06)」へ置換。
- `docs/pm/PM_GOVERNANCE.md` 8-X見出し行の直後(または同見出し内)に「Status: PRODUCTION_WIRED(2026-10-06、Fable判定、DECISION_LOG同管理ID参照)」を1行追記。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01_02.md --json-out docs\pm\delegation_log\2026-10-06_PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01_02.md_check.json`
2. 上記3箇所のEdit。
3. `git status --porcelain`→明示add→commit→push。

## SSOT追記文

上記のとおり。

## Git

明示add対象のみ: `DECISION_LOG.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/PM_GOVERNANCE.md`、`docs/pm/delegation_log/2026-10-06_PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01_02.md`(+`_check.json`)。
コミットメッセージ: `PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01: Fable判定=PRODUCTION_WIRED(受入条件9項目充足、Dangling Referenceなし)を記録(委任_02、¥0)`
SSOT編集権: あり(上記3ファイルの該当箇所のみ)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_RULE.md`末尾へ: 1. T-0結果。2. 記入箇所。3. commit hash・push結果。最終報告は5行以内。
