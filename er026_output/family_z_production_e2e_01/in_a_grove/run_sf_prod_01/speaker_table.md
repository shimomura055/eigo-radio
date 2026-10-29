# 話者表(全引用。人間確認用。LLM判定をそのまま採用、回想・独白の補助フィールドは設けない)

## Advanced

| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |
|---|---|---|---|---|---|---|
| q0_1 | 0 | “One stab in the chest. That’s what I saw,” | woodcutter | woodcutter | agree | The woodcutter is explicitly identified as the speaker. |
| q0_2 | 0 | “I found him this morning, in a thicket off the mountain road. The blood was dry. No sword or bow, sir—only rope beneath a cedar, and a comb. The broken bamboo and trampled earth showed a struggle.” | woodcutter | woodcutter | agree | He continues describing what he found. |
| q1_1 | 1 | “I passed them yesterday at noon,” | monk | monk | agree | The monk is explicitly identified as the speaker. |
| q1_2 | 1 | “He carried a sword and bow. His wife rode beside him, her face veiled. I hardly looked at them. Now I wish I had.” | monk | monk | agree | He continues recounting whom he passed. |
| q2_1 | 2 | “I caught Tajomaru, the famous bandit, by the stone bridge,” | constable | constable | agree | The constable is explicitly identified as the speaker. |
| q2_2 | 2 | “He’d fallen from a horse, but he still had the dead man’s bow. Find the woman. She’ll tell you what he did.” | constable | constable | agree | He continues describing the arrest and investigation. |
| q3_1 | 3 | “Takehiro was my daughter’s husband,” | old_woman | old_woman | agree | The old woman is explicitly identified as the speaker. |
| q3_2 | 3 | “A gentle samurai. Masago is proud, yes, but she’s only nineteen. Please find her. Don’t send me home without news.” | old_woman | old_woman | agree | She continues pleading for news of her daughter. |
| q4_1 | 4 | “Yes, I killed him,” | tajomaru | tajomaru | agree | Tajomaru is explicitly identified as the speaker and confesses to the events. |
| q5_1 | 5 | “Then she seized my arm. One of us must die, she said. She would go with the survivor. So I freed him. We fought fairly, sword against sword. Twenty-three strokes! No other man had lasted twenty. When he fell, she was gone. I took his weapons and left.” | None | tajomaru | llm_only | This continues Tajomaru’s first-person account. |
| q6_1 | 6 | “I crawled towards my husband after the bandit left,” | masago | masago | agree | Masago is explicitly identified as the speaker. |
| q8_1 | 8 | “Afterwards, I tried to drown myself. I couldn’t even do that. Where can I go now?” | None | masago | llm_only | She continues her account of trying to drown herself. |
| q9_1 | 9 | “I heard the bandit comforting her,” | takehiro | takehiro | agree | Takehiro’s spirit is explicitly identified as the speaker, speaking through the  |
| q13_1 | 13 | “I sank for ever into the darkness.” | None | takehiro | llm_only | This concludes Takehiro’s first-person account. |

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
| full_story_part2_c3 | tajomaru | Orus | "Then she seized my arm. One of us must die, she said. She would go with the survivor. So  |
| full_story_part3_c1 | masago | Kore | "I crawled towards my husband after the bandit left," |
| full_story_part3_c3 | masago | Kore | "Afterwards, I tried to drown myself. I couldn't even do that. Where can I go now?" |
| full_story_part3_c4 | takehiro | Puck | "I heard the bandit comforting her," |
| full_story_part3_c6 | takehiro | Puck | "I sank for ever into the darkness." |

## Standard

| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |
|---|---|---|---|---|---|---|
| q0_1 | 0 | “I found him in the bushes this morning,” | woodcutter | woodcutter | agree | The woodcutter says he found the body. |
| q0_2 | 0 | “He lay near the mountain road, stabbed once in the chest. The blood was already dry when I saw him. Broken bamboo and marks on the ground showed a fight. I found no sword or bow, only rope and a comb.” | woodcutter | woodcutter | agree | This continues the woodcutter’s account of the scene. |
| q1_1 | 1 | “I saw the couple yesterday at noon,” | monk | monk | agree | The traveling monk recounts seeing the couple. |
| q1_2 | 1 | “He carried a sword and bow, and his wife rode beside him.” | monk | monk | agree | This continues the monk’s account of the couple. |
| q2_1 | 2 | “I caught the famous bandit Tajomaru near the bridge,” | constable | constable | agree | The constable describes catching Tajomaru. |
| q2_2 | 2 | “He had fallen off a horse, but still had Takehiro’s bow. Find the wife and ask her what he did.” | constable | constable | agree | This continues the constable’s report and instruction. |
| q3_1 | 3 | “Takehiro, a kind samurai, married my daughter Masago,” | old_woman | old_woman | agree | The old woman identifies Takehiro as her daughter’s husband. |
| q3_2 | 3 | “She is proud and only nineteen. Please find her before you send me home without news.” | old_woman | old_woman | agree | She pleads for news of her daughter. |
| q4_1 | 4 | “I killed him fairly,” | tajomaru | tajomaru | agree | Tajomaru confesses and tells how he lured and tied up Takehiro. |
| q5_1 | 5 | “She held my arm and begged for one of us to die. She would leave with the man who lived. I freed him for a fair sword fight. Twenty-three blows—no other man had lasted twenty! She was gone when he fell. I took his weapons and left.” | None | tajomaru | llm_only | This continues Tajomaru’s account of the fight and his escape. |
| q6_1 | 6 | “I crawled towards my husband,” | masago | masago | agree | Masago tells her account at the temple. |
| q8_1 | 8 | “I later tried drowning myself, but I failed. Where can I go after that?” | None | masago | llm_only | This continues Masago’s account of her attempted drowning. |
| q9_1 | 9 | “I heard him speaking kindly to her,” | None | takehiro | llm_only | Takehiro’s spirit speaks through a medium and recounts events. |
| q13_1 | 13 | “I sank into the darkness and never came back.” | None | takehiro | llm_only | This concludes Takehiro’s account of his death. |

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
| full_story_part2_c3 | tajomaru | Orus | "She held my arm and begged for one of us to die. She would leave with the man who lived.  |
| full_story_part2_c4 | masago | Kore | "I crawled towards my husband," |
| full_story_part2_c6 | masago | Kore | "I later tried drowning myself, but I failed. Where can I go after that?" |
| full_story_part3_c1 | takehiro | Puck | "I heard him speaking kindly to her," |
| full_story_part3_c3 | takehiro | Puck | "I sank into the darkness and never came back." |

