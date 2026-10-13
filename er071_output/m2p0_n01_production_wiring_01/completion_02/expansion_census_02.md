# expansion_census_02 (OF-X3、API 0円)

対象: er*_output配下で`source_reference_contract`を持つitem(候補ID方式)を含むJSON 304ファイル。ユニーク(source_span, source_sentence) 141件。
拡張が起きた件数: **16件** / 141。拡張はcanonicalization入力・Rule7判定にのみ使い、選定結果source_spanは不変。左端ガード(OF-X1)あり。

| # | 元source_span | 拡張後 | 出現ファイル数 | 代表ファイル | role |
|---|---|---|---|---|---|
| 1 | `Hold on` | `Hold on before` | 81 | er019_output\family_x_audio_production_wiring_01\coffee_prices__run_m2p0_n01_01\b1b\key_phrases\keywords_canonicalized.json | important |
| 2 | `asking for` | `asking for another` | 5 | er073_output\family_z_kp_db_hybrid_m2p0_migration_01\runs\melos_adv\dbh_m2p0_run3\key_phrases\keywords_canonicalized.json | important |
| 3 | `based on` | `based on interviews` | 52 | er019_output\family_x_audio_production_wiring_01\coffee_prices__run_m2p0_n01_01\a2\key_phrases\keywords_runtime_metadata.json | important |
| 4 | `bring in` | `bring in a human` | 5 | er019_output\family_x_audio_production_wiring_01\meta__run_regen_01\a2\key_phrases\keywords_canonicalized.json | important |
| 5 | `comes with` | `comes with costs` | 65 | er019_output\family_x_audio_production_wiring_01\coffee_prices__run_v5_ms_01\b1b\key_phrases\keywords_canonicalized.json | important |
| 6 | `end of` | `end of the call` | 4 | er064_output\kp_no_way_fix_01\run_summary_02_stage1.json | important |
| 7 | `fell into` | `fell into the cold` | 12 | er030_output\family_x_kp_source_reference_contract_evidence_01\all_articles_summary.json |  |
| 8 | `instead of` | `instead of AI` | 2 | er064_output\kp_integrated_opt_01\round1\stage3_summary_r1.json | important |
| 9 | `instead of` | `instead of AI` | 2 | er064_output\kp_no_way_fix_01\run_summary_02_stage1.json | important |
| 10 | `passing through` | `passing through the Strait` | 5 | er035_output\kp_4plus1_evidence_01\hormuz_b1b\key_phrases\keywords_canonicalized.json | important |
| 11 | `rang through` | `rang through the hall` | 24 | er073_output\family_z_kp_db_hybrid_m2p0_migration_01\runs\melos_adv\dbh_m2p0_run1\key_phrases\keywords_canonicalized.json | important |
| 12 | `run on` | `run on different` | 30 | er019_output\coffee_prices\run_p8_wiring_01\a2\key_phrases\keywords_canonicalized.json | important |
| 13 | `speaks for` | `speaks for us` | 20 | er030_output\family_x_kp_source_reference_contract_evidence_01\meta_a2\key_phrases\keywords_canonicalized.json |  |
| 14 | `stayed on` | `stayed on the road` | 7 | er030_output\family_x_kp_source_reference_contract_evidence_01\all_articles_summary.json |  |
| 15 | `take for` | `take for bean` | 2 | er064_output\kp_integrated_opt_01\round1\stage2_summary_r1.json | important |
| 16 | `talking to` | `talking to AI` | 2 | er064_output\kp_no_way_fix_01\run_summary_02_stage1.json | important |

## 文(前後確認用)

1. `Hold on` -> `Hold on before`: Hold on before putting the two figures in the ring
2. `asking for` -> `asking for another`: His friend had trusted him without asking for another promise
3. `based on` -> `based on interviews`: However, "about nine months" is an estimate based on interviews
4. `bring in` -> `bring in a human`: So, is it wrong by itself to bring in a human helper
5. `comes with` -> `comes with costs`: And a cup at a cafe comes with costs besides the beans
6. `end of` -> `end of the call`: They were enjoying the convenience of AI, only to find a human on the other end of the call without realizing it
7. `fell into` -> `fell into the cold`: Melos fell into the cold river and nearly disappeared under the water
8. `instead of` -> `instead of AI`: But in some tests of its calling feature, trained human contract workers made the calls instead of AI
9. `instead of` -> `instead of AI`: However, in some tests of its calling feature, trained human contract workers made the calls instead of AI
10. `passing through` -> `passing through the Strait`: At 10:16 a.m., Trump posted that the United States would seek a 20% charge on all cargo passing through the Strait of Hormuz
11. `rang through` -> `rang through the hall`: Melos's voice rang through the hall
12. `run on` -> `run on different`: They are on different stages and run on different clocks
13. `speaks for` -> `speaks for us`: Before AI speaks for us, we need to know whether the voice belongs to AI or a person
14. `stayed on` -> `stayed on the road`: He smiled for his sister, but his eyes stayed on the road
15. `take for` -> `take for bean`: So, how long does it take for bean prices to reach a price tag
16. `talking to` -> `talking to AI`: And if this was not properly explained, users had no way to know whether they were talking to AI or a person
