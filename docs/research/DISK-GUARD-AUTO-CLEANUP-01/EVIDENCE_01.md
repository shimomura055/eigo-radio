# EVIDENCE_01: 模擬検証(原文§7-1〜5)
実行: `python tools/disk_guard_01_test_01.py --evidence-dir docs/research/DISK-GUARD-AUTO-CLEANUP-01/evidence_01`(sandboxのみ、実ファイル削除0、21/21 PASS)。
生出力=`evidence_01/test_run_01.txt`、結果json=`evidence_01/test_results_01.json`、実行記録例=`evidence_01/S1_run_record_sandbox.json`・`S5_run_record_sandbox.json`、実環境dry-run=`evidence_01/real_env_dry_run_simulated5GB.json`。

## 縮尺について
実10GB級のファイル作成は遅く(6GBのtruncateに約49秒)実ディスクを汚すため、**1000倍縮尺**(U=GB/1000)で検証した: 閾値`--warn-gb 0.02 --crit-gb 0.01 --target-gb 0.02`(=20/10/20 U)、模擬空き5U/15U/25U、ファイルは6U(約6.4MB)等。ロジックは閾値の絶対値に依存せず同一。製品既定値(20/10/20GB)の分岐はS0/S5(下の実環境dry-run含む)で別途確認していない=**縮尺検証である旨を明記**。

## sandbox配置(本物のgit repo+bare origin、本物のgit worktree)
安全対象: 古い大.output×2〜3(session内)・旧session小.output・pip cache(stub)・clean worktree4種(detached/origin/main~1/mergedブランチ/__pycache__のみ)。
保護対象: 稼働中(直近更新).output・handle保持中.output・SSOT名(`CURRENT_SPEC.md`/`OPEN_ITEMS.output`)・repo配下`er011_output/huge.output`・別project .output・現session小.output(稼働session内A2対象外)、worktree: tracked変更/untracked/ignored成果物/ahead=1(未push commit)/keepリスト/locked/直近更新/scratchpad外。

## 結果(原文§7)
| 完了条件 | 検証 | 結果 |
|---|---|---|
| 7-1 10GB未満で自動整理が発動 | S1: 模擬空き5U(<crit10U)+`--apply` → deleted=8(output3/pip1/worktree4)、記録json出力 | PASS |
| 7-1 予防警戒(10〜20GB) | S0: 15U+`--apply`でもdeleted=0・rc=1(WARN)・候補9件列挙・全残存 / S0b 25U=OK rc=0・候補走査なし | PASS |
| 7-2 安全対象のみ処理 | S1: 安全対象全消滅(output3・pip・worktree4)。S1b: 目標20U到達(5U+18U)で停止、worktree/pip/旧session小は未処理(最小削除)rc=0 | PASS |
| 7-3 未保存成果物・Production保護 | S1/S5: 保護対象(上記)が全て残存、`git worktree list`にも残る。保留理由が記録(dirty/untracked/ignored/ahead/keep/locked/recent/handle/not_in_allowlist) | PASS |
| 7-4 整理後に再計測 | S1: free_bytes_after = before + 削除bytes、17.0U(目標未達)でWARN rc=1。各削除後に目標判定(S1b) | PASS |
| 7-5 回復不能の警告 | S5: 安全対象が僅少→after<10U → CRITICAL・rc=2・`UNRECOVERED`警告・記録、保護対象無傷 | PASS |
| 補 dry-run優先 | S7: `--auto --dry-run`で削除0。S6: 5U dry-run削除0 | PASS |
| 補 quiet | `disk_guard: OK free=..`の1行(S5末尾) | PASS |
7-6(実経路の有効化)は委任_02。7-7は本commit。

## 実環境(dry-runのみ、削除0)
- 実空き67.9GB: `--dry-run --quiet` = 0.48秒(OK経路、記録なし)。
- `--dry-run --simulate-free-gb 5`(実環境の候補列挙。15秒): 候補2件=pip cache 0.00GB(既にpurge済み)・worktree`wt_n5q`0.28GB(dry-runのためrename probeは`probe_pending`)、合計**0.28GB**。.output候補0件(DISK-SPACE-RECOVERY-01で整理済み)。保留15件(他Worker稼働中のworktree: recent_update/dirty/ahead/self_or_cwd等)。ACTIVE_BIG_OUTPUT 0件。
- 所要: OK経路0.14〜0.5秒/低空き時の実環境走査約15〜17秒(S1相当のsandboxは1.6秒)。
