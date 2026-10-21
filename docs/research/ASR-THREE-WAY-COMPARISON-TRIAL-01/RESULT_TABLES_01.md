## A. 評価データ構成(重複除外後)

| tier | KP | 本文 | 計 | 音声秒(合計) |
|---|---|---|---|---|
| N_human | 28 | 29 | 57 | 469s |
| N_constructed | 0 | 6 | 6 | 17s |
| P_human | 1 | 0 | 1 | 1s |
| P_constructed | 5 | 12 | 17 | 39s |
| P_splice | 2 | 8 | 10 | 37s |

label x family x level: normal/X/Advanced=12; normal/X/Standard=18; normal/Z/Advanced=10; normal/Z/Standard=23; problem/X/Advanced=2; problem/X/Standard=6; problem/Z/Standard=20

Phrase List(Ledger hint)有の音声: 24件 (KPは0件=全KPがPL空)。

## B. 構成ラベル音声の監査(3方式の転写 vs 台本/読ませた文面)

| id | 誤り種別 | 台本(canonical) | 読ませた文面 | OpenAI(prod) | Azure(prod) | Whisper | 全方式が台本一致=ラベル疑義 |
|---|---|---|---|---|---|---|---|
| spl_body_almost_deleted | word_omission_meaning_change | "I almost lost my trust in you," | (splice) | I almost lost my trust in you. | I almost lost my trust in you. | I almost lost my trust in you. | 疑義 |
| spl_body_not_deleted | negation_omitted | As you listen, pay attention to who will | (splice) | As you listen, pay attention to who will not  | As you listen, pay attention to who will not  | As you listen, pay attention to who won't att |  |
| spl_kp_in_deleted | kp_function_word_omission | lose trust in someone | (splice) | Lose trust someone | Lose trust someone. | Lose trust someone |  |
| spl_body_late_deleted | word_omission_meaning_change | "Your friend must stay here. Return late | (splice) | Your friend must stay here, return, and he wi | Your friend must stay here. Return and he wil | Your friend must stay here, return, and he wi |  |
| spl_body_sword_duplicated | word_repetition_added | "Put the sword down and free both men." | (splice) | Put the sword down and free both men. | Put the sword sword down and free both men. | Put the sore sore down and free both men. |  |
| spl2_body_almost_deleted | word_omission_meaning_change | "I almost lost my trust in you," | (splice) | I just lost my trust in you. | I almost lost my trust in you. | I almost lost my trust in you. |  |
| spl2_body_not_deleted | negation_omitted | As you listen, pay attention to who will | (splice) | As you listen, pay attention to who will atta | As you listen, pay attention to who will atta | As you listen, pay attention to who won't att |  |
| spl2_kp_in_deleted | kp_function_word_omission | lose trust in someone | (splice) | Lose trust someone. | Lose trust someone. | Lose trust on one. |  |
| spl2_body_late_deleted | word_omission_meaning_change | "Your friend must stay here. Return late | (splice) | Your friend must stay here, return, and he wi | Your friend must stay here, returned, and he  | Your friend must stay here. Retreat, and he w |  |
| spl2_body_sword_duplicated | word_repetition_added | "Put the sword down and free both men." | (splice) | Put the sword down and free both men. | Put the sword sword down and free both men. | Put the sore sore down and free both men. |  |
| tts_kp_takepart_as_tart | consonant_swap(p->t) | take part | take tart | Take tart. | Take Tart. | Take Tart. |  |
| tts_kp_weaken_as_weekend | vowel/consonant_confusion(real_store_suspect) | weaken | weekend | Weekend. | Weekend. | Weekend? |  |
| tts_kp_turnon_as_turnoff | meaning_change_word_swap | turn on | turn off | Turn off? | Turn off. | Turn off. |  |
| tts_kp_makerewardsmaller_omit_a | function_word_omission | make a reward smaller | make reward smaller | Make rewards smaller. | Make rewards smaller. | Make rewards smaller. |  |
| tts_kp_farbank_as_furbank | vowel_swap | far bank | fur bank | For bank? | For bank. | for bank? |  |
| tts_body_threedays_as_thirteen | number_error | "Give me three days to see my sister's w | "Give me thirteen days to see my sister' | Give me thirteen days to see my sister's wedd | Give me 13 days to see my sister's wedding. | Give me 13 days to see my sister's wedding. |  |
| tts_body_return_negation_added | negation_added | "Then I will return to you." | "Then I will not return to you." | Then I will not return to you. | Then I will not return to you. | Then, I will not return to you. |  |
| tts_body_melos_as_milos | proper_noun_misreading | Melos said. | Milos said. | Milo said. | Milo said. | Milo said. |  |

## C. Phase 1(中立条件: OpenAI prompt無し・Azure Phrase List無し)単体verdict
(verdict=Production分類器`val.classify_asr_match`+`_step_alternate_pass`を転写に適用。NG=その方式単独ではPASSさせない)

### KP / 条件=neutral

| tier | n | OpenAI gpt-4o-mini-transcribe: PASS/NG(NG=検出) | Azure Speech en-US: PASS/NG(NG=検出) | faster-whisper small: PASS/NG(NG=検出) | faster-whisper medium(追加): PASS/NG(NG=検出) |
|---|---|---|---|---|---|
| N_human | 28 | PASS 23 / NG 5 | PASS 27 / NG 1 | PASS 26 / NG 2 | PASS 28 / NG 0 |
| P_human | 1 | PASS 0 / NG 1 | PASS 0 / NG 1 | PASS 0 / NG 1 | PASS 0 / NG 1 |
| P_constructed | 5 | PASS 0 / NG 5 | PASS 0 / NG 5 | PASS 0 / NG 5 | PASS 0 / NG 5 |
| P_splice | 2 | PASS 0 / NG 2 | PASS 0 / NG 2 | PASS 0 / NG 2 | PASS 0 / NG 2 |

### BODY / 条件=neutral

| tier | n | OpenAI gpt-4o-mini-transcribe: PASS/NG(NG=検出) | Azure Speech en-US: PASS/NG(NG=検出) | faster-whisper small: PASS/NG(NG=検出) | faster-whisper medium(追加): PASS/NG(NG=検出) |
|---|---|---|---|---|---|
| N_human | 29 | PASS 19 / NG 10 | PASS 21 / NG 8 | PASS 22 / NG 7 | PASS 21 / NG 8 |
| N_constructed | 6 | PASS 0 / NG 6 | PASS 2 / NG 4 | PASS 2 / NG 4 | PASS 1 / NG 5 |
| P_constructed | 12 | PASS 0 / NG 12 | PASS 1 / NG 11 | PASS 1 / NG 11 | PASS 0 / NG 12 |
| P_splice | 8 | PASS 4 / NG 4 | PASS 3 / NG 5 | PASS 4 / NG 4 | PASS 4 / NG 4 |

## D. Phase 2(Production運用条件: OpenAI KP=Production prompt・Azure=Ledger hint有ならPhrase List重み2.0)単体verdict

### KP / 条件=prod

| tier | n | OpenAI gpt-4o-mini-transcribe: PASS/NG(NG=検出) | Azure Speech en-US: PASS/NG(NG=検出) | faster-whisper small: PASS/NG(NG=検出) | faster-whisper medium(追加): PASS/NG(NG=検出) |
|---|---|---|---|---|---|
| N_human | 28 | PASS 28 / NG 0 | PASS 27 / NG 1 | PASS 26 / NG 2 | PASS 28 / NG 0 |
| P_human | 1 | PASS 0 / NG 1 | PASS 0 / NG 1 | PASS 0 / NG 1 | PASS 0 / NG 1 |
| P_constructed | 5 | PASS 0 / NG 5 | PASS 0 / NG 5 | PASS 0 / NG 5 | PASS 0 / NG 5 |
| P_splice | 2 | PASS 0 / NG 2 | PASS 0 / NG 2 | PASS 0 / NG 2 | PASS 0 / NG 2 |

### BODY / 条件=prod

| tier | n | OpenAI gpt-4o-mini-transcribe: PASS/NG(NG=検出) | Azure Speech en-US: PASS/NG(NG=検出) | faster-whisper small: PASS/NG(NG=検出) | faster-whisper medium(追加): PASS/NG(NG=検出) |
|---|---|---|---|---|---|
| N_human | 29 | PASS 19 / NG 10 | PASS 23 / NG 6 | PASS 22 / NG 7 | PASS 21 / NG 8 |
| N_constructed | 6 | PASS 0 / NG 6 | PASS 5 / NG 1 | PASS 2 / NG 4 | PASS 1 / NG 5 |
| P_constructed | 12 | PASS 0 / NG 12 | PASS 2 / NG 10 | PASS 1 / NG 11 | PASS 0 / NG 12 |
| P_splice | 8 | PASS 4 / NG 4 | PASS 3 / NG 5 | PASS 4 / NG 4 | PASS 4 / NG 4 |

### 文字起こし正確性(正常音声のみ、canonicalとの正規化WER/CER、Production条件)

| 種別 | openai WER平均/CER平均/完全一致 | azure WER平均/CER平均/完全一致 | whisper WER平均/CER平均/完全一致 | whisper_medium WER平均/CER平均/完全一致 |
|---|---|---|---|---|
| kp N_human(n=28) | 0.071 / 0.000 / 26/28 | 0.045 / 0.002 / 26/28 | 0.045 / 0.014 / 26/28 | 0.000 / 0.000 / 28/28 |
| body N_human(n=29) | 0.046 / 0.019 / 19/29 | 0.049 / 0.029 / 20/29 | 0.048 / 0.017 / 19/29 | 0.047 / 0.019 / 19/29 |

### 種別別(Production条件, 正常=N_human+N_constructed のPASS率 / 問題=NG検出率、tag別)

| tag | 正常n | openai 正常PASS | azure 正常PASS | whisper 正常PASS | whisper_medium 正常PASS | 問題n | openai 問題検出 | azure 問題検出 | whisper 問題検出 | whisper_medium 問題検出 |
|---|---|---|---|---|---|---|---|---|---|---|
| number | 12 | 7/12 (58%) | 8/12 (67%) | 8/12 (67%) | 7/12 (58%) | 0 | n/a | n/a | n/a | n/a |
| negation | 12 | 7/12 (58%) | 9/12 (75%) | 9/12 (75%) | 8/12 (67%) | 0 | n/a | n/a | n/a | n/a |
| proper_noun | 27 | 14/27 (52%) | 22/27 (81%) | 18/27 (67%) | 17/27 (63%) | 9 | 9/9 (100%) | 7/9 (78%) | 8/9 (89%) | 9/9 (100%) |
| hyphen_or_contraction | 16 | 10/16 (62%) | 12/16 (75%) | 12/16 (75%) | 11/16 (69%) | 0 | n/a | n/a | n/a | n/a |
| kp_single_word | 9 | 9/9 (100%) | 9/9 (100%) | 8/9 (89%) | 9/9 (100%) | 0 | n/a | n/a | n/a | n/a |
| kp_short_2w | 8 | 8/8 (100%) | 8/8 (100%) | 8/8 (100%) | 8/8 (100%) | 1 | 1/1 (100%) | 1/1 (100%) | 1/1 (100%) | 1/1 (100%) |
| kp_phrase_3w+ | 11 | 11/11 (100%) | 10/11 (91%) | 10/11 (91%) | 11/11 (100%) | 0 | n/a | n/a | n/a | n/a |
| body_short | 12 | 9/12 (75%) | 10/12 (83%) | 10/12 (83%) | 9/12 (75%) | 0 | n/a | n/a | n/a | n/a |
| body_mid | 9 | 7/9 (78%) | 9/9 (100%) | 8/9 (89%) | 9/9 (100%) | 0 | n/a | n/a | n/a | n/a |
| body_long | 8 | 3/8 (38%) | 4/8 (50%) | 4/8 (50%) | 3/8 (38%) | 0 | n/a | n/a | n/a | n/a |
| hr_approved_hard | 6 | 1/6 (17%) | 2/6 (33%) | 3/6 (50%) | 1/6 (17%) | 0 | n/a | n/a | n/a | n/a |

### Family/Level別(Production条件、正常PASS率 / 問題NG検出率)

| group | 正常n | openai | azure | whisper | whisper_medium | 問題n | openai | azure | whisper | whisper_medium |
|---|---|---|---|---|---|---|---|---|---|---|
| family=X | 30 | 25/30 (83%) | 27/30 (90%) | 26/30 (87%) | 26/30 (87%) | 8 | 7/8 (88%) | 7/8 (88%) | 6/8 (75%) | 6/8 (75%) |
| family=Z | 33 | 22/33 (67%) | 28/33 (85%) | 24/33 (73%) | 24/33 (73%) | 20 | 17/20 (85%) | 16/20 (80%) | 17/20 (85%) | 18/20 (90%) |
| level=Standard | 41 | 27/41 (66%) | 35/41 (85%) | 32/41 (78%) | 29/41 (71%) | 26 | 23/26 (88%) | 22/26 (85%) | 23/26 (88%) | 24/26 (92%) |
| level=Advanced | 22 | 20/22 (91%) | 20/22 (91%) | 18/22 (82%) | 21/22 (95%) | 2 | 1/2 (50%) | 1/2 (50%) | 0/2 (0%) | 0/2 (0%) |

### Phrase List有無(Azure、Ledger hint有の音声のみ。N_human+N_constructed正常の転写PASS)

| 条件 | 正常PASS | 問題NG検出 |
|---|---|---|
| Azure PLなし(neutral) | 3/14 (21%) | 9/10 (90%) |
| Azure PL重み2.0(prod) | 8/14 (57%) | 8/10 (80%) |

### OpenAI KP: Production prompt有無の差(KPのみ、全KP)

- neutral: 正常PASS 23/28 (82%) / 問題NG検出 8/8 (100%)
- prod: 正常PASS 28/28 (100%) / 問題NG検出 8/8 (100%)

## E. 安定性(同一音声の反復: 短尺KP 20本 x 3回、Production条件。独立音声の検証ではない)

| 方式 | 対象音声数 | 転写が3回とも同一 | 転写が変動した音声 | verdict(PASS/NG)が反転した音声 |
|---|---|---|---|---|
| OpenAI gpt-4o-mini-transcribe | 20 | 14 | 6 | 0 |
| Azure Speech en-US | 20 | 20 | 0 | 0 |
| faster-whisper small | 20 | 20 | 0 | 0 |
| faster-whisper medium(追加) | 0 | 0 | 0 | 0 |

変動実例:
- openai kp_boredom_a2_1 (canonical='meanness'): ['Meanness', 'Meanness.', 'Meanness.'] verdict=[True, True, True]
- openai kp_boredom_b1b_5 (canonical='stone video'): ['Stone Video.', 'Stone video.', 'Stone video.'] verdict=[True, True, True]
- openai kp_yemen_b1b_5 (canonical='intercept'): ['Intercept', 'intercept', 'Intercept'] verdict=[True, True, True]
- openai spl2_kp_in_deleted (canonical='lose trust in someone'): ['Lose trust someone.', 'Lose trust someone.', 'lose trust someone'] verdict=[False, False, False]
- openai spl_kp_in_deleted (canonical='lose trust in someone'): ['Lose trust someone', 'Lose trust someone.', 'Lose trust someone.'] verdict=[False, False, False]
- openai tts_kp_takepart_as_tart (canonical='take part'): ['Take tart.', 'TakeTart.', 'Take tart.'] verdict=[False, False, False]

## F. 処理速度(音声1本あたり、実測)

| 方式 | KP平均wall(s) | 本文平均wall(s) | 本文 wall/音声秒 | 備考 |
|---|---|---|---|---|
| OpenAI gpt-4o-mini-transcribe | 0.65 | 1.04 | 0.112 | API(6並列ThreadPool実行時の個別wall) |
| Azure Speech en-US | 0.72 | 3.86 | 0.416 | API(6並列ThreadPool実行時の個別wall) |
| faster-whisper small | 1.81 | 2.63 | 0.284 | CPU時間/音声秒(本文)=1.12 |
| faster-whisper medium(追加) | 5.30 | 7.50 | 0.807 | CPU時間/音声秒(本文)=3.19 |

Whisper同時実行(別process、同一24音声[各8秒以下]、モデルロード込み、16論理CPU):
- 2process: 全体wall 36.455s vs 直列合計43.714s(モデルロード別)、1件平均wall 2.842s(直列1.82s)、process別CPU時間 [135.016, 134.484]
- 4process: 全体wall 36.63s vs 直列合計43.714s(モデルロード別)、1件平均wall 5.473s(直列1.82s)、process別CPU時間 [115.516, 120.516, 120.484, 119.766]

## G. Phase 3 構成別の最終判定(Production判定関数をそのまま呼ぶ。入替構成は現行ルール流用の参考値)

### G-1 混同行列(正常/問題 x PASS/NG)、tier別

| 構成 | N_human: 正PASS/過剰NG | N_constr: 正PASS/過剰NG | P_human(take part): 誤PASS/検出 | P_constructed(TTS+plw): 誤PASS/検出 | P_splice(参考): 誤PASS/検出 | 正常全体の過剰NG率 | 問題全体の誤PASS率 | Secondary(Azure/OpenAI)呼出率 |
|---|---|---|---|---|---|---|---|---|
| C1 現行 OpenAI→Azure | 53/4 (n=57) | 5/1 (n=6) | 0/1 (n=1) | 2/15 (n=17) | 5/5 (n=10) | 5/63 (8%) | 2/18 (11%) | 38% |
| C1d 現行+両方PASS必須 | 51/6 (n=57) | 5/1 (n=6) | 0/1 (n=1) | 2/15 (n=17) | 3/7 (n=10) | 7/63 (11%) | 2/18 (11%) | 97% |
| C1dK KPのみ両方PASS必須(本文は現行) | 52/5 (n=57) | 5/1 (n=6) | 0/1 (n=1) | 2/15 (n=17) | 5/5 (n=10) | 6/63 (10%) | 2/18 (11%) | 69% |
| C2 Azure→OpenAI | 52/5 (n=57) | 5/1 (n=6) | 0/1 (n=1) | 2/15 (n=17) | 5/5 (n=10) | 6/63 (10%) | 2/18 (11%) | 29% |
| C3 Whisper→OpenAI | 52/5 (n=57) | 3/3 (n=6) | 0/1 (n=1) | 1/16 (n=17) | 6/4 (n=10) | 8/63 (13%) | 1/18 (6%) | 35% |
| C4 Whisper→Azure | 53/4 (n=57) | 5/1 (n=6) | 0/1 (n=1) | 2/15 (n=17) | 4/6 (n=10) | 5/63 (8%) | 2/18 (11%) | 35% |
| C5 現行+Whisper不一致時のみSecondary必須 | 52/5 (n=57) | 5/1 (n=6) | 0/1 (n=1) | 2/15 (n=17) | 3/7 (n=10) | 6/63 (10%) | 2/18 (11%) | 46% |
| C5K KPのみWhisper不一致時Secondary必須(本文は現行) | 52/5 (n=57) | 5/1 (n=6) | 0/1 (n=1) | 2/15 (n=17) | 5/5 (n=10) | 6/63 (10%) | 2/18 (11%) | 41% |
| C3m Whisper medium→OpenAI | 53/4 (n=57) | 2/4 (n=6) | 0/1 (n=1) | 0/17 (n=17) | 6/4 (n=10) | 8/63 (13%) | 0/18 (0%) | 34% |
| C4m Whisper medium→Azure | 53/4 (n=57) | 5/1 (n=6) | 0/1 (n=1) | 2/15 (n=17) | 4/6 (n=10) | 5/63 (8%) | 2/18 (11%) | 34% |
| C5m 現行+Whisper medium不一致時Secondary必須 | 52/5 (n=57) | 5/1 (n=6) | 0/1 (n=1) | 2/15 (n=17) | 3/7 (n=10) | 6/63 (10%) | 2/18 (11%) | 45% |

(各セルは `PASS数/NG数` [正常]または `誤PASS数/検出数` [問題]。splice(P_splice)は語の欠落が切断断片で残る可能性がありラベル確度が低いため、headlineの誤PASS率には含めない。)

### G-2 種別別(Phase 3、C1/C1d/C3/C4 のみ。KP/本文、family、問題種別)

| 区分 | C1 過剰NG/正常n | C1d 過剰NG/正常n | C1dK 過剰NG/正常n | C2 過剰NG/正常n | C3 過剰NG/正常n | C4 過剰NG/正常n | C5 過剰NG/正常n | C5K 過剰NG/正常n | C3m 過剰NG/正常n | C4m 過剰NG/正常n | C5m 過剰NG/正常n |
|---|---|---|---|---|---|---|---|---|---|---|---|
| KP正常 | 0/28 | 1/28 | 1/28 | 0/28 | 0/28 | 1/28 | 1/28 | 1/28 | 0/28 | 0/28 | 0/28 |
| 本文正常 | 5/35 | 6/35 | 5/35 | 6/35 | 8/35 | 4/35 | 5/35 | 5/35 | 8/35 | 5/35 | 6/35 |
| 本文正常 Family X | 2/12 | 3/12 | 2/12 | 3/12 | 2/12 | 2/12 | 2/12 | 2/12 | 3/12 | 3/12 | 3/12 |
| 本文正常 Family Z | 3/23 | 3/23 | 3/23 | 3/23 | 6/23 | 2/23 | 3/23 | 3/23 | 5/23 | 2/23 | 3/23 |
| Std正常 | 5/41 | 5/41 | 5/41 | 5/41 | 6/41 | 4/41 | 5/41 | 5/41 | 8/41 | 4/41 | 5/41 |
| Adv正常 | 0/22 | 2/22 | 1/22 | 1/22 | 2/22 | 1/22 | 1/22 | 1/22 | 0/22 | 1/22 | 1/22 |

| 問題区分(splice除く) | C1 誤PASS/n | C1d 誤PASS/n | C1dK 誤PASS/n | C2 誤PASS/n | C3 誤PASS/n | C4 誤PASS/n | C5 誤PASS/n | C5K 誤PASS/n | C3m 誤PASS/n | C4m 誤PASS/n | C5m 誤PASS/n |
|---|---|---|---|---|---|---|---|---|---|---|---|
| consonant_swap | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| proper_noun_misreading | 2/10 | 2/10 | 2/10 | 2/10 | 1/10 | 2/10 | 2/10 | 2/10 | 0/10 | 2/10 | 2/10 |
| vowel/consonant_confusion | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| meaning_change_word_swap | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| function_word_omission | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| vowel_swap | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| number_error | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| negation_added | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |

### G-3 誤PASS実例(問題音声がPASSした)と過剰NG実例(正常音声がNGになった)、構成別


**C1 現行 OpenAI→Azure** — 誤PASS 7件 / 過剰NG 5件
誤PASS:
- [P_constructed] plw_NM_P3_mullos_Aoede_take1 state=PASS_WITH_WARNING/secondary_confirmed | 台本『The man waiting at the gate was Melos.』 | Primary『The man waiting at the gate was Mellos.』 | Secondary『The man waiting at the gate was Melos.』
- [P_constructed] plw_NM_P4_mullos_Aoede_take1 state=PASS_WITH_WARNING/secondary_confirmed | 台本『Then Melos walked away.』 | Primary『Then Molos walked away.』 | Secondary『Then Melos walked away.』
- [P_splice] spl_body_almost_deleted state=PASS/primary_pass | 台本『"I almost lost my trust in you,"』 | Primary『I almost lost my trust in you.』 | Secondary『I almost lost my trust in you.』
- [P_splice] spl_body_not_deleted state=PASS/primary_pass | 台本『As you listen, pay attention to who will not attac』 | Primary『As you listen, pay attention to who will not attack the』 | Secondary『As you listen, pay attention to who will not attack the』
- [P_splice] spl_body_sword_duplicated state=PASS/primary_pass | 台本『"Put the sword down and free both men."』 | Primary『Put the sword down and free both men.』 | Secondary『Put the sword sword down and free both men.』
- [P_splice] spl2_body_almost_deleted state=PASS_WITH_WARNING/secondary_confirmed | 台本『"I almost lost my trust in you,"』 | Primary『I just lost my trust in you.』 | Secondary『I almost lost my trust in you.』
- [P_splice] spl2_body_sword_duplicated state=PASS/primary_pass | 台本『"Put the sword down and free both men."』 | Primary『Put the sword down and free both men.』 | Secondary『Put the sword sword down and free both men.』
過剰NG:
- [N_human] hr_run_e2e_04_a2_full_story_part3_c1 state=NG_BOTH/secondary_not_accepted | 台本『He remembered the hands held out for the chains. H』 | Primary『He remembered the hands held out for the chains. His fr』 | Secondary『He remembered the hands held out for the chains. His fr』
- [N_human] hr_run_e2e_02_a2_full_story_part1_c5 state=NG_BOTH/secondary_not_accepted | 台本『Melos said.』 | Primary『Mellis said.』 | Secondary『Mallow said.』
- [N_human] hr_space_weapons_a2_full_story_part1 state=NG_BOTH/secondary_not_accepted | 台本『The most important question in the new space-secur』 | Primary『The most important question in the new space security s』 | Secondary『The most important question in the new space security s』
- [N_human] hr_tiny_bags_a2_full_story_part2 state=NG_BOTH/secondary_not_accepted | 台本『The same pattern appeared in 2026. Small pouches a』 | Primary『The same pattern appeared in 2026. Small pouches appear』 | Secondary『The same pattern appeared in 2026. Small pouches appear』
- [N_constructed] plw_P1_nonsib_Aoede_take1 state=NG_BOTH/secondary_not_accepted | 台本『Melos drank deeply from the cold stream.』 | Primary『Mellos drink deeply from the cold stream.』 | Secondary『Mellow strength deeply from the cold stream.』

**C1d 現行+両方PASS必須** — 誤PASS 5件 / 過剰NG 7件
誤PASS:
- [P_constructed] plw_NM_P3_mullos_Aoede_take1 state=PASS_WITH_WARNING/secondary_confirmed | 台本『The man waiting at the gate was Melos.』 | Primary『The man waiting at the gate was Mellos.』 | Secondary『The man waiting at the gate was Melos.』
- [P_constructed] plw_NM_P4_mullos_Aoede_take1 state=PASS_WITH_WARNING/secondary_confirmed | 台本『Then Melos walked away.』 | Primary『Then Molos walked away.』 | Secondary『Then Melos walked away.』
- [P_splice] spl_body_almost_deleted state=PASS/force_secondary_agreed | 台本『"I almost lost my trust in you,"』 | Primary『I almost lost my trust in you.』 | Secondary『I almost lost my trust in you.』
- [P_splice] spl_body_not_deleted state=PASS/force_secondary_agreed | 台本『As you listen, pay attention to who will not attac』 | Primary『As you listen, pay attention to who will not attack the』 | Secondary『As you listen, pay attention to who will not attack the』
- [P_splice] spl2_body_almost_deleted state=PASS_WITH_WARNING/secondary_confirmed | 台本『"I almost lost my trust in you,"』 | Primary『I just lost my trust in you.』 | Secondary『I almost lost my trust in you.』
過剰NG:
- [N_human] kp_melos_b1b_1 state=NG_BOTH/secondary_not_accepted | 台本『sentence someone to death』 | Primary『Sentence someone to death.』 | Secondary『Sentenced someone to death.』
- [N_human] body_boredom_b1b_full_story_part1 state=NG_BOTH/secondary_value_diff | 台本『A stone. Still a stone. Surely something will happ』 | Primary『A stone. Still a stone. Surely something will happen so』 | Secondary『A stone. Still a stone. Surely something will happen so』
- [N_human] hr_run_e2e_04_a2_full_story_part3_c1 state=NG_BOTH/secondary_not_accepted | 台本『He remembered the hands held out for the chains. H』 | Primary『He remembered the hands held out for the chains. His fr』 | Secondary『He remembered the hands held out for the chains. His fr』
- [N_human] hr_run_e2e_02_a2_full_story_part1_c5 state=NG_BOTH/secondary_not_accepted | 台本『Melos said.』 | Primary『Mellis said.』 | Secondary『Mallow said.』
- [N_human] hr_space_weapons_a2_full_story_part1 state=NG_BOTH/secondary_not_accepted | 台本『The most important question in the new space-secur』 | Primary『The most important question in the new space security s』 | Secondary『The most important question in the new space security s』
- [N_human] hr_tiny_bags_a2_full_story_part2 state=NG_BOTH/secondary_not_accepted | 台本『The same pattern appeared in 2026. Small pouches a』 | Primary『The same pattern appeared in 2026. Small pouches appear』 | Secondary『The same pattern appeared in 2026. Small pouches appear』
- [N_constructed] plw_P1_nonsib_Aoede_take1 state=NG_BOTH/secondary_not_accepted | 台本『Melos drank deeply from the cold stream.』 | Primary『Mellos drink deeply from the cold stream.』 | Secondary『Mellow strength deeply from the cold stream.』

**C2 Azure→OpenAI** — 誤PASS 7件 / 過剰NG 6件
誤PASS:
- [P_constructed] plw_NM_P3_mullos_Aoede_take1 state=PASS/primary_pass | 台本『The man waiting at the gate was Melos.』 | Primary『The man waiting at the gate was Melos.』 | Secondary『The man waiting at the gate was Mellos.』
- [P_constructed] plw_NM_P4_mullos_Aoede_take1 state=PASS/primary_pass | 台本『Then Melos walked away.』 | Primary『Then Melos walked away.』 | Secondary『Then Molos walked away.』
- [P_splice] spl_body_almost_deleted state=PASS/primary_pass | 台本『"I almost lost my trust in you,"』 | Primary『I almost lost my trust in you.』 | Secondary『I almost lost my trust in you.』
- [P_splice] spl_body_not_deleted state=PASS/primary_pass | 台本『As you listen, pay attention to who will not attac』 | Primary『As you listen, pay attention to who will not attack the』 | Secondary『As you listen, pay attention to who will not attack the』
- [P_splice] spl_body_sword_duplicated state=PASS_WITH_WARNING/secondary_confirmed | 台本『"Put the sword down and free both men."』 | Primary『Put the sword sword down and free both men.』 | Secondary『Put the sword down and free both men.』
- [P_splice] spl2_body_almost_deleted state=PASS/primary_pass | 台本『"I almost lost my trust in you,"』 | Primary『I almost lost my trust in you.』 | Secondary『I just lost my trust in you.』
- [P_splice] spl2_body_sword_duplicated state=PASS_WITH_WARNING/secondary_confirmed | 台本『"Put the sword down and free both men."』 | Primary『Put the sword sword down and free both men.』 | Secondary『Put the sword down and free both men.』
過剰NG:
- [N_human] body_boredom_b1b_full_story_part1 state=NG_PROTECTED/p1_value_diff | 台本『A stone. Still a stone. Surely something will happ』 | Primary『A stone. Still a stone. Surely something will happen so』 | Secondary『A stone. Still a stone. Surely something will happen so』
- [N_human] hr_run_e2e_04_a2_full_story_part3_c1 state=NG_BOTH/secondary_not_accepted | 台本『He remembered the hands held out for the chains. H』 | Primary『He remembered the hands held out for the chains. His fr』 | Secondary『He remembered the hands held out for the chains. His fr』
- [N_human] hr_run_e2e_02_a2_full_story_part1_c5 state=NG_BOTH/secondary_not_accepted | 台本『Melos said.』 | Primary『Mallow said.』 | Secondary『Mellis said.』
- [N_human] hr_space_weapons_a2_full_story_part1 state=NG_BOTH/secondary_not_accepted | 台本『The most important question in the new space-secur』 | Primary『The most important question in the new space security s』 | Secondary『The most important question in the new space security s』
- [N_human] hr_tiny_bags_a2_full_story_part2 state=NG_BOTH/secondary_not_accepted | 台本『The same pattern appeared in 2026. Small pouches a』 | Primary『The same pattern appeared in 2026. Small pouches appear』 | Secondary『The same pattern appeared in 2026. Small pouches appear』
- [N_constructed] plw_P1_nonsib_Aoede_take1 state=NG_BOTH/secondary_not_accepted | 台本『Melos drank deeply from the cold stream.』 | Primary『Mellow strength deeply from the cold stream.』 | Secondary『Mellos drink deeply from the cold stream.』

**C3 Whisper→OpenAI** — 誤PASS 7件 / 過剰NG 8件
誤PASS:
- [P_constructed] plw_NM_P3_mullos_Aoede_take1 state=PASS/primary_pass | 台本『The man waiting at the gate was Melos.』 | Primary『The man waiting at the gate was Melos.』 | Secondary『The man waiting at the gate was Mellos.』
- [P_splice] spl_body_almost_deleted state=PASS/primary_pass | 台本『"I almost lost my trust in you,"』 | Primary『I almost lost my trust in you.』 | Secondary『I almost lost my trust in you.』
- [P_splice] spl_body_not_deleted state=PASS/primary_pass | 台本『As you listen, pay attention to who will not attac』 | Primary『As you listen, pay attention to who won't attack the Ho』 | Secondary『As you listen, pay attention to who will not attack the』
- [P_splice] spl_body_sword_duplicated state=PASS_WITH_WARNING/secondary_confirmed | 台本『"Put the sword down and free both men."』 | Primary『Put the sore sore down and free both men.』 | Secondary『Put the sword down and free both men.』
- [P_splice] spl2_body_almost_deleted state=PASS/primary_pass | 台本『"I almost lost my trust in you,"』 | Primary『I almost lost my trust in you.』 | Secondary『I just lost my trust in you.』
- [P_splice] spl2_body_not_deleted state=PASS/primary_pass | 台本『As you listen, pay attention to who will not attac』 | Primary『As you listen, pay attention to who won't attack the Ho』 | Secondary『As you listen, pay attention to who will attack the Hou』
- [P_splice] spl2_body_sword_duplicated state=PASS_WITH_WARNING/secondary_confirmed | 台本『"Put the sword down and free both men."』 | Primary『Put the sore sore down and free both men.』 | Secondary『Put the sword down and free both men.』
過剰NG:
- [N_human] body_melos_b1b_full_story_part1_c9 state=NG_BOTH/secondary_not_accepted | 台本『Melos turned to his friend, but before he could sp』 | Primary『Nellos turned to his friend, but before he could speak,』 | Secondary『Mellos turned to his friend, but before he could speak,』
- [N_human] body_melos_b1b_comment_1 state=NG_BOTH/secondary_not_accepted | 台本『Listen for what Melos promises before he leaves.』 | Primary『Listen for what Mello's promises before he leaves.』 | Secondary『Listen for what Mello promises before he leaves.』
- [N_human] hr_run_e2e_04_a2_full_story_part3_c1 state=NG_BOTH/secondary_not_accepted | 台本『He remembered the hands held out for the chains. H』 | Primary『He remembered the hands held out for the chains. His fr』 | Secondary『He remembered the hands held out for the chains. His fr』
- [N_human] hr_space_weapons_a2_full_story_part1 state=NG_BOTH/secondary_not_accepted | 台本『The most important question in the new space-secur』 | Primary『The most important question in the new space security s』 | Secondary『The most important question in the new space security s』
- [N_human] hr_tiny_bags_a2_full_story_part2 state=NG_BOTH/secondary_not_accepted | 台本『The same pattern appeared in 2026. Small pouches a』 | Primary『The same pattern appeared in 2026. Small pouches appear』 | Secondary『The same pattern appeared in 2026. Small pouches appear』
- [N_constructed] plw_P1_nonsib_Aoede_take1 state=NG_BOTH/secondary_not_accepted | 台本『Melos drank deeply from the cold stream.』 | Primary『Mellow strength deeply from the cold stream.』 | Secondary『Mellos drink deeply from the cold stream.』
- [N_constructed] plw_P4_mid_Aoede_take1 state=NG_BOTH/secondary_not_accepted | 台本『Then Melos walked away.』 | Primary『Then, mellows walked away.』 | Secondary『Then Mellos walked away.』
- [N_constructed] plw_P5_repeat_Aoede_take1 state=NG_BOTH/secondary_not_accepted | 台本『Melos spoke, and Melos listened.』 | Primary『Mello spoke and Mello's listened.』 | Secondary『Mella spoke, and Mella listened.』

**C4 Whisper→Azure** — 誤PASS 6件 / 過剰NG 5件
誤PASS:
- [P_constructed] plw_NM_P3_mullos_Aoede_take1 state=PASS/primary_pass | 台本『The man waiting at the gate was Melos.』 | Primary『The man waiting at the gate was Melos.』 | Secondary『The man waiting at the gate was Melos.』
- [P_constructed] plw_NM_P4_mullos_Aoede_take1 state=PASS_WITH_WARNING/secondary_confirmed | 台本『Then Melos walked away.』 | Primary『Then, Molo's walked away.』 | Secondary『Then Melos walked away.』
- [P_splice] spl_body_almost_deleted state=PASS/primary_pass | 台本『"I almost lost my trust in you,"』 | Primary『I almost lost my trust in you.』 | Secondary『I almost lost my trust in you.』
- [P_splice] spl_body_not_deleted state=PASS/primary_pass | 台本『As you listen, pay attention to who will not attac』 | Primary『As you listen, pay attention to who won't attack the Ho』 | Secondary『As you listen, pay attention to who will not attack the』
- [P_splice] spl2_body_almost_deleted state=PASS/primary_pass | 台本『"I almost lost my trust in you,"』 | Primary『I almost lost my trust in you.』 | Secondary『I almost lost my trust in you.』
- [P_splice] spl2_body_not_deleted state=PASS/primary_pass | 台本『As you listen, pay attention to who will not attac』 | Primary『As you listen, pay attention to who won't attack the Ho』 | Secondary『As you listen, pay attention to who will attack the Hou』
過剰NG:
- [N_human] kp_melos_b1b_1 state=NG_BOTH/secondary_not_accepted | 台本『sentence someone to death』 | Primary『Sentenced someone to death.』 | Secondary『Sentenced someone to death.』
- [N_human] hr_run_e2e_04_a2_full_story_part3_c1 state=NG_BOTH/secondary_not_accepted | 台本『He remembered the hands held out for the chains. H』 | Primary『He remembered the hands held out for the chains. His fr』 | Secondary『He remembered the hands held out for the chains. His fr』
- [N_human] hr_space_weapons_a2_full_story_part1 state=NG_BOTH/secondary_not_accepted | 台本『The most important question in the new space-secur』 | Primary『The most important question in the new space security s』 | Secondary『The most important question in the new space security s』
- [N_human] hr_tiny_bags_a2_full_story_part2 state=NG_BOTH/secondary_not_accepted | 台本『The same pattern appeared in 2026. Small pouches a』 | Primary『The same pattern appeared in 2026. Small pouches appear』 | Secondary『The same pattern appeared in 2026. Small pouches appear』
- [N_constructed] plw_P1_nonsib_Aoede_take1 state=NG_BOTH/secondary_not_accepted | 台本『Melos drank deeply from the cold stream.』 | Primary『Mellow strength deeply from the cold stream.』 | Secondary『Mellow strength deeply from the cold stream.』

**C5 現行+Whisper不一致時のみSecondary必須** — 誤PASS 5件 / 過剰NG 6件
誤PASS:
- [P_constructed] plw_NM_P3_mullos_Aoede_take1 state=PASS_WITH_WARNING/secondary_confirmed | 台本『The man waiting at the gate was Melos.』 | Primary『The man waiting at the gate was Mellos.』 | Secondary『The man waiting at the gate was Melos.』
- [P_constructed] plw_NM_P4_mullos_Aoede_take1 state=PASS_WITH_WARNING/secondary_confirmed | 台本『Then Melos walked away.』 | Primary『Then Molos walked away.』 | Secondary『Then Melos walked away.』
- [P_splice] spl_body_almost_deleted state=PASS/primary_pass | 台本『"I almost lost my trust in you,"』 | Primary『I almost lost my trust in you.』 | Secondary『I almost lost my trust in you.』
- [P_splice] spl_body_not_deleted state=PASS/primary_pass | 台本『As you listen, pay attention to who will not attac』 | Primary『As you listen, pay attention to who will not attack the』 | Secondary『As you listen, pay attention to who will not attack the』
- [P_splice] spl2_body_almost_deleted state=PASS_WITH_WARNING/secondary_confirmed | 台本『"I almost lost my trust in you,"』 | Primary『I just lost my trust in you.』 | Secondary『I almost lost my trust in you.』
過剰NG:
- [N_human] kp_melos_b1b_1 state=NG_BOTH/secondary_not_accepted | 台本『sentence someone to death』 | Primary『Sentence someone to death.』 | Secondary『Sentenced someone to death.』
- [N_human] hr_run_e2e_04_a2_full_story_part3_c1 state=NG_BOTH/secondary_not_accepted | 台本『He remembered the hands held out for the chains. H』 | Primary『He remembered the hands held out for the chains. His fr』 | Secondary『He remembered the hands held out for the chains. His fr』
- [N_human] hr_run_e2e_02_a2_full_story_part1_c5 state=NG_BOTH/secondary_not_accepted | 台本『Melos said.』 | Primary『Mellis said.』 | Secondary『Mallow said.』
- [N_human] hr_space_weapons_a2_full_story_part1 state=NG_BOTH/secondary_not_accepted | 台本『The most important question in the new space-secur』 | Primary『The most important question in the new space security s』 | Secondary『The most important question in the new space security s』
- [N_human] hr_tiny_bags_a2_full_story_part2 state=NG_BOTH/secondary_not_accepted | 台本『The same pattern appeared in 2026. Small pouches a』 | Primary『The same pattern appeared in 2026. Small pouches appear』 | Secondary『The same pattern appeared in 2026. Small pouches appear』
- [N_constructed] plw_P1_nonsib_Aoede_take1 state=NG_BOTH/secondary_not_accepted | 台本『Melos drank deeply from the cold stream.』 | Primary『Mellos drink deeply from the cold stream.』 | Secondary『Mellow strength deeply from the cold stream.』

### G-4 区分別の混同行列(Wilson95%区間付き)。KPと本文を分け、HR難例(人間が個別承認した6本)を除いた『通常記事音声』も併記

| 構成 | KP正常 過剰NG | KP問題(human+constructed) 誤PASS | 本文 通常記事音声(HR難例除く) 過剰NG | 本文 HR難例+plw正常 過剰NG | 本文問題(TTS+plw+human, splice除く) 誤PASS |
|---|---|---|---|---|---|
| C1 現行 OpenAI→Azure | 0/28 [0-12%] | 0/6 [0-39%] | 0/24 [0-14%] | 5/11 [21-72%] | 2/12 [5-45%] |
| C1d 現行+両方PASS必須 | 1/28 [1-18%] | 0/6 [0-39%] | 1/24 [1-20%] | 5/11 [21-72%] | 2/12 [5-45%] |
| C1dK KPのみ両方PASS必須(本文は現行) | 1/28 [1-18%] | 0/6 [0-39%] | 0/24 [0-14%] | 5/11 [21-72%] | 2/12 [5-45%] |
| C2 Azure→OpenAI | 0/28 [0-12%] | 0/6 [0-39%] | 1/24 [1-20%] | 5/11 [21-72%] | 2/12 [5-45%] |
| C3 Whisper→OpenAI | 0/28 [0-12%] | 0/6 [0-39%] | 2/24 [2-26%] | 6/11 [28-79%] | 1/12 [1-35%] |
| C4 Whisper→Azure | 1/28 [1-18%] | 0/6 [0-39%] | 0/24 [0-14%] | 4/11 [15-65%] | 2/12 [5-45%] |
| C5 現行+Whisper不一致時のみSecondary必須 | 1/28 [1-18%] | 0/6 [0-39%] | 0/24 [0-14%] | 5/11 [21-72%] | 2/12 [5-45%] |
| C5K KPのみWhisper不一致時Secondary必須(本文は現行) | 1/28 [1-18%] | 0/6 [0-39%] | 0/24 [0-14%] | 5/11 [21-72%] | 2/12 [5-45%] |
| C3m Whisper medium→OpenAI | 0/28 [0-12%] | 0/6 [0-39%] | 0/24 [0-14%] | 8/11 [43-90%] | 0/12 [0-24%] |
| C4m Whisper medium→Azure | 0/28 [0-12%] | 0/6 [0-39%] | 1/24 [1-20%] | 4/11 [15-65%] | 2/12 [5-45%] |
| C5m 現行+Whisper medium不一致時Secondary必須 | 0/28 [0-12%] | 0/6 [0-39%] | 1/24 [1-20%] | 5/11 [21-72%] | 2/12 [5-45%] |

## H. 1記事セット換算(記事B構成: KP 10音声[計11.5秒]、英語本文 Std5+Adv10=15セグメント[計388.7秒])

実測回帰(wall秒 = a + b×音声秒): OpenAI gpt-4o-mini-transcribe: a=0.67, b=0.034; Azure Speech en-US: a=-0.17, b=0.450; faster-whisper small: a=1.52, b=0.128; faster-whisper medium(追加): a=4.20, b=0.392。Whisper CPU時間=1.47s/音声秒。OpenAI実測原価=KP約JPY0.0070/回・本文約JPY0.0434/回(トークン実測)。

前提: 1記事セット=KP10+本文15の初回検証(再生成なし)を基準。構成別のSecondary呼出率は本Trialの通常記事音声(N_human)での実測(KP/本文別)。過剰NG→TTS再生成は『過剰NG率×音声のTTS原価』(Standard同期単価$6/M・25tok/s、Batchはその半額)。

| 構成 | ASR API原価/記事(JPY) | 検査時間/記事(直列合計, 秒) | うちWhisper CPU時間(秒) | 過剰NG期待数(KP/本文)[通常記事音声のレート] | 過剰NG由来の追加TTS原価(JPY, Standard単価) | HR到達期待(独立仮定の下限〜過剰NGが全枠NG確定の上限) |
|---|---|---|---|---|---|---|
| C1 現行 OpenAI→Azure | 6.18 (Secondary率 KP0%/本文31%) | 84 | 0 | 0.00/0.00 | 0.000 | 0.000〜0.00 |
| C1d 現行+両方PASS必須 | 19.08 (Secondary率 KP100%/本文100%) | 207 | 0 | 0.36/0.62 | 0.399 | 0.001〜0.98 |
| C1dK KPのみ両方PASS必須(本文は現行) | 6.94 (Secondary率 KP100%/本文31%) | 88 | 0 | 0.36/0.00 | 0.010 | 0.000〜0.36 |
| C2 Azure→OpenAI | 18.45 (Secondary率 KP4%/本文14%) | 180 | 0 | 0.00/0.62 | 0.389 | 0.001〜0.62 |
| C3 Whisper→OpenAI | 0.14 (Secondary率 KP7%/本文21%) | 95 | 590 | 0.00/1.25 | 0.777 | 0.009〜1.25 |
| C4 Whisper→Azure | 3.70 (Secondary率 KP7%/本文21%) | 125 | 590 | 0.36/0.00 | 0.010 | 0.000〜0.36 |
| C5 現行+Whisper不一致時のみSecondary必須 | 7.45 (Secondary率 KP7%/本文38%) | 185 | 590 | 0.36/0.00 | 0.010 | 0.000〜0.36 |
| C5K KPのみWhisper不一致時Secondary必須(本文は現行)【委任_02再計算】 | 6.26 (Secondary率 KP8.4%[Store 333件実測、OFFLINE_C5K_TRIGGER_RATE_01.md]/本文31%) | 約85 (C1 84+Azure約0.6) | 0 (Whisperは既存の吃音QAで実行済み=追加なし。旧値17は追加費用ではない) | 0.36/0.00 | 0.010 | 0.000〜0.36(再生成ループ込みの上限側は未評価) |
| C3m Whisper medium→OpenAI | 0.11 (Secondary率 KP0%/本文17%) | 266 | 1694 | 0.00/0.00 | 0.000 | 0.000〜0.00 |
| C4m Whisper medium→Azure | 3.03 (Secondary率 KP0%/本文17%) | 292 | 1694 | 0.00/0.62 | 0.389 | 0.001〜0.62 |
| C5m 現行+Whisper medium不一致時Secondary必須 | 8.00 (Secondary率 KP0%/本文41%) | 364 | 1694 | 0.00/0.62 | 0.389 | 0.001〜0.62 |

注: 時間は『各音声を1件ずつ直列に検査した場合の合計』(Productionは音声生成と検査が交互のため近似)。API方式は並列化可能(本Trialの221呼出を6スレッドで69秒=1呼出あたり実効0.31秒)。Whisperは別process同時実行でも約1.2倍の短縮に留まる(smallが自身で複数CPUスレッドを使うため)。


委任_02注: C5K行は`OFFLINE_C5K_TRIGGER_RATE_01.md`の発動率8.4%で再計算(旧: 101秒/CPU17秒/KP7%。R-08)。本文列(Phase 3本文)は`segment_id=None`等の条件差により参考値(R-06)。HR到達期待の上限は再生成ループ込みで未実測(R-05)。
## I. 『take part』旧NG音声(ユーザー聴感tart)×10回独立実行(旧Trial FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01の保存転写)にPhase 3構成を適用(同一音声の反復=安定性の証拠、独立10音声ではない)

OpenAI Primaryの転写分布(旧Trial 10回): 『Take part.』x3, 『Take tart.』x6, 『Take heart.』x1。Azure 10/10『Take Tart.』、Whisper small 10/10『Take Tarte.』。本Trial今回の再測定(OpenAI x4=『Take tart.』4/4、Azure x3、Whisper x3 同様)も整合。

| 構成 | 誤PASS(見逃し)/10 | 検出NG/10 | 備考 |
|---|---|---|---|
| C1 現行 OpenAI→Azure | 3 | 7 | OpenAI PASS時はSecondary不要のため見逃す |
| C1d 現行+両方PASS必須 | 0 | 10 | force_secondaryでAzureが常に拒否 |
| C2 Azure→OpenAI | 3 | 7 | Azure Primary NG後のOpenAI Secondaryが『part』で許容集合PASS |
| C3 Whisper→OpenAI | 3 | 7 | Whisper NG後のOpenAI Secondaryが『part』で救済 |
| C4 Whisper→Azure | 0 | 10 | Whisper NG後のAzure Secondaryが拒否 |
| C5 現行+Whisper不一致時のみSecondary必須 | 0 | 10 | Whisper不一致でforce_secondary→Azure拒否 |

含意: 『OpenAIが合意すればPASS』となる構成(C1/C2/C3)は、OpenAIが言語priorで『part』と補正する確率(旧Trial 3/10)だけ誤PASSする。Azureの拒否を必須にする構成(C1d/C4/C5)は本音声では10/10検出。ただしAzureが常に正しい保証はなく、本音声1本の観測(Azureはこの音声で10/10 tart)に限る。

## J. Whisper small→medium(容量由来の確認、追加1サイズ)

| 区分 | small PASS→medium PASS | small PASS→medium NG | small NG→medium PASS | small NG→medium NG |
|---|---|---|---|---|
| normal/kp | 26 | 0 | 2 | 0 |
| normal/body | 18 | 6 | 4 | 7 |
| problem/kp | 0 | 0 | 0 | 8 |
| problem/body | 4 | 1 | 0 | 15 |

改善例: kp_yemen_a2_4: small『WEEKEND』→medium『Weaken.』; kp_melos_b1b_1: small『Sentenced someone to death.』→medium『Sentence someone to death.』; body_melos_b1b_full_story_part1_c9: small『Nellos turned to his friend, b』→medium『Melos turned to his friend, bu』; body_melos_b1b_comment_1: small『Listen for what Mello's promis』→medium『Listen for what Melos promises』; body_yemen_b1b_full_story_part3: small『It is like someone saying, I w』→medium『It is like someone saying, I w』; plw_P4_mid_Aoede_take1: small『Then, mellows walked away.』→medium『Then, Melos walked away.』

medium処理時間: 1件平均 6.63s(small 2.20s)、CPU 4.23s/音声秒(small 1.47)。