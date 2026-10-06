# trigger_replay_01 (JPY0、保存データ決定論集計。考察なし)

注記: 非BLOCKING=llm_materiality!=BLOCKING(後段AI判定)。final(materiality)基準は参考列

注記: T-B=sub_reasonsが全て決定論種別(model無し)=Stage1 AIはSUPPORTED判定と同値の近似

注記: 語彙は検出用近似で設計の正本ではない。Ledger fact本文は保存jsonに無く、claim_textのみに適用


## (1a) 新9 run

| run | cycles | stage2件数 | T-A | T-B | T-C |
|---|---|---|---|---|---|
| bgroup_B3 | 3 | 15 | 9 | 9 | 8 |
| hormuz_run03_advanced | 1 | 11 | 1 | 1 | 6 |
| hormuz_run03_standard | 1 | 15 | 7 | 7 | 5 |
| meta_run03_advanced | 1 | 8 | 1 | 1 | 4 |
| meta_run03_standard | 2 | 20 | 7 | 7 | 9 |
| neg1_meta_b3prod_a2 | 1 | 16 | 5 | 5 | 4 |
| neg2_meta_refresh_a2 | 2 | 14 | 4 | 4 | 4 |
| neg3_hormuz_prodrunner_b1b | 4 | 19 | 7 | 7 | 12 |
| neg7_meta_prodrunner_b1b | 1 | 5 | 2 | 2 | 3 |
| 合計 | 16 | 123 | 43 | 43 | 55 |
| 件/run |  |  | 4.78 | 4.78 | 6.11 |
| 件/cycle |  |  | 2.69 | 2.69 | 3.44 |
| 参考:final非BLOCKING基準 |  |  | 43 | 43 | 55 |


## (1b) 旧9 run

| run | cycles | stage2件数 | T-A | T-B | T-C |
|---|---|---|---|---|---|
| bgroup_B3 | 3 | 24 | 10 | 10 | 8 |
| hormuz_run03_advanced | 3 | 28 | 2 | 2 | 13 |
| hormuz_run03_standard | 1 | 15 | 6 | 6 | 6 |
| meta_run03_advanced | 3 | 33 | 2 | 2 | 10 |
| meta_run03_standard | 3 | 47 | 7 | 7 | 18 |
| neg1_meta_b3prod_a2 | 4 | 82 | 13 | 13 | 15 |
| neg2_meta_refresh_a2 | 3 | 33 | 1 | 1 | 8 |
| neg3_hormuz_prodrunner_b1b | 3 | 27 | 6 | 6 | 14 |
| neg7_meta_prodrunner_b1b | 2 | 37 | 5 | 5 | 13 |
| 合計 | 25 | 326 | 52 | 52 | 105 |
| 件/run |  |  | 5.78 | 5.78 | 11.67 |
| 件/cycle |  |  | 2.08 | 2.08 | 4.2 |
| 参考:final非BLOCKING基準 |  |  | 52 | 52 | 93 |


## (1c) 段階A(Stage 1のみ、候補中の該当件数)

| run数 | 候補数 | T-C語彙該当 | 決定論由来候補 |
|---|---|---|---|
| 42 | 658 | 183 | 155 |


## (2) 新9 runラベル済み(結合123/123)の内訳

| 案 | trigger計 | 真に重大Y | 軽微 | 問題なし | UNDECIDABLE | その他 |
|---|---|---|---|---|---|---|
| T-A | 43 | 1 | 0 | 42 | 0 | 0 |
| T-B | 43 | 1 | 0 | 42 | 0 | 0 |
| T-C | 55 | 1 | 3 | 51 | 0 | 0 |


## (3) HC-012 (meta_run03_advanced cycle1)

| 案 | triggered | llm | final | sub_reasons |
|---|---|---|---|---|
| T-A | True | ACCEPTABLE | ACCEPTABLE | ['negation_polarity_mismatch'] |
| T-B | True | ACCEPTABLE | ACCEPTABLE | ['negation_polarity_mismatch'] |
| T-C | True | ACCEPTABLE | ACCEPTABLE | ['negation_polarity_mismatch'] |


## (4a) 新9 run 重大4件

| run | fact | sub_reasons | llm | final | T-A | T-B | T-C |
|---|---|---|---|---|---|---|---|
| bgroup_B3 | HF-007 | ['model'] | BLOCKING | BLOCKING | False | False | False |
| meta_run03_advanced | MUSE-HC-012 | ['negation_polarity_mismatch'] | ACCEPTABLE | ACCEPTABLE | True | True | True |
| meta_run03_standard | MUSE-HC-011 | ['model'] | BLOCKING | BLOCKING | False | False | False |
| neg3_hormuz_prodrunner_b1b | HF-009 | ['model'] | BLOCKING | BLOCKING | False | False | False |


## (4b)(5) 旧35件(結合35)のラベル別trigger件数

| 旧ラベル | n | T-A | T-B | T-C |
|---|---|---|---|---|
| 正当 | 6 | 0 | 0 | 0 |
| 不要 | 24 | 0 | 0 | 8 |
| 判断不能 | 5 | 0 | 0 | 3 |


## (4c) 段階A SC gold 6件

| sub_id | instance | run数 | 一致候補 | T-C語彙該当 | 決定論候補 | 例 |
|---|---|---|---|---|---|---|
| B3 | bgroup_B3 | 3 | 3 | 3 | 0 | Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the fla |
| A2A3-0 | safety_A2A3 | 3 | 3 | 0 | 0 | The idea was that those carrying the cargo would repay the money the United States spends to keep th |
| A4-0 | safety_A4 | 3 | 3 | 0 | 2 | Through Muse, trained human contract workers made some calls and completed the exchanges with users. |
| A5-0 | safety_A5 | 3 | 3 | 3 | 0 | They also temporarily put back the feature in which humans handled the calls. |
| B4-a | bgroup_B4 | 3 | 3 | 0 | 0 | A person can take over when AI alone has trouble. |
| B3-same@neg5 | neg5_hormuz_div_a2 | 3 | 3 | 0 | 0 | So the flashy 20% plan left the stage. |
