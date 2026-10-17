# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_18(Fable受入判定=Family Z `PRODUCTION_WIRED`のSSOT記録+Gate 7受入記録+旧pages_dir既定値の残置整理。**JPY0、有料API呼出0**)。日付: 2026-10-17。

## 性質・到達上限Status・禁止事項
- 性質: SSOT記録+軽微なコード整理(既定値の整合)+test。
- 到達上限Status: `PRODUCTION_WIRED_RECORDED_USER_LISTENING_PENDING`(Fable判定の記録。ユーザー試聴PASSは別=REGISTER #23は未判断のまま)。
- 禁止: 有料実行/音声・原稿・KP再生成/run_e2e_03成果物の変更/Style・Voice・Prompt変更/`ledger.json`のcommit/`user_test/family_z_melos_01`の変更/#23を判断済みにすること/#108・#109の再質問。
- 固定ブロック: **E-1**(CURRENT_SPEC Status表・OPEN-412/413・PM_GOVERNANCE 28節・Gate 7書式に整合)/**D-1**(不適用)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`)/**F-1**(JPY0。費用数字は委任_17 `audit/cost_by_stage_17.json`実測のみ引用)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_委任_18.md`へ保存し`check_delegation_prompt.py`実行、`_check.json`保持)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZ18.md`、ACTIVE_TASK.md先頭へ新ヘッダ追加・旧ヘッダ保持。sedによる一括置換は使わず、Edit/Writeで先頭追記のみ)。

## Fable受入判定(2026-10-17、本委任で記録する内容。ユーザー§6の10条件を独立照合済み)
照合evidence(Fable確認): `segment_style_table_17.json` exp_match true 58/false 0、`src_z_posthoc_01.json` 10/10解決(exact 7・unique_containment 3、quote_boundary_truncated 1、STOP 0)、`cost_by_stage_17.json` total_jpy_measured 36.3845、`pages_play_evidence_17.json` audio 12/51/50・console_errors []、Dialogue 21/21 run_e2e_02同一・PD06適用0、6%減速23/23、HR Lock 0、test 190+72+16 PASS、commit fb01f125f/43c75180f/6a29bb3d3。
1. 正式Production初回経路への実装=充足(er063 Style X定数参照/er026 `stage_kp` `_src_gate`)
2. retry/fallback/regeneration/resume整合=充足(単一call site、reuse/regenerate test、実走で`--regenerate-stage kp_expl_b1b`経由を実発火)
3. Trial/DEV専用経路ではない=充足
4. 正式runtimeでの実発火証拠=充足(run_e2e_03 audit群)
5. actual model_id・Style SHA・Voice・routing一致=充足(58/58、X定数sha一致16/16、Dialogue 21/21)
6. Regression/Validator/integration test PASS=充足(190+72+16、er020 1件は既存・別管理OPEN-414)
7. AUW/ASR・6%減速・Dialogue切替・Assembly=充足(PASS_WITH_WARNING 13件は事後試聴区分、HR Lock 0)
8. Dangling Reference Check=充足(定数残存0。残置=er063:1498 `PAGES_DIR`既定値・`tools/build_family_z_hr_review_page.py:12`のmelos_01=本委任で整理)
9. CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新=委任_17で事実記録済み、本委任で判定を記録
10. commit/push/merge=充足
**判定**: Family Zにおいて PD06(Narrator)/S3(Std JA Preview・Comment)/E1(Adv Preview)/K2(KP英語)/P8-KP(Std KP JA)/P7(Adv KP解説)/SRC D1(`z_sentence_id_posthoc_v1`)/Dialogue別Voice(Z固有・維持)/6%減速/AUW = **`PRODUCTION_WIRED`(2026-10-17 Fable、Family Z列)**。Adv Comment E2_UPBEAT=Z固有・現状維持。Opusレビューは条件Aレビュー_C(GO_WITH_FIXES)を配線完了判定に再利用(11-3、内容不変)。**ユーザー試聴PASS(REGISTER #23)は未、別扱い。** 「Family Z全体」ではなく上記仕様ごとの判定であることを明記。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZ17.md`
- `C:\Users\tensh\eigo-radio\docs\pm\PM_GOVERNANCE.md` Gate 7受入記録の5項目書式(Grep `Gate 7`で該当節のみ)・28節(L末尾付近、Grep `^## 28`)
- `C:\Users\tensh\eigo-radio\er063_family_z_audio_01.py` L1490-1505
- `C:\Users\tensh\eigo-radio\tools\build_family_z_hr_review_page.py` L1-30

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: Grep `共通仕様のFamily別配線Status表`→Z列の各行を「PRODUCTION_WIRED(2026-10-17 Fable、run_e2e_03 evidence、commit 43c75180f)」へ。SRC節(Grep `z_sentence_id_posthoc_v1`)に「Z: PRODUCTION_WIRED 2026-10-17 Fable」追記。Grep `別枠JPY100`→実測36.38/100を確認(既に委任_17で記録済みなら不変)。
- `OPEN_ITEMS.md`: Grep `OPEN-412`→Status `PRODUCTION_WIRED(2026-10-17 Fable)・USER_LISTENING_PENDING(#23)`、Gate 7受入記録5項目を本文に。Grep `OPEN-413`→Cross-Family原則の初適用事例(Z)として注記。Grep `OPEN-414`→er020残のみを明記。
- `DECISION_LOG.md`: 末尾へ「2026-10-17 委任_18 Fable受入判定: Family Z PRODUCTION_WIRED(仕様別)、10条件照合結果、ユーザー試聴は別」。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#23`→文言に「PRODUCTION_WIRED記録済み、試聴PASSは未」追記(判断済みにしない)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- `FZ_COMPLETION_PLAN_01.md`: 「## §12 Fable受入判定(委任_18)」追記。

## 作業
A. 上記SSOT記録(commit 1)。
B. 残置整理(commit 2): `er063_family_z_audio_01.py:1498`の`PAGES_DIR`既定値と`tools/build_family_z_hr_review_page.py:12`を、runnerの`E2E_PAGES_DIR`(`user_test/family_z_melos_02`)と単一の正本(runner定数をimportするか、er063側定数をrunnerが参照する)に揃える。履歴evidence文字列は不変。`er063`・`er026` runner/integration testを再実行しPASS数報告。`user_test/family_z_melos_01`配下は変更しない(git statusで確認)。
C. Dangling再Grep: `family_z_melos_01`をコード(.py)でGrepし、残存は履歴記録・test fixtureのみであることを報告。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_委任_18.md`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -m pytest C:\Users\tensh\eigo-radio\er063_family_z_audio_01_test_01.py C:\Users\tensh\eigo-radio\er063_family_z_common_style_wiring_01_test_01.py C:\Users\tensh\eigo-radio\er063_family_z_audio_01_pd06_run_style_test_01.py C:\Users\tensh\eigo-radio\er026_family_z_e2e_integration_test_01.py C:\Users\tensh\eigo-radio\er026_family_z_src_posthoc_01_test_01.py -q`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(実在するscan script名に置換)
- `git -C C:\Users\tensh\eigo-radio status --porcelain -- user_test/family_z_melos_01`(変更0を確認)

## SSOT追記文(要点)
- CURRENT_SPEC Status表 Z列: 「PRODUCTION_WIRED(2026-10-17 Fable、run_e2e_03、commit 43c75180f/6a29bb3d3)。ユーザー試聴PASSは別(#23)」。
- OPEN-412: Gate 7受入記録5項目(照合元/判定/evidence path/残課題/次アクション=ユーザー試聴)。
- DECISION_LOG: 上記Fable受入判定の全文(10条件の充足根拠を1行ずつ)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: delegation_log 委任_18+_check.json、CURRENT_SPEC.md、DECISION_LOG.md、OPEN_ITEMS.md、USER_DECISION_REGISTER_01.md、REPORT_LEDGER.md、FZ_COMPLETION_PLAN_01.md。msg: `FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_18: Fable受入判定=Family Z PRODUCTION_WIRED(PD06/S3/E1/K2/P8-KP/P7/SRC D1/Dialogue別Voice/6%減速/AUW、仕様別・run_e2e_03 evidence)をSSOT記録+Gate 7受入記録(ユーザー試聴#23は別、JPY0)`
- commit 2: `er063_family_z_audio_01.py`、`tools/build_family_z_hr_review_page.py`、更新test。msg: `FAMILY-Z: pages_dir既定値をrunner E2E_PAGES_DIR(family_z_melos_02)へ一本化(旧melos_01既定値の残置整理、evidence不変)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZ18.md`)
4行: (1)整合(編集行番号)(2)Production到達経路=既定値一本化のみ(挙動差なしの根拠)(3)成果物とcommit sha 2件、test PASS数(4)撤去/残置(`family_z_melos_01`残存Grep結果)。`判定整合:` 重大NG有無。`判断候補:` [A]〜[D]またはなし。T-0 check結果。自己チェック: 有料0/#23未判断のまま/melos_01未変更/ledger.json未commit。
