| case | Lv | 方針/leaf | シナリオ | TTS | 待機(秒) | LR | HRQ行 | Style列 | 最終 | 方針Gate(M3/Y/Z、当該seg) | 共有Audio Gate(Assemble、当該seg) | 判定 | 実費(円) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| X-Adv-1 | b1b | EN_LR_ADV/L1 | E-S1 | 3 | 180 | 0 | 0 | AAB | OK | BLOCKなし | PASS | PASS | 0.759 |
| X-Adv-2 | b1b | EN_LR_ADV/L1 | E-S2a | 4 | 180 | 1 | 0 | AABA | OK | BLOCKなし | PASS | PASS | 1.304 |
| X-Adv-3c | b1b | EN_LR_ADV/L1 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | BLOCKなし | BLOCK(comment_1=STOPPED) | PASS | 2.021 |
| X-Adv-4 | b1b | EN_LR_ADV/L1 | E-S7 | 3 | 180 | 1 | 1 | AAB | STOPPED | BLOCKなし | BLOCK(comment_1=STOPPED) | PASS | 0.973 |
| X-Adv-6 | b1b | EN_LR_ADV/L2 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | BLOCKなし | BLOCK(in_one_line=STOPPED) | PASS | 1.789 |
| X-Adv-7 | b1b | KP_EXPL/L5 | E-S1 | 3 | 180 | 0 | 0 | A,A,B[MINIMAL_INSTRUCTION_PREFIX] | OK | BLOCK(kp1_explanation:FINAL_STYLE_SHA_MISMATCH_NO_HINT) | PASS | PASS | 0.684 |
| X-Adv-8 | b1b | KP_EXPL/L5 | E-S3 | 3 | 180 | 0 | 1 | A,A,B[MINIMAL_INSTRUCTION_PREFIX] | STOPPED | BLOCK(kp1_explanation:KP_EXPLANATION_STATUS_NOT_OK+FINAL_STYLE_SHA_MISMATCH_NO_HINT) | BLOCK(kp1_explanation=STOPPED) | PASS | 0.695 |
| X-Adv-9 | b1b | KP_EXPL/L5 | E-X5 | 1 | - | 0 | 0 | A[MINIMAL_INSTRUCTION_PREFIX] | OK | BLOCK(kp1_explanation:STYLE_BASE_SHA_MISMATCH_OR_MISSING+FINAL_STYLE_SHA_MISMATCH_NO_HINT) | PASS | PASS | 0.413 |
| X-Adv-10 | b1b | KP_EN/L6 | E-S4 | 3 | 180 | 0 | 0 | A,A,B[ENGLISH_LOCK] | OK | BLOCKなし WARN(KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2) | PASS | PASS | 0.324 |
| X-Adv-11 | b1b | KP_EN/L6 | E-S4 | 4 | 180 | 0 | 1 | A,A,B[ENGLISH_LOCK],B[ENGLISH_LOCK] | STOPPED | BLOCK(kp1_english:KP_EN_STATUS_NOT_OK) WARN(KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2) | BLOCK(kp1_english=STOPPED) | PASS | 0.414 |
| X-Adv-12 | b1b | EN_LR_ADV/L1 | E-S6 | 3 | 60+0 | 0 | 0 | A | OK | BLOCKなし | PASS | PASS | 0.746 |
| X-Adv-13 | b1b | EN_LR_ADV/L1 | E-N | 1 | - | 0 | 0 | A | OK | BLOCKなし | PASS | PASS | 0.36 |
| X-Adv-14 | b1b | EN_LR_ADV/L1 | E-S1(Opus4-c b: Voice=Charon) | 3 | 180 | 1 | 1 | AAB | STOPPED | BLOCK(preview:FINAL_STYLE_RECORD_MISSING+PREVIEW_STYLE_PREFIX_NOT_E1_PREFIXED) | BLOCK(preview=STOPPED) | DEVIATION_NATURAL | 1.607 |
| X-Adv-14b | b1b | EN_LR_ADV/L1 | E-S1(Opus4-c b: Voice=Charon・再実行) | 3 | 180 | 0 | 0 | AAB | OK | BLOCK(preview:FINAL_STYLE_SHA_MISMATCH_NO_HINT+PREVIEW_STYLE_PREFIX_NOT_E1_PREFIXED+PREVIEW_MINIMAL_FALLBACK) | PASS | PASS | 1.672 |
| X-Adv-15 | b1b | EN_LR_ADV/L1 | E-S0(②PASS・待機なし) | 2 | - | 0 | 0 | AA | OK | BLOCKなし | PASS | PASS | 0.343 |
| X-Adv-16 | b1b | EN_LR_ADV/L2 | E-S6(R-5: LR block内kill) | 6 | 255+12 | 0 | 0 | A | OK | BLOCKなし | PASS | PASS | 1.851 |
| X-Std-1 | a2 | EN_LR_STD/L3 | E-S1 | 3 | 180 | 1 | 1 | AAB | STOPPED | BLOCKなし | BLOCK(topic_intro=STOPPED) | DEVIATION_NATURAL | 0.767 |
| X-Std-1b | a2 | EN_LR_STD/L3 | E-S1 | 3 | 180 | 0 | 0 | AAB | OK | BLOCKなし | PASS | PASS | 0.471 |
| X-Std-2 | a2 | EN_LR_STD/L3 | E-S2a | 4 | 180 | 1 | 0 | AABA | OK | BLOCKなし | PASS | PASS | 1.142 |
| X-Std-3 | a2 | EN_LR_STD/L3 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | BLOCKなし | BLOCK(topic_intro=STOPPED) | PASS | 2.203 |
| X-Std-4 | a2 | EN_LR_STD/L4 | E-S1 | 3 | 180 | 0 | 0 | AAB | OK | BLOCKなし | PASS | PASS | 0.804 |
| X-Std-5 | a2 | EN_LR_STD/L4 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | BLOCKなし | BLOCK(in_one_line=STOPPED) | PASS | 1.868 |
| X-Std-6 | a2 | JA_STD/L7 | E-S1 | 3 | 180 | 0 | 0 | AAB | OK | BLOCKなし | PASS | PASS | 0.238 |
| X-Std-7 | a2 | JA_STD/L7 | E-S3 | 3 | 180 | 0 | 0 | AAB | STOPPED | BLOCKなし | BLOCK(japanese_title=STOPPED) | PASS | 0.237 |
| X-Std-8 | a2 | KP_EN/L6 | E-S4 | 3 | 180 | 0 | 0 | A,A,B[ENGLISH_LOCK] | OK | BLOCKなし WARN(KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2) | PASS | PASS | 0.393 |
| X-Std-9 | a2 | KP_EN/L6 | E-S4 | 4 | 180 | 0 | 1 | A,A,B[ENGLISH_LOCK],B[ENGLISH_LOCK] | STOPPED | BLOCK(kp1_english:KP_EN_STATUS_NOT_OK) WARN(KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2) | BLOCK(kp1_english=STOPPED) | PASS | 0.523 |
| X-Std-10 | a2 | EN_LR_STD/L3 | E-S6 | 3 | 60+30 | 1 | 1 | A | STOPPED | BLOCKなし | BLOCK(topic_intro=STOPPED) | DEVIATION_NATURAL | 0.744 |
| X-Std-11 | a2 | EN_LR_STD+JA_STD/L3+L7 | E-N | 1 | - | 0 | 0 | A | OK | BLOCKなし | PASS | PASS | 0.265 |
| X-Std-12 | a2 | EN_LR_STD/L4 | E-C1(Opus4-c a) | 2 | - | 0 | 0 | AA | OK | BLOCKなし 減速Gate当該chunk違反なし | PASS | PASS | 1.175 |
