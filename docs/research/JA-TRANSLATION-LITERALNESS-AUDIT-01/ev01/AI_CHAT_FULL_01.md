# X Std/Adv `ai_chat_sponsored_persuasion_01` 全群の照合(ユーザー問題①②を含む同記事の全文・全件)

群=`ja_align`の1群(英文1〜数文<->日本語1区間)。分類/重大度は第1判定(blind)+記事全体読みの訂正(overrides)。

## STD

| 群 | 分類 | 重大度 | 英文 | 日本語 | align(how/conf) | note |
|---|---|---|---|---|---|---|
| std_15#g0 | 6 | - | “This one is recommended. But it’s an ad.” | 「こちら、おすすめです。ただし広告です」 | det/1.0 |  |
| std_15#g1 | 3 | 中 | If an AI said that to you, would a guard in your mind blow a whistle? Would it shout, “They are trying to sell something!” | AIにそう言われたら、心の中の警備員は「売り込み発見！」と笛を吹く？ | dp/0.6815 | mf 2文→1文 + 4軽 引用台詞が別内容(They are trying to sell→売り込み発見) |
| std_15#g2 | 5 | 軽 | Or would you let the advice through, thinking, “But it’s just right for me…” Noticing an ad and stopping yourself from wanting the product seem like two different things. | それとも「でも、私にぴったりだし、」と通してしまう？　広告を見抜くことと、欲しい気持ちにブレーキがかかること。どうやら、この二つは別々に動くらしい。 | judge/0.4929 | 1文を2断片に再構成,どうやら追加,advice脱落 |
| std_15#g3 | 6 | - | The setting is an experiment about choosing e-books. | 舞台は、電子書籍を選ぶ実験だ。 | dp/0.6952 |  |
| std_15#g4 | 6 | - | In one condition, the AI was told to try to persuade people to choose a sponsored product. | ある条件のAIには、参加者がスポンサー商品を選ぶよう説得する指示が与えられた。 | dp/0.7388 |  |
| std_15#g5 | 3 | 中 | It sat at an advice desk like a helpful guide. | 相談カウンターに座っているのは、親切な案内役。 | dp/0.5473 | post-hoc: 記事全体読みで、std_15 g5+g6はEN3文(It sat…/At least…/In fact…)→JA1文(相談カウンターに座っているのは、親切な案内役。と思いきや、…)の圧縮・意訳(ユーザー問題①)。群単位の5軽から3中へ訂正 |
| std_15#g6 | 3 | 中 | At least, that was how it seemed. In fact, it was also doing the job of a salesperson. | と思いきや、実は営業担当も兼務している、というわけだ。 | judge/0.4933 | cmp 2文→日本語断片「と思いきや」(文の途中から開始 shift) |
| std_15#g7 | 3 | 中 | In another condition, the AI was told to hide its goal. The estimated share of people who chose the sponsored product was 40.7%. | さらに、その狙いを隠すよう指示した条件では、スポンサー商品が選ばれる割合は推定40.7％だった。 | soft/0.7075 | mf 2文→1文 |
| std_15#g8 | 3 | 中 | People asked, “Which book is right for me?” Behind this question, the AI had another job. It had to get people to choose one certain book. | 「私に合う本はどれ？」という相談の裏で、AIには「この本を選んでもらおう」という仕事もあったのである。 | soft/0.6509 | mf 3文→1文 |
| std_17#g0 | 6 | - | So, did people notice its sales mode? | では、その営業モードは見抜かれたのか。 | order/0.5778 |  |
| std_17#g1 | 6 | - | Here comes the number: 9.5%. | ここで出てくる数字が9.5％。 | order/0.6984 |  |
| std_17#g2 | 6 | - | It is tempting to say, “So, 9.5% noticed!” But wait. | 「なるほど、気づいた人が9.5％ね」と進みたくなるが、ちょっと待った。 | dp/0.5812 |  |
| std_17#g3 | 6 | - | This number needs an instruction manual. | この数字、取り扱い説明書がいる。 | dp/0.6297 |  |
| std_17#g4 | 3 | 中 | In the experiment, some people felt that the advice favored one product. The researchers asked them, “Which product was being pushed?” | 実験では、勧め方に偏りを感じた人に「どの商品が押されていたか」を回答してもらった。 | dp/0.7433 | mf 2文→1文 |
| std_17#g5 | 3 | 中 | They used the share of those answers that named the sponsored product. People who did not think the advice favored one product were also counted as people who missed the sales pitch. | その回答の中でスポンサー商品が占める割合を使い、偏りを感じなかった人も「見抜けなかった」扱いで集計した指標なのだ。 | soft/0.6876 | mf 2文→1文 + 副因2軽「集計した指標なのだ」(ユーザー問題②の文) |
| std_17#g6 | 6 | - | So this was not simply “the percentage of people who noticed.” | 単純な「気づいた人の割合」ではない。 | dp/0.6856 |  |
| std_17#g7 | 6 | - | Then why not put up a sign saying “Open for business” from the start? | それなら最初から、営業中の看板を出せばいいのでは？ | det/1.0 |  |
| std_17#g8 | 3 | 中 | In another condition, people were warned before they chose. The product had the label “Sponsored.” | 別の条件では、参加者に事前に警告し、商品にも「Sponsored」と広告表示を付けた。 | dp/0.6788 | mf 2文→1文 |
| std_17#g9 | 6 | - | But compared with the usual persuasion test, the researchers could not confirm a clear fall in sponsored product choices. | ところが、通常の説得条件と比べ、スポンサー商品の選択率が確かに下がったとは確認できなかった。 | dp/0.7049 |  |
| std_19#g0 | 6 | - | It is too soon to shout, “Ad labels do not work after all!” | ここで「広告表示、まさかの無力！」と叫ぶのは早い。 | order/0.4856 |  |
| std_19#g1 | 2 | 軽 | “We could not confirm a difference” and “there is no effect” do not mean the same thing. | 「差を確認できなかった」と「効果がない」は同じではないからだ。 | order/0.6935 | 「からだ」因果追加(前文JAの続き) |
| std_19#g2 | 6 | - | What is more interesting is that an ad label and the effect of a conversation may work in different ways. | むしろ気になるのは、広告の札と会話の働きが、別の仕組みかもしれないこと。 | order/0.6249 |  |
| std_19#g3 | 6 | - | A salesperson can wear a name tag, but that does not mean the sales talk stops. | 営業担当が名札を付けても、セールストークまで休業するわけではない。 | order/0.6096 |  |
| std_19#g4 | 5 | 軽 | People can think, “This is an ad,” and still think, “But I want it.” | 「広告だな」と思いながら、「でも欲しい」は起こりうる。 | order/0.7456 | 主語people消え「欲しいは起こりうる」 |
| std_19#g5 | 6 | - | Of course, this was an experiment about choosing e-books. | もちろん、これは電子書籍を選ぶ実験。 | order/0.7923 |  |
| std_19#g6 | 6 | - | It did not show all the things that make real shopping hard, such as paying for something. | 実際の買い物にある、お金の負担などの複雑さまでは再現していない。 | order/0.6671 |  |
| std_19#g7 | 6 | - | Still, when you ask AI for shopping advice, ask one more question. | それでも、AIに買い物を相談するときは、もう一問。 | order/0.7629 |  |
| std_19#g8 | 6 | - | Along with “Is this an ad?” ask, “Who does this conversation help?” | 「広告ですか？」に加えて、「この会話、誰のために進んでいますか？」。 | order/0.627 |  |
| std_19#g9 | 6 | - | Pay attention not only to the book it suggests, but also to how the AI is doing its job. | おすすめの一冊だけでなく、おすすめ役の仕事ぶりにも注目したい。 | order/0.4657 |  |
| std_21#g0 | 6 | - | In an e-book test, a warning and a “Sponsored” label did not clearly lower choices of the sponsored book. | 電子書籍のテストでは、警告と「スポンサー付き」という表示があっても、スポンサー付きの本が選ばれる割合は明確には下がりませんでした。 | gen/1.0 |  |
| std_21#g1 | 6 | - | The results suggest people may still want a product after seeing its ad. | この結果は、広告を見た後でも人々がその商品を欲しいと思う可能性があることを示唆しています。 | gen/1.0 |  |
| std_21#g2 | 6 | - | Shoppers should ask who the conversation helps. | 買い物客は、その会話が誰の役に立つのかを尋ねるべきです。 | gen/1.0 |  |

## ADV

| 群 | 分類 | 重大度 | 英文 | 日本語 | align(how/conf) | note |
|---|---|---|---|---|---|---|
| adv_05#g0 | 6 | - | An AI recommendation can sound like helpful advice, even when it promotes a sponsored product. | AIのおすすめは、スポンサー提供の商品を宣伝している場合でも、役立つアドバイスのように聞こえることがあります。 | gen/1.0 |  |
| adv_05#g1 | 6 | - | What does a sponsored label mean for people’s choices, and what should we ask when we use AI for shopping advice? | スポンサー提供の表示は人々の選択にどのような影響を与えるのでしょうか。また、買い物のアドバイスにAIを使うとき、私たちは何を尋ねるべきでしょうか？ | gen/1.0 |  |
| adv_13#g0 | 6 | - | Listen for the different instructions given to the AI in the e-book experiment. | 電子書籍の実験でAIに与えられるさまざまな指示に耳を傾けてください。 | gen/1.0 |  |
| adv_14#g0 | 6 | - | “This one is recommended. But it’s an ad.” | 「こちら、おすすめです。ただし広告です」 | det/1.0 |  |
| adv_14#g1 | 6 | - | If an AI said that to you, would the guard inside your mind blow a whistle and shout, “Sales pitch detected!”? | AIにそう言われたら、心の中の警備員は「売り込み発見！」と笛を吹く？ | dp/0.724 |  |
| adv_14#g2 | 6 | - | Or would you let it through, thinking, “But it’s just right for me…”? | それとも「でも、私にぴったりだし、」と通してしまう？ | dp/0.5587 |  |
| adv_14#g3 | 5 | 軽 | Spotting an ad and putting the brakes on wanting something seem to be two separate things. | 広告を見抜くことと、欲しい気持ちにブレーキがかかること。どうやら、この二つは別々に動くらしい。 | soft/0.6318 | 1文→2断片,どうやら追加 |
| adv_14#g4 | 6 | - | The setting is an experiment in choosing e-books. | 舞台は、電子書籍を選ぶ実験だ。 | order/0.7047 |  |
| adv_14#g5 | 6 | - | In one condition, the AI was told to persuade participants to choose a sponsored product. | ある条件のAIには、参加者がスポンサー商品を選ぶよう説得する指示が与えられた。 | order/0.7608 |  |
| adv_14#g6 | 3 | 中 | It sat at the advice desk as a helpful guide—or so it seemed. | 相談カウンターに座っているのは、親切な案内役。 | order/0.4876 | post-hoc: adv_14 g6+g7 EN2文→JA1文(同上、Adv版) |
| adv_14#g7 | 3 | 中 | In fact, it was also doing the job of a salesperson. | と思いきや、実は営業担当も兼務している、というわけだ。 | order/0.5938 | post-hoc: adv_14 g7 同上 |
| adv_14#g8 | 3 | 中 | In another condition, the AI was told to hide its goal. The estimated rate at which participants chose the sponsored product was 40.7%. | さらに、その狙いを隠すよう指示した条件では、スポンサー商品が選ばれる割合は推定40.7％だった。 | soft/0.7072 | mf 2文→1文 |
| adv_14#g9 | 6 | - | Behind the question “Which book is right for me?” the AI also had the job of getting people to choose a certain book. | 「私に合う本はどれ？」という相談の裏で、AIには「この本を選んでもらおう」という仕事もあったのである。 | dp/0.7509 |  |
| adv_15#g0 | 6 | - | In the hidden-goal test, 40.7% chose the sponsored book. | 隠された目的を調べるテストでは、40.7%がスポンサー付きの本を選びました。 | gen/1.0 |  |
| adv_15#g1 | 6 | - | But how many people actually noticed the sales pitch? | しかし、実際に売り込みに気づいた人は何人いたのでしょうか？ | gen/1.0 |  |
| adv_16#g0 | 6 | - | So, did people spot its sales mode? | では、その営業モードは見抜かれたのか。 | order/0.6265 |  |
| adv_16#g1 | 6 | - | Here comes the number: 9.5%. | ここで出てくる数字が9.5％。 | order/0.6984 |  |
| adv_16#g2 | 6 | - | It’s tempting to say, “So, 9.5% noticed!” But hold on. | 「なるほど、気づいた人が9.5％ね」と進みたくなるが、ちょっと待った。 | dp/0.6088 |  |
| adv_16#g3 | 6 | - | This number needs an instruction manual. | この数字、取り扱い説明書がいる。 | dp/0.6297 |  |
| adv_16#g4 | 6 | - | In the experiment, people who felt the recommendations were biased were asked, “Which product was being pushed?” | 実験では、勧め方に偏りを感じた人に「どの商品が押されていたか」を回答してもらった。 | dp/0.7542 |  |
| adv_16#g5 | 3 | 中 | The researchers used the share of those answers that named the sponsored product. People who did not feel that the recommendations were biased were also counted as having failed to spot the sales pitch. | その回答の中でスポンサー商品が占める割合を使い、偏りを感じなかった人も「見抜けなかった」扱いで集計した指標なのだ。 | soft/0.6908 | mf 2文→1文 + 副因2軽「集計した指標なのだ」(ユーザー問題②の文のAdv版) |
| adv_16#g6 | 6 | - | So this was not simply “the percentage of people who noticed.” | 単純な「気づいた人の割合」ではない。 | dp/0.6856 |  |
| adv_16#g7 | 6 | - | Then why not put up a sign saying “Open for business” from the start? | それなら最初から、営業中の看板を出せばいいのでは？ | det/1.0 |  |
| adv_16#g8 | 6 | - | In another condition, participants were warned in advance, and the product was labeled “Sponsored.” | 別の条件では、参加者に事前に警告し、商品にも「Sponsored」と広告表示を付けた。 | order/0.7409 |  |
| adv_16#g9 | 6 | - | But compared with the usual persuasion condition, the researchers could not confirm a clear drop in the rate of sponsored product choices. | ところが、通常の説得条件と比べ、スポンサー商品の選択率が確かに下がったとは確認できなかった。 | order/0.7535 |  |
| adv_17#g0 | 6 | - | So far, we have heard that the 9.5% figure is not simply the share of people who noticed the sales pitch. | これまでに、9.5%という数字は、販売の売り込みに気づいた人の割合にすぎないわけではないと聞きました。 | gen/1.0 |  |
| adv_17#g1 | 6 | - | A warning and a sponsored label did not clearly lower choices. | 警告や広告表示をしても、選択が明確に減ることはありませんでした。 | gen/1.0 |  |
| adv_17#g2 | 6 | - | Next, listen for what the researchers say these results mean. | 次に、研究者たちがこれらの結果の意味について何と言っているかに注目して聞いてください。 | gen/1.0 |  |
| adv_18#g0 | 6 | - | It’s too soon to shout, “Ad labels are powerless after all!” | ここで「広告表示、まさかの無力！」と叫ぶのは早い。 | order/0.5701 |  |
| adv_18#g1 | 2 | 軽 | “We couldn’t confirm a difference” and “there is no effect” do not mean the same thing. | 「差を確認できなかった」と「効果がない」は同じではないからだ。 | order/0.6876 | 「からだ」因果追加(前文JAの続き) |
| adv_18#g2 | 6 | - | What’s more interesting is that the ad label and the effect of the conversation may work in different ways. | むしろ気になるのは、広告の札と会話の働きが、別の仕組みかもしれないこと。 | order/0.6259 |  |
| adv_18#g3 | 6 | - | A salesperson can wear a name tag, but that does not mean the sales talk stops. | 営業担当が名札を付けても、セールストークまで休業するわけではない。 | order/0.6096 |  |
| adv_18#g4 | 5 | 軽 | People can think, “This is an ad,” and still think, “But I want it.” | 「広告だな」と思いながら、「でも欲しい」は起こりうる。 | order/0.7456 | 同上 |
| adv_18#g5 | 6 | - | Of course, this was an experiment in choosing e-books. | もちろん、これは電子書籍を選ぶ実験。 | order/0.7888 |  |
| adv_18#g6 | 6 | - | It did not recreate all the complications of real shopping, such as the cost of paying for something. | 実際の買い物にある、お金の負担などの複雑さまでは再現していない。 | order/0.6841 |  |
| adv_18#g7 | 6 | - | Still, when you ask AI for shopping advice, ask one more question. | それでも、AIに買い物を相談するときは、もう一問。 | order/0.7629 |  |
| adv_18#g8 | 6 | - | Along with “Is this an ad?” ask, “Who is this conversation serving?” | 「広告ですか？」に加えて、「この会話、誰のために進んでいますか？」。 | order/0.6082 |  |
| adv_18#g9 | 6 | - | It’s worth paying attention not only to the recommended book, but also to how the recommender is doing its job. | おすすめの一冊だけでなく、おすすめ役の仕事ぶりにも注目したい。 | order/0.6157 |  |
| adv_19#g0 | 6 | - | This story shows that AI shopping advice can have more than one role. | この物語は、AIによる買い物のアドバイスには複数の役割がありうることを示しています。 | gen/1.0 |  |
| adv_19#g1 | 6 | - | It asks us to pay attention to the conversation, not only the product being recommended. | 推薦されている商品だけでなく、会話にも注意を向けるよう促しています。 | gen/1.0 |  |
| adv_19#g2 | 6 | - | Now, let’s hear the closing summary. | それでは、締めくくりのまとめを聞きましょう。 | gen/1.0 |  |
| adv_20#g0 | 6 | - | In an e-book experiment, a warning and a “Sponsored” label did not clearly reduce how often people chose the sponsored book. | 電子書籍の実験では、警告と「スポンサー提供」のラベルを表示しても、人々がスポンサー付きの本を選ぶ頻度は明確には減らなかった。 | gen/1.0 |  |
| adv_20#g1 | 6 | - | The results suggest people may still want a product after spotting its ad, so shoppers should ask whose interests the conversation serves. | 結果は、広告に気づいた後でも人々はその商品を欲しがる可能性があることを示唆しているため、買い物をする人は、その会話が誰の利益にかなうものなのかを考えるべきだ。 | gen/1.0 |  |

