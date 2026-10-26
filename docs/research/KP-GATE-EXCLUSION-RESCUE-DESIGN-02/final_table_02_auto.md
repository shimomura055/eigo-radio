# FINAL_TABLE (自動生成。決定論の判定 + LLM評価[複数回多数決]の重ね合わせ)

| # | era | Family/lv | 元候補 | 除外クラス | 修正後(display→key) | 既存Gate再検証 | LLM評価(採用可/回数) | 区分 |
|---|---|---|---|---|---|---|---|---|
| 0 | HR | X/a2 | `too soon to wave a flag` | WORDCOUNT_OVER5 | too soon→too soon | validator=True CMU=True sel=True dup=0 flags=- | 3/3(strict 2, reject 0) | 区分2(救済フロー本体の採否[後処理工程の新設]。受理面は不変) |
| 1 | HR | X/a2 | `studied separately` | RULE7_NORMALIZATION | studied separately→study separately | validator=True CMU=True sel=True dup=0 flags=aux,quant,adverb,past | 3/3(strict 3, reject 0) | 区分1 |
| 2 | HR | X/a2 | `put in place` | HUMAN_NG_EXCLUDED | - | - | - | 区分3 |
| 3 | HR | X/b1b | `off the hook` | HUMAN_NG_EXCLUDED | - | - | - | 区分3 |
| 4 | HR | X/b1b | `had our eye on` | FINITE_AUX_TOKEN | had our eye on→have our eye on | validator=True CMU=True sel=True dup=0 flags=aux,quant,adverb,past | 3/3(strict 3, reject 0) | 区分1 |
| 5 | HR | Z/b1b | `rose above` | RULE7_NORMALIZATION | rose above→rise above | validator=True CMU=True sel=True dup=0 flags=- | 2/3(strict 2, reject 0) | 区分2(救済フロー本体の採否。受理面は不変=LLM提案語∩display窓) |
| 6 | HR | Z/b1b | `held out` | RULE7_NORMALIZATION | held out→hold out | validator=True CMU=True sel=True dup=0 flags=- | 3/3(strict 2, reject 0) | 区分2(救済フロー本体の採否。受理面は不変=LLM提案語∩display窓) |
| 7 | HR | Z/b1b | `sentenced him to death` | HUMAN_NG_EXCLUDED | - | - | - | 区分3 |
| 8 | HR | Z/b1b | `rang through` | RULE7_NORMALIZATION | rang through→ring through | validator=True CMU=True sel=True dup=0 flags=aux,quant,adverb,past | 3/3(strict 3, reject 0) | 区分1 |
| 9 | HR | Y/a2 | `it can’t be helped` | FINITE_AUX_TOKEN | can’t be helped→can’t be helped | validator=True CMU=True sel=True dup=0 flags=aux,quant,adverb,past,idiom | 3/3(strict 3, reject 0) | 区分2 |
| 10 | HR | Y/a2 | `redelivery fee` | CMU_UNREGISTERED | - | - | - | 区分2(CMU規則の受理面拡大: 非推奨) |
| 11 | HR | Y/b1b | `can’t be helped` | FINITE_AUX_TOKEN | can’t be helped→can’t be helped | validator=True CMU=True sel=True dup=0 flags=aux,quant,adverb,past,idiom | 3/3(strict 3, reject 0) | 区分2 |
| 12 | HR | Y/b1b | `have a say` | FINITE_AUX_TOKEN | have a say→have a say | validator=True CMU=True sel=True dup=0 flags=aux,quant,adverb,past | 3/3(strict 3, reject 0) | 区分1 |
| 13 | HR | Y/b1b | `catch their interest` | NOT_CONTIGUOUS_IN_TEXT | catches their interest→catch their interest | validator=True CMU=True sel=True dup=0 flags=- | 3/3(strict 3, reject 0) | 区分2(救済フロー本体の採否。受理面は不変=本文逐語のspanに戻す) |
| 14 | pr | X/a2 | `minaudières` | CMU_UNREGISTERED | - | - | - | 区分3 |
| 16 | pr | X/a2 | `novelty minaudière` | CMU_UNREGISTERED | - | - | - | 区分3 |
| 17 | pr | X/a2 | `minaudière` | CMU_UNREGISTERED | - | - | - | 区分3 |
| 19 | pr | X/a2 | `have a big moment` | FINITE_AUX_TOKEN | having a big moment→have a big moment | validator=True CMU=True sel=True dup=0 flags=aux,quant,adverb,past | 3/3(strict 2, reject 0) | 区分1 |
| 23 | pr | Z/b1b | `were mocking me` | FINITE_AUX_TOKEN | mocking me→mocking me | validator=True CMU=True sel=True dup=0 flags=- | - | 区分2(救済フロー: 助動詞を外した連続部分列) |
| 24 | pr | Z/a2 | `offered his hands for the chains` | WORDCOUNT_OVER5 | offered his hands→offered his hands | validator=True CMU=True sel=True dup=0 flags=- | 3/3(strict 1, reject 0) | 区分2(救済フロー本体の採否[後処理工程の新設]。受理面は不変) |
| 25 | pr | Z/a2 | `lose my trust in you` | NOT_CONTIGUOUS_IN_TEXT | lost my trust in you→lose my trust in you | validator=True CMU=True sel=True dup=0 flags=- | 3/3(strict 3, reject 0) | 区分2(救済フロー本体の採否。受理面は不変=本文逐語のspanに戻す) |
| 26 | pr | Z/a2 | `in his place` | NOT_CONTIGUOUS_IN_TEXT | - | - | - | 区分3 |
| 27 | pr | Z/b1b | `Could you have borne it` | FINITE_AUX_TOKEN | - | - | - | 区分3 |
| 28 | pr | Z/b1b | `could have borne it` | FINITE_AUX_TOKEN | - | - | - | 区分3 |
| 29 | pr | Z/a2 | `Could you bear that?` | FINITE_AUX_TOKEN | bear→bear | validator=True CMU=True sel=True dup=0 flags=- | - | 区分2(救済フロー: 助動詞を外した連続部分列) |
| 44 | pr | Z/a2 | `could not bear` | FINITE_AUX_TOKEN | - | - | - | 区分3 |
| 45 | pr | Z/a2 | `could not bear another second` | FINITE_AUX_TOKEN | - | - | - | 区分3 |
| 58 | pr | Z/b1b | `my ears began to ring` | RULE7_NORMALIZATION | my ears began to ring→one's ears began to ring | validator=True CMU=True sel=True dup=0 flags=- | 3/3(strict 3, reject 0) | 区分2(救済フロー本体の採否。受理面は不変=LLM提案語∩display窓) |
| 59 | pr | Z/a2 | `lost touch` | RULE7_NORMALIZATION | lost touch→lose touch | validator=True CMU=True sel=True dup=0 flags=aux,quant,adverb,past,idiom,lexguard | 3/3(strict 3, reject 0) | 区分2(辞書裏付けguard等の受理面拡大) |
| 60 | pr | Z/b1b | `couldn't bring myself to arrest` | RULE7_NORMALIZATION | couldn't bring myself to arrest→couldn't bring oneself to arrest | validator=True CMU=True sel=True dup=0 flags=- | - | (除外ではなくなった) |
| 62 | pr | Z/b1b | `couldn't bring myself to` | RULE7_NORMALIZATION | couldn't bring myself to→couldn't bring oneself to | validator=True CMU=True sel=True dup=0 flags=- | - | (除外ではなくなった) |
| 63 | pr | Z/b1b | `struck a match` | RULE7_NORMALIZATION | struck a match→strike a match | validator=True CMU=True sel=True dup=0 flags=aux,quant,adverb,past | 3/3(strict 3, reject 0) | 区分1 |
| 64 | pr | Z/b1b | `sentenced him to death` | RULE7_NORMALIZATION | sentenced him to death→sentence someone to death | validator=True CMU=True sel=True dup=0 flags=- | - | (除外ではなくなった) |
| 65 | pr | Z/b1b | `nearly abandoned you` | RULE7_NORMALIZATION | nearly abandoned you→nearly abandoned someone | validator=True CMU=True sel=True dup=0 flags=- | 3/3(strict 3, reject 0) | 区分2(救済フロー本体の採否。受理面は不変=LLM提案語∩display窓) |
| 66 | pr | Z/a2 | `pulling free` | RULE7_NORMALIZATION | pulling free→pulling free | validator=True CMU=True sel=True dup=0 flags=- | 3/3(strict 3, reject 0) | 区分2(救済フロー本体の採否。受理面は不変=LLM提案語∩display窓) |
| 67 | pr | Z/b1b | `accepts no responsibility` | RULE7_NORMALIZATION | accepts no responsibility→accept no responsibility | validator=True CMU=True sel=True dup=0 flags=aux,quant,adverb,past | 3/3(strict 3, reject 0) | 区分1 |
| 69 | pr | Z/a2 | `growing louder and louder` | RULE7_NORMALIZATION | growing louder and louder→growing louder and louder | validator=True CMU=True sel=True dup=0 flags=- | 3/3(strict 3, reject 0) | 区分2(救済フロー本体の採否。受理面は不変=LLM提案語∩display窓) |
| 70 | pr | Z/b1b | `my blood went cold` | RULE7_NORMALIZATION | my blood went cold→one's blood went cold | validator=True CMU=True sel=True dup=0 flags=- | 3/3(strict 3, reject 0) | 区分2(救済フロー本体の採否。受理面は不変=LLM提案語∩display窓) |
| 76 | pr | Z/a2 | `froze my blood` | RULE7_NORMALIZATION | froze my blood→freeze my blood | validator=True CMU=True sel=True dup=0 flags=aux,quant,adverb,past | 3/3(strict 3, reject 0) | 区分1(+救済フロー) |
| 77 | pr | Z/b1b | `eased open` | RULE7_NORMALIZATION | eased open→eased open | validator=True CMU=True sel=True dup=0 flags=- | 3/3(strict 0, reject 0) | 区分2(救済フロー本体の採否。受理面は不変=LLM提案語∩display窓) |
| 80 | pr | Z/a2 | `sure of myself` | RULE7_NORMALIZATION | sure of myself→sure of oneself | validator=True CMU=True sel=True dup=0 flags=- | - | (除外ではなくなった) |
| 81 | pr | Z/a2 | `My ears began ringing` | RULE7_NORMALIZATION | My ears began ringing→one's ears began ringing | validator=True CMU=True sel=True dup=0 flags=- | 3/3(strict 3, reject 0) | 区分2(救済フロー本体の採否。受理面は不変=LLM提案語∩display窓) |
| 83 | pr | Z/? | `leaving no mark` | RULE7_NORMALIZATION | leaving no mark→leave no mark | validator=True CMU=True sel=True dup=0 flags=aux,quant,adverb,past | 3/3(strict 3, reject 0) | 区分1 |
