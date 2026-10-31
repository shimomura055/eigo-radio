# DESIGN_01: Cドライブ容量監視・自動整理 (DISK-GUARD-AUTO-CLEANUP-01 / OPEN-637)
状態: IMPLEMENTED_NOT_ACTIVATED(有効化=委任_02、Opus安全レビュー後)。ユーザー原文=`docs/pm/delegation_log/2026-10-31_DISK-GUARD-AUTO-CLEANUP-01_USER.md`。API 0。

## 1. 閾値と動作(原文§2)
| 空き | 動作 | rc |
|---|---|---|
| >=20GB | 何もしない(早期検知のみ。記録は書かない) | 0 |
| 10〜20GB | WARN。原因候補(削除可能候補+保留理由)を列挙。削除しない(安全整理を実施可とされるが、本実装は`--auto`でもcrit未満でのみ削除=過剰整理回避) | 1 |
| <10GB | `--apply`/`--auto`で自動整理。大きい順にoutput→pip→worktreeの順で削除し、**各削除後に再計測**、空き>=20GB(回復目標)到達で停止(最小削除) | 回復後の空きで判定 |
| 整理後も<10GB | CRITICAL。`UNRECOVERED`警告+記録+rc=2(原因調査・報告が必要) | 2 |
- 「10%以上」は目標20GBで充足(総容量453GBの10%=45GB。可能なら…は努力目標、本実装は20GB停止)。判断候補ではなく既定で、`--target-gb`で変更可。
- 早期検知(常時・軽量): 直近60分以内に更新された`.output`が>1GBならACTIVE_BIG_OUTPUTとしてtask-id/path/MBを警告列挙(削除しない)。Fable/Workerが停止判断。

## 2. 削除対象=許可リスト(コードで構造的に限定)
削除候補は次3種の**path patternに一致するものだけ**。それ以外(repo配下、`er0XX_output`、SSOT、pagefile等)は列挙コードが走査しないため到達不能。加えて`denied()`(SSOT名/er0xx_output/pagefile等のtoken)とreparse point(junction/symlink)拒否を二重に掛ける。
1. **task出力** `%LOCALAPPDATA%\Temp\claude\<this project>\<session>\tasks\*.output`(他projectは対象外)。
   - A1: size>200MB かつ 最終更新>=60分前 / A2: 稼働中でないsession(現session指定外かつ直近60分に更新されたファイルが無いsession)の24h超。
   - 稼働中除外: 直近60分以内更新は常に除外。**handle確認**=`CreateFileW(share=0)`で開けなければ使用中(他processがhandle保持)。確認不能(API失敗)も除外。削除直前に再確認。
2. **pip cache** `.venv\Scripts\python.exe -m pip cache purge`。`pip cache dir`の結果が`%LOCALAPPDATA%\pip\Cache`と一致/配下でなければ対象外。再取得可能。
3. **worktree** `git worktree list --porcelain`由来で、path=`<project>\<session>\scratchpad\<name>`のみ。全て成立で対象、1つでも不成立/確認不能は保留:
   - main worktree・locked・prunable・bare・reparse point・自プロセスのcwd/script配下は除外
   - 除外リスト: `<scratchpad>\.disk_guard_keep`(1行1path、相対可、#コメント)に列挙されたもの(Fableが`wt_fix1`等を指定)
   - merge/cherry-pick/revert/rebase/bisect進行中でない
   - `origin/main..HEAD`が0件(未push 0)、HEADがorigin/mainの祖先(merged。branch/detached共通)
   - git管理dir(index/HEAD/logs等)+worktree直下の最終更新>=60分(作業ツリー全走査はしない=高速化。未commit変更は次のstatusで検出)
   - `git status --porcelain --ignored`が空(例外=`__pycache__/`・`*.pyc`のignoredのみ)。untracked・ignored成果物があれば保留
   - dir rename往復probe(cwd/handle保持中のdirはrenameできない)で使用中でない。**dry-runではprobeしない**(実worktreeを触らない。候補に`probe_pending_in_dry_run`)
   - 除去は`git worktree remove <path>`(`--force`禁止。gitが拒否したら保留)。
   - `git`は`GIT_OPTIONAL_LOCKS=0`で実行(index更新で他processのmtimeを汚さない)。origin/mainは最後のfetch時点(networkなし)。

## 3. 記録
実行ごと(動作あり/OK以外/警告あり時のみ。通常OKは書かない)`%LOCALAPPDATA%\eigo-radio\disk_guard\runs\<ts>.json`: 前後空き・閾値・候補・削除・保留理由・警告・所要秒。repoには仕様と検証証拠のみ。

## 4. 起動経路(委任_02で有効化。本委任は案)
| 経路 | 呼出 | 負荷(実測、OK経路) |
|---|---|---|
| a. Claude Code SessionStart hook(`.claude/settings.json`) | `python tools/disk_guard_01.py --auto --quiet` | OK時<1秒(disk_usage+tasks stat)。1行出力 |
| b. Worker開始手順(`sonnet-worker.md`開始チェックに`stop_scope_check`と並記) | 同上 | 同上 |
| c. 長時間/有料処理の前(runner起動前チェック列) | 同上 | 同上 |
| d. タスクスケジューラ1日1回(ユーザー権限、常駐なし) | `schtasks /create /sc daily /st 04:00 /tn eigo-radio-disk-guard /tr "...python.exe tools/disk_guard_01.py --auto --quiet"` | 同上。<20GB時のみ重い走査(実環境で約16秒) |
警告/低空き時のみ走査が重い(worktree git status)。hookはOK経路が支配的なため許容。低空き時はhookを待たせないよう、必要なら`start /b`で非同期化(委任_02で判断)。多重起動はrename probe/再確認で安全側(削除はgit/OSが競合を拒否)。

## 5. 既存tool関係
- `tools/disk_space_check_01.py`: **残置**(単純チェッカー、rc=2。disk_guardのOK判定と等価。配線なし)。以降の新規配線はdisk_guard_01に一本化。
- `tools/claude_task_output_cleanup_01.py`: A1/A2規則を`disk_guard_01`へ**統合**(handle確認・稼働中session除外・再計測を追加)。cleanup_01は委任_02の有効化確認後に撤去候補(本委任では残置、無配線)。
- PREVENTION_01の「background対話型Python禁止・出力制限」はagent定義への注意として維持(変更なし)。

## 6. 範囲外
実削除(本委任は模擬sandboxのみ)、hook/agent定義/スケジューラ有効化、保存仕様・保持期間の変更、禁止対象への到達。
