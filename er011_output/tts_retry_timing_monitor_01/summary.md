# TTS retry timing monitor — summary

(自動生成。手動編集しないこと。再実行のたびに上書きされる。)

- attempt files scanned: 483 (load errors: 0)
- usable records (segment_id あり): 483
- distinct segment groups: 361 (2+ attempts: 85)
- human_review_queue.jsonl entries: 32

## 表1: 種別B(品質NG)のみ — P(次attemptがPASS | 直前連続NG回数, retry間隔bucket)

| 直前連続NG回数 | 間隔bucket | N | PASS数 | PASS率 |
|---|---|---|---|---|
| 1 | 1_immediate_lt5min | 41 | 27 | 0.6585 |
| 1 | 2_5to30min | 1 | 1 | 1.0 |
| 1 | 3_30min_to_6h | 1 | 1 | 1.0 |
| 2 | 1_immediate_lt5min | 12 | 2 | 0.1667 |
| 3plus | 1_immediate_lt5min | 8 | 1 | 0.125 |
| 3plus | 2_5to30min | 1 | 1 | 1.0 |
| 3plus | 3_30min_to_6h | 3 | 0 | 0.0 |
| 3plus | 4_6h_to_next_day_or_later | 3 | 2 | 0.6667 |

## 表2: 種別A(API/infra error疑い)— 同形式

| 直前連続NG回数 | 間隔bucket | N | PASS数 | PASS率 |
|---|---|---|---|---|
| 1 | 1_immediate_lt5min | 2 | 2 | 1.0 |
| 3plus | 1_immediate_lt5min | 2 | 0 | 0.0 |

## 検証ロジック変更(post-hoc)により表1から除外すべき行(household topic_intro型)

- (該当なし)

## パターン別件数(segment単位、group_pattern分類)

| パターン | 件数 |
|---|---|
| single_attempt_only | 276 |
| all_pass_no_retry_needed | 41 |
| ng_x1_then_pass_simple_retry | 30 |
| never_resolved_all_ng_in_log | 8 |
| ng_x3plus_then_eventually_pass | 4 |
| ng_x2_then_eventually_pass | 2 |

詳細は observations.jsonl / summary.json を参照。
