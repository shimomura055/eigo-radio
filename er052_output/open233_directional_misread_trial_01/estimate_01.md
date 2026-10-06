# estimate_01(委任_02、¥0、API不使用)

前提: 入力tokは文字種近似(非ASCII 0.8tok/字+ASCII 1/4tok)、単価はgpt-6-luna逆算(入力¥10.7/1M・出力¥81.7/1M)。effort=medium想定の出力(推論込み)tok/call: low300/mid650/high1500。5.6-luna(出典DECISION_LOG_HISTORY.md:5893 入力$0.2/出力$1.2)=単価2.0倍/2.4倍、5.6-sol($5/$30)=50倍/60倍で換算。

## call構成
- same_blind: Ledger/両側call 30件(平均入力約204tok)、記事側call 75件(平均入力約123tok)
- same_nonblind: Ledger/両側call 75件(平均入力約278tok)、記事側call 0件(平均入力約0tok)
- split_blind: Ledger/両側call 30件(平均入力約204tok)、記事側call 75件(平均入力約123tok)

## 費用(円)

| 構成 | low | mid | high |
|---|---|---|---|
| same_blind | 2.74 | 5.74 | 13.03 |
| same_nonblind | 2.06 | 4.21 | 9.41 |
| split_ledger_gpt-5.6-luna | 1.90 | 3.95 | 8.95 |
| split_ledger_gpt-5.6-sol | 47.40 | 98.87 | 223.87 |
| split_ledger_5calls_x1_gpt-5.6-sol | 7.91 | 16.49 | 37.32 |

## 合計

| 案 | low | mid | high |
|---|---|---|---|
| 3構成(split=gpt-5.6-luna, Ledger 30call) | 6.70 | 13.90 | 31.40 |
| 3構成(split=gpt-5.6-sol, Ledger 30call) | 52.20 | 108.82 | 246.32 |

判定: mid=13.90円(5.6-luna案) / 108.82円(sol案、予算超過なら不可)。mid<=15円=OK(実行)。
