# 委任文(Fable→sonnet-worker)

## 管理ID
PM-GIT-ACTIVE-TASK-UNTRACK-01 委任_01(是正のみ・API 0・費用JPY0): 直前のcommit 9665101b3 で、.gitignore対象の一時ファイル `docs/pm/ACTIVE_TASK.md` が `git add -f`(禁止操作)でGit管理に入った。履歴書換え(amend/rebase/force push)は禁止のため、**新しいcommitで追跡解除**する。

## 作業
S1. `git ls-files docs/pm/ACTIVE_TASK.md`で追跡状態を確認。`git rm --cached docs/pm/ACTIVE_TASK.md`(作業treeのファイルは残す)。`.gitignore`に`docs/pm/ACTIVE_TASK.md`(または該当パターン)が既にあることを確認(無ければ追加)。他の一時ファイル(`docs/pm/RESULT_PACKET_*.md`)が同様に追跡されていないか`git ls-files docs/pm/ | findstr RESULT_PACKET`で確認し、あれば同様に`--cached`で解除。
S2. commit(`PM-GIT-ACTIVE-TASK-UNTRACK-01: 誤って追跡されたdocs/pm/ACTIVE_TASK.md(gitignore対象の一時ファイル)をgit rm --cachedで追跡解除(履歴は書き換えない)`)→`git push origin HEAD:main`→到達確認。`git add -A/-u/-f`は使わない(今回のcommitは`git rm --cached`のstageのみ)。
S3. `docs/pm/REPORT_LEDGER.md`に1行(逸脱記録: 委任PLIR 委任_02で`git add -f`使用、本commitで是正、再発防止=委任文の禁止事項を遵守)。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_PM-GIT-ACTIVE-TASK-UNTRACK-01_委任_01.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「PM-GIT-ACTIVE-TASK-UNTRACK-01」を含む最新index)。これらは明示addで同commitまたは直後のcommitに含める。
S4. 報告(docs/pm/RESULT_PACKET_GITFIX2.md): 解除したファイル、commit hash、`git ls-files docs/pm/`の結果、到達確認。並行agent(BYUS 委任_07)のuntracked fileは触らない。