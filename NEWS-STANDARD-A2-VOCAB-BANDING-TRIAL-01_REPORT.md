# NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01 REPORT

管理ID: NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01
性質: Trial。到達上限 VALIDATED。Production変更なし・SSOT変更なし。
実行者: Sonnet(サンドイッチ委任、初回)
成果物ディレクトリ: `er015_output/news_standard_a2_vocab_banding_trial_01/`

## §1 頻度帯の定義と測定方法

`wordfreq.top_n_list("en", 20000)`(既存install再利用、追加installなし)で
英語頻度上位20,000語形の順位表を取得し、各語形を`simple_lemma()`
(規則活用のみの簡易正規化、既存Trial関数を無変更で再利用)でlemma化して
`lemma -> 最小順位`のマップを構築した(`frequency_rank_top20000.json`)。
記事側のcontent word(`extract_content_words()`、機能語除外は既存
`FUNCTION_WORDS`リストを再利用)についても同じlemma化を行い、
`simple_lemma_candidates()`の候補群のいずれかがマップに存在すればその
最小順位を採用して帯を判定した。

帯: A ≤3,000 / B 3,001–5,000 / C 5,001–10,000 / D >10,000
(20,000超の表外語もDに含める、ユーザー指定通り)。

固有名詞別枠: `capitalized_positions()`(既存関数)で、記事内で
「文頭以外の位置で大文字表記」された回数が1回以上ある語を
`proper_noun`バケツへ分離し、帯判定の対象から除外した。

既知の限界(機械ヒューリスティックであり厳密なCEFR判定ではない):
- 不規則活用は`simple_lemma()`非対応。
- 固有名詞判定は「文頭以外での大文字」に依存するため、同一語でも
  文の位置(先頭かどうか)によって判定が変わりうる(§4/§5参照、
  "Reuters"の事例)。
- `extract_content_words()`のトークン化は直立引用符(`'`)のみを
  апострофとして扱う既存正規表現をそのまま使用しており、本文中の
  曲線引用符(`’`)を含む所有格(例: "Meta's")は "Meta" + "s" に
  分割される(既存Trialから継承した既知の挙動、本Trialでは変更禁止)。
  この結果、"s"という1文字のノイズ語がcontent word集計に混入する
  (Meta Advanced/v4双方で1〜2回)。分析結果への影響は軽微
  (該当語がAA帯にaggregate、他の語の順位・帯判定には影響なし)。

## §2 帯別残存語(Sewer v3・Meta Advanced・Meta v4)

異なり語数(distinct) / 延べ語数(token):

| 記事 | A | B | C | D | proper_noun | content word 異なり/延べ |
|---|---|---|---|---|---|---|
| Sewer Standard v3 | 95 / 143 | 10 / 20 | 2 / 2 | 6 / 14 | 0 / 0 | 113 / 179 |
| Meta Advanced Baseline | 101 / 140 | 6 / 6 | 3 / 5 | 3 / 4 | 4 / 19 | 117 / 174 |
| Meta Standard v4 | 87 / 132 | 6 / 6 | 4 / 5 | 3 / 4 | 3 / 18 | 103 / 165 |

Sewer v3のD帯: septic, sewer(s), artery, faraway, wastewater
(専門語[septic/wastewater]・中心比喩[artery]・話題の核[sewer]として
既存Trialで意図的に残存、本Trialでは再生成していない参考値)。

Meta AdvancedのC/D帯: convenient(C), curtain(C, 比喩語), leak(C),
backstage(D, 比喩語), concierges(D, 引用語"human concierges"の一部),
understudy(D, 比喩語)。

Meta v4のC/D帯: curtain(C, 比喩語), convenient(C), paused(C, 新出),
reuters(C, 新出), backstage(D, 比喩語), concierges(D, 引用語),
understudy(D, 比喩語)。

詳細は`vocab_bands_baseline.md`(Sewer v3・Meta Advanced)・
`vocab_bands_evaluate.md`(Meta v4 + 差分)を参照。

## §3 v4 Prompt全文+v3差分

developerはv3と一字も変えていない(機械assert確認済み)。user template内の
v3の次の5行を7行へ置換した。それ以外の本文(段落順・改行含む、比喩語保持行
[Keep the metaphor words...]を含む)は一字も変えていない(機械assertで
確認済み)。

v3の該当5行(置換対象):
```
Use common, everyday words whenever a simpler word can express the same meaning.
Do not keep a difficult word just because it appears in the original article.
Keep a word above A2 level only if replacing it would lose an important fact or meaning (for example, a name, or a technical term with no simple equivalent).
Do not add an explanation for a hard word; make the sentence around it simple instead.
Before you finish, check every difficult word in your draft and replace each non-essential one with simpler English.
```

v4の置換後7行:
```
Use common, everyday words whenever a simpler word can express the same meaning.
Do not keep a difficult word just because it appears in the original article.
Think about how common a word is: very common words are fine; fairly common words may stay if they sound natural; uncommon words should usually be replaced when a clearly simpler natural choice exists; rare words should be replaced unless they are names, essential technical terms, or a key metaphor.
Do not replace a difficult word if the replacement sounds less natural or is not clearly easier. Prefer natural, simple English over forced simplification.
When simplifying vocabulary, prefer a common natural phrase over an awkward one-word replacement.
Do not add an explanation for a hard word; make the sentence around it simple instead.
Before you finish, check every difficult word in your draft. Replace it only if a clearly simpler and natural choice exists.
```

全文: `prompt_standard_v4.txt`、差分・変更意図の詳細: `prompt_diff_v3_v4.md`。

## §4 Meta v4全文(+Advanced全文並置)

全文並置は`comparison_meta_v4.md`(Advanced -> Standard v1(B-1) ->
Standard v4)を参照。Meta v4本文(`b1v4_standard_meta.md`):

> "Hello, I'm AI" — A Human Was Behind the AI Phone Call
>
> Letting AI make phone calls sounds like a helpful future service. A
> person only needs to say what they want. Then AI makes the call for
> them. This was the kind of phone service Meta was building.
>
> The lead role belonged to Muse, Meta's personal AI agent. Meta was
> trying to teach Muse to make calls for people.
>
> But people found something surprising when they looked backstage.
>
> In internal tests, contract workers—not AI—handled some parts of
> calls. Meta called these workers "human concierges."
>
> In other words, the sign said "AI phone service." But sometimes, a
> human handled the call. The stage looked like AI was working alone.
> In fact, a human understudy waited backstage.
>
> This is the most interesting part of the story. You may think an AI
> call is truly impressive. Then you may learn that a human was behind
> the curtain. It is like seeing a piano play by itself. Then you learn
> another performer was hidden inside it.
>
> Of course, there is nothing wrong with people helping. People can do
> parts that AI cannot do well yet. This is a natural way to work.
>
> But phone calls may contain personal information. Meta employees
> worried about privacy. One worry was that call content could leave
> the company. People may think AI handled the conversation alone. If
> contract workers actually listened and answered, people might be
> shocked.
>
> Reuters reviewed internal posts. A Meta executive said the company
> had paused the feature.
>
> With an AI phone service, it may not be enough to ask if it can make
> calls. Who is speaking on the stage? And who is behind the curtain?
> The more convenient the service is, the more it may need to explain
> itself. People may need this before they can truly feel safe
> trusting it.

## §5 明らかに置換可能で残った難語・無理な置換の不自然表現(Sonnet目視)

(a) 明らかに置換可能なのに残った難語: 該当なしと判断。C/D帯の7語は
いずれも (i) 比喩語ホワイトリスト該当(curtain/backstage/understudy、
Promptの"Keep the metaphor words..."行で明示的に保護)、(ii) 引用語の
一部(concierges、"human concierges"というMeta社の用語)、(iii)
話題固有の中核語(convenient — 記事冒頭の"a convenient/helpful
service"という評価軸そのもの)、(iv) 単発の意図的な語選択
(paused/reuters、詳細は(b)参照)であり、Sewer v3で見られたような
「置換すべきなのに理由なく残った難語」は本Trialでは確認できなかった。

(b) 無理な置換による不自然表現: Sewer v3の"installation→putting in"
のような明確な破綻は確認できなかった(v4はMeta記事のみで実行しており、
同一Sewer記事でのv4再生成は行っていないため、Sewer固有の問題が
v4で解消されたかどうかは未検証、§13参照)。一方、Meta v4で以下の
2点を意味のずれとして確認した。
  - "call content could leak outside the company"(Advanced)→
    "call content could leave the company"(v4)。leak(不正・意図しない
    漏えいのニュアンス、頻度帯C)がleave(中立的な「出て行く」)に
    置換され、プライバシー侵害を示す語のニュアンスが弱まっている
    (語の頻度は下がったが、意味の正確さは犠牲になっている)。
  - "the company had put the feature on hold"(Advanced)→
    "the company had paused the feature"(v4)。こちらは自然かつ
    正確な一語置換だが、機械測定では"paused"(順位7166、帯C)が
    idiom "put ... on hold"を構成する語("put"順位209・"hold"順位655、
    いずれも帯A)よりも頻度帯としては「難しい」と判定される。
    直感的な平易さ(自然な一語 > 不自然なイディオム)と頻度順位
    ベースの帯判定が逆転する例であり、頻度帯を機械的な合否基準
    にしないという設計思想(ユーザー指示の「頻度順位だけで機械的に
    書き換えない」)の妥当性を裏付ける事例。
  - 加えて"Reuters"がC帯(順位8719)として新たに検出された理由は
    語彙難易度の変化ではなく、v4で文頭位置("Reuters reviewed
    internal posts.")に移動したことで固有名詞ヒューリスティック
    (文頭以外の大文字表記)が発火しなくなったための誤分類
    (§1の限界参照)。

(c) 比喩語(stage/backstage/lead role/curtain/understudy/piano)の保持:
`structure_map.md`の機械集計で、stage/backstage/lead role/curtain/
understudyの5語すべてがAdvanced/v1/v4で"○"(保持)。pianoは
METAPHOR_WORDS固定リストに含まれていないため機械集計対象外だが、
本文中に"a piano play by itself"としてv4でも保持を目視確認した。

(d) "some parts of the calls"の維持(修正禁止): **維持されていない**。
Advanced「handled some parts of **the** calls」→v4「handled some
parts of calls」(定冠詞"the"が脱落)。加えて、指定範囲外だが関連する
事例として、Advanced「in **some** cases」→v4「**sometimes**」で
scope word "some"がまるごと脱落している(scope_word_counts: some
2→1、機械集計`fact_diff_machine.json`で確認)。もう一点、negation
countが4→2に減少しており("is still **not** good at"→"cannot do
well yet"、"it would **not** be surprising if...shocked"→"people
might be shocked")、Promptの「Keep every fact exactly as it is:
... negations ... exactly as it is」という明示指示に対する逸脱が
2件確認された。数値(numbers)・引用句(quoted_phrases)は完全一致。

## §6 Level指標

| 記事 | words | sentences | avg words/sent | avg syll/word | long-sent率 | subordinator/100w | FK grade |
|---|---|---|---|---|---|---|---|
| Meta Advanced Baseline | 330 | 25 | 13.2 | 1.455 | 0.16 | 4.55 | 6.72 |
| Meta Standard v1 (B-1) | 325 | 26 | 12.5 | 1.443 | 0.154 | 4.31 | 6.31 |
| Meta Standard v4 | 300 | 31 | 9.68 | 1.43 | 0.032 | 2.67 | 5.06 |
| Sewer Standard v3(参考、既存計算値引用・再計算なし) | 331 | 34 | 9.74 | 1.429 | 0.0 | 1.21 | 5.07 |

Meta v4の平均語/文(9.68)・FK grade(5.06)はSewer v3(9.74 / 5.07)と
ほぼ同水準であり、9–11語/文の目標にも収まっている。v3由来の文再構築
指示(Rebuild the sentences...)部分は変更していないため、この点は
語彙帯Promptの効果というよりv3から継承した効果である。

## §7 Story・比喩・Reveal・Ending

`structure_map.md`より: 段落数はAdvanced/v1/v4いずれも10段落で対応。
Reveal(human conciergesがAIの代わりに一部対応していたという発見の
段落構成)は○、Ending logic("Who is speaking on the stage? And who
is behind the curtain?"の結び)は○で維持。比喩語保持は§5(c)の通り。

## §8 Fact drift

`fact_diff_machine.json`(advanced_to_v4)より:
- numbers: 一致(両記事とも数値表現なし、missing/added とも空)。
- proper_nouns(正規表現`\b[A-Z][a-z]+\b`による粗い抽出、文頭語も
  含む既存ヒューリスティックのため実際の固有名詞とは限らない):
  missing=[According, Humans, That]、added=[One, People, This]。
  いずれも文頭の代名詞・接続語であり、実際の人名・組織名の欠落・
  追加ではない(Meta/Muse/Reutersは両記事に共通して存在)。
- quoted_phrases: 完全一致(["AI phone service.", "human
  concierges."])。
- negation_counts: not 4→2(§5(d)で詳述、意味の逸脱として指摘)。
- scope_word_counts: some 2→1、only 3→1(§5(d)で詳述)。

## §9 追加LLM call数・cost・latency・tokens

追加LLM call数: **1**(Meta Standard v4生成のみ、他のstepはLLM call
なし)。

`b1v4_standard_meta.meta.json` / `cost.json`より:
- model_requested = model実値 = `gpt-5.6-luna`(fallback_detected=false)
- effort = high
- retried = false(空出力なし、1回で成功)
- input_tokens = 921 / cached_input_tokens = 0 / output_tokens = 1406
  (reasoning_tokens内数 1034)
- elapsed_seconds = 13.013
- cost_usd = 0.001871 / cost_jpy = 0.2994
- 累計 total_cost_jpy = 0.2994(予算上限¥100に対し十分に内側)

## §10 Fable参考評価

### 10.1 Fable参考評価(Meta v4本文を通読)
- 自然さ: v4は不自然な一語置換(Sewer v3の installation→putting in 型)を起こしていない。"put on hold"→"paused"、"on a person's behalf"→"for people" など自然な置換のみ。文長9.68語/文・FK 5.06でSewer v3と同水準。
- 比喩・Story: lead role / backstage / understudy / curtain / piano をすべて保持し、v1で弱化した "lead role" も "The lead role belonged to Muse" として維持。Reveal・Endingは同位置。
- Fact: 機械diffの「not ×2脱落」「some脱落」は言い換えによるもので、通読では意味は保持されている("it would not be surprising if they were shocked"→"people might be shocked"、"the important question may not be only"→"it may not be enough to ask"、"some parts of the calls"→"some parts of calls"[定冠詞のみ脱落])。事実誤りなし。
- ニュアンスの軽微な弱化2件: (1) "leak outside the company"→"leave the company"(日本語R2「流出」の含意が薄れる)、(2) "According to internal posts reviewed by Reuters, a Meta executive said…"→"Reuters reviewed internal posts. A Meta executive said…"(発言の出典関係が分割で緩む)。いずれもFact driftではなく表現の弱化。
- "some parts of the calls" の意味はBaselineどおり維持(OPEN-177サブ項目のまま、本Trialでは修正していない)。

### 10.2 頻度帯指標について
Meta Advancedはもともと平易で、帯C/Dの異なり語はAdvanced 6→v4 7(固有名詞ヒューリスティックの誤判定"Reuters"と、"paused"のような自然だが順位上は高帯の語を含む)。この記事では頻度帯指標が方針の効果を示せず、指標側の限界(固有名詞判定・自然な語の順位ノイズ)も判明した。v4の「自然さ優先」が Sewer の不自然置換を実際に解消するかは、Sewerでv4を再生成しないと確認できない(本Trialの範囲外)。

## §11 分類

**VALIDATED(部分)**。別Topic(Meta)でも v4方針は Story・比喩・自然さを保ちつつ文長簡略化を再現し、不自然な一語置換を起こさなかった。ただし頻度帯別の語彙削減効果はこの記事では実証されず、Sewerでの不自然置換解消も未検証。Production採用ではない。

## §12 USER_DECISION_REQUIRED

1. 決定的な検証として、Sewer AdvancedからStandard v4を1本生成し(1 call、概算¥0.5)、v3の installation→putting in / collects→gathers / distant→faraway 型が解消するかを確認するか(Fable推奨: 実施。v4の主目的はこの型の抑止であり、Metaでは元々発生していなかった)。
2. ニュアンス弱化(leak→leave、出典関係の分割)を許容するか、v4 Promptに「否定・出典・漏えい等の意味を弱めない」旨の1行を足すか(Fable推奨: 1のSewer結果を見てから判断)。
3. 頻度帯指標の固有名詞判定(文頭位置依存)の改善は測定器側の課題として記録のみ(Open Item候補)。

## §13 未解決

- Sewer記事に対するv4プロンプトの再生成は本Trial範囲外(ユーザー指示
  「まずMeta記事1本で実行」「Variation禁止」に従い実施せず)。従って
  Sewer v3で確認された"installation→putting in"型の不自然置換が
  v4プロンプトで実際に解消されるかどうかは未検証。
- §2の通り、C/D帯(異なり語)はAdvanced 6語→v4 7語とわずかに増加して
  おり、単純な「頻度帯を下げれば残存難語数が減る」という結果には
  なっていない。増加分の主因は(i)固有名詞判定ヒューリスティックの
  文位置依存による誤分類("Reuters")、(ii)idiomから一語への置換で
  頻度順位としては上がる逆転現象("paused")であり、機械集計の
  異なり語数という単一指標だけでは効果を正しく評価できない可能性が
  ある(§5(b)参照)。頻度帯という数値指標と「自然さ」という質的指標
  の間にトレードオフがあることを示す事例として、Fableへの参考情報
  として記録する。
  Open Item候補(事実列挙、判断はしない): 頻度帯の「異なり語数」を
  唯一の定量指標として今後のTrialで使い続けるかどうかは未決。
- §5(d)の通り、"some parts of the calls"の定冠詞脱落、"in some
  cases"→"sometimes"のscope word脱落、2件のnegation脱落が確認された。
  いずれもPromptの明示的なfact保持指示("Keep every fact exactly as
  it is: ... negations ... and words of scope such as 'some' or
  'all'")に対する逸脱であり、語彙帯Prompt(v4)固有の問題というより
  文再構築指示(v3から継承、変更していない部分)との相互作用の可能性
  がある。追加LLM call・新Validatorを伴わない範囲での対処案は本Trial
  では検討していない(範囲外)。
- 一覧外Read/Grep: 用語の裏取りのため
  `grep -o "\bonly\b|\bsome [a-z]*\b"`をAdvanced/v4本文に対して実行し、
  機械集計(`fact_diff_machine.json`)の妥当性を手動確認した(事前指定
  Read一覧の範囲内での確認作業であり、追加ファイルの新規Readは行って
  いない)。

## §14 Sewer v4(ユーザー承認後の追加検証、修正2回目)

§1–§13は本セクション追加にあたり変更していない(既存内容は無変更)。
本セクションはユーザー承認(2026-09-25)により、Sewer Advancedから
Standard v4を1回追加生成し、Metaでは検証できなかった「頻度帯ごとの
扱い分け/不自然な言い換え抑止/難語→別の難語への単なる置換抑止」が
難語の多いSewer記事でも機能するかを確認した結果。

### 14.1 生成条件・cost

- 入力: `er015_output/news_natural_advanced_standard_a2_trial_01/a1_advanced_sewer.md`
  (Sewer Advanced、改変禁止)。sha256実測=
  `7e5aed46d6cb275629e61c7af99bedc0ced9482eb5063ca42305cb883eba1c6d`
  (`sewer_v4_generation_sources.json`に記録。`sources.json`にはこの
  ファイルに対応する期待値エントリが無いため突合対象ではなく実測値の
  記録)。
- v4 Prompt: Meta実行時(修正1回目)に書き込まれた
  `prompt_standard_v4.txt`とsha256一致を確認済み
  (`7bd8d2429b87aea80c4d042177bcc31dd077bb521061f1ba3ca8ebee1a7b792f`、
  一字も変えていない)。DEVELOPER/USER TEMPLATEともMeta用と完全同一の
  Python定数(`DEVELOPER_STD_V4`/`STANDARD_USER_TEMPLATE_V4`)を再利用。
- `a2v4_standard_sewer.meta.json`より: model_requested = model実値 =
  `gpt-5.6-luna`(fallback_detected=false)、effort=high、retried=false
  (空出力なし、1回で成功)、input_tokens=945 / cached_input_tokens=0 /
  output_tokens=4082(reasoning_tokens内数3624)、elapsed_seconds=34.383、
  cost_usd=0.005087 / cost_jpy=0.814。
- 追加LLM call数: **1**(`cost_sewer.json`: additional_llm_call_count=1、
  total_cost_jpy=0.814、budget_jpy=100、within_budget=true)。予算上限
  ¥100に対し十分に内側。Web Search未使用(web_search_used=false)。
- 実行時の作業ミス(記録): 初回コマンド実行時、bashのバックスラッシュ
  解釈により`--out-dir`が誤ったディレクトリ名
  (`er015_outputnews_standard_a2_vocab_banding_trial_01`)に展開され、
  生成物が一時的にそこへ書かれた。直後に正しい出力先
  (`er015_output/news_standard_a2_vocab_banding_trial_01/`)へファイル
  移動(内容の改変なし、sha256で同一性確認済み)し、誤ったディレクトリは
  削除した。API再呼び出しは発生していない(追加call数1のまま)。

### 14.2 Sewer v4全文(+Advanced/v3全文並置)

`comparison_sewer_v3_v4.md`(Advanced→Standard v3→Standard v4の3段階
全文)を参照。

### 14.3 帯別残存語(Sewer Advanced / v3 / v4)

`vocab_bands_sewer_all.json`(帯別測定生データ)/
`vocab_bands_sewer_evaluate.md`(帯表+3段階推移)より:

| 記事 | content word(延べ/異なり) | 帯A | 帯B | 帯C | 帯D |
|---|---|---|---|---|---|
| Sewer Advanced | 178 / 122 | 98 | 10 | 8 | 6 |
| Sewer Standard v3 | 179 / 113 | 95 | 10 | 2 | 6 |
| Sewer Standard v4 | 183 / 120 | 99 | 11 | 3 | 7 |

帯C/D(異なり語)の3段階推移: Advanced 14語 → v3 8語 → v4 10語。
- Advancedのみ(v3・v4いずれにも残らない): distant, divide, inspections,
  installation, invisible, municipalities(=いずれも何らかの形で簡略化
  された語、詳細は§14.4)。
- Advanced/v3/v4いずれも帯C/Dのまま: artery, flush, septic, sewer,
  sewers, surprisingly, wastewater(意図的な比喩・主題語の保持)。
- v4で新たに帯C/Dになった語: faraway(Advanced単独比較上は新規だが、
  実際はv3で既に導入済み。§14.4参照), unseen(Advanced/v3いずれにも
  なく、v4で新規に発生。invisible→hidden[v3]→unseenの逆行、§14.4)。
- v3では帯C/Dだがv4では帯C/Dでない語: (なし)。

### 14.4 語彙遷移表(9語+帯B/C/D全件)

詳細は`vocab_transition_sewer_v4.md`(全文)。要点:

- ユーザー指定3件のうち、**collects→gathers**と**distant→faraway**は
  v4でも一言一句同じ表現のまま再現され、解消されなかった(難語→別の
  難語、v3から変化なし)。
- **installation→put(ting) in**は語選択の型としてはv3と同一(自然な
  置換)。ただしv3の"putting in, checks, and cleaning"(動名詞+名詞+
  動名詞の混在で既存Trialが「やや不自然な句」と指摘)に対し、v4は
  "put in, checked, and cleaned"(過去分詞3つに統一)と文法的な
  自然さは改善されていた。
- 新規発見: **invisible→hidden(v3、良好)→unseen(v4)**。v4は
  Advanced本体(invisible, rank6153)より難しい語(unseen, rank12884)を
  導入しており、v3の改善を後退させた。v4 Promptの
  「明確に簡単で自然な代替がある場合のみ置換する」というself-check
  指示が、この事例では機能しなかった。
- **convenience**(v3は"life easy"へ言い換えて回避、v4はAdvancedのまま
  保持)、**rid**("getting rid of"、v3は"removing"へ簡略化、v4は
  Advanced表現へ後退)でも、v3の改善がv4で失われた。
- **municipalities→towns**(v3は2箇所とも統一)に対し、v4は1回目
  "towns or cities"(原文に無い"cities"を追加)、2回目"local
  governments"と、同一語に2通りの訳語が混在(一貫性の乱れ)。
- 一方、記事の中心比喩(main artery/washing machine)・主題語(septic/
  sewer/sewers/wastewater本文)は全版で一貫して保持された。
- 帯B/C/D全24語(Advanced基準)の集計: そのまま残った14語/自然に
  置換7語/難語→別の難語2語/v3の改善がv4で後退2語(rid, convenience。
  上記4分類のどれにも完全一致しないため別掲)。

### 14.5 Level指標

`level_metrics_sewer.md`より:

| 記事 | words | sentences | avg words/sent | FK grade(heuristic) |
|---|---|---|---|---|
| Sewer Advanced | 354 | 26 | 13.62 | 7.22 |
| Sewer Standard v3 | 331 | 34 | 9.74 | 5.07 |
| Sewer Standard v4 | 354 | 39 | 9.08 | 4.68 |

平均語/文はv3(9.74)→v4(9.08)でさらに短縮(-0.66語)。FK gradeも
5.07→4.68とやや低下。ただしword数はAdvancedと同じ354語までv4で増加
(v3は331語)しており、短い文を多数積み重ねる方向(sentences 34→39)で
簡略化が進んだことが分かる(§14.6の段落数増加と符合)。

### 14.6 Story・比喩・Ending

`structure_map_sewer.md`より:
- 段落数: Advanced 8段落 / v3 8段落 / **v4 14段落**。v4は1文単位の
  改行・短い段落分割が大幅に増えており、v1/v3までの「まとまった段落の
  feature記事」的な体裁から、より箇条書きに近い体裁に変化している。
- 比喩語保持: main artery / washing machineはAdvanced/v3/v4すべてで
  保持され、直喩(like/as)構文も維持(事実文化していない)。
- Reveal("combined septic tanks come in"以降の説明段落)は内容として
  v4でも保持されている(Sonnet目視確認)。機械チェックはv3の逐語表現
  ("small water-treatment"等)との一致を見るため×判定だが、これは
  v3自身がAdvancedの逐語("small water-treatment facilities")を
  既に言い換えていたためのv3・v4共通の既知の弱点であり、v4固有の
  問題ではない。
- Ending: "surprisingly familiar place"という結びは、v4で
  "The future of sewers may arrive in a familiar place. It may be
  surprisingly close—right near us."と2文に分割され、"surprisingly"の
  係り先が"familiar"(意外にも身近だった、という趣旨)から"close"
  (距離的な近さ)へ変化している。結末のニュアンスがわずかに変わって
  おり、Fact drift(事実誤り)ではないが物語的な余韻の変化として記録
  する。

### 14.7 Fact drift

`fact_diff_machine_sewer.json`(advanced_to_v4)より:
- numbers: 増減なし(Advanced/v4とも数値表現なし)。
- proper_nouns(機械ヒューリスティック、文頭大文字語の集合差分に近い):
  Advancedのみ(Because/Installation/Instead/Of/Since/When)、v4のみ
  (Flush/Having/So/Then/To/We/You)。実質的にはいずれも文頭語の検出
  ノイズであり、真の固有名詞の欠落・追加ではない(この記事にはもともと
  地名・組織名等の真の固有名詞は登場しない)。
- negation("not"): Advanced 6 → v4 7(増加、脱落なし)。
- scope word: "some"2/"all"1/"part"1は維持。"only"はAdvanced1→v4 0
  だが、これはv3の時点で既に"not only...but also"構文が失われており
  (v3も"only"0)、v4固有の新規脱落ではない。
- 通読による確認: municipalities→"towns or cities"の1回目の訳で
  "cities"という原文に無い語が加わっている点は、軽微な意味の拡張
  (事実追加とまでは言えないが、厳密には「一言一句の事実保持」からの
  逸脱)として§14.4と合わせて記録する。

### 14.8 Fable最終評価

Fable最終評価(Sewer v4本文を通読、Sonnetの語彙遷移表を確認):
- 主目的「難語→別の難語の置換抑止」は**達成されなかった**。collects→gathers、distant→faraway はv3と同一のまま再現。さらに invisible→hidden(v3、良好)が v4では unseen(rank 12,884、Advancedの invisible より低頻度)へ後退し、「明確に易しく自然な場合のみ置換」の自己点検指示が効いていない直接の反例となった。convenience・getting rid of もv3の改善からAdvanced水準へ後退。
- 改善点は限定的: installation→"put in, checked, and cleaned" は文法が揃い、v3の "putting in, checks, and cleaning" より自然。municipalities は "towns or cities"/"local governments" と平易化されたが訳語が不統一で、"cities" は原文にない軽微な拡張。
- 体裁: 段落8→14、1行1文の改行が多く "Turn on the tap. Flush the toilet." など短文の羅列に近づいた(v4 Promptが禁じる flat list 方向)。音声化では改行は影響しないが、文の流れは v3 より断片的。
- Story・比喩・Reveal: 維持。洗濯機の比喩は「〜とは違う」で論理を保ち、main artery も直喩のまま。Endingは "familiar place" と "surprisingly close" の2文に分割され、重心がやや移動(意味は保持)。
- Fact drift: 実質なし。
- 結論: Meta v4 の良好さは Meta Advanced がもともと平易だったことによるもので、難語の多い Sewer では v4 の頻度帯+自然さ指示は v3 に対して優位を示せず、一部後退した。Prompt文言だけでは語彙制御の再現性が低い(v2→v3→v4を通じた一貫した観察)。

### 14.9 最終分類

**REJECTED(v4語彙設計)**。Story・自然さは維持されたが、v4の目的(頻度帯ごとの扱い分け/不自然置換の抑止/難語→難語置換の抑止)がSewerで再現せず、v3からの後退(invisible→unseen、convenience復帰)も生じた。現時点のStandard A2 Promptの最良候補は v3(VALIDATED)のまま。Production採用はしない。

### 14.10 USER_DECISION_REQUIRED

1. Standard A2 の語彙制御について、次のどれを採るか:
   (a) v3 を当面の Standard Prompt 候補として固定し、語彙のPrompt反復をここで止める(Fable推奨。v2→v4で「Prompt文言だけでは語彙制御の再現性が低い」ことが確認できたため)。
   (b) v5: v3 に「置換の反例(例: collects→gathers、distant→faraway は易しくなっていない)」を数例だけ明示した最小変更で1回だけ再試行(¥1)。
   (c) 生成後に wordfreq の帯判定で難語をフラグし、1回だけ狙い撃ちの修正callを行う軽量な2段構成(これまで禁止していた工程追加に当たるため、方針転換の承認が必要)。
2. 頻度帯の測定基準(effectiveness Trial=top2,000圏外、banding Trial=帯A≤3,000)の統一方針(記録のみ、Open Item候補)。
