## 管理ID

OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01(委任_05c: 新仕様E2E 9 runの事後評価[真に問題/不要、真に重大/不要に重大、必要Rewrite/不要Rewrite]を複数workerへ分配するためのラベル付け基準書とシート仕様の事前作成。¥0)。並行タスク: 委任_04(runner/checker/テスト/SSOT編集・commit中)、委任_05a(`er052_output/open233_prod_e2e_01/e2e_run_02.py`等作成中)。**本委任はそれらのファイルを編集しない。git操作・SSOT編集もしない。** 書き込み先: `er052_output/open233_prod_e2e_01/labeling_guide_01.md`(新規)、同`labeling_examples_old9.md`(新規)、`docs/pm/RESULT_PACKET_LABEL.md`(新規)、`docs/pm/delegation_log/`。

**作業方式(必須)**: `Write`/`Edit`で小分け(1回40行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを2〜3分割して逐語保存。説明は最小限。

## 性質/到達上限Status/禁止事項

- 性質: 評価基準の文書化(¥0、read-only)。到達上限: 基準書完成。ラベル付け自体は本委任では行わない(E2E後に委任_06で実施)。
- 禁止: 有料API/コード・SSOT変更/gold・Safety-critical定義の変更/新しいSafety原則の追加(既存の「重大誤解原則」と線引き(委任_55/57、ユーザー正式採用)をそのまま使う)/35件の既存推測ラベルの書き換え(例示としての引用のみ)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 非該当(評価手順書)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果をRESULT_PACKETへ1行記録する(FAILでも作業は継続)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。本委任はTTSなし。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5): TTS実行前4点確認。本委任はTTSなし。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 本委任は¥0のためCap定型文は適用対象外。

## ユーザー指示(原文、報告で必要な事後評価)

> A. Checker: AI判定/機械判定それぞれ「候補にした件数/真に問題があった件数/不要に候補化した件数」。B. 後段AI: 重大/軽微/問題なしの件数と事後評価「真に重大だった件数/不要に重大判定した件数/真に重大だったのに軽微・問題なしとした件数」。後段機械判定(数字のみ): 発火/AI判定との重複/真に重大/不要に重大化。C. Rewrite: 発生件数/発生run数/必要だったRewrite件数/不要だったRewrite件数/Rewrite後に再修正が必要になった件数。E. 真の重大Fact見逃し件数/重大Fact検出件数。

## KPI provenance欄

ラベルは事後評価(Sonnet推測、Fable/ユーザー確認前提)。基準書にprovenance欄(label_source、確認状態)の列を必須化する。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

1. `docs/pm/design_open233_self_recovery_flow_01.md`: Grep `重大誤解原則|§0` →§0の原則文(判定の最初の問い)。
2. 線引き(ユーザー正式採用): `DECISION_LOG.md` Grep `委任_55|線引き|例2` →該当エントリの結論行のみ(BLOCKING/ACCEPTABLEの線引き例: Meta-1/Meta-2、A4-1がACCEPTABLEへ再ラベルされた理由)。`er052_open233_self_recovery_flow_runner_01.py` L9655-L9680(`SAFETY_CRITICAL_CLAIM_DEFS`と委任_55/57コメント、gold 6件の定義)。
3. `docs/pm/rca_open233_e2e_neg7_human_review_01.md`: L27-L31(誤BLOCKING/判断不能/正当の判定例と理由)。
4. `docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`: L38-L60(集計と再分類の判定語彙)。
5. `er052_output/open233_prod_e2e_01/baseline_old9/label_sheet.csv`: 先頭20行(列構成)。`docs/pm/RESULT_PACKET_AGG.md`: Grep `label|ラベル|--labels` →集計scriptが読むラベルjsonの形式。
6. `docs/pm/reclassify_open233_checker_selectivity_02.md`: Grep `境界例|NO_FACT_CLAIM|予測` →境界例の扱い(将来予測・一般傾向・認識推測文)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 追記位置: 新規ファイルのみ。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_05c.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_05c.md_check.json`
2. `labeling_guide_01.md`(§単位で作成): §1 用語定義(真に問題=Ledgerとの食い違い、またはLedgerにない具体的新事実の追加で、学習者に記事の本質について重大な誤解を与えうるもの[重大誤解原則]/軽微=誤りだが本質を損なわない/問題なし=Ledgerと整合、または具体的Factを含まない修辞・比喩・つなぎ・一般論・問いかけ)、「候補にして正しかった(true_problem)」の定義(問題あり[重大または軽微]ならtrue、問題なしならfalse)、「真に重大(true_critical)」の定義(gold 6件の定義+線引き例に照らす)、「必要なRewrite(rewrite_needed)」の定義(Rewrite前の文が真に重大または軽微で修正が妥当だったか)、「再修正要」の定義(集計scriptの定義に合わせる)、判断不能(UNSURE)の扱い(理由必須)。§2 手順(1 claimごと: 対象文→関連fact_id→Ledger原文+notes_for_writerを逐語確認→4観点[主体/相手先・対象/範囲/限定条件]+数値・日付・因果・否定・比較の照合→ラベル+1行理由+label_source)。§3 禁止(推測でLedgerを補完しない/記事全体の印象で判定しない/gold定義を広げない/floorやAIの判定結果を見てから引きずられない=判定前に隠す)。§4 シート形式(集計scriptの`--labels` json形式と`label_sheet.csv`列に合わせる: run/cycle/claim_key/claim_text/fact_id/true_problem/true_critical/severity_eval[重大/軽微/問題なし]/rewrite_needed/reason/label_source/confirmed_by)。§5 分配方法(run単位で3 workerへ、各workerは同じ基準書を使い、workerは互いの結果を見ない。完了後Fableが突合、UNSUREと重大判定はFable/ユーザー確認へ)。§6 所要時間目安(claim数×1〜2分)。
3. `labeling_examples_old9.md`: 旧9 runの35件(RCA推測ラベル付き)から各カテゴリ2〜3例(正当/不要/判断不能)を逐語引用し、基準書に沿った「判定の書き方」の見本を作る(既存ラベルの書き換えはしない)。
4. git操作なし。

## SSOT追記文

なし。

## Git

git操作なし。SSOT編集権なし。成果物一覧をRESULT_PACKET_LABELに列挙(後続commit対象)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_LABEL.md`へ: 1. T-0結果。2. 基準書の構成(§一覧)と用語定義の要点。3. シート形式(列一覧)と集計scriptとの対応。4. 分配案(3 worker、run単位)。5. 一覧外Read理由。6. 成果物一覧。最終報告は8行以内。
