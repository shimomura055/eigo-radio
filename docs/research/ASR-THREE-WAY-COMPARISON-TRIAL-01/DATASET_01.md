# DATASET_01 (ASR-THREE-WAY-COMPARISON-TRIAL-01 評価データ台帳、自動生成)

正本=`er091_output/asr_three_way_trial_01/dataset_manifest.jsonl`(全フィールド: wav path/sha256/duration/canonical/label/label_basis/tags/ledger_phrases/duplicate_of/src_wav)。音声wavは`er091_output/asr_three_way_trial_01/audio/`(orig=既存音声のコピー[git管理外、src_wavから再生成可]、tts_construct・splice=新規生成[*.wavは.gitignore対象のためgit管理外・ローカル(この作業環境)のみ。TTSは再生成不可なのでバックアップ要否はFable判断])。
label_strength: human_listened_article=ユーザー試聴PASS記事の一部(KP/セグメント単位の個別聴取ではない) / human_approved_segment=HR承認済み / human_listened_user_report=ユーザー聴感指摘(take part) / construction=人間試聴なし。
tags は自動付与(proper_noun は文頭の固有名詞を含め過検出あり)。

| id | kind | Family/Level | 台本(canonical) | label | label_strength | 問題種別 | PL | 秒 | dup |
|---|---|---|---|---|---|---|---|---|---|
| kp_boredom_a2_1 | kp | X/Standard | meanness | normal | human_listened_article |  |  | 1.2 |  |
| kp_boredom_a2_2 | kp | X/Standard | turn on | normal | human_listened_article |  |  | 1.2 |  |
| kp_boredom_a2_3 | kp | X/Standard | make a reward smaller | normal | human_listened_article |  |  | 2.3 |  |
| kp_boredom_a2_4 | kp | X/Standard | boredom | normal | human_listened_article |  |  | 1.2 |  |
| kp_boredom_a2_5 | kp | X/Standard | use its results | normal | human_listened_article |  |  | 1.5 |  |
| kp_boredom_b1b_1 | kp | X/Advanced | sadistic | normal | human_listened_article |  |  | 1.2 |  |
| kp_boredom_b1b_2 | kp | X/Advanced | turn on | normal | human_listened_article |  |  | 1.2 | kp_boredom_a2_2 |
| kp_boredom_b1b_3 | kp | X/Advanced | apply one's findings | normal | human_listened_article |  |  | 2.0 |  |
| kp_boredom_b1b_4 | kp | X/Advanced | jump to | normal | human_listened_article |  |  | 1.2 |  |
| kp_boredom_b1b_5 | kp | X/Advanced | stone video | normal | human_listened_article |  |  | 1.4 |  |
| kp_yemen_a2_1 | kp | X/Standard | refueling support | normal | human_listened_article |  |  | 1.6 |  |
| kp_yemen_a2_2 | kp | X/Standard | mix up | normal | human_listened_article |  |  | 1.0 |  |
| kp_yemen_a2_3 | kp | X/Standard | air defense mission | normal | human_listened_article |  |  | 1.8 |  |
| kp_yemen_a2_4 | kp | X/Standard | weaken | normal | human_listened_article |  |  | 1.1 |  |
| kp_yemen_a2_5 | kp | X/Standard | Houthi military targets | normal | human_listened_article |  |  | 2.2 |  |
| kp_yemen_b1b_1 | kp | X/Advanced | refueling support | normal | human_listened_article |  |  | 1.6 | kp_yemen_a2_1 |
| kp_yemen_b1b_2 | kp | X/Advanced | mix up | normal | human_listened_article |  |  | 1.0 | kp_yemen_a2_2 |
| kp_yemen_b1b_3 | kp | X/Advanced | all the same kind | normal | human_listened_article |  |  | 1.5 |  |
| kp_yemen_b1b_4 | kp | X/Advanced | take the wheel | normal | human_listened_article |  |  | 1.2 |  |
| kp_yemen_b1b_5 | kp | X/Advanced | intercept | normal | human_listened_article |  |  | 1.3 |  |
| kp_melos_a2_1 | kp | Z/Standard | pull someone under | normal | human_listened_article |  |  | 1.6 |  |
| kp_melos_a2_2 | kp | Z/Standard | in someone's place | normal | human_listened_article |  |  | 2.2 |  |
| kp_melos_a2_3 | kp | Z/Standard | lose trust in someone | normal | human_listened_article |  |  | 2.0 |  |
| kp_melos_a2_4 | kp | Z/Standard | hold out | normal | human_listened_article |  |  | 1.1 |  |
| kp_melos_a2_5 | kp | Z/Standard | far bank | normal | human_listened_article |  |  | 1.1 |  |
| kp_melos_b1b_1 | kp | Z/Advanced | sentence someone to death | normal | human_listened_article |  |  | 1.9 |  |
| kp_melos_b1b_2 | kp | Z/Advanced | current | normal | human_listened_article |  |  | 1.1 |  |
| kp_melos_b1b_3 | kp | Z/Advanced | hold out | normal | human_listened_article |  |  | 1.2 |  |
| kp_melos_b1b_4 | kp | Z/Advanced | seize | normal | human_listened_article |  |  | 1.2 |  |
| kp_melos_b1b_5 | kp | Z/Advanced | abandon | normal | human_listened_article |  |  | 1.2 |  |
| body_melos_a2_topic_intro_en | body | Z/Standard | Today's topic is The Three-Day Promise. | normal | human_listened_article |  |  | 3.3 |  |
| body_melos_a2_full_story_part1_c2 | body | Z/Standard | "You kill men from fear. You never give them a c | normal | human_listened_article |  |  | 4.8 |  |
| body_melos_a2_full_story_part1_c4 | body | Z/Standard | "Give me three days to see my sister's wedding," | normal | human_listened_article |  |  | 3.8 |  |
| body_melos_a2_full_story_part1_c5 | body | Z/Standard | Melos said. | normal | human_listened_article |  | Melos | 1.6 |  |
| body_melos_a2_full_story_part1_c6 | body | Z/Standard | "Then I will return to you." | normal | human_listened_article |  |  | 2.7 |  |
| body_melos_a2_full_story_part1_c8 | body | Z/Standard | "Your friend must stay here. Return late, and he | normal | human_listened_article |  |  | 7.1 |  |
| body_melos_a2_full_story_part3_c2 | body | Z/Standard | "Stop now! I'm back!" | normal | human_listened_article |  |  | 3.0 |  |
| body_melos_a2_full_story_part3_c6 | body | Z/Standard | "I almost lost my trust in you," | normal | human_listened_article |  |  | 2.9 |  |
| body_melos_a2_full_story_part3_c8 | body | Z/Standard | "Put the sword down and free both men." | normal | human_listened_article |  |  | 2.9 |  |
| body_melos_a2_full_story_part2_c1 | body | Z/Standard | The river stopped him; its bridge was gone. Rain | normal | human_listened_article |  |  | 46.0 |  |
| body_melos_b1b_full_story_part1_c2 | body | Z/Advanced | "You kill men because you fear them. You won't e | normal | human_listened_article |  |  | 5.3 |  |
| body_melos_b1b_full_story_part1_c9 | body | Z/Advanced | Melos turned to his friend, but before he could  | normal | human_listened_article |  | Melos | 6.3 |  |
| body_melos_b1b_full_story_part3_c4 | body | Z/Advanced | "I nearly abandoned you," | normal | human_listened_article |  |  | 2.4 |  |
| body_melos_b1b_comment_1 | body | Z/Advanced | Listen for what Melos promises before he leaves. | normal | human_listened_article |  | Melos | 3.3 |  |
| body_melos_b1b_preview | body | Z/Advanced | This story follows a young shepherd who speaks o | normal | human_listened_article |  |  | 13.2 |  |
| body_boredom_a2_topic_intro | body | X/Standard | Today's topic is If You Had to Watch a Stone for | normal | human_listened_article |  |  | 6.1 |  |
| body_boredom_a2_in_one_line | body | X/Standard | Stone-watchers were more likely to make another  | normal | human_listened_article |  |  | 21.6 |  |
| body_boredom_b1b_comment_1 | body | X/Advanced | Listen for the choices viewers could make while  | normal | human_listened_article |  |  | 4.4 |  |
| body_boredom_b1b_full_story_part1 | body | X/Advanced | A stone. Still a stone. Surely something will ha | normal | human_listened_article |  |  | 51.8 |  |
| body_yemen_a2_topic_intro | body | X/Standard | Today's topic is Who Says “We Won’t Attack”? A W | normal | human_listened_article |  |  | 6.0 |  |
| body_yemen_a2_in_one_line | body | X/Standard | Britain said its Typhoon jets would defend Saudi | normal | human_listened_article |  |  | 15.0 |  |
| body_yemen_b1b_comment_1 | body | X/Advanced | As you listen, pay attention to who will not att | normal | human_listened_article |  |  | 5.0 |  |
| body_yemen_b1b_comment_2 | body | X/Advanced | So far, we know the Typhoon jets will defend Sau | normal | human_listened_article |  |  | 10.9 |  |
| body_yemen_b1b_full_story_part3 | body | X/Advanced | It is like someone saying, “I won’t drive,” whil | normal | human_listened_article |  |  | 48.0 |  |
| hr_run_e2e_04_a2_full_story_part3_c1 | body | Z/Standard | He remembered the hands held out for the chains. | normal | human_approved_segment |  | Melos | 23.1 |  |
| hr_run_e2e_02_a2_full_story_part1_c5 | body | Z/Standard | Melos said. | normal | human_approved_segment |  | Melos | 1.6 |  |
| hr_space_weapons_a2_full_story_part1 | body | X/Standard | The most important question in the new space-sec | normal | human_approved_segment |  | Meink | 37.9 |  |
| hr_tiny_bags_a2_full_story_part2 | body | X/Standard | The same pattern appeared in 2026. Small pouches | normal | human_approved_segment |  | TOTEME,Kallmeyer,mini,Al | 67.6 |  |
| hr_convenience_ai_a2_point_two | body | X/Standard | FamilyMart took a different path. It used sales  | normal | human_approved_segment |  | canelé,Oimo no Canele,oi | 20.5 |  |
| hr_pool_n9_tip_screens_a2_kp2_english | kp | X/Standard | default | normal | human_approved_segment |  |  | 1.2 |  |
| prob_kp_takepart_user_reported | kp | X/Standard | take part | problem | human_listened_user_report | consonant_swap(p->t)_user_heard_ta |  | 1.3 |  |
| plw_P1_nonsib_Aoede_take1 | body | Z/Standard | Melos drank deeply from the cold stream. | normal | construction(TTSにその綴りを読ませた;  |  | Melos | 3.0 |  |
| plw_P2_sib_Aoede_take1 | body | Z/Standard | Melos said nothing to the guards. | normal | construction(TTSにその綴りを読ませた;  |  | Melos | 2.5 |  |
| plw_P3_final_Aoede_take1 | body | Z/Standard | The man waiting at the gate was Melos. | normal | construction(TTSにその綴りを読ませた;  |  | Melos | 3.0 |  |
| plw_P4_mid_Aoede_take1 | body | Z/Standard | Then Melos walked away. | normal | construction(TTSにその綴りを読ませた;  |  | Melos | 2.2 |  |
| plw_P5_repeat_Aoede_take1 | body | Z/Standard | Melos spoke, and Melos listened. | normal | construction(TTSにその綴りを読ませた;  |  | Melos | 2.9 |  |
| plw_P7_compete_Aoede_take1 | body | Z/Standard | Melos liked the mellow sound of the old bell. | normal | construction(TTSにその綴りを読ませた;  |  | Melos | 3.5 |  |
| plw_NM_P1_mello_Aoede_take1 | body | Z/Standard | Melos drank deeply from the cold stream. | problem | construction(TTSにその綴りを読ませた;  | proper_noun_misreading(Mello) | Melos | 3.0 |  |
| plw_NM_P1_melon_Aoede_take1 | body | Z/Standard | Melos drank deeply from the cold stream. | problem | construction(TTSにその綴りを読ませた;  | proper_noun_misreading(Melon) | Melos | 3.0 |  |
| plw_NM_P1_mullos_Aoede_take1 | body | Z/Standard | Melos drank deeply from the cold stream. | problem | construction(TTSにその綴りを読ませた;  | proper_noun_misreading(Mullos) | Melos | 3.6 |  |
| plw_NM_P3_mello_Aoede_take1 | body | Z/Standard | The man waiting at the gate was Melos. | problem | construction(TTSにその綴りを読ませた;  | proper_noun_misreading(Mello) | Melos | 2.9 |  |
| plw_NM_P3_melon_Aoede_take1 | body | Z/Standard | The man waiting at the gate was Melos. | problem | construction(TTSにその綴りを読ませた;  | proper_noun_misreading(Melon) | Melos | 2.8 |  |
| plw_NM_P3_mullos_Aoede_take1 | body | Z/Standard | The man waiting at the gate was Melos. | problem | construction(TTSにその綴りを読ませた;  | proper_noun_misreading(Mullos) | Melos | 3.0 |  |
| plw_NM_P4_mello_Aoede_take1 | body | Z/Standard | Then Melos walked away. | problem | construction(TTSにその綴りを読ませた;  | proper_noun_misreading(Mello) | Melos | 2.0 |  |
| plw_NM_P4_melon_Aoede_take1 | body | Z/Standard | Then Melos walked away. | problem | construction(TTSにその綴りを読ませた;  | proper_noun_misreading(Melon) | Melos | 2.4 |  |
| plw_NM_P4_mullos_Aoede_take1 | body | Z/Standard | Then Melos walked away. | problem | construction(TTSにその綴りを読ませた;  | proper_noun_misreading(Mullos) | Melos | 2.2 |  |
| spl_body_almost_deleted | body | Z/Standard | "I almost lost my trust in you," | problem | construction(word physically | word_omission_meaning_change |  | 2.6 |  |
| spl_body_not_deleted | body | X/Advanced | As you listen, pay attention to who will not att | problem | construction(word physically | negation_omitted |  | 4.7 |  |
| spl_kp_in_deleted | kp | Z/Standard | lose trust in someone | problem | construction(word physically | kp_function_word_omission |  | 1.7 |  |
| spl_body_late_deleted | body | Z/Standard | "Your friend must stay here. Return late, and he | problem | construction(word physically | word_omission_meaning_change |  | 6.3 |  |
| spl_body_sword_duplicated | body | Z/Standard | "Put the sword down and free both men." | problem | construction(word physically | word_repetition_added |  | 3.2 |  |
| spl2_body_almost_deleted | body | Z/Standard | "I almost lost my trust in you," | problem | construction(word physically | word_omission_meaning_change |  | 2.6 |  |
| spl2_body_not_deleted | body | X/Advanced | As you listen, pay attention to who will not att | problem | construction(word physically | negation_omitted |  | 4.6 |  |
| spl2_kp_in_deleted | kp | Z/Standard | lose trust in someone | problem | construction(word physically | kp_function_word_omission |  | 1.7 |  |
| spl2_body_late_deleted | body | Z/Standard | "Your friend must stay here. Return late, and he | problem | construction(word physically | word_omission_meaning_change |  | 6.5 |  |
| spl2_body_sword_duplicated | body | Z/Standard | "Put the sword down and free both men." | problem | construction(word physically | word_repetition_added |  | 3.2 |  |
| tts_kp_takepart_as_tart | kp | X/Standard | take part | problem | construction(TTSに台本と異なる文面を読ま | consonant_swap(p->t) |  | 1.4 |  |
| tts_kp_weaken_as_weekend | kp | X/Standard | weaken | problem | construction(TTSに台本と異なる文面を読ま | vowel/consonant_confusion(real_sto |  | 1.3 |  |
| tts_kp_turnon_as_turnoff | kp | X/Standard | turn on | problem | construction(TTSに台本と異なる文面を読ま | meaning_change_word_swap |  | 1.0 |  |
| tts_kp_makerewardsmaller_omit_a | kp | X/Standard | make a reward smaller | problem | construction(TTSに台本と異なる文面を読ま | function_word_omission |  | 2.0 |  |
| tts_kp_farbank_as_furbank | kp | X/Standard | far bank | problem | construction(TTSに台本と異なる文面を読ま | vowel_swap |  | 1.2 |  |
| tts_body_threedays_as_thirteen | body | Z/Standard | "Give me three days to see my sister's wedding," | problem | construction(TTSに台本と異なる文面を読ま | number_error |  | 3.0 |  |
| tts_body_return_negation_added | body | Z/Standard | "Then I will return to you." | problem | construction(TTSに台本と異なる文面を読ま | negation_added |  | 2.5 |  |
| tts_body_melos_as_milos | body | Z/Standard | Melos said. | problem | construction(TTSに台本と異なる文面を読ま | proper_noun_misreading | Melos | 1.3 |  |