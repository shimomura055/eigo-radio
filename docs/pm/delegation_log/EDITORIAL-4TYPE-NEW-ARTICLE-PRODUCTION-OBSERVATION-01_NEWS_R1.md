## 管理ID

EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01(記事1/4: News、Fable修正指示1回目)
並行タスク衝突確認: 並行してEDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07(er013_*とer013_output/のみ、Git操作なし)が走る。本タスクはer013_*に触れない。Git操作なし。SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は編集しない。RESULT_PACKETは`docs/pm/RESULT_PACKET_4T_NEWS.md`へ上書き。

## 性質/到達上限Status/禁止事項

- 性質: 既存Production記事タイプ(News)の**正常生成観測**(新仕様Trialではない)。前回委任はSonnetが「新規Topic用Ledgerの自動Research経路が正式pathに無い」としてSTOPしたが、**Fableが SSOT を照合した結果、以下のとおり先例に従って進める**:
  - DECISION_LOG L941(PM-CLOSEOUT-CONSOLIDATION-71系): 「Hanshin以外の新規News Ledgerを**既存Research正式経路**で作成(新テーマ=in-vivo CAR-T、14件CONFIRMED、費用¥57.89)」。その実装は`er011_news_stage3_new_theme_ledger_trial_09.py`(vfl01.run_researcher/run_verification[OpenAI Responses API web_search]→verified_fact_ledger.txt→`run_one_pattern`)。Discovery「wake before alarm」(`er011_discovery_generalization_wake_before_alarm_trial_12_run.py` L277-322 `run_researcher_for_topic`/`run_verification_for_topic`)も同一手順。
  - CURRENT_SPEC L760「手動供給のみ」は**Trend Production WriterへのLedger自動配線が未統合**という意味であり、Research経路の使用を禁じるものではない(この表記と先例の不一致はOpen Item候補として記録する)。
  - したがって本タスクでは **Step 1: Research/Ledger作成**(`vfl01.build_researcher_prompt(topic=)`→`run_researcher`相当→`build_verification_prompt`→`run_verification`相当、Trial-09/12と同一のclient呼び出し構造、Topicのみ差し替え)→ **Step 2: 記事生成**(`er003_v1_n3_01_articles_generate.run_one_pattern`、editorial_mode=None[News既定]、Trial-09のtopic/ledger_path/out_dir渡し方を踏襲)。これは仕様変更ではなく先例踏襲であり、Researchの費用は「量産時1記事単価」内の「Research/Ledger生成」区分として計上する。
- Topic: **AI regulation vs AI race**(AIの安全性・規制を強める動きと、国家・企業間のAI開発競争との緊張関係を、現在のNewsとして扱う)。Researcherへ渡すtopic文はこの英語Topic+狙いの一文(英語)とし、Sonnet自身の知識で事実を補わない(Ledgerの事実はweb_search由来のCONFIRMEDのみ)。
- レベル: A2のみ(B1は生成しない)。音声化(TTS)なし。
- **仕様変更禁止**: Prompt改善/QA追加/retry方式変更/新Validator/Story構造変更/Model routing変更/Production wiring変更/QA緩和は一切行わない。問題は可能な範囲で生成を完了し「Open Item候補」として報告。Fact Safety上の重大問題(例: Verificationで CONFIRMED件数が極端に少なく記事が成立しない)で正常生成不能な場合のみSTOP。
- 費用上限: 本記事¥130(Research込み・retry込み)。超過見込みで停止し報告。
- 禁止操作: `git add/commit/push`/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`/er013_*・SSOT編集。
- STOP条件: 上記Fact Safety/費用上限/`run_one_pattern`の実行にコード修正が必要と判明(修正せず報告)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(T-0の保存名は`docs/pm/delegation_log/EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_NEWS_R1.md`とする。)
---

## ユーザー指示(原文)

> A. News Topic: AI regulation vs AI race。狙い: AIの安全性・規制を強める動きと、国家・企業間のAI開発競争との緊張関係を、現在のNewsとして扱う。Newsの現行正式仕様・正式Production pathを使用してください。
> 新しい仕様開発や品質改善Trialを勝手に始めないでください。各記事について、現在の正式QAを通常どおり実施する。QAを今回のために緩めないこと。
> 5-A 量産時1記事生成API原価: retryなし部分/retry発生による追加費用/Research・Ledger生成/Writer/QA/rewrite・regenerationを可能な範囲で分ける。表記「量産時1記事単価(Standard同期・今回実測)」。
> 6. API token使用量: provider/actual model_id/input tokens/output tokens/cached input tokens/total tokens/API call回数を記事単位で集計。retryは通常生成分/retry追加分を可能なら分離。

## 事前指定Read一覧

1. `er011_news_stage3_new_theme_ledger_trial_09.py`: Grep `run_researcher|run_verification|verified_fact_ledger|run_one_pattern\(|editorial_mode|topic` → Research→Ledger保存→`run_one_pattern`呼び出しの該当範囲のみRead(引数の渡し方を踏襲する。Focus Module/Point Role hint等のTrial条件分岐は**使わず**、News既定[editorial_mode=None、hint無し]で呼ぶ)。
2. `er011_discovery_generalization_wake_before_alarm_trial_12_run.py` L271-330(`run_researcher_for_topic`/`run_verification_for_topic`とLedger保存の実装。News用に流用)。
3. `er003_v1_n3_01_articles_generate.py`: Grep `^def run_one_pattern` → シグネチャとdocstringのみRead(引数確認)。
4. `er005_cost_logger.py`: Grep `input_tokens|cached|output_tokens|def record` → usageログのフィールド名の範囲のみRead。
5. `er014_output/four_type_observation_01/path_survey.md` 全文(前回自分が作成した下調べ、再利用)。
6. `docs/pm/PM_GOVERNANCE.md`: Grep `15-5|5区分` → 費用報告5区分の定義範囲のみRead。

## 事前指定Grep一覧+追記位置・更新位置の手順

- driver: `er014_output/four_type_observation_01/news/run_news_a2.py`(新規、薄いrunner。Research→Verification→Ledger保存→`run_one_pattern`呼び出しのみ。Production関数のmonkeypatch・再実装禁止。費用上限¥130で停止するガード)。出力先`er014_output/four_type_observation_01/news/`(`research/verified_fact_ledger.txt`+researcher/verification生JSON、`reader_facing_article.txt`、QA結果json、`raw_usage_log.jsonl`、`cost_summary.json`)。
- 集計: `er014_output/four_type_observation_01/aggregate_usage.py`(新規、`--run-dir <dir> --out <json>`引数化、後続3記事で再利用)で`observation.json`を生成: {topic, level, article_type, production_path, model_id(実測、provider別), api_calls, input_tokens, output_tokens, cached_input_tokens, total_tokens, cost_jpy_total, cost_breakdown{research_ledger, writer, qa, rewrite_regeneration, retry_extra}, retry_count, qa_results{各QA名: verdict}, word_count, status, started_at, finished_at}。`logging_context`ラベルで区分を分ける(research/verification/writer/各QA/retry)。
- 中間ログ: `er014_output/four_type_observation_01/progress_log.md`に「News: 開始/終了時刻・費用・token・status」を1行追記。
- `docs/pm/RESULT_PACKET_4T_NEWS.md`を上書き。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_NEWS_R1.md --json-out docs\pm\delegation_log\EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_NEWS_R1_check.json`
2. 生成: `.venv\Scripts\python.exe er014_output\four_type_observation_01\news\run_news_a2.py`(driver内でtopic/out_dir/level="a2"/budget_jpy=130を固定。実際の全文コマンドとdriver内の固定値をRESULT_PACKETへ記録)
3. 集計: `.venv\Scripts\python.exe er014_output\four_type_observation_01\aggregate_usage.py --run-dir er014_output\four_type_observation_01\news --out er014_output\four_type_observation_01\news\observation.json`
(回帰実行は不要: Production/Trialコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETに「Open Item候補」を列挙(少なくとも: CURRENT_SPEC L760『手動供給のみ』表記と先例[Research正式経路による新規Ledger作成]の不一致)。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_4T_NEWS.md`(上書き)に: 1) status(生成成功/PARTIAL/STOP)と使用path(Research経路+`run_one_pattern`、根拠)、2) 記事: level・word count・`reader_facing_article.txt`相対パス、3) Ledger: CONFIRMED件数・Verification結果、4) 主要QA結果(Fact Checker/Ledger Deviation/Local Rewrite・diff QA発火有無/Point Overlap・Value QA各attempt/Directional Precheck)・retry回数・fallback有無、5) actual model_id(provider別)、6) 費用: 量産時1記事単価(Standard同期・今回実測)=¥xx.xx、内訳(Research/Ledger生成・Writer・QA・rewrite/regeneration・retry追加分・retryなし部分)、開発・検証費=¥0(追加API callがあれば別計上)、7) API token: provider/model_id/input/output/cached/total/calls(通常生成分/retry追加分)、8) Open Item候補、9) commit対象候補一覧、10) T-0結果・事前指定外Read(理由付き)・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥130)
- [x] 並行タスク衝突回避あり(er013不可・Git操作なし)
