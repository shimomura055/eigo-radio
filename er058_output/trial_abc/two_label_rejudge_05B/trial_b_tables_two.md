### 全体(Primary=validator should_pass、Secondary候補=厳格PASS集合[EXACT/NORMALIZED/TRANSCRIPT_STYLE_NORMALIZED/NUMERIC_EQUIVALENCE]のみPASS)
緩い基準(should_passのみ)ではPASSだが厳格集合ではNGとなったSecondary候補転写: ja_len3_mis/azure=PHONETIC_MATCH「雪が降った。」; ja_len3_ctl/azure=PHONETIC_MATCH「雪が降った。」; ja_len3_ctl/local_medium=PHONETIC_MATCH「雪が降った」; ja_hom1_mis/azure=PHONETIC_MATCH「会議を言った。」
| 指標 | 件数 |
|---|---|
| clip総数(誤読/対照) | 73 (44/29) |
| 誤読のうち誤読の証拠あり(ASRが誤読形を聴いた/原稿と不一致のASRあり/同形異音。以下「確認済み誤読」) | 30/44 |
| 誤読のうち全ASRが原稿形で転写(未確定)+同音除外 | 14 |
| 誤PASS率(確認済み誤読, primary) | 2/30 (7%) |
| 誤NG率(対照, primary) | 1/29 (3%) |
| 誤PASS率(確認済み誤読, azure) | 2/30 (7%) |
| 誤NG率(対照, azure) | 1/29 (3%) |
| 誤PASS率(確認済み誤読, local_medium) | 3/30 (10%) |
| 誤NG率(対照, local_medium) | 3/29 (10%) |
| 誤PASS率(確認済み誤読, azure_pl) | 0/3 (0%) |
| 誤NG率(対照, azure_pl) | 0/0 |
| 統一フロー: 確認済み誤読の誤採用(Primary or Azure PASS) | 3/30 (10%) |
| うちPrimaryがNG→SecondaryのPASSで誤採用(Secondary起因) | 1 |
| 統一フロー: 対照(正しい発話)の不採用(再生成対象) | 0/29 (0%) |

### 型別(en)。誤PASS = 確認済み誤読で原稿に対しPASS判定。表記: 誤PASS/確認済み誤読(母数)
| 型 | 誤読clip | 確認済み | Primary誤PASS | Azure誤PASS | Azure+PL誤PASS | local誤PASS | 統一フロー誤採用 | 対照 | 対照誤NG(P/A/L) | 対照フロー不採用 |
|---|---|---|---|---|---|---|---|---|---|---|
| number | 4 | 4 | 0/4 (0%) | 0/4 (0%) | 0/0 | 0/4 (0%) | 0/4 | 2 | P0/2 A0/2 L0/2 | 0/2 |
| negation | 3 | 3 | 0/3 (0%) | 0/3 (0%) | 0/0 | 0/3 (0%) | 0/3 | 2 | P0/2 A0/2 L0/2 | 0/2 |
| inflection | 4 | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 3 | P0/3 A0/3 L0/3 | 0/3 |
| voicing | 2 | 1 | 0/1 (0%) | 0/1 (0%) | 0/0 | 0/1 (0%) | 0/1 | 1 | P0/1 A0/1 L0/1 | 0/1 |
| length | 2 | 2 | 0/2 (0%) | 0/2 (0%) | 0/1 (0%) | 0/2 (0%) | 0/2 | 1 | P0/1 A0/1 L0/1 | 0/1 |
| minimal_pair | 2 | 2 | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) | 0/2 | 1 | P0/1 A0/1 L0/1 | 0/1 |
| proper_noun | 3 | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 3 | P0/3 A0/3 L1/3 | 0/3 |
| homograph | 2 | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 1 | P0/1 A0/1 L0/1 | 0/1 |
| format_control | 0 | 0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 1 | P0/1 A0/1 L0/1 | 0/1 |

### 型別(ja)。誤PASS = 確認済み誤読で原稿に対しPASS判定。表記: 誤PASS/確認済み誤読(母数)
| 型 | 誤読clip | 確認済み | Primary誤PASS | Azure誤PASS | Azure+PL誤PASS | local誤PASS | 統一フロー誤採用 | 対照 | 対照誤NG(P/A/L) | 対照フロー不採用 |
|---|---|---|---|---|---|---|---|---|---|---|
| voicing | 5 | 4 | 0/4 (0%) | 1/4 (25%) | 0/0 | 1/4 (25%) | 1/4 | 3 | P0/3 A0/3 L0/3 | 0/3 |
| number | 2 | 2 | 0/2 (0%) | 0/2 (0%) | 0/0 | 0/2 (0%) | 0/2 | 1 | P0/1 A0/1 L1/1 | 0/1 |
| negation | 2 | 2 | 0/2 (0%) | 0/2 (0%) | 0/0 | 0/2 (0%) | 0/2 | 2 | P0/2 A0/2 L0/2 | 0/2 |
| form | 2 | 2 | 0/2 (0%) | 0/2 (0%) | 0/0 | 0/2 (0%) | 0/2 | 1 | P0/1 A0/1 L0/1 | 0/1 |
| length | 3 | 3 | 0/3 (0%) | 0/3 (0%) | 0/0 | 0/3 (0%) | 0/3 | 2 | P0/2 A1/2 L1/2 | 0/2 |
| proper_noun | 3 | 1 | 0/1 (0%) | 0/1 (0%) | 0/0 | 0/1 (0%) | 0/1 | 2 | P1/2 A0/2 L0/2 | 0/2 |
| homograph | 3 | 3 | 2/3 (67%) | 1/3 (33%) | 0/0 | 2/3 (67%) | 2/3 | 2 | P0/2 A0/2 L0/2 | 0/2 |
| minimal_pair | 2 | 1 | 0/1 (0%) | 0/1 (0%) | 0/0 | 0/1 (0%) | 0/1 | 1 | P0/1 A0/1 L0/1 | 0/1 |

### clip別詳細(原稿 / 話した文 / 各ASR転写→判定)
| clip | 種別 | 原稿 | 話した文 | Primary | Azure | Azure+PL | local medium | フロー | 確認 |
|---|---|---|---|---|---|---|---|---|---|
| en_ctl_us_ctl | control | US data shows costs rose. | US data shows costs rose. | U.S. data shows costs rose. [PASS:NORMALIZED_MAT] | U.S. data shows costs rose. [PASS:NORMALIZED_MAT] | - | U.S. data shows costs rose. [PASS:NORMALIZED_MAT] | ADOPT_P |  |
| en_hom1_ctl | control | I will read it tomorrow. | I will read it tomorrow. | I will read it tomorrow. [PASS:EXACT_MATCH] | I will read it tomorrow. [PASS:EXACT_MATCH] | - | I will read it tomorrow. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_hom1_mis | misread | I will read it tomorrow. | I will red it tomorrow. | I will read it tomorrow. [PASS:EXACT_MATCH] | I will read it tomorrow. [PASS:EXACT_MATCH] | - | I will read it tomorrow. [PASS:EXACT_MATCH] | ADOPT_P | unverified(全ASRが原稿形) |
| en_hom2_mis | misread | He tried to lead the team. | He tried to led the team. | He tried to lead the team. [PASS:EXACT_MATCH] | He tried to lead the team. [PASS:EXACT_MATCH] | - | He tried to lead the team. [PASS:EXACT_MATCH] | ADOPT_P | unverified(全ASRが原稿形) |
| en_inf1_ctl | control | He showed us the map. | He showed us the map. | He showed us the map. [PASS:EXACT_MATCH] | He showed us the map. [PASS:EXACT_MATCH] | - | He showed us the map. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_inf1_mis | misread | He showed us the map. | He show us the map. | He showed us the map. [PASS:EXACT_MATCH] | He showed us the map. [PASS:EXACT_MATCH] | He showed us the map. [PASS:EXACT_MATCH] | He showed us the map. [PASS:EXACT_MATCH] | ADOPT_P | unverified(全ASRが原稿形) |
| en_inf2_ctl | control | She asked me twice. | She asked me twice. | She asked me twice. [PASS:EXACT_MATCH] | She asked me twice. [PASS:EXACT_MATCH] | - | She asked me twice. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_inf2_mis | misread | She asked me twice. | She ask me twice. | She asked me twice. [PASS:EXACT_MATCH] | She asked me twice. [PASS:EXACT_MATCH] | She asked me twice. [PASS:EXACT_MATCH] | She asked me twice. [PASS:EXACT_MATCH] | ADOPT_P | unverified(全ASRが原稿形) |
| en_inf3_ctl | control | The beans are cheap. | The beans are cheap. | The beans are cheap. [PASS:EXACT_MATCH] | The beans are cheap. [PASS:EXACT_MATCH] | - | The beans are cheap. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_inf3_mis | misread | The beans are cheap. | The bean are cheap. | The beans are cheap. [PASS:EXACT_MATCH] | The beans are cheap. [PASS:EXACT_MATCH] | The beans are cheap. [PASS:EXACT_MATCH] | The beans are cheap. [PASS:EXACT_MATCH] | ADOPT_P | unverified(全ASRが原稿形) |
| en_inf4_mis | misread | Costs rose last year. | Cost rose last year. | Costs rose last year. [PASS:EXACT_MATCH] | Costs rose last year. [PASS:EXACT_MATCH] | - | Costs rose last year. [PASS:EXACT_MATCH] | ADOPT_P | unverified(全ASRが原稿形) |
| en_len1_ctl | control | The ship left early. | The ship left early. | The ship left early. [PASS:EXACT_MATCH] | The ship left early. [PASS:EXACT_MATCH] | - | The ship left early. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_len1_mis | misread | The ship left early. | The sheep left early. | The sheep left early. [NG:TRUE_CONTENT_M] | The sheep left early. [NG:TRUE_CONTENT_M] | The sheep left early. [NG:TRUE_CONTENT_M] | The sheep left early. [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| en_len2_mis | misread | They are leaving now. | They are living now. | They are living now. [NG:TRUE_CONTENT_M] | They are living now. [NG:TRUE_CONTENT_M] | - | They are living now. [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| en_min1_ctl | control | The raw bean price rose. | The raw bean price rose. | The raw bean price rose. [PASS:EXACT_MATCH] | The raw bean price rose. [PASS:EXACT_MATCH] | - | The raw bean price rose. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_min1_mis | misread | The raw bean price rose. | The robin price rose. | The Robin price rose. [NG:TRUE_CONTENT_M] | The Robin price rose. [NG:TRUE_CONTENT_M] | The Robin price rose. [NG:TRUE_CONTENT_M] | The Robin Price rose. [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| en_min2_mis | misread | We buy raw beans. | We buy robbing beans. | we buy robbing beans. [NG:TRUE_CONTENT_M] | We buy robbing beans. [NG:TRUE_CONTENT_M] | We buy robbing beans. [NG:TRUE_CONTENT_M] | We buy robbing beans. [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| en_neg1_ctl | control | She can't come today. | She can't come today. | She can't come today. [PASS:EXACT_MATCH] | She can't come today. [PASS:EXACT_MATCH] | - | She can't come today. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_neg1_mis | misread | She can't come today. | She can come today. | She can come today. [NG:TRUE_CONTENT_M] | She can come today. [NG:TRUE_CONTENT_M] | - | She can come today. [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| en_neg2_ctl | control | He did not call me. | He did not call me. | He did not call me. [PASS:EXACT_MATCH] | He did not call me. [PASS:EXACT_MATCH] | - | He did not call me. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_neg2_mis | misread | He did not call me. | He did call me. | He did call me. [NG:TRUE_CONTENT_M] | He did call me. [NG:TRUE_CONTENT_M] | - | He did call me. [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| en_neg3_mis | misread | They don't sell it. | They do sell it. | They do sell it. [NG:TRUE_CONTENT_M] | They do sell it. [NG:TRUE_CONTENT_M] | - | They do sell it. [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| en_num1_ctl | control | I waited two hours. | I waited two hours. | I waited two hours. [PASS:EXACT_MATCH] | I waited two hours. [PASS:EXACT_MATCH] | - | I waited two hours. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_num1_mis | misread | I waited two hours. | I waited three hours. | I waited three hours. [NG:TRUE_CONTENT_M] | I waited 3 hours. [NG:TRUE_CONTENT_M] | - | I waited three hours. [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| en_num2_mis | misread | We sold two cups. | We sold ten cups. | We sold ten cups. [NG:TRUE_CONTENT_M] | We sold 10 cups. [NG:TRUE_CONTENT_M] | - | We sold 10 cups. [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| en_num3_ctl | control | It took nine months. | It took nine months. | It took nine months. [PASS:EXACT_MATCH] | It took nine months. [PASS:EXACT_MATCH] | - | It took nine months. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_num3_mis | misread | It took nine months. | It took five months. | It took five months. [NG:TRUE_CONTENT_M] | It took five months. [NG:TRUE_CONTENT_M] | - | It took five months. [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| en_num4_mis | misread | She bought two bags. | She bought three bags. | She bought three bags. [NG:TRUE_CONTENT_M] | She bought 3 bags. [NG:TRUE_CONTENT_M] | - | She bought three bags [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| en_prn1_ctl | control | We met at Starbucks. | We met at Starbucks. | We met at Starbucks. [PASS:EXACT_MATCH] | We met at Starbucks. [PASS:EXACT_MATCH] | - | We met at Starbucks. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_prn1_mis | misread | We met at Starbucks. | We met at Starbacks. | We met at Starbucks. [PASS:EXACT_MATCH] | We met at Starbucks. [PASS:EXACT_MATCH] | We met at Starbucks. [PASS:EXACT_MATCH] | We met at Starbucks. [PASS:EXACT_MATCH] | ADOPT_P | unverified(全ASRが原稿形) |
| en_prn2_ctl | control | Coffee from Colombia. | Coffee from Colombia. | Coffee from Colombia. [PASS:EXACT_MATCH] | Coffee from Colombia. [PASS:EXACT_MATCH] | - | Coffee from Columbia. [NG:ASR_VALIDATION] | ADOPT_P |  |
| en_prn2_mis | misread | Coffee from Colombia. | Coffee from Columbia. | Coffee from Colombia. [PASS:EXACT_MATCH] | Coffee from Colombia. [PASS:EXACT_MATCH] | Coffee from Colombia. [PASS:EXACT_MATCH] | Coffee from Colombia [PASS:NORMALIZED_MAT] | ADOPT_P | unverified(全ASRが原稿形) |
| en_prn3_ctl | control | Beans from Ethiopia. | Beans from Ethiopia. | Beans from Ethiopia. [PASS:EXACT_MATCH] | Beans from Ethiopia. [PASS:EXACT_MATCH] | - | Beans from Ethiopia. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_prn3_mis | misread | Beans from Ethiopia. | Beans from Ethopia. | Beans from Ethiopia. [PASS:EXACT_MATCH] | Beans from Ethiopia. [PASS:EXACT_MATCH] | Beans from Ethiopia. [PASS:EXACT_MATCH] | Beans from Ethiopia. [PASS:EXACT_MATCH] | ADOPT_P | unverified(全ASRが原稿形) |
| en_voi1_ctl | control | He parked the van. | He parked the van. | He parked the van. [PASS:EXACT_MATCH] | He parked the van. [PASS:EXACT_MATCH] | - | He parked the van. [PASS:EXACT_MATCH] | ADOPT_P |  |
| en_voi1_mis | misread | He parked the van. | He barked the van. | He parked the van. [PASS:EXACT_MATCH] | He parked the van. [PASS:EXACT_MATCH] | He parked the van. [PASS:EXACT_MATCH] | He parked the van. [PASS:EXACT_MATCH] | ADOPT_P | unverified(全ASRが原稿形) |
| en_voi2_mis | misread | The price went up. | The prize went up. | The prize went up. [NG:TRUE_CONTENT_M] | The prize went up. [NG:TRUE_CONTENT_M] | - | The prize went up. [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| ja_frm1_ctl | control | とても楽しいです。 | とても楽しいです。 | とても楽しいです。 [PASS:EXACT_MATCH] | とても楽しいです。 [PASS:EXACT_MATCH] | - | とても楽しいです [PASS:NORMALIZED_MAT] | ADOPT_P |  |
| ja_frm1_mis | misread | とても楽しいです。 | とても楽しかったです。 | とても楽しかったです。 [NG:TRUE_CONTENT_M] | とても楽しかったです。 [NG:TRUE_CONTENT_M] | - | とても楽しかったです [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| ja_frm2_mis | misread | 友達と会います。 | 友達と会いました。 | 友達と会いました。 [NG:TRUE_CONTENT_M] | 友達と会いました。 [NG:TRUE_CONTENT_M] | - | 友達と会いました [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| ja_hom1_ctl | control | 会議を行った。 | 会議を行った。 | 会議を行った。 [PASS:EXACT_MATCH] | 会議を行った。 [PASS:EXACT_MATCH] | - | 会議を行った [PASS:NORMALIZED_MAT] | ADOPT_P |  |
| ja_hom1_mis | misread | 会議を行った。 | 会議をいった。 | 会議を言った。 [PASS:PHONETIC_MATCH] | 会議を言った。 [NG:PHONETIC_MATCH] | - | 会議を行った [PASS:NORMALIZED_MAT] | ADOPT_P | confirmed_misread |
| ja_hom2_ctl | control | 人気がない。 | 人気がない。 | 人気がない。 [PASS:EXACT_MATCH] | 人気がない。 [PASS:EXACT_MATCH] | - | 人気がない [PASS:NORMALIZED_MAT] | ADOPT_P |  |
| ja_hom2_mis | misread | 人気がない。 | にんきがない。 | 人気がない。 [PASS:EXACT_MATCH] | 人気がない。 [PASS:EXACT_MATCH] | - | 人気がない [PASS:NORMALIZED_MAT] | ADOPT_P | confirmed_misread_same_text_readings |
| ja_hom3_mis | misread | そこへ行った。 | そこをおこなった。 | そこを行なった。 [NG:TRUE_CONTENT_M] | そこを行った。 [NG:TRUE_CONTENT_M] | - | そこを行った [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| ja_len1_ctl | control | おじさんが来た。 | おじさんが来た。 | おじさんが来た。 [PASS:EXACT_MATCH] | おじさんが来た。 [PASS:EXACT_MATCH] | - | おじさんが来た [PASS:NORMALIZED_MAT] | ADOPT_P |  |
| ja_len1_mis | misread | おじさんが来た。 | おじいさんが来た。 | おじいさんが来た。 [NG:TRUE_CONTENT_M] | おじいさんが来た。 [NG:TRUE_CONTENT_M] | - | おじいさんが来た [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| ja_len2_mis | misread | ビルを見た。 | ビールを見た。 | ビールを見た。 [NG:TRUE_CONTENT_M] | ビールを見た。 [NG:TRUE_CONTENT_M] | - | ビールを見た [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| ja_len3_ctl | control | ゆきが降った。 | ゆきが降った。 | 雪が降った。 [PASS:PHONETIC_MATCH] | 雪が降った。 [NG:PHONETIC_MATCH] | - | 雪が降った [NG:PHONETIC_MATCH] | ADOPT_P |  |
| ja_len3_mis | misread | ゆきが降った。 | ゆうきが降った。 | 雨季が降った。 [NG:TRUE_CONTENT_M] | 雪が降った。 [NG:PHONETIC_MATCH] | - | 勇気がふった [NG:TRUE_CONTENT_M] | REJECT | divergence_evidence |
| ja_min1_ctl | control | 社外の人が来た。 | 社外の人が来た。 | 社外の人が来た。 [PASS:EXACT_MATCH] | 社外の人が来た。 [PASS:EXACT_MATCH] | - | 社外の人が来た [PASS:NORMALIZED_MAT] | ADOPT_P |  |
| ja_min1_mis | misread | 社外の人が来た。 | 社会の人が来た。 | 社会の人が来た。 [NG:ASR_VALIDATION] | 社会の人が来た。 [NG:ASR_VALIDATION] | - | 社会の人が来た [NG:ASR_VALIDATION] | REJECT | confirmed_misread |
| ja_min2_mis | misread | 仕事を紹介した。 | 仕事を照会した。 | 仕事を紹介した。 [PASS:EXACT_MATCH] | 仕事を紹介した。 [PASS:EXACT_MATCH] | - | 仕事を紹介した [PASS:NORMALIZED_MAT] | ADOPT_P | homophone_no_audio_difference |
| ja_neg1_ctl | control | 彼は来なかった。 | 彼は来なかった。 | 彼は来なかった。 [PASS:EXACT_MATCH] | 彼は来なかった。 [PASS:EXACT_MATCH] | - | 彼は来なかった [PASS:NORMALIZED_MAT] | ADOPT_P |  |
| ja_neg1_mis | misread | 彼は来なかった。 | 彼は来た。 | 彼は来た。 [NG:TRUE_CONTENT_M] | 彼は来た。 [NG:TRUE_CONTENT_M] | - | 彼は来た [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| ja_neg2_ctl | control | 行きたくない。 | 行きたくない。 | 行きたくない。 [PASS:EXACT_MATCH] | 行きたくない。 [PASS:EXACT_MATCH] | - | 行きたくない [PASS:NORMALIZED_MAT] | ADOPT_P |  |
| ja_neg2_mis | misread | 行きたくない。 | 行きたい。 | 痛い。 [NG:TRUE_CONTENT_M] | 行きたい。 [NG:TRUE_CONTENT_M] | - | 行きたい [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| ja_num1_ctl | control | 三つ買った。 | 三つ買った。 | 三つ買った。 [PASS:EXACT_MATCH] | 三つ買った。 [PASS:EXACT_MATCH] | - | 見つかった [NG:TRUE_CONTENT_M] | ADOPT_P |  |
| ja_num1_mis | misread | 三つ買った。 | 四つ買った。 | 四つ買った。 [NG:TRUE_CONTENT_M] | 四つ買った。 [NG:TRUE_CONTENT_M] | - | 4つカット [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| ja_num2_mis | misread | 二人で行った。 | 三人で行った。 | 三人で行った。 [NG:TRUE_CONTENT_M] | 3人でいた。 [NG:TRUE_CONTENT_M] | - | 3人で行った [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| ja_prn1_ctl | control | メタンが増えた。 | メタンが増えた。 | メタンが増えた。 [PASS:EXACT_MATCH] | メタンが増えた。 [PASS:EXACT_MATCH] | - | メタンが増えた [PASS:NORMALIZED_MAT] | ADOPT_P |  |
| ja_prn1_mis | misread | メタンが増えた。 | メタが増えた。 | メタが増えた。 [NG:TRUE_CONTENT_M] | メタが増えた。 [NG:TRUE_CONTENT_M] | - | メタが増えた [NG:TRUE_CONTENT_M] | REJECT | confirmed_misread |
| ja_prn2_ctl | control | スターバックスで会う。 | スターバックスで会う。 | スタバックスで会う。 [NG:TRUE_CONTENT_M] | スターバックスで会う。 [PASS:EXACT_MATCH] | - | スターバックスで会う [PASS:NORMALIZED_MAT] | ADOPT_S |  |
| ja_prn2_mis | misread | スターバックスで会う。 | スターバクスで会う。 | スターバックスで会う。 [PASS:EXACT_MATCH] | スターバックスで会う。 [PASS:EXACT_MATCH] | - | スターバックスで会う [PASS:NORMALIZED_MAT] | ADOPT_P | unverified(全ASRが原稿形) |
| ja_prn3_mis | misread | コーヒーを飲む。 | コヒーを飲む。 | コーヒーを飲む。 [PASS:EXACT_MATCH] | コーヒーを飲む。 [PASS:EXACT_MATCH] | - | コーヒーを飲む [PASS:NORMALIZED_MAT] | ADOPT_P | unverified(全ASRが原稿形) |
| ja_voi1_ctl | control | ガスが出ました。 | ガスが出ました。 | ガスが出ました。 [PASS:EXACT_MATCH] | ガスが出ました。 [PASS:EXACT_MATCH] | - | ガスが出ました [PASS:NORMALIZED_MAT] | ADOPT_P |  |
| ja_voi1_mis | misread | ガスが出ました。 | カスが出ました。 | カスが出ました。 [NG:ASR_VALIDATION] | カスが出ました。 [NG:ASR_VALIDATION] | - | カスが出ました [NG:ASR_VALIDATION] | REJECT | confirmed_misread |
| ja_voi2_ctl | control | バスが来た。 | バスが来た。 | バスが来た。 [PASS:EXACT_MATCH] | バスが来た。 [PASS:EXACT_MATCH] | - | バスが来た [PASS:NORMALIZED_MAT] | ADOPT_P |  |
| ja_voi2_mis | misread | バスが来た。 | パスが来た。 | パスが来た。 [NG:ASR_VALIDATION] | パスが来た。 [NG:ASR_VALIDATION] | - | パスが来た [NG:ASR_VALIDATION] | REJECT | confirmed_misread |
| ja_voi3_mis | misread | ゴミを捨てた。 | コミを捨てた。 | ゴミを捨てた。 [PASS:EXACT_MATCH] | ゴミを捨てた。 [PASS:EXACT_MATCH] | - | ゴミを捨てた [PASS:NORMALIZED_MAT] | ADOPT_P | unverified(全ASRが原稿形) |
| ja_voi4_mis | misread | ビルが高い。 | ヒルが高い。 | 昼が高い。 [NG:ASR_VALIDATION] | 昼が高い。 [NG:ASR_VALIDATION] | - | 昼が高い [NG:ASR_VALIDATION] | REJECT | confirmed_misread |
| ja_voi5_ctl | control | 電気をつけた。 | 電気をつけた。 | 電気をつけた。 [PASS:EXACT_MATCH] | 電気をつけた。 [PASS:EXACT_MATCH] | - | 電気をつけた。 [PASS:EXACT_MATCH] | ADOPT_P |  |
| ja_voi5_mis | misread | 電気をつけた。 | てんきをつけた。 | 点灯をつけた。 [NG:TRUE_CONTENT_M] | 電気をつけた。 [PASS:EXACT_MATCH] | - | 電気をつけた [PASS:NORMALIZED_MAT] | ADOPT_S | divergence_evidence |

### 誤PASS事例(確認済み誤読で、いずれかのASRが原稿に対しPASS)
- ja_voi5_mis / azure: 原稿「電気をつけた。」 話した「てんきをつけた。」 転写「電気をつけた。」 判定=EXACT_MATCH フロー=ADOPT_S
- ja_voi5_mis / local_medium: 原稿「電気をつけた。」 話した「てんきをつけた。」 転写「電気をつけた」 判定=NORMALIZED_MATCH フロー=ADOPT_S
- ja_hom1_mis / primary: 原稿「会議を行った。」 話した「会議をいった。」 転写「会議を言った。」 判定=PHONETIC_MATCH フロー=ADOPT_P
- ja_hom1_mis / local_medium: 原稿「会議を行った。」 話した「会議をいった。」 転写「会議を行った」 判定=NORMALIZED_MATCH フロー=ADOPT_P
- ja_hom2_mis / primary: 原稿「人気がない。」 話した「にんきがない。」 転写「人気がない。」 判定=EXACT_MATCH フロー=ADOPT_P
- ja_hom2_mis / azure: 原稿「人気がない。」 話した「にんきがない。」 転写「人気がない。」 判定=EXACT_MATCH フロー=ADOPT_P
- ja_hom2_mis / local_medium: 原稿「人気がない。」 話した「にんきがない。」 転写「人気がない」 判定=NORMALIZED_MATCH フロー=ADOPT_P

### 日本語: Primary NGの内訳とC1(entity_like)
- ja_voi1_mis: Primary=NG(ASR_VALIDATION_UNCERTAIN, entity_like=True) / Azure=NG(ASR_VALIDATION_UNCERTAIN) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_voi2_mis: Primary=NG(ASR_VALIDATION_UNCERTAIN, entity_like=True) / Azure=NG(ASR_VALIDATION_UNCERTAIN) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_voi3_mis: Primary=PASS(EXACT_MATCH, entity_like=False) / Azure=PASS(EXACT_MATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_voi4_mis: Primary=NG(ASR_VALIDATION_UNCERTAIN, entity_like=True) / Azure=NG(ASR_VALIDATION_UNCERTAIN) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_voi5_mis: Primary=NG(TRUE_CONTENT_MISMATCH, entity_like=False) / Azure=PASS(EXACT_MATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_num1_mis: Primary=NG(TRUE_CONTENT_MISMATCH, entity_like=False) / Azure=NG(TRUE_CONTENT_MISMATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_num2_mis: Primary=NG(TRUE_CONTENT_MISMATCH, entity_like=False) / Azure=NG(TRUE_CONTENT_MISMATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_neg1_mis: Primary=NG(TRUE_CONTENT_MISMATCH, entity_like=False) / Azure=NG(TRUE_CONTENT_MISMATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_neg2_mis: Primary=NG(TRUE_CONTENT_MISMATCH, entity_like=False) / Azure=NG(TRUE_CONTENT_MISMATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_frm1_mis: Primary=NG(TRUE_CONTENT_MISMATCH, entity_like=False) / Azure=NG(TRUE_CONTENT_MISMATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_frm2_mis: Primary=NG(TRUE_CONTENT_MISMATCH, entity_like=False) / Azure=NG(TRUE_CONTENT_MISMATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_len1_mis: Primary=NG(TRUE_CONTENT_MISMATCH, entity_like=False) / Azure=NG(TRUE_CONTENT_MISMATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_len2_mis: Primary=NG(TRUE_CONTENT_MISMATCH, entity_like=False) / Azure=NG(TRUE_CONTENT_MISMATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_len3_mis: Primary=NG(TRUE_CONTENT_MISMATCH, entity_like=False) / Azure=NG(PHONETIC_MATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_prn1_mis: Primary=NG(TRUE_CONTENT_MISMATCH, entity_like=False) / Azure=NG(TRUE_CONTENT_MISMATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_prn2_mis: Primary=PASS(EXACT_MATCH, entity_like=False) / Azure=PASS(EXACT_MATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_prn3_mis: Primary=PASS(EXACT_MATCH, entity_like=False) / Azure=PASS(EXACT_MATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_hom1_mis: Primary=PASS(PHONETIC_MATCH, entity_like=False) / Azure=NG(PHONETIC_MATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_hom2_mis: Primary=PASS(EXACT_MATCH, entity_like=False) / Azure=PASS(EXACT_MATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_hom3_mis: Primary=NG(TRUE_CONTENT_MISMATCH, entity_like=False) / Azure=NG(TRUE_CONTENT_MISMATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_min1_mis: Primary=NG(ASR_VALIDATION_UNCERTAIN, entity_like=True) / Azure=NG(ASR_VALIDATION_UNCERTAIN) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外
- ja_min2_mis: Primary=PASS(EXACT_MATCH, entity_like=False) / Azure=PASS(EXACT_MATCH) / 現行Productionでは Primary NG かつ entity_like=True なら SCG(Secondary)除外