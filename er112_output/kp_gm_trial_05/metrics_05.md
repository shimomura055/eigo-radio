# Trial_05 決定論的集計(API 0、OF-KP1-05)

| arm | n出力 | callあたり円(平均) | reasoning_tokens平均/call | output_tokens平均/call | validate互換 valid/検査 | gloss==naive_ja | 文字数比>1.5(対B0平均) | 説明文型語尾 | 30字超 | conveys yes/partly/no |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 31 | 0.0585 | 304 | 447 | 31/31 | - | - | 1 | 0 | - |
| M | 7 | 0.0524 | 336 | 388 | 0/0 | - | 3/7 | 0 | 0 | - |
| X1 | 21 | 0.0654 | 528 | 679 | 21/21 | - | 11/21 | 3 | 0 | - |
| X2 | 31 | 0.1254 | 1074 | 1282 | 31/31 | 0/31 | 15/31 | 3 | 0 | 8/1/22 |
| Cp | 30 | 0.1566 | 1340 | 1551 | 30/30 | - | 5/26 | 1 | 0 | - |
| X2p | 85 | 0.1593 | 1394 | 1621 | 85/85 | 0/85 | 14/31 | 3 | 0 | 11/12/62 |

validate不合格の出力: 0件 []

## OF-KP1-03 reasoning_tokens(B0 vs Cp、新規実行で計測。Trial_04の既存ledgerのluna gen行には未記録のため過去分は比較不可)
- B0: 22 call、reasoning_tokens平均=304、output_tokens平均=447、1call平均費用=0.0585円
- M: 4 call、reasoning_tokens平均=336、output_tokens平均=388、1call平均費用=0.0524円
- X1: 12 call、reasoning_tokens平均=528、output_tokens平均=679、1call平均費用=0.0654円
- X2: 22 call、reasoning_tokens平均=1074、output_tokens平均=1282、1call平均費用=0.1254円
- Cp: 24 call、reasoning_tokens平均=1340、output_tokens平均=1551、1call平均費用=0.1566円
- X2p: 54 call、reasoning_tokens平均=1343、output_tokens平均=1561、1call平均費用=0.1593円
