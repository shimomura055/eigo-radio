# Phase 2 集計(層1=gate前selector生出力、層2=gate別)


## coffee STD 5件全文(gate前selector生出力、rank順、[T]=topic)

| 条件 | run | 5件 | backup | gate | 費用 |
|---|---|---|---|---|---|
| C0 | 1 | [T]raw bean / push prices up / take time / right away / on a regular basis | (未記録) | PASS | 0.81 |
| C0 | 2 | pump one's fist / right away / [T]raw-bean prices / push prices up / price tag | (未記録) | PASS | 0.82 |
| C0 | 3 | pump one's fist / [T]raw bean / push prices up / roast / on a regular basis | (未記録) | PASS | 0.85 |
| C2 | 1 | [T]raw beans / push prices up / roasting / take time / on a regular basis | (未記録) | PASS | 1.08 |
| C2 | 2 | push prices up / [T]raw beans / on a regular basis / be based on / feel like | (未記録) | PASS | 0.81 |
| C2 | 3 | push prices up / [T]raw beans / on a regular basis / feel like / take time | (未記録) | PASS | 0.89 |

## coffee ADV 5件全文(gate前selector生出力、rank順、[T]=topic)

| 条件 | run | 5件 | backup | gate | 費用 |
|---|---|---|---|---|---|
| C0 | 1 | lag / show up / [T]raw beans / come down / price tag | (未記録) | PASS | 0.80 |
| C0 | 2 | [T]lag / show up / raw beans / Hold on / come down | (未記録) | PASS | 0.77 |
| C0 | 3 | lag / show up / come down / hold on / [T]raw beans | (未記録) | PASS | 0.94 |
| C1 | 1 | [T]time lag / come down / show up / pump / hold on | (未記録) | PASS | 1.26 |
| C1 | 2 | [T]time lag / show up / come down / harvest / hold on | (未記録) | PASS | 0.93 |
| C1 | 3 | [T]time lag / come down / show up / hold on / roasting | (未記録) | PASS | 0.81 |
| C2 | 1 | show up / [T]time lag / come with / come down / hold on | (未記録) | PASS | 0.94 |
| C2 | 2 | show up / [T]time lag / come down / hold on / insiders | (未記録) | PASS | 0.88 |
| C2 | 3 | show up in prices / come with costs / [T]time lag / come down / hold on | (未記録) | PASS | 0.90 |
| C2p | 1 | be behind price increases / [T]lag / come with costs / come down / hold on | (未記録) | PASS | 1.01 |
| C2p | 2 | be behind price increases / show up / [T]price measure / come down / hold on | (未記録) | PASS | 0.87 |
| C2p | 3 | (選定INVALID) | (未記録) | SELECTION_INVALID | 0.42 |
| C0'(ABC-A) | 1 | lag / show up / be behind price increases / in the ring / [T]raw beans | - | - | - |
| C0'(ABC-A) | 2 | pump one's fist / in the ring / be behind price increases / lag / [T]price measure | - | - | - |
| C0'(ABC-A) | 3 | lag / come down / pump one's fist / be behind price increases / [T]price tag | - | - | - |

## meta STD 5件全文(gate前selector生出力、rank順、[T]=topic)

| 条件 | run | 5件 | backup | gate | 費用 |
|---|---|---|---|---|---|
| C0 | 1 | behind the scenes / the other end / [T]contract workers / concierge / by mistake | (未記録) | PASS | 0.81 |
| C0 | 2 | behind the scenes / [T]contract workers / on the other end / concierge / bargain | (未記録) | PASS | 0.86 |
| C0 | 3 | behind the scenes / [T]contract workers / other end / bargain / concierge | (未記録) | CANONICALIZATION_INVALID | 1.16 |
| C2 | 1 | (選定INVALID) | (未記録) | SELECTION_INVALID | 0.48 |
| C2 | 2 | behind the scenes / bargain / inappropriate / [T]contract workers / the other end | (未記録) | PASS | 0.87 |
| C2 | 3 | behind the scenes / inappropriate / [T]contract workers / on the other end / by mistake | (未記録) | PASS | 0.82 |

## meta ADV 5件全文(gate前selector生出力、rank順、[T]=topic)

| 条件 | run | 5件 | backup | gate | 費用 |
|---|---|---|---|---|---|
| C0 | 1 | contract workers / unintentionally / [T]behind the scenes / concierge / no way | (未記録) | CANONICALIZATION_INVALID | 0.77 |
| C0 | 2 | behind the scenes / [T]contract workers / unintentionally / no way / inappropriate | (未記録) | PASS | 0.90 |
| C0 | 3 | [T]contract workers / behind the scenes / unintentionally / no way / inappropriate | (未記録) | PASS | 0.84 |
| C2 | 1 | behind the scenes / unintentionally / concierge / no way / [T]contract worker | (未記録) | PASS | 1.00 |
| C2 | 2 | (選定INVALID) | (未記録) | SELECTION_INVALID | 0.41 |
| C2 | 3 | take care of / behind the scenes / unintentionally / [T]contract workers / no way to know | (未記録) | PASS | 1.00 |

## hormuz STD 5件全文(gate前selector生出力、rank順、[T]=topic)

| 条件 | run | 5件 | backup | gate | 費用 |
|---|---|---|---|---|---|
| C0 | 1 | (選定INVALID) | (未記録) | SELECTION_INVALID | 0.44 |
| C0 | 2 | take back / give back / pull back / [T]sea blockade / Brent crude | (未記録) | REDUNDANCY_NG | 0.86 |
| C0 | 3 | take back / give back / [T]Strait / sea blockade / pull back | (未記録) | REDUNDANCY_NG | 0.93 |
| C2 | 1 | take back a plan / [T]Brent crude / give back gains / pull back / center stage | (未記録) | REDUNDANCY_NG | 1.18 |
| C2 | 2 | take back / give back gains / [T]sea blockade / pull back / center stage | (未記録) | REDUNDANCY_NG | 0.97 |
| C2 | 3 | [T]Brent crude / give back gains / take back a plan / pull back / center stage | (未記録) | REDUNDANCY_NG | 0.99 |

## hormuz ADV 5件全文(gate前selector生出力、rank順、[T]=topic)

| 条件 | run | 5件 | backup | gate | 費用 |
|---|---|---|---|---|---|
| C0 | 1 | give back / futures / [T]sea blockade / pull back / center stage | (未記録) | REDUNDANCY_NG | 0.95 |
| C0 | 2 | give back / futures / [T]sea blockade / pull back / center stage | (未記録) | REDUNDANCY_NG | 0.70 |
| C0 | 3 | [T]sea blockade / Brent crude / give back / futures / pull back | (未記録) | REDUNDANCY_NG | 0.84 |
| C2 | 1 | give back gains / [T]Brent crude / pull back / be withdrawn / center stage | (未記録) | REDUNDANCY_NG | 1.02 |
| C2 | 2 | give back gains / [T]Brent crude / futures / center stage / pull back | (未記録) | REDUNDANCY_NG | 0.85 |
| C2 | 3 | give back gains / pull back / center stage / [T]sea blockade / Brent crude | (未記録) | REDUNDANCY_NG | 0.80 |

## セル別サマリー

| セル | n | Jaccard平均 | time lag | lag単独 | pump-fist | 低優先枠(件) | 創作Imp/Topic | gate | 費用/job | 秒/job | gloss旗 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| coffee_adv_C0 | 3 | 0.778 | 0 | 3 | 0 | 0 | 0/0 | {'PASS': 3} | 0.8366 | 89.9 | 0 |
| coffee_adv_C1 | 3 | 0.667 | 3 | 0 | 0 | 0 | 0/0 | {'PASS': 3} | 1.0003 | 110.2 | 0 |
| coffee_adv_C2 | 3 | 0.508 | 3 | 0 | 0 | 0 | 0/0 | {'PASS': 3} | 0.9046 | 105.4 | 0 |
| coffee_adv_C2p | 3 | 0.429 | 0 | 1 | 0 | 1 | 0/0 | {'PASS': 2, 'SELECTION_INVALID': 1} | 0.7652 | 93.7 | 0 |
| coffee_std_C0 | 3 | 0.31 | 0 | 0 | 2 | 5 | 0/0 | {'PASS': 3} | 0.8274 | 109.0 | 0 |
| coffee_std_C2 | 3 | 0.587 | 0 | 0 | 0 | 5 | 0/0 | {'PASS': 3} | 0.926 | 122.9 | 0 |
| hormuz_adv_C0 | 3 | 0.778 | 0 | 0 | 0 | 0 | 0/0 | {'REDUNDANCY_NG': 3} | 0.833 | 98.5 | 0 |
| hormuz_adv_C2 | 3 | 0.667 | 0 | 0 | 0 | 0 | 0/0 | {'REDUNDANCY_NG': 3} | 0.8912 | 105.0 | 0 |
| hormuz_std_C0 | 3 | 0.667 | 0 | 0 | 0 | 0 | 0/0 | {'SELECTION_INVALID': 1, 'REDUNDANCY_NG': 2} | 0.7422 | 87.3 | 0 |
| hormuz_std_C2 | 3 | 0.619 | 0 | 0 | 0 | 0 | 0/0 | {'REDUNDANCY_NG': 3} | 1.0454 | 128.7 | 0 |
| meta_adv_C0 | 3 | 0.778 | 0 | 0 | 0 | 0 | 0/0 | {'CANONICALIZATION_INVALID': 1, 'PASS': 2} | 0.8371 | 93.7 | 0 |
| meta_adv_C2 | 3 | 0.25 | 0 | 0 | 0 | 0 | 0/0 | {'PASS': 2, 'SELECTION_INVALID': 1} | 0.805 | 94.3 | 0 |
| meta_std_C0 | 3 | 0.508 | 0 | 0 | 0 | 0 | 0/0 | {'PASS': 2, 'CANONICALIZATION_INVALID': 1} | 0.942 | 114.2 | 0 |
| meta_std_C2 | 3 | 0.429 | 0 | 0 | 0 | 0 | 0/0 | {'SELECTION_INVALID': 1, 'PASS': 2} | 0.7217 | 88.4 | 0 |
| coffee_adv_C0p | 3 | 0.369 | 0 | 3 | 2 | 1 | 2/0 | - | - | - | - |
| coffee_std_C0p | 3 | 0.619 | 0 | 0 | 3 | 0 | 6/0 | - | - | - | - |