# OPEN-112-NEWS-MODE-DESIGN-08 報告書

対象: News系(A Family)を Major/Daily News と Trend Synthesis の2モードに整理し、
Discovery/Whyと同じ4層構造(Layer 1〜4)で成立するかを設計する。

**今回はコード変更・Prompt正式文言の確定・Trial実行・記事生成のいずれも行っていません。
設計整理のみです。**

前提として、[ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md](ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md)・
[OPEN112_NO18_4LAYER_REVIEW_PACK_06.md](OPEN112_NO18_4LAYER_REVIEW_PACK_06.md)・
`er011_open112_a_family_4layer_prompt_trial_05.py`(Discovery/Why Layer 3の先行実装)を参照している。

---

## 0. 前提の再確認

- A Family = Discovery/Why(Layer 3実装済み・Trial検証済み・Production未採用) + News系(今回設計)。
- A Family Common Skeleton(Layer 2) = Main Story / Point One / Point Two / In One Line。Hookは独立slot化しない(Main Story冒頭が兼務)。
- News系は Major/Daily News と Trend Synthesis の2モードに集約する。完全Personalizationは保留中。
- `editorial_type` はProduction Writerコードに未実装(前回OPEN-112-07で再確認済み)。今回もこの前提は変更しない。

---

## 1. News Mode 全体設計図

Discovery/Whyと同じ4層構造をそのまま踏襲する。

```
Layer 1: Common Writing Contract       … Discovery/Whyと完全共有。News専用の変更なし。
Layer 2: A Family Common Skeleton      … Discovery/Whyと完全共有。物理構造・見出し数の変更なし。
Layer 3: News Focus Module             … 新規。ただし「1つのModule」ではなく、
                                          相互排他な2つのModule variantとして設計する。
    - News Focus Module (Major/Daily variant)
    - News Focus Module (Trend Synthesis variant)
Layer 4: Article-specific Inputs       … News用に入力項目を拡張(§16参照)。
```

**設計判断**: Major/DailyとTrend Synthesisを1つのModuleに無理にまとめない。
Discovery Moduleの`DISCOVERY_FOCUS_MODULE_BLOCK`と同じ「Anchor 1箇所への単一Module挿入」方式を使い、
Mode判定の結果に応じてどちらか一方のModule変数を選んで同じAnchorに挿入する設計とする。
これによりSTOP条件20「News両モードを1 Moduleにまとめると責務が複雑すぎる」は
そもそも発生しない(1つに無理にまとめる設計を採らないため)。

上流フロー(§3の再掲・確定版):

```
ニュース候補収集(分野ごと20〜30件/日)
  → 候補整理(Evidence strengthタグ付け・Ledger化)
  → Mode判定(MAJOR_DAILY / TREND_SYNTHESIS) ※記事化するかどうかの自由裁量Gateではない
  → 対応するNews Focus Module variantを選択
  → 4層Writer(Layer1+2+3[選択済みvariant]+4)
  → 既存QA(Point Overlap/Value QA・Ledger Deviation Checker・Fact Checker)
  → 最終記事
```

Mode判定は「記事化候補として扱う」ことを前提にした分類であり、「記事化しない」判断をAIに与えない
(§19禁止事項・タスク前提と整合)。

---

## 2. Major / Daily News の Slot 役割設計

中心Question: *"What happened, why does it matter, and what should we watch next?"*

| Slot | 役割 | 設計メモ |
|---|---|---|
| Main Story | 何が起きたか/いつ・誰が・どこで/何が確定しているか/なぜ今日ニュースなのか | Storytelling First維持。Discovery版と同じく「事実の列挙」ではなく物語的提示 |
| Point One | 候補: なぜ重要か / 背景 / 直前までの経緯 / 誰に影響するか | 固定役割にしない(下記参照) |
| Point Two | 候補: 次に見るべきこと / 未確定な点 / 反応 / 実生活への影響 / 今後の分岐点 | 固定役割にしない(下記参照) |
| In One Line | 今日のニュースの一言理解。未確定部分を断定しない | Discovery版のIn One Lineと同じ「静かな要約」トーン踏襲 |

**Point One/Two役割の固定化について**: タスク文で「固定役割にするか、候補ロールからLedgerに応じて選ぶか」を
検討課題として挙げられていた点について、既存の **Point Role Planning**(Layer 1に属する既存Production機構、
Discovery/Whyでも共通利用)をそのまま流用し、記事ごとにLedger内容に応じて候補リストから実際の役割を選ばせる方式を
推奨する。理由: 固定役割にすると、Ledgerの実際の中心的事実と役割が噛み合わない記事(例: 「誰に影響するか」が
自明すぎて書くことがない日)が出た際に、Point Two/Value QAが機械的に「価値が薄い」と判定しやすくなるため。
Point Role Planningは既にこの種の動的選択を行う設計になっており、新規Validatorは不要。

---

## 3. Trend Synthesis の Slot 役割設計

中心Question: *"What is changing, and what do several independent signals together suggest?"*

| Slot | 役割 | 設計メモ |
|---|---|---|
| Main Story | Evidenceを列挙せず、まず共通する変化を提示。代表的Signalで説明。Trendの強さをEvidence以上に誇張しない | Rule 1(Do not manufacture a trend)の主たる実装箇所 |
| Point One | 候補: major driver / strongest signal / what changed from before / underlying mechanism | Point Role Planningで動的選択 |
| Point Two | 候補: counter-signal / limitation / who is affected / what would confirm-reverse / next inflection point / practical meaning | 下記の追加ルールあり |
| In One Line | 方向感+留保。「変化は見えるが確定ではない」等、Evidence strengthに整合させる | Discovery版In One Lineと同じ「断定しない」トーン |

**追加ルール(Trend Synthesis専用、Layer 3内に置く)**: Point Twoは
`counter-signal` または `limitation` のいずれかを既定候補として優先的に検討し、
該当するものが存在しない場合は「反証Signal・限界が見当たらない」こと自体を明示する
(単に省略しない)。これはRule 2(単発とTrendの区別)・Rule 3(Evidence強度の区別)を
Prompt文言レベルで機能させるための最低限のAnchorであり、Layer 1の一般原則
(Evidence-bounded Interpretation)を News/Trend向けに具体化したものと位置づける
(§7で詳述)。

---

## 4. Mode判定基準

「重要なニュースだからTrend」「ソースが複数あるからTrend」という誤った判定基準を明示的に排除し、
以下の2つの判定質問を基準とする。

1. **単一起点質問**: その記事のMain Storyを「[日付]に、Xが起きた」という1文で書いても
   記事の要点が失われないか？ → Yesなら `MAJOR_DAILY`。
2. **集約質問**: いずれか1つのSignalを取り除いても、記事の中心的主張(全体として見える変化)は
   大きく変わらないか？ → Yesなら `TREND_SYNTHESIS`。

具体例による境界確認:

| 候補 | 判定 | 理由 |
|---|---|---|
| 阪神が3-5で負けた | `MAJOR_DAILY` | 単一試合の単一結果 |
| 阪神が優勝した | `MAJOR_DAILY` | 「重要度が高い」だけでは判定を変えない。依然として単一起点イベント |
| 阪神の直近10試合で接戦勝ちが増加 | `TREND_SYNTHESIS` | どの1試合を除いても主張(傾向)は残る |
| 日銀会合前の円高 | `MAJOR_DAILY`(その日の値動きとして書く場合) | 単日の値動きという単一起点で書ける |
| 日銀利上げ決定 | `MAJOR_DAILY` | 単一の決定イベント |
| イラン情勢の日々の小さな動き | `MAJOR_DAILY`(その日の動きとして) | 個々の日次動向はそれぞれ単一起点 |
| イラン情勢で大きな停戦合意 | `MAJOR_DAILY` | 重要度に関わらず単一イベント |
| 数週間にわたる複数の外交・軍事Signal | `TREND_SYNTHESIS` | 単一起点では書けず、複数時点の集約が主張の本体 |

---

## 5. Trend成立条件

Validator実装はせず、Writer/Reviewerが判断する定性的Gate(qualitative gate)として以下を候補とする
(機械的な固定数閾値は今回採用しない。閾値化するかどうかは将来Trial段階の検討課題として保留):

- 独立した2件以上のSignalがある(同一出来事の重複報道ではない)
- 時間的または構造的な変化が識別できる(単なる「複数の出来事」ではなく「方向性の変化」)
- Signalの方向に一定の共通性がある(矛盾するノイズの寄せ集めではない)
- Counter-signal/limitationの有無を確認済み(§3のPoint Twoルールと連動)
- 単一ソースの言い換えでTrendを作っていない
- 直近の既存Trend記事と中心主張が実質同じでない(§8のTrend重複防止と連動)

---

## 6. Evidence Strength の扱い

数値スコアリングの正式仕様化は今回行わない。Layer 4入力(Ledger)に付与する
**分類タグ語彙**として以下を候補とする:

`official_statistics` / `government_regulator_announcement` / `formal_survey` /
`company_official_announcement` / `reputable_media_reporting` / `individual_case` /
`anecdotal` / `social_media_reaction`

目的は「強い/弱い」を数値化することではなく、Trend Synthesis Moduleが
「個別事例1件と全国統計を同列の証拠として扱わない」ことをPrompt上で機能させるための
Ledgerメタデータ設計。実装(Ledger構造への追加)は今回行わない。

---

## 7. Counter-signal / Limitation ルールの置き場所

一般原則(「Evidenceの範囲を超えて断定しない」)はLayer 1(Common Writing Contract、
Discovery/Whyと共有)に既に存在すると位置づけ、重複させない。

News/Trend固有の**具体的チェックリスト**(mixedならmixedと書く、regionalならregionalと書く、
1社の事例をindustry-wideとしない、correlationをcausalityとしない、early signsをestablished trendと
しない)は、Layer 1を肥大化させずLayer 3(Trend Synthesis Module)側に置く。
理由: これらはNews/Trend以外のEditorial Type(Discovery/Why、将来のB/C群)には当てはまらない
具体化された運用ルールであり、Layer 1は「Editorial Type非依存」という定義(既存LAYER_MAPPINGの分類方針)
と整合させる必要があるため。

---

## 8. Trend重複防止設計(将来設計のみ・今回実装禁止)

**Trend Memory**という将来概念を整理する。これは4層Prompt構造そのものではなく、
候補収集パイプライン(§1の「候補整理」〜「Mode判定」の間)に位置する上流機構と位置づける。

記録候補フィールド: `topic` / `central_claim` / `main_angle` / `supporting_signals` /
`counter_signal` / `conclusion` / `publication_date`

新規Trend候補に対する確認項目:
1. 前回と同じcentral claimか
2. 新しい強いSignalがあるか
3. 状態変化があるか
4. 視点変更があるか
5. 十分な期間が経過しているか

再記事化を許可する条件候補(A〜Dのいずれか): A. 状態変化 / B. 新しい強いSignal /
C. 新しい中心Question・angle / D. 十分な期間経過。

**今回は実装しない。** Layer 3/4の設計そのものには影響しない外側の仕組みとして切り離して整理した。

---

## 9. Personalization との将来整合

現在: `Coverage Required = false`(候補群から必要本数を選択する運用)。
将来: ユーザー登録テーマ(例: 阪神)については `Coverage Required = true` とし、
候補競争に関わらず継続的に記事化する概念を将来追加できるようにする。

**整合確認結果**: `Coverage Required` は候補選定パイプライン(§1の「候補収集」〜「Mode判定」より前)の
フラグであり、4層Prompt構造そのもの(Layer 1〜4)には影響しない。Coverage Required対象テーマの
日次更新(例: 阪神の通常の試合結果)も、§4のMode判定基準に従えば通常は単一起点イベントとして
`MAJOR_DAILY` に分類されるため、今回の設計と矛盾しない。今回の設計変更は不要。

---

## 10. 既存QA / Retry との整合・Gap一覧

**Point Role Planning / Point Value QA**: §2/§3で述べた通り、動的役割選択の仕組みとして
Major/Daily・Trend Synthesisいずれにも流用可能と判断。Trend Synthesisで
「Point One = Signal A の紹介、Point Two = Signal B の紹介」という単純な
Source列挙になることを防ぐため、Layer 3側で「Point One/Twoは個々のSignalの紹介ではなく、
意味づけ(driver/mechanism/counter-signal等)の違いで分ける」という指示を持たせる設計とする
(Prompt文言レベルの対応であり、新規Validatorコードは不要と判断)。

**Diagnostic Full Retry**: 既存の診断語彙(paraphrase/overlap系が中心)には、
News固有の失敗パターン(evidence listing・trend overclaim・weak counter-signal・
daily newsの背景過多・Point role collapse)に対応する語彙が**存在しない**。
これは**Gap**として明示する。今回は変更しないが、News系をProduction化する際は
診断語彙の拡張が必要になる可能性が高い(コード変更を伴うため、今回のスコープ外)。

**Fact Safety(Ledger Deviation Checker)**: 既存の10種類の変化検知
(`changed_fact`/`changed_scope`/`changed_causality`/`changed_certainty`/`changed_number`/
`changed_actor`/`changed_negation`/`changed_comparison`/`changed_time`/`unsupported_new_claim`)は、
event fact・date/time・sequence・causality・unsupported projectionをある程度カバーする。
一方、**trend overclaim(複数Signalをまたぐ相関→因果の飛躍、1社事例→業界全体化)**と
**source strength(個別事例と公式統計を同列に扱う)**に対応する専用カテゴリは存在しない。

これは新しい問題ではなく、[OPEN-112-DISCOVERY-4LAYER-FINAL-ADOPTION-READINESS-AND-OPEN114-REGISTER-07](OPEN_ITEMS.md)で
既に指摘された「Ledgerは事実単位の安全確認であり、複数Evidenceをまたぐ統合的な意味づけの強さそのものは
設計上のスコープ外」という既知のGapと同じ系統である。ただし、**Trend Synthesisは
Discovery/Whyよりも明示的に複数Signalの統合を要求するModuleであるため、この既知Gapが
より強く顕在化しやすい**点は今回新たに指摘しておく(§17リスク参照)。

---

## 11. 次Trial設計の論点(Trial自体は未実施)

Trial候補条件(タスク§18の再整理):

- **Major/Daily用**: 単発ニュースとして明確、Trend化不要、Fact Ledgerを作りやすい、A2/B1両方で比較可能
- **Trend用**: 複数独立Signal、Trendとして成立しそう、Counter-signal/limitationあり、過度に複雑でない

**Read-onlyでの候補確認結果**(既存Topic Master由来の`topic_package_*.py`をread-onlyで確認、
生成は行っていない):

- `topic_package_阪神タイガース_2026-07-15.py`: 単一試合結果、VERIFIED FACTS/CONTESTED/GENERAL
  KNOWLEDGE/SPECULATIONの区分が既に明確。**Major/Daily候補として好適**。
- `topic_package_イラン_アメリカ_情勢_2026-07-14.py`: 複数ソース(AP/WaPo/Axios/CBS等)、
  CONTESTED/SINGLE-SOURCE区分(イラン側主張の未確認情報、国際海事機関の見解相違等)が
  既にCounter-signal/limitationに近い形で整理されている。**Trend Synthesis候補として好適**。

いずれも新規収集不要で既存Topic Masterから使える状態にあることのみ確認した。
記事生成・Trial実行は今回行っていない。

---

## 12. A Family Common Skeleton との整合確認

Major/Daily・Trend Synthesisいずれも、Main Story/Point One/Point Two/In One Lineの
4slotで自然に設計できることを§2/§3で確認した。物理構造・見出し数の変更は不要。
片方だけ別構造が必要という事態は発生しなかった(STOP条件は発生しない)。

---

## 13. 総合リスクと結論

**構造的な結論**: News系2モードはDiscovery/Whyと同じ4層構造・同じPoint Role Planning機構の上で
成立する設計に到達した。STOP条件(§20)はいずれも発生しなかった。

**残るリスク(§10の再掲)**: Trend Synthesisは、既存Fact Safety(Ledger)のスコープ外にある
「複数Signalをまたぐ統合的な意味づけの強さ」を、Discovery/Whyよりも強く要求する設計になっている。
これは新設計の欠陥ではなく、既存の既知Gapが今回のモードでより表面化しやすいという指摘であり、
実際にTrialを行って測定するまでは実害の程度が不明である。

次工程(Trial設計)に進む前に、このリスクへの追加対策(例: Trend Synthesis Module内の
Counter-signal必須化ルール〔§3で既に設計に組み込み済み〕で十分か、それとも
Ledger側の拡張を先に検討すべきか)について、ユーザーの意向確認を推奨する。
