# FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-DESIGN-01 報告書

管理ID: FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-DESIGN-01。
**設計+Trial提案のみ(¥0、API呼び出しなし)。Production経路・Future設計
成果物(`EDITORIAL-FUTURE-*`、`er013_*`)・SSOT本文・Gitは一切変更していない。
Production採用の承認ではない。**

## ユーザー指示(原文)

> Discovery Focus Module Part Aは(a) Production案の再設計へ進めてください。これはProduction採用の承認ではありません。
> Point Role PlanningへFocusの方針、特に「Main Storyで何を示し、何をPointへ展開するか」を渡す接続案を設計してください。ただし、B1での書き分けの弱さや記事間の角度の類似が未接続に起因するかは未検証です。原因と決めつけず、Focus単独案と接続案を比較できる小規模Trialを提案してください。
> 評価にはFact Safety・REVIEW_REQUIRED・retryに加え、A2/B1それぞれの書き分け、Pointの価値と多様性、記事としての面白さを含めてください。前回のSonnetによる0〜2点は主観評価として扱い、採点根拠と実際の記事を私が確認できる形で提示してください。試行費用の見積もりと新規記事テーマ候補を先に報告し、テーマ選定と費用を伴う実行は私の判断を待ってください。既存Productionと並行中のFuture設計は変更しないでください。

## 0. 重要な事前発見(既存Trial-03の存在)

調査の過程で、本タスクが要求する接続メカニズムと本質的に同じものが、
**News/major_daily_news向けに既にTrial実施・Gate 1=VALIDATED判定済み**で
あることを発見した:`FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-CONNECTION-
TRIAL-03_REPORT.md`(未Production配線、`er011_point_role_planning_focus_
connection_trial_03.py`)。

- 途切れ箇所は本タスクの前提と同一:`run_point_role_planning(client, topic,
  verified_ledger_text, model, reasoning_effort)`は`editorial_type_module_
  block`を一切受け取らない(同ファイル124-145行)。
- 既に汎用の接続メカニズムを実装済み:`run_point_role_planning_connected`/
  `run_one_pattern_connected`(いずれも新規optional引数`point_role_hint_
  block: str = ""`を追加しただけのコピー、**monkeypatchは明示的に不使用**、
  Production 3ファイルは無編集[grep差分ゼロ、Gate 4 PASS])。
- `point_role_hint_block`は`topic`/`verified_ledger_text`と同じく**プレーン
  文字列引数**であり、News固有のハードコードは無い。News用の中身
  (`MAJOR_DAILY_NEWS_POINT_ROLE_HINT_BLOCK`)を渡しているだけで、**Discovery
  用の文字列を新規に用意して同じ関数へ渡せば、Discovery向け接続として
  そのまま再利用できる**(関数自体の再設計・再実装は不要)。
- News(major_daily_news相当、Hanshin Ledger)でのruntime検証(text-onlyまで、
  TTS未実行、¥12.0/22 calls)で、Point Role Planningの`role`出力がhintの
  語彙(mechanism/beyond-the-headline factor/limitation)を実際に反映し、
  Writer本文にもそれが反映されることを確認済み(B1B: OK、A2: 既存の
  overlap論点でNG_REVIEW_REQUIRED、原因はhint接続とは無関係と分析済み)。

したがって本タスクの設計は、**ゼロから接続メカニズムを考案するのではなく、
Trial-03が既に検証済みの汎用メカニズムに、Discovery固有のhint内容を新規
設計して載せる**ことが最小リスク・最小重複の経路である。ただし、Trial-03は
News向けの検証でありDiscovery向けには未検証(A2/B1の書き分け・Main Story
抑制という今回固有の論点はTrial-03では評価対象外だった)。この差分は本設計の
小規模Trial(3節)で埋める。

## 1. 接続案の設計(実装しない)

### 1-1. 比較した案

| 案 | 内容 | Trial-03での位置づけ | 評価 |
|---|---|---|---|
| 案1(Focus Module直接注入) | Discovery Focus Module Part A全文をそのまま`point_role_hint_block`へ渡す | Trial-03の(a)、unit testで実現可能性のみ確認・runtime検証はしていない | Main Story向けの長い一般指示(In One Line方針等)まで混入しノイズが大きい。Trial-03も非推奨と結論済み |
| **案2(推奨、Trial-03の(b)相当)** | Point Role Planning用に短く絞った「役割候補文」を新規作成し`point_role_hint_block`へ渡す | Trial-03の(b)、Newsでruntime検証済み(role出力に反映確認) | schema呼び出しの性質(6項目JSON)に合う短文。News実績あり。Discovery用文言のみ新規設計すればよい |
| 案3(role plan出力側にmain_story_scopeフィールド追加) | `_ROLE_PLAN_FIELDS`にMain Story側の制約を書き戻すフィールドを追加し、`build_role_planning_block`のレンダリングにも反映 | Trial-03では扱っていない(入力側のみ) | JSON schema変更を伴うため影響範囲が広い(Point Value QA等の下流は無関係だが、schema自体は`strict: True`のadditionalProperties: False)。案2の効果を見てからの拡張候補として温存 |

**推奨: 案2(Trial-03の(b)方式を踏襲)**。理由:
- 同一メカニズムがNewsで既にVALIDATED(既定値バイト不変・Trend Synthesis
  非影響・Diagnostic Full Retry経路への引き継ぎ・Dangling Referenceなし
  を確認済み)であり、Discoveryへ流用してもこれらの安全特性は変わらない。
- 案1のようにMain Story向けの長い一般指示を混入させない。
- 案3のスキーマ変更を伴わない(既存の6フィールド出力形式・Point Value QA/
  Point Overlap QAとの整合を変更しない)。

### 1-2. Discovery向けhint文言案(新規設計、未配線、draft)

Focus Module Part Aが実際に述べている2つの方針
(「Main Storyでは現象提示に留め、なぜの答えを完結させない」
「Point One・TwoでMain Storyが残した『なぜ』を異なる角度から一つずつ
深掘りする」)を、News同様の「短い役割候補文」形式に圧縮する案を
`er011_discovery_focus_role_planning_connection_draft_01.md`に用意した
(英語1段落、News hintと同じ体裁)。

### 1-3. 重要な限界(未接続と決めつけないための注記)

`build_role_planning_block()`の出力はWriter promptの**末尾**に追記される
ため、Main Story生成前にWriterはこれを読める(1回のLLM呼び出しで記事
全体を生成するため)。したがって理論上はMain Story抑制にも間接的に効く
可能性があるが、**Trial-03のNews runtime検証はPoint側のrole反映しか確認
していない(Main Story抑制効果は未検証)**。この点は本タスクのTrial(3節)
で初めて検証されることになる。

Main Story抑制をより直接的に狙うなら、hint文中に「これらの具体的な機序・
数値はPointに委ねられるため、Main Storyでは述べないでください」という
逆方向の一文を明示的に加える変種(案2')も考えられる。これは案3のような
schema変更を伴わない(`build_role_planning_block`のレンダリング文言を
増やすだけ)。draftファイルに案2・案2'の両方を記載した。**案2'はNewsでも
未検証の新規要素であり、小規模Trialでの検証対象に含めることを提案する**
(4節で言及)。

### 1-4. 変更箇所(実装する場合、実装はしない)

Production配線が将来承認された場合の変更箇所はTrial-03報告書6節が既に
提示済み(`ROLE_PLANNING_PROMPT_TEMPLATE`へのplaceholder追加、
`run_point_role_planning`/`run_one_pattern`への同名optional引数追加、
既定値""でバイト不変)。Discovery固有の追加作業は、Discovery用hint定数の
新規追加と、`resolve_editorial_type_module_block`相当のDiscovery向け解決
ロジック(現状Discoveryは`EDITORIAL_TYPE_MODULE_BLOCKS`辞書に未登録)のみ。
**今回は設計のみで、これらのファイルは一切編集していない。**

## 2. 接続なしでも改善しうる別要因(原因と決めつけないため)

| 要因 | Trialで切り分け可能か |
|---|---|
| モデル非決定性(role planが毎回異なる切り口を割り当てる) | 各条件N=2runにすれば方向感は得られる(3節の8記事案) |
| B1 instruction自体がFocus方針をA2ほど強く反映していない | **本Trialでは切り分けられない**(instruction自体は変更しない条件設計のため)。接続ありでもB1のMain Story抑制が改善しなければ、この要因の疑いが強まる間接的材料にはなる |
| Verified Fact Ledgerの具体値(ACTH等)が目立ちWriterが使いたくなる | 同上、切り分け不可。ただしLedger側の記述密度を変えずに接続の有無だけを操作するため、効果があれば「具体値の多さ」だけが単独原因ではないと言える |
| Point Role PlanningがMain Story方針を知らない構造(接続なし) | 本Trialの主目的、直接切り分け可能 |
| Evidence Compression Editor / Local Rewriteの事後編集が具体値を残す方向に働く | 追加コストなしで確認可能(`pre_editor_article.md`と`article.md`の差分を見るだけ、既存監査ログ) |
| cross-article角度収束(記事間の角度の類似) | 本Trialは同一テーマ・同一Ledgerのみで、他テーマとの比較を含まないため**切り分け不可**(直前Trialの限界と同じ、ユーザー指示にある「未検証」の通り) |

## 3. 小規模Trial提案(実装しない、Fable/ユーザー判断待ち)

### 3-1. 実行方式(Production無変更の確認)

新規Trial driver(`er011_discovery_focus_role_planning_connection_trial_XX_
run.py`、新規ファイル、Production未編集)で:
- `er011_discovery_focus_module_revalidation_01_run.py`のLedger再利用・
  出力構造・Fact Checker/Ledger Deviation/comparison HTML生成ロジックを
  そのまま流用。
- 「focus単独」条件は`build_common_block(..., editorial_type_module_block=
  DISCOVERY_FOCUS_MODULE_PART_A_BLOCK)`のまま**Production関数`run_one_
  pattern`を無変更で呼ぶ**(接続なし)。
- 「focus+接続」条件は、同じ`editorial_type_module_block`付きpromptを
  `er011_point_role_planning_focus_connection_trial_03.run_one_pattern_
  connected`(importして再利用、コピー不要)へ渡し、新規`point_role_hint_
  block=DISCOVERY_WHY_POINT_ROLE_HINT_BLOCK`を追加する。
- 実行前にTrial-03同様のGate 4静的確認(Production 3ファイルの無編集を
  grep差分で再確認)を行う。**Trial-03実施時点から時間が経っているため、
  Production側が変更されていないかの再確認は省略しない**(6節リスク参照)。

### 3-2. 規模案と費用見積り

前提: 直前Trial(`FAMILY-A-DISCOVERY-FOCUS-MODULE-REVALIDATION-01`)の
focus単独A2/B1記事(¥30.54+¥23.81=¥54.35相当)は**再利用し再生成しない**
(同一Ledger)。Ledger/Research自体も既存流用時は¥0(新規テーマ選定時は
¥55.47[前回実測]が別途必要)。

| 規模案 | 構成 | 新規生成が必要な記事数 | 費用見積り(既存Ledger再利用時) | 上限案 |
|---|---|---|---|---|
| 最小(4記事) | focus単独(A2/B1、再利用)+focus+接続(A2/B1、新規) | 2本 | ¥55〜70(News実測¥12.0/2本×A2 retryありのTrial-03単価感応を加味) | ¥150 |
| N増し(8記事) | 上記2条件×2run(focus単独は1runのみ既存流用、残り6本新規) | 6本 | ¥160〜190 | ¥400 |

新規テーマを選ぶ場合は、上記いずれの規模案にも¥55.47(Research+Ledger、
1回のみ、両条件で共有)を加算(最小4記事案: 実測目安¥110〜125、上限
¥250/N増し8記事案: 実測目安¥215〜245、上限¥500)。

**テーマ選定・Trial規模・費用上限の最終決定はユーザー判断待ち
(USER_DECISION_REQUIRED)。API呼び出しは行っていない。**

## 4. 評価設計

比較対象記事4〜8本について、以下を1つのHTML/Markdown比較artifact
(直前Trialの`comparison.md`/`index.html`形式を踏襲)にまとめる:

1. **Fact Safety系(客観)**: Fact Checker verdict、Ledger Deviation
   status(逸脱件数・重大度)、Directional Fact Precheck結果、
   REVIEW_REQUIRED発生有無、Point Overlap QA NG/retry回数、Local
   Rewrite適用有無。
2. **書き分け(A2/B1それぞれ)**: Main Story抑制度合い(現象提示のみに
   留まっているか、機序・具体値の残存有無を該当文引用で提示)、Point
   への繰り延べ度合い(role planの`evidence_anchor`/`must_not_overlap_
   with_full_story`と実際の本文の対応表を新規追加し、計画通りに実装
   されたかを機械的に突き合わせる)。
3. **Pointの価値と多様性**: 記事内(Point One対Two)の重複有無・新しい
   示唆の有無(該当文引用必須)、cross-article角度の重複(本Trialの
   4〜8本間、および直前Trial/前々回Trialとの角度比較、可能な範囲で)。
4. **記事としての面白さ**: 0〜2点、**主観評価であることを明記**し、
   採点根拠となる本文中の具体的な文を必ず引用する(引用なしの採点は
   記載しない)。
5. **比較artifactの構成**: 各記事について、本文全文・role plan JSON・
   上記1〜4の評価・「Main Storyに残した要素/Pointへ繰り延べた要素」の
   対応表を、A2/B1・focus単独/focus+接続を並べて閲覧できるレイアウトで
   提示(前回同様、ユーザーが実際の記事を確認できる形)。

## 5. 新規記事テーマ候補(PM_GOVERNANCE.md 13節準拠、Fable/Sonnetは選定しない)

Household以外のDiscovery/Whyテーマ候補(英語・日本語・短い選定理由):

| # | English | 日本語 | 選定理由(短) |
|---|---|---|---|
| 1 | Why do we get goosebumps even when we're not cold? | なぜ寒くないのに鳥肌が立つのか | 日常的で誰もが経験する現象、専門的すぎない |
| 2 | Why does time seem to speed up as we get older? | なぜ歳を取ると時間が早く感じるのか | 一般的関心が高い心理学トピック、最終版候補になりやすい |
| 3 | Why is yawning contagious? | なぜ他人のあくびがうつるのか | 定番のDiscovery/Whyテーマ、エビデンスが集めやすい |
| 4 | Why does music give us chills (frisson)? | なぜ音楽で鳥肌(chills)が起きるのか | ポップサイエンス的で面白さを狙いやすい |
| 5 | Why do embarrassing memories stick with us so vividly? | なぜ恥ずかしい記憶は鮮明に残るのか | 誰もが共感できる記憶心理学トピック |

**流用案(別枠、新規テーマ選定ルールの対象外)**: 既存Ledgerを流用する場合、
上記5候補より費用が安い(Research+Ledger再生成¥0):
- wake-before-alarm(`FAMILY-A-DISCOVERY-FOCUS-MODULE-REVALIDATION-01`の
  Ledger、直前Trialと直接比較できる利点あり)
- Towels(`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11`のLedger)

テーマ選定(新規5候補からの選択、または流用案の採用)はユーザー判断待ち。

## 6. STOP/リスク

- 接続メカニズム自体はNews向けにGate 1=VALIDATED済みだが、**Discovery向け
  runtime検証はゼロ**(本設計はNewsからの類推であり保証ではない)。
- 案2'(Main Story逆方向注記)はNewsでも未検証の新規要素であり、効果・
  副作用(Writerが過剰に萎縮し記事の面白さを損なう等)は小規模Trialで
  初めて分かる。
- Trial-03実施(このタスクより前の時点)からProduction側
  (`er003_v1_n3_01_articles_generate.py`/`er011_point_role_value_planning_
  01.py`)が変更されていないか、Trial実行前に再度Gate 4相当の静的確認が
  必要(現在の`git status`には両ファイルの変更は見られないが、実行時点で
  再確認すること)。
- 本Trialは同一テーマ・同一Ledgerのみのため、cross-article角度収束の
  原因切り分けはできない(2節参照、未解決のまま残る)。
- 接続を承認・Production配線する場合、Discovery Focus Module Part A自体の
  Production採用可否は別のユーザー判断であり、本設計・本Trialの結果が
  自動的にProduction採用を意味しない。
- 既存のPoint Overlap QA/Point Value QA/retry上限(2回)/Local Rewriteは
  そのまま維持し、独自に無効化・上限変更はしない。

## 7. 成果物パス

- 本ファイル(root)
- `er011_discovery_focus_role_planning_connection_draft_01.md`(hint文言案・
  ラッパー設計、未配線)
- `docs/pm/RESULT_PACKET_DFC.md`(短縮報告)
- 参照した既存成果物(無編集): `FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-
  CONNECTION-TRIAL-03_REPORT.md`、`er011_point_role_planning_focus_
  connection_trial_03.py`、`FAMILY-A-DISCOVERY-FOCUS-MODULE-REVALIDATION-
  01_REPORT.md`、`er011_discovery_focus_module_revalidation_01_run.py`、
  `er011_point_role_value_planning_01.py`、`er003_v1_n3_01_articles_
  generate.py`、`docs/pm/PM_GOVERNANCE.md`(13節)
