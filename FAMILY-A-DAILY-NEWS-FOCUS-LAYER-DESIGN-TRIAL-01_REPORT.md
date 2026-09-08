# FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01 報告書

管理ID: FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01(Lane A-2)。
**設計Trial。読み取り+設計Reportのみ。Production配線・コード/Prompt/SSOT編集・
Git操作は一切行っていない。API呼び出しは0件(費用¥0)。**
Lane A-1(CURRENT_SPEC編集中)・Lane B(`er012_*`)の成果物は参照していない。
`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は編集していない。CURRENT_SPEC.md
は該当行のみGrepで確認し(Trend Gate/mode関連の3行のみ)、本文の正は
DECISION_LOG.md該当行・既存ER-*_REPORTに置いている。

対象: 通常News固有の (1) Layer 3 News Focus Module(Major/Daily variant)、
(2) Major/Daily News mode判定基準、の設計。

参照元: `OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`(以下DESIGN-08)、
`FAMILY-A-DAILY-NEWS-SPEC-DRAFT-01_REPORT.md`(以下DRAFT-01)、
`FAMILY-A-LEGACY-NEWS-ASSET-SURVEY-01_REPORT.md`(以下SURVEY-01)、
`OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01_REPORT.md`(以下WIRING-01)、
`OPEN_ITEMS.md`該当行(Trend Gate記録関連、380行)、CURRENT_SPEC.md該当行
(378-381行、Trend Synthesis節)。加えて、DESIGN-08 §11がMajor/Daily候補・
Trend Synthesis候補として名指しした実記事本体
(`er003_output/n3_01/hanshin/b1b/article.md`・`health/b1b/article.md`・
`household/b1b/article.md`)を実際に読み、焦点構造を帰納した(DESIGN-08は
これらをtopic_package段階でread-only確認しただけで、完成記事本体は読んで
いなかった。本Trialが完成記事の実文面から焦点構造を帰納した初めての作業)。

---

## 0. 前提の再確認(DESIGN-08/DRAFT-01からの引き継ぎ)

- A Family Common Skeleton(Layer 2) = Main Story / Point One / Point Two /
  In One Line。この物理構造はNews固有設計でも変更しない(DESIGN-08 §12で
  既に整合確認済み、本Trialも追認)。
- Layer 3 News Focus Moduleは「1つのModule」ではなく、Major/Daily variantと
  Trend Synthesis variantの相互排他な2 variantとして設計する(DESIGN-08 §1)。
  Trend Synthesis variantは既に`APPROVED_FOR_PRODUCTION`(2026-09-08)で
  `TREND_SYNTHESIS_FOCUS_MODULE_BLOCK`+`TREND_SYNTHESIS_ENGAGEMENT_BLOCK`
  として`editorial_type_module_block`引数経由でPRODUCTION_WIRED済み
  (WIRING-01)。本Trialが設計するMajor/Daily variantは、この既存配線と
  **同じ注入経路**(`resolve_editorial_type_module_block(editorial_mode)`
  →`EDITORIAL_TYPE_MODULE_BLOCKS`辞書への追加)を前提とする。
- `editorial_type`はProduction Writerコードにこれまで未実装だったが、
  WIRING-01でTrend Synthesis側のみ実装済み。Major/Daily側は**未実装**
  (本Trialはコード変更を行わない設計のみ)。

---

## 1. Layer 3 News Focus Module(Major/Daily variant)設計

### 1.1 実記事からの焦点構造の帰納

DESIGN-08 §11はHanshin(阪神)をMajor/Daily候補、イラン情勢をTrend Synthesis
候補として"topic_package"段階でread-only確認していたが、実際に完成した
Hanshin/Health/Household(N3-01、Layer3不在時代の生成物、SURVEY-01)の記事
本文を読むと、Layer3が無くても以下の暗黙の焦点構造が既に自然発生していた
ことが分かる。

| 記事 | Main Story | Point One | Point Two | In One Line |
|---|---|---|---|---|
| Hanshin(単発試合結果) | 試合経過を時系列で物語的に提示(誰が・いつ・何をしたか) | 「Sato's Home Run Changed the Shape of the Game」= 序盤の1事象が結果を決定づけた**メカニズム** | 「The Late Runs Showed Hanshin's Full Strength」= 見出しの主役以外の**貢献の広がり**(1人のヒーローに矮小化しない) | 2つのPointを1文の因果イメージへ圧縮 |
| Health(単一研究発表) | 研究内容・数値結果を提示 | 「The power may be in the combination」= この研究の**切り口の新しさ**(単一習慣でなく組合せ) | 「These are clues, not personal instructions」= observational study・**確実性の限界**を明示的に断る | "a promising pattern, not a guarantee"と断定回避 |
| Household(evergreen解説、News性なし) | メカニズムの解説(エチレン/水分) | 「The fruit-or-vegetable rule can mislead」= 一般に信じられている**誤解の訂正** | 「Not every fresh food belongs in the drawer」= 追加の**例外・限界** | 単一原則への圧縮 |

**帰納された共通パターン**:
1. Point Oneは「なぜこの結果になったか(mechanism)」または「この切り口の
   新しさ・誤解の訂正」という、Main Storyで提示された事実に**説明の層**を
   足す役割を担う傾向が強い。DESIGN-08 §2の候補「なぜ重要か/背景」と
   整合するが、実記事はより具体的に「結果を決定づけたメカニズム」
   「よくある誤解の訂正」という形を取っていた。
2. Point Twoは「見出しの裏にある広がり(headline以外の貢献要因)」または
   「確実性の限界・未確定点」という役割を担う傾向が強い。DESIGN-08 §2の
   候補「未確定な点」と整合するが、Hanshinの「見出し以外の貢献の広がり」
   はDESIGN-08 §2の既存候補リストに**明示的には無かった**新しいパターン。
3. In One Lineは常に「断定しない・静かな圧縮」というDESIGN-08の想定通り
   のトーンだった(§2で既に一致確認済み、再確認のみ)。

### 1.2 Trend Synthesis Focus Moduleとの差分表

WIRING-01 §1.1(`TREND_SYNTHESIS_FOCUS_MODULE_BLOCK`/
`TREND_SYNTHESIS_ENGAGEMENT_BLOCK`が`EDITORIAL_TYPE_MODULE_BLOCKS`へ
登録済み)、DESIGN-08 §3/§5/§6/§7を根拠に整理する。

| 観点 | Major/Daily News Focus Module(本Trial設計、未実装) | Trend Synthesis Focus Module(PRODUCTION_WIRED、WIRING-01) |
|---|---|---|
| 中心Question | "What happened, why does it matter, and what should we watch next?"(DESIGN-08 §2) | "What is changing, and what do several independent signals together suggest?"(DESIGN-08 §3) |
| 前提とする事実構造 | 単一起点イベント(1つの日付・1つの決定・1つの結果・1つの研究発表) | 独立した複数Signalの集約(§5 Trend成立条件) |
| Point One候補(帰納後) | why-it-matters/background(DESIGN-08原型)+**mechanism(結果を決定づけた要因)**+**myth-correction(誤解の訂正)**(§1.1で新規追加、実記事から帰納) | major driver/strongest signal/what changed from before/underlying mechanism(DESIGN-08 §3) |
| Point Two候補(帰納後) | 次に見るべきこと/未確定な点/反応/実生活への影響(DESIGN-08原型)+**beyond-the-headline factor(見出し以外の貢献の広がり)**(§1.1で新規追加) | counter-signal/limitation/who is affected/what would confirm-reverse/next inflection point/practical meaning(DESIGN-08 §3)。**Point Twoの既定候補としてcounter-signal/limitationを優先**する専用ルールあり |
| 必須具体化ルール(Layer3固有、Layer1の一般原則の具体化) | (本Trial新規提案、§1.3参照)不確実・投影的な要素は明示的にunconfirmedと書く、省略しない | counter-signal/limitationが存在しない場合は「反証Signal・限界が見当たらない」ことを明示する(既にPRODUCTION_WIRED、DESIGN-08 §3) |
| Evidence Strength分類タグ | 対象外(単一Ledgerの通常Fact Safetyで足りる、新規タグ設計は不要と判断) | `official_statistics`等の分類タグ語彙が候補として存在(DESIGN-08 §6、**未実装**) |
| Engagement/Storytelling専用Block | 本Trialでは提案しない(Layer1のStorytelling First原則が既にCommon Writing Contractとして全Editorial Typeに適用済みであり、SURVEY-01 §7確認の通りNews記事もこの一般原則の対象。News固有の追加Engagement Blockが必要かどうかは**不明**、Trial実施後に判断すべき論点として§6で提起) | `TREND_SYNTHESIS_ENGAGEMENT_BLOCK`(Trial-10施策1)が別Blockとして存在、PRODUCTION_WIRED。施策2(Reference Digest)は含めない(WIRING-01) |
| Mode判定側の対応する質問 | 単一起点質問(DESIGN-08 §4 Q1) | 集約質問(DESIGN-08 §4 Q2) |
| 成立条件チェックリスト | 本Trialで新規提案(§2、Trend Gate 6条件と対称形、**未検証**) | Trend成立条件6項目(DESIGN-08 §5、WIRING-01で「Trend Gate 6条件」として手動判定・記録機構がPRODUCTION_WIRED) |
| Diagnostic Full Retry語彙Gap | News固有失敗パターン(evidence listing・daily newsの背景過多・Point role collapse)への専用語彙が存在しない(DESIGN-08 §10、Gap継続) | trend overclaim・weak counter-signal等への専用語彙が存在しない(同じGap、WIRING-01 §3で変更せずと明記) |
| 実装状態 | **未設計→本Trialで初めて設計案化。コード実装0%** | `PRODUCTION_WIRED`(2026-09-08、Gate 3受入済み) |

### 1.3 Prompt文言案(ドラフト、未採用、コード未反映)

**注記: 以下は既存Production Prompt文言(WIRING-01が報告した
`【Spoken-first原則(数字の扱い)】`のような日本語角括弧見出し+英語規則文の
書式)に語彙・書式を合わせた**新規ドラフト**である。Trend Synthesis
variantの実際のPrompt全文はLane A-1が現在編集対象としている
`er003_v1_n3_01_articles_generate.py`内にあり、本Trialでは同ファイルを
直接参照していない(Lane A-1成果物不参照の指示に従う)。したがって
Trend側との**字句単位**の一致は保証できない。書式・語彙の近似はWIRING-01
報告文中に引用された断片(`Trend Synthesis Focus`という文字列がprompt.txt
に実在すること、Rule 1〜3の内容、counter-signal/limitation必須化ルール)
から推定したものであり、**厳密な一致は不明**。**創作は最小限**とし、
各行の根拠Decisionを併記する。**このProduction Prompt文言案自体は
`APPROVED_FOR_PRODUCTION`ではない。**

```
【Major/Daily News Focus】
This article covers a single, dateable news event or announcement —
not an aggregated trend across independent occurrences. Do not present
this story as if it were a pattern seen across multiple separate events
over time. [根拠: DESIGN-08 §4 Q1(単一起点質問)、§7の「Layer3は
News/Trend固有の具体化のみを持つ」方針]

Point One and Point Two must each add a distinct layer of meaning to
what Main Story already established (for example: the mechanism that
decided the outcome, why this matters, who is affected, an additional
contributing factor beyond the headline fact, or what remains
unconfirmed). Do not let either Point simply restate a fact already
given in Main Story, and do not force a role the Ledger does not
actually support — choose the role Point Role Planning is designed to
choose. [根拠: DESIGN-08 §2(Point役割固定化せずPoint Role Planningへ
委ねる方針)、§1.1本帰納結果(mechanism/beyond-the-headline factor)]

If any part of this event is a projection, an ongoing situation, a
single study's finding, or otherwise not yet fully settled, state
plainly what is confirmed and what is not — do not smooth an
unconfirmed detail into settled fact. [根拠: DESIGN-08 §7(Layer1一般
原則のNews固有具体化という位置づけ、Trend側のcounter-signal必須化
ルールと対になる構造)、§1.1 Health記事の実例("observational study,
not an experiment")]
```

**位置づけの整理**: 上記3段落のうち、第1段落(単一起点前提)と第3段落
(不確実性明示)は、DESIGN-08 §7が示した「Layer1の一般原則(Evidence-
bounded Interpretation)をNews/Trend向けに具体化する」という設計方針の
Major/Daily側版であり、Trend側のcounter-signal/limitation必須化ルールと
構造的に対になる。第2段落はDESIGN-08 §2の「Point Role Planningへ委ねる」
方針をPrompt文言化したもので、Trend側の「Point One/Twoは個々のSignalの
紹介ではなく意味づけの違いで分ける」指示(DESIGN-08 §10)と対になる。

### 1.4 注入経路とmode名候補

既存`editorial_type_module_block`引数(WIRING-01でLane A-1配線済み、
`resolve_editorial_type_module_block(editorial_mode: str | None)`)を
前提とする。本Trialはコード変更を行っていないため、以下は**候補提案の
みで未実装**。

- mode名候補: `editorial_mode="major_daily_news"`。
  理由: WIRING-01の既存mode名`"trend_synthesis"`と対称的な命名規則
  (Focus Module variant名をそのままsnake_caseにする慣例)に合わせた。
  `"daily_news"`という短縮候補も考えられるが、DESIGN-08がMajor/Dailyを
  一貫して1つの区分(重要度に関わらず単一起点イベントは同じ扱い、
  DESIGN-08 §4境界確認表: 「阪神が優勝した」も`MAJOR_DAILY`)として
  扱っている以上、`"daily_news"`という省略名は「重要ニュースはMajor
  扱いで別モードがあるのでは」という誤解を招く可能性があるため、
  `"major_daily_news"`のほうが設計意図に忠実と判断する(**採用は
  ユーザー判断**)。
- `EDITORIAL_TYPE_MODULE_BLOCKS`辞書への追加候補:
  `{"major_daily_news": MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK}`
  (Trend側と異なりEngagement Blockは本Trialでは提案しない、§1.2参照)。
- 未知mode文字列への`ValueError`(fail-closed)という既存設計
  (WIRING-01 §1.1)は変更を要しない(新規mode追加時に自然に機能する)。

---

## 2. Major / Daily News mode判定基準(Trend Gate 6条件と対称形)

DESIGN-08 §4の2質問(単一起点質問/集約質問)は既に存在するが、Trend側の
「成立条件6項目」(DESIGN-08 §5、WIRING-01で「Trend Gate 6条件」として
手動判定・記録機構がPRODUCTION_WIRED)に対称する**Major/Daily側の
成立条件チェックリストはDESIGN-08に存在しなかった**。本Trialで新規に
以下を提案する(**未検証、Trial実施前の設計案**)。

### 2.1 Major/Daily Gate候補(6項目、Trend Gate 6条件と対称形)

1. **単一起点確認**: この記事のMain Storyを「[日付]に、Xが起きた」の
   1文で書いても要点が失われないか(=DESIGN-08 §4 Q1のYes)。
2. **重要度非依存確認**: 「重要度が高い」こと自体はMAJOR_DAILYから
   TREND_SYNTHESISへ判定を変えない(DESIGN-08 §4「阪神が優勝した」例の
   一般化)。
3. **Ledger充足確認**: 単一のVerified Fact Ledgerだけで、Main Story +
   Point One/Two 2つの異なる意味づけ(§1.1帰納候補から選択)を支える
   だけの確認済み情報があるか。
4. **不確実性明示確認**: 投影的・未確定な要素(進行中の状況、単一研究の
   知見等)が、断定ではなく明示的にunconfirmedとして書かれているか
   (§1.3第3段落と連動)。
5. **重複確認**: 同一の起点イベントについて、既に別のMajor/Daily記事が
   直近で存在しないか(Trend側「直近の既存Trend記事と中心主張が実質同じ
   でない」の対称。Trend Memory[DESIGN-08 §8]と同じ将来機構が必要になる
   可能性があるが、本Trialでは実装しない)。
6. **偽装Trend排除確認**: この記事を「Major/Daily」として書くために、
   実際には複数の独立した時点・出来事を横断的に参照する必要がある場合、
   それは実質的にTREND_SYNTHESISであり、MAJOR_DAILYと誤判定していないか
   (=DESIGN-08 §4 Q2の裏返し)。

**Trend Gate 6条件との対称性の限界(正直な注記)**: Trend側6条件
(DESIGN-08 §5)は「Trendが本当に成立しているか」という**積極的成立
証明**の性質を持つのに対し、上記6項目は「MAJOR_DAILYであり続けるための
**消去法的確認**(TREND側の条件に当てはまらないことの確認)」という
性質が強く、完全な対称構造ではない。これは意図的な設計判断ではなく、
本Trial着手時点でDESIGN-08側にMajor/Daily専用の積極的定義が存在しな
かったこと(DESIGN-08 §2は役割設計のみで「成立条件」は書いていない)に
起因する。この非対称性自体をユーザー判断事項として§6で提起する。

### 2.2 境界事例の当てはめ

DESIGN-08 §4境界確認表に加え、実記事で当てはめる。

| 対象 | Major/Daily Gate 6項目 | 判定 | 備考 |
|---|---|---|---|
| Hanshin(実記事、阪神-広島戦8-1) | 1〜6すべて充足(単一試合・単一起点、Ledgerで2つの異なる意味づけ[mechanism/beyond-headline]を確認済み、不確実要素なし、重複なし、複数時点参照なし) | `MAJOR_DAILY` | DESIGN-08 §11の候補指定と整合。実記事で初めて全項目を確認した |
| Health(実記事、UK Biobank単一研究発表) | 1〜4充足(単一研究発表という単一起点、不確実性は明示済み"observational, not experiment")。**5〜6が新規論点** | `MAJOR_DAILY`(ただし要検討) | 研究内容自体は"59,078人を8.1年追跡"という**内部的な集団データの集約**を含むが、これはTrend Synthesisが要求する「複数の**独立した外部Signal**の集約」とは異なる(1つの研究プロジェクト=1つの起点)。**この区別自体を本Trialで初めて明示化した**(DESIGN-08にはこの論点の記述なし)。境界がやや曖昧なため、大規模メタ分析(複数の独立研究を横断的に統合する記事)であればTREND_SYNTHESIS側に倒れる可能性がある、という限界を注記する |
| Household(実記事、冷蔵庫クリスパー) | 1(単一起点イベントが存在しない、evergreen解説でありそもそも「日付に起きた」ことがない)で**そもそも質問が成立しない** | **判定不能(Gap)** | 新たに発見した論点。Household記事はA Family Common Skeleton(Layer1+2)を使ってはいるが、そもそも「News」(Major/Daily・Trend Synthesisいずれの意味でも)ではないevergreen解説記事であり、DESIGN-08のNews 2モード分類の**対象外**である可能性が高い。SURVEY-01がHanshin/Health/Householdを一括して「N3-01系統」と分類していたため見過ごされていたが、実記事を読んで初めて判明した(§6で論点として提起) |
| (DESIGN-08 §4既掲載)阪神が優勝した | 2により重要度は判定を変えない、1により単一起点イベント | `MAJOR_DAILY` | DESIGN-08既掲載の再確認のみ |
| (DESIGN-08 §4既掲載)阪神の直近10試合で接戦勝ちが増加 | 6により複数時点参照が必須なため偽装Trend排除確認に抵触 | `TREND_SYNTHESIS` | DESIGN-08既掲載の再確認のみ |

**新規発見(重要)**: Household記事は、A Family Common Skeletonの上で
書かれてはいるが、News Focus Module(Major/Daily・Trend Synthesisいずれ)
の対象そのものではない可能性が高い。DRAFT-01・SURVEY-01は3記事
(Hanshin/Health/Household)をまとめて「通常News正式化のreference候補」
として扱っていたが、本Trialが初めて記事本文を精読した結果、Householdは
「News」という枠自体に当てはまらない evergreen explainer型のコンテンツ
であることが分かった。これは新しい仕様提案ではなく**発見した事実**として
報告し、§6でユーザー判断事項に加える。

---

## 3. Point Role候補リスト(News向け、DRAFT-01が未設計とした項目)

DESIGN-08 §2/§10、および§1.1の実記事帰納結果を統合した最終候補リスト
(Major/Dailyのみ、Trend Synthesisは§1.2参照)。

| # | 候補役割 | 出典 | Point One/Two適性 |
|---|---|---|---|
| 1 | why-it-matters / 背景 | DESIGN-08 §2原案 | 両方 |
| 2 | 誰に影響するか | DESIGN-08 §2原案 | 両方 |
| 3 | 次に見るべきこと/未確定な点 | DESIGN-08 §2原案 | 主にPoint Two |
| 4 | mechanism(結果を決定づけた要因) | 本Trial新規(§1.1 Hanshin帰納) | 主にPoint One |
| 5 | beyond-the-headline factor(見出し以外の貢献の広がり) | 本Trial新規(§1.1 Hanshin帰納) | 主にPoint Two |
| 6 | certainty/limitation caveat(確実性の限界) | 本Trial新規(§1.1 Health帰納、DESIGN-08 §7の一般原則の具体化) | 主にPoint Two |
| 7 | myth-correction(よくある誤解の訂正) | 本Trial新規(§1.1 Household帰納) | 主にPoint One。**§2.2の通りHouseholdはNews対象外の可能性が高く、この候補がMajor/Daily Newsに適用可能かは不明** |

既存Point Role Planning機構(Layer 1、DECISION_LOG.md記載の既存Production
機構、Discovery/Whyでも共通利用、DESIGN-08 §2で流用推奨済み)との整合:
候補7を除き1〜6はDESIGN-08の設計方針(固定役割にせず動的選択)とそのまま
整合する。候補7はHousehold由来のため、§2.2の発見(Householdは恐らくNews
対象外)を踏まえると、Major/Daily News向け候補リストからは**除外候補**
として保留するのが安全側の判断だと考えるが、最終判断は§6でユーザーに
委ねる。

---

## 4. 検証設計(実行しない、Trial案のみ)

### 4.1 Trial案

- **対象**: 既存の承認済みLedger`er003_output/n3_01/hanshin/research/
  verified_fact_ledger.txt`(Hanshin、Major/Daily候補として§2.2で
  確認済み)を再利用。同一Ledgerに対し、(a) 現行COMMON_BLOCK_TEMPLATE
  のみ(Layer3無し、既存Hanshin記事と同条件)と、(b) 本Trial設計の
  `editorial_type_module_block`(Major/Daily variant、§1.3ドラフト)を
  注入、の2条件で**同一Ledgerから再生成**し、焦点構造の変化を直接比較
  する設計とする。入力を固定することで、差分をFocus Module単体の効果に
  帰属させやすくする(WIRING-01のTheme 2 runと同じ「既定値不変+新規
  variant」比較設計を踏襲)。
- **本数**: A2 1本 + B1B 1本(Hanshin、Layer3あり版のみ新規生成。
  Layer3無し版は既存Hanshin記事をそのまま比較対象として流用、追加生成
  しない)。
- **成功基準**: (a) 既存QA全PASS(Fact Checker/Ledger Deviation
  Checker/Point Overlap QA、既存Loop Budget内)、(b) 既存Hanshin記事
  (Layer3無し)との焦点構造比較で、§1.1の意図した役割分化(mechanism/
  beyond-the-headline factor)が実際に生成テキストへ現れるか目視確認。
- **費用概算**: WIRING-01実績(Theme 2、Trend Synthesis、A2+B1B
  text-onlyでDiagnostic Full Retry込み約¥37.11、Key Phrase選定含め
  約¥81.39[¥37.11+¥44.28])を参考基準とする。Major/Daily側はTrend
  Synthesisより複雑な集約構造を要求しないため、同程度かやや低い
  **¥30〜¥80程度**(text-onlyでの1回試行、Diagnostic Full Retryが
  複数回発火した場合は上振れ、Key Phrase選定を含めるかは別途判断)と
  見積もるが、**これは類推による概算であり実測ではない**。

### 4.2 実行しないことの確認

本Trialでは上記4.1を一切実行していない(API呼び出し0件、コード変更0件)。

---

## 5. Gate 4観点の自己点検

**確認項目**: 本設計案がTrial-only仕様・未承認仕様に依存していないか。

- §1.2/§1.3で参照したTrend Synthesis側の内容は、いずれも
  `PRODUCTION_WIRED`(WIRING-01、2026-09-08)のものに限定し、DEFERRED
  扱いのReference Digest(施策2)・Mode判定自動化・News Ledger自動供給・
  Retry語彙拡張の4件(WIRING-01 §11.1所見、OPEN_ITEMS.md 381行「据え置き
  4件」)はいずれも本設計案へ組み込んでいない。
- ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02/WRITER-ARCH-01(参考資料
  指定、Trial-only、DRAFT-01 §3で既にobsolete除外済み)は引用していない。
- Discovery Layer3(Trial-05)は据え置き・参照のみの指示通り、本設計案の
  Point Role候補・Focus Module文言のいずれにも取り込んでいない(News固有
  帰納は全てHanshin/Health/Household実記事から行った、Discovery側の文言
  を流用していない)。
- Lane A-1(CURRENT_SPEC編集中)・Lane B(`er012_*`)の成果物は本タスクで
  参照していない(`er003_v1_n3_01_articles_generate.py`本体も直接読んで
  いない、§1.3で明記)。
- §1.3のPrompt文言案・§2.1のGate候補・§3の候補7はいずれも本Trial新規
  提案であり、Production採用済みの内容として書いていない(全て「未実装」
  「未検証」「ドラフト」と明記した)。

**結果: PASS(Trial-only仕様・未承認仕様の混入なし)。**

---

## 6. Gate 1分類・USER_DECISION_REQUIRED

**Gate 1分類: VALIDATED(設計としての内部整合性・既存Decisionとの整合は
確認できた。ただしTrial実施・記事生成は0件のためコード/Prompt採用の
判断材料としては不十分、Production採用は別途Gate 3配線+Trial実施が必要)。**

**採用判断はUSER_DECISION_REQUIRED。決定事項候補は以下の通り**:

1. **Major/Daily variant設計案(§1)の採用可否**: §1.3のPrompt文言案・
   mode名候補(`"major_daily_news"`)を次段階(Trial実施→Gate 3配線)へ
   進めてよいか。
2. **Household記事のNews分類対象外という発見(§2.2)への対応**: Household
   はMajor/Daily・Trend Synthesisいずれの対象でもないevergreen explainer
   である可能性が高いと判明した。これを踏まえ、DRAFT-01が前提としていた
   「Hanshin/Health/Householdを一括してNews reference」という枠組みを
   修正するか(Householdを別Editorial Type候補として切り離すか)。
3. **Health記事の境界(単一研究発表 vs 大規模メタ分析)の扱い(§2.2)**:
   単一研究の内部的な集団データ集約とTrend Synthesisの外部Signal集約を
   区別する原則を明文化するか、それとも将来Trial時の個別判断に委ねるか。
4. **§2 Major/Daily Gate 6項目(消去法的性質)の扱い**: Trend Gate6条件
   (積極的成立証明)と非対称であることを許容するか、それとも
   Major/Daily側にも積極的定義への書き換えを要求するか。
5. **§3候補7(myth-correction)の採否**: Household由来のためNews対象外の
   可能性が高いことを踏まえ、Major/Daily News向けPoint Role候補リストに
   残すか除外するか。
6. **§4 Trial実施の可否・時期**: Hanshin Ledger再利用によるA2/B1各1本の
   比較Trial(概算¥30〜80)を実施してよいか、Trend Synthesis側の残件
   (据え置き4件)を先に片付けるべきか。

以上、いずれも実行せず提案・列挙のみ。本Trialでの追加API呼び出し・
コード変更・SSOT編集・Git操作は行っていない。
