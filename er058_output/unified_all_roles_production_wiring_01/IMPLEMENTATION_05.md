# AUW 委任_05 IMPLEMENTATION (A2減速後判定の統一judge化 + Dialogue到達確認 + KP解説3回化 + runner共有cache/circuit breaker + is_last_slot配線 + B/C hook) -- branch feat/auw-unified-asr-01
JPY 0(mockのみ、Production API呼出0)。main無変更。Prompt/モデル/Voice/速度(6%減速)/閾値(KP解説の回数以外)/HR Lock(`er011_human_review_lock_01.py`)/予算guard/SSOT/U1・U2定数 無変更。U1=True, U2=A2_ONLY 維持(`er078_asr_unified_judge_01.py:65-66`、本委任で当該ファイル無編集)。
証跡: `patch_05/test_post_05_main_final.json`(98ファイル)・`patch_05/test_post_05_extra_final.json`(113ファイル)・`patch_05/test_post_05_rest.json`(102ファイル)・baseline=`patch_04/test_post_04.json`+`patch_05/baseline_extra.json`+`patch_05/baseline_rest_fails.json`。通信遮断=`scratchpad/ng04/netguard_attempts.log`(pytest plugin `-p netguard`)。

## 0. 当初目的(ユーザー原文を逐語。ファイル=`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`)
- L31「英語・日本語、全Family・全Sectionで、ASRの誤認に起因する不要なTTS再生成を減らし、数値・否定などの重要な内容を保護しながら、自動量産できる統一音声検証基盤を完成させる。」
- L39-L49「TTS生成① → Primary ASR → NGならSecondary ASR / 両方NGの場合: TTS再生成② → … / TTS再生成③ → … / 3回とも不合格の場合、既存の安全条件に従いLocal RewriteまたはHuman Reviewへ進む。」
- L53-L63「Primary PASSなら、その時点でASR合格。Secondaryは不要。/ Primary NGなら、不一致の種類によらず原則Secondaryを実行する。/ Primary NG・Secondary PASSなら、PASS_WITH_WARNINGとして採用する。/ … WARNING音声はユーザーが事後試聴できるリストへ自動登録する。/ Primary・Secondary両方NGなら次のTTS再生成へ進む。/ Secondaryが障害・利用不能の場合、PASS扱いせず、既存の安全な障害処理へ進む。/ 同じ音声に対するSecondaryの重複API呼び出しを防ぐ。/ 各TTS再生成では、原則として原稿・Prompt・モデル・Voice・速度を維持する。/ 既存の無音・反復・言語違い・異常長・発音品質等の独立QAは維持する。/ 既存のHuman Review Lock、承認・停止・予算上限は維持する。」
- L97「この安全条件と「Secondary PASSなら採用」の原則が競合する場合は、数値・否定などの明確な重大内容差を誤採用しないことを優先する。保護すべき差異を警告だけで無条件に解放する仕様にはしない。」
- L112-L117「`Melos said.` の2026年10月14日の実音声検証は重要なRegression基準とする。Full Story相当：12/12 PASS / Dialogue・見出し相当：12/12 PASS / M1新規救済：21観測 / M1起因の誤受理：0件」
- L143-L153「Section固有の既存例外は維持する。特に: 1. Key Phrase(…既存Minimal Prompt／English Language Lockとの整合を確認。全体のTTS3回仕様との競合は整理する。) 2. 日本語Local Rewrite(現行の英語用機構を機械的に流用しない。…Human Reviewへ進める。) 3. 見出し・短文(独立したQA・意味保護を維持する。) 4. A2の6%減速(減速前後のASR検証・再生成回数・音声品質が整合すること。) 5. Dialogue(複数Voiceの区分・話者帰属・既存Segment構造を維持する。) 新しいSection固有の例外を実装都合で勝手に増やさない。」
- L197-L222 必須受入条件15項目(本委任は1,3,4,6,7,8,10を担当。9=runtime evidence・11=SSOT・12=merge・13=Dangling・15=Fable照合は委任_06/07)。

## 1. 配線点 (file:line)
### A. A2減速後判定(J7)
| 項目 | 場所 |
|---|---|
| 統一judge経由の減速後判定(新) | `er003_v1_n3_01_tts_generate.py:178 _post_slowdown_unified_judge` → `secondary_asr.evaluate_attempt_with_cascade_detail`(EN adapter。Primary P-chain[Tier1 5role+baseline+contraction+B1 CS+CMU Case A/homophone+M1]は不変、後段で統一judge)。`attempt_ctx={"slot":1,"script_version":"v0","is_last_slot":…}`。adapter例外はfail-closed、`init_logger`/`[STOP]`は伝播(旧rescueと同じ方針) |
| 減速後再検証本体 | `er003_v1_n3_01_tts_generate.py:235 apply_a2_slowdown_postprocess(…, is_last_slot=True)`: 6%減速(`a2_slowdown.apply_a2_slowdown`)・Prompt・Voice・速度・比率按分(trim_info/duration/sha256)は不変。Primary転写取得(`routing.transcribe`)は不変、直接`classify_asr_match`は撤去 |
| is_last_slot | 既定True(外側ループのない呼出元=Dialogue(Z)・B Voices A2)。外側ループ(`generate_a2_segment_with_slowdown`)は `is_last_slot=(generations_used >= total_budget or attempt >= max_slowdown_attempts)`(`:411`)。HR queueへは書かない(`_detail`版=Review Lock側の既存経路に委ねる、旧と同じ) |
| asr_judgement退避 | 減速後wavで採用(verified)→ `result["asr_judgement"]` を減速後recordに置換、減速前recordは `asr_judgement_pre_slowdown` へ退避(維持)。NG時は `asr_judgement_post_slowdown_ng`(不採用音声の監査用、additive) |
| 結果キー互換 | `post_slowdown_asr_text` / `post_slowdown_classification`(=Primary層の分類ラベル、不変) / `post_slowdown_semantic_equivalence` / `post_slowdown_final_classification`(adapter最終status) / `post_slowdown_cascade`(Secondary等が走った時のみ、従来と同形+`asr_judgement`) / `post_slowdown_homophone_accepted`(`layers`に`cmu_alternate`) / `post_slowdown_cascade_accepted`(Secondary・補強stepが走って採用) |
| 静的監査 | `A2_PENDING_ENTRIES=[]`(`er078_asr_unified_wiring_static_audit_01.py:70`)、`PENDING_DELEGATION_05_CATEGORIES=()`、allowlist(phase=post_wiring、35 entry)に`a2_slowdown_pending_delegation_05`は0、`apply_a2_slowdown_postprocess`の`routing.transcribe`は`primary_acquisition`、`_post_slowdown_unified_judge`の`evaluate_attempt_with_cascade_detail`は`en_adapter_entry` |
| 残置 | `_post_slowdown_cascade_rescue`(`:120`、UNCERTAIN限定ゲート)は**Productionの経路からは呼ばれなくなった**が、既存test3ファイル(`er006_secondary_asr_01_m1_wiring_test_01.py`、`er065_…regression_test_01.py`、`er078_asr_unified_en_wiring_test_01.py`)が直接呼ぶため削除せず残置(整理=委任_07判断)。`import er006_preprod_hardening_01_validation as en_validator`も既存testがpatchするため残置 |

### B. Dialogue(er063 / Family Z)
- Std: `er063_family_z_audio_01.py:635 dialogue`(`a2`)= `bvoices.generate_voice_body_wide_margin`(J4=EN adapter)→`n3_tts.apply_a2_slowdown_postprocess`(J7=統一judge)。Adv: `generate_voice_body_wide_margin`のみ(減速なし)。**両方とも委任_03(J4)・本委任(J7)のEN adapterに既に到達**、未到達leaf/hookなし(JAはDialogueに無い)。Dialogue固有のPrompt(`A2_ENGLISH_STYLE_PREFIX_SLOWER`/Advは`style_prefix_override`を渡さない)・Voice(`spec.voice`)・閾値・話者帰属(`assert_dialogue_attribution`)は無変更(test: `test_dialogue_std_reaches_unified_judge_via_j4_and_j7_with_prompt_unchanged`、`test_dialogue_adv_has_no_slowdown_and_no_style_override`)。
- 静的監査: Z entrypoint(`er063_family_z_audio_01`)の閉包に`er012_b_family_voices_production_01`/`er003_v1_n3_01_tts_generate`/`er006_secondary_asr_01`が含まれ、J4・J7の双方にadapter入口(`en_adapter_entry`)がある(test: `test_dialogue_and_ja_paths_statically_reach_adapters_through_z_entrypoint`)。registry hook(`er063:989`)・ページ節は委任_03で配線済み(無変更)。
- **未実装(委任文A〜Hに無いため拡大せず記録)**: DESIGN_01 §4-8(C-L)の「Dialogue(Std)/Voices A2へ`gen_fn`引数を足して外側ループ(通算3)を適用」。現状=減速後NGは再生成せずSTOPPED(既存挙動のまま、`is_last_slot=True`なので最終slot扱い)。見出しminimal2撤去(OPEN-288)も未着手。

### C. KP解説3回化(OF-AUW-12)
- `er019_family_x_audio_production_runner_01.py:701 KP_EXPLANATION_MAX_ATTEMPTS = 3`、`:713 max_attempts=KP_EXPLANATION_MAX_ATTEMPTS`(旧`max_attempts=2`)。Zは同関数を呼ぶ(`er063:692 kp_expl_en`→`x_runner.generate_key_phrase_explanation_en_verified`)ので同時に3回化。**この1点のみ変更**(Prompt・`disfluency_qa=True`・`enable_non_latin_cascade=True`・`asr_prompt`・`safety_margin_seconds`・text-gate・`tts_safe_en`は不変)。根拠=ユーザー原文L39-L49(3回)+DESIGN_02_ADDENDUM_01 §9/OF-AUW-12(「3回仕様のユーザー決定逐語なし・Trial値max_attempts=2の継承。3回へ揃える」)。
- 不変: KP英語phrase=4回構成(MINIMAL 2 + ENGLISH_LOCK 2、`KEY_PHRASE_TOTAL_MAX_ATTEMPTS=4`、test済み)。JA KPは原則HR(LRなし)維持(`generate_a2_japanese_with_fallback`/`generate_charon_japanese`に`run_local_rewrite`なし、3NG→STOPPED→HR Lock)。
- **期待TTS呼出増分(委任_06費用試算の入力)**: KP解説1本あたり、最悪ケースで **+1回(TTS+1、OpenAI ASR+1、Secondary最大+1[Primary NG時のみ])**。増分が発生するのは「標準2回が両NG」の場合のみ(3回目で救済されなければ従来どおりSTOPPED→HR、旧は2回で打切り)。対象=Advanced(B1B) KP解説(Xは`kp{rank}_explanation_en`、Zは`kp_expl_en`)×rank数(通常5)。単価(`DESIGN_01.md` §9の既存実績: TTS Flash-Lite ¥0.062/clip短文・OpenAI ASR ≈¥0.01/短clip・Azure ¥0.0444/秒)で、解説は数秒〜十数秒想定→**1 KP解説あたり最大約¥0.07(TTS)+¥0.01(ASR)+Azure≲¥0.5(長さ10秒のとき)、5本全て最悪でも約¥3/記事**(上限見積り。実際は2回目までにPASSする確率が高く期待値は大幅に小さい。実NG分布は`attempt_history`から委任_06で試算)。

### D. runner共有cache / circuit breaker
`er078_secondary_run_scope_01.py`(新): `with_secondary_run`(decorator)。stage実行中だけ`er006_secondary_asr_01.begin_secondary_run()`(run単位SecondaryCache+circuit breaker/技術STOP記録、JA adapterも`_shared_run_cache_and_state`で共有)を有効化し、終了時(例外時含む)`end_secondary_run()`。入れ子は外側scopeを再利用。**判定・Prompt・回数は不変**(cache/breakerの有効化のみ)。技術STOPはHuman Review Lockを触らない(test)。
| Family/runner | 導入位置(decorator行) | 関数 | 備考 |
|---|---|---|---|
| X(Active) | `er019_family_x_audio_production_runner_01.py:788` / `:1107` | `generate_family_x_b1_segments` / `generate_family_x_a2_segments` | `main()`の`--stage tts`が呼ぶ。各levelで1 scope |
| Z(Active) | `er063_family_z_audio_01.py:923` | `run_tts_stage` | `er026 stage_tts`が`m.a63.run_tts_stage`経由で呼ぶ。dry_runでも開始するがASR呼出なし=無害 |
| B(Legacy) | `er012_b_family_production_runner_01.py:309` / `:1457` / `:1705` | `run_tts`(B1 2V) / `run_tts_a2` / `run_tts_a2_2v_new_topic` | |
| B(Legacy 3V) | `er012_b_family_voices_production_01.py:833` | `run_tts_3v` | `main_b1_3v`が`b1prod.run_tts_3v`経由 |
| C(Legacy) | `er013_family_c_production_runner_01.py:640` | `run_full_generation` | C内`get_or_run_asr`は診断のみ(判定に使わない、test済み) |
| A(Legacy n3) | `er003_v1_n3_01_tts_generate.py:1015` / `:1157` | `generate_b1_segments` / `generate_a2_segments` | `run_theme`/`main`が呼ぶ |
| E(Entertainment) | 導入なし | `er012_e_family_entertainment_two_level_runner_01.run_tts_stage` | 現状`RuntimeError(_FAMILY_X_ER019_MIGRATION_STOP_MESSAGE)`でTTSを持たない(X移行済み)。ASR呼出がないためscope不要 |
test: `test_every_production_runner_tts_entry_is_run_scoped`(10関数)、`test_run_scope_decorator_begin_end_nested_and_exception_cleanup`、`test_z_run_tts_stage_enables_run_scope_during_generators_and_cleans_up`、`test_en_and_ja_adapters_share_run_cache_same_wav_duplicate_secondary_zero`(run内3回判定でEN Azure=1/JA Azure=1)、`test_circuit_breaker_stops_secondary_after_consecutive_failures_and_is_technical_not_lock`(連続障害2回で停止、`record_outcome`呼出0)、`test_j7_same_wav_secondary_duplicate_zero_within_run_scope`。

### E. attempt_ctx / is_last_slot 配線
`er078_asr_unified_attempt_ctx_01.py`(新、純関数): `build_attempt_ctx(attempt, max_attempts, slot_offset, total_slots, script_version)` → `{"slot": slot_offset+attempt, "is_last_slot": slot >= total_slots, "script_version": …}`。`length_ok`は渡さない(EN leafは従来どおりleafでlengthをANDし、judgeの除外表の挙動を変えない)。
| leaf | 場所 | slot規約 |
|---|---|---|
| EN voice01 `generate_charon_english` | `er003_v1_sing01_voice01_generate.py:254` | attempt/max_attempts。LR後v1再TTSは`script_version="v1"`(`_retts_fn`) |
| EN news_tail_fix | `er003_v1_sing01_news_tail_fix.py:211` | 同上(LR後v1も`script_version="v1"`) |
| EN point_headings | `er003_v1_sing01_point_headings_aoede.py:131` | attempt/max_attempts |
| EN B voices | `er012_b_family_voices_production_01.py:556` | attempt/max_attempts |
| EN repro01 strict | `er003_v1_repro01_main_generate.py:364`(EN)・`:385`(JA) | `slot_offset`/`total_slots`引数(既定=この呼出のmax_attempts)。標準経路(後段fallbackあり)・KP 4回構成の前半は呼び出し側が通算上限を渡す |
| EN crosslevel | `er003_v1_crosslevel_audio_02_common.py:154`(標準2回、total=prior+max)・`:194`(minimal fallback、通算slot) | 標準2回はHR対象外、通算3回目のみ最終slot。LR後v1は03から`script_version="v1"`/`is_last_slot=True` |
| JA voice01 `generate_charon_japanese` | `er003_v1_sing01_voice01_generate.py:526`(標準)・`:578`(fallback、通算slot) | 標準2回=HR対象外、通算3回目=最終slot |
| JA repro01 JA分岐 | `er003_v1_repro01_main_generate.py:385` | n3 JA標準(`:681 slot_offset=0,total_slots=max_attempts`)から呼ばれるときはHR対象外 |
| JA n3 `generate_a2_japanese_with_fallback` | `er003_v1_n3_01_tts_generate.py:681`(標準→repro01)・`:710`(fallback、通算slot) | 同上 |
| KP英語phrase(4回構成) | `er003_v1_repro01_main_generate.py:815`(前半 offset0/total4)・`:827`(後半 offset2/total4)、`er063_family_z_audio_01.py:677`/`:688`(Zの同構成) | 最終slot=通算4回目のみHR対象 |
- **HR queue = 最終slotのNGのみ**: adapter(EN `er006_secondary_asr_01.py:957`、JA `er007_ja_secondary_asr_01.py:679`)が`is_last_slot`かつNGのとき`human_review_required=True`→wrapperが`_log_human_review`(`is_duplicate_queue_entry`で重複排除)。leaf側のHR Lock(`er011_human_review_lock_01`の`guarded_generate`/`record_outcome`)はstate(`review_lock_state.json`)を書くだけでqueueは書かない=二重投入なし(test: EN leaf 5種×queue=1行、slot==[3])。`er011_human_review_lock_01.py`は`git diff 961d5b360`で無変更(test)。
- 記録のみ(削除しない): 各leafの到達不能`if stop_retrying: return ASR_VALIDATION_UNCERTAIN …`分岐(adapterが`stop_retrying=False`固定=常に偽)。leaf 6ファイルに計8箇所残置(voice01 3、news_tail_fix 1、point_headings 1、B voices 1、repro01 1、n3 1)(test `test_hr_lock_module_unchanged_and_stop_retrying_branches_recorded_only`)。整理は委任_07判断。
- 留意(既存の流儀を踏襲): LR可能なleaf(CS層ON)でも、主ループの最終slot(通算3)をis_last_slotとする(03のcrosslevel minimal fallbackと同じ)。LRで救済された場合は、その前に最終slotでHR queueへ投入済みのentryが残る(旧cascade尽きHR直行と同じ時期・同等の内容。LR後v1のNGは別canonical textの別entry)。

### F. Family B / C hook
- B: `er012_b_family_production_runner_01.py:402`(`finalize_tts_results`)・`:834`(`_3v`)・`:1499`(`_a2`)・`:1783`(`_a2_2v_new_topic`)に`pww_registry.write_listening_list_safe(<run_dir>, standalone_html=True)`(例外を投げない・0件でも節あり)。results(`tts_generation_results.json`)確定直後。
- C: `er013_family_c_production_runner_01.py:932`(`tts_generation_results.json`書込直後・Gate`verify_episode_audio_validation_gate`前)に同hook。Cのaudit entryは従来`asr_judgement`を落としていたため、`to_audit_entry`が`asr_judgement`(新規生成)/`asr_judgement_inherited`(resume・reuse)をadditiveに載せ、`mark_ok`が`.ok`メタに`asr_judgement`を保存、`resumable_reuse`が**同一wav(sha256一致)の場合のみ**継承する(元のWARNINGを事後試聴リストへ引継ぎ、追補§8)。Gate入力(`tts_generation_results.json`のsegments/key_phrasesの意味)は変更なし(キー追加のみ)。`get_or_run_asr`は診断のみで判定に使わない(静的test済み)。

## 2. Section固有例外の維持(新例外ゼロ)
| 例外 | 維持の証拠 | 本委任の影響 |
|---|---|---|
| A2の6%減速 | `apply_a2_slowdown`呼出・比率按分・sha256更新・original_wav保持・Prompt(`A2_ENGLISH_STYLE_PREFIX_SLOWER`)は無変更。外側ループ通算TTS 3(05A)も無変更(test: `er058_asr_tts_prodfix_01_test_01` 27 passed) | 判定のみ統一judge |
| Dialogue | §1-B | 無変更 |
| KP | §1-C。英語phrase 4回・JA KP原則HR・学習対象語は変更しない | 解説のみ2→3回 |
| 日本語LR原則HR | `run_local_rewrite`呼出なし(test) | 無変更 |
| 見出し・短文 | `point_headings`のminimal切替(`minimal_after`)・独立QA(disfluency/repetition)は無変更 | slot渡しのみ |

## 3. 撤去・残置した規則(Grep)
- 撤去: `apply_a2_slowdown_postprocess`内の直接`en_validator.classify_asr_match`+`secondary_asr.is_homophone_candidate_mismatch`+`_step_alternate_pass`+`_post_slowdown_cascade_rescue`呼出(Production経路から)。UNCERTAIN限定のCascade入口条件は新経路に無い(=Primary NGなら原則Secondary 1回)。
- 残置(Grep結果): `_post_slowdown_cascade_rescue`(n3:120、test3ファイルが参照)、`en_validator` import(n3:50)、leaf `if stop_retrying:`(§1-E)、`A2_PENDING_ENTRIES`/`CAT_A2_DEFERRED`定数名(`=[]`/ALLOWED外、残存すればFAIL)。`rg "a2_slowdown_pending_delegation_05" er078_asr_unified_wiring_allowlist_01.json` = 0件。
- 追記: `rg -n "max_attempts=2" er019_family_x_audio_production_runner_01.py` → コメント内の旧値言及のみ(関数引数は`KP_EXPLANATION_MAX_ATTEMPTS`)。

## 4. test数値
- 新規 `er078_asr_unified_wiring_05_test_01.py`: **50 passed**(A/J7 9+静的監査1、Dialogue 3、KP解説/KP 7、runner scope 14[parametrize 10含む]、attempt_ctx/is_last_slot 13、B/C hook 3)。静的監査 `er078_asr_unified_wiring_static_audit_01.py` 15 passed(deferred 0・pending 0を追加assert)。
- 既存影響(per-file、`-p netguard`通信遮断付き、`patch_05/`):
  | 系統 | files | passed | failed | baseline比 |
  |---|---|---|---|---|
  | 9系統(er006/007/011/019/020/021/026/064/078) | 98(97+新規1)+静的監査 | 1,796 | 32 | **新規失敗0**(全てbaseline既存id) |
  | er003/008/009/012/013/058/063/065/068(er063/er013/B family含む) | 113 | 2,578 | 9 | **新規失敗0**(baseline 9 id同一) |
  | 残り(er002/005/010/015…/077) | 102 | 2,868 | 29(26 id+import error 3ファイル) | baseline(HEAD)と**失敗id 26が完全一致**(`baseline_rest_fails.json`、変更ファイルをHEADへ一時復元して実測→復元) |
  - er026 `post_slowdown` 3件(`final_classification_top_level_field`/`no_rescue_when_secondary_also_misspells`/`OuterLoop…no_rescue_consumes_budget`)はbaseline既存失敗(作業ツリー`ledger.json`の"melos"でM1が受理)。空ledgerに固定すると16/16 PASS(再現済み、新コードでも)。
  - `er026_family_z_e2e_integration_test_01::test_shared_state_files_unchanged_by_mock_run`は他suiteと並行すると揺れる(単独実行で42 passed、03bで既知)。
- 既存testの追随(期待値の意味を変えたのは下記1件。他は署名/形のみ):
  | test | 区分 | 内容 |
  |---|---|---|
  | `er026_post_slowdown…::test_no_rescue_for_content_word_error` | **β類似(最終判定)** | 旧=「内容語誤りはCascade対象外でAzure不呼出→STOPPED」。新=原文L54-L55に従い減速後wavへSecondary 1回、原稿全文を支持すればPASS_WITH_WARNING、支持しなければSTOPPED(誤受理0)。**委任_03c(Fable判断・選択肢A)と同じ根拠の適用**であり、委任文の「β期待値変更禁止」に抵触しうるため要Fable確認(§6) |
  | `er026_post_slowdown…::test_cmu_case_a_homophone_name_rescued_without_extra_asr` | α(回数) | Azure呼出0→≤1(adapterはTier3 corroboration[Azure、共有cache]→CMU Case Aの順。受理判定自体は不変) |
  | `er008_n8_a2_slowdown_sha256_refresh_22_test_01`(2件) | α(mock形) | 旧`classify_asr_match`のMock(`should_pass`のみ)はadapterのP-chainの形(protected等)に合わない→`wraps=`実関数(原稿==転写でEXACT_MATCH)。主題(sha256更新)は不変 |
  | `er007_reading_validation_wiring…` / `er011_keyphrase_en_asr_false_rejection…`(2) / `er011_open121_repetition_qa…`(1) / `er011_tts_attempt_audio_retention…`(3) | α(mock署名) | fakeの署名に`attempt_ctx=None`追加(04の`er011_open121`と同様) |
  | `er012_b_family_voices_a2_new_topic…` | α(mock署名) | fake_standardに`slot_offset`/`total_slots` |
  | `er058_asr_tts_prodfix_01_test_01` | α(mock署名) | `_stopped_slowdown`/`ok_slowdown`に`is_last_slot` |
  | γ(未commit-diff guard) | 0 | 前回commit済みのため該当なし |
- 通信遮断ログ: 本委任で触ったtest(新規`er078_asr_unified_wiring_05_test_01.py`・追随8ファイル)からの外部通信は**0**。遮断された試行は既存testのみ=huggingface.co(`er011_open121…EndToEnd`・`er008_disfluency_qa_18`・`er011_open128`)、api.openai.com(`er007_ja_secondary_asr_01_test::test_unrelated_kanji_reading_not_confirmed`ほか、test外)、en.wiktionary.org(er028〜er034のKP-DB既存失敗test)、oauth2.googleapis.com/169.254.169.254(`er003_test_b1_p5b_audio`)。いずれも本委任変更外(記録のみ)。有料API 0。

## 5. 受入観点(ユーザー原文)との照合メモ
- L54/L55: 減速後も「Primary NG→Secondary 1回→PASS_WITH_WARNING」(test: `test_j7_primary_ng_secondary_pass_…`)、Primary PASSでSecondary不呼出(`test_j7_primary_pass_never_calls_secondary`)。
- L58: 両NG→STOPPED→外側ループ/次slotへ(`test_j7_secondary_ng_both…`)。L59: Secondary障害はPASS不可(`NG_SECONDARY_UNAVAILABLE`)。L60: 同一wav重複0(run scope・J7)。
- L97: 値DIFF/否定差は減速後でもSecondary不呼出・不採用(`test_j7_value_and_negation_protected_diffs_not_rescued_by_secondary`)。
- L57: 減速後wavでWARNING採用→試聴リストに`adopted_sha256`=減速後wavのsha256で載る(`test_j7_pww_after_slowdown_appears_in_listening_list_with_post_slowdown_sha`)。
- L112-L117(Melos 12/12等): 本委任は保存データ再判定を行わない(判定ロジックの追加変更なし。Primary P-chainは不変)。実音声での合否は委任_06。

## 6. 逸脱・要判断・委任_06/07への注意点
1. **β類似の期待値変更1件**(§4): `test_no_rescue_for_content_word_error`。委任_03cの選択肢Aと同根拠で追随したが、委任文の「β期待値変更禁止→実装修正 or STOP」と形式上抵触しうる。実装側の代替(UNCERTAINのみSecondaryに戻す)はL54(「不一致の種類によらず原則Secondary」)に反するため採らなかった。差戻し時は当該test 1件の復元のみ(復元すると減速後の内容語差はSecondaryで採用される実装と矛盾して失敗する=設計判断)。
2. **コスト影響(委任_06へ)**: (a) A2減速後のPrimary NGは従来UNCERTAIN(固有名詞/同音語)のみSecondary対象→今後は不一致の種類によらずSecondary 1回(Azureは減速後wavにつき最大1回)。(b) 減速後でCMU Case A(無料)に当たる固有名詞差でも、adapterの順序(Tier3 corroboration→Case A)により先にAzureを1回呼ぶ(`FIVE_ROLES`のentity_only時)。無駄な呼出になりうる→adapterの順序変更は全leafに影響する新仕様判断のため**未実施**、委任_06の実測で頻度を見て判断。(c) KP解説+1回(§1-C)。(d) JA UNCERTAINの通算3回再生成(04記録)。
3. **未実装(委任文外)**: Dialogue(Std)/Voices A2の外側ループ汎化(DESIGN §4-8)、見出しminimal2撤去(OPEN-288)。Dialogue Std減速後NGは再生成なしでSTOPPED(既存挙動)。委任_06以降で判断を要する。
4. **委任_07へ**: (i) `_post_slowdown_cascade_rescue`・`en_validator` importの整理(test3ファイルが参照)、(ii) 各leafの到達不能`if stop_retrying:`削除、(iii) A2減速後の`post_slowdown_cascade`キー意味の変更(Secondaryが走った場合に付与、旧はUNCERTAIN限定)をDECISION_LOGへ、(iv) Cの`.ok`メタ・audit entryへのadditiveキー(`asr_judgement`/`asr_judgement_inherited`)記録、(v) `OPEN_ITEMS`の旧Cascade記述(OPEN-146系・OPEN-270)更新、(vi) mainへのmergeはGate 4(`git revert --no-commit`予行含む)後。
5. **新仕様候補**: なし(承認済み設計の範囲)。ただし上記2(b)のadapter順序最適化は仕様判断。
6. **runtime evidence(委任_06)の入力**: 実音声対象=R6(A2減速1clip: `generate_a2_segment_with_slowdown`/Z Dialogue Std短clip、TTS≤3・ASR≤6・Azure≤3、DESIGN §9見積約JPY0.8)、KP解説の3回目発火確認(NG音声がある場合のみ)、B/C hook(既存音声でAPI 0再導出可)。本委任の追加分(KP解説+1/KP、減速後Secondary常時化)の実NG分布での増分は`attempt_history`から委任_06で試算。

## 7. 未実装 → 委任_06/07
- 委任_06: 実音声runtime evidence(R1〜R8)、増分費用試算(15-9: 70円/記事セット)、Melos regression(12/12)、「PASS→NG(旧PASSが新NG)全件確認」(ADDENDUM §10)。
- 委任_07: SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)、Gate 3/4/7、main merge、旧規則の整理(§6-4)。

## 8. commit後の確認
- commit: 4019b5fe10e35c937d3c0091a1b8769defe70ba6 (branch feat/auw-unified-asr-01, 961d5b360..4019b5fe1 push済み、main無変更)
- secret_scan_01 --staged: hits=0 (41 files)
- 有料API: 0 / JPY 0 (netguardで外部試行0)
- commit後gamma再確認(er019 FamilyAUnchanged / er020 ProductionModuleUnchanged / er064 ProductionUnchanged系): 14 passed, 1 failed。
  失敗1件は er064_kp_int_03 AssetsUnchanged::test_state_guard_if_present で、patch_04/test_post_04.json のbaselineにも同一failとして存在(共有state hash driftの既存失敗、本委任起因ではない)。新規failure 0。
