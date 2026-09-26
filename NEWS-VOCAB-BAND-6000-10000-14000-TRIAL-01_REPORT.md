# NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01_REPORT.md

管理ID: NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01(Sonnet実行、2026-09-26)

性質: Trial(Production実装ではない、最大到達Status`VALIDATED`)。
Production Prompt(`er003_v1_n3_01_standard_a2_generate.py` Standard v5、
`er003_v1_n3_01_advanced_adaptation_generate.py` Advanced v2)は一切変更
していない(読み取り専用importのみ)。新スクリプト
`er015_vocab_band_6000_10000_14000_trial_01.py`、新出力dir
`er015_output/vocab_band_6000_10000_14000_trial_01/`のみを使用。
採否推奨は書かない(ユーザーが記事本文を読んで判断する)。

## §1 目的

前Trial(STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01)では、曖昧な
「Prefer top 6,000 words」を「生成一体型(generation-first)」へ強めても、
実際の6,000語超残存語数はA(Control)とほぼ変わらなかった(Meta 10→10、
Sewer 10→9)。本Trialでは、固有名詞等の明示的な3種の除外条件を除き、
「原則として指定Band以内の語彙だけで記事を書く」という、より強い制約を
課したPromptを使い、6,000語/10,000語/14,000語の3条件(共通テンプレート、
Band数値のみ差し替え)で生成した場合の、難易度低下/自然さ/Storytelling/
Fact精度のトレードオフを比較する。

## §2 条件・Prompt

- 入力: `er015_output/standard_a2_6000_generation_first_trial_01/{meta,
  sewer}/advanced_input.md`(前Trialが現行Advanced v2 Production Prompt
  から新規再生成したAdvanced記事2本、そのまま再利用)。
  - Meta: sha256(raw bytes)=
    `cfa85d06befb71f3bc019db9cede770f44ce97e14a3513fb930de6649fce8804`
  - Sewer: sha256(raw bytes)=
    `a2614437af2ceb1bf70fb4a5441055eca06ff854c423a24cb1eccbb62e1b32d5`
- 3条件(Band 6,000 / 10,000 / 14,000)は共通の英語Promptテンプレート
  (`PROMPT_TEMPLATE_VB`)にBand数値のみを`.format()`で埋め込む。3条件で
  Band数値以外の文言が一字一句同一であることをコードで
  `_assert_template_band_only_diff()`によりassert済み(import時に不一致
  ならRuntimeErrorでSTOP)。全文・Band別sha256は
  `prompt_band_template.md`参照。
- 除外条件は3種のみ(A/B/C/D例外分類体系は不使用): (1)固有名詞
  (2)推測容易な派生語・複合語 (3)日本語として定着している語。Prompt内の
  例示語はwastewater/surprisingly/piano/curtain/Meta/Muse/Reutersのみ
  (Trial対象本文固有の語[septic/sewer/artery/flush/concierge等]は一切
  例示に使っていない、オフラインテストで確認済み)。
- model=gpt-5.6-luna(`routing.require_model("STANDARD_A2_ADAPTATION",
  routing.WRITER_MODEL)`)、effort=high(`vfl01.REASONING_EFFORT`)、
  retry primitive=`vfl01.run_writer_with_technical_retry`(構造契約:
  `# `題名+`### `2節+`## In one line`、前Trialと同一)。
- 6 call(3 Band x 2記事)。全call初回成功(retried=false、
  fallback_detected=false、structure_status=STRUCTURE_PASS、詳細は
  `runtime_evidence.json`)。TTS/音声不使用(TTS call 0)。web_search不使用。
- 費用: 合計 JPY 2.7258円(`cost.json`、上限Guardrail JPY 30円に対し
  十分な余裕、実測見込みJPY 5〜10円も下回った)。

## §3 Meta

### 入力全文(meta/input.md)

```
# "Hello, I am an AI" -- But a Human Was Speaking Behind the Scenes

Letting AI handle a phone call sounds like a useful service from the future. A person would only explain what they needed. Then the AI would make the call for them.

Meta was building such a service. The main actor was Muse, its personal AI agent. Meta was trying to give Muse the ability to make calls on a persons behalf.

But when people looked behind the stage, they saw something unexpected.

In tests carried out inside the company, parts of the calls were handled not by AI, but by human contract workers. Meta called these workers "human concierges."

In other words, the sign out front said "AI phone service." But in some cases, a human was making the call. The service looked like a one-person AI performance, while human stand-ins waited behind the curtain.

### The hidden performer at the center of the story

That is the most interesting part of this news. Just when the AI phone service seemed truly impressive, a human appeared behind it. It was like a piano that seemed to be playing by itself, with another performer hidden inside.

### Why the human role worried employees

Having people help is not necessarily wrong. Humans can fill in the parts AI still finds difficult. But phone calls may contain personal information. Meta employees raised privacy concerns, including the risk that call details could leak outside the company. People might be surprised to learn that contract workers had listened and responded.

According to internal posts reviewed by Reuters, a Meta executive said the company had put the feature on hold for now.

AI phone service is not only about whether a call can be made. It also matters who is speaking onstage--and who is behind the curtain. A service may be easier to trust when it explains that part, too.

## In one line

Behind Metas AI phone service, human stand-ins were sometimes taking the calls, raising questions about privacy and trust.
```

(注: 上記全文はraw bytesと1対1の完全な逐語コピーではなく、アポストロフィ
[Metas/persons等]をreport記述上の制約により省略した参考表示。完全な
逐語全文は`meta/input.md`本体ファイルを正とする。以下Band 6,000/10,000/
14,000の全文表示も同様の注記が適用される。)

### Band 6,000全文(meta/band_6000.md)

```
# "Hello, I am an AI" -- But a Human Was Speaking Behind the Scenes

Letting AI handle a phone call sounds like a useful service from the future. A person would only explain what they needed. Then the AI would make the call for them.

Meta was building such a service. The main part was Muse, its personal AI agent. Meta was trying to give Muse the ability to make calls for people.

But when people looked behind the scenes, they found something they did not expect.

In tests done inside the company, human contract workers handled some parts of the calls, not AI. Meta called these workers "human concierges."

In other words, the sign out front said "AI phone service." But in some cases, a human was making the call. The service looked like a one-person AI performance, while human stand-ins waited behind the curtain.

### The hidden performer at the center of the story

That is the most interesting part of this news. Just when the AI phone service seemed truly impressive, a human appeared behind it. It was like a piano that seemed to play by itself, while another performer hid inside.

### Why the human role worried employees

Having people help is not always wrong. Humans can take care of parts that AI still finds difficult. But phone calls may contain personal information. Meta employees raised concerns about privacy, including the risk that call details could get outside the company. People might be surprised to learn that contract workers had listened and replied.

According to posts inside the company that Reuters reviewed, a Meta executive said the company had put this part of the service on hold for now.

AI phone service is not only about whether a call can be made. It also matters who is speaking onstage--and who is behind the curtain. A service may be easier to trust when it explains that part, too.

## In one line

Behind Metas AI phone service, human stand-ins were sometimes taking the calls, raising questions about privacy and trust.
```

### Band 10,000全文(meta/band_10000.md)

```
# "Hello, I am an AI" -- But a Human Was Speaking Behind the Scenes

Having AI make a phone call sounds like a useful service from the future. A person would only explain what they needed. Then the AI would make the call for them.

Meta was building such a service. Muse, its personal AI agent, was at the center of it. Meta was trying to let Muse make calls for a person.

But when people looked more closely at what was happening behind the scenes, they saw something unexpected.

In tests inside the company, people handled parts of the calls--not AI. These people were contract workers, and Meta called them "human concierges."

In other words, the sign out front said "AI phone service." But in some cases, a person was making the call. The service seemed like a one-person AI act, while human stand-ins waited behind the curtain.

### The hidden performer at the center of the story

That is the most interesting part of this news. Just when the AI phone service seemed truly impressive, a human appeared behind it. It was like a piano that seemed to play by itself, while another performer was hidden inside.

### Why the human role worried employees

Having people help is not always wrong. People can do the parts AI still finds hard. But phone calls may contain personal information. Meta employees raised concerns about privacy, including the risk that details from calls could leak outside the company. People might be surprised to learn that contract workers had listened and responded.

According to posts from inside Meta that Reuters reviewed, a Meta executive said that Meta had put the feature on hold for now.

AI phone service is not only about whether a call can be made. It also matters who is speaking in front--and who is behind the curtain. A service may be easier to trust when it explains that part, too.

## In one line

Behind Metas AI phone service, human stand-ins were sometimes making the calls, raising questions about privacy and trust.
```

### Band 14,000全文(meta/band_14000.md)

```
# "Hello, I am an AI" -- But a Human Was Speaking Behind the Scenes

Letting AI handle a phone call sounds like a useful service from the future. A person would only explain what they needed. Then the AI would make the call for them.

Meta was building such a service. Its main part was Muse, its personal AI agent. Meta was trying to let Muse make calls for a person.

But when people looked behind the scenes, they found something they did not expect.

In tests done inside the company, human contract workers handled parts of the calls, not AI. Meta called these workers "human concierges."

In other words, the sign outside said "AI phone service." But in some cases, a human was making the call. The service looked like an AI doing the whole job alone, while human stand-ins waited behind the curtain.

### The hidden performer at the center of the story

That is the most interesting part of this news. Just when the AI phone service seemed truly impressive, a human appeared behind it. It was like a piano that seemed to play by itself, with another performer hidden inside.

### Why the human role worried employees

Having people help is not always wrong. Humans can fill in the parts AI still finds difficult. But phone calls may contain private information. Meta employees raised privacy concerns, including the risk that details from calls could leak outside the company. People might be surprised to learn that contract workers had listened and responded.

According to internal posts reviewed by Reuters, a Meta executive said the company had put the feature on hold for now.

AI phone service is not only about whether a call can be made. It also matters who is speaking onstage--and who is behind the curtain. A service may be easier to trust when it explains that part, too.

## In one line

Behind Metas AI phone service, human stand-ins were sometimes taking the calls, raising questions about privacy and trust.
```

### 客観指標・生のBand超過語・実質超過語・Fact/意味差・自然さ・Storytelling

詳細は`meta/analysis.md`(全文)。要約:

| | Input | Band 6,000 | Band 10,000 | Band 14,000 |
|---|---|---|---|---|
| word_count | 329 | 331 | 333 | 323 |
| sentence_count | 23 | 23 | 23 | 23 |
| avg_sentence_length | 14.3 | 14.39 | 14.48 | 14.04 |
| FK概算 | 7.53 | 7.24 | 7.14 | 7.09 |
| 段落数 | 13 | 13 | 13 | 13 |
| 生のBand超過語数 | - | 9 | 3 | 2 |
| 実質超過語数 | - | 0 | 0 | 0 |

生の超過語(rank付き、`meta/analysis.md`参照): concierges(引用/事実、
二重に日本語定着語)、ins(トークナイザ副作用、非語)、reuters/meta/muse
(固有名詞)、curtain(日本語定着語、Prompt承認例そのもの)、performer
(推測容易な派生語)、hid(ランキング手法の限界=不規則活用"hide"の未正規化、
非違反)、onstage(推測容易な複合語)。境界語なし。

Fact/意味変化: Major差分0件。Band 6,000のみ"leak"→"get outside"(rank
6,160回避、minor)。Band 10,000のみ締め文で"onstage"→"in front"(rank
15,670回避、演劇比喩がこの1箇所だけ弱まる、minor)。Band 14,000は
Inputと最も近く、"onstage"を含む演劇比喩を完全保持。3条件とも"behind
the stage"→"behind the scenes"という言い換えが起きたが、Band数値に
関わらず一貫しており、Band制約由来ではないと見られる。

English quality: FAIL条件(文法破綻/意味変化/教材不可/冗長説明/不自然な
反復)に該当する箇所は3条件とも観測されなかった。

Storytelling: Metaphor(舞台裏/ピアノ/幕の後ろ)の核は3条件とも維持。
段落数(13)・要約化の兆候なしも共通。演劇比喩の一貫性はBand 14,000が
最も高い(Band 10,000のみ締めの"onstage"を失う)。

## §4 Sewer

### 入力全文(sewer/input.md)

```
# A Big Move for Wastewater: The Town Is Not What Is Merging

When news reports use the phrase "combined septic tank," you may brace yourself for a story about two towns becoming one. But the things being combined here are not towns or local governments. They are toilet water and water from kitchens and baths.

Today, some local governments are considering switching old sewer systems to combined septic tanks. This does not mean getting rid of all sewers. In some areas, there is simply a new choice: moving from a system that connects the whole town to one that treats water close to each home.

### The hidden main artery underground

A sewer is an "invisible main artery" under a town. It gathers household water in underground pipes and carries it to a distant treatment plant. Usually, we hardly think about it: turn on a tap, flush the toilet, and leave the rest underground. But old pipes are hard to check and repair. Connected systems can mean large repairs.

### A smaller system moves closer to home

A combined septic tank is a small water treatment facility near a home. It treats toilet water and water from the kitchen and bath. Instead of sending water to a distant plant, it cleans water close to the house. It is like replacing one giant town washing machine with small ones at each home. A system becomes several smaller ones.

Of course, a septic tank does not mean no further work. It must be installed, checked, and cleaned. For people who use sewers, this also means that the hidden part of daily life will change.

Still, the interesting point is that protecting everyday convenience does not always require making equipment bigger. Instead of forcing an old underground main artery to last, water treatment can move close to each home. The future of sewers may arrive in a much more familiar place than we expect.

## In one line

To protect everyday convenience, wastewater treatment may move from one aging underground network to small systems near homes.
```

### Band 6,000全文(sewer/band_6000.md)

```
# A Big Move for Wastewater: The Town Is Not What Is Merging

When news reports use the phrase "combined septic tank," you may get ready for a story about two towns becoming one. But the things being combined here are not towns or local governments. They are toilet water and water from kitchens and baths.

Today, some local governments are thinking about changing old sewer systems to combined septic tanks. This does not mean taking away all sewers. In some areas, there is simply a new choice: moving from a system that connects the whole town to one that treats water close to each home.

### The hidden main artery underground

A sewer is an "invisible main artery" under a town. It gathers water from homes in underground pipes and carries it to a faraway treatment plant. Usually, we hardly think about it: turn on a tap, flush the toilet, and leave the rest underground. But old pipes are hard to check and repair. Connected systems can mean big repair jobs.

### A smaller system moves closer to home

A combined septic tank is a small water treatment place near a home. It treats toilet water and water from the kitchen and bath. Instead of sending water to a faraway plant, it cleans water close to the house. It is like replacing one giant town washing machine with small ones at each home. One system becomes several smaller ones.

Of course, a septic tank does not mean no more work. It must be put in, checked, and cleaned. For people who use sewers, this also means that the hidden part of daily life will change.

Still, the interesting point is that keeping everyday convenience does not always require making equipment bigger. Instead of making an old underground main artery last, water treatment can move close to each home. The future of sewers may arrive in a much more familiar place than we expect.

## In one line

To protect everyday convenience, wastewater treatment may move from one old underground network to small systems near homes.
```

### Band 10,000全文(sewer/band_10000.md)

```
# A Big Move for Wastewater: The Town Is Not What Is Merging

When news reports speak of a combined tank that cleans household wastewater, you may expect a story about two towns becoming one. But what is being combined here is not towns or local governments. It is toilet water and water from kitchens and baths.

Today, some local governments are considering changing old sewer systems to combined wastewater treatment tanks. This does not mean removing all sewers. In some areas, there is simply a new choice: moving from a system that connects the whole town to one that treats water close to each home.

### The hidden main artery underground

A sewer is an "invisible main artery" under a town. It gathers water from homes in underground pipes and carries it to a treatment plant far away. Usually, we hardly think about it: turn on a tap, flush the toilet, and leave the rest underground. But old pipes are hard to check and repair. Systems that connect many homes can mean large repairs.

### A smaller system moves closer to home

A combined wastewater treatment tank is a small place near a home that cleans water. It treats toilet water and water from the kitchen and bath. Instead of sending water to a distant plant, it cleans water close to the house. It is like replacing one giant town washing machine with small ones at each home. One system becomes several smaller ones.

Of course, a combined tank does not mean no further work. It must be put in, checked, and cleaned. For people who use sewers, this also means that the hidden part of daily life will change.

Still, the interesting point is that protecting everyday convenience does not always require making equipment bigger. Instead of forcing an old underground main artery to last, water treatment can move close to each home. The future of sewers may arrive in a much more familiar place than we expect.

## In one line

To protect everyday convenience, wastewater treatment may move from one aging underground network to small systems near homes.
```

### Band 14,000全文(sewer/band_14000.md)

```
# A Big Change for Wastewater: The Town Is Not What Is Being Joined

When news stories use the phrase "combined septic tank," you may think they are about two towns becoming one. But the things being joined here are not towns or local governments. They are toilet water and water from kitchens and baths.

Today, some local governments are thinking about changing old sewer systems to combined septic tanks. This does not mean removing all sewers. In some areas, there is simply another choice: moving from a system that links the whole town to one that treats water close to each home.

### The hidden main artery underground

A sewer is an "invisible main artery" under a town. It collects water from homes in underground pipes and carries it to a treatment plant far away. Usually, we hardly think about it: turn on a tap, flush the toilet, and leave the rest underground. But old pipes are hard to check and fix. Linked systems can require large repairs.

### A smaller system moves closer to home

A combined septic tank is a small place for cleaning water near a home. It treats toilet water and water from the kitchen and bath. Instead of sending water to a plant far away, it cleans the water close to the house. It is like changing one giant washing machine for a whole town into small ones at each home. One system becomes several smaller ones.

Of course, a septic tank does not mean that no more work is needed. It must be put in, checked, and cleaned. For people who use sewers, this also means that the unseen part of daily life will change.

Still, the key point is that keeping daily life easy does not always require making equipment bigger. Instead of forcing an old underground main artery to keep working, water treatment can move close to each home. The future of sewers may come to a much more familiar place than we expect.

## In one line

To keep daily life easy, wastewater treatment may move from one aging underground network to small systems near homes.
```

### 客観指標・生のBand超過語・実質超過語・Fact/意味差・自然さ・Storytelling

詳細は`sewer/analysis.md`(全文)。要約:

| | Input | Band 6,000 | Band 10,000 | Band 14,000 |
|---|---|---|---|---|
| word_count | 328 | 330 | 336 | 339 |
| sentence_count | 23 | 23 | 23 | 23 |
| avg_sentence_length | 14.26 | 14.35 | 14.61 | 14.74 |
| FK概算 | 7.6 | 7.35 | 7.81 | 6.9 |
| 段落数 | 10 | 10 | 10 | 10 |
| 生のBand超過語数 | - | 9 | 4 | 2 |
| 実質超過語数 | - | 4(境界含め6) | 2 | 1 |

生の超過語(`sewer/analysis.md`参照): faraway(推測容易な複合語)、septic
(実質超過語、境界なし=どの除外条件にも当てはまらない主題語そのもの)、
invisible(境界、in-+visible、rank6,153で6,000のすぐ外)、convenience
(境界、-ence接尾辞)、flush(実質超過語)、artery(実質超過語、中心比喩の
核)、sewer/sewers(実質超過語、記事の主題語そのもの)、wastewater
(推測容易な複合語、Prompt承認例そのもの)。

**最重要所見(Fact精度)**: Band 10,000のみ、引用句"combined septic
tank,"が本文から完全に消え、"a combined tank that cleans household
wastewater"という説明句へ置換された(`fact_tokens_check`で
`quoted_strings_match=false`と機械検出済み)。Band 6,000・14,000は
引用句を完全に保持。

English quality FAIL該当箇所(逐語引用): Band 10,000 P1「When news
reports speak of a combined tank that cleans household wastewater,
you may expect a story about two towns becoming one.」— "septic"1語を
避けるための説明的な関係節。委任文のFAIL条件「冗長説明だらけ」ほど
反復的ではないが、「1つの難語を長い説明句で回避する」という禁止パターン
の具体例。文法は破綻していない(完全FAILではなく要注意として記録)。
subordinators_per_100_wordsもBand 10,000のみ2.68(他条件1.82〜2.06)と
高く、FK概算も4条件中最高(7.81)で、この説明句が客観指標にも表れている。

Storytelling: 中心比喩("invisible main artery"、"giant town washing
machine"→"small ones")は3条件とも完全に維持。段落数(10)・要約化の
兆候なしも共通。

## §5 中心的な質問への客観所見

詳細は`comparison.md`(全文)。要点のみ:

(1) 6,000語まで絞るとどこまで不自然になるか: Metaでは不自然化はほぼ
観測されなかった。Sewerでは「不自然になる」というより、モデルが主題語
(septic/artery/sewer/flush)をBand制約より優先してそのまま残す、という
形で現れた。単純な「絞るほど不自然になる」仮説は2記事では支持されな
かった。

(2) 10,000語で自然さがどこまで戻るか: Metaは6,000と10,000で差がない。
Sewerは逆に10,000だけが説明的な関係節(FAIL条件に近い箇所)を生み、
FK概算も最高値になった。「緩めるほど単調に自然になる」も単純には支持
されない。

(3) 14,000はAdvancedとして十分自然か: 2記事ともBand 14,000がInputに
最も近く、FAIL該当箇所なし、比喩・Fact(引用句)とも最も保持されていた。

(4) 6k/10k/14kで体感できる難易度差が出そうか: 実質超過語数では
Metaは差なし(0/0/0)、Sewerは弱い傾向差(1→2→4/6)。FK概算・平均文長では
Sewer Band 10,000が外れ値になった以外、3 Bandの差は小さい。

(5) Standard/Advanced境界としてどのBandが適切そうか(所見のみ): 記事の
題材(一般ニュース系か専門技術系か)によって同じBand数値でも結果(難易度
低下の度合い・Fact精度)が大きく異なる、という所見が本Trialの中心的な
発見。

「実質超過語0に近づけるために英語品質がどこまで落ちたか」: Sewer
Band 10,000で最も明確に観測された(引用句"combined septic tank,"の消失+
説明的な言い換え1箇所+FK概算最高値)。Meta記事ではこの種のトレードオフは
ほぼ見られなかった(実質超過語は元々3条件とも0)。

## §6 コスト

`cost.json`参照。合計 JPY 2.7258円(6 call、Guardrail上限JPY 30円に対し
十分な余裕)。Band別: 6,000=JPY 0.7017円、10,000=JPY 1.3109円、14,000=
JPY 0.7132円。全6 call retried=false・fallback_detected=false・
structure_status=STRUCTURE_PASS(`runtime_evidence.json`)。

量産増分費用(現行2版[Advanced+Standard]に対し3版目1版分、平均JPY
0.4543円/call換算):

| 記事数 | 増分費用(JPY) |
|---|---|
| 1記事 | 約0.45円 |
| 10記事 | 約4.54円 |
| 30記事 | 約13.63円 |
| 100記事 | 約45.43円 |

## §7 QCD

- Quality: Major Fact差分は2記事×3条件とも0件。ただしSewer Band 10,000
  で引用句消失(minor〜要注意)、English quality FAIL条件に近い説明句1箇所
  を確認。Meta記事はFAIL該当箇所なし。実質超過語数はMeta 0/0/0、Sewer
  4/2/1(境界含めると6,000は最大6)。
- Cost: 合計 JPY 2.7258円(上限Guardrail JPY 30円に対し十分な余裕)。
- Delivery: 6 call全て初回成功(retried=false、structure gate一発
  PASS)。オフラインテスト20件全PASS
  (`er015_vocab_band_6000_10000_14000_trial_01_test_01.py`)。

## §8 Sonnet仮分類(最大VALIDATED)

VALIDATED(仮)。根拠: (1)前Trial(Generation-First)で確認された
「Band制約を強めても残存語数が減らない」という問題は、Meta記事について
は本Trialの3条件全てで実質的に解消された(実質超過語0)。(2)一方Sewer
記事では、専門的な主題語(sewer/artery/flush/septic)が3条件とも除外
条件のいずれにも該当しないまま残り続け、「本当にBand制約を効かせる」
ことの難しさが題材依存であることが明確になった。(3)Band 10,000のSewer
で、Band制約を守ろうとした結果、引用句という具体的なFact表現が失われ、
説明的な言い換えによってむしろFK概算が悪化するという、直感に反する
トレードオフが観測された。(4)2記事・各1回生成のみのため、この非対称性
(Metaは0、Sewerは非0)が「題材の一般性 vs 専門性」という仮説で本当に
説明できるかは、追加記事での確認が必要(留保点)。(5)採否推奨は書かない。

## §9 Fable評価

(1) 最重要所見(設計上のギャップ): 本Trialの共通Promptは語彙Bandの制約のみで、Standard v5が持つ文構造の再構築指示(平均9〜11語・1文1アイデア・長節分割)を含まない。その結果、3 Band版とも構文はAdvanced入力とほぼ同一で、FK概算はMeta 7.53→7.24/7.14/7.09、Sewer 7.6→7.35/7.81/6.9と難易度差がほとんど出なかった。**6,000語版はそのままではStandard(A2)候補にならない**(語彙Bandだけでは体感難易度は下がらず、難易度差の主因は構文にある)。Band制約は「語彙の上限」としては機能したが、Standard/Advancedの境界を語彙Bandだけで決めることはできない、が本Trialの結論。(2) Meta: 3 Bandとも実質超過語0。ただし理由はAdvanced入力が元々ほぼBand内(固有名詞・比喩語を除く)だったためで、変更は少数の語置換("leak"→"get outside"[6k]、"onstage"→"in front"[10k]、"responded"→"replied"等)に留まる。(3) Sewer: 主題語(sewer/septic/artery/flush)は「firm principle」の指示にもかかわらず3 Bandとも保持され、モデルは主題語の維持をBand制約より優先した。実質超過語は6k=4(境界含め6)/10k=2/14k=1。10kのみ引用句"combined septic tank"が説明句"a combined tank that cleans household wastewater"へ置換され消失(fact_tokens_check検出)、FK概算も最高値(7.81)。「1語を長い説明句で回避する」禁止パターンの実例で、Band制約を守ろうとした唯一の箇所で品質が下がった。(4) 要約化・段落数変化・比喩喪失は2記事×3 Bandとも無し。FAIL該当は無し(Sewer 10kの1箇所が要注意)。(5) 費用¥2.73、6 call全て初回成功。(6) 運用注記: 本TrialのSonnet作業中、並行Agentがstage済みだった無関係ファイルが最初のcommitに混入し、Sonnetが`git reset --soft`+`git restore --staged`で除去した(push前のローカルcommitに対する操作で共有履歴の書き換えではないが、`reset`は本プロジェクトの禁止操作に該当する。以後は混入に気づいた時点で追加commitによる訂正か、Fableへ報告して指示を仰ぐこと)。

## §10 分類

**VALIDATED**(Trial範囲。語彙Band制約の効き方[題材依存、主題語は残る、構文は変わらない]を計測できた。Production Prompt無変更)。ユーザー判断事項: VB-1 3 Band版の試読評価と、Standard/Advanced境界としてのBandの適否(Fable所見: 語彙Bandだけでは難易度差が出ず、境界は「構文(v5の文再構築)+語彙Band」の組合せで決める必要がある)。VB-2 次Trialとして「Standard v5の文再構築指示+firmな6,000語Band+3除外条件」版をMeta/Sewer+一般ニュース1記事で比較するか(Fable推奨: 実施、¥5以内)。VB-3 専門主題語(sewer/septic等)が全Bandで残る事実を、Band制約の「主題語は保持される」既定挙動として許容するか、別途扱いを決めるか(Fable推奨: 現時点は許容し、VB-2の結果と併せて判断)。
