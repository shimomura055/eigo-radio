# TRIAL_B_INTENTIONAL_MISREAD_01(日英共通の意図的誤読テスト、2026-10-12、Trial限定・Production変更なし)

管理ID: ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04B(ユーザー承認: 費用約15〜20円、2026-10-12)。
実費 **JPY 12.52**(予算20円以内。`cost_actual_B_01.json`: TTS 3.99 / Azure 7.44 / OpenAI ASR 1.10。Azureは初回実行中断時の送信済み分10秒を保守的に加算済み)。
script: `er058_trial_b_intentional_misread_01.py`(`--mode mock`乾式→`--mode real --approved-budget-jpy 20`)、集計 `er058_trial_b_analyze_01.py`。結果 `trial_b_results_01.json` / `trial_b_summary_01.json` / `trial_b_tables_01.md`、実行ログ `trial_b_run_log_01.txt`・`_02.txt`、音声sha256 `audio_sha256_B_01.txt`(音声実体 `audio/*.wav` はgit非管理)。

## 0. 結論(先に)

### Q1. 「Secondary PASSを原則自動採用して安全か」: **条件付きで可。ただし「Secondaryが危険」ではなく「ASR(Primary/Secondary/local全て)では検出できない型が別にある」ことが本体**
- 証拠のある誤読30クリップ(誤読44のうち、いずれかのASRが原稿と不一致、または読み上同形異音)で、**Secondary(Azure、Phrase Listなし・厳格PASS集合)が原稿へ丸めて誤PASSした例は2件(2/30)、うちPrimary NG→Secondary PASSで誤採用に至ったのは1件**(`ja_voi5`: 原稿「電気をつけた」/話した「てんきをつけた」、Primary「点灯をつけた」NG、Azure「電気をつけた」PASS。ただし本クリップは全ASRが原稿形に近いためTTSが実際に何と読んだかは未確定=要試聴)。もう1件は同形異音の`ja_hom2`(Primaryも同時にPASS)。
- 数値・否定・語形(です/でした)・長音・最小対語(ship/sheep、robin、prize、living)・濁点(ガス/カス、バス/パス、ビル/ヒル)は、**Primary・Azure・local mediumの3系統すべてが誤読形を逐語で転写し、Validatorが正しくNG**(誤PASS 0件)。Azureは原稿を知らないため丸めず、特に`ガス→カス`(g8型)は3モデルとも`カス`と転写した。→ **g8のC1(entity_like)除外を外してSecondaryに送っても、この標本では誤PASSは出なかった**(Primary NG+entity_like=Trueの4本は全て真の誤読で、Azureも全てNG)。
- 統一フロー(Primary→NG→Secondary→どちらかPASSで採用)で、**正しい発話(対照29本)を誤って不採用にしたのは0本**(Primary偽NG 1本[`ja_prn2_ctl` スタバックス]はAzureが救済)。
- 注意(最重要の限界): 誤読44本中**14本は、Primary・Azure・local medium全てが「原稿どおりの形」で転写**した(下記Q2)。これは(a)TTSが誤った綴りを読まずに正しい形で読んだ、(b)3系統のASRが言語モデルで同じ方向に丸めた、のどちらかで、**ASRだけでは区別できない**。ground truth(人間試聴)は未実施で、これらは「未確定(要試聴)」。

### Q2. 「型別に例外が必要か」: **必要。ただし「Secondaryを呼ぶ/呼ばない」の分岐ではなく、「ASR PASSでも自動確定しない型」の例外として必要**
共通ルール(Primary→Secondary→どちらかPASSで採用)でも防げない型と、具体例(全て`trial_b_tables_01.md`の転写付き):
| 型 | 具体的に防げなかった事例(原稿→話した形→全ASR転写) | 共通ルールで防げない理由 |
|---|---|---|
| 英語の語尾 -ed/-s 脱落 | `showed→show`、`asked→ask`、`beans→bean`、`costs→cost`(4/4本) | 3系統とも原稿形(showed等)で転写。テキストASRのLM priorが活用形を補正、または TTSが正しく読んだ。Secondary/localを足しても同じ結果で、独立した証拠にならない。 |
| 英語の固有名詞綴り | `Starbucks→Starbacks`、`Colombia→Columbia`、`Ethiopia→Ethopia`(3/3本) | 同上。固有名詞のASRは正しい綴りへ寄る(Phrase List無しでも)。 |
| 英語の同形異音 | `read→red`、`lead→led`(2/2本) | 発音差はASR出力(綴り)に現れない。 |
| 英語 voicing(1/2) | `parked→barked`(全ASRが`parked`) | 同上(未確定)。`price→prize`は3系統とも検出。 |
| 日本語の同形異音(読み未指定の漢字) | `会議を行った`/`いった`(Primary・Azureが`言った`と転写しPHONETIC_MATCH=Primaryは通過、localは`行った`)、`人気がない`/`にんき`(全ASR `人気`) | ASR出力は漢字表記で読みが落ちる。`人気`の読み(にんき/ひとけ)は原稿側にも無い。 |
| 日本語の濁点・カタカナ(一部) | `ゴミ→コミ`、`スターバックス→スターバクス`、`コーヒー→コヒー`(3本とも全ASRが原稿形) | 一般語・既知語へLM補正(未確定)。一方 `ガス/カス`、`バス/パス`、`ビル/ヒル` は検出できた(3/3)ので型内でも差が大きい。 |
| 同音語 | `紹介→照会`(しょうかい) | 音声上区別不能で誤読ですらない(集計から除外)。 |
→ 結論: Secondary PASSを自動採用するかどうかとは独立に、**-ed/-s・固有名詞・同形異音・一部の濁点は「ASR PASS=正しい発音」とは言えない**。承認済み原則「ASR consensus ≠ pronunciation verification」の範囲が、日本語の一般カタカナ語と英語の語形変化にも及ぶことを、この標本は示す(M6の`PASS_WITH_WARNING`→試聴リスト連動の根拠)。

## 1. 設計(8-3-A準拠、規模は予算に合わせ縮小)
- TTS: `gemini-3.8-flash-lite-tts`(**Production同一・最新世代**)、`make_speech_metadata_call_fn`(Production経路の関数)を直接呼び、cost_loggerは未install(Production telemetry/queue/attempt_history/Master Store 無書込)。英語は Charon/Aoede 交互、日本語は Aoede。Style: 英語 `FAMILY_X_ROLE_STYLE_EN["FULL_STORY"]` + 承認済み減速指示(逐語、`er033_..._styles_01`)、日本語 `FAMILY_X_ROLE_STYLE_JA`(承認済みJ3、逐語)。
- ASR(全て現行Production同一モデル): Primary `gpt-4o-mini-transcribe`(`routing._transcribe_openai_mini`、prompt無し)、Azure Speech STT(英語 `get_full_text_via_azure_stt_with_phrase_list(phrases=None)` = Phrase Listなし=原稿を与えない、日本語 `_azure_stt_strict`)、local faster-whisper medium(無料)。**Phrase Listあり(EN誤読10本)も比較**(`azure_pl`列)。
- 判定: 既存validator `classify_asr_match`(英語)/`classify_ja_asr_match`(日本語、Reading Resolver LLMはOFF=費用0)を**正しい原稿**に対して呼ぶ。Primaryはvalidatorの`should_pass`。Secondary候補(Azure/Azure+PL/local)は現行SCGと同じ厳格PASS集合(EXACT/NORMALIZED/TRANSCRIPT_STYLE_NORMALIZED/NUMERIC_EQUIVALENCE)のみPASS(`PHONETIC_MATCH`等はNG扱い。緩い基準だと`ja_len3_mis`のAzure「雪が降った」[原稿「ゆきが降った」、話した「ゆうきが降った」]が誤PASSに加わる=下記)。
- clip: **73本**(英語37 = 誤読22 + 対照15、日本語36 = 誤読22 + 対照14)。「約80」より少ないのは20円枠(実費は12.5円で余裕が出たが、設計時の見積は3秒/clipで約18.8円だった)。対照(正しい発話)は同一原稿でspoken=canonical(合計29本、要求の20本以上)。型: 数値・否定・語尾(-ed/-s、です/でした)・濁点/語頭子音・長音/母音長・最小対語・固有名詞/カタカナ・同形異音。
- 「確認済み誤読」の定義(集計の母数): 誤読クリップのうち、(i)いずれかのASRが話した形と一致、(ii)原稿と不一致のASRがある、(iii)読み上同形異音で話した形と転写が一致、のいずれか。全ASRが原稿形で転写したもの(14本、`紹介/照会`の同音1本を含む)は「未確定」として母数から除外(誤PASSに数えない=誤PASS率は下限寄りに偏る点に注意)。

## 2. 結果(`trial_b_tables_01.md`の転記+注)
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

## 3. 指標の読み取り
1. **誤PASS率(型別・ASR別)**: 上表。確認済み誤読30本での合計は Primary 2/30、Azure 2/30、local medium 3/30、Azure+Phrase List 0/3(PL対象10本のうち確認済みは3本のみ)。母数が小さい(型ごとに2〜5本)ため率ではなく件数と事例で読むこと。
2. **対照の誤NG率**: Primary 1/29(`ja_prn2_ctl` スタバックス、Azureが救済)、Azure 1/29(`ja_len3_ctl` ゆき→「雪」がPHONETIC_MATCH=厳格集合外)、local medium 3/29(`en_prn2_ctl` Columbia、`ja_num1_ctl` 「見つかった」、`ja_len3_ctl`)。**統一フローで不採用になった対照は0/29**。localは単独の最終権威にできない(誤NG 10%)。
3. **Secondaryの「原稿寄せ」実例**: (a) `ja_voi5_mis`(てんき→「電気」、Primary「点灯」NG・Azure/local「電気」PASS。ただし話した「てんき」が本当に「てんき」だったかは未確定。Azureは「天気」ではなく原稿側の「電気」を選んだ)。(b) 緩い基準(PHONETIC_MATCH許容)では `ja_len3_mis`(ゆうき→Azure「雪」)も誤PASS。厳格集合なら防げる=**PHONETIC_MATCHをSecondary PASSに含めない現行SCGの条件が有効**。(c) 英語では「Primary NG→Azure PASS」の誤採用は0件(英語の誤読22本のうち、Azureが原稿形で転写したのは全ASR共通の10本のみ(Primary・localも同じ形)=Secondary固有の原稿寄せではない)。
4. **Phrase Listの有無**: EN誤読10本(ship/sheep、raw bean、-ed/-s、固有名詞)で`azure_pl`は`azure`と**転写が同一**(確認済み誤読3本はどちらも誤読形を逐語転写=PLが誤PASSを増やした例なし、`raw bean`をPLに入れても`Robin`/`robbing`のまま)。未確定のうちPL対象7本はPL有無に関わらず原稿形。→ **この標本ではPhrase Listが原稿寄せを悪化させた証拠は無い**が、PLが効いた(救済した)証拠も無い。母数小(n=10)。
5. **C1除外を外した場合の日本語**: Primary NG かつ `entity_like=True` の誤読は4本(`ja_voi1` ガス→カス、`ja_voi2` バス→パス、`ja_voi4` ビル→ヒル、`ja_min1` 社外→社会)。**4本ともAzureもNG(誤読形を逐語転写)=C1を外してSecondaryを呼んでも誤PASS 0/4**。C1除外は、この標本では「誤PASS防止」としては何も防いでおらず、g8型(原稿=ガス、Primaryがカスと誤認、AzureとwhisperがガスでPASS)の正しい救済を妨げるだけ。ただし、`ゴミ→コミ`のように全ASRが原稿形へ寄せる型は、そもそもC1の有無と無関係に検出できない。
6. **未確定14本の扱い**: (a) 英語10本(inflection 4、parked/barked、固有名詞3、read/red、lead/led)、(b) 日本語4本(`ja_voi3`ゴミ/コミ、`ja_prn2`スターバックス/スターバクス、`ja_prn3`コーヒー/コヒー、`ja_min2`紹介/照会[同音])。**音声実体(`audio/*.wav`、git非管理)を試聴すれば確定できる**(0円、ユーザー作業)。試聴対象の優先順位案: `en_inf1_mis`、`en_prn1_mis`、`en_voi1_mis`、`ja_voi3_mis`、`ja_prn3_mis`。

## 4. 限界・注意
- **ground truthは「話した形」の仮定**: TTSが誤った綴りをそのまま読んだとは限らない(英語の綴り誤りをTTSが補正して読む可能性)。誤PASS率は「確認済み誤読」だけを母数にしたため過小評価寄り、未確定14本を全て誤PASSと見なせば Primary/Azure とも最大で 16/44 近くまで上がる(ただし上限は仮定)。
- 標本: 型ごと2〜5本、音声は短文(平均1.9秒)。実運用の長文(数十秒)では、LM priorは文脈が増える分さらに強く働く可能性(未測定)。短文は丸め/誤読の検出が長文より容易な側にも、難しい側にも偏り得る。
- TTS/ASRは非決定的で、再実行すれば転写が変わり得る(1回のみ実行)。
- Azure単価はSnapshot値(F0無料枠の可能性は未確認)。OpenAI ASRは尺換算の概算。`ja_*`の判定はReading Resolver OFF(LLM無し)。
- Production telemetry/queue/attempt_history/Master Storeへの書込なし。Azureの内部cost記録は`azure_cl_log_B_local.jsonl`(trial_abc配下)のみ。
- 使用モデル(最新原則の例外): TTS/ASRは「Production経路の測定対象」のため現行Production同一モデルを使用(PM_GOVERNANCE 25節の例外として明記)。TTS gemini-3.8-flash-lite-tts[最新世代]、Primary gpt-4o-mini-transcribe[Production固定]、Azure Speech STT、faster-whisper medium。ASRの最新性は未確認(Fable確認事項)。
