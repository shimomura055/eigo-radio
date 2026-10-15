# AUW 委任_04 IMPLEMENTATION (JA統一judge配線 + J11 + 静的監査post_wiring) -- branch feat/auw-unified-asr-01
JPY 0(mockのみ、Production API呼出0)。main無変更。A2減速/Dialogue/KP max_attempts/Prompt/model/voice/速度/閾値/HR Lock/予算guard/SSOT 無変更。U1=True, U2=A2_ONLY 維持(`er078_asr_unified_judge_01.py:65-66`、`git diff HEAD`で当該行無変更)。
証跡: `patch_04/test_post_04.json`(96+1ファイル per-file、通信遮断plugin付き)、`patch_04/test_post_04_fixups.json`、`patch_04/run_stdout.txt`。

## 1. 配線点 (file:line)
| 項目 | 場所 |
|---|---|
| JA adapter本体 | `er007_ja_secondary_asr_01.py:504 evaluate_attempt_ja_with_cascade_detail`(署名の既存引数・戻りdictの既存キー維持、`attempt_ctx`追加)。統一judge呼出 `:616 unified_judge_mod.unified_judge(..., lang="ja", ...)` |
| Secondary呼出(1回/SecondaryCache共有) | `:589 _secondary_fn`(`_azure_stt_strict`=SCG専用strict wrapperを再利用。Phrase Listなし。cost guard=実秒、JA_SCG_ENABLED緊急停止) |
| Secondary許容集合 | `:602 _secondary_accept`: EXACT/NORMALIZED(`SCG_PASS_CLASSIFICATIONS`、10/11承認の2ラベル)+ORTHOGRAPHIC_VARIANT_CONFIRMED(Primary#1+Secondary#1の2エンジン確認)。`allow_reading_resolver=False`(LLM呼出なし) |
| 数値の値等価層(Primary側) | `:482 _numeric_value_equivalence`(値ガードEQUAL+数値トークン置換後の残り完全一致のみ。`三十人=30人`、`百円=100円`) |
| signals(従来のSCG除外条件と同一判定) | C1=`_scg_c1_reason`、C2=`_scg_c2_candidate`、類似度<0.4=`SCG_MIN_SIMILARITY`(U1現行維持)、per-span否定/fugashi否定マーカー差/数字不一致[値ガードUNKNOWN・NO_VALUES時]=`signals["protected_diff"]` |
| judge側 | `er078_asr_unified_judge_01.py:369-375` P1に`signals["protected_diff"]`を追加(additive。NG_PROTECTED、Secondary不呼出) |
| wrapper | `er007_ja_secondary_asr_01.py:689 evaluate_attempt_ja_with_cascade`(戻りtuple同形、`attempt_ctx`/`detail_out`追加) |
| JA leaf(asr_judgementをattempts_log+OK戻りへ) | `er003_v1_sing01_voice01_generate.py:517,567`(標準/fallback)、`er003_v1_n3_01_tts_generate.py:659`(fallback)、`er003_v1_repro01_main_generate.py:374`(標準経路のJA分岐) |
| J11 | `er019_family_x_validation_inheritance_01.py:227 rejudge_with_current_judge`、`:213 _j11_adopted_judgement`、`:115 build_inherited_entry`(`asr_judgement_inherited`) |
| 静的監査 | `er078_asr_unified_wiring_static_audit_01.py` + `er078_asr_unified_wiring_allowlist_01.json`(phase=post_wiring、35 entry) |

状態遷移(JA): Primary PASS→最終ANDゲート(値DIFF/否定差。READING_MATCH[PHONETIC_MATCH/READING_RESOLVED_MATCH]は再否定しない)→PASS/PASS_WITH_WARNING。Primary NG→P1(値DIFF/否定差/protected_diff)=NG_PROTECTED[Secondary不呼出]→P2(length NG・C2・[U1]類似度<0.4・C1)=NG_EXCLUDED→P3 Secondary 1回: 取得不能=NG_SECONDARY_UNAVAILABLE、転写に保護差=NG_BOTH、許容集合PASS=PASS_WITH_WARNING(SECONDARY_CONFIRMED)、値AMBIGUOUS(十分/10分)は原稿と同表層のSecondaryのみ`NUMERIC_AMBIGUOUS_SURFACE`。stop_retrying=False固定、HRはattempt_ctx.is_last_slot且つNGのみ(JA leafは未配線=最終STOPPEDは従来どおりleafのHR Lock経路)。

## 2. caller互換表(JA全呼出点)
| 呼出点 | 呼ぶ関数 | 使うキー | 互換 |
|---|---|---|---|
| voice01 `generate_charon_japanese` 標準 `:517` / fallback `:567` | wrapper tuple | verified, stop_retrying, cls(`.classification`,`.scg_info`,`.reading_resolver_info`) | tuple同形。`cls.scg_info`維持(TCM時)。additive: `detail_out`→`asr_judgement`をattempts_logとOK戻りへ |
| n3 `generate_a2_japanese_with_fallback` `:659`(fallback) | wrapper tuple | 同上 | 同上。`r["asr_judgement"]`追加。標準経路は下のrepro01 |
| repro01 `generate_narration_snippet_verified_strict` `:374`(JA分岐) | wrapper tuple | 同上 | 同上(`asr_judgement`はEN/JA共通キー化) |
| er038 trial `:354,:393`(DEV専用) | wrapper tuple | 同上 | 署名不変。test(`er038_..._test_01`)16 passed |
| `stop_retrying`消費箇所(各leaf `if stop_retrying: return ASR_VALIDATION_UNCERTAIN`) | - | - | 以後常にFalseで到達不能(コードは無改変で残置。整合は§6) |
| 戻りdict(`detail`)の既存キー | verified/stop_retrying/classification/cascade_invoked/steps/final_status/human_review_required/canonical_text/wav_path/scg_applied/scg_result/scg_info | 維持(test: `test_detail_keys_superset_and_wrapper_tuple_and_detail_out`) |
steps名: SCG経路=`scg_secondary`、UNCERTAIN経路=`secondary_1`(従来名維持)。`primary_2`/`secondary_2`は発生しない。final_status: TCM+Secondary採用=`SECONDARY_CONFIRMED_PRIMARY_FALSE_NG`(従来値維持)、2エンジン確認=`ORTHOGRAPHIC_VARIANT_CONFIRMED`、数値等価=`NUMERIC_VALUE_EQUIVALENT_MATCH`(新)。

## 3. Section固有例外の維持(新例外ゼロ)
| 例外 | 所在・維持の証拠(file:line) | 本委任の影響 |
|---|---|---|
| 日本語LR原則HR(JA Local Rewrite禁止) | JA leaf `generate_charon_japanese`(voice01 `:434` `@guarded_generate("ja")`)/`generate_a2_japanese_with_fallback`(n3 `:590`)に`run_local_rewrite_recovery`呼出なし(`grep run_local_rewrite_recovery`: crosslevel `:421`/news_tail_fix `:369`/voice01 `:360`[EN]のみ)。3NG→`{"status":"STOPPED"}`(voice01 `:604`、n3 `:707`)→`record_outcome`→HR Lock。judge/adapterは`LR`状態を持たず`local_rewrite`語を含まない | 無変更。test `test_ja_adapter_and_judge_have_no_local_rewrite_path` / `test_ja_leaf_functions_do_not_call_local_rewrite_and_end_in_stopped_for_hr_lock` |
| 日本語KP(Key Phrase meaning/gloss)の原則HR | KP日本語gloss=`n3.resolve_key_phrase_ja_gloss_tts`(n3 `:416`)→上記`generate_a2_japanese_with_fallback`経路。LR対象外・Lockは`guarded_generate("ja")`(n3 `:590`)。`er011_human_review_lock_01.py`は`git diff HEAD`で無変更(test `test_hr_lock_module_not_modified_by_wiring`) | 無変更。KP max_attempts 3化は委任_05 |
| 見出し・短文の独立QA | EN見出し=`sing01_point_headings_aoede`(J6、EN adapter経由、委任_03)。日本語の見出し相当(japanese_title/preview)は同じJA adapter経路。length NG(A3)は除外表で維持 | 無変更(minimal2撤去は委任_05のOPEN-288) |
| A2 6%減速 | `apply_a2_slowdown_postprocess`(n3 `:172-282`、EN)は本委任で未変更 → 静的監査の`a2_slowdown_pending_delegation_05` 2 entry | 委任_05 |
| Dialogue | `er063`の話者帰属Gate/voice割当は未変更 | JA経路を壊さないこと: `er063`系test(per-file 96ファイル)新規失敗0 |
| 構造の保存 | JA leafのattempt上限(`PRODUCTION_MAX_TTS_ATTEMPTS`=3)・fallback(minimal)・Lock・budget guardは無変更 | - |

## 4. J11(引継ぎ・再利用の再判定)
- `rejudge_with_current_judge(entry, level, label)`は、(EN)保存`asr_text`を現行`classify_asr_match`でPrimary再導出→(JA)日本語Primaryは再導出せず元の正式Validation(status=OK/asr_verified=inheritanceの前提)を維持→**`unified_judge`の最終ANDゲート**を採用転写に適用。Secondary新規呼出は行わない: `secondary_fn`は元entryに保存済みSecondary転写(`asr_judgement.secondary.text`/`scg_info.secondary_transcript`)を返すだけ、無ければ取得不能(PASS不可)。`secondary_new_calls`=0を戻り値に記録。
- 元entryが`asr_judgement`(PASS_WITH_WARNING等)を持てば`asr_judgement_inherited`へ移し(`build_inherited_entry` `:115`)、元のWARNINGを継承(警告は再導出分と合成)。`rec["inherited"]={via:"J11_rejudge_with_current_judge", api_calls:0, secondary_new_calls:0,...}`。試聴リスト(registry)に`inherited=True`で載る(test `test_j11_inherits_original_warning_and_uses_stored_secondary_only`)。
- 追補§3-1「保存転写に対して最終ANDゲート(値ガード+protected_check)をAPI 0で再適用し、WARNINGを再導出する」に一致。**JA Primary再導出を行わない根拠**: Reading Resolver(LLM)=API/課金を避ける(API 0)、既存の正式Validation結果を尊重(追補§3-1は「最終ANDゲートの再適用」と規定)。逸脱ではない。
- 旧: JAは`JA_SEGMENT_F1_NOT_APPLICABLE`(適用外)→新: 適用(F1自体は英語連結発音のため`f1_version`は返さない)。旧testは α更新(§7)。
- 実データ(既存run `coffee_prices__run_m2p0_n01_01/a2`、読取のみ・API 0): JA 5〜6件(japanese_title/preview/comment_1-4)が全てok=True(test `test_j11_real_stored_results_offline_rejudge_api0`)。
- 呼出元: `er019_family_x_clobber_restore_03.py:75`(`rj.get("applicable") and not rj.get("ok")`で拒否=同契約)、`rebuild_state`(`:301`)。

## 5. 静的監査snapshot(phase=post_wiring、35 entry)
カテゴリ別: primary_acquisition 8 / adapter_internal 8(EN adapter 4+JA adapter 4) / en_adapter_entry 7 / ja_adapter_entry 3 / library_internal 2 / safety_qa 2 / j11_unified_judge_entry 2 / diagnostic_not_judgement 1 / **a2_slowdown_pending_delegation_05 2**。deferredカテゴリ(ja_unwired/j11_deferred/diagnostic_unconfirmed)=**0**。
test(15 passed): snapshot完全一致、全entryがALLOWED_CATEGORIES、`category_for`再導出一致、EN leaf6 module+JA leaf3 moduleが統一judgeへ到達(`_closure`)、EN/JA両adapterが`er078_asr_unified_judge_01`をimport、判定点J1〜J6/J5・J8・J9・J10にadapter入口あり、judge/adapter以外の直接`classify_*`呼出は adapter/library内部・J11[unified_judge呼出をAST確認]・A2pending のみ、J11関数がtranscribe/Azure関数を呼ばない(AST)、Family C `get_or_run_asr`が判定系を呼ばない。
- **要判断(逸脱)**: 委任文Dの「deferredカテゴリ0」は、A2減速の直接判定2 entry(`apply_a2_slowdown_postprocess`の`en_validator.classify_asr_match`/`routing.transcribe`)が委任_05範囲のため、**カテゴリを`a2_slowdown_pending_delegation_05`として分離し「既知集合と完全一致」をassert**した。0件化は委任_05でA2を統一judge化した後に`A2_PENDING_ENTRIES`を空へ締める(本委任でA2に触れない=範囲拡大しない)。
- Family C `er013...get_or_run_asr`(DESIGN未列挙・未確認だった診断ASR): 確認済み=結果はaudit `asr_text`と`comment_consistency.json`の`match`(緩い文字列一致)に記録されるだけで、`asr_verified`/Gateに使われない(`er013:716-728,926`)。`diagnostic_not_judgement`へ再分類。

## 6. 残存・撤去した旧規則(Grep)
- 撤去: JA `Primary#2`(`routing._transcribe_openai_mini`呼出)、`Secondary#2`、4段尽きHR直行(`stop_retrying=True`)、JA cascadeの`p4.get_full_text_via_azure_stt_continuous`(90秒)呼出。Grep(Production): `_transcribe_openai_mini`の呼出は`er006_asr_provider_routing_01.py:107`(routing内部のopenai route)のみ。`primary_2`/`secondary_2` stepは`er007_ja_secondary_asr_01.py`に存在しない。
- **Primary#2を使う残存caller/test(表)**:
  | ファイル | 用途 | 扱い |
  |---|---|---|
  | `er008_n8_revalidation_15.py:61-66` | 評価script(`step_texts["primary_2"]`をmockしてdetailを再生) | DEV/評価専用・未実行。新adapterでは`primary_2`が出ない=旧再生は意味を持たない(記録のみ、変更せず) |
  | `er007_openai_ja_asr_quality_test_01/02.py:81,43` | OpenAI mini ASR品質を実測するscript(`test`名だがpytest収集0件) | 実API呼出scriptでProduction経路外。変更せず |
  | `er007_ja_secondary_asr_01_test.py`(`_forbid_primary_2`等) | 廃止の確認(呼ばれたらfail) | 意図した残置 |
  | `er007_ja_cost_latency_projection_01.py:82`、`er007_ja_tts_retry_path_fix_cost_01.py:175`、`er006_retry_cascade_prod_01_eval.py:6` | コメント/試算のみ | 変更せず |
- 残置: `VALID_CLASSIFICATIONS_JA`(`er007_ja_asr_validator_01.py:35`)は定義のみで参照ゼロ(Grep)。新ラベル`NUMERIC_VALUE_EQUIVALENT_MATCH`は追加していない(下流に許可リストが無いため不要)。
- 残置(到達不能): 各JA leafの`if stop_retrying: return ASR_VALIDATION_UNCERTAIN ...`分岐(`stop_retrying`が常にFalse)。無害のため無改変(委任_05/07で整理候補)。

## 7. test数値
- 新規 `er078_asr_unified_ja_wiring_test_01.py` **51 passed**(状態機械/値ガード[三人vs四人・三十人vs40人・25%vs26%・150vs140・十分vs10分]/数値等価[三十人=30人・百円=100円・1万2000人=一万二千人]/否定再否定ゲート/U1現行維持と解放挙動/C2・length・SCG緊急停止/COST_GUARD[200秒で不呼出・179秒で呼出]/SCG費用式値不変/重複防止[同一wav 1回・失敗非cache・run cache共有・circuit breaker]/2エンジン確認/Section例外維持/呼出元互換/e2e mock[voice01 JAでPrimary NG・Secondary PASSが最終成果物PASS_WITH_WARNING+試聴リストJSON+HTML節]/J11/OF-AUW-17)。
  変異確認: 値ガードDIFF検出を無効化するとDIFF系3 testが失敗(検出力あり)。
- 静的監査 15 passed。EN配線53/judge45/value_guard58/registry9: 全PASS。
- 9系統+er007+er019 per-file(`patch_04/test_post_04.json`、通信遮断plugin付き、W=1直列): files=97(baseline 96 + 新規1)、passed 1,728 / failed 31。baseline(`patch_03b/test_post_03c.json`: 1,679 / 30)に対し**新規失敗2件**(下記α)を同委任内で更新→再実行して解消(合成: passed **1,731** / failed **29** =全てbaselineと同一id)。baselineから消えた1件=`er026_family_z_e2e_integration_test_01::test_shared_state_files_unchanged_by_mock_run`(作業ツリーの未commit出力に依存して揺れる既知の件)。
- 追加実行(prefix外でJAに触る4ファイル): er009 JA foreign token 26 / er038 trial 16 / er058_asr_tts_prodfix 27 passed、er025 b1b EN wiringは1 failed(`KeyError: 'part2'`=`er019_family_x_audio_production_runner_01.py:895`の入力データ起因。runner無変更・JA無関係・96ファイル外でbaseline無し。記録のみ)。
- 29件の残存失敗(全てbaseline既存): gamma系4(未commit-diff guard: er019 FamilyAUnchanged, er020x2, er064 ProductionUnchanged→commit後に再確認)、er007 koro/single_engine 2(§8)、er006 provider routing 2/kp5 4/pricing 1、er011 open112 3、er020 fullseg 1、er026 cs_audit 4/post_slowdown 3、er064 3+2(tokens/state/runner safety)。
- 通信遮断ログ(`scratchpad/ng04/netguard_attempts.log`): 試行は既存testのみ=api.openai.com(`er007_ja_secondary_asr_01_test::test_unrelated_kanji_reading_not_confirmed`[Reading Resolver=既存Production挙動のLLM] 3件+test外3件)、huggingface.co(er011_open121/er011_open128 各1)。**本委任で触ったtest/新規testからの外部通信は0**(新規ファイルは全てmock、遮断ログに該当test名なし)。既存test由来はmock化せず記録のみ(指示どおり)。

## 8. α/β/γ区分(旧cascade前提の既存test)
| test | 区分 | 内容 |
|---|---|---|
| `er007_ja_secondary_asr_01_test::test_entity_like_mismatch_triggers_primary_2` → `..._triggers_secondary_once_without_primary_2` | α(経路) | Primary#2廃止。Secondary 1回・steps=[primary_1,secondary_1]・両NGでverified False |
| `::test_primary_2_pass_stops_cascade_before_secondary` → `test_secondary_exact_confirms_uncertain_entity_as_pass_with_warning` | α(経路) | Secondary EXACTでPASS_WITH_WARNING。誤PASS側(Secondary不一致)は別testで維持 |
| `::test_full_cascade_all_fail_routes_to_human_review` → `test_both_ng_goes_to_next_regeneration_and_hr_only_at_last_slot` | α(回数/HR時期) | HRは最終slot(attempt_ctx)のみ。stop_retrying=False |
| `::test_expected_readings_forwarded_to_primary_2_step` → `..._to_secondary_step` | α(経路) | 転送先をsecondary_1へ。TRUE_CONTENT_MISMATCH判定(転送の有無)は同じ強さで固定 |
| `::test_expected_readings_none_is_fully_backward_compatible` → `..._secondary_not_exact_is_not_auto_pass` | α+安全側強化 | 旧=Primary#2の偶然一致でPASS(既知の欠落挙動)→新=Secondary不一致ならPASSしない |
| `er007_ja_scg_test_01::test_uncertain_entity_path_unchanged_no_scg` | α(経路) | Primary#2→Secondary 1回。scg_info無し・SCG_FINAL_STATUSでない点は維持 |
| `er007_ja_scg_test_01::test_rec6_callers_pass_length_ok` | α(source文字列) | 呼出が`detail_out=`を追加で渡すため、length_ok転送のsource countを接頭辞一致へ。「全leafがlength_okを渡す」不変条件は維持 |
| `er019_test_family_x_validation_inheritance_01::test_f1_rejudge_not_applicable_for_japanese_labels` | α(仕様更新=J11がJA適用) | 適用=True・secondary_new_calls=0・値DIFFはok=False |
| `er011_open121_...::test_japanese_branch_never_invokes_repetition_qa_even_if_flag_passed` | α(mock署名) | fakeのシグネチャに`attempt_ctx`/`detail_out`を追加(repetition QA非呼出の検証は不変) |
| β(最終判定の固定でadapter側を直す必要があったもの) | **0件** | JA SCG系46+c2_neg17+phase0 12の最終判定assertは全て無変更で通過(Secondary独立確認・除外条件・誤PASS 0の期待値は変えていない) |
| baseline既存失敗 `test_koro_kanji_variant_confirmed...` / `test_single_engine_repetition...` | 既存失敗のまま(要記録) | OPEN-145のVariant層(Candidate D-2)が`ころ/頃`をPrimaryで`PHONETIC_MATCH`へ引上げるため、旧Cascade前提のORTHOGRAPHIC_VARIANT_CONFIRMEDに到達しない。本委任で悪化なし。2エンジン確認の制御は`test_orthographic_variant_requires_two_engines`(mock)で固定 |
| γ | 4(commit後に再確認) | 未commit-diff guard |

## 9. 受入観点(ユーザー原文)との照合メモ
- L54「Primary NGは不一致の種類によらず原則Secondary」: JAも、値DIFF/否定差[保護差=L97優先]とP2除外[length・C2・U1現行維持のC1/類似度]以外は全てSecondary 1回。UNCERTAINもSecondary対象。
- L55「Secondary PASS→PASS_WITH_WARNING自動採用」: e2e mockで最終成果物のstate=PASS_WITH_WARNING+試聴リスト掲載を確認。
- L97相当: 値DIFF/否定差はSecondaryがPASSでも不採用(test: Secondaryが原稿一致を返すmockでも`NG_PROTECTED`、Azure呼出0)。
- ユーザー必須正例/負例(JA): 三人↔3人 許容 / 三人↔四人 不許容 / 三十人↔30人 許容 / 三十人↔40人 不許容 / 十分↔10分 同表層のみ / 100円↔百円 許容(`100円で`↔`百円で`) / 25%↔26% 不許容: 全てtestで固定(§7)。`20%↔20 percent`のEN側はEN adapter(委任_03)。JA `20％↔20パーセント`はPrimaryで救わずSecondary判定へ(「パーセント」を助数詞辞書に持たないため。誤PASS側ではない)。

## 10. 未実装 / 逸脱 / 委任_05・06への注意点
- **未実装(委任_05)**: A2 6%減速後の再検証の統一judge化(静的監査の`a2_slowdown_pending_delegation_05` 2 entry)・Dialogue(Std)/Voices A2の外側ループ汎化・見出しのminimal2撤去・KP max_attempts 3回化。**未導入**: runnerへの`begin_secondary_run()`(JAもEN adapterのrun cache/circuit breakerを共有できる配線は済み=`_shared_run_cache_and_state`、test済み)、leafへの`attempt_ctx.is_last_slot`/`slot`/`script_version`の受渡し(JAのHR queue投入は未配線のまま=従来のleaf HR Lock経路)。
- **逸脱(要Fable確認)**:
  1. 静的監査の「deferredカテゴリ0」はA2 2 entryを`pending_delegation_05`として分離(§5)。
  2. DESIGN_01 §5-2が指す`protected_check_ja`の`_DIGIT_RE`分岐の置換は**validatorを編集せず**、adapter側の「値等価層」(`_numeric_value_equivalence`)で同効果(表記差のみ=Primary PASS、DIFF=NG_PROTECTED)を実現した(`er007_ja_asr_validator_01.py`は無変更=既存test `er007_ja_asr_validator_01_test`等への影響0。既存の`number_mismatches`は引き続きprotected_checkが記録し、adapterが値ガードで解釈)。
  3. JA UNCERTAIN経路のSecondary許容集合は縮小(OF-AUW-08 R+): 旧=Secondary#1が`should_pass`(PHONETIC_MATCH含む)ならPASS→新=EXACT/NORMALIZED+ORTHOGRAPHIC_VARIANT_CONFIRMED(2エンジン)のみ。DECISION_LOGへの記録文案は委任_07。
- **挙動変化(費用/件数に関わるため委任_06の試算に要反映)**: JAのUNCERTAIN(固有名詞/濁点ゆれ)で従来Cascade尽き→`ASR_VALIDATION_UNCERTAIN`即返却(TTS再生成せずHR)だった箇所が、統一フロー(D-7: 両NG→次のTTS再生成)により通算3回まで再生成する。TTS呼出回数が増える可能性(Secondary呼出は4回→1回に減る)。実NG分布での増分費用は`attempt_history`から委任_06で試算。
- **新仕様候補**: なし(実装は承認済み設計の範囲)。ただし上記2(adapterでの値等価)はDESIGN §5-2の実装形態の選択。
- 委任_07向け: 旧2 test(koro/single_engine)の扱い(削除またはVariant層前提の期待へ更新)はuser原文L97/承認範囲に影響しないが、期待値変更に当たるためFable判断を推奨。OPEN-146系の旧Cascade記述(SSOT)はP#2/S#2/HR直行廃止の反映が必要。

## 11. commit後の確認
- commit 9fb1d7fec9d5(branch feat/auw-unified-asr-01へpush済、main無変更、20 files、`secret_scan_01 --staged` hits=0、`docs/pm/RESULT_PACKET_AUW4.md`は.gitignore対象のため非コミットのローカルファイル)。
- gamma(未commit-diff guard)4 id(er019 FamilyAUnchanged / er020 ProductionModuleUnchanged x2 / er064 ProductionUnchanged[class全体7件])をcommit後に再実行: **7 passed**(gamma解消)。したがって残存失敗29件のうちgamma 4件は解消、残り25件がbaselineから変わらない既存失敗。
