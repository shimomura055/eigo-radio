# RUNTIME_EVIDENCE_01 -- ②英米綴り(UKUS) Production実装 X runtime evidence + Z手順(B工程向け)
(UKUS 委任_04 / 2026-10-23 / commit 719de3adc。Z evidenceは**本委任では未実行**[後続B工程]。PRODUCTION_WIRED判定はFable受入後=X/Z双方のevidence必須)

## 1. X: 正式TTS段の実run(W-08(1)) -- 陽性証拠(証拠区分: **実run・発火あり**)
- 入口: `er019_family_x_audio_production_runner_01.generate_family_x_b1_segments`(`@er109_scope.family_scope("X")`付きの本物のX正式TTS段関数。`__er109_scoped__=="X"`を確認)。呼出script=`er109_ukus_runtime_evidence_01.py`(隔離run_dir=`er109_output/ukus_prod_01/x_formal_tts_run`、検証用segment textを`parts.json`に与えた。**既存run・既存canonical本文は無改変**)。scope/flagはProduction同一(hook差し替え・monkeypatchなし)。TTS backend=`speech_metadata_flash_lite`(承認済み正式)、`_ONLY_SEGMENTS={"full_story_part1"}`(CLIの`--only-segments`と同じmodule global)、shared narration/KPは非実行(Store書込なし)。
- 検証用text(UK専用綴り4語): `The organisation opened a new centre in the city. Its programme for colour printing began last week.`
- 結果(`x_formal_tts_part1.json`): **1 clip・attempt 1で発火して停止**(上限3clipのうち1clipのみ使用)。
  - ASR転写(Primary/OpenAI): `The organization opened a new center in the city. Its program for color printing began last week.`(米綴り化)
  - 判定: `state=PASS`(reason_code=primary_pass)、`warnings=[]`、`primary.label=ORTHOGRAPHIC_EQUIVALENT_MATCH`、**`orthographic_equivalence.sites[0].er109.rules=['ukus_spelling_variant','cmu_homophone']`**、`version=er109_orthographic_equivalence_v2_ukus01`、`scope=X`、`ukus_table_sha256=c5598eb6…2dee`。
  - `ukus_pairs`: `organisation/organization`(T1・varcon・both・**pron_differs=true**)。centre/center・programme/program・colour/color は既存の`cmu_homophone`(CMU同音)で合格(UKUS層に入る前に既存判定が合格=救済関数は呼ばれない)。
  - 費用・副作用: Secondary(Azure)呼出0(`secondary.called=false`、`azure_calls=0`)、retry 0(attempt 1でPASS)、LR 0、cooldown 0、HR 0、`human_review_required`なし。TTS 1 call=0.085円(cost_log)+OpenAI ASR 1(推定1円未満)。**合計 < 1円**(上限10円)。
  - 実行scope外の確認: `ukus_run_evidence_outside_scope = {scope:null, ukus_active:false, layer_version:v2_ukus01, ukus_flag:true, table_sha256, active_pairs:6361}` -- scope外では`ukus_active=false`。run summary記録関数`er109_xz_scope_01.ukus_run_evidence()`の戻り値例。
  - STOP確認: `stop_check_before_tts.json`(rc=0、非停止)。他agentの有料run(TTS)なし(python process一覧で確認)。再起動なし(1回のみ)。
  - 共有追記型ログへの副作用: `er011_output/attempt_history.jsonl`(+4,315 B、本番関数が追記)のみ。`master_audio_store_01/manifest.json`・`pronunciation_ledger_01/ledger.json`・`human_review_queue.jsonl`は不変(`shared_files_before/after.txt`)。
  - 音声: `er109_output/ukus_prod_01/x_formal_tts_run/b1b/narration/full_story_part1.wav`(sha256 `547c5e37…5494`)。git未追跡。**試聴確認点(W-09類似)**: `organisation`はpron_differs=true(TTSが英式[/ɒɡ-/]で読んだか米式で読んだかは対表上区別しない)。
- 証拠区分の整理: **実run発火(上記)**。非発火の記録のみではない(W-08の求める陽性証拠)。

## 2. API 0: V6行列(Primary/Secondary/KP票/継承再判定/Store guard × X・Z)の再実行(W-08(2))、hook差し替えなしの実コード
- `er109_ukus_spelling_01_test_01.py::Hooks`(T-E1〜E5、本物の`sec.evaluate_attempt_with_cascade_detail`/`kp3v.make_voter`/`vi.rejudge_with_current_judge`/`rvg.guard_entry`をscope内で実行、Secondary/Whisperのみmock)全PASS。
- golden UKUS合成行14件×5経路×X/Z(`WIRING/V6_matrix_golden_UKUS_rows_01.json`、`GOLDEN_CHANGE_01.md`): c12がadapter/adapter_kp/guard(REJUDGE_OK)/rejudge/voterすべてでOFF(配線前)=NG -> ON=PASS(`ukus_spelling_variant`)、負例(固有名詞/綴り差+実誤読/+実数値差/+not脱落/mum-mom/AMB逆方向/語数違い)はNG維持(数・否定差はNG_PROTECTED、Store guardはPROTECTED_DIFFでblocked)。
- 保存データ再判定(`DIFF_TEST_RESULT_stored_01.json`、6,158行): PASS->NG 0、Trial⇔Production差分0、NG->PASS 6行(すべて`ukus_spelling_variant`が原因)。

## 3. Z: 手順(B工程向け、本委任では実行しない)
対象: 『開いた窓』Advanced `full_story_part3_c12`(canonical `…Vera's speciality.`、現entryは`forte`音声[LR]、ユーザー指示B=原稿`speciality`のまま再生成し原稿と音声の一致を確認)。run=`er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01`、level=b1b。
0. 事前: `tools/stop_scope_check_01.py --managed-id <ID> --run-dir <run>` rc=0、他行の有料run(TTS)進行中でないことを確認・待機、`git status`でer063/er019/er109系の未commit変更がないこと(①RET実装が走っていれば完了・全回帰後に)。
1. **保全(W-02)**: `b1b/audit/{tts_generation_results.json,review_lock_state.json}`・`b1b/narration/full_story_part3_c12.wav`(+`_original`があれば)・`er011_output/local_rewrite_recovery/run_sf_prod_01/b1b/local_rewrite_recovery_full_story_part3_c12.json`・`writer/provenance.json`を `b1b/audit/preserved_c12_forte_01/` へコピーし sha256一覧を残す。追記型ログ(attempt_history等)は触らない。
2. **checkpoint確認(W-02(1))**: `b1b/audit/tts_checkpoint.json`(`_merge_checkpoint` er063:1325がcachedへ再注入し得る)が**不在**であること(2026-10-23時点で不在を確認済み)。存在する場合は該当c12キーの不在を確認し、あれば停止してFableへ報告。
3. **解除は『segmentsキー削除』ではなく`reuse_blocked`印(W-02(4))**: `tts_generation_results.json`の`segments.full_story_part3_c12`に `"reuse_blocked": {"reason": "UKUS_REGEN_USER_INSTRUCTION_B: Advanced forteをspeciality原稿一致へ再生成(ユーザー指示B 2026-10-23)", "date": "2026-10-23", "preserved_copy": "<保全copyのpath>"}` を付与(c12 entryのみ・他clipは不変)。`er078_reuse_value_guard_01.guard_entry`が常にblock(:46-49の`REUSE_BLOCKED_MARK`)、`er063.generate_or_reuse_z`(:764-768)が再生成し、旧理由は`reuse_value_guard_blocked_previous`へ自動記録される。
4. **累積カウンタ(W-02(3))**: c12の`review_lock_state`は`state=RESOLVED`・`cumulative_tts_attempts=4`・`cumulative_asr_calls=4`(上限`MAX_CUMULATIVE_TTS_ATTEMPTS=15`/`ASR=60`、1回のrunでTTS最大3 attempt=計7 < 15)。RESOLVEDはblockしない。attemptファイルは自動採番。実装時の確認は『`canonical_text_sha256`(`577510e1…a904a19`)が現行TTS入力hashと一致すること』のみ。
5. **再生成(1回のみ)**: `er026_family_z_fiction_production_runner_01.py --stage tts_b1b --only-clips full_story_part3_c12`(追加script・監督ループ・ラッパを作らない。再起動は委任文の許可回数のみ)。費用見込み: TTS 1+ASR 1(+Azure 0〜1) ≈ 0.4〜0.8円(失敗時retry3回で約1.5円)。
6. **検証**: c12 entryの`asr_text`が`specialty`(または英綴り)、`asr_judgement.orthographic_equivalence.sites[].er109.rules`に`ukus_spelling_variant`、`ukus_pairs`に`speciality/specialty`(**`pron_differs=true`**)、`audio_text_deviation`なし、`attempt=1`、LR 0、cooldown 0、HR 0、wav sha更新、他clip(Bertie HR Lock対象等)のentry shaが不変(全clip sha一覧の前後差分=c12のみ)。`writer/provenance.json`の`audio_text_deviations`のforte記録は**削除せず**「superseded by UKUS regeneration(日付・保全copy path・新wav sha)」の注記を追記(または本証跡で明示)(W-02(2))。
7. **失敗時**: ASR NG(UKUS層で救済できない転写)となればLRは既存どおり働く。その場合は保全copyから元のentry(forte版)を復元して停止・報告(復元はFable承認後)。
8. **B報告に明記する最終試聴確認点(W-09)**: c12は`pron_differs=true`(speciality と specialty は CMU上の音素列が交わらない対)。PASSでも**TTSがどちらで読んだかは判定上区別できない**ため、ユーザー最終試聴で『speciality』の読みを確認(Gate・基準変更ではなく残存リスクの明示)。
