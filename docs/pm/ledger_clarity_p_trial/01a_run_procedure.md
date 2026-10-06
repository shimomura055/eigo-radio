# 01a P'実行手順書(Phase 1、有料実行は未実施・要承認。DEV/Trial専用、Production採用ではない)
前提: python=`.venv/Scripts/python.exe`(dotenv/openai/pytest入り)。Before topic=`Meta Muse AI電話代行「人間コンシェルジュ」実験`(er019 meta/run_03と完全一致、既定値)。

## 1 台帳段のみ(実行前に必ず--dry-runでprompt sha/構成確認、¥0)
```
OPEN233_RESEARCHER_VARIANT=pprime .venv/Scripts/python.exe er052_open233_ledger_clarity_pprime_dev_01.py --dry-run
OPEN233_RESEARCHER_VARIANT=pprime .venv/Scripts/python.exe er052_open233_ledger_clarity_pprime_dev_01.py --stage ledger --theme "Meta Muse AI電話代行「人間コンシェルジュ」実験" --slug meta --out-dir er052_output/open233_ledger_clarity_p_trial_01/after_pprime_01 --budget-jpy 60 --yes-run-paid
```
## 2 全連鎖(台帳→B3→JA→EN advanced。台帳段実費が¥40超なら後段へ続行しない=gated_ledger)
```
OPEN233_RESEARCHER_VARIANT=pprime .venv/Scripts/python.exe er052_open233_ledger_clarity_pprime_dev_01.py --stage advanced --theme "Meta Muse AI電話代行「人間コンシェルジュ」実験" --slug meta --out-dir er052_output/open233_ledger_clarity_p_trial_01/after_pprime_01 --budget-jpy 60 --yes-run-paid
```
注: 1と2は同じout-dirを使えない(M-b(4): research_ledger等が存在するとSystemExit。再利用を避ける設計)。台帳段だけで止めた後に続行したい場合は、別out-dir(例 after_pprime_01b)で2を実行するか、承認のうえ1を飛ばして2のみ実行する(推奨: 2のみ、台帳段で自動gate)。
## 3 Checker(After記事1 run、E2E_02同一スイッチ、`--budget-jpy 10`)
```
.venv/Scripts/python.exe er052_output/open233_ledger_clarity_p_trial_01/tools/run_checker_after_p01.py --after-dir er052_output/open233_ledger_clarity_p_trial_01/after_pprime_01 --out-dir er052_output/open233_ledger_clarity_p_trial_01/checker_after_01 --budget-jpy 10 --yes-run-paid
```
(事前確認: 同コマンドに`--dry-run`。入力=`<after>/research_ledger/verified_fact_ledger.txt`、`<after>/b1b/article.md`、`<after>/ja_writer/revision2.md`)
## 4 E2E state非混入の根拠
- er019 runnerはout-dir内にだけ書く(`cl.install(<out>/raw_usage_log.jsonl)` er019 L~303、`entry_point.json`等)。`attempt_history`の参照はer011_human_review_lock_01.py(L112)のみで、er019/er012/er003/er052 runnerのいずれにも無い(grep確認、本日)。
- Checker側: `runner.OUT_DIR`/`runner.BUDGET_STATE_PATH`/`TOTAL_BUDGET_JPY`を`checker_after_01/`配下へ上書き(e2e_run_02.py L165-167と同形)。E2E_02の`open233_prod_e2e_02/`やbudget_state_runner_worker*.jsonへは書かない。`open233_prod_e2e`/`open233_e2e_acceptance_01`を含むパスは拒否。
- Production file(er003/er012/er019/er052 runner/e2e_run_02.py)は無変更(git status空を確認)。差替えはプロセス内のみ(contextmanager、終了時復元)。
## 5 見込み費用(¥100上限案の内数、Phase 0実測ベース【推測】)
台帳段≈¥31(Researcher≈¥15+Verification≈¥14.5+P'増分¥1〜3) / 連鎖(B3+JA+EN)≈¥12 / Checker≈¥3.5 / 合計≈¥47。ledger-gate¥40、連鎖`--budget-jpy 60`、Checker`10`。
## 6 出力とprovenance
`after_pprime_01/pprime_provenance.json`(variant、追記ブロックsha256、送信最終prompt sha256、E2E_02 switch dump sha256、model ID、topic、引数、検索回数・引用URL、reused)。Checkerは`checker_after_01/checker_after_provenance.json`。
