| 検出器 | units(重大/人間確認/非重大) | Recall_human(主) | Recall_all(副) | FPR_clear | FPR_boundary | FPR_hardneg | Flag(unit,sent,type)/unit | Flag固有文/unit | Rollback | 方向反転(別Fact) | 費用JPY |
|---|---|---|---|---|---|---|---|---|---|---|---|
| d0_none_synthetic_dev | 7(7/0/0) | - | 2/7 (29%, CI 8%-64%) | - | - | - | 0.29 | 0.29 | 1/2 | 0/1 | 0.00 |
| d1full_gpt-6.1-sol_synthetic_dev_gate | 7(7/0/0) | - | 5/7 (71%, CI 36%-92%) | - | - | - | 1.14 | 0.71 | 2/2 | 1/1 | 26.07 |
| d2_gpt-6.1-sol_synthetic_dev_rep1 | 7(7/0/0) | - | 5/7 (71%, CI 36%-92%) | - | - | - | 0.71 | 0.71 | 2/2 | 1/1 | 6.36 |
| d2_gpt-6.1-sol_synthetic_dev_rep2 | 7(7/0/0) | - | 5/7 (71%, CI 36%-92%) | - | - | - | 0.71 | 0.71 | 2/2 | 1/1 | 6.35 |
| d3_d0rb_d1gate_synthetic_dev_gpt-6.1-sol_synthetic_dev | 7(7/0/0) | - | 5/7 (71%, CI 36%-92%) | - | - | - | 1.14 | 0.71 | 2/2 | 1/1 | 26.07 |
| d3_d0rb_d2r1_synthetic_dev_gpt-6.1-sol_synthetic_dev | 7(7/0/0) | - | 5/7 (71%, CI 36%-92%) | - | - | - | 0.71 | 0.71 | 2/2 | 1/1 | 6.36 |
| d3_all_r1_synthetic_dev_gpt-6.1-sol_synthetic_dev | 7(7/0/0) | - | 5/7 (71%, CI 36%-92%) | - | - | - | 1.57 | 0.71 | 2/2 | 1/1 | 32.43 |

見逃し重大 / 誤Flag(clear・boundary・hardneg):
- d0_none_synthetic_dev: 見逃し=S-02,S-08,S-09,S-10,S-13 / 誤Flag clear=- boundary=- hardneg=-
- d1full_gpt-6.1-sol_synthetic_dev_gate: 見逃し=S-02,S-08 / 誤Flag clear=- boundary=- hardneg=-
- d2_gpt-6.1-sol_synthetic_dev_rep1: 見逃し=S-02,S-08 / 誤Flag clear=- boundary=- hardneg=-
- d2_gpt-6.1-sol_synthetic_dev_rep2: 見逃し=S-02,S-08 / 誤Flag clear=- boundary=- hardneg=-
- d3_d0rb_d1gate_synthetic_dev_gpt-6.1-sol_synthetic_dev: 見逃し=S-02,S-08 / 誤Flag clear=- boundary=- hardneg=-
- d3_d0rb_d2r1_synthetic_dev_gpt-6.1-sol_synthetic_dev: 見逃し=S-02,S-08 / 誤Flag clear=- boundary=- hardneg=-
- d3_all_r1_synthetic_dev_gpt-6.1-sol_synthetic_dev: 見逃し=S-02,S-08 / 誤Flag clear=- boundary=- hardneg=-

### 既知事故別(拾った/件数)
| 検出器 | Rollback方向反転 |
|---|---|
| d0_none_synthetic_dev | 1/2 |
| d1full_gpt-6.1-sol_synthetic_dev_gate | 2/2 |
| d2_gpt-6.1-sol_synthetic_dev_rep1 | 2/2 |
| d2_gpt-6.1-sol_synthetic_dev_rep2 | 2/2 |
| d3_d0rb_d1gate_synthetic_dev_gpt-6.1-sol_synthetic_dev | 2/2 |
| d3_d0rb_d2r1_synthetic_dev_gpt-6.1-sol_synthetic_dev | 2/2 |
| d3_all_r1_synthetic_dev_gpt-6.1-sol_synthetic_dev | 2/2 |

### タイプ別Recall(重大ケースのaccident_type別、hit/n)
| 検出器 | rollback方向反転 | 数量時系列 | 方向反転(別Fact) |
|---|---|---|---|
| d0_none_synthetic_dev | 1/2 | 1/4 | 0/1 |
| d1full_gpt-6.1-sol_synthetic_dev_gate | 2/2 | 2/4 | 1/1 |
| d2_gpt-6.1-sol_synthetic_dev_rep1 | 2/2 | 2/4 | 1/1 |
| d2_gpt-6.1-sol_synthetic_dev_rep2 | 2/2 | 2/4 | 1/1 |
| d3_d0rb_d1gate_synthetic_dev_gpt-6.1-sol_synthetic_dev | 2/2 | 2/4 | 1/1 |
| d3_d0rb_d2r1_synthetic_dev_gpt-6.1-sol_synthetic_dev | 2/2 | 2/4 | 1/1 |
| d3_all_r1_synthetic_dev_gpt-6.1-sol_synthetic_dev | 2/2 | 2/4 | 1/1 |
