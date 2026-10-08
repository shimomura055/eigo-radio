## 管理ID

PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01(委任_05: Fable判定PRODUCTION_WIRED確定のSSOT反映)+ FACTLOCK-WRITER-REDESIGN-TRIAL-01(委任_08: v1/R3/sol/残NG突合/sweep生成物のSSOT反映とcommit)。並行タスク: FACTLOCK委任_04c(sweep評価、`er052_output/factlock_writer_trial_01/sweep_01/eval/`へ書込中。このディレクトリはaddしない・読まない)。他にgit/SSOTを使うagentはなし。

## 性質/到達上限Status/禁止事項

- 性質: SSOT反映+commit(Closeout作業)。Production code変更なし・API課金なし。
- Fable判定(2026-10-08、PM_GOVERNANCE 11-3照合済み): OPEN-241はPRODUCTION_WIRED確定。根拠=受入a〜e充足(正式入口から実行/12 stage・14 callのmodel_id実測が全て6-luna・5.6残存0[KP解説stageはrunner対象外、Phase 0 probeで互換確認済み]/cost.json ¥19.1>0・予算ガード4.70>0/回帰5266/5278で残12件は無関係既知失敗/fail-closed維持・単価未登録例外なし)。O3観測はEN STOP 1/2本(継続観測)。Opus条件C M1〜M6/O1〜O3反映済み。
- 禁止: `git add -A`・amend・rebase・force push。`sweep_01/eval/**`・`eval/_private/**`・`sweep_01/eval/_private/**`はaddしない。Production code編集禁止。
- 時間見込み: 約40分。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一ファイル再読なし。D-1: Grep→範囲Read。G-1: git出力は--porcelain/--stat/--short。F-1: 退避不要。T-0: 委任文を本ファイルへ全文保存しcheck_delegation_prompt.py実行、結果1行記録。T-2: TTSなし。T-3: 課金なし。

## ユーザー指示(原文)

判断7「全6-luna化をProduction方針として進めてOK」(2026-10-08)。名称内番号「Aで良いです」。sweep費用上限¥300(異議なし)。「1本だけ作らせて」「その記事をまずは私に見せて。それ以外はまだ実施しないで」(6-sol R3はN=1のみ)。

## KPI provenance欄

該当なし(記録作業)。

## Opus台帳更新

docs/pm/OPUS_FINDINGS_LEDGER.md: OF-065(M3)をCLOSEOUT_CONFIRMED(Fable判定2026-10-08)へ。FACTLOCK条件A(M1〜M9)・任意レビュー(sweep評価M1〜M7)の行が未登録なら、RESULT_PACKET_FACTLOCK.md・_V2.md・_SWEEP_EVAL.md(存在すれば。04c作成中なら読まない)の台帳文案を元に登録。

## 事前指定Read一覧

- docs/pm/RESULT_PACKET.md 全文
- RESULT_PACKET_FACTLOCK.md / _RESIDUAL.md / _V2.md / _R3.md / _R3_SOL.md / _SWEEP.md の各「SSOT追記文案」節と結果数値
- OPEN_ITEMS.md: Grep OPEN-241|OPEN-242|OPEN-233-SELF-RECOVERY-TRIAL-01
- DECISION_LOG.md: Grep ^## PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01|^## ALL-6-LUNA
- OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md: Grep ^## §10[0-9]
- docs/pm/ACTIVE_TASK.md L1-20

## 事前指定Grep一覧+追記位置・更新位置の手順

- OPEN_ITEMS OPEN-241: Status文字列を PRODUCTION_WIRED(Fable判定2026-10-08確定、受入a〜e充足、O3観測 EN STOP 1/2本継続) に更新、1文追記。
- DECISION_LOG: `## PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01: Fable判定(PRODUCTION_WIRED確定、2026-10-08、委任_05)`(根拠a〜e、KP解説stage未観測の注記、O3観測、切り戻し手順再掲、OPEN-242参照)。続けて `## FACTLOCK-WRITER-REDESIGN-TRIAL-01: ユーザー判断・結果記録(2026-10-08、委任_08)`: ユーザー判断逐語要旨(数値規則(c)・R1/R2 5則・Fable提案ベース・名称内番号A・6-lunaで実施・決定A例外・しきい値なし・面白さNG→禁止誘導最小のsweep方針・ChatGPT R3ヒント・sol N=1のみ)/結果: v1 MEASURED(軽微 JA 0.21・EN 0.32、重大0、面白さ実質9勝35敗、¥173.2[¥23.2超過・T-3運用])、残NG突合(照合検出1/9、照合不整合13文は盲検NGと0重複、EN軽微の半分は翻訳段)、診断(数字2.6倍・常体化・比喩種増・judge誘導語/位置バイアス)、R3-MINIMAL(fresh 8.5/12・MAJOR 0→6、chain 7.0/12・MAJOR 0→4、位置バイアスB勝39/48)、sol N=1(¥1.72、FC 0件、22%短縮、構成組替えなし)、sweep生成33本(完走29・STOP4、¥186.6、評価中)、Opus条件A(M1〜M9)・任意(評価M1〜M7)反映、harness欠陥(phase2 JA再生成でタグ残存=Production採用時要修正)/Status: v1 MEASURED・sweep EVALUATING/Production変更なし・採用判断はユーザー。索引行(L5形式)2行。
- OPEN_ITEMS OPEN-233行末: 「【2026-10-08 FACTLOCK】v1 MEASURED(軽微最少・面白さNG)、sweep 11変種評価中、R3最小指示は6-lunaで事実逸脱増、sol N=1は構成組替えなし。詳細REPORT §(番号)」。
- REPORT 新§(次番号): FACTLOCK v1/残NG突合/診断/R3/sol/sweep生成の統合節(結果表・限界・artifactパス)。sweep評価結果は「評価中、後続§で追記」と明記。
- REPORT_LEDGER: FACTLOCK行追加(初回報告日2026-10-08・§番号・Status)。
- ACTIVE_TASK.md固定ヘッダ: 管理ID=FACTLOCK sweep評価中+OPEN-241 PRODUCTION_WIRED確定、UDR-blocking=判断1〜6保留・sweep結果後の方向判断・OPEN-242修正可否・重大候補人間確認(A2件/B2件)、APPROVED未配線=なし、未回答報告=朝の統合報告(判断1〜6)+前日分3件、次アクション=sweep評価結果報告。

## 実行コマンド全文

cwd=C:\Users\tensh\eigo-radio。
0. .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-08_PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01_05.md --json-out docs\pm\delegation_log\2026-10-08_PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01_05.md_check.json
1. SSOT反映(上記)。
2. commit 1(配線確定): 明示add OPEN_ITEMS.md DECISION_LOG.md docs/pm/OPUS_FINDINGS_LEDGER.md docs/pm/REPORT_LEDGER.md 委任文(+check.json)。メッセージ「PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01: Fable判定PRODUCTION_WIRED確定(受入a〜e充足、E2E完走1本・全12 stage 6-luna実測、O3観測1/2本)」。
3. commit 2(FACTLOCK成果物): 明示add er052_factlock_writer_trial_01_run.py er052_factlock_writer_trial_01_test_01.py er052_factlock_sweep_01_run.py er052_factlock_sweep_01_test_01.py と er052_output/factlock_writer_trial_01/配下のうち DESIGN_01.md PREREGISTRATION.md FIXED_SHAS.json RESULT.md MANIFEST.json briefs/** tools/** runs/** eval/*.md eval/residual_analysis/** v2_design/** r3_minimal_01/** sweep_01/DESIGN_SWEEP_01.md sweep_01/PREREGISTRATION_SWEEP.md sweep_01/variants.json sweep_01/build_variants.py sweep_01/MANIFEST.json sweep_01/tools/** sweep_01/runs/**(eval/_private/・sweep_01/eval/は除外)、docs/pm/opus_l2_review_factlock_writer_trial_01.md docs/pm/opus_l2_review_factlock_sweep_eval_01.md(存在すれば)、FACTLOCK系delegation_log(01/02a/02b/03/04a/04b/04d/05/06/07)、OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md、OPEN_ITEMS.md、DECISION_LOG.md、docs/pm/REPORT_LEDGER.md。巨大ファイル(>5MB)はaddせず一覧報告。メッセージ「FACTLOCK-WRITER-REDESIGN-TRIAL-01: v1 MEASURED(軽微最少・面白さ9勝35敗)、残NG突合・診断・R3最小指示(6-luna事実逸脱増)・sol N=1・sweep生成33本、Opus条件A/任意反映、実費 v1¥173.2/R3¥13.0/sol¥2.0/sweep¥186.6、Production変更なし」。
4. push origin main。

## SSOT追記文

上記Grep手順に記載。

## Git

編集権: DECISION_LOG.md/OPEN_ITEMS.md/OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md/docs/pm/REPORT_LEDGER.md/docs/pm/OPUS_FINDINGS_LEDGER.md/docs/pm/ACTIVE_TASK.md(CURRENT_SPEC/PM_GOVERNANCEは不可)。

## 報告(RESULT_PACKET項目)

docs/pm/RESULT_PACKET.md上書き(ヘッダ: 両管理ID・Status・¥0・commit 1/2 hash)。本文: 反映箇所一覧(ファイル:行)、addしたファイル群の件数とadd除外一覧、REPORT §番号、問題・残作業、check結果、raw URL。
