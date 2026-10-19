# ITEM1_PHONETIC_EQUIVALENCE_ROOT_CAUSE_01(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_01、2026-10-19)

Status: `ITEM1_ROOT_CAUSE_IDENTIFIED_FIX_DESIGNED_PENDING_OPUS`。コード変更0・HR Lock不変(`review_lock_state.json` sha256 `6720ce80b7eedba9789dc190a431b030e20486b298a451479129e4d017fb3e19` 前後一致)・新規TTS 0・LLM 0・`ledger.json` sha256不変(script内で前後比較)。
実費(推定。実請求は未確認): ASR再転写のみ。Azure STT 約6.5円(USD1.0/audio hour、`er005_output/cost_baseline_01/pricing_snapshot.json`。実音声秒数=調査専用cost log `asr_consistency_part3c1_01_cost_log.jsonl` 4呼出97.49秒+cost logger未初期化のscript不備[私のscript bug、`init_logger`未呼出]で`record`が例外になった2回の中断実行内のAzure各24.59秒[未記録・billed扱いで加算]=計146.67秒×160JPY/USD)+OpenAI gpt-4o-mini-transcribe 約0.5円(5呼出×約0.1円、run_04 cost_log行196の実測トークン245/82を外挿)= **約7.0円(上限10円以内)**。

## 0. 結論(先に)
1. **既存の音韻同等性判定に「承認済み仕様どおりに動いていないコード不具合」は、この録音2の棄却箇所には存在しない**(全棄却を関数:行で追跡し、全て仕様文または採用済みOpus指摘[OF-178]と一致)。ただし、ユーザーが指摘した「自然にMelosと聞こえるのにPASSしない」を生む**構造要因を4つ特定**した(下記)。うち2つは**承認済み仕様どうしの食い違い・空白**であり、修正には仕様変更(ユーザー判断)が必要なため**採用せず「仕様変更候補」として分離**した。
2. **要因1(最大): Melo/Mello非対称(既知のOPEN-330、USER_DECISION_REQUIRED・未決)**。同じ音素列`M EH L OW`の`Melo`は現行で自動PASS(`_is_benign_plural_pair`+一致率、`er006_preprod_hardening_01_validation.py:645,1149`)なのに、`Mello`/`Mellow`はM1の`_post_check`が「F1(Pattern A)で説明できること」を要求して棄却する(`er006_m1_multi_candidate_01.py:407-422`、Opus BLOCKER OF-178採用済み・CURRENT_SPEC L2798)。録音2の**同一wavをOpenAIで再転写すると`Melo drank`が返りPASSする**(今回再実測)。つまり**同じ音声が、ASRの綴りのサイコロ(Melo/Mello)だけでPASS/NGに分かれる**。これが「期待どおり機能していない」という実感の主因。
3. **要因2: ASR側のOOV語(`Mellows`)は音素を持てない**。`Mellows`はCMU辞書に無く(`pronouncing.phones_for_word('mellows')=[]`)、G2Pも承認されていない(UDR #52「綴りだけを根拠に任意の発音を許容しない」、M1はC3=G2P非採用)ため、M1は`asr_word_not_in_cmu`で比較に入れない。さらに**音素が得られても語末`S`と`Z`の有声性差を許容する規則が存在しない**(`forms_from` `er006_m1:293-309`は`drop_final_S_or_Z`/`add_s`のみ。Eq Layerは明示的に「manner/voicingが変わる場合は語幹自体の置換とみなし対象外」`er011_connected_speech_equivalence_layer_production_01.py:163-168,183`)=**仕様の空白(一部は明示的に非許容)**。
4. **要因3: ASR転写の確率的ばらつきが音声の同一性を覆い隠す**。本件wavの語末には**無声歯擦音(/s/)の物理的存在を簡易指標で確認**(§4: 録音1・2・3・run_03 PASS版の全5音声で、name語直後に105〜125msの無声(低域80-500Hz≈-54〜-58dB)・非周期(自己相関0.13〜0.19)・高域4-10kHz優勢の区間)。つまり**音声に`s`はあり、`Mello`(s脱落)も`Mellows`(z化)もASRの誤転写側**と見るのが妥当(ただし簡易指標で、人間の聴感や強制アライメントの代替ではない)。同一wavでもエンジンが固定的に別綴りを返す(Azure: 録音2・録音3・run_03 PASS版の3wav全てでProduction記録と同一綴りが再現=3/3。録音2はPhraseListあり/なしとも`Mellows drank`でPhraseListの効果なし)。
5. **要因4: Primary#2(同一音声の再転写)が統一ASR判定で廃止済み**(CURRENT_SPEC L2814、2026-10-15ユーザー決定)。再転写すればPASSした可能性がある音声(録音2)も、1回の転写で確定する。これは承認済み仕様どおりでバグではない。
6. 修正設計: **P1(推奨、仕様変更候補)**=M1の`_post_check`を「置換後の文が既存Production判定でshould_pass+F1残差0」へ置換し、`Mello`/`Mellow`を`Melo`と同判定にする(OPEN-330(a)の事実上の確定+OF-178改訂が前提)。録音2・3のPrimary(`Mello drank`)がM1で受理されることをoffline what-ifで確認(API 0)。**P2(非推奨、仕様変更候補)**=ASR OOV語の規則屈折音素導出(G-1)+語末歯擦音有声性許容(G-2)。**個別例外(Melos↔Mellows)・閾値緩和は不採用**。

## 1. 音韻同等性判定の全機構マップ
入力の型: 【綴】=綴り文字列、【CMU】=CMU辞書音素列、【L】=Pronunciation Ledger由来IPA→ARPAbet、【音響】=音声。呼出順は`er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail`(L682)内の実順序。

| # | 機構(関数:行) | 入力 | 受理条件(仕様) | 呼出順・使用経路 | Family |
|---|---|---|---|---|---|
| 1 | `classify_asr_match` `er006_preprod_hardening_01_validation.py:1200`(`protected_check`→entity/homophone判定L699-725→`_is_benign_plural_pair`L645→一致率L1149) | 【綴】+【CMU】(homophone_candidate=CMU完全一致) | 数値/否定保護通過+内容語差なし(benign単複含む)かつ一致率≥閾値→`HIGH_SIMILARITY_SAFE`。固有名詞のみ差は`ASR_VALIDATION_UNCERTAIN`(should_pass=False)。CURRENT_SPEC L2136 | **全Primary/Secondary判定の第1段**。Secondary転写にも同関数 | X/Y/Z・B1/A2共通(英語本文) |
| 2 | F1/Pattern A・B・C `er011_b1_connected_speech_validator_01.py:240`(`classify_connected_speech`)、Pattern A=L152-168(`s_suffix_label_if_match`L88/`final_s_sound`L35/`initial_sound`L65/`SIBILANTS`L84) | 【綴】(綴り水準) | A: canonical語から`s/es`を除いた綴り==ASR語**かつ次語頭が歯擦音**。B: 破裂音連続。C: 再分節。全差分点検・残差0のみ受理(L2150、OPEN-340) | 1の内側(`classify_asr_match`から呼出)。M1の`_post_check`も再利用 | 共通 |
| 3 | Case A/homophone `er006_secondary_asr_01.py:523`(`_step_alternate_pass`)、`:506`(`_case_a_entity_pass`)→`er008_asr_variant_hardening_15_homophone_en.py:73,103,138` | 【CMU】代表(先頭)発音の完全一致 | 両語がCMUにあり代表発音一致のみ(`PROPER_NOUN_ENTITY_ARPABET_CONFIRMED`/`HOMOPHONE_EQUIVALENT`)。**OOVはunresolved(None)=不受理・HR行き**(CURRENT_SPEC L1829(B)/L1831) | Primary: `_m1_try`直前(L890-896)。Secondary: `secondary_accept_fn`内(L938-944) | 共通 |
| 4 | Connected Speech Equivalence Layer(OPEN-122) `er011_connected_speech_equivalence_layer_production_01.py:80,142,163`(`phonetic_environment_categories`/`phoneme_prefix_drop`/`phoneme_final_place_substitution`)、呼出`er006_secondary_asr_01.py:412,762` | 【CMU】音素+【音響】ではなく独立ASR corroboration | カテゴリA〜G+corroboration≥1。**入口は`TRUE_CONTENT_MISMATCH`限定**、A2/B1英語本文4 segmentのみ(L2151)。**voicing/manner変化は語幹置換として対象外**(L163-168) | 2の後段(L760付近) | A2/B1(Z適用は未確認) |
| 5 | Tier3(EN ASR Semantic Equivalence)`er021_en_asr_semantic_equivalence_production_01.py:716(locate_single_token_diff),731(corroboration_supports),742(determine_sub_reason)`、呼出`er006_secondary_asr_01.py:~785-840`(L808) | **【綴】トークン完全一致**(`other_tokens[idx]==canon_tokens[idx]`)。**音素比較ではない** | role∈5(FULL_STORY等)・sub_reason∈{plural_only,entity_only}・Azureがdiff位置でcanonical語**そのもの**を返す(L2144) | 3の前(Tier3→non-latin→Case A→M1) | 共通(5 role) |
| 6 | M1 複数発音候補 `er006_m1_multi_candidate_01.py`: `freeze_candidates`L248/`_c2_candidates`L208/`forms_from`L293/`_enumerate_subs`L356/`_post_check`L407/`_entry_gate`L425/`_judge_core`L443/`m1_multi_candidate_judge`L485。呼出`er006_secondary_asr_01.py::_m1_try`L214(Primary L896、Secondary L946) | 【CMU】C1=CMU全異読、【L】C2=Ledger IPA→ARPAbet(CMU未収録語のみ)。**ASR語は【CMU】のみ**(`_variants`、OOV不可) | 置換後文のF1残差0かつexact以外の置換がF1の`f1_explained`(Pattern A/B/C)に含まれる(**benign吸収は不受理**、OF-178)。入口: Production分類が`ASR_VALIDATION_UNCERTAIN`+protected通過(L2794-2801) | Primary#1直後(Case A不成立時)とSecondary許容集合内。減速後も同じcascade | 共通(en-US) |
| 7 | 統一ASR判定 `er078_asr_unified_judge_01.py:352`(`unified_judge`、L523で`secondary_accept_fn`) | 音韻判定は**持たない**(注入された許容集合の結果を受けるだけ) | Primary NG→Secondary 1回+cache、Secondary許容集合(1+3+6)を満たせばPASS_WITH_WARNING。Primary#2廃止(L2814) | 全Family全Section | 共通 |
| 8 | Pronunciation Ledger/PhraseList `er006_pronunciation_ledger_01.py`(get_hint_for_text)→Azure PhraseList(`er006_secondary_asr_01.py:70`)+M1のC2候補(L208) | 【L】 | **PhraseListは聞き取りのバイアスのみで受理根拠にならない**。C2候補は6の入力(canonical_spelling≠surface除外等=OF-181) | 判定前に読取 | 共通 |
| 9 | Pronunciation Resolution Core `er025_entity_pronunciation_resolver_core_01.py:439,462`(`min_confidence="medium"`) | 【L】 | **TTS側のstyle prefix注入**。ASR受理には無関係。Melos=low・cascade_unresolved→hints未適用(OPEN-318「TTS注入は別Phase」) | TTS生成前 | 共通(Z経路で確認) |
| 10 | (参考)旧entity phonetic corroboration(soundex)`validation.py:1538` | 【綴】 | **呼出元0件・置換済み**(CURRENT_SPEC L2098注記)。撤去していない旧コードが残存 | - | - |

Trial(Production未配線): er065 `p2_phon.py::explain_diff`(音素水準の連結発音診断、`Mellows`型は音響独立証拠AUC0.74で単独gate不可・自動許容REJECTED、DECISION_LOG L20795付近)、er068 offline(M1原型、V1'REJECTED/V2'未決)。

## 2. 音素比較の事実(`phoneme_compare_melos_01_result.json`、API 0)
| 語 | 音素列 | 出所 |
|---|---|---|
| Melos | 凍結C2候補4件: `M IY L AA S` / `M IH L AA S` / `M EH L AA S` / `M EH L OW S`(`ec716e185835dba3`、confidence=low) | Ledger IPA→ARPAbet(`ipa_to_arpa`)。CMUに`melos`は無い |
| Mellows | `M EH L OW Z` | **既存機構では取得不能**(CMUに無くG2P非導入)。**分析専用の規則導出**=CMU`mellow`(`M EH L OW`)+規則複数形-s(母音語末→/z/)。既存機構ではない |
| Mello / Melo / Mellow | `M EH L OW`(3語とも同一) | CMU(pronouncing) |
| Mellos(参考) | `M EH L OW Z`(同上導出) | 分析専用 |

音素差分(`M EH L OW S`基準):
| ASR語 | 差分 | 種別 |
|---|---|---|
| Mellows (`…OW Z`) | 語末 S→Z のみ(manner=fricative・place=alveolar同一、voicingのみ相違 `er011 eq layer:46-62`) | **語末歯擦音の有声性のみの差**。母音差0・音節数差0 |
| Mello/Melo/Mellow (`…OW`) | 語末 S 脱落 | **語末音素の脱落**(母音差0・音節数差0) |
| (主発音候補 `M IY L AA S` 基準) | 母音2か所差 | 別の発音(Ledger主発音とは不一致) |

**「同等」定義との照合**: 承認済みの「同等」は(a)音素列厳密一致(Case A/homophone、M1 exact)、(b)語末S/Zの**脱落**のみ(M1 `drop_final_S_or_Z`+F1 Pattern Aの歯擦音連続=次語頭が歯擦音の文脈限定、CURRENT_SPEC L2798)、(c)-sの付加(Pattern C/M1 `add_s`)。**有声性だけが異なる語末S↔Zを同等とする規則は仕様に存在しない**(Eq Layerは明示的に除外)。したがって`Mellows`は**既存定義では「同等とされるべき」でも「同等でないと定義された」でもなく、空白+Eq Layer内の非許容原則**。`Mello`/`Melo`/`Mellow`は(b)の脱落型で、**次語が歯擦音(said等)の文でのみ受理、`drank`では受理されない**(が、綴りが`Melo`ならbenign単複で受理される=非対称)。

## 3. 棄却箇所の特定と3区分(録音2 attempt2、E21 telemetry行9613-9614、`attempt_history`行15172-15176、`m1_offline_replay_part3c1_10_result.json`、今回再現`phoneme_compare_melos_01_result.json`)
全て実判定をoffline再実行(Production module呼出、API 0)で確認。「Primary=Mello drank(OpenAI)」「Secondary=Mellows drank(Azure PL)」。

| # | 対象 | 機構 | 棄却の条件式(実測) | 区分 |
|---|---|---|---|---|
| R1 | Primary `Mello` | #1 classify | entity_only diff(`melos→mello`、entity_like=capitalized)→`ASR_VALIDATION_UNCERTAIN`、should_pass=False(`validation.py`entity分岐L1141付近) | 仕様どおり |
| R2 | Primary `Mello` | #3 Case A | `entity_span_arpabet_match('melos','mello')`→`melos`がCMU未収録=unresolved→不成立。仕様L1829(B)「CMU辞書に無い外国由来固有名詞はHuman Review行きのまま」 | 仕様どおり |
| R3 | Primary `Mello` | #2 F1 | `classify_connected_speech`→`UNCLASSIFIED_FALLS_THROUGH`(Pattern Aは次語頭=歯擦音が必要。`drank`は/d/、L152-168) | 仕様どおり |
| R4 | Primary `Mello` | #6 M1 | 入口通過(applicable=True)、置換案`mello→melo`(`drop_final_S_or_Z`、C2_ledger_alt `M EH L OW S`)を生成。**`_post_check`(`er006_m1:407-422`)で`cs2.new_judgment`が`CONNECTED_SPEECH_ACCEPT/RESEGMENTATION`でない→`SUBSTITUTION_NOT_F1_EXPLAINED`**(Opus BLOCKER OF-178採用、CURRENT_SPEC L2798) | **仕様どおり(ただしMelo/Mello非対称=OPEN-330未決を顕在化させる箇所)** |
| R5 | Primary `Mello` | #5 Tier3 | `corroboration_supports`(`er021:731`)=`other_tokens[27]=='mellows'`≠`'melos'`→False(`corroborated_by=[]`、E21行9614) | 仕様どおり(Tier3は音素比較でなく文字列一致。仕様L2144) |
| R6 | Secondary `Mellows` | #1 classify | entity_only→`ASR_VALIDATION_UNCERTAIN` | 仕様どおり |
| R7 | Secondary `Mellows` | #3 Case A | `melos`・`mellows`ともCMU未収録→unresolved | 仕様どおり |
| R8 | Secondary `Mellows` | #6 M1 | `_enumerate_subs`(`er006_m1:356`)の`avs=_variants(cmu,'mellows')=[]`→`asr_word_not_in_cmu`(L371)→`MULTI_CANDIDATE_NO_MATCH`。**ASR OOV語の音素を得る手段が仕様上存在しない**(C3=G2P非採用、UDR #52) | **仕様の空白(非採用が明示された領域。許容基準の新設を要する)** |
| R9 | Secondary `Mellows`(仮に音素が得られても) | #6 M1 `forms_from` | 候補`M EH L OW S`から生成される受理形は`exact`/`drop`(`…OW`)/`add_s`(`…S S`,`…S Z`,`…S IH Z`)のみ。`…OW Z`は無い | **仕様の空白**(語末歯擦音の有声性差は未定義。Eq Layerは非許容) |
| R10 | Secondary `Mellows` | #4 Eq Layer | 入口が`TRUE_CONTENT_MISMATCH`限定(本件はUNCERTAIN)=不呼出。呼んでも`melos`が未収録で音素取得不能、かつ`phoneme_final_place_substitution`はvoicing変化を除外(L183) | 仕様どおり |
| R11 | 統一judge | #7 | Primary NG+Secondary許容集合不成立→`NG_BOTH`(`p3_primary_ng`、RLS) | 仕様どおり |
| R12 | Resolver | #9 | `min_confidence="medium"`、Melos=low→hints未適用 | 仕様どおり |

**「仕様では受理すべきなのにコードが棄却」(不具合)=0件**。「仕様の空白」=R8・R9(Secondary)。R4は仕様どおりだが仕様どうしの食い違い(下記)。

**仕様どうしの食い違い(要ユーザー判断)**: ①2026-10-13合意の設計原則「同じ音韻現象には同じ判定を適用する。同じ現象の一部だけに異なる厳格な証拠基準を課さない」(DECISION_LOG L20918、`docs/pm/design_principles/connected_speech_proper_noun_phonetic_equivalence_2026-10-13.md`)と、②OF-178(Opus BLOCKER・採用、`docs/pm/OPUS_FINDINGS_LEDGER.md:205`)+CURRENT_SPEC L2798「benign吸収は不受理」+現行Pattern Aの綴り水準受理(OPEN-330)。`Melo drank`=PASS(要因=benign単複)/`Mello drank`=NG(同音素列)は①に反し、②に従う。本件の録音2は**この食い違いの直撃**(同一wavをOpenAIが`Melo drank`と書く回はPASS)。

## 4. Secondaryが`Mellows`を返した理由の切り分け(`asr_consistency_part3c1_01_result.json`、`acoustic_tail_part3c1_01_result.json`)
**再転写(同条件、既存ASR経路、各wav1回)**:
| wav | OpenAI(今回) | Azure PLあり | Azure PLなし |
|---|---|---|---|
| 録音2 attempt2 | `Melo drank,…` | **`Mellows drank,…`**(Production記録と同一=再現) | **`Mellows drank,…`**(PLの効果なし) |
| 録音3 attempt3 | `Mello drank,…` | `Mellow strength got…`(Production記録`Mellow strength`と同一) | 未実施 |
| run_03 PASS版 attempt1 | `Mellow drank,…` | `Melos drank,…`(Production記録と同一) | 未実施 |
- **PhraseList**(Ledger由来`["Melos"]`、`size1`)の効果: 録音2でPLあり/なしとも`Mellows`=**効果なし**。Azureは同一wavに対し決定的に同じ綴りを返す(Production→今回で再現)が、**take(録音)ごとに違う綴り**(Mellows/Mellow strength/Melos)。つまりAzureの固有名詞推定が揺れるのではなく、**takeごとの微小な音声差に対して決定的に別綴りを返す**。
- **OpenAIはtakeでなく呼出ごとに揺れる**: 録音2のwavに対し過去の3回再転写(HR_LOCK_PART3C1_ROOT_CAUSE_01.md §3)は`Mello/Melo/Mello`、今回は`Melo`。`Melo`の回はPASS。
- **音声そのもの(簡易音響指標、local faster-whisper=無料+numpy/scipy。語境界は粗い[約20ms]ため診断用で合否根拠にしない)**: name語直後の歯擦音様区間(4-10kHzが80-500Hzより優勢・自己相関<0.4):
| 音声 | 区間長 | 高域4-10kHz平均 | 低域80-500Hz平均 | 周期性 |
|---|---|---|---|---|
| 録音1 att1 | 105ms | -28.8dB | -56.3dB | 0.133 |
| 録音2 att2 | **125ms** | **-22.0dB(最大)** | -54.3dB | 0.190 |
| 録音3 att3 | 105ms | -29.3dB | -54.3dB | 0.154 |
| run_03 PASS(減速前) | 105ms | -30.9dB | -57.1dB | 0.157 |
| run_03 PASS(減速後) | 105ms | -31.6dB | -58.0dB | 0.137 |
→ **全音声に無声(低域≈-54〜-58dB=声帯振動なし)・非周期の歯擦音様区間が約105〜125msある**=音響的には/s/(/z/なら低域に有声バーが出る)。**録音2は逆にs区間が最長・最強**(Azureの`Mellows`は音声の欠陥ではない)。local whisperの語境界は録音1・2で`Mello's strength`(sが次語`drank`と融合し`strength/strained`に聞こえる:/s#dr/連続)。OpenAIの`Melo strained`(録音1)と整合。**結論**: 原因は**(a)音声に/s/はある(簡易指標。人間の聴感[ユーザー: 自然にMelos drank]と整合)、(b)/s#dr/連続をASRが語頭`str`に取り込む/語末を脱落/z化する揺れ**であり、TTS音声の欠陥ではなく**ASRの誤転写側**。ただし**負例(sの無いtake)の音響対照を持たず、AUC0.74で単独gate不可との既存知見(DECISION_LOG L20796付近)も変わらない**=合否根拠にはしない。人間の聴感が最終確認。
- Azure固有名詞推定: `Mellows`は語彙上自然な英単語(mellowの複数形/3単現)で、言語モデルが好む綴り。PhraseList`Melos`は重み付けのみで強制しない(`er006_secondary_asr_01.py:70`のdocstring)。

## 5. 修正設計
### 5-1. 区分
| 案 | 内容 | 区分 |
|---|---|---|
| **P1(推奨)** | M1 `_post_check`を「置換後の文が既存Production判定(`classify_asr_match`)でshould_pass、かつF1残差0」へ変更。`Mello`/`Mellow`(CMU同一音素列`M EH L OW`)を`Melo`と同判定にする | **仕様変更候補(採用しない)**。OF-178(Opus BLOCKER・採用済み)の撤回/改訂+OPEN-330(a)の事実上の確定を伴う。2026-10-13合意の設計原則とは整合。新しい許容語を増やすのではなく「`Melo`が現行で通る文脈」に`Mello/Mellow`を揃える |
| P2(非推奨) | G-1: ASR OOV語を「CMU語幹+規則屈折allomorph(S/Z/IH Z)」で音素導出 + G-2: C2候補の語末歯擦音の有声性差(S↔Z)を許容 | **仕様変更候補**(新しい許容基準+UDR #52「綴りだけを根拠にしない」との境界。ASRの誤転写を受理することになる) |
| (不採用) | `Melos↔Mellows`個別許容/辞書追加/閾値緩和/Pattern Aの非歯擦音後続への拡張(Opus R-D不採用済み) | 禁止/不採用 |
| (範囲外) | R1原稿ルール・OPEN-318 C-a(1回の人間聴感でLedger確定)・TTS注入 | 既存の別判断(UDR #43/OPEN-318) |
**既存仕様内の不具合修正に該当する項目=0件**(よって実装委任_03はP1/P2の採否ユーザー判断後)。

### 5-2. P1の変更箇所・影響
- 変更: `er006_m1_multi_candidate_01.py:407-422`(`_post_check`)のみ(+`CURRENT_SPEC.md` L2798文言、`OPUS_FINDINGS_LEDGER` OF-178の状態更新、testのOF-178系アサート改訂)。M1の`forms_from`/凍結候補/入口条件は無変更。
- 影響Family: M1は`m1_enabled`既定True・en-US限定で`evaluate_attempt_with_cascade_detail`内に1箇所のため**X(B1/A2)・Z・将来Y共通**(Family固有分岐なし)。A/B/Cは対象外(委任外)。
- retry/fallback/resume/減速後: M1は純関数(ASR転写+凍結候補のみ入力)で、Primary#1・Secondary許容集合・forced-secondary・減速後の統一judge・LR回復後の再検証で同一ロジック(OF-173/172)。凍結候補は最初の試行前に1回=resumeでも再生成されない。変更後も判定はroute非依存。
- 費用: 実装JPY0・test JPY0。生産では`Mello drank`型でTTS再生成(各約JPY2〜5)/LR/HR待ちが減る。追加API 0。
- offline what-if(`m1_post_check_whatif_01.py`/`_result.json`、API 0): 
  - 録音2 Primary`Mello drank`: 現行M1=不受理(`SUBSTITUTION_NOT_F1_EXPLAINED`)→P1=**`M1_MULTI_CANDIDATE_ACCEPT`(PASS_WITH_WARNING)** → **録音2は2回目のTTSでPASSし、3回目TTS・LR(Melos→He)・HR Lock・減速後の旧原稿照合に到達しない**。
  - 録音3 Primary`Mello drank`も同様に受理。run_03 PASS版Primary`Mellow drank`も受理(現行はTier3経由でPASS)。録音3 Azure`Mellow strength`は`TRUE_CONTENT_MISMATCH`のまま不受理(内容語`strength`)、録音1(`strained`)も不受理=誤受理は増えない。
  - 記事非依存fixture(Melos文脈): `left`型(非歯擦音後続)`Mello`→現行不受理/P1受理、`said`型→両方受理、母音差`Milo`/`Malos`→両方不受理、語末脱落`Mel`→両方不受理、`Mello took`(別内容語)→両方不受理。
  - 実データcensus: 既存E21 telemetryの`entity_only`行2309のうち、現行M1受理368→P1受理392。**新規受理は24行・1ペアのみ=(`melos`,`mello`)**。他の固有名詞・一般語で新規受理0(誤受理増分の観測0。ただし実データのOOV canonicalペアは30のみで、Melos以外の語末s名での検証は未実施=PASS_WITH_WARNING+試聴リストで事後確認される前提)。
- P2のwhat-if(`phoneme_compare_melos_01_result.json``whatif_G1_G2_prototype`、script内プロトタイプ。Production無接続): 録音2 Azure`Mellows drank`・PLなし版→受理(PASS_WITH_WARNING)。Primaryは`Mello`で不受理のため**Azureのみ**でPASS。E21のunique差分97ペア中、OOV canonical+Ledger C2のペア30、新規受理3ペア(`melos→mellows`52行/`mellos`89行/`mellowes`4行)=**全てMelos**、他語0。記事非依存fixture 7件(正例1・負例6: 母音差/語末脱落/S↔SH/語中S↔Z/IH Z付加/語幹子音差)全期待どおり。
### 5-3. Regression案(実装時。記事非依存)
M1 `_post_check`単体: ①(正)CMU同音素列綴り違い+Melo現行PASS文脈→受理 ②(負)母音差/語末脱落/別内容語/末尾欠落/数値否定→不受理 ③(負)canonical非OOV(C1)での`bus→buzz`型が影響を受けない ④F1残差ありは不受理 ⑤減速前後の同一転写で同一判定 ⑥凍結候補の注入契約(OF-179)・ASR非依存契約(OF-180)の既存test全PASS ⑦`Melos left`型の新規受理を許容した旨のcharacterization test(OPEN-330(a)承認の固定)。DefaultOffIsolation型は不要(限定例外ではなく既存関数の仕様変更のため、ユーザー承認後に実装)。
### 5-4. QCD(P1)
- 品質(Q): 受理面の拡大は「`Melo`が現行で受理している文脈と同じ範囲」に限定され、音素が同一(`M EH L OW`)の綴りのみ。語末`s`欠落(発音が`Melo drank`)との区別はASRではできない(OPEN-330と同じ未解決。簡易音響指標でも録音2はs区間最長でASR誤転写が支配的)。`PASS_WITH_WARNING`+事後試聴リストで人間確認が残る。
- 速度(D)/コスト(C): HR・LR・再生成の削減(Melos型名前入りclipのNG率は約6%、約0.8回/記事[HR_LOCK_PART3C1_ROOT_CAUSE_01.md §6、推定])。実装JPY0。
- P2: Qリスク大(ASR誤転写の受理規則を新設)、効果はAzure経路のみ。**非推奨**。

## 6. Opusレビュー観点案(5件以内)
1. P1はOF-178(Opus BLOCKER)の趣旨「M1がF1より緩い受理面を作らない」を損なわず、2026-10-13設計原則との整合を取れているか(`Melo`が受理される文脈への限定が`classify_asr_match`+F1残差0で保証されるか、`HIGH_SIMILARITY_SAFE`の一致率依存[文の長さで`Melo left`の判定が変わる:短文では`ASR_VALIDATION_UNCERTAIN`]の影響)。
2. OPEN-330(a)/(b)/(c)のどれを正式仕様にするか(P1は(a)の事実上の承認)。(b)接尾辞限定にして`Melo`も不受理に揃える逆方向(HR増)との比較。
3. 簡易音響指標(s区間の存在)を合否根拠にしない現行方針の維持でよいか(負例音響対照なし・AUC0.74)。独立証拠なしで`PASS_WITH_WARNING`+試聴リストに頼る妥当性。
4. P2(G-1/G-2)をやらない判断の妥当性(UDR #52との境界、OF-184「直接音素置換は範囲外・no_match理由別telemetryで需要測定」を満たす測定手段が現在Production成果物に残っていない点)。
5. LR発火条件⑤乖離・OPEN-283・本件M1判定の三者の整合(M1で救済されればLRが発動しない一方、LR/減速後原稿照合は委任_02で是正中=干渉しないか)。

## 7. E-1 既存仕様照合(行番号付き)
- CURRENT_SPEC: L1829(固有名詞ASR不一致の自動PASS条件(A)CMU代表発音一致のみ/(B)OOVはHR、「ASR consensus ≠ pronunciation verification」)、L1831(homophone CMU完全一致)、L2098(旧soundex corroboration=superseded)、L2136(Validator)、L2139(Ledger)、L2144(Tier3=Secondary corroboration必須、規則的複数形・固有名詞のみ)、L2150(Pattern A/B/C・F1・OPEN-330言及)、L2151(Eq Layer A〜G)、L2794-2801(M1: 受理=F1残差0かつexact以外はf1_explained、benign不受理、C3なし、2026-10-14再確認「綴りだけを根拠に任意の発音を許容してはならない」)、L2803-2818(統一ASR、Secondary 1回+cache、Primary#2廃止L2814、LR発火条件L2818)。
- OPEN: OPEN-318(固有名詞読み・R1・C-a)、OPEN-330(Melo/Mello非対称USER_DECISION_REQUIRED)、OPEN-339(M1/G2P/OOV)、OPEN-340(F1)、OPEN-419(Z品質分析)、OPEN-283(減速後旧原稿照合・委任_02)。Opus: OF-178(BLOCKER採用)・OF-179〜181・OF-183/184/187・OF-AUW-07(合意誤読の判定式=委任_02領域)。UDR: #52(OOV: 綴りだけを根拠にしない)、#55(F1/M1分離)、#116(本件HR判断・保留)。
- 過去Trial: er068(M1原型・V1'REJECTED)、er075(OOV_SAFETY_01: OOV fallback(iii)は未承認、M1_BENEFIT_CENSUS: M1(i)新規受理0)、er065 Phase2(音響独立証拠AUC0.74・自動許容REJECTED)、er069(Melos 12-take)、HR_LOCK_PART3C1_ROOT_CAUSE_01.md。
- Cross-Family/Family固有: M1・F1・Case A・Tier3・統一judgeはX/Y/Z共通の共有cascade(Family分岐なし)。Z固有は①Ledger内容(Melos)②Std/Advancedの減速経路③PhraseList(canonical_spelling)のみ。Eq Layerはfull_story_part1/2・point_one/twoにのみ配線(Z narratorは未確認)。本調査はProduction配線を変更していないため、配線状況の変化なし(`PRODUCTION_WIRED`宣言なし)。
- 副次観測(要追跡・新規OPENにしない): ①M1のreject audit(`m1_multi_candidate_rejected`)は永続成果物(attempt/TGR/attempt_history)から検出できず(`er026_output`・`er011_output`をGrep、受理5件のみ)、OF-184/187の「no_match理由別telemetry」が蓄積されていない可能性(未確認)。②旧soundex corroboration関数が呼出元0のまま残存(撤去は別判断)。
