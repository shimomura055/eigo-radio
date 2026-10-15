# B_ARTIFACT_OBSERVATION_01(FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01 委任_01B、2026-10-15、成果物側の実artifact観測)

性質: Read-only監査。有料API 0(JPY0)、音声再生成0、SSOT/コード/Prompt/profile/音声/user_test無編集。到達Status: `AUDIT_PART_B_COMPLETE`(仕様判定は01A/委任_02/Fableに委ね、本書は「観測事実」のみ)。
KPI provenance: すべて`reuse`(既存artifact・ログ・validation記録の読取)。`fresh`は完成MP3の音声長のみ(`soundfile`、ffprobe無し・ローカル無料)。使用モデル: LLM/TTS/ASRの新規呼出なし。
略称: RUN=`er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01`、TR=`<level>/audit/tts_generation_results.json`(Std=a2、Adv=b1b)。コード行番号は`git show 64d3ec975:<path>`のHEAD固定版。Machine-readable版: `B_SEGMENT_PROVENANCE_01.csv`(68行)。

## §0 超サマリ(10行)
1. 完成版final_03の実態: Std/Advとも`--stage assemble`は成功(Std 314.865秒/Adv 315.430秒、完成MP3と試聴ページの音声長は完全一致)。M3 Style Gate=両level PASS。ただしGate対象は「profile対象role」のみ(Std 8 segment/Adv 9 segment)。
2. **In One Lineは両levelとも1文15語**(Std「Falling coffee bean prices may take at least nine months to affect US shop prices.」/Adv「…US retail prices.」)。Trial final v3の2文版(Std 31語/Adv 40語)ではなく旧1文版。新2文方針(OPEN-299)は反映されていない(観測)。
3. **gloss再整合の適用版は旧legacy**(`version=ER-003-KP-GLOSS-ALIGN-01`、status=`GLOSS_REALIGNED`、`gloss_alignment_status`キー無し、HR無し)。2026-10-14 20:14 JSTの実行で、corrected設計(2026-10-15 12:40 commit 7ca292b44)より前。Advは日本語glossが音声に使われず再整合も未実行。
4. **K2(KP英語)・M2(KP日本語意味)は反映されていない**: 実使用はProduction既定のKP英語MINIMAL Prompt(1076字、sha 2b0c7505…)とFAMILY_X_ROLE_STYLE_JA(65字、sha ae68e3e6…)。K2(9d905cfe…)/M2(e7617e15…)のhashとは不一致(Std 9 segment、Adv 8 segment=不一致、Std/Adv計3 segmentは記録欠如で推定のみ)。
5. 反映済み(hash一致): Std Preview/Comment1〜4=R2(625826c1…)、Adv Preview=E1(8862317f…、fresh再生成)、Adv KP英英解説5件=P3(a8aaec59…)、Full Story 6件=N01(d1956c91…)、Std Full Story 6%減速実値5.966/5.987/5.969%。
6. **Adv Comment1〜4**は`calm, conversational`(E0、57c3fda6…)でProduction定数とは一致するが、Trial v3の「既存承認E2_UPBEAT」とは不一致(OPEN-350、E0_RECONCILIATION_04)。
7. **固定Master phrase/Intro**: Welcome=A5・Preview intro=B5は**Trialで生成したwav(seed、origin T)**を無加工で組込み。KP intro/Full Story intro/番号はMaster Store(`TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02`)。いずれも`tts_generation_results.json`の`segments`/`key_phrases`に載らず、Audio Validation Gateの走査対象外(`shared_narration={}`)。
8. 由来集計(`tts_generation_results.json`記録あり=Std 21+Adv 25 entry): fresh=Std 11+Adv 5、REUSED_VALIDATED=Std 9+Adv 20、Master cache hit=Std 1(別途seed/store: 固定phrase 9×2 level=18 wav、results外)。Secondary ASR cascade採用=Std Full Story Part2の減速後(Azure、primary 2回 UNCERTAIN後)の1件。
9. 品質参考値(Trial値、合否基準ではない): Std WPM 157.7(参考157±6内)/Adv 178.2(参考167±6外)/文末ポーズ平均Std 629ms(参考ref≦498ms外)・Adv 572ms(参考≦593ms内)/800ms以上の無音 Std 5・Adv 0。測定対象はFull Storyのみ。
10. 確認できなかった事項: 日本語読みの聴感(人手)、固定phrase(A5/B5/shell)の生成時Prompt全文hash(results記録なし)、Adv Preview/Comment1〜4の`sha256`欄(entryに無い)、raw_usage_logにgloss再整合/In One Line生成のtag行が無いこと(stage/segment=None)、Adv In One Lineをwav sha 897ca8bf…にした再利用元の生成時刻詳細。

---

## §1 原稿構成表(parts.json、segment_plan.json、試聴ページ)
共通: title=「Coffee Bean Prices Fall. Are Price Tags Still on a Journey?」、10段落、boundary_i=3/boundary_j=7(Part1=段落1-3、Part2=段落4-7、Part3=段落8-10)、Story分割数=**3 part**。記事source=`er019_output/coffee_prices/run_v5_ms_01/{a2,b1b}/article.md`(`RUN/audit/scaffold_article_sha256.json`: a2 `a3cc7bb98af7…`、b1b `d9b77190905d…`)。`rf_tts_guard.json`のa2に警告`a2_derived_from_advanced_sha_mismatch(観測のみ)`。

### Standard(a2)
| 順 | segment(segment_plan.json) | 種別 | 語数(parts.json word_counts) | 文数(概算) | 備考 |
|---|---|---|---|---|---|
|1| Intro | SFX | – | – | mp3 10.7秒 |
|2| Welcome | FIXED_SHARED | – | – | 固定(A5 seed) |
|3| Topic intro | TOPIC_INTRO | – | 1 | 「Today's topic is Coffee Bean Prices Fall. Are Price Tags Still on a Journey?.」 |
|4| Japanese title | JAPANESE_TITLE | – | 1 | コーヒー豆は値下がり。値札は、まだ旅の途中？ |
|5| Notification 1 | SFX | | | |
|6| Preview intro | FIXED_SHARED | | | 固定(B5 seed) |
|7| Preview | PREVIEW(JA) | – | 2 | R2 |
|8| Notification 2 | SFX | | | |
|9| Key phrases intro | FIXED_SHARED | | | store |
|10| Key Phrase 1..5 | KEY_PHRASE | – | – | 英語KP→日本語意味→(英語KP繰返し無し) |
|11| Notification 3 / Full story intro | | | | |
|12| Comment 1 → Full Story Part1 | COMMENT / FULL_STORY | 118(実数117) | 13 | 推定47.2秒(plan) |
|13| Comment 2 → Part2 | | 163(161) | 13 | 推定65.2秒 |
|14| Comment 3 → Part3 | | 134(134) | 11 | 推定53.6秒 |
|15| Comment 4 | COMMENT | – | 3 | 「…最後に、英語で記事の要点を振り返ります。」 |
|16| **In One Line** | IN_ONE_LINE | **15** | **1** | 推定11.7秒(plan)/実測6.225秒 |
|17| Outro | SFX | | | 6.144秒 |
合計本文語数415(plan `body_word_counts`)。

### Advanced(b1b)
同順(Welcome/Topic intro/Preview intro/Preview/KP intro/KP×5/Full Story intro/Comment1→Part1/…/Comment4/In One Line/Outro)。Japanese titleは無し。Part語数131/178(実179)/152、合計461。文数(概算)Part1=8、Part2=12、Part3=8。In One Line 15語・1文。plan推定6.0秒/実測5.28秒。

### In One Line 実文と生成Prompt所在
| level | 実文(parts.json `in_one_line`) | 文数 | 語数 | TTS入力(数字正規化後) |
|---|---|---|---|---|
| Std | 「Falling coffee bean prices may take at least nine months to affect US shop prices.」 | **1** | 15 | 「…at least 9 months…」 |
| Adv | 「Falling coffee bean prices may take at least nine months to affect US retail prices.」 | **1** | 15 | 「…at least 9 months…US retail prices.」 |
- 出所: `RUN/{a2,b1b}/parts.json`の`in_one_line`キー、`TR`の`segments.in_one_line.text`/`canonical_text`(canonical=parts一致)。Full Story 3 partも`canonical_text`==parts(引用符・空白正規化後、6 segmentすべてTrue)。
- Trial v3の2文版との差: `er057_output/coffee_final_audio_assembly_01/IN_ONE_LINE_REWRITE_01.md`は新原稿 Std「Coffee bean prices fell, but shop prices may take at least about nine months to change. Other costs also matter, so lower bean prices do not promise a cheaper cafe cup.」(31語2文)、Adv 40語2文を確定、「旧(参考)=1文」と明記。final_03は**旧1文**(観測)。ADv seed(`seed_provenance_03_assemble.json`、wav sha `645cac39…`=2文版13.36秒)は`b1b/validation_state_rebuilt_01.json`で`WITNESS_SHA256_MISMATCH`により不採用、実在wavは5.28秒(sha `897ca8bf983e…`、tone-run由来REUSED_VALIDATED)。
- **生成Promptの所在**: In One Line**原稿**の生成Prompt本文/hashは`RUN`内に専用記録なし。parts.jsonは`scaffold`段(raw_usage_log.jsonlの`stage=scaffold`、gpt-6-luna、2026-10-13 10:25〜13:32 UTC計15 call=複数scaffold run)の出力の一部。個別tag/promptファイルは**未確認**(`RUN/raw_usage_log.jsonl`の100行は`stage`/`segment`のみで`tag`欄が無い)。In One Line**TTS**のStyle: Std `style_prefix` 266字(sha `10e21170b1b13b9f577f1642a987511eaa68eed7334aeb6807ecc2fb4f01b860`)=`FAMILY_X_ROLE_STYLE_EN["IN_ONE_LINE"]`(82字、sha `63495557ec82…`)+A2減速指示、Adv=82字そのもの。

### 各Commentと本文の接続(観測)
Std(JA、R2): C1「コーヒーの価格を示す数字がどう変わり、豆の供給がどう関係しているのかに注目してください。」→Part1(豆価格下落・供給)。C2「…お店の値札はすぐには変わらないようです。では、…どれくらいかかるのでしょうか。」→Part2(約9か月)。C3「…これからは、豆の価格の変化が店の価格にどう関わるのかに注目してください。」→Part3。C4「…カフェの値段には、豆以外の費用も関わっています。最後に、英語で記事の要点を振り返ります。」→In One Line。**C4は「最後に」を含む**(承認済みComment4 Prompt2文追加と整合する観測)。
Adv(EN、E0): C1「Listen for how the news about bean prices compares with the prices people see in shops.」/C2「…But when might that change show up on a price tag?」/C3「So far, bean prices have fallen… The 2 figures cover different things… notice what happens between the raw beans and the price customers pay.」(17.9秒、最長)/C4「…There can be a delay, and other costs matter too. Now, let's bring the main idea together.」。いずれも本文Part内容と話題は接続(人手の意味判定は未実施)。ページには**Comment・Preview・KP英英解説・In One Lineの本文は表示されない**(index.htmlはFull Story本文とKPのみ)。
Std Preview/Comment textは`run_v5_ms_01`の`a2_support_texts.json`コピー(`audit/seed_provenance_02.json`)。

### 難易度・原稿整合(観測のみ)
Std 415語 vs Adv 461語(Part語数はAdvが11〜13%多い)。Advの文は長め(Part1: 8文/131語)でStdは短文(13文/117語)。Stdは平易化版、AdvはPart1に長い並列文を含む。difficultyの正式判定は本監査範囲外(未確認)。

---

## §2 KP表
### Standard(`RUN/a2/key_phrases/keywords_canonicalized.json`)
| rank | 英語KP(used_form) | display | 日本語gloss(=TTS読み) | source_span / canonicalization_source_span | candidate | Rule7関連 | canonicalization qa | `gloss_alignment`/status |
|---|---|---|---|---|---|---|---|---|
|1|pump one's fist|pump one's fist|大喜びする|pumps its fist(canon:なし)|C27(reserved slot,rule_poss_pattern)|qa_traceable_contiguous_span=PASS|PASS|なし|
|2|raw bean|raw bean|生豆|raw-bean(canon:「raw-bean prices take at least」)|C21|PASS(**candidate_mismatch_suspected=true**)|PASS|なし|
|3|right away|right away|すぐに|right away|C5|PASS|PASS|なし|
|4|based on interviews|based on(`changed_from_display_phrase=true`、`restore_semantic_complement`)|インタビューをもとにした|based on(canon:「based on interviews」、`kp_extends_beyond_candidate=true`)|C1|PASS|PASS|**version=ER-003-KP-GLOSS-ALIGN-01、status=GLOSS_REALIGNED、original=「～をもとにした」、verdict=false**(keywords_canonicalized.json:145-148)|
|5|take time|take time|時間がかかる|take time|C7|PASS|PASS|なし|
- overall_status=PASS。`audit/key_phrase_source_gate.json`: PASS(total 5/present 5/missing 0)。`key_phrases_db_hybrid/m2_supply_report.json`: kp_supply=m2、n2=290、n_candidates=28、reserved=[pumps its fist, imagine your usual]、fragment_risk 0、selected_rows(rank1〜5)。`keywords_runtime_metadata.json`: kp_backend=db_hybrid、strategy L、cost JPY0.3731、model gpt-6-luna。redundancy QA=REDUNDANCY_PASS。`scaffold_run_summary.json`: `key_phrases_status=CANONICALIZATION_PASS`、`m2_fallback=null`、`m2_fallback_events=[]`(assemble stdout「[M2-FALLBACK] 発生なし」)。
- 「Rule7」は`qa_traceable_contiguous_span`・`key_phrase_source_gate`で記録され、**専用の`rule7`欄は無い**。rank2「raw bean」は元span「raw-bean」と異なるが本文に「raw beans」が実在するため源gate PASS(観測)。
- 選定数5(KP難易度/意味整合の人手判定は未実施=未確認)。

### Advanced(`RUN/b1b/key_phrases/keywords_canonicalized.json`)
| rank | 英語KP | 日本語gloss(音声未使用) | source_span | candidate | 英英解説(音声) | gloss_alignment |
|---|---|---|---|---|---|---|
|1|time lag|変化が伝わるまでの時間差|time lag|C27|a delay between a change happening and its effect being seen or felt|なし|
|2|show up|価格に表れる|show up|C11|to become visible or noticeable in a place or situation|なし|
|3|come down|値段が下がる|come down|C5|to become lower, especially in price or amount|なし|
|4|pump one's fist|うれしくてこぶしを突き上げる|pumps its fist|C34|to raise a closed hand in the air to show excitement or victory|なし|
|5|hold on|ちょっと待って|Hold on|C8|to wait or pause before doing something|なし|
- overall_status=PASS。m2_supply_report: n2=312、n_candidates=34、reserved=[pumps its fist]、`dropped_non_contiguous=["news your wallet"]`、`u2_removed_tier_h_m1=["lag"]`。英英解説は`key_phrase_explanations_text`(gpt-6-luna、`reused_from_previous_run=true`、max15語QA全PASS、audit.management_id=FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01)。
- 順序: Advは「英語KP→英英解説→英語KP繰返し」(`kp?.english`/`explanation`/`phrase_repeat`の3 entry)、Stdは「英語KP→日本語意味」(`english`/`japanese_meaning`の2 entry、**英語KPの繰返し(3回目)はStdのresultsに無い**)。ユーザー記載の「Standard：英語KP→日本語意味→英語KP」に対し、Stdは実装・entryとも**英語KP→日本語意味の2要素**(page KP行の秒数: Std 6.6〜8.7秒/Adv 9.0〜11.5秒から構成を推定、繰返し音声の有無は`timeline.json`で個別part化されていないため**未確認**)。

### gloss再整合の実際の適用版=旧legacy(証拠行)
1. `RUN/a2/key_phrases/gloss_alignment_runtime_metadata.json:3` `"version": "ER-003-KP-GLOSS-ALIGN-01"`、`:4` `"final_status": "ALIGN_PASS"`、`:7` `targets:[4]`、model_id gpt-6-luna、response_id resp_0ee809aa8b39a19c…(同ファイルのみ。raw_usage_logに無し)。
2. `RUN/a2/key_phrases/keywords_canonicalized.json:145-148`: `gloss_alignment.version=ER-003-KP-GLOSS-ALIGN-01`、`status="GLOSS_REALIGNED"`。**`gloss_alignment_status`キー・`mode`キー・HR項目は0件**(grep、a2/b1b両方)。
3. HEAD固定コード`64d3ec975:er003_key_words_gloss_alignment.py`: `:39 GLOSS_ALIGNMENT_VERSION = "ER-003-KP-GLOSS-ALIGN-01"`、`:363 "status": "GLOSS_REALIGNED" if changed else "GLOSS_ALREADY_CONSISTENT"`(legacy書込)、`:510 GLOSS_ALIGNMENT_MODE = GLOSS_ALIGNMENT_MODE_LEGACY`、`:512 STATUS_HR_REQUIRED=…(correctedのみが書く)`、`:121 select_alignment_targets`(`kp_extends_beyond_candidate`またはdisplay語追加itemのみ=target1件)。
4. 実行時刻: `gloss_alignment_runtime_metadata.json`のmtime=2026-10-14 20:14(JST)。corrected設計commit `7ca292b44`は2026-10-15 12:40(JST)=本Coffee音声より後。CHECKLIST_05 #11: 「gloss再整合工程は新しい処理フロー1段で、ユーザー承認・Opus条件A・Fable判定が未実施」と自認。`keywords_canonicalized_before_gloss_align_04.json`: rank4 gloss「～をもとにした」(置換前)、他4件は無変更。
5. 結論(観測): 完成音声の日本語glossに使われたのは旧legacy(rank4のみ「～をもとにした」→「インタビューをもとにした」)で、corrected工程(唯一化・mapping_gate・HR・既定ON)の適用ではない。Std rank1〜3,5は再整合の入力にならず(target外)。Advは日本語glossを音声に使わないため再整合はそもそも未実行。

---

## §3 Voice/Style照合表(全segment。詳細は`B_SEGMENT_PROVENANCE_01.csv`)
照合方法: 期待Style=SSOT記載role(CURRENT_SPEC:2620-2626)・`er019_family_x_style_profile_01.py`(定数と`sha256_text`)・`er033_tts_flash_lite_family_x_styles_01.py`・Trial `er057_tone_trial_kp_ja_gen_01.py`(K2/M2)・`er057_tone_trial_tts_gen_01.py`(A5/B5)。実使用=`TR`のentry `style_prefix`のsha256(`hashlib.sha256(text.encode('utf-8'))`、`sha256_text`と同一方式)+`style_profile`欄。Style定義hash:
R2 `625826c1…2252f`(168字)/N01 `d1956c91…0477`(202字)/E1 `8862317f…c4cb`(68字)/P3 `a8aaec59…acc`(141字)/K2(Trial、332字)`9d905cfe6c040cd001c4e7877327044f540a72bd315776f2c297e0f58f7aea42`/M2(Trial、67字)`e7617e15c29e43cb76668d77e6c7102671754aae810fb15cd9367294f71a228d`/TOPIC_INTRO `d16e099c…`/JA既定 `ae68e3e6…`/IN_ONE_LINE `63495557…`/COMMENT(E0) `57c3fda6…`/A5(125字)`2c530b21d351…`/B5(127字)`5e28dd287f20…`。実使用KP英語MINIMAL(1076字)sha `2b0c7505f48ee5470fbe866535088f01704634b4973d22c7f90b8f021fc3696d`。

actual model_id: 全TTS entryで`gemini-3.8-flash-lite-tts`、backend=`speech_metadata_flash_lite`、voice=Std Aoede/Adv Full Story・IOL・KP Aoede+topic/preview/comment Charon。ASR primary=gpt-4o-mini-transcribe、secondary=azure(raw_usage_log)。KP canonicalization/gloss/英英解説/scaffold=gpt-6-luna(最新世代上位系)。

### Std(a2)
| segment | 期待Style | 実使用hash(先頭12) | 判定 | profile | 6%減速 | 由来 | ASR(audio_classification) |
|---|---|---|---|---|---|---|---|
| Intro/Outro | SFX | – | N/A | – | – | asset mp3 | – |
| Welcome | A5 | 記録なし(wav sha 44f6ceb9…=Trial A5.wav) | **証拠不足**(間接的にTrial一致のみ) | – | – | seed T | results外 |
| Preview intro | B5 | 記録なし(wav sha 19932746…=Trial B5.wav) | 証拠不足 | – | – | seed T | results外 |
| Key phrases intro/Full story intro/num×5 | 既存承認 | manifest key(charon_english_fixed_shell v3_champion) | 部分(manifest sha一致、Prompt本文hash未確認) | – | – | Master Store seed(origin P) | manifest `asr_verified=true` |
| Topic intro | TOPIC_INTRO(E2) | d16e099c | 一致 | – | – | REUSED_VALIDATED(run_e_tone_01) | NORMALIZED_MATCH |
| Japanese title | JA既定 | ae68e3e6 | 一致 | – | – | fresh | NORMALIZED_MATCH |
| Preview | R2 | 625826c1 | **一致** | coffee_final_v5(R2同sha) | – | REUSED_VALIDATED(run_v5_ms_01) | NORMALIZED_MATCH |
| Comment1/2/3/4 | R2 | 625826c1 | **一致**×4 | 同上 | – | REUSED_VALIDATED(v5_ms_01) | EXACT/NORMALIZED/NORMALIZED/PHONETIC_MATCH |
| KP1 英語 | K2 | 記録なし(Master cache `17447f5f19aeda376599ac2b`、style_instruction_id=key_phrase_english_component v2_margin030) | 証拠不足(推定=MINIMAL、K2不一致) | – | – | MASTER_CACHE_HIT(2026-10-13T19:46:06作成) | asr_verified、disfluency未flag |
| KP2〜5 英語 | K2 | 2b0c7505(MINIMAL 1076字) | **不一致**×4 | – | – | fresh | NORMALIZED_MATCH×4 |
| KP1〜5 日本語意味 | M2 | ae68e3e6(JA既定65字) | **不一致**×5 | – | – | fresh | EXACT×4/NORMALIZED×1 |
| Full Story P1/P2/P3 | N01 | d1956c91 | **一致**×3 | coffee_n01_r2_p3(P1,P3)/…_e1(P2) | 実値5.966/5.987/5.969%(target6) | P1,P3=REUSED_VALIDATED(same_out_dir)、P2=fresh | P1 NUMERIC_EQUIV、P2 NORMALIZED(減速後primary ASR_VALIDATION_UNCERTAIN→**secondary azure cascade採用**)、P3 NORMALIZED |
| In One Line | 既存承認(IOL const+A2減速指示) | 10e21170b(=63495557+減速指示) | 一致(構成は既存。**新2文方針未反映**) | – | 5.873% | REUSED_VALIDATED(run_e_tone_01) | NORMALIZED_MATCH |
### Adv(b1b)
| segment | 期待Style | 実使用hash | 判定 | 由来 | ASR |
|---|---|---|---|---|---|
| Welcome/Preview intro(Charon) | A5/B5 | 記録なし(Trial wav一致) | 証拠不足 | seed T | results外 |
| KP intro/FS intro/num×5 | 既存承認 | manifest key | 部分 | Master Store | manifest |
| Topic intro | TOPIC_INTRO | d16e099c | 一致 | REUSED(run_e_tone_01) | NORMALIZED |
| Preview | E1 | 8862317f | **一致**(style_profile PREVIEW、gate PASS) | **fresh**(seed E1.wav `c7a8bb97…`はwitness mismatchで不採用、実在wav `0370f184…`12.07秒、entryにsha256無し) | NORMALIZED |
| Comment1〜4 | Trial v3「既存承認E2_UPBEAT」/ Production定数E0 | 57c3fda6(`calm, conversational`) | Production定数と一致、**Trial v3とは不一致** | fresh(tone seed `200ad3c7…`等と別sha、entryにsha256/VI無し、c2に再生成1回) | EXACT/NORMALIZED/NUMERIC_EQUIV/EXACT |
| KP1〜5 英語(+繰返し) | K2 | 2b0c7505(記録あるもの8件)、kp2 english/phrase_repeatは記録なし | **不一致**8/証拠不足2 | REUSED_VALIDATED(same_out_dir) | EXACT/NORMALIZED(kp4は再試行1回) |
| KP1〜5 英英解説 | P3 | a8aaec59 | **一致**×5 | REUSED_VALIDATED(same_out_dir) | NORMALIZED×5 |
| Full Story P1/P2/P3 | N01(減速なし) | d1956c91 | **一致**×3 | REUSED_VALIDATED(`same_out_dir_clobbered_by_only_segments_rerun`、証拠=`backup_entry_wav_mtime_before_overwrite_and_trimmed_duration`=**sha一致ではなくmtime+長さ**による継承) | NORMALIZED×2/HIGH_SIMILARITY_SAFE(P3) |
| In One Line | 既存承認(IOL const) | 63495557 | 一致(**新2文方針未反映**) | REUSED_VALIDATED(run_e_tone_01) | NORMALIZED |

### 集計(CSV 68行からIntro/Outro SFX 4行を除く64行=Std 30/Adv 34)
- 一致(MATCH/MATCH_BASE+SLOWER_HINT/MATCH_PROD_CONST): Std 11、Adv 15。
- 不一致(MISMATCH): Std 9(KP英語4・KP日本語意味5)、Adv 8(KP英語/繰返し)。
- 証拠不足(EVIDENCE_GAP): Std 3(Welcome、Preview intro、KP1英語)、Adv 4(Welcome、Preview intro、kp2 english、kp2 phrase_repeat)。
- 部分(EVIDENCE_PARTIAL=固定Master phrase manifest sha一致のみ): Std 7、Adv 7。
- Welcome/Preview introのA5/B5は、hashはTrial wavとの一致のみ。Production runner経由で生成されたものではない(`seed_provenance_04_std_assemble.json`/`seed_provenance_03_assemble.json` `origin:"T"`)。

### P8/PD8/N01の上書き経緯(観測、コード内コメント+SSOT)
- 2026-10-12以前: Full Story=PD8(CURRENT_SPEC:2620)→2026-10-12ユーザー決定でP8へ置換(`er019_family_x_style_profile_01.py` L38以下、P8 sha `3eadf4f6…5595`、profile `coffee_p8`)→2026-10-12 V5でR2(Std Preview/Comment)・P3(Adv KP英英解説)追加(`coffee_final_v5`)→2026-10-13 N01で上書き(`coffee_n01_r2_p3`、sha `d1956c91…`)→E1追加(`coffee_n01_r2_p3_e1`、2026-10-13 22:30移行、`audit/style_profile.json`/`style_profile_migrated_from_01.json`)。`RUN/audit/style_profile.json`: overridden_roles=[FULL_STORY,KP_EXPLANATION_EN,PREVIEW,SUPPORT_JA]。**K2/M2/A5/B5は上記profileに含まれず**、`er019_family_x_style_profile_01.py:16-17`が「他Role(K2/M2/A5/B5/E1/R2等)は後続Phase」と明記、OPEN-313(COFFEE-STYLE-PROFILE-PHASE2-ROLES-HANDOFF-01)で申し送り。
- 現在の実使用profile: Std Part2のentry表示は`coffee_final_v5`(古いentry継承)と`coffee_n01_r2_p3_e1`(新規Part2)が混在するが、overrideしたbase sha(N01 `d1956c91…`/R2 `625826c1…`)は全てprofile定義と一致(`style_profile.expected_base_sha256==style_base_sha256` Trueを全8+9 entryで確認)。

### Audio Validation Gate・M3 Style Gate・固定Master phraseの走査外根拠
- Audio Validation Gate: `64d3ec975:er003_v1_n3_01_assemble.py` `:89 AUDIO_GATE_ALLOWED_STATUSES=("VALIDATED","HUMAN_APPROVED")`、`:469-508 verify_episode_audio_validation_gate`: 走査対象は`data["segments"]`と`data["key_phrases"]`のみ(`:478-500`)。**固定Master phrase(welcome/preview_intro/key_phrases_intro/full_story_intro/num_*)は、B1ローダ`:548`/`:552`で`narration/*_charon.wav`を直接読むだけでGate走査を通らない**。Std(A2)ローダ`load_a2_sources :739-`は共有名を`c.A01_NARRATION_DIR`から読む実装で、Coffee Stdはrunnerの正式assemble前に`er071_coffee_assemble_seed_04_std.py`(docstring :1-5「tts_generation_results.jsonに載らずAudio Validation Gateの走査対象外」)が`a2/narration`へseedをコピーしており、runner assembleがどの経路でこのseedを読むかは本監査では追跡していない(timeline.jsonのWelcome 2.28/Preview intro 1.68/KP intro 2.0/FS intro 1.83秒がseed wav長と一致=seed使用と整合、未確認)。`TR`の`shared_narration`は両levelとも`{}`(`dict_keys([])`)。CHECKLIST_05 #3も同限界を自認。
- M3 Style Gate: `er019_family_x_style_profile_01.py:482 m3_assembly_gate`(runner `64d3ec975:er019_family_x_audio_production_runner_01.py:1542`呼出し、結果は`audit/style_profile_gate.json`に保存)。結果: Std=PASS(checked: full_story_part1/2/3, preview, comment_1〜4)、Adv=PASS(checked: full_story_part1/2/3, kp1〜5_explanation, preview)、blocked 0、human_approved 0。**Gate対象roleはoverride済みrole(FULL_STORY/SUPPORT_JA/KP_EXPLANATION_EN/PREVIEW)のみ**(`:463 _gate_targets`)。対象外(未検査): Std/Adv KP英語(K2)・Std KP日本語意味(M2)・In One Line・Topic intro・Japanese title・Adv Comment1〜4・固定phrase。

---

## §4 音声品質・完成状態
### WPM・文末ポーズ・長無音(参考値。Trial値でProductionの合否基準ではない)
出典: `er071_output/m2p0_n01_production_wiring_01/completion_04/measure/speed_pause_04.json`(測定対象=Full Story 3 partのみ、閾値-40dBFS)。CHECKLIST_05 UDR #49と一致。
| level | WPM(全体) | 語数/総秒 | 文末ポーズ平均/最大(ms) | 800ms以上の無音 | 参考値との関係 |
|---|---|---|---|---|---|
| Std(N01+6%減速後) | 157.7 | 412/156.78 | 629/1030 | 5 | WPM参考157±6内。ポーズ平均参考≦498ms外、長無音参考≦1外 |
| Adv(N01、減速なし) | 178.2 | 462/155.58 | 572/790 | 0 | WPM参考167±6外。ポーズ平均参考≦593ms内、長無音内 |
Part別: Std P1 146.3/P2 165.2/P3 159.7、Adv P1 159.5/P2 186.5/P3 187.2。`er057_output/coffee_final_listening_tone_trial_01/wpm_measurement_01/WPM_MEASUREMENT_01.md`はTrial F5版Adv(全体208.6WPM)の測定で、final_03とは別音声(final_03のNo.1値ではない)。CURRENT_SPECはStd英語ナレーション約135WPMを「目安」(hard constraintではない)としており、Production側に自動化された速度/ポーズ合否基準は無い(`production_criteria_note`)。
- 未測定: Full Story以外(Comment・KP・In One Line・Preview)のWPM/ポーズ。Std 6%減速後の聴感品質は人手未確認(ASRは減速後も実施、上表)。
### ASR検証・不自然な日本語読み
- 全TTS entryで`asr_verified=True`(Std 20/Adv 23 entry)。classification分布: EXACT/NORMALIZED/NUMERIC_EQUIVALENCE/PHONETIC_MATCH(Std comment_4)/HIGH_SIMILARITY_SAFE(Adv Full Story P3)。Std Full Story P2のみ減速後primary 2回UNCERTAIN→azure secondary採用。再試行(TRUE_CONTENT_MISMATCH→再生成成功)はStd comment_1、Adv comment_2・Full Story P1・kp4 english・kp4 phrase_repeat。
- 日本語読み: Std KP日本語意味5件はASRでEXACT×4/NORMALIZED×1(テキスト一致のみ)。聴感上の不自然さ(アクセント・間)は人手で聴取していないため**未確認**。
### 再利用音声のValidation継承
- `validation_inheritance.label=REUSED_VALIDATED`: Std 9(topic_intro, preview, comment_1〜4, full_story_part1/3, in_one_line)、Adv 20(topic_intro, full_story_part1〜3, in_one_line, KP english×5/explanation×5/phrase_repeat×5)。evidence種別: Std=`entry_sha256`、Adv KP=`entry_sha256`(same_out_dir_previous_results)、Adv topic_intro/in_one_line=`witness_sha256_and_trimmed_duration`、Adv Full Story=`backup_entry_wav_mtime_before_overwrite_and_trimmed_duration`(mtime+長さ=sha非依存)。source_style_version=`v5_j2_e2upbeat_f15_tone_refresh_fallback_style_retention`(tone-run)または`v3_j3_kp_meaning_and_explanation_guard`。現在のresults style_version=`v3_j3_kp_meaning_and_explanation_guard`(`b1b/validation_state_rebuilt_01.json`の`current_style_version_in_results`と`source_style_version`が異なるentryあり)。
- fresh entryでentryに`sha256`が無い: Adv preview/comment_1〜4(wavは実在、file sha: preview `0370f184cc46`、comment_1 `13219796ea49`、c2 `b864c11d37f2`、c3 `f32c2cc5ff4b`、c4 `5ba798ed8c77`)。他の全entryは`sha256`==実ファイルsha(Std 21/21、Adv 20/20 MATCH)。
### Audio Validation Gate結果と完成状態
- Std/Adv ともassemble成功: `a2/run_summary_assemble.json` status OK、duration 314.865、peak 0.91547、clipping False、headroom valve非発動。`b1b/run_summary_assemble.json` 315.43、peak 0.9304。stdout: `[M2-FALLBACK] 発生なし`、累計費用Std JPY34.45/Adv JPY30.01。
- 完成MP3と試聴ページ(`user_test/coffee_m2p0_n01_final_03/`)の一致: `Coffee_Standard_final_03.mp3` 5,038,892B・**314.865秒**(assembled wav 314.865と一致)、`Coffee_Advanced_final_03.mp3` 5,047,724B・**315.430秒**(assembled wav 315.4303と一致)。分割mp3: std_00〜24(25本)/adv_00〜23(24本)=timeline.jsonのpart数(25/24)と一致、index.html参照51件(CHECKLIST_05 Dangling Reference: Playwright 51/51再生OK)。ページ表示のStd Full Story本文/KP gloss/TTS読みは`parts.json`/`keywords_canonicalized.json`と一致(目視確認)。ページ上の「通し全編315秒」は両levelに同表記(Std 314.865/Adv 315.43の丸め)。
- ページが**表示しない**情報: Comment/Preview/In One Line/英英解説の本文、使用Style、再利用由来。ユーザーが試聴ページ上で上記の欠落・差異に気付ける情報は無い(観測)。
- 「最新仕様の反映漏れによる品質リスク」(観測としての列挙。判定は01A): K2/M2未反映(§5-A)、In One Line旧1文(§5-B)、gloss再整合はlegacy(§2)、Adv Commentは非E2_UPBEAT(§5-C)、A5/B5固定phraseのGate外、Std Full Story P2はsecondary ASR採用。

---

## §5 観測から見える「未反映・部分反映・証拠不足」候補一覧(仕様判定は01A/委任_02/Fableに委ねる)
| ID | 区分 | 観測(期待と違う点) | 根拠(ファイル:位置) |
|---|---|---|---|
| A | **未反映** | KP英語がK2(332字)でなくProduction既定MINIMAL(1076字)。KP英語: hash不一致12 entry(Std 4+Adv 8)+記録なし3 entry(Std kp1英語、Adv kp2英語/繰返し) | `TR`各`key_phrases[n].english.style_prefix` sha 2b0c7505…、K2 sha 9d905cfe…、`style_profile.py:16-17`、OPEN-313 |
| A' | **未反映** | Std KP日本語意味がM2(67字)でなくFAMILY_X_ROLE_STYLE_JA(65字、ae68e3e6…)×5 | `a2/TR` `key_phrases[n].japanese_meaning.style_prefix` |
| B | **未反映** | In One Lineが旧1文15語(両level)。Trial v3は2文(Std 31/Adv 40語)。新2文方針は未仕様化(OPEN-299) | `parts.json in_one_line`、`IN_ONE_LINE_REWRITE_01.md` |
| C | 部分/要判断 | Adv Comment1〜4=E0(`calm, conversational`)。Trial v3は「既存承認E2_UPBEAT」、tone-runは`warm, upbeat…`(sha 37c52d6e…、main SSOT承認記載なし) | `E0_RECONCILIATION_04.md`、`B_SEGMENT_PROVENANCE_01.csv` |
| D | 部分反映 | gloss再整合は旧legacy(Std rank4のみ)。corrected工程ではない。Advは日本語gloss未使用 | §2証拠行1〜5 |
| E | 証拠不足 | Welcome=A5・Preview intro=B5はTrial wav seed。生成時Prompt hashは`RUN`内に記録なし、Audio Gate走査対象外 | `seed_provenance_04/03`、assemble `:548/:552` |
| F | 証拠不足 | 固定Master phrase(KP intro/FS intro/num)はmanifestのsha一致のみ。Style本文のhash照合不可 | manifest.json:9408/9435 |
| G | 証拠不足 | Adv preview/comment_1〜4のentryに`sha256`/`validation_inheritance`が無い(wav実在) | `b1b/TR` |
| H | 弱い継承 | Adv Full Story P1〜3のREUSED_VALIDATEDがmtime+長さ(`same_out_dir_clobbered_by_only_segments_rerun`)根拠 | `b1b/TR` `validation_inheritance.evidence` |
| I | 観測 | Std KP構成は英語KP→日本語意味の2要素(ユーザー記載「→英語KP」の繰返しがStd resultsに無い)。Advは3要素 | `a2/TR`、`b1b/TR` |
| J | 観測 | Std Full Story P2は減速後primary ASR 2回UNCERTAIN、azure secondary cascadeでNORMALIZED_MATCH採用 | `a2/TR full_story_part2.post_slowdown_cascade` |
| K | 観測 | Std Preview/Comment・Topic intro・In One Lineは他run(v5_ms_01/tone-run)からのREUSED。現runで再生成されていない | `validation_inheritance.source_ref` |
| L | 観測 | rank2「raw bean」`candidate_mismatch_suspected=true`(source_span「raw-bean」、canon_source「raw-bean prices take at least」) | `a2/keywords_canonicalized.json` rank2 |
| M | 観測 | raw_usage_log(100行)に`tag`/gloss再整合/In One Line生成の識別が無い(stage=scaffold/tts、segment=None) | `RUN/raw_usage_log.jsonl` |
| N | 観測 | segment_planの`estimated_seconds`(In One Line Std 11.7/Adv 6.0)と実測(6.225/5.28)に差(planの根拠未確認) | `segment_plan.json` |
| O | 観測 | ページは本文/Style/由来を表示しない(Comment・IOL・英英解説・使用Style不可視) | `index.html` |

## §6 再生成が必要になった場合の最小範囲案(segment単位、全再生成しない。実装・実行は本委任範囲外)
- A(K2適用): Std KP英語×5(kp1〜5_en)+Adv KP英語×5・繰返し×5(`kp?_en.wav`は繰返しと同ファイル共有: Adv kp1〜5_en 5ファイル)。他segment・Full Storyは不変。assemble再実行のみ。
- A'(M2適用): Std `meaning_1〜5.wav` 5 segmentのみ。KPテキスト・gloss(rank4再整合含む)は不変。
- B(In One Line 2文): 原稿再生成(LLM)+Std/Adv `in_one_line` 各1 segment(Stdは6%減速)。Comment4接続の再確認を伴う可能性(Std C4は「最後に」を含む)。他不変。
- C(Adv Comment E2_UPBEAT等へ変更が必要と判定された場合のみ): Adv `comment_1〜4` 4 segment。
- D(corrected gloss再整合適用): Std rank4(`based on interviews`)のみ再判定。gloss変化があれば`meaning_4.wav` 1 segment。他rankはtarget外で変化なし(legacy/correctedとも再整合対象はrank4のみ。ただし再整合結果の変動は未確認)。
- E(A5/B5をProduction経由に統一する場合): Welcome/Preview intro 各level2 segment(固定phrase 4 wav)。Audio Gate走査対象への追加は別問題。
- いずれも`only_segments`系の既存機構が前提。全Full Story・Preview・他Commentは再生成不要(hash一致済み)。実施前にAssembleのseed/継承再計算が必要。

## §7 確認できなかった事項(推定/事実)
- 事実として未確認: (1)日本語読み・アクセント・間の聴感(人手聴取なし)。(2)A5/B5/shell固定phraseの生成時Prompt全文(RUN内記録なし、Trial `er057_tone_trial_tts_gen_01.py` SPECSの文字列hashのみ照合)。(3)Adv Preview/Comment1〜4・Std japanese_title・KP日本語意味の`validation_inheritance`は無し(freshのため不要か欠落かは判定せず)。(4)In One Line原稿LLMのPrompt本文/hash(RUNに専用記録なし)。(5)Adv `in_one_line`(wav `897ca8bf…`)のrun_e_tone_01側の生成時刻・正確な由来。(6)Std/Adv KP難易度・意味整合の人手判定。(7)Std KPの英語繰返し音声の有無(timeline上KP単位でしか分割されない)。(8)`er021_output/.../telemetry.jsonl`にcoffee_prices該当行は0件(grep count=0)でASR semantic equivalence telemetryとの突合は不可。
- 推定: Std KP1英語(master cache hit)のStyleは、同cacheキー`key_phrase_english_component v2_margin030`から他KPと同じMINIMAL Prompt(K2でない)と推定(entryにstyle_prefix無し)。Adv kp2 english/phrase_repeatも同様。
- 環境: `ffprobe`無し→音声長は`soundfile`(libsndfile)で測定(mp3対応、assembled wavの秒数と一致を確認)。
