# analysis.md (Meta)

NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01。採否推奨は書かない(客観データと
所見のみ、Sonnet仮分類)。

## 客観指標

| | Input(Advanced相当) | Band 6,000 | Band 10,000 | Band 14,000 |
|---|---|---|---|---|
| word_count | 329 | 331 | 333 | 323 |
| sentence_count | 23 | 23 | 23 | 23 |
| avg_sentence_length_words | 14.3 | 14.39 | 14.48 | 14.04 |
| subordinators_per_100_words | 3.65 | 4.53 | 4.5 | 3.72 |
| flesch_kincaid_grade_heuristic | 7.53 | 7.24 | 7.14 | 7.09 |
| paragraph_count | 13 | 13 | 13 | 13 |
| 生のBand超過語数 | - | 9 | 3 | 2 |

段落数はBand6,000/10,000/14,000とも入力と同一(13)。要約化・段落削減は
観測されなかった。sentence_countも全条件で入力と完全一致(23)であり、
語彙制約による極端な文分割・断片化は起きていない(前Trial[Generation-
First]のA条件で見られた"...onstage. And who is behind the curtain."の
ような断片化は本Trialでは観測されなかった)。

FK概算は3条件ともInputよりわずかに下がる(7.53→7.09〜7.24)が、Band数値
(6,000/10,000/14,000)と単調に対応してはいない(Band 14,000が最も低い
7.09、Band 6,000が最も高い7.24)。FK概算は主に文長・音節数で決まるため、
「語の頻度順位」という今回の操作変数を直接反映しない指標であることが
分かる(客観指標としては残存語数の方が本Trialの操作変数を直接測る)。

## 生のBand超過語(rank付き)とSonnet分類

| Word | Rank | 6,000 | 10,000 | 14,000 | 分類 | 理由 |
|---|---|---|---|---|---|---|
| concierges | >20,000(zipf1.70) | O | O | - | 引用/事実(準固有名詞) | Metaが実際に使った呼称"human concierges"の引用そのもの。同時に日本語で「コンシェルジュ」は定着した外来語でもある(二重に除外条件を満たす、境界なし)。 |
| ins | 8,050 | O | - | - | **トークナイザ副作用(非語)** | "stand-ins"がハイフンで"stand"/"ins"に分割される既知の限界(前Trialのanalysis.mdと同じ現象)。実在する難語ではない。 |
| reuters | 8,719 | O | - | - | 固有名詞 | 通信社名。 |
| curtain | 8,776 | O | - | - | 日本語定着語(カーテン) | Prompt自身が承認例として明示した語そのもの。 |
| performer | 9,646 | O | - | - | 推測容易な派生語 | perform(既知語)+ -er(行為者接尾辞)、意味は容易に推測できる。 |
| hid | 9,760 | O | - | - | **ランキング手法の限界(非違反)** | "hide"(基本語、top2,000相当と推定)の不規則過去形。既存lemma化ロジック(-s/-es/-ies/-ed/-ing/-ly の単純規則のみ)は不規則活用を正規化できないため、表層形順位(9,760)がそのまま採用されている。実際の難語ではない。 |
| meta | 10,578 | O | O | - | 固有名詞 | 企業名。 |
| muse | 13,199 | O | O | - | 固有名詞 | 製品(AIエージェント)名。 |
| onstage | 15,670 | O | O | O | 推測容易な複合語 | on + stage、意味は容易に推測できる。 |

**実質超過語数(除外理由の付かない語)**: Band 6,000=0、Band 10,000=0、
Band 14,000=0。Meta記事は3条件すべてで「除外条件に当てはまらない難語」が
残らなかった(トークナイザ副作用・ランキング手法の限界を除く)。判断が
割れる境界語は無し(concierges/curtain/performer/onstageは委任文の除外例
[wastewater/surprisingly/piano/curtain]と同型の透明な派生・定着語・固有
名詞であり、境界とは判定しなかった)。

## Fact/意味変化(段落単位、Input→各Band対応表)

全13段落を確認。**Major差分は0件**。

| # | Input要旨 | Band 6,000 | Band 10,000 | Band 14,000 | 意味差 |
|---|---|---|---|---|---|
| 2 | "The main actor was Muse"/"on a person's behalf" | "The main part was Muse"/"for people" | "Muse...was at the center of it"/"for a person" | "Its main part was Muse"/"for a person" | none(actor→part/central、behalfの言い換えは意味を変えない) |
| 3 | "behind the stage" | "behind the scenes" | "behind the scenes" | "behind the scenes" | minor(3条件ともstage比喩から外れ"scenes"を使用。Band数値に関係なく一貫して発生しており、Band制約由来ではなくモデルの一般的な言い換え傾向と見られる。stage系比喩ファミリーの一部だけがわずかに弱まるが、curtain/performer/onstageは維持) |
| 19 | "leak outside the company" | "get outside the company" | "leak outside the company" | "leak outside the company" | minor(Band 6,000のみ"leak"[rank6,160、6,000のすぐ外]を避けて"get"に置換。「不正に漏れる」というニュアンスが「外に出る」という中立的な表現へやや弱まる) |
| 23(締め) | "who is speaking onstage—and who is behind the curtain" | "onstage...curtain"(維持) | "in front—and who is behind the curtain"("onstage"→"in front") | "onstage...curtain"(維持、Inputと同一) | minor(Band 10,000のみ"onstage"[rank15,670、10,000超]を一般語"in front"へ置換。演劇比喩がこの1箇所だけ弱まる。Band 14,000はrank内のため"onstage"を維持し、比喩を完全保持) |
| その他10段落 | - | 言い換えのみ、Fact・因果・主体・数量に変化なし | 同左 | 同左 | none |

`fact_tokens_check`(数字・引用句・大文字語)は3条件とも
`quoted_strings_match=true`・`numbers_match=true`。`proper_noun_words_
match=false`は3条件とも「But」が文頭以外の位置に来た1箇所の差のみで、
目視確認の結果Major Fact差分ではない(前Trialと同じ既知のヒューリス
ティック限界)。

## English quality

- FAIL条件(文法破綻/意味変化/教材不可/冗長説明/不自然な反復)に該当する
  箇所は3条件とも**観測されなかった**。3条件とも自然に音読できる文章。
- Band 10,000の締め文"who is speaking in front—and who is behind the
  curtain"は、"onstage"という具体的な演劇語を失った分だけ、Band 14,000
  (Inputと同一の"onstage")より比喩の精度がわずかに落ちる(FAILではなく
  Storytelling上の軽微な劣化として記録)。
- Band 6,000の"get outside the company"は、"leak"(rank 6,160)を避けた
  結果としての言い換えだが、不自然ではなく意味も大きく変わらない(minor
  記録のみ)。

## Storytelling

- Metaphor(舞台裏/ピアノ/幕の後ろ)の核はBand 6,000/10,000/14,000とも
  維持されている(curtain/performer/pianoは3条件とも残存)。
- 演劇比喩の一貫性という観点では Band 14,000 > Band 6,000 ≈ Band 10,000
  (Band 10,000のみ締めの"onstage"を失う。Band 6,000は"onstage"自体は
  10,000超だが残存語リストに含まれており実際には保持されている=つまり
  締め文の比較上、Band 10,000だけが"onstage"を手放した点が唯一の逆転
  現象)。
- 段落数(13)・要約化の兆候なし、は3条件で共通。
