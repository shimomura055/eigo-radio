## 管理ID

OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01(委任_02: 報告A〜Eの集計scriptを新設し、旧仕様9 run出力(frozen、比較基準用。正式Evidenceではない)で動作確認・基準値を出す。¥0)。並行タスク: Opus条件Aレビュー(read-only、計画doc対象)。**本委任はgit操作・SSOT編集・runner/checker/テストの変更をしない。** 書き込み先: `er052_output/open233_prod_e2e_01/`(新規: `aggregate_report_abcde_01.py`、出力json/md、ラベル用シート)、`docs/pm/RESULT_PACKET_AGG.md`(新規)、`docs/pm/delegation_log/`。

**作業方式(必須)**: 書き出しは`Write`/`Edit`で小分け(1回40行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを2〜3分割して逐語保存。説明は最小限。

## 性質/到達上限Status/禁止事項

- 性質: 集計ツール作成(¥0、read-only分析)。到達上限: script動作確認済み+旧9 runの基準値表。
- 禁止: 有料API/runner・checker・既存テストの変更/SSOT編集/git操作/旧9 runを「新仕様のEvidence」として扱うこと(基準値=比較用と明記)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 非該当(集計ツール)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-1: 事前指定Read/Grep一覧に従う。一覧外の追加Readはその理由をRESULT_PACKETに1行記録。
T-0: 委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語保存し、check_delegation_prompt.pyを実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。
T-2: 本委任はTTSなし。 T-3: 本委任は¥0のためCap定型文は適用対象外。

## ユーザー指示(原文、報告で必ず出す数値)

> A. Checker: Checker AI判定(候補にした件数/真に問題があった件数/不要に候補化した件数)。Checker機械判定(同3件数)。AI＋機械の関係(AIのみが拾った件数/機械のみが拾った件数/AIと機械の両方が拾った重複件数/重複除外前の延べ件数/重複除外後のChecker総候補件数)。Checker全体で何件を後段へ渡したのかが一目で分かるようにする。
> B. 後段判定: 後段AI(重大/軽微/問題なしの件数。事後評価: 真に重大だった件数/不要に重大判定した件数/真に重大だったのに軽微・問題なしとした件数)。後段の機械判定(今回残すのは数字のみ: 発火件数/AI判定との重複件数/真に重大だった件数/不要に重大化した件数)。
> C. Rewrite: Rewrite発生件数/Rewriteが発生したrun数 / 9 run/必要だったRewrite件数/不要だったRewrite件数/Rewrite後に再修正が必要になった件数。
> D. Human Review: 目標0件。発生時は対象英文/対応するLedger Fact/Checker AI判定/Checker機械判定/後段AI判定/後段機械判定/Rewrite内容/Recheck結果/Human Reviewに到達した直接原因。
> E. Safety・Cost: 真の重大Fact見逃し件数/重大Fact検出件数/1 runごとの費用/9 run合計費用/1 run平均/Rewrite関連費用/Checker関連費用/後段判定関連費用。

## KPI provenance欄

旧9 run基準値: frozen(`er052_output/open233_e2e_acceptance_01/`、旧仕様、比較用のみ)。事後評価ラベルは、(1)既存の推測ラベル(RCA委任_22の35件、`e2e_neg7_rca_extract_01.json`)があればそれを転記し`label_source=rca_22_sonnet_guess`、(2)無いものは`UNLABELED`とし、ラベル用シート(claim一覧)を出力。本委任で新たに推測ラベルを付けない。

## 事前指定Read一覧(要旨)

1. plan_open233_checker_floor_production_e2e_01.md: Grep集計関連のみ。2. 旧E2E出力ディレクトリ一覧→e2e_aggregate.json→run json1件の構造確認。3. e2e_neg7_rca_extract_01.json構造確認。4. floor_fire_analysis_01.py: Grep `def |load|cost`。

## Opus台帳更新

該当なし。

## 事前指定Grep一覧+追記位置・更新位置の手順

- run json内のキー特定: Grep `"source"|"provenance"|"r3"|"r5"|"deterministic"|"coverage_gap"`(Checker AI/機械の区別)、`"floor_reason"|"deterministic_floor"|"changed_"`(後段機械判定)、`"materiality"|"llm_materiality"`(後段AI)、`"rewrite_records"|"guard_ok"|"method"`(Rewrite)、`"stage4_reason"|"escalation"`(Human Review)、`"cost_jpy"|"usage"|"call_log"|"stage"`(費用のstage別分離)。
- 追記位置: 新規ファイルのみ。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_02.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_02.md_check.json`
2. script作成 `er052_output/open233_prod_e2e_01/aggregate_report_abcde_01.py`(引数: --runs-dir/--out-dir/--labels)。A〜Eを上記定義どおりに算出。
3. 動作確認(旧9 run、比較基準): 旧runs-dirに対し baseline_old9 へ出力(labelsはRCA22の35件転記json)。
4. 出力: report_abcde.json / report_abcde.md / label_sheet.csv。
5. git操作なし。

## SSOT追記文

なし。

## Git

git操作なし。SSOT編集権なし。成果物一覧をRESULT_PACKET_AGGに列挙(後続commit対象)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_AGG.md`へ: T-0結果、script入出力仕様、旧9 run基準値表A〜E、取り出せなかった項目、一覧外Read理由、成果物一覧。最終報告は12行以内。
(注: 本ファイルは一部要約保存。初回保存時に要旨化した箇所あり)