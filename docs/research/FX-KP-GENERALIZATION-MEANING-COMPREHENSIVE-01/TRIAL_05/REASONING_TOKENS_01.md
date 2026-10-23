# REASONING_TOKENS_01 (OF-KP1-03: B0対Cpの reasoning_tokens 比較。委任_22)

## 既存ledgerでの確認(API 0)
`er112_output/kp_gm_trial_04/paid_calls.jsonl`(389行)のluna生成行(`kind=gen`)の`usage`は`input_tokens`/`output_tokens`/`cached_input_tokens`のみで、**`reasoning_tokens`は未記録**(`er112_kp_gm_trial_02.cost_of`→`kx._usage_dict`が出力tokenの内訳を落とす)。`reasoning_tokens`が入っているのは Sonnet参考Judge行のみ(trial_01/02/03/04のjudge行)。よってOPUS_REVIEW_07が想定した「0円の既存データでのCp対B0比較」は**不可能**だった。間接証拠として、Trial_04の`output_tokens`平均は B0 518 / M 324 / Cp 1,717(Cpが約3.3倍)=可視の追加欄は1項目あたり数十〜百token程度なので、増分の大半は非可視(推論)tokenと推定される(未検証の推定)。

## 新規実行での実測(本Trial_05の台帳に`reasoning_tokens`を記録、追加費用0)
effort=high、luna。R(4記事グループ)の1callあたり平均(`paid_calls.jsonl`):

| arm | call数 | output_tokens | reasoning_tokens | 可視出力(output-reasoning)概算 | 1call円 |
|---|---|---|---|---|---|
| B0(現行) | 12 | 539 | 361 | 178 | 0.0573 |
| M | 4 | 387 | 335 | 52 | 0.0524 |
| X1(制約句置換のみ、Production互換欄) | 12 | 678 | 527 | 151 | 0.0654 |
| X2(gloss前に3欄) | 12 | 1,454 | 1,206 | 248 | 0.1306 |
| Cp(gloss後に4欄) | 5 | 2,599 | 2,308 | 291 | 0.2424 |

held-out(1KP/call中心): B0 reasoning 234 / X2 915(いずれも出力は短い単KP call)。

## 所見(事実と解釈を分ける)
- **事実**: Cpの欄は`japanese_gloss`の**後**に置かれているが、Cpのreasoning_tokens(平均2,308)はB0(361)の約6.4倍。可視出力の増加は約113 token、reasoningの増加は約1,950 tokenで、**増分の約95%は非可視の推論**。X2はreasoningがB0の約3.3倍(1,206)。X1(欄追加なし、制約句置換+Production互換欄)は約1.5倍(527)。
- **解釈(Opus所見との整合)**: 「gloss後の欄は出力に影響しない」という前提は成り立たない。欄の存在(特に全欄を埋める必要があること)が、effort=highの隠れた推論を大きく増やしている。Cpの効果(hard-core 0/4、F層FAIL 0/41)の機序は「欄が熟考を誘発した」ことと整合する(**因果の直接証明ではない**。Cpは入力tokenも異なる、呼出数が少ない)。
- **含意**: (1)案Aのgloss前の可視欄(`meaning_in_text_en`等)は、Cpと同様に推論を誘発する一方で、推論量はCpの約半分(1,206 vs 2,308)で費用は約半分(0.131 vs 0.242円)。「Cpの効果を保ちつつ安い」かは Fable盲検の品質比較で決まる(OF-KP1-03判定: X2がCpと同等以上でより安い→案A、劣る→案C最適化版)。(2)Cpの費用はTrial_04平均(0.179円)より高い0.242円(5call、変動0.098〜0.359円)。
- **限界**: Cpはrep1の4call+rep2の1callのみ(HALTにより停止)、X2/B0と記事グループの混ざり方が同一でない(Cpはrep1の4グループ全部+rep2のdraw a lineグループのみ)。少数callの平均であり、分散(同一グループでも0.098〜0.283円)が大きい。
