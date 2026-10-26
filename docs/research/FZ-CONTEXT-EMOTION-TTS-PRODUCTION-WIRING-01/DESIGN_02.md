# DESIGN_02 — Family Z 文脈・感情付きTTS 正式Production Wiring 設計(Opus条件A反映・実装済み)

管理ID: FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02(Phase 1、2026-10-26)。到達上限Status=**IMPLEMENTED_PENDING_EVIDENCE**(PRODUCTION_WIREDではない。Phase 2 runtime evidence後にFableが判定)。
ユーザー決定=APPROVED_FOR_PRODUCTION(2026-10-26、原文`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md`)。Opus条件Aレビュー原文=`OPUS_REVIEW_01.md`(無改変)。
DESIGN_01(`DESIGN_01.md`)からの差分と、実装箇所・testを本書に記す。DESIGN_01のうち変更が無い節は参照のみ(§E Trial観測6項目の扱い、§F 新基準を作らない宣言、§G Dangling Reference表)。
Fable照合結果(委任文): Claude案とOpusは骨子で一致。M/Rは実装の穴の是正で既存ユーザー承認内容を変えない→**全件採用**(ユーザー判断事項なし。J-1はLR未配線の事実を完了報告で開示)。

## 0. M/R対応表(番号 / Fable決定 / 実装箇所 / test)

実装箇所の略: `P`=`er122_fz_ctx_policy_01.py` `N`=`er122_fz_ctx_notes_01.py` `Z`=`er063_family_z_audio_01.py` `B`=`er012_b_family_voices_production_01.py` `T3`=`er003_v1_n3_01_tts_generate.py` `D`=`er122_fzcw_runtime_evidence_01.py`。
test略: `pol`=`er122_fz_ctx_policy_test_01.py` `nt`=`er122_fz_ctx_notes_test_01.py` `wi`=`er063_fz_ctx_wiring_test_01.py` `dv`=`er122_fzcw_runtime_evidence_test_01.py`。

| # | Fable決定 | 実装箇所(file:line) | test |
|---|---|---|---|
| M-1 | 採用: 試行ごとに計上済み印。`carried_log()`は未計上行のみ。外側ループへ既定0の`prior_generations` | P:`carried_log`(252)・`mark_counted`(263)・`prior_generations`(248)、T3:439,448(キーワード専用・既定0)、Z:`generate_dialogue_ctx`の`gen`内`mark_counted`と`prior_generations=policy.prior_generations()`(927〜950) | pol:`test_m1_carried_log_only_uncounted_rows_and_prior_generations`・`test_m1_record_outcome_counts_each_attempt_exactly_once_across_resume`・`test_hook_none_outer_loop_prior_generations_default_zero_is_identity`、wi:`test_w7_adv_resume_after_pass1_counted_does_not_double_count` |
| M-2 | 採用: `max_attempts=min(外側残予算, policy.remaining())`で通算nと最終slotを一致 | Z:Std `max_attempts=policy.remaining()`(929)、Adv `ma = min(max_attempts, policy.remaining())`(943)。hookのstop(P:`before_attempt`)は安全網 | pol:`test_m2_resume_final_slot_matches_overall_n_and_hr_queue_row_exists`・`test_m2_no_resume_last_slot_only_at_n3` |
| M-3 | **(ii)採用**: 既存の行数会計(CURRENT_SPEC「4回目以降は生成しない」=ユーザー原文「総試行3回」と同義)を維持。ctx試行内minimal_fallback(1周2行)で外側予算が先に尽きる稀ケースは安全側でSTOPPED->HR Lock | 実装は**既存会計をそのまま使う**(`count_tts_generations_in_result`)。Zは`min(外側, policy)`で自然にこの挙動。記録名=`entry.dialogue_tts.terminal_before_fallback`(Z:954)、`effective_mode=minimal_fallback_in_ctx_attempt`(P:`after_attempt`) | pol:`test_technical_failure_inside_ctx_attempt_*`・`test_technical_failure_row_counts_two_rows_for_one_attempt`、wi:`test_w6_m3_ii_*` |
| M-4 | 採用: 再生成判定は明示信号のみ(`--only-clips`対象/`consuming_regenerate_approval`/本文sha不一致)。`record_outcome`直後に結果dict+wav shaをDONE_OKとして保存、sha一致なら採用(API 0)。Adv減速後判定前に落ちた試行はNG(消費済み) | P:`_open`(188)・`_restart`(217)・`saved_result`(228)・`finish`(390)、Z:`prepare_dialogue_ctx`(883: `only_clips`->`explicit_regenerate`)・`generate_dialogue_ctx`(922〜926: lockの`consuming_regenerate_approval`、saved採用) | pol:`test_m4_*`(5件)・`test_resume_with_only_clips_signal_still_continues_in_progress_cycle`、wi:`test_w9_*`・`test_w9b_*` |
| M-5 | 採用: LLMを呼ばないpolicy解決を`:1401`と`:1409`の間(cached読込の前)に置く | Z:`prepare_dialogue_ctx`呼出(1524、`assert_run_style_record(write=False)`後・`load_results`前)。reuse_keyへ`dialogue_tts`(Z:819: policyと文脈入力sha) | wi:`test_w1_*`・`test_w3_std_first_pass_*`(再開時に新policyのentryが再利用されTTS 0・LLM 0) |
| M-6 | 採用: Adv narrator chunk展開を親clip列へ畳み戻すadapter。`ALLOWED_NAMES`を引数化。story別一致test | N:`story_clips_from_plan`(170)・`validate_emotion_items(..., allowed_names)`(300)・`story_data`(142) | nt:`test_m6_chunk_fold_back_adapter_matches_trial_segment_plan`・`test_m6_allowed_names_is_per_story_not_global`・`test_01_trial_equivalence_*`・`test_01b_all_53_clips_compared` |
| M-7 | 採用: notes LLMが1回再試行後も失敗->そのlevelのdialogue TTS前に技術STOP(再開可・承認不要・既存STOP系例外型)。`missing_item`は既存DISCARDED処理で続行 | N:`NotesProvider._generate`(LLM_MAX_ATTEMPTS=2、失敗時`stop_type()`)、Z:`FamilyZDialogueCtxStop(FamilyZAudioStop)`(129) | nt:`test_m7_*`(3件)・`test_missing_item_stays_discarded_and_run_continues`、wi:`test_w13_*` |
| M-8 | 採用: 採用された試行の実効style(ctx/従来)を記録。attempt metadataにもmode | Z:`_effective_style_sha_for_result`(1278)、B:`attempt_hook.attempt_metadata()`(609)、P:`attempt_metadata`・`after_attempt` | wi:`test_w3_std_*`・`test_w3b_*`・`test_w3c_*` |
| M-9 | 採用: 基準commit(`ab111631c`、`HEAD`と対象4ファイルともsha同一)で変更前コードのgolden fixtureをPhase 1冒頭に凍結 | `golden/golden_hook_none_01.json`+`golden/MANIFEST.json`(source sha・golden sha)、生成=`er122_fz_ctx_fakes_01.py --freeze`(変更前コードで生成) | pol:`test_hook_none_is_byte_identical_to_frozen_golden_for_all_scenarios`、wi:`test_w12_*`・`test_w3c_*`(attempt3 promptがgoldenの旧promptとバイト一致) |
| M-10 | 採用(Phase 2計画へ): E-5(1回目のみ強制NG+n=1 NG後kill->再開)・Adv外側ループ継続(減速後判定側で注入=E-6)・E-4 Std/Adv両方・E-4期待値からASR由来HR queue行を外す | D:`CASE_DEFAULT_PLANS`(E-1〜E-6)・`make_post_slowdown_wrapper`・`make_kill_wrappers` | dv:`test_case_plans_*`・`test_e4_*`・`test_e5_*`・`test_e6_*`・`test_kill_*`。計画=`EVIDENCE_PLAN_02.md` |
| R-1 | 採用: driverが前後の行数とrun dir識別子を記録。forced run由来のHR queue行は台帳で「evidence専用・対応不要」。driverは正式runner main()を同一プロセスで起動 | D:`ledger_snapshot`・`ledger_diff`・`collect_added_rows`・`run_case`(runner main()同一process) | dv:`test_run_case_writes_evidence_*`・`test_collect_added_rows_*` |
| R-2 | 採用: policy固定=run単位、本文変更時=level単位でLLM再call(Q>C 1 call)、`mark_prev_postprocess_ng`は廃止(採用は`finish()`のみ)、表示名=既存roster/話者表優先、STOP例外型統一 | P:`resolve_run_policy`(95、`run_dir/audit/dialogue_tts_policy.json`)、N:`NotesProvider.ensure`(本文sha不一致->再call+`.prev`)・`_roster_display_from_attr_text`(124)、P:`note_final_ng`(273: NG確定時刻の記録のみ。採否の判定は変えない) | wi:`test_w1b_*`・`test_w1c_*`、nt:`test_14_*`・`test_16b_*` |
| (補) | Opus補足: Phase 2でctx音声peak分布(`check_clip_audio_quality` peak_max=0.999)を観測値として報告(新基準ではない) | D:`peak_distribution` | dv(driver出力項目) |

追加の自己発見(Fableへ開示): (a) runnerは`story_key`に`--slug`を渡す->既知story keyへ解決する`N:resolve_story_key`(107)を追加(Trial検証済みdataが黙ってfallbackに落ちるのを防止。test=`nt:test_story_key_resolution_keeps_trial_data_for_custom_slug`)。(b) システム`py`(3.14)にgoogle.genai/pykakasiが無く既存er012/er078系testが「importできない」ため、遮断harnessを継承しつつ空stubを補う`env_stub/sitecustomize.py`を追加(後述§K)。

## A. 感情・文脈情報生成の正式経路(DESIGN_01 §Aからの差分)

- 新module `er122_fz_ctx_notes_01.py`(Trial module `er118_*`をimportしない。TEST-11)。呼出点=`generate_dialogue_ctx`(Z:903)が最初のdialogue生成時に`provider.style_for(clip_id)`でlevel単位1 call(保存済みなら0)。**`prepare_dialogue_ctx`(Z:883)自体はLLMを呼ばない**(M-5。run単位policy解決+dialogue specへ`extra["dialogue_ctx"]`)。
- 逐語移植(Trial実成果物とsha一致をtestで固定): `extract_context`/`allowed_source_text`/`EMOTION_DEVELOPER` rule 1-10/`EMOTION_SCHEMA`/`emotion_user_message`/`validate_emotion_items`/`CONTEXT_HEAD`/`CONTEXT_TAIL`/`build_context_block`/`leakage_check`。引数化したのは話者表示名・許可語・作品名のみ(M-6)。
  - 一致の証明(`nt:test_01b_all_53_clips_compared`): 猿の手Std15/Adv17・メロスStd10/Adv11=**53 clip全てでstyle sha256がTrial `gen/<cid>/result.json`の`style_sha256`と一致**、`emotion_prompt_sha`とLLM user message shaがTrialの実call記録と一致、Fable目視で覆した件0(自動受理と同等)。
- 自動受理: 決定論検査の3値(ACCEPTED/NO_EXPLICIT_CUE/DISCARDED)をそのまま消費。**「Trialでの目視レビューを決定論の検査へ置換した」**(判定結果が同等の工程置換。品質基準の緩和ではない。根拠=Trial決定済み77件でvalidatorとFableが100%一致・覆し0、Trial `BUDGET_PLAN_01:48`が量産では自動化が必要と事前記載)。LLM創作の残余(上限約3.9%)はnotes保存のみで許容(新しい警告種別・blocking条件は作らない)。
- notes保存: `<level_dir>/audit/dialogue_ctx_notes.json`(`raw_output`・`validated`・`prompt_sha256`・`user_message_sha256`・`body_sha256`・`speaker_display_source`・費用)。run内不変。本文/Prompt/モデルが変わればlevel単位で再call(旧は`.prev`)。費用は`cl.segment_context("dialogue_ctx_notes:<level>")`でnotes生成として計上。
- Trial未検証story(`after_twenty_years`/`the_tell_tale_heart`/将来作): 表示名=既存話者表`attr_roster_text`の名称句>話者keyのTitle化(R-2)、許可語=表示名token+話者key token。`speaker_display_source`を各clipのevidenceに記録。失敗モード=誤DISCARD(中立化=安全側)。
- LLM call: model=`gpt-6-luna`、reasoning effort=low、structured output(Trial `run_llm_case`と同一call形)。本番ラインのモデル選定は別判断(PM_GOVERNANCE 25節)のため据置。

## B. TTS指示合成(DESIGN_01 §Bから変更なし。実装確認)

- ctx Style=`ENGLISH_STYLE_PREFIX.rstrip()+"\n\n"+CONTEXT block`(`N:build_ctx_style`)。base styleのshaを`EXPECTED_BASE_STYLE_SHA`で検査(不一致=技術STOP)。
- **従来方式への完全復帰**: 3回目の`style_prefix_override`は`None`(P:`before_attempt`がn=3で`None`を返し、ctx styleを保持した引数を渡さない)。共有ループは`style_prefix_override or p9a.ENGLISH_STYLE_PREFIX`(B:536)のままなので、**現行Z dialogueと同一のprompt**が送られる。test: `pol:test_fallback_attempt_prompt_is_byte_identical_to_baseline_legacy_prompt`(基準commit凍結のgolden prompt[`S1_success`]とバイト一致+CONTEXT/話者/前後セリフ/manner wordsが1文字も含まれない)、`wi:test_w3c_*`・`test_w5_*`(stage経由でも同一)。Voice・model・ASR呼出順は同一ループ。
- ctx試行内の`minimal_fallback`(技術失敗時の既存安全装置)は許容。最終方式として`minimal_fallback_in_ctx_attempt`を記録(M-3)。

## C. retry/fallback状態機械(確定版)

```
START -> n=1 [ctx] -PASS-> DONE_OK(mode=ctx)
              -NG-> n=2 [ctx, 待機0] -PASS-> DONE_OK(mode=ctx)
                          -NG-> COOLDOWN(固定600秒・実時間・5秒刻みSTOP確認) -> n=3 [style=None=従来] -PASS-> DONE_OK(mode=legacy_fallback)
                                                                                         -NG-> TERMINAL_NG -> STOPPED -> record_outcome -> HUMAN_REVIEW_REQUIRED(Lock) -> Gate BLOCK / STOP
```
- 『NG』=現行の採否chain全体の不採用(Std: 統一judge->disfluency->repetition QA。Adv: これに加え減速後の統一judge再検証)。ctx固有のNG条件は追加しない。総TTS試行(ループ反復)3回、3回目がfallbackそのもの(4回目なし)。HR Lockの累積guard(15回、er011:68)は不変。
- **実装方式=案A(Opus: 最善)**: 共有ループは1コピーのまま、キーワード専用・既定Noneの`attempt_hook`(B:513)だけ追加。差込点は4つ: 関数先頭の`carried_log()`(B:523)、各反復先頭の`before_attempt()`(B:528)、技術失敗`continue`直前と通常終端の`after_attempt()`(B:560,613)、attempt metadata(B:609)、最終STOPPED理由(B:633)。hook=Noneはバイト同一(golden)。B/Cのhook=None呼出、X/Y(この関数群を呼ばない)は不変。`er012_b`/`er003_n3`に新importなし(`pol:test_hook_signature_is_keyword_only_default_none_and_no_new_import_in_shared_modules`、er109_xz_isolation 回帰)。
- hookのインタフェース(実装済み、P:156〜): `carried_log`/`before_attempt`/`after_attempt`/`attempt_metadata`/`final_reason`、dialogue()側で`remaining`/`prior_generations`/`mark_counted`/`note_final_ng`/`saved_result`/`finish`/`evidence`。決定者は1つ(policy object)。
- state(P:121〜): `<level_dir>/audit/dialogue_ctx_attempt_state.json`(tmp+`os.replace`)。clip単位 `{canonical_text_sha256, policy, ctx_style_sha256, status, n_started, attempts[{n, mode, effective_mode, started_epoch, finished_epoch, verified, counted, rows, log_rows, final_ng_epoch}], cooldown{ref_epoch, requested_seconds, started_epoch, ended_epoch, waited_seconds_this_process, total_elapsed_since_ref_seconds, resumed}, done{result, wav_sha256}, history[], cycle}`。TTS呼出**前**に`n_started`を書く=TTS中に落ちても消費済み。
- resume規則(確定): state無し->新規 / 同一(text sha, policy, ctx style sha)かつIN_PROGRESS->**続行**(`--only-clips`が付いていても同一サイクルの再開は新規生成ではない) / DONE_OK+明示信号なし+wav sha一致->保存結果を採用(API 0) / 明示信号(`--only-clips`対象・lockの`consuming_regenerate_approval`)・不一致・wav不一致->新規サイクル(旧は`history`に残す) / TERMINAL_NG+明示信号なし->remaining=0(API 0)。state破損=技術STOP(消費済み試行を忘れて4回目を回さない)。
- cooldown: 起点=直前試行の最終NG確定時刻(`final_ng_epoch`、Advの減速後NG確定)>完了時刻>(完了前に落ちていれば)開始時刻。待機=`起点+600−現在`の実時間(再開しても10分未満にならず、10分経過済みなら0)。`er020.COOLDOWN_SECONDS`を参照(複製・短縮なし)。再開時の証跡には前回NGからの総経過秒を記録。イベント`CTX_COOLDOWN_BEFORE_FALLBACK`をattempt_historyへ。既存narratorのcooldown(`time.sleep(600)`単一)は変更しない。
- **Local Rewrite(J-1)**: Z dialogueにはLRが未配線(EXISTING_SPEC_CHECK_01 §2、`er003_v1_n3_01_tts_generate.py:319`)。新設せず、**3回NG->STOPPED->HR Lock->STOP**(原文「Local Rewriteで解決できなければ既存のHuman Review／STOP規則」を満たす)。LR新設は古典作品のセリフをLLMで書換える音声と表示本文の乖離を生む新仕様でありユーザー承認事項。将来配線する場合は「LR再TTSは従来style(`style_prefix_override=None`)・`max_attempts=1`・既存`lr_used==0`・累積15回guard維持」が要件(本設計は妨げない)。
- M-3(ii)の確定挙動: Advの外側ループは行数で会計し、minimal_fallbackは1周2行。ctx試行で技術失敗->minimal fallbackが起きると外側の行予算が先に尽き、従来方式(3回目)に到達せずSTOPPED->HR Lockへ送る(実TTS生成は3回を超えない)。`dialogue_tts.terminal_before_fallback=true`で開示。(i)(外側ループの数え方をpolicyに合わせる)への変更は既存のA2予算規則の変更でありユーザー判断事項(OPEN_TRACKING_02)。

## D. X/Y/B/C不変の保証(確定版)

1. 入口=Z dialogue closure(`real_generators().dialogue`)のみ。X(`er019_*`)/Y(`er121_*`)は`generate_voice_body_wide_margin`も`er063.real_generators`も呼ばず、新module/新引数への参照0(`wi:test_w11_x_y_runners_do_not_reference_new_modules_or_hook`)。
2. 共有関数(B/Cも呼ぶ)は`attempt_hook=None`/`prior_generations=0`既定。hook=Noneは**変更前コードで凍結したgoldenと全8シナリオ(成功/NG/3NG/技術失敗2種/stop_retrying/max_attempts=2)+外側ループ6シナリオでバイト一致**(`pol:test_hook_none_is_byte_identical_to_frozen_golden_for_all_scenarios`)。
3. narrator/topic_intro/preview/comment/japanese_title/kp_*のgeneratorソースは基準commitと一字一句同一(`wi:test_w11b_*`)。`style_text_for`・`FAMILY_Z_ROLE_STYLE`・non-dialogueの`build_reuse_key`は不変(`wi:test_w1_*`・`test_w11c_*`)。
4. ロールバック=`Z_DIALOGUE_CTX_POLICY_DEFAULT`(P:30)を`"legacy"`にする1行(前例`A3_SECONDARY_LENGTH_REEVAL`)。**env/flag/起動script/.envでON/OFFしない**(`pol:test_case3b_*`)。policy=legacy(既存run・ロールバック)ではdialogueは現行と同一(`wi:test_w12_*`)。
5. run単位のpolicy固定: `<run_dir>/audit/dialogue_tts_policy.json`。既存のrun state(`tts_generation_results.json`/`tts_checkpoint.json`/`review_lock_state.json`/`human_approved_segments.json`)があるrunは**levelをまたいでlegacy固定**(a2が旧方式で生成済み・b1b未着手でも方式が混在しない: `wi:test_w1b_*`)。新規runのみ`fz_ctx_v1`。`audit/`は`copy_reusable_run_assets`で新runへ持ち込まれない(REUSE_DENY_DIR_SEGMENTS)。

## E〜G. Trial観測6項目・品質基準・Dangling Reference

DESIGN_01 §E/§F/§Gのとおり(変更なし)。Phase 1で新たに撤去した規則・検査・testは**0**。維持した旧方式の参照点(`ENGLISH_STYLE_PREFIX`/`style_text_for`/`build_reuse_key`/`_effective_style_sha`/`extract_attempt_evidence`/`generate_voice_body_minimal_fallback`/`verify_z_speed_profile`/`check_clip_audio_quality`/Gate)は全て残存(`wi:test_w15_*`)。新キー(entry `dialogue_tts`、attempts row `tts_mode`等、reuse_key `dialogue_tts`)はadditive(`wi:test_w16_*`)。

## H. Phase 2 計画への反映(M-10)

`EVIDENCE_PLAN_02.md`・`BUDGET_PLAN_02.md`参照。E-1(正常経路 Std+Adv)、E-2(強制NG 1・2回目->cooldown->従来)、E-3(E-2+cooldown中にkill->再開)、E-4(3回強制NG、Std/Adv両方)、E-5(1回目のみ強制NG->2回目ctx即時PASS+n=1 NG後kill->再開)、E-6(Adv: n=1が減速後NG->外側ループ継続)。強制NGはdriver(`D`)のみ・NG方向のみ。強制NGはrepetition QA段階でASR判定はPASSのため、**ASR由来のHR queue行は期待値に含めない**(HR Lockは最終STOPPEDで立つ)。

## I. 費用・時間(要約)

`BUDGET_PLAN_02.md`参照。Phase 1=API 0・JPY0。Phase 2見積(期待約50円・保守約62円・天井約80円)は全て300円以下=Fable自律枠。

## J. CURRENT_SPEC追記案(Phase 2完了+Fable判定後に別委任で反映。ここでは文案のみ)

『Family Z dialogue 文脈・感情付きTTS(OPEN-528、APPROVED_FOR_PRODUCTION 2026-10-26、Z専用・Std/Adv)』: セリフclipは新規run(run state無し)で文脈・感情付きTTSを標準とし、TTS総試行は初回含め最大3回(1・2回目=文脈・感情付き、2回目NG後に固定600秒[`er020.COOLDOWN_SECONDS`、実時間]のクールダウン、3回目=従来style[`style_prefix_override=None`=文脈・感情情報を完全除外])。『NG』は既存のASR/disfluency/repetition QA(Advは減速後再検証を含む)の採否そのもの。**3回NGは現行どおりSTOPPED->Review Lock(HUMAN_REVIEW_REQUIRED)->STOP。Z dialogueにLocal Rewriteは未配線のため、受入表の『3回NG->Local Rewrite／Human Review／STOP』はHuman Review／STOPで満たす(LR配線は別判断)。** 感情・文脈情報はTrialと同一Prompt/rule 1-10/model(`gpt-6-luna`、reasoning low)/CONTEXT書式でlevel単位1 call(+1回再試行、失敗は技術STOP)、run内不変保存(`<level>/audit/dialogue_ctx_notes.json`)。**Trialでの目視レビュー(Fable)は撤去し、決定論の検査(逐語引用一致・語数・新規固有名詞・強度語)の3値を自動受理する工程置換**(Trial決定済み77件で判定一致100%・覆し0)。leakageは観測のみ。attempt状態は`<level>/audit/dialogue_ctx_attempt_state.json`に永続化し、再開は消費済み試行を再実行せず、明示再生成信号(`--only-clips`対象・`consuming_regenerate_approval`・本文/policy/ctx style不一致)のときだけ新規サイクル。ctx試行内の技術失敗minimal fallbackは既存の安全装置として許容し`minimal_fallback_in_ctx_attempt`と記録。Advで行会計により従来方式へ到達せず終わる稀ケースは安全側でSTOPPED->HR Lock(`terminal_before_fallback`、M-3(ii))。run単位のpolicyは`<run>/audit/dialogue_tts_policy.json`で固定(既存run state有=legacy、新規=`fz_ctx_v1`、ロールバック=`Z_DIALOGUE_CTX_POLICY_DEFAULT`)。X/Y/B/C/narrator/KPは不変。Status=PRODUCTION_WIRED(Phase 2 runtime evidence+Fable独立照合後に限る)。

## K. offline test環境(開示)

システム`py`(3.14.6)には`google.genai`・`pykakasi`が無く、`er012_b`/`er063`系の既存testは遮断harness下でも「importできない」ため、変更前(HEAD)でも多数がerrorになる(`baseline_regression/base_er*.out`)。`.venv\Scripts\python.exe`は委任文で禁止のため、`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/env_stub/sitecustomize.py`を追加した: (1)`netblock_harness_01/sitecustomize.py`(外部接続遮断)を同一processで読み込む (2)import名のみ空stub(実物がある環境[.venv]では何もしない=実APIは呼べない)。使い方=`$env:PYTHONPATH="docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/env_stub"; $env:NETBLOCK_LOG=<log>; py -m pytest <files>`。この環境で変更前後の既存testを比較した(結果=RESULT_PACKET_FZCW2)。
