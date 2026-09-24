# 委任文 NEWS-HOOK-MODEL-COMPARISON-01

## 管理ID

`NEWS-HOOK-MODEL-COMPARISON-01`(初回委任)。並行タスクなし。一時ファイルは標準名`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`を上書きしてよい(前タスクNEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02はcommit済み)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(Hook生成のModel差比較 + ユーザー評価datasetのRepo保存)。到達上限Status=`VALIDATED`。Production採用はユーザー判断であり、Sonnet/Fableは行わない。
- 禁止事項:
  - Production(`er006_model_routing_contract_01.py`、Daily Runner、Topic Selector、Production Prompt)・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`を変更しない。既存の`er016_topic_selection_chatgpt_repro_01.py`/`_cont02.py`も変更しない(importして再利用のみ)。
  - **Reference Hook(`REFERENCE_20[*]["hook_ja"]`)・`type_tags`・ユーザー評価点・他モデルの生成Hook・過去Hook Trial(CONT-02 hook_test_*)の回答例を、生成Promptへ一切入れない。** 各モデルの入力は`REFERENCE_20[*]["id"]`と`topic_ja`のみ(CONT-02の`REFERENCE_MATERIALS_ONLY`と同じ形)。3モデルは互いに独立call(previous_response_id共有なし)。
  - 3モデルで**完全同一Prompt・同一schema・同一reasoning effort(medium)・同一temperature等**。モデル別のPrompt調整禁止。
  - 費用上限¥100(超えそうなら停止して報告)。API callは各モデルStage1+Stage2の計6 callのみ(retryはJSON parse失敗時1回まで)。
  - 品質の主観評価・ランキングはSonnetが行わない(観察事実・機械集計のみ。全文比較はFable)。
  - Sonnet自身による新しいProduction Selection Rule(「商品記事除外」等)の作成・記述禁止。
  - `git add -A`/`stash`/`amend`禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

要点抜粋(全文は本委任文末尾の【ユーザー指示全文】を`docs/pm/delegation_log/NEWS-HOOK-MODEL-COMPARISON-01.md`に含めて保存すること):
- 「各モデルにはReference Hookを絶対に見せないこと。入力はReferenceの素材概要・必要最小限の素材情報のみ。」
- 「同一条件で以下3モデルを比較する。`gpt-5.6-luna` / Terra / `gpt-5.6-sol`。Terraについては、現在APIで利用可能な正式model_idを確認して使用すること。全callで`response.model`の実値を保存する。」
- 「3モデルで完全に同じPromptを使用する。CONT-02で最も有望だった『面白い見方を考える → 短いHookにする』2段思考方式をベース。」
- 「各モデルについて必ず記録: 20 Hook総費用/1 Hook平均費用/input・output token/reasoning token等/latency/actual model_id。毎日20 Hook×30日の月額概算。」
- 「Original Reference Hookは生成完了後に初めて結合する。」
- 「User Evaluation Dataset A(ChatGPT API Search 20件)/B(Luna最新17件)を、今後Topic Search Trialから参照できるPM/TrialデータファイルとしてRepoへ保存。metadata: 評価者User/尺度1〜10/5以上=採用可能相当/評価対象=Topic+現在のHookの総合評価/5未満でもHook改善で上昇可能/Search教師データとして使用可/Production scoring ruleとしては未承認。Reference 20件の既存User Scoreも同じDatasetから辿れる状態にする。」
- STOP条件: 「3モデルで同一Prompt条件を維持できない/Terra正式model_idが利用不可/actual model_idが指定と一致しない/Reference HookがPromptへ混入した/model routingのため公平比較にならない/Fact逸脱が顕著/新しいPrompt仕様判断が必要」

## 事前指定Read一覧

- `er016_topic_selection_chatgpt_repro_01.py`: 行40-60(MODEL_LUNA/MODEL_SOL/EFFORT_DEFAULT定義)、行89-131(`REFERENCE_20`。**hook_jaは生成に使わない**)、`def response_meta`をGrepして該当関数全体、`def call_model`または同等のResponses API呼出関数をGrepして該当範囲、行1500-1530(`_price`・pricing計算)。
- `er016_topic_selection_chatgpt_repro_01_cont02.py`: 行30-110(MODEL/EFFORT/`call_model`定義)、行200-215(`REFERENCE_MATERIALS_ONLY`)、`H2_STAGE1_SCHEMA`/`H2_STAGE2_SCHEMA`をGrepして定義範囲、行962-1042(H3 Stage1/Stage2 Prompt。**Stage1のuser1・developer1、Stage2のh3分岐のuser2・developer2を逐語で流用**)、行1160-1200(cost集計。`model_id`キーで集計する修正済み箇所を確認)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: `gpt-5.6-sol`/`gpt-5.6-luna`の単価行(Grep後該当範囲)。terraは存在しない想定(下記Grep手順)。
- `generate_test.py`: 行30-34(`MODEL_WRITE = "gpt-5.6-terra"`、既存Production Writerで使用中のTerra model_id)。
- `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02_REPORT.md`: 行1-30(REPORT冒頭書式の参考のみ)。
- `docs/pm/PM_BRIEF.md`: 行151-175(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

1. Terra単価: `Grep pattern="terra" -i path=er005_output/cost_baseline_01/pricing_snapshot.json` → 無ければ `Grep pattern="terra.*(円|JPY|USD|\$)" -i glob="*_REPORT.md"` および `Grep pattern="gpt-5.6-terra" glob="er005_output/**/*.json"`。それでも単価が見つからない場合、`curl -sL https://openai.com/api/pricing/`(または`https://platform.openai.com/docs/pricing`)で取得を1回試み、取得できた場合は取得元URL・日時・数値を`cost.json`の`price_source`に記録。取得できない場合は**単価を捏造せず**`terra_price_status: "UNKNOWN"`とし、tokenのみ記録して報告(STOP条件ではない)。
2. 既存datasetの有無: `Glob docs/pm/*eval*`・`Glob docs/pm/*EVAL*`・`Glob docs/pm/*dataset*`・`Glob docs/pm/*DATASET*`・`Grep pattern="User Score" glob="docs/pm/*.md"`。既存のTopic Selectionユーザー評価datasetファイルがあればそこへ追記、無ければ新規作成(下記)。
3. Reference非混入検査: 生成後、`er016_output/news_hook_model_comparison_01/prompts/*.json`全ファイルに対し、`REFERENCE_20[*]["hook_ja"]`の各全文、`type_tags`各値、下記のユーザー評価点表の行、CONT-02 `hook_test_h3.json`/`hook_test_h3_sol.json`の各hook_ja全文が**含まれないこと**をPythonで機械検査し、結果を`contamination_check.json`へ保存。
4. actual model検査: 各callの`response.model`が要求model_idと一致(前方一致可、例`gpt-5.6-terra-2026-xx-xx`は一致扱い)することを検査。不一致があれば**その時点で残りのcallを実行せずSTOP**し報告。

## 実行コマンド全文

### Step 1: 新規スクリプト作成 `C:\Users\tensh\eigo-radio\er016_news_hook_model_comparison_01.py`

設計:
- `import er016_topic_selection_chatgpt_repro_01 as base`、`import er016_topic_selection_chatgpt_repro_01_cont02 as cont02`(cont02のimport時副作用があれば、必要な定数・schemaのみ複製して`# 複製元: cont02.py 行XX`とコメント)。
- `MODELS = {"luna": "gpt-5.6-luna", "terra": "gpt-5.6-terra", "sol": "gpt-5.6-sol"}`、`EFFORT = "medium"`(3モデル共通)。
- 入力: `MATERIALS = [{"reference_id": r["id"], "topic_ja": r["topic_ja"]} for r in base.REFERENCE_20]`(hook_ja/type_tags不使用)。
- 各モデルについて: Stage1(developer1・user1をcont02行968-977と逐語一致、schema=H2_STAGE1_SCHEMA、web_search=False)→Stage2(developer2・cont02のh3分岐user2 行1016-1030と逐語一致、schema=H2_STAGE2_SCHEMA、入力はそのモデル自身のStage1結果のみ)。独立call。
- 各callで保存: `prompts/{model}_stage{1,2}.json`(developer/user全文)、`raw_responses/{model}_stage{1,2}.json`(`response.model`実値、`usage`全項目[input_tokens/output_tokens/output_tokens_details.reasoning_tokens/cached等]、latency秒[time.perf_counter]、response_id、effort)、`hooks_{model}_stage1.json`/`hooks_{model}.json`。
- Terra呼出で`reasoning`パラメータ等が拒否された場合: 他モデルの条件を変えて合わせることは**禁止**。エラー全文を記録し、STOP条件「3モデルで同一Prompt条件を維持できない」として報告(Luna/Solの結果は保存してよい)。
- 生成6 call完了後にのみ`comparison_table.md`を生成: 列 `# | 素材(topic_ja) | Original Reference Hook(hook_ja) | Luna | Terra | Sol`、20行。加えて各モデルの`hook_ja`文字数(平均・最大・最小)、末尾が「？」の件数、「でしょうか」含有件数、`answer_in_source == "NOT_IN_SOURCE"`件数を`mechanical_stats.json`と`comparison_table.md`末尾に記載(観察事実のみ)。
- `cost.json`: モデル別に total_jpy、per_hook_jpy(=total/20)、input/output/reasoning tokens、latency合計(Stage1+Stage2)、actual model_id、単価出典、月額概算(per-20-hook cost × 30)。集計は`model_id`キーで行う(CONT-02の`model`キー誤集計と同じバグを再発させない)。JPY換算レートは`pricing_snapshot.json`の既存レートを使用し記録。
- `run_meta.json`: 実行日時(JST)、script sha、models、effort、call数。
- 出力先: `C:\Users\tensh\eigo-radio\er016_output\news_hook_model_comparison_01\`

実行:
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er016_news_hook_model_comparison_01.py --out-dir er016_output\news_hook_model_comparison_01 --models luna,terra,sol --effort medium
.venv\Scripts\python.exe er016_news_hook_model_comparison_01.py --out-dir er016_output\news_hook_model_comparison_01 --assemble-only
.venv\Scripts\python.exe er016_news_hook_model_comparison_01.py --out-dir er016_output\news_hook_model_comparison_01 --contamination-check
```
(`--assemble-only`はReference結合表・stats・cost生成、`--contamination-check`は上記Grep手順3・4の検査。3つを1コマンドにまとめてもよいが、生成→結合の順序が保証されること。)

### Step 2: ユーザー評価dataset保存

既存datasetが無い場合、以下2ファイルを新規作成:
- `C:\Users\tensh\eigo-radio\docs\pm\topic_selection_user_eval_dataset.json`(機械参照用)
- `C:\Users\tensh\eigo-radio\docs\pm\TOPIC_SELECTION_USER_EVAL_DATASET.md`(閲覧用、同内容の表+metadata)

(全表はACTIVE_TASK.md/委任文本体を参照。ここでは省略せず本文をSonnetが受領した委任テキストそのまま保存する運用のため、以下に実データを再掲する。)

共通metadata(両ファイル冒頭に必ず記載):
```
evaluator: User(shimomura055)
scale: 1〜10
threshold_note: 5以上=現時点では採用可能相当
evaluation_target: Topic + 現在付いているHook の総合評価(素材だけの評価ではない)
caveat: 5未満でもHookの付け方によって点数が上がる可能性がある。score<5→当該Topic類型を検索除外、のような機械利用は禁止
usage: Search教師データとして使用可(素材が弱い/Hookが弱い/両方弱いを区別する教師データ)
production_status: Production scoring ruleとしては未承認(NOT_APPROVED)
prompt_injection: Hook生成・Selection Promptへ本datasetの点数・Hook・Reference Hookを直接投入することは禁止(汚染防止)
management_id: NEWS-HOOK-MODEL-COMPARISON-01(保存時)、評価データ出典: TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02(Reference 20)、NEWS-HOOK-MODEL-COMPARISON-01(Dataset A/B)
recorded_at: 2026-09-24
```

Dataset R: Reference 20件 User Score: 1:8, 2:4, 3:7, 4:8, 5:5, 6:3, 7:6, 8:7, 9:6, 10:7, 11:7, 12:5, 13:7, 14:8, 15:5, 16:6, 17:4, 18:4, 19:5, 20:7

Dataset A: ChatGPT API Search 20件(topic/hook/score、詳細は元委任文参照、下記スクリプトで転記済み)。
Dataset B: Luna最新17件(topic/hook/score、詳細は元委任文参照、下記スクリプトで転記済み)。

集計(観察事実として記載): 各datasetの平均点、5以上件数/総数。**傾向解釈・除外ルール化は書かない。**

### Step 3: REPORT作成 `C:\Users\tensh\eigo-radio\NEWS-HOOK-MODEL-COMPARISON-01_REPORT.md`

章立て: §0 条件/§A 全20件比較表/§B 機械統計/§C actual model_id・usage・latency・cost表/§D 非混入検査結果/§E Terra関連の技術観察/§F dataset保存先とmetadata/§G Fable記入欄(空欄)/§H Status `[Fable分類待ち]`/§I Production変更なし宣言。

### Step 4: ACTIVE_TASK/RESULT_PACKET

`docs/pm/ACTIVE_TASK.md`を固定ヘッダ書式(PM_BRIEF行162-175)で上書き。`docs/pm/RESULT_PACKET.md`を報告項目で上書き。

## SSOT追記文

なし(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`CURRENT_SPEC.md`は変更しない)。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `er016_news_hook_model_comparison_01.py`、`er016_output/news_hook_model_comparison_01/`(配下全て)、`docs/pm/topic_selection_user_eval_dataset.json`、`docs/pm/TOPIC_SELECTION_USER_EVAL_DATASET.md`、`NEWS-HOOK-MODEL-COMPARISON-01_REPORT.md`、`docs/pm/delegation_log/NEWS-HOOK-MODEL-COMPARISON-01.md`、同`_check.json`、`docs/pm/ACTIVE_TASK.md`、`docs/pm/RESULT_PACKET.md`。
メッセージ: `NEWS-HOOK-MODEL-COMPARISON-01: Hook 2段生成のLuna/Terra/Sol同一条件比較(Reference 20素材、Reference Hook非混入)+Topic Selectionユーザー評価dataset保存(R20/A20/B17)、Production変更なし`
trailer: `Management-ID: NEWS-HOOK-MODEL-COMPARISON-01`

## 報告(RESULT_PACKET項目)

0〜12: T-0結果/Terra使用model・受理可否/一致検査/比較表所在/機械統計/cost/非混入検査/dataset保存先・件数・平均点/Fact観察/Production変更なし確認/commit SHA・push結果/一覧外Read理由/懸念。

---

## 【ユーザー指示全文】

管理ID: `NEWS-HOOK-MODEL-COMPARISON-01`

### 1. 目的
現在、Topic Selectionには別々の2問題が残っている。
#### Problem A — Search / Topic Discovery
Reference 20件と比較すると、APIによる自律検索では選ばれる素材自体のQualityがまだ低い。
#### Problem B — Hook
同じ素材でも、Hook生成品質にモデル差がある可能性が高い。
今回はまず **Problem BのModel差を明確にする**。
同時に、ユーザーから追加されたTopic評価37件を、今後のSearch改善で利用できる評価データとして保存する。

### 2. Hook比較対象
以前のReference 20素材を使用する。
重要：
#### 各モデルにはReference Hookを絶対に見せないこと。
入力はReferenceの、素材概要・必要最小限の素材情報のみ。
以下は生成時に混入禁止：Reference Hook/Reference Hookの言い換え/ユーザー評価点/他モデルが生成したHook/過去Hook Trialの回答例
Reference Hookは全モデル生成終了後の評価時にのみ使用する。

### 3. 比較モデル
同一条件で以下3モデルを比較する。`gpt-5.6-luna` / Terra / `gpt-5.6-sol`
Terraについては、現在APIで利用可能な正式model_idを確認して使用すること。
全callで `response.model` の実値を保存する。
モデルroutingによる代理実行ではなく、比較対象モデルが実際に使用されたEvidenceを残すこと。

### 4. Prompt条件
3モデルで完全に同じPromptを使用する。以前のCONT-02で最も有望だった、「面白い見方を考える → 短いHookにする」という2段思考方式をベースにする。
ただし、Luna用にPromptを変える/Terraだけ追加説明する/Solだけ自由度を上げる などは禁止。完全同条件で比較する。

### 5. Hook生成の基本思想
Hookは単なる見出しの疑問文化ではない。まず内部的に「このニュースの何が、人間にとって意外・身近・逆説的・気になるのか」を考え、その「面白い見方」から「音声番組で聞いた瞬間に『ちょっと知りたい』と思う短いHook」を作る。狙いはReferenceと同じ方向。ただしReference Hook自体は見せない。

### 6. 比較方法
20素材 × 3モデル。各素材について | # | 素材 | Original Reference Hook | Luna | Terra | Sol | を並べる。Original Reference Hookは生成完了後に初めて結合する。

### 7. 評価観点
数値自動Scoreだけで結論を出さない。Fable自身が全文を読んで比較する。最低限：元Headlineの言い換えに留まっていないか/一段深い「見方」へ移れているか/短いか/話し言葉として自然か/答えを知りたくなるか/対象者が狭すぎないか/元素材に興味がない人にも届くか/過剰な煽りになっていないか/Referenceの面白さに近いか/Factから逸脱していないか

### 8. 特に確認したい仮説
Luna: 深く考えさせる→長い・硬い、短く指定する→短いが平板。Sol: 同一Promptでも再解釈・短さ・会話的自然さを比較的同時に実現。今回Terraを追加して「TerraがSolにどこまで近づけるか」を見る。Production観点では Lunaで十分か/TerraがCost/QualityのSweet Spotか/Solまで必要か を判断できるEvidenceを作る。

### 9. Cost / latency
各モデルについて必ず記録：20 Hook総費用/1 Hook平均費用/input/output token/reasoning token等取得可能なusage/latency/actual model_id。毎日20 Hook×30日の月額概算も提示。

### 10. 最終報告
A. 全20件比較表(Reference/Luna/Terra/Sol) B. モデル別特徴 C. Reference再現性(Reference級/採用可能だがReference未満/弱い、具体例付き) D. QCD E. Fable推奨(Production採用はユーザー判断)

### 11. 追加：Topic Search用ユーザー評価データを保存
この評価は「素材だけ」の評価ではなく、「素材＋現在付いているHook」を含めた総合評価。NG(5未満)の素材でも、Hookの付け方によって点数が上がる可能性がある。したがって今後のSearchで `score < 5 → このTopic類型を検索対象から除外` のように機械利用してはいけない。素材自体が弱い可能性/Hookが弱いため低評価になった可能性/両方弱い可能性 を区別する教師データとして使う。

### 12/13. User Evaluation Dataset A(ChatGPT API Search 20件)/B(Luna最新17件)
本委任文Step 2の表のとおり(下記スクリプトで実データ転記済み)。

### 14. 保存先
今後Topic Search Trialから確実に参照できる、適切なPM/TrialデータファイルとしてRepoへ保存する。既存にユーザー評価dataset/Topic Selection評価datasetがある場合は重複ファイルを作らず、そこへ追加してよい。必ずmetadata(評価者User/尺度1〜10/5以上=採用可能相当/評価対象=Topic+現在のHookの総合評価/5未満でもHook改善で上昇可能/Search教師データとして使用可/Production scoring ruleとしては未承認)を残す。Reference 20件の既存User Scoreも同じDatasetから辿れる状態にすること。

### 15. Dangling Reference / Production禁止
このUser Scoreから新しいProduction Selection Ruleを勝手に作らない(「商品記事は除外」「芸能は除外」「5点以下カテゴリは検索しない」等を自動で正式仕様化しない)。あくまで次のSearch Trial設計に使うEvidence。

### 16. Status
Hook Model Comparisonの最大Status：`VALIDATED`。各モデルのProduction採用はユーザー判断待ち。TerraまたはSolが明確に良くても、自動でProduction Routerへ変更しない。Search側も今回変更しない。

### 17. STOP条件
3モデルで同一Prompt条件を維持できない/Terra正式model_idが利用不可/actual model_idが指定と一致しない/Reference Hookが生成Promptへ混入した/model routingのため公平比較にならない/Fact逸脱が顕著/新しいPrompt仕様判断が必要

### 18. Closeout
報告時に必ず：1. 20素材×Reference/Luna/Terra/Sol一覧 2. 各モデルの特徴 3. Referenceへの近さ 4. Cost 5. Latency 6. actual model_id 7. Fable推奨 8. USER_DECISION_REQUIRED項目 9. Topic Search評価dataset保存先 10. Production変更なし を提示してSTOP。ユーザー判断なしにHook modelをProduction採用しないこと。
