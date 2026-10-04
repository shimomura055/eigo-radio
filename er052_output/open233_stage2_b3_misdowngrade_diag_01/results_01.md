# results_01.md (委任_67 B3誤降格診断)

cost_jpy_total=5.7761 calls=50 errors=0

## (a) rep25 B3 s1同一入力

- a_V7b: n=10 BLOCKING=10 非BLOCKING=0 率=0.0 dist={'BLOCKING': 10} sha一致(rep25)=True
- a_V7: n=10 BLOCKING=9 非BLOCKING=1 率=0.1 dist={'ACCEPTABLE': 1, 'BLOCKING': 9} sha一致(rep25)=False

## (a) basis逐語(非BLOCKING回)

- a_V7 run7: ACCEPTABLE basis=none hint=''

## (a) basis逐語(BLOCKING回の代表、各版先頭1件)

- a_V7b run1: BLOCKING basis=unsupported_relationship kind=narrow_scope hint='「Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage」を修正してください。安全上の懸念が計画撤回の理由だったという因果を削り、HF-007に沿って、トランプ氏が中東指導者との協議に基づく決定だと説明したことを記述してください。'
- a_V7 run1: BLOCKING basis=unsupported_relationship kind=narrow_scope hint='「Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage」を修正し、継続していた懸念が撤回の原因だったと読める因果関係を削除してください。撤回については、トランプ氏が中東指導者との協議に基づく決定だと説明した内容に沿って記述してください（HF-007）。'

## (c) Safety-critical残り+K16/K20 (V7b)

| group | sub_id | target | 期待 | n | BLOCKING | 非BLOCKING | 分布 |
|---|---|---|---|---|---|---|---|
| B4 | B4-d |  | BLOCKING | 5 | 0 | 5 | {'ACCEPTABLE': 5} |
| B4 | B4-a | * | BLOCKING | 5 | 5 | 0 | {'BLOCKING': 5} |
| B4 | B4-b |  | QUALITY | 5 | 0 | 5 | {'ACCEPTABLE': 2, 'QUALITY': 3} |
| B4 | B4-c |  | QUALITY | 5 | 0 | 5 | {'ACCEPTABLE': 3, 'QUALITY': 2} |
| A2A3 | A2A3-0 | * | BLOCKING | 5 | 5 | 0 | {'BLOCKING': 5} |
| A2A3 | A2A3-1 |  | BLOCKING | 5 | 5 | 0 | {'BLOCKING': 5} |
| A4 | A4-0 | * | BLOCKING | 5 | 5 | 0 | {'BLOCKING': 5} |
| A4 | A4-1 |  | BLOCKING | 5 | 0 | 5 | {'ACCEPTABLE': 5} |
| A4 | A4-2 |  | BLOCKING | 5 | 5 | 0 | {'BLOCKING': 5} |
| A5 | A5-0 | * | BLOCKING | 5 | 5 | 0 | {'BLOCKING': 5} |
| A5 | A5-1 |  | BLOCKING | 5 | 0 | 5 | {'ACCEPTABLE': 5} |
| E1_neg3 | e-K16 | * | BLOCKING | 5 | 5 | 0 | {'BLOCKING': 5} |
| E2_a4 | e-K20(B4-a型) | * | BLOCKING | 5 | 5 | 0 | {'BLOCKING': 5} |

## (c) 非BLOCKING回のbasis逐語(target行のみ)

