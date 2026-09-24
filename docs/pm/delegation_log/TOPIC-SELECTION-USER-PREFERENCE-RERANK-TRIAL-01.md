## 管理ID

`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`(初回委任)。**並行タスクあり**: 別sonnet-workerが`NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`(er015_output配下、標準ACTIVE_TASK/RESULT_PACKET使用)を実行中。衝突回避: 本タスクは`er015_*`に触らず、一時ファイルは`docs/pm/ACTIVE_TASK_RR.md`/`docs/pm/RESULT_PACKET_RR.md`、SSOT無変更、commit時`index.lock`は10秒待ち再試行(最大3回)、自タスクのファイルのみ明示add。

## 性質/到達上限Status/禁止事項

- 性質: Trial。ユーザー実評価済みTeacher Data(57件)をfew-shot/preference examplesとして直接渡し、同一Candidate Poolを4モデル(Luna/Terra/Sol/Jev)がユーザー嗜好に沿って順位付けできるかを比較する。到達上限`VALIDATED`。**モデル自身のScoreで勝敗を決めない。ユーザーが新Candidateを評価した後に相関等を計算する。** Production採用なし。
- 禁止事項: Production実装/追加のSearch Trial・Prompt Trial/Hook生成/モデルごとにPrompt条件を変えること/Teacher Dataを抽象Ruleへ圧縮して渡すこと(実Topic+実点数を渡す)/既知評価TopicをPoolへ混入/**Jev API keyの表示・log保存・commit・report記載**(環境変数`JEV_API_KEY`を参照するのみ。存在確認は`bool(os.environ.get("JEV_API_KEY"))`の真偽のみ記録)/Jevへのretry storm(429時はRetry-After等に従い待機、連打禁止)。SSOT無変更。既存script無変更(importのみ)。`git add -A`/`stash`/`amend`禁止。総費用上限**¥150**(Search≤¥30、Reranking主費用。Jevは料金体系不明なら少数件で確認後に本実行)。
- **Jev armが実施不能(接続不可・rate limit未解決・API仕様が特定できない)の場合は、Luna/Terra/Solを先行完了させて「4-way比較完了」としない。Jev接続確認をSTEP 1(他armの前)で行い、不能なら`USER_DECISION_REQUIRED`でSTOP報告**(Pool作成までは完了してよい)。
- STOP条件(ユーザー指定): Jev rate limitが解決しない/Teacher Dataが不完全/Candidate Poolがモデル間で一致しない/既知評価TopicがPoolへ混入/Cost上限超過見込み/モデルごとにPrompt条件が変わる/追加仕様判断が必要。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

(2026-09-24、管理ID `TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`。全文を末尾【ユーザー指示全文】としてdelegation_logへ保存)。要点: 「ユーザーの実評価済みTeacher Dataを直接使い、Candidate Poolをどのモデルが最もユーザー嗜好に近く順位付けできるかを検証。比較: Luna/Terra/Sol/Jev。」「Teacher Data=Reference 20+ChatGPT API-only 20+Luna API 17=57件と1〜10評価。抽象Ruleに圧縮せず、実Topic内容+実点数をfew-shot/preference examplesとして直接渡す。」「Candidate Poolは全モデルで完全に同一。既存Search成果物からSource品質が一定以上のCandidateを50件前後。不足時のみ最小限の追加Search。Teacher Dataと同一Topicは除外。」「Source Gate: PR/Advertorial/Sponsored/アフィリエイト/個人ブログ/note/Reddit/SNS検索結果/商品ランキング・Sale を除外。」「Jev: Searchさせない。CandidateごとまたはAPI仕様上効率的なbatch単位で『このユーザーの過去評価パターンに照らして、どの程度続きを聞きたいTopicか』を判定。`JEV_API_KEY`使用、key本文を表示・log・commit・report禁止。開始時1回だけ接続確認。429時は連打せずRetry-After確認。Jev不能ならUSER_DECISION_REQUIREDでSTOP。」「Preference Prompt: まずTeacher Dataを読ませ、高評価と低評価の差をモデル自身に推論させる(固定Ruleを与えすぎない)。予測対象は『英語学習用News Audioとして、このユーザーが続きを聞きたいと思うか』(社会的重要性・ニュース価値ではない)。」「出力: 各モデルのCandidate全件predicted score/Top20/簡潔な理由(内部用)。ユーザー評価用にモデル名を隠したブラインド比較。」「評価: ユーザー評価後に predicted vs user scoreの相関(Pearson/Spearman)/Top20内5点以上率/Top10内5点以上率/7点以上のRecall/明らかな低評価Topicを上位に置いた数。」「Hook生成なし(Topic単体低評価でもHookで改善し得ることをLimitationとして明記)。」「Teacher DataのSSOT=`docs/pm/topic_selection_user_eval_dataset.json`/`TOPIC_SELECTION_USER_EVAL_DATASET.md`。重複・欠落は補正せず報告。」「Cost上限¥150。開始前に概算Costを出す。」「最終報告17項目。ユーザー評価取得前に『どのモデルが最良』と結論づけない。」

## 事前指定Read一覧

- `docs/pm/topic_selection_user_eval_dataset.json`: 全文(Teacher Data 57件。件数・欠落・重複を機械確認、補正せず報告)。
- 既存Search成果物(Pool材料。**Teacher Dataと同一Topic=dataset A[REPRO-01 final 20相当]/B[CONT-02 final_new 17相当]/R[Reference]は除外**): `er016_output/topic_selection_search_trial_03/pool_final.json`、`er016_output/topic_selection_reference_process_trial_01/pool.json`(kept/dropped全件。dropped理由がUGC/PR以外[窓外・クラスタ重複等]のものは候補に戻してよい)、`er016_output/topic_selection_chatgpt_repro_01_cont02/pool_new.json`・`a1.json`〜`a5_feedback.json`・`b1.json`・`b2.json`(Grep `title|url|summary`で候補列のみ)、`er016_output/topic_selection_chatgpt_repro_01/candidates_raw.json`(同上。**stepE_final系はdataset Aと同一のため使わない**)。
- `er016_topic_selection_reference_process_trial_01.py`/`er016_topic_selection_search_trial_03.py`: Grep `def gate|UGC|domain|def verify|def call_search|def _price|cost`→Source Gate・公開日時検証・search call・cost集計の実装(流用)。
- `er016_topic_selection_chatgpt_repro_01.py`: 行133-160(`REFERENCE_CONTAMINATION_KEYWORDS`、Pool混入検査に使用)。
- Jev: `Grep pattern="jev|JEV" -i glob="*.{py,md,json,txt,env.example}"`でRepo内のclient/仕様/記録の有無を確認。無ければ公式ドキュメント(Jev公式サイト/API docs)を`curl`で1回取得し、endpoint・認証ヘッダ・request/response schema・料金・rate limitを`jev_api_notes.md`に記録(key本文は絶対に書かない)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna/sol/terra(未掲載ならUNKNOWN)単価。
- `docs/pm/PM_BRIEF.md`: 行151-175。

## 事前指定Grep一覧+追記位置・更新位置の手順

### STEP 0 Teacher Data確認
- 57件(R20/A20/B17)の件数・score欠落・topic重複を機械確認→`teacher_check.json`。不完全ならSTOP報告。

### STEP 1 Jev接続確認(他armより先)
- `JEV_API_KEY`存在の真偽のみ記録。Repo/公式docsからAPI仕様を特定し、**1回だけ**最小request(候補1件・Teacher例5件程度)で接続確認。応答schema・latency・課金情報(取得できれば)を`jev_probe.json`(key・生responseにkeyが含まれないことを確認して保存)。429/401/仕様不明→連打せずSTOP(`stop_reason.json`)、以降のarmを実行しない(Pool作成は継続可)。

### STEP 2 Candidate Pool(全モデル共通)
- 既存成果物から候補を収集→URL正規化で重複排除→Source Gate(既存機械signal+UGCドメインlist[note.com/reddit.com/minkara/ameblo/hatenablog/x.com/twitter.com/instagram/gravity/threads等]+Luna分類1 call[NEWS/FEATURE|PRODUCT_PHENOMENON|PR_ADVERTORIAL|AFFILIATE_RANKING|SALE_PRICE|UGC_PERSONAL|LISTING_PAGE|UNCLEAR])→除外後、**既知評価Topic混入検査**(Teacher 57件のtopic_ja/hook_jaとの文字列類似[difflib≥0.5]+Luna 1 callで「同一事象か」判定→同一は除外)→目標50件(40〜60)。40件未満なら最小限の追加Search(Luna web_search、`search_context_size=low`、最大4 call、窓は公開日時2026-09-22 21:05 JST〜検証時刻)で補充。
- `candidate_pool.json`: id(C001…)/topic_ja(1行)/summary_ja(1〜2文)/url/媒体/公開日/由来Trial/source_class。全モデルに**同一ファイル(sha256)**を渡し、sha256を各armのapi_metaに記録。

### STEP 3 Preference Prompt(Luna/Terra/Sol完全同一、effort medium、web_searchなし、schema出力)
- developer: `You predict how much one specific listener would want to keep listening to an English-learning news audio piece about each topic.`
- user(逐語):
```
Below are 57 topics that this listener has already rated from 1 (would not want to listen) to 10 (would definitely want to listen). Each item shows the topic, the hook that was attached at the time, and the listener's score. Note: the score reflects the topic together with that hook, so a low score does not always mean the topic itself is bad.

[Rated examples]
{57件: dataset_id / topic_ja / hook_ja / user_score}

First, in 5–8 sentences, describe in your own words what separates the topics this listener rates high from the ones they rate low. Do not use a fixed checklist; infer it from the examples.

Then, for each candidate below, predict the score this listener would give it as a topic for an English-learning news audio piece (1–10), and give one short reason. Predict the listener's wish to keep listening — not the topic's social importance or news value.

[Candidates]
{candidate_pool: id / topic_ja / summary_ja / 媒体}

Return JSON: {"preference_summary": string, "predictions": [{"id": string, "predicted_score": number, "reason": string}]}.
```
- Arm L=`gpt-5.6-luna`、Arm T=`gpt-5.6-terra`、Arm S=`gpt-5.6-sol`。各1 call(候補が多くcontextが不足する場合のみ同一Promptで2 batchに分割し、分割は3モデルで同一)。`response.model`実値・usage・latency・costを記録。
- Arm J(Jev): Searchさせない。Jev API仕様に合わせ、Teacher 57件を「このユーザーの過去評価」として与え、候補ごと(またはbatch)に「続きを聞きたい度」1〜10を判定させる。Jev用の入力はLuna/Terra/Solと同じ内容(Teacher 57件+候補)を、Jevのschemaに合わせて整形(意味を変えない)。`jev_decision_schema.md`にrequest/response schemaを保存。少数件(5件)でcost/rate limitを確認してから全件。
- 保存: `arms/{L,T,S,J}/predictions.json`(全件score+reason)、`top20.json`、`preference_summary.txt`、`api_meta.json`。

### STEP 4 集計・評価資料
- モデル間一致率: Top20の重複数(6ペア)、全件scoreのSpearman(6ペア)→`model_agreement.md`。
- **ユーザー評価用ブラインド一覧** `USER_EVAL_RERANK_POOL.md`: 候補全件をランダム順で `| # | Topic | 内容(1〜2文) | Source | あなたの評価(1〜10) |`(モデルscore・順位・理由は載せない)。対応表`user_eval_id_map.json`。
- 評価script `er016_rerank_eval_01.py --user-scores <path>`: ユーザー点数(id→score)を読み、各モデルについて Pearson/Spearman、Top20内5点以上率、Top10内5点以上率、7点以上Recall、Top20内の3点以下件数 を計算しmd出力(今回はscriptとdry-run[ダミー点数]のみ、実計算はユーザー評価後)。
- REPORT `TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_REPORT.md`: §1 Teacher Data確認/§2 Pool件数・由来・Source Gate結果・既知Topic除外/§3 追加Searchの有無/§4 Prompt全文・model実値(L/T/S)/§5 Jev設定・decision schema・接続確認・rate limit状況/§6 各モデルTop20/§7 全件predicted score表/§8 モデル間一致率/§9 cost・latency/§10 ブラインド一覧のパス/§11 評価方法(ユーザー評価後の計算)/§12 Limitation(Hookで改善し得る)/§13 Fable記入欄(分類・UDR・未解決)`[Fable記入]`/§14 Production変更なし。

## 実行コマンド全文

```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step teacher-check
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step jev-probe
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step pool --target 50 --max-search-calls 4
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step cost-estimate --budget-jpy 150
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step rerank --arms J,L,T,S
.venv\Scripts\python.exe er016_topic_selection_user_preference_rerank_trial_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --step assemble
.venv\Scripts\python.exe er016_rerank_eval_01.py --out-dir er016_output\topic_selection_user_preference_rerank_trial_01 --user-scores er016_output\topic_selection_user_preference_rerank_trial_01\user_scores_DUMMY.json --dry-run
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01.md --json-out docs\pm\delegation_log\TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01.md_check.json
git status --short
```
(`--step rerank --arms J,L,T,S`: Jev armを最初に実行し、Jev失敗時は残りを実行せず非0終了。)

## SSOT追記文

なし。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `er016_topic_selection_user_preference_rerank_trial_01.py`、`er016_rerank_eval_01.py`、`er016_output/topic_selection_user_preference_rerank_trial_01/`(配下全て。**commit前にkey文字列の混入がないことを`grep -r`で確認**)、`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01_REPORT.md`、`USER_EVAL_RERANK_POOL.md`(root直下)、`docs/pm/delegation_log/TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01.md`、同`_check.json`。
メッセージ: `TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01: ユーザー実評価57件をpreference examplesとして直接渡し、同一Candidate PoolをLuna/Terra/Sol/Jevが順位付け(ブラインド評価一覧・相関評価script、Production変更なし)`
trailer: `Management-ID: TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`
STOP時もそこまでをcommit(`STOP:`接頭)。

## 報告(RESULT_PACKET_RR項目)

0. T-0結果。
1. Teacher Data確認(件数・欠落・重複)。
2. Jev: key存在真偽・API仕様出典・接続確認結果・schema・latency・課金/rate limit状況(key本文なし)。
3. Pool: 件数・由来別内訳・Source Gate除外(分類別)・既知Topic除外件数・追加Search有無・sha256。
4. 概算Cost(実行前)と実績(モデル別・合計、¥150以内か)。
5. Prompt全文・`response.model`実値(L/T/S)・Jev decision schema。
6. 各モデルTop20(RESULT_PACKETにも転記)、全件predicted scoreの所在。
7. モデル間一致率(Top20重複・Spearman)。
8. `USER_EVAL_RERANK_POOL.md`/`user_eval_id_map.json`の絶対パス、評価scriptのdry-run結果。
9. Production/SSOT無変更、key混入なしの確認、`git status --short`、commit SHA、push結果。
10. 一覧外Read/Grepの理由、STOP該当の有無、改善案があればOpen Item候補として事実列挙(提案ではなく)。

---
【ユーザー指示全文】(delegation_logへそのまま保存)

管理ID: `TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`

## 目的
これまでのSearch Trialでは、AIが一般論として「面白そう」と判断するTopicと、実際にユーザーが「聞きたい」と評価するTopicにズレが大きかった。今回はSearch方法そのものの改善ではなく、ユーザーの実評価済みTeacher Dataを直接使い、Candidate Poolをどのモデルが最もユーザー嗜好に近く順位付けできるかを検証する。比較対象: Luna/Terra/Sol/Jev。Production実装は禁止。

## Teacher Data
既存のユーザー評価済みDataを使用する。最低限: Reference 20/ChatGPT API-only 20/Luna API 17/各Topicに対するユーザー1〜10評価。合計57件。重要: これまでのようにTeacher DataをReversal/Everyday Why/Personal/Talkability等の抽象Ruleだけに圧縮しない。今回は実際のTopic内容＋実際のユーザー点数をfew-shot/preference examplesとして直接モデルへ渡す。

## 仮説
LunaがSearch/Selectionで弱かった理由は、ユーザー嗜好を抽象ルールだけでは十分理解できていなかった可能性がある。一方、ChatGPT interactiveではある程度ユーザー嗜好を捉えられていた。そこで、実評価例を直接読ませた場合、モデル差が出るかを見る。

## Candidate Pool
全モデルで完全に同じCandidate Poolを使う。今回新たに検索方式の優劣を混ぜない。可能なら既存Search成果物から、Source品質が一定以上あるCandidateを50件前後集める。不足する場合のみ最小限の追加Searchを許容。ただし今回の主目的はSearchではなくReranking。Candidate Poolにはユーザー評価済みTeacher Dataと同一Topicを混ぜない。既知評価Topicが入っていた場合は除外する。

## Source Gate
Candidate Poolに入れる前に、PR/Advertorial/Sponsored/アフィリエイト/個人ブログ/note個人投稿/Reddit/SNS検索結果ページ/商品ランキング・Sale記事 を除外。全モデルへ同じPoolを渡す。

## Model Arms
Arm L: Luna(ユーザー評価済み57件をTeacher Dataとして提示し、Candidate Poolをユーザーの「聞きたい度」に基づいて順位付け)。Arm T: Terra(同一Prompt・同一Teacher Data・同一Candidate Pool)。Arm S: Sol(同一条件)。Arm J: Jev(JevはSearchさせない。Candidateごと、またはJevのAPI仕様上最も効率的なbatch単位で「このユーザーの過去評価パターンに照らして、どの程度『続きを聞きたいTopic』か」を判定させる。Jev API keyは環境変数`JEV_API_KEY`を使用。絶対に key本文を表示しない/log保存しない/commitしない/reportへ書かない)。

## Jev接続
Trial開始時に1回だけ接続確認。429/rate limitが出た場合: 連打しない/retry storm禁止/待機・Retry-After等を確認/Trial全体を止める必要がある場合はSTOPして報告。Jevだけ失敗した場合でも、Luna/Terra/Solを勝手に先行完了させて「4-way比較完了」としない。Jev armが実施不能なら`USER_DECISION_REQUIRED`でSTOP。

## Preference Prompt
各モデルへは、まずTeacher Dataを読ませ、このユーザーが高く評価するTopicと低く評価するTopicの差を推定させる。ただし最初に固定Ruleを与えすぎない。モデル自身に評価差からPreferenceを推論させる。重要: Topicの社会的重要性・ニュース価値ではなく「英語学習用News Audioとして、このユーザーが続きを聞きたいと思うか」を予測対象とする。

## 出力
各モデル: Candidate全件へのpredicted score/Top20/簡潔な選定理由 を保存。理由は内部分析用。ユーザー評価時には、モデル名を隠したブラインド比較を可能なら作成。

## 評価設計
最重要: モデル自身のScoreで勝敗を決めない。ユーザーが新Candidateを実際に1〜10で評価した後に、各モデルについて predicted score vs user scoreの相関/Top20内のユーザー5点以上率/Top10内のユーザー5点以上率/ユーザー7点以上のRecall/明らかな低評価Topicを上位に置いた数 を比較する。相関はPearson/Spearmanの両方を出せるなら出す。ただし最終モデル採用判断はユーザー。

## Hookとの分離
今回Hook生成はしない。ただし、Topic単体では低評価でもHookで改善する可能性があることはLimitationとして明記。今回測るのは、Hook前のTopic Selectionとして、誰がユーザー嗜好を最も理解できるかである。

## 既存データの扱い
Teacher DataはRepo内の既存`docs/pm/topic_selection_user_eval_dataset.json`/`docs/pm/TOPIC_SELECTION_USER_EVAL_DATASET.md`等をSSOTとして確認。重複や欠落があれば、勝手に補正せず報告。

## Cost / QCD
Searchに費用を使いすぎない。主費用はReranking比較。Trial開始前に概算Costを出す。上限¥150。ただしJevの料金体系が不明・想定外の場合は、少数件でCost/Rate limitを確認してから本実行。

## Claude独自Trial
今回は比較条件を汚すため、追加のSearch Trial・Prompt Trialを勝手に実施しない。必要な改善案を発見した場合はOpen Itemとして報告。

## Status
開始`TRIAL`。最大`VALIDATED`。終了時REJECTED/VALIDATED/USER_DECISION_REQUIRED。良いモデルが見つかってもProduction採用しない。

## STOP条件
Jev rate limitが解決しない/Teacher Dataが不完全/Candidate Poolがモデル間で一致しない/既知評価TopicがCandidate Poolへ混入/Cost上限超過見込み/モデルごとにPrompt条件が変わる/追加仕様判断が必要

## 最終報告
1.Teacher Data件数・内容確認 2.Candidate Pool件数 3.Source Gate結果 4.Luna prompt/model_id 5.Terra prompt/model_id 6.Sol prompt/model_id 7.Jev設定・decision schema 8.各モデルTop20 9.各Candidate predicted score 10.モデル間一致率 11.cost/latency 12.Jev rate-limit状況 13.ユーザー評価用ブラインド一覧 14.ユーザー評価取得後の相関計算方法 15.Trial分類 16.USER_DECISION_REQUIRED 17.未解決事項。ユーザー評価取得前に「どのモデルが最良」と結論づけない。完了後STOP。
