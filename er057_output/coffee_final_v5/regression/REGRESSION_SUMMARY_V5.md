# REGRESSION_SUMMARY_V5 (2026-10-12、実行層が実際に実行した結果。APIコール0)
`.venv/Scripts/python.exe -m unittest <module>`
- er019_family_x_style_profile_01_test_01: 49件OK(既存32+V5新17)
- er019_family_x_audio_production_runner_01_test_01: 49 OK / er019_family_x_flash_lite_role_style_wiring_02: 8 OK / er019_family_x_ja_recheck_retry_01: 4 OK / er019_family_x_kp_structure_wiring_01: 36 OK / er019_family_x_new_structure_wiring_01: OK / er019_family_x_opus_l2_fixes_01: 24 OK / er019_family_x_pointless_01: 10 OK / er019_family_x_variable_role_style_wiring_01: OK / er019_family_x_b3_production_wiring_01: 30 OK / er019_family_x_entertainment_production_runner_01: 20 OK / er019_family_x_section_segmentation_trial_01: 15 OK / er019_family_x_concreteness_an3_t0_production_wiring_01: 18 OK / er019_family_x_ja_writer_o_r1_r2_01: 7 OK / er019_writer_run_summary_reconstruction_01: 8 OK
- er003_v1_n3_01_standard_a2_generate_test_01: 27 OK / er003_v1_n3_01_advanced_adaptation_generate_test_01: 28 OK
- er021_en_asr_semantic_equivalence_production_wiring_01: 62 OK
- er026_post_slowdown_cascade_rescue_01_test_01: 11 OK(本日 commit 808685df の減速後cascade再配線。今回の対象roleは減速対象外[Std JA Preview/Commentは減速なし、Full Storyはv4音声流用]なので挙動変化なし)
- er053_c3_audio_guard: 33 OK / er053_c5_review_fixes: 10 OK / er058_asr_tts_prodfix: 27 OK / er063_family_z_audio_01: 47 OK / er030 key_phrase_db_hybrid family_x wiring: 32 OK
- er025_pronunciation_resolution_phase3_b1b_en_wiring_01: 29件中1件ERROR(`test_b1_segments_pass_enable_pronunciation_resolver_true`、`KeyError: 'part2'`=テスト固定データ(parts.json)不備。本委任の変更箇所ではなく、runnerの本文3分割ループの既存コード。ROOT-CAUSE-01報告でも「HEADでも既存エラー」と記録済み)
- er003 assemble専用の単体testは存在せず(assemble本体は無変更)、runnerのstage_assemble統合は style_profile `AssembleIntegrationTests` で確認。
