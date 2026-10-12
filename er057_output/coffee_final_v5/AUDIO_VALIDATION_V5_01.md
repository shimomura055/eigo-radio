# AUDIO_VALIDATION_V5_01 (Audio Validation Gate 相当の記録、再計算のみ)

- 位置づけ: runner `--stage assemble` のAudio Validation Gateは**通していない**(Trial assembler `er057_coffee_final_v5_build_01.py` で組立)。本書はその代替としての事後記録(wav sha256再計算、減速有無、既存QA参照)。API呼出・音声再生成なし。
- 生成: `er057_coffee_final_v5_audio_validation_01.py`(assembly_manifest_v5_01.json / gen_summary_v4.json / v5 tts_generation_results.json から)。
- 全体QA(peak/clipping/headroom/長さ/内部無音/RMS/mp3整合)は `qa_v5_01.json`、known anomaly照合は `known_anomaly_compare_v5.json`、検出器は `anomaly_v5_std.json`/`anomaly_v5_adv.json`。
- A2減速列: 「適用(6%)」=ファイル名`*_slow6`かつv4 gen_summaryにslowdown記録あり。「なし(JA経路)」=Production runnerのJA生成経路(generate_a2_japanese_with_reading_safety)は6%減速post-process対象外で、v5 results の trim_info/attempts_log にも減速記録なし。「記録なし(流用)」=Trial/既承認wavで減速記録なし(v4と同一sha)。Adv=A2減速の対象外。

## Standard (30 role)

| role | origin | style | wav sha256(再計算,先頭12) | manifest一致 | v4と同一 | A2減速 | 既存QA参照 |
|---|---|---|---|---|---|---|---|
| preview | R | R2(Production runner、coffee_final_v5) | b9739f509f5e | OK | **v5新規** | なし(JA経路) | v5 results a2: status OK, asr_verified True, NORMALIZED_MATCH, attempt 1 |
| welcome | T | A5 | 44f6ceb9255b | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| preview_intro | T | B5 | 199327468779 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| key_phrases_intro | P | 既存承認(変更なし) | a21e1242a987 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| full_story_intro | P | 既存承認(変更なし) | 327b86d46f26 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| num_one | P | 既存承認(変更なし) | a3a4e9883b9f | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| num_two | P | 既存承認(変更なし) | f612e4308037 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| num_three | P | 既存承認(変更なし) | 052f4cba47ff | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| num_four | P | 既存承認(変更なし) | 6cb9d3a14604 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| num_five | P | 既存承認(変更なし) | 7bd81d17b43c | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| topic_intro | R | 既存承認TOPIC_INTRO(変更なし)・STD-24対処で1回再生成 | 5c3de348b373 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| japanese_title | P | 既存承認(変更なし) | 6e2d14e2b51b | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| kp1_en | T | K2 | 7b667d9542b8 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| meaning_1 | T | M2 | 940b4b6e6a56 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| kp2_en | T | K2 | 5b4363e66554 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| meaning_2 | T | M2 | 0dfb3f67ac4c | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| kp3_en | T | K2 | 46b00c613503 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| meaning_3 | T | M2 | 537554529bdc | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| kp4_en | T | K2 | b36b606098d2 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| meaning_4 | T | M2 | 27bc00ef2d20 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| kp5_en | T | K2 | fd13e6ea5671 | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| meaning_5 | T | M2 | ae7bb24c93ea | OK | 同一 | 記録なし(流用) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| comment_1 | R | R2(Production runner、coffee_final_v5) | 1381b2418be6 | OK | **v5新規** | なし(JA経路) | v5 results a2: status OK, asr_verified True, EXACT_MATCH, attempt 1 |
| comment_2 | R | R2(Production runner、coffee_final_v5) | 9a588e46c189 | OK | **v5新規** | なし(JA経路) | v5 results a2: status OK, asr_verified True, NORMALIZED_MATCH, attempt 1 |
| comment_3 | R | R2(Production runner、coffee_final_v5) | 4500cb0fb87d | OK | **v5新規** | なし(JA経路) | v5 results a2: status OK, asr_verified True, NORMALIZED_MATCH, attempt 1 |
| comment_4 | R | R2(Production runner、coffee_final_v5) | d108c5872efd | OK | **v5新規** | なし(JA経路) | v5 results a2: status OK, asr_verified True, PHONETIC_MATCH, attempt 1 |
| full_story_part1 | R | P8+6%減速(v4新規生成) | 6546b00f7805 | OK | 同一 | 適用(6%, 実測5.963%) | v4 gen_summary_v4.json std_part1: OK/NORMALIZED_MATCH, slow_asr NORMALIZED_MATCH |
| full_story_part2 | R | P8+6%減速(v4新規生成) | dd032240b5d8 | OK | 同一 | 適用(6%, 実測5.988%) | v4 gen_summary_v4.json std_part2: OK/NUMERIC_EQUIVALENCE_MATCH, slow_asr NORMALIZED_MATCH |
| full_story_part3 | R | P8+6%減速(v4新規生成) | cb3c33166f0e | OK | 同一 | 適用(6%, 実測5.986%) | v4 gen_summary_v4.json std_part3: OK/NUMERIC_EQUIVALENCE_MATCH, slow_asr NUMERIC_EQUIVALENCE_MATCH |
| in_one_line | R | IN_ONE_LINE既存承認Style+A2減速指示+6%減速・新原稿(2文) | c82267e275dc | OK | 同一 | 適用(6%, ファイル名std_in_one_line_slow6) | v4継続(coffee_final_audio_assembly_01/segments、IOL 2文版)。v4 PLAY_EVIDENCE/qa_v4_01.json |

- 小計: 30 role、sha再計算一致 30/30、欠落 なし

## Advanced (29 role)

| role | origin | style | wav sha256(再計算,先頭12) | manifest一致 | v4と同一 | A2減速 | 既存QA参照 |
|---|---|---|---|---|---|---|---|
| welcome_charon | T | A5 | 44f6ceb9255b | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| preview_intro_charon | T | B5 | 199327468779 | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| key_phrases_intro_charon | P | 既存承認(変更なし) | a21e1242a987 | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| full_story_intro_charon | P | 既存承認(変更なし) | 327b86d46f26 | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| num_one_charon | P | 既存承認(変更なし) | a3a4e9883b9f | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| num_two_charon | P | 既存承認(変更なし) | f612e4308037 | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| num_three_charon | P | 既存承認(変更なし) | 052f4cba47ff | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| num_four_charon | P | 既存承認(変更なし) | 6cb9d3a14604 | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| num_five_charon | P | 既存承認(変更なし) | 7bd81d17b43c | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| topic_intro | P | 既存承認(変更なし) | 03aba23283fa | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| full_story_part1 | R | P8(Aoede Style Trial-03、v4新規生成) | 8b616edca69c | OK | 同一 | 対象外(Adv) | v4 gen_summary_v4.json adv_part1: OK/NORMALIZED_MATCH |
| full_story_part2 | R | P8(Aoede Style Trial-03、v4新規生成) | c79194e1dbd4 | OK | 同一 | 対象外(Adv) | v4 gen_summary_v4.json adv_part2: OK/NORMALIZED_MATCH |
| full_story_part3 | R | P8(Aoede Style Trial-03、v4新規生成) | f8831096f101 | OK | 同一 | 対象外(Adv) | v4 gen_summary_v4.json adv_part3: OK/HIGH_SIMILARITY_SAFE |
| comment_1 | P | 既存承認(変更なし) | 200ad3c76535 | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| comment_2 | P | 既存承認(変更なし) | 019db624aff2 | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| comment_3 | P | 既存承認(変更なし) | 195457b46fe8 | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| comment_4 | P | 既存承認(変更なし) | e10e14ff66f3 | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| preview | T | E1 | c7a8bb97f77d | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| in_one_line | R | IN_ONE_LINE既存承認Style・新原稿(2文) | 645cac39d8a6 | OK | 同一 | 対象外(Adv) | v4継続(adv_in_one_line_raw、2文版) |
| kp1_en | T | K2(委任_04生成、Final v2と同一) | 20b8b303e860 | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| kp1_explanation_en | R | P3(Production runner、coffee_final_v5) | da1d5b752d65 | OK | **v5新規** | 対象外(Adv) | v5 results b1b: status OK, asr_verified True, NORMALIZED_MATCH, disfluency_checked True, call_count 1 |
| kp2_en | T | K2(委任_04生成、Final v2と同一) | a2f5660de5bb | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| kp2_explanation_en | R | P3(Production runner、coffee_final_v5) | f86f7a907c5f | OK | **v5新規** | 対象外(Adv) | v5 results b1b: status OK, asr_verified True, NORMALIZED_MATCH, disfluency_checked True, call_count 1 |
| kp3_en | T | K2(委任_04生成、Final v2と同一) | 197f7afff745 | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| kp3_explanation_en | R | P3(Production runner、coffee_final_v5) | 69e6cd9a7a2d | OK | **v5新規** | 対象外(Adv) | v5 results b1b: status OK, asr_verified True, NORMALIZED_MATCH, disfluency_checked True, call_count 1 |
| kp4_en | T | K2(委任_04生成、Final v2と同一) | e7a616366bbf | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| kp4_explanation_en | R | P3(Production runner、coffee_final_v5) | 99695c64900e | OK | **v5新規** | 対象外(Adv) | v5 results b1b: status OK, asr_verified True, NORMALIZED_MATCH, disfluency_checked True, call_count 1 |
| kp5_en | T | K2(委任_04生成、Final v2と同一) | 58602a650987 | OK | 同一 | 対象外(Adv) | v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json |
| kp5_explanation_en | R | P3(Production runner、coffee_final_v5) | 9e37b57805ab | OK | **v5新規** | 対象外(Adv) | v5 results b1b: status OK, asr_verified True, NORMALIZED_MATCH, disfluency_checked True, call_count 1 |

- 小計: 29 role、sha再計算一致 29/29、欠落 なし

