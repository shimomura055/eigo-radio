# Latency表(NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02、3テーマ横断)

機械集計は`latency.json`(本Trialの`raw_usage_log.jsonl`の`elapsed_seconds`)。
下水道Trial-01の値は`er015_output/news_iterative_entertainment_trial_01/
raw_usage_log.jsonl`から転記(同ファイルに`elapsed_seconds`が実測記録されて
おり、Trial-01のREPORTには未転記だったため今回追加で参照した)。

| テーマ | 段階 | elapsed_seconds | 累計(Original起点) |
|---|---|---|---|
| A(AI電話代行) | Original | 19.778 | 19.778 |
| A(AI電話代行) | R1 | 13.007 | 32.785 |
| A(AI電話代行) | R2 | 12.491 | 45.276 |
| A(AI電話代行) | R3 | 11.534 | 56.810 |
| B(旅行の荷物) | Original | 12.162 | 12.162 |
| B(旅行の荷物) | R1 | 9.901 | 22.063 |
| B(旅行の荷物) | R2 | 10.162 | 32.225 |
| B(旅行の荷物) | R3 | 12.237 | 44.462 |
| 下水道(Trial-01) | Original | 18.503 | 18.503 |
| 下水道(Trial-01) | R1 | 11.996 | 30.499 |
| 下水道(Trial-01) | R2 | 19.696 | 50.195 |
| 下水道(Trial-01) | R3 | 20.523 | 70.718 |

## Original→R2止め vs Original→R3までの累計時間差

| テーマ | Original→R2累計(秒) | Original→R3累計(秒) | R3を追加することによる増分(秒) |
|---|---|---|---|
| A(AI電話代行) | 45.276 | 56.810 | 11.534 |
| B(旅行の荷物) | 32.225 | 44.462 | 12.237 |
| 下水道(Trial-01) | 50.195 | 70.718 | 20.523 |

R3追加分の増分は下水道(+20.5秒)がA/B(+11.5秒/+12.2秒)よりおよそ8〜9秒
大きい。ただしcall回数は同一(4call)で、増分はR3単体のAPI応答時間そのもの
であり、テーマ間のばらつき(11.5〜20.5秒)が何に起因するかの評価は
`[Fable記入]`。

## 費用(cost.json)

| stage | input_tokens | cached_input_tokens | output_tokens | USD |
|---|---|---|---|---|
| A_original | 462 | 0 | 1797 | 0.002249 |
| A_r1 | 2294 | 0 | 1058 | 0.001728 |
| A_r2 | 3388 | 2291 | 1072 | 0.001552 |
| A_r3 | 4496 | 3385 | 1085 | 0.001592 |
| B_original | 445 | 0 | 991 | 0.001278 |
| B_r1 | 1471 | 0 | 834 | 0.001295 |
| B_r2 | 2341 | 1468 | 879 | 0.001259 |
| B_r3 | 3256 | 2338 | 935 | 0.001352 |

合計: total_calls=8, total_usd=0.0123, **total_jpy=1.97円**(上限¥60以内)。
参考: 下水道Trial-01は4call・total_jpy=1.02円。本Trial(A+B、8call)は
1.97円で、1記事あたりに換算すると約0.99円(下水道とほぼ同水準)。
