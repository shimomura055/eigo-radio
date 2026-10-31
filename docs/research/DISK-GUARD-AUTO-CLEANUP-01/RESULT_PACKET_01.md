# RESULT_PACKET DISK-GUARD-AUTO-CLEANUP-01 委任_01 (正本コピー。docs/pm/RESULT_PACKET_DG_01.mdはgitignore)
実装: tools/disk_guard_01.py(+_test_01.py)。状態=IMPLEMENTED_NOT_ACTIVATED(OPEN-637)。実ファイル削除0、API 0。
設計: 閾値20/10/20GB。許可リスト3種(task .output[handle確認]/pip cache purge/scratchpad直下のclean・pushed・merged・60分未更新・keep外worktree→git worktree remove、force無し)。1条件でも不成立/確認不能=保留。稼働中>1GB .outputは早期WARNのみ。記録=%LOCALAPPDATA%\eigo-radio\disk_guard\runs\*.json。
検証(sandbox・1000倍縮尺・本物のgit worktree)21/21 PASS: §7-1(5U<10U→自動整理発動 deleted=8)/15UはWARNのみ削除0・§7-2(安全対象のみ削除、目標到達で最小停止)・§7-3(未commit/untracked/ignored/ahead/keep/locked/直近/scratchpad外/handle保持/SSOT名/repo配下/別project全残存)・§7-4(再計測=before+削除bytes)・§7-5(回復不能でCRITICAL rc=2+UNRECOVERED+記録)。詳細=EVIDENCE_01.md。
実環境dry-run: 空き67.9GB(OK経路0.48秒)。模擬5GBのdry-run候補=2件0.28GB(pip 0GB+worktree wt_n5q)、.output候補0件、保留15件(他Worker稼働worktree)。
起動経路案(ACTIVATION_PROPOSAL_01.md): SessionStart hook / Worker開始手順 / runner前 / schtasks daily。OK経路0.14〜0.5秒、低空き時走査約15秒。
(1)整合: DESIGN_01.md§5(disk_space_check残置・cleanup_01統合)、sonnet-worker.md:100(stop_scope並記案) (2)未承認機能の既定: 全て無配線(hook/agent定義/スケジューラ変更0、tools新規のみ)・既定dry-run (3)失敗終了時成果物: 回復不能時は削除せず警告+rc=2+runs記録 (4)撤去/残置: cleanup_01・disk_space_check_01残置(無配線)、grep: 両ファイル参照は PREVENTION_01.md/DESIGN_01.mdのみ
判定整合: 重大NG=なし
