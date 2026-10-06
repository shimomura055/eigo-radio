# trial_summary_02(事実のみ、Status判定はFable)

実費 2.484556円 / calls 154 / items 63

## 合格基準チェック

| 基準 | 結果 | 根拠 |
|---|---|---|
| 1 HC-012 3/3検出 | 充足 | 3/3 rep0=REVERSED |
| 2 A5-0 3/3検出 | 充足 | 3/3 rep0=REVERSED |
| 3 正常文の誤重大判定2%以下 | 未達 | 3/43=0.0698 ids=['F-09', 'F-10', 'F-19'] |
| 4 不要Rewrite見込み0.335以下(全3水準) | 未達 | {'low': 0.232, 'mid': 0.521, 'high': 2.133} |
| 5 前回誤爆3件解消(3反復ともREVERSEDでない) | 未達 | {'F-09': ['REVERSED'], 'F-10': ['REVERSED'], 'F-19': ['REVERSED']} |
| 6 新しい重大見逃しなし(前回検出gold/人工反転の今回見逃し) | 充足 | {'new_misses': []} |

## 前回比

| 項目 | TRIAL-01 | TRIAL-02 |
|---|---|---|
| HC-012(G-01) k/n | 3/3 | 3/3 |
| A5-0(G-02) k/n | 3/3 | 3/3 |
| D61(G-03) k/n | 2/3 | 2/3 |
| gold repeat計 | 8/9 | 8/9 |
| 正常文誤重大 件(rate) | 3(0.0698) | 3(0.0698) |
| 正常文誤重大 ids | ['F-09', 'F-10', 'F-19'] | ['F-09', 'F-10', 'F-19'] |
| UNCLEAR全体 | 14 | 14 |
| 人工反転 検出 | 5/14 | 5/14 |
| low 追加円/run | 0.369 | 0.274 |
| low 不要Rewrite/run | 0.232 | 0.232 |
| mid 追加円/run | 0.429 | 0.341 |
| mid 不要Rewrite/run | 0.521 | 0.521 |
| high 追加円/run | 0.76 | 0.714 |
| high 不要Rewrite/run | 2.133 | 2.133 |

## gold
```
{
 "G-01": {
  "name": "HC-012",
  "rep0": "REVERSED",
  "rep0_detected": true,
  "compares": [
   "REVERSED",
   "REVERSED",
   "REVERSED"
  ],
  "k": 3,
  "n": 3
 },
 "G-02": {
  "name": "A5-0",
  "rep0": "REVERSED",
  "rep0_detected": true,
  "compares": [
   "REVERSED",
   "REVERSED",
   "REVERSED"
  ],
  "k": 3,
  "n": 3
 },
 "G-03": {
  "name": "D61",
  "rep0": "NOT_MENTIONED",
  "rep0_detected": false,
  "compares": [
   "NOT_MENTIONED",
   "REVERSED",
   "REVERSED"
  ],
  "k": 2,
  "n": 3
 }
}
```

## normal
```
{
 "n": 43,
 "false_reversal": 3,
 "false_reversal_ids": [
  "F-09",
  "F-10",
  "F-19"
 ],
 "rate_rep0": 0.0698,
 "rate_all_repeats": 0.0698,
 "unclear": 9,
 "not_mentioned": 25
}
```

## prev_false_alarms
```
{
 "F-09": {
  "rep0": "REVERSED",
  "compares": [
   "REVERSED"
  ],
  "resolved": false
 },
 "F-10": {
  "rep0": "REVERSED",
  "compares": [
   "REVERSED"
  ],
  "resolved": false
 },
 "F-19": {
  "rep0": "REVERSED",
  "compares": [
   "REVERSED"
  ],
  "resolved": false
 }
}
```

## synthetic
```
{
 "n": 14,
 "strict_n": 6,
 "strict_detected": 3,
 "tolerant_n": 8,
 "tolerant_detected": 2,
 "tolerant_ok_by_acceptable": 5,
 "detected": 5,
 "missed_ids": [
  "S-01",
  "S-02",
  "S-03",
  "S-04",
  "S-05",
  "S-08",
  "S-09",
  "S-11",
  "S-14"
 ]
}
```

## ambiguous
```
{
 "G-04": {
  "rep0": "UNCLEAR",
  "compares": [
   "UNCLEAR",
   "NOT_MENTIONED",
   "NOT_MENTIONED"
  ],
  "any_reversed": false
 },
 "G-05": {
  "rep0": "NOT_MENTIONED",
  "compares": [
   "NOT_MENTIONED",
   "REVERSED",
   "NOT_MENTIONED"
  ],
  "any_reversed": true
 },
 "G-06": {
  "rep0": "UNCLEAR",
  "compares": [
   "UNCLEAR",
   "UNCLEAR",
   "UNCLEAR"
  ],
  "any_reversed": false
 }
}
```

## fluctuation
```
{
 "n_multi_repeat_items": 6,
 "all_agree": 3,
 "agree_rate": 0.5,
 "disagree_ids": [
  "G-03",
  "G-04",
  "G-05"
 ]
}
```

## ledger_side
```
{
 "n_facts": 10,
 "n_ledger_reps": 30,
 "has_direction_accuracy": 0.8667,
 "event_match_rate": 0.9333,
 "state_accuracy_given_match": 0.3571,
 "state_accuracy_all_truth_events": 0.3333,
 "extra_events_per_rep": 0.333,
 "repeat_agreement_facts": "8/10",
 "repeat_agreement_rate": 0.8
}
```

## article_side
```
{
 "selected_event_n": 0,
 "selected_event_accuracy": null,
 "article_state_n": 75,
 "article_state_accuracy": 0.44
}
```

## per_run
```
{
 "jpy_per_call": 0.01613,
 "levels": {
  "low": {
   "units_per_run": 3.33,
   "added_calls": 17.0,
   "added_jpy": 0.274,
   "unneeded_rewrite_per_run": 0.232,
   "vs_baseline_rewrite_0.67": 0.35,
   "le_half_baseline_0.335": true
  },
  "mid": {
   "units_per_run": 7.46,
   "added_calls": 21.13,
   "added_jpy": 0.341,
   "unneeded_rewrite_per_run": 0.521,
   "vs_baseline_rewrite_0.67": 0.78,
   "le_half_baseline_0.335": false
  },
  "high": {
   "units_per_run": 30.56,
   "added_calls": 44.23,
   "added_jpy": 0.714,
   "unneeded_rewrite_per_run": 2.133,
   "vs_baseline_rewrite_0.67": 3.18,
   "le_half_baseline_0.335": false
  }
 }
}
```
