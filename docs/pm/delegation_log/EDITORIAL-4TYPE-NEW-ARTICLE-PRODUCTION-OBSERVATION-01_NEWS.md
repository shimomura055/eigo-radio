## 管理ID

EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01(記事1/4: News)
並行タスク衝突確認: 並行してEDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07(er013_*とer013_output/のみ、Git操作なし)が走る。本タスクはer013_*に触れない。本タスクもGit操作を行わない(4記事完了後にFableがCONSOLIDATIONで統合)。SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は編集しない。RESULT_PACKETは`docs/pm/RESULT_PACKET_4T_NEWS.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 既存Production記事タイプ(News)の**正常生成観測**。新仕様Trialではない。生成成功を理由にいかなる仕様のStatusも変更しない。
- 主目的(ユーザー): (1)現行記事タイプの実出力をユーザーが確認できる状態にする、(2)Production相当の1記事生成コストを観測、(3)1記事生成でClaude Code側がどの程度利用量を消費するか観測。
- Topic: **AI regulation vs AI race**(AIの安全性・規制を強める動きと、国家・企業間のAI開発競争との緊張関係を、現在のNewsとして扱う)。Newsの現行正式仕様・正式Production pathを使用。
- レベル: 正式pathの既定がB1+A2一体なら両方生成(無効化しない)、レベル選択可能ならA2を生成(B1は生成しない)。音声化(TTS)は行わない(記事本文のみ)。
- **仕様変更禁止**: Prompt改善/QA追加/retry方式変更/新Validator/Story構造変更/Model routing変更/Production wiring変更を一切行わない。QAを緩めない。問題を発見したら可能な範囲で生成を完了し「Open Item候補」として報告。安全性・Fact Safety上の重大問題で正常生成不能な場合のみSTOP。
- 費用上限: 本記事¥120(retry込み)。超過見込みで停止し報告。費用区分は「量産時1記事単価(Standard同期・今回実測)」と「開発・検証費」(今回は原則¥0、正式path確認のための追加API callがあれば別計上)を混ぜない。
- 禁止操作: `git add/commit/push`/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`/er013_*・SSOTの編集/Trial専用スクリプトによる生成(正式path以外)。
- STOP条件: 正式Production pathがCURRENT_SPEC上で特定できない、または存在するスクリプトが現行コードで動かず修正が必要(→修正せずUSER_DECISION_REQUIREDで報告)/費用上限/Fact Safety重大問題。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(T-0の保存名は`docs/pm/delegation_log/EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_NEWS.md`とする。)
---

## ユーザー指示(原文)

> 以下4テーマについて、新規記事を各1本生成してください。今回の主目的は、1. 現在の各記事タイプの実出力をユーザーが確認できる状態にする 2. Production相当の1記事生成コストを観測する 3. 1記事生成作業でClaude Code側がどの程度トークン/利用量を消費するか観測する ことです。新しい仕様開発や品質改善Trialを勝手に始めないでください。
> A. News Topic: AI regulation vs AI race。狙い: AIの安全性・規制を強める動きと、国家・企業間のAI開発競争との緊張関係を、現在のNewsとして扱う。Newsの現行正式仕様・正式Production pathを使用してください。
> 各記事について、現在の正式QAを通常どおり実施する(Fact QA/Ledger・Evidence整合/overlap・value QA/directional・editorial QA/retry・fallback/level・structure validation等)。QAを今回のために緩めないこと。
> 費用: 5-A 量産時1記事生成API原価(retryなし部分/retry発生による追加費用/Research・Ledger生成/Writer/QA/rewrite・regenerationを可能な範囲で分ける。表記「量産時1記事単価(Standard同期・今回実測)」)/5-B 開発・Trial/検証費(別計上)。
> 6. API token使用量: provider/actual model_id/input tokens/output tokens/cached input tokens/total tokens/API call回数を記事単位で集計。retryは通常生成分/retry追加分を可能なら分離。
> 8. 各記事開始前: API cost baseline。終了後: API cost delta、token delta。1本終わるごとに中間ログへ保存。

## 事前指定Read一覧

1. `CURRENT_SPEC.md`: Grep `News Major|News Daily|正式Production|Production経路|editorial_mode` → Newsの正式Production path(スクリプト名・CLI・既定レベル・既定QA)を定義している範囲のみRead(全文禁止)。
2. 上記で特定した正式Production runnerスクリプト: Grep `add_argument|def main|__main__` → CLI引数・既定値の範囲のみRead(新規Topicでの実行に必要な引数を確定するため)。
3. `er005_cost_logger.py`: Grep `^def (record|install|init_logger)|input_tokens|cached|output_tokens` → usageログの記録フィールド名の範囲のみRead(token集計のため)。
4. `docs/pm/PM_GOVERNANCE.md`: Grep `15-5|5区分` → 費用報告5区分の定義範囲のみRead。
5. `er011_output/discovery_s2_production_runtime_evidence_02/cost_summary.json`(費用集計の出力形式の参考)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Step 0(¥0、全4タイプ共通の下調べ、後続3記事の委任で再利用する): `CURRENT_SPEC.md`をGrep `Trend Synthesis|Discovery Focus S2|Voices|3V|2 Voices|two voices|B-Family` して、Trend/Discovery S2/Voicesの正式Production path(スクリプト・editorial_mode・既定レベル)と、**Voicesの正式仕様が3 Voices限定か2 Voicesをサポートするか**を該当行範囲のみReadして`er014_output/four_type_observation_01/path_survey.md`に表で記録(スクリプト名・関数名・CLI・根拠行番号・2 Voices可否と根拠)。実行は行わない。
- 出力先: `er014_output/four_type_observation_01/news/`(新規)。正式pathの出力先が固定されている場合はそちらで生成し、完了後に`reader_facing_article*.txt`・QA結果json・`raw_usage_log.jsonl`・`cost_summary.json`をこのdirへコピー(元は残す)。
- 記事単位ログ: `er014_output/four_type_observation_01/news/observation.json`に {topic, level(s), article_type, production_path(スクリプト/関数), model_id(実測), api_calls, input_tokens, output_tokens, cached_input_tokens, total_tokens, cost_jpy_total, cost_breakdown{research_ledger, writer, qa, rewrite_regeneration, retry_extra}, retry_count, qa_results{各QA名: verdict}, word_count, status, started_at, finished_at} を保存。
- 中間ログ: `er014_output/four_type_observation_01/progress_log.md`に「News: 開始時刻/終了時刻/費用/token/status」を1行追記(新規作成)。
- `docs/pm/RESULT_PACKET_4T_NEWS.md`は新規作成。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_NEWS.md --json-out docs\pm\delegation_log\EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_NEWS_check.json`
2. 正式path実行: CURRENT_SPECで特定した正式runnerを`.venv\Scripts\python.exe <正式runner>.py <Topic・レベル・出力先等の引数実値>`で実行(引数実値はRead 2で確定し、実際に使った全文コマンドをRESULT_PACKETへ記録)。TTS/音声化フラグがあれば無効化(記事本文のみ)。
3. token/費用集計: `raw_usage_log.jsonl`から記事単位で集計する小スクリプトを`er014_output/four_type_observation_01/aggregate_usage.py`として作成(後続3記事でも再利用できるよう`--run-dir <dir> --out <json>`引数化)し、`.venv\Scripts\python.exe er014_output\four_type_observation_01\aggregate_usage.py --run-dir er014_output\four_type_observation_01\news --out er014_output\four_type_observation_01\news\observation.json`で実行。
(回帰実行は不要: コード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETに「Open Item候補」を列挙する(あれば)。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_4T_NEWS.md`に: 1) status(生成成功/PARTIAL/STOP)と使用した正式path(スクリプト・関数・CURRENT_SPEC根拠行)、2) 記事: level・word count・`reader_facing_article`の相対パス、3) 主要QA結果(Fact QA/Ledger/overlap・value/directional・structure)と retry回数・fallback有無、4) actual model_id(実測、provider別)、5) 費用: 量産時1記事単価(Standard同期・今回実測)=¥xx.xx、内訳(retryなし部分/retry追加分/Research・Ledger/Writer/QA/rewrite・regeneration)、開発・検証費=¥(あれば)、6) API token: provider/model_id/input/output/cached/total/calls(通常生成分/retry追加分を可能なら分離)、7) Step 0のpath_survey結果要約(特にVoices 2V可否と根拠)、8) 新たに見つかった問題(品質/コスト/retry/routing)をOpen Item候補として列挙、9) commit対象候補一覧、10) T-0結果・事前指定外Read(理由付き)・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり(正式runnerの引数はRead 2で確定し全文記録)
- [x] 禁止事項・費用上限あり(¥120)
- [x] 並行タスク衝突回避あり(er013不可・Git操作なし)
