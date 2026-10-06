# trial_summary_01(委任_02 一次集計、Status分類はFable)

累計実費: ¥10.3542

| 項目 | same_blind | same_nonblind | split_blind |
|---|---|---|---|
| model(ledger/article) | gpt-6-luna/gpt-6-luna | gpt-6-luna/gpt-6-luna | gpt-5.6-luna/gpt-6-luna |
| calls/実費¥/¥per call | 154/2.484556/0.01613 | 75/4.543433/0.06058 | 149/3.326217/0.02232 |
| 失敗call/予算停止 | 0/False | 0/False | 0/False |
| gold検出(rep0)/repeat計 | 2/3, 8/9 | 2/3, 5/9 | 2/3, 7/9 |
| 人工反転 厳密/許容 検出 | 3/6, 2/8 | 4/6, 1/8 | 2/6, 2/8 |
| 反転17件 検出/見逃し | 7/10 | 7/10 | 6/11 |
| 正常43 誤反転(rate) | 3 (0.0698) 全repeat率0.0698 | 0 (0.0) 全repeat率0.0 | 2 (0.0465) 全repeat率0.0465 |
| 判断不能(UNCLEAR)全体/正常内 | 14/9 | 12/5 | 15/10 |
| 機械比較分布 | {'UNCLEAR': 14, 'NOT_MENTIONED': 32, 'REVERSED': 10, 'LEDGER_NO_DIRECTION': 7} | {'UNCLEAR': 12, 'NOT_MENTIONED': 33, 'SAME': 5, 'LEDGER_NO_DIRECTION': 6, 'REVERSED': 7} | {'UNCLEAR': 15, 'NOT_MENTIONED': 33, 'REVERSED': 8, 'SAME': 1, 'LEDGER_NO_DIRECTION': 6} |
| Ledger has_direction精度/state精度/揺れfact | 0.8667/0.3333(any0.5333)/1 | 0.8/0.4(any0.6)/0 | 0.6667/0.3333(any0.5333)/3 |
| 記事側state精度(n) | 0.5357(56) | 0.5789(57) | 0.5088(57) |
| 曖昧3件 | {'G-04': {'expected': 'UNCLEAR', 'repeat_compares': ['UNCLEAR', 'NOT_MENTIONED', 'NOT_MENTIONED']}, 'G-05': {'expected': 'UNCLEAR', 'repeat_compares': ['NOT_MENTIONED', 'REVERSED', 'NOT_MENTIONED']}, 'G-06': {'expected': 'UNCLEAR', 'repeat_compares': ['UNCLEAR', 'UNCLEAR', 'UNCLEAR']}} | {'G-04': {'expected': 'UNCLEAR', 'repeat_compares': ['NOT_MENTIONED', 'NOT_MENTIONED', 'NOT_MENTIONED']}, 'G-05': {'expected': 'UNCLEAR', 'repeat_compares': ['UNCLEAR', 'SAME', 'SAME']}, 'G-06': {'expected': 'UNCLEAR', 'repeat_compares': ['NOT_MENTIONED', 'NOT_MENTIONED', 'NOT_MENTIONED']}} | {'G-04': {'expected': 'UNCLEAR', 'repeat_compares': ['NOT_MENTIONED', 'UNCLEAR', 'NOT_MENTIONED']}, 'G-05': {'expected': 'UNCLEAR', 'repeat_compares': ['NOT_MENTIONED', 'NOT_MENTIONED', 'REVERSED']}, 'G-06': {'expected': 'UNCLEAR', 'repeat_compares': ['NOT_MENTIONED', 'UNCLEAR', 'UNCLEAR']}} |

## 比較

```
{
 "ledger_same_vs_split": {
  "pair_agreement": 0.7667,
  "pairs": 30,
  "facts_fully_agree": 6,
  "facts": 10
 },
 "blind_vs_nonblind_gold": {
  "same_blind": {
   "rep0": 2,
   "repeats": "8/9"
  },
  "same_nonblind": {
   "rep0": 2,
   "repeats": "5/9"
  }
 }
}
```

## 1 runあたり追加処理・費用・不要Rewrite見込み(基準: 現行Rewrite 0.67件/run)

### same_blind
- low(記事側3.33単位+Ledger13.67fact): 追加call 17.0/run、追加¥0.369/run、不要Rewrite見込み 0.232件/run(現行0.67の0.35倍)
- mid(記事側7.46単位+Ledger13.67fact): 追加call 21.13/run、追加¥0.429/run、不要Rewrite見込み 0.521件/run(現行0.67の0.78倍)
- high(記事側30.56単位+Ledger13.67fact): 追加call 44.23/run、追加¥0.76/run、不要Rewrite見込み 2.133件/run(現行0.67の3.18倍)
### same_nonblind
- low(記事側3.33単位+Ledger13.67fact): 追加call 3.33/run、追加¥0.202/run、不要Rewrite見込み 0.0件/run(現行0.67の0.0倍)
- mid(記事側7.46単位+Ledger13.67fact): 追加call 7.46/run、追加¥0.452/run、不要Rewrite見込み 0.0件/run(現行0.67の0.0倍)
- high(記事側30.56単位+Ledger13.67fact): 追加call 30.56/run、追加¥1.851/run、不要Rewrite見込み 0.0件/run(現行0.67の0.0倍)
### split_blind
- low(記事側3.33単位+Ledger13.67fact): 追加call 17.0/run、追加¥0.422/run、不要Rewrite見込み 0.155件/run(現行0.67の0.23倍)
- mid(記事側7.46単位+Ledger13.67fact): 追加call 21.13/run、追加¥0.511/run、不要Rewrite見込み 0.347件/run(現行0.67の0.52倍)
- high(記事側30.56単位+Ledger13.67fact): 追加call 44.23/run、追加¥1.007/run、不要Rewrite見込み 1.421件/run(現行0.67の2.12倍)

(注) 反転17件=gold3+人工14。誤反転はrep0基準、全repeat率併記。詳細はtrial_summary_01.json。
