# KEY-PHRASE-LEVEL-SPEC-TRIAL-01_REPORT.md

管理ID: `KEY-PHRASE-LEVEL-SPEC-TRIAL-01`
実行者: Sonnet(サンドイッチ委任、初回)
性質: Trial。到達上限 `VALIDATED`(本Trialの実測ではPromptの再現性が
低く`REJECTED`寄りの結果になったため、最終Statusは§13でFable/ユーザー
判断を仰ぐ)。Production採用・配線は行っていない。

証跡格納先: `er017_output/key_phrase_level_spec_trial_01/`
(`inputs_resolved.json`, `conflict_check.md`, `outputs/*.json`,
`expected_sets.json`, `match_results.json`, `match_results.md`,
`cost.json`, `summary.json`)

---

## §1 入力記事・Prompt全文・schema

### 1.1 入力記事(採用パス・sha256、優先順で存在するものを採用)

| combo | 採用パス | 採用理由 | sha256(先頭16桁) | 文字数 |
|---|---|---|---|---|
| sewer_standard | `er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/a2v5_standard_sewer.md` | Production経路の`er012_output/.../sewer/a2/article.md`が未生成(並行タスク`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`実行中)のためfallback | `12a40a0b03e967b1` | 1971 |
| sewer_advanced | `er015_output/news_natural_advanced_standard_a2_trial_01/a1_advanced_sewer.md` | 同上、Production経路の`sewer/b1b/article.md`未生成のためfallback | `7e5aed46d6cb2756` | 2090 |
| meta_standard | `er012_output/e_family_two_level_wiring_01/meta/a2/article.md` | Production経路で生成済み、優先パスを採用 | `cb5bf4fe851fc658` | 1865 |
| meta_advanced | `er012_output/e_family_two_level_wiring_01/meta/b1b/article.md` | Production経路で生成済み、優先パスを採用 | `10ccdd99e82aafbb` | 1926 |

Sewer 2本はいずれもfallbackパスを使用した(委任文に明記された優先順
ルールどおり)。読み取りのみで、いずれの入力ファイルも変更していない。

### 1.2 Prompt全文(逐語)

developer(共通):
> You choose Key Phrases for an English-learning news audio program for
> Japanese adult learners. The goal of Key Phrases is not only to
> understand this article, but to take away English that the learner
> can reuse in other situations.

user(Standard)・user(Advanced)は委任文に記載の内容を一字一句
`er017_key_phrase_level_spec_trial_01.py`の`STANDARD_USER_TEMPLATE`/
`ADVANCED_USER_TEMPLATE`へ転記して使用(`{article}`のみ実記事本文へ
差し込み)。全文は`er017_output/.../outputs/{stage}_prompt.txt`に
保存済み。

### 1.3 schema(strict)

`key_phrases`配列、`minItems=maxItems=5`。各itemは
`phrase/is_topic_word/example_sentence/reason_ja/explanation_ja`
(Standard)または`phrase/is_topic_word/example_sentence/reason_ja/
explanation_en`(Advanced)の5フィールド必須、`additionalProperties:
false`。

---

## §2 既存仕様との競合確認

`er017_output/key_phrase_level_spec_trial_01/conflict_check.md`に全文
記録。要点:

1. **個数**: 既存5個・新Trial5個で一致。
2. **レベル別選定基準**: 既存(`er003_b1_p2_keywords.py`が使う
   `b1_p2_keywords_l_prompt_template.txt`)はA2/B1で**同一Prompt**を
   共用し、「初回リスニング困難度」を最優先(汎用性は優先順位の最後)。
   新Trialはレベル別に別Promptを持ち、「汎用性・学習価値」を最優先
   (既存と優先順位が逆)。
3. **Topic Word概念**: 既存に該当フィールドなし。新Trialの新概念。
4. **解説言語**: 既存はA2/B1いずれも日本語グロスのみ(実例:
   `keywords_canonicalized.json`のMeta b1b記事でも英語解説なし)。
   新Trialは Advanced=英語解説という新方針。
5. **"..."スロット記法**: 既存は日本語グロス側で明示的に禁止(逐語:
   「『…』のようなプレースホルダー記号は使わないでください」)。
   新Trialは英語Phrase側で明示的に許容。
6. **出力構造**: 既存は選定→正規化→冗長性QAの3段構成・多観点QA
   フィールド。新Trialは単一段・5フィールドの最小構成。

**判定**: 上記いずれも`er017_key_phrase_level_spec_trial_01.py`が
独立したPrompt/schema/API呼び出しを持つことで実現でき、既存Production
関数(`run_key_phrases`/`run_key_phrase_selection`/`bk.*`/`kc.*`/
`prod.*`/`p2g.*`)への変更や呼び出しは一切不要だった。**STOP条件
「既存Production仕様を変更しないとTrialできない」には該当しない。**
実際、本Trial scriptはこれら既存モジュールを一切importしていない。

---

## §3 Standard(Sewer/Meta)の5個+選定理由+日本語解説(実際の出力、転記)

### Sewer Standard

| # | phrase | is_topic_word | reason_ja | explanation_ja |
|---|---|---|---|---|
| 1 | joining together | false | 人やグループが一緒になることを表す、ニュースでも日常会話でも使える表現です。 | 「一緒になる」「協力してまとまる」という意味です。towns, companies, groups などにも使えます。 |
| 2 | instead of ... | false | 二つの選択肢を比べるときに使える基本表現です。 | 「…の代わりに」という意味です。後ろには名詞や動名詞（-ing形）を置きます。 |
| 3 | take care of the rest | false | 「残りを任せる・処理する」という日常的で便利な表現です。 | 「残りのことを処理する」「あとは任せる」という意味です。人や機械が仕事をしてくれるときに使えます。 |
| 4 | hard to find | false | 問題や物を見つけるのが難しいと伝える、よく使う形です。 | 「見つけるのが難しい」という意味です。hard to + 動詞で、何かをするのが難しいことを表します。 |
| 5 | grow old | false | 物や人が古くなることを表す基本的な組み合わせです。 | 「年を取る」「古くなる」という意味です。people にも things にも使えます。 |

### Meta Standard

| # | phrase | is_topic_word | reason_ja | explanation_ja |
|---|---|---|---|---|
| 1 | tell ... what you need | false | 必要なことを伝えるときに幅広く使える基本表現だからです。 | 「…に必要なことを伝える」という意味です。tell someone what you need の形で使います。 |
| 2 | not always a bad thing | false | 物事を単純に良い・悪いと決めつけない便利な表現だからです。 | 「いつも悪いとは限らない」という意味です。人や行動について、柔らかく意見を述べるときに使います。 |
| 3 | contain personal information | false | 電話や書類などについて、他の話題でも使える自然な組み合わせだからです。 | 「個人情報を含む」という意味です。contain は「中に含んでいる」という動詞です。 |
| 4 | hand ... to ... | false | 仕事や責任を誰かに渡す場面で使える重要な句動詞だからです。 | 「…を…に渡す、任せる」という意味です。hand the work to her のようにも使えます。 |
| 5 | feel safe | false | 安心や安全について話す日常的で使いやすい表現だからです。 | 「安心している、安全だと感じる」という意味です。feel safe doing something で「安心して何かをする」と言えます。 |

いずれのセットも`is_topic_word=true`は1件も無かった(4セット全体で
0/20、詳細は§6・§8)。

---

## §4 Advanced(Sewer/Meta)の5個+選定理由+英語解説(実際の出力、転記)

### Sewer Advanced

| # | phrase | is_topic_word | reason_ja | explanation_en |
|---|---|---|---|---|
| 1 | replace A with B | false | AをBに置き換えるという、説明や提案で使いやすい表現です。 | to use B instead of A |
| 2 | take care of the rest | false | 残りを処理するという意味で、日常生活や仕事にも応用しやすい表現です。 | to deal with everything that remains |
| 3 | hard to find where A is damaged | false | 問題や故障の場所を特定する難しさを説明できる表現です。 | difficult to discover the exact place where A has a problem |
| 4 | come in | false | 解決策や新しい要素が役立つ場面を示す、ニュースでも使われる句動詞です。 | to become useful or important in a situation |
| 5 | move A closer to B | false | サービスや活動を人や場所の近くに移すことを説明できます。 | to put A nearer to B |

### Meta Advanced

| # | phrase | is_topic_word | reason_ja | explanation_en |
|---|---|---|---|---|
| 1 | on A's behalf | false | 誰かの代わりに行動することを表す、再利用性の高い表現だから。 | to do something for someone instead of them |
| 2 | raise concerns | false | ニュースや説明文で、問題への懸念を述べる際によく使う組み合わせだから。 | to make people think that something may be a problem |
| 3 | put A on hold | false | 計画やサービスを一時停止する際に幅広く使える表現だから。 | to stop something for a while |
| 4 | fill in | false | 不足している部分を補うという意味で、仕事や技術の説明に使いやすいから。 | to provide help where something is missing or weak |
| 5 | appear to be | false | 見た目と実際が異なる状況を説明するニュース表現として有用だから。 | to seem to be something, even when that may not be true |

---

## §5 一致表と判定(4セット+全体)

機械判定(exact/substringのみ、`match_results.md`)に加え、委任文が
求める「同義・同一学習単位」の目視判定(Sonnet仮判定)を行った結果を
併記する。

| combo | expected | actual上位一致(目視含む) | 一致数/5(目視) | 判定 |
|---|---|---|---|---|
| sewer_standard | take care of / instead of / keep ... going / treatment plant / sewer(TW) | instead of ...≈instead of(近似一致)、take care of the rest≈take care of(語追加あり、近似一致) | **2/5** | FAIL |
| sewer_advanced | replace A with B / be connected to / main artery / treatment plant / septic tank(TW) | replace A with B(完全一致) | **1/5** | FAIL |
| meta_standard | in other words / put ... on hold / raise concerns / there is nothing wrong with ... / AI agent(TW) | 該当なし(下記参照) | **0/5** | FAIL |
| meta_advanced | raise privacy concerns / put ... on hold / behind the curtain / personal information / human concierge(TW) | raise concerns≈raise privacy concerns(privacy欠落、近似一致)、put A on hold≈put ... on hold(スロット記法差のみ、近似一致) | **2/5** | FAIL |

**全体一致率(目視込み仮判定): 5/20 = 25%**(ユーザー指定の目安
60%を大きく下回る)。4セットいずれもPASS基準(3個以上)に届かず、
**4/4セットがFAIL**。

Topic Wordは4セットとも1件も選ばれなかった(想定Topic Word: sewer/
AI agent/septic tank/human conciergeはいずれも未出現)。

---

## §6 不一致Phraseの理由(Sonnet仮分析)

- **sewer_standard**: `keep ... going`(想定)に相当する表現は出力
  されず、代わりに記事内の別語彙(`joining together`/`hard to find`/
  `grow old`)が選ばれた。`treatment plant`(想定)も未出現。Topic
  Word`sewer`も未出現——記事のテーマそのものを表す語を「記事固有
  なだけの語」として除外した可能性が高い(§8参照)。
- **sewer_advanced**: `be connected to`/`main artery`/
  `treatment plant`/`septic tank`(想定)がいずれも未出現。記事本文
  には"aging underground main artery"という句が実在する
  (`move A closer to B`のexample_sentenceに引用されている)にも
  関わらず、`main artery`という語そのものは選定されなかった。
  Standardと同じ`take care of the rest`を再選定しており、
  レベル差別化が働いていない(§7参照)。
- **meta_standard**: 想定5個(`in other words`/`put ... on hold`/
  `raise concerns`/`there is nothing wrong with ...`/`AI agent`)は
  いずれも未出現。実際の記事文には`raise concerns`に近い文が存在する
  はずだが(Meta Advanced版では`raise concerns`が選ばれている)、
  Standard記事側では選ばれなかった。Standard記事本文の実際の言い回し
  がAdvanced版と異なる(Standard化で表現が変わっている)ことも一因と
  考えられる。
- **meta_advanced**: `raise concerns`(想定`raise privacy concerns`
  からprivacyが欠落)、`put A on hold`(想定`put ... on hold`と
  ほぼ同一、スロット記法の差のみ)の2件は近似一致。`behind the
  curtain`/`personal information`/Topic Word`human concierge`は
  いずれも未出現。特に`human concierge`は既存Production(Meta b1b
  `keywords_canonicalized.json`)でもrank1として実際に選ばれている
  語であり(§9参照)、新Trialでも学習価値が高いはずだが、Topic Word
  枠が一度も使われなかったため落選した可能性がある。

全体として、想定セットはユーザーの例示(理想像)であり、実際のモデル
出力は「汎用性優先」という指示には概ね従っているものの、想定した
テーマ固有の重要語(sewer/main artery/treatment plant/septic tank/
AI agent/human concierge/behind the curtain等)をほぼ一貫して避ける
方向に振れた。

---

## §7 Phrase品質・Advanced解説チェック

### 7.1 学習ポイントの重複・不要語の付加(目視)

- **`take care of the rest`がSewer Standard・Sewer Advancedの両方で
  選定された**(同一記事・同一句、レベル差別化なし)。加えてこの形は、
  Advanced Prompt内でユーザーが明示的に挙げた「悪い例」そのもの
  (Prompt原文: `"take care of", not "take care of the rest"`)に
  該当する。Advanced側でこの禁止パターンがそのまま出力されたのは、
  Prompt指示への明確な不遵守。
- **`hard to find where A is damaged`(Sewer Advanced)**は、
  「hard to find」という学習ポイントに「where A is damaged」という
  関係節を付加しており、「one learning point per phrase」指示に反する
  (Standard版は同じ記事から素直に`hard to find`単体を選んでおり、
  Advanced版の方がむしろ複雑化している)。
- 記事固有名詞の不用意な固定化は見当たらなかった(4セットとも
  A/B/...のスロット記法や一般名詞を用いており、記事固有の企業名・
  地名等をそのまま固定した例はない)。

### 7.2 Advanced解説チェック(`match_results.json`の機械計測)

| combo | phrase | 解説語数 | phrase最小zipf | 解説内でphraseより難しい語 |
|---|---|---|---|---|
| sewer_advanced | replace A with B | 6語 | 4.58 | なし |
| sewer_advanced | take care of the rest | 6語 | 5.23 | remains |
| sewer_advanced | hard to find where A is damaged | 11語 | 4.39 | なし |
| sewer_advanced | come in | 8語 | 5.78 | become / useful / important / situation |
| sewer_advanced | move A closer to B | 6語 | 4.73 | nearer |
| meta_advanced | on A's behalf | 8語 | 3.49 | なし |
| meta_advanced | raise concerns | 10語 | 4.59 | なし |
| meta_advanced | put A on hold | 6語 | 5.19 | なし |
| meta_advanced | fill in | 9語 | 4.64 | なし |
| meta_advanced | appear to be | 12語 | 4.85 | なし |

- 語数はいずれも目安15語以内に収まっている(最大12語)。長文化は
  確認されなかった。
- `come in`(zipf 5.78、非常に高頻度=易しい句)の解説"to become
  useful or important in a situation"は、解説内の4語すべてが
  phrase自体よりwordfreq順位で難しい(zipfが低い)。句自体は易しいが
  説明がやや硬い可能性がある。
- `take care of the rest`と`move A closer to B`もそれぞれ解説内に
  phraseより難しい語(remains/nearer)を1語含む。
- 意味の正しさ(目視): 10件すべて、日本語で見ても英文の意味として
  誤りは見当たらなかった。
- 長文化・難化がSTOP基準に達するほど顕著ではないが、`come in`の
  ように易しい句に対してやや硬めの解説語彙を使う傾向は事実として
  記録する。

---

## §8 Prompt上の問題点候補(事実列挙、追加Trialしない)

1. **Topic Word枠が4/4セットで一度も使われなかった**。Prompt上
   「At most ONE ... may be a Topic Word ... optional, not required」
   という文言が、「使わない」方向にモデルを強く誘導している可能性が
   ある。想定セット4件すべてに記事固有の中心語(sewer/AI agent/
   septic tank/human concierge)がTopic Wordとして含まれていたが、
   実際の出力はこれらをことごとく回避した。
2. **「難しいだけ・記事固有なだけの語を優先しない」という指示が、
   記事のテーマそのものを表す中心語(sewer, treatment plant, main
   artery, personal information等)まで一律に除外する方向に強く
   作用している**可能性がある。既存Production(§9参照)では
   `human concierges`のような記事固有色の強い語がrank1に選ばれて
   おり、新Trialの「汎用性最優先」方針が、テーマ理解に資する語を
   犠牲にしている可能性がある。
3. **Advanced Promptの負例指示(`"take care of", not "take care of
   the rest"`)が守られなかった**実例(§7.1)があり、Prompt内の
   否定的指示(何をしないか)よりも記事本文の表現をそのまま流用する
   傾向が強い可能性がある。
4. **StandardとAdvancedで同一記事から同一句(`take care of the
   rest`)が選ばれ、レベル差別化が機能しなかった**実例が1件確認
   された。
5. Meta StandardとMeta Advancedは同一テーマの記事だが、Standard側で
   選ばれた5個とAdvanced側で選ばれた5個の間に意味的な重なりが
   `raise concerns`程度しかなく、Standard/Advancedで学習の連続性
   (同じテーマを違う難度で反復学習する効果)がほぼ無かった。

以上は事実の列挙であり、追加Trial・仕様修正の実装は行っていない。

---

## §9 既存Production結果との差分(参考、優劣判断なし)

既存Production(`er012_output/e_family_two_level_wiring_01/meta/b1b/
key_phrases/keywords_canonicalized.json`、L方式)のMeta b1b選定5個:
`human concierges`(rank1)/`put on hold`(rank2)/`behind the
curtain`(rank3)/`fill in`(rank4)/`on a user's behalf`(rank5)。

新Trial Meta Advancedの選定5個: `on A's behalf`/`raise concerns`/
`put A on hold`/`fill in`/`appear to be`。

**表面的な字面一致**: `put on hold`↔`put A on hold`、`fill in`↔
`fill in`(完全一致)、`on a user's behalf`↔`on A's behalf`(ほぼ
同一)の3件が、既存Production選定と新Trial選定の両方に共通して出現
した。一方で既存が選んだ`human concierges`(記事の中心的発見)と
`behind the curtain`(記事の結びの比喩)は、新Trialでは選ばれなかった
(いずれも本Trialの想定セットにも含まれていた語)。

同様に既存Production Meta a2の選定5個: `human concierge`/`hand the
call to AI`/`leak outside the company`/`pause the feature`/`feel
safe`。新Trial Meta Standardの選定5個(`tell ... what you need`/
`not always a bad thing`/`contain personal information`/`hand ...
to ...`/`feel safe`)との共通は、`feel safe`(完全一致)と`hand ...
to ...`↔`hand the call to AI`(部分的に近い)の2件のみ。

差の傾向として、既存Productionは記事固有の中心的発見・キーワード
(human concierge等)を上位に選ぶ一方、新Trialはそれらを避けて
より一般的な句(feel safe/fill in/put on hold等)に収束する傾向が
見える(優劣判断はしない、事実の記録のみ)。

---

## §10 cost・latency・model実値

| stage | model実値 | fallback | effort | elapsed | retried | cost_jpy |
|---|---|---|---|---|---|---|
| sewer_standard | gpt-5.6-luna | false | medium | 16.314s | false | 0.2162 |
| sewer_advanced | gpt-5.6-luna | false | medium | 17.02s | false | 0.3004 |
| meta_standard | gpt-5.6-luna | false | medium | 21.911s | false | 0.2921 |
| meta_advanced | gpt-5.6-luna | false | medium | 18.992s | false | 0.3254 |

**合計cost: JPY 1.1341**(予算上限JPY 20以内、4 call全て`gpt-5.6-luna`
で応答、fallbackなし、schema再試行なし)。詳細は`cost.json`/
`outputs/*.json`。

---

## §11 Fable参考評価

### 11.1 一致判定(Fable、同義・学習単位を含む)
- Sewer Standard: instead of(一致)/take care of the rest(学習単位は take care of と同じだが不要語付加=切り方×)/joining together・hard to find・grow old(不一致、汎用句としては妥当)。Topic Word(sewer)未選択。→ **2/5 FAIL**。
- Sewer Advanced: replace A with B(完全一致)/take care of the rest(Standard級かつ不要語付加)/hard to find where A is damaged(記事固有の固定化)/come in・move A closer to B(不一致)。main artery / treatment plant / be connected to / septic tank すべて未選択。→ **1/5 FAIL**。
- Meta Standard: 期待の in other words / put ... on hold / raise concerns / there is nothing wrong with … / AI agent はいずれも未選択。not always a bad thing は意味的に近いが別Phrase、contain personal information はAdvanced期待の personal information に近い。→ **0〜1/5 FAIL**。
- Meta Advanced: raise concerns(raise privacy concerns と同一学習単位、切り方は許容)/put A on hold(一致)/on A's behalf(良い汎用句)/fill in・appear to be(不一致)。behind the curtain / personal information / human concierge 未選択。→ **2/5 FAIL**。
- 全体: 5/20(25%)。目安60%を大きく下回る。

### 11.2 構造的な観察
- **Topic Word枠が4回とも未使用**: 「任意」と書いたため、記事の中心テーマ語(sewer / septic tank / AI agent / human concierge)がすべて落ちた。
- **句の種類が動詞句に偏る**: 「1 Phrase=1学習ポイント」「不要語を付けない」の指示が、名詞複合語(treatment plant / personal information / main artery)や談話標識(in other words)を避ける方向に働いた。
- **レベル配分が期待と逆転**: put ... on hold / raise concerns はStandard期待だったがAdvancedで選ばれ、Standardは tell … what you need / feel safe など基本動詞句に寄った。
- **Prompt内の禁止例が守られない**: Advanced Promptで明示した「take care of the rest ではなく take care of」が、Sewer Standard/Advanced両方で take care of the rest として出現。指示の「例」だけでは抑止できていない。
- 費用¥1.13、4 callとも`gpt-5.6-luna`。Production変更ゼロ確認済み。

## §12 分類

**REJECTED(Trial Prompt v1)**。ユーザーの選定方針そのものではなく、方針をPromptに落とした第1版が狙いのPhraseを再現できなかった(全4セットFAIL、25%)。Production変更なし。

## §13 USER_DECISION_REQUIRED

1. Prompt v2での再Trial(4 call、¥2以内)を承認するか。v2の変更候補(Fable案、答えの漏洩は避け一般例のみ): (a) Topic Wordを「記事に中心テーマ語があれば通常1個含める」に変更、(b) 句の種類の多様性を要求(談話標識/句動詞/コロケーション/再利用しやすい名詞複合語 から偏らずに選ぶ、他分野の一般例で示す)、(c) 「不要語を付けない」の禁止例を、例示ではなく出力後の自己点検指示(各Phraseから記事固有語・余分な語を削れるか確認)に変更、(d) Standard/Advancedの差を「Advancedは基本句(A2級)を避け、Standardで選びそうな句は除く」と明示、(e) 記事固有の固定化(hard to find where A is damaged型)の禁止を明示。
2. 想定セット自体の妥当性確認: Meta Standard期待の in other words / there is nothing wrong with … は談話・定型表現であり、現Promptの「再利用性」定義に含まれることを明記する必要がある(ユーザーの意図確認)。
3. 既存Production Key Phrase仕様との関係: 現行Production(記事固有の中心語を上位に選ぶ傾向)を置き換える前提か、併存(Topic Word枠)か(方針確認、今回は判断不要)。

**Sonnetからの参考事実(判断はしない)**: 全体一致率(目視込み仮判定)
25%(5/20)はユーザー指定の目安60%を大きく下回り、4セット全てが
FAIL基準(2個以下一致)に該当した。Topic Word枠は4/4回とも未使用
だった。既存Prompt文言のまま追加Trialは行っていない
(STOP条件どおり)。

---

## §14 Production変更ゼロの確認

```
$ git diff --stat -- er003_key_words_production.py er003_key_words_min_unit.py \
    er003_b1_p2_keywords.py er003_key_words_canonicalization.py \
    er003_v1_n3_01_scaffold_generate.py er012_e_family_entertainment_two_level_runner_01.py
(差分なし、出力ゼロ行)
```

Key Phrase Production仕様ファイル(上記6ファイル)に本タスクによる
差分は無い。`git diff --stat`を`CURRENT_SPEC.md`/`DECISION_LOG.md`/
`OPEN_ITEMS.md`まで含めて実行すると差分が出るが、これは本タスク開始
前から存在した並行タスク
(`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`)による未commit差分であり、
本タスクではこれらのSSOTファイルを一切編集していない(Read専用)。
commit対象にも含めない。
