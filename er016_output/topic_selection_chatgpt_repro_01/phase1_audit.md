# Phase 1: 条件差分Audit(API実行前、文書のみ)

管理ID: TOPIC-SELECTION-CHATGPT-REPRO-01
作成時刻: 2026-09-24(JST、本文書作成時点)

本表はAPI実行前に作成する。「ChatGPT実行」列はユーザー指示原文に明記された
事実のみを記載し、原文に無い項目は「不明」とする(推測で埋めない)。
「前回Trial-01」列は`TOPIC-SELECTION-LUNA-API-TRIAL-01`(2026-09-24T07:48
JST実行、`er016_output/topic_selection_luna_api_trial_01/`)の実際の
`run_meta.json`・`prompts/*.json`から抽出した事実。「今回」列は本委任の
Fable設計。

| 項目 | ChatGPT実行(ユーザー指示記載事実) | 前回Trial-01(実績) | 今回(本Trial設計) |
|---|---|---|---|
| 検索基準時刻 | 2026-09-23 21:05 JST(ユーザー指示「実行日時」として明記) | `T_now`=実行時刻の実時刻(2026-09-24T07:48:25 JST、probeコマンド実行時に`datetime.now(JST)`で取得) | 2026-09-23 21:05 JST固定(`--window-end`引数で指定、実行時刻とは独立) |
| 検索期間 | 不明(ChatGPT側の「直近24時間」の運用実態・API/Web Search実装は非公開) | `T_cut`=`T_now − 24h`(2026-09-23T07:48:25 JST 〜 2026-09-24T07:48:25 JST、実行時刻に連動するスライド窓) | 2026-09-22T21:05 JST 〜 2026-09-23T21:05 JST固定窓(実行時刻に連動しない) |
| Search backend | ChatGPT Web Search(ChatGPT製品内蔵、非公開実装) | OpenAI Responses API `web_search`tool(`tools=[{"type":"web_search"}]`) | 同左(OpenAI Responses API `web_search`tool)。ChatGPT Web Search自体は本Trialでは使用不可(API経由再現の対象範囲外) |
| query設計 | 不明(ChatGPT内部のquery生成はSonnet側から不可視) | Luna(モデル)が各レーンPrompt文面から自律的にquery生成(Sonnet側でqueryを直接指定していない) | 同左。ただしPromptに「2026年9月23日」等の日付語を候補query生成の手がかりとして明記する点が前回と異なる(時刻窓固定に伴う追加) |
| 探索カテゴリ | ユーザー指示に列挙: 日本国内News/海外一般News/国際/経済/AI・Technology/Science/Health/Consumer/Lifestyle/Food/Travel/Fashion/Culture/Entertainment/Sports/新商品・新サービス/SNS話題/Google Trends等/軽い話題/俗っぽい話題(カテゴリ均等化は明示的に否定) | 5レーン(general/everyday/scitech/light/sns)。粒度が今回より粗い | 8サブレーン(1.国内一般News/2.海外一般・国際・経済/3.AI・Tech・Science/4.Health・睡眠・医療調査/5.生活・Consumer・Food・コンビニ・新商品/6.Travel・Fashion・Culture・Lifestyle/7.Entertainment・Sports・ゲーム・芸能/8.SNS・Trend Signal)。ユーザー指示のカテゴリ列挙へ「ChatGPT条件へ揃えるため」細分化 |
| SNS・Trendの扱い | 「日本人が今何に反応しているかを発見するDiscovery Signal」「SNSだけをEvidenceにしない」「2026-09-23 21:05 JST時点で話題性があったかというSignalも見る」 | SNSレーンで`signal_source`/`signal_time_as_shown`/`confirm_source_url`を収集(実体確認、null許容) | Phase 0で09-23アーカイブSignal取得可否をプローブしてからサブレーン8で実施。`signal_source_url`/`signal_time_as_shown`/`entity_url`を収集する点は類似だがPhase 0切り出しが今回追加(時刻窓固定に伴う「アーカイブ到達可否」の事前確認が必要なため) |
| Candidate pool規模 | 不明(ChatGPT側の内部候補数は非公開、最終出力20件のみが既知) | 5レーン×10〜15件 = 約50〜75件(Phase 1合計) | 8サブレーン×12〜15件 = 約96〜120件(Step A合計)。前回より細分化・増量 |
| Topic selection instruction | ユーザー指示Step B: 身近/純粋に理由を知りたい/意外/生活に関係/人に話したくなる/軽く面白い/大きな世界の変化、の7観点。「カテゴリを均等に埋めることではない」 | Phase 3(rank)で選定基準とHook・distance・dedupeを同時に扱う単一プロンプト | Step B(選定のみ、最大40件)とStep E(最終20件選定)に分離。Step Bはユーザー指示Step Bの7観点のみを使用する点が前回と異なる(「ChatGPT条件へ揃えるため」選定とHookを別工程化) |
| Hook生成instruction(例示の有無) | ユーザー指示Step C: 「元記事のHeadlineを疑問形にするのではない。一段抽象化・再解釈」。例2つ明記(台風停電/Meta Muse) | Hook絶対条件4項目(釣り禁止・答えられない疑問禁止・Fact以上の断定禁止・実質的に答えられる必要)を文章で指示。具体例の提示は無し | Step Cで同条件に加え、ユーザー指示の例2つ(台風停電/Meta Muse)をPromptに明示的に例示として含める点が前回と異なる(「ChatGPT条件へ揃えるため」抽象化・再解釈の要求を具体例で補強) |
| Ranking基準 | ユーザー指示§1: 探索範囲の広さ/Topicの質/多様性/日本人距離/俗っぽさ/Hook/聞きたい品質の7観点、§4距離の考え方(国ではなく心理的距離) | Phase 3で距離・特徴・俗っぽさ・dedupe・beyond_article等を単一Promptで判定 | Step E(独立工程)でユーザー指示§1の7観点要旨+§4距離の考え方のみを渡す。Hookは書き換えさせない制約を明記(前回はHook生成とRankingが同一Promptに混在していなかったが、選定基準の粒度をユーザー指示の文言に近づけた点が異なる) |
| 検証の位置(Ranking前後) | 不明(ChatGPT側の検証工程は非公開) | Phase 4(verify)はPhase 3(rank、最終20件選定)の**後**にHTTP検証を実施(20件のみ検証) | Step D(verify)はStep E(最終20件選定)の**前**に全Step C通過候補を検証し、機械的に除外してからStep Eへ渡す。除外基準(404/outside_window/NOT_IN_SOURCE/url_in_citations=false)を事前適用する点が前回と異なる(「ChatGPT条件へ揃えるため」というより、ユーザー指示のStep D「HookとNews内容の整合確認」をStep E選定前に置く設計指示に従った) |
| モデル | 不明(ChatGPT製品の内部モデル、GPT系列と推測されるが型番非公開) | `gpt-5.6-luna`(`routing.WRITER_MODEL`)、`effort=medium`固定 | Phase 0/2(Step A〜E)/Phase 4(a)(b)は`gpt-5.6-luna`・`effort=medium`。Phase 4(c)のみ条件付きで`gpt-5.6-sol`を1回、Phase 4(d)のみ`effort=high`で1回(診断目的、委任文で明示許可) |
| reasoning effort | 不明 | `medium`固定 | 同左(`medium`)。Phase 4(d)のみ`high`で比較実施(条件付き) |
| 1 callあたりのcontext | 不明 | レーンごとの候補件数がPhase 2(hooks)・Phase 3(rank)へ全件まとめて渡される(Phase 2は5レーン合計約50〜75件を1 callで処理) | Step B以降は8サブレーン合計約96〜120件を1 callで処理(前回よりcontext量が増加。件数増に伴う自然な帰結であり意図的な条件変更ではない) |
| 対話的反復の有無 | 不明(ユーザーがChatGPT上で対話的にフォローアップした可能性は本委任文からは不明) | 無し(各Phase 1 callで完結、フォローアップなし) | 無し(各Step 1 callで完結)。Phase 4は診断目的の追加callのみ |

## 今回の設計が前回と異なる点(「ChatGPT条件へ揃えるため」の変更、まとめ)

1. 時刻窓を実行時刻連動のスライド24hから、ユーザー指示の固定窓
   (2026-09-22T21:05〜2026-09-23T21:05 JST)へ変更。
2. 探索レーンを5→8へ細分化(ユーザー指示のカテゴリ列挙に近づけるため)。
3. Topic選定(Step B)とHook生成(Step C)とRanking(Step E)を3工程に分離
   (前回はHook生成とRanking相当の判断が一部同一Promptに混在)。
4. Hook生成Promptに具体例2つを明示追加(ユーザー指示Step Cの「一段抽象化・
   再解釈」という抽象的要求を、具体例で補強するため)。
5. 検証(Step D)をRanking(Step E)の**前**に移動し、機械的除外を先に適用。
6. Phase 4として検索/Hook/モデル/effort差分切り分けの診断工程を新設
   (前回Trial-01には無かった、Reference Outputとの比較のための追加)。

## 時刻窓の再現限界(制約の明記)

- OpenAI `web_search`ツールには日付フィルタ引数が無い。本Trialでは
  (1)Promptに窓を明記しqueryに日付語を含めさせる、(2)候補の
  `published_time_as_shown`を申告させる、(3)Step Dでスクリプトが記事
  ページのメタ時刻を実取得し窓内判定する、の3段で時刻窓を近似的に実現する。
- 検索インデックスは現在時点(2026-09-24)のものであり、2026-09-23当時に
  ChatGPT Web Searchが「見えていた」検索結果集合を完全に再現することは
  技術的に不可能である。2026-09-24公開の記事はStep D窓内判定で
  `outside_window`として除外される。
- SNS/Trend Signal(Step Aサブレーン8)は「2026-09-23時点のアーカイブ
  ページ」(トレンドカレンダー日付別ページ、Twittrend時間別アーカイブ、
  Google Trends日次等)を対象とするが、これらアーカイブページの実在・
  アクセス可否はPhase 0のプローブ結果に依存する(未確認)。
