# Fable CPチェックリスト(機械生成: in_a_grove、essentials sha a931dbcde7fe)

各行の『本文の該当引用』欄にstage別の本文引用(逐語)を記入する。引用できない=欠落。判定・記入はCP担当(Fable/Sonnet記入→Fable確認)。

処置規則(ユーザー承認2026-10-23。narrationを(A)へ追加=案A承認2026-10-25の§1語り口維持・§6 PRODUCTION_WIRED条件との整合): (A)重大=ending_reveal・key_roles(keep_name人物の脱落/他人名の増加)・key_causality・setups_and_payoffs・narration(人称・視点・語り手の立場の変更)のいずれかの欠落 -> CP不合格。TTS前に修正(Writer再実行=承認済みの明示--regenerate-stage、または決定論パッチ)し、原因分析を記録し、C案(軽量事後確認)要否をユーザーへ提示する(報告で`判断候補`)。(B)軽微=結末直前の付加文など、結末前の示唆(withhold_until_end)を希釈する不要文のみ -> 決定論の削除パッチ(exact文字列の削除)を適用し、削除した文・理由・前後sha・対象stageを記録する。所見を処置せずTTSへ進めてはならない。自動判定・LLM検査・retry・Human Reviewは無い。

| # | 深刻度 | 項目 | 内容 | 本文の該当引用(r0) | 本文の該当引用(r1) | 本文の該当引用(r2) | 本文の該当引用(std_adjust) | 判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | 重大 | ending_reveal(種明かしが最終に在る) | The last testimony, spoken by the dead man's spirit through a medium, says that after the bandit left and his wife fled, he rose from the cedar, took up the small dagger she had dropped and stabbed himself in the chest; the thicket fell silent, then someone crept up to him and an unseen hand quietly drew the dagger out of his chest, and he sank for ever into the darkness. The story ends on that last scene, with no verdict, no word on which of the three accounts is true, and no explanation of who the unseen person was or what really happened. [原作最終文: おれはそれぎり永久に、中有の闇へ沈んでしまった。] |  |  |  |  |  |
| 2 | 軽微 | withhold_until_end(結末前の示唆・結末直前の付加文が無い) | Before the last testimony, do not say or hint what the dead man will tell (that he stabbed himself, or that an unseen hand drew the dagger from his chest), and do not preview, in the introductions or anywhere else, what any later testimony will say; never tell the listener who the real killer is or which account is true, never say that the accounts will be settled or explained, and never add a verdict, a solution, a moral or a comment. |  |  |  |  |  |
| 3 | 重大 | key_role keep_name=Tajomaru(名前が維持され他人名が増えていない) | the famous bandit, caught by the constable, who confesses with pride that he killed the man in a fair sword fight |  |  |  |  |  |
| 4 | 重大 | key_role keep_name=Masago(名前が維持され他人名が増えていない) | the wife, who says in her account at the temple that she herself stabbed her helpless husband with the dagger |  |  |  |  |  |
| 5 | 重大 | key_role keep_name=Takehiro(名前が維持され他人名が増えていない) | the dead husband, a samurai, whose spirit speaks through a medium and says he killed himself with the dagger |  |  |  |  |  |
| 6 | 重大 | key_role(役割・関係で表され名前が付いていない) | the woodcutter who found the body, a brief outside witness |  |  |  |  |  |
| 7 | 重大 | key_role(役割・関係で表され名前が付いていない) | the traveling monk who met the couple the day before, a brief outside witness |  |  |  |  |  |
| 8 | 重大 | key_role(役割・関係で表され名前が付いていない) | the constable who caught the bandit and blames him |  |  |  |  |  |
| 9 | 重大 | key_role(役割・関係で表され名前が付いていない) | the old woman, Masago's mother, who begs the magistrate to find her daughter |  |  |  |  |  |
| 10 | 重大 | key_causality | One man is found dead in a thicket, and seven people speak about it in turn: four outsiders set the scene (no sword found, only a rope and a comb; the man had been travelling with his wife; the bandit Tajomaru was caught with his bow; the wife is missing), and then each of the three people who were there claims the death for himself or herself, for reasons that fit their own pride, shame or bitterness: Tajomaru says he killed the husband fairly after the wife begged one of the two men to die, Masago says she stabbed her helpless husband because of the cold contempt in his eyes, and Takehiro says he killed himself after his wife asked the bandit to kill him; the accounts clash on who did what, and no one, in or out of the story, resolves the clash. |  |  |  |  |  |
| 11 | 重大 | narration(人称・語り手の立場が各stageで保たれている) | The story has no narrator of its own: it is a series of spoken testimonies, each told in the first person ('I') by the person who gives it, in that person's own voice and self-interest; a short, neutral outside narrator may only say who is speaking (for example 'The woodcutter was questioned first.'), never judges, comments or says which account is true, and is never the one who knows what happened; the police magistrate who questions the witnesses stays silent, and the dead man speaks through a medium but in his own first-person voice. |  |  |  |  |  |

## 各stageの最終段落(機械抽出、参考。結末直前の付加文の有無はこの直前段落も確認)

### r0(段落数8、語数426)
- 最終段落: “I rose from the cedar and picked up the small dagger she had dropped. I stabbed myself in the chest. The thicket fell silent. Then someone crept towards me on soft feet. An unseen hand quietly drew the dagger from my chest. I sank for ever into the darkness.”
- 最終の直前段落: “I heard the bandit comforting her,” said Takehiro’s spirit through the medium. “Then my wife said, ‘Take me anywhere.’ She pointed at me. ‘Kill that man.’ The bandit pushed her away and asked me whether she should live or die. For that, I almost forgave him. But she fled. He cut one rope and left.

### r1(段落数14、語数433)
- 最終段落: “I sank for ever into the darkness.”
- 最終の直前段落: “The thicket fell silent. Then someone crept towards me on soft feet. An unseen hand quietly drew the dagger from my chest.

### r2(段落数14、語数421)
- 最終段落: “I sank for ever into the darkness.”
- 最終の直前段落: “The thicket fell silent. Then someone crept towards me on soft feet. An unseen hand quietly drew the dagger from my chest.

### std_adjust(段落数14、語数422)
- 最終段落: “Then I sank into darkness and stayed there for ever.”
- 最終の直前段落: “The bushes around me became silent. Then someone came towards me with slow, quiet steps. A hand I couldn’t see quietly pulled the dagger from my chest.

