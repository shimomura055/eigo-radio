# canon_compare_03 (委任_03、Opus推奨の少額比較run)

model: gpt-5.6-sol(canonicalizationのみ再実行、選定は記録済みitemを再利用、3記事。LLM費用 各約JPY1。ただし初回実行でスクリプト不具合により2記事分の呼出が結果保存前に失われ再実行したため、比較runの合計は約JPY5-6の見込み、実測は報告参照)。
「候補外へ延長」= KPが元候補span/display_phraseに無い語をA'窓の右拡張部分から取り込んだ(`kp_extends_beyond_candidate`と同定義)。活用形正規化(gave->give)は含まない。旧記録は旧入力(窓なし)のため同定義で窓を仮に当てて判定。

## hormuz_b1b  status=CANONICALIZATION_PASS

| rank | display_phrase | 候補span | A'窓 | 旧記録KP | 今回KP | 変更(旧/今回) | 候補外へ延長(旧/今回) |
|---|---|---|---|---|---|---|---|
| 1 | give back | gave back | gave back some of their | give back | give back | False/False | False/False |
| 2 | sea blockade | sea blockade | sea blockade of Iran | sea blockade | sea blockade | False/False | False/False |
| 3 | the Strait | Strait | Strait of Hormuz | Strait | Strait of Hormuz | True/True | False/True |
| 4 | center stage | center stage | - | center stage | center stage | False/False | False/False |
| 5 | pass through | passing through | passing through the Strait of | pass through | pass through | False/False | False/False |

## meta_b1b  status=CANONICALIZATION_PASS

| rank | display_phrase | 候補span | A'窓 | 旧記録KP | 今回KP | 変更(旧/今回) | 候補外へ延長(旧/今回) |
|---|---|---|---|---|---|---|---|
| 1 | contract workers | contract workers | - | contract workers | contract workers | False/False | False/False |
| 2 | turn out | turned out | turned out not to be | turn out | turn out | False/False | False/False |
| 3 | be rolled back | rolled back | rolled back for now | be rolled back | be rolled back | False/False | False/False |
| 4 | concierge | concierge | concierge feature has been rolled | concierge | concierge | False/False | False/False |
| 5 | take over | take over | take over is not necessarily | take over | take over | False/False | False/False |

## hormuz_a2  status=CANONICALIZATION_PASS

| rank | display_phrase | 候補span | A'窓 | 旧記録KP | 今回KP | 変更(旧/今回) | 候補外へ延長(旧/今回) |
|---|---|---|---|---|---|---|---|
| 1 | be taken back | Taken Back | - | be taken back | be taken back | False/False | False/False |
| 2 | give back | gave back | gave back some gains | give back | give back | False/False | False/False |
| 3 | Brent crude | Brent crude | Brent crude futures briefly gave | Brent crude | Brent crude | False/False | False/False |
| 4 | sea blockade | sea blockade | sea blockade of Iran | sea blockade | sea blockade | False/False | False/False |
| 5 | center stage | center stage | - | center stage | center stage | False/False | False/False |

## 集計
- display_phraseから変更された率: 旧記録 1/15 -> 今回(A') 1/15
- 候補外(窓の右拡張部分)へ伸びたKP: 旧記録 0/15 -> 今回(A') 1/15

