## 管理ID
OPEN-242-BUDGET-GUARD-WEB-SEARCH-COST-GAP-FIX-01 委任_01(ユーザー指示「OPEN-242を修正してください。」2026-10-08)

## 性質/到達上限Status/禁止事項
Production修正(小規模)。到達上限Status: PRODUCTION_WIRED候補(Fable受入待ち)。禁止: git add -A・amend・rebase・force push。API課金なし、TTSなし(TTS_EXECUTION_MODE=STANDARD該当せず)。費用¥0。Opus独立技術レビューGate非該当。

## 固定ブロック
E-1 / D-1 / G-1 / F-1 / T-0 / T-2: TTSなし / T-3: 課金なし。
KPI provenance: reuse(既存raw_usage_log再計算)。Opus台帳更新: 該当なし(OPUS_FINDINGS_LEDGER対象外)。

## 事前指定Read一覧
OPEN_ITEMS.md OPEN-242行、er012_e...runner_01.py L100-150、er019...runner_01.py L235-280、pricing_snapshot.json web_search、er052_output/gpt6_wiring_e2e_01/run_02/raw_usage_log.jsonl・cost.json

## 事前指定Grep一覧+追記位置・更新位置の手順
Grep web_search。修正: ガード累計にweb_search_call課金加算(単価はpricing_snapshot既存、共通関数化、未登録fail-closed)。検証: run_01/02再計算でcost.json±0.5円。SSOT: OPEN_ITEMS/DECISION_LOG/REPORT_LEDGER/ACTIVE_TASK。

## 実行コマンド全文
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-08_OPEN-242-BUDGET-GUARD-WEB-SEARCH-COST-GAP-FIX-01_01.md --json-out docs\pm\delegation_log\2026-10-08_OPEN-242-BUDGET-GUARD-WEB-SEARCH-COST-GAP-FIX-01_01.md_check.json
.venv\Scripts\python.exe run_project_regression.py --pattern "er012*_test*.py"
.venv\Scripts\python.exe run_project_regression.py --pattern "er019*_test*.py"
.venv\Scripts\python.exe run_project_regression.py --pattern "er006*_test*.py"

## SSOT追記文
OPEN-242 Status更新、DECISION_LOGエントリ、REPORT_LEDGER 1行(本文はDECISION_LOG参照)。

## 報告(RESULT_PACKET項目)
問題・変更内容・検証値・テスト結果・リスク・commit hash。Git: 変更ファイルのみ明示git add、commit trailer付き。
