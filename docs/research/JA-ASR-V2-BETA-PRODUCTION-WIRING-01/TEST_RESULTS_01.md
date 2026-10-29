# TEST_RESULTS_01(JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A)

実行系: `.venv/Scripts/python.exe`(Python 3.14.6)。合格基準(委任文§2-3)=『HEAD失敗ID集合からの新規失敗0』+新test全PASS。

## 1. 先行commit(配線commitと分離): HEAD失敗test 5件の是正
commit `8368add34`「委任_02A-0: 既存失敗test5件是正」(Production挙動変更0・API 0)。原因確認 -> 不変条件で修正:
- `er007_ja_secondary_asr_01_test.py` 2件: ころ/頃はVariant Layer D-2(CURRENT_SPEC)でPrimary単独のPHONETIC_MATCHでPASSする。ORTHO確認ラベルを単一エンジンの繰返しで出さない不変条件へ。
- `er109_xz_isolation_01_test_01.py` 2件: Trial/fake 4 scriptを具体名で`DEV_TRIAL_SCOPE_SCRIPTS`へ追記(Productionからimport 0の検査は維持)。
- `er078_asr_unified_wiring_05_test_01.py` 1件: 基準commitを`6e7fa7cf5`へ更新+`961d5b360`からコード(非コメント行)同一の不変条件を追加。
承認済み仕様からの逸脱は見つからなかった(testの期待値が古かっただけ)。

## 2. 新規test(112件、全PASS。`.venv/Scripts/python.exe -m pytest er078_ja_v2beta_01_test_01.py er078_ja_v2beta_wiring_test_01.py -q` -> 112 passed)
| file | 件数 | 主な内容(TEST_PLAN §2・Opus M-1〜M-6/R-9対応) |
|---|---|---|
| `er078_ja_v2beta_01_test_01.py` | 74 | v2読み規則(助詞は->わ・数詞表記同値)T-L1、汎用題positive 10(PASS_W・Azure 0)/negative 6 x Secondary 3条件(新層の寄与0)、metamorphic(題材語差替え・前置き追加で不変)T-G3、M-1(不規則読み数詞は救済しない)、B-light β T-B(観測形のPrimary数字崩れのみ・非観測形4種は説明されない・Secondary失敗/circuit open/precheck偽ではAzureを呼ばない・M-3 Primary長さNGは救済しない・M-7 `phrase_list_hash`空/来歴欠落でfail-closed・R-1 no_speechはβ入力にしない・否定/P2除外では発火しない)、M-2(β費用=監査record=RunState)・sha共有で重複課金なし、M-6(E3/E4があれば全新層ブロック)、T-W1(新層の救済は必ずPASS_W、clean PASSにならない)、R-3(実効経路で`rescue_basis`決定)、R-7(定数OFFで従来判定+`disabled_by`記録)、scope外でキー無し、T-D1(`JA_V2_BETA_ENABLED is True`・読取は`is_active_for_run()`内のみ[AST])、T-D2(撤去ルールの残存0)、T-G1/G4(題固有語・記事ID参照なし)、NB5(制御フローが報告専用fieldを読まない)、NB6(公開/配信機構なし)、**M-4(判定核hash pin: 核を変えて`JUDGE_RULE_VERSION`を上げ忘れると失敗)**、R-9(a) precheck健全性(評価コーパス全行で composite成立 -> precheck成立) |
| `er078_ja_v2beta_wiring_test_01.py` | 38 | T-P1(月6本 = 4 PASS_W / 2 HR。βは保存転写を残す)、T-A1(scope外396判定のバイト一致=HEAD金型)、T-NB1(PASS_W非ブロッキング: adapter/wrapper/HR queue)、再試行loop(PASS_Wで終了)、M-5(依存欠落/例外 -> 従来判定へフォールバック+`ja_v2beta.error`記録、`is_config_stop_error`は再送出)、Store再利用(M-4: 印の無いentryに作用しない・scope外で再利用しない・版違いはAPI 0再判定)、J11継承、registry/完了ブロック(R-6/R-8: 内訳・無効化件数・HR一覧・Y節[dev限定]・X/Z節との整合)、import graph(scope外は新module・重い依存をimportしない)、R-9(e) E0 runnerが本番results/Store/承認記録へ書かない(静的)、**T-P3(proto逐行parity 2,103行0不一致・負例増分=既知8行と行集合同一・回帰0・新層例外0・R-4=0)**、ヘルス集計の二重計上防止 |

## 3. 既存regression(TEST_PLAN §1。162 file = `er078_*/er007_*/er109_*/er127_*/er130_*/er019_*/er121_*/er063_*/er026_*/er006_*/er011_*` の `*test*.py` 全件 + TEST_PLAN列挙分。4並列shard)
- 最終実行: **3,409 passed / 18 failed**(2,500超のsubtest含む)。
- 18 failedの内訳:
  - **14件 = HEADのクリーンcheckout(git worktree)でも同一メッセージで失敗する既存失敗**(新規失敗0): `er109_wiring_golden_test_01.py::GoldenSignatures` 3、`er006_asr_provider_routing_01_test.py` 2、`er006_kp5_canonical_bug_01_test.py` 4、`er019_x_std_chunk_opus_test_01.py::R4HunkClassifierTest` 1、`er063_fz_ctx_wiring_test_01.py::test_w11b...` 1、`er078_asr_unified_wiring_static_audit_01.py::test_asr_call_inventory_matches_allowlist` 1(**diff集合[unlisted 3 + count_changed 1]がHEADと完全一致**=本変更は寄与していない)、`er121_family_y_structure_match_test_01.py::test_a2_common_calls_not_dropped` 1、`er063_family_z_audio_01_test_01.py::WiringTest::test_preview_comment_kp_styles` 1(mainの作業ツリーのみ: 過去のtest実行が残した未追跡`x/a2/audit/review_lock_state.json`[2026-10-28]がHR Lockを返す。クリーンcheckoutでは通る。OPEN-588)。
  - **4件 = 本変更と無関係**: `er121_*_test_no_network_or_real_client_attempts` 3(`er121_family_y_audio_chunk/hr_approval_guard/std_chunk`)は4 shard並列実行時のみ散発(直列では3件ともPASS。初回の並列実行でも別組合せで散発)。`er121_family_y_voice_table_test_01.py::test_existing_run_01_and_public_pages_not_modified` は**並行Workerが編集中の`user_test/selection_form_v3/form_logic.js`・`index.html`**(git status `M`)を検出して失敗(本ID・本変更は`user_test/`を編集していない)。
- 初回の並列実行で見つかった**本変更起因の失敗3系統は是正済み**(再実行でPASS): (1)`er078_asr_unified_ja_wiring_test_01::test_new_ja_label_is_not_embedded_in_any_downstream_allowlist`(新moduleのコメントに既存ラベル名を書いていた -> 削除。ラベルは`value_label`引数でadapterから渡す)、(2)`er078_asr_r5_measurement_test_01::test_unknown_keys_are_not_read_by_registry`(registryが`r5`を読んでいた -> `asr_models`欄を廃止。model_idは判定record本体の`r5.models`に残る)、(3)`er078_asr_unified_wiring_static_audit_01::test_post_wiring_every_entry_has_known_category`・`..._ja_phase_dependent_wiring`(新moduleのadapter内部呼出を`category_for`と許可moduleに追加)。
- 並列実行の注意: shard間でProductionの共有state(HR queue・attempt_history等)を触るtestが散発失敗する。判定は『単独/直列で再実行して通る』ことで行った。
- 旧規則・旧検査の撤去/残置(Grep): 撤去したProduction規則は無い(新規additive)。`test_t_d2_removed_rules_are_not_present_in_production`で、委任文が不採用とした規則(ASR再試行・L3別表・R-1コード・veto・自動公開)の識別子がProductionに0件であることを固定。

## 4. 追加の不変性確認
- scope外(None=Family A/B/C・単体呼出)バイト同一: HEAD(`8368add34`)で`tools/gen_golden_scope_none_01.py`が生成した396判定(月6本+評価コーパス抽出 x 2 ctx)の出力sha256 `9c0f740fe0a6...` と現行コードの出力が一致(`test_t_a1_scope_none_output_is_byte_identical_to_head_golden`)。金型=`golden_scope_none_head_01.json.gz`。
- E5(runtime、API 0): 保存済み転写6本をscope外で判定 -> 新キー(`ja_v2beta`/`verdict`/`rescue_basis`/`judge_rule_version`)は全行で無し、従来のNG判定(`RUNTIME_EVIDENCE_01.md` §1)。
- `unified_judge`(`er078_asr_unified_judge_01.py`)・`er011_human_review_lock_01.py`・HUMAN_APPROVED関連は無改変(`git diff`で差分0)。
