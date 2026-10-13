## 管理ID

FAMILY-Z-KP-DB-HYBRID-M2P0-MIGRATION-TRIAL-01 委任_01(初回。ユーザーTrial承認: 2026-10-13 FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 追加決定§4)。並行タスク: FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_03(別sonnet-worker、`er030_*`/`er019_*`/`er063_*`/Coffee run dir/SSOT編集中)。本委任は**SSOT編集権なし**(追記文案はRESULT_PACKETへ)。Production module(`er030_key_phrase_db_hybrid_*`、`er062_*`、`er063_*`、`er026_*`)は**読み取り・importのみ、編集禁止**。出力: `er073_output/family_z_kp_db_hybrid_m2p0_migration_01/`、script `er073_family_z_kp_db_hybrid_m2p0_migration_01_*.py`。一時ファイル: `docs/pm/ACTIVE_TASK_FZKP.md`/`docs/pm/RESULT_PACKET_FZKP.md`。`.git/index.lock`存在時は30秒待ち×3回、commit前に`git fetch origin && git merge --ff-only origin/main`(不可なら`git pull --no-rebase`、conflict時は両追記保持)。全commitに`Managed-ID: FAMILY-Z-KP-DB-HYBRID-M2P0-MIGRATION-TRIAL-01` trailer。

## 性質/到達上限Status/禁止事項

- 性質: Trial(Productionに影響しない独立Trial)。Family ZのKP選定を現行Strategy LからDB Hybrid+M2P0へ移行する方式の設計+評価。
- 到達上限Status: `VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`。**Trial結果だけを根拠にProduction実装しない**(移行方式はユーザーの正式採用判断が必要)。
- 費用: 上限¥50(Guardrail。PM_GOVERNANCE 7-7のFable承認範囲。soft ¥35)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase 2(有料)の前に`plan_01.md`へ設計(job数×単価、出典付き)を事前登録。見積が¥50超なら縮小、縮小不可なら未実施でSTOP。
- 禁止: Family Zの記事再生成・音声化・Production KP再生成(STOP維持)、Production code/Prompt/DB/gateの編集、Family Z Previewの先行採用、N01・M2P0以外の方式探索、P0以外の選定Prompt(Family Z用guidanceが必要な場合は「Family X guidanceの最小置換」として差分表で提示し、新Promptとして扱う=ユーザー判断事項)、Validator緩和、未承認ASR改善ロジック混入、`git add -A`/`-f`、amend/rebase/force push、stash/clean/`reset --hard`/`checkout -f`、`.env`、秘密値出力、wav/telemetry/logのadd、ACTIVE_TASK/RESULT_PACKETのcommit、Melos run_e2e_02配下・Master Store・HR・attempt_history・telemetryへの書込(`append_telemetry_log`等はno-op化)、外部プロセス再起動、監督ループ/timeoutラッパ、Batch。
- STOP条件: Production経路の変更なしにTrialが成立しない/Family Z用guidanceの新規作成が不可避で差分が「必要最小限」と説明できない/予算暴走疑い/`STOP_NOTICE`/`STOP`/`STOP_ALL`。
- STOP確認義務: 開始時に`er026_output/family_z_production_e2e_01/`配下の`STOP_NOTICE`/`STOP`/`STOP_ALL`を確認し記録(旧記録は非適用)。
- Opus独立技術レビューGate判定: 本委任は設計+Trial。Production採用提案時に条件A/Cを別途。設計書にOpus論点を残す。
- 時間見込み: 90〜120分(構造差20/設計25/Trial実装・実行35/評価・報告20)。並列化: XZW 委任_03と並列(ファイル領域分離)。
- 最新モデル原則: 選定LLMはProduction同一`gpt-6-luna`(比較可能性の例外)。model_id実測を記録。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1/T-0/T-2/T-3: 委任文のとおり(同一ファイル再読禁止、Grep→範囲Read、git出力最小化、transcript退避不要、委任文保存+check_delegation_prompt実行、TTSなし、費用Guardrail定型文)。

## ユーザー指示(原文)

(2026-10-13、FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 追加決定 §4)「ユーザーは、Family ZのKey Phrase選定をDB Hybrid+M2P0へ移行するためのTrial実施を承認した。したがって、以下を実施する。1.Family Zの現行Strategy Lと、Family XのDB Hybrid+M2P0の構造差を確認する。2.Family Zへの適用方式を設計する。3.Productionに影響しない独立したTrialを実施する。4.選定品質、既存Validatorとの整合、コスト、処理時間、既存方式からの品質劣化の有無を評価する。5.Trial結果を`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`に分類して報告する。Family ZのDB Hybridへの移行方式は、新たな仕様変更に該当するため、Trial結果だけを根拠にProduction実装しない。ユーザーによる移行方式の正式採用判断が必要。一方、M2P0をFamily Zにも適用するという既存の正式決定は維持する。」(§6)「Family Z: Standard Previewの仕様が正式決定し、必要なProduction反映が完了するまで、記事再生成・音声化を停止する。N01の配線と、M2P0移行Trialなど、記事再生成・音声化を伴わない作業のみ許可する。Trial成功をFamily Zの音声化GOと解釈しないこと。」(§9)「Trial結果に追加のユーザー判断が必要…USER_DECISION_REQUIREDが発生した場合はSTOPし、ユーザーの判断を待つこと。」

## 作業内容(要点。全文は受領委任文)

Phase 1(¥0): P1-1 構造差表 STRUCTURE_DIFF_01.md / P1-2 適用方式設計 MIGRATION_DESIGN_01.md(案1=Family X経路流用、guidance逐語+必要最小限置換差分表、既存Validator整合、retry/fallback、処理時間、費用、Opus論点) / P1-3 plan_01.md(Melos Std/Adv(+他Z原稿1本)×{現行Strategy L再現(既存出力再利用)、DB Hybrid+M2P0案1}×n=3、費用見積、¥50内)。
Phase 2(有料、上限¥50): er073_..._run.py でProduction moduleをimportしTrial隔離実行。state_guard(run_e2e_02配下・Production py sha256不変、telemetry行数不変)。
評価 TRIAL_REPORT_01.md: (1)選定品質目視ラベル (2)既存Validator整合 (3)コスト・時間 (4)品質劣化の有無 (5)安定性Jaccard。Status、Production実装に必要な変更一覧(未実装・未承認)、ユーザー判断事項。
報告: docs/pm/RESULT_PACKET_FZKP.md(0)〜(8)。Git: 明示add、trailer付き、push。
(注: 本ファイルは受領委任文の保存。長大な固定ブロック・Read/Grep一覧・実行コマンド全文の逐語は、受領文のまま task transcript に存在。)

## KPI provenance欄

Phase 1=`reuse`(既存Melos原稿・既存Strategy L結果の読取)。Phase 2=`fresh`(Trial隔離の選定LLM呼出、Production経路ではない)。fresh Production初回path E2E値: No。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

1. Family Z現行KP: `er062_family_z_writer_01.py`・`er026_family_z_fiction_production_runner_01.py` `Grep -n "kp_backend|strategy_l|key_phrase|run_key_phrases|KP"`→Z KP stageの入出力。`er020_*`/`er003_key_words_*`のStrategy L実装。
2. Family X DB Hybrid+M2P0: `er030_key_phrase_db_hybrid_selector_01.py`(`run_db_hybrid_selection`全体、`family_profile`分岐と`NotImplementedError`箇所)、`er030_key_phrase_db_hybrid_m2_supply_01.py`、`er030_key_phrase_db_hybrid_core_01.py` L425-484、Family X guidance/P0 Prompt定数の所在。
3. Melos既存成果物(読取のみ): `er026_output/family_z_production_e2e_01/melos/run_e2e_02/writer/std.md`、Adv原稿、同`kp/`配下の現行Strategy L出力。他のFamily Z原稿があれば(`er055_output/**/story*.{md,txt}`最大2本)一般化用に使用。
4. KP品質の評価基準: `er064_output/kp_integrated_opt_01/round1/ROUND1_REPORT_01.md` §1。Family Zではアンカーが無いため、評価軸を「P0が求める価値基準での目視ラベル+gate PASS率+Redundancy+Rule7 INVALID率+既存Strategy L結果との差分」とする。
5. `CURRENT_SPEC.md` Strategy L/Family Z KP行、`OPEN_ITEMS.md` OPEN-344/325/336/337/310。

## 事前指定Grep一覧+追記位置・更新位置の手順

SSOT編集なし。RESULT_PACKETに「DECISION_LOG/OPEN-344追記文案」を記載。

## 実行コマンド全文

```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-13_FAMILY-Z-KP-DB-HYBRID-M2P0-MIGRATION-TRIAL-01_01.md --json-out docs\pm\delegation_log\2026-10-13_FAMILY-Z-KP-DB-HYBRID-M2P0-MIGRATION-TRIAL-01_01_check.json
set PYTHONUTF8=1
.venv\Scripts\python.exe er073_family_z_kp_db_hybrid_m2p0_migration_01_diff.py --out-dir er073_output\family_z_kp_db_hybrid_m2p0_migration_01
.venv\Scripts\python.exe er073_family_z_kp_db_hybrid_m2p0_migration_01_run.py --plan er073_output\family_z_kp_db_hybrid_m2p0_migration_01\plan_01.json --out-dir er073_output\family_z_kp_db_hybrid_m2p0_migration_01\runs --budget-jpy 50 --no-telemetry
.venv\Scripts\python.exe er073_family_z_kp_db_hybrid_m2p0_migration_01_test_01.py
.venv\Scripts\python.exe tools\secret_scan_01.py --staged
```

## SSOT追記文

編集せず文案のみ(DECISION_LOG本ID、OPEN-344更新)。

## Git(明示add対象・コミットメッセージ・trailer)

SSOT編集権なし。明示add: `er073_*.py`、`er073_output/family_z_kp_db_hybrid_m2p0_migration_01/**/*.{md,json}`、`docs/pm/delegation_log/..._01.md`(+`_check.json`)。コミット: 「FAMILY-Z-KP-DB-HYBRID-M2P0-MIGRATION-TRIAL-01 委任_01: Family Z KP DB Hybrid+M2P0移行Trial(構造差+設計+Trial JPY<実費>、Status=<判定>、Production無変更・採用判断なし)」trailer付き。push。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FZKP.md`に: (0)check結果、STOP確認、(1)構造差要約、(2)移行方式設計要約、(3)Trial結果、(4)Status・根拠、(5)費用・model_id、回帰・state_guard、(6)SSOT追記文案、Dangling Reference、(7)ユーザー判断事項、(8)commit hash+raw URL。
