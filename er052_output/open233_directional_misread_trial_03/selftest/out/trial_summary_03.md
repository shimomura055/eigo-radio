# trial_summary_03(事実のみ、Status判定はFable)

## 合格基準チェック(8行)

| 基準 | X | X根拠 | Y | Y根拠 |
|---|---|---|---|---|
| 1 HC-012 3/3維持 | 充足 | 3/3 rep0=REVERSED | 充足 | 3/3 rep0=REVERSED |
| 2 A5-0 3/3維持 | 充足 | 3/3 rep0=REVERSED | 充足 | 3/3 rep0=REVERSED |
| 3 D61 2/3以上 | 未達 | 0/3 rep0=NOT_MENTIONED | 未達 | 0/3 rep0=NOT_MENTIONED |
| 4 held-out重大例 平均2/3以上かつ全例1/3以上 | 判定不能 | held-out重大例なし | 判定不能 | held-out重大例なし |
| 5 正常文+held-out正常例 不要な重大判定0 | 充足 | 0/43 ids=[] (全repeat[]) | 充足 | 0/43 ids=[] (全repeat[]) |
| 6 不要Rewrite見込み0件/run | 充足 | {'low': 0.0, 'mid': 0.0, 'high': 0.0} | 充足 | {'low': 0.0, 'mid': 0.0, 'high': 0.0} |
| 7 新たな重大見逃し0(前回REVERSED→今回非REVERSED) | 充足 | {'new_misses': [], 'outside_event_list_ref': []} | 充足 | {'new_misses': [], 'outside_event_list_ref': []} |
| 8 前回誤爆3件(F-09/F-10/F-19)再発なし | 充足 | {'F-09': ['SAME', 'SAME', 'SAME'], 'F-10': ['SAME', 'SAME', 'SAME'], 'F-19': ['SAME', 'SAME_FAMILY', 'SAME_FAMILY']} | 充足 | {'F-09': ['SAME', 'SAME', 'SAME'], 'F-10': ['SAME', 'SAME', 'SAME'], 'F-19': ['SAME', 'SAME_FAMILY', 'SAME_FAMILY']} |

## 構成X: 実費1.38545円 / calls 111 / items 63

### gold
```
{
 "G-01": {
  "name": "HC-012",
  "rep0": "REVERSED",
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
### held_gold
```
{
 "items": {},
 "mean_k_rate": null,
 "min_k_rate": null
}
```
### normal_pool
```
{
 "n": 43,
 "n_held_normal": 0,
 "false_reversal": 0,
 "false_reversal_ids": [],
 "rate_rep0": 0.0,
 "rate_all_repeats": 0.0,
 "false_reversal_any_repeat_ids": []
}
```
### prev_false_alarms
```
{
 "F-09": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME",
   "SAME"
  ],
  "k": 0,
  "n": 3,
  "recurred": false
 },
 "F-10": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME",
   "SAME"
  ],
  "k": 0,
  "n": 3,
  "recurred": false
 },
 "F-19": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME_FAMILY",
   "SAME_FAMILY"
  ],
  "k": 0,
  "n": 3,
  "recurred": false
 }
}
```
### fluctuation
```
{
 "n_multi": 9,
 "all_agree": 6,
 "agree_rate": 0.6667,
 "disagree_ids": [
  "F-19",
  "G-04",
  "G-05"
 ]
}
```
### fallback
```
{
 "items_with_fallback": 0,
 "repeats_with_fallback": 0,
 "repeat_fallback_rate": 0.0,
 "fallback_calls": 0,
 "fallback_ids": [],
 "summary_fallback_calls": null,
 "fallback_cost_jpy": null
}
```
### phase
```
{
 "article_phase_distribution": {
  "None": 81
 },
 "expected_phase_n": 0,
 "expected_phase_match": null,
 "phase_repeat_items": 0,
 "phase_repeat_agree_rate": null
}
```
### rep0_distribution
```
{
 "NOT_MENTIONED": 35,
 "UNCLEAR": 6,
 "SAME": 8,
 "LEDGER_NO_DIRECTION": 7,
 "SAME_FAMILY": 1,
 "REVERSED": 6
}
```
### ledger_side / per_run
```
{
 "ledger": {
  "n_ledger_reps": 30,
  "has_direction_accuracy": 0.8667,
  "event_match_rate": 0.6667,
  "state_accuracy_given_match": 0.9615,
  "ledger_phase_n": 0,
  "ledger_phase_accuracy": null
 },
 "per_run": {
  "jpy_per_call": 0.01248,
  "fallback_calls_per_repeat": 0.0,
  "levels": {
   "low": {
    "units_per_run": 3.33,
    "added_calls": 17.0,
    "added_jpy": 0.212,
    "unneeded_rewrite_per_run": 0.0
   },
   "mid": {
    "units_per_run": 7.46,
    "added_calls": 21.13,
    "added_jpy": 0.264,
    "unneeded_rewrite_per_run": 0.0
   },
   "high": {
    "units_per_run": 30.56,
    "added_calls": 44.23,
    "added_jpy": 0.552,
    "unneeded_rewrite_per_run": 0.0
   }
  }
 }
}
```
### 前回比(TRIAL-02)

| 項目 | 前回(TRIAL-02) | 今回 |
|---|---|---|
| G-01 検出k/3 | 3 | 3 |
| G-02 検出k/3 | 3 | 3 |
| G-03 検出k/3 | 0 | 0 |
| 正常文 誤REVERSED(rep0) | 0 [] | 0 [] |
| UNCLEAR(rep0) | 6 | 6 |
| 実費(円) | 2.081872 | 1.38545 (差 -0.6964) |

項目数 前回63 / 今回63、今回のみのid: []
REVERSEDになった: []
REVERSEDでなくなった: []

rep0変化id一覧:
- なし

## 構成Y: 実費1.38545円 / calls 111 / items 63

### gold
```
{
 "G-01": {
  "name": "HC-012",
  "rep0": "REVERSED",
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
### held_gold
```
{
 "items": {},
 "mean_k_rate": null,
 "min_k_rate": null
}
```
### normal_pool
```
{
 "n": 43,
 "n_held_normal": 0,
 "false_reversal": 0,
 "false_reversal_ids": [],
 "rate_rep0": 0.0,
 "rate_all_repeats": 0.0,
 "false_reversal_any_repeat_ids": []
}
```
### prev_false_alarms
```
{
 "F-09": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME",
   "SAME"
  ],
  "k": 0,
  "n": 3,
  "recurred": false
 },
 "F-10": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME",
   "SAME"
  ],
  "k": 0,
  "n": 3,
  "recurred": false
 },
 "F-19": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME_FAMILY",
   "SAME_FAMILY"
  ],
  "k": 0,
  "n": 3,
  "recurred": false
 }
}
```
### fluctuation
```
{
 "n_multi": 9,
 "all_agree": 6,
 "agree_rate": 0.6667,
 "disagree_ids": [
  "F-19",
  "G-04",
  "G-05"
 ]
}
```
### fallback
```
{
 "items_with_fallback": 0,
 "repeats_with_fallback": 0,
 "repeat_fallback_rate": 0.0,
 "fallback_calls": 0,
 "fallback_ids": [],
 "summary_fallback_calls": null,
 "fallback_cost_jpy": null
}
```
### phase
```
{
 "article_phase_distribution": {
  "None": 81
 },
 "expected_phase_n": 0,
 "expected_phase_match": null,
 "phase_repeat_items": 0,
 "phase_repeat_agree_rate": null
}
```
### rep0_distribution
```
{
 "NOT_MENTIONED": 35,
 "UNCLEAR": 6,
 "SAME": 8,
 "LEDGER_NO_DIRECTION": 7,
 "SAME_FAMILY": 1,
 "REVERSED": 6
}
```
### ledger_side / per_run
```
{
 "ledger": {
  "n_ledger_reps": 30,
  "has_direction_accuracy": 0.8667,
  "event_match_rate": 0.6667,
  "state_accuracy_given_match": 0.9615,
  "ledger_phase_n": 0,
  "ledger_phase_accuracy": null
 },
 "per_run": {
  "jpy_per_call": 0.01248,
  "fallback_calls_per_repeat": 0.0,
  "levels": {
   "low": {
    "units_per_run": 3.33,
    "added_calls": 17.0,
    "added_jpy": 0.212,
    "unneeded_rewrite_per_run": 0.0
   },
   "mid": {
    "units_per_run": 7.46,
    "added_calls": 21.13,
    "added_jpy": 0.264,
    "unneeded_rewrite_per_run": 0.0
   },
   "high": {
    "units_per_run": 30.56,
    "added_calls": 44.23,
    "added_jpy": 0.552,
    "unneeded_rewrite_per_run": 0.0
   }
  }
 }
}
```
### 前回比(TRIAL-02)

| 項目 | 前回(TRIAL-02) | 今回 |
|---|---|---|
| G-01 検出k/3 | 3 | 3 |
| G-02 検出k/3 | 3 | 3 |
| G-03 検出k/3 | 0 | 0 |
| 正常文 誤REVERSED(rep0) | 0 [] | 0 [] |
| UNCLEAR(rep0) | 6 | 6 |
| 実費(円) | 2.081872 | 1.38545 (差 -0.6964) |

項目数 前回63 / 今回63、今回のみのid: []
REVERSEDになった: []
REVERSEDでなくなった: []

rep0変化id一覧:
- なし
