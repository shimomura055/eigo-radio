# TEST_PLAN_01 (委任_02で実施。本委任ではtest実行なし=¥0・code無変更)

実行環境: `set PYTHONUTF8=1` + `.venv\Scripts\python.exe`。Production runner/moduleは変更前に**ベースライン(変更前PASS件数)を取得**し、変更後と比較する(件数が減らないこと)。

## 1. 既存回帰(変更後も無変更でPASS、コード・期待値を緩めない)

| 区分 | test file | 守る対象 |
|---|---|---|
| KP DB Hybrid | `er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`、`er030_key_phrase_db_hybrid_source_reference_contract_01_test.py` | selector/Source Reference Contract/fallback/cost cap/`Er028UtilByteParityTests` |
| KP 共有 | `er003_test_key_words_min_unit.py`、`er003_test_key_words_min_unit_4plus1_01.py`、`er003_test_key_words_canonicalization.py`、`er003_test_key_phrase_source_gate_01.py`、`er011_test_key_phrase_set_redundancy_qa_01.py` | min unit/4+1/canonicalization(Rule7)/source gate/Redundancy QA |
| KP Trial(無変更で通る=Trial記録の再現性) | `er064_kp_int_01_test_01.py`(22件)、`er064_kp_int_02_test_01.py`、`er064_kp_int_03_test_01.py`、`er064_kp_idiom_trial_01_test_01.py`、`er064_kp_opt_01_upstream_test_01.py`、`er064_kp_opt_01_prompt_test.py` | Trial定義(M2/P0逐語)。Trial fileを変更しないことの確認 |
| TTS style | `er019_family_x_style_profile_01_test_01.py`(49件)、`er019_family_x_audio_production_runner_01_test_01.py`(53件)、`er033_tts_flash_lite_family_x_styles_01_test_01.py`、`er033_tts_flash_lite_backend_wiring_01_test_01.py`、`er033_tts_flash_lite_family_x_wiring_phase1_regression_01_test_01.py` | profile/default byte一致/runner style解決/backend |
| TTS 品質Gate・減速・retry | `er011_human_review_lock_01_test_01.py`、`er011_tts_execution_mode_switch_wiring_01_test.py`、`er011_tts_cooldown_observation_01_test_01.py`、`er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py`、`er011_open121_repetition_qa_production_wiring_01_test_01.py`、`er011_no18_tight_speech_and_trim030_production_wiring_23_test_01.py`、`er011_ending_clarity_fallback_01_test.py`、`er026_post_slowdown_cascade_rescue_01_test_01.py`、`er003_v1_n3_01_standard_a2_generate_test_01.py`、`er003_v1_n3_01_advanced_adaptation_generate_test_01.py` | 減速後再検証/cascade rescue/retry上限3/fallback |
| Family Z | `er063_family_z_audio_01_test_01.py`、`er062_family_z_writer_01_test_01.py`、`er026_family_z_fiction_production_runner_01_test.py`、`er026_family_z_e2e_integration_test_01.py`、`er026_family_z_stop_sentinel_test_01.py`、`er026_cs_audit_regression_01_test_01.py` | Z style表sha・STOP sentinel・Z KP outer retry |
| 並行タスク混入防止 | `er065_short_clip_asr_context_trial_01_regression_test_01.py`、`er068_*_test_01.py`、`er069_*_test_01.py`(実行は読取確認のみ。これらのfile・挙動を変更しない) | 未承認の連結発音/帰属clip改善がProductionに混入していないこと |

ベースライン採取コマンド例(委任_02開始時、変更前):

```
set PYTHONUTF8=1
.venv\Scripts\python.exe -m unittest er030_key_phrase_db_hybrid_family_x_production_wiring_01_test er030_key_phrase_db_hybrid_source_reference_contract_01_test er064_kp_int_01_test_01 er019_family_x_style_profile_01_test_01 er019_family_x_audio_production_runner_01_test_01 er033_tts_flash_lite_family_x_styles_01_test_01 er063_family_z_audio_01_test_01 -v
```
(上記は実行コマンドの形式。実際は上表のfileを全て列挙し、結果の件数を`er071_output/m2p0_n01_production_wiring_01/`の委任_02証跡へ保存する。unittest形式でないfileがある場合は各fileを`.venv\Scripts\python.exe <file>`で個別実行する。)

## 2. 新規test(委任_02で追加。Production module側へ置く)

### 2-1 M2 supply module(`er030_key_phrase_db_hybrid_m2_supply_01_test.py`、新規)

| # | test | 方法 |
|---|---|---|
| M-1 | Trial関数とのbyte parity | `placeholder_candidates`/`rule_possessive_pattern_candidates`/`compute_containment`/`fragment_risk`/`reserved_sort_key`/`candidate_row_text`相当の**出力**をTrial module(`er064_*`)の同入力出力と照合(test内でのみTrialをimport。Production moduleはimportしない) |
| M-2 | Snapshot回帰(¥0) | `er064_output/kp_extraction_selection_opt_01/phase1_a/wiktionary_snapshot_01.json`を照会関数のスタブ(ネットワークなし)に使い、9記事x Std/Adv(Trial対象)でProduction版M2のshortlist/rows_text sha256が`er064_output/kp_integrated_opt_01/round1/shortlists_r1.sha256.txt`のM2行と**完全一致** |
| M-3 | `demoted_allow`方式(B)同値性 | 方式(B)(拡大1回+先頭60窓)とTrial方式(現行窓survivors)の`demoted_allow`集合が全対象記事で一致(不一致なら設計見直し=Opus論点①) |
| M-4 | 予約枠cap3が外側 | cap15のphrase枠と独立に最大3件追加/overflowは候補に入らずmetaに記録/句読点またぎ3-gramは除外 |
| M-5 | 候補行に`match:`が出ない | M3ではないこと |
| M-6 | 決定論 | 同入力で2回実行しsha一致 |
| M-7 | Trial非依存(Dangling) | Production moduleのimport文にTrial(`er064_*`/`er057_*`)がない(ast検査) |

### 2-2 selector/runner配線test

| # | test | 方法 |
|---|---|---|
| S-1 | P0無変更sha | template file `69d0e6ff…`、`extract_static_instructions` `b8af4d50…`、guidance `026aa730…`を固定。M2配線後の`build_lightweight_user_message`出力のstatic部/guidance部が一致 |
| S-2 | M2が既定で発火 | `run_db_hybrid_selection`(selector/LLMはmock)が`candidate_supply="m2"`で`m2_supply`を呼び、telemetryに`kp_supply="m2"` |
| S-3 | retry時に再照会しない | `shortlist_cache`共有でWiktionary照会mockの呼出回数が1回 |
| S-4 | 失敗時は既存経路 | Wiktionary照会mockが429枯渇でraise → `DbHybridFailure(SELECTOR_EXCEPTION)`→既存Strategy L fallback、**M0に落ちない**、telemetryに`kp_supply`が付かない/M2不発火が記録される |
| S-5 | 上限・cost cap不変 | `MAX_PRODUCTION_RETRY_ATTEMPTS=2`/`KEY_PHRASE_REDUNDANCY_RETRY_MAX=2`/`KP_ARTICLE_COST_CAP_JPY=15`の値test |
| S-6 | KP単独stage(採用時) | `--scaffold-only kp`でPreview/Comment生成関数が呼ばれない(mock) |
| S-7 | Family Z KPは無変更 | Zの`run_kp_stage`が`kp_backend`未指定(strategy_l)のまま、`family_profile="family_z"`は`NotImplementedError`のまま(Z-1未決の間のguard test) |

### 2-3 N01 test

| # | test | 方法 |
|---|---|---|
| N-1 | N01 sha | 定数テキスト=`d1956c91…`/202文字。`assert_no_wpm_specification`通過。`prompts_r5.json`の該当エントリとbyte一致(testでのみ読込) |
| N-2 | profile定義 | `n01` profileは`FULL_STORY`のみoverride・`std_append_slower_instruction=False`。他role(IN_ONE_LINE/PREVIEW/COMMENT/KP等)は`resolve_role_style`がbase素通し |
| N-3 | Std逐語・Adv | Std styleに`A2_SLOWER_PACE_INSTRUCTION`が連結されない/Advも同一文言(a2/b1b両方) |
| N-4 | default不変 | `--style-profile`未指定・記録なしでdefault(バイト同一)(案C採用時) |
| N-5 | 既存profile後方互換 | `coffee_p8`/`coffee_final_v5`のP8定数・shaは無変更(`3eadf4f6…`) |
| N-6 | 固定記録/M2/M5 | 新profileは既存run記録のあるout_dirでSTOP、legacy backendでSTOP |
| N-7 | 減速・Gate無変更 | `A2_SLOWDOWN_PERCENT`、`apply_a2_slowdown_postprocess`、`PRODUCTION_MAX_TTS_ATTEMPTS=3`の値/呼出test(既存testの再実行で担保+値test) |
| N-8 | fallback takeはN01ではない | Std/Advのminimal instruction経路のstyle引数がN01を含まない(mock呼出引数を検査) |
| Z-1m | Z mock | `style_text_for(spec)`が`NARRATOR_FULL_STORY_*`でN01、`DIALOGUE_*`/Preview/Comment/KP/TOPIC_INTRO/JA title/SHELLで従来値。`assert_style_table_integrity`PASS。生成関数はmock(課金・生成なし) |
| Z-2m | Zはprofile機構と独立 | Z narratorはtext定数経由でrunner`--style-profile`を参照しない(確認のみ) |

### 2-4 Dangling Reference / Trial無変更

- `git diff --stat`でTrial file(`er064_*`/`er057_*`/`er065_*`/`er068_*`/`er069_*`)に差分がないこと。
- Production module→Trialのimportゼロ(ast)、`PD8`/`P8`/`coffee_p8`系定数の参照元一覧(削除しない場合の保持理由を記録)。
- `tools\secret_scan_01.py --staged`(commit前)。
