# trial_summary_02(事実のみ、Status判定はFable)

実費 2.081872円 / calls 104 / items 63

## 合格基準チェック

| 基準 | 結果 | 根拠 |
|---|---|---|
| 1 HC-012 3/3検出 | 充足 | 3/3 rep0=REVERSED |
| 2 A5-0 3/3検出 | 充足 | 3/3 rep0=REVERSED |
| 3 正常文の誤重大判定2%以下 | 充足 | 0/43=0.0 ids=[] |
| 4 不要Rewrite見込み0.335以下(全3水準) | 充足 | {'low': 0.0, 'mid': 0.0, 'high': 0.0} |
| 5 前回誤爆3件解消(3反復ともREVERSEDでない) | 充足 | {'F-09': ['SAME', 'SAME', 'SAME'], 'F-10': ['SAME', 'SAME', 'SAME'], 'F-19': ['SAME', 'SAME_FAMILY', 'SAME_FAMILY']} |
| 6 新しい重大見逃しなし(前回検出gold/人工反転の今回見逃し) | 未達 | {'new_misses': ['S-06']} |

## 前回比

| 項目 | TRIAL-01 | TRIAL-02 |
|---|---|---|
| HC-012(G-01) k/n | 3/3 | 3/3 |
| A5-0(G-02) k/n | 3/3 | 3/3 |
| D61(G-03) k/n | 2/3 | 0/3 |
| gold repeat計 | 8/9 | 6/9 |
| 正常文誤重大 件(rate) | 3(0.0698) | 0(0.0) |
| 正常文誤重大 ids | ['F-09', 'F-10', 'F-19'] | [] |
| UNCLEAR全体 | 14 | 6 |
| 人工反転 検出 | 5/14 | 4/14 |
| low 追加円/run | 0.369 | 0.34 |
| low 不要Rewrite/run | 0.232 | 0.0 |
| mid 追加円/run | 0.429 | 0.423 |
| mid 不要Rewrite/run | 0.521 | 0.0 |
| high 追加円/run | 0.76 | 0.885 |
| high 不要Rewrite/run | 2.133 | 0.0 |

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
   "NOT_MENTIONED",
   "NOT_MENTIONED"
  ],
  "k": 0,
  "n": 3
 }
}
```

## normal
```
{
 "n": 43,
 "false_reversal": 0,
 "false_reversal_ids": [],
 "rate_rep0": 0.0,
 "rate_all_repeats": 0.0,
 "unclear": 5,
 "not_mentioned": 25
}
```

## prev_false_alarms
```
{
 "F-09": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME",
   "SAME"
  ],
  "resolved": true
 },
 "F-10": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME",
   "SAME"
  ],
  "resolved": true
 },
 "F-19": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME_FAMILY",
   "SAME_FAMILY"
  ],
  "resolved": true
 }
}
```

## synthetic
```
{
 "n": 14,
 "strict_n": 7,
 "strict_detected": 4,
 "tolerant_n": 7,
 "tolerant_detected": 0,
 "tolerant_ok_by_acceptable": 6,
 "detected": 4,
 "missed_ids": [
  "S-01",
  "S-02",
  "S-03",
  "S-04",
  "S-05",
  "S-06",
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
  "rep0": "NOT_MENTIONED",
  "compares": [
   "NOT_MENTIONED",
   "UNCLEAR",
   "UNCLEAR"
  ],
  "any_reversed": false
 },
 "G-05": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "NOT_MENTIONED",
   "SAME"
  ],
  "any_reversed": false
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
 "n_multi_repeat_items": 9,
 "all_agree": 6,
 "agree_rate": 0.6667,
 "disagree_ids": [
  "F-19",
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
 "event_match_rate": 0.6667,
 "state_accuracy_given_match": 0.9615,
 "state_accuracy_all_truth_events": 0.641,
 "extra_events_per_rep": 0.033,
 "repeat_agreement_facts": "6/10",
 "repeat_agreement_rate": 0.6
}
```

## article_side
```
{
 "selected_event_n": 81,
 "selected_event_accuracy": 0.6914,
 "article_state_n": 0,
 "article_state_accuracy": null
}
```

## per_run
```
{
 "jpy_per_call": 0.02002,
 "levels": {
  "low": {
   "units_per_run": 3.33,
   "added_calls": 17.0,
   "added_jpy": 0.34,
   "unneeded_rewrite_per_run": 0.0,
   "vs_baseline_rewrite_0.67": 0.0,
   "le_half_baseline_0.335": true
  },
  "mid": {
   "units_per_run": 7.46,
   "added_calls": 21.13,
   "added_jpy": 0.423,
   "unneeded_rewrite_per_run": 0.0,
   "vs_baseline_rewrite_0.67": 0.0,
   "le_half_baseline_0.335": true
  },
  "high": {
   "units_per_run": 30.56,
   "added_calls": 44.23,
   "added_jpy": 0.885,
   "unneeded_rewrite_per_run": 0.0,
   "vs_baseline_rewrite_0.67": 0.0,
   "le_half_baseline_0.335": true
  }
 }
}
```

## D. repeat別内訳(選択subject / ledger_state / article_state / compare)

| id | label | rep | selected_subject | ledger_state | article_state | compare |
|---|---|---|---|---|---|---|
| F-09 | 忠実 | 1 | Brent先物の上げ幅 | DECREASED | DECREASED | SAME |
| F-09 | 忠実 | 2 | Brent先物の上げ幅 | DECREASED | DECREASED | SAME |
| F-09 | 忠実 | 3 | Brent先物の上げ幅 | DECREASED | DECREASED | SAME |
| F-10 | 忠実 | 1 | Brent先物の上げ幅 | DECREASED | DECREASED | SAME |
| F-10 | 忠実 | 2 | Brent先物の上げ幅 | DECREASED | DECREASED | SAME |
| F-10 | 忠実 | 3 | Brent先物の上げ幅 | DECREASED | DECREASED | SAME |
| F-19 | 忠実 | 1 | 機能 | STOPPED | STOPPED | SAME |
| F-19 | 忠実 | 2 | 機能 | PAUSED | STOPPED | SAME_FAMILY |
| F-19 | 忠実 | 3 | 機能 | PAUSED | STOPPED | SAME_FAMILY |
| G-01 | 真の反転 | 1 | 機能 | STOPPED | AVAILABLE | REVERSED |
| G-01 | 真の反転 | 2 | 機能 | PAUSED | AVAILABLE | REVERSED |
| G-01 | 真の反転 | 3 | 機能 | PAUSED | AVAILABLE | REVERSED |
| G-02 | 真の反転 | 1 | 機能 | STOPPED | AVAILABLE | REVERSED |
| G-02 | 真の反転 | 2 | 機能 | PAUSED | AVAILABLE | REVERSED |
| G-02 | 真の反転 | 3 | 機能 | PAUSED | AVAILABLE | REVERSED |
| G-03 | 真の反転 | 1 | NONE | None | NOT_MENTIONED | NOT_MENTIONED |
| G-03 | 真の反転 | 2 | NONE | None | NOT_MENTIONED | NOT_MENTIONED |
| G-03 | 真の反転 | 3 | NONE | None | NOT_MENTIONED | NOT_MENTIONED |
| G-04 | 曖昧 | 1 | NONE | None | NOT_MENTIONED | NOT_MENTIONED |
| G-04 | 曖昧 | 2 | Brent先物の価格水準 | INCREASED | UNCLEAR | UNCLEAR |
| G-04 | 曖昧 | 3 | Brent先物の価格水準 | INCREASED | UNCLEAR | UNCLEAR |
| G-05 | 曖昧 | 1 | Brent先物の水準 | INCREASED | INCREASED | SAME |
| G-05 | 曖昧 | 2 | NONE | None | NOT_MENTIONED | NOT_MENTIONED |
| G-05 | 曖昧 | 3 | Brent先物の価格水準 | INCREASED | INCREASED | SAME |
| G-06 | 曖昧 | 1 | 機能 | STOPPED | UNCHANGED | UNCLEAR |
| G-06 | 曖昧 | 2 | 機能 | PAUSED | UNCLEAR | UNCLEAR |
| G-06 | 曖昧 | 3 | 機能 | PAUSED | UNCHANGED | UNCLEAR |
| S-06 | 人工反転 | 1 | Brent先物の上げ幅 | DECREASED | DECREASED | SAME |

注: S-06は事象リスト外(outside_event_list)の人工反転。前回検出→今回見逃し=新重大見逃し候補(判断はFable)。
