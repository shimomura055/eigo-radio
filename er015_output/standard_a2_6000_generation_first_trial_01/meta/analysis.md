# analysis.md (Meta)

STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01。採否推奨は書かない(客観データ
と所見のみ)。

## 客観指標

| | Advanced(入力) | A(Control v5) | B(Gen-First) |
|---|---|---|---|
| word_count | 329 | 290 | 321 |
| sentence_count | 23 | 32 | 30 |
| avg_sentence_length_words | 14.3 | 9.06 | 10.7 |
| flesch_kincaid_grade_heuristic | 7.53 | 5.77 | 5.79 |
| paragraph_count | 13 | 13 | 14(注1) |
| residual_word_count_over_6000 | 9 | 10 | 10 |

注1: Bは1箇所(「プライバシー懸念」段落)で1文が2段落に分割されている
(内容の欠落ではなく改行のみ追加、後述)。

## 6,000位超残存語(rank付き、Sonnet事後診断)

| Word | Rank | A | B | 診断タグ | 理由 |
|---|---|---|---|---|---|
| concierges | >20,000(zipf 1.70) | O | O | 事実引用/意味精度 | Metaが実際に使った呼称"human concierges"の引用。簡単な語に置換すると事実(呼称)を損なう。 |
| Reuters | 8,719 | O | O | 固有名詞 | 通信社名。 |
| Meta | 10,578 | O | O | 固有名詞 | 企業名。 |
| Muse | 13,199 | O | O | 固有名詞 | 製品(AIエージェント)名。 |
| curtain | 8,776 | O | O | Metaphor維持 | 記事全体の「舞台裏」比喩(stage/curtain/onstage/performer)の一部。v5 Prompt自体が例示するmetaphor許容語。 |
| performer | 9,646 | O | O | 主題語/Metaphor維持 | 「隠れた演奏者」という記事の核心比喩(見出し名"The hidden performer..."そのもの)。 |
| onstage | 15,670 | O | O | 推測可能複合語/Metaphor維持 | on+stageで推測可能、同じ比喩ファミリーの一部。 |
| paused | 7,166 | O | - | 軽度残存 | 一般語("pause"の過去形)、平易で自然。無理に置換する必要性は低い。 |
| ins | 8,050 | O | O | トークナイザ副作用(非語) | "stand-ins"がハイフンで"stand"/"ins"に分割される既存分析ツール(v3mod.extract_content_words)の既知の限界。実在する難語ではない。A/B双方に同じ副作用が出るため差の要因ではない。 |
| futuristic | 17,848 | O | - | 軽度残存 | future+-isticで推測可能、Aのみ出現("useful and futuristic")。 |
| leak | 6,160 | - | O | 軽度残存 | 一般語、Bのみ出現("call details could leak")。 |

不要な難語(固有名詞でも主題語でもMetaphorでもない、単なる難語の残存)は
A/Bとも観測されなかった(ins除く。insは非語)。A/Bの残存語一覧はほぼ同一
集合であり、この記事(Meta)はもともと難語が少なく、生成一体型(B)の効果を
判別しにくい題材だった。

## Fact/意味変化(文単位、Advanced→A/B対応表)

全13段落を確認。**Major差分は0件**。

| # | Advanced要旨 | A | B | 意味差 |
|---|---|---|---|
| 1 | AIに電話代行させるのは未来的で便利 | 文分割のみ | 文分割のみ | none |
| 2 | MetaがMuseに電話代行機能を持たせようとした | 同上 | 同上 | none |
| 3 | 舞台裏を見ると意外な光景 | "behind the stage"維持 | "behind the **scenes**"に変更 | minor(比喩語のvariation。stage系比喩ファミリーの一貫性がわずかに低下するが、他のonstage/curtain/performer表現は維持されており記事全体の比喩は壊れていない) |
| 4 | 社内試験で人間契約スタッフが対応、Metaは"human concierges"と呼称 | 文分割のみ | 文分割のみ | none |
| 5 | 表向きはAI電話代行だが人間代役が控えていた | 同上 | 同上 | none |
| 6(見出し1) | ピアノの比喩(一人で弾いているようで実は別演奏者) | 文分割のみ、比喩維持 | 同上 | none |
| 7 | プライバシー懸念、通話流出のリスク、契約スタッフが対応していたと知れば驚く | 文分割のみ | **1段落を2段落に分割**(内容欠落なし) | none |
| 8 | Reutersが確認した社内投稿、Meta幹部が機能停止を説明 | 文再構成(Reutersが文頭主語に) | 同上 | none(ただし機械的fact_tokens_checkはReutersの「文中大文字」判定が文頭移動により外れ、見かけ上proper_noun_words不一致となる。目視で確認した結果、Reutersという固有名詞自体は本文に残存しており事実欠落ではない、機械判定の既知の限界) |
| 9 | 「誰が舞台で話し誰が幕の後ろにいるか」で締め | Aは"who is speaking onstage. And who is behind the curtain."と2文に分割(文法的にはやや断片的な短文2つ) | Bは原文同様"...onstage-and who is behind the curtain."を1文のまま維持(より自然) | none(意味は同じだが、English qualityの所見としてBの方が自然、下記参照) |
| 締め(In one line) | 人間代役が通話対応、プライバシーと信頼への疑問 | 文分割のみ | 文分割のみ | none |

## English quality(具体文引用)

- B P3で"behind the stage"->"behind the scenes"へ変化。誤りではないが、
  記事内の一貫した「舞台(stage)」比喩ファミリー(onstage/curtain/
  performer/piano)からわずかに外れた語選択。
- A P9で"It also matters who is speaking onstage. And who is behind the
  curtain."と2文に分割。"And who is behind the curtain."は主動詞を欠く
  文断片的な短文で、平均文長9-11語ルールを機械的に適用した結果とみられる
  (読み上げると若干ぎこちない)。B は同じ箇所を原文のダッシュ構造を
  保持したまま1文で表現しており、この1箇所においてはBの方が自然だった。
- 冗長な説明句での難語回避(制約2で禁止)は両方とも観測されなかった
  (該当なし)。

## Learning quality / Storytelling

- 段落数: Advanced 13 -> A 13 -> B 14(内容欠落なし、1段落が2つに分割された
  のみ)。Storylineの順序・驚きの配置(舞台裏に人間がいた、というreveal)は
  A/Bとも維持。
- Metaphor(舞台裏/ピアノ/幕の後ろ)は両方とも維持されている。要約化の
  兆候(Detail削除)は観測されなかった。
- FK概算はA 5.77・B 5.79とほぼ同水準(Advanced 7.53より明確に易化)。
  平均文長はA 9.06語・B 10.7語(B の方がv5指示の目標レンジ9-11語の中央
  寄り、Aはやや目標下限寄り)。
