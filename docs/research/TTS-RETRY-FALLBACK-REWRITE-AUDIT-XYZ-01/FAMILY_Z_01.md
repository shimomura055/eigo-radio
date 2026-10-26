# FAMILY_Z_01 — Family Z の TTS Retry・Fallback・Local Rewrite・Human Review 仕様棚卸し

管理ID: TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01Z(2026-10-26)。性質=read-only調査(API 0・JPY0・コード/SSOT/run dir 編集なし)。到達上限Status=調査完了(AUDITED)。
ユーザー指示原文=`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_USER.md`。共通核(`er003_v1_n3_01_tts_generate.py`/`er020_*`/`er011_*`)の正本記述はX担当。本書はZがそれらを「どの関数・どの引数で呼び、結果としてLR/Fallbackが有効か無効か」を書く。
行番号は2026-10-26時点のworktree(`git log -1`=764901e3a)。表のセルは事実(ファイル:行・文書)のみ。技術的見解は §11「所見(事実ではない)」に分離した。
構造化データ=`family_z_01.json`(同内容、14行+星取表②)。

## 0. 結論(先に)

1. **Zの音声部位のうちLocal Rewrite(LR)が有効なのは英語のナレーション系3部位だけ**: 地の文(narrator。Std/Adv、chunk含む)・Adv Preview英語・Adv Comment英語。有効化は専用引数ではなく `enable_connected_speech_equivalence_layer=cs(spec)=connected_speech_enabled_for(clip_id)` 1本で、Connected Speech層・600秒cooldown・LRが同時にON/OFFされる(`er020_tts_retry_local_rewrite_01.py:188`、呼出元 `er063_family_z_audio_01.py:1004,1015,1037-1042`)。
2. **登場人物のセリフ(dialogue)にはLRが無い**(文脈・感情付きctx方式もlegacy方式も同じ)。dialogueは `er012_b_family_voices_production_01.py:483 generate_voice_body_wide_margin` を呼び、この関数にはLR/cooldown呼出が存在しない(`git log -S local_rewrite -- er012_b_family_voices_production_01.py` は0件)。ctx方式の600秒cooldownは `attempt_hook`(`er122_fz_ctx_policy_01.py:282-338`)が差し込む別実装。
3. **dialogueにLRが無い理由として、ユーザーの明示不採用の記録は見つからなかった。** 設計記録にあるのは Fable判断J-1(`DESIGN_02.md:6,61`)=「Z dialogueにLR未配線の事実+LR新設は新仕様でユーザー承認事項」のみ(Opus `OPUS_REVIEW_01.md:63-70` も同意見)。これはユーザー承認ではない。ユーザー原文は「NG → 既存のLocal Rewrite処理へ」(`FZ…_USER.md:30`)と書いており、前提(dialogueに既存LRがある)と実装が食い違う。分類=**C**(既存OPEN-528 Deferred(1)と重複)。
4. **Zの文脈・感情付きdialogue**: 通常ctx2+Fallback(従来方式)1+LR後0=総3、4回目なし。2回目NG後に固定600秒。runtime evidence(E-1〜E-6、melos Std/Adv、実TTS/実ASR)あり。ただし強制NGは repetition QA gate の上書きで、実ASR NG由来の3回目HR queue追記は未観測。
5. **Z narrator のLRは実走している**: Z run走査でLR採用(`audio_text_deviation`あり)10件(Adv 9・Std 1)、cooldown発生 narrator 9件(a2 6・b1b 3)。LR経由のZ Std **chunk** 実runは未取得(`EVIDENCE_Z_01.md` §5)。
6. **B(承認済み仕様との不一致)1系統**: Z `topic_intro_en`(Std/Adv)が5 roleのTopic introに解決されず、cooldown・LR非適用(`resolve_narrative_role('topic_intro_en')=None` を実測)。Xの `topic_intro` は適用される。設計メモ `IMPLEMENTATION_DESIGN_02.md:34` の「既存C/Xと同じ扱い」はXについて事実と異なる。ユーザー承認の除外記録なし。
7. **C(ユーザー判断事項)**: (i) Z dialogueへのLR(J-1、OPEN-528 Deferred(1)) (ii) M-3(ii)=Advで行会計により従来方式(3回目)に到達せずSTOPする稀ケース(OPEN-528 Deferred(2))。いずれも新規OPEN不要(既存OPEN-528へ追記候補)。

## 1. Z正式Productionで音声化される全部位(clip plan)

出典: `er063_family_z_audio_01.py:555-609 build_level_plan`、`:992-1118 real_generators`、`er026_family_z_fiction_production_runner_01.py:2298-2318 load_level_inputs`(`LEVELS=("b1b","a2")` :1128)。shell(welcome等)・番号音声は `provision_shell_assets`(`er063:1941-1964`)で既存Master資産を **コピー(TTSなし)**。

| レベル | clip_id | 種別(kind) | role_key / Style | 生成関数(real_generators) |
|---|---|---|---|---|
| Std(a2) | `topic_intro_en` | topic_intro | TOPIC_INTRO_EN / X_TOPIC_INTRO(Aoede) | `crosslevel.generate_english_segment_with_fallback`(er063:1044) |
| Std | `japanese_title` | japanese_title | JAPANESE_TITLE / X_J3 | `ja_simple`→`generate_a2_japanese_with_reading_safety`(:1052) |
| Std | `preview` | preview(日本語) | STD_JA_PREVIEW / S3 | 同上(:1057) |
| Std | `comment_1..3` | comment(日本語) | STD_JA_COMMENT / S3 | 同上 |
| Std | `kp{r}_en` | kp_en | KP_EN / K2 | `_kp_en_two_stage`(:1069) |
| Std | `kp{r}_ja` | kp_ja | KP_JA / P8_KP | `generate_a2_japanese_with_reading_safety`(:1108) |
| Std | `full_story_part{n}_c{k}`(narrator、>100語は `_k{j}` chunk) | narrator | NARRATOR_FULL_STORY_STD / PD06 | `generate_a2_segment_with_slowdown`(:1007、6%減速) |
| Std | `full_story_part{n}_c{k}`(dialogue) | dialogue | DIALOGUE_STD / 従来Dialogue Style(ctx方式では ctx style→従来) | `generate_dialogue_ctx`(:908)または `generate_voice_body_wide_margin`(:1019) |
| Adv(b1b) | `topic_intro_en` | topic_intro | X_TOPIC_INTRO(Charon) | `charon_en`→`voice01.generate_charon_english`(:1037,:1044) |
| Adv | `preview` | preview(英語) | ADV_EN_PREVIEW / E1 | 同上(:1057) |
| Adv | `comment_1..3` | comment(英語) | ADV_EN_COMMENT / E2_UPBEAT | 同上 |
| Adv | `kp{r}_en` | kp_en | KP_EN / K2 | `_kp_en_two_stage` |
| Adv | `kp{r}_explanation_en` | kp_expl_en | KP_EXPL_EN / P7 | `x_runner.generate_key_phrase_explanation_en_verified`(:1103) |
| Adv | `full_story_part{n}_c{k}`(narrator、>100語は chunk) | narrator | NARRATOR_FULL_STORY_ADV / PD06 | `news_tail_fix.generate_news_narration_wide_margin`(:1007) |
| Adv | `full_story_part{n}_c{k}`(dialogue) | dialogue | DIALOGUE_ADV / 従来Dialogue Style | `generate_dialogue_ctx` または `generate_voice_body_wide_margin`+外側ループ(atempo 1.06) |

注: Std の KP 日本語意味は `kp_explanations is None` のとき、Adv は英語解説(`kp_explanations` あり)(`er063:589-599`、`er026:2300-2304`)。chunk化は `build_level_plan`(`:600-606`)で narrator のみ(dialogueは対象外)、Std/Adv 両方。narrator と dialogue の clip_id は同じ `full_story_part{n}_c{k}` 形式で、`resolve_narrative_role` は両方を FULL_STORY に解決する(`er020:152-156`)が、生成関数は異なる。

## 2. 星取表①(Z行)

用語: 通常=同一設定の試行、Fallback=設定切替(F-Style/F-Model/F-Voice/F-Prompt/F-Tech)、LR=本文局所書換え後の再TTS。数え方は「通常n+Fallback m+LR後k=総N」。各行のID(`Z-…`)は §3 と `family_z_01.json` の `id` に対応。「cs」=`connected_speech_enabled_for(clip_id)`。

|Family|レベル|音声部位|通常TTS上限|Retry条件|Fallback有無・種類|Rewrite有無|Rewrite発動条件|最終NG時|仕様・実装一致|
|---|---|---|---|---|---|---|---|---|---|
|Z|Standard(a2)|地の文(narrator) story clip[full_story_part{n}_c{k}]・100語超はchunk[_k{j}](`Z-A2-NARR`)|標準2(PD06)+Fallback1=通算3。技術エラーは別枠(各呼出内1回)|統一judge NG(Primary→Secondary)/長さ/disfluency/repetition。減速後再検証NGも通算3の残予算で取り直し|F-Style(3回目=minimal instruction)。直前に600秒|あり(cs=True)|通算3(標準2+Fallback1)不合格後に書換え1回→再TTS1回|LR None→STOPPED→HR Lock→rc=2(HR+STOP)|一致(Std chunk経由のLR等はruntime証拠なし)|
|Z|Standard(a2)|登場人物のセリフ(dialogue) policy=fz_ctx_v1(新規runの既定)(`Z-A2-DIALOGUE-CTX`)|ctx2+従来方式1=通算3(4回目なし)。技術エラー別枠|同上(統一judge)。NG判定はattempt直後|F-Prompt(3回目=ctx→従来Style)。直前に600秒。attempt内F-Tech(minimal)有|なし(未配線)|-(3回NGで即HR Lock)|STOPPED→HR Lock→TERMINAL_NG→rc=2(HR+STOP)|前段一致/LR段=仕様記録なし(C)|
|Z|Standard(a2)|登場人物のセリフ(dialogue) policy=legacy(既存run・ロールバック時)(`Z-A2-DIALOGUE-LEGACY`)|同一従来Styleで通算3|統一judge|F-Techのみ(attempt内minimal)。cooldownなし|なし(未配線)|-|STOPPED→HR Lock→rc=2|仕様記録なし(C)|
|Z|Standard(a2)|Topic intro(topic_intro_en、Aoede)(`Z-A2-TOPIC`)|標準2+Fallback1=通算3|統一judge|F-Style(minimal)。cooldownなし|なし(cs=False:clip_id topic_intro_enが未分類)|-|STOPPED→HR Lock→rc=2|不一致(B)|
|Z|Standard(a2)|日本語タイトル(japanese_title)/Preview(preview)/Comment 1-3(comment_n)(`Z-A2-JA`)|標準2+Fallback1=通算3|日本語統一judge(Primary→Secondary+全文Validator+SCG)|F-Style(minimal)|なし(日本語)|-|STOPPED→HR Lock→rc=2|一致|
|Z|Standard(a2)|Key Phrase英語(kp{r}_en)(`Z-A2-KPEN`)|K2 2+ENGLISH_LOCK 2=通算4(例外)|3-ASR多数決+disfluency|F-Style(K2→ENGLISH_LOCK)|なし(KP非適用)|-|通算4 NG→HR Lock→rc=2|一致|
|Z|Standard(a2)|Key Phrase日本語意味(kp{r}_ja)(`Z-A2-KPJA`)|標準2+Fallback1=通算3|日本語統一judge|F-Style(minimal)|なし(日本語・KP)|-|STOPPED→HR Lock→rc=2|一致|
|Z|Advanced(b1b)|地の文(narrator) story clip・100語超はchunk[_k{j}](`Z-B1B-NARR`)|同一PD06で通算3。技術エラー別枠|統一judge NG|品質NGにFallbackなし(attempt内F-Techのみ)。attempt3直前に600秒|あり(cs=True)|通算3不合格後に書換え1回→再TTS1回(Styleは標準ENGLISH_STYLE_PREFIX)|LR None→STOPPED→HR Lock→rc=2|一致|
|Z|Advanced(b1b)|登場人物のセリフ(dialogue) policy=fz_ctx_v1(新規runの既定)(`Z-B1B-DIALOGUE-CTX`)|ctx2+従来方式1=通算3(減速後NGも数える)|統一judge+減速後(atempo1.06)再検証|F-Prompt(3回目)。直前に600秒。attempt内F-Tech有|なし(未配線)|-|STOPPED→finalize/HR Lock→rc=2。M-3(ii)で従来方式未到達のまま停止する稀ケース有|前段一致/LR段=仕様記録なし(C)|
|Z|Advanced(b1b)|登場人物のセリフ(dialogue) policy=legacy(`Z-B1B-DIALOGUE-LEGACY`)|同一従来Styleで通算3|統一judge+減速後再検証|F-Techのみ|なし(未配線)|-|STOPPED→HR Lock→rc=2|仕様記録なし(C)|
|Z|Advanced(b1b)|Topic intro(topic_intro_en、Charon)(`Z-B1B-TOPIC`)|同一Styleで通算3|統一judge|なし|なし(cs=False)|-|STOPPED→HR Lock→rc=2|不一致(B)|
|Z|Advanced(b1b)|Preview英語(preview、E1)/Comment 1-3英語(comment_n、E2_UPBEAT)(`Z-B1B-PREVCOM`)|同一Styleで通算3|統一judge+disfluency|品質NGにFallbackなし。attempt3直前に600秒|あり(cs=True)|通算3不合格後に書換え1回→再TTS1回(元Style転送)|LR None→STOPPED→HR Lock→rc=2|一致(LR実走証拠なし)|
|Z|Advanced(b1b)|Key Phrase英語(kp{r}_en)(`Z-B1B-KPEN`)|K2 2+ENGLISH_LOCK 2=通算4(例外)|3-ASR多数決+disfluency|F-Style(K2→ENGLISH_LOCK)|なし(KP非適用)|-|通算4 NG→HR Lock→rc=2|一致|
|Z|Advanced(b1b)|Key Phrase英語解説(kp{r}_explanation_en、P7)(`Z-B1B-KPEXPL`)|同一P7で通算3|統一judge+disfluency|なし|なし(5 role外)|-|STOPPED→HR Lock→rc=2|一致(名指し除外記録は未確認)|


注(全行共通の事実): (a) 品質NG判定=統一judge(Primary=OpenAI→NGならSecondary=Azure)。ASR表記違いのみでは再生成しない(PASS/PASS_WITH_WARNING、`er006:908` docstring)。(b) 技術エラー(429/5xx)再試行は各TTS呼出内 `_call_tts_with_retry(max_retry=1)`(`er002_common.py:703`)で品質NG回数とは別枠。(c) 最終NGは `guarded_generate`→`record_outcome`(`er011:357`)→HUMAN_REVIEW_REQUIRED(Lock)。HR queue追記は最終slot(通算上限)NGのときだけ judge が行う(`er006:644,:1294`、`er078_asr_unified_attempt_ctx_01.py:1-14`)。(d) runnerは全clip処理後に status!=OK があれば `FamilyZTtsClipFailedStop`(rc=2、STOP sentinel ファイルは作らない、`er026:2357`)。再実行は承認または `--only-clips`(`er026:2358-2359`)。(e) 累積15回/60 ASRでBUDGET_GUARD(`er011:68-69`)。

## 3. 部位別詳細(星取表①の根拠。ファイル:行)

### Z-A2-NARR — Standard(a2) / 地の文(narrator) story clip[full_story_part{n}_c{k}]・100語超はchunk[_k{j}]

- 生成関数: er063_family_z_audio_01.py:1007 narrator() → er003_v1_n3_01_tts_generate.py:331 generate_a2_segment_with_slowdown → er003_v1_crosslevel_audio_02_common.py:95 generate_english_segment_with_fallback(@guarded_generate('en')) ; 減速=n3:194 apply_a2_slowdown_postprocess
- 呼出し引数: text=_norm_for_tts, expected_substring=first_words(text), style_prefix_override=PD06(style_text_for), disfluency_qa=False, enable_connected_speech_equivalence_layer=cs(spec)=True[clip_idがresolve_narrative_roleでFULL_STORY解決: er020:152-156,:188], enable_repetition_qa=True, tts_backend=TTS_BACKEND。内部=max_attempts=残予算(<=3), standard_attempts=min(2,残), prior_generations, cooldown_total_budget=3, max_slowdown_attempts=3。attempt_hook/LR専用引数なし(cs=TrueがCS層・cooldown・LRを同時に有効化)
- 通常TTS上限: 品質NG: 標準経路2(同一PD06 Style)+Fallback1=通算3(er011_human_review_lock_01.py:80 PRODUCTION_MAX_TTS_ATTEMPTS、:102-104 標準2+minimal1)。外側ループ(減速後NG)は通算3の残予算を共有(n3:376-415)。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠
- Retry条件: 統一judge(er006_secondary_asr_01.py:586 evaluate_attempt_with_cascade/:874 _detail): Primary=OpenAI→NGならSecondary=Azure(force_secondary時はPrimary PASSでもSecondary必須)。発音NG・内容不一致はjudge内分類(TRUE_CONTENT_MISMATCH/entity-like等)でNG、ASR表記違い・音韻同等はPASS/PASS_WITH_WARNING(再生成しない)。長さNG=final_length_ok(er078_asr_unified_judge_01)。さらにdisfluency gate(dq18)・repetition QA gateのAND。無音/発話区間検出失敗/異常長=detect_duration_anomaly(er003_audio_tts_asr_safety.py:189)で当該attemptを技術失敗扱い。加えて減速後再検証NG(n3:121 _post_slowdown_unified_judge、LR採用後は書換え文を正解とする n3:215-243)。標準経路のTTS技術失敗(p9a status!=OK)はそのattemptを消費(repro01:358-360)
- Fallback: [F-Style] 条件=標準経路2回とも不合格(3回目); PD06 Style(標準経路) → MINIMAL_INSTRUCTION(_run_a2_minimal_fallback_attempt crosslevel:327→repro01.generate_english_component_minimal_instruction)、Secondary必須(force_secondary=True); cooldown=直前に600秒(crosslevel:196-205)
- Local Rewrite: 有効。有効化の仕組み=cs(spec)=connected_speech_enabled_for(clip_id)=True(er063:1004,1015 → crosslevel:287,318)。発動=通算3回(標準2+Fallback1)とも不合格のあと、STOPPED返却直前(crosslevel:318-323)。stop_retrying分岐(:288)はコードに残るが統一judgeはstop_retrying=False固定(er006:908記述)。書換え上限=1(候補生成1回→1候補選択)。再TTS=1回(_run_a2_minimal_fallback_attempt=minimal instruction、script_version=v1、cooldownなし、force_secondary)。検査=run_local_rewrite_recovery(er020:739-812): NG span特定(identify_ng_span)→Luna(gpt-5.6-luna)で候補5件生成→7 Gate QA(意味保持/role/Fact/文脈/Natural English/局所性/非全文)→全PASS候補1件選択→再TTS(retts_fn)1回。候補なし/再TTS不合格→None(呼出元が従来のSTOPPED→HR Lockへ)。再TTS後は統一judge(書換え文を正解、M1 anchor=元原稿)。採用後に6%減速+減速後再検証
- 総試行表記: 通常2+Fallback1+LR後1=総4(減速後NGの取り直しは通算3の残予算内)
- cooldown: 固定600秒(er020_tts_retry_local_rewrite_01.py:57 COOLDOWN_SECONDS、maybe_cooldown_before_attempt :64-92)。通算3回目attemptの直前のみ・connected_speech_enabled_for(segment_id)=Trueのときだけ。単一time.sleep(600)でSTOP sentinel確認なし(:85-86)
- HR/Lock: record_outcome:新状態HUMAN_REVIEW_REQUIRED、累積TTS>15またはASR>60でBUDGET_GUARD(er011:68-69,:387-410)
- 最終NG時: LR None→STOPPED→guarded_generate.record_outcome→HUMAN_REVIEW_REQUIRED(er011:357-)。HR queue追記=最終slot(通算3)NGでjudgeが追記(er006:644,:1294)。runner: 全clip処理後 status!=OK があれば FamilyZTtsClipFailedStop rc=2(er026:2357)。減速後NGが最終slot=finalize_a2_slowdown_final_ng(n3:309)でHR Lock、LRなし(n3:319 docstring)
- STOP: HR+STOP(stage例外rc=2、sentinelなし)
- 仕様参照: CURRENT_SPEC.md:2176(2026-09-26 cooldown+LR+5 role); CURRENT_SPEC.md:2886(2026-10-19決定・基本フロー); docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md §3
- runtime evidence: Std narrator LR実走1件: er011_output/local_rewrite_recovery/run_sf_prod_01/a2/local_rewrite_recovery_full_story_part1_c10.json(RESOLVED_BY_LOCAL_REWRITE、the_monkeys_paw、非chunk時代) | cooldown発生 narrator a2 6件(複数run合算・重複あり、er026_output/family_z_production_e2e_01/*/*/a2/audit/tts_generation_results.json走査) | Std chunk: docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/EVIDENCE_Z_01.md=正常経路のみ。LR/強制NG fallback/exhaustのZ Std chunk実runは未取得(§5)
- 仕様・実装一致: 一致(Std chunk経由のLR/fallback/exhaustはruntime証拠なし[未検証])(分類A)
- 補足(事実): LR再TTSはminimal instruction(PD06でない)。OPEN-274(未承認候補)が同事象を記録済み / 3NGにSecondary障害を含まない条件は未実装(CURRENT_SPEC:2886、OPEN-371)

### Z-A2-DIALOGUE-CTX — Standard(a2) / 登場人物のセリフ(dialogue) policy=fz_ctx_v1(新規runの既定)

- 生成関数: er063:1019 dialogue() → er063:908 generate_dialogue_ctx → er012_b_family_voices_production_01.py:483 generate_voice_body_wide_margin(@guarded_generate('en'), attempt_hook=DialogueAttemptPolicy[er122_fz_ctx_policy_01.py])
- 呼出し引数: text=_norm_for_tts, voice=spec.voice, max_attempts=policy.remaining()(初回3), attempt_hook=policy(er063:934)。style_prefix_override=policy.before_attemptが決定(n<=2:ctx style、n=3:None=従来)。enable_connected_speech_equivalence_layer=True(既定:judge内CS層のみ。cooldown/LRは本関数に呼出なし)。LR関連引数・LR呼出なし。dialogue_ctx(spec.extra)はprepare_dialogue_ctx(er063:888)が付与
- 通常TTS上限: 品質NG: n=1 ctx, n=2 ctx(待機0), n=3 従来方式=通算3(MAX_TOTAL_ATTEMPTS=3 er122_fz_ctx_policy:31、CTX_ATTEMPTS=2 :32)。4回目なし。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠。attempt内で技術失敗/発話区間検出失敗/異常長のときのみ同attempt番号でminimal_fallback 1回追加(er012_b:550-562、effective_mode=minimal_fallback_in_ctx_attempt/..._in_legacy_attempt)
- Retry条件: 統一judge(er006_secondary_asr_01.py:586 evaluate_attempt_with_cascade/:874 _detail): Primary=OpenAI→NGならSecondary=Azure(force_secondary時はPrimary PASSでもSecondary必須)。発音NG・内容不一致はjudge内分類(TRUE_CONTENT_MISMATCH/entity-like等)でNG、ASR表記違い・音韻同等はPASS/PASS_WITH_WARNING(再生成しない)。長さNG=final_length_ok(er078_asr_unified_judge_01)。さらにdisfluency gate(dq18)・repetition QA gateのAND。無音/発話区間検出失敗/異常長=detect_duration_anomaly(er003_audio_tts_asr_safety.py:189)で当該attemptを技術失敗扱い(回数はn=1..3、NG判定はattempt直後)
- Fallback: [F-Prompt] 条件=n=1,n=2(ctx)とも不合格(3回目); 文脈・感情付きStyle(sty['style']) → 従来Dialogue Style(style_prefix_override=None→p9a.ENGLISH_STYLE_PREFIX、CONTEXT/話者/前後セリフ/manner完全除外); cooldown=直前に600秒(er122:298 _cooldown_before_fallback、起点=直前試行の最終NG確定時刻、5秒刻みSTOP sentinel確認、実時間・再開時も10分未満にならない) / [F-Tech(Style兼)] 条件=attempt内でTTS技術失敗/発話区間検出失敗/異常長; 当該attemptのStyle → MINIMAL_INSTRUCTION(generate_voice_body_minimal_fallback er012_b:451); cooldown=なし
- Local Rewrite: 無効。有効化の仕組み=未配線(generate_voice_body_wide_margin・generate_dialogue_ctx・dialogue()にLR呼出なし。git log -S local_rewrite -- er012_b…は0件)
- 総試行表記: 通常ctx2+Fallback(従来方式)1+LR後0=総3(4回目なし)
- cooldown: n=3の直前のみ600秒(er122:288-289,298-338)
- HR/Lock: guarded_generate(er012_b:482)+record_outcome。ctx stateは<level>/audit/dialogue_ctx_attempt_state.json(TTS呼出前にn_startedを書く)。再生成はexplicit_regenerate/consuming_regenerate_approval/本文・policy・ctx style不一致のみ新規サイクル(er122:_open)。Lock判定はstate更新より先(er063:919-923)
- 最終NG時: 3回目NG→STOPPED(attempt_hook.final_reason)→record_outcome→HUMAN_REVIEW_REQUIRED→policy.finish→state TERMINAL_NG(er122:390-)→runner stage例外FamilyZTtsClipFailedStop rc=2(sentinelなし)。HR queue追記=最終slotのASR由来NGの場合のみ(forced repetition QA NGのE-4ではqueue追記0)
- STOP: HR+STOP(stage例外rc=2)。cooldown中のSTOP sentinelは5秒刻みで確認し、検知時はFamilyZDialogueCtxStop等で中断(stateは起点保持)
- 仕様参照: docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md §2,§6; CURRENT_SPEC.md:1644-1654; docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/DESIGN_02.md:61(J-1)
- runtime evidence: E-1(正常経路・Std dialogue 10 clip ctx): docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_E-1_run_fzcw_e1_01.json | E-2 Std(強制NG→cooldown実測600.001s→従来方式PASS): RUNTIME_EVIDENCE_E-2_run_fzcw_e2_a2_01.json | E-3 Std(cooldown中kill→再開、重複TTS 0): RUNTIME_EVIDENCE_E-3_run_fzcw_e3_a2_01_resume.json | E-4 Std(3回強制NG→TERMINAL_NG+HR Lock+rc=2): RUNTIME_EVIDENCE_E-4_run_fzcw_e4_a2_01.json | E-5 Std(1回目NG→kill→再開で2回目ctx即時PASS): RUNTIME_EVIDENCE_E-5_run_fzcw_e5_a2_01_resume.json | (強制NGはrepetition QA gate上書き。実ASR NG由来のn=3 HR queue追記は未観測=runtime証拠なし)
- 仕様・実装一致: 一致(ユーザー原文§2の前段[ctx→ctx→cooldown→従来方式、総3回]) / 原文§2の「NG→既存のLocal Rewrite処理へ」段は 不一致(未配線、ユーザー承認の除外記録なし=仕様記録なし(C))(分類C)
- 補足(事実): ユーザー原文§2:『3回目…NG → 既存のLocal Rewrite処理へ』『Local Rewriteで解決できなければ、既存のHuman Review／STOP規則に従う』、§6表『3回ともNG → Local Rewrite／Human Review／STOPへ正しく移行』 / J-1=Fable判断(DESIGN_02.md:6,61)。ユーザー承認の記録なし(UDR/OPEN-528でDeferred非blocking)

### Z-A2-DIALOGUE-LEGACY — Standard(a2) / 登場人物のセリフ(dialogue) policy=legacy(既存run・ロールバック時)

- 生成関数: er063:1019 dialogue() → er012_b:483 generate_voice_body_wide_margin(attempt_hook=None)
- 呼出し引数: text, voice=spec.voice(max_attempts既定=3、style_prefix_override=None、enable_connected_speech_equivalence_layer=True[judgeのみ]、enable_repetition_qa=True)。LR/cooldown引数なし
- 通常TTS上限: 品質NG: 同一従来Dialogue Styleで通算3。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠。attempt内技術失敗時のみminimal_fallback 1回追加
- Retry条件: 統一judge(er006_secondary_asr_01.py:586 evaluate_attempt_with_cascade/:874 _detail): Primary=OpenAI→NGならSecondary=Azure(force_secondary時はPrimary PASSでもSecondary必須)。発音NG・内容不一致はjudge内分類(TRUE_CONTENT_MISMATCH/entity-like等)でNG、ASR表記違い・音韻同等はPASS/PASS_WITH_WARNING(再生成しない)。長さNG=final_length_ok(er078_asr_unified_judge_01)。さらにdisfluency gate(dq18)・repetition QA gateのAND。無音/発話区間検出失敗/異常長=detect_duration_anomaly(er003_audio_tts_asr_safety.py:189)で当該attemptを技術失敗扱い
- Fallback: [F-Tech(Style兼)] 条件=attempt内でTTS技術失敗/発話区間検出失敗/異常長; 従来Dialogue Style → MINIMAL_INSTRUCTION; cooldown=なし
- Local Rewrite: 無効。有効化の仕組み=未配線
- 総試行表記: 通常3+Fallback0+LR後0=総3
- cooldown: なし(dialogue経路に呼出なし。EXISTING_SPEC_CHECK_01 §2)
- HR/Lock: guarded_generate+record_outcome
- 最終NG時: 3回NG→STOPPED→record_outcome→HUMAN_REVIEW_REQUIRED→rc=2。待機(cooldown)なし
- STOP: HR+STOP(rc=2)
- 仕様参照: CURRENT_SPEC.md:1644-1654(legacy維持・ロールバック); er122_fz_ctx_policy_01.py:95 resolve_run_policy
- runtime evidence: 過去Z run(複数run合算・重複あり)dialogue a2 347 entry: 2回以上16 / 3回以上6 / notOK 4(er026_output/family_z_production_e2e_01/*/a2/audit/tts_generation_results.json走査。the_open_window run_sf_prod_01_preserve_20261023 part1_c14,part3_c2が3回STOPPED)
- 仕様・実装一致: 仕様記録なし(C): dialogueにLR/cooldownを置かない根拠の承認記録なし(上記ctx行と同じ)(分類C)

### Z-A2-TOPIC — Standard(a2) / Topic intro(topic_intro_en、Aoede)

- 生成関数: er063:1044 topic_intro() → crosslevel.generate_english_segment_with_fallback(er003_v1_crosslevel_audio_02_common.py:95)
- 呼出し引数: text, out, first_words(…,3), max_extra_chars=30, style_prefix_override=X_TOPIC_INTRO, enable_connected_speech_equivalence_layer=cs(spec)=False[resolve_narrative_role('topic_intro_en')=None を実測]、tts_backend
- 通常TTS上限: 標準2(同一Style)+Fallback1=通算3。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠
- Retry条件: 統一judge(er006_secondary_asr_01.py:586 evaluate_attempt_with_cascade/:874 _detail): Primary=OpenAI→NGならSecondary=Azure(force_secondary時はPrimary PASSでもSecondary必須)。発音NG・内容不一致はjudge内分類(TRUE_CONTENT_MISMATCH/entity-like等)でNG、ASR表記違い・音韻同等はPASS/PASS_WITH_WARNING(再生成しない)。長さNG=final_length_ok(er078_asr_unified_judge_01)。さらにdisfluency gate(dq18)・repetition QA gateのAND。無音/発話区間検出失敗/異常長=detect_duration_anomaly(er003_audio_tts_asr_safety.py:189)で当該attemptを技術失敗扱い
- Fallback: [F-Style] 条件=標準2回不合格(3回目); X_TOPIC_INTRO Style → MINIMAL_INSTRUCTION; cooldown=なし(cs=False)
- Local Rewrite: 無効。有効化の仕組み=cs=Falseのため無効(crosslevel:287,318のif enable_connected_speech_equivalence_layer)
- 総試行表記: 通常2+Fallback1+LR後0=総3
- cooldown: なし
- HR/Lock: guarded_generate
- 最終NG時: STOPPED→HR Lock→rc=2
- STOP: HR+STOP
- 仕様参照: CURRENT_SPEC.md:2176(Topic introは5 roleに含まれる); er060_output/melos_production_e2e_01/IMPLEMENTATION_DESIGN_02.md:34; docs/research/PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/RUNTIME_EVIDENCE_02.md:18
- runtime evidence: Z topic_intro a2 34 entry(複数run合算): 再試行0・notOK 0(走査)=LR/cooldown不発火の実データなし
- 仕様・実装一致: 不一致(B): 承認済み5 roleにTopic introが含まれるがZ clip_id topic_intro_enは未分類(role None)(分類B)
- 補足(事実): Xのsegment_idは'topic_intro'(er019_family_x_audio_production_runner_01.py:1504)でTOPIC_INTROに解決される(er020:156)

### Z-A2-JA — Standard(a2) / 日本語タイトル(japanese_title)/Preview(preview)/Comment 1-3(comment_n)

- 生成関数: er063:1052 ja_simple() → er003_v1_n3_01_tts_generate.py:819 generate_a2_japanese_with_reading_safety → :693 generate_a2_japanese_with_fallback
- 呼出し引数: spec.text, out, expected_substring_ja, style_prefix_override=X_J3/S3, tts_backend。cs/cooldown/LR引数なし。reading-safety等のゲート(placeholder/禁止記号/外来語トークン)でTTS前STOPPED有り(n3:826-858)
- 通常TTS上限: 標準2(同一Style)+Fallback1=通算3(n3:732)。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠
- Retry条件: 日本語統一judge: er007_ja_secondary_asr_01.py:762 evaluate_attempt_ja_with_cascade(Primary OpenAI→Secondary、全文Validator+SCG)+長さ。disfluency/repetition gateなし
- Fallback: [F-Style] 条件=標準2回不合格(3回目); X_J3/S3 Style → _generate_a2_japanese_minimal_instruction(minimal); cooldown=なし
- Local Rewrite: 無効。有効化の仕組み=日本語経路にLR呼出なし(英語5 roleのみ)
- 総試行表記: 通常2+Fallback1+LR後0=総3
- cooldown: なし
- HR/Lock: guarded_generate相当(generate_narration_snippet_verified_strict経由)
- 最終NG時: STOPPED→HR Lock(最終slot NGでJA queue追記)→rc=2。外来語/記号残存はHR queueへ即時(safety.log_foreign_token_human_review)
- STOP: HR+STOP
- 仕様参照: docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md(DECISION_LOG.md:21596-21598 日本語Local Rewrite); CURRENT_SPEC.md:2176(A2 Preview/Commentは日本語で5 role適用対象なし); OPEN_ITEMS.md OPEN-260(日本語LR未配線)
- runtime evidence: Z a2 comment 102 entry(重複あり): 2回以上22 / 3回以上7 / notOK 7、preview 3回以上1、japanese_title 2回以上6件(走査)。LR=0
- 仕様・実装一致: 一致(分類A)

### Z-A2-KPEN — Standard(a2) / Key Phrase英語(kp{r}_en)

- 生成関数: er063:1060 kp_en() → :1069 _kp_en_two_stage(@guarded_generate('en')) → repro01.generate_narration_snippet_verified_strict×2段(er003_v1_repro01_main_generate.py:198)
- 呼出し引数: 段1: max_attempts=KEY_PHRASE_MINIMAL_MAX_ATTEMPTS=2, style=K2, slot_offset=0,total_slots=4, vote_pass_required=kp_vote.vote_enabled()。段2: max_attempts=KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS=2, style=KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION, slot_offset=2,total_slots=4。cs引数なし(cooldown/LR不可)
- 通常TTS上限: K2 Style 2+ENGLISH_LOCK 2=通算4(repro01:685-687 KEY_PHRASE_TOTAL_MAX_ATTEMPTS=4。全体『TTS3回』の唯一の例外 CURRENT_SPEC.md:2885(1))。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠
- Retry条件: KP3V: 3-ASR多数決(OpenAI・Azure・Whisper、2/3 PASS)+disfluency gate。Azure circuit open時は段2をskip(技術STOP) (er063:1080)
- Fallback: [F-Style] 条件=段1(K2)2回不合格; K2 Style → ENGLISH_LOCK instruction(2回); cooldown=なし
- Local Rewrite: 無効。有効化の仕組み=Key Phraseは5 roleの明示的非適用(er020:117-121)
- 総試行表記: 通常2+Fallback2+LR後0=総4
- cooldown: なし
- HR/Lock: 外側guard1つ(er063:1068)
- 最終NG時: 段2最終slot(通算4)NG→STOPPED→HR Lock→rc=2(HR queue追記は通算4のみ)
- STOP: HR+STOP
- 仕様参照: CURRENT_SPEC.md:2885(1); CURRENT_SPEC.md:2873(KP3V)
- runtime evidence: Z a2 kp_english 138 entry: 再試行0
- 仕様・実装一致: 一致(分類A)

### Z-A2-KPJA — Standard(a2) / Key Phrase日本語意味(kp{r}_ja)

- 生成関数: er063:1108 kp_ja() → generate_a2_japanese_with_reading_safety(n3:819)
- 呼出し引数: max_extra_chars=30, known_key_phrase_terms=[used_form], style=P8_KP
- 通常TTS上限: 標準2+Fallback(minimal)1=通算3
- Retry条件: 日本語統一judge(Z-A2-JAと同じ)
- Fallback: [F-Style] 条件=標準2回不合格; P8_KP Style → minimal instruction; cooldown=なし
- Local Rewrite: 無効。有効化の仕組み=日本語・Key Phrase
- 総試行表記: 通常2+Fallback1+LR後0=総3
- cooldown: なし
- HR/Lock: あり
- 最終NG時: STOPPED→HR Lock→rc=2
- STOP: HR+STOP
- 仕様参照: er020_tts_retry_local_rewrite_01.py:117-121
- runtime evidence: Z a2 kp_japanese_meaning 138 entry: 2回以上1
- 仕様・実装一致: 一致(分類A)

### Z-B1B-NARR — Advanced(b1b) / 地の文(narrator) story clip・100語超はchunk[_k{j}]

- 生成関数: er063:1007 narrator() → er003_v1_sing01_news_tail_fix.py:63 generate_news_narration_wide_margin(@guarded_generate('en'))
- 呼出し引数: disfluency_qa=False, enable_connected_speech_equivalence_layer=cs(spec)=True, enable_repetition_qa=True, enable_pronunciation_resolver=True, style_prefix_override=PD06, tts_backend。max_attempts既定=3。attempt_hook/prior_generationsなし
- 通常TTS上限: 品質NG: 同一PD06 Styleで通算3(news_tail:144)。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠。attempt内でTTS失敗/発話区間検出失敗/異常長→同attempt番号でminimal_fallback 1回追加(news_tail:179-186)
- Retry条件: 統一judge(er006_secondary_asr_01.py:586 evaluate_attempt_with_cascade/:874 _detail): Primary=OpenAI→NGならSecondary=Azure(force_secondary時はPrimary PASSでもSecondary必須)。発音NG・内容不一致はjudge内分類(TRUE_CONTENT_MISMATCH/entity-like等)でNG、ASR表記違い・音韻同等はPASS/PASS_WITH_WARNING(再生成しない)。長さNG=final_length_ok(er078_asr_unified_judge_01)。さらにdisfluency gate(dq18)・repetition QA gateのAND。無音/発話区間検出失敗/異常長=detect_duration_anomaly(er003_audio_tts_asr_safety.py:189)で当該attemptを技術失敗扱い
- Fallback: [F-Tech(Style兼)] 条件=attempt内でTTS技術失敗/発話区間検出失敗/異常長のみ; PD06 Style → MINIMAL_INSTRUCTION(repro01.generate_english_component_minimal_instruction); cooldown=なし / [(品質NGに対するFallbackなし)] 条件=-; - → -; cooldown=attempt3直前に600秒(news_tail:149)
- Local Rewrite: 有効。有効化の仕組み=cs(spec)=True(news_tail:301,327)。発動=通算3回不合格のあと、STOPPED返却直前(news_tail:327-335)。stop_retrying分岐(:301)はjudgeがFalse固定のため実質不通。書換え上限=1。再TTS=1回(generate_news_narration_wide_margin.__wrapped__(max_attempts=1, script_version='v1', m1_anchor_text=元原稿)。style_prefix_overrideは転送されずp9a.ENGLISH_STYLE_PREFIX[PD06でない]、news_tail:370-377)。cooldownなし(max_attempts=1<3)。検査=run_local_rewrite_recovery(er020:739-812): NG span特定(identify_ng_span)→Luna(gpt-5.6-luna)で候補5件生成→7 Gate QA(意味保持/role/Fact/文脈/Natural English/局所性/非全文)→全PASS候補1件選択→再TTS(retts_fn)1回。候補なし/再TTS不合格→None(呼出元が従来のSTOPPED→HR Lockへ)
- 総試行表記: 通常3+Fallback0+LR後1=総4(attempt内技術minimal行は別計上)
- cooldown: 固定600秒(er020_tts_retry_local_rewrite_01.py:57 COOLDOWN_SECONDS、maybe_cooldown_before_attempt :64-92)。通算3回目attemptの直前のみ・connected_speech_enabled_for(segment_id)=Trueのときだけ。単一time.sleep(600)でSTOP sentinel確認なし(:85-86)
- HR/Lock: record_outcome(累積TTS>15でBUDGET_GUARD)
- 最終NG時: LR None→STOPPED→record_outcome→HUMAN_REVIEW_REQUIRED。HR queue追記=最終slot(attempt3)NGでjudge(LR成否に先行)。runner rc=2(er026:2357)
- STOP: HR+STOP
- 仕様参照: CURRENT_SPEC.md:2176; CURRENT_SPEC.md:2886; 2026-10-19ユーザー決定(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md §3-4)
- runtime evidence: Adv narrator LR実走9件(melos run_e2e_01/02/04, run_kga3_off_z_01, run_kgcpw_z_01, run_kgcpw_z_e5_a2/b1b_01, the_open_window run_sf_prod_01_preserve_20261023): audio_text_deviationあり・status OK(走査) | cooldown発生 narrator b1b 3件 | Adv chunk正常経路: docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_01.md(LR 0)
- 仕様・実装一致: 一致(分類A)
- 補足(事実): LR再TTSのStyleはPD06ではない(OPEN-274)

### Z-B1B-DIALOGUE-CTX — Advanced(b1b) / 登場人物のセリフ(dialogue) policy=fz_ctx_v1(新規runの既定)

- 生成関数: er063:1019 dialogue() → er063:908 generate_dialogue_ctx → er003_v1_n3_01_tts_generate.py:434 generate_with_a2_slowdown_outer_loop(gen=er012_b:483 generate_voice_body_wide_margin, attempt_hook=policy)
- 呼出し引数: 外側: slowdown_pct=Z_ADV_DIALOGUE_SLOWDOWN_PCT(-5.66=約6%高速化)、prior_generations=policy.prior_generations()(er063:953)。内側gen(): ma=min(max_attempts, policy.remaining())、attempt_hook=policy、passごとにpolicy.note_final_ng/mark_counted。LR関連引数なし
- 通常TTS上限: 品質NG: n=1 ctx, n=2 ctx(待機0), n=3 従来方式=通算3。減速後NGも1回に数え、外側ループ(max_slowdown_attempts=3)と内側ループが同じpolicy n を共有(passをまたいで継続)。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠。attempt内minimal_fallback有
- Retry条件: 統一judge(er006_secondary_asr_01.py:586 evaluate_attempt_with_cascade/:874 _detail): Primary=OpenAI→NGならSecondary=Azure(force_secondary時はPrimary PASSでもSecondary必須)。発音NG・内容不一致はjudge内分類(TRUE_CONTENT_MISMATCH/entity-like等)でNG、ASR表記違い・音韻同等はPASS/PASS_WITH_WARNING(再生成しない)。長さNG=final_length_ok(er078_asr_unified_judge_01)。さらにdisfluency gate(dq18)・repetition QA gateのAND。無音/発話区間検出失敗/異常長=detect_duration_anomaly(er003_audio_tts_asr_safety.py:189)で当該attemptを技術失敗扱い。加えて減速後(atempo 1.06)再検証NG(n3:121,:194→統一judge)
- Fallback: [F-Prompt] 条件=n=1,n=2(ctx)不合格(3回目); 文脈・感情付きStyle → 従来Dialogue Style(style_prefix_override=None); cooldown=直前に600秒(減速後NGのpassでは起点=final_ng_epoch) / [F-Tech(Style兼)] 条件=attempt内技術失敗等; 当該Style → MINIMAL_INSTRUCTION; cooldown=なし
- Local Rewrite: 無効。有効化の仕組み=未配線
- 総試行表記: 通常ctx2+Fallback(従来方式)1+LR後0=総3(実TTS3回を超えない)
- cooldown: n=3の直前600秒
- HR/Lock: 同上
- 最終NG時: n=3 NG(ASR前または減速後)→STOPPED→finalize_a2_slowdown_final_ng(減速後NG時、n3:309)/record_outcome→HR Lock→TERMINAL_NG→rc=2。M-3(ii):行会計(count_tts_generations_in_result=attempts_log行数、minimal行も計上)で外側予算が先に尽きn=3(従来方式)に到達しない稀ケースはSTOPPED+HR Lock(terminal_before_fallback=True、er063:959)
- STOP: HR+STOP
- 仕様参照: FZ原文§2,§6; CURRENT_SPEC.md:1644-1654(M-3=(ii))
- runtime evidence: E-1 Adv(dialogue 11 clip ctx): RUNTIME_EVIDENCE_E-1_run_fzcw_e1_01.json | E-2 Adv: RUNTIME_EVIDENCE_E-2_run_fzcw_e2_b1b_01.json | E-4 Adv(3回強制NG→TERMINAL_NG): RUNTIME_EVIDENCE_E-4_run_fzcw_e4_b1b_01.json | E-6 Adv(減速後NG→外側ループ継続・通算2回目ctx PASS): RUNTIME_EVIDENCE_E-6_run_fzcw_e6_b1b_01.json | M-3(i)併発シナリオ(Advのminimal_fallback併発)は未観測(EVIDENCE_01.md:125)
- 仕様・実装一致: 一致(前段) / LR段は不一致(仕様記録なし(C)) / M-3(ii)の『行会計で従来方式未到達』は仕様記録なし(C、Fable採用・ユーザー判断候補)(分類C)
- 補足(事実): M-3(i)は既存A2予算規則変更のため未実施=OPEN-528 Deferred(2)

### Z-B1B-DIALOGUE-LEGACY — Advanced(b1b) / 登場人物のセリフ(dialogue) policy=legacy

- 生成関数: er063:1026-1031 dialogue() → n3:434 generate_with_a2_slowdown_outer_loop(gen=er012_b:483 generate_voice_body_wide_margin(max_attempts=max_attempts))
- 呼出し引数: slowdown_pct=Z_ADV_DIALOGUE_SLOWDOWN_PCT、prior_generations既定0、attempt_hookなし、style_prefix_overrideなし
- 通常TTS上限: 同一従来Dialogue Styleで通算3(減速後NGも通算3に含む)。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠
- Retry条件: 統一judge(er006_secondary_asr_01.py:586 evaluate_attempt_with_cascade/:874 _detail): Primary=OpenAI→NGならSecondary=Azure(force_secondary時はPrimary PASSでもSecondary必須)。発音NG・内容不一致はjudge内分類(TRUE_CONTENT_MISMATCH/entity-like等)でNG、ASR表記違い・音韻同等はPASS/PASS_WITH_WARNING(再生成しない)。長さNG=final_length_ok(er078_asr_unified_judge_01)。さらにdisfluency gate(dq18)・repetition QA gateのAND。無音/発話区間検出失敗/異常長=detect_duration_anomaly(er003_audio_tts_asr_safety.py:189)で当該attemptを技術失敗扱い+減速後再検証
- Fallback: [F-Tech(Style兼)] 条件=attempt内技術失敗等; 従来Dialogue Style → MINIMAL_INSTRUCTION; cooldown=なし
- Local Rewrite: 無効。有効化の仕組み=未配線
- 総試行表記: 通常3+Fallback0+LR後0=総3
- cooldown: なし
- HR/Lock: あり
- 最終NG時: STOPPED→finalize_a2_slowdown_final_ng/record_outcome→HR Lock→rc=2
- STOP: HR+STOP
- 仕様参照: CURRENT_SPEC.md:2885(5)(6)
- runtime evidence: Z b1b dialogue 369 entry(重複あり): 2回以上14 / 3回以上5 / notOK 4(走査)
- 仕様・実装一致: 仕様記録なし(C): LR/cooldownをdialogueに置かない根拠の承認記録なし(分類C)

### Z-B1B-TOPIC — Advanced(b1b) / Topic intro(topic_intro_en、Charon)

- 生成関数: er063:1044 topic_intro() → :1037 charon_en() → er003_v1_sing01_voice01_generate.py:49 generate_charon_english
- 呼出し引数: disfluency_qa=False(kind=topic_intro), enable_connected_speech_equivalence_layer=cs(spec)=False[role None], enable_pronunciation_resolver=True, style_prefix_override=X_TOPIC_INTRO, tts_backend
- 通常TTS上限: 同一Styleで通算3。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠
- Retry条件: 統一judge(er006_secondary_asr_01.py:586 evaluate_attempt_with_cascade/:874 _detail): Primary=OpenAI→NGならSecondary=Azure(force_secondary時はPrimary PASSでもSecondary必須)。発音NG・内容不一致はjudge内分類(TRUE_CONTENT_MISMATCH/entity-like等)でNG、ASR表記違い・音韻同等はPASS/PASS_WITH_WARNING(再生成しない)。長さNG=final_length_ok(er078_asr_unified_judge_01)。さらにdisfluency gate(dq18)・repetition QA gateのAND。無音/発話区間検出失敗/異常長=detect_duration_anomaly(er003_audio_tts_asr_safety.py:189)で当該attemptを技術失敗扱い
- Fallback: [なし] 条件=-; - → -; cooldown=なし(cs=False)
- Local Rewrite: 無効。有効化の仕組み=cs=Falseのため無効(voice01:305,325)
- 総試行表記: 通常3+Fallback0+LR後0=総3
- cooldown: なし
- HR/Lock: あり
- 最終NG時: STOPPED→HR Lock→rc=2
- STOP: HR+STOP
- 仕様参照: CURRENT_SPEC.md:2176; IMPLEMENTATION_DESIGN_02.md:34
- runtime evidence: Z topic_intro b1b 34 entry: 再試行0
- 仕様・実装一致: 不一致(B): 5 roleにTopic introが含まれるがZ clip_idが未分類(分類B)

### Z-B1B-PREVCOM — Advanced(b1b) / Preview英語(preview、E1)/Comment 1-3英語(comment_n、E2_UPBEAT)

- 生成関数: er063:1057 preview()/comment → :1037 charon_en() → voice01.generate_charon_english(er003_v1_sing01_voice01_generate.py:49)
- 呼出し引数: disfluency_qa=True(preview/comment), enable_connected_speech_equivalence_layer=cs(spec)=True(role PREVIEW/COMMENT), enable_pronunciation_resolver=True, style_prefix_override=E1/E2_UPBEAT, tts_backend
- 通常TTS上限: 同一Styleで通算3(voice01:151)。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠
- Retry条件: 統一judge(er006_secondary_asr_01.py:586 evaluate_attempt_with_cascade/:874 _detail): Primary=OpenAI→NGならSecondary=Azure(force_secondary時はPrimary PASSでもSecondary必須)。発音NG・内容不一致はjudge内分類(TRUE_CONTENT_MISMATCH/entity-like等)でNG、ASR表記違い・音韻同等はPASS/PASS_WITH_WARNING(再生成しない)。長さNG=final_length_ok(er078_asr_unified_judge_01)。さらにdisfluency gate(dq18)・repetition QA gateのAND。無音/発話区間検出失敗/異常長=detect_duration_anomaly(er003_audio_tts_asr_safety.py:189)で当該attemptを技術失敗扱い
- Fallback: [なし(品質NG)] 条件=-; - → -; cooldown=attempt3直前600秒(voice01:156)
- Local Rewrite: 有効。有効化の仕組み=cs=True(voice01:305,325)。発動=通算3回不合格のあと(voice01:325-331)。書換え上限=1。再TTS=1回(generate_charon_english.__wrapped__(max_attempts=1, style_prefix_override=元のStyleを転送, script_version=v1), voice01:364-)。検査=run_local_rewrite_recovery(er020:739-812): NG span特定(identify_ng_span)→Luna(gpt-5.6-luna)で候補5件生成→7 Gate QA(意味保持/role/Fact/文脈/Natural English/局所性/非全文)→全PASS候補1件選択→再TTS(retts_fn)1回。候補なし/再TTS不合格→None(呼出元が従来のSTOPPED→HR Lockへ)
- 総試行表記: 通常3+Fallback0+LR後1=総4
- cooldown: 固定600秒(er020_tts_retry_local_rewrite_01.py:57 COOLDOWN_SECONDS、maybe_cooldown_before_attempt :64-92)。通算3回目attemptの直前のみ・connected_speech_enabled_for(segment_id)=Trueのときだけ。単一time.sleep(600)でSTOP sentinel確認なし(:85-86)
- HR/Lock: record_outcome
- 最終NG時: LR None→STOPPED→HR Lock→rc=2
- STOP: HR+STOP
- 仕様参照: CURRENT_SPEC.md:2176; CURRENT_SPEC.md:2886
- runtime evidence: Z b1b comment 102 entry(重複あり): 2回以上1・LR 0。LR実走なし=runtime証拠なし(未検証)
- 仕様・実装一致: 一致(LR実走はruntime証拠なし[未検証])(分類A)

### Z-B1B-KPEN — Advanced(b1b) / Key Phrase英語(kp{r}_en)

- 生成関数: Z-A2-KPENと同じ(er063:1060 kp_en)
- 呼出し引数: 同上
- 通常TTS上限: K2 2+ENGLISH_LOCK 2=通算4。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠
- Retry条件: KP3V 3-ASR多数決+disfluency
- Fallback: [F-Style] 条件=段1不合格; K2 → ENGLISH_LOCK; cooldown=なし
- Local Rewrite: 無効。有効化の仕組み=Key Phrase非適用
- 総試行表記: 通常2+Fallback2+LR後0=総4
- cooldown: なし
- HR/Lock: あり
- 最終NG時: 通算4 NG→STOPPED→HR Lock→rc=2
- STOP: HR+STOP
- 仕様参照: CURRENT_SPEC.md:2885(1)
- runtime evidence: Z b1b kp_english 136 entry(重複あり): 2回以上5・notOK 3・fallback 3
- 仕様・実装一致: 一致(分類A)

### Z-B1B-KPEXPL — Advanced(b1b) / Key Phrase英語解説(kp{r}_explanation_en、P7)

- 生成関数: er063:1103 kp_expl_en() → er019_family_x_audio_production_runner_01.py:1205 generate_key_phrase_explanation_en_verified → repro01.generate_narration_snippet_verified_strict
- 呼出し引数: max_attempts=KP_EXPLANATION_MAX_ATTEMPTS=3(er019:1202)、disfluency_qa=True、enable_non_latin_cascade=True、style=P7。cs引数なし
- 通常TTS上限: 同一Styleで通算3。技術エラー(429/5xx/timeout等)=各TTS呼出内の_call_tts_with_retry(er002_common.py:703、max_retry=MAX_TTS_TECHNICAL_RETRY=1[p9a:138→p4c:42→p4b:39→p4:61])=品質NG回数とは別枠
- Retry条件: 統一judge(er006_secondary_asr_01.py:586 evaluate_attempt_with_cascade/:874 _detail): Primary=OpenAI→NGならSecondary=Azure(force_secondary時はPrimary PASSでもSecondary必須)。発音NG・内容不一致はjudge内分類(TRUE_CONTENT_MISMATCH/entity-like等)でNG、ASR表記違い・音韻同等はPASS/PASS_WITH_WARNING(再生成しない)。長さNG=final_length_ok(er078_asr_unified_judge_01)。さらにdisfluency gate(dq18)・repetition QA gateのAND。無音/発話区間検出失敗/異常長=detect_duration_anomaly(er003_audio_tts_asr_safety.py:189)で当該attemptを技術失敗扱い(英語KP解説)
- Fallback: [なし] 条件=-; - → -; cooldown=なし
- Local Rewrite: 無効。有効化の仕組み=5 role外(resolve_narrative_role('kp1_explanation_en')=None、実測)
- 総試行表記: 通常3+Fallback0+LR後0=総3
- cooldown: なし
- HR/Lock: あり
- 最終NG時: 通算3 NG→STOPPED→HR Lock→rc=2
- STOP: HR+STOP
- 仕様参照: er019:1212-1213(統一フロー『TTS①②③、3回NGでLR/HR』に揃えた)
- runtime evidence: Z b1b kp_explanation 130 entry: 再試行0
- 仕様・実装一致: 一致(5 role列挙外のため非適用。明示除外の承認記録はKey Phraseまで=KP解説を名指しした除外記録は未確認)(分類A)
- 補足(事実): er019:1212の注記は『3回NGでLR/HR』と書くが、本関数にLR呼出はない(roleがNone)



## 4. 星取表②(Z行: Rewriteが無い/例外の理由と承認)

理由区分は指示原文の5区分(ユーザーが明示不採用/承認済み仕様として対象外/実装当時の技術的制約/共通仕様の適用漏れ・配線漏れ/設計・承認記録に理由なし)。

|Family|音声部位|Rewrite|不適用・例外の理由|ユーザー承認の有無|根拠資料|分類|
|---|---|---|---|---|---|---|
|Z(Adv/Std)|地の文(narrator)・chunk|あり(cs=True)|-|あり(2026-09-26 LR配線承認+2026-10-19発動条件決定)|CURRENT_SPEC.md:2176,2886 / DECISION_LOG.md 2026-10-19|A|
|Z(Adv)|Preview英語・Comment英語|あり(cs=True)|-|あり(同上)|CURRENT_SPEC.md:2176|A|
|Z(Adv)|Topic intro(topic_intro_en)|なし|共通仕様の適用漏れ・配線漏れ(承認済み5 roleにTopic introを含むが、Z clip_idが未分類)。設計メモIMPLEMENTATION_DESIGN_02.md:34は「既存C/Xと同じ扱い」と記すが、Xのsegment_idは'topic_intro'(er019:1504)でTOPIC_INTROに解決される|Z topic introを除外する承認記録は未確認|CURRENT_SPEC.md:2176 / er020:112,156 / RUNTIME_EVIDENCE_02.md:18|B|
|Z(Std)|Topic intro(topic_intro_en)|なし|同上|同上|同上|B|
|Z(Std)|日本語タイトル・Preview日本語・Comment日本語|なし|承認済み仕様として対象外(LRは英語5 roleのみ。2026-10-15ユーザー決定:『日本語Local Rewrite:現行の英語用機構を機械的に流用しない。安全な実装が成立していない場合はHuman Reviewへ進める』)|あり(2026-10-15)|DECISION_LOG.md:21596-21598 / CURRENT_SPEC.md:2176,2873 / OPEN-260|A|
|Z(Std/Adv)|Key Phrase英語・日本語意味|なし|承認済み仕様として対象外(Heading readout・Key Phraseは明示的非適用)。KP英語は4回構成が『TTS3回』の唯一の例外|あり(2026-09-26。明示除外)|er020:117-121(コメント『ユーザー承認済み、明示的除外』) / CURRENT_SPEC.md:2885(1)|A|
|Z(Adv)|Key Phrase英語解説|なし|5 role列挙外(resolve_narrative_role=None)。KP解説を名指しした除外記録は未確認|KP解説単独の除外承認は未確認|er019:1205-1218 / er020:135-176|A|
|Z(Std/Adv)|登場人物のセリフ(dialogue)・ctx方式|なし|(i)ユーザーが明示不採用: 記録なし。(ii)承認済み仕様として対象外: CURRENT_SPECは『Local Rewrite(英語のみ・5 role)』と書くがdialogueを名指しした除外はなし。(iii)実装当時の技術的制約: 記録なし(er012_bは2026-09-08作成、LR配線2026-09-26の commit cdcbf37b6 は er012_b を変更していない)。(iv)Fable判断J-1(DESIGN_02.md:6,61):『Z dialogueにLR未配線の事実+LR新設は古典作品のセリフをLLMで書換える音声と表示本文の乖離を生む新仕様でありユーザー承認事項』(Opus OPUS_REVIEW_01.md:64-70も同意見)=ユーザー承認ではない設計判断|なし(ユーザー原文§2は『既存のLocal Rewrite処理へ』と書く。除外・不採用の承認は記録なし)|ユーザー原文§2,§6 / DESIGN_02.md:6,61 / OPUS_REVIEW_01.md:63-70 / EXISTING_SPEC_CHECK_01.md §2,§3行3 / OPEN_TRACKING_01.md J-1 / OPEN-528 Deferred(1)|C|
|Z(Std/Adv)|登場人物のセリフ(dialogue)・legacy方式(既存run)|なし|同上(ctx導入前から未配線。理由は記録なし)|なし|EXISTING_SPEC_CHECK_01.md §2(全Z run dialogue 667 entryでaudit_text_deviation=0)|C|


## 5. 部位別の現行発動フロー(正確な順序)

凡例: `→`=順序、`[…]`=待機/ゲート、「NG」=統一judgeまたはdisfluency/repetition gateまたは減速後再検証の不合格。HR queue追記は最終slot NG。

### 5-1. dialogue — Std・ctx方式(`Z-A2-DIALOGUE-CTX`)
```
[Review Lock確認 check_before_generation(er063:919)] HUMAN_REVIEW_REQUIRED/HUMAN_APPROVEDなら0 APIで既存block結果を返す
→ [感情notes: level単位1 LLM call(保存済みなら0)、失敗=技術STOP]
→ n=1 ctx Style TTS → judge → PASS=採用(state DONE_OK保存)
   NG → n=2 ctx Style TTS(待機0) → judge → PASS=採用
   NG → [固定600秒 cooldown(5秒刻みSTOP確認、起点=2回目NG確定時刻、再開時も実時間で10分)]
      → n=3 従来Dialogue Style(style_prefix_override=None) TTS → judge → PASS=採用
      NG → STOPPED → record_outcome → HUMAN_REVIEW_REQUIRED(Lock) → state TERMINAL_NG
         → (Local Rewrite段なし) → 全clip後 FamilyZTtsClipFailedStop rc=2
各attempt内: TTS呼出失敗(技術再試行1回後)/発話区間検出失敗/異常長 → 同nで minimal_fallback 1回(F-Tech、effective_mode=minimal_fallback_in_*_attempt)
表記: 通常(ctx)2 + Fallback(従来方式 F-Prompt)1 + LR後0 = 総3(4回目なし)
```
根拠: `er063:908-970`、`er122_fz_ctx_policy_01.py:282-338,348-,390-`、`er012_b:483-640`。

### 5-2. dialogue — Adv・ctx方式(`Z-B1B-DIALOGUE-CTX`)
```
[Lock確認] → 外側ループ generate_with_a2_slowdown_outer_loop(n3:434) 各pass:
   gen(): 内側 generate_voice_body_wide_margin(ma=min(外側残, policy.remaining()))  ← n=ctx/ctx/従来 を policy が通算管理
        → judge PASS → atempo 1.06 → 減速後 統一judge(n3:121,194)
              PASS=採用 / NG → policy.note_final_ng() → 次pass(同じpolicyのnを継続)
   n=2のNG後 → n=3 の直前に 600秒(起点=final_ng_epoch) → 従来Dialogue Style
最終NG: 内側STOPPED または 減速後NGで通算上限 → finalize_a2_slowdown_final_ng(n3:309)/record_outcome → HR Lock → TERMINAL_NG → rc=2
M-3(ii): 外側の行会計(attempts_log行数、minimal行も計上)が先に尽き n=3 未到達で終わるとき → STOPPED+HR Lock(terminal_before_fallback、er063:959)
表記: 通常(ctx)2 + Fallback(従来方式)1 + LR後0 = 総3(実TTS3回超なし)
```

### 5-3. dialogue — legacy方式(Std/Adv、`Z-A2-DIALOGUE-LEGACY`/`Z-B1B-DIALOGUE-LEGACY`)
```
[Lock確認] → 同一従来Style TTS①→judge→NG→②(待機0)→NG→③(待機0、cooldownなし)→NG → STOPPED → HR Lock → rc=2
Adv: 各passのPASS後に atempo 1.06 → 減速後judge → NGなら通算3の残予算で取り直し(最終slot NG→finalize→HR Lock)
各attempt内: 技術失敗等 → minimal_fallback 1回(F-Tech)
表記: 通常3 + Fallback0 + LR後0 = 総3
```

### 5-4. narrator — Std(`Z-A2-NARR`)
```
[Lock確認(guarded_generate)]
→ 標準① PD06 TTS → judge → NG → 標準② PD06(待機0) → judge → NG
→ [固定600秒 cooldown(cs=True時のみ、単一sleep・STOP確認なし)]
→ Fallback③ MINIMAL_INSTRUCTION(F-Style、Secondary必須) → judge
     PASS=採用
     NG → [Local Rewrite] NG span特定→Luna候補5→7 Gate QA→1候補 → LR再TTS(minimal instruction、script_version=v1、1回、cooldownなし) → judge(書換え文を正解)
              PASS=採用(LR_REWRITTEN警告、audio_text_deviation記録のみ。canonical原稿は変更しない)
              NG/候補なし/Gate不合格 → STOPPED → record_outcome → HR Lock(HR queue行は最終slot=通算3のNG時に追記済み)
→ (OK後) 6%減速 → 減速後 統一judge(LR採用時は書換え文を正解)
     NG → 通算3の残予算があれば標準経路から取り直し(外側ループ、max 3周)/残0 → finalize_a2_slowdown_final_ng → HR Lock(LRなし)
→ 全clip後 status!=OK があれば rc=2
表記: 通常2 + Fallback1 + LR後1 = 総4
chunk(>100語): 各chunkが上記を単独で通る(chunk_idがHR Lockのkey)。chunk別6%減速+ASR再検証+厳格Gate(FamilyZSlowdownGateStop、gate stage)
```
根拠: `er003_v1_n3_01_tts_generate.py:331-432`、`crosslevel…:95-325,402-455`、`er020:739-812`。

### 5-5. narrator — Adv(`Z-B1B-NARR`)
```
[Lock確認]
→ ① PD06 TTS → judge → NG → ② PD06(待機0) → NG → [固定600秒(cs=True)] → ③ PD06 → judge → NG
→ [Local Rewrite] → LR再TTS(generate_news_narration_wide_margin.__wrapped__, max_attempts=1, style_prefix_override非転送=標準ENGLISH_STYLE_PREFIX, v1) → judge(書換え文を正解)
     PASS=採用 / NG・候補なし → STOPPED → record_outcome → HR Lock → rc=2
各attempt内: TTS失敗/発話区間検出失敗/異常長 → 同attemptで minimal_fallback 1回(F-Tech)
表記: 通常3 + Fallback0 + LR後1 = 総4(attempt内技術minimal行は別計上)
```

### 5-6. Adv Preview英語・Comment英語(`Z-B1B-PREVCOM`)
```
① E1/E2_UPBEAT → NG → ② 同(待機0) → NG → [600秒] → ③ 同 → NG → LR(元Style転送の再TTS 1回) → NG → STOPPED → HR Lock → rc=2
表記: 通常3 + Fallback0 + LR後1 = 総4(LR実走はruntime証拠なし)
```

### 5-7. Topic intro(Std/Adv、`Z-A2-TOPIC`/`Z-B1B-TOPIC`)
```
Std: 標準①②(X_TOPIC_INTRO) → Fallback③(minimal) → NG → STOPPED → HR Lock → rc=2(cooldownなし、LRなし)   表記: 通常2+Fallback1+LR後0=総3
Adv: ①②③(同一Style)  → NG → STOPPED → HR Lock → rc=2                                                    表記: 通常3+Fallback0+LR後0=総3
(cs=False: clip_id `topic_intro_en` が resolve_narrative_role で未分類)
```

### 5-8. Std日本語(japanese_title/preview/comment/kp_ja、`Z-A2-JA`/`Z-A2-KPJA`)
```
[TTS前ゲート: placeholder/禁止記号/外来語トークン→該当時はTTSなしでSTOPPED+HR queue]
→ 標準①②(JA Style) → 日本語judge → NG → Fallback③(minimal) → NG → STOPPED → HR Lock → rc=2(cooldownなし、LRなし)
表記: 通常2 + Fallback1 + LR後0 = 総3
```

### 5-9. Key Phrase英語(Std/Adv、`Z-A2-KPEN`/`Z-B1B-KPEN`)
```
段1 K2 Style ①② → 3-ASR多数決 → NG → 段2 ENGLISH_LOCK ③④ → NG → STOPPED → HR Lock(HR queue=通算4のみ) → rc=2
(Azure circuit open時は段2をskipして技術STOP) 表記: 通常2 + Fallback(F-Style)2 + LR後0 = 総4
```

### 5-10. Key Phrase英語解説(Adv、`Z-B1B-KPEXPL`)
```
①②③(P7、同一Style) → NG → STOPPED → HR Lock → rc=2   表記: 通常3 + Fallback0 + LR後0 = 総3
```

## 6. ZでLRが有効/無効になる仕組み(事実)

1. LR本体は `er020_tts_retry_local_rewrite_01.run_local_rewrite_recovery`(`:739`)。呼出元は3関数だけ: `voice01._local_rewrite_recovery_for_charon_english`(`er003_v1_sing01_voice01_generate.py:337`)、`news_tail_fix._local_rewrite_recovery_for_news_narration`(`er003_v1_sing01_news_tail_fix.py:346`)、`crosslevel._local_rewrite_recovery_for_english_segment_with_fallback`(`er003_v1_crosslevel_audio_02_common.py:402`)。いずれも `if enable_connected_speech_equivalence_layer:` の内側でのみ呼ぶ。
2. Zが呼ぶ関数と有効性: narrator Adv=`news_tail_fix`(cs=`connected_speech_enabled_for(clip_id)`)、narrator Std=`generate_a2_segment_with_slowdown`→`crosslevel`(同)、Adv Preview/Comment/Topic intro=`voice01.generate_charon_english`、Std Topic intro=`crosslevel`(直接)。`connected_speech_enabled_for` は `resolve_narrative_role(segment_id)` が FULL_STORY/COMMENT/PREVIEW/TOPIC_INTRO/IN_ONE_LINE のとき True(`er020:188-193`)。
3. 実測(`py -c` で関数を呼んだ結果): `topic_intro_en`=None/False、`japanese_title`=None/False、`preview`=PREVIEW/True、`comment_1..3`=COMMENT/True、`kp1_en`/`kp1_ja`=KEY_PHRASE/False、`kp1_explanation_en`=None/False、`full_story_part1_c1`/`part3_c12`/`part1_c2_k1`/`part2_c3_k4`=FULL_STORY/True。
4. Z dialogue(`full_story_part{n}_c{k}`)のclip_idは FULL_STORY に解決される(`er020:152-156`、FAMILY-Z-MELOS 委任_03のOpus M6で追加)が、dialogue生成関数 `generate_voice_body_wide_margin` は `cs` 値を使わず、LR/cooldown呼出を持たない(`er012_b:483-640`)。同関数の `enable_connected_speech_equivalence_layer`(既定True)は judge 内のConnected Speech層(判定)にのみ渡る(`er012_b:579`)。
5. 時系列(事実): `er012_b_family_voices_production_01.py` 新規作成=2026-09-08(commit 1a7f00810)。cooldown+LR+5 role配線=2026-09-26(commit cdcbf37b6、変更ファイル=`er003_v1_n3_01_tts_generate.py`・`er003_v1_sing01_news_tail_fix.py`・`er003_v1_sing01_voice01_generate.py`、`er012_b`は含まれない)。同commitの `TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01_REPORT.md` §2 のrole別表にDialogue/Voices行はない。`er012_b` に `attempt_hook` が入ったのは 2026-10-26(commit 7768af1d2)で、これはLRではなくStyle切替・cooldown用。
6. LR採用後のZ側処理: `_handle_local_rewrite`(`er063:1668-1686`)は `audio_text_deviation` を `writer/provenance.json` の `audio_text_deviations` へ追記するだけで、canonical原稿・表示本文は変更しない。2026-10-12ユーザー決定でer061再検証は撤去済み(`:1671-1674`)。LR再TTSのStyle: Adv narrator=標準 `ENGLISH_STYLE_PREFIX`(PD06は転送されない)、Std narrator=minimal instruction、Adv Preview/Comment=元Style転送。既存OPEN-274が同事象を記録。

## 7. 承認記録との照合(逐語引用)

### 7-1. 2026-10-19 ユーザー決定(Rewrite発動条件)
出典=`docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md` §3(:41-63)。
> 「両ASRが同じ箇所の誤読に合意すること」というRewrite発動条件を削除する。 / Status：`APPROVED_FOR_PRODUCTION` / 基本フロー：TTS初回生成 → Primary／Secondaryによる承認済み検証 → NGなら最大2回のTTS再生成 → なおNGならRewriteへ進む。 / … / この仕様変更によって、別の未承認のRewrite許容条件や品質基準を追加しないこと。

照合: (1) 原文は音声部位・Family・role・dialogueを指定していない(文脈=Zナレーションの `Melos drank`→`He drank`、`:67`)。(2) 反映先 `CURRENT_SPEC.md:2886` は「Local Rewrite(英語のみ・5 role)…発火条件=slot3 NG・role∈5 role・`lr_used==0`…」。(3) **この決定はZ dialogueをLR対象に含むとも除くとも書いていない**(原文・DECISION_LOG.md:21941,21944とも)。(4) Z narrator(5 role=FULL_STORY)にはこの発動条件が実装済み(§5-4,5-5、実走10件)。Z dialogueは LR 関数自体が呼ばれないため、この決定の適用対象になる経路が無い。

### 7-2. 2026-10-15 ユーザー決定(統一フロー。LRまたはHR)
出典=`DECISION_LOG.md:21542,21596-21599`(原文 `docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md` §2,§5)。
> 3回とも不合格の場合、既存の安全条件に従いLocal RewriteまたはHuman Reviewへ進む。
> 2. **日本語Local Rewrite**：現行の英語用機構を機械的に流用しない。安全な実装が成立していない場合はHuman Reviewへ進める。
> 5. **Dialogue**：複数Voiceの区分・話者帰属・既存Segment構造を維持する。

照合: 「LRまたはHR」は「既存の安全条件に従い」どちらかへ進むと書く。dialogueは「複数Voice/話者帰属/Segment構造の維持」の指示で、LRの要否は述べていない。日本語LRの不適用(Z Std日本語部位)はこの決定で明示承認済み(分類A)。

### 7-3. 2026-10-26 FZ 文脈・感情付きTTS 正式採用(ユーザー原文)
出典=`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md`。
> :30 `- NG → 既存のLocal Rewrite処理へ` / :32 `Local Rewriteで解決できなければ、既存のHuman Review／STOP規則に従う。` / :36 `Local Rewriteも既存の回数上限・安全条件を維持し、無制限な再生成を発生させない。` / :136 `| 3回ともNG | Local Rewrite／Human Review／STOPへ正しく移行 |` / :176 `今回の最重要目的は、Family Zで文脈・感情付きTTSを標準方式とし、2回失敗した場合だけ、10分クールダウン後の3回目に従来方式へ戻すこと。そして、その動作を正式Productionの全経路で保証することです。`

照合: 実装は :176(最重要目的)と §2(総3回・2回目NG後cooldown・3回目に従来方式)を満たし(§5-1,5-2、E-1〜E-6)、**:30・:136 の「Local Rewrite」段は実装されていない**(dialogueに既存LRが無いため)。:32 の「解決できなければHR/STOP」は実装済み。

### 7-4. J-1(Fable判断。ユーザー承認ではない)
- `DESIGN_02.md:6`: 「Fable照合結果(委任文): Claude案とOpusは骨子で一致。M/Rは実装の穴の是正で既存ユーザー承認内容を変えない→全件採用(ユーザー判断事項なし。J-1はLR未配線の事実を完了報告で開示)。」
- `DESIGN_02.md:61`: 「Z dialogueにはLRが未配線(EXISTING_SPEC_CHECK_01 §2、`er003_v1_n3_01_tts_generate.py:319`)。新設せず、3回NG->STOPPED->HR Lock->STOP(原文「Local Rewriteで解決できなければ既存のHuman Review／STOP規則」を満たす)。LR新設は古典作品のセリフをLLMで書換える音声と表示本文の乖離を生む新仕様でありユーザー承認事項。」
- `OPUS_REVIEW_01.md:64-70`: 「LRを新設せず『3回NG→STOPPED→HR Lock→STOP』とする既定が、ユーザー原文に最も忠実です。… ただしユーザーはLRが存在する前提で書いた可能性が高いです。非ブロッキング扱いで埋もれさせず、…完了報告に明示すること。」
- `CLOSEOUT_01.md:25,28`: 「Z dialogueにLocal Rewrite未配線(別承認)」「Z dialogue Local Rewrite新設(新仕様)。いずれも現行の安全側動作で運用可能。」
- `USER_DECISION_REGISTER_01.md:434,444`/`OPEN_ITEMS.md` OPEN-528 Deferred(1): 「Z dialogue Local Rewrite新設(新仕様、現行は3回NG→HR Lock/STOP)」=非blocking・ユーザー判断までは現行維持。

照合結果: J-1の結論は Fable判断とOpus意見であり、ユーザーが承認または不採用とした記録は見つからない(UDR/DECISION_LOGの該当は「判断候補・Deferred」のみ)。

### 7-5. その他のユーザー決定で関係するもの
- 2026-10-12(`DECISION_LOG.md:20716`): 「③原作保持LLM Validator(er061)は不要・中止…④Family Z編集方針=原作のエッセンスを活かし面白さ・自然なStorytelling優先、原作と異なる展開も許容」。Z narrator LRは audio_text_deviation の監査記録のみ(`er063:1668`)で運用されている(実走10件)。
- 2026-09-26 LR承認(`CURRENT_SPEC.md:2176`): LRは Full Story/Comment/Preview/Topic intro/In One Line の5 roleのみ。Heading readout・Key Phraseは明示的非適用(`er020:117-121`)。Dialogue/Voicesを名指しした記述は確認した範囲で無い。

## 8. runtime evidence 有無表

| 項目 | 証拠(実在path) | 区分 |
|---|---|---|
| dialogue ctx 正常経路(Std 10・Adv 11 clip全てmode=ctx) | `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_E-1_run_fzcw_e1_01.json`、`EVIDENCE_01.md` §1,§2 | あり(実TTS/ASR、作品=melos) |
| E-2 強制NG→cooldown 600.001s→従来方式PASS | `RUNTIME_EVIDENCE_E-2_run_fzcw_e2_a2_01.json`/`…_b1b_01.json`、`legacy_prompt_check_01.json` | あり(強制NG=repetition QA gate上書き) |
| E-3 cooldown中kill→再開(重複TTS 0) | `RUNTIME_EVIDENCE_E-3_run_fzcw_e3_a2_01_resume.json` | あり(Stdのみ) |
| E-4 3回強制NG→TERMINAL_NG+HR Lock+rc=2、4回目なし | `RUNTIME_EVIDENCE_E-4_run_fzcw_e4_a2_01.json`/`…_b1b_01.json` | あり。HR queue追記は0(強制NGがASR由来でないため)=ASR由来最終slotのqueue追記は未観測 |
| E-5 1回目NG→kill→再開で2回目ctx即時PASS | `RUNTIME_EVIDENCE_E-5_run_fzcw_e5_a2_01_resume.json` | あり(Stdのみ) |
| E-6 Adv減速後NG→外側ループ継続 | `RUNTIME_EVIDENCE_E-6_run_fzcw_e6_b1b_01.json` | あり(Advのみ) |
| M-3(i)併発(Advでminimal_fallbackが併発し従来方式未到達) | `EVIDENCE_01.md:125` | 未観測(runtime証拠なし) |
| dialogue **LR** | 該当なし(LR未配線)。Z run走査で dialogue `audio_text_deviation`=0(716 entry、重複あり) | 経路なし |
| narrator LR 実走(Adv 9件) | `er026_output/family_z_production_e2e_01/` 配下 `audio_text_deviation` あり: melos/run_e2e_01 b1b part2_c1・part2_c2、melos/run_e2e_02 b1b part3_c1、melos/run_e2e_04 b1b part3_c1、melos/run_kga3_off_z_01 b1b part3_c1、melos/run_kgcpw_z_01 b1b part3_c1、melos/run_kgcpw_z_e5_a2_01 b1b part3_c1、melos/run_kgcpw_z_e5_b1b_01 b1b part3_c1、the_open_window/run_sf_prod_01_preserve_20261023 b1b part3_c12(各 `<level>/audit/tts_generation_results.json`)。LR記録は `er011_output/local_rewrite_recovery/<run>/<level>/local_rewrite_recovery_<clip>.json`。複製run由来の重複の有無は未検証 | あり |
| narrator LR 実走(Std 1件) | `er011_output/local_rewrite_recovery/run_sf_prod_01/a2/local_rewrite_recovery_full_story_part1_c10.json`(the_monkeys_paw、非chunk時代) | あり |
| narrator cooldown 実発生 | Z走査 a2 6件・b1b 3件(`cooldown_occurred`) | あり |
| Std chunk 正常経路 | `docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/EVIDENCE_Z_01.md`(melos part2_c1、134語→76/58語、比1.0597/1.0592) | あり |
| Std chunk のLR・強制NG fallback・exhaust | `EVIDENCE_Z_01.md` §5 | **未取得(offline testのみ)**=runtime証拠なし(未検証) |
| Adv chunk 正常経路 | `docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_01.md` | あり(LR 0・fallback 0) |
| Adv Preview/Comment のLR実走 | なし(Z走査で comment/preview の `audio_text_deviation`=0) | runtime証拠なし(未検証) |
| Z topic_intro のcooldown/LR | なし(cs=False。34 entryで再試行0) | 経路なし |
| 実データ: dialogueが3回STOPPED(legacy時代) | `er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01_preserve_20261023{,_b7}/*/audit/tts_generation_results.json`(`part1_c14`,`part3_c2`) | あり(LRなしでHR行き) |

走査方法: `er026_output/family_z_production_e2e_01/*/*/*/audit/tts_generation_results.json` の `segments`/`key_phrases` を読み取り(read-only)。複数runを合算しており同一clipの重複を含む。

## 9. 発見した不一致・理由不明(分類 A/B/C と影響)

| # | 事項 | 分類 | 重要度 | 品質リスク | 量産単価 | Delivery | 備考 |
|---|---|---|---|---|---|---|---|
| Z-1 | Z dialogueに3回NG後のLR段が無い(ユーザー原文§2・§6の「Local Rewrite」段が空。除外のユーザー承認記録なし。Fable判断J-1のみ) | **C** | 中 | ctx導入後の実データ: E-1 dialogue 21 clip中、3回NGなし。legacy時代の実データはdialogue 3回STOPPED 6件(the_open_window、複数run重複)。LRがあれば救済できたかは未検証 | LR配線の費用は未確認(BUDGET_PLAN_01:23「配線する場合は別見積」) | HR待ちで再生成が止まる(人手待ち)。頻度はctx後で未測定 | 既存OPEN-528 Deferred(1)と重複。ユーザー判断事項(LR新設は新仕様) |
| Z-2 | Z `topic_intro_en`(Std/Adv)がcooldown・LR非適用(5 role承認にTopic introを含む) | **B** | 低 | topic introは短文(34 entryで再試行0)。ただし最終NGで即HR | LR未発火のため0 | 低 | 承認済み仕様との不一致(11-8テストT2相当の不具合候補)。設計メモ`IMPLEMENTATION_DESIGN_02.md:34`の「既存C/Xと同じ扱い」はXについて不正確 |
| Z-3 | M-3(ii): Advでminimal_fallbackが併発すると外側行会計が先に尽き、従来方式(3回目)に到達しないまま STOPPED+HR Lock(`terminal_before_fallback`)。ユーザー原文は「3回目で従来方式」 | **C** | 低〜中 | 稀(未観測) | 0 | HR待ち | OPEN-528 Deferred(2)。(i)=行会計をpolicy基準にする案は既存A2予算規則の変更 |
| Z-4 | narrator の600秒cooldownは単一 `time.sleep(600)` でSTOP sentinel確認なし(dialogue ctxは5秒刻みで確認) | **C(仕様記録なし)** | 低 | なし | なし | cooldown中にSTOPが出ても10分後に次TTSが走る可能性。SDK入口guard(委任_12A)が別に効くかは本調査で未確認 | `EXISTING_SPEC_CHECK_01.md §3 行7`が同事実を記載。既存OPEN未確認 |
| Z-5 | Adv narrator LR再TTSが PD06 を転送せず標準ENGLISH_STYLE_PREFIXで再TTS(Std narratorは minimal) | **C(既存OPEN-274)** | 低〜中 | LR後の音声Styleが通常と異なる | 0 | なし | 既存OPEN-274(未承認候補)・CURRENT_SPEC:2886が「LR後v1=標準Prompt」と記述。新規OPEN不要 |
| Z-6 | 3NGにSecondary障害を含まない条件は未実装 | **C(既存OPEN-371)** | 低 | Secondary障害時もNGとして数える | 0 | HR増の可能性 | 既存OPEN-371 |
| Z-7 | Std chunk のLR/強制NG fallback/exhaust の実run証拠なし | runtime証拠なし(未検証) | 低 | offline testのみ(`er063_z_std_chunk_test_01.py` R7) | — | — | 判断不要。必要なら後続でevidence取得 |

## 10. 古いルールの残存・矛盾(Grep/Read確認)

1. `er122_fz_ctx_policy_01.py:16`・`CURRENT_SPEC.md:1650`・`DESIGN_02.md:61`: 「Z dialogueにLR未配線」は現コードと一致(残存矛盾なし)。
2. `er060_output/melos_production_e2e_01/CONFLICT_RESOLUTION_01.md:24`(S5): 「Dialogue clipのASR連続NG…ASR/Connected Speech/Local Rewriteが連続NGになりうる(Local Rewrite上限到達でSTOP)」と書くが、dialogue関数にLR呼出は無い(古い/不正確な記述。設計メモであり実装には影響しない)。
3. `docs/pm/design/2026-10-11_FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01_XZ_MAPPING_01.md:153`: 「Z未配線…Connected Speech 5roleはresolve_narrative_roleがfull_story_part1/2/3完全一致のためZ 8 voice-clipは対象外(known_gap)」は、その後 `_FAMILY_Z_STORY_CLIP_PATTERN`(`er020:122,152-156`)追加で narrator 側は解消済み(旧記述)。
4. `er019_family_x_audio_production_runner_01.py:1212-1213` のコメント「統一フロー『TTS①②③、3回NGでLR/HR』に揃える」は KP解説でLR呼出なし(roleがNone)。「LR/HR」はLRまたはHRの意で、LRが無い部位はHRへ進む。
5. `er003_v1_n3_01_tts_generate.py:319`: 「A2外側ループ内にはLR配線が無く」は減速後NGの外側ループを指し、`generate_a2_segment_with_slowdown`内側(crosslevel)のLRとは別。現コードと一致。
6. 撤去・残置: 旧「両ASR合意」LR発動条件=コード・呼出元から撤去済み(`er020:739-760` docstring、CURRENT_SPEC:2886)。Grepで残存を確認する範囲は本書の対象外(X担当の共通核記述に委ねる)。Z側でLR発動条件に関する旧規則の残存は確認できなかった。

## 11. 所見(事実ではない)

- 所見1: 実装履歴(`er012_b`が2026-09-08作成、LR/cooldown配線が2026-09-26で`er012_b`を触っていない)からは、dialogueが未配線なのは配線対象の列挙に入らなかった結果である可能性がある。ただし設計・承認記録に理由は無く、「意図的な除外」と「配線漏れ」のどちらかは記録からは確定できない(確認方法=ユーザーまたは2026-09-26当時の判断者への確認のみ)。
- 所見2: J-1の理由「音声と表示本文の乖離」は、Z narrator LRにも同じく当てはまる(`audio_text_deviation`のみ記録、表示本文は不変)。narrator LRはユーザー承認下で運用済みなので、dialogueだけが乖離を理由に除外される根拠としては弱い可能性がある。一方、dialogueの書換えは話者の台詞自体を変える点で性質が異なるという見方もあり、判断はユーザー事項。
- 所見3: dialogueへLRを配線する場合は、既存のcs=Trueで暗黙にON/OFFされる仕組み(cooldownもLRも一括)に載せると、ctx方式の自前cooldownと二重になる。ctx policyのn=3の後に1回だけLR再TTS(従来style・max_attempts=1・既存lr_used==0・累積15回guard維持)を付ける設計が `DESIGN_01.md:122` に既にある。
- 所見4: Z topic_intro_en は clip_id を `topic_intro` にするか、`resolve_narrative_role` に `topic_intro_en` を追加すれば適用できる見込み(共通核の変更を伴うためX担当との調整が必要)。
- 所見5: runtime evidence の強制NGは repetition QA gate 上書きで、HR queue追記(ASR由来最終slot)を通らない。ASR由来のn=3 NG時にHR queueへ正しく1行入るかは、narrator側の実績(`HUMAN_REVIEW_QUEUE_DUPLICATE_SUPPRESSED` 6件)から共通機構の動作は推定できるが、dialogue ctx経路では未観測。

## 12. 参照文書・一覧外Read

主な参照: `CURRENT_SPEC.md:1644-1654,2176,2873,2885-2886`、`DECISION_LOG.md:20716,21542,21596-21599,21941-21944`、`OPEN_ITEMS.md`(OPEN-260/274/371/528/511/516)、`docs/pm/USER_DECISION_REGISTER_01.md:31,286,433-444`、`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/{EXISTING_SPEC_CHECK_01,DESIGN_01,DESIGN_02,OPUS_REVIEW_01,CLOSEOUT_01,OPEN_TRACKING_01,OPEN_TRACKING_02,SPEC_LEDGER_01,EVIDENCE_01}.md`、`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/{EVIDENCE_Z_01,DESIGN_Z_01}.md`、`docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_01.md`、`docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md:78-92`(§8 E-1 Family別配線状況表: 「Dialogue内側はLRなし(voice body)」)、`er058_output/unified_all_roles_production_wiring_01/DESIGN_01.md:128`、`er060_output/melos_production_e2e_01/{CONFLICT_RESOLUTION_01,IMPLEMENTATION_DESIGN_02}.md`、`TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01_REPORT.md`、`docs/pm/design/2026-10-11_FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01_XZ_MAPPING_01.md`。
一覧外Read(事前指定Read一覧にないもの): `er003_v1_crosslevel_audio_02_common.py`・`er003_v1_sing01_news_tail_fix.py`・`er003_v1_sing01_voice01_generate.py`・`er003_v1_repro01_main_generate.py`・`er006_secondary_asr_01.py`・`er078_asr_unified_attempt_ctx_01.py`・`er019_family_x_audio_production_runner_01.py:1205`(共通核の呼出先確認)、`TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01_REPORT.md`、`er060_output/…`、`er058_output/…DESIGN_01.md`、`docs/pm/design/2026-10-11_…XZ_MAPPING_01.md`、`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`、`er026_output/family_z_production_e2e_01/*/*/*/audit/tts_generation_results.json`(走査のみ)、`er011_output/attempt_history.jsonl`(件数集計のみ)。
