# Fable CPチェックリスト(機械生成: the_monkeys_paw、essentials sha 2b5ce66008dc)

各行の『本文の該当引用』欄にstage別の本文引用(逐語)を記入する。引用できない=欠落。判定・記入はCP担当(Fable/Sonnet記入→Fable確認)。

処置規則(ユーザー承認2026-10-23): (A)重大=ending_reveal・key_roles(keep_name人物の脱落/他人名の増加)・key_causality・setups_and_payoffsのいずれかの欠落 -> CP不合格。TTS前に修正(Writer再実行=承認済みの明示--regenerate-stage、または決定論パッチ)し、原因分析を記録し、C案(軽量事後確認)要否をユーザーへ提示する(報告で`判断候補`)。(B)軽微=結末直前の付加文など、結末前の示唆(withhold_until_end)を希釈する不要文のみ -> 決定論の削除パッチ(exact文字列の削除)を適用し、削除した文・理由・前後sha・対象stageを記録する。所見を処置せずTTSへ進めてはならない。自動判定・LLM検査・retry・Human Reviewは無い。

| # | 深刻度 | 項目 | 内容 | 本文の該当引用(r0) | 本文の該当引用(r1) | 本文の該当引用(r2) | 本文の該当引用(std_adjust) | 判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | 重大 | ending_reveal(種明かしが最終に在る) | The husband makes the third and last wish just as his wife is about to open the front door, the terrible knocking stops, and when the door is opened there is nobody there: only the cold wind, the wife's wail of loss, and the street lamp shining on a quiet, deserted road. The story never says what the third wish was or what was outside; the reader is left to understand, and the chill comes from that silence. [原作最終文: The street lamp flickering opposite shone on a quiet and deserted road.] |  |  |  |  |  |
| 2 | 軽微 | withhold_until_end(結末前の示唆・結末直前の付加文が無い) | Before the man from the firm speaks, do not hint that Herbert will be hurt or killed or that the two hundred pounds comes as compensation for his death; never state what the third wish was or what stood outside the door; do not explain the ending or comment on it. |  |  |  |  |  |
| 3 | 重大 | key_role keep_name=Mr. White(名前が維持され他人名が増えていない) | the father and head of the family, who takes the monkey's paw and makes all three wishes |  |  |  |  |  |
| 4 | 重大 | key_role keep_name=Mrs. White(名前が維持され他人名が増えていない) | Herbert's mother, who demands the second wish to bring her son back and runs to open the door |  |  |  |  |  |
| 5 | 重大 | key_role keep_name=Herbert(名前が維持され他人名が増えていない) | the Whites' grown son, who jokes about the paw and suggests the wish for two hundred pounds, then dies in an accident at work |  |  |  |  |  |
| 6 | 重大 | key_role(役割・関係で表され名前が付いていない) | the old friend, a retired sergeant-major who brings the paw from India and warns them not to use it |  |  |  |  |  |
| 7 | 重大 | key_role(役割・関係で表され名前が付いていない) | the stranger from the firm who brings the news of Herbert's death and the two hundred pounds |  |  |  |  |  |
| 8 | 重大 | key_causality | The old sergeant-major brings a monkey's paw that grants three wishes and warns the Whites that it brings sorrow to those who interfere with fate; Mr. White, joking with his family, wishes for two hundred pounds, the paw twists in his hand, and the next day the money arrives as compensation for Herbert's death at work; grief drives Mrs. White to demand a second wish to bring Herbert back, Mr. White is afraid of what would return, and after that wish a knock sounds at the door in the night; Mrs. White runs to open it while her husband makes the third and last wish, and the knocking stops. |  |  |  |  |  |

## 各stageの最終段落(機械抽出、参考。結末直前の付加文の有無はこの直前段落も確認)

### r0(段落数48、語数449)
- 最終段落: The street lamp opposite shone on a quiet, deserted road.
- 最終の直前段落: The door opened. Cold wind entered, and Mrs. White gave a long cry of loss.

### r1(段落数38、語数411)
- 最終段落: The street lamp opposite shone on a quiet, deserted road.
- 最終の直前段落: She pulled the door open. Cold wind swept into the house, and her long wail of loss rose into the night.

### r2(段落数32、語数430)
- 最終段落: The street lamp opposite shone on a quiet, deserted road.
- 最終の直前段落: She pulled the door open. There was nobody there. Cold wind swept into the house, and her long wail of loss rose into the night.

### std_adjust(段落数32、語数439)
- 最終段落: Across the street, the lamp shone on an empty, silent road.
- 最終の直前段落: She opened the door, but no one stood outside. Cold wind blew in as her long cry of loss rose into the night.

