FABLE-DELEGATION-MARKER: HR-QUEUE-TEST-CONTAMINATION-FIX-委任_02-20261022

# 委任(HR-QUEUE-TEST-CONTAMINATION-FIX-01 委任_02: 単体テストが監査ログ`er011_output/attempt_history.jsonl`へtest行を追記している疑い(er021系)の確認と隔離。既存仕様内の自律修正。API 0・JPY0)

## 管理ID
HR-QUEUE-TEST-CONTAMINATION-FIX-01 委任_02(OPEN-447。並行: 別agentがStage 2 Closeout(`er100_*closeout*`、OPEN-441行、UDR、DECISION_LOG、OPUS_FINDINGS_LEDGER)を作業中。共有SSOT(`OPEN_ITEMS.md` OPEN-447行のみ・`REPORT_LEDGER.md`)は`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち。`er100_*`・`er006_output/**`には触らない)。

## 性質/到達上限Status/禁止事項
- 性質: test隔離(不具合是正)+記録。到達Status: OPEN-447=`FIXED_RECORDED(attempt_history含む)`。Opus Gate: 非該当。費用: JPY0。
- 修正範囲(11-8): 範囲内=`*_test*.py`のwriter隔離(attempt_history/HR queue/telemetryへProductionパスで書くtestの差替え)、隔離検証test、OPEN-447/REPORT_LEDGER追記。範囲外=Production code挙動変更、`attempt_history.jsonl`本体の編集・削除(append-only監査ログ。混入行はsidecar `er011_output/attempt_history_exclusions_01.json`に行番号・theme_id・timestamp・根拠を記録するのみ)。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。他agentの未commit差分を混ぜない(`attempt_history.jsonl`は作業tree上`M`のまま=未commit差分。触らない)。

## 事実
- 委任_01(commit a73d6d3ad)でer026 testのHR queue/attempt_history書込は隔離済み。その検証中に`attempt_history.jsonl`へ+5〜7行(theme_id=`wiring_theme_asrw2/asrw3/flx2`、2026-10-22 14:01:00〜14:01:11)が増え、同時刻に`er021_en_asr_semantic_equivalence_production_wiring_01_test_01`等が実行されていた(RESULT_PACKET_HRQFIX1、PNPS9 `r3/protect_note.json`)。
- OPEN_ITEMS:831付近の過去記録: `run_project_regression.py --pattern er011*_test*.py`が`attempt_history.jsonl`へtest fixtureを追記する旨の既知記述あり(委任文作成時点の要約。該当行をGrepで確認)。

## 実行内容
1. 特定: `wiring_theme_asrw2|wiring_theme_asrw3|wiring_theme_flx2` を`*_test*.py`/`er0*.py`でGrepし、書込元test(と経路: `er011_human_review_lock_01.py:112 ATTEMPT_HISTORY_PATH`等)を`file:行`で確定。`er011*_test*.py`の既知件も確認。
2. 是正: 該当testの`setUpModule`/fixtureで`ATTEMPT_HISTORY_PATH`(および同経路のHR queue/telemetry)をtmpへ差替え(委任_01のer026と同じ方式)。横展開: `ATTEMPT_HISTORY_PATH|attempt_history` を`*_test*.py`でGrepし、未隔離の全testを同様に隔離。隔離検証test(実行前後で`attempt_history.jsonl`の行数・sha256不変)を各対象へ1件追加または共通helper化。
3. 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er021*_test*.py"`、`--pattern "er011*_test*.py"`、修正した他のpattern。実行前後で`attempt_history.jsonl`/HR queue/telemetryの行数・sha256が不変であることを記録(実行前後のsha256を明記)。
4. sidecar: 2026-10-22 14:01の追記行(+本日分で特定できたtest由来行)を`er011_output/attempt_history_exclusions_01.json`に記録(行番号・timestamp・theme_id・根拠・管理ID)。過去分の全件特定は不要(範囲が広い場合は「本日分のみ」と明記し、過去分は注記)。
5. SSOT: `OPEN_ITEMS.md` OPEN-447に追記(attempt_history側の原因・是正・横展開結果・sidecar・影響=監査ログの件数集計のみ)。`REPORT_LEDGER.md`1行。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_HR-QUEUE-TEST-CONTAMINATION-FIX-01_委任_02.md`(Nは`FABLE-DELEGATION-MARKER: HR-QUEUE-TEST-CONTAMINATION-FIX-委任_02-20261022`を含むAgent tool_useの通番、275前後。先頭行で一致確認)。
6. commit→push→到達確認。`RESULT_PACKET_HRQFIX2.md`。

## Git
- 明示add: 修正testファイル、追加test/helper、sidecar json、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、delegation_log。
- commit: `HRQFIX 委任_02: 単体テスト(er021系ほか)の監査ログattempt_history書込を隔離+再発防止test、混入行sidecar、本体無変更、¥0`。

## 報告(RESULT_PACKET_HRQFIX2.md)
原因(file:行)/是正・横展開一覧/回帰結果と前後sha256/sidecar要約/影響範囲/RESULT_PACKET 4行/raw URL。