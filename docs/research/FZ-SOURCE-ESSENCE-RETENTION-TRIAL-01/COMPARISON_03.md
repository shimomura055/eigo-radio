# COMPARISON_03: 『告げ口心臓』現行 run_sf_prod_01(旧・三人称寄りAdv/Std) vs 新 run_sf_prod_02(案A配線後) — Fable目視用抜粋

作成: 2026-10-25 / 委任_04 / 自動判定ではない。人称・聞き手への呼びかけ・自己正当化の語り・結末の引用抜粋。**最終判断はFable目視、最終試聴はユーザー**。

出典: `er026_output/family_z_production_e2e_01/the_tell_tale_heart/{run_sf_prod_01,run_sf_prod_02}/writer/{r2,std}.md`(r2=Advanced最終、std=Standard)


## Advanced

### 語彙カウント(機械集計、参考)
| | 旧 run_sf_prod_01 | 新 run_sf_prod_02 |
|---|---|---|
| I | 1 | 28 |
| my | 1 | 13 |
| me | 0 | 5 |
| you | 0 | 6 |
| your | 0 | 0 |
| he | 28 | 7 |
| housemate | 2 | 0 |
| narrator | 0 | 0 |
| words | 439 | 422 |

### 旧 run_sf_prod_01: 冒頭2段落

> He was not mad, the old man’s housemate insisted. Only nervous. His illness had sharpened his senses, especially his hearing. He heard everything in heaven and earth. Surely that proved he was sane. His listener should judge how calmly he told the story.
>
> He loved the old man, who had never hurt him. He wanted no money. But that pale blue eye, covered by a thin film like a vulture’s, made his blood turn cold. He would kill the old man and close it forever.

### 旧 run_sf_prod_01: 聞き手への語りかけ(you / listener を含む文)

- His listener should judge how calmly he told the story.
- For an hour, he stood perfectly still while the old man sat upright, listening.

### 旧 run_sf_prod_01: 結末(最終段落)

> “Stop pretending!” he screamed. “I did it! Tear up the planks! Here, beneath my feet! It is the beating of his hideous heart!”

### 新 run_sf_prod_02: 冒頭2段落

> You call me mad. No. Nervous, perhaps, but perfectly sane. My illness sharpened my senses, especially my hearing. I hear everything in heaven and earth. Listen to my calm voice, and judge for yourself.
>
> I loved the old man who shared my home. He had never hurt me; I wanted none of his money. But his eye! Pale blue, covered by a cloudy film—a vulture’s eye. Whenever it turned towards me, my blood went cold. I had to be free of it.

### 新 run_sf_prod_02: 聞き手への語りかけ(you / listener を含む文)

- You call me mad.
- Listen to my calm voice, and judge for yourself.
- You should have seen my patience!
- You understand: I hated the eye, not the man.
- For an hour he sat in bed, listening.
- You could have searched all night.
- You see how little I feared?
- Could you have borne it?

### 新 run_sf_prod_02: 結末(最終段落)

> “I did it!” I screamed. “Tear up the planks! Here! It is the beating of his hideous heart!”

## Standard

### 語彙カウント(機械集計、参考)
| | 旧 run_sf_prod_01 | 新 run_sf_prod_02 |
|---|---|---|
| I | 29 | 33 |
| my | 11 | 12 |
| me | 2 | 3 |
| you | 1 | 6 |
| your | 0 | 0 |
| he | 3 | 6 |
| housemate | 0 | 0 |
| narrator | 0 | 0 |
| words | 442 | 440 |

### 旧 run_sf_prod_01: 冒頭2段落

> I was only nervous, not mad, and I knew it. My illness made all my senses stronger, especially my hearing. I could hear everything in heaven and on earth. Judge how calmly I tell you this whole story.
>
> I loved the old man who shared my home. He never hurt me, and I wanted none of his money. But his pale blue eye had a thin covering, like a vulture’s. It froze my blood. I would kill him and close that eye forever.

### 旧 run_sf_prod_01: 聞き手への語りかけ(you / listener を含む文)

- Judge how calmly I tell you this whole story.
- I stood still for an hour while he sat listening.

### 旧 run_sf_prod_01: 結末(最終段落)

> “Don’t pretend anymore!” I screamed. “I killed him! Pull up the floorboards here, under my feet! It is his horrible heart beating!”

### 新 run_sf_prod_02: 冒頭2段落

> You think I am mad, but I am only nervous. Illness made my senses stronger, especially my hearing. I hear everything in heaven and on earth. Listen, and judge how calmly I tell you this.
>
> I loved the old man who lived with me. He never hurt me, and I wanted none of his money. But a cloudy film covered his pale blue eye. That vulture’s eye made my blood turn cold. I had to get free of it.

### 新 run_sf_prod_02: 聞き手への語りかけ(you / listener を含む文)

- You think I am mad, but I am only nervous.
- Listen, and judge how calmly I tell you this.
- You should have seen my patience—he never even moved!
- For an hour, he sat listening while I stood completely still.
- You could search all night and find no mark.
- You see, I sat right above the body without fear.
- Could you bear that?

### 新 run_sf_prod_02: 結末(最終段落)

> “I killed him!” I screamed. “Pull up the floorboards here! That is the beating of his horrible heart!”

## Sonnet所見(CP、最終はFable)
- narration行(CP#9): 新Adv/Stdとも全22段落が語り手本人の一人称('I'/'my'/'me')で、聞き手'you'への呼びかけが複数箇所に在る。'housemate'/'narrator'は本文0件(`grep -ci`)。旧Advは冒頭から三人称('the old man's housemate'、'He was not mad')。
- 自己正当化・自己陶酔の語り: 新Advの冒頭『Listen to my calm voice, and judge for yourself.』『You should have seen my patience!』『I nearly laughed at my cleverness』『You see how little I feared?』。
- ending_reveal: 最終文は自白+心臓音(Adv『“I did it!” … It is the beating of his hideous heart!』)。結末前に音の正体は示唆されていない(『A low, quick beating…』は現実か妄想かを語らない)。
- 注意: Std guardrailの`STD_AVG_SENT_LEN_NOT_SHORTER`(8.39 vs adv 5.55)はWARNのみ(failures=[]、Adv文が極端に短いため)。段落数Adv22/Std22一致。

## 公開ページ本文からの引用(user_test/family_z_tell_tale_heart_01/{advanced,standard}.html、一人称`I`・聞き手`you`、Fable目視用。自動判定ではない)

### Advanced: 英文セル16件中 一人称(I/my/me)を含む=4件、聞き手(you)を含む=4件、housemate=0件

聞き手への語りかけ(you):
- Voice: Charon / Style: E1A narrator insists that he is perfectly sane, then tells a disturbing story about his home. As you listen, consider whether his actions support his claim.
- Voice: Aoede / Style: PD06For seven nights, at midnight, I lifted his latch. You should have seen my patience! I eased the door open so slowly he never stirred, then let one thin ray escape my lantern. The eye was always closed. So I could do nothing. You understand: I hated the eye, not the man. Each morning I kindly asked how he had slept. On the eighth night, I nearly laughed at my cleverness. Then my thumb slipped against the lantern's fastening.
- Voice: Aoede / Style: PD06I stood motionless. For an hour he sat in bed, listening. At last he groaned softly. Not pain—terror. I knew that sound. I uncovered the lantern. Its narrow beam found the eye. Wide open. A low, quick beating reached me, like a watch wrapped in cotton. His heart! Faster it went, and louder. What if a neighbour heard? I rushed forward. He shrieked once. I dragged him down and pulled the heavy bed over him. Finally, the beating stopped. I checked his pulse. Nothing. I hid his body beneath three floorboards and fitted them back exactly. Not a mark! You could have searched all night. At four in the morning, three police officers knocked. A neighbour had heard a shriek.
- Voice: Aoede / Style: PD06I welcomed them. A bad dream, I explained; the cry was mine. The old man was away in the country. I showed them every room, then brought chairs into his bedroom. I sat directly above the body. You see how little I feared? They chatted pleasantly. I smiled. Then my head began to ache. A ringing filled my ears—but no. That low, quick beating again. I spoke louder. It grew louder too. I paced and scraped my chair across the boards. Still they chatted. Still they smiled. Louder. Louder! Could you have borne it? They heard! They knew! Their smiles were mocking me. I could bear no more. "I did it!" I screamed. "Tear up the planks! Here! It is the beating of his hideous heart!"

一人称の例(先頭3件):
- Voice: Aoede / Style: PD06You call me mad. No. Nervous, perhaps, but perfectly sane. My illness sharpened my senses, especially my hearing. I hear everything in heaven and earth. Listen to my calm voice, and judge for yourself. I loved the old man who shared my home. He had never hurt me; I wanted none of his money. But his eye! Pale blue, covered by a cloudy film—a vulture's eye. Whenever it turned towards me, my blood went cold. I had to be free of it.
- Voice: Aoede / Style: PD06For seven nights, at midnight, I lifted his latch. You should have seen my patience! I eased the door open so slowly he never stirred, then let one thin ray escape my lantern. The eye was always closed. So I could do nothing. You understand: I hated the eye, not the man. Each morning I kindly asked how he had slept. On the eighth night, I nearly laughed at my cleverness. Then my thumb slipped against the lantern's fastening.
- Voice: Aoede / Style: PD06I stood motionless. For an hour he sat in bed, listening. At last he groaned softly. Not pain—terror. I knew that sound. I uncovered the lantern. Its narrow beam found the eye. Wide open. A low, quick beating reached me, like a watch wrapped in cotton. His heart! Faster it went, and louder. What if a neighbour heard? I rushed forward. He shrieked once. I dragged him down and pulled the heavy bed over him. Finally, the beating stopped. I checked his pulse. Nothing. I hid his body beneath three floorboards and fitted them back exactly. Not a mark! You could have searched all night. At four in the morning, three police officers knocked. A neighbour had heard a shriek.

### Standard: 英文セル11件中 一人称(I/my/me)を含む=4件、聞き手(you)を含む=4件、housemate=0件(委任_05で訂正)

**訂正(委任_05確認1)**: 旧記載『10件中 一人称=0件・you=0件』は抽出の不具合による誤り。Standardの本文セルは`<div class='note'>6%減速適用(比…)</div>`(日本語)がVoice行とscriptの間に入るHTML構造のため、日本語文字を含むセルを除外する旧抽出が本文セルを落としていた。公開Stdは`run_sf_prod_02/writer/std.md`と22段落全一致(ACCEPTANCE_CHECK_01.md)。

聞き手への語りかけ(you、文単位):
- You think I am mad, but I am only nervous.
- Listen, and judge how calmly I tell you this.
- You should have seen my patience—he never even moved!
- You could search all night and find no mark.
- You see, I sat right above the body without fear.
- Could you bear that?

一人称の例(先頭3件):
- You think I am mad, but I am only nervous. Illness made my senses stronger, especially my hearing. I hear everything in heaven and on earth. Listen, and judge how calmly I tell you this. I loved the o
- At midnight for seven nights, I slowly opened his door. You should have seen my patience—he never even moved! Then I let one thin ray escape from my lantern. But I always found that eye shut. I could 
- For an hour, he sat listening while I stood completely still. Finally, he groaned softly in fear, not pain. I knew that sound well. I opened the lantern's cover, sending light onto his eye. It was com
