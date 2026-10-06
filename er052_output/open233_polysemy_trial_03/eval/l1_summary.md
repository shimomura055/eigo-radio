| pattern | theme | recall | extra | cand | attach | rate | avg_len | max_len | empty_sq | rev_true/quote_mismatch | cost | rejected(reasons) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_onepass | meta | 2/2 | 1 | 3 | 3/15 | 0.20 | 47.33 | 53 | 0 | 3/0 | 1.74 | 0 {} |
| A_onepass | hormuz | 1/2 | 7 | 8 | 8/12 | 0.67 | 49.75 | 61 | 0 | 8/0 | 3.59 | 0 {} |
| A_onepass | space_weapons | 3/4 | 13 | 16 | 16/22 | 0.73 | 51.44 | 62 | 0 | 16/0 | 3.05 | 0 {} |
| A_onepass | sewer | 2/3 | 3 | 5 | 5/20 | 0.25 | 48.80 | 51 | 0 | 5/0 | 3.39 | 0 {} |
| A_onepass | ai_control | 0/3 | 3 | 3 | 3/16 | 0.19 | 57.00 | 61 | 0 | 3/0 | 2.23 | 0 {} |
| A_onepass | A02 | 2/2 | 7 | 9 | 9/19 | 0.47 | 50.44 | 58 | 0 | 9/0 | 3.27 | 0 {} |
| A_onepass | small_bag | 0/0 | 10 | 10 | 10/17 | 0.59 | 58.10 | 67 | 0 | 10/0 | 2.90 | 0 {} |
| A_onepass | ALL(core5) | 8/14 | 27 | 35 | 35/85 | 0.41 | 50.80 | 62 | 0 | 35/0 | 13.99 | 0 {} |
<!-- A_onepass tolerant_prefix: rescued_notes=0 rescued_target_hits=0 ; quote_mismatch/reversible_true=0/35 -->
<!-- A_onepass attach_distribution: {"meta": [3, 15], "hormuz": [8, 12], "space_weapons": [16, 22], "sewer": [5, 20], "ai_control": [3, 16], "A02": [9, 19], "small_bag": [10, 17]} -->
| B_twostage | meta | 2/2 | 1 | 3 | 3/15 | 0.20 | 69.67 | 77 | 0 | 3/0 | 3.14 | 0 {} |
| B_twostage | hormuz | 2/2 | 9 | 11 | 11/12 | 0.92 | 74.91 | 91 | 0 | 11/0 | 4.96 | 0 {} |
| B_twostage | space_weapons | 0/4 | 0 | 8 | 0/22 | 0.00 | 0.00 | 0 | 0 | 8/0 | 4.62 | 8 {"bad_prefix": 8} |
| B_twostage | sewer | 2/3 | 3 | 5 | 5/20 | 0.25 | 70.60 | 84 | 0 | 5/0 | 4.47 | 0 {} |
| B_twostage | ai_control | 0/3 | 0 | 10 | 0/16 | 0.00 | 0.00 | 0 | 0 | 10/0 | 5.28 | 10 {"self_check_false": 10} |
| B_twostage | A02 | 2/2 | 8 | 11 | 10/19 | 0.53 | 70.20 | 83 | 0 | 11/0 | 4.35 | 0 {} |
| B_twostage | small_bag | 0/0 | 0 | 0 | 0/17 | 0.00 | 0.00 | 0 | 0 | 0/0 | 1.07 | 0 {} |
| B_twostage | ALL(core5) | 6/14 | 13 | 37 | 19/85 | 0.22 | 72.95 | 91 | 0 | 37/0 | 22.46 | 18 {"bad_prefix": 8, "self_check_false": 10} |
<!-- B_twostage tolerant_prefix: rescued_notes=8 rescued_target_hits=3 ; quote_mismatch/reversible_true=0/37 -->
<!-- B_twostage attach_distribution: {"meta": [3, 15], "hormuz": [11, 12], "space_weapons": [0, 22], "sewer": [5, 20], "ai_control": [0, 16], "A02": [10, 19], "small_bag": [0, 17]} -->
| C_promote | meta | 1/2 | 1 | 2 | 2/15 | 0.13 | 63.00 | 71 | 0 | 0/0 | 1.76 | 0 {} |
| C_promote | hormuz | 2/2 | 6 | 8 | 8/12 | 0.67 | 60.62 | 71 | 0 | 0/0 | 1.79 | 0 {} |
| C_promote | space_weapons | 2/4 | 11 | 13 | 13/22 | 0.59 | 60.85 | 79 | 0 | 0/0 | 2.41 | 0 {} |
| C_promote | sewer | 3/3 | 2 | 5 | 5/20 | 0.25 | 61.80 | 68 | 0 | 0/0 | 2.09 | 0 {} |
| C_promote | ai_control | 1/3 | 8 | 9 | 9/16 | 0.56 | 63.67 | 75 | 0 | 0/0 | 2.19 | 0 {} |
| C_promote | A02 | 2/2 | 11 | 13 | 13/19 | 0.68 | 70.85 | 96 | 0 | 0/0 | 3.30 | 1 {"source_prohibition_not_verbatim": 1} |
| C_promote | small_bag | 0/0 | 1 | 1 | 1/17 | 0.06 | 79.00 | 79 | 0 | 0/0 | 1.49 | 0 {} |
| C_promote | ALL(core5) | 9/14 | 28 | 37 | 37/85 | 0.44 | 61.73 | 79 | 0 | 0/0 | 10.24 | 0 {} |
<!-- C_promote tolerant_prefix: rescued_notes=0 rescued_target_hits=0 ; quote_mismatch/reversible_true=0/0 -->
<!-- C_promote attach_distribution: {"meta": [2, 15], "hormuz": [8, 12], "space_weapons": [13, 22], "sewer": [5, 20], "ai_control": [9, 16], "A02": [13, 19], "small_bag": [1, 17]} -->