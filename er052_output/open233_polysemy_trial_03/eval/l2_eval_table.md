| pattern | theme | recall | extra | cand | attach | rate | avg_len | max_len | empty_sq | rev_true/quote_mismatch | warn | cost | rejected(reasons) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B_twostage | meta | 2/2 | 1 | 3 | 3/15 | 0.20 | 69.67 | 77 | 0 | 3/0 | 0 | 3.14 | 0 {} |
| B_twostage | hormuz | 2/2 | 9 | 11 | 11/12 | 0.92 | 74.91 | 91 | 0 | 11/0 | 0 | 4.96 | 0 {} |
| B_twostage | space_weapons | 0/4 | 0 | 8 | 0/22 | 0.00 | 0.00 | 0 | 0 | 8/0 | 0 | 4.62 | 8 {"bad_prefix": 8} |
| B_twostage | sewer | 2/3 | 3 | 5 | 5/20 | 0.25 | 70.60 | 84 | 0 | 5/0 | 0 | 4.47 | 0 {} |
| B_twostage | ai_control | 0/3 | 0 | 10 | 0/16 | 0.00 | 0.00 | 0 | 0 | 10/0 | 0 | 5.28 | 10 {"self_check_false": 10} |
| B_twostage | A02 | 2/2 | 8 | 11 | 10/19 | 0.53 | 70.20 | 83 | 0 | 11/0 | 0 | 4.35 | 0 {} |
| B_twostage | small_bag | 0/0 | 0 | 0 | 0/17 | 0.00 | 0.00 | 0 | 0 | 0/0 | 0 | 1.07 | 0 {} |
| B_twostage | ALL(core5) | 6/14 | 13 | 37 | 19/85 | 0.22 | 72.95 | 91 | 0 | 37/0 | 0 | 22.46 | 18 {"bad_prefix": 8, "self_check_false": 10} |
<!-- B_twostage tolerant_prefix: rescued_notes=8 rescued_target_hits=3 ; quote_mismatch/reversible_true=0/37 -->
<!-- B_twostage attach_distribution: {"meta": [3, 15], "hormuz": [11, 12], "space_weapons": [0, 22], "sewer": [5, 20], "ai_control": [0, 16], "A02": [10, 19], "small_bag": [0, 17]} -->
| B2_twostage_hint | meta | 2/2 | 6 | 8 | 8/15 | 0.53 | 65.88 | 78 | 0 | 8/0 | 0 | 3.72 | 0 {} |
| B2_twostage_hint | hormuz | 1/2 | 4 | 5 | 5/12 | 0.42 | 72.40 | 83 | 0 | 6/1 | 0 | 3.88 | 0 {} |
| B2_twostage_hint | space_weapons | 3/4 | 6 | 9 | 9/22 | 0.41 | 64.44 | 75 | 0 | 9/0 | 0 | 4.20 | 0 {} |
| B2_twostage_hint | sewer | 3/3 | 3 | 6 | 6/20 | 0.30 | 79.17 | 88 | 0 | 6/0 | 0 | 4.05 | 0 {} |
| B2_twostage_hint | ai_control | 1/3 | 7 | 10 | 8/16 | 0.50 | 73.25 | 88 | 0 | 10/0 | 0 | 3.84 | 2 {"too_long": 2} |
| B2_twostage_hint | A02 | 0/2 | 4 | 4 | 4/19 | 0.21 | 72.50 | 78 | 0 | 4/0 | 0 | 5.28 | 0 {} |
| B2_twostage_hint | small_bag | 0/0 | 0 | 0 | 0/17 | 0.00 | 0.00 | 0 | 0 | 0/0 | 0 | 1.54 | 0 {} |
| B2_twostage_hint | ALL(core5) | 10/14 | 26 | 38 | 36/85 | 0.42 | 70.28 | 88 | 0 | 39/1 | 0 | 19.69 | 2 {"too_long": 2} |
<!-- B2_twostage_hint tolerant_prefix: rescued_notes=0 rescued_target_hits=0 ; quote_mismatch/reversible_true=1/39 -->
<!-- B2_twostage_hint attach_distribution: {"meta": [8, 15], "hormuz": [5, 12], "space_weapons": [9, 22], "sewer": [6, 20], "ai_control": [8, 16], "A02": [4, 19], "small_bag": [0, 17]} -->
| B2n_twostage_nohint | meta | 0/2 | 5 | 5 | 5/15 | 0.33 | 83.80 | 99 | 0 | 5/0 | 0 | 3.57 | 0 {} |
| B2n_twostage_nohint | hormuz | 0/2 | 1 | 2 | 1/12 | 0.08 | 89.00 | 89 | 0 | 2/0 | 0 | 1.76 | 1 {"too_long": 1} |
| B2n_twostage_nohint | space_weapons | 3/4 | 9 | 14 | 12/22 | 0.55 | 76.67 | 87 | 0 | 14/0 | 0 | 5.32 | 2 {"too_long": 2} |
| B2n_twostage_nohint | sewer | 2/3 | 4 | 6 | 6/20 | 0.30 | 72.83 | 82 | 0 | 6/0 | 0 | 3.63 | 0 {} |
| B2n_twostage_nohint | ai_control | 1/3 | 8 | 10 | 9/16 | 0.56 | 75.44 | 91 | 0 | 10/0 | 0 | 3.72 | 1 {"too_long": 1} |
| B2n_twostage_nohint | A02 | 0/2 | 4 | 4 | 4/19 | 0.21 | 78.50 | 90 | 0 | 4/0 | 2 | 4.11 | 0 {} |
| B2n_twostage_nohint | small_bag | 0/0 | 1 | 1 | 1/17 | 0.06 | 73.00 | 73 | 0 | 1/0 | 0 | 2.07 | 0 {} |
| B2n_twostage_nohint | ALL(core5) | 6/14 | 27 | 37 | 33/85 | 0.39 | 77.09 | 99 | 0 | 37/0 | 0 | 18.01 | 4 {"too_long": 4} |
<!-- B2n_twostage_nohint tolerant_prefix: rescued_notes=0 rescued_target_hits=0 ; quote_mismatch/reversible_true=0/37 -->
<!-- B2n_twostage_nohint attach_distribution: {"meta": [5, 15], "hormuz": [1, 12], "space_weapons": [12, 22], "sewer": [6, 20], "ai_control": [9, 16], "A02": [4, 19], "small_bag": [1, 17]} -->