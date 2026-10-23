# 話者表(全引用。人間確認用。LLM判定をそのまま採用、回想・独白の補助フィールドは設けない)

## Advanced

| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |
|---|---|---|---|---|---|---|
| q2_1 | 2 | “Just waiting for a friend,” | bob | bob | agree | Bob explains to the patrolman why he is waiting. |
| q2_2 | 2 | “There used to be a restaurant here.” | bob | bob | agree | Bob tells the patrolman about the restaurant where he and Jimmy last met. |
| q3_1 | 3 | “They pulled it down five years ago.” | None | patrolman | llm_only | The patrolman answers Bob about the restaurant. |
| q5_1 | 5 | “We had our last dinner there twenty years ago tonight. My best friend, Jimmy. We grew up together, like brothers.” | None | bob | llm_only | Bob recounts his last dinner with Jimmy. |
| q7_1 | 7 | “I went West,” | bob | bob | agree | Bob describes going West. |
| q7_2 | 7 | “Jimmy stayed here. He thought New York was the only place worth living. Before we parted, we promised to meet here at ten tonight, whatever happened.” | bob | bob | agree | Bob contrasts his own move with Jimmy staying in New York. |
| q8_1 | 8 | “Have you heard from him?” | None | patrolman | llm_only | The patrolman asks whether Bob has heard from Jimmy. |
| q9_1 | 9 | “Not for years. We lost touch.” | bob | bob | agree | Bob says he and Jimmy lost touch. |
| q9_2 | 9 | “Still, a promise meant something to Jimmy. He’ll come if he’s alive.” | bob | bob | agree | Bob says he expects Jimmy to keep their promise. |
| q10_1 | 10 | “How long will you wait?” | None | patrolman | llm_only | The patrolman asks how long Bob will wait. |
| q11_1 | 11 | “Half an hour.” | None | bob | llm_only | Bob answers that he will wait half an hour. |
| q12_1 | 12 | “Well, I hope he turns up. Good night.” | None | patrolman | llm_only | The patrolman wishes Bob well and says good night before walking on. |
| q16_1 | 16 | “Is that you, Bob?” | None | detective | llm_only | The tall plain-clothes officer, pretending to be Jimmy, asks Bob if he is Bob. |
| q17_1 | 17 | “Jimmy!” | None | bob | llm_only | Bob recognizes the tall man as Jimmy. |
| q22_1 | 22 | “You’re not Jimmy. Twenty years can change a man, but not the shape of his nose.” | None | bob | llm_only | Bob realizes the man is not Jimmy and says so. |
| q23_1 | 23 | “They can change a good man into a bad one,” | detective | detective | agree | The tall man replies that people can change. |
| q23_2 | 23 | “You’re under arrest, Bob. You’re wanted in Chicago.” | detective | detective | agree | The tall man identifies himself as the arresting officer and tells Bob he is und |
| q25_1 | 25 | “Before we go, there’s a note for you.” | None | detective | llm_only | The tall man tells Bob there is a note for him. |
| q27_1 | 27 | “Bob, it’s Jimmy. I was the patrolman you spoke to. I came on time to keep our promise. When you struck that match, I recognized your face as the man wanted in Chicago. But I couldn’t bring myself to arrest my old friend, so I found a plain-clothes officer to do it for me.” | None | patrolman | llm_only | The note is signed Jimmy and explains that its writer was the patrolman who spok |

dialogue clip(声がnarrator以外):

| clip | speaker | voice | text |
|---|---|---|---|
| full_story_part1_c2 | bob | Algieba | "Just waiting for a friend," |
| full_story_part1_c4 | bob | Algieba | "There used to be a restaurant here." |
| full_story_part1_c5 | patrolman | Schedar | "They pulled it down five years ago." |
| full_story_part1_c7 | bob | Algieba | "We had our last dinner there twenty years ago tonight. My best friend, Jimmy. We grew up  |
| full_story_part1_c9 | bob | Algieba | "I went West," |
| full_story_part1_c11 | bob | Algieba | "Jimmy stayed here. He thought New York was the only place worth living. Before we parted, |
| full_story_part2_c1 | patrolman | Schedar | "Have you heard from him?" |
| full_story_part2_c2 | bob | Algieba | "Not for years. We lost touch." |
| full_story_part2_c4 | bob | Algieba | "Still, a promise meant something to Jimmy. He'll come if he's alive." |
| full_story_part2_c5 | patrolman | Schedar | "How long will you wait?" |
| full_story_part2_c6 | bob | Algieba | "Half an hour." |
| full_story_part2_c7 | patrolman | Schedar | "Well, I hope he turns up. Good night." |
| full_story_part2_c9 | detective | Fenrir | "Is that you, Bob?" |
| full_story_part2_c10 | bob | Algieba | "Jimmy!" |
| full_story_part3_c1 | bob | Algieba | "You're not Jimmy. Twenty years can change a man, but not the shape of his nose." |
| full_story_part3_c2 | detective | Fenrir | "They can change a good man into a bad one," |
| full_story_part3_c4 | detective | Fenrir | "You're under arrest, Bob. You're wanted in Chicago." |
| full_story_part3_c6 | detective | Fenrir | "Before we go, there's a note for you." |
| full_story_part3_c8 | patrolman | Schedar | "Bob, it's Jimmy. I was the patrolman you spoke to. I came on time to keep our promise. Wh |

## Standard

| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |
|---|---|---|---|---|---|---|
| q2_1 | 2 | “I’m only waiting for a friend,” | bob | bob | agree | Bob tells the officer he is waiting for a friend. |
| q2_2 | 2 | “There was a restaurant here once.” | bob | bob | agree | Bob continues explaining that the restaurant used to be there. |
| q3_1 | 3 | “The restaurant was knocked down five years ago.” | None | patrolman | llm_only | The officer corrects Bob about when the restaurant was demolished. |
| q5_1 | 5 | “Jimmy and I ate there twenty years ago tonight. We were best friends and grew up like brothers.” | None | bob | llm_only | Bob tells the officer about his friendship and the restaurant. |
| q7_1 | 7 | “I moved West, but Jimmy stayed in New York. For him, no other place was good enough. We promised to meet here tonight at ten, whatever happened.” | None | bob | llm_only | Bob explains to the officer his move West and the promise to meet. |
| q8_1 | 8 | “Do you hear from him these days?” | None | patrolman | llm_only | The officer asks Bob whether he hears from Jimmy. |
| q9_1 | 9 | “We lost touch years ago,” | bob | bob | agree | The narration explicitly says Bob speaks this line. |
| q9_2 | 9 | “But Jimmy always kept his promises, so he’ll come if he’s alive.” | bob | bob | agree | Bob continues answering the officer about Jimmy's promise. |
| q10_1 | 10 | “How much longer will you stay?” | None | patrolman | llm_only | The officer asks how long Bob will wait. |
| q11_1 | 11 | “I’ll give him thirty minutes.” | None | bob | llm_only | Bob answers that he will wait thirty minutes. |
| q12_1 | 12 | “Good night, and I hope your friend arrives soon.” | None | patrolman | llm_only | The officer says good night as he continues down the street. |
| q16_1 | 16 | “Bob, is that really you?” | None | detective | llm_only | The tall man in the overcoat greets Bob. |
| q17_1 | 17 | “Jimmy, you’re here!” | None | bob | llm_only | Bob recognizes the tall man as Jimmy. |
| q22_1 | 22 | “You can’t be Jimmy! A man may look different after twenty years, but his nose won’t change.” | None | bob | llm_only | Bob challenges the tall man after noticing his nose is different. |
| q23_1 | 23 | “Twenty years can turn a good man bad,” | detective | detective | agree | The tall man replies to Bob's accusation. |
| q23_2 | 23 | “I’m arresting you, Bob, because Chicago’s police are looking for you.” | detective | detective | agree | The tall man says he is arresting Bob. |
| q25_1 | 25 | “I have a note for you before we leave.” | None | detective | llm_only | The tall man says he has a note for Bob before they leave. |
| q27_1 | 27 | “Bob, this is Jimmy. I was the officer who spoke to you. I came at ten to keep our promise. Your match lit your face, and I recognized you. I knew Chicago’s police were looking for you. I couldn’t arrest my old friend myself, so I found an officer in ordinary clothes to do it for me.” | None | patrolman | llm_only | This is the note signed Jimmy, written by the officer who spoke to Bob earlier. |

dialogue clip(声がnarrator以外):

| clip | speaker | voice | text |
|---|---|---|---|
| full_story_part1_c2 | bob | Algieba | "I'm only waiting for a friend," |
| full_story_part1_c4 | bob | Algieba | "There was a restaurant here once." |
| full_story_part1_c5 | patrolman | Schedar | "The restaurant was knocked down five years ago." |
| full_story_part1_c7 | bob | Algieba | "Jimmy and I ate there twenty years ago tonight. We were best friends and grew up like bro |
| full_story_part1_c9 | bob | Algieba | "I moved West, but Jimmy stayed in New York. For him, no other place was good enough. We p |
| full_story_part2_c1 | patrolman | Schedar | "Do you hear from him these days?" |
| full_story_part2_c2 | bob | Algieba | "We lost touch years ago," |
| full_story_part2_c4 | bob | Algieba | "But Jimmy always kept his promises, so he'll come if he's alive." |
| full_story_part2_c5 | patrolman | Schedar | "How much longer will you stay?" |
| full_story_part2_c6 | bob | Algieba | "I'll give him thirty minutes." |
| full_story_part2_c7 | patrolman | Schedar | "Good night, and I hope your friend arrives soon." |
| full_story_part2_c9 | detective | Fenrir | "Bob, is that really you?" |
| full_story_part2_c10 | bob | Algieba | "Jimmy, you're here!" |
| full_story_part3_c1 | bob | Algieba | "You can't be Jimmy! A man may look different after twenty years, but his nose won't chang |
| full_story_part3_c2 | detective | Fenrir | "Twenty years can turn a good man bad," |
| full_story_part3_c4 | detective | Fenrir | "I'm arresting you, Bob, because Chicago's police are looking for you." |
| full_story_part3_c6 | detective | Fenrir | "I have a note for you before we leave." |
| full_story_part3_c8 | patrolman | Schedar | "Bob, this is Jimmy. I was the officer who spoke to you. I came at ten to keep our promise |

