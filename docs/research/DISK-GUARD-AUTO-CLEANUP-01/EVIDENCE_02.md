# EVIDENCE_02 (DISK-GUARD-AUTO-CLEANUP-01 委任_02: Opus条件Aレビュー反映・有効化・実環境検証)

API 0・費用0。証跡dir=`evidence_02/`。レビュー全文=`OPUS_REVIEW_01.md`。状態=OPEN-637 `ACTIVATED_PENDING_FABLE`(hook実発火の証跡は未取得)。

## 1. Opus指摘の対応表

| ID | 対応 | 実装/証跡 |
|---|---|---|
| M-1 | `--hook`: 常にexit 0・stdout 1行+stderr同文。WARN以上/ACTIVE_BIG/ERRORは「Fableは即時報告すること」、CRITICALは「ユーザーへも即時報告」。記録path付き。内部エラー・不正引数・不正stdinでもexit 0 | `hook_main`/`main`、test S12(8件) |
| M-2 | `.claude/settings.json`新規(hooksのみ・`/`区切り・matcher=`startup\|resume`・timeout 30)。JSON構文OK。**実発火の証跡=未取得**(Fableが次セッション開始時に取得) | `.claude/settings.json`、`json.load`検証 |
| M-3 | rename往復probe(`dir_in_use`)を撤去。使用中判定=locked+`.disk_guard_keep`+親session非稼働(`<session>/tasks`最新mtimeが3時間以上前、現sessionでない、確認不能は稼働扱い)+Win32_ProcessのCommandLine/ExecutablePathにworktree pathを含むprocessがあれば保留(一覧取得失敗も保留) | `session_is_active`/`proc_cmdlines`/`check_worktree`、test S1(使用中process・稼働session・probe撤去) |
| M-4 | `git worktree remove`直前に`worktree_list`+`check_worktree`(ahead/merge-base/mtime/`status --porcelain --ignored`/lock/keep/session/process)を全再実行。変化=保留(`recheck:…`) | `remove_worktree`、test S11(untracked追加・未push commit追加で保留) |
| M-5 | 実機観測: 稼働中taskの`.output`で`file_in_use`=True(7秒・213秒・879秒無出力時点)、task終了後False。A1への条件追加は不要 | `evidence_02/m5_observations.txt` |
| M-6 | hookは高速判定+1行のみ。<10GBの整理は別process(`DETACHED_PROCESS|CREATE_NEW_PROCESS_GROUP`)。単一lock(`<state_dir>/.lock`、O_EXCL、stale 1時間回収、完了後解放)。matcher限定 | `hook_main`/`acquire_lock`、test S12/S13 |
| R-1 | LOCALAPPDATA非絶対→rc=3失敗。project_dir/session dirのreparse拒否+warning。`denied_both`(生path+realpath)。project_dir無しはwarning | test S10/S10b/S10c(junction実体無傷) |
| R-2 | 削除記録に`git.head`(40桁)・`branch`・`reflog`(直近20) | test S1 |
| R-3 | (a)schtasks 60分間隔 (b)前回サイズ保存→増加速度>1GB/10分でACTIVE_BIG(growing) (c)Restart Manager(`RmGetList`)+Win32_Processで書き手PID/command lineを警告へ(killなし) (d)Worker規約 | test S0b(書き手PID一致)/S9、schtasks証跡 |
| R-4 | A1削除前に先頭・末尾各64KB抜粋を`runs/excerpts/`へ。CRITICAL flag→次hookで1回表示。runs rotation(50件)。quiet行にrecord path | test S1/S14 |
| R-5 | hook stdin JSON `session_id` > 環境変数。不明=全session稼働扱い(A2を行わない)。子processへ`--current-session`で引継ぎ | test S8/S12 |
| R-6 | 使用中process・junction・製品既定値の実環境dry-run/apply(下記) | test + `real_*` |
| R-7 | `claude_task_output_cleanup_01.py`をgit rm、`disk_space_check_01.py`は`--hook`の薄い別名 | git diff |
| R-8 | `pythonw.exe`・XMLでStartWhenAvailable・電池駆動可・IgnoreNew・実行制限15分 | `tools/disk_guard_task_install_01.py`、`schtasks_task_final.xml` |
| 規約文 | `.claude/agents/sonnet-worker.md`のstop_scope_check項(100-105行)の直後に3行追記(他の行は不変) | git diff |

## 2. テスト(sandbox。実環境の削除なし)
`tools/disk_guard_01_test_01.py` 54/54 PASS(委任_01の21件から33件追加)。結果=`evidence_02/test_results_02.json`、全出力=`evidence_02/test_stdout_02.txt`。追加分: 書き手PID、使用中process保留、稼働sessionのworktree対象外、probe撤去、A1抜粋、reflog記録、current_session、S8(A2の安全側)、S9(増加速度)、S10(junction/LOCALAPPDATA/project無し)、S11(TOCTOU 2種)、S12(hook 8種)、S13(lock多重実行skip・stale回収)、S14(flag・rotation・quiet record)。

## 3. 実環境検証(R-6。実worktree/outputは削除されず)
1. `--simulate-free-gb 9 --dry-run`(製品既定値): `evidence_02/real_dry_run_01.json`。state=CRITICAL(模擬)。**候補=pip cacheのみ(0.00GB)**、.output候補0件(>200MB・60分以上のものなし)、worktree候補0件(全18件が保留: locked=wt_cap/wt_cnt/wt_dg/wt_fix1/wt_fix2/wt_jaq/wt_n5q/wt_n5r ほか、稼働session scratchpad=parent_session_active)。
2. 候補がpipのみのため`--simulate-free-gb 9 --apply`を1回実行: `real_apply_01.json`。deleted=pip cache(2,234 bytes)のみ。worktree一覧は前後で同一(`real_worktrees_before/after.txt`、diff空)。pip cache dir 400KB→400KB(du。既に空に近い)。
3. 前後の空き: 実測 約64-67GB(模擬9GBの再計測は+2,234bytes)。実環境の空きは整理前後でほぼ不変。
4. schtasks: `eigo-radio-disk-guard`を登録(検証用にwt_dgのscriptで登録→`schtasks /run`→`last_run.json`更新[state=OK,free=67.15GB]と`Last Result=0`を確認→最終形のmain treeのscript pathで再登録)。`schtasks_query_final.txt`: 繰り返し間隔1時間・ユーザー権限(tensh)・実行=`pythonw.exe "…\tools\disk_guard_01.py" --auto --quiet`。**注意: 最終登録のscript pathはメインツリーの`tools/disk_guard_01.py`。メインツリーへ本commitが反映されるまで、毎時の実行はscript不在で失敗する(無害)。**

## 4. 未取得・制約
- hook実発火の証跡(新セッション開始時の1行出力): 未取得。hookコマンドはメインツリーの`tools/disk_guard_01.py`を参照するため、メインツリーへの反映(commit取込)が先に必要。
- プロセス照合は「command line/実行pathにworktree pathを含むもの」。cwdだけを保持しpathを引数に持たないプロセス(素のcmd.exe等)は検出できない。この残余リスクは`git worktree add --lock`規約(M-3(i))と親session非稼働条件(3時間)で補う。
- 稼働中sessionの`<session>/tasks`で`.output`をA2/A1が削除するとtasks dirのmtimeが更新され、そのsessionのworktreeは以後3時間保留になる(安全側)。
- 実環境でlockしていない稼働中sessionのworktree(ejh03b/eu06/wt_cnt_base/wt_disk/wt_flapt/wt_flapt2/wt_n5/wt_sub等)は、親session非稼働(3時間)条件で保護される。session終了後3時間経過すれば、clean・push済み・merged・無使用の場合のみ削除候補になる。
