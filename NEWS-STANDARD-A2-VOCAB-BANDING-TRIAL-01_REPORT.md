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
`[Fable記入]`

## §11 分類
`[Fable記入]`

## §12 USER_DECISION_REQUIRED
`[Fable記入]`

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
