# OPEN-112-ENGAGEMENT-REFERENCE-CROSS-TOPIC-AB-TRIAL-11 最終報告

## 1. 最終Status

`USER_DECISION_REQUIRED`

理由: 施策1(Entertainment/Engagement根底指示)は、性質の異なる2つの新テーマ
(週4日勤務・スロー旅行)でも、Trial-10(イラン/ホルムズ)と同様に「見かけと実態の
ギャップ」を軸にした構成へ安定して改善した。施策2(Reference Digest)は今回も
安全性(Fact漏洩ゼロ・コストほぼゼロ)は確認できたが、Entertainment性そのものへの
明確な追加効果はやはり確定できなかった。さらに、本Trialで新たに、
「Main StoryがGap/Tension構造を取ると、Point TwoがFull Storyの言い換えになり
やすく、既存QA(Point Value QA・Point Overlap)を通過しにくくなる」という、
Trial-10では顕在化しなかった新しいTrade-offが見つかった(Theme 2 Aは既存の
安全装置により`NG_REVIEW_REQUIRED`でHuman Review行きとなった)。また、今回の
新しいResearch経路(Perplexity sonar-pro)でも、独立verificationをすり抜けた
軽微なLedger精度の粒度問題が1件見つかった(§15)。これらはいずれもユーザー判断を
要する論点であり、`REJECTED`でも単純な`VALIDATED`でもない。

## 2. 対象範囲・非対象範囲の確認

Production Prompt・Common Writing Contract・Reference Digest正式実装・Engagement
正式実装・News Focus Module正式化・Discovery変更・Ledger Production自動化・新
Validator・Point Overlap閾値・Point長・Trend severityルール・SSOT上のProduction
statusは一切変更していない。`er003_v1_n3_01_articles_generate.py`を含む既存
ファイルは無変更。`gen.run_one_pattern()`を無変更のまま呼び出した。Engagement
根底指示は Trial-10 の`ENTERTAINMENT_ENGAGEMENT_BLOCK`と一字一句同一を使用した
(`er011_output/open112_engagement_reference_cross_topic_ab_trial_11/audit/candidate_template_A.txt`
参照)。新規Trial script
`er011_open112_engagement_reference_cross_topic_ab_trial_11.py`をTrial-10 scriptを
土台に新規作成し、出力先は
`er011_output/open112_engagement_reference_cross_topic_ab_trial_11/`に隔離した。
Git操作・他Agent起動は行っていない。

## 3. Research方法(重要な設計変更点)

本Trial実行時点でAgentにWebSearch/WebFetchツールが与えられていなかったため、
Trial-9/10のような直接WebSearch/WebFetchではなく、既存の承認済みAPI呼び出し
パターン(`er006_pronunciation_research_01.py`等で既に使われている、Perplexity
`chat/completions`エンドポイント・model=`sonar-pro`をrequests経由で呼ぶパターン)
を、本Trial script内の新規関数として再利用した(新規Production Researcher
モジュールは作らない、既存パターンの流用のみ)。

- Stage 1: 各テーマについてsonar-proへ構造化JSON schemaでfact収集を依頼
  (実際のWeb検索結果に基づく回答、citations付き)。
- Stage 2: 収集したfactリストを渡し、同じsonar-proに**独立した別プロンプト・
  別検索**でverification(CONFIRMED/PARTIALLY_CONFIRMED/COULD_NOT_CONFIRM/
  CONTRADICTED判定)を依頼。
- Stage 3: Reference Articles探索(sonar-pro、実在URL・発行元・日付を返させる)。
- Stage 4: Reference Articlesの「構成・切り口」のみを抽出させる制約付き
  プロンプト(具体的事実・数字・固有名詞・引用の書き出しを明示的に禁止)。

生ログはすべて`er011_output/open112_engagement_reference_cross_topic_ab_trial_11/research/`
配下に保存した(`theme{1,2}_..._facts_raw.json`、
`theme{1,2}_..._facts_verification_raw.json`、
`theme{1,2}_..._reference_discovery_raw.json`、
`theme{1,2}_..._reference_structure_raw.json`)。この設計変更自体はTrial範囲内の
Research手法の変更であり、Production Researcher実装ではない。

## 4. Theme 1 Trend Gate

対象: 日本企業における選択的週休3日制・週4日勤務の導入・検討動向(2026年9月時点)。
Ledger全文: `er011_output/open112_engagement_reference_cross_topic_ab_trial_11/research/theme1_verified_fact_ledger.txt`

判定: **TREND_READY**(ただし「単純増加」ではなく「Gap Trend」として)

1. 独立した複数Signal: 政府公式統計(F-101/F-102)・個別大手企業の発表
   (JT=F-103、日立/パナソニック/ファストリテイリング/ロート製薬等=F-104)・
   求人サイトデータ(Indeed=F-105)・従業員意識調査(日経調査=F-107)・利用実態
   報道(パナソニック=F-106)・トヨタの検討報道(F-109)という、出所の異なる
   最低6系統の独立Signalを確認。
2. 共通方向: 単純な「一方向の増加」ではなく、「個別の発表・関心の高まり」と
   「全国統計上の普及率(直近でむしろ低下)」という、2つの系列が同時に別方向へ
   動く**Gap構造**が共通して観察される。これ自体を「変化の性格」として扱う
   (Trial-10のIran/HormuzでもF-009単日実績 vs F-010/F-012独立統計という
   類似のGap構造があり、前例に沿う設計)。
3. 時間的/構造的変化: 2021年(塩野義)〜2027年(JT)にかけて複数年にわたる制度
   導入の広がりと、2024年度→2025年度の統計比較という、時系列比較が可能。
4. Counter-signal/limitation: F-101(統計上の低下)・F-106(パナソニックの
   低利用率)を明確な counter-signal として明記。
5. 単一イベントのTrend化でないか: 複数企業・複数年・複数調査に基づくため
   単一イベントではない。
6. Evidence strengthを同列扱いしていないか: official_statistics /
   company_official_announcement / reputable_media_reporting /
   industry_survey / private_analysis を明示的に区別し、Ledger内の
   `counter_signal_or_limitation`欄で混同を戒めている。

## 5. Theme 2 Trend Gate

対象: 日本の若者(10代後半〜30代前半)の旅行における「スロー志向」の高まりと、
実際の滞在日数とのギャップ(2026年9月時点)。
Ledger全文: `er011_output/open112_engagement_reference_cross_topic_ab_trial_11/research/theme2_verified_fact_ledger.txt`

判定: **TREND_READY**(Theme 1と同様、「完全な行動シフト」ではなく「Gap Trend」として)

1. 独立した複数Signal: JTB総合研究所調査(F-202)・観光庁調査(F-203/F-206)・
   じゃらんリサーチセンター調査2件(F-204/F-205)・ヒルトン グローバル調査
   (F-201)・じゃらん同行形態調査(F-208)という、最低5系統の独立Signal。
2. 共通方向: 「自分のペースでゆっくり過ごしたい」という意識・願望の高まり
   (F-201/F-202/F-203/F-204)と、「実際の滞在日数は依然として短い」
   (F-205/F-206)という、意識と行動のGap。
3. 時間的/構造的変化: 2022年(コロナ直後の近場・短期旅行増加)〜2025年
   (Z世代個別調査)にかけての変化、および同一調査シリーズ内での「希望」対
   「実際」の対比。
4. Counter-signal/limitation: F-205(実際の宿泊日数は平均1.8泊)・F-206
   (観光庁自身が「滞在長期化が必要」と明記)・F-202(女性29歳以下は依然
   「有名な観光地を巡る」志向が44.7%と高い)を明記。
5. 単一イベントか: 複数の独立調査機関・複数年にまたがるため単一イベントでない。
6. Evidence strength: official_statistics(観光白書)/
   company_official_announcement(じゃらん・ヒルトン)/
   government_official_announcement(観光庁)/reputable_media_reporting
   を区別。1件(F-207、やまとごころ記事のデータ)は独立検索で
   `COULD_NOT_CONFIRM`となったため、Writerに使用回避を明示指示し、
   実際に最終記事では使用されなかった(§17で確認)。

## 6. Ledger Verification結果サマリ

- Theme 1: 13 fact中、CONFIRMED 9件、PARTIALLY_CONFIRMED 4件(F-102の一次
  資料表現差異、F-106のパナソニック利用率0.24%が二次分析記事由来である点など)。
  CONTRADICTED・COULD_NOT_CONFIRMは0件。
- Theme 2: 独立verificationにかけた15 fact中、CONFIRMED 12件、
  PARTIALLY_CONFIRMED 2件、COULD_NOT_CONFIRM 1件(F-207、やまとごころ記事)。
  CONTRADICTEDは0件。
- 生ログ: `research/theme1_4day_workweek_facts_verification_raw.json`、
  `research/theme2_slow_travel_facts_verification_raw.json`。

## 7. Theme 1 A記事全文(施策1のみ、Reference Digestなし)

```markdown
# Japan’s Four-Day Workweek: Big Attention, Small Reach

In Japan, the four-day workweek is becoming easier to see—but it is not yet common. That is the striking gap in the story.

JT announced in June 2026 that it plans to start a selective three-day weekend system in April 2027. Employees in eligible jobs will be able to choose from different work patterns.

Other major companies have also introduced some form of a three-day weekend or four-day workweek. These announcements make change look close.

Interest is growing, too. Over the past five years, job listings related to a three-day weekend rose 5.3 times. Searches for those jobs showed the same pattern.

But the official national picture tells a different story.

According to a Japanese government survey, the share of companies using any kind of three-day weekend system fell from 1.6 percent in the 2024 survey to 0.9 percent in the 2025 survey.

So two different images exist at the same time.

In company announcements and job searches, the idea is becoming more visible. Across companies as a whole, however, the system remains rare, and the latest official figure is even lower.

This is not a simple story of rapid nationwide growth. It is a story of attention moving faster than broad adoption.

### When attention moves faster than adoption

The labor-market conversation is gaining momentum. A three-day weekend was also among the workplace benefits employees most wanted in a survey. These figures show rising interest in more flexible choices, not a major change in most workplaces. For future headlines, ask one simple question: is this evidence of demand, or evidence of actual adoption?

### What the label can hide

A “three-day weekend” does not always mean the same pay for fewer hours. JT’s planned system has two models: one keeps weekly hours the same by making workdays longer, while the other adjusts pay when working days fall. Eligibility will also depend on the job and other conditions. At Panasonic, reports said 93 employees used the hours-maintained option, while four used shorter-hours options in 2023. A program on paper may still affect only a small group.

## In one line…

Japan is seeing more attention and more company programs, but not yet a common four-day workweek. The strongest nationwide data still show limited uptake, with a recent decline.
```

パイプライン最終status: `OK`(Fact Checker `REVIEW_REQUIRED`、非blocking。
Ledger Deviation `LEDGER_COMPLIANT`、deviations 0件)。

## 8. Theme 1 B記事全文(施策1+施策2、Reference Digestあり)

```markdown
# Japan’s Four-Day Week: Big Headlines, Small National Footprint

As of September 2026, Japan’s four-day workweek story has two faces. The idea is becoming easier to see, but it is not yet clearly spreading across the country.

JT announced that it will introduce a selective three-day weekend system in April 2027. Some eligible employees will be able to choose how many days they work. The company plans two options. One keeps total weekly working hours the same by making workdays longer. The other reduces pay as working days decrease. The system will not be available to every employee.

Similar programs are already available at several large companies. Interest is also rising. One report found that job postings mentioning a three-day weekend grew 5.3 times over five years. Searches for those jobs showed the same pattern. A separate survey also found that employees placed a three-day weekend system among the workplace programs they most wanted.

Then comes the surprise.

Official national data from Japan’s Ministry of Health, Labour and Welfare shows a different direction. The share of companies with some kind of three-day weekend system fell from 1.6 percent in the 2024 survey to 0.9 percent in the 2025 survey. The share with a fully fixed three-day weekend also fell, from 0.3 percent to 0.0 percent.

So this is not a simple story of growth. Big companies are making visible announcements, and workers are showing strong interest. But the strongest nationwide measure does not show broad adoption. Japan has more attention around the idea, while its measured reach remains small.

### A four-day week is not one deal

The label hides the actual deal. JT’s planned choices show that one route can keep total hours unchanged, while another can reduce pay. Other companies use different models, and access may be limited to selected roles. At one company, 93 employees were reported to use the hours-maintained option, and four the shorter-hours option. Availability is not the same as use.

### What each number is really measuring

A rise in searches, job listings, or employee preference is an early signal of demand. It does not measure the same thing as formal company adoption or actual employee use. One reported 7.5 percent figure also uses a wider definition, so it cannot be placed beside the official 0.9 percent without care. When a new headline appears, ask: is it about demand, advertising, availability, or use?

## In one line…

Japan is showing real and growing interest in shorter workweeks, but the clearest national data still points to limited adoption. For now, this is a visible group of experiments, not yet a settled national shift.
```

パイプライン最終status: `OK`(Fact Checker `PASS`。Ledger Deviation
`LEDGER_COMPLIANT`、deviations 0件)。

## 9. Theme 2 A記事全文(施策1のみ、Reference Digestなし)

```markdown
# Japan’s Young Travelers Want More Control, but Their Trips Are Still Short

A curious gap is opening in the way young people in Japan think about travel.

They seem to want trips that move at their own speed. They want time for personal interests, and less pressure to visit one famous place after another.

Several independent surveys point in this direction. Among Japanese Gen Z travelers with overseas travel experience, nearly 90% wanted free time during a tour. Most of them wanted at least half a day.

But the wish for more time does not yet match the length of a typical trip.

When people were asked what they would do if they could take a full month off, the most common answer was a trip of about one week. It was chosen by about 24% of respondents.

In a separate autumn survey of people planning a trip, however, the expected stay was much shorter: 1.8 nights on average, with a median of 2 nights.

These answers are not necessarily contradictory. One question imagined a full month away. The other looked at a more ordinary trip. Together, they show a clear tension: the idea of slow travel is becoming more attractive, while actual travel plans remain short.

An official tourism report also lists longer stays and more trips as continuing policy goals. So this is not yet a complete move from sightseeing to long, relaxed stays.

### Slow travel can mean control, not just more nights

Here, slow travel may be less about adding nights and more about deciding how those hours are used. In a survey, men aged 29 and under chose solo travel at 25.2%, while hobby-focused travel was also among their leading styles. At the same age, about 45% of women still showed interest in visiting famous sights. The message is not that sightseeing is over. Travel design may need both shared routes and meaningful personal time.

### The missing step is turning a wish into a trip

The one-week answer may show some unused appetite for longer travel, but it does not prove that week-long trips are already normal. It came under the special condition of having a full month off. For tourism planners, the practical question is whether that wish can become extra nights or repeat visits. The surveys do not identify one single reason why stays remain short.

## In one line…

Japan’s travel culture is bending toward more self-directed trips, especially among young men, but the evidence still shows an emerging wish—not a settled move to long stays.
```

パイプライン最終status: `NG_REVIEW_REQUIRED`(§13参照。Point Two が
Point Value QAで`qa_not_full_story_paraphrase`/`qa_adds_new_value`に
FAILし続け、かつPoint Overlap `before_overlap`が0.462で閾値0.40超のため
Point-only regeneration相当を試みたが、ER-008-N8-FINAL-QA-HARDENING-21
によりPoint-only自動regenerationはProduction経路から既に外されており
[過去のFact fabrication事例のため]、既存の安全装置どおりHuman Review行きと
なった。Fact CheckerおよびLedger Deviation Checkerには到達していない)。

## 10. Theme 2 B記事全文(施策1+施策2、Reference Digestあり)

```markdown
# Young Japanese Travelers Want More Room to Breathe. But Their Trips Are Still Short

A quiet change may be taking place in the way young people in Japan think about travel.

The question is no longer only, “Where should we go?”

It is also, “Can I travel at my own pace?”

Several surveys point in this direction, especially among young men. Solo trips, hobby-focused travel, and free time inside organized tours are becoming important parts of the picture.

But there is a twist.

Wanting more freedom does not always mean staying longer. Surveys of planned autumn trips still show short stays. So Japan may be seeing a change in travel preferences before a clear change in travel behavior.

This is not yet a complete move from sightseeing to long stays.

It is a story about a gap: the wish for a slower, more personal trip is becoming easier to see, while the time people plan to spend at their destination remains limited.

### Slow travel can mean control, not just more days

Here, “slow” does not always mean taking a long holiday. It can mean choosing the pace and subject of the trip. Among men aged 29 and under, solo travel was 25.2%, while hobby-focused travel showed a similar level of interest. About nine in ten Gen Z travelers with overseas experience wanted free time in a tour, and most wanted half a day or more. But nearly half of young women still favored famous attractions. That points to flexible travel, not one standard model.

### The wish has not become a stable pattern yet

The harder question is whether this wish becomes a stable pattern. When asked about taking a month-long break, about one in four chose “about one week,” the most popular answer. Yet autumn travel plans averaged under two nights, with a median of two. For now, slow travel looks like possible demand, not established behavior. A policy report still lists longer stays as a goal. The key test is realized nights, not ideals alone.

## In one line…

Young people in Japan appear to be moving toward more personal, slower travel, but the evidence still shows an emerging preference—not a completed change in how long they stay.
```

パイプライン最終status: `OK`(Fact Checker `REVIEW_REQUIRED`、非blocking。
Ledger Deviation `LEDGER_COMPLIANT`、deviations 0件。ただし、Point Value QA/
Point Overlapで2回のDiagnostic Full Retryを要した後、3回目の生成attemptで
クリアに通過。詳細§13)。

## 11. Theme 1 A/B比較(§9評価項目)

| # | 項目 | A | B |
|---|---|---|---|
| 1 | 冒頭で興味を引くか | Yes(「注目は増えているが普及していない」という対比を明示) | Yes(「二つの顔がある」という対比を明示) |
| 2 | 時系列羅列脱却 | Yes(冒頭で性格づけ→根拠の順) | Yes(同様の構成) |
| 3 | 意外性 | 中(統計が「増えている」の逆を示す点が主眼) | 中(Aとほぼ同水準) |
| 4 | throughline | Yes(「注目 vs 普及のGap」で一貫) | Yes(同じGapで一貫、"two faces"という言い回し) |
| 5 | 聞いていて面白いか | Yes | Yes |
| 6 | 人に話したくなるポイント | 「統計はむしろ下がっている」という逆説 | 同左 |
| 7 | Point One/Twoの切り口 | Point One=関心の高まり側、Point Two=制度の中身の落とし穴(パナソニック実例) | 同様の役割分担、Point Twoに「数字が何を測っているか」という追加の解釈フレームあり |
| 8 | BがAより明確に優れているか | — | **明確な優位とは言えない**(§14参照。Fact Checker結果はBがクリーンだが、構成・面白さの差は僅少) |

安全6項目: Fact逸脱=両方なし(Ledger Deviation 0件)。Trend overclaim=
Fact Checkerで両方とも矛盾なし(A/B共にcontradictions=[])。unsupported
causality=検出なし。sensationalism=検出なし。Reference Fact leakage=
該当なし(Aはそもそも対象外、Bは§17で確認)。Counter-signal保持=両方とも
F-101(統計低下)・F-106(パナソニック低利用率)を保持。

## 12. Theme 2 A/B比較(§9評価項目)

| # | 項目 | A | B |
|---|---|---|---|
| 1 | 冒頭で興味を引くか | Yes(「奇妙なGapが生まれつつある」という直接的な提示) | Yes(「Where should we go?」→「Can I travel at my own pace?」という問いの転換) |
| 2 | 時系列羅列脱却 | Yes | Yes(Aよりさらに対話的・断片的な文構造) |
| 3 | 意外性 | 中(意識と行動のGapという構造自体は共通) | 中(Aとほぼ同水準。ただし短文を多用したテンポの違いあり) |
| 4 | throughline | Yes(「願望 vs 実際の滞在日数」のGap) | Yes(同じGap。"But there is a twist"という明示的な転換点あり) |
| 5 | 聞いていて面白いか | Yes | Yes(短文が続き、より会話的なリズム) |
| 6 | 人に話したくなるポイント | 「1週間希望 vs 実際1.8泊」という数字の対比 | 同左 |
| 7 | Point One/Twoの切り口 | Point One=男女差、Point Two=「1週間という答えの限界」 | 同様の役割分担 |
| 8 | BがAより明確に優れているか | — | パイプライン結果としては**Bのみ完走**(§13参照)。ただし完走したこと自体はReference Digestの効果と断定できない(Point Role PlanningのretryはA/B両方で発生しており、Bはたまたま3回目で閾値内に収まった可能性がある) |

安全6項目: Fact逸脱=Aはこの段階に未到達(Ledger Deviation Checker未実行)、
Bはdeviations 0件。Trend overclaim=Bの Fact Checkerが4件のReview指摘
(§15)。unsupported causality=B側でFact Checkerが「単時点調査から
"高まり""変化"と書くのは時系列証明が弱い」と指摘(§15)。sensationalism=
検出なし。Reference Fact leakage=該当なし(§17)。Counter-signal保持=
両方ともF-205(実際は短い)・F-206(政策課題として明記)・女性の観光地志向
44.7%を保持。

## 13. 既存Production Retry/Diagnostic機構の発火状況(全4パターン)

| パターン | Point Role Planning retry | Point Value QA attempts | Diagnostic Full Retry(全文re-attempt) | Local Rewrite | Point Overlap flag | Fact Checker | Ledger Deviation |
|---|---|---|---|---|---|---|---|
| Theme1 A | 0回(初回PASS) | 1回(PASS) | 0回 | 0回 | flagなし | REVIEW_REQUIRED | LEDGER_COMPLIANT(0件) |
| Theme1 B | 0回(初回PASS) | 1回(PASS) | 0回 | 0回 | flagなし | PASS | LEDGER_COMPLIANT(0件) |
| Theme2 A | 2回(計3 attempts) | 3回(attempt0 NG, attempt1 PASS値だがOverlap flag, attempt2 NG) | 2回(未解決のままPoint-only regenerationは無効化されているため`NG_REVIEW_REQUIRED`で停止) | 0回(到達せず) | attempt0/1/2すべてPoint Twoでflag | 未到達 | 未到達 |
| Theme2 B | 2回(計3 attempts) | 3回(attempt0/1 PASS値だがOverlap flag、attempt2クリア) | 2回(3回目でクリア) | 0回 | attempt0/1でflag、attempt2でクリア | REVIEW_REQUIRED | LEDGER_COMPLIANT(0件) |

いずれも既存のProduction安全装置(ER-008-N8-FINAL-QA-HARDENING-21で
Point-only regenerationがProduction経路から外されている措置を含む)が
無変更のまま動作した結果であり、本Trialで新しい閾値・新しいQA・追加の
再生成上限緩和は一切行っていない。Theme 2 Aは、既存の安全装置が正しく
「危険なPoint-only自動修正」を回避し、Human Review行きにした事例として
記録する(止めない・追加しないという指示どおり、これ以上の追加attemptは
行わなかった)。

## 14. Cross-topic評価(Trial-10を含めた3テーマ横断)

| テーマ | A最終status | B最終status | Fact Checker A | Fact Checker B | B完走性 |
|---|---|---|---|---|---|
| Trial-10: イラン/ホルムズ | NG_REVIEW_REQUIRED(Fact Checker FAIL、Ledger入力ミスが原因) | OK | FAIL(Ledger起因、Writer起因でない) | REVIEW_REQUIRED | Bのみ完走 |
| Theme 1: 週4日勤務 | OK | OK | REVIEW_REQUIRED | PASS | 両方完走、Bがよりクリーン |
| Theme 2: スロー旅行 | NG_REVIEW_REQUIRED(Point Overlap/Value QA起因、Ledger起因でない) | OK | 未到達 | REVIEW_REQUIRED | Bのみ完走 |

3テーマ中2テーマ(Iran、Theme 2)でAがNG_REVIEW_REQUIRED、Bのみ完走という
同じパターンが再現した。ただし**原因はテーマごとに異なる**(Iranは
Ledger入力ミス起因のFact Checker FAIL、Theme 2はPoint構造上の
Overlap/Value QA起因)。したがって「Bだから完走した」という単純な因果は
主張できない。しかし、「A/Bで同じ入力・同じLedgerを使っているにもかかわらず、
Bの方が最終的に安定してクリアに通過する傾向が3回中3回とも観察された
(一度もAがBより明確に優れた結果にならなかった)」という、頻度としての
一貫したパターンは記録に値する。イランだから/週4日勤務だから/旅行だから
特定の結果になったという単一テーマ限定の偶然ではなく、3つの異なる性質の
テーマで繰り返し観察された。

## 15. Engagement原則の再現性

3テーマすべてで、Main Storyの冒頭が「時系列の出来事列挙」ではなく、
「見かけと実態のGap」「意識と行動のGap」「単日実績と統計のGap」という
共通の技法(gap between appearance and reality)に自然に収束した。これは
テーマの内容に応じてEngagement根底指示が機械的に同じ言葉を繰り返すのでは
なく、それぞれのLedgerが実際に支持するGap構造を見つけて使えていることを
示す(Ledgerにない意外性を発明していない)。3テーマ中3テーマで再現した
ことから、Engagement原則自体の効果は本Trial範囲では**再現性が高い**と判断する。

## 16. Reference Digestの追加価値

Theme 1・Theme 2とも、Reference DigestはFact漏洩なし・コストほぼゼロ
(§19)という「安全に使える」ことは改めて確認できたが、「Engagement原則
だけの場合と比べて記事が明確に良くなった」とまでは、今回も断定できな
かった。§14の「Bの方が安定してクリアに通過する」という頻度パターンは
興味深いが、原因がテーマごとに異なる(Ledger精度 vs Point構造)ため、
Reference Digestが直接の原因だと断定する根拠にはならない。むしろ、
Point Role Planningのretry機構が持つ確率的な変動(同じLedgerでも複数回
生成すれば結果が変わりうる)による可能性を排除できない。

## 17. Trend overclaim

- Theme 1 A: Fact Checker `contradictions: []`。overclaimに相当する指摘は
  0件(§15参照の`unsupported_specific_claims`2件は「数値の厳密な表現の
  精度」に関する指摘であり、事実の逸脱・誇張ではない)。
- Theme 1 B: `contradictions: []`、`unsupported_specific_claims: []`。
  overclaim 0件。
- Theme 2 A: Fact Checkerに未到達のため測定不能。
- Theme 2 B: `contradictions: []`。`unsupported_specific_claims`4件
  (§18で詳述)はいずれも「単時点調査から"高まり"と書く際の時系列証明の
  弱さ」「対象母集団の限定の有無」「予定日数を実績として扱っていないか」
  という、precision(厳密性)に関する指摘であり、Ledgerにない事実の
  捏造やsensationalismには該当しない。

Ledger Deviation Checker側のdeviationsは、到達した3パターンすべてで
**0件**(A theme1=0、B theme1=0、B theme2=0)。Local Rewrite・Point-only
regenerationの結果としての本文修正は、全4パターンで**0件**(Theme 2の
Diagnostic Full Retryは既存のPoint Role Planningからの再生成であり、
既存テキストの部分編集ではないため、trial10と同じ意味での「修正Case」
形式には該当しない。§13の表に発火事実・回数として記録した)。

## 18. overclaim/精度指摘の詳細(Fact Checkerの`unsupported_specific_claims`全件)

**Case 1(Theme 1 A)**: Indeedの「5.3倍」表現について、Fact Checkerは
「Indeedの一次発表は求人**件数**そのものではなく、100万件あたりの掲載割合・
3か月移動平均で測定しており、記事の"job listings...rose 5.3 times"という
書き方はやや不正確」と指摘(ただし上昇トレンドと5.3倍という数字自体は
支持されるとした)。**本文修正: なし**(Fact Checkerの verdict は
REVIEW_REQUIRED止まりで、既存のFact Checker運用ではLocal Rewrite等の
自動修正をトリガーしない非blocking判定のため、記事はそのまま採用)。
Fact Safety: 実害は軽微(トレンド方向自体は誤っていない)。Entertainment
impact: 該当なし(本文修正が発生していないため)。

**Case 2(Theme 1 A)**: JTの「二つのモデル」という制度説明について、
Fact Checkerは「JT公式発表(2026年6月11日)はこの2モデルを明記しておらず、
二次報道(日経等)による補足情報」と指摘。**本文修正: なし**(同上、
non-blocking)。Fact Safety: 実害は軽微(二次報道自体は複数確認されており、
Ledger F-104の元情報とも整合)。

**Case 3(Theme 2 B)**: 「nearly 90% wanted free time」の対象を
"Gen Z travelers with overseas travel experience"と限定した記述について、
Fact Checkerは「観光庁の公式資料は19〜25歳のZ世代400人全体に対する調査
であり、海外旅行**経験者限定**の集計とは明記していない」と指摘。これは
本Trialの追加Research(supplemental fact_12)の元記事の見出しが
"Japanese Generation Z who have experienced overseas travels"という
限定表現を使っていたため、Ledger作成段階でこの限定が本調査の設計に
由来するのか記事見出しの単純化かを区別できなかったことに起因する。
**本文修正: なし**(non-blocking、記事はそのまま採用)。Fact Safety:
軽微(方向性自体は誤っていない可能性が高いが、対象母集団の厳密さに
限界がある)。**これはTrial-9/10で見つかった3件のLedger精度誤りに続く、
4件目の同種の精度課題として記録する**(§21参照)。

**Case 4(Theme 2 B)**: 「Solo trips...are becoming important」
「Japan may be seeing a change」等の"高まり""変化"という表現について、
Fact Checkerは「引用調査の多くが単時点の横断調査であり、時系列の増加
傾向や因果関係そのものを直接証明していない」と指摘。**本文修正: なし**
(non-blocking)。Fact Safety: 軽微〜中程度(Ledgerの central_claim自体が
「意識の高まり」を主張しているため、この指摘はLedgerの設計段階の限界を
反映しており、Writerの逸脱ではない)。

**Case 5(Theme 2 B)**: 「Their Trips Are Still Short」という中心対比が、
実際には完了した旅行実績ではなく「予定・検討中」の宿泊予定日数(じゃらん
2024年秋調査)に基づく点について、Fact Checkerは「予定日数を実現した
行動の実測値として扱うことはできない」と指摘。**本文修正: なし**
(non-blocking)。Fact Safety: 軽微(「予定」であることはLedger F-205にも
明記されており、記事本文も"Surveys of planned autumn trips"と明示している
ため、読者に誤解を与える記述ではないと判断できるが、Fact Checkerの
慎重な指摘として記録する)。

## 19. 安全修正後のEntertainment impact

該当なし。§17・§18のとおり、本Trialでは4パターンいずれにおいても
Fact Checker指摘・Ledger Deviation指摘に基づく本文修正(Local Rewrite・
Point-only regeneration)は1件も発動しなかった(すべてnon-blockingの
REVIEW_REQUIRED、またはdeviations 0件のため)。

## 20. Reference Fact leakage

Theme 1 B・Theme 2 Bそれぞれについて、Reference Articles固有の具体的
要素を逐語チェックした。

- Theme 1 Reference固有要素(未使用を確認): 著名経営者個人名の予測発言、
  UK/Microsoft Japan等の他国・他社の週4日勤務トライアル具体数値
  (61社・92%継続・18社恒久化等)、Wellcome Trust、SMBC日興証券の2020年
  開始時期、World Economic Forum記事の具体的トライアル参加者数、
  Forbes報告の「世界2%」という具体的数値(Ledger F-108として独自収集
  済みだが、B記事本文では未使用)。**いずれも本文に混入していない**。
- Theme 2 Reference固有要素(未使用を確認): 「観光客6000万人目標」
  (Travel And Tour World)、Dentsu-ho調査の具体的数値、Japan Wise Life/
  Craft Travelのラグジュアリー旅程・地名の具体例。**いずれも本文に
  混入していない**。

Reference Digest自体(`research/theme{1,2}_..._reference_digest_block_used.txt`)
にも、冒頭の警告文が両テーマとも含まれており、具体的な数字・固有名詞・
引用は一切含まれていないことを目視確認した。

## 21. Cost Trace

生ログ: `er011_output/open112_engagement_reference_cross_topic_ab_trial_11/raw_usage_log_trial11.jsonl`
(OpenAI呼び出し)、および`research/`配下の各`*_raw.json`(Perplexity呼び出し、
公式API応答内の`usage.cost`フィールドをそのまま採用。Perplexityは
`er005_output/cost_baseline_01/pricing_snapshot.json`に価格情報が無いため、
独自に金額を推測せず、公式レスポンスに含まれる実測cost値のみを使用した)。

### OpenAI(Writer/QAチェーン + Reference Digest生成、gpt-5.6-luna、
`er005_output/cost_baseline_01/pricing_snapshot.json`記載単価:
input $0.20/1M・cached $0.02/1M・output $1.20/1M)

| パターン | API呼び出し数 | input tokens(累計) | output tokens(累計) | runtime | cost(USD) | cost(円換算 @¥159/$) |
|---|---|---|---|---|---|---|
| Theme1 A | 6 | 143,273 | 10,367 | 158.0秒 | $0.0411 | 約¥6.5 |
| Theme1 B | 7(Digest含む) | 143,584(うちcache 10,211) | 14,405 | 171.4秒 | $0.0442 | 約¥7.0 |
| Theme2 A | 12(Retry含む、未完走) | 65,548(うちcache 11,410) | 19,926 | 202.1秒 | $0.0350 | 約¥5.6 |
| Theme2 B | 15(Digest+Retry含む) | 178,282(うちcache 21,586) | 32,380 | 302.8秒 | $0.0706 | 約¥11.2 |
| **OpenAI合計** | **40** | **530,687** | **77,078** | — | **$0.1909** | **約¥30.3** |

### Perplexity(Research/Reference収集、model=sonar-pro、公式API応答の
実測cost値)

| 呼び出し | prompt tokens | completion tokens | cost(USD、公式応答値) |
|---|---|---|---|
| Theme1 facts収集 | 451 | 4,860 | $0.0803 |
| Theme1 facts verification | 4,827 | 2,528 | $0.0584 |
| Theme1 reference発見 | 109 | 355 | $0.0117 |
| Theme1 reference構成分析 | 482 | 2,385 | $0.0432 |
| Theme2 facts収集(一般) | 465 | 4,490 | $0.0748 |
| Theme2 facts収集(補足) | 367 | 6,358 | $0.1025 |
| Theme2 facts verification | 7,402 | 3,498 | $0.0807 |
| Theme2 reference発見 | 115 | 309 | $0.0110 |
| Theme2 reference構成分析 | 440 | 958 | $0.0217 |
| **Perplexity合計** | — | — | **$0.4842** |

### 合計(Research + 記事生成 + Reference Digest、Trial全体)

**$0.6751(約¥107.3、@¥159/$)**。うち記事生成・QA・Reference Digest
生成(OpenAI)が$0.1909、新規Research手法(Perplexity)が$0.4842。
Perplexityベースの新Research手法自体は、Trial-9/10がClaude Codeの
WebSearch/WebFetch(このコストロガーの対象外)を使っていたため、
過去TrialとPerplexityコストを直接比較する基準がない。この点は
Trial-9/10とのコスト比較上の新しい変数として明記しておく。

## 22. Reference Digestの追加cost/article

Trial-10と同じ方法(Reference Digest生成呼び出し単体 + Writer本体への
追加input token分のみを切り出す)で算出。

- Theme 1: Reference Digest生成呼び出し $0.00245(input 1,880/output
  1,727) + Writer本体入力増分(+1,609トークン) $0.00032 = **合計
  $0.00277(約¥0.44/記事)**。
- Theme 2: Reference Digest生成呼び出し $0.00211(input 1,535/output
  1,500) + Writer本体入力増分(+1,577トークン) $0.00032 = **合計
  $0.00243(約¥0.39/記事)**。
- Trial-10(参考): 約¥0.43/記事。

3テーマとも約¥0.4/記事という、ほぼ同水準・無視できるコストで一貫して
いる。テーマ単位で複数記事に使い回せば、さらに1記事あたりのコストは
低下する(Trial-10 §25と同じロジック)。

## 23. New QA必要性

**現時点では新QAの追加は不要と判断する。ただし新しい観察事項がある**。
§13で見たとおり、Theme 2ではPoint TwoがFull Storyの言い換えになりやすい
という問題が、既存のPoint Value QA・Point Overlap QAによって**正しく
検知**され、既存の安全装置(Point-only regeneration無効化措置)により
Human Review行きとなった。これは「新しいQAが必要」という結論ではなく、
「既存QAが機能した」証拠である。しかし、この失敗パターン自体
(Gap構造のMain Storyほど、Point TwoがMain Storyの結論を反復しやすい)
は、Trial-10では顕在化しなかった新しい観察であり、Engagement/
Storytelling原則を今後さらに広げる場合には、Point Role Planningの
プロンプト側で「Gap構造のMain Storyの場合のPoint Two設計指針」を
追加検討する余地があることをユーザーへ報告する(今回はPrompt変更を
一切行っていない)。

## 24. USER_DECISION_REQUIRED(今回新規+持ち越し)

1. **新しいTrade-off(今回新規発見)**: Main StoryがGap/Tension構造を
   取ると、Point TwoがFull Storyの言い換えになりやすく、既存QAで
   NG_REVIEW_REQUIRED(Human Review行き)になりやすい(Theme 2 Aで実際に
   発生)。Engagement原則をさらに広げる場合、この構造的難点への対応方針
   (Point Role Planningプロンプトの調整要否等)をユーザーが判断する
   必要がある。
2. **Reference Digestを今後も検証し続けるか(Trial-10から持ち越し)**:
   3テーマ中3テーマで、Bが安定してクリアに完走する頻度パターンは
   観察されたが、原因がテーマごとに異なり(Ledger精度 vs Point構造)、
   Reference Digestが直接の原因とは断定できない。追加検証(同一条件での
   複数run比較等)を行うかはユーザー判断。
3. **Ledger自動化の緊急性(Trial-9/10から持ち越し、今回さらに1件追加)**:
   本Trialの新しいPerplexityベースResearch+独立verification手法でも、
   Theme 2 B(§18 Case 3)で1件の精度課題(調査対象母集団の限定表現)が
   verificationをすり抜け、Fact Checkerの独立Web検索でのみ発覚した。
   Trial-9/10の3件と合わせ、通算4件目。既存Fact Checkerが最終的に
   検知しているため実害は出ていないが、ユーザー判断が必要。
4. **Point長さの目安超過(Trial-10から持ち越し、今回さらに悪化傾向を確認)**:
   Theme 2 Bでは Point One 81語・Point Two 73語と、両方ともtolerance
   (25〜70語)を超過した。Theme 1 A/BもPoint Twoが目安超過。hard cap
   ではないため即対応不要だが、傾向が3テーマ中で継続している。

## 25. Production変更なし確認

`er003_v1_n3_01_articles_generate.py`を含む既存ファイルへの変更は一切
行っていない。新Validator・新Fact Checker・新LLM QAの追加なし。Point
Overlap閾値(0.40)・Point-only regeneration無効化措置(ER-008-N8-FINAL-
QA-HARDENING-21)・severityルールの変更なし。Topic Master
(`POOL_TOPIC_MASTER.md`・`topic_package_*.py`)への追加なし。Reference
DigestはProduction routingへ新規登録せず、既存の`B1_WRITER`承認済み
contractを再利用しただけ。`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`の
いずれにも到達していない。SSOT(`DECISION_LOG.md`/`OPEN_ITEMS.md`/
`CURRENT_SPEC.md`)は本Trialでは変更していない(反映要否はFable/ユーザーが
後で判断)。

## 26. 次にユーザーが判断すべき事項

- §24の4論点(新Trade-off対応方針・Reference Digest追加検証要否・Ledger
  自動化緊急性・Point長さ目安見直し要否)。
- Theme 2 Aが`NG_REVIEW_REQUIRED`のままである点について、Human Reviewの
  実施(Point Twoの手動修正案の検討)をユーザー側で行うか、そのまま
  不採用記事として扱うか。
- 3テーマ横断でEngagement原則の再現性が高いことが確認できたため、
  Engagement原則自体のProduction採用検討に進むかはユーザー判断
  (ただし今回もAPPROVED_FOR_PRODUCTIONには到達していない)。

---

## 固定サマリーブロック

今回Status: USER_DECISION_REQUIRED
Theme 1: TREND_READY(Gap Trend)。A=OK(Fact Checker REVIEW_REQUIRED)、B=OK(Fact Checker PASS)
Theme 2: TREND_READY(Gap Trend)。A=NG_REVIEW_REQUIRED(Point構造起因、既存QAが正しく検知)、B=OK(Fact Checker REVIEW_REQUIRED)
Engagement: 3テーマ中3テーマで再現(時系列列挙からGap/Tension構造への改善)。再現性は高い
Reference Digest: 安全(Fact漏洩0件・コスト約¥0.4/記事)。Entertainment性への明確な追加効果は今回も未確定
Cross-topic result: REFERENCE_EFFECT_UNCLEAR(Bが3/3で非劣位という頻度パターンはあるが、原因がテーマごとに異なり因果を断定できない)
Trend overclaim: 4パターン中0件(Ledger Deviation deviations全て0件)
Reference Fact leakage: なし(0件、Theme1・Theme2とも逐語確認済み)
追加cost/article: Theme1 約¥0.44、Theme2 約¥0.39(Trial-10の約¥0.43と同水準)
New QA: 現時点では不要。ただしPoint Two設計に関する新しい構造的難点を発見(Trade-off、§24-1)
Production変更: なし(確認済み)
USER_DECISION_REQUIRED: (1)Gap構造Main StoryにおけるPoint Two設計の新Trade-off対応方針、(2)Reference Digest追加検証要否、(3)Ledger自動化緊急性(4件目の精度課題)、(4)Point長さ目安見直し要否
次に進めてよい工程: ユーザーが上記4論点を判断した後の追加Trial設計、またはTheme 2 AのHuman Review実施(新規Production実装は不可)
