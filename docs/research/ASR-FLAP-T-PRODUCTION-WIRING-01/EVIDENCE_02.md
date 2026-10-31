# ASR-FLAP-T-PRODUCTION-WIRING-01 委任_02 EVIDENCE_02(実装・検証。2026-10-31)

ユーザー原文=`docs/pm/delegation_log/2026-10-31_ASR-FLAP-T-PRODUCTION-WIRING-01_USER.md`(§2仕様・§4配線・§5受入)。設計=`DESIGN_01.md`+Opus条件Aレビュー(Fable採用済み)。実装worktree=origin/main(`445ce77bc`+02A `dea4439a4`)から新規作成。範囲(11-8)=承認済みFlap-T救済の正式配線と回帰・検証のみ(救済面・閾値・方式の拡大、既存同音救済/CS救済/Primary・Secondary/最終ANDゲートの変更は0)。PRODUCTION_WIREDの判定はFable。

## 1. 実装(新規3ファイル+既存の最小加算)
| 種別 | file | 内容 |
|---|---|---|
| 新規 | `er139_flapt_equivalence_01.py` | 純規則(Trial 36 case移植+M1 tokenizer)・`FlapEq`・Voice適用ゲート`decide()`・CMU sha固定・Voice表loader・`reuse_still_valid`。flag `FLAP_T_EQUIVALENCE_ENABLED=True`(literal)。 |
| 新規 | `er139_flapt_provenance_01.py` | 出自台帳(sha256(wav)→voice/model/source/transforms)・記録点API・`judging_wav`(memo+sidecar)・`adapter_context`/`rejudge_entry_context` decorator・hydrate |
| 新規 | `er139_flapt_voice_table_01.json` | 02A作成(20行、confirmed 19/Puck\|pro=false)。本委任では無変更 |
| 新規 | `er139_flapt_equivalence_01_test_01.py` | 72 test(純規則・Voice表・台帳・adapter実経路・memo/audit形・Store guard/hydrate・AST inventory・A/B/C no-op) |
| 既存 | `er109_xz_scope_01.py` | `decision()`に第3層分岐(er109が`equivalent=False`のときだけ`er139.decide`)・`W_FLAPT`を`ORTHO_WARNING_LABELS`へ・`flapt_contributed()`・`token_regex()`窓口(er109純関数のimport隔離維持) |
| 既存 | `er006_batch_tts_wiring_01.py:_record` | SUCCESS分岐で`note_tts_sent`(cost logger未install即returnより前) |
| 既存 | `er002_gemini_client.py` / `er003_b1_p7a_audio.py` / `er033_tts_flash_lite_backend_wiring_01.py` | Standard call_fn成功直後の`_flapt_note`(空音声=失敗では記録しない・cost logger非依存) |
| 既存 | `er002_common.write_wav_float` | 末尾で`bind_pending`(mono 24kHzのみ・単一用途) |
| 既存 | `er008_a2_postprocess_slowdown_01.apply_a2_slowdown` | 子wavへ親の出自+transform(Std 6%/Z Adv 1.06x)を引継ぐ唯一の点 |
| 既存 | `er006_secondary_asr_01.py` | `evaluate_attempt_with_cascade_detail`に`@adapter_context`(EN・X/Y/Z scope内のみ`judging_wav`)・`flapt_declined`の監査転記(該当時のみ) |
| 既存 | `er078_asr_unified_judge_01.py` | attempt auditに`tts_provenance`(解決できたときのみ) |
| 既存 | `er078_reuse_value_guard_01.py` | Flap-T寄与音声のStore再利用ガード(scope外/flag OFF/表sha・CMU sha変更/未確認/audit不読=block) |
| 既存 | `er019_family_x_validation_inheritance_01.py` / `er104_kp_vote_reuse_01.py` / `er109_hr_lock_rejudge_01.py` | 保存entry/attemptの記録(sha/voice/model/tts_provenance)からhydrateして再判定(出自なし=適用外) |
| 既存test | `er109_xz_isolation_01_test_01.py` | `PRODUCTION_SCOPE_IMPORTERS`にer139の2 moduleを追加(scope読取のみ・入口呼出なし。Flap層追加分のみ) |

## 2. Opus必須修正・推奨・Fable追加の反映
| # | 条件 | 実装/固定test(`er139_flapt_equivalence_01_test_01.py`) |
|---|---|---|
| 1 | 出自記録点=Batch `_record()` SUCCESS(cost logger判定より前)。静的inventory | `test_batch_record_success_notes_even_without_cost_logger`、`test_er006_batch_call_fn_end_to_end_with_z_voice_override`、`test_er033_flash_lite_batch_call_fn_end_to_end`、`StaticInventory.test_note_tts_sent_inventory_exactly_the_four_record_points`、`test_every_audio_generate_content_and_batches_create_callsite_reaches_a_record_point`(新規の呼出点が増えたらFAIL)、`test_batch_callsites_reach_record_via__record_success_branch`、`test_submit_batch_multi_not_called_from_production`(Productionから未呼出を固定) |
| 2 | Standardはcall_fn factory成功直後(cost logger非依存) | `test_standard_factories_note_after_success_without_cost_logger`、`test_standard_failure_does_not_note`、`test_standard_record_after_empty_check_and_independent_of_cost_logger` |
| 3 | 不発火の可視化 | `AdapterIntegration.test_not_rescued_without_provenance_logs_provenance_missing`/`test_unconfirmed_and_unknown_voice_not_rescued`(`asr_judgement.flapt_declined`)、`test_sidecar_coverage_every_en_judgement_resolved`、`test_normal_pass_and_ng_have_no_flapt_keys`(通常行はキー無し) |
| 4a | `judging_wav`内memo(二重呼出でも警告が消えない) | `MemoAndAudit.test_decide_memo_within_judging_wav...`、`test_decision_called_twice_same_result_in_xz`、`AdapterIntegration.test_kp_vote_warning_survives_double_decision_calls` |
| 4b | `FlapEq.audit()`はdict・version/rules/spans・`ukus_pairs`なし | `test_flapeq_audit_shape_for_ukus_contributed_guard` |
| 4c | CMU sha不一致=救済せずrun警告・model_id完全一致・親flag rollbackでFlapも停止 | `test_cmu_sha_mismatch_declines_and_warns`、`VoiceTable.test_exact_key_match_only`、`test_flag_off_and_scope_outside_are_conventional_ng`(親flag) |
| 1-d | 子登録は`apply_a2_slowdown`内1点・pct条件つき | `test_apply_a2_slowdown_registers_child_for_6pct_and_z_speedup`、`test_bind_point_is_write_wav_float_only_and_child_point_is_apply_a2_slowdown_only`、`VoiceTable.test_speed_conditions`、`test_speed_conditions_through_adapter` |
| 1-e | pendingはthread-local単一slot・後着上書き・mono 24kHz書込みのみ | `test_pending_consumed_once_and_overwritten_by_latest`、`test_stereo_and_non_24k_writes_do_not_bind_or_consume`、`test_pending_expires` |
| 1-f | 共有moduleの記録点は先頭で`_active()` | `test_hook_first_statement_returns_when_inactive`、`AbcNoop.*` |
| 1-g | er019 hydrate(Store entry)+`provenance_source`明記 | `test_rejudge_with_current_judge_hydrates_from_store_entry_and_rescues`、audit `flapt.provenance_source` |
| 追加 | 数詞・否定語対は非救済 | `test_number_and_negation_words_never_pair_rescue` |
| Fable追加 | attempt audit `tts_provenance`+retry/resume/HR rejudgeでhydrate | 実run(下記5節)で`tts_provenance`保存を確認、`test_rejudge_with_attempt_audit_provenance_known_transforms`、`test_hr_rejudge_entry_carries_voice_model`、`test_kp_vote_reuse_ok_is_wrapped_and_hydrates_store_entry` |
| 追加 | 3-2項3(`vote_check_from_audit`の包み)は削除 | 実装なし(KP票はadapter内の同一contextで評価される) |

## 3. test結果
- 新規 `er139_flapt_equivalence_01_test_01.py`: **72 passed**(subtests 89)。Trial 34 case(P/N/X/U 全件)+Trial protoとのparity(M1差分=数字tokenのみ)。
- 既存回帰(er006/er078/er103/er104/er109/er127/er011 Repetition QA/er019 inheritance/er020 計67 file)を**変更前(origin/main + 未参照の新file)と変更後で同一shard条件**で実行し、失敗集合を比較: 変更前26 failed→変更後24 failed(+shard外のer078 static audit単独FAIL=変更前と同一)。**変更後の失敗集合は変更前の部分集合=新規失敗0**。変更前の2件差は(i)er078 static audit(後は単独実行)と(ii)変更前取得中に自分の未追跡er139 fileが出現した汚染で一時FAILした`importers_of_scope_module_are_a_fixed_production_list`(list更新後PASS)。内訳は`ev02/regression_summary.txt`。環境起因の既存失敗(例: `er006_asr_provider_routing_01_test` 5件、`er011_open121_repetition_qa_production_wiring_01_test` 5件、`er109_wiring_golden_test_01` 3件[OPEN-501]、`er109_xz_isolation_01_test_01::test_f_existing_static_audit_still_zero_new_asr_calls`、`er078_asr_unified_wiring_static_audit_01::test_asr_call_inventory_matches_allowlist`[`rejudge_with_current_judge`のclassify呼出数は変更前後とも5=本変更で不変、allowlist=2の既存乖離])は変更前から失敗しており、差分なし。※委任文の「OPEN-501既存失敗4件」より本環境の既存失敗は多いが、変更前後で集合同一であることを確認(変更前をclean worktreeで取得)。
- 変更前の取得: 本worktreeを編集する前(origin/main HEAD)に4 shard並列実行。変更前取得中に新規untracked file(`er139_*.py`)が出現したため`test_importers_of_scope_module_are_a_fixed_production_list`が一時的に変更前FAILと記録されたが、list更新後のafterではPASS(=自分起因・解消済み)。

## 4. 保存ASR記録・Voice probe転写のreplay(API 0。`tools/flapt_replay_prod_02.py`、結果=`ev02/replay_prod_02.json`・`replay_prod_02_line_diff_S1_vs_S0.txt`)
母集団: 保存results 9,715行+HR queue 554行(692 results file)→**11,181転写**(OpenAI/Azure)。各転写を『既存判定(classify_asr_match+同音救済)→`er109_xz_scope_01.decision`(er109→Flap-T)』で行単位判定。
| 条件 | 変更前(S0=Flap-T flag OFF)との行単位差分 |
|---|---|
| S2 出自なし | **0行** |
| S3 未確認Voice(Puck\|pro) | **0行** |
| S1 確認済みVoice(Aoede\|fl) | **71行**。全て`NG→ORTHO:FLAP_T_EQUIVALENT`で、語対は **bertie→birdie 61行(Z The Open Window)・latter→ladder 10行(X⑨)** の2種のみ。非flap行(PASS 8,155/NG 2,883/er109 ORTHO 72)は完全一致 |
- Voice probe転写(`voice_probe_02/03.json`、writer 38転写・観測7項目): **writer→rider型は救済0**(NG 5・既存PASS 33、`ORTHO:FLAP_T_EQUIVALENT`なし)。d綴り正例(latter 33・atom 35・coating 32・betting 13・metal 1)は確認済みVoice条件で救済、metal/betting/waitingのNG残(18)はd綴り以外(別語・非flap転写)でNG維持。
- 実際に起きた偽NGの保存attemptを正式再判定入口(`rejudge_with_current_judge`、出自はattempt記録のsha/voice/modelからhydrate)で再判定(`tools/flapt_attempt_replay_02.py`、`ev02/attempt_replay_02.json`):
  - FX4⑨ vocab_extra_3_en(Aoede\|fl, `Ladder`): **ON=PASS_WITH_WARNING[FLAP_T_EQUIVALENT]**。出自なし/未確認Voice(Puck\|pro)/flag OFF/scope外(A/B/C)はいずれも**NG_BOTH**(従来どおり)。
  - FZ The Open Window `Bertie→Birdie`(Zephyr\|pro。**独立probe `voice_probe_03.json`で確認済み**): attempt1/3/4=PASS_WITH_WARNING、attempt2は別条件でNG(Flap対象外の差分)。出自なし/Puck\|pro/flag OFF/scope外はNG。

## 5. Production runtime発火証拠(Production既定BATCHモード・API実run。`TTS_EXECUTION_MODE`未設定=BATCH既定。Standardモード実runは証拠にしていない)
複製run(新規out dir・既存記事/runは無変更・本文/記事のLLM再生成なし)で最小本文(`latter`含む)を実行。各runの前に`stop_scope_check_01.py`(rc=0: `ev02/stop_check_*.json`)。起動間隔≥150秒・300秒窓≤2回を遵守。
| run | 入口(正式) | clip | batches.create(model_id/voice/結果) | 台帳・束縛 | sidecar(`flapt_provenance_coverage.jsonl`) | audit `tts_provenance` |
|---|---|---|---|---|---|---|
| X Adv(b1b) | **正式runner CLI** `er019_family_x_audio_production_runner_01.py --stage tts --level b1b --only-segments in_one_line --budget-jpy 5`(`meta_waddle_world`複製run、`in_one_line`本文のみ`latter`入り文に置換) | `in_one_line`(Aoede) | `gemini-3.8-flash-lite-tts`/`Aoede`/SUCCESS/BATCH(raw_usage_log: `provider=gemini_batch, api=batches.create`) | wav sha `5ecca5f6…`へ束縛 | generation: **1/1解決**(Aoede\|fl, `sdk_boundary_batch`, table=confirmed)。同runで継承再判定(rejudge)18/21解決、3件(kp1-3_english)は当時hydrate未接続の旧Store entry→**本委任で`er104_kp_vote_reuse_01.kp_vote_reuse_ok`にhydrate接続を追加**(unit固定) | `{voice:Aoede, model_id:gemini-3.8-flash-lite-tts, path:fl, source:sdk_boundary_batch, transforms:[]}` |
| Z Adv(b1b) | Z正式TTS段 `er063_family_z_audio_01.run_tts_stage`(runner `stage_tts`が呼ぶ関数、`family_scope("Z")`)+`real_generators()`(`tools/flapt_z_runtime_evidence_02.py`。※Z runner CLIは全記事状態を要するため複製runの最小planで同関数を直接実行) | `full_story_part1_c1` narrator(Fenrir, `voice_override`) / `full_story_part1_c2` dialogue(Algieba) | narrator: `gemini-3.8-flash-lite-tts`/**Fenrir**(Aoede既定ではなく実送信値)/SUCCESS/BATCH、dialogue: `gemini-2.5-pro-preview-tts`/Algieba/SUCCESS/BATCH | narrator sha`10afae86…`、dialogue原音→**1.06x高速化後sha`8e2cc36a…`へ子登録(transform `slowdown_pct=-5.6604`)** | generation **3/3解決**(Fenrir\|fl; Algieba\|pro[原音]; Algieba\|pro[+atempo -5.66], table=confirmed)※このrunは`phase/tag`欄追加前のcodeで実行(判定・解決は同一) | narrator `{Fenrir, fl}`、dialogue `{Algieba, gemini-2.5-pro-preview-tts, pro, transforms:[{atempo,-5.6604}]}` |
| Z Std(a2) | 同上(`level=a2`) | `full_story_part1_c1` narrator(Aoede) | `gemini-3.8-flash-lite-tts`/Aoede/SUCCESS/BATCH | 原音sha`ec79b363…`→**6%減速後sha`2bff3339…`へ子登録(transform `slowdown_pct=6.0`)** | **2/2解決**(phase=generation, tag=full_story_part1_c1) | `{Aoede, fl, transforms:[{atempo,6.0}]}` |
- **sidecarカバー率(新規生成音声のEN判定)=6/6=100%**(X 1、Z Adv 3、Z Std 2)。voice/model/sha/source/transformsがBatch実送信の記録(`raw_usage_log.jsonl`の`batches.create` model_id/voice)と一致。各runの全判定はPASS(Flap対なし=不発火記録なし・誤救済0)。
- 費用(raw_usage_log集計): X ¥0.128、Z Adv ¥0.294、Z Std ¥0.062 = **約¥0.49**(Azure STTの按分は¥0.1未満の見込みで未計上)。個別Cap ¥15に対し3.3%。
- **注意(正直な限界)**: 実run中に「実際のFlap-T転写(latter→Ladder等)」は自然発生しなかった(再生成の反復は費用規律上しない)。**発火(救済)そのもの**は§4の保存attempt正式再判定+§2のadapter実経路test(実wav束縛→実adapter)で、**到達性(実送信→台帳→束縛→判定context→sidecar)**は本節の実Batch runで証拠化した(DESIGN 9節の分担どおり)。

## 6. Family×Level別 到達性(静的inventory+replay+実run)
| Family | Level | EN judge到達(runner→leaf→adapter) | 実Voice/model(表) | 実run | Status |
|---|---|---|---|---|---|
| X | Std(a2) | `generate_family_x_a2_segments`(`er019_family_x_audio_production_runner_01.py:2037` `family_scope("X")`)→共有leaf(n3/crosslevel/repro01)→adapter。6%減速子登録は`apply_a2_slowdown`1点 | Aoede\|fl, Charon\|fl=confirmed | X Std専用runは未実施(共有leafのStd+6%減速はZ Std実runで実証、unitでX scope) | 配線済み・共有leaf実run証拠(X Std runner自体の実runなし) |
| X | Adv(b1b) | `generate_family_x_b1_segments`(`:1663` `family_scope("X")`)→leaf→adapter | Aoede\|fl, Charon\|fl=confirmed | **実run済み**(in_one_line, BATCH) | 配線済み・実run証拠あり |
| Y | Std/Adv | `generate_y_a2_segments`(`er121_family_y_audio_01.py:645`)/`generate_y_b1_segments`(`:555`) `family_scope("Y")`→同じ共有leaf→adapter | Aoede/Algieba/Charon/Schedar/Zephyr/Puck\|fl=confirmed | Y専用runなし(scope "Y"はunit `test_all_x_y_z_scopes_rescue`、共有leafはX/Z runで実証) | 配線済み(Y runner実runなし) |
| Z | Std(a2) | `run_tts_stage`(`er063_family_z_audio_01.py:1630` `family_scope("Z")`)→narrator `generate_a2_segment_with_slowdown`/dialogue(減速なし)→adapter | fl{Aoede,Charon,Fenrir}, pro{Algieba,Schedar,Zephyr,Charon,Aoede,Fenrir,Orus,Kore,Erinome,Sulafat,Leda,Iapetus}=confirmed、Puck\|pro=false | **実run済み**(narrator Aoede 6%) | 配線済み・実run証拠あり |
| Z | Adv(b1b) | 同上、narrator `generate_news_narration_wide_margin`/dialogue `generate_with_a2_slowdown_outer_loop`(1.06x) | 同上。1.06xは`fast106_confirmed`のVoiceのみ(Aoede/Schedar/Zephyr\|fl、Fenrir\|fl、Orus/Kore\|pro) | **実run済み**(narrator Fenrir[voice_override]、dialogue Algieba\|pro+1.06x) | 配線済み・実run証拠あり |
- 「適用外」の区別: **新規生成音声**=出自が台帳/attempt auditに残り、retry/resume/HR rejudgeでhydrate可能。**既存の保存音声で出自(sha/voice/model/tts_provenance)がないもの**は承認仕様どおりfail-closed(適用外)。保存entryにvoice/modelがあるもの(Store entry、attempt JSON)はhydrate(変換履歴不明=Std[a2]は高速化がないため確認済み扱い、Adv[b1b]は`fast106_confirmed`未確認Voiceなら適用外)。

## 7. retry / fallback / regeneration / resume / 既存Gate(Flapは各attempt判定に『合格を1つ増やす』のみ)
- retry/fallback/LR: 救済はそのattemptを`verified`にして外側ループを終える=試行回数・上限・180秒待機・LR・HR条件は不変(`er127`等は無変更、test: 既存の`er127_*`/`er020_*`/`er011 Repetition QA`は変更前後で失敗集合同一)。Local Rewrite後の再TTSは書換え後文をcanonicalに同じ規則で再judge(出自は再TTSの実送信値)。
- 再生成: attempt auditに`tts_provenance`が残るので、再判定・継承でも同じ出自を使う。減速/高速化後の再検証(`_post_slowdown_unified_judge`)は子wavの出自で判定(Z Std/Adv実runで確認)。
- resume: 判定済みattemptは再judgeされない。保存音声の再judge(`rejudge_with_current_judge`、`kp_vote_reuse_ok`、HR rejudge)は記録からhydrate、出自なしは従来どおりNG。
- 最終ANDゲート: 判定objectのversionをer139専用にして`explain_protected`は`decision_not_equivalent_or_version_mismatch`でFalse=値DIFF/否定差を解除しない。`latter 13`↔`ladder 30`、`not the latter`↔`the ladder`はNG_PROTECTED/NG(`test_value_and_negation_diff_never_unlocked_by_flap`)。
- 既存同音救済との整合: er109が先、Flapは`equivalent=False`時のみ(S0とS1の非flap行が完全一致=§4)。CS層は語末脱落型で別経路。

## 8. 誤救済・未解決
- 誤救済: replay 11,181転写+Voice probe転写で**誤救済0**(救済71行は全てbertie→birdie/latter→ladder)。writer/rider・title/tidal・数字付き・未確認Voice・出自なし・scope外・flag OFFは全てNG維持。
- 未解決/残(分類):
  1. 実run中にFlap転写の自然発生なし(§5注意)= 実害なし(発火は保存attempt再判定とadapter実経路testで確認)。
  2. Y runner・X Std runnerの専用実runは未実施(共有leaf+scope unit+X Adv/Z Std/Z Adv実runで到達を実証)= 実害なし。Fable判断で追加実runが必要なら次委任(約¥0.3/clip)。
  3. `Puck|pro`はconfirmed=false(02A、INDETERMINATE)= 仕様どおり適用外。
  4. 変更前から存在する回帰失敗(§3)は不変・本変更と無関係(OPEN-501等の既存管理)= 実害なし。

## 9. 量産単価・実費
- 量産単価影響 **+0円**(量産経路に新ASR/TTS/LLM呼出なし。CMU辞書はローカル、台帳は処理内メモリ、sidecarはローカルJSONL)。
- 本委任のAPI実費: 約¥0.49(Cap ¥15)。02A probeは別費用(約¥16.7)。
