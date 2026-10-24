# Fable CPチェックリスト(機械生成: the_tell_tale_heart、essentials sha 5e74e34b91d6)

各行の『本文の該当引用』欄にstage別の本文引用(逐語)を記入する。引用できない=欠落。判定・記入はCP担当(Fable/Sonnet記入→Fable確認)。

処置規則(ユーザー承認2026-10-23): (A)重大=ending_reveal・key_roles(keep_name人物の脱落/他人名の増加)・key_causality・setups_and_payoffsのいずれかの欠落 -> CP不合格。TTS前に修正(Writer再実行=承認済みの明示--regenerate-stage、または決定論パッチ)し、原因分析を記録し、C案(軽量事後確認)要否をユーザーへ提示する(報告で`判断候補`)。(B)軽微=結末直前の付加文など、結末前の示唆(withhold_until_end)を希釈する不要文のみ -> 決定論の削除パッチ(exact文字列の削除)を適用し、削除した文・理由・前後sha・対象stageを記録する。所見を処置せずTTSへ進めてはならない。自動判定・LLM検査・retry・Human Reviewは無い。

| # | 深刻度 | 項目 | 内容 | 本文の該当引用(r0) | 本文の該当引用(r1) | 本文の該当引用(r2) | 本文の該当引用(std_adjust) | 判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | 重大 | ending_reveal(種明かしが最終に在る) | The narrator, who has insisted all along that he is calm and sane, sits above the floorboards where he hid the old man's body while the officers chat. He hears the low, quick beating again, louder and louder, which the officers do not seem to hear; he decides they know and are mocking him, cannot bear it, and screams that he did the deed and that they must tear up the planks, because it is the beating of the old man's hideous heart. The story ends on that confession, with no aftermath and no explanation of whether the sound was real or only in his mind. [原作最終文: It is the beating of his hideous heart!] |  |  |  |  |  |
| 2 | 軽微 | withhold_until_end(結末前の示唆・結末直前の付加文が無い) | Before the final scene, do not hint that the narrator will confess, that the officers will not hear the sound, or that the sound in the last scene is the heartbeat again; do not explain the ending, say whether the sound was real or imagined, mention an arrest or any aftermath, or add a moral or comment. |  |  |  |  |  |
| 3 | 重大 | setup と payoff | The narrator claims his senses are over-acute and that he hears all things in heaven and earth, so he is not mad, and he asks the listener to judge how calmly he tells the story  ->  In the last scene he alone hears the low, quick heartbeat of the dead man, louder and louder, and is driven to confess |  |  |  |  |  |
| 4 | 重大 | setup と payoff | The old man's pale blue 'vulture eye' is the only reason for the killing; it is closed on seven midnights, so the narrator cannot act  ->  On the eighth night the ray of light falls on the wide-open eye and the heartbeat begins, and the narrator kills the old man |  |  |  |  |  |
| 5 | 重大 | key_role(役割・関係で表され名前が付いていない) | the narrator, the unnamed first-person speaker who insists he is sane, kills the old man and finally confesses |  |  |  |  |  |
| 6 | 重大 | key_role(役割・関係で表され名前が付いていない) | the old man, the narrator's housemate whose pale blue vulture eye the narrator cannot bear, who is killed on the eighth night |  |  |  |  |  |
| 7 | 重大 | key_role(役割・関係で表され名前が付いていない) | the three police officers who come at four in the morning, are welcomed and shown the house, and sit chatting above the hidden body |  |  |  |  |  |
| 8 | 重大 | key_causality | The narrator, obsessed with the old man's vulture eye, looks in on seven midnights but the eye is always closed; on the eighth night the old man wakes and sits listening in terror, the ray falls on the open eye, the narrator hears the heart beat louder and louder and, afraid a neighbour will hear it, kills the old man and hides the body under the floor; the officers come because a neighbour heard a shriek, the narrator confidently seats himself over the hiding place, hears the beating again, louder and louder, and unable to bear it confesses. |  |  |  |  |  |

## 各stageの最終段落(機械抽出、参考。結末直前の付加文の有無はこの直前段落も確認)

### r0(段落数19、語数421)
- 最終段落: “Stop pretending!” I screamed. “I did it! Tear up the planks! Here, here! It is the beating of his hideous heart!”
- 最終の直前段落: I could not bear another moment.

### r1(段落数16、語数437)
- 最終段落: “Stop pretending!” I screamed. “I did it! Tear up the planks! Here, beneath my chair! It is the beating of his hideous heart!”
- 最終の直前段落: They heard it. They knew! Those smiles were meant to mock me. I could not bear another moment.

### r2(段落数17、語数409)
- 最終段落: “Stop pretending!” I screamed. “I did it! Tear up the planks! Here, under my chair! It is the beating of his hideous heart!”
- 最終の直前段落: Of course they heard! They knew everything. Their smiles mocked me. The beating grew louder, louder. I could not bear it.

### std_adjust(段落数17、語数424)
- 最終段落: “Don’t pretend anymore!” I shouted. “I killed him! Pull up the floorboards, here below my chair! That is his terrible heart beating!”
- 最終の直前段落: Of course they heard, and they knew what I had done! Behind those smiles, they were laughing at me. The beating kept growing louder until I could stand no more.


## narration行(DEV追加。DESIGN_02 §3-4)

| 深刻度 | 項目 | 内容 | 本文の該当引用(r0/r1/r2/std) | 判定 |
|---|---|---|---|---|
| 重大 | narration(人称・語り手の立場) | The narrator speaks as 'I' (an unnamed first-person speaker) and keeps addressing the listener as 'you'; his calm, proud, over-confident voice, insisting that he is sane while he relishes his own cunning, is where the horror comes from. |  |  |
