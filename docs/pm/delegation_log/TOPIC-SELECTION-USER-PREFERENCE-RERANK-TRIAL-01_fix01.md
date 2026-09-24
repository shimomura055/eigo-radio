## 管理ID
`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`(修正1回目=再開。ユーザー指示2026-09-24: 「`.env`に`JEV_API_KEY`を追加済み。再開。まずJev接続確認を行い、キー本文は表示・log・report・commitに出さない。Jev接続が通った場合のみ、既存の固定Candidate Pool 60件・既存Teacher Data 57件・既存Prompt条件を変えず、Luna/Terra/Sol/Jevの4-way rerankへ進む。Jevのendpoint/auth/schemaが依然として不明な場合はSTOP」)。**並行タスクあり**: 別sonnet-workerが`NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01`(er015_*、標準ACTIVE_TASK/RESULT_PACKET)を実行中。本タスクは`docs/pm/ACTIVE_TASK_RR.md`/`RESULT_PACKET_RR.md`を使い、er015_*に触らない。commit時`index.lock`は10秒待ち再試行(最大3回)、自タスクのファイルのみ明示add。**`docs/pm/ACTIVE_TASK*.md`/`RESULT_PACKET*.md`/`.env`はcommitに含めない**(前回`ACTIVE_TASK_RR.md`が誤commitされているが、今回はその処置をしない)。

## 性質/上限Status/禁止事項(前回委任と同一、変更点のみ明記)
- Trial。到達上限`VALIDATED`。ユーザー評価前に「どのモデルが最良」と結論づけない。Production/SSOT無変更。総費用上限¥150(前回実績¥2.93を含む)。
- **鍵の扱い(最重要)**: `.env`を読む場合は`python-dotenv`(`.venv`に既にあれば)または自前パース(標準ライブラリ)で**プロセス環境へ読み込むだけ**。`.env`の値を`print`/log/JSON/REPORT/RESULT_PACKET/delegation_log/git diffのいずれにも出さない。`.env`の**変数名のみ**(`JEV_`で始まるもの)を列挙してよい(値は禁止)。API responseやエラーメッセージに鍵が含まれる可能性があるため、保存前に鍵文字列の存在チェック(値との完全一致・先頭8文字一致)を行い、含まれていればマスクして保存。commit前に`git diff --cached`に鍵文字列が含まれないことを機械確認(`git diff --cached | findstr /C:"<先頭8文字>"`ではなくPython内で比較し、結果の真偽のみ記録)。**`.env`が`.gitignore`に含まれているか最初に確認し、含まれていなければ`.env`を絶対にaddしない上で報告**。
- **endpoint不明時**: 鍵を推測したhostへ送らない(鍵漏洩リスク)。`.env`内の`JEV_BASE_URL`/`JEV_ENDPOINT`/`JEV_MODEL`等の変数名、Repo内docs、または前回`jev_api_notes.md`で公式endpoint/auth/schemaが確定できない場合は**接続試行せずSTOP**(`stop_reason.json`更新、`USER_DECISION_REQUIRED`)。
- 429/rate limit: 連打禁止、`Retry-After`に従い最大2回まで待機再試行、解決しなければSTOP。Jev失敗時はLuna/Terra/Solを実行しない(前回同様)。
- STOP条件・禁止事項はそれ以外すべて前回委任(`docs/pm/delegation_log/TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01.md`)と同一。

## 固定ブロック
E-1/D-1/G-1/F-1は前回同一。T-0: 本委任文を`docs/pm/delegation_log/TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_fix01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKET_RRへ1行(FAILでも継続)。

## 事前指定Read一覧
- `docs/pm/RESULT_PACKET_RR.md`: 全文(前回の到達点・ファイル配置)。
- `.gitignore`: Grep `\.env`。
- `.env`: **変数名のみ**を`Grep pattern="^JEV_[A-Z_]*=" -o`で取得(値を出さないため`-o`で`JEV_xxx=`の部分だけ)。
- `er016_output/topic_selection_user_preference_rerank_trial_01/jev_probe.json`・`stop_reason.json`・`jev_api_notes.md`(存在すれば): 前回のJev調査内容。
- `er016_topic_selection_user_preference_rerank_trial_01.py`: Grep `def step_jev_probe|def call_jev|JEV_|def step_rerank|--arms|dotenv`→再開に必要な箇所のみ。`.env`読込を追加する場合、`--env-file .env`オプション(既定なし)で読み、値をログしない実装にする。
- `candidate_pool_sha256.json`/`candidate_pool.json`(sha256の再計算一致確認のみ、変更禁止)、`teacher_check.json`(57件確認済み、再チェックは機械確認のみ)。

## 実行手順
### STEP 1 Jev接続確認(1回)
`.env`から`JEV_API_KEY`(+あれば`JEV_BASE_URL`/`JEV_MODEL`)をプロセス環境へ読込→存在真偽のみ記録→endpoint/auth/schemaが確定できる場合のみ、最小request(候補1件・Teacher例5件)を**1回**送信→`jev_probe.json`更新(鍵マスク確認済みで保存: status/latency/response schema/model名/usage・課金情報があれば)。不確定ならSTOP。
### STEP 2 少数件プローブ(5件)でJevのcost/rate limitを確認→`cost_estimate.json`更新(¥150以内の見込みを記録)。
### STEP 3 `--step rerank --arms J,L,T,S`(Jev→Luna→Terra→Sol、Pool sha256一致確認、Prompt前回逐語同一、各armの`api_meta.json`にsha256と`response.model`実値)。Jev用入力はLuna等と同内容をJev schemaへ整形(意味を変えない)、`jev_decision_schema.md`保存。
### STEP 4 `--step assemble`(model_agreement.md: Top20重複6ペア・Spearman 6ペア/各arm top20.json/preference_summary.txt)、評価script dry-run、REPORT §4〜§9・§12更新(§13 `[Fable記入]`は残す)。`USER_EVAL_RERANK_POOL.md`は変更しない(既に60件のブラインド一覧、順序固定)。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --env-file .env --step jev-probe
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --env-file .env --step cost-estimate --budget-jpy 150
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --env-file .env --step rerank --arms J,L,T,S
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step assemble
.venv\Scripts\python.exe er016_rerank_eval_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --user-scores er016_output\topic_selection_user_preference_rerank_trial_01\user_scores_DUMMY.json --dry-run
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_fix01.md --json-out docs\pm\delegation_log\TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_fix01.md_check.json
git status --short
```

## SSOT追記文
なし。

## Git
明示add: `er016_topic_selection_user_preference_rerank_trial_01.py`、`er016_output/topic_selection_user_preference_rerank_trial_01/`配下(**鍵混入なしを機械確認後**)、`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_fix01.md`、同`_check.json`。`.env`・`ACTIVE_TASK*`・`RESULT_PACKET*`は絶対にaddしない。
メッセージ: `TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01: Jev接続確認後、固定Pool 60件・Teacher 57件・同一PromptでLuna/Terra/Sol/Jev 4-way rerankを実行、モデル間一致率・評価資料を作成(Production変更なし)`(STOP時は`STOP:`接頭)。trailer: `Management-ID: TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`

## 報告(RESULT_PACKET_RR)
0. T-0 1. `.gitignore`の`.env`有無、`.env`内JEV_変数名一覧(値なし)、鍵存在真偽 2. Jev endpoint/auth/schemaの出典と確定可否、接続確認結果(status/latency/model名)、rate limit状況 3. 少数件プローブのcost、全体見込み、実績(arm別・合計、¥150以内か) 4. Pool sha256一致、Prompt同一性(前回ファイルとのdiffなし) 5. 各arm`response.model`実値/Jevのmodel名、Top20(4 arm転記) 6. モデル間一致率 7. 鍵混入なしの機械確認結果(真偽のみ) 8. STOP該当の有無 9. `git status --short`、commit SHA、push 10. 一覧外Read/Grepの理由、Open Item候補(事実列挙)。
