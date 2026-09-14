## 管理ID

EDITORIAL-4TYPE-FOLLOWUP-01-NEWS-B1-ADDITION
並行タスク衝突確認: 並行して Trend再生成(`er014_output/four_type_observation_01/trend/`)・Discovery修正(`.../discovery/`)・SSOT登録タスク(SSOT+Git)が走る。本タスクは`er014_output/four_type_observation_01/news/`配下のみを書き、SSOT・Git・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`を触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_4T_NEWS_B1.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 観測タスクの**生成漏れ補完**(Production正式pathでB1[B1B]を追加生成)。新仕様Trialではない。仕様Status変更なし。
- 実施: テーマ「AI regulation vs AI race」の作成済みVerified Fact Ledger(`er014_output/four_type_observation_01/news/research/verified_fact_ledger.txt`)を再利用し、**Research/Verificationを再実行せず**、`er003_v1_n3_01_articles_generate.run_one_pattern`でB1Bを正式pathどおり生成(editorial_mode=None、News既定、hintなし)。A2既存成果物は無変更。B1の正式QA(Point Overlap/Value QA・Fact Checker・Ledger Deviation・Local Rewrite/diff QA・Directional Precheck)を通常どおり実行。A2/B1のCross-Level Consistency(同一Ledger由来で主張・数値・方向性が矛盾しないか)を既存の仕組みがあればそれで、無ければ主要主張の突合表(手動)で確認。
- 費用上限: ¥50(B1生成+QA。Research再実行禁止)。
- 禁止: 仕様変更/Prompt改善/QA追加・緩和/Research再実行/A2再生成/Git/SSOT/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: B1追加生成に新Production仕様が必要と判明/Fact Safety重大問題/費用上限。

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

> News: B1を即時追加生成。今回NewsはA2しか生成されていなかったが、Productionコードは同一LedgerからA2/B1双方を生成可能である。これは仕様不足ではなく、今回観測タスクの生成漏れ。既存Newsテーマ「AI regulation vs AI race」について、今回作成済みのVerified Fact Ledgerを再利用/Research / Verificationを再実行しない/B1Bを正式Production pathで追加生成/A2は既存成果物を維持/B1の正式QAを実施すること。A2/B1のCross-Level Consistencyも確認。
> コスト報告: Familyごとに「Production 1生成セット総原価」(共通Research/Ledger + A2+B1)を主指標。共通費を50:50配賦した擬似単価は作らない。機械分離できる直接費だけを参考内訳として示す。

## 事前指定Read一覧

1. `er014_output/four_type_observation_01/news/run_news_a2.py` 全文(A2 driver。Research部分を外しB1B生成のみ行う`run_news_b1b.py`を派生)。
2. `er003_v1_n3_01_articles_generate.py`: Grep `^def run_one_pattern|level|b1b|B1B` → run_one_patternのlevel指定方法の該当範囲のみRead。
3. `er014_output/four_type_observation_01/news/observation.json` 全文(A2の費用・token、セット原価の合算用)。
4. `er014_output/four_type_observation_01/aggregate_usage.py`: Grep `add_argument|def ` → 引数一覧のみ(再利用)。
5. `CURRENT_SPEC.md`: Grep `Cross-Level|cross_level|レベル間整合` → 既存のCross-Level Consistency確認手段があれば該当範囲のみRead(無ければ「該当なし」と記録し手動突合)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- driver: `er014_output/four_type_observation_01/news/run_news_b1b.py`(新規。既存Ledger読込→`run_one_pattern`でB1B生成。費用上限¥50ガード)。出力: `er014_output/four_type_observation_01/news/b1b/`配下(記事・QA json)、`reader_facing_article_b1b.txt`、`cost_summary_b1b.json`、`raw_usage_log_b1b.jsonl`(A2のログと混ぜない。既存`raw_usage_log.jsonl`に追記される仕組みなら、開始前の行数を記録し差分で集計)。
- 集計: `aggregate_usage.py`でB1B分の`observation_b1b.json`を生成。さらに`news/production_set_cost.json`(新規)に「Production 1生成セット総原価=Research/Ledger[A2生成時の¥42.52]+A2直接費+B1B直接費+QA+retry+rewrite」の合計と、機械分離できる直接費内訳(Research/Ledger、A2 Writer、B1 Writer、QA[レベル別に分離できる分]、retry、rewrite、その他)を記録。50:50配賦はしない。
- Cross-Level Consistency: `news/cross_level_consistency.md`(新規)に主要主張(日付・数値・因果・断定度)のA2/B1突合表と判定。
- 中間ログ: `er014_output/four_type_observation_01/progress_log.md`に「News B1B: …」1行追記。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-01-NEWS-B1-ADDITION.md --json-out docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-01-NEWS-B1-ADDITION_check.json`
2. 生成: `.venv\Scripts\python.exe er014_output\four_type_observation_01\news\run_news_b1b.py`(driver内でledger_path/out_dir/level="b1b"/budget_jpy=50を固定。全文コマンドと固定値をRESULT_PACKETへ記録)
3. 集計: `.venv\Scripts\python.exe er014_output\four_type_observation_01\aggregate_usage.py --run-dir er014_output\four_type_observation_01\news\b1b --out er014_output\four_type_observation_01\news\observation_b1b.json`(run-dir構成が合わない場合は`--run-dir`を実際のB1B出力dirに合わせ、使ったコマンドを記録)
(回帰不要: Production/Trialコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOpen Item候補(あれば)を列挙。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_4T_NEWS_B1.md`に: 1) status・使用path、2) B1記事(語数・相対パス)、3) B1主要QA結果・retry・Local Rewrite/diff QA発火有無・Directional、4) Cross-Level Consistency判定(突合表の要約、矛盾があれば列挙)、5) actual model_id、6) 費用: **News Production 1生成セット総原価(共通Research/Ledger+A2+B1)=¥xx.xx** と直接費内訳(Research/Ledger ¥42.52[既存]、A2 Writer、B1 Writer、QA、retry、rewrite、その他)、B1追加分の実費、7) API token(B1分)、8) Open Item候補、9) commit対象候補一覧、10) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥50)
- [x] 並行タスク衝突回避あり(news/配下限定・Git操作なし)
