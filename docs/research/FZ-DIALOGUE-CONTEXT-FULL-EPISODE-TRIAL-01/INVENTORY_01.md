# INVENTORY_01 — 全編通しTrialの対象棚卸(FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_01、API 0)

出典: 各作品の公開済み完成版runの `segment_plan_<lv>.json` / `<lv>/audit/tts_generation_results.json` / `<lv>/assembly/timeline.json` / `voice_assignment.json`(読取のみ)。機械可読: `er118_output/fz_full_episode_trial_01/inventory.json`(`py er118_fz_full_episode_trial_01.py inventory` で再生成可)。

## 1. 作品×レベルの総括

| 作品 | レベル | 正本run | 話者別セリフ数 | セリフ計 | 語数(min/max/計/≤2語) | 地の文clip | 通し秒 | セリフ占有 | Production試行/clip数 | base style一致 | 速度仕様 | 公開通しmp3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 猿の手 | Standard(a2) | `er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01` | {'morris': 4, 'mr_white': 5, 'herbert': 1, 'visitor': 2, 'mrs_white': 3} | 15 | 2/15/118/2 | 15 | 301.8 | 17.6% | 15/15 | True | std_dialogue_none | `user_test/family_z_monkeys_paw_01/audio_standard/MonkeysPaw_a2_full.mp3`(実在=True) |
| 猿の手 | Advanced(b1b) | `er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01` | {'morris': 5, 'mr_white': 5, 'herbert': 1, 'visitor': 3, 'mrs_white': 3} | 17 | 1/13/102/4 | 17 | 291.2 | 15.9% | 18/17 | True | adv_dialogue_fast6 | `user_test/family_z_monkeys_paw_01/audio_advanced/MonkeysPaw_b1b_full.mp3`(実在=True) |
| 走れメロス | Standard(a2) | `er026_output/family_z_production_e2e_01/melos/run_e2e_06` | {'melos': 5, 'king': 3, 'friend': 2} | 10 | 4/14/83/0 | 13 | 301.9 | 11.9% | 10/10 | True | std_dialogue_none | `user_test/family_z_melos_02/audio_standard/Melos_a2_full.mp3`(実在=True) |
| 走れメロス | Advanced(b1b) | `er026_output/family_z_production_e2e_01/melos/run_e2e_06` | {'melos': 5, 'king': 4, 'friend': 2} | 11 | 3/13/73/0 | 14 | 293.1 | 11.3% | 11/11 | True | adv_dialogue_fast6 | `user_test/family_z_melos_02/audio_advanced/Melos_b1b_full.mp3`(実在=True) |

- **新規生成対象セリフ総数: 53 clip**(猿の手 Std 15 / Adv 17、メロス Std 10 / Adv 11)。両作品とも Standard(a2)・Advanced(b1b)の2レベルが既存完成版に存在する。
- 地の文・Intro/Welcome/Preview/Key Phrase/Comment/Outro等の既存音声は Production run の `<lv>/narration/` を再利用(新規生成しない)。
- 公開ページURL(Production・比較用の参照のみ): https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_02/index.html / https://shimomura055.github.io/eigo-radio/user_test/family_z_monkeys_paw_01/index.html

## 2. セリフclip一覧(作品×レベル)

### 猿の手 / Standard (`monkeys_paw/a2`) — Voice {'morris': 'Algieba', 'mr_white': 'Schedar', 'herbert': 'Fenrir', 'visitor': 'Orus', 'mrs_white': 'Zephyr'}

| clip_id | 話者 | 語数 | 原音秒 | Production試行 | ASR | status | 速度 | Round 2流用禁止 | 本文 |
|---|---|---|---|---|---|---|---|---|---|
| `full_story_part1_c2` | morris | 5 | 3.091 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "The paw gives three wishes," |
| `full_story_part1_c4` | morris | 8 | 4.531 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "But trying to change your fate brings sadness." |
| `full_story_part1_c5` | mr_white | 5 | 1.931 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "Did you make any wishes?" |
| `full_story_part1_c7` | morris | 6 | 3.411 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "I've already used all three wishes." |
| `full_story_part1_c9` | morris | 9 | 3.891 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "Burn it, or don't blame me for what happens," |
| `full_story_part1_c11` | herbert | 12 | 5.011 | 1 | PASS/ORTHOGRAPHIC_EQUIVALENT_MATCH | OK | std_dialogue_none | - | "Ask for two hundred pounds, Father! That would pay for the house." |
| `full_story_part1_c13` | mr_white | 7 | 3.371 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "I wish to have two hundred pounds." |
| `full_story_part2_c2` | visitor | 10 | 4.221 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "Your son died after a machine caught him at work," |
| `full_story_part2_c4` | visitor | 15 | 5.251 | 1 | PASS/ORTHOGRAPHIC_EQUIVALENT_MATCH | OK | std_dialogue_none | - | "The company says it isn't to blame, but offers two hundred pounds for |
| `full_story_part2_c6` | mrs_white | 14 | 5.831 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "There are still two wishes in the paw! Bring our son back to life!" |
| `full_story_part2_c8` | mr_white | 11 | 3.901 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "You didn't see him, and I'm afraid of what might return." |
| `full_story_part2_c9` | mrs_white | 5 | 2.211 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "But he's our own son!" |
| `full_story_part3_c1` | mr_white | 7 | 2.731 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "I wish for Herbert to live again." |
| `full_story_part3_c3` | mrs_white | 2 | 1.691 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "It's Herbert!" |
| `full_story_part3_c5` | mr_white | 2 | 1.971 | 1 | PASS/NORMALIZED_MATCH | OK | std_dialogue_none | - | "Please wait!" |

### 猿の手 / Advanced (`monkeys_paw/b1b`) — Voice {'morris': 'Algieba', 'mr_white': 'Schedar', 'herbert': 'Fenrir', 'visitor': 'Orus', 'mrs_white': 'Zephyr'}

| clip_id | 話者 | 語数 | 原音秒 | Production試行 | ASR | status | 速度 | Round 2流用禁止 | 本文 |
|---|---|---|---|---|---|---|---|---|---|
| `full_story_part1_c2` | morris | 4 | 2.651 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | - | "It grants three wishes," |
| `full_story_part1_c4` | morris | 9 | 4.331 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | **はい** | "but brings sorrow to anyone who interferes with fate." |
| `full_story_part1_c5` | mr_white | 4 | 1.371 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | - | "Have you used it?" |
| `full_story_part1_c7` | morris | 2 | 1.661 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | - | "All three." |
| `full_story_part1_c9` | morris | 2 | 0.961 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | - | "Burn it," |
| `full_story_part1_c11` | morris | 8 | 3.081 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | - | "And don't blame me if you keep it." |
| `full_story_part1_c13` | herbert | 12 | 4.651 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | **はい** | "Ask for two hundred pounds, Father. Enough to pay off the house!" |
| `full_story_part1_c15` | mr_white | 6 | 3.531 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | **はい** | "I wish for two hundred pounds." |
| `full_story_part2_c2` | visitor | 7 | 2.411 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | **はい** | "Your son was caught in the machinery," |
| `full_story_part2_c4` | visitor | 3 | 1.851 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | - | "He is dead." |
| `full_story_part2_c6` | visitor | 13 | 6.221 | 1 | PASS/ORTHOGRAPHIC_EQUIVALENT_MATCH | OK | adv_dialogue_fast6 | **はい** | "The firm accepts no responsibility, but offers you two hundred pounds |
| `full_story_part2_c8` | mrs_white | 11 | 5.321 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | **はい** | "The paw! We have two wishes left. Wish him alive again!" |
| `full_story_part2_c10` | mr_white | 11 | 3.931 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | **はい** | "You didn't see him. I'm afraid of what might come back." |
| `full_story_part2_c11` | mrs_white | 3 | 1.451 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | - | "He's our son!" |
| `full_story_part3_c1` | mr_white | 5 | 2.891 | 2 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | **はい** | "I wish Herbert alive again." |
| `full_story_part3_c3` | mrs_white | 1 | 1.491 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | - | "Herbert!" |
| `full_story_part3_c5` | mr_white | 1 | 1.051 | 1 | PASS/NORMALIZED_MATCH | OK | adv_dialogue_fast6 | - | "Wait!" |

### 走れメロス / Standard (`melos/a2`) — Voice {'melos': 'Algieba', 'king': 'Charon', 'friend': 'Erinome'}

| clip_id | 話者 | 語数 | 原音秒 | Production試行 | ASR | status | 速度 | Round 2流用禁止 | 本文 |
|---|---|---|---|---|---|---|---|---|---|
| `full_story_part1_c2` | melos | 13 | 4.771 | 1 | (inherited)PASS/None | OK | std_dialogue_none | - | "You kill men from fear. You never give them a chance to speak." |
| `full_story_part1_c4` | melos | 9 | 3.811 | 1 | (inherited)PASS/None | OK | std_dialogue_none | - | "Give me three days to see my sister's wedding," |
| `full_story_part1_c6` | melos | 6 | 2.701 | 1 | (inherited)PASS/None | OK | std_dialogue_none | - | "Then I will return to you." |
| `full_story_part1_c8` | king | 14 | 7.051 | 1 | (inherited)PASS/None | OK | std_dialogue_none | - | "Your friend must stay here. Return late, and he will die in your plac |
| `full_story_part1_c10` | friend | 9 | 3.451 | 1 | (inherited)PASS/None | OK | std_dialogue_none | - | "Go now, because I know you will come back." |
| `full_story_part3_c2` | melos | 4 | 2.961 | 1 | (inherited)PASS/None | OK | std_dialogue_none | - | "Stop now! I'm back!" |
| `full_story_part3_c4` | melos | 6 | 2.341 | 1 | (inherited)PASS/None | OK | std_dialogue_none | - | "I almost left you to die," |
| `full_story_part3_c6` | friend | 7 | 2.931 | 1 | (inherited)PASS/None | OK | std_dialogue_none | - | "I almost lost my trust in you," |
| `full_story_part3_c8` | king | 8 | 2.901 | 1 | (inherited)PASS/None | OK | std_dialogue_none | - | "Put the sword down and free both men." |
| `full_story_part3_c10` | king | 7 | 2.921 | 1 | (inherited)PASS/None | OK | std_dialogue_none | - | "How can a man win such trust?" |

### 走れメロス / Advanced (`melos/b1b`) — Voice {'melos': 'Algieba', 'king': 'Charon', 'friend': 'Erinome'}

| clip_id | 話者 | 語数 | 原音秒 | Production試行 | ASR | status | 速度 | Round 2流用禁止 | 本文 |
|---|---|---|---|---|---|---|---|---|---|
| `full_story_part1_c2` | melos | 13 | 5.331 | 1 | (inherited)PASS/None | OK | adv_dialogue_fast6 | - | "You kill men because you fear them. You won't even let them speak." |
| `full_story_part1_c4` | melos | 4 | 2.491 | 1 | (inherited)PASS/None | OK | adv_dialogue_fast6 | - | "Give me three days," |
| `full_story_part1_c6` | melos | 13 | 4.761 | 1 | (inherited)PASS/None | OK | adv_dialogue_fast6 | - | "My sister is getting married. Let me see her wedding. I will return." |
| `full_story_part1_c8` | king | 12 | 5.741 | 1 | (inherited)PASS/None | OK | adv_dialogue_fast6 | - | "Your friend will stay here. If you are late, he dies instead." |
| `full_story_part1_c10` | friend | 6 | 2.651 | 1 | (inherited)PASS/None | OK | adv_dialogue_fast6 | - | "Go. I know you'll come back." |
| `full_story_part3_c2` | melos | 4 | 2.491 | 1 | (inherited)PASS/None | OK | adv_dialogue_fast6 | - | "Stop! I am here!" |
| `full_story_part3_c4` | melos | 4 | 2.361 | 1 | (inherited)PASS/None | OK | adv_dialogue_fast6 | - | "I nearly abandoned you," |
| `full_story_part3_c6` | friend | 4 | 2.651 | 1 | (inherited)PASS/None | OK | adv_dialogue_fast6 | - | "I nearly stopped believing," |
| `full_story_part3_c8` | king | 3 | 1.781 | 1 | (inherited)PASS/None | OK | adv_dialogue_fast6 | - | "Lower the sword," |
| `full_story_part3_c10` | king | 3 | 1.651 | 1 | (inherited)PASS/None | OK | adv_dialogue_fast6 | - | "Free them both." |
| `full_story_part3_c12` | king | 7 | 2.921 | 1 | (inherited)PASS/None | OK | adv_dialogue_fast6 | - | "How does a man earn such trust?" |

## 3. 流用禁止・再利用の範囲(ユーザー原文§2)

- 猿の手 Adv のうちRound 2 A/Bで生成済みの 8 clip(`full_story_part1_c4, full_story_part1_c13, full_story_part1_c15, full_story_part2_c2, full_story_part2_c6, full_story_part2_c8, full_story_part2_c10, full_story_part3_c1`)は **新規に作り直す**(Round 2の生成音声を流用しない)。Std側はRound 2に無く全件新規。
- メロスは全セリフ新規(Round 1/2に未登場)。
- 比較条件が変わる範囲(明示): 地の文・Intro/Preview/KP/Comment/Outro・無音・gainルールは Production と同一音声/同一規則。**差はセリフclipのみ**(ただしgain/平均RMSはclip単位のProduction規則を適用、Production試行で確定した音声ではなく新規生成のため音量は規則で再計算される)。

## 4. 注意・限界(観測事実)

- `monkeys_paw/a2`: 2語以下のセリフ 2 件(短文は話速が不安定=Round 2 EVAL_02 §5)
- `monkeys_paw/b1b`: 2語以下のセリフ 4 件(短文は話速が不安定=Round 2 EVAL_02 §5)
- `melos/a2`: Production clipは前run再利用(reused_from_previous_run); ASR判定は新形式でなく継承/旧形式(asr_judgement_inherited等)
- `melos/b1b`: Production clipは前run再利用(reused_from_previous_run); ASR判定は新形式でなく継承/旧形式(asr_judgement_inherited等)

