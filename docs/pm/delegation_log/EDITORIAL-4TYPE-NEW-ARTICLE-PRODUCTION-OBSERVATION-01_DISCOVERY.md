## 管理ID

EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01(記事3/4: Discovery S2)
並行タスク衝突確認: 並行タスクなし(News/Trend記事は完了済み)。本タスクもGit操作を行わない。SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は編集しない。RESULT_PACKETは`docs/pm/RESULT_PACKET_4T_DISCOVERY.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 既存Production記事タイプ(Discovery S2、`PRODUCTION_WIRED`)の**正常生成観測**。新仕様Trialではない。生成成功を理由にいかなる仕様Statusも変更しない。
- Topic: **Why can silence feel uncomfortable?**
- 正式path: `er003_discovery_focus_staged_production_01.run_one_pattern_staged_discovery_focus()`(opt-in `editorial_mode="discovery_focus_staged"`、Focus→Stage 1 Main Story+QA→Stage 2 Point Role Planning→Stage 3 Points+EC→結合→Overlap/Value QA→記事全体Fact Checker/Ledger/Local Rewrite/diff QA→Directional Precheck)。前回の正常完走evidence(`er011_output/discovery_s2_production_runtime_evidence_02/run_happy_path_a2.py`)と同じ薄いdriver方式(monkeypatch・再実装なし)。
- Ledger供給(Fable判断、News/Trend記事と同じ先例踏襲): Research/Verification(`vfl01.build_researcher_prompt`/`build_verification_prompt`+web_search、News driverと同一構造、topicのみ差し替え)でVerified Fact Ledgerを作成→上記正式関数へ投入。Sonnet自身の知識で事実を補わない。
- **改善禁止(ユーザー明示)**: 新しい改善Trialを行わない。Point Overlap retryによるコスト上振れ(OPEN-148、HIGH、意図的defer)は今回の生成中に**勝手に最適化しない**(retryが発生したらそのまま記録)。
- レベル: A2のみ。音声化(TTS)なし。
- **仕様変更禁止**: Prompt改善/QA追加/retry方式変更/新Validator/Story構造変更/Model routing変更/Production wiring変更/QA緩和は一切行わない。問題は可能な範囲で生成を完了し「Open Item候補」として報告。Fact Safety上の重大問題で正常生成不能な場合のみSTOP。fail-closed(NG_REVIEW_REQUIRED)で停止した場合は再生成せず、その結果を記録して報告。
- 費用上限: 本記事¥140(Research込み・retry込み。前回happy path実測¥55.30+Research約¥40〜45を想定)。超過見込みで停止し報告。
- 禁止操作: `git add/commit/push`/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`/er013_*・SSOT編集。
- STOP条件: Fact Safety重大問題/費用上限/正式関数の実行にコード修正が必要と判明(修正せず報告)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(T-0の保存名は`docs/pm/delegation_log/EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_DISCOVERY.md`とする。)
---

## ユーザー指示(原文)

> C. Discovery Topic: Why can silence feel uncomfortable? 現行Production Wired済みのDiscovery S2、Focus→Stage 1 Main Story→Stage 2 Point Role Planning→Stage 3 Pointsの正式Production pathを使用してください。新しい改善Trialは行わないこと。Point Overlap retryによるコスト上振れ問題は別HIGH Open Itemとして管理し、今回の記事生成中に勝手に最適化しないでください。
> 各記事について、現在の正式QAを通常どおり実施する。QAを今回のために緩めないこと。5-A 量産時1記事生成API原価(retryなし部分/retry追加分/Research・Ledger生成/Writer/QA/rewrite・regeneration)。6. API token使用量。7. Claude Code側の利用量(取得できる実測値/取得できない値/代替指標)。8. 各記事開始前後でusage snapshot、中間ログ保存。

## 事前指定Read一覧

1. `er011_output/discovery_s2_production_runtime_evidence_02/run_happy_path_a2.py` 全文(前回正常完走driver。Ledger/topicパスを新規Research出力へ差し替えて流用)。
2. `er014_output/four_type_observation_01/news/run_news_a2.py`: Grep `def |researcher|verification|verified_fact_ledger` → Research→Verification→Ledger保存の関数範囲のみRead(流用)。
3. `er014_output/four_type_observation_01/trend/run_trend_a2.py`: Grep `claude_usage|measure_delegation|collect_subagent` → Step 0の実装があればその範囲のみRead(なければ`er014_output/four_type_observation_01/claude_usage_log.md`全文を読み書式を揃える)。
4. `er014_output/four_type_observation_01/aggregate_usage.py`: Grep `add_argument|def |retry_occurred` → 引数・関数一覧・retry判定箇所のみRead(Trend記事で判明した「ネスト型run_result.jsonでretry_occurredをfalse誤検出」の限界を踏まえ、Discovery記事では`audit/stage_trace.json`から retry回数を直接読む補助処理を**driver側またはaggregate_usage.pyの新規オプション`--stage-trace <path>`として追加**してよい[集計ツールの改善は仕様変更に当たらない])。
5. `docs/pm/RESULT_PACKET_4T_TREND.md` L1-60(Trend記事の書式・費用区分に揃える)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- **Step 0(Claude Code側利用量、¥0)**: Trend委任(taskId `a5bdd52c4daad7ab8`)のtranscriptを退避し、`measure_delegation_task.py`で累積usage(input/output/cache_read/cache_write/tool_uses/turns)を集計して`er014_output/four_type_observation_01/claude_usage_log.md`に行追加(Trend行。Fable通知の最終ターン値: tokens 124,254・tool_uses 46・1,238秒を併記)。取得不能な値は「取得不能」と明記し推定しない。
- driver: `er014_output/four_type_observation_01/discovery/run_discovery_a2.py`(新規。Research→Verification→Ledger保存→`run_one_pattern_staged_discovery_focus()`呼び出し。費用上限¥140ガード)。出力先`er014_output/four_type_observation_01/discovery/`(`research/verified_fact_ledger.txt`+生JSON、`reader_facing_article.txt`、`audit/stage_trace.json`、各QA生JSON、`raw_usage_log.jsonl`、`cost_summary.json`)。
- 集計: `aggregate_usage.py --run-dir er014_output/four_type_observation_01/discovery --out .../discovery/observation.json`(+必要なら`--stage-trace`)。工程別区分: research/verification/stage1(writer+QA)/stage2/stage3+EC/overlap・value QA/final Fact Checker/Ledger/Local Rewrite・diff QA/Directional。retry追加分=Stage 1再生成・Stage 2-3 retryに要した不使用round分(前回evidenceの「不使用round0=¥21.20」と同じ定義)。
- 中間ログ: `er014_output/four_type_observation_01/progress_log.md`に「Discovery: 開始/終了時刻・費用・token・status」を1行追記。
- `docs/pm/RESULT_PACKET_4T_DISCOVERY.md`は新規作成。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_DISCOVERY.md --json-out docs\pm\delegation_log\EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_DISCOVERY_check.json`
2. Step 0退避: `.venv\Scripts\python.exe docs\pm\tools\collect_subagent_transcripts.py --tasks-dir "C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks" --subagents-dir "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents" --transcripts-dir "docs\pm\transcripts" --only-task-ids a5bdd52c4daad7ab8 --apply`
3. Step 0集計: Trend記事のRESULT_PACKETに記録された`measure_delegation_task.py`の全文コマンドと同形式で`docs\pm\transcripts\a5bdd52c4daad7ab8_recovered.jsonl`を対象に実行(実際のコマンドをRESULT_PACKETへ記録)。
4. 生成: `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_a2.py`(driver内でtopic/out_dir/level="a2"/budget_jpy=140を固定。全文コマンドと固定値をRESULT_PACKETへ記録)
5. 集計: `.venv\Scripts\python.exe er014_output\four_type_observation_01\aggregate_usage.py --run-dir er014_output\four_type_observation_01\discovery --out er014_output\four_type_observation_01\discovery\observation.json`(`--stage-trace`を追加した場合はその実値も付ける)
(回帰実行は不要: Production/Trialコード変更なし。aggregate_usage.pyは観測用ツールであり回帰対象外。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETに「Open Item候補」を列挙。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_4T_DISCOVERY.md`に: 1) status(OK/NG_REVIEW_REQUIRED/STOP)と使用path、2) 記事: level・word count・相対パス、3) Ledger: CONFIRMED件数・Verification結果、4) Stage別経過(`stage_trace.json`要約: Stage 1回数・escalation有無・Stage 2-3 retry回数・各QA verdict・Local Rewrite/diff QA発火有無・Directional結果)、5) actual model_id(provider別)、6) 費用: 量産時1記事単価(Standard同期・今回実測)=¥xx.xx、内訳(Research/Ledger・Writer[Stage1/2/3]・QA・rewrite/regeneration・retry追加分[不使用round]・retryなし部分)、開発・検証費=¥0(あれば別計上)、7) API token(provider/model_id/input/output/cached/total/calls、通常/retry分離)、8) Step 0のClaude Code側集計(Trend行)、9) Open Item候補(OPEN-148該当のretry発生有無を含む)、10) commit対象候補一覧、11) T-0結果・事前指定外Read(理由付き)・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥140)
- [x] 並行タスク衝突回避あり(並行なし・Git操作なし)
