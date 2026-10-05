# Stage 1 coverage_union fixture dry-run(委任_06、¥0・決定論・LLM呼び出しなし)

- instance数: 29 / 正式gold(expected=BLOCKING): 6 claim -> 単位IDへ対応: **6/6**
- neg5の関係単位(「continued on July 14.」+「So the flashy 20% plan...」): **有** ['R:L1+L2']
- 判定対象単位数/記事: 平均20.4(最小1、最大38)
- 関係単位: 計6件(6記事) / 同文グループ: 計0件(0記事)
- 全単位のoffsetが本文と逐語一致: True

## 正式gold 6 claim -> 単位ID

| instance | sub_id | fact | 対応単位ID | 関係単位(当該文) | mapped |
|---|---|---|---|---|---|
| safety_A2A3 | A2A3-0 | HF-003 | S3.2 | - | True |
| safety_A4 | A4-0 | MUSE-HC-006 | S2.1 | - | True |
| safety_A5 | A5-0 | MUSE-HC-012 | S8.2 | - | True |
| bgroup_B3 | B3 | HF-007 | L1 | - | True |
| bgroup_B4 | B4-a | MUSE-HC-002 | S4.3 | - | True |
| neg5_hormuz_div_a2 | B3-same@neg5 | HF-007 | L2 | R:L1+L2 | True |

## instance別

| instance | group | 文字数 | 判定単位 | 関係単位 | 同文G | fact数 | R3 prompt字 | R5 prompt字 |
|---|---|---|---|---|---|---|---|---|
| safety_er009_changed_number | safety | 163 | 1 | 0 | 0 | 17 | 9970 | 9661 |
| safety_er009_changed_actor | safety | 185 | 1 | 0 | 0 | 17 | 9992 | 9683 |
| safety_er009_changed_scope | safety | 219 | 1 | 0 | 0 | 17 | 10026 | 9717 |
| safety_er009_changed_causality | safety | 179 | 1 | 0 | 0 | 17 | 9986 | 9677 |
| safety_er009_changed_certainty | safety | 108 | 1 | 0 | 0 | 17 | 9915 | 9606 |
| safety_er009_changed_negation | safety | 148 | 1 | 0 | 0 | 17 | 9955 | 9646 |
| safety_er009_changed_comparison | safety | 146 | 1 | 0 | 0 | 17 | 9953 | 9644 |
| safety_er009_changed_time | safety | 185 | 1 | 0 | 0 | 17 | 9992 | 9683 |
| safety_er009_unsupported_new_claim | safety | 149 | 1 | 0 | 0 | 17 | 9956 | 9647 |
| safety_A2A3 | safety | 2183 | 22 | 0 | 0 | 12 | 9109 | 8659 |
| safety_A4 | safety | 1744 | 27 | 1 | 0 | 15 | 10451 | 10063 |
| safety_A5 | safety | 2029 | 30 | 0 | 0 | 15 | 10621 | 10212 |
| bgroup_B1 | b_group | 773 | 21 | 0 | 0 | 12 | 7732 | 7279 |
| bgroup_B2_hormuz | b_group | 2193 | 28 | 1 | 0 | 12 | 9438 | 8935 |
| bgroup_B3 | b_group | 1972 | 27 | 0 | 0 | 12 | 8977 | 8497 |
| bgroup_B4 | b_group | 1677 | 26 | 0 | 0 | 15 | 10176 | 9801 |
| meta_run03_standard | meta | 2054 | 37 | 0 | 0 | 15 | 10737 | 10292 |
| meta_run03_advanced | meta | 2199 | 28 | 0 | 0 | 15 | 10747 | 10356 |
| hormuz_run03_advanced | hormuz | 2198 | 24 | 0 | 0 | 12 | 9181 | 8715 |
| hormuz_run03_standard | hormuz | 2058 | 34 | 1 | 0 | 12 | 9353 | 8820 |
| hormuz_run01_advanced | hormuz | 2223 | 25 | 0 | 0 | 12 | 9221 | 8749 |
| hormuz_run02_advanced | hormuz | 2193 | 28 | 1 | 0 | 12 | 9438 | 8935 |
| neg1_meta_b3prod_a2 | negative | 2139 | 38 | 0 | 0 | 15 | 10862 | 10405 |
| neg2_meta_refresh_a2 | negative | 2098 | 33 | 0 | 0 | 15 | 10721 | 10300 |
| neg3_hormuz_prodrunner_b1b | negative | 1822 | 20 | 0 | 0 | 12 | 8718 | 8280 |
| neg4_smallbag_div_a2 | negative | 1783 | 36 | 0 | 0 | 17 | 16311 | 15783 |
| neg5_hormuz_div_a2 | negative | 2080 | 38 | 1 | 0 | 12 | 9399 | 8856 |
| neg6_smallbag_div_b1b | negative | 1830 | 26 | 0 | 0 | 17 | 16204 | 15736 |
| neg7_meta_prodrunner_b1b | negative | 2148 | 34 | 1 | 0 | 15 | 10963 | 10533 |
