# REVERT_REHEARSAL_07: Gate 4 revert予行(AUW 委任_07、ADDENDUM §2 L99 / OF-AUW-13)

管理ID: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_07。性質: mainへ入れる前のロールバック予行。**結果は破棄**(別worktreeのみ。本番ツリー・branch・mainは無変更)。有料API 0。

## 0. 当初目的(ユーザー原文L176・L210の関連部分、`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`)
- L176(§7)「既存の正常な動作を壊さず、ロールバック可能性を確保する。」
- L210(§9条件10)「必要なUnit／Regression／Integration testがPASS。」(Gate 4: ADDENDUM §2 L99「(1)`git revert --no-commit`の予行(結果は破棄)、(2)旧testの再実行、(3)新キーに対する後方互換test」)

## 1. 条件
- 対象=`origin/main`(cf4aca321)から本branch HEAD(a6d9cc754、`origin/main`取込済み)までの差分。`git diff --stat origin/main...HEAD` = 1,131 file(+252,352/-815)、うち`.py` 71 file。branch上の非merge commit 16件(委任_02b〜06e+07の取込前提commit 1件)。
- worktree 3つ(`git worktree add --detach`、パス `C:\Users\tensh\eigo-radio-auw-revert` ほか。パス長は最長でも既存repoと同程度で問題なし):
  - A=`eigo-radio-auw-revert`(HEAD)→ `git revert --no-commit`
  - B=`eigo-radio-auw-revert-b`(HEAD)→ `git diff origin/main...HEAD -- '*.py' '*.json' | git apply -R`
  - M=`eigo-radio-auw-main`(`origin/main`そのもの。旧test基準)
- テスト用pythonは本repoの`.venv`を使い、**cwd=各worktree**で実行(`import er003_v1_n3_01_tts_generate`の`__file__`が各worktree配下であること、およびAのreverted tree/Mでは`_post_slowdown_cascade_rescue`が存在し`_post_slowdown_unified_judge`が無いことを確認済み)。

## 2. (i) 適用が衝突なく通る
| 方式 | コマンド | 結果 |
|---|---|---|
| A: `git revert` | `git revert --no-commit <AUWの非merge commit 15件>`(newest→oldest。branchに途中のmerge `39fe53c0e`[mainの文書取込]を含むため範囲指定ではなくcommit列挙。取込前提の同一内容commit `143d1b78a`は除外) | **衝突0**(`UU/AA/DU/UD` = 0件)。`git diff origin/main --name-only`=**0 file**(**revert後のツリーは`origin/main`と完全一致**。コード・test・json・docsの全て) |
| B: patch逆適用 | `git diff origin/main...HEAD -- '*.py' '*.json'`(10,189,432 byte)を`git apply -R --check`→`git apply -R` | **check rc=0・適用成功**。`git diff origin/main --name-only -- '*.py' '*.json'` = **0 file**(py/jsonは完全にmain相当へ復元。残差は`er058_output`の新規mdファイル等のdocs 290 file[追加のみ]で、コードに影響しない) |

注: 実際のロールバックは`main`上で`git revert -m 1 <AUW merge commit>`(merge 1個=revert単位、OF-AUW-02)。上記Aは同じ変更を15個のcommit単位で戻したもので、merge単位のrevertと結果の木は同一になる(mainにAUW以外の変更が先に入っていない前提)。mainにAUW以外のcommitが先に載った場合の挙動は未検証(merge時点で再確認する)。

## 3. (ii) 旧test(main時点baseline)がmain時点と同じ結果
- 対象: `origin/main`のtest file(`*test*.py`)のうち、AUWが変更した18の本番module(`er003_v1_crosslevel_audio_02_common`/`er003_v1_n3_01_tts_generate`/`er003_v1_repro01_main_generate`/`er003_v1_sing01_news_tail_fix`/`er003_v1_sing01_point_headings_aoede`/`er003_v1_sing01_voice01_generate`/`er006_master_audio_store_01`/`er006_preprod_hardening_01_validation`/`er006_secondary_asr_01`/`er007_ja_secondary_asr_01`/`er011_human_review_lock_01`/`er012_b_family_production_runner_01`/`er012_b_family_voices_a2_production_01`/`er012_b_family_voices_production_01`/`er013_family_c_production_runner_01`/`er019_family_x_audio_production_runner_01`/`er019_family_x_validation_inheritance_01`/`er063_family_z_audio_01`)をimportする**83 file**。
- 実行: 通信遮断plugin(`netguard`)付き、M(`origin/main`)とA(revert後)を同条件で各1回(同時起動、各worktree内で隔離)。
- 結果: M と A で**1,768 test case(pytest junit)の outcome 差 0**(pass 1,606/failure 123/error 25/skipped 14、どちらも同一)。`evidence_07/old_tests_main_vs_revert.txt`(比較script出力)。
- 注意(正直な記録): この83 fileにはmain時点で**既に148件(failure 123+error 25)の失敗**がある(環境依存・外部通信遮断・作業ツリーの未commit出力依存。06cの`baseline`失敗idと同系)。本予行が確認したのは「revert後のtreeでの結果がmain時点と同一」であり、「旧testが全PASS」ではない。AUW branch上でこれら83 fileを回した場合の差は、各委任(03〜06e)の per-file 比較で「baseline失敗idに無い新規失敗0」を確認済み(`patch_03b`/`patch_05`/`patch_06c`/`patch_06e`の`summary`)。
- 副作用: testが追跡state file(`er011_output/attempt_history.jsonl`ほか6件)を追記する既存挙動により、test実行後のrevert worktreeには7 file(state)の差が出る(予行worktree内のみ。OPEN-374)。revert直後(test前)は0 file差。

## 4. (iii) flag OFFロールバック経路test(06c)がbranch上でPASS
- `er078_asr_unified_wiring_06c_test_01.py -k test_g`(`cascade_enabled=False`→旧leaf挙動[統一judge/Secondary不呼出、`stop_retrying`分岐]/`FEATURE_FLAG_SECONDARY_ASR_ENABLED is True`の既定/leafの`stop_retrying`分岐が保持されていること): **3 passed**(`evidence_07/tests_flag_off_rollback_branch.txt`、branch HEAD、`origin/main`取込後)。
- 追加: AUW中核12 file `411 passed`・静的監査15 passedが取込後も一致(`tests_auw_core_post_merge.txt`、`static_audit_post_merge.txt`)。後方互換test 53 passedは`RUNTIME_EVIDENCE_06.md`§15-2。

## 5. 後始末
- worktree 3つは`git worktree remove --force`で撤去(予行結果は破棄)。`git worktree list`で撤去を確認した結果は`CLOSEOUT_PLAN_07.md`§6に記載。
- 未確認: mainにAUW以外のcommitが載った後のrevert(競合の可能性)。merge直前に`git merge --no-commit --no-ff`の予行を再度行うこと(`CLOSEOUT_PLAN_07.md`§1)。
