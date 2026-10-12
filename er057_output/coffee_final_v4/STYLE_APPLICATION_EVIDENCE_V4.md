# STYLE_APPLICATION_EVIDENCE_V4 (委任_01A, 2026-10-12)
新規生成は Full Story Part1〜3 x 2Level のみ(6 call、全て attempt1採択)。Style = P8(Aoede Style Trial-03、Coffee Full Story専用[ユーザー決定2026-10-12])、
prompt sha256 = `3eadf4f6f788b822c90f17ba56d893bccb5fab840358cf48845472cd4f4e5595`(prompts_aoede_style_03.md のP8ブロックと逐語一致をassert、Trial-03 generation_logのP8 style_sha256とも一致を確認)。
model = gemini-3.8-flash-lite-tts(応答model_version実測)、voice = Aoede、speech_metadata方式、Standard同期(DEV Trial; Production既定=Batch)。
P8 Prompt逐語:
```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy. Let the pitch rise and fall a little more on key words. Add a touch more brightness and a hint of a smile in the voice, while staying unhurried. Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard.
```
ユーザー指示の「既存A2減速指示」について: v3のStandard Full Storyの実装は PD8 本文そのまま(追加のA2減速指示句なし)+生成後6%減速(apply_a2_slowdown)であり、v4もv3と同一経路としてP8逐語+生成後6%減速とした(PD8自体に unhurried を含む。追加句は付けていない)。

## 生成clip別
| clip | attempt | model_version | ASR判定 | 尺 | 6%減速 | wav sha | 費用 |
|---|---|---|---|---|---|---|---|
| std_part1 | 1 | gemini-3.8-flash-lite-tts | NORMALIZED_MATCH (primary) | 45.53s | ratio 1.0596 (実5.963%) | 8f8ede12a4b6 | tts JPY 1.1049 |
| std_part2 | 1 | gemini-3.8-flash-lite-tts | NUMERIC_EQUIVALENCE_MATCH (primary) | 53.31s | ratio 1.0599 (実5.988%) | dac2eb9b3d5e | tts JPY 1.2978 |
| std_part3 | 1 | gemini-3.8-flash-lite-tts | NUMERIC_EQUIVALENCE_MATCH (primary) | 45.0s | ratio 1.0599 (実5.986%) | 715744661d7c | tts JPY 1.0926 |
| adv_part1 | 1 | gemini-3.8-flash-lite-tts | NORMALIZED_MATCH (primary) | 47.08s | - | 8b616edca69c | tts JPY 1.1425 |
| adv_part2 | 1 | gemini-3.8-flash-lite-tts | NORMALIZED_MATCH (primary) | 55.88s | - | c79194e1dbd4 | tts JPY 1.3574 |
| adv_part3 | 1 | gemini-3.8-flash-lite-tts | HIGH_SIMILARITY_SAFE (primary) | 50.44s | - | f8831096f101 | tts JPY 1.2244 |

canonical原稿: 6本とも tts_input sha256 が v3(Std=generation_log_v3_01、Adv=pace_trial_02 PD8 log)と完全一致(assert済み)。
## Level別 role x origin x Style x sha (provenanceのorigin: T=Trial生成済み音声再利用 / P=既存承認再利用 / R=再生成)
### std
| role | origin | style | wav sha先頭12 | voice |
|---|---|---|---|---|
| preview | T | P2 | 9e54868b1342 | (v3と同一) |
| welcome | T | A5 | 44f6ceb9255b | (v3と同一) |
| preview_intro | T | B5 | 199327468779 | (v3と同一) |
| key_phrases_intro | P | 既存承認(変更なし) | a21e1242a987 | (v3と同一) |
| full_story_intro | P | 既存承認(変更なし) | 327b86d46f26 | (v3と同一) |
| num_one | P | 既存承認(変更なし) | a3a4e9883b9f | (v3と同一) |
| num_two | P | 既存承認(変更なし) | f612e4308037 | (v3と同一) |
| num_three | P | 既存承認(変更なし) | 052f4cba47ff | (v3と同一) |
| num_four | P | 既存承認(変更なし) | 6cb9d3a14604 | (v3と同一) |
| num_five | P | 既存承認(変更なし) | 7bd81d17b43c | (v3と同一) |
| topic_intro | R | 既存承認TOPIC_INTRO(変更なし)・STD-24対処で1回再生成 | 5c3de348b373 | (v3と同一) |
| japanese_title | P | 既存承認(変更なし) | 6e2d14e2b51b | (v3と同一) |
| kp1_en | T | K2 | 7b667d9542b8 | (v3と同一) |
| meaning_1 | T | M2 | 940b4b6e6a56 | (v3と同一) |
| kp2_en | T | K2 | 5b4363e66554 | (v3と同一) |
| meaning_2 | T | M2 | 0dfb3f67ac4c | (v3と同一) |
| kp3_en | T | K2 | 46b00c613503 | (v3と同一) |
| meaning_3 | T | M2 | 537554529bdc | (v3と同一) |
| kp4_en | T | K2 | b36b606098d2 | (v3と同一) |
| meaning_4 | T | M2 | 27bc00ef2d20 | (v3と同一) |
| kp5_en | T | K2 | fd13e6ea5671 | (v3と同一) |
| meaning_5 | T | M2 | ae7bb24c93ea | (v3と同一) |
| comment_1 | T | P2 | 8b2248d7a82d | (v3と同一) |
| comment_2 | T | P2 | d94da2084ffb | (v3と同一) |
| comment_3 | T | P2 | b9496509481b | (v3と同一) |
| comment_4 | T | P2 | 237d2c7f584b | (v3と同一) |
| full_story_part1 | R | P8+6%減速(v4新規生成) | 6546b00f7805 | Aoede |
| full_story_part2 | R | P8+6%減速(v4新規生成) | dd032240b5d8 | Aoede |
| full_story_part3 | R | P8+6%減速(v4新規生成) | cb3c33166f0e | Aoede |
| in_one_line | R | IN_ONE_LINE既存承認Style+A2減速指示+6%減速・新原稿(2文) | c82267e275dc | (v3と同一) |
### adv
| role | origin | style | wav sha先頭12 | voice |
|---|---|---|---|---|
| welcome_charon | T | A5 | 44f6ceb9255b | (v3と同一) |
| preview_intro_charon | T | B5 | 199327468779 | (v3と同一) |
| key_phrases_intro_charon | P | 既存承認(変更なし) | a21e1242a987 | (v3と同一) |
| full_story_intro_charon | P | 既存承認(変更なし) | 327b86d46f26 | (v3と同一) |
| num_one_charon | P | 既存承認(変更なし) | a3a4e9883b9f | (v3と同一) |
| num_two_charon | P | 既存承認(変更なし) | f612e4308037 | (v3と同一) |
| num_three_charon | P | 既存承認(変更なし) | 052f4cba47ff | (v3と同一) |
| num_four_charon | P | 既存承認(変更なし) | 6cb9d3a14604 | (v3と同一) |
| num_five_charon | P | 既存承認(変更なし) | 7bd81d17b43c | (v3と同一) |
| topic_intro | P | 既存承認(変更なし) | 03aba23283fa | (v3と同一) |
| full_story_part1 | R | P8(Aoede Style Trial-03、v4新規生成) | 8b616edca69c | Aoede |
| full_story_part2 | R | P8(Aoede Style Trial-03、v4新規生成) | c79194e1dbd4 | Aoede |
| full_story_part3 | R | P8(Aoede Style Trial-03、v4新規生成) | f8831096f101 | Aoede |
| comment_1 | P | 既存承認(変更なし) | 200ad3c76535 | (v3と同一) |
| comment_2 | P | 既存承認(変更なし) | 019db624aff2 | (v3と同一) |
| comment_3 | P | 既存承認(変更なし) | 195457b46fe8 | (v3と同一) |
| comment_4 | P | 既存承認(変更なし) | e10e14ff66f3 | (v3と同一) |
| preview | T | E1 | c7a8bb97f77d | (v3と同一) |
| in_one_line | R | IN_ONE_LINE既存承認Style・新原稿(2文) | 645cac39d8a6 | (v3と同一) |
| kp1_en | T | K2(委任_04生成、Final v2と同一) | 20b8b303e860 | (v3と同一) |
| kp1_explanation_en | P | 既存承認(変更なし) | 1f5728335b06 | (v3と同一) |
| kp2_en | T | K2(委任_04生成、Final v2と同一) | a2f5660de5bb | (v3と同一) |
| kp2_explanation_en | P | 既存承認(変更なし) | 00840679c3b9 | (v3と同一) |
| kp3_en | T | K2(委任_04生成、Final v2と同一) | 197f7afff745 | (v3と同一) |
| kp3_explanation_en | P | 既存承認(変更なし) | 613e88f0e604 | (v3と同一) |
| kp4_en | T | K2(委任_04生成、Final v2と同一) | e7a616366bbf | (v3と同一) |
| kp4_explanation_en | P | 既存承認(変更なし) | ecc706afc931 | (v3と同一) |
| kp5_en | T | K2(委任_04生成、Final v2と同一) | 58602a650987 | (v3と同一) |
| kp5_explanation_en | P | 既存承認(変更なし) | fc58921d490c | (v3と同一) |
(Full Story Part1〜3 のみ sha が v3から変化。他role全件は v3と同一sha[PRODUCTION_DIFF_V4参照]。)
