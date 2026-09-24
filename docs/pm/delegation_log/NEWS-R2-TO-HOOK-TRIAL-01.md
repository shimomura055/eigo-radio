# 委任文: NEWS-R2-TO-HOOK-TRIAL-01

## 管理ID

`NEWS-R2-TO-HOOK-TRIAL-01`(初回委任)。並行タスクなし。一時ファイルは標準名`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`を上書きしてよい(前タスクNEWS-ITERATIVE-R2-PRODUCTION-WIRING-01 Phase 0はcommit 9dd27358済み。同IDは`APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`でユーザー判断待ちのため、ACTIVE_TASKヘッダの「APPROVED未配線」欄に必ず残すこと)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(仮説「Hookを記事作成前ではなく2回目revision完成記事[Trial呼称R2]の後に作れば、Reference級Hookへ近づく」の検証)。到達上限Status=`VALIDATED`。Hook Productionモデル・生成順序・R2タイトル流用のいずれもProduction採用しない(ユーザー判断)。
- 禁止事項:
  - Production Hook generator/Production routing/Topic Search/Writer/retry・fallback/`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/Production promptを変更しない。既存`er015_*`/`er016_*`scriptを変更しない(importまたは複製のみ)。
  - **新しく記事本文を生成しない。** 既存R2全文をそのまま入力に使う。
  - **生成Promptへ以下を一切入れない**: Reference Hook(`er016_topic_selection_chatgpt_repro_01.REFERENCE_20[*]["hook_ja"]`)、過去のLuna/Terra/Sol Hook(`er016_output/news_hook_model_comparison_01/hooks_*.json`、`er016_output/topic_selection_chatgpt_repro_01_cont02/hook_test_*.json`)、ユーザー評価点、Fable評価、他モデルの出力。
  - 3モデルで完全同一Prompt・同一schema・同一effort(medium)。モデル別調整禁止。各callは独立(previous_response_id不使用)。
  - Prompt本文はFableが下記で固定した逐語を使用し、Sonnetが条件を追加しない(「比喩を複数」「逆転を必ず」「驚き2回」等の追加禁止)。
  - API callは3記事×3モデル=9 callのみ(JSON parse失敗時のretryは各1回まで)。費用上限¥30。
  - 品質の主観評価・ランキングはSonnetが行わない(観察事実・機械集計のみ。全文比較はFable)。
  - `git add -A`/`stash`/`amend`禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

(2026-09-24、管理ID `NEWS-R2-TO-HOOK-TRIAL-01`。要点抜粋。全文は本委任文末尾【ユーザー指示全文】としてdelegation_logへ保存)
- 「仮説: Hookを記事作成前に作るのではなく、R2完成記事の後に作れば、Reference級のHookへ近づくのではないか。」
- 「対象記事: A. 下水道(テーマ: 老朽化する下水道をめぐり、一部自治体が合併浄化槽への切り替えを検討、入力=TRIAL-01のR2全文)/B. AI電話代行(テーマ: AIに電話を頼んだら、裏では人間スタッフが話していた、入力=TRIAL-02 Article A R2全文)/C. 旅行荷物(テーマ: 旅行の荷物はなぜ毎回バッグいっぱいになるのか、入力=TRIAL-02 Article B R2全文)。新しく記事本文は生成しない。」
- 「同一入力・同一Promptで`gpt-5.6-luna`/`gpt-5.6-terra`/`gpt-5.6-sol`を比較。全callでactual `response.model`を保存。」
- 「各モデルにはTopic概要とR2完成記事全文のみを与える。過去のReference Hook/過去のLuna・Terra・Sol Hook/ユーザー評価点/Fable評価/他モデルの出力は見せない。」
- 「Promptは過度に複雑化しない。比喩を複数作れ/逆転を必ず入れろ/驚きを2回入れろ 等の追加条件は禁止。」
- 「R2記事タイトルそのものが既にHookとして十分強いケースがある可能性も確認する(別途Hook生成が必要か/R2タイトルをそのまま使えるか/少し短くするだけでよいか)。勝手にProduction仕様へ変更しない。」
- 「全9 Hook callについて actual model_id/latency/input・output・reasoning token/cost を記録。」
- 「最大Status=VALIDATED。Production変更なし。最後に必ずSTOP。」

## 事前指定Read一覧

- `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/sewer_revision2.md`全文(=TRIAL-01 R2)、`ai_phone_revision2.md`全文(=TRIAL-02 A R2)、`travel_bag_revision2.md`全文(=TRIAL-02 B R2)。これら3ファイルをそのまま入力に使う(元artifact `er015_output/news_iterative_entertainment_trial_01/revision2.md`、`er015_output/news_iterative_entertainment_trial_02/A_revision2.md`/`B_revision2.md`とsha256一致をrun_metaに記録)。
- `er016_news_hook_model_comparison_01.py`: Grep `def call_model|def response_meta|MODELS|EFFORT|schema|def compute_cost|price`で位置特定→該当範囲Read(Responses API呼出・usage/latency記録・cost集計・単価取得の実装を流用)。
- `er016_output/news_hook_model_comparison_01/cost.json`: `by_model.terra.price_probe_evidence`と`price_source`の範囲のみ(Terra単価UNKNOWN扱いを踏襲)。
- `er016_output/news_hook_model_comparison_01/hooks_luna.json`/`hooks_terra.json`/`hooks_sol.json`: **生成完了後にのみ**、reference_id 1(Meta Muse)と13(圧縮ポーチ)の`hook_ja`を比較表用に読む(生成前に読んでもよいがPromptへは入れない。読んだ時刻をrun_metaに記録)。
- `er016_topic_selection_chatgpt_repro_01.py`: 行89-131の`REFERENCE_20`から id 1・13の`hook_ja`を**生成完了後にのみ**比較表へ転記。
- `docs/pm/PM_BRIEF.md`: 行151-175(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

1. 非混入検査(生成後): `er016_output/news_r2_to_hook_trial_01/prompts/*.json`全6〜9ファイルに対し、`REFERENCE_20[*]["hook_ja"]`20件、`news_hook_model_comparison_01/hooks_{luna,terra,sol}.json`の`hook_ja`60件、`topic_selection_chatgpt_repro_01_cont02/hook_test_h3.json`/`hook_test_h3_sol.json`の`hook_ja`40件、`docs/pm/topic_selection_user_eval_dataset.json`の`hook_ja`57件、が**含まれないこと**をPythonで機械検査→`contamination_check.json`。
2. actual model検査: 各`response.model`が要求model_idと一致(前方一致可)。不一致があればその時点で残りを実行せずSTOP報告。
3. 記事タイトル抽出: 各R2記事の1行目(タイトル)を`r2_titles.json`へ保存(比較表「R2タイトル」列用)。
4. 機械統計: 各hook_jaの文字数、「？」終端、「でしょうか」含有、R2タイトルとの文字列一致率(difflib.SequenceMatcher ratio)、R2本文に存在しない固有名詞・数字の有無(hook中の数字・カタカナ語・漢字固有名詞候補がR2本文またはテーマ文に部分一致するか。主観判定なし、機械一致のみ)→`mechanical_stats.json`。

## 実行コマンド全文

### Step 1: 新規スクリプト `C:\Users\tensh\eigo-radio\er016_news_r2_to_hook_trial_01.py`

- `MODELS = {"luna": "gpt-5.6-luna", "terra": "gpt-5.6-terra", "sol": "gpt-5.6-sol"}`、`EFFORT = "medium"`。
- ARTICLES = [("sewer", テーマ文「老朽化する下水道をめぐり、一部自治体が合併浄化槽への切り替えを検討」, sewer_revision2.md全文), ("ai_phone", 「AIに電話を頼んだら、裏では人間スタッフが話していた」, ai_phone_revision2.md全文), ("travel_bag", 「旅行の荷物はなぜ毎回バッグいっぱいになるのか」, travel_bag_revision2.md全文)]。
- **Prompt(逐語、Fable固定。変更・追加禁止)**:
  - developer: `あなたはHook Writerです。`
  - user:
```
以下は、音声番組で読み上げる予定の完成記事です。この記事をまだ聞いていない人が、聞いた瞬間に「ちょっと知りたい」と思う短いHookを1つ作ってください。

記事タイトルの言い換えや要約ではなく、記事の中にすでにある一番面白い見方や、具体的な場面を使ってください。友人に話しかけるような短い一文の問いにし、目安は30字前後。「〜でしょうか」は使わず、「〜？」で終えてください。記事にない事実は加えず、誇張はしないでください。

【テーマ】
{topic}

【記事】
{article_full_text}

hook_ja(Hook 1文)と、used_angle_ja(記事のどの見方・場面を使ったか、1文)を返してください。
```
  - schema(json_schema strict): `{"hook_ja": string, "used_angle_ja": string}`。
- 3記事×3モデル=9 call、独立。各callで`prompts/{article}_{model}.json`(developer/user全文)、`raw_responses/{article}_{model}.json`(`response.model`実値・usage全項目[input/output/reasoning]・latency秒・response_id・effort)、`hooks/{article}_{model}.json`を保存。
- 生成完了後のみ`comparison_table.md`を生成: 表1 `| Article | R2タイトル | Existing/Reference Hook | 旧方式(Topic概要→Hook) Luna/Terra/Sol | Luna from R2 | Terra from R2 | Sol from R2 |`(Existing: ai_phone=REFERENCE_20 id1 hook_ja、travel_bag=id13 hook_ja、sewer=「Referenceなし」と記載しR2タイトルを比較対象とする。旧方式=news_hook_model_comparison_01のid1/id13の各モデルhook_ja、sewerは「旧方式なし」)。表2 `| Article | Model | used_angle_ja |`。表3 機械統計。
- `cost.json`: モデル別 総費用¥・1 Hook平均¥・tokens・latency(3 call合計と各call)・actual model_id・単価出典(Terraは前回同様UNKNOWN扱い、tokenのみ)。`model_id`キーで集計。
- `run_meta.json`: 実行日時(JST)、入力3ファイルのsha256と元artifactとの一致、models、effort、call数、比較用Hookを読んだ時刻(生成完了後であること)。

実行:
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er016_news_r2_to_hook_trial_01.py --out-dir er016_output\news_r2_to_hook_trial_01 --models luna,terra,sol --effort medium
.venv\Scripts\python.exe er016_news_r2_to_hook_trial_01.py --out-dir er016_output\news_r2_to_hook_trial_01 --assemble-only
.venv\Scripts\python.exe er016_news_r2_to_hook_trial_01.py --out-dir er016_output\news_r2_to_hook_trial_01 --contamination-check
```

### Step 2: REPORT `C:\Users\tensh\eigo-radio\NEWS-R2-TO-HOOK-TRIAL-01_REPORT.md`

§0 条件(Prompt逐語、入力=テーマ文+R2全文のみ、含めていないもの明示、model/effort/schema)/§A 比較表1〜3(転記)/§B actual model_id・usage・latency・cost/§C 非混入検査/§D 機械統計(タイトル一致率・Fact機械一致)/§E Fable記入欄(Q1〜Q5・Referenceへの近さ・R2タイトルとの比較・推奨: `[Fable記入]`空欄)/§F Status `[Fable分類待ち]`/§G Production変更なし宣言。

### Step 3: ACTIVE_TASK/RESULT_PACKET

`docs/pm/ACTIVE_TASK.md`を固定ヘッダ書式で上書き(管理ID=本ID、APPROVED未配線: `NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`(配線先経路未確定、ユーザー判断待ち)、UDR-deferred: 同ID+`OPEN-174`)。`docs/pm/RESULT_PACKET.md`を下記「報告」で上書き。

## SSOT追記文

なし(SSOT変更なし)。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `er016_news_r2_to_hook_trial_01.py`、`er016_output/news_r2_to_hook_trial_01/`(配下全て)、`NEWS-R2-TO-HOOK-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-R2-TO-HOOK-TRIAL-01.md`、同`_check.json`。
メッセージ: `NEWS-R2-TO-HOOK-TRIAL-01: 2回目revision完成記事(R2)を入力にしたHook生成をLuna/Terra/Sol同一条件で比較(3記事×3モデル、Reference/過去Hook非混入)、Production変更なし`
trailer: `Management-ID: NEWS-R2-TO-HOOK-TRIAL-01`
push後、`git rev-parse HEAD`と`git status --short`を記録。

## 報告(RESULT_PACKET項目)

0. T-0結果。
1. 9 callのactual model_id一致検査(要求vs実値)、STOP発生の有無。
2. 比較表1(3記事×[R2タイトル/Existing/旧方式3モデル/新方式3モデル])の全文をRESULT_PACKETにも転記(Fableが読む主対象)。表2 used_angle_ja全文。
3. 機械統計(文字数・「？」終端・「でしょうか」・R2タイトル一致率・Fact機械一致の結果)。
4. cost(モデル別総費用¥・1 Hook平均・tokens・latency各call/合計・単価出典)、合計費用(¥30以内か)。
5. 非混入検査結果(検査対象文字列数、検出0件か)。
6. 入力3ファイルのsha256一致結果、比較用Hookを読んだ時刻が生成完了後であること。
7. Production/SSOT変更なしの確認、`git status --short`、commit SHA、push結果。
8. 一覧外Read/Grepの理由(あれば1行)。
9. 想定外事項・懸念(あれば)。

---
【ユーザー指示全文】(delegation_logへそのまま保存)

管理ID: `NEWS-R2-TO-HOOK-TRIAL-01`

## 1. 目的
これまでのHook Trialでは「Topic概要 → Hook」の順でHookを生成していた。一方、News記事の逐次Revision Trialでは「Topic → Original → R1 → R2」と記事を改善する過程で、記事固有の面白い見方/具体的な生活場面/読者との距離の近さ/一つの統一された見立て が後から形成されることが確認された。今回の仮説は「Hookを記事作成前に作るのではなく、R2完成記事の後に作れば、Reference級のHookへ近づくのではないか。」これを検証する。

## 2. 対象記事
すでにOriginal→R1→R2まで作成済みの以下3記事のみを使用する。A. 下水道(テーマ: 老朽化する下水道をめぐり、一部自治体が合併浄化槽への切り替えを検討。入力: `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01`のR2全文)/B. AI電話代行・Meta Muse(テーマ: AIに電話を頼んだら、裏では人間スタッフが話していた。入力: `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02`のArticle A R2全文)/C. 旅行荷物・圧縮ポーチ(テーマ: 旅行の荷物はなぜ毎回バッグいっぱいになるのか。入力: `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02`のArticle B R2全文)。新しく記事本文は生成しない。既存R2をそのまま使う。

## 3. 比較モデル
同一入力・同一Promptで `gpt-5.6-luna`/`gpt-5.6-terra`/`gpt-5.6-sol` を比較する。全callでactual `response.model` を保存すること。

## 4. Hook生成条件
各モデルには Topic概要/R2完成記事全文 のみを与える。以下は生成時に見せない: 過去に作ったReference Hook/過去のLuna・Terra・Sol Hook/ユーザー評価点/Fable評価/他モデルの出力。

## 5. Hook生成Prompt
目的は「完成記事を読んだうえで、その記事をまだ聞いていない人が『ちょっと知りたい』と思う短いHookを1つ作ること」。記事タイトルの要約ではない。R2記事の中にすでに存在する 一番面白い見方/具体場面/日常との接点/逆転/意外性 を利用すること。ただしPromptは過度に複雑化しない。比喩を複数作れ/逆転を必ず入れろ/驚きを2回入れろ 等の追加条件は禁止。

## 6. 比較対象
① 既存Referenceまたは既存の良いHook(生成完了後に表示。AI電話「AIに店への電話を頼んだら、裏では人間が話していた？」、旅行荷物「旅行の荷物は、なぜ毎回バッグいっぱいになる？」、下水道は既存Trialで最も良かったタイトル/Hook相当表現を比較用に使用してよいが生成Promptには混入しない)。② 以前のTopic概要→Hook方式(既存のLuna/Terra/Sol Hook)。③ 今回のR2記事→Hook方式(Luna/Terra/Sol)。

## 7. 最重要の比較問い
Q1 R2完成記事を読ませることで、HookはTopic概要だけから作る場合より改善するか。Q2 Reference Hookの特徴であった「具体的な場面へ落とす」ことが増えるか。Q3 Lunaでも十分なHookが作れるようになるか。Q4 それでもTerra/Solとの差は残るか。Q5 差が残るなら Model能力差/Prompt差/R2記事自体の内容差 のどこに原因がありそうか。

## 8. 評価観点
一瞬で意味が分かるか/続きを知りたくなるか/具体場面があるか/元Topicに興味がなくても届くか/記事タイトルの言い換えに留まっていないか/R2記事で得られた「見方」を活用しているか/短い話し言葉として自然か/Factを逸脱していないか/過剰に煽っていないか。

## 9. 比較表
| Article | Existing/Reference Hook | Luna from R2 | Terra from R2 | Sol from R2 | と、可能なら | Model | Topic概要→Hook | R2記事→Hook | 改善したか |。

## 10. 重要：タイトルとの関係
R2記事タイトルそのものが既にHookとして十分強いケースがある可能性も確認する(別途Hook生成が必要か/R2記事タイトルをそのままHookとして利用できるか/少し短くするだけでよいか)。勝手にProduction仕様へ変更しない。

## 11. Cost / latency
全9 Hook callについて actual model_id/latency/input・output・reasoning token/cost を記録。

## 12. もし全モデルで改善しなかった場合
原因仮説を出す(R2記事の「見方」がHook化しにくいのか/Hook Promptがまだ抽象的すぎるのか/タイトル生成とHook生成ではタスク性質が違うのか/Reference Hookは記事生成後ではなく人間的な再解釈がさらに必要なのか)。必要以上の追加Trialは行わずSTOP。

## 13. Status
最大Status `VALIDATED`。Hook Productionモデル・Hook生成順序は未承認。Luna/Terra/Sol/R2後Hook方式/R2タイトル流用 のいずれもProduction採用しない。

## 14. Production禁止
Production Hook generator/Production routing/Topic Search/Writer/retry・fallback/CURRENT_SPEC/Production prompt を変更しない。Trial結果のみ取得する。

## 15. 最終報告
1. 3記事×3モデルのHook全文 2. 既存Hookとの比較 3. Topic概要→Hook方式から改善したか 4. Referenceへの近さ 5. R2記事タイトルそのものとの比較 6. Luna/Terra/Solの差 7. cost/latency 8. Fable推奨 9. 未解決問題 10. USER_DECISION_REQUIRED 11. Production変更なし。最後に必ずSTOPし、ユーザー判断を待つこと。
