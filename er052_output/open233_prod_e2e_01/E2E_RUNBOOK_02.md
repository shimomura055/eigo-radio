# E2E_RUNBOOK_02 (OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 委任_05b用)

## 1. 事前確認(委任_04完了後)
- `git status --porcelain er052_open233_self_recovery_flow_runner_01.py`が委任_04のcommit済みであること。
- dry-run(3 worker全て、`¥0`)が成功すること:
  `.venv\Scripts\python.exe er052_output\open233_prod_e2e_01\e2e_run_02.py --out-dir er052_output\open233_prod_e2e_02\runs --phase first9 --worker-id 1 --budget-jpy 20 --run-cap-jpy 20 --dry-run`(2/3も)
- 「インターフェース未検出」「主要スイッチ不一致」が出たら実行せず報告(名前は`e2e_run_02.py`冒頭の`RUNNER_INTERFACE`/`REQUIRED_SWITCHES`の1箇所表)。

## 2. 3プロセス並列起動(有料。`--yes-run-paid`必須、プロセスCap各JPY20=合計JPY60)
worker別担当(旧実績wall秒で均等化。W1約1246秒/W2約1180秒/W3約1085秒):
- W1: neg1_meta_b3prod_a2, meta_run03_standard, hormuz_run03_standard
- W2: neg7_meta_prodrunner_b1b, meta_run03_advanced, hormuz_run03_advanced
- W3: bgroup_B3, neg3_hormuz_prodrunner_b1b, neg2_meta_refresh_a2

PowerShell(リポジトリroot):
```
$py = ".venv\Scripts\python.exe"; $s = "er052_output\open233_prod_e2e_01\e2e_run_02.py"
New-Item -ItemType Directory -Force er052_output\open233_prod_e2e_02\logs | Out-Null
1..3 | ForEach-Object { Start-Process -FilePath $py -NoNewWindow -ArgumentList "$s --out-dir er052_output\open233_prod_e2e_02\runs --phase first9 --worker-id $_ --budget-jpy 20 --run-cap-jpy 20 --yes-run-paid" -RedirectStandardOutput "er052_output\open233_prod_e2e_02\logs\worker$_.out.log" -RedirectStandardError "er052_output\open233_prod_e2e_02\logs\worker$_.err.log" }
```
(または3つの別ターミナルで同じコマンドを`--worker-id 1/2/3`で実行)

## 3. 完了待ち
- 各`budget_state_worker<n>.json`に`finished_at`が出れば完了(`logs\worker<n>.out.log`の末尾にもsummary行)。
- 途中中断した場合は同じコマンドに`--resume`を付けて再開(既存run jsonをskip、既定はskipなし)。

## 4. 合算と集計
```
.venv\Scripts\python.exe er052_output\open233_prod_e2e_01\e2e_merge_02.py --base-dir er052_output\open233_prod_e2e_02
.venv\Scripts\python.exe er052_output\open233_prod_e2e_01\aggregate_report_abcde_01.py --runs-dir er052_output\open233_prod_e2e_02\runs --out-dir er052_output\open233_prod_e2e_02\report
```
`e2e_summary_02.json`: run別費用/合計/平均/failed・aborted・skipped一覧/worker別経過秒。

## 5. 停止条件(これ以外で止めない)
(i)技術障害(API障害・例外): 当該runを2回まで再試行、なお失敗ならfailed記録(`failed_worker<n>_<id>.json`)して次へ。(ii)1 run費用>JPY20: abort記録(`runs/<id>.json`に`aborted`)して次へ。(iii)プロセス累計>`--budget-jpy`: 残runをskipped記録して終了。Human Review/STAGE4/waste flag/provenance違反/品質問題は記録のみ。

## 6. レート制限(429等)に当たった場合の逐次fallback
並列で429が続きfailedが出たら、全workerの終了後に未完了instanceだけを逐次実行する: `--instances <failed/skippedのid,...> --worker-id 1 --budget-jpy <残枠> --yes-run-paid`を1プロセスずつ(`--resume`併用)。逐次worker番号は未使用の4以降を推奨(budget stateが分離され、mergeが合算)。ただし`--phase first9`を使わず`--instances`で指定する。

## 7. 技術障害時の報告項目
障害種別(API/例外/データ破損)、発生worker・instance、再試行回数とエラー文(`failed_worker*.json`)、発生時点の累計費用(`budget_state_worker<n>.json`)、完了済みrun一覧、未実行instance、`logs\worker<n>.err.log`末尾。9 runは継続可能な限り最後まで走らせる(品質問題で止めない)。
