| 検出器 | units(重大/人間確認/非重大) | Recall_human(主) | Recall_all(副) | FPR_clear | FPR_boundary | FPR_hardneg | Flag(unit,sent,type)/unit | Flag固有文/unit | Rollback | 方向反転(別Fact) | 費用JPY |
|---|---|---|---|---|---|---|---|---|---|---|---|
| d2_gpt-6.1-sol_synthetic_dev_rep1 | 7(7/0/0) | - | 5/7 (71%, CI 36%-92%) | - | - | - | 0.71 | 0.71 | 2/2 | 1/1 | 6.36 |
| d1full_gpt-6.1-sol_synthetic_dev_gate | 7(7/0/0) | - | 5/7 (71%, CI 36%-92%) | - | - | - | 1.14 | 0.71 | 2/2 | 1/1 | 26.07 |

見逃し重大 / 誤Flag(clear・boundary・hardneg):
- d2_gpt-6.1-sol_synthetic_dev_rep1: 見逃し=S-02,S-08 / 誤Flag clear=- boundary=- hardneg=-
- d1full_gpt-6.1-sol_synthetic_dev_gate: 見逃し=S-02,S-08 / 誤Flag clear=- boundary=- hardneg=-

### 既知事故別(拾った/件数)
| 検出器 | Rollback方向反転 |
|---|---|
| d2_gpt-6.1-sol_synthetic_dev_rep1 | 2/2 |
| d1full_gpt-6.1-sol_synthetic_dev_gate | 2/2 |

### タイプ別Recall(重大ケースのaccident_type別、hit/n)
| 検出器 | rollback方向反転 | 数量時系列 | 方向反転(別Fact) |
|---|---|---|---|
| d2_gpt-6.1-sol_synthetic_dev_rep1 | 2/2 | 2/4 | 1/1 |
| d1full_gpt-6.1-sol_synthetic_dev_gate | 2/2 | 2/4 | 1/1 |
### confidence閾値曲線: d2_gpt-6.1-sol_synthetic_dev_rep1
| 閾値 | Recall_human | Recall_all | FPR_clear | FPR_boundary | FPR_hardneg | Flag(unit,sent,type) | Flag固有文 |
|---|---|---|---|---|---|---|---|
| 0.00 | - | 5/7 (71%, CI 36%-92%) | - | - | - | 5 | 5 |
| 0.50 | - | 4/7 (57%, CI 25%-84%) | - | - | - | 4 | 4 |
| 0.90 | - | 4/7 (57%, CI 25%-84%) | - | - | - | 4 | 4 |
### confidence閾値曲線: d1full_gpt-6.1-sol_synthetic_dev_gate
| 閾値 | Recall_human | Recall_all | FPR_clear | FPR_boundary | FPR_hardneg | Flag(unit,sent,type) | Flag固有文 |
|---|---|---|---|---|---|---|---|
| 0.00 | - | 5/7 (71%, CI 36%-92%) | - | - | - | 8 | 5 |
| 0.50 | - | 5/7 (71%, CI 36%-92%) | - | - | - | 8 | 5 |
| 0.90 | - | 4/7 (57%, CI 25%-84%) | - | - | - | 7 | 4 |
