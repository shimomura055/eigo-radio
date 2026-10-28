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
| q0_1 | 0 | “This morning, I found a body in the bushes,” | woodcutter | woodcutter | agree | The woodcutter is identified as the speaker. |
| q0_2 | 0 | “He had one stab wound in his chest. His blood had dried. No sword or bow, sir, just rope under a cedar and a comb. The broken bamboo showed a fight.” | woodcutter | woodcutter | agree | This continues the woodcutter’s account of finding the body. |
| q1_1 | 1 | “I saw them yesterday at noon,” | monk | monk | agree | The monk is identified as the speaker. |
| q1_2 | 1 | “The man carried weapons, and his wife rode beside him with her face covered.” | monk | monk | agree | This continues the monk’s account of seeing the couple. |
| q2_1 | 2 | “I caught Tajomaru, the famous bandit,” | constable | constable | agree | The constable is identified as the speaker. |
| q2_2 | 2 | “He had Takehiro’s bow. Find the wife, and she’ll tell you what he did.” | constable | constable | agree | This continues the constable’s statement about catching Tajomaru. |
| q3_1 | 3 | “Takehiro was my daughter’s husband, a kind samurai,” | old_woman | old_woman | agree | The old woman is identified as the speaker. |
| q3_2 | 3 | “Masago is nineteen. Please find her before I go home without news.” | old_woman | old_woman | agree | This continues the old woman’s request for news of her daughter. |
| q4_1 | 4 | “I killed him, but listen before calling me a coward,” | tajomaru | tajomaru | agree | Tajomaru is identified as the speaker of his confession. |
| q5_1 | 5 | “She grabbed my arm and said one of us must die. She would leave with the man who lived. I untied him, and we fought fairly with swords. He lasted twenty-three strokes, but nobody else had reached twenty. When he fell, she’d disappeared. I took his weapons and went away.” | None | tajomaru | llm_only | This continues Tajomaru’s account of the fight and what followed. |
| q6_1 | 6 | “After the bandit left, I crawled towards my husband,” | masago | masago | agree | Masago is identified as the speaker recounting what happened after the bandit le |
| q8_1 | 8 | “I tried drowning myself later, but I couldn’t even do that. Where can I go from here?” | None | masago | llm_only | This continues Masago’s account at the temple. |
| q9_1 | 9 | “I heard the bandit trying to comfort her,” | None | takehiro | llm_only | Takehiro’s spirit speaks through a medium and recounts his own experience. |
| q13_1 | 13 | “Then I sank into darkness and stayed there for ever.” | None | takehiro | llm_only | This concludes Takehiro’s account. |

dialogue clip(声がnarrator以外):

| clip | speaker | voice | text |
|---|---|---|---|
| full_story_part1_c1 | woodcutter | Algieba | "This morning, I found a body in the bushes," |
| full_story_part1_c3 | woodcutter | Algieba | "He had one stab wound in his chest. His blood had dried. No sword or bow, sir, just rope  |
| full_story_part1_c4 | monk | Schedar | "I saw them yesterday at noon," |
| full_story_part1_c6 | monk | Schedar | "The man carried weapons, and his wife rode beside him with her face covered." |
| full_story_part1_c7 | constable | Fenrir | "I caught Tajomaru, the famous bandit," |
| full_story_part1_c9 | constable | Fenrir | "He had Takehiro's bow. Find the wife, and she'll tell you what he did." |
| full_story_part1_c10 | old_woman | Zephyr | "Takehiro was my daughter's husband, a kind samurai," |
| full_story_part1_c12 | old_woman | Zephyr | "Masago is nineteen. Please find her before I go home without news." |
| full_story_part2_c1 | tajomaru | Orus | "I killed him, but listen before calling me a coward," |
| full_story_part2_c3 | tajomaru | Orus | "She grabbed my arm and said one of us must die. She would leave with the man who lived. I |
| full_story_part2_c4 | masago | Kore | "After the bandit left, I crawled towards my husband," |
| full_story_part2_c6 | masago | Kore | "I tried drowning myself later, but I couldn't even do that. Where can I go from here?" |
| full_story_part3_c1 | takehiro | Puck | "I heard the bandit trying to comfort her," |
| full_story_part3_c3 | takehiro | Puck | "Then I sank into darkness and stayed there for ever." |

