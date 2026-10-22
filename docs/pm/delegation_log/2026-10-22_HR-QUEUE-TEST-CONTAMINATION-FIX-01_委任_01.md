FABLE-DELEGATION-MARKER: HR-QUEUE-TEST-CONTAMINATION-FIX-委任_01-20261022

# 委任(HR-QUEUE-TEST-CONTAMINATION-FIX-01 委任_01: 単体テストがProductionのHuman Review queueへmock行を書き込んでいた問題の是正[test隔離]+混入行のsidecar記録。既存仕様内の自律修正(PM_GOVERNANCE 10-2-a)。API 0・JPY0)

## 管理ID
HR-QUEUE-TEST-CONTAMINATION-FIX-01 委任_01(発見元=PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 第2巡 S2R-02(b)。並行: 別agentがStage 2 第3巡(`er100_*_r3_*`、`user_test/pnps_stage2_hr7_listen_03/`)を実行中でOPEN-441行・REPORT_LEDGER・OPUS_FINDINGS_LEDGERを編集する。共有SSOTは`git status`→該当行再Grep→自分の行だけ→即add+commit。`index.lock`は30秒待ち。`er100_*`・`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`本体には触らない[本体の行削除・編集禁止、読み取りとsidecarのみ])。

## 性質/到達上限Status/禁止事項
- 性質: 不具合是正(test隔離)+記録。到達Status: `FIXED_RECORDED`。Opus Gate: 非該当(test隔離・sidecar追加のみ、Production処理フロー不変)。
- 修正範囲(11-8): 範囲内=`er026_post_slowdown_cascade_rescue_01_test_01.py`(mockがProductionのHR queueパスへ書かないよう隔離)、同種の他testの横展開確認(Grep)、sidecar `er006_output/audio_retry_cascade_prod_01/human_review_queue_exclusions_01.json`(混入25行の特定子とその根拠)、OPEN_ITEMS新規項目。範囲外=HR queue本体の行削除/編集、Production code(`er006_*`/`er011_*`)の挙動変更、HR件数集計ロジックの変更(必要なら提案のみ)。
- 費用/日次: JPY0。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止。他agentの未commit差分を混ぜない。

## 事実(第2巡の確認、`docs/pm/RESULT_PACKET_PNPS8.md` S2R-02(b))
- HR queue 113行中25行(22%)は`wav_path`が`er026_pscr_outer_*`(mkdtemp)で、`er026_post_slowdown_cascade_rescue_01_test_01.py:250`のmock出力。ASR文字列「Mello said.」/「Mellow said.」がテストのmock入力と完全一致し、音声実体なし。対象7語のHR事象58のうち25(43%)、Melos 36 lookupのうち25がこの混入。
- 影響: HR件数・HR率の集計(PM報告・Trial母数)が水増しされる。ユーザー向け音声・Production判定には影響なし(実害=計測の歪みのみ)。

## 実行内容
1. 原因特定: 当該testがProductionのqueueパスへ到達する経路(mockの範囲外のwriter、環境変数/既定パス)を特定し、`file:行`で記録。
2. 是正: testがProductionパスへ一切書かないよう隔離(例: queue writerのパスをtmp配下へmonkeypatch/環境変数で差し替え、またはwriter自体をmock)。**同種の経路を持つ他test**をGrep(`human_review_queue|audio_retry_cascade_prod_01` in `*_test*.py`)し、同じ問題があれば同様に隔離。回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er026*_test*.py"`と、隔離の検証(test実行前後でHR queueの行数・sha256が不変であることを確認するtestを1件追加)。
3. sidecar: `human_review_queue_exclusions_01.json`に、混入25行の特定子(行番号・timestamp・wav_path・ASR文字列)と根拠(test mockとの一致)・作成日・作成管理IDを記録。本体は無変更(backupも不要=無変更のため)。HR件数集計を行う既存script(Grep `human_review_queue.jsonl` in `*.py`、Production以外の集計/report用)があれば、sidecarを除外に使えるよう**提案のみ**(改修はしない)をRESULT_PACKETに書く。
4. SSOT: `OPEN_ITEMS.md`新規項目(最新番号+1)「HR-QUEUE-TEST-CONTAMINATION-FIX-01」Status `FIXED_RECORDED`(事実・影響範囲[計測のみ]・是正内容・sidecar・残課題[集計scriptのsidecar対応は提案]・HR件数を過去に報告した箇所への注記=「2026-10-22以前のHR queue由来の件数は最大25行の単体テスト混入を含み得る」)。`docs/pm/REPORT_LEDGER.md`1行。DECISION_LOGは書かない。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_HR-QUEUE-TEST-CONTAMINATION-FIX-01_委任_01.md`(Nは`FABLE-DELEGATION-MARKER: HR-QUEUE-TEST-CONTAMINATION-FIX-委任_01-20261022`を含むAgent tool_useの通番、272〜273前後。先頭行で一致確認)。
5. commit→push→到達確認。`ACTIVE_TASK.md`固定ヘッダ(短く)。`RESULT_PACKET_HRQFIX1.md`。

## 事前指定Read/Grep
- Read: `er026_post_slowdown_cascade_rescue_01_test_01.py:200-300`、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl:87-113`(読み取りのみ)。
- Grep: `human_review_queue` in `er006_*.py`/`er011_*.py`(writerの既定パス)、`human_review_queue|audio_retry_cascade_prod_01` in `*_test*.py`、`OPEN-44[0-9]|OPEN-45[0-9]` in `OPEN_ITEMS.md`。

## Git
- 明示add: 修正したtestファイル、追加test、sidecar json、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、delegation_log。
- commit: `HRQFIX 委任_01: 単体テスト(er026)がProduction HR queueへmock行25件を書いていた問題をtest隔離で是正+混入行sidecar記録、HR queue本体無変更、¥0`。

## 報告(RESULT_PACKET_HRQFIX1.md)
原因(file:行)/是正内容/横展開結果/回帰結果/sidecar内容の要約/影響範囲(計測のみ・音声無影響)/集計scriptへの提案/RESULT_PACKET 4行/raw URL。