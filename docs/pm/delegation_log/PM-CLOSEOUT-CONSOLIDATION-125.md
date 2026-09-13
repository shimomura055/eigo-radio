## 管理ID

PM-CLOSEOUT-CONSOLIDATION-125
並行タスク衝突確認: 並行タスクなし(両タスク完了済み)。Git操作は本タスクのみ。

## 性質/到達上限Status/禁止事項

- 性質: Closeout統合(¥0、API呼び出しなし)。(A) Family C Trial-06成果物のGit記録+OPEN-147/DECISION_LOG/MODEL_ROUTING反映、(B) transcript退避2件、(C) ACTIVE_TASK固定ヘッダ更新。
- 禁止: API呼び出し/記事生成/`run_project_regression.py --pattern`に`_test`を含まないglob/`git add -A`・`.`・`stash`・`clean`・`amend`・`rebase`・`force push`/Family Cへの`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`付与(Family CはTrial VALIDATED止まり)/er013_*コード編集。
- STOP条件: push失敗が3回続く→報告。

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

> (Future) 今回最大Status: VALIDATED。Production採用は禁止。費用は「開発・Trial費」と「量産時1記事あたり単価」に分けて報告。未確定なら「量産単価: 未確定」と明記。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_FC6.md` 全文(短い)。
2. `EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06_REPORT.md`: Grep `^## ` で節位置を特定し、7節(Story Spark Gate結果)・12節(費用)・末尾「SSOT追記文案」節のみRead。
3. `docs/pm/RESULT_PACKET_S2H.md` L1-35(Discovery確定内容・費用、既にSSOT反映済みのため確認のみ)。
4. `docs/pm/tools/README.md`: Grep `collect_subagent_transcripts` → 使用法の該当範囲のみRead。
5. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `^\| OPEN-147 ` → 行末尾へ追記(下記①)。既存内容は削除しない。
- `DECISION_LOG.md`: Grep `FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01` で直近エントリ位置・索引書式を確認 → 直後に新エントリ「PM-CLOSEOUT-CONSOLIDATION-125」(②)+索引1行。
- `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: Grep `family_c_future_trial_05|Trial-05` → 直近Family C行の直後にTrial-06/06b/06_bmi行(モデルは各`raw_usage_log.jsonl`をGrep `model_id`で実測、費用¥1.21/¥11.19/¥8.76)を追記。
- transcript退避: session `294958fe-da6e-491c-8a02-4f864d8195c8`のtaskId `a14cee879e6287b5d`(Discovery happy path)と`a018dbd5354e380b0`(Family C v6)を`docs/pm/transcripts/`へ(README/前回CONSOLIDATION-124と同じ`--tasks-dir/--subagents-dir/--transcripts-dir/--only-task-ids/--apply`形式)。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(管理ID=本タスク、Status、UDR-blocking=なし[ユーザー判断事項はFable報告で提示]、UDR-deferred=OPEN-134/121(d)等既存、APPROVED未配線=OPEN-83/145/146(+OPEN-120 3Vゲートruntime evidence待ち)、STOP条件=なし、次アクション=ユーザー報告、報告単位Status: Discovery S2=PRODUCTION_WIRED(正式受入済み、正常完走evidence取得) / Family C=Trial VALIDATED v6(Production未採用、ユーザー人間評価待ち))。
- RESULT_PACKETは`docs/pm/RESULT_PACKET.md`へ上書き。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-125.md --json-out docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-125_check.json`
2. offline確認(1回): `.venv\Scripts\python.exe run_project_regression.py --pattern "er013*_test_*.py"`(期待88/88 PASS)
3. transcript退避: `.venv\Scripts\python.exe docs\pm\tools\collect_subagent_transcripts.py --tasks-dir "C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks" --subagents-dir "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents" --transcripts-dir "docs\pm\transcripts" --only-task-ids a14cee879e6287b5d,a018dbd5354e380b0 --apply`
4. `git status --porcelain` / `git diff --stat` → 明示add → commit → `git push origin main`(classifierブロック時は同一コマンドを最大3回再試行)。

## SSOT追記文

① OPEN-147末尾: 「(EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06、2026-09-14) ユーザー人間評価: Trial-05(v5)は『NG、論外』(未来ラベルでも冒頭場面が現在と同じ、Future Leap弱い、わくわく感なし)→QA VALIDATEDより人間評価を優先しv5不採用方向。再設計v6: Provocative Future Premise→Core Provocation(候補5〜10→6軸評価→最も面白くSafety boundary内の案を選定)→Story(制約5項目、約350語A2)→Story Spark Gate(5軸、Fact/語数より上位、FAILなら記事FAIL)→3レイヤーFact Safety(CURRENT FACT=A'厳密/PLAUSIBILITY BRIDGE/IMAGINED FUTURE)。結果: home_robots初回(06)はSpark Gate FAIL(future_leap=1、冒頭に現在統計を置いた設計ギャップ)→最小改善1回(06b)でPASS、BCI一般化(06_bmi)1回でPASS。3 Voicesは目標提示のみで希釈なし。制約項目v5=16→v6=5。Fact Safety 3層overall_pass=True、A' verdict=PASS(REVIEW_REQUIRED未発生)。開発・Trial費¥21.16(06=¥1.21/06b=¥11.19/06_bmi=¥8.76)、量産単価: 未確定。Family C残額¥182.13→¥160.97。分類: VALIDATED(Trial、Production未採用)。Fable直読所見: (i)v6記事はv5より明確にFuture Leap・問いの強さが向上、(ii)ただし06/06bとも本文中に[[FACT]]由来の現在統計文(2023年販売台数)が物語を分断する形で挿入されており没入を削ぐ(CURRENT FACT要件が物語へのデータ挿入を強制している疑い)、(iii)Spark Gate FAILとなった06本文はFable評価では06bと同等以上に面白く、Gateの再現性・判定妥当性は未検証、(iv)最終判定はユーザーの人間評価待ち。」
② DECISION_LOG新エントリ: 「2026-09-14: PM-CLOSEOUT-CONSOLIDATION-125。Family C Trial-06(v6再設計、VALIDATED、Production未採用)をGit記録・OPEN-147反映。Discovery S2は同日FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01で正常完走evidence取得済み・PRODUCTION_WIRED正式受入(SSOT反映済み、本エントリは索引目的)。transcript退避2件。詳細: 各REPORT。」
- 数値はRESULT_PACKET_FC6/REPORTと照合し、差異があれば実値優先+RESULT_PACKETに報告。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add: `er013_family_c_future_provocation_06.py`、`er013_family_c_future_writer_06.py`、`er013_family_c_future_spark_gate_06.py`、`er013_family_c_future_safety_06.py`、`er013_family_c_future_trial_06_run.py`、`er013_family_c_future_qa_test_06.py`、`er013_output/family_c_future_trial_06/`、`er013_output/family_c_future_trial_06b/`、`er013_output/family_c_future_trial_06_bmi/`(各dir一式、大容量音声なし想定)、`EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06_REPORT.md`、`docs/pm/RESULT_PACKET_FC6.md`、`docs/pm/RESULT_PACKET_S2H.md`(未commitなら)、`docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06.md`+`_check.json`、`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-125.md`+`_check.json`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/transcripts/`新規2件、`docs/pm/ACTIVE_TASK.md`。無関係既存差分はaddしない。
- コミットメッセージ: `PM-CLOSEOUT-CONSOLIDATION-125: Family C v6再設計Trial-06(Core Provocation First、VALIDATED)のGit記録+SSOT反映+transcript退避` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ: 1) commit hash(full)・push結果、2) add件数と内訳、3) er013回帰結果、4) transcript退避結果(2件、サイズ)、5) SSOT追記位置、6) 数値照合差異の有無、7) T-0結果・事前指定外Read、8) ACTIVE_TASK更新済み、9) STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(並行なし)
