# WORKTREE_RECLAIM_01 (DISK-SPACE-RECOVERY-01 委任_02, 2026-10-31)

API 0。STOP check rc=0。`git worktree remove`(--forceなし)のみ使用。

空き容量(C:): 前 45,945,769,984 B (42.8 GiB) -> 後 73,909,551,104 B (68.8 GiB)。回収 約28.0 GB。
メインツリー `git status --porcelain` 件数: 12986 -> 12986(不変)。除外worktree(wt_cap=7, wt_fix1=0, wt_fix2=24, wt_n5q=0, wt_n5r=2)の status行数は不変。wt_capw は実在せず(worktree未登録)。wt_disk は記録用に使用中のため対象外。

## 回収(9本, 各約3.1GB、wt_jaのみ3.3MB。全条件(1)-(5)充足, ahead=0, 最終更新1146分以上前)
| worktree | HEAD | size | 結果 |
|---|---|---|---|
| ejhpush | 521de87ec | 3141.9MB | removed |
| fx06 | 1526136c8 | 3116.9MB | removed |
| fx09 | 8150f426f | 3144.7MB | removed |
| kpd03 | f094a3f80 | 3080.5MB | removed |
| kpd05 | a8cb41708 | 3104.3MB | removed |
| kpg03wt | 4994442cc | 3134.8MB | removed |
| wt | 89343d65e | 3143.2MB | removed |
| wt05 | 3bbf7d55d | 3099.9MB | removed |
| wt_ja | 6827ff051 | 3.3MB | removed (branch ja-gloss-nuance-01 は origin/main merged済、branch自体は残置) |

## 保留(7本, 条件(1) status非空。いずれも未コミット変更を含むため触れない)
| worktree | HEAD | size | 理由 |
|---|---|---|---|
| ejh03b | 1d0607f30 | 3144.6MB | status 75行 |
| eu06 | f069eee53 | 3094.9MB | status 1行 |
| wt_cnt | 3a0bf398f | 101.9MB | status 4行(最終更新144分前) |
| wt_flapt | dea4439a4 | 3192.8MB | status 3行 |
| wt_flapt2 | 1c1d719bd | 3200.6MB | status 6行 |
| wt_n5 | 92a4e79c3 | 3208.7MB | status 39行 |
| wt_sub | ff73d25cb | 284.9MB | status 4行 |

保留分は内容確認(不要/要保存の判断)後に追加回収可能(最大約16GB)。`git worktree prune` は回収後1回実行済み。
