# IMPLEMENTATION_01 — TTS Retry/Fallback/LR 統一3回構成フロー(X/Y/Z)実装記録(委任_02)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02 / 2026-10-26 / API 0・費用0円。到達上限Status=IMPLEMENTED(offline test PASS)。runtime evidenceは委任_03、PRODUCTION_WIRED判定はFable。
設計は`DESIGN_01.md`(骨格)+`DESIGN_02.md`(Opus M-1〜M-11・R-1〜R-7の反映と実装確定事項I-1〜I-8)。撤去結果は`REMOVAL_RESULT_01.md`。

## 1. 何を実装したか(ユーザー承認2026-10-26の仕様)
X/Y/Z run scope内(`er109_xz_scope_01.current_scope() in {X,Y,Z}`)の正式経路で、TTSを「1ブロック=①②=呼出元のStyle→②NG後に180秒待機→③=Fallback Style」に統一した。LR(Local Rewrite)ありの部位は③NG後にLRを1回行い、書換え後の文で**同じ3回ブロックを1回**(最大TTS6回・待機2回)。LRなし部位(JA・Z会話・KP解説)は3回、KP英語は4回(前段2+ENGLISH_LOCK段2、待機は③直前に1回)。技術エラーの即時再試行(F-Tech)は別枠として従来のまま。
- 共通核: `er127_tts_block_policy_01.py`(`unified_flow_active()`=唯一の読取関数、9 policy表、`cooldown_core`[180秒を1箇所で定義・5秒刻みSTOP確認・resume残時間]、`BlockRun.step/done/finish`、`BlockProgress`[segment単位の永続state]、`lr_recover`、`register_terminal_hr`、`TtsBlockStopError(BaseException)`)。
- leaf adapter(scope内分岐のみ追加。scope外は従来コード=byte同一): L1 `voice01.generate_charon_english`、L2 `news_tail_fix.generate_news_narration_wide_margin`、L3 `crosslevel.generate_english_segment_with_fallback`、L4 `n3_tts.generate_a2_segment_with_slowdown`(減速は各attempt内=案A)、L5 KP英語解説 `er019.generate_key_phrase_explanation_en_verified`→`_kp_explanation_unified`、L6 KP英語phrase(`repro01`/`er019_kp_en_k2_store`/`er063._kp_en_two_stage`)、L7 JA(`n3 generate_a2_japanese_with_fallback`・`voice01.generate_charon_japanese`)、L8 Z会話legacy(`er012_b.generate_voice_body_wide_margin`。ctx方式は`er122`が同じ`cooldown_core`を使用)。
- call site: X(KP解説L5)・Z(`_kp_en_two_stage`のstage_kwargs・終端HR、clipループでZ STOP sentinelを`register_stop_check`)・Y(`generate_y_b1/a2_segments`でY STOP sentinelを`register_stop_check`。衝突確認はRESULT_PACKET参照)。
- 追加修正: OPEN-312(旧L2のLR再TTSがstyle_prefix_overrideを脱落)、OPEN-376(LR再入・無限再帰)、D11 `topic_intro_en`のTOPIC_INTRO役割(scope内限定)、Master Audio Store manifestの保存直前reload-merge+原子書込(Opus M-7)。

## 2. policy表(`er127.PROFILES`)
| policy | 1ブロックTTS | 待機位置 | LR | 最大TTS | 最大待機 | ③のStyle |
|---|---|---|---|---|---|---|
| EN_LR_STD / EN_LR_ADV | 3 | ③前 | ○(③NG後・1回) | 6 | 2 | Fallback(minimal)+Secondary必須 |
| JA_STD | 3 | ③前 | × | 3 | 1 | JA minimal |
| KP_EN | 4 | ENGLISH_LOCK段の最初の前 | × | 4 | 1 | ENGLISH_LOCK |
| KP_EXPL | 3 | ③前 | × | 3 | 1 | minimal+Secondary必須 |
| Z_DLG_CTX / Z_DLG_LEGACY | 3 | ③前 | ×(従来方式) | 3 | 1 | 従来Dialogue Style |
| SHELL_EN | 現行維持(表外・同一Style3回・LRなし・待機なし) | — | × | 3 | 0 | — |
| NO_TTS | 0 | — | — | 0 | 0 | — |
49行の対応(`ROW_MAPPING_01.json`)は`er127_tts_block_policy_01_test_01.MapTests`で機械照合(49行、LR対象24行)。

## 3. Gate契約(M-5。Gate規則自体は無変更)
③採用音声は、Adv(L1/L2)で`instruction_type="minimal_fallback"`・top-level`style_prefix`=実際に送ったminimal文字列・`fallback_used=True`、Std(L3/L4)で`fallback_used=True`、LR採用は`local_rewrite_recovery`。X M3 Gate(`ADV_MINIMAL_FALLBACK`/`ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED`/`STD_FALLBACK_USED_OR_UNKNOWN`/`LOCAL_REWRITE_RECOVERY`)がこれを検知することを`GateContractTests`で固定(Gate緩和なし)。Voiceは全attempt同一(Adv L1=Charon、M-10)。Gate緩和の要否はHR待ち増の実測(R-7)後にユーザー判断。

## 4. STOP/resume契約
- STOP: `TtsBlockStopError(BaseException)`は`except Exception`で握られない。待機は5秒ごと、attempt開始前にも`run_stop_check`(登録済みrunner stop + 絶対path`er026_output/family_z_production_e2e_01/STOP_ALL`)。STOP時はguardにSTOPPED結果を保存せず(`record_outcome`なし)IN_PROGRESSのまま残る。
- resume: `BlockProgress`(`<level_dir>/audit/tts_block_progress/<segment_id>.json`、key=segment+元原稿sha+Style/backend/policy指紋。深さ0/1は同一file共有)。TTS呼出**前**にn_startedを永続化。再開時は消費済みattemptを再生成せずstub行として会計し、残り待機時間だけ払う。LR書換え本文も保存(再開時にLR LLMを再実行しない)。新規サイクル=key不一致/DONE/6時間超のIN_PROGRESS/Lockの`REGENERATE_APPROVED`/verified済みattempt有り。
- 終端NG1件=HRQ1行(`register_terminal_hr`、重複は既存`is_duplicate_queue_entry`)。技術STOP(`TECHNICAL_STOP_STATES`)はLR/HRに入れない。

## 5. Trial/toolへの影響(Opus R-4)
scope(X/Y/Z)を被せて実生成するTrial/tool(er113_fx_paragraph_chunk_trial_01・er114_fz_narration_chunk_trial_02・er118_fz_*_trial・er019_family_x_clobber_restore_03・er019_family_x_validation_inheritance_01・er121_e1_slowed_asr_recheck_01等)は、scope内で実leafを通る場合**新flow(180秒・3回ブロック・LR block)になる**。API 0のoffline testは`er127.RUNTIME`のclock/sleep(`er127_test_fakes_01.FakeClock`)を置換して実sleepしない。Productionにenv/hook迂回口はない(`unified_flow_active`は引数なし・env非参照、静的testで固定)。再実行する場合は新flowの待機(最大2×180秒/segment)を見込むこと。

## 6. 委任_03(runtime evidence)への引継ぎ
- evidence注入はdriver側monkeypatchのみ(Opus M-8)。Production moduleにhook/envを追加していない。`injected_override_count`のordinal別記録はdriver側で行う。
- Opus 4-c: 追加の実run 2本(合計約10円、既存cap約210円の範囲)=(a)LRありpartで③NG→LR block ①'②'③' の6TTS・待機2回、(b)減速後NG→LRの案A確認。R-5(LR block内kill→resume実走)は任意、R-7(Adv③がGate対象になることのHR待ち増の数値化)は委任_03で報告。
- clip単価guard見積り(Opus R-6): Z`E2E_TTS_CLIP_EST_JPY`・Y`TTS_CLIP_EST_JPY`を1.0→2.0円へ更新(最悪clip=6TTS+ASR+LR LLM)。費用上限(Cap)自体は不変。
- 実run前に必ず`tools/stop_scope_check_01.py`を実行(rc=3なら新規API呼出なし)。

## 7. 既知の注意
- `ER-011`の累積上限(TTS15/ASR60)・Review Lock・RESTART_STORM/RUN_LOCK・予算guard・Assemble前Gateは不変。LRあり部位は1回のgenerateで最大6TTS(15以内)。
- scope外(A/B/C)の既知欠陥(OPEN-376: cs=Trueで全NGのとき無限再帰)は**据置**(Legacy凍結)。goldenの`KNOWN_LEGACY_DEFECT_CASES`として除外し、挙動を変えていない。
- 既存の`er109_wiring_golden`・`er120_part2`等の失敗は本件以前からの既知(RESULT_PACKET参照)。
