# Fable CPチェックリスト(機械生成: yuki_onna、essentials sha 9c77e83ab1cd)

各行の『本文の該当引用』欄にstage別の本文引用(逐語)を記入する。引用できない=欠落。判定・記入はCP担当(Fable/Sonnet記入→Fable確認)。

処置規則(ユーザー承認2026-10-23。narrationを(A)へ追加=案A承認2026-10-25の§1語り口維持・§6 PRODUCTION_WIRED条件との整合): (A)重大=ending_reveal・key_roles(keep_name人物の脱落/他人名の増加)・key_causality・setups_and_payoffs・narration(人称・視点・語り手の立場の変更)のいずれかの欠落 -> CP不合格。TTS前に修正(Writer再実行=承認済みの明示--regenerate-stage、または決定論パッチ)し、原因分析を記録し、C案(軽量事後確認)要否をユーザーへ提示する(報告で`判断候補`)。(B)軽微=結末直前の付加文など、結末前の示唆(withhold_until_end)を希釈する不要文のみ -> 決定論の削除パッチ(exact文字列の削除)を適用し、削除した文・理由・前後sha・対象stageを記録する。所見を処置せずTTSへ進めてはならない。自動判定・LLM検査・retry・Human Reviewは無い。

| # | 深刻度 | 項目 | 内容 | 本文の該当引用(r0) | 本文の該当引用(r1) | 本文の該当引用(r2) | 本文の該当引用(std_adjust) | 判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | 重大 | ending_reveal(種明かしが最終に在る) | Years after the night in the hut, Minokichi breaks his promise: by the lamp he tells his wife Yuki the whole story of the woman in white, saying she looked very like her. Yuki then reveals that she was that woman, repeats that she told him she would kill him if he ever said a word, and says that only the sleeping children keep her from killing him now; she orders him to take very good care of them. Her voice thins like wind, she melts into white mist and slips away through the smoke-hole, and she is never seen again. She spares him a second time (the first time because he was young, now for the children) but leaves forever. [原作最終文: Never again was she seen.] |  |  |  |  |  |
| 2 | 軽微 | withhold_until_end(結末前の示唆・結末直前の付加文が無い) | Before the last scene, do not say or hint outright that Yuki is the woman in white and do not tell the listener that Minokichi will break his promise or that Yuki will leave; do not explain the ending, add a moral, or comment on it. The original's quiet clues (her white skin, her fair children, her never growing old) may appear as plain facts without comment. |  |  |  |  |  |
| 3 | 重大 | setup と payoff | In the hut the woman in white spares young Minokichi on one condition: if he ever tells anybody, even his own mother, what he saw this night, she will know it and kill him; afterwards he keeps silent, even about the old man's death  ->  Years later he tells his wife, Yuki, the whole story; she reveals she is that woman, repeats the condition he broke, and spares him only because of the children before she melts away |  |  |  |  |  |
| 4 | 重大 | key_role keep_name=Minokichi(名前が維持され他人名が増えていない) | the young woodcutter, eighteen at the start, who is spared in the hut on the condition of silence, later marries Yuki and breaks the promise |  |  |  |  |  |
| 5 | 重大 | key_role keep_name=Yuki(名前が維持され他人名が増えていない) | the beautiful girl who joins Minokichi's family, becomes his wife and the mother of his ten children, and is revealed to be the woman in white (the same speaker as the woman in the hut) |  |  |  |  |  |
| 6 | 重大 | key_role(役割・関係で表され名前が付いていない) | the old woodcutter, Minokichi's master, who is frozen to death in the hut (no spoken lines, no name) |  |  |  |  |  |
| 7 | 重大 | key_role(役割・関係で表され名前が付いていない) | Minokichi's widowed mother, who welcomes Yuki and persuades her to stay (no spoken lines, no name) |  |  |  |  |  |
| 8 | 重大 | key_causality | A snowstorm drives the old and the young woodcutter into a hut; a woman in white kills the old man with her breath but spares the young man, because he is young, on the condition that he never tells anybody what he saw; he keeps silent. The next winter a girl called Yuki joins his household and becomes his wife, and they have ten children. Years later, by the lamp, he tells her the story of the hut and says she looks like the woman; she reveals that she was that woman, tells him he has broken the condition and that only the children save him, and melts into mist, never seen again. |  |  |  |  |  |
| 9 | 重大 | narration(人称・語り手の立場が各stageで保たれている) | A calm storyteller in the third person and the past tense (no 'I'), telling an old Japanese ghost story to a listener; the storyteller plainly says when and where each scene happens and who is speaking, keeps a quiet eerie tone, and never explains the ending. |  |  |  |  |  |

## 各stageの最終段落(機械抽出、参考。結末直前の付加文の有無はこの直前段落も確認)

### r0(段落数18、語数379)
- 最終段落: She was never seen again.
- 最終の直前段落: Her voice grew thin, like the crying of the wind. She melted into white mist, rose towards the roof beams, and slipped away through the smoke-hole.

### r1(段落数16、語数410)
- 最終段落: She was never seen again.
- 最終の直前段落: Her voice grew thin, like the crying of the wind. She melted into white mist, rose towards the roof beams, and slipped away through the smoke-hole.

### r2(段落数16、語数405)
- 最終段落: She was never seen again.
- 最終の直前段落: Her voice grew thin, like the crying of the wind. She melted into white mist, rose towards the roof beams, and slipped away through the smoke-hole.

### std_adjust(段落数16、語数399)
- 最終段落: No one ever saw Yuki after that.
- 最終の直前段落: Her voice grew weak, like the sound of crying wind. She melted into white mist and rose towards the roof beams. Then she slipped away through the smoke-hole in the roof.

