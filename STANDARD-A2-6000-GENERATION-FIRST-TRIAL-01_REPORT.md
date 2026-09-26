# STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01_REPORT.md

管理ID: STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01(Sonnet実行、2026-09-26)

性質: Trial(Production実装ではない、最大到達Status`VALIDATED`)。
Production Prompt(`er003_v1_n3_01_standard_a2_generate.py` Standard v5、
`er003_v1_n3_01_advanced_adaptation_generate.py` Advanced v2)は一切変更
していない(読み取り専用importのみ、`generate_standard_a2()`/
`generate_advanced_adaptation()`をそのまま呼び出した)。新スクリプト
`er015_standard_a2_6000_generation_first_trial_01.py`、新出力dir
`er015_output/standard_a2_6000_generation_first_trial_01/`のみを使用。
採否推奨は書かない(ユーザーが記事本文を読んで判断する)。

## §1 目的

前回Trial(VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01)で、難語を個別に事後
置換する方式(A/B/C/D例外判定)が`flush->use`・`septic tank->treatment
tank`・`sewer->underground pipe system`のような意味変化・不自然化を
引き起こすことが判明した。本Trialは、例外分類をさらに複雑化する方向を
止め、代わりに「Standard記事を生成する時点で、文章全体を6,000語中心の
自然なA2英語として書き直す」方式(生成一体型、Generation-First)が機能
するかを、現行Production候補Standard v5 Prompt(Control、以下A)との
A/B比較で検証する。

## §2 条件

- 入力Advanced記事: 委任文が提示した既存artifact(`vocab_abcd_strict_
  exception_trial_01/advanced_{meta,sewer}_before.md`)は、事前調査の
  結果、現行Advanced v2 Production Promptの出力ではないことが判明した
  ため使用せず、日本語R2原文から`generate_advanced_adaptation()`を直接
  呼び出して新規に再生成した(詳細は`comparison.md`「入力の由来」節、
  および本ファイル末尾に転記)。
- A(Control): 現行Production候補Standard A2 v5 Prompt
  (`STANDARD_A2_PROMPT_V5`、一字一句無変更)を`generate_standard_a2()`
  で直接呼び出し。
- B(Trial): Aと同じDEVELOPER・同じ構造契約・同じmodel(gpt-5.6-luna)・
  同じeffort(high)・同じretry primitive(`run_writer_with_technical_
  retry`)だが、語彙段落のみを「生成一体型」指示(GEN_FIRST_PROMPT_V1)に
  差し替えた。構築方法はSTANDARD_A2_PROMPT_V5から語彙段落の逐語部分
  文字列をstr.replace()した(それ以外は完全に同一であることをオフライン
  テストで保証、置換元テキストが変わっていた場合はimport時にRuntimeError
  でSTOPする)。A/Bとも「各語をA/B/C/Dへ分類させる」指示・候補語リスト・
  分類JSON出力要求は一切含まない。
- 6 call(Advanced regen: Meta/Sewer各1回 + Standard A/B: Meta/Sewer各
  2回)。model=gpt-5.6-luna、reasoning effort=high、previous_response_id
  なし、web_searchなし。全call初回成功(retried=false、fallback_
  detected=false、structure_status=STRUCTURE_PASS、詳細は
  `runtime_evidence.json`)。TTS/音声は使用していない(TTS call 0)。
- 費用: 合計 JPY 3.09円(`cost.json`、上限Guardrail JPY 40円に対し十分
  な余裕)。

## §3 Meta

### Advanced入力全文(`meta/advanced_input.md`、日本語原文からの新規再生成)

```
# "Hello, I'm an AI" -- But a Human Was Speaking Behind the Scenes

Letting AI handle a phone call sounds like a useful service from the future. A person would only explain what they needed. Then the AI would make the call for them.

Meta was building such a service. The main actor was Muse, its personal AI agent. Meta was trying to give Muse the ability to make calls on a person's behalf.

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

Behind Meta's AI phone service, human stand-ins were sometimes taking the calls, raising questions about privacy and trust.
```

### A(Control v5)全文(`meta/a_v5.md`)

```
# "Hello, I'm an AI" -- But a Human Spoke Behind the Scenes

Letting AI handle a phone call sounds useful and futuristic. A person would explain only what they needed. Then AI would make the call for them.

Meta was building this kind of service. Its main actor was Muse, a personal AI agent. Meta wanted Muse to make calls for people.

But people who looked behind the stage saw something unexpected.

In company tests, humans handled parts of the calls, not AI. These people were contract workers. Meta called them "human concierges."

In other words, the sign outside said "AI phone service." But sometimes, a human made the call. The service looked like a solo AI show. Yet human stand-ins waited behind the curtain.

### The hidden performer at the center of the story

That is the most interesting part of this news. The AI phone service seemed truly impressive. Then a human appeared behind it. It was like a piano playing alone. Another performer was hidden inside.

### Why the human role worried employees

Having people help is not always wrong. Humans can do what AI still finds difficult. But phone calls may include personal information. Meta employees worried about privacy. They also worried that call details could leave the company. People might be surprised to learn this. Contract workers had listened and answered.

Reuters reviewed posts inside the company. In them, a Meta executive said the company had paused the feature for now.

AI phone service is not only about making a call. It also matters who is speaking onstage. And who is behind the curtain. A service may be easier to trust when it explains that, too.

## In one line

Behind Meta's AI phone service, human stand-ins sometimes took calls. This raised questions about privacy and trust.
```

### B(Gen-First)全文(`meta/b_gen_first.md`)

```
# "Hello, I'm an AI" -- But a Human Was Speaking Behind the Scenes

Letting AI handle a phone call sounds like a useful service from the future. A person would only explain what they needed. Then the AI would make the call for them.

Meta was building this kind of service. Muse was the main actor. It was Meta's personal AI agent. Meta was trying to let Muse make calls for people.

But when people looked behind the scenes, they found something surprising.

In tests inside the company, contract workers handled parts of the calls. The AI did not handle those parts. Meta called these workers "human concierges."

In other words, the sign outside said "AI phone service." But in some cases, a human made the call. The service looked like a one-person AI performance. At the same time, human stand-ins waited behind the curtain.

### The hidden performer at the center of the story

That is the most interesting part of this news. Just when the service seemed truly impressive, a human appeared behind it. It was like a piano that seemed to play by itself. Another performer was hidden inside.

### Why the human role worried employees

It is not always wrong to have people help. Humans can do parts that AI still finds difficult. But phone calls may contain personal information.

Meta employees worried about privacy. They worried that call details could leak outside the company. People might be surprised that contract workers had listened and responded.

Reuters reviewed posts from inside Meta. In those posts, a Meta executive said the company had paused the feature for now.

AI phone service is not only about whether a call can be made. It also matters who is speaking onstage--and who is behind the curtain. A service may be easier to trust when it explains that part, too.

## In one line

Behind Meta's AI phone service, human stand-ins sometimes took the calls. This raised questions about privacy and trust.
```

### 客観指標・残存語・Fact/意味差

詳細は`meta/analysis.md`(全文)。要約:

| | Advanced | A | B |
|---|---|---|---|
| word_count | 329 | 290 | 321 |
| sentence_count | 23 | 32 | 30 |
| avg_sentence_length | 14.3 | 9.06 | 10.7 |
| FK概算 | 7.53 | 5.77 | 5.79 |
| 段落数 | 13 | 13 | 14(内容欠落なし、1段落分割) |
| 6,000超残存語数 | 9 | 10 | 10 |

残存語は両方式ともconcierges(Metaの実際の呼称)/Reuters・Meta・Muse
(固有名詞)/curtain・performer・onstage(比喩維持語)が中心で、「不要な
難語」は観測されなかった(トークナイザ副作用"ins"[stand-insの分割]を
除く)。fact_tokens_check機械判定はA/BともFalseだが、目視確認の結果
Reutersの文頭移動によるヒューリスティックの既知の限界であり、Major
Fact差分は0件。English qualityではB P9(ダッシュ構造維持)がAより自然
だった一方、B P3で"stage"->"scenes"という比喩語のvariationが見られた。

## §4 Sewer

### Advanced入力全文(`sewer/advanced_input.md`、日本語原文からの新規再生成)

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

### A(Control v5)全文(`sewer/a_v5.md`)

```
# A Big Move for Wastewater: The Town Is Not What Is Merging

When news reports say "combined septic tank," you may expect two towns to become one. But the things joining here are not towns or local governments. They are toilet water and water from kitchens and baths.

Today, some local governments are thinking about replacing old sewer systems with combined septic tanks. This does not mean removing every sewer. In some areas, people now have another choice. They can move from one town-wide system to systems that treat water near each home.

### The hidden main artery underground

A sewer is an "invisible main artery" beneath a town. It collects water from homes in underground pipes. Then it carries that water to a treatment plant far away. Usually, we hardly notice it. We turn on a tap, flush the toilet, and leave the rest underground. But old pipes are difficult to inspect and fix. Connected systems can require very large repairs.

### A smaller system moves closer to home

A combined septic tank is a small water treatment plant near a home. It treats toilet water and water from the kitchen and bath. It cleans the water close to the house. It does not send the water to a faraway plant. This is like replacing one giant town washing machine with small ones in each home. One system becomes several smaller systems.

Of course, a septic tank does not mean the work is over. Workers must install, check, and clean it. For people who use sewers, this also changes a hidden part of daily life.

Still, the interesting point is this. Protecting daily convenience does not always mean making equipment bigger. Instead of making an old underground main artery last, water treatment can move close to each home. The future of sewers may come to a much more familiar place than we expect.

## In one line

To protect daily convenience, wastewater treatment may move from one old underground network to small systems near homes.
```

### B(Gen-First)全文(`sewer/b_gen_first.md`)

```
# A Big Change for Wastewater: The Town Is Not Joining

When news reports say "combined septic tank," you may expect a story about two towns becoming one. But the things joined here are not towns or local governments. They are toilet water and water from kitchens and baths.

Today, some local governments are thinking about changing old sewer systems to combined septic tanks. This does not mean removing all sewers. In some places, there is simply a new choice. A town can move from one system for the whole town to one that treats water near each home.

### The hidden main artery underground

A sewer is an "invisible main artery" under a town. It collects water from homes in underground pipes. Then it takes the water to a faraway treatment plant. Usually, we hardly think about it. We turn on a tap, flush the toilet, and leave the rest underground. But old pipes are hard to check and fix. Systems with many connections can need big repairs.

### A smaller system moves closer to home

A combined septic tank is a small place that treats water near a home. It treats toilet water and water from the kitchen and bath. Instead of sending water to a faraway plant, it cleans water near the house. It is like replacing one giant town washing machine with small ones in each home. One system becomes several smaller ones.

Of course, a septic tank still needs more work. It must be put in, checked, and cleaned. For people who use sewers, this also means that a hidden part of daily life will change.

The interesting point is simple: daily convenience does not always need bigger equipment. Instead of making an old underground main artery last, water treatment can move close to each home. The future of sewers may come to a much more familiar place than we expect.

## In one line

To protect daily convenience, wastewater treatment may move from one old underground network to small systems near homes.
```

### 客観指標・残存語・Fact/意味差

詳細は`sewer/analysis.md`(全文)。要約:

| | Advanced | A | B |
|---|---|---|---|
| word_count | 328 | 322 | 324 |
| sentence_count | 23 | 28 | 26 |
| avg_sentence_length | 14.26 | 11.5 | 12.46 |
| FK概算 | 7.6 | 6.3 | 6.31 |
| 段落数 | 10 | 10 | 10 |
| 6,000超残存語数 | 9 | 10 | 9 |

**最重要所見**: 前回Trial(VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01)で
`septic->treatment`・`flush->use`・`sewer->underground pipe system`
という意味変化を起こした語(septic/flush/artery/sewer/sewers)は、本
TrialのA・Bどちらの方式でも一切変更されなかった。`fact_tokens_check`
(数字・引用符内フレーズ・固有名詞候補)はA/Bとも`overall_fact_tokens_
match = True`(Advancedと完全一致)。生成一体型(B)固有の効果例として、
"installed"->"put in"(P5)・"inspect"->"check"(P3)という自然な平易語
言い換えが観測された。一方Bでは逆接"Still,"の省略(P6)という軽微な結束性
の変化も観測された。

## §5 総合客観比較

詳細は`comparison.md`(全文)。要点:

1. 前回Trialで問題になった意味変化型の事後置換は、本TrialのA・Bどちら
   でも発生しなかった(Sewerのfact_tokens_check完全一致で確認)。これは
   Bに固有の効果ではなく、現行Standard v5 Prompt自体の歯止め
   ("Do not force a replacement if it makes the sentence less natural
   or changes the meaning.")がこの2記事に対しては機能していたことを
   示す観測でもある。
2. 6,000超残存語数はMeta(10,10で同数)・Sewer(10,9でBが1語少ない)。
   差は僅少で、いずれも「不要な難語」ではなく固有名詞・主題語・Metaphor
   維持語が大半を占めた。
3. English qualityの具体的な差分(Meta P9のダッシュ構造維持、Sewer P5の
   "put in"言い換え)ではBがやや自然な例が見られた一方、Meta P3の
   比喩語variation、Sewer P6の逆接省略というBの軽微なマイナス面も観測
   された。
4. Storytelling(段落数・中心比喩の保持)はA/Bとも、両記事で維持されて
   いた。要約化の兆候は観測されなかった。
5. 6 call全てretried=false・fallback_detected=false・
   structure_status=STRUCTURE_PASS(`runtime_evidence.json`)。

## §6 QCD

- Quality: 上記の通り、Major Fact差分0件・意味変化型の事後置換0件(A/B
  とも)。English quality/Storytellingの差は僅少かつ両方向に存在(Bが
  優れる例・Aが優れる例が両方観測された)。
- Cost: 合計 JPY 3.09円(6 call、上限Guardrail JPY 40円に対し十分な
  余裕、`cost.json`)。
- Delivery: 6 call全て初回成功(retried=false、structure gate一発
  PASS)。オフラインテスト14件全PASS
  (`er015_standard_a2_6000_generation_first_trial_01_test_01.py`)。

## §7 Sonnet仮分類(最大VALIDATED)

**VALIDATED**(仮)。根拠: (1)本Trialの2記事では、A(現行Control v5)も
B(Gen-First)も、前回Trialで問題になった意味変化型の事後置換を発生させ
なかった。(2)Bに固有の効果(生成一体型による自然な平易語言い換え)は
Sewer P5"put in"/P3"check"の2箇所で明確に観測された。(3)一方で、Bが
Aより明確に優れているという強い客観的差(残存語数・Fact保持・FK概算は
ほぼ同水準)は、この2記事だけでは確認できなかった。(4)Meta記事はもと
もと難語が少なく、比較材料としての判別力が低かった(留保点)。(5)本
Trialの結果は「Bが機能しないことの反証にはならないが、Aに対する明確な
優位性の実証にも至っていない」という中間的な結果であり、Fable/ユーザー
による追加判断(記事本文の目視評価、他記事での追試の要否)を要する。

## §8 Fable評価

(空欄、Fable記入待ち)

## §9 分類

(空欄、Fable記入待ち)

## 付録: 入力の由来の詳細記録(委任文からの逸脱点)

委任文は`er015_output/vocab_abcd_strict_exception_trial_01/advanced_
meta_before.md` / `advanced_sewer_before.md`を入力候補として提示し、
「これがAdvanced v2 Production Prompt出力であることを...確認し、
path+sha256を記録。異なる場合は正しいAdvanced本文を特定して使う」と
指示していた。事前調査の結果は以下の通り(詳細根拠は`comparison.md`
「入力の由来」節に転記済み):

1. `advanced_sewer_before.md`の実体(`er015_output/news_natural_
   advanced_standard_a2_trial_01/a1_advanced_sewer.md`)は、現行
   Advanced v2 Production Prompt(PROCESS_LABEL=NATURAL_ENGLISH_
   ADAPTATION、語彙ルールv2込み)ではなく、その前身のTrial
   (NEWS-JA-TO-EN-ADAPTATION-TRIAL-01 arm3「Natural English」、Sewer
   固有のpreserve bullet文言)で生成されたものだった。
   (`er015_output/news_natural_advanced_standard_a2_trial_01/
   prompt_advanced_a1.txt`の文言と、Production module内
   `ADVANCED_GENERAL_PRESERVE_BULLETS`[記事非依存の一般形]の文言を
   比較して確認)。
2. `advanced_meta_before.md`の実体(`er012_output/e_family_two_level_
   wiring_01/meta/b1b/article.md`)は、`er012_e_family_entertainment_
   two_level_runner_01.py`経由でAdvanced v2 Production関数
   (`adv_gen.generate_advanced_adaptation`)を直接呼び出して生成された
   点は正しい(コード上の呼び出しチェーンで確認)。ただし生成コミット
   (`0e028301`、NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01、
   2026-09-25)は、語彙ルールv2をProductionへ組み込んだコミット
   (`7c93d146`、ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01)より**前**
   であり(`git log --oneline -- er003_v1_n3_01_advanced_adaptation_
   generate.py`で確認)、現行(語彙ルールv2込み)のAdvanced v2
   Production Promptの出力ではなかった。

このため、Meta/Sewerとも「現行Advanced v2 Production Promptの出力」
としての整合性を持たせるため、両記事を同日・同モジュールで新規に
再生成した(日本語原文・Fact変更なし、Production module変更なし、
読み取り専用importのみ)。

日本語R2原文(APPROVED_FOR_PRODUCTION、配線未完了、Fact変更なし):
- Meta: `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/
  ai_phone_revision2.md`
  - sha256(text-mode LF正規化、Pythonの`open(path, encoding="utf-8")`
    で読んだ場合。er012ランナーの`sha256_text()`と同じ正規化方式)=
    `a5d77646cf162974ab53e196da6ba8bc29a8e35172294336a9d12ba777c1cb81`
    (`er012_output/e_family_two_level_wiring_01/meta/entry_point.json`
    の`ja_article_sha256`と一致することを確認済み)
  - sha256(raw bytes、CRLF含む)=
    `474c2a1669b6f90f835d3901cbe6b4fd80f556edf440f0c610fb3589767b1a48`
- Sewer: `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/
  sewer_revision2.md`
  - sha256(raw bytes、CRLF含む)=
    `a7fa4fd7dcd02b5570521eff361153eef24885de7ec79edeb518740386040769`
    (`er015_output/news_natural_advanced_standard_a2_trial_01/
    sources.json`の`sewer_ja_r2.sha256`と一致することを確認済み)

再生成した新Advanced本文のresponse_id・sha256は
`advanced_regeneration_provenance.json`に記録済み(全calls
`retried=false`・`structure_status=STRUCTURE_PASS`)。
