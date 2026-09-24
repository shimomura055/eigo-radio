## 管理ID
`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`(修正3回目=最終。ユーザー方針変更2026-09-25: **Jevは正式にDEFERRED**。理由: TypeSafe公式Jevは現在新規登録不可・公式API access取得不可・非公式Jevサービスは比較対象に使用しない。Luna/Terra/Solの3-way Rerankを先行実行)。**並行タスクあり**: 別sonnet-workerが`NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01`(er015_*、標準ACTIVE_TASK/RESULT_PACKET)を実行中。本タスクは`docs/pm/ACTIVE_TASK_RR.md`/`RESULT_PACKET_RR.md`を使い、er015_*に触らない。commit時`index.lock`は10秒待ち再試行(最大3回)。`git status --short`で他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない(`ACTIVE_TASK_RR.md`は前回commitで既に追跡解除済み。未解除ならこのcommitで`git rm --cached`、履歴書き換え禁止)。

## 性質/到達上限/禁止
- Trial。到達上限`VALIDATED`。**3-way完了時は`USER_DECISION_REQUIRED`でSTOP**(ユーザー評価前にwinner・Production採用を決めない)。
- **再作成禁止・そのまま使用**: Teacher Data 57件/Candidate Pool 60件(sha256 `fe39660b643f6081…`、`candidate_pool_sha256.json`と再計算一致を確認)/Source Gate結果/contamination check/`USER_EVAL_RERANK_POOL.md`/`user_eval_id_map.json`/`er016_rerank_eval_01.py`。
- Jevへの接続・呼び出しは**一切行わない**(鍵も読まない。`--env-file`不使用)。既存Jev client実装は削除せず、`--arms`にJが含まれた場合は「DEFERRED」で即終了するようにguard文言のみ更新。
- 費用上限**¥100**(暴走防止目的。数円単位でSTOPしない。予期しない大量call・loopのみSTOP)。Terra単価は`pricing_snapshot.json`にUNKNOWNなら「UNKNOWN(tokens実測のみ)」と記録。Web Search禁止。SSOT編集はOPEN_ITEMS.mdのみ(下記C)。`git add -A`/`stash`/`amend`禁止。
- STOP条件(ユーザー指定): Candidate Poolが変わる/Teacher Dataが変わる/モデル間でPrompt条件が揃わない/追加Searchが必要/¥100超過見込み/新しいSelection仕様が必要/予期しない大量call。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_fix03.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKET_RRへ1行(FAILでも継続)。

## 事前指定Read一覧
- `docs/pm/delegation_log/TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01.md`: Grep `STEP 3 Preference Prompt`→その節(developer文・user Prompt逐語・schema・arm定義・batch規則)を該当行範囲Read。**このPromptを逐語で実装する(新規設計しない)。**
- `docs/pm/RESULT_PACKET_RR.md`: 全文(前回到達点)。
- `er016_topic_selection_user_preference_rerank_trial_01.py`: Grep `def cmd_rerank|def call_openai|def build_|responses.create|def _price|def step_assemble|json_schema`→L/T/S分岐の実装位置とOpenAI呼び出し・cost関数(Pool作成時のLuna分類callで使ったもの)を流用。
- `er016_output/topic_selection_user_preference_rerank_trial_01/candidate_pool.json`(id/topic_ja/summary_ja/媒体をPromptへ)、`docs/pm/topic_selection_user_eval_dataset.json`(dataset_id/topic_ja/hook_ja/user_scoreをPromptへ、57件)。
- `er016_news_hook_model_comparison_01.py`: Grep `gpt-5.6-terra|gpt-5.6-sol|model=`→Terra/Solの呼び出し実績(model名文字列・effort指定の書き方)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna/sol/terra単価。
- `OPEN_ITEMS.md`: Grep `OPEN-17[0-9]|Jev|RERANK|TOPIC-SELECTION|ENGLISH|META-SOURCE|ENTERTAINMENT-PRODUCTION-LINE|REFERENCE-PROCESS|SEARCH-TRIAL-03|CONT-02|R25|BASELINE-REPRO|CORE-IDEA|TOPIC-LUNA|ITERATIVE-01|Terra`→最大番号・既存項目の有無・書式。

## 実行手順
### (A) 3-way rerank
1. Pool sha256再計算一致、Teacher 57件件数一致を機械確認(不一致ならSTOP)。
2. 初回委任STEP 3のPromptを逐語実装(developer `You predict how much one specific listener would want to keep listening to an English-learning news audio piece about each topic.`、user本文逐語、`[Rated examples]`に57件を`dataset_id / topic_ja / hook_ja / user_score`、`[Candidates]`に60件を`id / topic_ja / summary_ja / 媒体`、JSON schema `{"preference_summary": string, "predictions": [{"id","predicted_score","reason"}]}`)。effort medium、web_searchなし。**3モデルで入力文字列が完全同一**(sha256をapi_metaに記録)。60件で1 callに収まる想定(分割が必要なら3モデル同一分割、理由記録)。
3. Arm L=`gpt-5.6-luna`、T=`gpt-5.6-terra`、S=`gpt-5.6-sol`。各`response.model`実値・response_id・tokens・latency・JPY(Terra UNKNOWNならtokensのみ)。60件すべてにscoreがあるか検証(欠落があれば同一Promptで**1回のみ**再実行、理由記録)。
4. 保存: `arms/{L,T,S}/predictions.json`(id/predicted_score/reason)、`top20.json`、`top10.json`、`preference_summary.txt`、`api_meta.json`。
5. `--step assemble`: `model_agreement.md`(Top20重複数・Top10重複数・全60件Spearman、3ペア)、全件predicted score表(3列)`predicted_scores_all.md`。評価script dry-run(変更なし)。`USER_EVAL_RERANK_POOL.md`は無変更(モデル名・scoreを載せない)。

### (B) Jev DEFERRED記録
- `er016_output/.../jev_deferred.md`: official TypeSafe Jev access unavailable(新規登録不可)/non-official wrapper(`www.jevai.org`)は比較対象に使用しない/access取得後、同じ60件・同じTeacher Data・同じ評価条件で追加測定可能(Pool sha256・Prompt・schema参照)/現在の3-way結果はJev未比較。既存`jev_probe*.json`・`jev_api_notes.md`は履歴として残す。
- OPEN_ITEMS.md: 新規1件(次番号)「Jev arm DEFERRED / NON-BLOCKING(TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01)」に上記4点を記録。Production採用判断ではない旨明記。

### (C) 旧Trial UDRの整理(ユーザー指示: 現行方針でsuperseded/deferredのものをnon-blockingとして整理。新しい判断を要求せず、再Trial・Production採用もしない)
OPEN_ITEMS.mdに新規1件(次番号)「旧Trial USER_DECISION_REQUIRED整理(2026-09-25、NON-BLOCKING)」を追加し、以下を列挙(各行: 管理ID / 旧UDR内容の要約 / 整理区分 / 根拠)。既存OPEN項目に同内容があれば行内で参照し重複記載しない。
- SUPERSEDED(Advanced=Natural English Adaptation採用[CURRENT_SPEC行829、OPEN-177]により英語直接生成ルートは非採用): `NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01`(C2/B再現Trial・英語Prompt候補確定)、`NEWS-META-ENGLISH-ONLY-TRIAL-01`(モデル差arm)、`NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`(contract単離Trial)、`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`(full_story_part2 ASR対応(a)/(b)/(c)・WIRING (a')→OPEN-177の配線作業へ引き継ぎ)、`NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01`素材テスト、`NEWS-BASELINE-REPRO`(ChatGPT素材提供)、`NEWS-CORE-IDEA`(保留)。各TrialのVALIDATED確認は「記録上VALIDATED(Trial上限)、Production非採用」として扱う。
- DEFERRED(Topic選定はRERANK方式[本Trial]の結果待ち、固定レーン/逐次探索Searchの追加Trialは保留): `TOPIC-SELECTION-SEARCH-TRIAL-03`(17件評価・Trial-03b)、`TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01`(9件評価・2回目探索・逮捕/事故/訃報除外方針・OPEN-174へUGC追加)、`TOPIC-SELECTION-CHATGPT-REPRO-01-CONT02`、`R25`、`TOPIC-SELECTION-LUNA-01`。ユーザー評価一覧(`USER_EVAL_TRIAL03_20.md`/`USER_EVAL_REFPROC_20.md`)は任意提出のまま保持。
- DEFERRED(事実確認のみ): Terra単価の出典確認(pricing_snapshot UNKNOWN)、旧Trial約17件のDECISION_LOG一括反映。
- 上記IDの管理ID名がRepo内の実名と異なる場合は`Grep <ID断片> glob="*_REPORT.md" -l`で実名に修正して記載(推測で作らない。見つからないIDは「REPORT未発見」と記す)。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step verify-fixed
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step cost-estimate --budget-jpy 100 --arms L,T,S
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step rerank --arms L,T,S --budget-jpy 100
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step assemble
.venv\Scripts\python.exe er016_rerank_eval_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --user-scores er016_output\topic_selection_user_preference_rerank_trial_01\user_scores_DUMMY.json --dry-run
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_fix03.md --json-out docs\pm\delegation_log\TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_fix03.md_check.json
git status --short
```

## SSOT追記文
OPEN_ITEMS.mdのみ(上記B・C)。CURRENT_SPEC/DECISION_LOG無変更。

## Git
明示add: `er016_topic_selection_user_preference_rerank_trial_01.py`、`er016_output/topic_selection_user_preference_rerank_trial_01/`配下、`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_REPORT.md`(§4〜§12更新、§13 `[Fable記入]`維持)、`OPEN_ITEMS.md`、`docs/pm/delegation_log/TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_fix03.md`、同`_check.json`。
メッセージ: `TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01: Jev DEFERRED(公式access不可、非公式不使用)としてLuna/Terra/Solの3-way rerankを固定Pool 60件・Teacher 57件・同一Promptで実行、一致率・評価資料作成、旧Trial UDRをOPEN_ITEMSでsuperseded/deferred整理(Production変更なし)`
trailer: `Management-ID: TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`

## 報告(RESULT_PACKET_RR)
0. T-0 1. Teacher 57件・Pool sha256一致 2. 共通Prompt(逐語ファイルパス)と3モデル入力sha256一致 3. L/T/S `response.model`実値/tokens/latency/JPY(Terra UNKNOWN明記)/再実行有無、合計(¥100以内) 4. 各モデルTop20・Top10(転記) 5. モデル間一致率(Top20/Top10重複、Spearman、3ペア) 6. `USER_EVAL_RERANK_POOL.md`無変更確認、評価script dry-run 7. Jev deferred記録(ファイル・OPEN番号) 8. 旧UDR整理(OPEN番号・件数・REPORT未発見ID) 9. ACTIVE_TASK_RR処置、`git status --short`、commit SHA、push 10. 一覧外Read/Grep理由、Open Item候補(事実列挙)。
