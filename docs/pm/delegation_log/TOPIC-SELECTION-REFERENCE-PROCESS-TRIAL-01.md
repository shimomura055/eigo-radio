# 委任文: TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01

## 管理ID

`TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01`(初回委任)。**並行タスクあり**: 別sonnet-workerが`NEWS-META-ENGLISH-ONLY-TRIAL-01`(er015_output配下、標準ACTIVE_TASK/RESULT_PACKET使用)を実行中。衝突回避: 本タスクは`er015_*`に触らず、一時ファイルは`docs/pm/ACTIVE_TASK_RP.md`/`docs/pm/RESULT_PACKET_RP.md`、SSOT無変更、commit時`index.lock`は10秒待ち再試行(最大3回)、自タスクのファイルのみ明示add。

## 性質/到達上限Status/禁止事項

- 性質: Topic Search方式Trial。固定Lane/固定Query方式(Trial-03)ではなく、**検索結果を読みながらその場で探索方針を更新する逐次探索プロセス**でReference級Topicを最大20件集める。到達上限Status=`VALIDATED`。最終品質判定はユーザー。Production採用なし。
- **本Trialに限り、Sonnet自身が探索中の判断(候補の拾い上げ・棄却・次の探索方向・Source差替え)を行ってよい**(ユーザーがClaude側の逐次判断を明示的に求めているため)。ただし最終候補の品質評価(Reference級か等)はSonnetが下さず、Fable参考評価→ユーザー評価とする。判断理由は全てログに残す。
- 禁止事項: 20〜30 Queryの一括生成/固定LaneのQuota埋め/同じSearch Patternの機械的反復/Reference記事の固有語で直接検索(`REFERENCE_CONTAMINATION_KEYWORDS`+評価datasetのtopic_ja/hook_jaを全Query・全Promptで機械検査、検出0を証跡化)/PR・UGCを数合わせに使う/Production Search・Router・Prompt変更/Hook生成/Writer生成/Audio生成/別方式の大型Trial並行起票/数合わせ(品質が落ちるならN件でSTOP)。SSOT無変更。既存scriptは変更しない(importのみ)。`git add -A`/`stash`/`amend`禁止。
- 費用上限**¥150**。Round 1終了時に1 callあたり費用を計測し、20 call相当で¥150を超える見込みならSTOP報告(無理に使い切らない)。
- STOP条件(ユーザー指定): Cost上限超過見込み/候補品質が数ラウンド改善しない/同じSearchの堂々巡り/Candidate PoolがPR・UGC中心/Referenceを直接当てに行くSearch/Production変更が必要/ユーザー仕様判断が必要。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

(2026-09-24、管理ID `TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01`。要点抜粋。全文は本委任文末尾【ユーザー指示全文】としてdelegation_logへ保存)
- 目的: 「Referenceを作ったときに近い『逐次探索・方向転換型』のプロセスをClaude/Fable側で再現し、Reference級の『聞きたくなるTopic』を自律的に20件集められるか検証する。主眼は『どのQueryが良いか』ではなく『検索結果を見ながら、その場で探索方針を更新していくプロセス自体』。」
- 基本方針: 固定Lane中心にしない。Quotaを置かない。面白い具体的な記事・事象の発見を優先。
- 探索プロセス: Step 1 少数(2〜4本)の広いSearch(今どんな面白いニュースが出ているかを眺める)→Step 2 候補を読む(「これ、少し気になる」「人に話したくなる」「続きを知りたい」を拾う。過度にScore化しない)→Step 3 結果から次の探索方向を決める(生活ネタが見つかった→周辺を広げる/AIばかり→方向転換/硬いニュースばかり→日常・健康・文化・旅行へ/逆転事例→同じ型を別カテゴリで/SNS由来→報じた記事を探す)→Step 4 Pool更新(良い候補だけ残す、重複統合、弱いSourceは差替え)→Step 5 5〜8件ごとに途中レビュー(偏り・硬さ・Tech過多・商品過多・Everyday不足・Talkability不足・同一クラスタ過多)→Step 6 20件まで繰り返す(数合わせ禁止、品質が落ちるならN件でSTOP)。
- Query: 最初から大量生成しない。各ラウンドで少数だけ。途中で捨ててよい。
- Reference: Teacher Dataとして使用可だが、タイトル・固有フレーズ・記事名・正解Topicの固有キーワードをQueryに入れて既知記事を再発見するのは禁止。学んでよいのは「どんな具体性・自分事性・意外性・Talkabilityが強かったか」まで。
- 面白さの見方(自然言語で判断): 一瞬で意味が分かるか/具体的な場面が浮かぶか/「それ何？」と思えるか/自分にも少し関係があるか/人に話したくなるか/数字や専門説明がなくても成立するか/社会的重要性だけで選んでいないか。
- Source Quality(原則除外): PR/Advertorial/Sponsored/アフィリエイト/ECランキング/セール中心/個人ブログ/note等の個人投稿/Redditスレッドそのもの/SNS検索結果ページ/記事ではない投稿一覧。SNSで起きている現象を通常のニュース媒体が報じている場合は可。
- Source差替え: Topicが面白いのにSourceが弱い場合、同じTopicを報じる一次媒体/通常ニュース媒体を探して差替え。Topicを捨てる前にSource改善を試してよい。
- Cost制御: Search回数を少数ラウンドで管理。search_context_size低設定/「検索は必要最小限」/1回のSearchで複数候補を返す を試してよい。
- 最重要ログ: 各ラウンドで 1.現在のCandidate Pool 2.何が足りないと判断したか 3.次に何を探すと決めたか 4.実際に使ったQuery 5.新しく見つかった候補 6.捨てた候補と理由 7.次の方向転換 を記録。
- 比較: Reference 20/ChatGPT API-only 20/Luna API 17/Trial-03 17/今回。ユーザー評価用にTopic/短い内容/Sourceの一覧(1〜10評価できる形)。
- 最終報告19項目(下記「報告」参照)。完了後STOP。最終候補品質の判断はユーザー。

## 事前指定Read一覧

- `er016_topic_selection_search_trial_03.py`: Grep `def call_search|web_search|search_context_size|def verify|published|def gate|UGC|def classify|contamination|def _price|cost`→検索call・公開日時検証・Source Gate・非混入検査・cost集計の実装(流用)。
- `er016_output/topic_selection_search_trial_03/cost.json`: 1 callあたり費用と内部検索回数の実測(Grep `per_call|web_search_calls|total`)。
- `TOPIC-SELECTION-SEARCH-TRIAL-03_REPORT.md`: 行403-460(§14〜§16、弱かった点: UGC通過・Lane D・費用構造)のみ。
- `docs/pm/topic_selection_user_eval_dataset.json`: Teacher Data(分析にのみ使用。**Query/Promptへ文字列を入れない**。非混入検査対象)。
- `er016_topic_selection_chatgpt_repro_01.py`: 行133-160(`REFERENCE_CONTAMINATION_KEYWORDS`)。
- `USER_EVAL_TRIAL03_20.md`: 全文(比較用の17件。Queryには使わない)。
- `docs/pm/PM_BRIEF.md`: 行151-175。

## 事前指定Grep一覧+追記位置・更新位置の手順

### 設計(Fable固定。逐次判断はSonnet)
- model: `gpt-5.6-luna`、effort medium。Search callは`tools=[{"type":"web_search","search_context_size":"low"}]`(APIが受理しない場合は省略し記録)、Promptに「検索は必要最小限(1〜2回)にし、見つかった記事から最大10件を返す」を明記、schema出力(title/url/媒体/公開日/2文要約/なぜ気になるか1文)。
- 時間窓: 公開日時 2026-09-22 21:05 JST〜実行開始時刻(Trial-03と同じ)。HTTPメタで検証、窓外・取得不能は除外(403は記録)。
- **Round 1(2〜4 call)**: 広いQuery(例: 「今週 話題 ニュース 意外」「最近増えている 現象 なぜ」「海外 ニュース 変わった 生活」「SNSで話題 現象 報道」等。カテゴリ名単独やReference固有語は不可)。Sonnetが結果を読み、`exploration_log.md`にRound 1の7項目(Pool/不足/次の方向/Query/新候補/棄却と理由/方向転換)を書く。
- **Round 1終了時の費用計測**: 1 callあたり平均費用×20が¥150を超える見込みならSTOP報告。
- **Round 2〜N(各2〜4 call)**: 前ラウンドの所見から次Queryを少数作成(方向転換・周辺深掘り・Source差替え検索を含む)。5〜8件溜まるごとに途中レビュー(偏り7項目)を`exploration_log.md`へ。**総Search call上限20**(Source差替え検索を含む)。同じQuery Patternの反復・堂々巡りを自覚したらSTOP。
- Pool管理: `pool.json`(候補: id/topic_ja/summary_2sent/url/媒体/lane_free[自由記述の型]/why_ja/status[kept|dropped|replaced]/round_found/drop_reason/source_replaced_from)。Source Gateは機械signal(Trial-03流用+UGCドメイン: note.com/reddit.com/minkara/ameblo/hatenablog/x.com/twitter.com/instagram/gravity等)+Sonnet判断。
- 終了条件: 20件到達、または品質が落ちると判断した時点でN件(理由をログ)、またはcall上限。
- 最終: `final_candidates.json`と`USER_EVAL_REFPROC_20.md`(`| # | Topic | 内容(1〜2文) | Source(媒体・URL) | なぜ気になったか(1文) |`、内部Scoreなし)。
- 比較: Reference/A/B/Trial-03 17/今回 の5集合をLuna分類call 1回で型付け(Everyday/Personal/Reversal/Talkability/BigChange/HardSocial/Tech/Product/Entertainment)+PR/UGC混入率+国内比率→`comparison_sets.md`。Referenceとの話題重複(機械+Sonnet目視)を記録(組織的重複は「到達できた」の観察として肯定的に記録、Queryでの直当てでない限り問題ではない)。
- 非混入検査→`contamination_check.json`。
- Claude独自Idea: 逐次探索の枠内で試したこと(周辺探索・抽象度変更・国内外切替・粒度変更等)を`ideas_tried.md`に何を疑い・なぜ・結果・費用で記録。
- REPORT `TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01_REPORT.md`: §1 Search期間・条件/§2 初回Query/§3 各ラウンド(exploration_log転記)/§4 方向転換理由一覧/§5 Pool推移(round別 kept/dropped/replaced件数)/§6 Source差替え記録/§7 最終候補一覧/§8 PR・UGC混入状況/§9 5集合比較/§10 Search回数/§11 model実値/§12 tokens/§13 latency/§14 cost(round別・合計)/§15 逐次探索が効いた具体例(Sonnet観察)/§16 効かなかった点(Sonnet観察)/§17 Claude独自Idea/§18 Fable記入欄(分類・参考評価・UDR)`[Fable記入]`/§19 Production変更なし。

## 実行コマンド全文

```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er016_topic_selection_reference_process_trial_01.py --out-dir er016_output\topic_selection_reference_process_trial_01 --step search --round 1 --queries-file er016_output\topic_selection_reference_process_trial_01\queries_round1.json --context-size low
.venv\Scripts\python.exe er016_topic_selection_reference_process_trial_01.py --out-dir er016_output\topic_selection_reference_process_trial_01 --step cost-check --budget-jpy 150 --planned-calls 20
(以降、Sonnetが各ラウンドで`queries_round{n}.json`を作成し `--step search --round {n}` を実行、`--step verify`で公開日時検証、`--step gate`でSource Gate、`--step pool` でpool.json更新。総call上限20)
.venv\Scripts\python.exe er016_topic_selection_reference_process_trial_01.py --out-dir er016_output\topic_selection_reference_process_trial_01 --step compare
.venv\Scripts\python.exe er016_topic_selection_reference_process_trial_01.py --out-dir er016_output\topic_selection_reference_process_trial_01 --step contamination-check
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01.md --json-out docs\pm\delegation_log\TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01.md_check.json
git status --short
```
(新規script。各stepは費用累計を`cost.json`へ更新し、上限到達見込みで非0終了+`stop_reason.json`。)

## SSOT追記文

なし。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `er016_topic_selection_reference_process_trial_01.py`、`er016_output/topic_selection_reference_process_trial_01/`(配下全て)、`TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01_REPORT.md`、`USER_EVAL_REFPROC_20.md`(root直下)、`docs/pm/delegation_log/TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01.md`、同`_check.json`。
メッセージ: `TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01: 逐次探索・方向転換型Topic Search(少数広域Query→読む→次方向決定→Pool更新→途中レビュー、Source差替え、UGC除外、探索ログ保存、Luna、Production変更なし)`
trailer: `Management-ID: TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01`
STOP時もそこまでをcommit(`STOP:`接頭)。

## 報告(RESULT_PACKET_RP項目)

0. T-0結果。
1. Search期間・条件・model実値・`search_context_size`受理可否。
2. 初回Query全文、各ラウンドのQuery全文とラウンド数。
3. `exploration_log.md`の要約(ラウンド別: 不足判断→次方向→新候補→棄却→方向転換)。
4. Pool推移(round別kept/dropped/replaced)、Source差替え一覧。
5. 最終候補N件(全項目。RESULT_PACKETにも転記)、N<20の場合の理由、公開日時検証結果。
6. PR/UGC混入状況(Gate除外一覧)。
7. 5集合比較表、Referenceとの話題重複。
8. Search call数(round別)・内部検索回数・tokens・latency・cost(round別・合計、¥150以内か)、Round 1時点の1 call費用と継続判断。
9. 非混入検査結果。
10. 逐次探索が効いた具体例/効かなかった点(Sonnet観察、事実ベース)。
11. Claude独自Idea(`ideas_tried.md`要約)。
12. `USER_EVAL_REFPROC_20.md`の絶対パス。
13. Production/SSOT無変更、`git status --short`、commit SHA、push結果。
14. 一覧外Read/Grepの理由、STOP該当の有無、Fable/ユーザー判断が必要な事実。

---
【ユーザー指示全文】

管理ID: `TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01`

## 目的
これまでの固定Lane/固定Query中心のSearch Trialではなく、Referenceを作ったときに近い「逐次探索・方向転換型」のプロセスをClaude/Fable側で再現し、Reference級の「聞きたくなるTopic」を自律的に20件集められるか検証する。今回の主眼は「どのQueryが良いか」ではなく「検索結果を見ながら、その場で探索方向を更新していくプロセス自体」にある。Production実装はしない。

## 背景
これまでのTrialでは、面白さの型をLane化/LaneごとにQueryを先に作成/Query群を順番に実行/最後にSelection という方式を使った。しかしReferenceは、検索前に「Reversal」「Everyday Why」等の型を固定して探したというより、広くニュースを見ながら「これは面白い」と感じる具体的事象を拾い、見つかった内容に応じて次の探索方向を変えた可能性が高い。今回はこちらのプロセスを試す。

## 今回の基本方針
固定Lane中心にしない。最初からLane A/B/Cのように候補枠を埋めに行かない。「20件を5カテゴリ×4件」のようなQuotaも置かない。Referenceのように、面白い具体的な記事・事象を発見することを優先する。

## 探索プロセス
Step 1: 少数の広いSearch(最初は2〜4本程度の広いQuery。目的は今どんな面白いニュースが出ているかを眺めること)。Step 2: 候補を読む(「これ、少し気になる」「人に話したくなる」「続きを知りたい」と思える具体的な事象を拾う。過度にScore化しない)。Step 3: その結果から次の探索方向を決める(面白い生活ネタが1つ見つかった→同じ現象周辺を少し広げて探す/AIばかり増えた→AI以外へ方向転換/硬い政治・経済ニュースばかり→日常・健康・文化・旅行などへ移る/面白い逆転事例が見つかった→同じ「型」を別カテゴリで軽く探す/SNS由来で面白い現象が見つかった→SNS投稿自体ではなく、それを報じた記事を探す。Search結果を見て次のQueryをその場で作る)。Step 4: Candidate Poolを更新(良い候補だけ残す。同じ話題の重複はまとめる。Sourceが弱ければ、同じTopicを扱うより良い媒体へ差し替える)。Step 5: 途中レビュー(5〜8件程度候補が集まるたびに、偏り/硬さ/Tech過多/商品過多/Everyday不足/Talkability不足/同一クラスタ過多を確認。必要なら方向転換)。Step 6: 20件になるまで繰り返す(20件を無理に埋めない。品質が明確に落ちる場合は「良質候補はN件まで」としてSTOPしてよい。数合わせ禁止)。

## Search Queryの考え方
Queryは最初から大量生成しない。各ラウンドで、次に何を探せばCandidate Poolが良くなるかを考えて、少数だけ作る。Query自体は途中で捨ててもよい。

## Referenceの使い方
Reference 20件とユーザー評価はTeacher Dataとして使用可。ただし、Referenceタイトル/固有フレーズ/記事名/正解Topicの固有キーワードをそのままSearch Queryへ入れて、既知記事を再発見するのは禁止。Referenceから学んでよいのは、どんな具体性・自分事性・意外性・Talkabilityが強かったかまで。

## 面白さの見方
固定Scoreだけで決めない。特に以下を自然言語で判断する: 一瞬で意味が分かるか/具体的な場面が浮かぶか/「それ何？」と思えるか/自分にも少し関係があるか/人に話したくなるか/数字や専門説明がなくても成立するか/社会的重要性だけで選んでいないか。

## Source Quality
以下は原則除外: PR/Advertorial/Sponsored/アフィリエイト/ECランキング/セール中心/個人ブログ/note等の個人投稿/Redditスレッドそのもの/SNS検索結果ページ/記事ではない投稿一覧。ただし、SNSで起きている現象を通常のニュース媒体が報じている場合は候補にしてよい。

## Source差替え
Topic自体が面白いのにSourceが弱い場合、同じTopicを報じる一次媒体/通常ニュース媒体を探して差し替える。Topicを捨てる前にSource改善を試してよい。

## Candidate選定
最終候補には、Topic/1〜2文の内容説明/Source/なぜ気になったか を保存。内部Scoreは参考にしてよいが、最終ユーザー表示では長いモデル評価を出さない。

## Searchの自由度
今回のTrialでは、Claude/Fableに以下を許容する: 探索途中でQuery方針変更/カテゴリ変更/Search Laneの追加・破棄/Candidateの入替/弱いSourceから強いSourceへの差替え/面白いTopic周辺の追加深掘り/偏りを見て反対方向へ探索。つまり、最初に決めた計画に固執しない。ただし変更理由はログに残す。

## 禁止事項
20〜30 Queryを最初に一括生成/固定LaneのQuota埋め/同じSearch Patternを機械的に反復/Reference記事の固有語で直接検索/PR・UGCを数合わせに使う/Production Searchへの反映/Hook生成/Writer生成/Audio生成

## Cost制御
前回は1 Query call内で複数回web_searchが走り、費用が膨らんだ。今回は、Search回数を少数ラウンドで管理する。1ラウンドあたりSearch call数を抑え、候補をある程度まとめて取得する。可能なら、search_context_size低設定/「検索は必要最小限」/1回のSearchで複数候補を返す などを試してよい。

## Cost上限
総費用¥150以内を上限とする。ただし最初の数ラウンドでコスト効率を計測し、この方式では上限内で十分な探索ができないと分かった場合はSTOP。無理に使い切らない。

## 最重要ログ
今回、最終候補だけでなく、探索の思考プロセスを残す。最低限、各ラウンドで: 1.現在のCandidate Pool 2.何が足りないと判断したか 3.次に何を探すと決めたか 4.実際に使ったQuery 5.新しく見つかった候補 6.捨てた候補と理由 7.次の方向転換 を記録。これが今回の主成果の一つ。

## Main評価
最終的に、Reference型の逐次探索プロセスが、固定Lane型より候補品質を上げたかを見る。比較対象: Reference 20/ChatGPT API-only 20/Luna API 17/Trial-03 17/今回Trial。

## ユーザー評価
最終品質の判定はユーザー。Fable/Claudeは参考評価のみ。最終候補を、Topic/短い内容/Source の分かりやすい一覧で提示する。ユーザーが1〜10評価できる形にする。

## Claude独自Idea
今回の「逐次探索」という基本思想を壊さない範囲で、Claude/Fableが探索中に良いIdeaを見つけた場合は試してよい(面白い候補の周辺探索/Source差替え/Queryの抽象度変更/海外→国内への切替/国内→海外への切替/Search roundの粒度変更)。ただし、別方式の大型Trialを並行起票しない。今回の1本の逐次探索Trialの中で扱う。

## Status
開始時`TRIAL`。最大到達`VALIDATED`。終了時にREJECTED/VALIDATED/USER_DECISION_REQUIREDで分類。Production採用はしない。

## STOP条件
Cost上限超過見込み/候補品質が数ラウンド改善しない/同じSearchの堂々巡り/Candidate PoolがPR・UGC中心になる/Referenceを直接当てに行くSearchになる/Production変更が必要/ユーザー仕様判断が必要

## 最終報告
1.Search期間 2.初回Query 3.各探索ラウンド 4.各ラウンドの方向転換理由 5.Candidate Pool推移 6.Source差替え記録 7.最終候補一覧 8.PR/UGC混入状況 9.Reference/Trial-03との比較 10.Search回数 11.model_id 12.tokens 13.latency 14.cost 15.逐次探索が効いた具体例 16.効かなかった点 17.Claude独自Idea 18.Trial分類 19.USER_DECISION_REQUIRED。完了後STOP。最終候補品質の判断はユーザーに委ねること。
