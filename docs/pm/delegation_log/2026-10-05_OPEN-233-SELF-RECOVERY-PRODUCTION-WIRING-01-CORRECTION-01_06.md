# 委任_06 OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-01

親: OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01。並行: 委任_05(ユーザー指示により中止中)。本委任は OPEN_ITEMS.md/REPORT/REPORT_LEDGER.md/Gap文書を編集しない。編集は新規文書1本とDECISION_LOG.md末尾のみ。gitは本委任ファイルのみ明示add。

## 性質/到達上限/禁止事項

- 性質: 0円・調査と記録のみ。有料API実行禁止。(a)ユーザー是正指示をDECISION_LOGへ逐語記録(スクリプト転写)、(b)rep30のStage 1 Checkerが実際にどの構成だったかを記録から確定する。
- Fable判断(逐語記録): 「委任_05の2×2比較(V0×gpt-6-luna/候補×gpt-5.6-luna)は、rep30構成の忠実な再現に必要な原因調査ではなく、Checker/モデルの再選定に当たるため、ユーザー是正指示に従い中止する。既に発生した費用は記録し、結果はRegression参考値として保存のみとする(採否判断に使わない)。今後の作業は『rep30でVALIDATEDされた構成の忠実なProduction再現』に限定し、Checker/モデル候補の新設・比較は行わない。」
- 到達上限: APPROVED_FOR_PRODUCTIONのまま。PRODUCTION_WIREDにしない。
- 禁止: コード変更禁止。CURRENT_SPEC.md/PM_GOVERNANCE.md/OPEN_ITEMS.md/REPORT/Gap文書は編集しない。git add -A/stash/amend禁止。既存M差分・untrackedに触れない。ACTIVE_TASK.md/RESULT_PACKET.mdはaddしない。1回の書き込みは2,500文字以下。

## 作業(要約)

1. T-0保存→check。
2. DECISION_LOG.md末尾に見出し「## 2026-10-05 ユーザー是正指示 OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-01(目的の是正: 比較・再選定ではなくrep30構成の忠実な配線)」+「### ユーザー指示原文(逐語)」(本ログの````ブロックから転写)+「### Fable判断」。
3. rep30 Stage 1実構成の確定(docs/pm/rep30_stage1_provenance_01.md): 38 instance-runをrun単位表化(区分fresh/frozen-reuse/V0-substitute、model_id、prompt構成、schema、pre-check、Stage 2へ渡したclaim件数とseverity、severity_final使用有無)。集計: fresh n、frozen n、V0-substitute n、Production候補構成でfreshされた件数。6 claim(bgroup_B4 4件・safety_A2A3 1件・bgroup_B2_hormuz 1件)の出所。結論でユーザー§5判定をYes/No/部分で答える。
4. commit/push(明示add: DECISION_LOG.md、rep30_stage1_provenance_01.md、委任ログ+check.json)。メッセージ: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-01: ユーザー是正指示を逐語記録、委任_05比較を中止、rep30 Stage 1の実構成(fresh/frozen/V0差替え・model・prompt・schema)をrun単位で確定(委任_06、0円)`

## 実行コマンド

- T-0 check: check_delegation_prompt.py --file 本ログ --json-out 本ログ.md_check.json
- 転写: append_decision_log_from_sources_01.py --dry-run → 本実行
- 集計: er052_output/open233_kpi_recovery_02_offline_01/agg_rep30_stage1_provenance_01.py
- Git: status --porcelain→明示add→commit→push origin main→log -1

## ユーザー指示(原文、全文。転写元)

````
Claude Code 指示
管理ID：OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-01
今回の作業目的を修正する。
ユーザーが正式採用したのは、OPEN-233 rep30でVALIDATEDされた構成をProduction正式経路へ配線することである。
したがって、現行Production Checkerと新Checker候補の優劣を改めて比較し、Checkerやモデルを再選定する作業は今回の目的ではない。
1. 現在進行中の比較について
委任_05で進めている
- V0 × gpt-6-luna
- 新Checker候補 × gpt-5.6-luna
の追加比較は、以下の場合に限り継続してよい。
rep30でVALIDATEDされた構成とProduction候補の挙動差の原因を特定し、同じ構成をProductionへ正しく再現するために必要な場合。
単に、
- どのCheckerが優秀か
- どのモデルがよいか
- Production Checkerを再選定する
ための比較なら中止すること。
不要な追加Trial・API課金を行わない。

2. まず確認すること
rep30について、Stage 1 Checkerが実際にどの構成だったかを正確に確定する。
最低限、
- model_id
- Prompt / developer message
- schema
- deterministic pre-check
- fresh callだったケース
- 過去出力をreuseしたケース
- reuseした場合、その出力を生成したChecker/model
- Stage 2以降へ渡したデータ
を確認する。
特に重要なのは、rep30の29ケースすべてで新Checkerをfresh実行したわけではない可能性である。
その場合、
rep30でVALIDATEDされたもの
と
今回Production候補として作ろうとしているChecker

を混同してはいけない。
3. Production配線の原則
今回やるべきことは、
rep30で実際にVALIDATEDされた仕様・処理をProduction正式pathへ忠実に移すこと。
新しいChecker設計や新しいモデル構成を勝手に追加しない。
Production候補がrep30と違うなら、
「新しい候補を比較して選ぶ」のではなく、「なぜrep30と違っているのか」を特定し、承認済み構成へ合わせること。
4. 現行Productionとの比較の位置づけ
現行Production V0はRegression基準としてのみ使う。
確認目的は、
- 現行で拾えていた重大問題を新Production経路で不当に落としていないか
- 正常記事を壊していないか
である。
V0とrep30候補の勝敗を決めるA/B Trialにはしない。
差が出た場合は、
1. rep30とProduction候補の配線差
2. model/routing差
3. Prompt差
4. reuse/fresh差
5. schema/input差
を調べ、まず実装差を解消すること。
5. 重要な確認
今回報告された、
Production候補Stage 1が、現行V0で検出していた6 claimを見逃した

という事実は無視しない。
ただし、これを理由にChecker再選定へ進むのではなく、
その6件の差が「rep30で承認した構成とProduction候補が一致していないため」なのかを最優先で確認する。
もしrep30自体がその6件についてfresh Stage 1 Checkerを検証しておらず、reuseデータに依存していたため、Productionで使うStage 1 Checkerの正式仕様が未検証だと判明した場合は、
Production wiringの未充足事項としてSTOPして報告すること。
その場合のみ、ユーザー判断が必要かPM側で判断する。
Claude/Fableが独自にChecker仕様を新設してProductionへ入れてはいけない。
6. 今回の到達Status
ユーザー承認済み仕様は引き続き：
APPROVED_FOR_PRODUCTION
である。
以下を満たすまで：
PRODUCTION_WIRED
にしない。
- rep30承認仕様とProduction実装が一致
- Production正式初回path
- retry / fallback / regeneration
- runtime evidence
- Regression / integration test
- actual model_id / routing
- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- Git反映
- Dangling Referenceなし
7. 作業方針
ここからは仕様再選定ではなくProduction wiring作業に戻ること。
必要な比較は、
「承認済みrep30構成をProductionで同じように動かすための原因調査」
に限定する。
それ以外の追加Trial・モデル比較・Checker比較は行わない。
もし承認済みrep30構成そのものにProduction化できない未検証部分が見つかった場合のみSTOPし、事実と影響を報告すること。
````

## 事前指定Read一覧

rep30 Stage 1実構成確定のGrep→範囲Read(runner全文Read禁止)。instance JSONはPythonで一括集計(個別全文Readしない)。er051_output配下はGlob→メタ部分のみ。

## 事前指定Grep一覧+追記位置・更新位置の手順

Grep: stage1_call_used|stage1_recall_miss_substituted|substitute_baseline_on_stage1_miss|stage1_fresh_with_enumeration|def run_stage1|V4A|baseline_parsed|frozen|reuse|er051_output(runner)、V4A|developer|MISCONCEPTION|schema|same_fact_id_locations|classify_deviation_trial(er051)。DECISION_LOG末尾はスクリプト転写。新規文書は新規作成のみ。

## SSOT追記先

DECISION_LOG.md末尾のみ。新規文書 docs/pm/rep30_stage1_provenance_01.md。

## 実行コマンド全文

T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-01_06.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-01_06.md_check.json
転写: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\append_decision_log_from_sources_01.py --dry-run ... → 本実行。
集計: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\agg_rep30_stage1_provenance_01.py
Git: git status --porcelain→明示add→commit→git push origin main→git log --oneline -1

## 固定ブロック

E-1/D-1/G-1/F-1/T-2/T-3は従来どおり(E-1: 範囲遵守、D-1: 有料API禁止、G-1: 明示add、F-1: 報告短縮)。
