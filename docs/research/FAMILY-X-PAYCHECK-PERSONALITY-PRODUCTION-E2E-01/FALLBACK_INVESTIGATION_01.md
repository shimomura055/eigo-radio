# FALLBACK_INVESTIGATION_01 (FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_03、2026-10-21、API 0・JPY0)

調査のみ。TTS/ASR/LLM呼出0、wav/Lock/state/Production code変更0、`record_human_approval`未実行。fallback take採用は保留。
ユーザー原文=docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_FALLBACK-INVESTIGATION_USER.md。
最終分類(A/B/C)はFable。本書の分類案は「判断候補」。

## 0. 先頭4点
1. 実際のStyle/モデル: モデル=`gemini-3.8-flash-lite-tts`(Voice=Aoede、backend=speech_metadata_flash_lite、同期STANDARD実行)。Style=`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`="natural, clear, conversational"(30字、sha256 `dba23e664f387c6641f9dd003cf4571f78af87613c68536ddbb5f1e52cad964b`、本文からのsha検算一致)。承認Style(PD06 177字 sha `3a680861…`)は落ちている。N01(`d1956c91…`)ではない(後述: 2026-10-16以降のFamily X Full Story既定はN01でなくPD06)。
2. 承認: (a)fallback段の存在と「標準2回+minimal fallback1回=合計3回」=2026-09-04ユーザー正式決定(CURRENT_SPEC.md:1828)。(b)fallback時のEN短文style=FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]の実配線=2026-09-28のユーザー確定仕様D(DECISION_LOG.md:11285、要旨のみ保存・原文未保存)と、同日のユーザー承認原文「fallback短文style残り2経路の配線…既存の FAMILY_X_ROLE_STYLE_EN_FALLBACK[0] を流用してよいです。新しいstyle文言は作らないこと」(docs/pm/delegation_log/2026-09-28_TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02_05.md:23)。(c)「fallback使用=M3 Gateで人間承認必須(BLOCK)」は開発側設計(Fable+Opus条件A、docs/pm/design/2026-10-12_COFFEE-P8-PRODUCTION-WIRING-DESIGN-02.md:38-40、DECISION_LOG.md:20619)で、ユーザーが文言承認した記録は無い(REGISTER #5はUDR未回答)。
3. 候補になった経緯: 標準PD06がattempt1/2とも統一judgeでNG_BOTH(一次OpenAI=TRUE_CONTENT_MISMATCH[use→used等]かつ二次Azure=TRUE_CONTENT_MISMATCH)。承認済み3回構成の最終slot(minimal fallback)が発火し、一次NORMALIZED_MATCH+Azure強制照合force_secondary_agreedで合格、6%減速後再検証も合格したため「内容検証済みsegment」になった。M3 Style Gateだけが「承認Styleで生成されていない」としてBLOCK。
4. 有効性(判断候補): 内容検証(ASR 2系統+減速後再検証+反復QA)は全合格=内容面は既存Gateを満たす。一方Style面は承認profile(PD06)で生成されておらず、同記事part1/part3と声の調子が異なる可能性がある(未試聴・未確定)。「M3 BLOCKをhuman approvalで通す」経路は実装上の既存正規経路(record_human_approval)だが、「ユーザーがfallback takeのStyle逸脱を人間承認で採用してよい」と明示承認した記録は無い。ユーザー直近の先例(2026-10-13、Coffee Std Part2の旧Fallback音声)は「承認Styleで再生成せよ」だった。

## 1. S1 承認履歴・仕様整合

### 1-1 現行Family X Full StyleはN01ではなくPD06
- N01(sha `d1956c91…`、202字)=2026-10-13ユーザー正式決定(CURRENT_SPEC.md:2756)。「fallback takeはN01ではない」「N01は判定緩和を含まない(ASR判定・速度/ポーズ基準・retry/fallback/STOP条件は無変更)」(同:2756)。
- 2026-10-16ユーザー最終判断でFamily XのFull StoryはPD06に置換(CURRENT_SPEC.md:1249「Family XではN01→PD06に置換、Family ZはN01維持」、:1216)。新規run既定profile=fx_20261017(er019_family_x_style_profile_01.py:184-188、FULL_STORY=PD06 sha 3a680861…、:111)。本runの`audit/style_profile.json`もprofile fx_20261017/FULL_STORY sha 3a680861…。
- よってユーザー原文§1の「N01がFull Story通常Style」はFamily Xでは旧記述。fallbackがPD06でもN01でもないことは同じ。「fallback takeはN01ではない」(CURRENT_SPEC.md:2756)はtest(`er019_family_x_style_profile_01_n01_test_01.py:58` N-8、`er019_family_x_variable_role_style_wiring_01_test_01.py:203-204` FALLBACK定数不変)で現在も「FALLBACKにN01を混入しない」不変条件として有効。
- 用語整理: 原文の「N01採用時」は、現行Family Xでは「PD06採用時(2026-10-16)」に対応する。PD06採用時にfallback維持を明示した判断記録は無い(ユーザー原文docs/pm/delegation_log/2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_USER.md:73,94,197は「retry／fallback／regeneration／resumeも整合」を受入条件にしているのみ)。

### 1-2 (a) fallback経路を承認した判断
| 内容 | 日付 | 出典 | 適用範囲 |
|---|---|---|---|
| 標準2回+Minimal fallback 1回=合計3回をProduction正式仕様 | 2026-09-04ユーザー正式決定(ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-25/FINAL-26) | CURRENT_SPEC.md:1828、DECISION_LOG.md:87-88 | EN本文`generate_english_segment_with_fallback`(Std full_story_part1/2等)、JA |
| Flash-Lite(speech_metadata)をFamily Xへ段階導入、6-role style | 2026-09-27ユーザー正式決定 | DECISION_LOG.md:10262-10285 | Family X |
| fallback時の短文style配線(FAMILY_X_ROLE_STYLE_EN_FALLBACKを実配線、JA minimalは既存テキスト流用) | 2026-09-28「ユーザー確定仕様」(逐語要旨。項目名は「D 既存不足の是正(ユーザー判断不要)」) | docs/pm/delegation_log/2026-09-28_TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02_01.md:10、DECISION_LOG.md:11285,11690-11695、CURRENT_SPEC.md:1791-1809 | Flash-Lite backend時のEN fallback(repro01/voice01/point_headings 3経路) |
| 上記の追加経路+shell流用 | 2026-09-28ユーザー承認原文「1. Flash-Lite修正 承認…fallback短文style残り2経路の配線…既存の FAMILY_X_ROLE_STYLE_EN_FALLBACK[0] を流用してよいです。新しいstyle文言は作らないこと」 | docs/pm/delegation_log/2026-09-28_TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02_05.md:23 | 同上 |
- 注意: `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`="natural, clear, conversational"とTrial attempt2の対応は、定義側コメントが「実測に基づくものではなくPhase 1時点の技術判断…Phase 2の結果を見てOpus L2・Fableが妥当性を再確認」と自認(er033_tts_flash_lite_family_x_styles_01.py:51-61)。ユーザーが文言そのものを個別に選んだ記録ではなく、「既存定数流用・新文言を作らない」を承認した形。2026-09-28のD項目はユーザー原文が保存されておらず要旨のみ(記録上の不足)。

### 1-3 (b) N01(PD06)採用時のfallback維持判断
- 「retry/fallback/STOP条件は無変更」(CURRENT_SPEC.md:2756)はN01が判定緩和を含まないという記述で、fallback takeの扱いを決めた記述ではない。fallback takeをM3 Gateで人間承認必須とする判断主体は開発側設計(DESIGN-02 :38-40、DECISION_LOG.md:20619「(M3)…満たさなければrecord_human_approvalが無い限りBLOCK」)。ユーザー承認原文は見つからない。
- 関連REGISTER: #5「P8のfallback/Local Rewrite扱い・PRODUCTION_WIRED判定」=UDR(未回答)(docs/pm/USER_DECISION_REGISTER_01.md:22)。#47「fallback takeの人間承認か再生成か」は2026-10-13ユーザー指示で「開発側責任として是正」へ区分変更(同:66)。

### 1-4 (c) fallback takeの正式解決手順(SSOT上の定義)
- (i)人間承認(`record_human_approval`、`er003_v1_n3_01_assemble.py:96-117`)で採用: 実装上の正規経路。M3 Gate(`er019_family_x_style_profile_01.py:628-725`)が`_approved()`でcanonical text sha一致の承認を要求。Audio Validation Gate側の人間承認はCURRENT_SPEC.md:2095(ASR_VALIDATION_UNCERTAIN/HUMAN_REVIEW_LOCKED対象)に定義済み。ただしM3 Style Gateの「fallback使用take」をこの経路で採用してよいとSSOTが明記した行は未発見(設計書DESIGN-02のみ)。
- (ii)承認Styleで再生成: ユーザー先例あり。2026-10-13「Standard Part 2が、正式採用済みN01ではない旧Fallback音声のまま残っている…承認済みN01で再生成し、正式Validationを実施すること」(docs/pm/delegation_log/2026-10-13_FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01_01.md:44,135-146。『旧Fallback音声残存』を開発側の既存不具合・未完了作業と位置付け)。Coffee Part2はN01標準経路で再生成して完成(CURRENT_SPEC.md:2762)。
- (iii)未定義: 再生成しても再び標準2回NG→fallbackとなる場合の扱い。TOTAL3回上限(CURRENT_SPEC.md:1828「4回目以降は絶対にTTS生成しない」)と、segment単位再生成時にattempt予算が新規になるかのSSOT明文は確認できず(E2E_PLAN_01.md §5-6は新audio run=新規予算と整理)。
- 過去の人間承認先例: Toteme full_story_part2(2026-09-17、ユーザー試聴「現在の音声でOK、最終版として採用」、DECISION_LOG.md:8215)、Space Weapons B1(標準route wavを採用し旧fallback wavは`..._fallback_rejected.wav`へ退避、DECISION_LOG.md:7925)。いずれもprofile(M3 Gate)導入前。MEY comment_2(2026-10-21、REGISTER #128): 標準・fallbackとも不合格のReview Lockをユーザー試聴承認で解決(DECISION_LOG.md:21863、results上comment_2 status=HUMAN_REVIEW_LOCKED、fallback_used=None)。本件(fallbackが「合格」しStyle逸脱のみで止まった)とはゲートが異なる(Audio Validation/Review Lock=内容面、M3=Style provenance)。Style逸脱takeそのものを人間承認で通した確定先例は、本調査では確認できず(未確認)。

### 1-5 (d) Dangling Reference・旧経路
- 現行Family Xの実配線: Std本文=`er003_v1_crosslevel_audio_02_common.py::generate_english_segment_with_fallback`(:81-)→`_run_a2_minimal_fallback_attempt`→`er003_v1_repro01_main_generate.py:578`(FALLBACK[0])。他EN fallbackも`er003_v1_sing01_voice01_generate.py:189-194`、`er003_v1_sing01_point_headings_aoede.py:99`で同定数。Flash-Lite backend時のみで、既定structured_separationのMINIMAL_INSTRUCTION_PREFIXはlegacy用。Family Xのrunnerは既定=speech_metadata_flash_lite、legacyは`--allow-legacy-backend`必須(er019_family_x_audio_production_runner_01.py:2270-2282)。「長いlegacy instruction」への到達はFamily X既定では無い(Dangling無し)。
- JA側minimalはFAMILY-X-02 D-1方針で意図的に旧テキスト流用のまま(`er003_v1_n3_01_tts_generate.py:612-625`)。M3は`JA_FALLBACK_USED_OR_UNKNOWN`でBLOCK(style_profile_01.py:692-693)。今回はEN。
- 追跡定数`FAMILY_X_ROLE_STYLE_EN["FULL_STORY"]`(旧「calm, steady news narration…」)はprofile有効時にoverrideされFull Story生成には使われない。
- 記録上の欠陥(実害なし): fallback attemptの`attempts/full_story_part2_attempt3_minimalfallback.json`の`"model"`が`gemini-2.5-pro-preview-tts`(`p9a.ENGLISH_MODEL_NAME`固定値、`er003_v1_crosslevel_audio_02_common.py:233`)と記載されるが、実際は`gemini-3.8-flash-lite-tts`(結果dict `model`=`resolve_actual_model_name`、raw_usage_log.jsonl:41 model_id)。標準attemptのjsonは正しい(model=flash-lite、tts_backend記載)。fallback jsonには`tts_backend`キーも無い。修正案(報告のみ・実装はFable判断後): :233を`flw.resolve_actual_model_name(p9a.ENGLISH_MODEL_NAME, tts_backend)`に、`"tts_backend": tts_backend`を追加。挙動不変。無課金testの計画: sidecar dictのmodel値をassert(flash-lite backend時=gemini-3.8-flash-lite-tts、既定backend時=従来値と同一)。承認範囲内の記録不具合(11-8)。
- 補足: raw_usage_logのinput_tokens(attempt1/2/3とも189)はstyleがspeech_metadata経由でtoken計上されない(または差が小さい)ため、API側ログだけでfallback styleの送信を独立証明できない。送信styleの証拠は結果record(style_prefix sha)とコード経路(repro01.py:578→resolve_tts_call_and_prompt)。

## 2. S2 今回run証拠(`er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_01/a2/`、audit/tts_generation_results.json segments.full_story_part2)
### 2-1 attempt表
| 項目 | attempt1(標準) | attempt2(標準) | attempt3(minimal fallback) |
|---|---|---|---|
| 経路 | standard_attempts_log[0] | standard_attempts_log[1] | fallback_attempts_log[0](instruction_label=FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]) |
| モデル/Voice | gemini-3.8-flash-lite-tts / Aoede | 同 | 結果top-level model=gemini-3.8-flash-lite-tts / Aoede(raw_usage_log.jsonl:41)。sidecar jsonのmodel表記は誤記(1-5) |
| backend/実行方式 | speech_metadata_flash_lite / STANDARD(同期) | 同 | 同 |
| Style | PD06 177字「Speak directly to one listener with warmth and a smile in your voice; calm, steady and reassuring, like a favorite morning radio host, while keeping the news clear and credible.」sha `3a680861e4d9d1bc46ddba4dc1fc91f26c68f9f9c5e5e450a85fcba7fda43c2d`=承認profileのexpected_baseと一致(N01 d1956c91…ではない) | 同 | 「natural, clear, conversational」30字 sha `dba23e664f387c6641f9dd003cf4571f78af87613c68536ddbb5f1e52cad964b`(PD06と不一致) |
| 生成時刻(JST) | 12:56:51 | 12:57:28 | 13:08:03(直前に10分cool-down 12:57:55→13:07:55、cooldown_events) |
| 音声duration | 55.44s | 52.43s | 48.68s(減速前) |
| wav | attempts/full_story_part2_attempt1_customa3c4625e.wav(sha 84410a2e…、存在) | attempt2_customa3c4625e.wav(sha 1fba4cf7…、存在) | attempts/full_story_part2_attempt3_minimalfallback.wav(sha cf412737…、存在) |
| 一次ASR(gpt-4o-mini-transcribe) | TRUE_CONTENT_MISMATCH。「you used to look」「Then you'd turn」「serious?」 | TRUE_CONTENT_MISMATCH。「you used to look」「serious?」「Wait, before」 | NORMALIZED_MATCH。「you use to look」「Then you turn」「serious.」 |
| 二次ASR(Azure en-US) | TRUE_CONTENT_MISMATCH(overtime、neighbors[所有格'欠落]、you'd turn、One Direction、文区切り欠落) | TRUE_CONTENT_MISMATCH(earning more→Ernie Moore、neighbors) | NORMALIZED_MATCH(over time→overtime、neighbor's→neighbors は空白除去後一致扱い) |
| 統一judge | NG_BOTH / secondary_not_accepted(p3_primary_ng) | NG_BOTH / secondary_not_accepted | PASS / force_secondary_agreed(slot3=最終slot) |
| value/negation guard | EQUAL / 否定差なし | 同 | 同 |
| 採否 | 不合格 | 不合格 | 採用候補(一次+二次PASS)。repetition QA checked・flagged=false(意図的反復2件intentional=true) |
- 減速: 目標6%(実測5.974%)で48.68s→51.588s(`slowdown_info`)。再検証=`post_slowdown_final_classification`=NORMALIZED_MATCH(一次OpenAIのみ1回、raw_usage_log:44)。
- 通算TTS=3(`tts_generations_used`=3、上限3内)。再起動なし。

### 2-2 fallbackが発動した正確な条件(コード+実ログ)
- コード: `generate_english_segment_with_fallback`(`er003_v1_crosslevel_audio_02_common.py:81-`)は`standard = generate_narration_snippet_verified_strict(..., max_attempts=standard_attempts(=2))`を実行。standardがstatus OKでも`HUMAN_REVIEW_LOCKED`でもない場合、`fallback_budget = max(0, max_attempts(3) - len(standard.attempts_log))`=1回、`_run_a2_minimal_fallback_attempt`を実行(=2026-09-04仕様)。
- 実ログ: standard_attempts_log 2件ともasr_judgement.state=NG_BOTH → fallback 1回発火 → PASS(force_secondary_agreed)→ `fallback_used=true`。
- M3 Gate: `m3_assembly_gate`(`er019_family_x_style_profile_01.py:658-725`)がFULL_STORY Stdで`fallback_used is not False`→`STD_FALLBACK_USED_OR_UNKNOWN`、M4 Final Style判定→`FINAL_STYLE_SHA_MISMATCH_NO_HINT`(`audit/style_profile_gate.json`: status=BLOCK、human_approved=[])。Audio Validation Gate(内容面)ではなくStyle provenance Gate。

### 2-3 「Fallbackで合格した検査」と「人間承認が必要になった理由」
- 合格: 一次ASR NORMALIZED_MATCH、二次Azure NORMALIZED_MATCH、value/negation guard、長さ、反復QA(flagged=false)、減速後再検証NORMALIZED_MATCH。承認済みASR Gate(判定緩和なし)そのもの。
- 人間承認が要る理由: 生成Styleが承認profile(PD06)でない(M3 Gate設計: roleのStyleを落とすfallback takeは黙って採用しない、DESIGN-02:38-40)。承認はテキストsha紐づき(wav非紐づき、E2E_PLAN_01.md §5-1)。Review Lock(HR queue)は発生しておらず(review_lock_state 0件)、MEYのような「内容不合格のHuman Review」ではない。

## 3. S3 発音不良かASR誤認識か(既存証拠のみ。音声の良否は未試聴=未確定)
canonical(parts.json part2)と各ASR転写を、リポジトリの判定関数(`er006_preprod_hardening_01_validation.classify_asr_match(segment_id="full_story_part2")`、純ローカル・API 0)で再計算して差分語を取った(結果はrun記録と一致: attempt1/2一次=TRUE_CONTENT_MISMATCH、fallback一次=NORMALIZED_MATCH)。
| 転写 | 差分語(正規化後) | 分類 |
|---|---|---|
| a1 一次(OpenAI) | use→used、+d(you'd turn) | 活用/縮約(use to↔used to、you turn↔you'd turn)。句読点差(serious? / Wait before)は正規化で無視 |
| a1 二次(Azure) | over time→overtime、neighbor s→neighbors、+d(you'd turn) | 複合語/所有格表記+縮約。`you'd turn`は一次と二重一致(2系統が同じ箇所を聞いている) |
| a2 一次(OpenAI) | use→used のみ | 活用。他は句読点 |
| a2 二次(Azure) | neighbor s→neighbors、earning more→ernie moore | 所有格表記+固有名詞化誤認識(一次OpenAIは同箇所を正しく転写) |
| fb 一次 | 差分0 | 句読点のみ |
| fb 二次 | over time→overtime、neighbor s→neighbors | 空白除去後一致(複合語分かち書き) |
- 統一judgeの根拠(引用): 一次reason=「固有名詞以外の内容語に差がある(内容誤りの可能性): [{'type': 'replace', 'canonical': 'use', 'asr': 'used', …}]」。state=NG_BOTH、reason_code=`secondary_not_accepted`(一次NGなら二次が受理しない限りNG)。
- 解釈(断定しない):
  - attempt2: 一次の差は`use`→`used`の1点のみで、同箇所をAzureは「use」と転写(canonicalと一致)。逆にAzureは`earning more`→`Ernie Moore`と誤認識し、同箇所を一次は正しく転写。2系統の誤りが重ならない=ASR側の揺れ/誤認識が主因の可能性が高い。ただし実際の発音は未試聴で確定不可。
  - attempt1: `you'd turn`を2系統が一致して転写 → 実際に縮約形(余計な'd)が読まれた可能性が相対的に高い。`use/used`は2系統が不一致。
  - 統一judgeは「一次NGなら二次が受理しない限りNG」という厳格運用で、2系統の誤りが非重複でも落ちる(既存仕様どおりの動作。仕様変更は提案しない。判断候補ではなく観測)。
- attempt1/2のwavは存在し、HR試聴ページに「承認Style attempt1/2」として掲載済み(user_test/paycheck_personality_e2e_01/hr_full_story_part2/audio/part2_style_attempt1.mp3、part2_style_attempt2.mp3。E2E_PLAN_01.md:50-51)。

## 4. S4 分類材料(最終はFable。以下は判断候補)
- A(承認済み仕様どおり)に該当しうる事実: 標準2+minimal fallback1=計3回(2026-09-04ユーザー決定); FALLBACK[0]流用はユーザーが2026-09-28に明示承認(02_05.md:23); M3 Gateは設計どおりBLOCKし迂回なし; 内容検証Gateは全合格; STOP/再起動なし。
- B(仕様・記録の不整合)に該当しうる事実: (1)M3 Gateの「fallback使用=人間承認で通す」にユーザー承認原文が無い(DESIGN-02は開発側設計、REGISTER #5未回答); (2)2026-09-28のD項目は要旨のみで原文未保存、かつ「ユーザー判断不要」とラベル; (3)Family X Full StyleがN01→PD06へ置換後、CURRENT_SPEC.md:2756にN01記述が残り「fallback takeはN01ではない」が現行(PD06)状況へ読み替えられていない; (4)fallback sidecar jsonのmodel誤記; (5)PD06 PRODUCTION_WIRED判定時に「Std fallback分岐はtest evidenceのみ」(CURRENT_SPEC.md:1258付近(c))=今回が初のruntime発火; (6)2026-10-13ユーザー先例(旧Fallback音声は承認Styleで再生成)と「人間承認で採用」という代替経路の優先関係が未定義。
- C(未承認・不正経路)に該当しうる事実: 確認できず。FALLBACK[0]はユーザー承認済み定数で、新Style文言・Production Prompt変更・未承認flag・Gate迂回の痕跡は無い。fallback takeは承認前に完成版へ入っていない(M3 BLOCK)。
- 分類案(判断候補): B寄り(動作はA相当、記録・優先関係に不足)。C該当なし。
- 判断候補の整理(27-3): 「fallback takeを人間承認で採用するか、承認Styleで再生成するか」は、2026-10-13ユーザー指示(10-13_COMPLETION-01_01.md:135-146)に照らすと再生成が既判断寄り(A既判断)。ただし再生成でも再び標準2回NG→fallbackとなる確率は不明(E2E_PLAN_01.md §5-6)。統一judgeのNG_BOTH運用自体の変更は新仕様候補でありここでは提案のみ・実装しない。

## 5. 実装不具合の有無
- 承認範囲内の明確な不具合: fallback sidecar `model`/`tts_backend`記録のみ(1-5、挙動影響なし)。修正は報告止まり(実装はFable判断後)。
- Gate/retry/fallback本体に不具合は確認せず(cascadeは仕様どおり)。
