# V1_REWRITE_DIFF_01: 人物1(V1)英語の言い換え前後(委任_10、修復案B)

目的=Repetition QA method D'(短ラグ)の偽陽性回避とASR揺れ回避。Gate・閾値・HR Lockは無変更。日本語稿は無変更。対象=`er110_output/family_y_persona_trial_01/school_phone_ban/it3/english/{b1b,a2}/article.md`の第1段落(V1)のみ(変更前は同dir `article.md.before_fyt7`)。根拠=V1_REPAIR_PLAN_01.md / AUDIO_QA_03.md(flag位置: Adv 21.9s=in the charging basket in the living room、36.5〜37.8s=I want…I don't want、Std 33.4s=I had no answer. I want her to…。ASR揺れ=can/could、it/I)。

## Advanced(b1b)
| # | 前 | 後 | 狙い |
|---|---|---|---|
| 1 | to put her phone in the charging basket in the living room. | to put her phone in the living-room charging basket. | in the…in the の反復除去 |
| 2 | If I can say, “That's the rule at school too,” then I don't have to be the only bad guy. | If the school has the same rule, then I'm not the only bad guy. | can/could揺れ・引用形回避 |
| 3 | I had no answer for that. I want her to stick to what we've agreed. I don't want to yell like my father, either. | Her words left me speechless. Still, a promise is a promise, and I want it kept. Yelling like my father is out of the question, too. | I+動詞の連続・I want…I don't want反復の除去 |

## Standard(a2)
| # | 前 | 後 |
|---|---|---|
| 1 | She was supposed to put her phone in the charging basket in the living room. | She was supposed to put her phone in the living-room charging basket. |
| 2 | If I can say, “It's the school rule too,” I won't be the only bad guy. | If the school has the same rule, I won't be the only bad guy. |
| 3 | I had no answer. I want her to keep our promise. I don't want to shout like my father, either. | Her words left me speechless. A promise is a promise, and I want it kept. Shouting like my father is not what I want, either. |

## 意味不変の確認文
いずれも日本語原稿(「学校でもそう決まってると言えたら、俺だけが悪者にならずに済む」「俺は言い返せなかった」「決めたことは守ってほしいんだ」「親父みたいに怒鳴るのも嫌だ」)の意味・感情(言い返せなかった無力感、約束を守ってほしい気持ち、父のように怒鳴りたくない気持ち、一人だけ悪者になりたくない気持ち)を保つ。Key Phrase(Adv: cut off contact/lose trust in/off-limits、Std: left out/off-limits/phone-free time)は変更箇所を含まない。人物差(Voice名・口調・立場)は無変更。
## 難易度指標(第1段落)
Adv 174語・13文(平均13.4語/文)、Std 176語・17文(平均10.4語/文)。変更前は Adv 181語/Std 176語。Std<Advの文長差を維持。
