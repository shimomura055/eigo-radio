## 管理ID
`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`(修正2回目=再開。ユーザーがJev公式API仕様を確認済み)。並行タスクなし。一時ファイルは`docs/pm/ACTIVE_TASK_RR.md`/`RESULT_PACKET_RR.md`。**今回のcommitで`git rm --cached docs/pm/ACTIVE_TASK_RR.md`を実行して追跡解除してよい(ユーザー承認済み、履歴書き換え禁止)**。`.env`/`ACTIVE_TASK*`/`RESULT_PACKET*`はaddしない。

## 性質/上限Status/禁止(前回委任と同一、追加分のみ)
- Trial。到達上限`VALIDATED`。**4-way完了後も「最良モデル」を決めない**(ユーザー実評価との相関が出るまで`USER_DECISION_REQUIRED`)。Production/SSOT無変更。総費用上限¥150(累計¥2.93含む)。
- **Candidate Pool 60件(sha256固定)、Teacher Data 57件、既存評価script(`er016_rerank_eval_01.py`)、`USER_EVAL_RERANK_POOL.md`、Luna/Terra/Sol用Promptは再作成・変更しない。**
- 鍵: 値を表示・log・JSON・REPORT・RESULT_PACKET・delegation_log・commitへ絶対に出さない(前回同様の機械leakチェックをstaged diff・artifact・scriptに対して実施し真偽のみ記録)。
- STOP条件(ユーザー指定・追加): Teacher 57件が32 KiBに収まらない(勝手に要約Ruleへ圧縮しない。STOPし、毎回同一の決定論的subset案を提示)/JevだけTeacher DataやCandidate情報量が大幅に異なる状態になる(API制約上同一条件にできない)/料金不明のまま大規模callが必要で¥150を管理できない/429が解決しない(`Retry-After`に従い最大2回待機、連打禁止)/仕様と実応答が不一致でschemaを特定できない。前回委任のSTOP条件も継続。

## ユーザー提示のJev接続仕様(逐語、これ以外のendpointへ鍵を送らない)
- Base URL: `https://www.jevai.org`
- Endpoint: `POST /api/v1/decisions`
- Auth: `Authorization: Bearer $JEV_API_KEY`(`.env`から読込、値非表示)
- Content-Type: `application/json`
- OpenAI互換APIではない。`/chat/completions`は使用禁止。
- Requestは `state` + `questions`。今回は`model` fieldを省略し、サービス側default Jevを使用。
- Response `{code, message, data}` の `code == 0` を成功条件。
- Request body上限 32 KiB。
- Jev armではNative Decisionsの**score question**を使用し、Candidateの「このユーザーが英語学習用News Audioとして続きを聞きたいと思う度合い」を評価する。
- Teacher Data 57件を`state`にPreference examplesとして直接渡す(32 KiB厳守)。
- 60件を一括送信しない。同一stateを維持した決定論的batchで処理。batch方法が評価結果を変える可能性があれば記録。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_fix02.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKET_RRへ1行(FAILでも継続)。

## 事前指定Read一覧
- `docs/pm/RESULT_PACKET_RR.md`: 全文(到達点)。
- `er016_topic_selection_user_preference_rerank_trial_01.py`: Grep `def step_jev_probe|def call_jev|def step_rerank|def build_prompt|def load_env|JEV_`→Jev client部分を仕様に合わせて実装/置換。Luna/Terra/Sol部分は変更しない。
- `er016_output/topic_selection_user_preference_rerank_trial_01/candidate_pool.json`・`candidate_pool_sha256.json`(sha256再計算一致のみ)、`teacher_check.json`。
- `docs/pm/topic_selection_user_eval_dataset.json`: Grep `"dataset_id"|"topic_ja"|"hook_ja"|"user_score"`で構造確認(前回と同じ57件、内容改変禁止)。
- Jev公式docs: `https://www.jevai.org`配下のAPIドキュメント(Native Decisions / score question / state / questions / answers のschema・usage/課金情報・rate limit)を鍵なしで`curl`取得(最大3ページ)、要点を`jev_api_notes.md`へ記録(URL・取得日時・schema抜粋)。**docsで確認できない項目は「不明」と記録し推測実装しない。**

## 実行手順(ユーザー指定順)
1. **鍵存在確認**(`.env`読込、真偽のみ)。
2. **1件だけ接続確認**: state=Teacher 57件(dataset_id/topic_ja/hook_ja/user_score、Luna等と同一フィールド)+評価目的文(Luna Promptの予測対象文と同義の日本語または英語1〜2文、逐語をREPORTに記録)、questions=Candidate C001の score question 1問(質問文は逐語記録)。`code==0`と`data.answers`の実値・型・スケール(1〜10か0〜1か等)を確認→`jev_probe.json`(鍵マスク確認後保存)。スケールがLuna等の1〜10と異なる場合は線形変換ルールを決めて記録(順位相関には影響しないことを明記)。
3. **5 Candidate probe**(C001〜C005、同一state、questions 5問または1問×5 call — docsの仕様に従い、どちらを採るか理由を記録): payload size(bytes)/latency/rate limit headers/response schema/usage・課金情報の有無を`jev_probe_batch5.json`に記録。**usage・料金情報が返らない場合**: 「Jev cost UNKNOWN」と記録し、残りのJev call数が**15 call以下**なら小規模として続行、超えるならSTOP(理由: ¥150管理不能)。
4. **60件へ拡張**: 決定論的batch(id昇順、1 batchのquestions数はpayloadが32 KiB以内に収まる最大の固定数N、Nを記録)。各batchで同一state。全応答を`arms/J/raw/batch_XX.json`(鍵マスク確認)、`arms/J/predictions.json`(id/predicted_score/変換前raw/reason[返れば])、`top20.json`、`api_meta.json`(endpoint/model省略の旨/response内のmodel名があれば/batch数/N/pool sha256)。batch境界が結果に影響し得る点を`jev_decision_schema.md`に記録。
5. **Luna/Terra/Sol**: 前回設計どおり`--step rerank --arms L,T,S`(同一Pool・同一Teacher・前回逐語Prompt、`response.model`実値記録)。
6. `--step assemble`(model_agreement.md 4 arm 6ペア、preference_summary)、評価script dry-run(変更なし)。REPORT §4〜§9・§12更新(§13は`[Fable記入]`のまま)。
7. 情報量の同一性確認: Jevに渡したCandidateフィールド(id/topic_ja/summary_ja/媒体)とTeacherフィールドが、Luna等に渡した内容と**byte単位で同一**(文字列比較)であることを機械確認し真偽を記録。32 KiBのために削る必要が出た場合は削らずSTOP。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --env-file .env --step jev-probe
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --env-file .env --step jev-probe-batch5
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --env-file .env --step cost-estimate --budget-jpy 150
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --env-file .env --step rerank --arms J
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step rerank --arms L,T,S
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step assemble
.venv\Scripts\python.exe er016_rerank_eval_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --user-scores er016_output\topic_selection_user_preference_rerank_trial_01\user_scores_DUMMY.json --dry-run
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_fix02.md --json-out docs\pm\delegation_log\TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_fix02.md_check.json
git rm --cached docs\pm\ACTIVE_TASK_RR.md
git status --short
```

## SSOT追記文
なし。

## Git
明示add: `er016_topic_selection_user_preference_rerank_trial_01.py`、`er016_output/topic_selection_user_preference_rerank_trial_01/`配下(鍵leakチェック後)、`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_fix02.md`、同`_check.json`。`git rm --cached docs/pm/ACTIVE_TASK_RR.md`を同一commitに含める。
メッセージ: `TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01: Jev Decisions API(score question、決定論的batch)接続後、固定Pool 60件・Teacher 57件でLuna/Terra/Sol/Jev 4-way rerankを実行、一致率・評価資料作成(ACTIVE_TASK_RR追跡解除、Production変更なし)`(STOP時`STOP:`接頭)。trailer: `Management-ID: TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`

## 報告(RESULT_PACKET_RR)
0. T-0 1. 鍵存在真偽、docs取得URLと確認できた/できなかった項目 2. 1件接続: HTTP status/`code`/`data.answers`実値・型・スケール/latency 3. 5件probe: payload bytes/latency/rate limit headers/usage・課金情報の有無/採用したbatch方式と理由 4. Teacher 57件のstate内bytes、batch数N、32 KiB遵守の証跡 5. 情報量同一性(byte比較)真偽 6. 各arm `response.model`実値(Jevはresponse内model名 or 「default(省略)」)、Top20(4 arm転記) 7. モデル間一致率(Top20重複6ペア・Spearman 6ペア) 8. 費用: Luna/Terra/Sol実績、Jev(usage有無、UNKNOWNならその旨)、合計と¥150判定 9. 鍵leakチェック真偽、STOP該当有無、`git status --short`、commit SHA、push、ACTIVE_TASK_RR追跡解除結果 10. 一覧外Read/Grep理由、Open Item候補(事実列挙)。
