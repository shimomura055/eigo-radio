# METRICS_06: 補強Trial_06 実測(委任_31。API 0で台帳から集計)

総call(台帳行)=102 / 総費用=19.306円 / 総wall(call合計)=2108.3s

## arm x set x 構成(level/call単位。重複行を除く)
| set | arm | level(call group)数 | call数(retry込) | 評価KP出力 | 対象KP総数(sibling込) | 入力tok | 出力tok | reasoning tok | 円 | wall合計s | wall/group平均s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HC/R | B0p | 16 | 16 | 18 | 18 | 36890 | 7741 | 5774 | 0.944 | 105.0 | 6.6 |
| HC/R | X2pp | 20 | 20 | 25 | 25 | 53856 | 27399 | 23667 | 2.744 | 307.6 | 15.4 |
| S2 | B0p | 33 | 33 | 54 | 161 | 83854 | 36741 | 23532 | 4.281 | 422.4 | 12.8 |
| S2 | X2pp | 33 | 33 | 54 | 161 | 95654 | 122579 | 102907 | 11.337 | 1273.4 | 38.6 |

## Stage 2(本番構成)単価・B0p比
- B0p: 総4.281円 / 対象KP161 -> 0.0266円/KP / wall/level 12.8s / 出力tok/KP 228 / reasoning tok/KP 146
- X2pp: 総11.337円 / 対象KP161 -> 0.0704円/KP / wall/level 38.6s / 出力tok/KP 761 / reasoning tok/KP 639
- 1記事セット(約10KP想定、sibling込み)換算: B0p 0.266円 / X2pp 0.704円 / 増分 0.438円(=0.63% of 70円目標)。X2pp/B0p費用比=2.6倍
- level(1 call)あたりwall増分 25.8s(X2pp 38.6s - B0p 12.8s)。1記事セットのlevel数が1(約10KP/level)の場合の増分に等しい。

## 機械的事実(判定しない)
- 持ち込み検出(record-only detect_import、評価KP出力): {('B0p', 'neg_in_gloss_not_in_kp'): 2, ('X2pp', 'neg_in_gloss_not_in_kp'): 5}
- ALIGN_PASS以外のgroup: 0 / retry(attempts>1)のgroup: 0
- 評価KP出力行数: {('B0p', 'HC'): 18, ('B0p', 'S2'): 54, ('X2pp', 'HC'): 18, ('X2pp', 'S2'): 54, ('X2pp', 'R'): 7}
