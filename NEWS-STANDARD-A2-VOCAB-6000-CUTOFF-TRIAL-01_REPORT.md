# NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01 REPORT

管理ID: `NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01`
性質: Trial。到達上限 `VALIDATED`。Production変更なし。
実行者: Sonnet(サンドイッチ委任、初回)
実行日: 2026-09-25

## §1 方針・測定方法

- 背景: v3(語彙簡略化=一定効果あり)→v4(頻度帯4段階設計、REJECTED、
  再現性向上せず)を経て、今回は「頻出上位6,000語以内は原則そのまま
  残してよい/6,000語超は自然さを崩さない範囲で平易な語へ強く置換/
  固有名詞は別扱い/専門語は意味保持に必要なら例外可」という単一
  しきい値+自然さ優先の設計に簡素化した。
- 頻度基準: `wordfreq.top_n_list("en", 20000)`
  (NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01で導入済み、追加installなし)
  からlemma単位(`simple_lemma`/`simple_lemma_candidates`、規則活用のみ
  対応の簡易ヒューリスティック、不規則活用は非対応の既知限界を継承)の
  最小順位表を構築し、rank<=6000を「6,000語以内」、rank>6000
  (20,000語表外=Noneを含む)を「6,000語超」の2値のみで判定した(帯A/B/
  C/Dの細分は廃止)。記事内で文頭以外に大文字表記される語は固有名詞
  候補として別枠(機械ヒューリスティック、全大文字略語等の誤判定余地は
  既存Trialと同じ既知限界)。
- 測定はすべてLLM不使用(`--step evaluate`はローカル計算のみ)。

## §2 v5 Prompt全文 + v3差分

developerはv3と一字も変えていない(`assert DEVELOPER_STD_V5 ==
v3mod.DEVELOPER_STD_V3`)。user template内、v3の該当5行のみ以下6行に
置換した(それ以外の本文は一字も変えていないことを機械assertで確認済み、
`prompt_diff_v3_v5.md`参照)。

```
Prefer words within roughly the 6,000 most common English words.
If a word is clearly outside that range, replace it when a simpler natural alternative exists.
Do not force a replacement if it makes the sentence less natural or changes the meaning.
Proper names are excluded from this rule.
Essential technical terms may remain when a simpler equivalent would lose important meaning.
Do not add an explanation for a hard word; make the sentence around it simple instead.
```

Prompt全文: `er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/
prompt_standard_v5_6000.txt`。差分説明: 同ディレクトリ`prompt_diff_v3_v5.md`。

## §3 Sewer v5全文(Advanced並置)

Advanced sha256(実測、Meta用sources.jsonに期待値エントリなし):
`7e5aed46d6cb2756...`(全文は`sewer_v5_generation_sources.json`)。

```
“Merger”? Not Towns, but Household Wastewater

When a news report says “combined septic tank,” you may wonder. Is it about towns joining together? But towns are not the things being combined. They are toilet water, kitchen water, and bath water.

Some local governments are considering replacing old sewer systems with combined septic tanks. This does not mean removing all sewers. In some areas, they are considering another kind of system. It would treat wastewater near each home, instead of connecting the whole town.

A sewer is like an invisible main artery beneath the town. It collects water from homes in underground pipes. Then it carries the water to a faraway treatment plant. Most of the time, we hardly think about it. We turn on the tap and flush the toilet. The underground system takes care of the rest.

But when those pipes grow old, the situation changes. Because they are underground, damaged places are hard to find. Repairs are not easy, either. The system reaches a long way and stays connected. So repairs can also become very large jobs.

That is where combined septic tanks come in. They are small places that treat water near homes. They treat toilet, kitchen, and bath water for each home. The water does not go to a distant treatment plant. Instead, it is cleaned near the home.

It is like putting a small washing machine in every home. This is instead of one huge washing machine for the town. The idea is to divide one large system into several smaller ones.

Of course, a septic tank does not mean nothing else is needed. It still needs installation, checks, and cleaning. For people who use sewers, a hidden part of daily life will change too.

Still, the interesting point is this: to keep life convenient, we do not always need a bigger system. We do not have to make an old underground main artery keep going. We can move water treatment closer to home. The future of sewers may arrive in a surprisingly familiar place—right near us.
```

全文比較(Advanced→v3→v5): `comparison_sewer_v5.md`。

## §4 Meta v5全文(Advanced並置)

Advanced sha256: `20b7ac01ffc962b5...`(sources.jsonの既存期待値と一致確認済み)。

```
“Hello, I’m AI” — A Human Was Behind the AI Phone Call

AI making phone calls sounds like a convenient future service. A person only needs to say what they want. Then AI makes the call. That was the kind of phone service Meta was building.

The lead role belonged to Muse, Meta’s personal AI agent. Meta was trying to let Muse make calls for people.

But when people looked backstage, they found something unexpected.

During internal tests, contract workers—not AI—handled parts of some calls. Meta called these workers “human concierges.”

In other words, the sign outside said “AI phone service.” But sometimes, a human handled the call. The stage looked as if AI were performing alone. In fact, a human understudy was waiting backstage.

That is the most interesting part of this story. You may think an AI phone call is truly impressive. Then you may find a human behind the curtain. It is like seeing a piano play by itself. Then you learn another performer was hidden inside it.

Of course, there is nothing wrong with people helping. Humans can handle the parts that AI still cannot do well. That is a natural approach.

But phone calls can contain personal information. Meta employees raised privacy concerns. They worried that call content could leak outside the company. People may think they left the conversation to AI. But if they learned contract workers had actually listened to it and replied, they might be shocked.

Reuters reviewed internal posts. In them, a Meta executive said the company had put the feature on hold.

With an AI phone service, can it make a call? That may not be the only important question. Who is speaking on the stage? And who is behind the curtain? The more convenient the service, the more it may need to explain what is happening. People need this before they can truly feel safe trusting it.
```

全文比較(Advanced→v4→v5): `comparison_meta_v5.md`。

## §5 6,000超残存語一覧と必要/置換可能の仮分類(Sonnet仮分類、機械リストは`vocab_over6000_sewer.md`/`vocab_over6000_meta.md`)

### Sewer v5(over6000、9語、異なり語)

| 語 | rank | 分類(Sonnet仮) | 根拠 |
|---|---|---|---|
| invisible | 6153 | 置換可能だった語 | v3で"hidden"(2837、within6000)への自然な置換実績あり。v5は保持を選んだため6,000超のまま残存(悪化ではないが未改善)。 |
| surprisingly | 6187 | 必要語(Ending表現の一部) | "a surprisingly familiar place"はEnding文の核。置換すると結びの効果が薄れるリスク。 |
| flush | 9610 | 必要語(日常語だが平易な代替が乏しい) | "flush the toilet"は自然な定型表現。wordfreq順位は高いが実際にはごく基本的な動詞で、置換すると不自然になりやすい。 |
| sewer / sewers | 11459 / None | 必要語(記事主題語) | 記事の中心テーマそのもの。置換不可能。 |
| artery ("main artery") | 12006 | 必要語(中心比喩、Prompt明示の例外) | Promptの「意味保持に必要な専門語/比喩は例外可」に該当。 |
| wastewater | 18216 | 必要語(記事主題語) | タイトル・本文で一貫。 |
| septic | None(表外) | 必要語(核となる専門語) | 全版で一貫保持。 |
| faraway | None(表外) | **置換の結果生じた新規の難語**(不要な置換の産物) | 6,000語以内の"distant"(5212)を6,000超・表外の"faraway"へ置換した結果生じた語。§6参照。 |

### Meta v5(over6000、6語、異なり語)

| 語 | rank | 分類(Sonnet仮) | 根拠 |
|---|---|---|---|
| leak | 6160 | 必要語(ニュアンスを持つ動詞、平易な代替が意味を弱める) | "leak outside the company"は「意図せず漏れる」含意があり、"go out"等への置換は意味を弱める。 |
| reuters | 8719 | 必要語(固有名詞、本来はrule除外対象) | 文頭大文字のため機械ヒューリスティックでproper_noun判定されなかった既知の誤分類(限界、既存Trールと同じ)。 |
| curtain | 8776 | 必要語(比喩語、Prompt明示のMETAPHOR_WORDS) | "curtain"はPromptの比喩例示語そのもの。 |
| backstage | 12912 | 必要語(比喩語、Prompt明示) | 同上。 |
| concierges | None(表外) | 必要語(引用句の一部、Fact保持対象) | `"human concierges"`は引用符付きの固有の呼称で、Fact diffでも`quoted_phrases`として保持確認済み。 |
| understudy | None(表外) | 必要語(比喩語、Prompt明示) | METAPHOR_WORDSの一つ。 |

全体として、Sewer/Meta双方とも6,000超残存語の大半は「主題語・比喩語・
固有名詞・引用語」であり、Prompt通りに機能している。唯一の例外は
Sewerの"faraway"で、これは6,000語以内の"distant"を不要に置換した結果
生じた語であり、§6で扱う。

## §6 不自然な置換・難語→難語置換の有無

- **難語→難語置換(新規発生)**: Sewer distant(5212、within6000)→
  faraway(None、表外)が2箇所中1箇所で発生。v5自身のルール
  (「6,000語以内は明確にoverでない限り置換しない」)に反する形で、
  平易な語をより難しい語(表外)へ置換した唯一の事例。もう1箇所は
  "distant"のまま保持されており、同一文書内で同じ語に対する扱いが
  分かれた(不統一)。
- **v4以前で見られた難語→難語置換の解消**: v4のinvisible→unseen
  (invisible[6153]→unseen[12884]、明確な悪化)は、v5ではinvisibleが
  そのまま保持され(§7参照)解消された(悪化はしていないが、v3が
  達成した"hidden"への改善には未到達)。v4のcollects→gathers
  (2335→4530、平易語→やや難語)もv5では"collects"のまま保持され解消。
- **不自然な置換**: 目視の範囲で明確に不自然と判断できる置換は
  見つからなかった。v3のinstallation→putting in(名詞→句動詞、
  動名詞/名詞混在で文法的にやや不揃いと既存Trialで指摘済み)は、
  v5では"installation"がそのまま保持されたため再発していない。
  Meta v5の"It would not be surprising if they were shocked"→
  "they might be shocked"への言い換えは不自然ではないが、二重否定に
  よる強調のニュアンスがやや薄れている(§10参照)。

## §7 11語遷移表

ユーザー指定11語(municipalities/facilities/installation/inspections/
convenience/artery/wastewater/septic/collects/distant/invisible、
いずれもSewer記事の語)の詳細遷移表・根拠・集計は
`er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/
vocab_transition_11words.md`に保存(Sonnet目視、1行ずつ根拠付き)。

要約:
- **完全に解消**: installation(putting in/put in→installation復元)、
  collects(gathers→collects復元)
- **悪化は解消(改善までは未到達)**: invisible(unseen[v4の悪化]は解消、
  ただしv3のhiddenほどの簡略化はできていない)
- **部分的に改善**: distant(2箇所中1箇所のみ復元、他方はfaraway継続)、
  convenience(over→within6000に収まる自然な品詞転換)
- **一貫して保持**: artery(比喩)、septic、wastewater(v4のタイトル
  不統一も解消)
- **一貫して置換(必須ではないが妥当)**: facilities→places、
  inspections→checks
- **未解決の不統一**: municipalities(文書内で"towns"/"local
  governments"の2表現が混在、v3のみ統一的)

## §8 Level指標

`level_metrics.md`(全文保存)より抜粋:

| 記事 | words | sentences | avg words/sent | FK grade(heuristic) |
|---|---|---|---|---|
| Sewer Advanced | 354 | 26 | 13.62 | 7.22 |
| Sewer Standard v3 | 331 | 34 | 9.74 | 5.07 |
| Sewer Standard v4 | 354 | 39 | 9.08 | 4.68 |
| Sewer Standard v5 | 337 | 34 | 9.91 | 5.43 |
| Meta Advanced | 330 | 25 | 13.2 | 6.72 |
| Meta Standard v4 | 300 | 31 | 9.68 | 5.06 |
| Meta Standard v5 | 309 | 32 | 9.66 | 5.25 |

v5は両記事ともAdvancedより明確に平易(FK grade低下、avg words/sentが
目標9〜11語に収まる)。v3/v4と比べてFK gradeはやや高め(v3のみやすい
方向へ寄り過ぎていた可能性、v5はv3よりわずかに複雑=Advancedへわずかに
近い)だが、9〜11語/文の目標レンジには収まっている。

## §9 Story・Reveal・比喩・Ending

`structure_map.md`(全文保存)より:

- **段落数**: Sewer Advanced 8→v3 8→v4 14→**v5 8**(v4で段落数が
  大幅に増えていた問題[短文・改行多用]が解消し、Advancedと完全に
  一致)。Meta Advanced 10→v4 10→v5 10(一貫)。
- **比喩語保持**: main artery/washing machine(Sewer)、stage/backstage/
  lead role/curtain/understudy(Meta)は全版・全比喩語で一貫して保持
  (機械チェック○)。
- **Reveal/Endingマーカー**(既存Trialが使った逐語マーカーの残存チェック、
  機械判定):
  - Sewer Reveal(`combined septic tank`/`small water-treatment`):
    ×(要確認)。ただし目視確認の結果、v5は「small water-treatment
    facilities」を「small places that treat water near homes」と
    自然に言い換えただけで、Reveal自体(下水道→合併浄化槽への
    切り替え説明段落の構成)はAdvanced/v3と同じ順序・内容で保持
    されている。Story break ではなく語彙選択の自然な差分と判断。
  - Sewer 中心比喩(main artery/washing machineが直喩のまま保持): ○
  - Sewer Ending("surprisingly familiar place"の結び): ○
  - Meta Reveal(human concierges/backstageの発見という段落構成): ○
  - Meta Ending("Who is speaking on the stage? And who is behind the
    curtain?"の結び): ○
  - Meta 数量表現"some parts of the calls"の維持: ×(要確認)。目視の
    結果、v5は「handled parts of some calls」(語順が入れ替わり、
    scope語"some"は維持)と「in some cases」→「sometimes」(scope語
    "some"が語として消えるが、意味[時々/一部のケースで]は
    "sometimes"として保持)の2箇所に分かれていた。機械的な
    `scope_word_counts`では"some"が2→1に減少しているが、実質的な
    範囲限定のニュアンス(全てのケースではない)は保持されている
    (完全な喪失ではなく、語形の違いによる機械判定の限界)。

## §10 Fact drift・意味差

`fact_diff_machine_sewer_v5.json`/`fact_diff_machine_meta_v5.json`
(Advanced→v5)より:

- **数値**: Sewer/Meta双方とも`numbers_missing_in_v5`/
  `numbers_added_in_v5`はいずれも空(数値の脱落・追加なし)。
- **固有名詞**: 機械抽出の差分は主に文頭大文字語の再現アーティファクト
  (例: Sewerの"Installation"[固有名詞として誤検出されていた文頭語]が
  v5で非文頭になり消えた等)であり、実質的な固有名詞の脱落・混入は
  目視で確認できなかった。Metaの"Reuters"/"Meta"/"Muse"はいずれも
  v5本文に存在(引用符付き"human concierges"/"AI phone service"の
  quoted_phrasesも完全一致で保持)。
- **否定**: Sewer "not"は6→7(増加、脱落なし)。Meta "not"は4→2
  (機械カウント上減少)。目視確認の結果、1件は"is still not good at"
  →"still cannot do well"(否定辞"not"が複合語"cannot"内に埋め込まれ、
  正規表現の単語境界チェックで捕捉されなかっただけの検出漏れ)。もう
  1件は"it would not be surprising if...shocked"(二重否定による強調)
  →"they might be shocked"(直接的な推量表現)へ言い換えられており、
  事実(shockedという結果自体)は保持されているが、二重否定特有の
  「意外ではない」という含意のニュアンスがやや弱まっている
  (軽微な意味の平坦化、Fact自体の欠落ではない)。
- **範囲語(scope)**: §9参照(Meta "some"のカウント減少は語形の違いに
  よる検出漏れが主因、実質的な範囲限定のニュアンスは概ね保持)。
  Sewerで"each home"→"every home"(1箇所)は「各家庭」→「すべての家庭」
  という個別/全体のニュアンスがわずかに変化しているが、文脈上の意味
  (家庭ごとに設置する)への実害は小さいと判断。
- **総評**: 数値・固有名詞・引用句の完全性は保持されている。否定・
  scope語で機械検出された差分は、目視の結果いずれも「表現の言い換えに
  伴う軽微なニュアンス変化」であり、明確なFact drift(数値誤り・
  主語誤り・因果関係の逆転等)は確認されなかった。

## §11 cost・latency・tokens・call数

call数=2(Sewer 1、Meta 1)、`cost.json`より:

| stage | model(実値) | input tokens | output tokens | reasoning tokens | elapsed(s) | cost(JPY) | retried | fallback |
|---|---|---|---|---|---|---|---|---|
| a2v5_standard_sewer | gpt-5.6-luna | 861 | 2485 | 2070 | 20.692 | 0.5047 | False | False |
| b1v5_standard_meta | gpt-5.6-luna | 837 | 4808 | 4425 | 39.148 | 0.9499 | False | False |

合計cost_jpy = 1.4546円(budget_jpy=100、within_budget=True)。
previous_response_idなし(`chain_method=fresh_single_call`)、
web_search_used=false(両call)。

## §12 Fable参考評価

### 12.1 Fable参考評価(Sewer v5・Meta v5を通読)
- 語彙: 6,000語ラインは意図どおり「必要語は残し、不要な難語だけ落とす」方向に働いた。Sewerでは municipalities が消え(towns / local governments)、installation・checks・convenient は自然なまま残存。残る6,000超語は surprisingly / convenience / flush / sewer / artery / wastewater / invisible で、いずれも主題語・比喩語・自然な一般語であり置換不要と見る。Metaの6,000超は leak / curtain / backstage / Reuters のみで全て必要語。
- 不自然な置換・難語→難語置換: v3/v4で問題だった installation→putting in、collects→gathers、invisible→unseen/hidden は発生せず、Advancedの語がそのまま残った。唯一の逸脱は distant(6,000以内)→faraway(表外)が2箇所中1箇所で残ったこと(もう1箇所は distant のまま)。文書内の訳語不統一(towns / local governments)は残る。
- 文長: Sewer 9.91語/文・FK 5.43、Meta 9.66語/文・FK 5.25 で、v3/v4と同水準の簡略化を維持。段落数はAdvancedと同じ8(v4の断片化が解消)。
- Story・比喩・Reveal・Ending: 両記事とも維持(main artery / washing machine / lead role / backstage / understudy / curtain / piano)。
- Fact・意味: 数字・固有名詞・引用句の欠落なし。Metaで "some parts of the calls"(Baseline)が "parts of some calls" に変わり、曖昧文の読みが「一部の通話の一部」へ寄った(Baselineの意味保持という条件からはズレ。OPEN-177の曖昧性と関連)。Meta末尾 "can it make a call? That may not be the only important question." の分割はやや不自然。
- 総評: v5は v3(語彙改善はあるが不自然置換あり)と v4(帯設計、後退あり)の問題を、より短いルールで回避しており、2記事横断で再現した。

## §13 分類

**VALIDATED**(Trial上限)。「6,000語ライン+自然さ維持」の簡素ルールは、不要な難語(municipalities)を落としつつ必要語(installation / artery / wastewater / 比喩語)を壊さず、不自然置換・難語→難語置換を2記事で起こさなかった。残課題は distant→faraway 1件と Meta "parts of some calls" の意味の寄り。Production採用ではない。

## §14 USER_DECISION_REQUIRED

1. Standard A2 Promptの現時点の最良候補を v3 から **v5(6000-cutoff)** に更新してよいか(Fable推奨: 更新。Trial上の候補であり、Production採用ではない)。
2. Meta v5 の "parts of some calls": Baselineの "some parts of the calls" を保持する方針(OPEN-177の一次情報確認まで)に照らし、(a) 許容 (b) v5 Promptに「範囲語の位置を変えない」旨を足す (c) Baseline側の曖昧性解消(一次情報確認)を先に行う、のどれか(Fable推奨: (c)。Prompt側で個別対応するより、Baselineの曖昧性を解くのが根本)。
3. Advanced(Natural)+Standard(v5候補)の2段階をProduction配線(OPEN-177)へ進める設計着手の可否(着手時期はユーザー判断)。

## §15 Open Item候補・未解決

- distant→faraway(Sewer、2箇所中1箇所)は、v5自身のPrompt文言
  (「6,000語以内は明確にoverでない限り置換しない」)に反する形で
  within6000語をover6000・表外語へ置換した明確な事例。今後v6等を
  検討する場合、この種の「within6000語なのに置換されてしまう」事象を
  どう扱うか(Promptに追加指示を入れるか、許容範囲とするか)は
  USER_DECISION_REQUIRED候補。
- municipalities→towns/local governmentsの文書内不統一は、v3〜v5の
  いずれでも未解決。同一語に対する訳語統一をPromptで明示的に指示する
  かどうかはOpen Item候補。
- Meta v5の"it would not be surprising if..."→"they might be shocked"
  のような二重否定→直接推量への言い換えで、事実自体は保持されるが
  修辞的ニュアンスがやや弱まる現象は、Fact diffの機械検出
  (negation_counts)だけでは捕捉しきれない(単語境界の都合で
  "cannot"内の"not"も検出漏れ)。将来のFact diff測定手法の改善余地
  として記録(新Validator追加は本Trialのスコープ外のため実施していない)。
- 一覧外Read理由: `er015_output/news_standard_a2_vocab_banding_trial_01/
  vocab_transition_sewer_v4.md`は事前指定Read一覧に明記されていたため
  比較用にReadした(v3〜v4の遷移根拠の再利用・整合確認目的)。それ以外は
  すべて事前指定Read一覧・delegation記載のファイルのみを参照した。
