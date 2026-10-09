# D0_ARTICLE_SWEEP_01(P0' D0実測、¥0)

- 対象: casebank_01.json の articles 18記事の各言語版(JA_R2 / EN_Adv_b1b / EN_Std_a2)。ラベル・既知重大文は一切参照しない。
- 規則: `d0_directional.detect`(方向語を含む文 × 方向語を含むFactの総当たり、言語をまたぐ)。rollback=和集合投入対象(gate_only=False)、全D0=gate_only(不在断定・数量・増減/許可)を含む。
- 数え方: 固有文数=Flagが立った異なる文の数 / (sent,type)=同一文の複数タイプは別件。

| 記事 | 版 | 文数 | Fact数 | rollback固有文 | rollback(sent,type) | 全D0固有文 | 全D0(sent,type) |
|---|---|---|---|---|---|---|---|
| byd_recall/new | JA_R2 | 12 | 11 | 0 | 0 | 0 | 0 |
| byd_recall/new | EN_Adv_b1b | 27 | 11 | 0 | 0 | 0 | 0 |
| byd_recall/old | JA_R2 | 8 | 11 | 0 | 0 | 1 | 1 |
| byd_recall/old | EN_Adv_b1b | 27 | 11 | 0 | 0 | 0 | 0 |
| central_bank_mortgage/old | JA_R2 | 7 | 11 | 0 | 0 | 0 | 0 |
| central_bank_mortgage/old | EN_Adv_b1b | 28 | 11 | 0 | 0 | 1 | 1 |
| central_bank_mortgage/old | EN_Std_a2 | 32 | 11 | 0 | 0 | 1 | 1 |
| hormuz/new | JA_R2 | 10 | 12 | 1 | 1 | 4 | 4 |
| hormuz/new | EN_Adv_b1b | 35 | 12 | 1 | 1 | 3 | 3 |
| hormuz/new | EN_Std_a2 | 44 | 12 | 1 | 1 | 4 | 4 |
| meta/new | JA_R2 | 12 | 15 | 0 | 0 | 0 | 0 |
| meta/new | EN_Adv_b1b | 32 | 15 | 0 | 0 | 0 | 0 |
| meta/new | EN_Std_a2 | 36 | 15 | 0 | 0 | 0 | 0 |
| openai_copyright/new | JA_R2 | 10 | 8 | 0 | 0 | 0 | 0 |
| openai_copyright/old | JA_R2 | 6 | 8 | 0 | 0 | 0 | 0 |
| openai_copyright/old | EN_Adv_b1b | 21 | 8 | 0 | 0 | 2 | 2 |
| openai_copyright/old | EN_Std_a2 | 32 | 8 | 0 | 0 | 3 | 3 |
| semiconductor_earnings/new | JA_R2 | 8 | 5 | 0 | 0 | 0 | 0 |
| semiconductor_earnings/old | JA_R2 | 6 | 5 | 0 | 0 | 0 | 0 |
| semiconductor_earnings/old | EN_Adv_b1b | 24 | 5 | 0 | 0 | 5 | 5 |
| semiconductor_earnings/old | EN_Std_a2 | 31 | 5 | 0 | 0 | 5 | 5 |
| small_bag/new | JA_R2 | 12 | 6 | 0 | 0 | 0 | 0 |
| small_bag/new | EN_Adv_b1b | 28 | 6 | 0 | 0 | 0 | 0 |
| small_bag/new | EN_Std_a2 | 39 | 6 | 0 | 0 | 0 | 0 |
| small_bag/old | JA_R2 | 6 | 6 | 0 | 0 | 0 | 0 |
| small_bag/old | EN_Adv_b1b | 19 | 6 | 0 | 0 | 0 | 0 |
| space_weapons/new | JA_R2 | 9 | 22 | 0 | 0 | 4 | 5 |
| space_weapons/new | EN_Adv_b1b | 33 | 22 | 0 | 0 | 2 | 2 |
| space_weapons/old | JA_R2 | 8 | 22 | 0 | 0 | 2 | 2 |
| space_weapons/old | EN_Adv_b1b | 35 | 22 | 0 | 0 | 3 | 3 |
| space_weapons/old | EN_Std_a2 | 45 | 22 | 0 | 0 | 4 | 4 |
| streaming_price/new | JA_R2 | 8 | 5 | 0 | 0 | 0 | 0 |
| streaming_price/new | EN_Adv_b1b | 34 | 5 | 0 | 0 | 0 | 0 |
| streaming_price/new | EN_Std_a2 | 45 | 5 | 0 | 0 | 0 | 0 |
| streaming_price/old | JA_R2 | 6 | 5 | 0 | 0 | 1 | 1 |
| streaming_price/old | EN_Adv_b1b | 21 | 5 | 0 | 0 | 1 | 1 |
| streaming_price/old | EN_Std_a2 | 30 | 5 | 0 | 0 | 1 | 1 |

## 言語版別の要約(KPI3の判定線: 合格 平均≤5 Flag/記事/言語版、不合格線 >12。上限は『人間に見せる件数』= 和集合に入れるrollback)

- JA版(n=15): rollback固有文 平均0.1 / 中央値0.0 / 最大1 / 全D0固有文 平均0.8 / 中央値0.0 / 最大4
- EN版(n=22): rollback固有文 平均0.1 / 中央値0.0 / 最大1 / 全D0固有文 平均1.6 / 中央値1.0 / 最大5
- 全版(n=37): rollback固有文 平均0.1 / 中央値0.0 / 最大1 / 全D0固有文 平均1.3 / 中央値0.0 / 最大5
- タイプ別 固有文数の合計(全37版): rollback反転=3, その他=20, 不在断定=7, 数量時系列=18
