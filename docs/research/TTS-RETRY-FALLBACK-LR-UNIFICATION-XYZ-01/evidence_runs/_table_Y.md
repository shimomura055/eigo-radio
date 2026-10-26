| case | Lv | 方針/leaf | シナリオ | TTS | 待機(秒) | LR | HRQ行 | Style列 | 最終 | 方針Gate(M3/Y/Z、当該seg) | 共有Audio Gate(Assemble、当該seg) | 判定 | 実費(円) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Y-Adv-1 | b1b | EN_LR_ADV/L1 | E-S2a | 4 | 180 | 1 | 0 | AABA | OK | BLOCKなし | PASS | PASS | 1.152 |
| Y-Adv-2 | b1b | KP_EXPL/L5 | E-S1 | 3 | 180 | 0 | 0 | A,A,B[MINIMAL_INSTRUCTION_PREFIX] | OK | BLOCKなし | PASS | PASS | 0.409 |
| Y-Adv-3 | b1b | KP_EN/L6 | E-S4 | 3 | 180 | 0 | 0 | A,A,B[ENGLISH_LOCK] | OK | BLOCKなし | PASS | PASS | 0.411 |
| Y-Adv-4 | b1b | EN_LR_ADV/L2 | E-S2a+YGate | 3 | 180 | 1 | 1 | AAB | STOPPED | BLOCK(y_voice_1:FINAL_STYLE_RECORD_MISSING+ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED) | BLOCK(y_voice_1=STOPPED) | DEVIATION_NATURAL | 7.058 |
| Y-Adv-4b | b1b | EN_LR_ADV/L2 | E-S2a+YGate | 4 | 180 | 1 | 0 | AABA | OK | BLOCK(y_voice_1:LOCAL_REWRITE_RECOVERY) | PASS | PASS | 8.558 |
| Y-Adv-5 | b1b | EN_LR_ADV/L1 | E-N | 1 | - | 0 | 0 | A | OK | BLOCKなし | PASS | PASS | 0.282 |
| Y-Std-1 | a2 | EN_LR_STD/L3 | E-S2b | 6 | 180+180 | 1 | 1 | AABAAB | STOPPED | BLOCKなし | BLOCK(topic_intro=STOPPED) | PASS | 1.323 |
| Y-Std-2 | a2 | JA_STD/L7 | E-S1 | 3 | 180 | 0 | 1 | AAB | STOPPED | BLOCKなし | BLOCK(japanese_title=STOPPED) | DEVIATION_NATURAL | 0.325 |
| Y-Std-2b | a2 | JA_STD/L7 | E-S1 | 3 | 180 | 0 | 0 | AAB | OK | BLOCKなし | PASS | PASS | 0.494 |
| Y-Std-3 | a2 | KP_EN/L6 | E-S4 | 3 | 180 | 0 | 0 | A,A,B[ENGLISH_LOCK] | OK | BLOCKなし | PASS | PASS | 0.318 |
| Y-Std-4 | a2 | EN_LR_STD/L4 | E-S1+YGate | 3 | 180 | 1 | 1 | AAB | STOPPED | BLOCK(y_voice_1:FINAL_STYLE_SHA_MISMATCH_NO_HINT+STD_FALLBACK_USED_OR_UNKNOWN;y_voice_1:Y_MISSING_MANDATORY_A2_SLOWDOWN) | BLOCK(y_voice_1=STOPPED) | DEVIATION_NATURAL | 4.827 |
| Y-Std-4b | a2 | EN_LR_STD/L4 | E-S1+YGate | 3 | 180 | 0 | 0 | AAB | OK | BLOCK(y_voice_1:FINAL_STYLE_SHA_MISMATCH_NO_HINT+STD_FALLBACK_USED_OR_UNKNOWN) | PASS | PASS | 6.539 |
| Y-Std-5 | a2 | EN_LR_STD+JA_STD/L3+L7 | E-N | 1 | - | 0 | 0 | A | OK | BLOCKなし | PASS | PASS | 0.218 |
| Y-Std-6 | a2 | EN_LR_STD/L3 | E-STOP | 2 | - | 0 | 0 | AA | None | 結果未保存(STOP中断のためGate対象なし) | PASS | PASS | 0.255 |
