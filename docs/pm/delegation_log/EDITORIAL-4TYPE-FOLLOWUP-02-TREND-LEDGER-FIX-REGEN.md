## 管理ID

EDITORIAL-4TYPE-FOLLOWUP-02-TREND-LEDGER-FIX-REGEN
並行タスク衝突確認: 並行して News B1追加(`.../news/`)・Discovery修正(`.../discovery/`)・SSOT登録タスク(SSOT+Git)が走る。本タスクは`er014_output/four_type_observation_01/trend/`配下のみを書き、SSOT・Git・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`を触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_4T_TREND_FIX.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: **判明済みFactのLedger修正+正式pathでの再生成**(新仕様Trialではない、仕様Status変更なし)。
- 背景(ユーザー判断): 前回Trend生成で、Ledger/記事に「Google XR glasses are still a development-stage demonstration」相当の記述が残った一方、Fact Checkerは「Googleが2026-05-19に2026年秋発売を公式発表済み」というResearch時点で既に存在した事実を検出した。これは時間経過による陳腐化ではなく**上流Research/Ledgerの取りこぼし**として扱う。
- 実施手順: (1)**再確認**: 当該事実(Google Android XRメガネの発売時期の公式発表)をGoogle公式等の信頼できるsourceで再確認する。Sonnet自身にはweb検索ツールが無いため、既存の`vfl01.build_verification_prompt`/Verification呼び出し(OpenAI web_search)を「当該1件+関連する既存Ledger該当fact」に限定して実行し、URL・発表日・内容を取得する(Research全体の再実行は禁止)。確認できなければSTOP。(2)**Ledger修正**: 確認できた事実関係に基づき`verified_fact_ledger.txt`を修正(旧Ledgerは`research/verified_fact_ledger_v1_before_fix.txt`として保存、修正版は`research/verified_fact_ledger.txt`を上書きし、差分を`research/ledger_fix_diff.md`に記録[旧fact→新fact、根拠URL・日付])。矛盾する旧factは削除または修正し、関連するfactの断定度も整合させる。(3)**再生成**: 修正版Ledgerを共通Fact源として、Trend正式path`er006_pool_pilot_01_writer.run_writer_for_theme(editorial_mode="trend_synthesis", trend_gate_checklist=...)`で**B1+A2の両方をWriterから再実行**(旧記事の局所置換は禁止)。Fact Checker/Ledger Deviation/Local Rewrite・diff QA/Point Overlap・Value QA/Directional Precheckを通常どおり実行。A2/B1片側だけを直してcloseしない。旧成果物は`trend/run1_before_fix/`へ退避(削除しない)。
- 費用上限: ¥80(限定Verification+B1/A2再生成+QA)。
- 禁止: Research全体の再実行/仕様変更/Prompt改善/QA追加・緩和/Git/SSOT/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: 当該事実を信頼できるsourceで確認できない/Ledger修正だけではFact矛盾を解消できない(再生成後もFact Checker FAIL)/費用上限/新仕様が必要。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> Trend: Fact Ledgerを修正して記事を再生成。まずGoogle公式等の信頼できるsourceで当該事実を再確認すること。確認できた事実関係に基づき、Verified Fact Ledgerを修正する。その修正Ledgerを共通Fact源として、B1/A2の両方を正式Production pathで再生成すること。旧記事を局所置換するだけではなく、修正版LedgerからWriterを再実行する。Fact Checker / Ledger Deviation / その他既存正式QAも通常通り実行。A2/B1片側だけを直してcloseしない。
> 最終成果物: 修正Ledger/再生成B1/再生成A2/Fact Checker結果/旧Factとの差分/1 Production生成セット原価。
> コスト報告: Trend Production 1生成セット(A2+B1)=¥xx と表示。共通費の50:50配賦はしない。

## 事前指定Read一覧

1. `er014_output/four_type_observation_01/trend/run_trend_a2.py` 全文(前回driver。Research部を「限定Verification」に置き換え、Ledger修正→再生成を行う`run_trend_fix_regen.py`を派生)。
2. `er014_output/four_type_observation_01/trend/research/verified_fact_ledger.txt` 全文(修正対象)。
3. `er014_output/four_type_observation_01/trend/a2/`配下: Glob `*fact_check*.json` → Fact Checker FAILの生JSON全文(検出した事実・URL・日付の一次情報)。
4. `er003_v1_en_direct_vfl_01_generate.py`: Grep `^def build_verification_prompt|VERIFICATION_JSON_SCHEMA|VERIFICATION_DEVELOPER_MESSAGE` → 限定Verificationに必要な範囲のみRead。
5. `er014_output/four_type_observation_01/trend/trend_gate_checklist.json` 全文(再生成時に再判定して更新)。
6. `docs/pm/RESULT_PACKET_4T_TREND.md` L57-80(前回QA結果、比較用)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 退避: `trend/run1_before_fix/`へ前回の`a2/`・`b1b/`・`reader_facing_article*.txt`・`run_result.json`・`observation.json`・`cost_summary.json`・`raw_usage_log.jsonl`をコピー(元は上書きされる前にコピー)。
- driver: `trend/run_trend_fix_regen.py`(新規。限定Verification→Ledger修正[差分記録]→`run_writer_for_theme`再実行→集計。費用上限¥80ガード)。
- 出力: `trend/`直下に再生成後の`a2/`・`b1b/`・`reader_facing_article.txt`(A2)・`reader_facing_article_b1b.txt`・`run_result.json`・`cost_summary.json`・`raw_usage_log.jsonl`(前回分と混ざる場合は行数差分で分離)。`trend/production_set_cost.json`(新規): 「Trend Production 1生成セット(A2+B1)総原価」=前回Research/Ledger ¥48.73+今回限定Verification+今回A2/B1 Writer+QA+retry+rewrite。参考として「初回run1(FAIL含む)総額¥87.98」も併記し、本修正runの実費を別行に。
- Fact差分: `trend/research/ledger_fix_diff.md`。
- 中間ログ: `progress_log.md`に「Trend fix: …」1行追記。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-02-TREND-LEDGER-FIX-REGEN.md --json-out docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-02-TREND-LEDGER-FIX-REGEN_check.json`
2. 実行: `.venv\Scripts\python.exe er014_output\four_type_observation_01\trend\run_trend_fix_regen.py`(driver内でtopic/out_dir/editorial_mode="trend_synthesis"/budget_jpy=80を固定。全文コマンドと固定値をRESULT_PACKETへ記録)
3. 集計: `.venv\Scripts\python.exe er014_output\four_type_observation_01\aggregate_usage.py --run-dir er014_output\four_type_observation_01\trend --out er014_output\four_type_observation_01\trend\observation_fix.json`
(回帰不要: Production/Trialコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOpen Item候補(あれば)を列挙。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_4T_TREND_FIX.md`に: 1) status(A2/B1それぞれOK/NG)、2) 再確認結果(source URL・発表日・内容、限定Verificationの生JSONパス)、3) Ledger差分(旧fact→新fact、削除/修正/追加の一覧)、4) 再生成A2/B1(語数・相対パス)、5) 主要QA結果(Fact Checker verdict[A2/B1]・Ledger Deviation・Local Rewrite/diff QA発火・Overlap/Value・Directional)・retry回数、6) Trend Gate再判定、7) actual model_id、8) 費用: **Trend Production 1生成セット(A2+B1)総原価=¥xx.xx**(内訳: Research/Ledger[初回¥48.73]+限定Verification+A2 Writer+B1 Writer+QA+retry+rewrite。機械分離できない分は「共通」と明記、50:50配賦禁止)、本修正runの実費、9) API token(本run)、10) Open Item候補、11) commit対象候補一覧、12) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥80)
- [x] 並行タスク衝突回避あり(trend/配下限定・Git操作なし)
