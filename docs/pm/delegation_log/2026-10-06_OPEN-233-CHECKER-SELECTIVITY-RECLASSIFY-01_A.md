# 委任_A OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01(2026-10-06、受領委任文の要約保存)

管理ID: OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01 委任_A。性質: Trial、到達上限VALIDATED。git操作禁止・SSOT/ACTIVE_TASK/RESULT_PACKET/runner/checker編集禁止。
新規ファイルは er052_output/open233_reclassify_01/ 配下、docs/pm/reclassify_open233_checker_selectivity_01.md、docs/pm/RESULT_PACKET_A.md のみ。

## 目的
既存42 run(er052_output/open233_stage1_stageA_01)の保存候補を、新しい問い(3択 SUPPORTED/NO_FACT_CLAIM/CANDIDATE)で再分類。「Ledgerに明示されていない」だけでは候補にしない。数値・日付・固有名・因果・否定・比較を含む主張はLedgerと一致しない限りCANDIDATE。
決定論由来候補・coverage_gapは対象外で不変保持。run単位1 call。モデル・effortは既存r3構成(E2Eのr3=medium)。

## KPI/合否
KPI変更禁止。合否はgold 6件残存100%のみ。候補減少量は参考指標。Safety基準を緩めない。

## 費用
上限¥10(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。実行前にestimate、見積>¥10ならSTOP。

## 報告項目
RESULT_PACKET_A.md: T-0結果/prompt全文・モデル/候補数Before-After/gold内訳/見逃しケース残存/2方向和集合/費用/例文/所見/一覧外Read理由/SSOT追記文案/成果物一覧。Opus台帳(OF-027等)は編集せず該当ID記録。

## KPI provenance欄
候補数Before: reuse(段階A 42 run保存出力)。After・gold残存・2方向和集合: fresh(新しい問いによる分類callを保存候補へ適用)。E2E自己確認: No。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Readを基本とする。
G-1: git出力は最小化(本委任はgit操作なし)。
F-1: transcript退避は不要。
T-0: 本ファイル保存+check_delegation_prompt実行。

## 事前指定Read一覧
design_open233_stage1_loop3_prep_01.md全文 / rca_open233_e2e_neg7_human_review_01.md L6-L31 / opus_l2_review_open233_stage1_loop2_17.md L10-L30 / 段階A保存出力 / open233_missed_candidates_reclassification_2026-10-03.md / SAFETY_CRITICAL_CLAIM_DEFS

## 事前指定Grep一覧+追記位置・更新位置の手順
A4-0|neg5|B3-same|HF-011|K19 / OPUS_FINDINGS_LEDGER.md(編集しない)。追記位置は新規ファイルのみ。

## 実行コマンド全文
.venv\Scripts\python.exe er052_output\open233_reclassify_01\reclassify_candidates_01.py --input-dir er052_output\open233_stage1_stageA_01 --out-dir er052_output\open233_reclassify_01 --stage estimate
.venv\Scripts\python.exe er052_output\open233_reclassify_01\reclassify_candidates_01.py --input-dir er052_output\open233_stage1_stageA_01 --out-dir er052_output\open233_reclassify_01 --stage run --yes-run-paid --budget-jpy 10
.venv\Scripts\python.exe er052_output\open233_reclassify_01\reclassify_candidates_01.py --input-dir er052_output\open233_stage1_stageA_01 --out-dir er052_output\open233_reclassify_01 --stage agg

## Opus台帳更新
台帳は編集しない。OF-027等の該当IDをRESULT_PACKET_Aに記録。
