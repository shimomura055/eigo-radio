
## STD 全run Key Phrase 5件(正規化後key_phrase)

V0(Phase B既存、Production現行shortlist+現行guidance)最終5: raw bean / push prices up / take time / right away / on a regular basis

| Version | run | Key Phrase 5件(rank順) | pump-fist | run最終gate | 重複QA | 費用 |
|---|---|---|---|---|---|---|
| A | 1 | raw bean / two numbers in the ring / pump one's fist / push prices up / its own hidden clock | 採択 | PASS | REDUNDANCY_PASS | 1.51 |
| A | 2 | raw bean / two numbers in the ring / one's own hidden clock / pump one's fist / roasting | 採択 | PASS | REDUNDANCY_PASS | 1.00 |
| A | 3 | two numbers in the ring / raw-bean / its own hidden clock / pump one's fist / push prices up | 採択 | PASS | REDUNDANCY_PASS | 1.44 |
| B | 1 | two numbers in the ring / raw bean / pump one's fist / one's own hidden clock / right away | 採択 | REDUNDANCY_NG | REDUNDANCY_NG | 1.09 |
| B | 2 | raw-bean / two numbers in the ring / one's own hidden clock / pump one's fist / push prices up | 採択 | CANONICALIZATION_REVIEW_REQUIRED | REDUNDANCY_PASS | 1.66 |
| B | 3 | (なし) | - | SELECTION_INVALID | None | 0.52 |
| C | 1 | two numbers in the ring / pumps its fist / raw-bean / its own hidden clock / right away | 採択 | CANONICALIZATION_INVALID | None | 1.16 |
| C | 2 | raw bean / pump one's fist / two numbers in the ring / push prices up / one's own hidden clock | 採択 | CANONICALIZATION_REVIEW_REQUIRED | REDUNDANCY_PASS | 1.07 |
| C | 3 | raw-bean / two numbers in the ring / its own hidden clock / pump one's fist / push prices up | 採択 | CANONICALIZATION_INVALID | None | 1.23 |

### STD Version別サマリー

| Version | pump-fist採択 | run最終gate完全PASS | Jaccard(平均/各対) | 出現頻度(n=3中) | V0から消えた(全run不在) | V0から残った | V0に無い新規 |
|---|---|---|---|---|---|---|---|
| A | 3/3 | 3/3 | 0.619 ([0.429, 1.0, 0.429]) | two numbers in the ring:3, pump one's fist:3, raw bean:3, its own hidden clock:2, push prices up:2, one's own hidden clock:1, roasting:1 | on a regular basis, right away, take time | push prices up, raw bean | its own hidden clock, one's own hidden clock, pump one's fist, roasting, two numbers in the ring |
| B | 2/3 | 0/3 | 0.667 ([0.667]) | two numbers in the ring:2, pump one's fist:2, raw bean:2, one's own hidden clock:2, right away:1, push prices up:1 | on a regular basis, take time | push prices up, raw bean, right away | one's own hidden clock, pump one's fist, two numbers in the ring |
| C | 3/3 | 0/3 | 0.448 ([0.25, 0.429, 0.667]) | two numbers in the ring:3, raw bean:3, its own hidden clock:2, pump one's fist:2, push prices up:2, pumps its fist:1, right away:1, one's own hidden clock:1 | on a regular basis, take time | push prices up, raw bean, right away | its own hidden clock, one's own hidden clock, pump one's fist, pumps its fist, two numbers in the ring |

### STD A/B/C間の入替わり(頻度合計、同一run数n=3)

| 表現 | A | B | C |
|---|---|---|---|
| raw bean | 3 | 2 | 3 |
| two numbers in the ring | 3 | 2 | 3 |
| pump one's fist | 3 | 2 | 2 |
| push prices up | 2 | 1 | 2 |
| its own hidden clock | 2 | 0 | 2 |
| one's own hidden clock | 1 | 2 | 1 |
| right away | 0 | 1 | 1 |
| pumps its fist | 0 | 0 | 1 |
| roasting | 1 | 0 | 0 |

## ADV 全run Key Phrase 5件(正規化後key_phrase)

V0(Phase B既存、Production現行shortlist+現行guidance)最終5: lag / price tag / show up / come down / come with

| Version | run | Key Phrase 5件(rank順) | pump-fist | run最終gate | 重複QA | 費用 |
|---|---|---|---|---|---|---|
| A | 1 | lag / show up / be behind price increases / in the ring / raw beans | - | PASS | REDUNDANCY_PASS | 0.84 |
| A | 2 | pump one's fist / in the ring / be behind price increases / lag / price measure | 採択 | PASS | REDUNDANCY_PASS | 0.79 |
| A | 3 | lag / come down / pump one's fist / be behind price increases / price tag | 採択 | PASS | REDUNDANCY_PASS | 0.87 |
| B | 1 | lag / show up / be behind / pump its fist / price tag | 採択 | CANONICALIZATION_INVALID | None | 1.09 |
| B | 2 | show up / lag / pump one's fist / in the ring / price tag | 採択 | PASS | REDUNDANCY_PASS | 0.92 |
| B | 3 | lag / be behind price increases / raw beans / in the ring / pump one's fist | 採択 | PASS | REDUNDANCY_PASS | 0.85 |
| C | 1 | lag / show up / retail price / be behind / pump one's fist | 採択 | CANONICALIZATION_INVALID | None | 1.28 |
| C | 2 | show up / lag / price measure / be behind price increases / in the ring | - | PASS | REDUNDANCY_PASS | 0.81 |
| C | 3 | show up / be behind / lag / price measure / come down | - | CANONICALIZATION_INVALID | None | 0.99 |

### ADV Version別サマリー

| Version | pump-fist採択 | run最終gate完全PASS | Jaccard(平均/各対) | 出現頻度(n=3中) | V0から消えた(全run不在) | V0から残った | V0に無い新規 |
|---|---|---|---|---|---|---|---|
| A | 2/3 | 3/3 | 0.369 ([0.429, 0.25, 0.429]) | lag:3, be behind price increases:3, in the ring:2, pump one's fist:2, show up:1, raw beans:1, price measure:1, price tag:1, come down:1 | come with | come down, lag, price tag, show up | be behind price increases, in the ring, price measure, pump one's fist, raw beans |
| B | 3/3 | 2/3 | 0.323 ([0.429, 0.111, 0.429]) | lag:3, show up:2, price tag:2, in the ring:2, pump one's fist:2, pump its fist:1, be behind:1, raw beans:1, be behind price increases:1 | come down, come with | lag, price tag, show up | be behind, be behind price increases, in the ring, pump its fist, pump one's fist, raw beans |
| C | 1/3 | 1/3 | 0.369 ([0.25, 0.429, 0.429]) | show up:3, lag:3, be behind:2, price measure:2, retail price:1, pump one's fist:1, in the ring:1, be behind price increases:1, come down:1 | come with, price tag | come down, lag, show up | be behind, be behind price increases, in the ring, price measure, pump one's fist, retail price |

### ADV A/B/C間の入替わり(頻度合計、同一run数n=3)

| 表現 | A | B | C |
|---|---|---|---|
| lag | 3 | 3 | 3 |
| show up | 1 | 2 | 3 |
| be behind price increases | 3 | 1 | 1 |
| in the ring | 2 | 2 | 1 |
| pump one's fist | 2 | 2 | 1 |
| be behind | 0 | 1 | 2 |
| price measure | 1 | 0 | 2 |
| price tag | 1 | 2 | 0 |
| come down | 1 | 0 | 1 |
| raw beans | 1 | 1 | 0 |
| pump its fist | 0 | 1 | 0 |
| retail price | 0 | 0 | 1 |

## 選定理由(LLM出力 selection_reason / listening_difficulty_reason、全run全件)


### adv_A_run1
- r1 `lag` (word/general_unknown_word/important) : 値下がりが店頭価格に反映されるまでの遅れを示す、記事の中心的な語。 | 聞き取り困難: 短い語だが、意味を知らないと価格変化の説明の要点を取り逃しやすい。
- r2 `show up` (phrasal_verb/compact_listening_pattern/important) : 生豆の価格が小売価格に反映される、という記事の重要なつながりを表す。 | 聞き取り困難: show と up が続く音声ではまとまりを聞き取りにくく、意味も「現れる」以外に広がる。
- r3 `be behind price increases` (collocation/causal_contrast/important) : 豆の購入費や人件費などが値上がりの要因だった、という説明をつかむ助けになる。 | 聞き取り困難: behind を場所の「後ろ」と取ると、原因を表す意味に切り替えにくい。
- r4 `in the ring` (idiom/figurative_emotional/important) : 二つの価格の数字を単純に比べないよう促す、比喩的な表現。 | 聞き取り困難: 直訳ではボクシングのリングを思い浮かべやすく、比較する意味を一度で取りにくい。
- r5 `raw beans` (noun_phrase/domain_expression/topic) : 生豆の価格と店頭のコーヒー価格の違いを追うために重要な、この記事の題材に関わる語。 | 聞き取り困難: 単語自体は推測しやすいが、raw が焙煎前の状態を指すと分からないと価格の話の対象を取り違えやすい。

### adv_A_run2
- r1 `pump one's fist` (idiom/figurative_emotional/important) : 財布が喜ぶ様子を表す比喩で、冒頭の感情や記事の軽い語り口をつかむ助けになる。 | 聞き取り困難: 文字どおりの動作ではなく、比喩として「喜ぶ」という意味を音声だけで取る必要がある。
- r2 `in the ring` (idiom/figurative_emotional/important) : 二つの数字をそのまま比べてはいけない、という記事の重要な注意を理解する助けになる。 | 聞き取り困難: 数字をボクシングのリングに入れる比喩から、比較する意味を補う必要がある。
- r3 `be behind price increases` (collocation/causal_contrast/important) : カフェの値上がりに何が関係していたかを示す、記事後半の原因説明を押さえられる。 | 聞き取り困難: be behind が「後ろにいる」ではなく「原因になっている」を表し、音声では意味を取り違えやすい。
- r4 `lag` (word/general_unknown_word/important) : 豆の価格が下がっても店頭価格の変化には時間がかかる、という記事の中心的な考えを短く表す。 | 聞き取り困難: 音が短く、別の語と聞き分けにくい場合があり、価格の文脈での意味も瞬時には浮かびにくい。
- r5 `price measure` (noun_phrase/domain_expression/topic) : 記事で紹介される価格の数字が、カフェの一杯の値段そのものとは限らないと理解する助けになる。 | 聞き取り困難: measure が「測ること」ではなく、ここでは価格を表す指標の意味で使われている。

### adv_A_run3
- r1 `lag` (word/general_unknown_word/important) : 値下がりが店頭価格に反映されるまでの遅れを表す、記事の要点となる語。 | 聞き取り困難: 短い語だが、音声だけでは意味がすぐ浮かばず、価格の変化に関する説明を取り違える可能性がある。
- r2 `come down` (phrasal_verb/compact_listening_pattern/important) : 豆の価格が下がったことと、カップの値段への期待をつなぐ表現。 | 聞き取り困難: come と down の組み合わせから、値段が下がる意味を瞬時に取れないことがある。
- r3 `pump one's fist` (idiom/figurative_emotional/important) : 価格下落の知らせを聞いたときの喜びを、記事らしいユーモアで表す。 | 聞き取り困難: 単語自体は比較的聞き取りやすくても、財布が拳を突き上げるという比喩は一度聞いただけでは意図を取りにくい。
- r4 `be behind price increases` (collocation/causal_contrast/important) : 豆の購入費や人件費などが値上がりの原因だったという説明を捉える助けになる。 | 聞き取り困難: had been behind が続く音声では、behind を場所の意味に取って原因を表す用法を逃しやすい。
- r5 `price tag` (noun_phrase/domain_expression/topic) : 記事の題名にも関わり、豆の価格が実際の店頭価格にどう反映されるかを追うための中心語。 | 聞き取り困難: 語自体は比較的推測しやすいが、繰り返し登場するため、聞き逃すと話題の軸を見失いやすい。

### adv_B_run1
- r1 `lag` (word/general_unknown_word/important) : 豆の価格が店頭価格に届くまでの時間差を表し、記事の中心的な説明を理解する鍵になる。 | 聞き取り困難: 短い語だが、音声だけでは聞き落としやすく、価格の話での意味をすぐ捉えにくい。
- r2 `show up` (phrasal_verb/compact_listening_pattern/important) : 生豆の価格変化が小売価格にどうつながるかを表す重要な句。 | 聞き取り困難: よくある句動詞だが、ここでは「現れる」ではなく価格に変化が表れる意味で使われている。
- r3 `be behind` (collocation/causal_contrast/important) : カップや人件費などが値上がりにつながったという因果関係を捉えるのに役立つ。 | 聞き取り困難: behind の位置関係の意味ではなく、原因や背景を表す用法なので、音声だけでは意味を取り違えやすい。
- r4 `pump its fist` (idiom/figurative_emotional/important) : 値下がりの知らせを受けたときの、財布が喜ぶという記事冒頭の比喩をつかめる。 | 聞き取り困難: 財布がこぶしを突き上げるという擬人化が使われており、文字どおりの意味では内容を取りにくい。
- r5 `price tag` (noun_phrase/domain_expression/topic) : 記事では値札の価格がいつ変わるのかが繰り返し話題になり、題材を追う助けになる。 | 聞き取り困難: 語自体は比較的推測しやすいが、記事中で何度も使われる中心表現。

### adv_B_run2
- r1 `show up` (phrasal_verb/compact_listening_pattern/important) : 豆の価格が小売価格に反映されるまでの時間差を説明する表現。 | 聞き取り困難: 「現れる」以外に価格へ反映される意味があり、音声だけでは取りにくい。
- r2 `lag` (word/general_unknown_word/topic) : 価格がすぐには変わらないという記事の中心的な考えを表す。 | 聞き取り困難: 短い語だが、音声だけでは意味が結びつかない可能性がある。
- r3 `pump one's fist` (idiom/figurative_emotional/important) : 値下がりの知らせに財布が喜ぶという冒頭の比喩を理解できる。 | 聞き取り困難: 財布が拳を突き上げるという比喩で、文字どおりの意味から意図を取りにくい。
- r4 `in the ring` (idiom/figurative_emotional/important) : 二つの価格の数字を単純に比べないよう促す箇所の比喩。 | 聞き取り困難: 「リングの中で」という字義どおりの意味では、比較の意図をつかみにくい。
- r5 `price tag` (noun_phrase/domain_expression/important) : 記事で繰り返される、店で商品に付いた価格を指す語。 | 聞き取り困難: 語自体は比較的推測しやすいが、記事の中心となる対象を示す。

### adv_B_run3
- r1 `lag` (word/general_unknown_word/topic) : 値下がりが店頭価格にすぐ反映されないという記事の中心的な考えを表す。 | 聞き取り困難: 短い語だが、音声だけでは「遅れ」という意味をすぐ取れない可能性がある。
- r2 `be behind price increases` (collocation/causal_contrast/important) : カップや人件費などが値上がりの原因になっていた、という記事の説明をつかむのに役立つ。 | 聞き取り困難: behind が位置ではなく、原因や背景を表すため、音声だけでは意味を取り違えやすい。
- r3 `raw beans` (noun_phrase/domain_expression/important) : 生豆の価格が小売価格に反映されるまで時間がかかる、という本文の説明に欠かせない。 | 聞き取り困難: 個々の語は比較的わかりやすいが、コーヒー豆の価格の話で何を指すか聞き分ける必要がある。
- r4 `in the ring` (idiom/figurative_emotional/important) : 二つの価格の数字を比べる前に注意を促す比喩表現で、話の展開を追う助けになる。 | 聞き取り困難: 文字どおりの「リングの中」と受け取ると、数字を比べる場面とのつながりを取りにくい。
- r5 `pump one's fist` (idiom/figurative_emotional/important) : 値下がりの知らせを聞いた人の喜びを描く、記事冒頭の印象的な比喩。 | 聞き取り困難: 財布がこぶしを突き上げるという擬人化なので、語を聞いただけでは意図をつかみにくい。

### adv_C_run1
- r1 `lag` (word/general_unknown_word/topic) : 価格が下がっても店頭価格にはすぐ反映されないという、記事の中心となる話をつかむ手がかり。 | 聞き取り困難: 短い語だが、価格の文脈で「遅れ」を表す意味を一度で取れない可能性がある。
- r2 `show up` (phrasal_verb/compact_listening_pattern/important) : 生豆の価格変化が小売価格に反映される流れを説明する表現。 | 聞き取り困難: 「現れる」以外にも使われる句動詞で、価格に反映される意味を即座に取りにくい。
- r3 `retail price` (noun_phrase/domain_expression/important) : 生豆の価格と店頭での販売価格の違いを追ううえで重要な語。 | 聞き取り困難: retail の意味を聞き取れないと、どの価格の話か取り違える可能性がある。
- r4 `be behind` (collocation/causal_contrast/important) : 値上がりの原因を述べる箇所の因果関係を理解するのに役立つ。 | 聞き取り困難: behind を位置関係ではなく「原因となっている」と取る必要がある。
- r5 `pump one's fist` (idiom/figurative_emotional/important) : 財布が喜ぶという導入のユーモアや感情をつかめる表現。 | 聞き取り困難: 財布を人のように描く比喩であり、文字どおりの動作だけでは意味が取りにくい。

### adv_C_run2
- r1 `show up` (phrasal_verb/compact_listening_pattern/important) : 生豆の価格変化が店頭価格に反映されることを理解する中心表現。 | 聞き取り困難: show と up の組み合わせから「価格に反映される」と瞬時に取りにくい。
- r2 `lag` (word/general_unknown_word/topic) : 値下がりが店頭価格にすぐ表れないという、記事全体の中心となる考えをつかめる。 | 聞き取り困難: 短い語だが、音声では聞き逃しやすく、遅れを表す意味も即座に出にくい。
- r3 `price measure` (noun_phrase/domain_expression/important) : 記事で報告される価格と、カフェの一杯の価格が同じものではないと理解する助けになる。 | 聞き取り困難: measure が「測定」なのか「指標」なのか、音声だけでは意味を決めにくい。
- r4 `be behind price increases` (collocation/causal_contrast/important) : コーヒー豆の購入費などが値上げの原因になったという説明をつかめる。 | 聞き取り困難: behind を位置の意味に取ると、原因を表す用法に気づきにくい。
- r5 `in the ring` (idiom/figurative_emotional/important) : 異なる二つの価格の数字を安易に比べないよう促す箇所の意味を取れる。 | 聞き取り困難: 字面どおりの「リングの中」と比喩的な比較の意味が結びつきにくい。

### adv_C_run3
- r1 `show up` (phrasal_verb/compact_listening_pattern/important) : 豆の価格変化が小売価格に反映される、という記事の中心的なつながりを表す。 | 聞き取り困難: show up は「現れる」以外の意味もあり、価格に反映されるという用法は音声だけでは取りにくい。
- r2 `be behind` (collocation/causal_contrast/important) : 値上がりの原因を説明する表現で、記事後半の因果関係をつかむ助けになる。 | 聞き取り困難: behind を「後ろにいる」と取ると、原因を表す意味にすぐ結びつきにくい。
- r3 `lag` (word/general_unknown_word/important) : 豆の価格が小売価格に反映されるまでの遅れが、記事の主要な説明になっている。 | 聞き取り困難: 短い語だが、音声で聞き慣れないと意味を取れず、価格変化の時期をめぐる話を追いにくくなる。
- r4 `price measure` (noun_phrase/domain_expression/topic) : 記事で報告される価格と、店で飲むコーヒーの価格との違いを追う手がかりになるため、topic項目として選定。 | 聞き取り困難: 一般的な measure の意味から、価格の動きを表す指標という用法を音声だけで判断しにくい。
- r5 `come down` (phrasal_verb/compact_listening_pattern/important) : コーヒー価格が下がったという話を、店頭価格の話と区別して追う助けになる。 | 聞き取り困難: come down の複数の意味の中から、価格が下がる意味を瞬時に選びにくい。

### std_A_run1
- r1 `raw bean` (technical_term/domain_expression/topic) : コーヒー豆の仕入れ価格と店頭価格の違いを追うための、記事の中心となる表現。 | 聞き取り困難: raw が「生の」ではなく、焙煎前の豆を指すことを音声だけで判断しにくい。
- r2 `two numbers in the ring` (idiom/causal_contrast/important) : 市場価格と店頭価格をすぐに比べないよう促す比喩で、記事の比較の仕方に関わる。 | 聞き取り困難: 数字をリングに入れるという文字どおりの意味ではなく、ボクシングの比喩として処理する必要がある。
- r3 `pump one's fist` (idiom/figurative_emotional/important) : 豆の値下がりを聞いたときの、財布が喜ぶというユーモラスな反応を表す。 | 聞き取り困難: 財布が拳を突き上げるという擬人化なので、聞いたままでは意図を取りにくい。
- r4 `push prices up` (phrasal_verb/causal_contrast/important) : カフェの値上げにつながった複数のコストを説明する、原因と結果を結ぶ表現。 | 聞き取り困難: push が物を押す意味ではなく、価格を上げる意味で使われている。
- r5 `its own hidden clock` (idiom/figurative_emotional/important) : 店頭の値札が市場ニュースとは別の時間差で変わる、記事の締めの考えを表す。 | 聞き取り困難: 時計の話ではなく、値段が変わるまでの独自の時間差を表す比喩。

### std_A_run2
- r1 `raw bean` (technical_term/domain_expression/topic) : 生豆の価格と店頭の価格の違いが記事の中心なので、意味を押さえると本文全体を追いやすくなります。 | 聞き取り困難: raw と bean が続く音を一度で処理し、焙煎前の豆を指すと判断する必要があります。
- r2 `two numbers in the ring` (idiom/causal_contrast/important) : 二つの価格指標をすぐ比較すべきでないという記事の注意点に関わる表現です。 | 聞き取り困難: 数字がリングに入るという比喩から、比較する意味を音声だけでつかむのは難しめです。
- r3 `its own hidden clock` (idiom/figurative_emotional/important) : 市場の価格変化が店頭価格に届くまで時間差がある、という記事の結論を支える表現です。 | 聞き取り困難: 価格に時計があるという比喩を、実際の時計ではなく価格が動く時間差として捉える必要があります。
- r4 `pump its fist` (idiom/figurative_emotional/important) : 値下がりを聞いたときの喜びを表す、記事冒頭の印象的な表現です。 | 聞き取り困難: 財布が拳を突き上げるという擬人化を、喜びの表現として理解する必要があります。
- r5 `roasting` (technical_term/domain_expression/important) : 豆を仕入れてから店頭価格になるまで時間がかかる理由の一つを理解する助けになります。 | 聞き取り困難: コーヒーの加工工程を指す語で、音声では意味を即座に結び付けにくい場合があります。

### std_A_run3
- r1 `two numbers in the ring` (idiom/figurative_emotional/important) : 価格を比べる段落の要点に関わる比喩で、意味を取り違えると比較の話が追いにくくなります。 | 聞き取り困難: 数字をリングに入れるという表現から、比較する意味を音声だけで推測しにくいです。
- r2 `raw-bean` (technical_term/domain_expression/topic) : 生豆の価格が店頭価格に反映されるまでの時間が記事の中心テーマです。 | 聞き取り困難: raw beanがコーヒー業界で焙煎前の豆を指すと、音声だけではすぐに分からない可能性があります。
- r3 `its own hidden clock` (idiom/figurative_emotional/important) : 記事の結論を表す比喩で、相場の変化と店頭価格の動きにずれがあることを捉えるのに役立ちます。 | 聞き取り困難: 値札に時計があるという比喩から、価格が変わる時期のずれを聞き取る必要があります。
- r4 `pump one's fist` (idiom/figurative_emotional/important) : 財布が喜ぶという擬人化が冒頭のユーモアを作り、値下がりへの期待を示しています。 | 聞き取り困難: 財布が拳を突き上げるという文字どおりではない表現なので、比喩だと気づきにくいです。
- r5 `push prices up` (phrasal_verb/causal_contrast/important) : 値上がりの原因を述べる表現で、記事中の因果関係をつかむ助けになります。 | 聞き取り困難: 短い句ですが、pushが価格上昇の原因となる意味で使われていることを聞き取る必要があります。

### std_B_run1
- r1 `two numbers in the ring` (idiom/figurative_emotional/important) : 二つの指標を比べるなという意味が比喩に隠れており、記事の説明を追ううえで重要。 | 聞き取り困難: 聞き慣れない比喩なので、音声だけでは数字を比べる話だとすぐ結びつかない可能性がある。
- r2 `raw bean` (technical_term/domain_expression/topic) : 記事で扱う焙煎前の豆の価格を指し、店頭価格との違いや値下がりの遅れを理解する鍵になる。 | 聞き取り困難: raw と bean が続く複合語で、初回では価格の対象が何かを取り違える可能性がある。
- r3 `pump one's fist` (idiom/figurative_emotional/important) : 財布が喜ぶという擬人化で、記事冒頭のユーモアと値下がりへの反応を伝える。 | 聞き取り困難: 財布が実際に拳を握るのではなく喜びを表す比喩なので、一度聞いただけでは意味を取りにくい。
- r4 `its own hidden clock` (idiom/figurative_emotional/important) : コーヒーの店頭価格には市場価格とは別の動き方がある、という記事のまとめを表す。 | 聞き取り困難: hidden clock は実際の時計ではなく価格変化のタイミングを指すため、比喩の解釈が必要。
- r5 `right away` (idiom/compact_listening_pattern/important) : 豆の価格が下がっても店の価格はすぐには変わらない、という中心的な対比に関わる。 | 聞き取り困難: 短い定型表現で、音声では語のまとまりを聞き逃すと価格が変わる時期を取り違えやすい。

### std_B_run2
- r1 `raw-bean` (technical_term/domain_expression/topic) : 店頭価格と生豆の価格を区別する記事の中心語で、知っていると説明の流れを追いやすくなる。 | 聞き取り困難: raw と bean が続く複合語で、raw が豆の加工状態を表すと音声だけで即座に判断しにくい。
- r2 `two numbers in the ring` (idiom/figurative_emotional/important) : 異なる種類の価格を早まって比べないという記事の注意点を理解する助けになる。 | 聞き取り困難: 数字をリングに入れるという比喩から、価格の比較を指すと一度で推測しにくい。
- r3 `its own hidden clock` (noun_phrase/figurative_emotional/important) : 値札の変化には市場ニュースとは別の時間差があるという結論をつかみやすくする。 | 聞き取り困難: hidden clock は文字どおりの時計ではなく価格反映の遅れを表すため、比喩の意図を聞き逃しやすい。
- r4 `pump one's fist` (idiom/figurative_emotional/important) : 値下がりを聞いた財布が喜ぶという冒頭のユーモアを理解できる。 | 聞き取り困難: 財布がこぶしを突き上げるという擬人化で、単語を聞き取れても意図がすぐには伝わりにくい。
- r5 `push prices up` (phrasal_verb/causal_contrast/important) : カフェの価格を上げた要因について述べる箇所の因果関係をつかみやすくする。 | 聞き取り困難: 動詞と目的語の後に up が続くため、音声ではひとまとまりの「値上げする」という意味を捉えにくいことがある。

### std_B_run3: 選定structure INVALID(項目なし)

### std_C_run1
- r1 `two numbers in the ring` (idiom/causal_contrast/important) : 数字をリングで戦わせるという比喩は意味を推測しにくく、記事の比較上の注意を理解する助けになる。 | 聞き取り困難: 語自体は基本的でも、比喩の意図は一度聞いただけではつかみにくい。
- r2 `pumps its fist` (idiom/figurative_emotional/important) : 財布を人のように描く表現で、値下がりを喜ぶ導入の感情が伝わる。 | 聞き取り困難: 単語ごとの意味から、財布が喜ぶという比喩をすぐに結びつけにくい。
- r3 `raw-bean` (technical_term/domain_expression/topic) : 生豆の価格と店頭価格の違いが記事の中心で、事前に意味を知ると本文全体を追いやすい。 | 聞き取り困難: ハイフンを含む複合語で、音声では一語のまとまりとして聞き取りにくいことがある。
- r4 `its own hidden clock` (idiom/figurative_emotional/important) : 値札の変化には市場価格とは別の時間差がある、という記事の結論を表す。 | 聞き取り困難: 時計を時間差の比喩として使っているため、文字どおりの意味だけでは意図を取りにくい。
- r5 `right away` (idiom/compact_listening_pattern/important) : 価格がすぐには変わらないという時間の説明をつかむのに役立つ、汎用性の高い表現。 | 聞き取り困難: 短い定型句で、音声ではまとまりとして認識できないと意味を取り逃しやすい。

### std_C_run2
- r1 `raw bean` (technical_term/domain_expression/topic) : 生豆の価格と店頭価格の違いが、記事の中心的な話題を追う手がかりになる。 | 聞き取り困難: raw と bean が続く複合語で、音声だけだと一語のまとまりとして取りにくいことがある。
- r2 `pump one's fist` (idiom/figurative_emotional/important) : 価格が下がると聞いた人の期待を、ユーモラスに表す重要な比喩。 | 聞き取り困難: 直訳の意味と文脈上の意味が異なり、短い表現でも一度聞いただけでは取り違えやすい。
- r3 `two numbers in the ring` (idiom/causal_contrast/important) : 異なる種類の価格データをすぐに比べないという記事の説明を理解する助けになる。 | 聞き取り困難: 数字をリングに入れるという比喩は、語句だけから意図を推測しにくい。
- r4 `push prices up` (phrasal_verb/causal_contrast/important) : 複数の費用が価格上昇につながったという因果関係を理解するのに役立つ。 | 聞き取り困難: push と up が離れて聞こえる場合があり、句動詞としてまとまりを取りにくい。
- r5 `its own hidden clock` (noun_phrase/figurative_emotional/important) : 市場価格の動きと店頭価格の反映時期にずれがある、という記事の要点を印象づける比喩。 | 聞き取り困難: 時計の比喩が価格の反映の遅れを指すことは、表現だけではすぐには分かりにくい。

### std_C_run3
- r1 `raw-bean` (technical_term/domain_expression/topic) : 生豆と店頭価格の違いが、記事の価格差や反映の遅れを追う手がかりになる。 | 聞き取り困難: 日常語の raw と bean が結び付いた記事固有の用法で、音声では一語の複合表現として処理しにくい。
- r2 `two numbers in the ring` (idiom/figurative_emotional/important) : 市場価格と店頭価格をすぐ比較しない、という説明の要点を担う。 | 聞き取り困難: 数字をリングに入れるという比喩から、比較の意味を音声だけで推測しにくい。
- r3 `its own hidden clock` (idiom/figurative_emotional/important) : 価格が市場の動きと同時には変わらないという、記事の結論を表す。 | 聞き取り困難: 価格に時計があるという比喩で、直訳から意味をつかみにくい。
- r4 `pump one's fist` (idiom/figurative_emotional/important) : 豆の価格が下がったと聞いたときの、消費者の反応を表す。 | 聞き取り困難: 財布がこぶしを突き上げるという擬人化は、文字通りの意味では理解できない。
- r5 `push prices up` (phrasal_verb/causal_contrast/important) : 複数の費用が価格上昇につながったという因果関係をつかめる。 | 聞き取り困難: 動詞と副詞の結び付きに気付きにくいと、価格が上がった理由を聞き逃すことがある。