# HR_LOCK_PART3C1_ROOT_CAUSE_01(委任_10、2026-10-19、Status=`HR_LOCK_ROOT_CAUSE_ANALYZED_PENDING_FABLE`)

対象: `er026_output/family_z_production_e2e_01/melos/run_e2e_04/a2` Standard `full_story_part3_c1`(Narrator FULL_STORY)。HR Lock維持(`review_lock_state.json` sha256 `6720ce80b7eedba9789dc190a431b030e20486b298a451479129e4d017fb3e19` 前後一致)。新規TTS 0・Azure 0・LLM 0。ASR再評価=OpenAI ASR 24呼出(概算JPY2.75、出典=`er005_output/cost_baseline_01/pricing_snapshot.json` input 1.25/output 5.0 USD per 1M tokens、160JPY/USD、トークン数はrun_04 cost_log行196等の実測245/82で外挿。実請求は未確認=推定)。
期待テキスト(canonical sha256 `b6d4377342693cf0925f2f9fbd89faf93c463d6d5b38bbd6c5052f3e62abccf8`、`tts_generation_results.json` segments.full_story_part3_c1.reuse_key): 4文目 `Melos drank, got onto his knees, and stood up.`(直前=`Water came slowly through a crack in the rock.`、直後語=`drank`)。

## 0. 結論(先に)
1. HR Lockの直接原因は「Melosの読みの確定失敗」だけではなく、**2段の連鎖**: (i) 3回のTTSがいずれも自動合格しない(Primary="Mello drank"系、Azureは毎回別綴り) → (ii) 仕様上は"合意誤読のみ"のはずの**Local Rewrite(LR)が発火し、Melos→Heに置換**(4回目の生成) → (iii) A2の6%減速後の再検証が**書換え前の原稿(Melos入り)と照合**し不一致 → STOPPED → HR Lock(finalize_a2_slowdown_final_ng)。(iii)は既知の**OPEN-283(未承認候補)**そのもの。
2. M1・Primary/Secondary・Tier3・Ledger PhraseListは**仕様どおり発動し、受理条件を満たさず不採用**。「発動すべきなのに発動しなかった」配線漏れは**0件**。ただし**仕様乖離1件**(CURRENT_SPEC L2816のLR発火条件⑤「両エンジン合意誤読のみ」がコードに存在しない=抑止すべきLRが発動)と**仕様の空白1件**(OPEN-283)を検出。いずれも修正は方式/閾値判断を含み、かつ本件では「HR削減」にならない(下記§4)ため**修正せずFableへ判断候補として報告**。
3. A/B: **区別不能(B寄り)**。B側の実測根拠が多い(同一wavの再転写で綴りが変わる、attempt1のTRUE_CONTENT_MISMATCH"strained"は再転写で消える、run_03 PASS音声の減速前もOpenAIは"Mello drank"で本件attempt群と同一)。A側の弱い根拠(減速後run_03は"Melos"×3、本件attempt減速後は"Mello"5/6)も残るため断定不可。不足証拠=人間の試聴・語単位の音響分析・第3の独立ASR。
4. HR再提示は**必要**(自動で通る経路が無く、最も近い自動経路は名前を消すLR版)。HRページを更新済み(§5)。前回ページの「現在ファイル=録音3の後処理版」は**誤り**(実体はLR版[Melos→He]の6%減速)。

## 1. 対策別の発動実績表(ユーザー§1の1〜5)
出典略称: TGR=`run_e2e_04/a2/audit/tts_generation_results.json`、RLS=`.../audit/review_lock_state.json`(full_story_part3_c1.last_attempts_log)、AH=`er011_output/attempt_history.jsonl`(行15173=内側生成、15175=減速後、15176=Lock)、AJ=attempt jsonの`cascade_steps`、E21=`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`行、CL=`run_e2e_04/cost_log.jsonl`行、M1R=`m1_offline_replay_part3c1_10_result.json`(本委任のoffline再判定、保存済み転写に対するM1のみ・API 0)。

| 項目 | attempt1(flash-lite標準) | attempt2(同) | attempt3(minimal fallback) | LR再TTS(4回目)+6%減速 |
|---|---|---|---|---|
| 保存wav | attempts/..attempt1_customa3c4625e.wav(25.18秒) | ..attempt2..(24.59秒) | ..attempt3_minimalfallback.wav(23.56秒) | `full_story_part3_c1_original.wav`(23.12秒、sha40c6907e..)→`full_story_part3_c1.wav`(24.492秒、sha713252..) |
| Primary(OpenAI gpt-4o-mini-transcribe, en) | `...Melo strained, got onto...` → TRUE_CONTENT_MISMATCH(E21行9611: content_word、entity_like_source=[]) | `Mello drank` → ASR_VALIDATION_UNCERTAIN(E21行9613: entity_only、diff=index27 melos→mello、entity_like_source=capitalized) | `Mello drank` UNCERTAIN(E21行9616) | `He drank`(書換え文に対しNORMALIZED_MATCH) / 減速後は書換え前原稿との照合でUNCERTAIN(E21行9619: melos→he) |
| Secondary(Azure en-US、PhraseList size1) | 呼出あり(p3_primary_ng、CL行197、25.18秒=JPY1.1556): `Mellow Strength` → TRUE_CONTENT_MISMATCH(E21行9612)→NG_BOTH `secondary_not_accepted`(RLS) | Tier3用に1回呼出(CL行200)→同textをsecondary_1にcache流用(`cached:true`、追加Azure 0): `Mellows drank` → UNCERTAIN → NG_BOTH | Tier3用に1回(CL行203)+cache流用: `Mellow strength` → TRUE_CONTENT_MISMATCH(E21行9618) → NG_BOTH | retts後: Azure`He drank, got on to` → force_secondary_agreedでPASS_WITH_WARNING(script v1)。減速後: Azure`He drank, got on to`(CL行210)→Tier3不成立・secondary TRUE_CONTENT_MISMATCH |
| M1(複数発音候補) | 入口条件(`_entry_gate` er006_m1_multi_candidate_01.py:425)でBASE_CLASSIFICATION_NOT_UNCERTAIN→対象外(M1R) | **発動(applicable=True)**: 凍結候補4件(下記)、置換案`mello→melo`(rule=drop_final_S_or_Z、C2_ledger_alt /ˈmɛloʊs/)を生成、`_post_check`(L407)で**SUBSTITUTION_NOT_F1_EXPLAINED**で不受理(M1R)。Azure`Mellows`は`asr_word_not_in_cmu` | 同左(Primary: SUBSTITUTION_NOT_F1_EXPLAINED、Azure`Mellow strength`はBASE_NOT_UNCERTAIN) | 対象外(語がHe) |
| Ledger「Melos」登録 | `ledger.json` key `ec716e185835dba3`(surface melos、canonical_spelling Melos、entity_type cascade_unresolved_entity、confidence=low、updated_at 2026-10-12T13:17:58、sources 10件、expected /ˈmiː.lɑːs/、alt /ˈmɪlɒs/ /ˈmɛlɒs/ /ˈmɛloʊs/)+`ff3c8d6f3362c90a`(ja_reading_katakana メロス、work_canon、M1ではja_reading_katakana除外)。M1凍結候補=C2_ledger_expected M IY L AA S / alt M IH L AA S / M EH L AA S / M EH L OW S(CMUに"melos"無し=`default_cmu('melos')`=[])。Azure PhraseListにcanonical_spelling使用(`phrase_list_used:true`) | 同 | 同 | 同 |
| EN ASR semantic equivalence(Tier3) | entity_onlyでないため(content_word)**非発動**(仕様どおり) | **発動**(E21行9614: tier3_attempted_no_corroboration、corroborated_by=[]): Azure`Mellows`≠canonical`melos`(`corroboration_supports` er021_en_asr_semantic_equivalence_production_01.py:731は位置一致の完全一致のみ) | **発動**(E21行9617相当): Azure`Mellow strength`で不成立 | 減速後に**発動**(E21行9620): Azure`He`≠`melos`で不成立 |
| Pronunciation Resolution Core(er025) | 呼出あり(`repro01.py:305`、標準経路)。`resolve_and_augment_en_style_prefix`(er025_..core_01.py:439)は`min_confidence="medium"`(L462)で、Melosはlow・cascade_unresolved_entity(再research対象外)のため**hints_applied=False**。style sha(3a680861..)=effective sha(同)で確認(TGR style) | 同 | 同(fallbackは`repro01.py:585`、style_prefix_len30 `natural, clear, conversational`) | 同。er025 telemetry(`pronunciation_resolution_core_telemetry_01/telemetry.jsonl`)は最終行2026-10-16でweb lookupイベントのみ記録=本件に該当行なし(仕様どおり:低confidence再researchは`_web_lookup_allowed`等で非発動) |
| PASS_WITH_WARNING等の自動救済 | **不適用**: Secondary(Azure)が許容集合(should_pass/CMU CaseA・homophone/M1)に入らずNG_BOTH(er078_asr_unified_judge_01.py:352 unified_judge、p3_primary_ng) | 不適用(同) | 不適用(同) | LR再TTSは**PASS_WITH_WARNING(force_secondary_agreed)で採用**されたが、減速後再検証でNG_BOTH |
| 最終判定→遷移 | NG_BOTH(slot1) | NG_BOTH(slot2) | NG_BOTH(slot3、最終slotのHR queue記録=human_review_queue.jsonl行94 12:13:13) | LR(RESOLVED_BY_LOCAL_REWRITE)→status OK(AH行15173 `result_status:OK` `final_lock_state:RESOLVED`)→減速後NG_BOTH→STOPPED(AH行15175)→`finalize_a2_slowdown_final_ng`(n3_tts L281)→`record_outcome`→Lock=HUMAN_REVIEW_REQUIRED(AH行15176、RLS reason「最終status=STOPPED。post-process(6%減速)後の音声がASR再検証で不一致: classification=ASR_VALIDATION_UNCERTAIN」)→`FamilyZTtsClipFailedStop` |

**§1-4(3回のTTSのNG根拠)**: attempt1=Primary/Secondaryとも"drank"部を`strained`/`Strength`と認識(2エンジン一致して内容語不一致、M1/Tier3入口外)。attempt2/3=Primaryは名前のみ差異のentity_only UNCERTAIN→M1はF1(Pattern A)が非歯擦音後続(drank)を説明できず不受理、Tier3は副Azureがcanonical語`melos`を返さず不成立、Secondaryは許容集合外。
**LRの経緯(AH行15172/RLSでなく`er011_output/local_rewrite_recovery/run_e2e_04/a2/local_rewrite_recovery_full_story_part3_c1.json`)**: NG span=`melos`→`mello`(Primary転写のみ。`last_asr_text`はprimary)、Luna(gpt-6-luna)候補5件が全7 Gate PASS、`unchanged_ratio`最小の候補1`Melos→He`(single_word_swap)を採用、再TTS(CL行206、flash-lite+`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`)→PASS_WITH_WARNING。

**clip費用/時間(CL行195〜210)**: TTS 4回、OpenAI ASR 5回、Azure 5回(合計120.9秒、単価1.1556/25.18秒=0.0459JPY/秒から約JPY5.5)、Luna 2回。壁時計03:02:28→03:14:25 UTC(約12分、うち固定600秒cool-down)。clip単体の合計JPYは未集計(`run_e2e_04/audit/cost_by_stage_04.json`はstage別のみ[a2配下ではなくrun直下audit]、run合計JPY46.1364/100)。

## 2. 前回PASS(run_e2e_03)との差分
| 項目 | run_e2e_03(PASS) | run_e2e_04(HR) | 区分 |
|---|---|---|---|
| canonical text sha | b6d43773..(TGR reuse_key) | 同一 | 差なし |
| Voice / TTS backend / model | Aoede / speech_metadata_flash_lite / gemini-3.8-flash-lite-tts | 同一(attempt3のjson`model:gemini-2.5-pro-preview-tts`は**記録ラベルの不整合**。実際のAPIはCL行201 `model_id=gemini-3.8-flash-lite-tts`。FZQI7/9の「Pro fallback」記述は誤記) | 差なし(記録ラベル不整合は別件) |
| Style(PD06) sha | 3a680861..(style.effective同) | 同一。fallbackは`natural, clear, conversational`(sha dba23e66..) | 差なし |
| role_style_key / Narration or Dialogue | NARRATOR_FULL_STORY_STD(Narration) | 同一 | **Narration**。③(Std Dialogue=生成時減速指示撤去)は`er063:171`(NARRATOR_STD=PD06+生成後6%)、`style_text_for` L700-707(narratorのみPD06、dialogueはNone)、`ac0ea83fe`のdiff(narrator項は無変更)で**Narratorへ適用されていない**を確認 |
| 速度 | 生成時減速指示なし・生成後6%減速(slowdown_ratio 1.0594) | 同一仕様。LR版に6%適用(23.12→24.492=1.0594) | 差なし |
| FAMILY_Z_ROLE_STYLE_VERSION | z_v2_pd8_r2_e1_e2up_k2_m2_kpx_20261012 | 同一(er063:41) | 差なし |
| Ledger Melos entry | updated_at 2026-10-12(run_03より前) | 同一(2026-10-12。今回run前に更新なし) | 差なし |
| ASR設定 | OpenAI gpt-4o-mini-transcribe/en、Azure en-US PhraseList | 同一。ASR/判定module(er006_secondary_asr_01/er078/er021/er011 CS/er003 n3・crosslevel/er025/er020)は10-17以降**無変更**(`git log --since=2026-10-17`: er063の2commit[10-18 pages、10-19 ③ Dialogue]のみ) | 差なし |
| 検査条件(Gate) | 同 | 同 | 差なし |
| 前回ASR | 減速前 Primary`Mello drank`→Tier3: Azure`Melos drank`→SECONDARY_ASR_CORROBORATED_MATCH(run_03 attempt json)。減速後 OpenAI`Melos drank`×3(本委任の再転写)→PASS | 今回: 上表 | **差は「読み上げ音声の確率的揺れ」+「Azureが返した綴り」のみ** |

→ 差分は**仕様上許容される確率的揺れ**。仕様逸脱・配線差は無い(10-17以降のコード差分はDialogue用の③と試聴ページのみ)。

## 3. A/B切り分け(結論=区別不能・B寄り)
追加ASR実測(`asr_reeval_part3c1_10.py`、`asr_reeval_part3c1_10_result.json`、`asr_reeval_slowed_part3c1_10.py`、`..._result.json`。既存経路=`er006_asr_provider_routing_01.transcribe`、OpenAI、prompt無し、新規TTS 0):
| wav | 再転写3回の名前部 |
|---|---|
| run04 attempt1(元の記録は`Melo strained`) | Mello drank / Mello drank / Melo drank |
| run04 attempt2 | Mello / Melo / Mello |
| run04 attempt3 | Mello / Mello / Melost |
| run04 LR版(減速前) | He drank ×3(名前なし) |
| run03 attempt1(減速前、PASS時) | Mello / Mello / Mellowe |
| run03 最終(減速後、PASS) | Melos ×3 |
| 診断: run04 attempt1/2/3に既存6%減速(ローカルffmpeg、scratchコピー)を適用して各2回 | att1: Mello,Mello / att2: Mello,Mello / att3: Mello,Melo |
B寄りの根拠: (1)同一wavで綴りが変わる(attempt1の"strained"=TRUE_CONTENT_MISMATCHは再転写で消える→"drank"は音声に存在) (2)run04の3 attemptは減速前のOpenAI転写がrun03のPASS音声(減速前)と同型(Mello) (3)全転写で最初の音節は`Mel-`(Mee-/Mil-/Mal-は無し)=期待発音の母音/ɛ/と整合 (4)Azureに`Mellows`(語末z)や`Melost`(OpenAI)があり語末sibilantは存在し得る。
A側の弱い根拠: (a)run04 attempt群の減速後転写は`Mello`が5/6でrun03減速後の`Melos`3/3と異なる(語末/s/の顕在度が低い可能性) (b)Azure(PhraseListあり)は本件3attemptで0/3 Melos(run03は1/1)。
不足証拠: ①人間の試聴(約9〜11秒付近。無音区間検出からの推定でattempt1≈10.7秒、attempt2≈9.8秒、attempt3≈9.3秒付近) ②語単位強制アライメント/語末摩擦音の音響測定(未実施) ③第3の独立ASR(未実施)。ASRだけでは"綴りの再現可否"しか分からず、仕様(CURRENT_SPEC L1827「ASR consensus ≠ pronunciation verification」、OPEN-318)も発音の良否のASR自動判定を認めていない。

## 4. 配線漏れ・不具合の判定(3区分)と修正
| 対策 | 区分 | 根拠 |
|---|---|---|
| Primary ASR | 仕様どおり発動 | AJ/TGR |
| Secondary ASR(Azure、1回+cache) | 仕様どおり(att1=P3、att2/3=Tier3呼出をcache流用で重複Azure 0) | AJ cache:true、CL |
| M1 | 仕様どおり発動し受理条件外(att1は入口条件外) | M1R。置換案mello→meloは生成されたが、F1 Pattern A(`er011_b1_connected_speech_validator_01.py:153-168`)は**次語頭が歯擦音の場合のみ**説明可。本件の次語`drank`は/d/→`_post_check`(er006_m1_multi_candidate_01.py:407)で不受理。CURRENT_SPEC L2792-2799のMelos実績21/24は後続がs始まり語。**M1は設計どおり。バグではない** |
| Tier3 corroboration(er021) | 仕様どおり | er006_secondary_asr_01.py:805-860。副が位置一致でcanonical語を返さないと不成立 |
| PASS_WITH_WARNING/secondary_confirmed | 仕様上の適用条件外(att1〜3)。LR版には適用 | er078 unified_judge L352-550 |
| Ledger(PhraseList・M1 C2) | 仕様どおり | ledger key ec716e..、M1R |
| TTSへの発音ヒント注入(Resolver) | 仕様上の発動条件外 | er025_..core_01.py:462 `min_confidence="medium"`、Melos=low/cascade_unresolved。CURRENT_SPEC L2137は「TTS Pronunciation Hint未配線」。OPEN-318「TTS注入は別Phase」 |
| 6%減速の再検証(統一judge) | 仕様どおり動作したが**書換え前原稿と照合** | n3_tts `apply_a2_slowdown_postprocess` L182-282は引数`tts_input_text`(書換え前)で判定。**OPEN-283(未承認候補)**。what-if(本委任のoffline、`lr_slowdown_whatif_part3c1_10.py`): 同じ減速後転写を`書換え前canonical`で判定=ASR_VALIDATION_UNCERTAIN、`書換え後の実送信文`で判定=NORMALIZED_MATCH(should_pass=True) |
| **Local Rewriteの発火条件** | **仕様乖離(抑止すべきLRが発動)** | CURRENT_SPEC L2816「発火条件=…両エンジン合意誤読(`identify_ng_span`の差分spanが一致)…エンジンごとに転写が異なる場合は書き換えずHR」。DESIGN_01 §4-7⑤・変更表#17に「`run_local_rewrite_recovery`入口の合意誤読ガード」。**コードに不在**: `er020_tts_retry_local_rewrite_01.py:708-775`(run_local_rewrite_recovery)は`last_asr_text`(primary転写のみ、crosslevel L395-)で`identify_ng_span`するのみ。IMPLEMENTATION_02b〜13・CLOSEOUT_PLAN_07に当該実装記録なし。本件はPrimary`Mello`/Azure`Mellow strength`で不一致=仕様ではLR不可・HR直行 |
| HR Lockへの遷移 | 仕様どおり | `finalize_a2_slowdown_final_ng` n3_tts L281、`record_outcome` er011_human_review_lock_01.py:357 |
| 記録ラベル不整合 | 別件(軽微) | attempt3 jsonの`model`が`p9a.ENGLISH_MODEL_NAME`固定ラベルで実backend(flash-lite)と不一致(crosslevel L231付近の`save_tts_attempt_audio`引数) |

**「発動すべきなのに発動しなかった」=0件。修正は実施せず(コード/Regression変更なし、HR Lock不変)。** 修正を見送った理由:
1. LRガード(仕様乖離): 「合意」の定義はADDENDUM §5が"語一致またはARPAbet距離が閾値以下"とするが**閾値が未定義**(OF-AUW-07でOpusが定義の内部矛盾を指摘)。閾値を私が決めると品質基準の新設・変更になる(D-1違反)。また実装すると**本件ではHRが減らず**(LRなしでもattempt3でHR)、b1bの`part3_c1`(run_04ではLRでMelos→Heが無HRで通過済み)など**他箇所のHRが増える**(ユーザーの「不要なHR削減」目的と逆方向)。X/B1/Z全Familyに波及する。→判断候補。
2. OPEN-283: 未承認候補(OPEN_ITEMS L786「ユーザー判断待ち・未実装」)。修正すると本件は自動PASS_WITH_WARNING(LR_REWRITTEN)になるが、**名前が音声から消える**文が自動採用される品質判断を含む。→判断候補。
3. 上記2点は互いに逆向きの対策(LRガード=書換え抑止、OPEN-283=書換え救済)。**一括でユーザー判断**が必要。

## 5. HR依頼の再提示案(必要と判断。`user_test/family_z_melos_hr_run04/index.html`を更新済み、音声ファイル5本は不変)
- 疑い: ①語末s/zが弱い・drankと溶ける(A) ②読みは許容範囲で聞き取り側の綴りが揺れているだけ(B)。 ③自動書換え版(録音4=現在ファイル)は名前が消える。
- 確認箇所: 各録音の約9〜11秒付近(3文目直後のMelos drank)。期待=メロス(/ˈmɛlɒs/ または /ˈmɛloʊs/)、観点=語頭がメル(Mel-)か/語末ス・ズが聞こえるか/直後drankが明瞭か/前後の途切れ。
- 各録音の機械判定: 録音1=TRUE_CONTENT_MISMATCH(両エンジンとも`strained/Strength`)、録音2=UNCERTAIN(主`Mello`/副`Mellows`)、録音3=UNCERTAIN(主`Mello`/副`Mellow strength`)、録音4=書換え後の文としてはPASS_WITH_WARNING相当、停止原因は原稿(Melos入り)との照合。
- 人間判断→次処理: (a)録音N承認→最終音声確定(他clipと同じ6%減速を機械適用)→Lock解除→Gate→assemble→pages、追加費用ほぼ0 / (b)全却下→再生成(Fable許可で最大2回、JPY2〜5。ただし過去3回自動合格せず再度HRの可能性) / (c)録音4承認=この文のみ名前なし(Advanced版は同じ書換えで通過済み、整合) / (d)保留。
- ページ訂正点: 前回の「現在ファイル=録音3の後処理版」は誤り(実体=LR版の6%減速、`full_story_part3_c1_original.wav` sha40c6907e..がLR減速前)、ASR(副)を録音3にも記載(attempt3のAzure=`Mellow strength`はAH行15173で確認、前回は「記録なし」と表示)。

## 6. 再発防止評価(ユーザー§4)
**防げなかった理由**: ①仕様の空白(CURRENT_SPEC L1827: CMU未収録の外国由来固有名詞は"HR行きのまま"。M1が限定的に置換したが、F1 Pattern Aが次語歯擦音に限られるため`Melos`+非歯擦音語は対象外。OPEN-318 R1「語末s名+s始まり語」と同根) ②確率的揺れ(同一設定でAzureが"Melos"を返すかが運次第) ③仕様乖離(LRガード不在)と未承認候補(OPEN-283)の組合せで、ASR不一致が"名前消去版の減速後NG"に化けてHRに到達。配線漏れ(発動すべきなのに未発動)は0。
**量産時の再発見込み(実績)**: Family Z Melos run_e2e_01〜04の全clip 274(a2+b1b)中、非OK 5(1.8%)=HRまたはSTOPPED。うちMelos名を含むEN clip(約50)でのHR/STOP=3(run_02 part1_c5 a2/b1bの2、run_04 part3_c1の1)=約6%。run_03は名前含有13 clip中0。run_04はa2 29 clip中1(3.4%)・b1b 30中0(ただしb1bのpart3_c1はLRでMelos→Heが無HRで通過、audio_text_deviationに記録)。1記事あたり名前入りclipが約13本なら、p≈6%で**約0.8回/記事**(推定、n小)。固有名を多く含む物語ほど上がる。
**改善候補(すべて"候補・Production未採用"。優先順は既存機構を先)**
| ID | 内容 | 既存機構との関係 | 効果 | QCD | 要判断 |
|---|---|---|---|---|---|
| R-A | OPEN-283是正: 減速後再検証を書換え後の実送信文で照合 | 既存`apply_a2_slowdown_postprocess`の引数のみ(L182付近、呼出元の`result["text"]`渡し) | 本件型(LR後減速NG)を自動PASS_WITH_WARNING化 | Q: 名前が消える文を自動採用(LR_REWRITTEN警告+試聴リストで事後確認可)/C: 実装JPY0・testのみ、HR待ち削減/D: 待ち時間削減 | 要(OPEN-283未承認) |
| R-B | LR発火条件⑤(合意誤読ガード)の実装+「合意」閾値の確定 | CURRENT_SPEC L2816を実装に合わせる(新機構でない) | ASR不安定を原稿書換えで隠さない。ただし本件でもHRは残り、他でHRが増える | Q+/D−(HR増)/C≈0 | 要(閾値の新設=Opus定義矛盾OF-AUW-07の決着) |
| R-C | Pronunciation Ledgerの`Melos`を、1回の人間試聴で読み確定(OPEN-318 C-a)し、work_canon英語読み+confidenceをmedium以上へ → Resolverが発音ヒントをTTS style prefixに注入 | **既存Ledger/Resolverをそのまま使用**(新機構なし)。ただし"TTS注入は別Phase"(未承認) | 上流で語末sの発音を安定化しうる(根拠:同種Trialの効果は未検証) | Q+/D: 1回のHR(今回の判断と兼用可)/C: 追加Trial要(見積前)。Style sha変更→Melos含むclipの再利用キー変化 | 要(Production挙動変更) |
| R-D | M1/F1の歯擦音限定を非歯擦音後続へ拡張 | 既存M1/F1 | — | Opus独立レビューで不採用済み(OPEN-318 C-b、安全≠成功原則に反する) | 非推奨 |
| R-E | Azure以外の第3エンジン/OpenAI promptにLedger語を渡す | `routing.transcribe(prompt=)`は既存だが綴り誘導で誤受理リスク | 未知 | 綴りだけで受理しない原則(CURRENT_SPEC M1節)に抵触しうる。Trial要 | 非推奨(先に不要) |
**推奨**: 今回のHR判断(聴感)を"Melosの許容読み確定"として記録し(R-C)、R-A/R-Bはセットでユーザー判断(逆方向の施策なので片方だけ採用しない)。以上は採用せず提案のみ。

## 7. E-1 既存仕様照合(仕様上の発動条件、行番号付き)
| 対策 | 仕様(CURRENT_SPEC行) | コード(関数:行) | 実績との突合 |
|---|---|---|---|
| Audio Validation Gate/Human Review Lock | L2113(3回不合格→cool-down600秒→LR→HR)、L2801-2816(統一ASR判定) | `PRODUCTION_MAX_TTS_ATTEMPTS=3`(er011_human_review_lock_01.py:80)、`record_outcome` :357 | 仕様どおり(3回+LR1回) |
| 統一ASR判定(PASS/PASS_WITH_WARNING/NG_*) | L2801-2815 | er078_asr_unified_judge_01.py:352 unified_judge | 仕様どおり |
| Secondary ASR | L2807(Primary NG→原則Secondary 1回+cache) | er006_secondary_asr_01.py:682 evaluate_attempt_with_cascade_detail、:751 cache | 仕様どおり |
| M1複数発音候補 | L2792-2799 | er006_m1_multi_candidate_01.py:248 freeze_candidates、:425 _entry_gate、:407 _post_check、:485 judge。呼出 er006_secondary_asr_01.py:896,946 | 仕様どおり(受理条件外) |
| F1 Pattern A | (M1の内側) | er011_b1_connected_speech_validator_01.py:153-168 | 仕様どおり(次語歯擦音のみ) |
| EN ASR semantic equivalence(Tier3) | L2142 | er021_en_asr_semantic_equivalence_production_01.py:731 corroboration_supports、:739-770 determine_sub_reason。呼出 er006_secondary_asr_01.py:805-860 | 仕様どおり |
| Pronunciation Ledger | L2137(ASR側配線のみ・TTS Hint未配線) | er006_pronunciation_ledger_01.py(get_hint_for_text)、n3_tts _post_slowdown_unified_judge L121付近 | 仕様どおり |
| Pronunciation Resolution Core(er025) | L2137次項/OPEN-318 | er025_entity_pronunciation_resolver_core_01.py:439-462、repro01:305,585 | 仕様どおり(medium未満は注入しない) |
| 固有名詞ASR不一致 | L1827 | (M1以外は自動PASSなし) | 仕様の空白(CMU未収録名×非歯擦音後続) |
| Local Rewrite | L2113、**L2816(発火条件⑤)** | er020_tts_retry_local_rewrite_01.py:708、crosslevel:386 | **仕様乖離(⑤未実装)** |
| 6%減速後再検証 | L2810(統一judge)+OPEN-283 | n3_tts:121(_post_slowdown_unified_judge)、:182 | 仕様どおり。OPEN-283未承認 |
| Family Z音声仕様 | er063:41,162-182,700,773-790 | narrator=PD06+post6%、Dialogue=③ | Narrationへ③未適用を確認 |
OPEN-318: Melos語末s名+後続語の問題の実績に本件を追記(R1型の非sibilant後続)。OPEN-419: 本分析を追記。#116: 分析結果=B寄り・区別不能、HR再提示、Status=HR再提示(Fable判定待ち)。

## 8. 付録: 保存した証跡
- `docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/`: `m1_offline_replay_part3c1_10.py`/`_result.json`(M1 offline再判定、API 0)、`asr_reeval_part3c1_10.py`/`_result.json`(OpenAI 18呼出)、`asr_reeval_slowed_part3c1_10.py`/`_result.json`(6呼出、scratch上の減速コピー)、`lr_slowdown_whatif_part3c1_10.py`/`_result.json`(OPEN-283 what-if、API 0)。
