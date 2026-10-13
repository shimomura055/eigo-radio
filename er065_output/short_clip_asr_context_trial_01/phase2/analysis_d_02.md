## D-1. 実データ(Production tts_generation_results 2,149 text/ASR対のうち英語2,030対)における、語境界の子音連続の型別 出現数と『綴り差が境界付近に出た割合』

母集団=Productionが実際に生成しASR照合した英語本文/Key Phrase等。『境界付近の綴り差』は同一対内の差分が境界の前後語に掛かる件数(境界と無関係な差分も含む上限値)。
| 境界の型 | 境界数 | 境界付近に綴り差 | 割合(上限) |
|---|---|---|---|
| 同一子音の重なり(s+s,t+t,d+d,n+n,l+l,k+k...) | 1841 | 163 | 8.9% |
| その他の破裂音+破裂音 | 3343 | 53 | 1.6% |
| 同位置の破裂音連続 | 877 | 24 | 2.7% |
| 歯擦音連続(s+z,z+s) | 476 | 35 | 7.4% |
| 歯擦音+口蓋歯擦音(s+sh,z+ch...) | 509 | 22 | 4.3% |
| t/d/s/z+y(did you型) | 366 | 4 | 1.1% |

## D-2. 実データの境界差分 124 instance(窓=差分語+前後1語)の判定: 現行Production vs Trial音韻判定

| Trial音韻判定 | 件数 | 現行Production判定の内訳 |
|---|---|---|
| PHON_EXPLAINED_FUSION | 15 | {'CONNECTED_SPEECH_ACCEPT': 6, 'ASR_VALIDATION_UNCERTAIN': 8, 'TRUE_CONTENT_MISMATCH': 1} |
| PHON_EXPLAINED_VOICING | 2 | {'ASR_VALIDATION_UNCERTAIN': 2} |
| PHON_HOMOPHONE_ONLY | 26 | {'NORMALIZED_MATCH': 14, 'ASR_VALIDATION_UNCERTAIN': 10, 'HOMOPHONE_MATCH_NUMBER_EXCEPTION': 1, 'CONNECTED_SPEECH_ACCEPT': 1} |
| NO_PHONOLOGICAL_EVIDENCE | 11 | {'NORMALIZED_MATCH': 1, 'TRUE_CONTENT_MISMATCH': 5, 'NUMERIC_EQUIVALENCE_MATCH': 3, 'ASR_VALIDATION_UNCERTAIN': 2} |
| NOT_EXPLAINED | 70 | {'TRUE_CONTENT_MISMATCH': 31, 'ASR_VALIDATION_UNCERTAIN': 28, 'CONNECTED_SPEECH_PASS_WITH_WARNING': 1, 'CONNECTED_SPEECH_ACCEPT': 5, 'NORMALIZED_MATCH': 2, 'TRANSCRIPT_STYLE_NORMALIZED_MATCH': 2, 'TTS_FAILURE': 1} |

### D-2a. Trialが『連結発音で説明可(FUSION/VOICING)』とした実データinstance全件と、現行Productionの扱い

| 境界の型 | canonical窓 -> ASR窓 | 現行Production | 現行CS Validator | 現行EqLayer(cheap) | Trial | 出所 |
|---|---|---|---|---|---|---|
| GEMINATE_SAME | `are modeled differences` -> `are model differences` | CONNECTED_SPEECH_ACCEPT | CONNECTED_SPEECH_ACCEPT | CONNECTED_SPEECH_ACCEPT | PHON_EXPLAINED_FUSION | er003_output\n3_01\health\b1b\audit\tts_ |
| GEMINATE_SAME,SIBILANT_SEQ | `the products stores stock` -> `the products' store stock` | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | PHON_EXPLAINED_FUSION | er014_output\user_test_news_convenience_ |
| SIBILANT_SEQ | `stores stock` -> `Store stock` | CONNECTED_SPEECH_ACCEPT | CONNECTED_SPEECH_ACCEPT | CONNECTED_SPEECH_ACCEPT | PHON_EXPLAINED_FUSION | er014_output\user_test_news_convenience_ |
| GEMINATE_SAME | `Some Muse calls` -> `Some use calls` | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | PHON_EXPLAINED_VOICING | er019_output\family_x_audio_production_w |
| SIBILANT_SEQ | `Melos said` -> `Mello said` | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | PHON_EXPLAINED_FUSION | er026_output\family_z_production_e2e_01\ |
| SIBILANT_SEQ | `The guards stopped` -> `The guard stopped` | CONNECTED_SPEECH_ACCEPT | CONNECTED_SPEECH_ACCEPT | CONNECTED_SPEECH_ACCEPT | PHON_EXPLAINED_FUSION | er026_output\family_z_production_e2e_01\ |
| SIBILANT_SEQ | `when Melos spoke` -> `when Mello spoke` | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | PHON_EXPLAINED_FUSION | er026_output\family_z_production_e2e_01\ |
| SIBILANT_SEQ | `wedding Melos smiled` -> `wedding mellow smiled` | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | PHON_EXPLAINED_FUSION | er026_output\family_z_production_e2e_01\ |
| SIBILANT_SEQ | `the guards seized` -> `the guard seized` | CONNECTED_SPEECH_ACCEPT | CONNECTED_SPEECH_ACCEPT | CONNECTED_SPEECH_ACCEPT | PHON_EXPLAINED_FUSION | er026_output\family_z_production_e2e_01\ |
| SIBILANT_SEQ | `flashed Melos struck` -> `flashed Melo struck` | CONNECTED_SPEECH_ACCEPT | CONNECTED_SPEECH_ACCEPT | CONNECTED_SPEECH_ACCEPT | PHON_EXPLAINED_FUSION | er026_output\family_z_production_e2e_01\ |
| GEMINATE_SAME | `some Muse calls` -> `some use calls` | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | PHON_EXPLAINED_VOICING | hr_queue:tier3_corroboration_secondary |
| SIBILANT_SEQ | `flood Melos searched` -> `flood Mellow searched` | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | PHON_EXPLAINED_FUSION | hr_queue:tier3_corroboration_secondary |
| SIBILANT_SEQ | `stick Melos struck` -> `stick Mello struck` | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | PHON_EXPLAINED_FUSION | hr_queue:primary_1 |
| SIBILANT_SEQ | `stick Melos struck` -> `stick Melo struck` | CONNECTED_SPEECH_ACCEPT | CONNECTED_SPEECH_ACCEPT | CONNECTED_SPEECH_ACCEPT | PHON_EXPLAINED_FUSION | hr_queue:tier3_corroboration_secondary |
| SIBILANT_SEQ | `Melos said` -> `Mellow said` | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | PHON_EXPLAINED_FUSION | hr_queue:tier3_corroboration_secondary |
| STOP_STOP_UNRELEASED | `pay showed coffee` -> `pay show coffee` | TRUE_CONTENT_MISMATCH | UNCLASSIFIED | EQUIVALENCE_LAYER_INSUFFICIENT_EVIDENCE | PHON_EXPLAINED_FUSION | er021_telemetry |
| SIBILANT_SEQ | `flood Melos searched` -> `flood Mello searched` | ASR_VALIDATION_UNCERTAIN | UNCLASSIFIED | NOT_A_PHONEME_PREFIX_DROP | PHON_EXPLAINED_FUSION | er021_telemetry |

### D-2b. Productionが連結発音として受理(CONNECTED_SPEECH_ACCEPT/PWW)したがTrialでは『説明不能』となったinstance(= Productionの綴り水準規則がTrialの音素水準より広い範囲)

- `upward group still` -> `upward groups still` (CONNECTED_SPEECH_PASS_WITH_WARNING; 理由: 複数形/三単現の接尾辞sの付替え=形態素差であり、語境界の子音融合で説明される音韻差ではない[studies/study + suggest/suggests型])
- `The studies suggest that` -> `The study suggests that` (CONNECTED_SPEECH_ACCEPT; 理由: 複数形/三単現の接尾辞sの付替え=形態素差であり、語境界の子音融合で説明される音韻差ではない[studies/study + suggest/suggests型])
- `headline numbers suggest Robots` -> `headline number suggests Robots` (CONNECTED_SPEECH_ACCEPT; 理由: 複数形/三単現の接尾辞sの付替え=形態素差であり、語境界の子音融合で説明される音韻差ではない[studies/study + suggest/suggests型])
- `a US sea blockade` -> `a U S se blockade` (CONNECTED_SPEECH_ACCEPT; 理由: 複数形/三単現の接尾辞sの付替え=形態素差であり、語境界の子音融合で説明される音韻差ではない[studies/study + suggest/suggests型])
- `a US sea blockade` -> `a U S blockade` (CONNECTED_SPEECH_ACCEPT; 理由: 複数形/三単現の接尾辞sの付替え=形態素差であり、語境界の子音融合で説明される音韻差ではない[studies/study + suggest/suggests型])
- `planned US sea blockade` -> `planned U S blockade` (CONNECTED_SPEECH_ACCEPT; 理由: 複数形/三単現の接尾辞sの付替え=形態素差であり、語境界の子音融合で説明される音韻差ではない[studies/study + suggest/suggests型])

## D-3. 一般語2語窓(Production採用済み正常音声の実境界を切出し)の3分類: 現行Production vs Trial(独立証拠なし)

正常音声(Production採用済み)を2語に切り出したclipのため、真値=『正常な連結発音』。許容=綴り一致、HR=音韻説明可だが綴り不一致、NG=連結発音で説明不能(=ASRの別語化)。
| 型 | engine | 観測 | 現行Production PASS | Trial 許容(綴り一致) | Trial HR | Trial NG(説明不能) |
|---|---|---|---|---|---|---|
| SS | openai | 24 | 12/24 (50%) | 12/24 (50%) | 1/24 (4%) | 11/24 (46%) |
| SS | azure | 8 | 4/8 (50%) | 3/8 (38%) | 1/8 (12%) | 4/8 (50%) |
| SS | whisper:small | 8 | 3/8 (38%) | 2/8 (25%) | 1/8 (12%) | 5/8 (62%) |
| SS | whisper:medium | 8 | 4/8 (50%) | 3/8 (38%) | 1/8 (12%) | 4/8 (50%) |
| TT | openai | 24 | 9/24 (38%) | 9/24 (38%) | 0/24 (0%) | 15/24 (62%) |
| TT | azure | 8 | 3/8 (38%) | 3/8 (38%) | 0/8 (0%) | 5/8 (62%) |
| TT | whisper:small | 8 | 2/8 (25%) | 2/8 (25%) | 0/8 (0%) | 6/8 (75%) |
| TT | whisper:medium | 8 | 4/8 (50%) | 4/8 (50%) | 0/8 (0%) | 4/8 (50%) |
| DD | openai | 24 | 9/24 (38%) | 7/24 (29%) | 2/24 (8%) | 15/24 (62%) |
| DD | azure | 8 | 6/8 (75%) | 6/8 (75%) | 0/8 (0%) | 2/8 (25%) |
| DD | whisper:small | 8 | 8/8 (100%) | 8/8 (100%) | 0/8 (0%) | 0/8 (0%) |
| DD | whisper:medium | 8 | 7/8 (88%) | 7/8 (88%) | 0/8 (0%) | 1/8 (12%) |
| NN | openai | 24 | 16/24 (67%) | 16/24 (67%) | 0/24 (0%) | 8/24 (33%) |
| NN | azure | 8 | 4/8 (50%) | 3/8 (38%) | 0/8 (0%) | 5/8 (62%) |
| NN | whisper:small | 8 | 2/8 (25%) | 2/8 (25%) | 0/8 (0%) | 6/8 (75%) |
| NN | whisper:medium | 8 | 3/8 (38%) | 3/8 (38%) | 0/8 (0%) | 5/8 (62%) |
| YOD | openai | 24 | 10/24 (42%) | 10/24 (42%) | 0/24 (0%) | 14/24 (58%) |
| YOD | azure | 8 | 2/8 (25%) | 1/8 (12%) | 0/8 (0%) | 7/8 (88%) |
| YOD | whisper:small | 8 | 3/8 (38%) | 3/8 (38%) | 0/8 (0%) | 5/8 (62%) |
| YOD | whisper:medium | 8 | 3/8 (38%) | 3/8 (38%) | 0/8 (0%) | 5/8 (62%) |
| SHS | openai | 24 | 6/24 (25%) | 3/24 (12%) | 0/24 (0%) | 21/24 (88%) |
| SHS | azure | 8 | 5/8 (62%) | 4/8 (50%) | 0/8 (0%) | 4/8 (50%) |
| SHS | whisper:small | 8 | 2/8 (25%) | 2/8 (25%) | 0/8 (0%) | 6/8 (75%) |
| SHS | whisper:medium | 8 | 2/8 (25%) | 1/8 (12%) | 0/8 (0%) | 7/8 (88%) |
| CTRL | openai | 24 | 15/24 (62%) | 12/24 (50%) | 2/24 (8%) | 10/24 (42%) |
| CTRL | azure | 8 | 4/8 (50%) | 3/8 (38%) | 1/8 (12%) | 4/8 (50%) |
| CTRL | whisper:small | 8 | 7/8 (88%) | 5/8 (62%) | 0/8 (0%) | 3/8 (38%) |
| CTRL | whisper:medium | 8 | 7/8 (88%) | 5/8 (62%) | 0/8 (0%) | 3/8 (38%) |

融合型(SS/TT/DD/NN/YOD/SHS)全体 n=288: 現行Production PASS 129/288 (45%) / Trial 許容 117/288 (41%) / HR 6/288 (2%) / NG 165/288 (57%)
対照(CTRL) n=48: 現行Production PASS 33/48 (69%) / Trial 許容 25/48 (52%) / HR 3/48 (6%) / NG 20/48 (42%)

### D-3a. 融合型で綴り不一致になった観測の全列挙(正常音声のASR別綴り/脱落)

| 型 | engine | canonical -> ASR | 現行Production | Trial音韻 | Trial 3分類 | 現行CS Validator |
|---|---|---|---|---|---|---|
| DD | azure | `and drying` -> `and dry` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| DD | openai | `and drying` -> `quick and dry` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| DD | openai | `shared desks` -> `to your desks` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| DD | openai | `shared desks` -> `sheer deaths` | TTS_FAILURE | NOT_EXPLAINED | NG | UNCLASSIFIED |
| DD | azure | `assigned desks` -> `assigns desks` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| DD | openai | `assigned desks` -> `assign desks` | CONNECTED_SPEECH_ACCEPT | PHON_EXPLAINED_FUSION | HR | CONNECTED_SPEECH_ACCEPT |
| DD | openai | `assigned desks` -> `assign desk` | TTS_FAILURE | NOT_EXPLAINED | NG | CONNECTED_SPEECH_ACCEPT |
| DD | openai | `shared desks` -> `shared desk` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| DD | openai | `and daily` -> `late and daily` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| DD | openai | `and daily` -> `ate and daily` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| DD | openai | `and do` -> `and do you` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| NN | azure | `listen notice` -> `listen no` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| NN | whisper:medium | `listen notice` -> `you listen` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| NN | whisper:small | `listen notice` -> `listen note` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| NN | whisper:small | `pattern not` -> `pattern` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| NN | azure | `expectation not` -> `expectation` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| NN | whisper:medium | `expectation not` -> `and expectation` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| NN | azure | `design needs` -> `design need` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| NN | openai | `win Next` -> `next` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| NN | azure | `association not` -> `an association not` | NORMALIZED_MATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| NN | openai | `association not` -> `association non` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| NN | openai | `association not` -> `association` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| NN | azure | `pattern not` -> `` | EMPTY | NOT_EXPLAINED | NG | - |
| NN | whisper:medium | `listen notice` -> `if you listen notice` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | azure | `researchers changed` -> `researchers change` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | whisper:medium | `researchers changed` -> `the researchers changed their minds and decided to go back to the lab` | TTS_FAILURE | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | azure | `evidence shows` -> `the evidence shows` | NORMALIZED_MATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | openai | `use shared` -> `will you share` | TTS_FAILURE | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | openai | `use shared` -> `i'll use share` | TTS_FAILURE | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | whisper:medium | `use shared` -> `we'll use share` | TTS_FAILURE | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | whisper:small | `use shared` -> `` | EMPTY | NOT_EXPLAINED | NG | - |
| SHS | azure | `choice changes` -> `choice change` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | openai | `choice changes` -> `all choices change` | TTS_FAILURE | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | openai | `choice changes` -> `all choice change` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | openai | `choice changes` -> `all choice changed` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | whisper:medium | `choice changes` -> `all choice changes` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | openai | `coverage Small` -> `in coverage` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | whisper:medium | `coverage Small` -> `coverage` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | azure | `makes checking` -> `makes check` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | openai | `makes checking` -> `he makes checking` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SHS | openai | `makes checking` -> `he makes check` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | azure | `this small` -> `by this small` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | whisper:small | `These studies` -> `these study` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | azure | `his sister's` -> `his sisters` | NORMALIZED_MATCH | PHON_HOMOPHONE_ONLY | HR | UNCLASSIFIED |
| SS | azure | `users stayed` -> `top users state` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | openai | `users stayed` -> `top users stay` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | whisper:small | `users stayed` -> `users state` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | azure | `affects someone` -> `` | EMPTY | NOT_EXPLAINED | NG | - |
| SS | openai | `affects someone` -> `the facts someone` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | openai | `affects someone` -> `the effects someone` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | whisper:medium | `affects someone` -> `affect someone` | CONNECTED_SPEECH_ACCEPT | PHON_EXPLAINED_FUSION | HR | CONNECTED_SPEECH_ACCEPT |
| SS | openai | `tests some` -> `altaz some` | TRUE_CONTENT_MISMATCH | NO_PHONOLOGICAL_EVIDENCE | HR | UNCLASSIFIED |
| SS | openai | `tests some` -> `altas` | TTS_FAILURE | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | openai | `tests some` -> `multitasks some` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | whisper:medium | `tests some` -> `` | EMPTY | NOT_EXPLAINED | NG | - |
| SS | whisper:small | `tests some` -> `tests` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | whisper:medium | `times so` -> `different times so let's get started` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | whisper:small | `times so` -> `times` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | azure | `these situations` -> `in these situations` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| SS | whisper:medium | `these situations` -> `in these situations change is necessary` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | openai | `meant to` -> `meant to be` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | whisper:small | `meant to` -> `meant` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | azure | `different to` -> `different different differe` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | openai | `different to` -> `is different to you` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | openai | `different to` -> `is different to` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | whisper:medium | `different to` -> `different` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | azure | `restaurant tipping` -> `restaurant tip` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | azure | `without telling` -> `` | EMPTY | NOT_EXPLAINED | NG | - |
| TT | openai | `without telling` -> `this without telling` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | openai | `without telling` -> `this is without telling` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | whisper:small | `without telling` -> `news without telling` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | azure | `market to` -> `` | EMPTY | NOT_EXPLAINED | NG | - |
| TT | whisper:medium | `market to` -> `market` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | openai | `what to` -> `decide what to` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | openai | `what to` -> `decide what to believe` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | azure | `sunlight touched` -> `sunlight touch` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| TT | openai | `sunlight touched` -> `sunlight touches` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | azure | `what you` -> `` | EMPTY | NOT_EXPLAINED | NG | - |
| YOD | azure | `what users` -> `and what use` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | openai | `what users` -> `and what you` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | whisper:medium | `what you` -> `but what you` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | openai | `not use` -> `not using` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | whisper:small | `not use` -> `not used` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | azure | `end you` -> `the end you` | NORMALIZED_MATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | openai | `end you` -> `in the end you` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | whisper:small | `end you` -> `the end` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | azure | `that users` -> `that use` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | openai | `that users` -> `it's that you` | TTS_FAILURE | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | whisper:medium | `that users` -> `is that use` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | whisper:small | `that users` -> `is that you` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | azure | `end you'll` -> `` | EMPTY | NOT_EXPLAINED | NG | - |
| YOD | openai | `end you'll` -> `and you'll` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | openai | `end you'll` -> `in the end you'll` | ASR_VALIDATION_UNCERTAIN | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | whisper:small | `end you'll` -> `the end you're` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |
| YOD | azure | `It used` -> `it use` | TRUE_CONTENT_MISMATCH | NOT_EXPLAINED | NG | UNCLASSIFIED |

## D-4. 反例(真値既知)の判定: 誤って『許容』にされないか

出所: 委任_01 synthetic(既知欠陥を編集した音声)・natural_ng proxy・Melos 反例ASR。独立証拠を最大(音響OK+別engine一致)と仮定しても許容になるかを見る。
既知欠陥の観測に対し、Trial規則が**新たに**許容を増やすか(増分誤許容 = 現行ProductionがPASSにしない観測のうち、Trial(独立証拠最大)が許容にした数)を見る。
| 群/欠陥種別 | 観測数 | 現行Production PASS(既存の誤許容) | Trial許容(証拠なし) | Trial許容(証拠最大) | 増分誤許容(証拠最大, 現行非PASS->許容) | 増分(例) |
|---|---|---|---|---|---|---|
| synthetic/synthetic_final_consonant_loss | 150 | 122 | 103 | 132 | 19 | [('Melos said.', 'mello said'), ('Melos said.', 'mellow said')] |
| synthetic/synthetic_missing_word | 26 | 0 | 0 | 0 | 0 | [] |
| synthetic/synthetic_wrong_name | 15 | 0 | 0 | 0 | 0 | [] |
| synthetic/intact_control | 33 | 25 | 22 | 28 | 5 | [('Melos said.', 'mello said'), ('Melos said.', 'mellow said')] |
| natural_ng/proper_noun_mispronounced | 39 | 0 | 0 | 0 | 0 | [] |
| natural_ng/final_consonant_added | 34 | 23 | 22 | 22 | 0 | [] |
| natural_ng/context_guessable_homophone | 31 | 28 | 28 | 28 | 0 | [] |
| natural_ng/final_consonant_drop | 13 | 1 | 1 | 1 | 0 | [] |
| natural_ng/content_mispronounced | 8 | 0 | 0 | 0 | 0 | [] |

既知欠陥(intact_control除く)に対する増分誤許容 合計: **19** 件。intact_controlは欠陥のない対照で、増分許容=正しい救済。
注: syn_B1_trunc*(`said`語末の切詰)は`Melos`のs+s領域に欠陥が無く、ASR転写はintactと同一(`mello said`)。Trial規則は語末切詰を検出も誤許容の増分も生まない(現行と同じ『ASR文字列では検出されない』限界はそのまま)。