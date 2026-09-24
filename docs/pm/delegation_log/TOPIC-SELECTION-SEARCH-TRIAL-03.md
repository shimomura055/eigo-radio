## 管理ID

`TOPIC-SELECTION-SEARCH-TRIAL-03`(初回委任)。**並行タスクあり**: 別のsonnet-workerが`NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01`(er015_output配下・標準ACTIVE_TASK/RESULT_PACKET使用)を実行中。衝突回避: 本タスクは(1)`er015_*`に触らない、(2)一時ファイルは`docs/pm/ACTIVE_TASK_TS3.md`/`docs/pm/RESULT_PACKET_TS3.md`、(3)SSOTを触らない、(4)commit時`index.lock`があれば10秒待って再試行(最大3回)、自タスクのファイルのみ明示add。

## 性質/到達上限Status/禁止事項

- 性質: Topic Search/Source Selection/最終Selectionの品質改善Trial(Hook改善ではない)。到達上限Status=`VALIDATED`。良好でもProduction採用しない。最終評価はユーザーが20件を見て行う(モデルScoreで確定しない)。
- 禁止事項: Production Search/Router/Prompt/Writer Prompt/Hook Writerを変更しない。Audio生成・記事生成なし。CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS無変更。**ReferenceのタイトルやHook、評価dataset(`docs/pm/topic_selection_user_eval_dataset.json`)のtopic/hook文字列をQuery・Prompt・Selection入力に入れない**(Teacher Dataは「定性記述・型の分布」としてのみ使用。`er016_topic_selection_chatgpt_repro_01.REFERENCE_CONTAMINATION_KEYWORDS`+dataset A/Bのtopic_ja/hook_jaで全Prompt/Queryを機械検査し検出0を証跡化)。Web Searchの大量反復禁止(下記call上限)。総費用上限**¥200**(Main≤¥130、Fable追加arm≤¥40、残りは予備。超過見込みでSTOP)。品質の主観評価はSonnetが行わない(観察・機械集計。評価はFable/ユーザー)。`git add -A`/`stash`/`amend`禁止。
- STOP条件(ユーザー指定): Search Cost急増/同じQuery Patternの反復/Candidate品質が明確に改善しない/Referenceを直接当てるQueryになっている/PR・広告除外がTopic Diversityを過度に壊す/新しい仕様判断が必要/Production変更が必要。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

(2026-09-24、管理ID `TOPIC-SELECTION-SEARCH-TRIAL-03`。要点抜粋。全文は本委任文末尾【ユーザー指示全文】としてdelegation_logへ保存)
- 目的: 「Reference級の『聞きたくなる素材』を自律的に発見できる検索・選定方式を改善する。主目的はHook改善ではなく、検索・Source Selection・最終Topic Selectionそのものの品質改善。Production実装は行わない。」
- 背景: 「Reference 20件: 平均約5.95、5点以上16/20/ChatGPT API-only 20件: 平均約4.5、10/20/Luna API 17件: 平均約2.53、0/17。Web上に良い記事が存在しないのではなく、自律的なQuery設計・探索・選定が弱いことが主要因。」
- 仮説1: カテゴリ検索だけでは弱い→「面白さの型」から検索するレーンを重視。仮説2: 一発検索ではなく「複数レーン初期探索→候補Pool確認→不足タイプ診断→追加Query生成→再探索→最終Selection」の反復型。仮説3: Selectionも重要。最終Selectionでは「広い人が聞きたくなるか」を独立した観点として強く扱う。
- Search Lane(意図を維持): A Unexpected Reversal(一見Aだが実はB/技術の裏に人間/便利になるはずが別の問題/常識の逆転)/B Everyday Why(「そういえば、なんで？」)/C Personal Relevance(「自分にも関係ありそう」: 生活・仕事・スマホ・買い物・睡眠・旅行・食事・家・通勤)/D Talkability・Casual(「これ知ってる？」: SNS・小さな流行・ちょっと変な現象・身近な驚き。単に軽いだけは選ばない)/E Big Change in One Sentence(一文で「世の中が少し変わった」)。
- 自己診断: 初期Pool後に「Referenceに比べどのタイプが不足しているか」(Everyday Whyが少ない/人間的な逆転が少ない/国内生活系が少ない/俗っぽいTopicが少ない/技術偏重/硬い社会ニュース過多等)を診断→追加Queryを自動生成して再Search。結果を見てSearch戦略を修正する。
- Query設計: カテゴリ名だけで検索せず「なぜ？」「え、本当？」「それ自分にもある」と感じる構造をQueryへ。ReferenceのタイトルやHookをQueryに埋め込み既知記事を当てに行くカンニングは禁止。
- Source Quality Gate(OPEN-174統合): PR記事/Sponsored・Advertorial/アフィリエイト/「おすすめ○選」/ECランキング/楽天・Amazon売れ筋中心/セール訴求/価格比較中心/購買誘導中心/商品購入が記事目的 は原則除外または強く減点。ただし商品・サービスを扱うニュース自体は禁止しない(新しい生活習慣/消費者行動の変化/新サービスの社会的影響/なぜ売れているかという現象は可)。
- Selection Gate: 1聞きたくなるか 2一般性 3自分事性 4意外性・Reversal 5Talkability 6Audio適性(数字・固有名詞・統計・専門説明が大量に必要でないか) 7Source品質。注意: 社会的重要性が高い≠聞きたい/技術的に新しい≠面白い/軽い話題≠面白い/有名企業≠広く聞きたい。
- Teacher Data: Reference 20/ChatGPT API-only 20/Luna API 17/ユーザー1〜10評価/5以上=採用可能 を分析に使う。「5未満=Topic自体が完全に悪い」と固定しない。評価するのはTopic+Sourceの素材としての強さ。
- Hook: 最終Topicに独立したHook生成は不要。Topicの短い説明と「なぜ聞きたくなる候補なのか」程度の内部評価で十分。
- Main Trial: 20件の候補。可能ならReference評価時と近い時間窓・条件。検索対象期間を明記。
- 比較: Reference 20/ChatGPT API-only 20/Luna API 17/今回Trial-03 について、Topicタイプの多様性/Everyday・Personal系比率/硬い社会ニュース比率/Tech偏重/PR・広告Source混入率/Talkability/Audio適性/Referenceで強かったPatternの再現度。
- ユーザー評価用Output: 20件一覧(Topic/日本語での簡潔な内容説明/Source/Search Lane/なぜ候補に残したか)。内部Scoreやモデルの長い理由で読みづらくしない。
- Claude独自の追加Trial許容(Search/Selection品質を直接改善するもの。Production実装・Prompt変更・Hook改善・Audio・記事生成・仕様採用は禁止。VALIDATED止まり。何を疑ったか/なぜ/差/結果/Cost/採否候補を報告。無制限に試行しない)。
- Cost: 総費用上限¥200。最終報告18項目(下記「報告」参照)。完了後STOP、ユーザー評価待ち。

## 事前指定Read一覧

- `er016_topic_selection_chatgpt_repro_01.py`: 行40-60(MODEL/EFFORT)、行133-160(`REFERENCE_CONTAMINATION_KEYWORDS`)、Grep `def call_model|def response_meta|web_search|def verify_published|published_time|def fetch_meta|def _price|pricing`→Responses API+web_search呼出・公開日時検証(HTTPメタ取得)・cost集計の実装(流用)。**`REFERENCE_20`のtopic_ja/hook_jaはPromptに使わない**(型分布の集計にのみ`type_tags`を使用)。
- `er016_topic_selection_chatgpt_repro_01_cont02.py`: Grep `interest|feedback|SEL|selection_criteria|def run_search|lane|domestic|PR`→Round 1の関心語起点探索・Feedback round・選定基準文・国内レーンの実装(流用可。選定基準文「聞き手が反応するのは、意外な逆転/答えを知りたくなる問い/自分事になる/日常の小さな謎/世界の変化を一言で理解できる切り口/人に話したくなる/少し俗っぽい/『そう言われると確かに気になる』。身近さだけを軸にしない。重要なニュースであることや、技術的に新しいことや、軽いことは、それだけでは理由にならない。」は再利用可)。
- `TOPIC-SELECTION-CHATGPT-REPRO-01_REPORT.md`: Grep `CONT-02|Round 1|Round 2|結論|Search Test A|Search Test B|PR`→CONT-02の結論部のみ(何が効いたか: 関心語起点+Feedback roundがReference型メディア空間へ到達、PR/商品記事混入の課題)。
- `docs/pm/topic_selection_user_eval_dataset.json`: 全文(Teacher Data。**分析にのみ使用**: 型分布・5以上/未満の傾向を定性記述にまとめる。topic/hook文字列は非混入検査の対象にもする)。
- `OPEN_ITEMS.md`: 行323(OPEN-174の行、Source品質Gate候補リストの原文確認)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna/sol/web_search単価。
- `docs/pm/PM_BRIEF.md`: 行151-175。

## 事前指定Grep一覧+追記位置・更新位置の手順

### 設計(Fable固定。Sonnetは実装し、変更点があればRESULT_PACKETに記録)
- model: Search/診断/Source分類/Selection=`gpt-5.6-luna`、effort medium(CONT-02と同一)。Fable追加arm(下記)のみSol。
- **時間窓**: 公開日時 2026-09-22 21:05 JST 〜 実行開始時刻(Reference窓[09-22 21:05→09-23 21:05]を含む直近窓)。全候補について公開日時をHTTPメタ(`article:published_time`/JSON-LD)で検証し窓外・取得不能は除外(CONT-02と同じ扱い。403は取得不能として記録)。実際の窓をrun_metaに明記。
- **Teacher Data定性化(1 call、web_searchなし)**: datasetのR/A/Bを与え「5以上と5未満を分ける性質」「Referenceに多い型」「A/Bに多い失敗型」を**具体話題・Hook・点数を含まない定性記述**(各5行以内)として出力→`teacher_summary.json`。以後のPromptにはこの定性記述のみ使用(datasetそのものは入れない)。
- **Step 1 Query生成(1 call)**: 5レーン(A〜E)の定義+Teacher定性記述を与え、レーンごとに4本、計20本のQuery案(日本語中心、国内生活系はレーンB/C/Dで国内メディアが当たる語彙にする)。制約: カテゴリ名単独禁止、「なぜ/本当に/自分にも」構造、既知記事名の埋め込み禁止。→`queries_round1.json`。非混入検査PASS必須。
- **Step 2 初期探索(最大20 call、web_search、各1 query)**: 各callで候補≤6件(title/url/媒体/公開日/1行要約/lane)をschema出力→`pool_round1.json`(URL重複排除)。
- **Step 3 Source Quality Gate(機械+1 call)**: 機械signal(URL/タイトルに `prtimes|/pr/|sponsored|PR|おすすめ|選|ランキング|セール|価格比較|楽天|amazon|アフィリエイト|clip|kakaku` 等)+Luna分類call(候補一覧を与え `NEWS/FEATURE | PRODUCT_PHENOMENON(可) | PR_ADVERTORIAL | AFFILIATE_RANKING | SALE_PRICE | UNCLEAR` と理由1行)→`source_gate_round1.json`。除外=PR_ADVERTORIAL/AFFILIATE_RANKING/SALE_PRICE、UNCLEARは減点扱いで残す。除外がPoolの50%超なら「Diversity過度破壊」候補としてFableへ報告(STOP判定はFable)。
- **Step 4 自己診断(1 call)**: Gate後Poolのtitle+1行要約+lane(点数なし)と、Reference型分布(`REFERENCE_20.type_tags`を機械集計した比率表のみ。話題名なし)を与え、不足タイプ(Everyday Why/人間的逆転/国内生活/俗っぽさ/Tech偏重/硬い社会過多 等)を診断し、**追加Query最大8本**を生成→`diagnosis.json`/`queries_round2.json`。非混入検査。
- **Step 5 追加探索(最大8 call)**→`pool_round2.json`→Source Gate再適用→統合Pool`pool_final.json`。
- **Step 6 Selection(Luna、1〜2 call)**: 統合Pool(title/媒体/1行要約/lane/Source分類。点数なし)+Selection Gate 7観点(「広い人が聞きたくなるか」を独立観点として最重視)+注意4項(重要≠聞きたい等)+選定基準文(CONT-02再利用)を与え、20件+予備5件を選定。各件: topic_ja(短い説明)、why_ja(なぜ聞きたくなる候補か1文)、lane、source。→`selection_luna.json`。
- **Step 7 検証**: 20件の公開日時・HTTP status確認、窓外/取得不能は予備から補充→`final20.json`。
- **Fable追加arm(Selection model差、Sol 1 call、≤¥40)**: Step 6と**完全同一Prompt・同一Pool**で`gpt-5.6-sol`が20件選定→`selection_sol.json`。Luna選定との重複数・差分一覧を`selection_model_diff.md`(観察のみ)。目的: 「Searchは同じでもSelectionのモデル差で最終20件の質が変わるか」の切り分け(CONT-02でSolのHook優位が出たため、Selectionでも差があるかを疑った)。**最終20件(ユーザー評価用)はLuna選定を主とし、Sol選定は比較参考として別表で提示**。
- **比較表(機械)**: 4集合(Reference/A/B/Trial-03[Luna])を同一のLuna分類call(1 call)で型付け(Everyday/Personal/Reversal/Talkability/BigChange/HardSocial/Tech/Product/Entertainment、複数可)し、比率表+PR混入率(Trial-03はSource Gate結果、R/A/Bは同じ分類callで判定)+国内/海外比率+Referenceとの話題重複数(URLまたは事象一致、機械+目視候補)→`comparison_sets.md`。
- **ユーザー評価用一覧** `USER_EVAL_TRIAL03_20.md`: `| # | Topic | 内容説明(日本語1〜2文) | Source(媒体・URL) | Lane | なぜ候補に残したか(1文) |`。内部Scoreなし。
- 非混入検査: 全Query・全Prompt・Selection入力に対し、`REFERENCE_CONTAMINATION_KEYWORDS`+dataset R/A/Bのtopic_ja/hook_ja全文が含まれないことを機械検査→`contamination_check.json`(検出があれば該当Queryを破棄し再生成、2回目も検出ならSTOP)。
- call上限: web_search 28 call(20+8)、非search 6 call(Teacher/Query/Gate×2/診断/Selection)+分類1+Sol 1。費用を逐次集計し¥130(Main)到達見込みで次stepへ進まずSTOP。

### Fable評価・報告用
- REPORT `TOPIC-SELECTION-SEARCH-TRIAL-03_REPORT.md`: §1 Search期間・条件・model/§2 Lane定義/§3 Teacher定性記述・初期Query全文/§4 初期Pool(件数・レーン別・Gate前後)/§5 自己診断結果・追加Query全文/§6 追加Pool/§7 Source Gate結果(分類別件数・除外一覧)/§8 最終20件(全項目)+予備/§9 比較表(4集合)/§10 PR混入状況/§11 Search回数・model実値・tokens・latency・cost(step別)/§12 Fable追加arm(Sol Selection)結果と差分/§13 非混入検査/§14 Fable記入欄(改善点・弱い部分・Status・UDR)`[Fable記入]`/§15 Production変更なし。

## 実行コマンド全文

```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er016_topic_selection_search_trial_03.py --out-dir er016_output\topic_selection_search_trial_03 --step teacher
.venv\Scripts\python.exe er016_topic_selection_search_trial_03.py --out-dir er016_output\topic_selection_search_trial_03 --step queries1
.venv\Scripts\python.exe er016_topic_selection_search_trial_03.py --out-dir er016_output\topic_selection_search_trial_03 --step search1 --max-calls 20
.venv\Scripts\python.exe er016_topic_selection_search_trial_03.py --out-dir er016_output\topic_selection_search_trial_03 --step gate1
.venv\Scripts\python.exe er016_topic_selection_search_trial_03.py --out-dir er016_output\topic_selection_search_trial_03 --step diagnose
.venv\Scripts\python.exe er016_topic_selection_search_trial_03.py --out-dir er016_output\topic_selection_search_trial_03 --step search2 --max-calls 8
.venv\Scripts\python.exe er016_topic_selection_search_trial_03.py --out-dir er016_output\topic_selection_search_trial_03 --step gate2
.venv\Scripts\python.exe er016_topic_selection_search_trial_03.py --out-dir er016_output\topic_selection_search_trial_03 --step select --model luna
.venv\Scripts\python.exe er016_topic_selection_search_trial_03.py --out-dir er016_output\topic_selection_search_trial_03 --step verify
.venv\Scripts\python.exe er016_topic_selection_search_trial_03.py --out-dir er016_output\topic_selection_search_trial_03 --step select --model sol --arm fable_selection_model
.venv\Scripts\python.exe er016_topic_selection_search_trial_03.py --out-dir er016_output\topic_selection_search_trial_03 --step compare
.venv\Scripts\python.exe er016_topic_selection_search_trial_03.py --out-dir er016_output\topic_selection_search_trial_03 --step contamination-check
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\TOPIC-SELECTION-SEARCH-TRIAL-03.md --json-out docs\pm\delegation_log\TOPIC-SELECTION-SEARCH-TRIAL-03.md_check.json
git status --short
```
(新規script `er016_topic_selection_search_trial_03.py`。既存`er016_*`はimportのみ。各stepは費用累計を`cost.json`に更新し、上限到達見込みで非0終了+`stop_reason.json`。)

## SSOT追記文

なし。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `er016_topic_selection_search_trial_03.py`、`er016_output/topic_selection_search_trial_03/`(配下全て)、`TOPIC-SELECTION-SEARCH-TRIAL-03_REPORT.md`、`USER_EVAL_TRIAL03_20.md`(root直下)、`docs/pm/delegation_log/TOPIC-SELECTION-SEARCH-TRIAL-03.md`、同`_check.json`。
メッセージ: `TOPIC-SELECTION-SEARCH-TRIAL-03: 面白さの型5レーン探索→Source品質Gate(OPEN-174統合)→不足タイプ自己診断→追加探索→Selection Gateで20件候補(Luna)、Sol Selection比較arm、Reference/A/Bとの型比較(Production変更なし)`
trailer: `Management-ID: TOPIC-SELECTION-SEARCH-TRIAL-03`
STOP時もそこまでをcommit(`STOP:`接頭)。

## 報告(RESULT_PACKET_TS3項目)

0. T-0結果。
1. Search期間(実際の窓)・条件・model実値(全call)。
2. Lane定義・Teacher定性記述(全文)・初期Query 20本全文・追加Query全文。
3. 初期Pool件数(レーン別、Gate前/後)、追加Pool件数、統合Pool件数。
4. 自己診断結果(不足タイプ、根拠)。
5. Source Gate: 分類別件数、除外一覧(title/媒体/理由)、除外率(50%超か)。
6. 最終20件+予備5件(全項目。RESULT_PACKETにも転記)、公開日時検証結果、Referenceとの話題重複数。
7. 比較表(4集合の型比率・PR混入率・国内比率)。
8. Sol Selection arm: 20件、Luna選定との重複数・差分、費用。
9. Search回数(round別)・tokens・latency・cost(step別・合計、¥200以内か)。
10. 非混入検査結果(検査文字列数・検出0か・破棄再生成の有無)。
11. `USER_EVAL_TRIAL03_20.md`の絶対パス。
12. Production/SSOT無変更、`git status --short`、commit SHA、push結果。
13. 一覧外Read/Grepの理由、STOP該当の有無、Fable/ユーザー判断が必要な事実(提案はしない)。

---
【ユーザー指示全文】(delegation_logへそのまま保存)

管理ID: `TOPIC-SELECTION-SEARCH-TRIAL-03`

## 目的
NewsのTopic Searchについて、Reference級の「聞きたくなる素材」を、自律的に発見できる検索・選定方式を改善する。今回の主目的はHook改善ではなく、検索・Source Selection・最終Topic Selectionそのものの品質改善である。Production実装は行わない。

## 背景
これまでのユーザー評価では、概ね以下の品質差が出ている。Reference 20件: 平均約5.95、5点以上16/20/ChatGPT API-only 20件: 平均約4.5、5点以上10/20/Luna API 17件: 平均約2.53、5点以上0/17。また、既知のReference記事・特徴を具体的に検索すると見つかるケースがあることから、「Web上に良い記事が存在しない」のではなく、自律的なQuery設計・探索・選定が弱いことが主要因と考えている。

# 今回の基本仮説
仮説1: カテゴリ検索だけでは弱い。「AI」「健康」「旅行」などのカテゴリ検索だけでは、説明的/固い/社会的重要性はあるが聞きたくならないTopicが増えやすい。したがって、カテゴリーではなく「面白さの型」から検索するレーンを重視する。
仮説2: 一発検索ではなく探索→不足診断→追加探索が必要。1.複数レーンで初期探索 2.候補Poolを確認 3.足りない面白さタイプを診断 4.追加Queryを生成 5.再探索 6.最終Selection という反復型探索を試す。
仮説3: SearchだけでなくSelectionも重要。検索できても、社会的重要性が高いTopic/技術的に新しいTopic/軽いだけのTopic を過大評価すると、最終20件が弱くなる。最終Selectionでは「広い人が聞きたくなるか」を独立した観点として強く扱う。

# Search Lane
Lane A: Unexpected Reversal(一見Aだが実はB/技術の裏に人間/便利になるはずが別の問題/常識の逆転)。Lane B: Everyday Why(日常で自然に「そういえば、なんで？」と思える話。例: なぜ旅行バッグは毎回いっぱいになるのか/なぜ眠れないだけで病院へ行っていいのか/なぜ○○が最近増えているのか)。Lane C: Personal Relevance(「自分にも関係ありそう」。生活、仕事、スマホ、買い物、睡眠、旅行、食事、家、通勤など)。Lane D: Talkability/Casual(友人に「これ知ってる？」と話しやすいTopic。SNS、小さな流行、ちょっと変な現象、身近な驚きなど。ただし、単に軽いだけの記事は選ばない)。Lane E: Big Change in One Sentence(一文で「世の中が少し変わった」と感じられるニュース。AI、人間の役割、働き方、生活習慣、社会の変化など)。

# 初期探索後の自己診断
初期Candidate Poolを作った後、「Referenceに比べ、どのタイプが不足しているか」を診断する(Everyday Whyが少ない/人間的な逆転が少ない/国内生活系が少ない/俗っぽいTopicが少ない/技術ニュースに偏っている/硬い社会ニュースが多すぎる等)。その診断結果から追加Queryを自動生成して再Searchする。最初から固定Queryを大量投入するだけではなく、結果を見てSearch戦略を修正すること。

# Query設計
カテゴリ名だけで検索せず、人が「なぜ？」「え、本当？」「それ自分にもある」と感じる構造をQueryへ反映する。ただし、ReferenceのタイトルやHookをそのままQueryに埋め込み、既知記事を当てに行くのは禁止。ReferenceはTeacher Dataとして使ってよいが、具体的な正解記事を検索するカンニングにはしない。

# Source Quality Gate — OPEN-174統合
以下は原則として候補から除外または強く減点する: PR記事/Sponsored・Advertorial/アフィリエイト記事/「おすすめ○選」/ECランキング/楽天・Amazon等の売れ筋ランキング中心/セール訴求/価格比較中心/購買誘導中心/商品購入が記事目的になっているもの。ただし、商品・サービスを扱うニュース自体は禁止しない(新しい生活習慣/消費者行動の変化/新サービスの社会的影響/なぜ売れているかという現象などは候補にしてよい)。問題は、Topicが面白いかどうかではなく、Source自体が広告・販促記事になっているケースである。

# Selection Gate
1.聞きたくなるか(タイトルを聞いただけで「続きが少し気になる」となるか) 2.一般性(一部専門家だけではなく比較的広い人に届くか) 3.自分事性(生活・仕事・人間関係・社会変化などとの接点) 4.意外性/Reversal(単なる新情報ではなく「そうなの？」があるか) 5.Talkability(人に話したくなるか) 6.Audio適性(数字・固有名詞・統計・専門説明が大量に必要にならないか) 7.Source品質(PR・広告・販促記事ではないか)。

# 注意
社会的重要性が高い≠聞きたい/技術的に新しい≠面白い/軽い話題≠面白い/有名企業の記事≠広く聞きたい を混同しない。

# Teacher Data
既存のユーザー評価済みDataを使うこと(Reference 20/ChatGPT API-only 20/Luna API 17/ユーザー1〜10評価/5以上=現時点で採用可能)。ただし低評価TopicもHook改善で上がる可能性があるため「5未満＝Topic自体が完全に悪い」と固定しない。今回評価するのは、Topic+Sourceの素材としての強さを中心とする。

# Hookについて
今回、最終Topicに独立したHook生成は不要。検索品質とHook品質を混ぜない。最終候補については、Topicの短い説明/「なぜ聞きたくなる候補なのか」程度の内部評価で十分。Hook Writer Trialは別管理。

# Main Trial
まず上記方式で20件の候補を作成する。可能ならReference評価時と近い時間窓・条件を使う。検索対象期間を明記すること。

# 比較
最低限以下と比較する: 1.Reference 20 2.ChatGPT API-only 20 3.Luna API 17 4.今回Trial-03。比較項目: Topicタイプの多様性/Everyday・Personal系比率/硬い社会ニュース比率/Tech偏重/PR・広告Source混入率/Talkability/Audio適性/Referenceで強かったPatternの再現度。

# ユーザー評価用Output
ユーザーが評価しやすいように20件を一覧化する。各候補について最低限: Topic/日本語での簡潔な内容説明/Source/Search Lane/なぜ候補に残したか。ただし内部Scoreやモデルの長い理由はユーザー向け一覧を読みづらくしないこと。

# Claude独自の追加Trialを許容
今回に限り、上記の基本方針をベースに、Claude/Fable側で有望な改善Ideaが見つかった場合、追加Trialを実施してよい。許容: 新しいSearch Lane/Query生成方法の比較/Search→Selection間のFiltering方法/Pool diversityの確保方法/Self-diagnosis方法/広いInterest Gateの改善など、Search/Selection品質を直接改善するTrial。禁止: Production実装/Production Prompt変更/Writer Prompt変更/Hook Writer改善/Audio生成/新しい記事生成方式/ユーザー承認なしの正式仕様採用。追加Trialで良い結果が出てもVALIDATED止まり。

# 追加Trialの運用
追加Trialを行う場合、何を疑ったか/なぜ試したか/Main Trialとの差/結果/Cost/採否候補 を報告する。無制限に試行しない。同じ方向で改善が出ない場合は深追いせずSTOP。

# Cost / QCD
Main Trial+Claude独自追加Trialを含め、総費用上限¥200を目安とする。上限超過が必要な場合はSTOPして報告。特にWeb Searchの大量反復でCostを膨らませない。以前のように「Searchを何度も追加したが品質がほとんど改善しない」状態を避ける。

# Status
開始時`TRIAL`。最大到達Status`VALIDATED`。終了時にREJECTED/VALIDATED/USER_DECISION_REQUIREDを分類。良好でもProduction採用しない。

# Production / SSOT
Production Search/Router/Promptは変更しない。Trial artifactとして実施。Trial結果は保存するが、CURRENT_SPECへの正式仕様追加はユーザー判断後。

# STOP条件
Search Costが急増/同じQuery Patternの反復になっている/Candidate品質が明確に改善しない/Referenceを直接当てるQueryになっている/PR・広告記事の除外がTopic Diversityを過度に壊す/新しい仕様判断が必要/Production変更が必要。

# 最終報告
1.Search期間・Search条件 2.使用Lane 3.初期Query設計 4.初期Candidate Pool 5.不足タイプ自己診断 6.追加Search内容 7.Source Quality Gate結果 8.最終20件 9.Reference/API-only/Lunaとの比較 10.PR/広告混入状況 11.Search回数 12.model_id 13.tokens/latency/cost 14.Claude独自追加Trialがあれば全内容 15.何が改善したか 16.まだ弱い部分 17.Trial status 18.USER_DECISION_REQUIRED事項。完了後はSTOPし、ユーザー評価を待つこと。今回の最終評価は、モデル自身のScoreだけで確定しない。最終20件はユーザーが実際にTopicを見て評価することを前提とする。
