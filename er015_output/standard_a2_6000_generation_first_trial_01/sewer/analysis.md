# analysis.md (Sewer)

STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01。採否推奨は書かない(客観データ
と所見のみ)。

## 客観指標

| | Advanced(入力) | A(Control v5) | B(Gen-First) |
|---|---|---|---|
| word_count | 328 | 322 | 324 |
| sentence_count | 23 | 28 | 26 |
| avg_sentence_length_words | 14.26 | 11.5 | 12.46 |
| flesch_kincaid_grade_heuristic | 7.6 | 6.3 | 6.31 |
| paragraph_count | 10 | 10 | 10 |
| residual_word_count_over_6000 | 9 | 10 | 9 |

## 6,000位超残存語(rank付き、Sonnet事後診断)

| Word | Rank | A | B | 診断タグ | 理由 |
|---|---|---|---|---|---|
| septic | >20,000(zipf 3.21) | O(x4) | O(x4) | 主題語/意味精度(不可欠語) | JA原文の引用句"combined septic tank"(合併浄化槽)の核となる技術語。前回Trial(VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01)で"septic->treatment"へ誤って置換されFact変化を起こした語だが、本Trialでは両方とも一切置換されず、fact_tokens_check完全一致を維持した。 |
| sewer / sewers | 12,324 | O(sewer x3) | O(sewer x2, sewers x3) | 主題語(記事の主題そのもの) | 記事の主題(下水道)を表す名詞。簡単な語に置換すると記事が何についてかが曖昧になる。 |
| artery | 12,006 | O(x3) | O(x3) | Metaphor維持(記事の中心比喩) | 「見えない大動脈」という記事全体を貫く中心比喩、見出し名にも使用。 |
| flush | 9,610 | O(x1) | O(x1) | 意味精度(不可欠語) | 「トイレを流す」動作を正確に表す動詞。前回Trialで"flush->use"へ誤って簡略化され動作の意味が変わった語だが、本Trialでは両方とも維持された。 |
| wastewater | 18,216 | O(x1) | O(x1) | 推測可能複合語/主題語 | waste+waterで推測可能、記事タイトルにも使われる主題語。 |
| faraway | >20,000(zipf 2.99) | O(x1) | O(x2) | 推測可能複合語 | far+awayで推測可能。 |
| invisible | 6,153 | O(x1) | O(x1) | 軽度残存 | 閾値をわずかに超えるだけの平易な語。 |
| convenience | 6,887 | O(x2) | O(x2) | 軽度残存 | 閾値をわずかに超えるだけの平易な語。 |
| inspect | 12,445 | O(x1) | - | 軽度残存(Aのみ) | Bでは同じ箇所が"check"(平易語)へ自然に言い換えられ、残存語から外れた(下記参照、生成一体型の効果例)。 |

不要な難語(固有名詞でも主題語でもMetaphorでもない、単なる難語の残存)は
観測されなかった。Sewerは前回Trial(VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01)
でseptic/flush/artery/sewerの事後置換が意味変化・不自然化を起こした記事
であり、本Trialでは両方式(A/B)ともこれらの語を一切変更せず、fact_tokens_
checkが完全一致した点が重要な観測事実である。

## Fact/意味変化(文単位、Advanced→A/B対応表)

全10段落を確認。**Major差分は0件。fact_tokens_check.overall_fact_tokens_
match = True(A/Bとも)**(数字・引用符内フレーズ・固有名詞候補すべて一致)。

| # | Advanced要旨 | A | B | 意味差 |
|---|---|---|---|
| 1 | 「合併浄化槽」という語から町の合併を連想するが実際はトイレ等の水の話 | 文分割のみ | 文分割のみ | none |
| 2 | 一部自治体が下水道を合併浄化槽へ切替検討、下水道全廃ではない | 同上 | 同上 | none |
| 3(見出し1) | 下水道は「見えない大動脈」、蛇口・トイレ→地下管→処理場、老朽化で修理困難 | "check and repair"->"inspect and fix"(inspectが残存語) | "check and fix"(inspectを使わず平易語で表現) | none(意味同一。Bはinspectという難語を使わず自然に表現した点でGen-First目的に合致) |
| 4(見出し2) | 合併浄化槽=家庭近くの小規模処理施設、大きな仕組みを小さく分散 | 文分割のみ | "a small water treatment facility"->"a small place that treats water"(facility相当をより平易な記述句へ) | none(意味同一) |
| 5 | 浄化槽も設置・点検・清掃が必要、暮らしの裏側が変わる | "installed"を使用 | **"installed"->"put in"**(句動詞、より平易) | none(意味同一。生成一体型の意図した効果の好例) |
| 6 | 便利さを守るため設備を大きくする必要はない、下水道の未来は身近な場所に | "Still,"(逆接)を維持 | **"Still,"を省略**("The interesting point is simple:"で開始) | none(Factは同一。前段落の「作業が必要」との対比を示す逆接語が省略され、文章の繋がり[結束性]がわずかに弱まる、下記English quality参照) |
| 締め(In one line) | 便利さを守るため、水処理は老朽化した地下網から家近くの小規模系へ移るかもしれない | 文簡略化のみ | 文簡略化のみ(Aと文面ほぼ同一) | none |

## English quality(具体文引用)

- B P5: "It must be **put in**, checked, and cleaned."(Advanced/Aの
  "installed"を、意味を変えずに平易な句動詞"put in"へ言い換えた。冗長な
  説明句にはなっておらず、生成一体型が狙った「最初から簡単な表現で書く」
  効果の具体例)。
- B P6: 逆接の"Still,"が省略され、"The interesting point is simple:"から
  始まる。Factは変わらないが、直前段落(点検・清掃という手間がある話)との
  対比のニュアンスがA/Advancedよりわずかに弱い(軽微な結束性の変化、
  意味変化ではない)。
- 冗長な説明句での難語回避(制約2で禁止)による不自然な重さは、A/Bとも
  観測されなかった。B P4の"a small place that treats water"はやや説明的
  だが、1文中1箇所のみで許容範囲内(不自然な繰り返しではない)。

## Learning quality / Storytelling

- 段落数はAdvanced/A/Bとも10段落で完全一致。中心比喩(「見えない大動脈」
  ->「洗濯機」の比喩)・Storyline(合併=町ではなく水、という意外性の
  提示順序)はA/Bとも維持されている。要約化の兆候は観測されなかった。
- FK概算はA 6.3・B 6.31とほぼ同水準(Advanced 7.6より明確に易化)。
  平均文長はA 11.5語・B 12.46語(v5指示の目標9-11語のレンジからは
  両方ともやや長め、Bの方がさらにやや長い)。
- 前回Trial(VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01)で問題になった
  septic/flush/sewer/arteryの不自然な事後置換は、本TrialのA/Bどちらの
  方式でも発生しなかった。
