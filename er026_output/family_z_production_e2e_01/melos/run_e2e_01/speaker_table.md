# 話者表(全引用。人間確認用。LLM判定をそのまま採用、回想・独白の補助フィールドは設けない)

## Advanced

| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |
|---|---|---|---|---|---|---|
| q1_1 | 1 | “You kill people without a fair trial,” | king | melos | human_override | Melos addresses the ruler, accusing him of killing people without a fair trial. |
| q1_2 | 1 | “A man only has to frighten you, and you order his death.” | king | melos | human_override | This continues Melos’s accusation to the ruler. |
| q3_1 | 3 | “Then you shall die as well.” | king | king | agree | The ruler threatens Melos with death. |
| q5_1 | 5 | “Give me three days,” | None | melos | llm_only | Melos asks the ruler for three days. |
| q5_2 | 5 | “My sister is getting married. Let me attend her wedding. Then I will return.” | None | melos | llm_only | Melos explains that he wants to attend his sister’s wedding and return. |
| q6_1 | 6 | “To your own execution?” | king | king | agree | The ruler laughs and challenges Melos about returning to his execution. |
| q7_1 | 7 | “My friend will stay in my place.” | None | melos | llm_only | Melos offers his friend to stay in his place. |
| q9_1 | 9 | “Before sunset on the third day,” | friend | king | human_override | The ruler sets the deadline for Melos’s return. |
| q9_2 | 9 | “If you are late, your friend dies.” | None | king | llm_only | The ruler warns that the friend will die if Melos is late. |
| q11_1 | 11 | “Go. I’ll wait.” | None | friend | llm_only | Melos’s friend tells him to go and promises to wait. |
| q28_1 | 28 | “I’ll wait.” | None | friend | llm_only | This repeats the friend’s earlier promise that he would wait. |
| q35_1 | 35 | “Wait!” | None | melos | llm_only | Melos calls out to stop the execution as he arrives. |
| q37_1 | 37 | “I’m here.” | None | melos | llm_only | Melos announces that he is there. |
| q40_1 | 40 | “I nearly gave up,” | None | melos | llm_only | Melos tells his friend that he nearly gave up. |
| q41_1 | 41 | “But you came.” | None | friend | llm_only | His friend responds that Melos came. |
| q43_1 | 43 | “I believed every man would save himself,” | None | king | llm_only | The ruler reflects on his belief that everyone would save himself. |
| q46_1 | 46 | “Could you teach me to trust?” | None | king | llm_only | The ruler asks the friends to teach him to trust. |

dialogue clip(声がnarrator以外):

| clip | speaker | voice | text |
|---|---|---|---|
| full_story_part1_c2 | melos | Algieba | "You kill people without a fair trial," |
| full_story_part1_c4 | melos | Algieba | "A man only has to frighten you, and you order his death." |
| full_story_part1_c6 | king | Charon | "Then you shall die as well." |
| full_story_part1_c8 | melos | Algieba | "Give me three days," |
| full_story_part1_c10 | melos | Algieba | "My sister is getting married. Let me attend her wedding. Then I will return." |
| full_story_part1_c11 | king | Charon | "To your own execution?" |
| full_story_part1_c13 | melos | Algieba | "My friend will stay in my place." |
| full_story_part1_c15 | king | Charon | "Before sunset on the third day," |
| full_story_part1_c17 | king | Charon | "If you are late, your friend dies." |
| full_story_part1_c19 | friend | Erinome | "Go. I'll wait." |
| full_story_part2_c3 | friend | Erinome | "I'll wait." |
| full_story_part3_c2 | melos | Algieba | "Wait!" |
| full_story_part3_c4 | melos | Algieba | "I'm here." |
| full_story_part3_c6 | melos | Algieba | "I nearly gave up," |
| full_story_part3_c8 | friend | Erinome | "But you came." |
| full_story_part3_c10 | king | Charon | "I believed every man would save himself," |
| full_story_part3_c12 | king | Charon | "Could you teach me to trust?" |

## Standard

| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |
|---|---|---|---|---|---|---|
| q1_1 | 1 | “You give people no fair trial before killing them,” | king | melos | human_override | He tells the ruler that people are killed without fair trials. |
| q1_2 | 1 | “If someone scares you, you order his death.” | king | melos | human_override | It continues Melos’s accusation against the ruler. |
| q3_1 | 3 | “You will die too.” | king | king | agree | The ruler threatens Melos. |
| q5_1 | 5 | “May I have three days for my sister’s wedding?” | None | melos | llm_only | Melos asks the ruler for three days. |
| q5_2 | 5 | “Then I'll come back.” | None | melos | llm_only | Melos promises to return. |
| q6_1 | 6 | “Back to die?” | king | king | agree | The ruler asks whether Melos will come back to die. |
| q7_1 | 7 | “My friend can take my place here.” | None | melos | llm_only | Melos offers his friend as a substitute. |
| q9_1 | 9 | “Return before sunset on day three,” | friend | king | human_override | The ruler sets the deadline for Melos’s return. |
| q9_2 | 9 | “Your friend dies if you're late.” | None | king | llm_only | The ruler threatens Melos’s friend if Melos is late. |
| q11_1 | 11 | “Leave now. I'll wait for you.” | None | friend | llm_only | Melos’s friend tells him to leave and promises to wait. |
| q28_1 | 28 | “I'll wait for you.” | None | friend | llm_only | Melos remembers his friend saying this as he held his hand. |
| q35_1 | 35 | “Wait, please!” | None | melos | llm_only | Melos arrives and calls for the execution to stop. |
| q37_1 | 37 | “I've come back!” | None | melos | llm_only | Melos announces that he has returned. |
| q40_1 | 40 | “I almost stopped trying,” | None | melos | llm_only | Melos admits to his friend that he almost gave up. |
| q41_1 | 41 | “You came back, though.” | None | friend | llm_only | His friend responds to Melos’s admission. |
| q43_1 | 43 | “I thought everyone would save himself,” | None | king | llm_only | The ruler says he thought everyone would save himself. |
| q46_1 | 46 | “Can you show me how to trust?” | None | king | llm_only | The ruler asks the two men to teach him trust. |

dialogue clip(声がnarrator以外):

| clip | speaker | voice | text |
|---|---|---|---|
| full_story_part1_c2 | melos | Algieba | "You give people no fair trial before killing them," |
| full_story_part1_c4 | melos | Algieba | "If someone scares you, you order his death." |
| full_story_part1_c6 | king | Charon | "You will die too." |
| full_story_part1_c8 | melos | Algieba | "May I have three days for my sister's wedding?" |
| full_story_part1_c10 | melos | Algieba | "Then I'll come back." |
| full_story_part1_c12 | king | Charon | "Back to die?" |
| full_story_part1_c13 | melos | Algieba | "My friend can take my place here." |
| full_story_part1_c15 | king | Charon | "Return before sunset on day three," |
| full_story_part1_c17 | king | Charon | "Your friend dies if you're late." |
| full_story_part1_c19 | friend | Erinome | "Leave now. I'll wait for you." |
| full_story_part2_c3 | friend | Erinome | "I'll wait for you." |
| full_story_part3_c2 | melos | Algieba | "Wait, please!" |
| full_story_part3_c4 | melos | Algieba | "I've come back!" |
| full_story_part3_c6 | melos | Algieba | "I almost stopped trying," |
| full_story_part3_c8 | friend | Erinome | "You came back, though." |
| full_story_part3_c10 | king | Charon | "I thought everyone would save himself," |
| full_story_part3_c12 | king | Charon | "Can you show me how to trust?" |

