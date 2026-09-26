# analysis.md (Sewer)

NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01。採否推奨は書かない(客観データと
所見のみ、Sonnet仮分類)。

## 客観指標

| | Input(Advanced相当) | Band 6,000 | Band 10,000 | Band 14,000 |
|---|---|---|---|---|
| word_count | 328 | 330 | 336 | 339 |
| sentence_count | 23 | 23 | 23 | 23 |
| avg_sentence_length_words | 14.26 | 14.35 | 14.61 | 14.74 |
| subordinators_per_100_words | 1.83 | 1.82 | 2.68 | 2.06 |
| flesch_kincaid_grade_heuristic | 7.6 | 7.35 | **7.81** | 6.9 |
| paragraph_count | 10 | 10 | 10 | 10 |
| 生のBand超過語数 | - | 9 | 4 | 2 |

段落数・文数は4条件とも完全一致(10段落・23文)。要約化・断片化は観測
されなかった。

**注目点**: Band 10,000のFK概算(7.81)はInput(7.6)より**高い**(=難化)。
これは残存語数が減った(9→4)にもかかわらず起きている逆転現象であり、
下記「Fact/意味変化」で説明する「septicを避けるための説明的な言い換え」
が原因と見られる(subordinators_per_100_wordsもBand 10,000だけ2.68と
他条件[1.82〜2.06]より高く、従属節が増えたことと整合する)。

## 生のBand超過語(rank付き)とSonnet分類

| Word | Rank | 6,000 | 10,000 | 14,000 | 分類 | 理由 |
|---|---|---|---|---|---|---|
| faraway | >20,000(zipf2.99) | O | - | - | 推測容易な複合語 | far + away、意味は容易に推測できる。 |
| septic | >20,000(zipf3.21) | O | - | O | **実質超過語(境界)** | 語根そのもので、既知の簡単な語からの透明な派生・複合ではない。日本語では「浄化槽」という訳語はあるが「セプティック」という定着した外来語ではないため、除外条件(3)にも当てはまらない。記事の主題そのものを表す語であり、除外条件のいずれにも属さないまま3条件中2条件(6,000・14,000)で保持されている(下記Fact節参照)。 |
| invisible | 6,153 | O | - | - | 境界(推測容易な派生、僅差) | in-(否定接頭辞)+ visible(既知語)。ただし6,000のすぐ外(153位差)で、教育的には独立見出し語として扱われることが多く判断が割れうる。 |
| convenience | 6,887 | O | - | - | 境界(派生、判断が割れうる) | convenient(既知語と推定)+ -ence(名詞化接尾辞)。-enceによる品詞転換は「透明」と言い切れるかは判断が割れる。 |
| flush | 9,610 | O | - | - | **実質超過語** | 語根そのもの、除外条件のいずれにも該当しない(日本語の「フラッシュ」はカメラ用法が主で、トイレの意味では定着していない)。 |
| artery | 12,006 | O | O | - | **実質超過語** | 語根そのもの、除外条件のいずれにも該当しない。記事の中心比喩("invisible main artery")の核。 |
| sewer | 12,324 | O | O | - | **実質超過語** | 語根そのもの("sew"[縫う]とは無関係の別語根、派生ではない)。記事の主題語そのもの。 |
| sewers | 12,324(lemma) | O | O | - | **実質超過語** | sewerの複数形(lemma処理で同一視)。 |
| wastewater | 18,216 | O | O | O | 推測容易な複合語(Prompt承認例そのもの) | waste + water。Promptが除外条件(2)の例として明示した語そのもの。 |

**実質超過語数(除外理由の付かない語、境界を除く)**:
- Band 6,000 = **4語相当**(septic / flush / artery / sewer+sewers)。
  境界2語(invisible/convenience)を含めても6語相当。
- Band 10,000 = **2語相当**(artery / sewer+sewers)。
- Band 14,000 = **1語**(septic)。

Sewer記事は、Metaと異なり**3条件すべてで実質超過語が残った**(0にはならな
かった)。記事の主題(下水道工学)そのものを表す語(sewer/artery/flush/
septic)が、除外条件(固有名詞・推測容易な派生複合・日本語定着語)のいず
れにも当てはまらないまま、Bandを問わず高頻度で使われ続けている。

## Fact/意味変化(段落単位、Input→各Band対応表)

**最重要所見**: Band 10,000のみ、引用句"combined septic tank,"が本文から
完全に消えた(`fact_tokens_check`で`quoted_strings_match=false`と機械
検出済み)。

| # | Input | Band 6,000 | Band 10,000 | Band 14,000 | 意味差 |
|---|---|---|---|---|---|
| 1 | "combined septic tank,"(引用句) | "combined septic tank,"(維持) | **"a combined tank that cleans household wastewater"(引用句が説明句へ置換、"septic"消失)** | "combined septic tank"(維持) | **Band 10,000のみminor〜要注意**(具体的な技術用語"septic tank"という呼称自体が失われ、説明的な言い換えに置き換わった。下水処理の仕組みという意味自体は保たれているが、記事が実際に使われている用語[septic tank]を報じているという事実精度がこの1文で下がる) |
| 2 | "combined septic tanks" | "combined septic tanks"(維持) | "combined wastewater treatment tanks"(語彙置換、意味は同じ) | "combined septic tanks"(維持) | minor(用語統一の観点でBand 10,000のみ一貫して"septic"を避けている) |
| 13 | "combined septic tank is a small water treatment facility" | "small water treatment place"(facility→place、意味変化なし) | "small place near a home that cleans water"(同上、説明的だが意味は同じ) | "small place for cleaning water near a home"(同上) | none |
| その他 | artery比喩・washing machine比喩・flush等 | 全て維持(下記Storytelling参照) | 全て維持 | 全て維持 | none |

`fact_tokens_check`: Band 6,000/14,000は`overall_fact_tokens_match=
true`(Inputと完全一致)。**Band 10,000のみ`quoted_strings_match=false`
(`overall_fact_tokens_match=false`)**、上記の通り引用句消失が原因(コード
による自動検出、目視でも確認済み)。数字・固有名詞候補の不一致は無し。

## English quality(FAIL条件の逐語引用)

- **Band 10,000 P1**(逐語引用): "When news reports speak of a combined
  tank that cleans household wastewater, you may expect a story about
  two towns becoming one." — "septic"という1語を避けるために、"a
  combined tank that cleans household wastewater"という説明的な関係節
  を追加している。委任文のFAIL条件「冗長説明だらけ」ほど反復的ではない
  (1箇所のみ)が、「1つの難語を長い説明句で回避する」という禁止パターン
  に該当する具体例であり、記事冒頭の主題提示という重要な文でこれが起きた
  点は注意が必要。文法は破綻しておらず、教材として使えないほどではない
  (完全FAILではなく「軽度〜要注意」として記録)。
- 他の箇所・他の2条件ではFAIL条件に該当する逐語引用は見つからなかった。
- Band 10,000で従属節が増えた(subordinators_per_100_words 2.68、他条件
  1.82〜2.06)ことは、上記の説明的言い換えと整合する客観的な裏付けである。

## Storytelling

- 中心比喩("invisible main artery"の見出し、"giant town washing
  machine"→"small ones"の比喩)は3条件とも完全に維持されている(逐語確認
  済み)。
- 段落数(10)・要約化の兆候は3条件とも無し。
- Band 10,000のみ、記事の核となる技術用語("septic tank")そのものが本文
  から失われた点は、Storytellingというより用語精度・Fact精度の問題として
  上記Fact節で扱った。
