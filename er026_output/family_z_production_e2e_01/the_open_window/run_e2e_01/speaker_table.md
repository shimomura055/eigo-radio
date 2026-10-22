# 話者表(全引用。人間確認用。LLM判定をそのまま採用、回想・独白の補助フィールドは設けない)

## Advanced

| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |
|---|---|---|---|---|---|---|
| q1_1 | 1 | “My aunt will be down soon,” | vera | vera | agree | The fifteen-year-old girl says her aunt will be down soon. |
| q1_2 | 1 | “Do you know much about her?” | vera | vera | agree | It continues the girl's question to Framton. |
| q2_1 | 2 | “Nothing, really.” | None | framton | llm_only | He replies that he knows nothing about the aunt. |
| q4_1 | 4 | “You may wonder why that’s open in October.” | None | vera | llm_only | The girl begins explaining the open window. |
| q5_1 | 5 | “It’s quite warm,” | framton | framton | agree | Framton answers that it is quite warm. |
| q6_1 | 6 | “Three years ago today, her husband and her two young brothers went shooting. They left through that window.” | None | vera | llm_only | The girl tells Framton what happened to her aunt's husband and brothers. |
| q8_1 | 8 | “They never came back. They crossed the marsh where the ground seemed firm, and all three sank into a bog. Their little brown spaniel went too. The bodies were never found.” | None | vera | llm_only | She continues the story of their disappearance. |
| q10_1 | 10 | “My aunt thinks they’ll return. She keeps the window open until dark. Her husband had his white waterproof coat over his shoulders. Her youngest brother sang, ‘Oh, brother, why do you bound?’ He always did that to annoy her.” | None | vera | llm_only | The girl describes her aunt's belief and the men's habits. |
| q12_1 | 12 | “Sometimes, when it starts getting dark, I almost feel they really will—” | None | vera | llm_only | The girl says she almost feels the men will return. |
| q15_1 | 15 | “I hope my niece has entertained you. You don’t mind the open window? My husband and brothers will be back directly. They’ve been shooting. Such a mess they’ll make of my carpets!” | None | mrs_sappleton | llm_only | The hostess speaks to Framton about her niece and the open window. |
| q18_1 | 18 | “Here they are at last!” | None | mrs_sappleton | llm_only | The hostess recognizes the approaching men and announces their return. |
| q22_1 | 22 | “Oh, brother, why do you bound?” | None | men | llm_only | One of the returning men calls out the song, as the girl had described. |
| q25_1 | 25 | “Who was that running away?” | men | men | agree | The husband asks who ran away. |
| q26_1 | 26 | “A most peculiar visitor,” | None | mrs_sappleton | llm_only | The wife replies to her husband's question. |
| q26_2 | 26 | “You’d think he’d seen a ghost.” | None | mrs_sappleton | llm_only | The wife continues describing the visitor. |
| q27_1 | 27 | “It was the spaniel,” | vera | vera | agree | The girl calmly explains that the visitor was frightened by the spaniel. |
| q27_2 | 27 | “He told me he was terrified of dogs. A pack once chased him into a cemetery. He spent the night in an empty grave, with them looking down at him.” | vera | vera | agree | She continues her invented explanation of Framton's fear. |
| q29_1 | 29 | “He said they took turns.” | None | vera | llm_only | The girl adds another detail to her story about the visitor. |

dialogue clip(声がnarrator以外):

| clip | speaker | voice | text |
|---|---|---|---|
| full_story_part1_c2 | vera | Zephyr | "My aunt will be down soon," |
| full_story_part1_c4 | vera | Zephyr | "Do you know much about her?" |
| full_story_part1_c5 | framton | Algieba | "Nothing, really." |
| full_story_part1_c7 | vera | Zephyr | "You may wonder why that's open in October." |
| full_story_part1_c8 | framton | Algieba | "It's quite warm," |
| full_story_part1_c10 | vera | Zephyr | "Three years ago today, her husband and her two young brothers went shooting. They left th |
| full_story_part1_c12 | vera | Zephyr | "They never came back. They crossed the marsh where the ground seemed firm, and all three  |
| full_story_part2_c2 | vera | Zephyr | "My aunt thinks they'll return. She keeps the window open until dark. Her husband had his  |
| full_story_part2_c4 | vera | Zephyr | "Sometimes, when it starts getting dark, I almost feel they really will—" |
| full_story_part2_c6 | mrs_sappleton | Kore | "I hope my niece has entertained you. You don't mind the open window? My husband and broth |
| full_story_part2_c8 | mrs_sappleton | Kore | "Here they are at last!" |
| full_story_part3_c2 | men | Schedar | "Oh, brother, why do you bound?" |
| full_story_part3_c4 | men | Schedar | "Who was that running away?" |
| full_story_part3_c6 | mrs_sappleton | Kore | "A most peculiar visitor," |
| full_story_part3_c8 | mrs_sappleton | Kore | "You'd think he'd seen a ghost." |
| full_story_part3_c9 | vera | Zephyr | "It was the spaniel," |
| full_story_part3_c11 | vera | Zephyr | "He told me he was terrified of dogs. A pack once chased him into a cemetery. He spent the |
| full_story_part3_c13 | vera | Zephyr | "He said they took turns." |

## Standard

| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |
|---|---|---|---|---|---|---|
| q1_1 | 1 | “My aunt will come downstairs in a minute,” | None | vera | llm_only | The fifteen-year-old niece says her aunt will come downstairs. |
| q1_2 | 1 | “How well do you know her?” | None | vera | llm_only | She asks Framton how well he knows her aunt. |
| q2_1 | 2 | “I don’t really know anything about her.” | None | framton | llm_only | He answers that he does not know anything about the aunt. |
| q4_1 | 4 | “Doesn’t that open window seem strange at this time in October?” | None | vera | llm_only | She draws attention to the open window before Framton comments on the warm weath |
| q5_1 | 5 | “Well, the weather’s still quite warm,” | framton | framton | agree | The narration explicitly says Framton answered. |
| q6_1 | 6 | “Her husband and two young brothers went shooting three years ago today. They went outside through that very window.” | None | vera | llm_only | She begins the invented story about her aunt’s husband and brothers. |
| q8_1 | 8 | “They never came back from the marsh, where the ground seemed firm. All three sank into deep mud with their little brown spaniel. Nobody ever found their bodies.” | None | vera | llm_only | She continues the story of the men disappearing in the marsh. |
| q10_1 | 10 | “She expects them back and leaves it open until dark. Her husband wore a white waterproof coat over his shoulders. Her youngest brother sang, ‘Oh, brother, why are you jumping?’ He always sang that to annoy her.” | None | vera | llm_only | She explains the open window and adds details about the men and the song. |
| q12_1 | 12 | “When it starts getting dark, I sometimes almost feel they really will—” | None | vera | llm_only | She continues her tale, saying she almost believes the men will return. |
| q15_1 | 15 | “I hope you’ve enjoyed talking to my niece. Is the open window all right with you? My husband and brothers will soon return from shooting. They’ll get my carpets so dirty!” | None | mrs_sappleton | llm_only | The host speaks to Framton about her niece, the window, and her husband and brot |
| q18_1 | 18 | “They’re finally back!” | None | mrs_sappleton | llm_only | The aunt recognizes the returning men and announces their arrival. |
| q22_1 | 22 | “Oh, brother, why are you jumping?” | None | men | llm_only | One of the returning men calls out the song associated with Ronnie. |
| q25_1 | 25 | “Who’s the man who just ran away?” | men | men | agree | The husband asks who ran away as he cleans his boots. |
| q26_1 | 26 | “Such a strange visitor!” | None | mrs_sappleton | llm_only | The aunt replies that the visitor was strange. |
| q26_2 | 26 | “He looked like he’d seen a ghost.” | None | mrs_sappleton | llm_only | She continues describing Framton’s frightened appearance. |
| q27_1 | 27 | “The spaniel frightened him,” | vera | vera | agree | The girl explains that the spaniel frightened Framton. |
| q27_2 | 27 | “He told me he was terribly afraid of dogs. Once, a pack chased him into a cemetery. He spent the night in an empty grave, with the dogs looking down at him.” | vera | vera | agree | She invents the story about Framton’s fear of dogs. |
| q29_1 | 29 | “He told me they took turns.” | None | vera | llm_only | She adds that the dogs took turns watching him, continuing her explanation. |

dialogue clip(声がnarrator以外):

| clip | speaker | voice | text |
|---|---|---|---|
| full_story_part1_c2 | vera | Zephyr | "My aunt will come downstairs in a minute," |
| full_story_part1_c4 | vera | Zephyr | "How well do you know her?" |
| full_story_part1_c5 | framton | Algieba | "I don't really know anything about her." |
| full_story_part1_c7 | vera | Zephyr | "Doesn't that open window seem strange at this time in October?" |
| full_story_part1_c8 | framton | Algieba | "Well, the weather's still quite warm," |
| full_story_part1_c10 | vera | Zephyr | "Her husband and two young brothers went shooting three years ago today. They went outside |
| full_story_part1_c12 | vera | Zephyr | "They never came back from the marsh, where the ground seemed firm. All three sank into de |
| full_story_part2_c2 | vera | Zephyr | "She expects them back and leaves it open until dark. Her husband wore a white waterproof  |
| full_story_part2_c4 | vera | Zephyr | "When it starts getting dark, I sometimes almost feel they really will—" |
| full_story_part2_c6 | mrs_sappleton | Kore | "I hope you've enjoyed talking to my niece. Is the open window all right with you? My husb |
| full_story_part2_c8 | mrs_sappleton | Kore | "They're finally back!" |
| full_story_part3_c2 | men | Schedar | "Oh, brother, why are you jumping?" |
| full_story_part3_c4 | men | Schedar | "Who's the man who just ran away?" |
| full_story_part3_c6 | mrs_sappleton | Kore | "Such a strange visitor!" |
| full_story_part3_c8 | mrs_sappleton | Kore | "He looked like he'd seen a ghost." |
| full_story_part3_c9 | vera | Zephyr | "The spaniel frightened him," |
| full_story_part3_c11 | vera | Zephyr | "He told me he was terribly afraid of dogs. Once, a pack chased him into a cemetery. He sp |
| full_story_part3_c13 | vera | Zephyr | "He told me they took turns." |

