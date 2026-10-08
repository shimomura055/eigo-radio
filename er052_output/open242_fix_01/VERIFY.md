# OPEN-242 修正検証(reuse: 既存raw_usage_log再計算、API課金なし)

| run | 修正前ガード表示 | 修正後ガード累計 | cost.json total | 差 |
|---|---|---|---|---|
| run_01 | 6.68 | 19.481 | 19.48 | +0.001 |
| run_02 | 4.70 | 19.105 | 19.105 | 0.000 |

生出力 verify_raw.txt。単価=pricing_snapshot.json openai/"N/A (tool, all models)"/web_search_call $10/1,000calls。
回帰: er012*_test* 224/224, er019*_test* 268/268, er006*_test* 39/39 PASS(新規失敗0)。
