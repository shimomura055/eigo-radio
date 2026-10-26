| case | Lv | 方針/leaf | シナリオ | TTS | 待機(秒) | LR | HRQ行 | Style列 | 最終 | 方針Gate(M3/Y/Z、当該seg) | 共有Audio Gate(Assemble、当該seg) | 判定 | 実費(円) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Z-Adv-1 | b1b | EN_LR_ADV/L2 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | Z Gate BLOCK(FamilyZTtsResultsIncompleteStop:full_story_part1_c14=STOPPED) | BLOCK(full_story_part1_c14=STOPPED) | PASS | 1.065 |
| Z-Adv-2 | b1b | Z_DLG_CTX/L8 | E-S1(L8 ctx,減速後NG) | 3 | 180 | 0 | 0 |  | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 1.22 |
| Z-Adv-3 | b1b | Z_DLG_CTX/L8 | E-S3(L8 ctx) | 3 | 180 | 0 | 0 |  | STOPPED | Z Gate BLOCK(FamilyZTtsResultsIncompleteStop:full_story_part1_c15=STOPPED) | BLOCK(full_story_part1_c15=STOPPED) | PASS | 1.282 |
| Z-Adv-3b | b1b | Z_DLG_CTX/L8 | E-S3(L8 ctx・減速後NG×3でHRQ) | 3 | 180 | 0 | 1 |  | STOPPED | Z Gate BLOCK(FamilyZTtsResultsIncompleteStop:full_story_part1_c15=STOPPED) | BLOCK(full_story_part1_c15=STOPPED) | PASS | 1.512 |
| Z-Adv-4 | b1b | EN_LR_ADV/L1 | E-S2a(U-06) | 4 | 180 | 1 | 0 | AABA | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.633 |
| Z-Adv-5 | b1b | KP_EXPL/L5 | E-S1 | 3 | 180 | 0 | 0 | A,A,B[MINIMAL_INSTRUCTION_PREFIX] | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.464 |
| Z-Adv-6 | b1b | KP_EN/L6 | E-S4 | 3 | 180 | 0 | 0 | A,A,B[ENGLISH_LOCK] | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.452 |
| Z-Adv-8 | b1b | EN_LR_ADV/L1 | E-N | 1 | - | 0 | 0 | A | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.218 |
| Z-Std-1 | a2 | EN_LR_STD/L4 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | Z Gate BLOCK(FamilyZTtsResultsIncompleteStop:full_story_part1_c14=STOPPED) | BLOCK(full_story_part1_c14=STOPPED) | PASS | 2.499 |
| Z-Std-2 | a2 | Z_DLG_CTX/L8 | E-S1(L8 ctx) | 3 | 180 | 0 | 0 |  | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 1.513 |
| Z-Std-4 | a2 | JA_STD/L7 | E-S1 | 3 | 180 | 0 | 0 | AAB | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.199 |
| Z-Std-5 | a2 | KP_EN/L6 | E-S4 | 3 | 180 | 0 | 0 | A,A,B[ENGLISH_LOCK] | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.377 |
| Z-Std-6 | a2 | EN_LR_STD/L3 | E-S2a(U-06) | 4 | 180 | 1 | 0 | AABA | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.702 |
| Z-Std-7 | a2 | EN_LR_STD+JA_STD/L3+L7 | E-N | 1 | - | 0 | 0 | A | OK | Z Gate PASS(m2_complete/audio_gate) | PASS | PASS | 0.133 |
| Z-Std-8 | a2 | EN_LR_STD/L3 | E-STOP | 2 | - | 0 | 0 | AA | None | Z Gate BLOCK(FamilyZTtsResultsIncompleteStop:結果ファイル未生成) | PASS | PASS | 0.169 |
