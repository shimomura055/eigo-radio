# Fable CPチェックリスト(機械生成: the_gift_of_the_magi、essentials sha 64f183e39162)

各行の『本文の該当引用』欄にstage別の本文引用(逐語)を記入する。引用できない=欠落。判定・記入はCP担当(Fable/Sonnet記入→Fable確認)。

処置規則(ユーザー承認2026-10-23): (A)重大=ending_reveal・key_roles(keep_name人物の脱落/他人名の増加)・key_causality・setups_and_payoffsのいずれかの欠落 -> CP不合格。TTS前に修正(Writer再実行=承認済みの明示--regenerate-stage、または決定論パッチ)し、原因分析を記録し、C案(軽量事後確認)要否をユーザーへ提示する(報告で`判断候補`)。(B)軽微=結末直前の付加文など、結末前の示唆(withhold_until_end)を希釈する不要文のみ -> 決定論の削除パッチ(exact文字列の削除)を適用し、削除した文・理由・前後sha・対象stageを記録する。所見を処置せずTTSへ進めてはならない。自動判定・LLM検査・retry・Human Reviewは無い。

| # | 深刻度 | 項目 | 内容 | 本文の該当引用(r0) | 本文の該当引用(r1) | 本文の該当引用(r2) | 本文の該当引用(std_adjust) | 判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | 重大 | ending_reveal(種明かしが最終に在る) | Each of the two has sold their greatest treasure to buy a gift for the other, and each gift is now useless: Della's hair is gone, so the combs are useless, and Jim's watch is sold, so the chain is useless. Yet the love behind the sacrifices makes the two foolish young people the wisest of all gift-givers, the magi, which explains the title. [原作最終文: Everywhere they are wisest. They are the magi.] |  |  |  |  |  |
| 2 | 軽微 | withhold_until_end(結末前の示唆・結末直前の付加文が無い) | Before Jim reveals it, do not hint that Jim has sold his watch, that the present in his pocket is a set of combs, or that Della's gift will turn out to be useless; do not comment on the irony before the ending. |  |  |  |  |  |
| 3 | 重大 | setup と payoff | The couple's two proud possessions are Jim's gold watch (his father's and grandfather's) and Della's long brown hair; Della sells her hair to buy Jim a platinum chain for the watch.  ->  Jim gives Della tortoise-shell combs for her hair, and then says he sold the watch to buy them, so the chain has no watch to hang on. |  |  |  |  |  |
| 4 | 重大 | key_role keep_name=Della(名前が維持され他人名が増えていない) | the young wife who sells her beautiful hair on Christmas Eve to buy a chain for her husband's watch |  |  |  |  |  |
| 5 | 重大 | key_role keep_name=Jim(名前が維持され他人名が増えていない) | Della's husband, who sells his gold watch to buy combs for her hair |  |  |  |  |  |
| 6 | 重大 | key_role(役割・関係で表され名前が付いていない) | the owner of the hair-goods shop who buys Della's hair for twenty dollars |  |  |  |  |  |
| 7 | 重大 | key_causality | Both want to give the other a Christmas present they cannot afford; each sells their one great treasure (Della her hair, Jim his watch) to buy a gift that fits the other's treasure (a chain for the watch, combs for the hair), so each gift becomes useless, but the love behind the sacrifice remains. |  |  |  |  |  |

## 各stageの最終段落(機械抽出、参考。結末直前の付加文の有無はこの直前段落も確認)

### r0(段落数27、語数416)
- 最終段落: The magi were the wise men who brought gifts to the Babe in the manger and invented the art of giving Christmas presents. These two foolish young people had given up their greatest treasures for each other. Yet, of all who give gifts, they were the wisest. They are the magi.
- 最終の直前段落: Della looked from the chain to the combs. Then she sat beside him and took his hand.

### r1(段落数25、語数432)
- 最終段落: The magi were the wise men who brought gifts on the first Christmas. Yet these two foolish young people, whose gifts they could not use, were the wisest of all gift-givers. They were the magi.
- 最終の直前段落: Della sat beside him and took his hand. The combs had no long hair to hold; the chain had no watch to carry. Neither had been able to afford a gift, so each had given up their greatest treasure.

### r2(段落数30、語数428)
- 最終段落: The magi were wise men who brought gifts on the first Christmas. Yet here, with gifts they could not use, sat two foolish young people whose love made them the wisest of all gift-givers. They were the magi.
- 最終の直前段落: Della sat beside him and took his hand. Her hair was gone; the combs could not hold it. His watch was gone; the chain had nothing to carry. Each had sold their greatest treasure to buy the other a gift.

### std_adjust(段落数30、語数443)
- 最終段落: Wise men called the magi brought gifts on the first Christmas. The two young people seemed foolish with their useless gifts. But their love made them wiser than all other gift-givers. In every place, they are the wisest; these two are the magi.
- 最終の直前段落: Della joined him and held his hand. Without her hair, she could not use the combs. Without his watch, he could not use the chain. Both had sold their greatest treasure for the other’s gift.

