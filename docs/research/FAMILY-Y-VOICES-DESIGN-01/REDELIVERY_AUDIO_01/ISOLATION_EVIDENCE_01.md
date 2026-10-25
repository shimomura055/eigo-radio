# ISOLATION_EVIDENCE_01 (委任_27: Production隔離の証跡。API 0)

取得: 有料前 2026-10-25T11:18:16.220847 / 有料後 (本ファイル生成時)。並行agent(Z TTS・X/Z Production等)が共有storeへ書込む可能性があるため、shaが変化した場合は変化が本Trial起因かを下記で判定する。

## 1. 共有ファイルのsha比較

| file | before sha256 | after sha256 | 変化 |
|---|---|---|---|
| er006_output/master_audio_store_01/manifest.json | c933b24027c40c20 | c933b24027c40c20 | 変化なし |
| er006_output/pronunciation_ledger_01/ledger.json | 90633657ec4e2132 | 90633657ec4e2132 | 変化なし |
| er006_output/master_audio_store_01/reuse_telemetry.jsonl | 32c3f22ba284a352 | 893dc14acd76fd6d | **変化** |

- Production Master Audio Store audio件数: before 489 / after 489
- Trial名前空間store: `er110_output/family_y_redelivery_audio_01/audio/master_store_trial_r0`(存在=True)。process内で `er006_master_audio_store_01.STORE_DIR/AUDIO_DIR/MANIFEST_PATH/TELEMETRY_PATH` をここへ差替え(`trial_store_info.json`)
- 変化したファイルに本Trial固有の識別子(`redelivery`/run dir名)を含むか: {"er006_output/master_audio_store_01/reuse_telemetry.jsonl": []}
  - 識別子が無い場合、変化は並行agent(同時刻にTTS/Production runを実行中)によるもので、本Trialの書込みではない(本TrialのTTS clip・manifest・telemetryはTrial名前空間storeにのみ存在)。
- Trial store manifest bytes=838768(Production manifest bytes=802453)

## 2. y_entry_point / production_reachable

- `er110_output/family_y_redelivery_audio_01/audio/r0/y_entry_point.json`: production_reachable=False, tts_backend=speech_metadata_flash_lite, style_profile=fx_20261017, fixed_voices={'voice_1': 'Algieba', 'voice_2': 'Zephyr', 'voice_3': 'Schedar'}
- Voice割当照合(`er110_output/family_y_redelivery_audio_01/voice_assignment_check.json`): {"z_rule_assignment": {"voice_1": "Algieba", "voice_3": "Schedar", "voice_2": "Zephyr"}, "y_fixed_slots": {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"}, "narrator": "Aoede", "match": true}

## 3. 既存tracked .pyの変更

`git status --porcelain -- '*.py'`(本Trialの3新規fileは除外して表示):
```
?? docs/research/FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_AUDIO_01/build_isolation_01.py
?? docs/research/FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_AUDIO_01/build_reports_01.py
?? docs/research/FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01/_scratch04/er078_old.py
?? er003_v1_p2_preflight.py
?? er003_v1_p2d_review.py
?? er003_v1_p2e_review.py
?? er003_v1_p2f_review.py
?? er003_v1_p2g_review.py
?? er008_n8_a2_comment4_fix_01.py
?? er008_n8_a2_resume_01.py
?? er008_n8_b1_resume_01.py
?? er008_n8_baseline_run_01.py
?? er008_n8_deviation_recheck_01.py
?? er008_n8_factcheck_recheck_01.py
?? er009_ledger_generalization_boundary_06.py
?? er009_n1_a2_slowdown_apply_06.py
?? er009_n1_diagnostic_full_retry_forced_validation_14.py
?? er009_n1_diagnostic_full_retry_verification_14.py
?? er009_n1_final_ledger_recheck_03.py
?? er009_n1_full_writer_ledger_integration_08.py
?? er009_n1_human_review_approve_04.py
?? er009_n1_kp3_a2_regenerate_05.py
?? er009_n1_local_rewrite_rule_trial_07.py
?? er009_n1_no9_ledger_revision_14.py
?? er009_n1_regression_test_14.py
?? er009_n1_scope_clarification_recheck_01.py
?? er009_writer_trial_diagnostic_03.py
?? er009_writer_trial_diagnostic_04.py
?? er009_writer_trial_diagnostic_05.py
?? er014_output/four_type_observation_01/voices/writer_generic_before_v2.py
?? er019_output/_fxnr7_shadow_head/er019_family_x_audio_production_runner_01.py
?? er052_step2_astra_r3_01_run.py
?? er110_family_y_redelivery_play_verify_01.py
?? test_writer_api.py
?? x_tmp.py
```
- 上記に他agent起因の変更が含まれる場合も、本Trialのcommitには含めない(`git commit --only`でpath限定)。本Trialが変更したtracked .pyは0件。

## 4. sink付替え(Local Rewrite recovery出力先)

- `er110_output/.../audio/local_rewrite_recovery/` 配下の出力: 0件。`er011_output/local_rewrite_recovery/` への本Trial起因の書込みは付替えにより0(発動時のみ生成、未発動なら0)

## 5. DefaultOffIsolation(未承認機能の既定値)

- flag/環境変数/CLI引数でProduction挙動が変わる経路なし。`--paid`と`BUDGET_APPROVED.json`が無いと全コマンドが例外で止まり副作用0(`er110_family_y_redelivery_audio_01_test_01.py::test_default_off_no_paid_flag_raises_before_any_side_effect`)。どのProduction runner/.env/起動scriptも本moduleを参照しない(`test_no_production_reference`)。Production run dir・公開ページへの書込みなし。

## 6. 変化した1ファイル(reuse_telemetry.jsonl)の帰属(手動確認、API 0)
- 有料前のbytes=1,333,551 → 現在 1,339,433。追記は10行で、全行が `moon_shrinking__run_ms_03`(Family X『月が縮む』の並行agent run、`er019_output/family_x_audio_production_wiring_01/...`)のreused event。`redelivery`/`family_y`を含む行は0件。
- 本Trialは `er006_master_audio_store_01.TELEMETRY_PATH` を Trial名前空間 `audio/master_store_trial_r0/reuse_telemetry.jsonl` に差し替えて動作したため、Production側への書込みは無い。Production `manifest.json`・`pronunciation_ledger_01/ledger.json` は有料前後で sha256 完全一致、Production store の audio 件数も 489 → 489。
- 結論: 本Trial起因のProduction書込み=0。変化は並行agentによる。
