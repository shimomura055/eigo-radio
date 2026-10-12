# STYLE_APPLICATION_EVIDENCE_V3_01(委任_02、role x Style x prompt sha x model)

Style選択は「Coffee限定APPROVED_FOR_PRODUCTION」(ユーザー決定2026-10-12)。Trial隔離で適用、Production未配線。新規生成分は応答model_version実測=`gemini-3.8-flash-lite-tts`(voice Aoede、speech_metadata方式、Standard同期)。再利用分はFinal v2/pace_trial_02と同一wav sha(下表)。

新規生成分(委任_01+02): PD8 prompt sha先頭12=329ff46a5ec3(Std Part1/2/3)、IN_ONE_LINE Std=10e21170b1b1(既存承認prefix+A2減速指示)、Adv=63495557ec82(既存承認prefix)。Part2は3 attempt全て同一Prompt、採用=attempt1(Secondary cascade NORMALIZED_MATCH、local whisper差分最少)。

## std
| role | origin | Style | wav sha先頭12 |
|---|---|---|---|
| preview | T | P2 | 9e54868b1342 |
| welcome | T | A5 | 44f6ceb9255b |
| preview_intro | T | B5 | 199327468779 |
| key_phrases_intro | P | 既存承認(変更なし) | a21e1242a987 |
| full_story_intro | P | 既存承認(変更なし) | 327b86d46f26 |
| num_one | P | 既存承認(変更なし) | a3a4e9883b9f |
| num_two | P | 既存承認(変更なし) | f612e4308037 |
| num_three | P | 既存承認(変更なし) | 052f4cba47ff |
| num_four | P | 既存承認(変更なし) | 6cb9d3a14604 |
| num_five | P | 既存承認(変更なし) | 7bd81d17b43c |
| topic_intro | R | 既存承認TOPIC_INTRO(変更なし)・STD-24対処で1回再生成 | 5c3de348b373 |
| japanese_title | P | 既存承認(変更なし) | 6e2d14e2b51b |
| kp1_en | T | K2 | 7b667d9542b8 |
| meaning_1 | T | M2 | 940b4b6e6a56 |
| kp2_en | T | K2 | 5b4363e66554 |
| meaning_2 | T | M2 | 0dfb3f67ac4c |
| kp3_en | T | K2 | 46b00c613503 |
| meaning_3 | T | M2 | 537554529bdc |
| kp4_en | T | K2 | b36b606098d2 |
| meaning_4 | T | M2 | 27bc00ef2d20 |
| kp5_en | T | K2 | fd13e6ea5671 |
| meaning_5 | T | M2 | ae7bb24c93ea |
| comment_1 | T | P2 | 8b2248d7a82d |
| comment_2 | T | P2 | d94da2084ffb |
| comment_3 | T | P2 | b9496509481b |
| comment_4 | T | P2 | 237d2c7f584b |
| full_story_part1 | R | PD8+6%減速 | e9c2685debcc |
| full_story_part2 | R | PD8+6%減速 | 4734c08b135a |
| full_story_part3 | R | PD8+6%減速 | a3909766d3ee |
| in_one_line | R | IN_ONE_LINE既存承認Style+A2減速指示+6%減速・新原稿(2文) | c82267e275dc |

## adv
| role | origin | Style | wav sha先頭12 |
|---|---|---|---|
| welcome_charon | T | A5 | 44f6ceb9255b |
| preview_intro_charon | T | B5 | 199327468779 |
| key_phrases_intro_charon | P | 既存承認(変更なし) | a21e1242a987 |
| full_story_intro_charon | P | 既存承認(変更なし) | 327b86d46f26 |
| num_one_charon | P | 既存承認(変更なし) | a3a4e9883b9f |
| num_two_charon | P | 既存承認(変更なし) | f612e4308037 |
| num_three_charon | P | 既存承認(変更なし) | 052f4cba47ff |
| num_four_charon | P | 既存承認(変更なし) | 6cb9d3a14604 |
| num_five_charon | P | 既存承認(変更なし) | 7bd81d17b43c |
| topic_intro | P | 既存承認(変更なし) | 03aba23283fa |
| full_story_part1 | T | PD8(pace_trial_02生成、再利用) | b20b1208c2f3 |
| full_story_part2 | T | PD8(pace_trial_02生成、再利用) | b00c12342491 |
| full_story_part3 | T | PD8(pace_trial_02生成、再利用) | a148fd7d9320 |
| comment_1 | P | 既存承認(変更なし) | 200ad3c76535 |
| comment_2 | P | 既存承認(変更なし) | 019db624aff2 |
| comment_3 | P | 既存承認(変更なし) | 195457b46fe8 |
| comment_4 | P | 既存承認(変更なし) | e10e14ff66f3 |
| preview | T | E1 | c7a8bb97f77d |
| in_one_line | R | IN_ONE_LINE既存承認Style・新原稿(2文) | 645cac39d8a6 |
| kp1_en | T | K2(委任_04生成、Final v2と同一) | 20b8b303e860 |
| kp1_explanation_en | P | 既存承認(変更なし) | 1f5728335b06 |
| kp2_en | T | K2(委任_04生成、Final v2と同一) | a2f5660de5bb |
| kp2_explanation_en | P | 既存承認(変更なし) | 00840679c3b9 |
| kp3_en | T | K2(委任_04生成、Final v2と同一) | 197f7afff745 |
| kp3_explanation_en | P | 既存承認(変更なし) | 613e88f0e604 |
| kp4_en | T | K2(委任_04生成、Final v2と同一) | e7a616366bbf |
| kp4_explanation_en | P | 既存承認(変更なし) | ecc706afc931 |
| kp5_en | T | K2(委任_04生成、Final v2と同一) | 58602a650987 |
| kp5_explanation_en | P | 既存承認(変更なし) | fc58921d490c |

origin: T=Trial生成済み音声再利用/新規(委任記録参照)、R=今回再生成(または既存承認の加工版)、その他=既存承認音声。