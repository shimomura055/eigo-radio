# 話者表(全引用。人間確認用。LLM判定をそのまま採用、回想・独白の補助フィールドは設けない)

## Advanced

| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |
|---|---|---|---|---|---|---|
| q0_1 | 0 | “One stab in the chest. That’s what I saw,” | woodcutter | woodcutter | agree | The speech tag says the woodcutter said it. |
| q0_2 | 0 | “I found him this morning, in a thicket off the mountain road. The blood was dry. No sword or bow, sir—only rope beneath a cedar, and a comb. The broken bamboo and trampled earth showed a struggle.” | woodcutter | woodcutter | agree | It continues the woodcutter’s account of finding the body. |
| q1_1 | 1 | “I passed them yesterday at noon,” | monk | monk | agree | The speech tag says the monk said it. |
| q1_2 | 1 | “He carried a sword and bow. His wife rode beside him, her face veiled. I hardly looked at them. Now I wish I had.” | monk | monk | agree | It continues the monk’s account of seeing the couple. |
| q2_1 | 2 | “I caught Tajomaru, the famous bandit, by the stone bridge,” | constable | constable | agree | The speech tag says the constable said it. |
| q2_2 | 2 | “He’d fallen from a horse, but he still had the dead man’s bow. Find the woman. She’ll tell you what he did.” | constable | constable | agree | It continues the constable’s account of catching Tajomaru. |
| q3_1 | 3 | “Takehiro was my daughter’s husband,” | old_woman | old_woman | agree | The speech tag says the old woman said it. |
| q3_2 | 3 | “A gentle samurai. Masago is proud, yes, but she’s only nineteen. Please find her. Don’t send me home without news.” | old_woman | old_woman | agree | It continues the mother’s plea for news of her daughter. |
| q4_1 | 4 | “Yes, I killed him,” | tajomaru | tajomaru | agree | The speech tag identifies Tajomaru as the speaker. |
| q4_2 | 4 | “But listen before you call me a coward! A breeze lifted her veil, and I wanted her. I promised him buried treasure, led him into the thicket and tied him to the cedar. She fought with her dagger, but I took her by force. | tajomaru | tajomaru | agree | It continues Tajomaru’s first-person confession. |
| q5_1 | 5 | “Then she seized my arm. One of us must die, she said. She would go with the survivor. So I freed him. We fought fairly, sword against sword. Twenty-three strokes! No other man had lasted twenty. When he fell, she was gone. I took his weapons and left.” | None | tajomaru | llm_only | It continues Tajomaru’s account of the fight and his escape. |
| q6_1 | 6 | “I crawled towards my husband after the bandit left,” | masago | masago | agree | The speech tag says Masago said it. |
| q6_2 | 6 | “He was still tied up. I begged him to die with me. But his eyes held nothing except cold contempt. For me. His own wife. | masago | masago | agree | It continues Masago’s account of finding her husband. |
| q7_1 | 7 | “I held my dagger. His lips moved: ‘Kill me.’ So I stabbed him. How could I bear those eyes? | None | masago | llm_only | It continues Masago’s account; the quoted words of Takehiro are being reported b |
| q8_1 | 8 | “Afterwards, I tried to drown myself. I couldn’t even do that. Where can I go now?” | None | masago | llm_only | It continues Masago’s first-person account. |
| q9_1 | 9 | “I heard the bandit comforting her,” | takehiro | takehiro | agree | The speech tag identifies Takehiro’s spirit as speaking through the medium. |
| q9_2 | 9 | “My wife said, ‘Take me anywhere.’ Then she pointed at me. ‘Kill that man.’ | takehiro | takehiro | agree | It continues Takehiro’s account; the embedded words are reported speech. |
| q10_1 | 10 | “He pushed her away and asked me whether she should live or die. For that, I almost forgave him. But she fled. He cut one rope and left. | None | takehiro | llm_only | It continues Takehiro’s account of what happened in the thicket. |
| q11_1 | 11 | “I rose from the cedar and picked up the small dagger she had dropped. I stabbed myself in the chest. | None | takehiro | llm_only | It continues Takehiro’s first-person account of his death. |
| q12_1 | 12 | “The thicket fell silent. Then someone crept towards me on soft feet. An unseen hand quietly drew the dagger from my chest. | None | takehiro | llm_only | It continues Takehiro’s account of the dagger being taken. |
| q13_1 | 13 | “I sank for ever into the darkness.” | None | takehiro | llm_only | It concludes Takehiro’s account. |

dialogue clip(声がnarrator以外):

| clip | speaker | voice | text |
|---|---|---|---|
| full_story_part1_c1 | woodcutter | Algieba | "One stab in the chest. That's what I saw," |
| full_story_part1_c3 | woodcutter | Algieba | "I found him this morning, in a thicket off the mountain road. The blood was dry. No sword |
| full_story_part1_c4 | monk | Schedar | "I passed them yesterday at noon," |
| full_story_part1_c6 | monk | Schedar | "He carried a sword and bow. His wife rode beside him, her face veiled. I hardly looked at |
| full_story_part1_c7 | constable | Fenrir | "I caught Tajomaru, the famous bandit, by the stone bridge," |
| full_story_part1_c9 | constable | Fenrir | "He'd fallen from a horse, but he still had the dead man's bow. Find the woman. She'll tel |
| full_story_part1_c10 | old_woman | Zephyr | "Takehiro was my daughter's husband," |
| full_story_part1_c12 | old_woman | Zephyr | "A gentle samurai. Masago is proud, yes, but she's only nineteen. Please find her. Don't s |
| full_story_part2_c1 | tajomaru | Orus | "Yes, I killed him," |
| full_story_part2_c3 | tajomaru | Orus | "But listen before you call me a coward! A breeze lifted her veil, and I wanted her. I pro |
| full_story_part3_c1 | masago | Kore | "I crawled towards my husband after the bandit left," |
| full_story_part3_c3 | masago | Kore | "He was still tied up. I begged him to die with me. But his eyes held nothing except cold  |
| full_story_part3_c4 | takehiro | Puck | "I heard the bandit comforting her," |
| full_story_part3_c6 | takehiro | Puck | "My wife said, 'Take me anywhere.' Then she pointed at me. 'Kill that man.' "He pushed her |

## Standard

| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |
|---|---|---|---|---|---|---|
| q0_1 | 0 | “I found him in the bushes this morning,” | woodcutter | woodcutter | agree | The woodcutter says he found the body. |
| q0_2 | 0 | “He lay near the mountain road, stabbed once in the chest. The blood was already dry when I saw him. Broken bamboo and marks on the ground showed a fight. I found no sword or bow, only rope and a comb.” | woodcutter | woodcutter | agree | It continues his account of the body and what he found. |
| q1_1 | 1 | “I saw the couple yesterday at noon,” | monk | monk | agree | The traveling monk says he saw the couple. |
| q1_2 | 1 | “He carried a sword and bow, and his wife rode beside him.” | monk | monk | agree | It continues the monk’s description of the couple. |
| q2_1 | 2 | “I caught the famous bandit Tajomaru near the bridge,” | constable | constable | agree | The constable says he caught Tajomaru. |
| q2_2 | 2 | “He had fallen off a horse, but still had Takehiro’s bow. Find the wife and ask her what he did.” | constable | constable | agree | It continues the constable’s account and instruction. |
| q3_1 | 3 | “Takehiro, a kind samurai, married my daughter Masago,” | old_woman | old_woman | agree | The old woman identifies Takehiro as her daughter’s husband. |
| q3_2 | 3 | “She is proud and only nineteen. Please find her before you send me home without news.” | old_woman | old_woman | agree | She pleads for news of her daughter. |
| q4_1 | 4 | “I killed him fairly,” | tajomaru | tajomaru | agree | Tajomaru says he killed Takehiro. |
| q4_2 | 4 | “The wind lifted her face covering, and I wanted her. I promised him buried treasure and led him into the bushes. There I tied him to a cedar tree. She fought with her dagger. | tajomaru | tajomaru | agree | It continues Tajomaru’s confession. |
| q5_1 | 5 | “She held my arm and begged for one of us to die. She would leave with the man who lived. I freed him for a fair sword fight. Twenty-three blows—no other man had lasted twenty! She was gone when he fell. I took his weapons and left.” | None | tajomaru | llm_only | It recounts the sword fight and Tajomaru’s escape. |
| q6_1 | 6 | “I crawled towards my husband,” | masago | masago | agree | Masago says she crawled to her husband. |
| q6_2 | 6 | “The bandit had left him tied up. I begged him to die with me. His cold eyes said I was nothing, even though I was his wife. | masago | masago | agree | It continues Masago’s account at the temple. |
| q7_1 | 7 | “He moved his lips while I held my dagger. ‘Kill me,’ he said, so I stabbed him. I could not stand those eyes. | None | masago | llm_only | Masago recounts her husband’s words and her stabbing him. |
| q8_1 | 8 | “I later tried drowning myself, but I failed. Where can I go after that?” | None | masago | llm_only | Masago describes her failed suicide attempt. |
| q9_1 | 9 | “I heard him speaking kindly to her,” | None | takehiro | llm_only | Takehiro’s spirit speaks through a medium. |
| q9_2 | 9 | “She asked him to take her anywhere. Then she pointed at me: ‘Kill that man.’ | None | takehiro | llm_only | It continues Takehiro’s account; the quoted command is reported speech. |
| q10_1 | 10 | “He pushed her away and asked if she should live or die. I nearly forgave him then, but she ran away. He cut one rope and left me. | None | takehiro | llm_only | It continues the spirit’s account of what happened. |
| q11_1 | 11 | “I got up beside the cedar and picked up her small dagger. She had dropped it there. I pushed it into my own chest. | None | takehiro | llm_only | Takehiro describes picking up the dagger and stabbing himself. |
| q12_1 | 12 | “The bushes around me grew quiet. Someone came slowly towards me on silent feet. A hand I could not see quietly pulled the dagger from my chest. | None | takehiro | llm_only | Takehiro recounts what happened as he lay dying. |
| q13_1 | 13 | “I sank into the darkness and never came back.” | None | takehiro | llm_only | It concludes Takehiro’s account. |

dialogue clip(声がnarrator以外):

| clip | speaker | voice | text |
|---|---|---|---|
| full_story_part1_c1 | woodcutter | Algieba | "I found him in the bushes this morning," |
| full_story_part1_c3 | woodcutter | Algieba | "He lay near the mountain road, stabbed once in the chest. The blood was already dry when  |
| full_story_part1_c4 | monk | Schedar | "I saw the couple yesterday at noon," |
| full_story_part1_c6 | monk | Schedar | "He carried a sword and bow, and his wife rode beside him." |
| full_story_part1_c7 | constable | Fenrir | "I caught the famous bandit Tajomaru near the bridge," |
| full_story_part1_c9 | constable | Fenrir | "He had fallen off a horse, but still had Takehiro's bow. Find the wife and ask her what h |
| full_story_part1_c10 | old_woman | Zephyr | "Takehiro, a kind samurai, married my daughter Masago," |
| full_story_part1_c12 | old_woman | Zephyr | "She is proud and only nineteen. Please find her before you send me home without news." |
| full_story_part2_c1 | tajomaru | Orus | "I killed him fairly," |
| full_story_part2_c3 | tajomaru | Orus | "The wind lifted her face covering, and I wanted her. I promised him buried treasure and l |
| full_story_part2_c4 | masago | Kore | "I crawled towards my husband," |
| full_story_part2_c6 | masago | Kore | "The bandit had left him tied up. I begged him to die with me. His cold eyes said I was no |
| full_story_part3_c1 | takehiro | Puck | "I heard him speaking kindly to her," |
| full_story_part3_c3 | takehiro | Puck | "She asked him to take her anywhere. Then she pointed at me: 'Kill that man.' "He pushed h |

