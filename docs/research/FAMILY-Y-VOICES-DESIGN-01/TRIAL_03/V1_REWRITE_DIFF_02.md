# V1_REWRITE_DIFF_02: Standard人物1(V1)英語の追加言い換え(委任_11、修復案B2、Std専用)

目的=Repetition QA method D'(短ラグ)が委任_10のStd 2テイクでflagした2位置(6.58秒付近=冒頭2〜3文、31.5秒付近=`Her words left me speechless… Shouting like my father…`)の約1〜2秒間隔の語句反復を崩す、およびfallbackテイクでAzureが`next morning`->`next warning`と誤転写した連語の回避。Gate・閾値・HR Lockは無変更。日本語稿・Adv英文は無変更。対象=`er110_output/family_y_persona_trial_01/school_phone_ban/it3/english/a2/article.md`第1段落(変更前は同dir `article.md.before_fyt8`)。

| # | 前 | 後 | 狙い |
|---|---|---|---|
| 1 | I am for a rule at my daughter's high school. It would keep phones off during breaks and lunch, too. Only banning them in class is not enough. I get home late from the job site. Fighting about phones every night makes me tired. | I support a rule at my daughter's high school. Phones should be off during breaks and lunch, too. A ban in class alone is not enough. I come home late from the job site, and fighting over phones every night wears me out. | 冒頭の`I... It would... Only banning...`の文頭連続を崩す、`I get home / Fighting about`を結合 |
| 2 | My daughter did not keep our agreement. She was supposed to put her phone in the living-room charging basket. I took her phone away. The next morning, it was hard to talk to her at breakfast. | My daughter broke our agreement. She did not put her phone in the living-room charging basket, so I took it away. At breakfast the next day, it was hard to talk to her. | 2短文を結合、`her phone`反復除去、`next morning`(Azure誤転写語)を`the next day`へ |
| 3 | Her words left me speechless. A promise is a promise, and I want it kept. Shouting like my father is not what I want, either. | I could not say a word back. A promise is a promise, and I want it kept. I do not want to shout like my father, either. | 31.5秒付近の`Her words…/ Shouting… is not what I want`の語句類似を崩す |

## 意味不変の確認文
日本語原稿(「学校でも休み時間まで禁止にしてほしい」「俺は言い返せなかった」「決めたことは守ってほしいんだ」「親父みたいに怒鳴るのも嫌だ」「学校でもそう決まってると言えたら、俺だけが悪者にならずに済む」)の意味・感情(無力感、約束を守ってほしい気持ち、父のように怒鳴りたくない気持ち、一人だけ悪者になりたくない気持ち)を保つ。`daughter broke the agreement/phone taken away`の事実関係、`left out`(Key Phrase)・`off-limits`・`phone-free time`への影響なし(変更箇所に含まれない)。人物差(Voice名・口調・立場)、Std/Adv難易度差(Std短文中心)は維持。
## 難易度指標(第1段落)
Std 174語・15文(平均11.6語/文、変更前176語・17文・10.4語/文)、Adv 174語・13文(平均13.4語/文)。Std文長<Adv文長を維持(差は縮小、Stdの目安10〜12語/文内)。
