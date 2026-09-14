## 管理ID

PM-CLOSEOUT-CONSOLIDATION-129
並行タスク衝突確認: 並行タスクなし。Git操作は本タスクのみ。

## 性質/到達上限Status/禁止事項

- 性質: Closeout統合(¥0)。Family C Trial-08成果物のGit記録+OPEN-147/DECISION_LOG/MODEL_ROUTING反映+transcript退避1件+ACTIVE_TASK更新。
- 禁止: API呼び出し/`run_project_regression.py --pattern`に`_test`を含まないglob/`git add -A`・`.`・`stash`・`clean`・`amend`・`rebase`・`force push`/Family Cへの`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`付与/er013_*コード編集/新規OPEN行の追加。
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

> (Trial-08) Trial終了時Status: REJECTED/VALIDATED/USER_DECISION_REQUIRED。VALIDATEDでもProductionへ進まない。費用は開発・Trial費と量産時1記事単価を分けて報告(未確定なら明記)。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_FC8.md` 全文。
2. `EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08_REPORT.md`: Grep `^## ` で節位置を特定し、末尾「SSOT追記文案」節のみRead。
3. `docs/pm/tools/README.md`: Grep `collect_subagent_transcripts` → 使用法のみ。
4. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `^\| OPEN-147 ` → 行末尾へ追記(下記①)。
- `DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-128` で直近エントリ位置・索引書式を確認 → 直後に新エントリ(②)+索引1行。
- `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: Grep -i `trial_07|Trial-07` でFamily C直近行を特定 → 直後にTrial-08行(5記事、gpt-5.6-luna[`er013_output/family_c_future_trial_08/raw_usage_log.jsonl`をGrep `model_id`で実測]、¥3.72、A' skip)を追記。
- transcript退避: session `294958fe-da6e-491c-8a02-4f864d8195c8`、taskId `a049e0b5503111412`。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(管理ID=本タスク、UDR-blocking=4TYPE Voices 2V path不在の対応方針(未回答)/Open Item候補10件の登録範囲(未回答)、UDR-deferred=OPEN-148(HIGH)/OPEN-134等、APPROVED未配線=OPEN-83/145/146(+OPEN-120)、STOP条件=なし、次アクション=ユーザー報告、未回答報告=4TYPE観測(判断1・2)、報告単位Status: Family C=Trial-08 VALIDATED(人間評価待ち) / 4TYPE観測=3/4完了・Voices UDR / Discovery S2=PRODUCTION_WIRED)。
- RESULT_PACKETは`docs/pm/RESULT_PACKET.md`へ上書き。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-129.md --json-out docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-129_check.json`
2. offline確認: `.venv\Scripts\python.exe run_project_regression.py --pattern "er013*_test_*.py"`(期待121/121 PASS)
3. transcript退避: `.venv\Scripts\python.exe docs\pm\tools\collect_subagent_transcripts.py --tasks-dir "C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks" --subagents-dir "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents" --transcripts-dir "docs\pm\transcripts" --only-task-ids a049e0b5503111412 --apply`
4. `git status --porcelain` → 明示add → commit → `git push origin main`(classifierブロック時は同一コマンド最大3回再試行)。

## SSOT追記文

① OPEN-147末尾: 「(EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08、2026-09-14) ユーザー人間評価(Trial-07): 『どれも悪くないが、指定すると少し凝った形になり面白み・分かりやすさが薄れる』→仮説『型を指定せず自由生成の方が面白い』を検証。Hard方針2つのみ(Reader-facing Current Fact禁止=0件が正常/登場人物1〜2人・最大3人、主人公以外は関係性表現)、スケール指定・強制ランキング・新Gateなし、Core Provocationは1〜3案から選定、Writer制約6項目。結果5本: home_robots『便利さが好みを奪う』429語/bci『発話前の意図が検知される』395語/memory『封印した記憶は保存中に変質する』384語/digital_twins『デジタルツインが"本人のため"に選択する』380語/language『翻訳が躊躇を消し母娘が誤解する』375語。全5本CURRENT FACT 0件・leak scan 0件、Fact Safety 3層PASS、人物数2(手動確認)、補助評価Future Leap 2〜3/面白さ3。Trial限定でA' skip(節約≈¥9.47)。開発・Trial費¥3.72(bci技術retry1回含む)、量産単価: 未確定(参考¥0.744/記事、A' skip込み・Batch/TTS除く)。Family C残額¥137.71→¥133.99。分類: VALIDATED(Trial、Production未採用)。Fable直読所見: (i)5本ともTrial-07より平易で耳で追いやすく、仮説を支持(特にlanguage・bci・memory)、(ii)残存パターン: 主人公名がMaya×2/Mara/Mira/Lenaと類似音・重複(home_robotsとlanguageが同名Maya)、bold UIテキスト(CARE HOUSE/UNSPOKEN INTENT/SPEECH SETTINGS等)が5本中4本に登場しTTS時の扱い要検討、開幕『At 7:00/6:10』型が2本、(iii)digital_twinsのAI『Echo』命名はグレーゾーン、(iv)最終判定はユーザー人間評価待ち。」
② DECISION_LOG新エントリ: 「2026-09-14: PM-CLOSEOUT-CONSOLIDATION-129。Family C Trial-08(自由生成5テーマ、VALIDATED、Production未採用)をGit記録・OPEN-147反映。transcript退避1件。」

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add: `er013_family_c_future_writer_08.py`、`er013_family_c_future_provocation_08.py`、`er013_family_c_future_eval_08.py`、`er013_family_c_future_trial_08_run.py`、`er013_family_c_future_qa_test_08.py`、`er013_output/family_c_future_trial_08/`(一式)、`EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08_REPORT.md`、`docs/pm/RESULT_PACKET_FC8.md`、`docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08.md`+`_check.json`、`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-129.md`+`_check.json`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/transcripts/a049e0b5503111412_recovered.jsonl`。
- コミットメッセージ: `PM-CLOSEOUT-CONSOLIDATION-129: Family C Trial-08(自由生成5テーマ、VALIDATED)のGit記録+SSOT反映+transcript退避` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ: 1) commit hash(full)・push結果、2) add件数、3) er013回帰結果、4) transcript退避結果、5) SSOT追記位置、6) 数値照合差異、7) T-0・事前指定外Read、8) STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(並行なし)
