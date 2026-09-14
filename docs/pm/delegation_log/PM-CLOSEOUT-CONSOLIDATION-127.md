## 管理ID

PM-CLOSEOUT-CONSOLIDATION-127
並行タスク衝突確認: 並行してEDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01(News再委任、`er014_output/`と`docs/pm/RESULT_PACKET_4T_NEWS.md`・`docs/pm/delegation_log/*_NEWS_R1*`のみ、Git操作なし)が走る。本タスクは`er014_output/`と`docs/pm/RESULT_PACKET_4T_*`を**addしない・触らない**。Git操作は本タスクのみ。

## 性質/到達上限Status/禁止事項

- 性質: Closeout統合(¥0)。Family C Trial-07成果物のGit記録+OPEN-147/DECISION_LOG/MODEL_ROUTING反映+transcript退避2件+ACTIVE_TASK更新。
- 禁止: API呼び出し/`run_project_regression.py --pattern`に`_test`を含まないglob/`git add -A`・`.`・`stash`・`clean`・`amend`・`rebase`・`force push`/Family Cへの`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`付与/er013_*コード編集/`er014_output/`のadd。
- STOP条件: push失敗3回→報告。

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

> (Trial-07) Trial終了時: REJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれか。VALIDATEDでもProductionへ進まない。費用は「開発・Trial費」と「量産時1記事単価」を分けて報告。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_FC7.md` 全文(短い)。
2. `EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07_REPORT.md` L516-572(費用・量産単価)とL675-720(SSOT追記文案)。
3. `docs/pm/tools/README.md`: Grep `collect_subagent_transcripts` → 使用法のみ。
4. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `^\| OPEN-147 ` → 行末尾へ追記(下記①)。
- `DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-126` で直近エントリ位置・索引書式を確認 → 直後に新エントリ(②)+索引1行。
- `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: Grep `family_c_future_trial_06` → 直近Family C行の直後にTrial-07行(home_robots 3本¥9.20/bci 3本¥14.06、model_idは`er013_output/family_c_future_trial_07/raw_usage_log.jsonl`をGrep `model_id`で実測)を追記。
- transcript退避: session `294958fe-da6e-491c-8a02-4f864d8195c8`、taskId `a8650d882bfda363f`(Trial-07)と`ae39a6a0807fea6e1`(4TYPE News初回、STOPで完了済み)。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(管理ID=本タスク、UDR-blocking=なし、UDR-deferred=OPEN-148(HIGH)/OPEN-134/121(d)等既存、APPROVED未配線=OPEN-83/145/146(+OPEN-120)、STOP条件=なし、次アクション=4TYPE観測(News→Trend→Discovery→Voices)進行中、報告単位Status: Discovery S2=PRODUCTION_WIRED / Family C=Trial-07 VALIDATED(Production未採用、ユーザー人間評価待ち) / 4TYPE観測=News再委任中)。
- RESULT_PACKETは`docs/pm/RESULT_PACKET.md`へ上書き。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-127.md --json-out docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-127_check.json`
2. offline確認: `.venv\Scripts\python.exe run_project_regression.py --pattern "er013*_test_*.py"`(期待102/102 PASS)
3. transcript退避: `.venv\Scripts\python.exe docs\pm\tools\collect_subagent_transcripts.py --tasks-dir "C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks" --subagents-dir "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents" --transcripts-dir "docs\pm\transcripts" --only-task-ids a8650d882bfda363f,ae39a6a0807fea6e1 --apply`
4. `git status --porcelain` → 明示add → commit → `git push origin main`(classifierブロック時は同一コマンド最大3回再試行)。

## SSOT追記文

① OPEN-147末尾: 「(EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07、2026-09-14) ユーザー人間評価(v6): BCI=良い(1側面Story成立、ただしもっと派手・大きな未来も期待)/Robot=惜しい/本文への現在統計挿入は明確にNG。方針変更: Reader-facing本文へのCURRENT FACT最低1件契約を撤廃(既定0件、Fact SafetyはQA側)。Trial-07: 同一テーマをIntimate/Societal/Radical+Second-order/Inversionレンズで候補生成(home_robots 15件・bci 11件)→LLM強制ランキング(同順位禁止)→各スケール1本ずつ生成(home_robots 3本: The House That Remembers 387語/The Robot's Second Job 393語/When the House Chooses 401語、bci 3本: Before She Speaks 378語/The Moment Before the Move 382語/Which Me Is Me? 348語)。全6本CURRENT FACT 0件、Spark Gate(補助)・Fact Safety 3層PASS、Writer制約5項目(v6と同数)、Plausibility Pass等の新Gateなし。追加レンズ(E_inversion)はhome_robotsで僅差2位だが4本目は未生成。開発・Trial費¥23.26(home_robots¥9.20/bci¥14.06、うちFACT文0件でもFact Checker A'が実行され¥11.36)、量産単価: 未確定(参考: 記事1本平均¥2.27〜2.47[Research/QA周辺工程除く])。Family C残額¥160.97→¥137.71。分類: VALIDATED(Trial、Production未採用)。Fable直読所見: (i)6本ともv6より一段強く、スケール差が読み味の差として明確(Intimate=故人の習慣を守る家/Societal=privacy vs protect/Radical=目標だけ与えられた家が価値を解釈)、(ii)BCI Societal(法廷での運動意図)・Radical(認知プロファイル)はFuture Leapが特に大きい、(iii)残存パターン: 6本中5本が『At seven/7:10 each morning…』で開幕、BCI 3本の主人公名が全て『Mara』(LLMの反復癖、修正せず記録)、(iv)最終判定はユーザー人間評価待ち。」
② DECISION_LOG新エントリ: 「2026-09-14: PM-CLOSEOUT-CONSOLIDATION-127。Family C Trial-07(発想スケール比較、VALIDATED、Production未採用)をGit記録・OPEN-147反映。CURRENT FACT本文契約撤廃はユーザー判断(2026-09-14)。transcript退避2件。」

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add: `er013_family_c_future_provocation_07.py`、`er013_family_c_future_writer_07.py`、`er013_family_c_future_trial_07_run.py`、`er013_family_c_future_qa_test_07.py`、`er013_output/family_c_future_trial_07/`(一式)、`EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07_REPORT.md`、`docs/pm/RESULT_PACKET_FC7.md`、`docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07.md`+`_check.json`、`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-127.md`+`_check.json`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/transcripts/`新規2件。(`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は.gitignore対象のためaddしない。)
- コミットメッセージ: `PM-CLOSEOUT-CONSOLIDATION-127: Family C Trial-07(発想スケール比較、6記事、VALIDATED)のGit記録+SSOT反映+transcript退避` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ: 1) commit hash(full)・push結果、2) add件数、3) er013回帰結果、4) transcript退避結果、5) SSOT追記位置、6) 数値照合差異、7) T-0・事前指定外Read、8) STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(er014不可・RESULT_PACKET_4T不可)
