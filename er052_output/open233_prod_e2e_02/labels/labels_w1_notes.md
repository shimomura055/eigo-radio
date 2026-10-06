# labels_w1 notes(委任_06-W1、事後評価・Sonnet推測、Fable/ユーザー確認前)

label_source=sonnet_w1_2026-10-06 / confirmed_by=空欄。担当51 claim(hormuz_run03_standard 15、meta_run03_standard 20[cycle1=12/cycle2=8]、neg1_meta_b3prod_a2 16)。
Ledger出典: runner.build_target_instances()のfixture ledger_text(meta_standardとneg1は同一Ledger)。判定列は見ずに判定。
rewrite_needed: label_sheetに該当列の値が無い(空/UNLABELED)ため全件N_A。meta_standardはcycle2で消えた文(cycle1の23/24/26相当)がRewrite対象の可能性があるが、対象特定はFableが集計側で行う(下記true_problemを根拠に使用可)。

## run別集計
| run | claim | 問題なし | 軽微 | 重大 | UNDECIDABLE | true_problem Y/N/UND | true_critical Y/UND |
|---|---|---|---|---|---|---|---|
| hormuz_run03_standard | 15 | 14 | 1 | 0 | 0 | 1/14/0 | 0/0 |
| meta_run03_standard | 20 | 16 | 3 | 1 | 0 | 4/16/0 | 1/0 |
| neg1_meta_b3prod_a2 | 16 | 14 | 1 | 0 | 1 | 1/14/1 | 0/1 |
| 計 | 51 | 44 | 5 | 1 | 1 | 6/44/1 | 1/1 |

## 重大Y・UNDECIDABLE全件(逐語)
1. meta_run03_standard cycle1 / MUSE-HC-011 / 重大 true_critical=Y
   - claim_text: "It said human staff made inappropriate comments about race during calls."
   - Ledger HC-011: 「Museにインターネット・ケーブル料金の交渉を依頼した従業員は、電話の記録に人間の契約スタッフによる人種に関する不適切な発言があったと報告した。」scope: 1件として報道された事例 / numeric_value: 1件の従業員報告 / notes: 「従業員の報告として記録する。契約スタッフ全体の行動や実験全体の性質へ一般化しない。」
   - 理由: 見本B(同一文でY/Y/重大)に倣う。報告元(従業員)・単発事例の限定が落ち、一般化と読める。ただし文頭の『It』の指示対象が不明で、報告元が保持されている可能性もある(【推測】Fable確認推奨)。
2. neg1_meta_b3prod_a2 cycle1 / MUSE-HC-008 / UNDECIDABLE
   - claim_text: "A human can handle situations that AI alone finds difficult."
   - Ledger HC-008: 「人間が電話を担当した一部テストで成功率95〜98%の可能性が示された。AIだけの場合はそれより低いとされたが具体的数値なし」 conditions: 成功率の定義・サンプル数・比較対象・測定方法は非公開 / notes: 「『人間の方が95〜98%で成功した』と一般化しない」
   - 理由: 一般論か、HC-008の一般化(範囲拡張)かが曖昧。見本Cと同型。

## 軽微(Y/N)4件(参考)
- hormuz row10 "Oil prices moved briefly, then returned to a high level." Brent先物→oil pricesの一般化(許容候補)。
- meta cycle1/2 "They enjoyed AI's convenience, but a human was on the other end." ユーザー体験の断定(Ledger未記載)。cycle2同文。
- meta cycle1 "These calls were about trying to lower internet or cable fees." HC-011の1件を複数形に。
- neg1 "AI had not learned to speak like a human." AI能力・理由の断定(Ledger未記載)。

## 境界例の所感(【推測】)
- "In other words, no one had actually started collecting the fee."(hormuz)、"They did not realize it."(meta)、"A call ... exactly this surprise"(neg1)は、Ledger未記載の推論だが4観点mismatchなしとしてN。軽微とする見方もあり得る。
- "AI had not learned to speak like a human."は理由・仕組みの断定側に寄るため重大とする見方もあり得る(軽微と判定)。
- meta cycle1の"That was a mistake."は直前の人種発言2文の後にあり、指示対象が人種発言と読める恐れ(claim単体はN)。cycle2は直前が"That was a mistake"の前文脈が変わり解消。
- hormuz "oil prices"系(見出し・row6/8)は一般化だが具体的な値動きの主張ではないためN、row10のみ軽微とした。基準の揺れの可能性あり。
