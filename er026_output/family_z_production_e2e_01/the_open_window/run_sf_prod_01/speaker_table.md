# 話者表(全引用。人間確認用。LLM判定をそのまま採用、回想・独白の補助フィールドは設けない)

## Advanced

| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |
|---|---|---|---|---|---|---|
| q1_1 | 1 | “My aunt will be down soon,” | vera | vera | agree | The narration explicitly says Vera tells Framton her aunt will be down soon. |
| q1_2 | 1 | “Do you know much about her?” | vera | vera | agree | It continues Vera’s question to Framton. |
| q2_1 | 2 | “Almost nothing,” | None | framton | llm_only | The narration says he admitted knowing almost nothing. |
| q4_1 | 4 | “Her great tragedy happened three years ago today.” | None | vera | llm_only | Vera begins telling Framton about her aunt’s supposed tragedy. |
| q6_1 | 6 | “Her husband and her two young brothers went out shooting through that window. Their little brown spaniel went with them. They tried to cross a bog, but the ground gave way beneath them. They all disappeared. Their bodies were never found.” | None | vera | llm_only | This continues Vera’s account of the tragedy. |
| q7_1 | 7 | “How terrible,” | framton | framton | agree | The narration identifies Framton as murmuring this response. |
| q8_1 | 8 | “My aunt still thinks they’ll come back. She keeps the window open until dark, waiting for them.” | vera | vera | agree | Vera explains her aunt’s belief about the men returning. |
| q8_2 | 8 | “Her husband had his white coat over his arm. Her youngest brother was singing, ‘Bertie, why do you bound?’ He always sang it to tease her.” | vera | vera | agree | Vera continues describing the men and the song one brother sang. |
| q10_1 | 10 | “Sometimes, on evenings like this, I almost expect to see them.” | None | vera | llm_only | The narration says Vera looks across the lawn before she speaks. |
| q12_1 | 12 | “I hope Vera has kept you company! You don’t mind the open window? My husband and brothers will be back soon. They’ve been shooting. Their boots will be covered in mud, of course!” | None | mrs_sappleton | llm_only | The aunt hurries in and addresses her visitor. |
| q16_1 | 16 | “Here they are at last!” | None | mrs_sappleton | llm_only | The hostess’s face brightens as she sees the men arriving. |
| q21_1 | 21 | “Bertie, why do you bound?” | None | men | llm_only | A young voice from the approaching men sings the familiar song. |
| q25_1 | 25 | “Who was that?” | men | men | agree | The husband asks who the visitor was after stepping inside. |
| q26_1 | 26 | “A most peculiar visitor,” | None | mrs_sappleton | llm_only | The narration says the wife answers the husband. |
| q26_2 | 26 | “He talked about his nerves, then suddenly ran away.” | None | mrs_sappleton | llm_only | It continues the wife’s explanation of Framton’s sudden departure. |
| q27_1 | 27 | “It was the spaniel,” | vera | vera | agree | The narration explicitly attributes this statement to Vera. |
| q27_2 | 27 | “He told me he was terrified of dogs. In India, a pack chased him into an empty grave. He spent the whole night there, with them snarling above him.” | vera | vera | agree | Vera continues inventing an explanation for Framton’s flight. |

dialogue clip(声がnarrator以外):

| clip | speaker | voice | text |
|---|---|---|---|
| full_story_part1_c2 | vera | Zephyr | "My aunt will be down soon," |
| full_story_part1_c4 | vera | Zephyr | "Do you know much about her?" |
| full_story_part1_c5 | framton | Algieba | "Almost nothing," |
| full_story_part1_c7 | vera | Zephyr | "Her great tragedy happened three years ago today." |
| full_story_part1_c9 | vera | Zephyr | "Her husband and her two young brothers went out shooting through that window. Their littl |
| full_story_part1_c10 | framton | Algieba | "How terrible," |
| full_story_part1_c12 | vera | Zephyr | "My aunt still thinks they'll come back. She keeps the window open until dark, waiting for |
| full_story_part1_c14 | vera | Zephyr | "Her husband had his white coat over his arm. Her youngest brother was singing, 'Bertie, w |
| full_story_part2_c2 | vera | Zephyr | "Sometimes, on evenings like this, I almost expect to see them." |
| full_story_part2_c4 | mrs_sappleton | Kore | "I hope Vera has kept you company! You don't mind the open window? My husband and brothers |
| full_story_part2_c6 | mrs_sappleton | Kore | "Here they are at last!" |
| full_story_part3_c2 | men | Schedar | "Bertie, why do you bound?" |
| full_story_part3_c4 | men | Schedar | "Who was that?" |
| full_story_part3_c6 | mrs_sappleton | Kore | "A most peculiar visitor," |
| full_story_part3_c8 | mrs_sappleton | Kore | "He talked about his nerves, then suddenly ran away." |
| full_story_part3_c9 | vera | Zephyr | "It was the spaniel," |
| full_story_part3_c11 | vera | Zephyr | "He told me he was terrified of dogs. In India, a pack chased him into an empty grave. He  |

## Standard

| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |
|---|---|---|---|---|---|---|
| q1_1 | 1 | “My aunt will join us soon,” | vera | vera | agree | Vera says this as she introduces her aunt. |
| q1_2 | 1 | “How well do you know her?” | vera | vera | agree | Vera asks Framton how well he knows her aunt. |
| q2_1 | 2 | “I know very little,” | framton | framton | agree | The narration identifies Framton as the person answering. |
| q4_1 | 4 | “Something terrible happened to her exactly three years ago today.” | None | vera | llm_only | Vera begins her invented account of the tragedy. |
| q6_1 | 6 | “Her husband and two younger brothers left through that window. They went shooting, taking their small brown spaniel with them. They tried crossing wet ground, but it broke under them. All of them disappeared, and nobody ever found their bodies.” | None | vera | llm_only | Vera continues telling Framton the fabricated story. |
| q7_1 | 7 | “How awful,” | framton | framton | agree | Framton reacts to Vera’s story. |
| q8_1 | 8 | “She still believes they’ll return, so she waits until dark. That’s why she leaves the window open,” | vera | vera | agree | The narration explicitly says Vera said this. |
| q8_2 | 8 | “Her husband carried his white coat over his arm. Her youngest brother sang, ‘Bertie, why do you bound?’ He always sang that song to annoy her.” | vera | vera | agree | Vera continues her explanation; the song is quoted within her speech. |
| q10_1 | 10 | “On evenings like this, I sometimes think they might appear.” | None | vera | llm_only | Vera says this while looking across the lawn. |
| q12_1 | 12 | “Has Vera been looking after you? I hope the open window doesn’t bother you. My husband and brothers are coming back from shooting soon. Their boots will be muddy, as usual!” | None | mrs_sappleton | llm_only | The aunt enters and addresses Framton about Vera and the open window. |
| q16_1 | 16 | “Look, they’re finally home!” | None | mrs_sappleton | llm_only | Mrs. Sappleton smiles at the returning men and announces their arrival. |
| q21_1 | 21 | “Bertie, why do you bound?” | None | men | llm_only | One of the returning men calls out the familiar song. |
| q25_1 | 25 | “Who just left?” | men | men | agree | Mrs. Sappleton’s husband asks who left. |
| q26_1 | 26 | “Such a strange man,” | None | mrs_sappleton | llm_only | She replies to her husband’s question. |
| q26_2 | 26 | “He described his nervous problems, then ran off without warning.” | None | mrs_sappleton | llm_only | She continues describing Framton’s departure. |
| q27_1 | 27 | “The dog frightened him,” | vera | vera | agree | Vera offers an explanation for Framton’s sudden flight. |
| q27_2 | 27 | “He told me dogs terrified him. A group chased him into an empty grave in India. He stayed there all night while they growled above him.” | vera | vera | agree | Vera continues her invented story about Framton. |

dialogue clip(声がnarrator以外):

| clip | speaker | voice | text |
|---|---|---|---|
| full_story_part1_c2 | vera | Zephyr | "My aunt will join us soon," |
| full_story_part1_c4 | vera | Zephyr | "How well do you know her?" |
| full_story_part1_c5 | framton | Algieba | "I know very little," |
| full_story_part1_c7 | vera | Zephyr | "Something terrible happened to her exactly three years ago today." |
| full_story_part1_c9 | vera | Zephyr | "Her husband and two younger brothers left through that window. They went shooting, taking |
| full_story_part1_c10 | framton | Algieba | "How awful," |
| full_story_part1_c12 | vera | Zephyr | "She still believes they'll return, so she waits until dark. That's why she leaves the win |
| full_story_part1_c14 | vera | Zephyr | "Her husband carried his white coat over his arm. Her youngest brother sang, 'Bertie, why  |
| full_story_part2_c2 | vera | Zephyr | "On evenings like this, I sometimes think they might appear." |
| full_story_part2_c4 | mrs_sappleton | Kore | "Has Vera been looking after you? I hope the open window doesn't bother you. My husband an |
| full_story_part2_c6 | mrs_sappleton | Kore | "Look, they're finally home!" |
| full_story_part3_c2 | men | Schedar | "Bertie, why do you bound?" |
| full_story_part3_c4 | men | Schedar | "Who just left?" |
| full_story_part3_c6 | mrs_sappleton | Kore | "Such a strange man," |
| full_story_part3_c8 | mrs_sappleton | Kore | "He described his nervous problems, then ran off without warning." |
| full_story_part3_c9 | vera | Zephyr | "The dog frightened him," |
| full_story_part3_c11 | vera | Zephyr | "He told me dogs terrified him. A group chased him into an empty grave in India. He stayed |

