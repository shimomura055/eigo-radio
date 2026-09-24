# NEWS-JA-TO-EN-ADAPTATION-TRIAL-01 REPORT

管理ID: `NEWS-JA-TO-EN-ADAPTATION-TRIAL-01`
日付: 2026-09-24
性質: Trial(Production実装ではない、到達上限`VALIDATED`、最終品質判断はユーザー)
Artifact directory: `er015_output/news_ja_to_en_adaptation_trial_01/`
Script: `er015_news_ja_to_en_adaptation_trial_01.py`

## §1 日本語R2全文(入力、逐語再利用)

Source: `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/ai_phone_revision2.md`
sha256: `474c2a1669b6f90f835d3901cbe6b4fd80f556edf440f0c610fb3589767b1a48`
(元artifact `er015_output/news_iterative_entertainment_trial_02/A_revision2.md` とsha256完全一致を確認)

```
「もしもし、AIです」――その声の裏で、人間が代役を務めていた

AIに電話を任せる。いかにも未来の便利なサービスです。人間は用件を伝えるだけ。あとはAIが電話をしてくれる。そんな電話の舞台が、Metaで作られていました。

主役は、個人向けAIエージェント「Muse」です。MetaはMuseに、電話の代行機能を持たせようとしていました。

ところが、舞台裏をのぞいてみると、少し意外な光景がありました。

社内で行われた試験では、通話の一部をAIではなく、人間の契約スタッフが担当していたのです。Metaはこの役割を「人間コンシェルジュ」と呼んでいました。

つまり、表に出ている看板は「AI電話代行」。でも、その一部では人間が電話を担当していた。AIがひとりで演じているように見える舞台に、実は人間の代役が控えていたわけです。

ここが、このニュースのいちばん面白いところです。AIの電話が本当にすごいのかと思ったら、舞台裏には人間がいる。まるで、ひとりで演奏しているように見えたピアノの中に、別の演奏者が隠れていたような話です。

もちろん、人間が手伝うこと自体は悪いことではありません。AIがまだ苦手な部分を、人間が補う。考え方としては自然です。

ただし、電話には個人的な情報が含まれることがあります。Metaの従業員からは、通話内容が外部に流出するなど、プライバシーへの懸念が出ました。AIに任せたつもりの会話を、実際には契約スタッフが聞いて対応していたと知れば、驚く人がいても不思議ではありません。

Reutersが確認した社内投稿によると、Metaの幹部は、この機能をいったん取りやめたと説明しています。

AI電話代行で大事なのは、電話をかけられるかだけではなさそうです。舞台の上で誰が話しているのか。そして、幕の後ろに誰がいるのか。便利なサービスほど、その説明まで含めて初めて「安心して任せられる」のかもしれません。
```

## §2〜§4 各Arm Prompt全文(Fable固定・3 arm共通developer+共通制約ブロック+arm別ブロック、末尾に[Japanese article]+日本語R2全文)

developer(3 arm共通、124字):
```
You are an editor who adapts finished Japanese feature articles into natural English for listeners who are learning English.
```

共通制約ブロック(3 arm共通、userの先頭):
```
Adapt the Japanese article below into English.

Do not rewrite the article from scratch. Do not add new ideas, claims, background, general observations, examples, or facts that are not in the Japanese article. Preserve the Japanese article's editorial angle, structure, and sense of surprise:
- the opening expectation of a convenient "AI makes the phone call" future;
- the reversal that a human was actually working behind the scenes;
- the framing of lead role / backstage / understudy;
- the theme fixed on "there was a human behind the AI phone call";
- privacy treated as necessary later information, not as the main theme;
- the ending that returns to the image of the stage and what is behind the curtain.
Keep every fact exactly as in the Japanese article. Use short, simple English that a learner could understand by listening once.

Output only the English title and the English body.
```

Arm 1(Faithful)追加ブロック:
```
Adaptation level: FAITHFUL.
Keep the same paragraph order, the same order of information, the same metaphors, and the same ending. Follow the Japanese sentence by sentence as closely as natural English allows. Change wording only where a literal rendering would be clearly unnatural in English. Do not merge, split, or reorder paragraphs.
```

Arm 2(Balanced)追加ブロック:
```
Adaptation level: BALANCED.
Keep the editorial angle, the story structure, the metaphors, the selection of information, and the logic of the ending exactly as in the Japanese. Within that, you may reconstruct sentences, adjust paragraph rhythm, and avoid repetition so that the piece reads as if it had been written in English. Do not change what makes the piece interesting.
```

Arm 3(Natural)追加ブロック:
```
Adaptation level: NATURAL ENGLISH.
Make the piece read like a natural English news feature. Keep the central metaphor, the theme, the facts, the selection of information, and the conclusion. You may reorder, merge, or reshape paragraphs, and adjust the wording of metaphors where English needs it. Still add nothing that is not in the Japanese article.
```

末尾(3 arm共通): `[Japanese article]` + 日本語R2全文(タイトル行を含む逐語、§1と同一)。

Prompt文字数(developer+user、`api_meta.json`の`prompt_developer_char_count`/`prompt_user_char_count`より):
- Arm1: developer 124字 / user 3599字(user.txtファイルバイト数。うち共通制約+arm別ブロック+日本語R2全文)
- Arm2: developer 124字 / user 3636字
- Arm3: developer 124字 / user 3613字

各arm実ファイル: `er015_output/news_ja_to_en_adaptation_trial_01/arms/{arm1,arm2,arm3}/prompt_developer.txt`、`prompt_user.txt`

## §5〜§7 各Arm出力全文・タイトル・語数・段落数

### Arm 1 (Faithful) — Title: "Hello, I'm AI" — A Human Was Acting as a Stand-In Behind the Voice
語数360 / 段落数10 / 文字数2005

```
“Hello, I’m AI” — A Human Was Acting as a Stand-In Behind the Voice

Let AI handle your phone calls. It sounds like a convenient service from the future. People only have to say what they need. Then AI makes the call for them. A phone-call stage like this was being built at Meta.

The lead role was Muse, a personal AI agent for individuals. Meta was trying to give Muse the ability to make calls on people’s behalf.

But when we looked behind the stage, we found a slightly surprising scene.

In tests held inside the company, human contract staff handled some of the calls instead of AI. Meta called this role the “human concierge.”

In other words, the sign out front said, “AI phone service.” But in some cases, a human was making the call. On a stage that looked as if AI were performing alone, a human understudy was actually waiting backstage.

This is the most interesting part of the news. We may think AI phone calls are truly amazing, but there is a human backstage. It is like a piano that seems to be playing by itself, while another performer is hidden inside.

Of course, there is nothing wrong with humans helping. Humans can fill in the parts that AI is still not good at. As an idea, that is natural.

However, phone calls can contain personal information. Meta employees raised privacy concerns, such as the possibility that call content could leak outside the company. If people learned that a conversation they thought they had left to AI was actually heard and handled by contract staff, it would not be surprising if they were shocked.

According to internal posts reviewed by Reuters, a Meta executive explained that the company had put this feature on hold for the time being.

With an AI phone service, the important question may not be only whether it can make a call. Who is speaking on the stage? And who is behind the curtain? The more convenient the service, the more it may need to explain what is behind the curtain before people can truly feel safe leaving things to it.
```

### Arm 2 (Balanced, 本命候補) — Title: "Hello, I'm AI" — A Human Was the Understudy Behind the Voice
語数356 / 段落数10 / 文字数2003

```
“Hello, I’m AI” — A Human Was the Understudy Behind the Voice

Letting AI handle your phone calls sounds like a useful service from the future. You only tell it what you need. Then AI makes the call for you. At Meta, a phone service built around this idea was being developed.

The lead role was played by Muse, Meta’s personal AI agent. Meta was trying to give Muse a feature that would make calls on a user’s behalf.

But when we looked backstage, we found something unexpected.

In an internal test, some parts of the calls were handled not by AI, but by human contract workers. Meta called this role a “human concierge.”

In other words, the sign out front said “AI phone service.” But for some calls, a human was actually making the call. It looked as if AI were performing alone on stage. In fact, a human understudy was waiting backstage.

That is the most interesting part of this news. You might think the AI phone service was truly impressive, only to find a human behind the curtain. It was like seeing a piano play by itself, then discovering another musician hidden inside it.

Of course, there is nothing wrong with humans helping. People can fill in the areas where AI is still weak. That idea makes sense.

But phone calls can include personal information. Meta employees raised privacy concerns, such as the possibility that the contents of calls could leak outside the company. If people learned that contract workers had actually listened to and handled conversations they thought they had left to AI, it would not be surprising if they were shocked.

According to internal posts reviewed by Reuters, a Meta executive said the company had put the feature on hold for the time being.

With an AI phone service, the important question may not be only whether it can make a call. Who is speaking on the stage? And who is behind the curtain? The more convenient a service is, the more it may need to explain what is happening behind the scenes before people can safely leave it in charge.
```

### Arm 3 (Natural English) — Title: "Hello, I'm AI" — A Human Was Behind the AI Phone Call
語数338 / 段落数10 / 文字数1937

```
“Hello, I’m AI” — A Human Was Behind the AI Phone Call

Letting AI make phone calls sounds like a convenient service from the future. A person only needs to explain what they want. Then AI makes the call. That was the kind of phone service Meta was building.

The lead role was Muse, Meta’s personal AI agent. Meta was trying to give Muse the ability to make calls on a person’s behalf.

But when people looked backstage, they found something unexpected.

In internal tests, contract workers—not AI—handled some parts of the calls. Meta called these workers “human concierges.”

In other words, the sign out front said “AI phone service.” But in some cases, a human was handling the call. The stage looked as if AI were performing alone. In fact, a human understudy was waiting backstage.

That is the most interesting part of this story. You may think an AI phone call is truly impressive, only to find a human behind the curtain. It is like seeing a piano that seems to be playing by itself, then learning that another performer was hidden inside it.

Of course, there is nothing wrong with people helping. Humans can fill in the parts that AI is still not good at. That is a natural approach.

But phone calls can contain personal information. Meta employees raised privacy concerns, including the possibility that call content could leak outside the company. If people learned that contract workers had actually listened and responded to a conversation they thought they had left to AI, it would not be surprising if they were shocked.

According to internal posts reviewed by Reuters, a Meta executive said the company had put the feature on hold.

With an AI phone service, the important question may not be only whether it can make a call. Who is speaking on the stage? And who is behind the curtain? The more convenient the service, the more it may need to explain what is happening before people can truly feel safe trusting it.
```

## §8 構造対応・未対応文(機械観測、判定はFable)

`structure_map.json`: 日本語R2の10段落それぞれに主要名詞・見立てを英訳したアンカーキーワード集合を事前設定し、各Armの英語段落における出現数から最尤対応段落を機械的に推定(全arm、段落数は日本語R2・英語出力とも10段落で一致)。

Arm1/Arm2/Arm3すべてで、ja_para_1〜ja_para_10のうち9個が en段落index 0〜9へほぼ単調増加(paragraph i → paragraph i)で対応し、段落順序の入れ替えは観測されなかった。唯一の例外はArm1のja_para_3(「舞台裏をのぞくと意外な光景」)がen段落index 9(最終段落、hits=2)に最大一致した点だが、これは日本語原文が意図的に終盤で「舞台の上・幕の後ろ」の比喩へ戻る設計(ユーザー指示の必須維持項目)のため、backstage/curtainという同一アンカー語が第3段落と最終段落の両方に出現することによるキーワード重複の影響であり、段落の実際の並べ替えを意味しない(Arm1原文でもja_para_3の実際の対応先は第3段落"But when we looked behind the stage, we found a slightly surprising scene."であることを目視でも確認)。

`unmatched_sentences.json`(観察のみ、Fact/一般論追加の候補として列挙。判定はFable):
- Arm1(1文): "People only have to say what they need."(JA「人間は用件を伝えるだけ」の言い換えで、アンカー語に一致しなかっただけの既存文。新規主張ではない)
- Arm2(2文): "You only tell it what you need."(同上の言い換え)、"That idea makes sense."(JA「考え方としては自然です」の言い換え)
- Arm3(0文): 未対応文なし

3 arm合計で3文のみが未対応と判定されたが、いずれも目視で日本語R2内の既存文の言い換えであり、新しい主張・一般論・背景説明の追加ではないことを確認した(機械観測の限界: アンカーキーワード集合に含まれない言い換え表現は「未対応」として拾われるため、実際のFact追加とは別物)。

## §9 参考B・C2との並置(生成完了後)

参考B(`er015_output/news_meta_english_prompt_variation_trial_01/arms/B/revision2.md`)・参考C2(同`arms/C2/revision2.md`)は、日本語Prompt/意味強調英語Promptから英語で新規に記事を書いたTrial(Adaptationではない)。両者とも見立て自体はMeta/Muse/人間コンシェルジュの骨格を保持しているが、JA R2にない新しい一般化文が観測された。例:
- 参考B: "The future may not be a clean battle between humans and machines, with one side replacing the other."(JA R2にない新しい一般論)
- 参考C2: "A confused machine is irritating. A hidden human raises a much more personal question..."(JA R2にない新しい対比・一般化)

Arm1/2/3ではこの種の新規一般化文は§8の機械観測・目視確認いずれにおいても検出されなかった。全文は`comparison_all.md`に並置済み。

## §10 Fact機械観測(`fact_diff_machine.json`)

全arm共通: `numbers`(数字)は0件(JA R2自体に数字がないことと整合)。`quoted_spans`はいずれも3件で、JA R2の「人間コンシェルジュ」「AI電話代行」に対応する引用符付き語句のみ(Arm1/2: "human concierge."/"AI phone service."、Arm3: "human concierges."/"AI phone service.")、JA R2にない新規の引用発言は検出されず。`capitalized_words_not_in_reference_list`は全て文頭の一般語("The"/"But"/"If"等)またはタイトルの語("Voice"/"Stand"/"Understudy"/"Call"/"Phone")であり、新しい固有名詞は検出されなかった(機械抽出の性質上、文頭の通常語が誤検出される既知の限界。詳細はJSON内`note`参照、判定はFable)。

## §11 cost・latency・token・Prompt長・retry

| Arm | model実値 | response_id | input | cached | output | reasoning | latency(s) | cost(JPY) | retried |
|---|---|---|---|---|---|---|---|---|---|
| arm1 | gpt-5.6-luna | resp_0158487c...442 | 848 | 0 | 937 | 516 | 12.313 | 0.207 | false |
| arm2 | gpt-5.6-luna | resp_07e73080...eb1 | 856 | 0 | 933 | 516 | 12.135 | 0.2065 | false |
| arm3 | gpt-5.6-luna | resp_0caf40c8...270 | 854 | 0 | 1409 | 1008 | 14.904 | 0.2979 | false |

合計: 3 call / input 2558 tok / output 3279 tok(reasoning込み) / **総額 ¥0.71**(予算¥10以内、見込み¥1と整合)。retry発生なし(空出力・API失敗いずれも無し)。詳細: `er015_output/news_ja_to_en_adaptation_trial_01/cost.json`

## §12 量産適性の観察(事実のみ)

- call数: 1記事あたり1 call/arm(Original→R1→R2連鎖なし、previous_response_idなし)。
- latency: 12.1〜14.9秒/call(Arm3のみreasoning_tokensが約2倍[1008 vs 516]でlatencyもやや長い)。
- token: input 848〜856(ほぼ一定、日本語R2の長さに依存)/output 933〜1409(Arm3のみ多い)。
- Prompt長: developer 124字固定・user 3599〜3636字(共通制約ブロック+arm別ブロック+日本語R2全文)。
- retry有無: 3 callとも初回成功、retryなし。
- Human Reviewなしでの安定性: 本Trialの3 callでは全armが単一構造(タイトル1行+本文10段落)・目立ったFact drift・崩れた出力なしで安定して返ったが、n=3(1記事×3arm×1回)のみの観察であり、量産安定性の統計的根拠にはならない。
- Adaptationだけで十分か: 今回のJA R2は既に完成したEditorial designを持つため、3 armとも見立て・情報順序・結びを保持したまま英訳できた。原文の完成度に強く依存する方式である可能性が高い(未完成/構成が弱い日本語記事でも同様に機能するかは本Trialでは未検証)。
- 原文品質依存度: 本Trialの範囲では検証できず(単一のEditorial設計が確立したJA R2のみを使用)。
- Fact drift発生率: 本Trial(3 call)では機械観測・目視確認いずれでも0件。

## §13 Fable記入欄(参考順位・分類・UDR・未解決)

### 13.1 Fableブラインド参考評価(blind.md を先読み→blind_key.json 開封、2026-09-24)

参考順位(僅差): **Z(arm2 Balanced) ≥ Y(arm3 Natural) > X(arm1 Faithful)**。3本とも日本語R2の編集設計(主役Muse/舞台裏の人間/代役/最後に舞台と幕へ戻る結び)を保持しており、差は英語表現の硬さ・省略の有無のみで、B/C2(英語で最初から生成)との差より明らかに小さい。

- X(arm1 Faithful): 「A phone-call stage like this was being built at Meta」「human contract staff」「there is a human backstage」など日本語構文をそのまま移した箇所があり、聴取時にやや硬い。一方、「通話の一部」を "some of the calls" と解釈しており、Reuters報道の事実("some calls were handled by human contract workers")に最も近い。
- Y(arm3 Natural): 最も平易で聴きやすいが、「当面の間」に当たる "for the time being" が落ち、結びの「幕の後ろに何があるかを説明する」が "explain what is happening" に一般化されるなど、小さな省略・簡略化がある。
- Z(arm2 Balanced): 自然な英語で、"for the time being"・"behind the scenes"・"we looked backstage" 等の要素を保持。省略が最少で聴きやすさも十分。

### 13.2 Fact/ニュアンス観察
- 機械チェック(数字追加0・新規固有名詞なし・新規引用発言なし)をFableも確認。B/C2で見られた「日本語記事にない一般論の追加」は3 armとも無し。
- 日本語R2「通話の一部を…担当」は「一部の通話」とも「通話内の一部」とも読める曖昧文。X="some of the calls"、Y/Z="some parts of the calls" と解釈が分かれた。Adaptation方式では日本語側の曖昧さがそのまま英語へ伝播するため、英語化時にVerified Fact Ledgerと照合する工程が量産時に必要(Open Item候補、提案ではなく事実列挙)。

### 13.3 分類
**VALIDATED**(Trial上限)。仮説「完成した日本語R2をAdaptすれば、英語で最初から書くより編集設計を保ちやすく一般論の追加も起きにくい」は記事1本・3 armの範囲で支持された。Production採用ではない。

### 13.4 USER_DECISION_REQUIRED
なし(ブロッキング判断なし)。ユーザーへの提示事項: (1) X/Y/Zの品質判断(Fable参考順位はZ≥Y>X)、(2) 再現Trial(下水道・旅行の日本語R2を同じBalanced指示でAdapt、¥5以内)の要否、(3) 英語版の量産ルートを「Adaptation(日本語R2→英語)」と「英語直接生成(C2)」のどちらを本命候補にするか。

### 13.5 未解決
- 記事1本のみで再現性未検証。
- Adaptation時のLedger照合工程は未設計(13.2)。
- 英語Adaptation後にProduction contract(2つの`### `節・`## In one line`)を付与する工程は本Trialの範囲外で未検証。

## §14 Production変更なし

Production code・SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)への追記・変更は行っていない。既存script(`er003_v1_en_direct_vfl_01_generate.py`/`er005_cost_logger.py`/`er015_news_core_idea_editorial_trial_01.py`/`er015_news_iterative_entertainment_trial_02.py`/`er015_news_original_baseline_repro_01.py`)はimportのみで無変更。新規記事生成・Web Search・Ledger生成・Audio生成は行っていない。

## §15 USER_DECISION_REQUIRED

なし(本Trial自体はSTOP条件非該当、正常完了)。ただし本Trialの結果自体(3 armのうちどれを今後の方向性として扱うか、Production採用の是非)は、Trial運用上の原則により**ユーザー判断待ち**(Production採用は人間ユーザーのみが承認可能)。

## §16 未解決事項

- Arm2(Balanced)が「本命候補」としてユーザーから事前指定されていたが、最終的な参考順位・分類判断はFable/ユーザーに委ねる(§13未記入)。
- 原文品質依存度・量産安定性は、単一記事・3 callのみの観察であり、複数記事での再現性は未検証(本Trialのスコープ外)。
- 参考B/C2との「新規一般化文の有無」の比較は目視+機械観測の組み合わせであり、Sonnetによる主観評価は含めていない(禁止事項どおり)。
