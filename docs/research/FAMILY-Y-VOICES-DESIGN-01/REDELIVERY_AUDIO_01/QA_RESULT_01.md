# QA_RESULT_01 (委任_27: 再配達音声化Trial 音声QA。正式Gate結果、clip別。API 0)

証跡: `er110_output/family_y_redelivery_audio_01/audio/r0/{a2,b1b}/audit/`(tts_generation_results.json・review_lock_state.json・y_style_profile_gate.json・run_summary_assemble.json)、`er110_output/family_y_redelivery_audio_01/audio/r0/audio_qa_summary.json`、`er110_output/family_y_redelivery_audio_01/audio/r0/raw_usage_log.jsonl`。

凡例: calls/retry=TTS呼出数/再試行数。ASR=最終ASR照合。Repetition QA=method A+D'。

## Advanced

| segment | Voice | status | calls/retry | ASR | Repetition QA | 備考 |
|---|---|---|---|---|---|---|
| topic_intro | Charon | OK | 1/None | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 4.0s |
| preview | Charon | OK | 1/None | EXACT_MATCH(asr_verified) | 未実施 | - / 12.8s |
| comment_1 | Charon | OK | 1/None | NUMERIC_EQUIVALENCE_MATCH(asr_verified) | 未実施 | - / 5.2s |
| comment_2 | Charon | OK | 1/None | NUMERIC_EQUIVALENCE_MATCH(asr_verified) | 未実施 | - / 7.4s |
| comment_3 | Charon | OK | 1/None | EXACT_MATCH(asr_verified) | 未実施 | - / 11.6s |
| full_story_part1 | Aoede | OK | 1/None | NORMALIZED_MATCH(asr_verified) | PASS | - / 21.6s |
| full_story_part2 | Algieba | OK | 1/None | NORMALIZED_MATCH(asr_verified) | PASS | - / 39.8s |
| full_story_part3 | Zephyr | OK | 2/None | NORMALIZED_MATCH(asr_verified) | PASS | - / 47.1s |
| full_story_part3_c2 | Schedar | OK | 1/None | NORMALIZED_MATCH(asr_verified) | PASS | - / 47.4s |
| full_story_part3_c3 | Aoede | OK | 1/None | NORMALIZED_MATCH(asr_verified) | PASS | - / 41.8s |
| in_one_line | Aoede | OK | 1/None | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 12.8s |
| kp1_english | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 1.7s |
| kp1_explanation | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 3.2s |
| kp1_phrase_repeat | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 1.7s |
| kp2_english | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 1.5s |
| kp2_explanation | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 3.1s |
| kp2_phrase_repeat | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 1.5s |
| kp3_english | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 1.8s |
| kp3_explanation | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 2.9s |
| kp3_phrase_repeat | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 1.8s |

- Human Review Lock: なし(全segment final_status=OK)
- Y style gate(M3+Y追加検査): PASS
- Assembly: status=OK duration=321.47 clipping=False peak=0.91645
- pass_with_warning(読み方の揺れ・非ブロッキング、事後試聴参考): 1件 full_story_part3
- 局所Rewrite(recovery)発動: なし

## Standard

| segment | Voice | status | calls/retry | ASR | Repetition QA | 備考 |
|---|---|---|---|---|---|---|
| topic_intro | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 3.9s |
| japanese_title | Aoede | OK | 1/0 | EXACT_MATCH(asr_verified) | 未実施 | - / 3.8s |
| preview | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 12.2s |
| comment_1 | Aoede | OK | 1/0 | NUMERIC_VALUE_EQUIVALENT_MATCH(asr_verified) | 未実施 | - / 7.4s |
| comment_2 | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 9.4s |
| comment_3 | Aoede | OK | 1/0 | EXACT_MATCH(asr_verified) | 未実施 | - / 9.7s |
| full_story_part1 | Aoede | OK | 1/0 | NUMERIC_EQUIVALENCE_MATCH(asr_verified) | PASS | 6%減速 / 22.1s |
| full_story_part2 | Algieba | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | PASS | 6%減速 / 42.0s |
| full_story_part3 | Zephyr | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | PASS | 6%減速 / 51.3s |
| full_story_part3_c2 | Schedar | OK | 1/0 | NUMERIC_EQUIVALENCE_MATCH(asr_verified) | PASS | 6%減速 / 55.0s |
| full_story_part3_c3 | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | PASS | 6%減速 / 42.4s |
| in_one_line | Aoede | OK | 1/0 | NUMERIC_EQUIVALENCE_MATCH(asr_verified) | 未実施 | 6%減速 / 17.0s |
| kp1_english | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 1.4s |
| kp1_japanese_meaning | Aoede | OK | 1/0 | EXACT_MATCH(asr_verified) | 未実施 | - / 2.2s |
| kp2_english | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 1.4s |
| kp2_japanese_meaning | Aoede | OK | 1/0 | EXACT_MATCH(asr_verified) | 未実施 | - / 1.4s |
| kp3_english | Aoede | OK | 1/0 | NORMALIZED_MATCH(asr_verified) | 未実施 | - / 1.7s |
| kp3_japanese_meaning | Aoede | OK | 1/0 | EXACT_MATCH(asr_verified) | 未実施 | - / 1.8s |

- Human Review Lock: なし(全segment final_status=OK)
- Y style gate(M3+Y追加検査): PASS
- Assembly: status=OK duration=342.799 clipping=False peak=0.95105
- pass_with_warning(読み方の揺れ・非ブロッキング、事後試聴参考): 0件 
- 局所Rewrite(recovery)発動: なし

## Voice別実測(F0は自己相関法の簡易推定で、Voice間の相対比較用)

| level | パート | Voice | 長さ(s) | 語数 | 語/分 | F0中央値(Hz) | F0幅(半音) | 重心(Hz) |
|---|---|---|---|---|---|---|---|---|
| b1b | lead | Aoede | 21.6 | 68 | 188.9 | 177.8 | 9.48 | 3174.0 |
| b1b | voice_1 | Algieba | 39.81 | 130 | 195.9 | 104.8 | 12.73 | 2488.0 |
| b1b | voice_2 | Zephyr | 47.08 | 154 | 196.3 | 171.4 | 9.79 | 3048.0 |
| b1b | voice_3 | Schedar | 47.44 | 162 | 204.9 | 103.4 | 15.34 | 3791.0 |
| b1b | final | Aoede | 41.84 | 133 | 190.7 | 173.9 | 10.18 | 2752.0 |
| b1b | in_one_line | Aoede | 12.81 | 34 | 159.3 | 156.9 | 8.97 | 2834.0 |
| a2 | lead | Aoede | 22.15 | 67 | 181.5 | 172.7 | 10.12 | 3026.0 |
| a2 | voice_1 | Algieba | 42.04 | 129 | 184.1 | 106.7 | 14.82 | 2348.0 |
| a2 | voice_2 | Zephyr | 51.33 | 162 | 189.3 | 173.9 | 10.16 | 2017.0 |
| a2 | voice_3 | Schedar | 55.01 | 163 | 177.8 | 139.5 | 15.07 | 3166.0 |
| a2 | final | Aoede | 42.39 | 125 | 176.9 | 165.5 | 10.16 | 3188.0 |
| a2 | in_one_line | Aoede | 16.99 | 41 | 144.8 | 177.8 | 8.84 | 2608.0 |

- 費用(このaudio dirのraw usage log、openai+gemini+azure換算): 19.72 円 {'gemini_batch': 8.27, 'openai_asr': 4.55, 'azure': 6.88, 'openai': 0.02}
