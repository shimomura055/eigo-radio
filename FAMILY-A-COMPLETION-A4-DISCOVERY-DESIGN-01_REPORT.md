# FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-01 — Discovery/Why 設計(読み取り専用・設計のみ)

管理ID: FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-01(Lane A、Step A4)
実施日: 2026-09-09
性質: **設計のみ**。Production実装・コード/Prompt/SSOT編集・Trial実行・
API呼び出し・Git操作は一切行っていない(費用¥0)。並列稼働中の他Lane
(A2 Trend end-to-end `er011_output/family_a_completion_a2_*`、Lane B 3V
Trial `er012_*`、LDC[Ledger Deviation Checker]コスト調査、SSOT統合)の
成果物は参照していない。`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は
編集していない。

前提: OPEN-135(Family A Completion Program、2026-09-09ユーザー正式決定)の
Step A4は「最初からProduction実装しない。設計判断はすべて
`USER_DECISION_REQUIRED`」と明記されており、本タスクは設計案の提示のみを
目的とする。以下のSSOT/Reportを実際に確認した(推測補完なし):
`FAMILY-A-COMPLETION-GAP-AUDIT-A1-01_REPORT.md`、
`FAMILY-A-DISCOVERY-DEFERRED-CLASSIFICATION-01_REPORT.md`、
`FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`、
`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01_REPORT.md`、
`OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`、
`OPEN112_NO18_4LAYER_REVIEW_PACK_06.md`(Trial-05詳細)、
`FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-CONNECTION-TRIAL-03_REPORT.md`、
`OPEN_ITEMS.md`OPEN-130/135行、`DECISION_LOG.md`A-UDR-9/10、
`POOL_TOPIC_MASTER.md`(No.1〜20全件)、
`er003_output/n3_01/household/b1b/article.md`(実記事本文)。

---

## 1. 対象定義(帰納)と排他的・再現可能な判定基準

### 1.1 過去記事からの帰納

| 記事 | 中心的主張の型 | 単一起点日付への圧縮可否 | 複数外部Signalの集約要否 | 備考 |
|---|---|---|---|---|
| Hanshin(阪神-広島戦) | 「[日付]にXが起きた」 | 可(1試合) | 不要 | Major/Daily |
| イラン情勢(複数外交Signal) | 「複数独立Signalが同方向を示す」 | 不可 | 必要(除去で主張崩壊) | Trend Synthesis |
| Health(UK Biobank単一研究) | 「[日付]に研究が発表され、Xを示した」 | 可(1研究発表という単一起点) | 不要 | Major/Daily(A-UDR-10で確定) |
| Household(冷蔵庫クリスパー) | 「なぜこの機構(湿度設定)がこう設計されているか」 | 不可(そもそも起点日付が存在しない) | 不要 | Discovery/Why候補(A-UDR-9) |
| No.18(通知を無視できない心理) | 「なぜこの持続的な心理現象が起きるか」(複数研究は証拠として引用、主張自体は研究発表日に依存しない) | 不可(2研究+調査を1つの日付に圧縮すると論旨が失われる) | 不要(Trendのように「どのSignalを除いても主張が残るか」を問う集約構造ではない) | Discovery/Why(既存baseline) |

**帰納された対象定義**: Discovery/Whyは、(a) 単一起点イベント(News)でも
(b) 複数独立Signalの集約による変化の主張(Trend)でもなく、(c) **持続的な
仕組み・メカニズム・設計理由・心理的パターンを「なぜそうなっているか」の
観点で説明する**、時期に依存しない(evergreen)コンテンツを対象とする。
研究・調査は「証拠」として引用されるが、記事の存在理由(newsworthiness)が
「その研究が最近発表されたこと」自体ではない点が、Major/Daily Newsの
単一研究発表記事(Health)との決定的な違いである。

**副次的発見(重要)**: `POOL_TOPIC_MASTER.md`の正式20 Topic(Pool型、
「特定の1件の最近の出来事に依存しない」と定義済み)は、No.1〜20**全件が
「Why」または「なぜ」を問うタイトル**であり(例: No.1「なぜ都市は公共
ベンチを見直し始めているのか」、No.13「アプリはなぜ通知をオンにして
ほしいのか」)、既存SSOTの定義上すでにDiscovery/Whyの実質的な母集団と
一致している可能性が高い。ただしPOOL_TOPIC_MASTER.md本体には
「Discovery/Why」という語自体は存在しない(grep未実施、既存報告
`FAMILY-A-BRANCH-FACT-CHECK-02`のCURRENT_SPEC.md grep結果[0件]から類推)。
この一致は**発見**であり、正式な再分類提案ではない(§6でユーザー判断
事項として提起)。

### 1.2 排他的・再現可能な判定チェックリスト(新規提案、未承認)

OPEN-130が指摘した「Major/Daily Gate 6項目は消去法的・非対称」という
問題を踏まえ、3 Editorial Type間で**相互排他的**に働くよう、以下の
5問を**この順序で**適用する一本の判定木として設計する(いずれかで
Yesが出たら判定確定・以降の質問は評価しない)。

1. **単一起点イベント判定**: そのMain Storyを「[日付]に、Xが起きた/
   発表された」という1文に圧縮しても要点が失われないか？
   → Yesなら`MAJOR_DAILY`(単一研究発表・単一試合・単一決定を含む)。
2. **集約変化判定**: 複数の独立した外部Signal(出来事・観測)のうち、
   いずれか1つを除いても「変化・傾向」という中心的主張は大きく変わらない
   か(=Trend成立条件)？
   → Yesなら`TREND_SYNTHESIS`。
3. **時事性依存判定(News hook test、本提案の核心)**: この記事が
   存在する理由が「これが最近発表・発生したこと」自体にあるか(=発表日を
   取り除くと記事の必然性が消えるか)？
   → Yesなら`MAJOR_DAILY`寄りに倒す(質問1でYesにならなかった場合でも、
   時事性が主たる動機なら通常Newsの一種として扱う趣旨)。
4. **メカニズム・説明判定**: 中心的主張が「なぜこの持続的な仕組み・
   構造・心理的パターンがこうなっているか」という説明であるか？
   → Yesなら`DISCOVERY_WHY`候補。
5. **evergreen耐久性判定**: 中心的主張は、ほぼ任意の日付に公開しても
   実質的に同じ妥当性を持つか(「今だから書く」必然性が無いか)？
   → Yesなら`DISCOVERY_WHY`を確定。Noなら、いずれの型にも明確に
   当てはまらない**判定不能(Gap)**として個別にユーザー判断を仰ぐ。

**境界事例への当てはめ(表1の記事に適用)**:

| 記事 | Q1 | Q2 | Q3 | Q4 | Q5 | 判定 |
|---|---|---|---|---|---|---|
| Hanshin | Yes | — | — | — | — | `MAJOR_DAILY` |
| イラン情勢 | No | Yes | — | — | — | `TREND_SYNTHESIS` |
| Health(単一研究) | Yes(研究発表という単一起点) | — | — | — | — | `MAJOR_DAILY` |
| Household | No | No | No | Yes | Yes | `DISCOVERY_WHY` |
| No.18 | No(2研究+調査を1文の起点に圧縮不可) | No(「変化」の主張ではない) | No(発表日依存ではない) | Yes | Yes | `DISCOVERY_WHY` |

**限界・正直な注記**: (a) Health/No.18の境界は、Q1の「単一起点への圧縮
可否」の判定に主観が残る(両者とも「研究」を引用する点は共通)。本提案は
Q1を「その記事の存在理由が発表イベント自体か、それとも証拠として引用
されただけの持続的現象か」で区別するが、**この区別自体が新規提案であり
Trial・ユーザー確認は未実施**。(b) Q3は既存Gate(News/Trend双方)に
存在しなかった**完全新規の質問**であり、既存SSOTのいずれの決定にも
根拠を持たない。(c) 本チェックリストは机上の帰納(5記事のみ)に基づく
ものであり、N数が少ない。採否・追加検証要否は§6でユーザー判断事項とする。

---

## 2. Discovery固有Research方式(設計案)

現状(Gap Audit確認済み): Discovery/Whyの研究収集は「共通経路のみ
(Fact Checkerの独立Web検索)」であり、**Discovery固有のResearch経路は
存在しない**。No.18のVerified Fact Ledgerが既存自動Research pipeline
(`er002_ja_web_research_r3.py`)経由で作られたか、人手WebSearchで作られた
かは、本タスク範囲では**不明**(いずれの報告にも明記なし)。

**設計案(新規提案、未検証)**: News(候補収集→Ledger化→Mode判定)・
Trend(独立Signal収集)とは異なり、Discoveryは「なぜ」という問いを起点に
**説明源**を集める方式が適すると考える。

1. **Why-question分解ステップ(新規)**: Discoveryテーマ(人間選定、
   POOL_TOPIC_MASTER.md由来)を、記事化前に「この現象を説明するために
   検証すべきサブ問い」へ分解する(例: Household「なぜガス放出食品と
   水分蒸発食品で扱いを変えるべきか」→「エチレンガスが何をするか」
   「高湿度がなぜ水分保持に効くか」の2サブ問い)。
2. **説明源の優先順位付け**: News/Trendの一次資料(報道・公式発表)とは
   異なり、Discoveryは「大学Extension Service(UC Davis/Iowa State等、
   Household記事の実際の出典)」「査読済み研究(No.18の実際の出典)」
   「公的機関の解説ページ」等、**説明・メカニズムを目的とした資料**を
   優先する設計候補とする。
3. **Ledger構造自体は既存のまま**: Hanshin/イランで使われている
   `topic_package_*.py`のVERIFIED FACTS/CONTESTED/GENERAL KNOWLEDGE/
   SPECULATION区分をそのまま流用可能と考える(構造変更は提案しない)。
   変更が必要と考えられるのは「何を集めるか」という上流の観点のみ。
4. **Fact Safetyとの整合**: 上記1・2はいずれもLedger構築**前**の工程
   であり、既存Fact Checker/Ledger Deviation Checkerのロジックには
   影響しない(構造上、既存QAをそのまま通す設計)。

**Gate 4観点での正直な注記**: 上記4項目はすべて**本Reportでの新規提案**
であり、既存SSOT・Trialに根拠を持つ実装は存在しない。既存er002 pipeline
で足りるかどうかの検証(Trial)も未実施。

---

## 3. Focus Module(Layer3、Discovery固有)

### 3.1 既存VALIDATED内容の引用

`DISCOVERY_FOCUS_MODULE_BLOCK`(Trial-05、`er011_open112_a_family_
4layer_prompt_trial_05.py`)は、単一Anchorへの1箇所機械的insert方式
(News/Trend Focus Moduleと同一のアーキテクチャ)。No.18 Article-only
Trialで観測された効果(`OPEN112_NO18_4LAYER_REVIEW_PACK_06.md`§5より):

- Main Story・Point One/Twoの役割分離が明確化(Point One=メカニズム/
  心理的説明寄り、Point Two=社会的文脈寄り、という分担がA2・B1双方で
  一貫して出現)。
- 2研究をまたいだ「2層」「2つの標的」という統合的フレーミングが出現。
  これはDiscovery/Whyとして意図通りの効果だが、**同時にFact Checkerが
  この統合的解釈を`REVIEW_REQUIRED`として指摘**(A2: unsupported_
  specific_claims 0→3件、B1: 3→5件、いずれもblockingなし)。

### 3.2 4-layer構想との関係・Trend/Newsとの差分

Layer1(Common Writing Contract)・Layer2(A Family Common Skeleton:
Main Story/Point One/Point Two/In One Line)はDiscovery/News/Trend
3タイプ共通。Layer3のみEditorial Type固有。Discoveryは「Point One=
メカニズム説明、Point Two=限界・社会的次元」という役割分担が実記事で
自然発生しており、これはNews(Major/Daily)のPoint候補
(mechanism/beyond-the-headline factor/myth-correction/certainty-
limitation、`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01`§3で
Hanshin/Health/**Household**から帰納)と**語彙的に重複する**。

**重要な整合結果**: 上記候補7件のうち「myth-correction」はHousehold
由来であり、Trial-01自身が「HouseholdはNews対象外の可能性が高いため
Major/Daily向け候補リストからは除外候補」と保留していた
(Trial-01§2.2/§3)。本タスクのA-UDR-9再確認(Household=Discovery候補)
と合わせると、**myth-correctionはMajor/Daily NewsではなくDiscovery/Why
のPoint Role候補として位置づけ直すのが整合的**、というのが本タスクでの
再照合結果である(これはTrial-01が既に示唆していた保留を確定させる
再照合であり、新規の飛躍した提案ではない)。

**Discovery固有Point Role候補(新規提案、本Reportで初めて統合)**:

| # | 候補役割 | 出典 |
|---|---|---|
| 1 | mechanism(なぜこの現象が起きるか、仕組みの説明) | Trial-05(No.18「2層の注意散漫」)、Household(ガス/水分の物理) |
| 2 | myth-correction(よくある誤解の訂正) | Household(「fruit-or-vegetable rule can mislead」)。Trial-01保留分の再照合(上記) |
| 3 | certainty/limitation(実験・一般化の限界) | Trial-05(「この実験・課題に当てはまるものであり、日常のすべてを説明しない」) |
| 4 | broader-dimension(社会的・実践的次元) | Trial-05(Point Two「返信への圧力」) |

### 3.3 実装イメージ(未配線、設計のみ)

- **`editorial_type_module_block`経路**(配線済みアーキテクチャ):
  `EDITORIAL_TYPE_MODULE_BLOCKS`辞書へ`{"discovery_why":
  DISCOVERY_FOCUS_MODULE_BLOCK}`を追加する形が、既存Trend Synthesis配線
  (`OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01`)と同一パターン
  になると考えられる(未実装)。
- **Point Role hint(Trial-03、未配線)**: `point_role_hint_block`引数
  (既定`""`でバイト不変、Trial-03で検証済みの安全な接続方式)へ、上記
  3.2の4候補を短文化したDiscovery版hintを渡す設計が、Major/Daily側の
  実装パターンとそのまま同型で流用できると考えられる(未検証、Discovery
  での runtime確認は本Reportでは実施していない)。

### 3.4 Fact Checker REVIEW_REQUIRED増加への対処案(未検証)

Deferred Classification report(§4(C))が既に提起した緩和Trial案
(「解釈強化リスクの緩和検証」)に加え、本タスクで新たに考えられる対処
候補:

1. **Prompt側の抑制**: Focus Module文言に「複数Evidenceを統合する際は、
   統合的な解釈自体もLedgerの範囲内で書けているか、断定の強さがEvidence
   を超えていないかを自己点検する」という一文を追加する案(Trend
   Synthesis側のcounter-signal必須化ルールと同じ設計思想)。
2. **REVIEW_REQUIRED増加の許容判断**: 増加は現状すべてnon-blocking
   (Fact矛盾0件)であるため、「解釈の深さ」と引き換えのコストとして
   許容するという判断もあり得る。
3. いずれも**未検証・未実装**。採否は§6でユーザー判断事項とする。

---

## 4. Ledger/Reference

Discoveryのevidenceは、Hanshin(誰が・何を・いつ)のような単純事実よりも
「説明・因果」に近い性質を持つ(No.18「なぜ通知を無視できないか」、
Household「なぜこの設計になっているか」)。既存Ledger Deviation Checker
の10種変化検知(`changed_fact`/`changed_scope`/`changed_causality`/
`changed_certainty`/`changed_number`/`changed_actor`/`changed_negation`/
`changed_comparison`/`changed_time`/`unsupported_new_claim`)のうち、
Discoveryで最も負荷がかかるのは`changed_causality`・`changed_certainty`・
`unsupported_new_claim`の3種と考えられる(Trial-05 B1のLocal Rewrite
事例[「Clear response windows could ease it」→書き換え]がこの3種の
境界線上で発生した)。

**既知Gap(Trend Synthesisと同一系統)**: 複数Evidenceをまたぐ統合的な
意味づけの強さそのものを判定する専用カテゴリは存在しない
(`OPEN-112-DISCOVERY-4LAYER-FINAL-ADOPTION-READINESS-AND-OPEN114-
REGISTER-07`で既に指摘済み)。Trendと違うのは、Discoveryではこの
Gapが**理論値ではなく実測**(A2 0→3、B1 3→5)として既に顕在化して
いる点である。

**対処方針(提案、未実装)**: 新規専用カテゴリを作るのではなく、既存の
`changed_causality`/`unsupported_new_claim`タグを流用し、
`REVIEW_REQUIRED`(non-blocking)として人間確認に委ねる現行運用を継続
する案が、Trend Synthesis側の扱い(既存タグで代替検知)と一貫性がある。
専用カテゴリの新設はコード変更を伴うため本タスクの範囲外(§6の
ユーザー判断事項)。

Reference供給: 3 Editorial Type共通で「承認済みLedgerの手動供給」が
正式initial path(自動供給は3タイプとも`USER_DECISION_REQUIRED`のまま)。
Discovery固有の自動供給機構は存在せず、本Reportでも新規提案していない
(§2のWhy-question分解は上流工程の提案であり、Ledger自動供給そのものの
提案ではない)。

---

## 5. Writer固有要求

**構造(問い→仕組み→限界)**: 実記事帰納(§1.1)により、Discovery/Why
記事は概ね以下の構造を取る。

1. **問い(Main Story冒頭)**: 「なぜXなのか」という不思議・違和感の
   提示(No.18「見なくても注意の一部を奪われる」、Household「小さな
   スライダーがこの単純な操作で新鮮さを左右する」)。
2. **仕組み(Main Story本体+Point One)**: 証拠(研究・専門機関資料)に
   基づくメカニズムの説明。
3. **限界(Point Two)**: 一般化の限界・社会的次元・誤解の訂正など、
   Main Story/Point Oneとは異なる角度の追加(§3.2候補2〜4)。
4. **In One Line**: 断定しない静かな圧縮(News/Trendと共通のトーン)。

**Point Role候補**: §3.2の4候補(mechanism/myth-correction/certainty-
limitation/broader-dimension)。既存Point Role Planning機構(動的選択、
News/Trend共通利用)にそのまま流用できる設計と考えられる(Trial-03の
接続パターンが技術的に転用可能、Discovery版hintの実際の効果は未検証)。

**Engagement原則の適用要否**: Engagement/Storytelling原則(時系列列挙
禁止)は、Trend Synthesis側でのみA/B検証済み(Trial-10/11、`PRODUCTION_
WIRED`はTrend側のみ)。Discovery記事でのA/B Trial実施記録は**見つから
なかった**(Deferred Classification§1で既確認)。No.18のTrial-05比較を
見る限り、Discovery記事は元々「時系列の出来事列挙」ではなく「研究結果の
提示→意味づけ」という構造のため、時系列列挙防止ルールの必要性自体が
Newsほど高くない可能性があるが、**これは推測であり検証していない**。
適用要否は既存の未解決UDR項目のまま。

---

## 6. 段階案(次の検証Trial設計、実行しない)

**前提**: Production実装は行わない。以下は次段階でユーザーが承認した
場合にのみ着手すべきTrial案。

### 6.1 Trial案A: Household Ledger再利用によるDiscovery Focus Module適用確認

- **対象**: 既存Household Ledger(`er003_output/n3_01/household/`系統、
  Article-only、A2+B1B各1本)。
- **目的**: (a) §1.2チェックリストがHouseholdを`DISCOVERY_WHY`と判定
  することの再確認、(b) `DISCOVERY_FOCUS_MODULE_BLOCK`(Trial-05既存
  スクリプト流用)を適用した場合の焦点構造変化・Fact Checker
  REVIEW_REQUIRED増減を、既存Household記事(Layer3無し)と比較。
- **費用概算**: Trial-03(Point Role接続、Hanshin A2+B1B text-only)実測
  ¥12.0、Trial-05(No.18 4-layer、A2+B1B)実測水準¥90.9級を参考に、
  **¥30〜100程度**(実測ではなく類推、Major/Daily側Trial-01の見積もり
  ¥30〜80と同水準と考える)。

### 6.2 Trial案B: Point Role hint(Discovery版)の効果検証

- Trial-03と同型のPoint Role hint機構へ§3.2の4候補を渡し、Fact Checker
  REVIEW_REQUIRED増加(§3.4課題)が緩和されるかを検証。Trial案Aと
  同時実施が効率的と考えられる(費用は6.1に含めて概算可能)。

### 6.3 Trial実施前に必要なユーザー判断(実施しない、列挙のみ)

1. §1.2の排他的判定チェックリスト(新規提案)を採用するか、それとも
   既存Major/Daily Gate・Trend Gateと同様「消去法的・非対称のまま許容」
   とするか。
2. Discovery 4-layer Focus Module Production採用可否(既存UDR、
   §3.4対処案含めて再検討するか、そのままDEFERRED維持か)。
3. Discovery固有Research方式(§2 why-question分解)をTrial対象とするか。
4. Point Role hint(Discovery版、§3.3/6.2)のTrial実施可否。
5. Engagement原則のDiscoveryへの適用検証要否(既存UDR)。
6. myth-correction候補のNews→Discovery移管(§3.2)を正式に確定するか。
7. Trial案A/Bの実施可否・時期。

---

## 7. Reconciliation Check(既存対策との重複・競合)・コスト影響評価

**重複・競合チェック**: Focus Moduleのアーキテクチャ(単一Anchor機械的
insert)はNews/Trend/Discoveryで完全に同一パターンであり、競合なし。
Point Role hint機構(Trial-03)は既定値`""`でバイト不変が保証された汎用
接続であり、Discovery版hintを追加してもTrend/News側の挙動には影響しない
(Trial-03の単体テストで既に確認済みの設計)。Engagement Blockは現状
Trend専用であり、Discoveryへの流用はまだ提案・検証していない(競合の
可能性は無いが、効果も未検証)。Ledger Deviation Checkerの専用カテゴリ
欠如は、Trend・Discovery共通の未解決Gapであり、本タスクで新たな競合や
二重対応は発生していない。

**LLM呼び出し・コスト影響**:

| 要素 | 追加LLM呼び出し | 根拠 |
|---|---|---|
| Focus Module(Layer3)注入 | 0回(既存Writer呼び出しへの文字列insert) | Trial-05「1箇所のみの機械的insert」 |
| Point Role hint | 0回(既存Point Role Planning呼び出しへのplaceholder追加) | Trial-03実測(既存呼び出し内で完結) |
| §2 Why-question分解(新規提案) | +1回/記事以上(サブ問い生成の新規LLM呼び出しが必要と考えられる) | 本Report新規提案、実測なし |

1記事あたりの概算コスト(text-only、Focus Module+Point Role hint適用):
Trial-03実測(¥12.0、Hanshin A2+B1B)とTrial-05実測水準(¥90.9級、No.18
A2+B1)の間で、**¥30〜100程度**と見積もる(実測ではなく類推)。
§2 Why-question分解を追加する場合の追加コストは**不明**(Trial未実施、
既存の小規模計画系呼び出しの実測値から類推すると数円〜20円程度の増分と
推測されるが、これは概算であり実測ではない)。

---

## 8. Gate 4観点: Trial-only仕様への依存箇所の明示

以下はいずれも既存Production/Prompt/SSOTに未採用の内容であり、本Report
の設計案がこれらに依存している箇所を明示する。

- **`DISCOVERY_FOCUS_MODULE_BLOCK`**(Trial-05、Article-onlyのTrial止まり、
  Production未配線、採否`DEFERRED`)。§3全体がこれに依存。
- **Point Role hint機構**(Trial-03、`VALIDATED`止まり、Major/Daily相当
  でのみruntime検証済み、Discoveryでの効果は未検証)。§3.3/§6.2が
  これに依存。
- **§1.2排他的判定チェックリスト**: 本Reportの完全新規提案。既存Gate
  (News/Trend Gate)を参考にしたが、Q3(時事性依存判定)は既存SSOTに
  根拠を持たない新規質問であり、既存Decisionからの承認は一切ない。
- **§2 Research方式(why-question分解)**: 完全新規提案。既存Production
  ・Trialいずれにも実装・検証記録なし。
- **§3.2 Discovery固有Point Role候補4件・§5 Writer構造(問い→仕組み→
  限界)**: 個々の要素(mechanism/myth-correction/certainty-limitation/
  broader-dimension)はTrial-05・Trial-01の実記事帰納に根拠を持つが、
  これらを統合的なDiscovery専用リストとして体系化したのは本Reportが
  初めてであり、ユーザー承認された正式リストではない。

**結論**: 本Reportの提案はすべて設計段階であり、Production採用の判断は
一切下していない。§6.3の7項目はいずれも実行前にユーザー判断が必要。

---

## 「不明」とした項目

- No.18のB1完成音声が、旧OPEN-107 STOP以降の全体的なKey Phrase/TTS改善
  (OPEN-116/119/121/122/123等)適用後に最終的にどう解決したか(Gap Audit
  で既に「不明」とされており、本タスクでも再確認していない)。
- No.18・Householdの既存Verified Fact Ledgerが、既存自動Research
  pipeline(`er002_ja_web_research_r3.py`)経由で作られたか、人手WebSearch
  で作られたかは、いずれの既存報告にも明記されておらず不明。
- §3.3のPoint Role hint(Discovery版)・§2のWhy-question分解を実際に
  Trialした場合の効果(REVIEW_REQUIRED増加緩和・記事品質への影響)は、
  Trial未実施のため不明。
- §7の追加LLM呼び出しコスト概算(why-question分解、数円〜20円程度)は
  類推であり実測ではない。
- Engagement原則のDiscovery記事への適用効果(Deferred Classification
  同様、実施記録なし)。
- §1.2チェックリストのQ1(Health vs No.18の境界判定)が、本Report記載の
  5記事以外(POOL_TOPIC_MASTER.md No.1〜20の残り18件、Hanshin/Health/
  Household以外のNews候補)に対しても再現性を持つかは、当てはめ未実施の
  ため不明。
