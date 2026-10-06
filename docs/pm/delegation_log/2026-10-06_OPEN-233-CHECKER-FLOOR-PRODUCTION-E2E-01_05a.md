## 管理ID

OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01(委任_05a: 新仕様E2E実行script_02の並行作成[3プロセス並列対応]。実装委任_04と並行。¥0)。並行タスク: 委任_04(runner/coverage_checker/新module `er052_open233_stage1_reclassify_01.py`/テスト/SSOTを編集・commit中)。**本委任は委任_04が編集中のファイル(runner・coverage_checker・reclassify module・テスト・SSOT・REPORT・ACTIVE_TASK・RESULT_PACKET)を編集しない。git操作もしない。** 書き込み先: `er052_output/open233_prod_e2e_01/e2e_run_02.py`(新規)、同`e2e_merge_02.py`(新規)、同`E2E_RUNBOOK_02.md`(新規)、`docs/pm/RESULT_PACKET_E2E_PREP.md`(新規)、`docs/pm/delegation_log/`。

**作業方式(必須)**: `Write`/`Edit`で小分け(1回40行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを2〜3分割して逐語保存。説明は最小限。

## 性質/到達上限Status/禁止事項

- 性質: E2E実行ツール作成(¥0、有料実行はしない)。到達上限: scriptのdry-run(`--dry-run`で構成assert・run一覧・予算配分の表示まで)成功。
- 前提インターフェース(委任_04で実装中、名前固定): runnerに`OPEN233_APPROVED_FLOW_SWITCHES`(dict)と`apply_open233_approved_flow_switches()`(適用関数、適用後の値をdictで返す)が新設される。scriptはこれを呼び、E2E開始前に主要スイッチ(`FLOOR_MODE=number_only`、`FLOOR_VERIFY_MODE=off`、`CAUSAL_FLOOR=False`、`STAGE2_DOWNGRADE_VERIFY=False`、`TIER0_G_L_ENABLED=False`、`STAGE1_RECLASSIFY=on`、precheck=number_only)をassertし、dumpをrun出力dirへ保存する。実装側の実名が異なる場合に備え、スイッチ名は1箇所の定数表にまとめ、起動時に`hasattr`で存在確認して不一致を明示エラーにする(黙って旧挙動で走らない)。
- 禁止: 有料API実行/runner・checker・テスト・SSOTの変更/旧E2E出力dir(`er052_output/open233_e2e_acceptance_01/`)への書込/独自の停止条件追加(技術障害・1 run¥20超abort・プロセスCap以外で止めない)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 非該当(実行ツール。構成は承認済み定数を参照するのみ)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果をRESULT_PACKETへ1行記録する(FAILでも作業は継続)。
T-2: TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。本委任はTTSなし。T-2追記: TTS実行前4点確認。本委任はTTSなし。
T-3: 本委任は¥0のためCap定型文は適用対象外。有料実行時(委任_05b)のCapは本script内の`--budget-jpy`(プロセス別)で実装する。

## ユーザー指示(原文、要点)

> 旧仕様で完了済みの9 runは、新仕様の正式Evidenceには使用しない。新仕様で20 runを最初からやり直す。今回はまず、新仕様 9/20 runまで実行 → 集計 → 報告で一旦区切る。
> 9 run中のSTOPルール: 品質問題・重大Fact見逃し・Human Reviewが発生しても、そこでSTOPしない。9 runは最後まで走らせ、結果をまとめて報告すること。問題を見つけても、その場で勝手に仕様変更・Prompt変更・追加対策を実装しない。ただし、API障害・実行不能・データ破損など、物理的に9 runを継続できない技術障害だけは例外として報告する。
> Fable判断: 9 runは3プロセス並列(instanceを3分割、budget stateを分離し後で合算)で実行してよい(条件は同一、順序依存なし)。1 run¥20超は当該runをabort記録して次へ継続。全体Guardrail¥60相当(プロセス別Cap合計)。

## KPI provenance欄

本委任は¥0(dry-runのみ)。E2E本実行(委任_05b)はfresh・Production初回path含む=Yes。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

1. `docs/pm/plan_open233_checker_floor_production_e2e_01.md`: Grep `E2E|script_02|run構成|順序|9 run|budget` →§4 E2E計画のみ(20 run構成と最初の9 runのinstance一覧・順序)。
2. 旧E2E script(Globで特定: `er052_output/open233_e2e_acceptance_01/*.py` または root `er052_*e2e*.py`): Grep `def main|add_argument|run_instance|budget|skip|apply_kpi_trial_switches|waste|post_run` →引数・run_instance呼び出し・予算・skip existing・停止条件の範囲のみ(踏襲する部分と変える部分を明確化)。
3. runner `er052_open233_self_recovery_flow_runner_01.py`: Grep `def run_instance|def apply_kpi_trial_switches|KPI_TRIAL_SWITCHES|budget_state|cost_jpy|def load_instance|SC_IDS|INSTANCE` →run_instanceの引数・戻り・費用記録・instance定義の範囲のみ(委任_04が編集中のため、読むだけ。関数名の最新は完了後に再確認する前提で、不一致時は明示エラー)。
4. `docs/pm/RESULT_PACKET_AGG.md`: Grep `引継ぎ|MISSING|追跡ID|Recheck` →集計側が必要とするrun jsonフィールド(claim追跡ID・最終cycle Recheck結果・再分類前後)。scriptはrun jsonをそのまま保存し、集計で不足する項目は「run jsonに無ければ集計でMISSING」の方針を踏襲(runner側の追加は委任_04/05bで判断)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 9 runのinstance一覧: 計画doc §4に従う(旧E2Eの最初の9 run=非SC 8+neg7等、計画docの記載を正とする)。3分割はrun時間の均等化を考慮(旧実績のrun別所要秒が`e2e_stop_analysis`/旧aggregateにあればGrep `elapsed|seconds|秒`で参照)。
- 追記位置: 新規ファイルのみ。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_05a.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_05a.md_check.json`
2. `e2e_run_02.py`(新規)仕様: 引数 `--out-dir er052_output\open233_prod_e2e_02\runs`(新dir)、`--instances <comma list>`(このプロセスが担当するinstance)、`--worker-id <n>`、`--budget-jpy <プロセスCap>`、`--run-cap-jpy 20`、`--yes-run-paid`、`--dry-run`、`--phase first9`(9 runの既定一覧を3分割する補助: `--worker-id 1/2/3`で担当を自動決定)。動作: 開始時に`apply_open233_approved_flow_switches()`→assert→`approved_switches_dump_worker<n>.json`保存→各instanceを`run_instance`で実行→run jsonを`runs/<instance>.json`へ保存→プロセス別`budget_state_worker<n>.json`に累計費用・run別費用・経過秒を記録。停止条件は(i)例外・API障害(当該runをfailed記録、2回まで再試行後に次へ)、(ii)run費用>`--run-cap-jpy`(abort記録して次へ)、(iii)プロセス累計>`--budget-jpy`(残runをskipped記録して終了)のみ。Human Review・STAGE4・waste flag・品質問題では止めない(記録のみ)。skip existingは既定off(新仕様でやり直すため)、`--resume`指定時のみ既存run jsonをskip。
3. `e2e_merge_02.py`(新規): 3プロセスの`budget_state_worker*.json`とruns/を合算し`e2e_summary_02.json`(run別費用・合計・平均・failed/aborted/skipped一覧・worker別経過秒)を出力。
4. `E2E_RUNBOOK_02.md`: 実行手順(3プロセスの起動コマンド実値: worker1/2/3の`--instances`と`--budget-jpy 20`、PowerShellでの並列起動例`Start-Process`または3つの別ターミナル、完了待ち、merge、集計script `aggregate_report_abcde_01.py --runs-dir er052_output\open233_prod_e2e_02\runs --out-dir er052_output\open233_prod_e2e_02\report`の呼び出し)、レート制限に当たった場合の逐次fallback手順、技術障害時の報告項目。
5. dry-run: `.venv\Scripts\python.exe er052_output\open233_prod_e2e_01\e2e_run_02.py --out-dir er052_output\open233_prod_e2e_02\runs --phase first9 --worker-id 1 --budget-jpy 20 --run-cap-jpy 20 --dry-run`(worker 2/3も同様)。委任_04未完了で`apply_open233_approved_flow_switches`が無い場合はdry-runが「インターフェース未検出」で明示エラーになることを確認し、その旨を記録(正常)。
6. git操作なし。

## SSOT追記文

なし。

## Git

git操作なし。SSOT編集権なし。成果物一覧をRESULT_PACKET_E2E_PREPに列挙(後続commit対象)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_E2E_PREP.md`へ: 1. T-0結果。2. scriptの引数・停止条件・記録項目の一覧。3. 9 runの3分割案(instance別・旧所要秒ベースの均等化)。4. dry-run結果(インターフェース検出可否)。5. 委任_04完了後に確認が必要な点(関数名・スイッチ名・run_instance引数)。6. 一覧外Read理由。7. 成果物一覧。最終報告は10行以内。
(注: 本ファイルは受領文の逐語保存。固定ブロック中のT-0/T-2/T-3の括弧内の参照ID文言のみ圧縮)
