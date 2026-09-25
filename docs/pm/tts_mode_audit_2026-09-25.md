# TTS実行方式(Standard同期/Batch)横展開点検 — 2026-09-25

管理ID: `PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`(既存ガバナンス
PM_GOVERNANCE.md 7-1/7-2の再確認・運用是正、新仕様ではない)。

## 方法

`Grep pattern="tts_generate|make_batch_tts_call_fn|run_tts|TTS_EXECUTION_MODE"
glob="er0*.py"` で133ファイルがヒット。各ファイルについて
`os.environ.setdefault("TTS_EXECUTION_MODE", ...)` / `os.environ["TTS_EXECUTION_MODE"] = ...`
の実assignmentパターンをGrep/スクリプトで機械判定し、9分類(A〜G5)へ分けた
(本タスクでの是正実施はF[E2E runner]のみ、他は既存実行済み/テスト/
参照のみ/要判断のいずれか)。

## 分類サマリ(133ファイル)

| 区分 | 件数 | 内容 | 是正要否 |
|---|---|---|---|
| A. 既に`TTS_EXECUTION_MODE=STANDARD`を明示(既存) | 31 | Trial/開発runner(`er012_editorial_b_voices_*`/`er013_family_c_episode_trial_*`/`er012_b_family_production_runner_01.py`等)。全ファイルで値は`STANDARD`のみ確認(`BATCH`ハードコードは0件)。 | 是正不要(既に7-1準拠) |
| F. E2E runner(本タスクで是正) | 1 | `er012_e_family_entertainment_two_level_runner_01.py`。`--tts-mode`未実装により`TTS_EXECUTION_MODE`未設定のまま`er006_batch_tts_wiring_01.DEFAULT_TTS_EXECUTION_MODE`(=BATCH)に依存していた(E2E-WIRING-01のBatch長時間化の直接原因)。 | **是正実施**(`--tts-mode {STANDARD,BATCH}`既定STANDARD追加、BATCH時`--batch-reason`必須、`entry_point.json`へ記録) |
| F-test. Fのunittest | 1 | `er012_e_family_entertainment_two_level_runner_test_01.py`(mock使用、実TTS呼び出し無し)。今回`TtsModeCliTests`を追加。 | 是正実施(テスト追加のみ) |
| B. 共有Production TTSライブラリ本体 | 1 | `er006_batch_tts_wiring_01.py`(`DEFAULT_TTS_EXECUTION_MODE = BATCH`の定義元、`resolve_tts_execution_mode()`)。 | **対象外**(委任条件「既定値は変更しない」、量産Production既定を保持) |
| C. TTS呼び出し無し(player.html生成のみ、HTML内ラベル表示) | 5 | `er011_family_a_completion_a2_trend_end_to_end_01_a2_continuation_player_01.py`/`..._b1b_continuation_player_01.py`/`er011_family_a_trend_synthesis_ai_manufacturing_production_run_01_a2_player.py`/`..._b1b_player.py`/`er011_wake_before_alarm_trial12_std_player_01.py`。いずれも`make_batch_tts_call_fn`等を呼ばず(実測0件)、既に生成済み音声の説明文に`TTS_EXECUTION_MODE=STANDARD`という文字列を記載しているだけ。 | 是正不要(TTS呼び出し自体が無い) |
| D. TTS_EXECUTION_MODE切替機構自体のtest/evidence | 2 | `er011_tts_execution_mode_switch_wiring_01_test.py`/`..._runtime_evidence_run.py`。両方式(STANDARD/BATCH)を意図的に検証することが目的(PM_GOVERNANCE.md 7-2例外1「Batch API固有の挙動そのものの検証」に該当)。 | 是正不要(例外1に該当する目的が明白、実行済み) |
| E. 既存実行済みevidence(BATCH既定フォールバック読み取りのみ) | 1 | `er011_kp_en_asr_false_rejection_prod_wiring_01_runtime_evidence.py`(`os.environ.get("TTS_EXECUTION_MODE", "BATCH")`で結果記録用に読むのみ、実行済みrun)。 | 対象外(実行済みHistorical、変更しても既存evidenceは変わらない) |
| G1. テスト(mock使用、実TTS呼び出し無し) | 21 | `er002_test_common.py`/`er003_test_b1_p3r_audio.py`等(下記全リスト参照)。unittest+mock構成を個別確認(該当ファイルはいずれも`mock`/`unittest`を使用)。 | 是正不要(実API呼び出しがそもそも発生しない) |
| G2. 既存実行済み一回限りHistoricalスクリプト | 65 | `er008_n8_*`/`er009_*`/`er011_no18_*`/`er011_open11*`等、特定のTopic番号・Trial番号・regen番号に紐づく完了済み一回限りscript(下記全リスト参照)。 | 是正しない(既に実行完了、成果物は変更しない前提。将来の再利用は想定されないため、今回の是正対象[今回のE2E runner・今後新設する開発用runner・Trial harness]には該当しないと判断) |
| G3. Standard相当を別方式(関数monkeypatch)で既に実現済み(TTS_EXECUTION_MODE導入前の実装) | 2 | `er009_n1_production_integration_01.py`/`er011_no18_discovery_why_full_production_run_01.py`。ER-011-TTS-EXECUTION-MODE-SWITCH-PRODUCTION-WIRING-01(環境変数方式)導入前の実装で、`batch_wiring.make_batch_tts_call_fn`をStandard版へ関数差し替え(monkeypatch)する方式により、既にユーザー指示(2026-08-29)でStandard相当を実現済み(コメントに明記)。いずれも特定Topic番号(No.9/No.18)に紐づく実行済みrunner。 | 是正不要(既にStandard相当・実行済み・one-off) |
| G4. TTS呼び出し無し(コメント中の関数名参照のみ) | 1 | `er011_open121_repetition_qa_production_01.py`(TTS後処理QA検出ロジックのモジュールで、`er003_v1_n3_01_tts_generate.py`はコメント中の定数出典表記のみ、`def main`/`argparse`無し、実TTS呼び出しは無し)。 | 是正不要(TTS呼び出し自体が無い) |
| G5. Production ライブラリモジュール(独自CLI入口なし、呼び出し元での対応要否は未確認) | 2 | `er012_b_family_voices_a2_production_01.py`/`er012_b_family_voices_production_01.py`。`er003_v1_n3_01_tts_generate`をimportし実TTS関数を提供するが、自身は`if __name__ == "__main__"`を持たないライブラリモジュール(`argparse`/`def main`無し)。主要呼び出し元と確認できた`er012_b_family_production_runner_01.py`は既に`TTS_EXECUTION_MODE=STANDARD`をハードコード済み(区分A)のため、その経路では問題ない。ただし他の呼び出し元(下記「一覧外で確認した関連ファイル」参照)を全て個別確認してはいない。 | **要判断**(Fable/ユーザー判断待ち、本タスクでは編集しない) |

合計: 31+1+1+1+5+2+1+21+65+2+1+2 = 133。

## 一覧外で確認した関連ファイル(グレー領域、事実列挙のみ)

- `er013_family_c_production_runner_01.py`: 本委任の事前指定Grepパターン
  (`tts_generate|make_batch_tts_call_fn|run_tts|TTS_EXECUTION_MODE`)には
  ヒットしない(自身はこれらの文字列を含まない)が、`import
  er012_b_family_voices_a2_production_01`を行っており、`def main`/
  `argparse`を持つ独立Family C Production runnerである。このrunner自体が
  `TTS_EXECUTION_MODE`を設定しているかは本タスクでは未確認(グレップ
  パターン外のため事前指定Read一覧・横展開点検の対象外だった)。
  **要判断**として報告する(本タスクでは編集していない)。
- `er012_b_family_voices_a2_production_01.py`/`er012_b_family_voices_production_01.py`を
  importする他の28ファイル(`er012_b_voices_3v_a2_kp_fix_ai_hiring_01.py`
  等)のうち、`er012_b_family_production_runner_01.py`以外は個別に
  `TTS_EXECUTION_MODE`設定有無を確認していない(件数が多いため本タスクの
  スコープでは未実施、G5と合わせて要判断)。

## G1(テスト、mock使用)全リスト(21件)

er002_test_common.py, er003_test_b1_p3r_audio.py, er003_test_b1_p3s_audio.py,
er003_test_b1_p3t_audio.py, er003_test_b1_p4c_audio.py,
er003_test_v1_n3_01_tts_generate.py, er006_batch_tts_wiring_01_test.py,
er006_kp5_canonical_bug_01_test.py, er007_ja_blindspot_test_01.py,
er007_ja_tts_retry_path_fix_test_01.py, er008_a2_slowdown_invariant_19_test_01.py,
er008_n8_a2_slowdown_sha256_refresh_22_test_01.py,
er008_n8_reicher_pronunciation_22_test_01.py, er009_ja_foreign_token_gate_01_test_01.py,
er011_no18_connected_speech_reading_resolver_wiring_08_test.py,
er011_open121_repetition_qa_production_wiring_01_test_01.py,
er011_open129_structural_completeness_production_wiring_01_test_01.py,
er012_b_family_voices_a2_new_topic_production_01_test_01.py,
er012_b_voices_3v_a2_user_test_01.py, er012_editorial_b_family_production_phase1_test_01.py,
er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py

## G2(既存実行済みHistorical)全リスト(65件)

er001b10_hanshin_common_spec.py, er001b9_caregiving_common_spec.py, er002_common.py,
er002_gemini_client.py, er002_runner.py, er003_b1_p6a_audio.py, er003_b1_p8a_audio.py,
er003_v1_b1_p6a_generate.py, er003_v1_n3_01_assemble.py, er003_v1_n3_01_tts_generate.py,
er003_v1_repro01_main_generate.py, er003_v1_repro02_main_generate.py,
er003_v1_sing01_news_tail_fix.py, er003_v1_sing01_point_headings_aoede.py,
er003_v1_sing01_voice01_generate.py, er005_e2e_tts_cost_quality_01.py,
er005_llm_cost_structure_r1.py, er005_stage4_tts_generate.py, er005_tts_audit_analyze.py,
er006_audio_cost_pilot_02_run.py, er006_audio_cost_spec_fix_01_static_audit.py,
er006_pool_pilot_01_audio.py, er007_evidence_density_ab_01_tts.py,
er007_no2_pronunciation_rca_01.py, er008_a2_speed_same_text_abc_09.py,
er008_n7_content_audio_qa_02.py, er008_n7_pilot_run_01.py, er008_n8_a2_comment4_fix_01.py,
er008_n8_a2_resume_01.py, er008_n8_b1_resume_01.py, er008_n8_baseline_run_01.py,
er008_n8_final_audio_regen_20.py, er008_n8_location_compression_24.py,
er008_n8_wait_and_date_fix_retts_22.py, er008_pool_n4_audio_qa_sync_01.py,
er009_n1_a2_slowdown_apply_06.py, er009_n1_kp3_a2_regenerate_05.py,
er009_pool_n4_comment2_fix_01.py, er009_pool_n5_a2_slowdown_01.py,
er009_pool_n5_b1_fix_01.py, er010_no9_a2_only_audio_rerun_17.py,
er010_pool_n5_part2_revalidate_01.py,
er011_discovery_generalization_towels_trial_11_audio_02_resume_human_review.py,
er011_discovery_generalization_towels_trial_11_audio_04_b1b_fullstory_resume_human_review.py,
er011_ending_clarity_fallback_01.py,
er011_household_unified_final_candidate_01_segfix_comment3_01.py,
er011_no18_a2_reading_trial_06.py,
er011_no18_connected_speech_reading_resolver_audio_stage_08.py,
er011_no18_connected_speech_reading_resolver_scoped_retry_08.py,
er011_no18_evidence_compression_a_precision_21r_audio_stage.py,
er011_no18_open107_audio_stage_03.py, er011_no18_open107_b1_failed_segments_retry_03.py,
er011_no18_open107_runtime_evidence_03.py, er011_no18_open109_a2_audio_stage_04.py,
er011_no18_open110_comment2_ending_clarity_retry_04.py,
er011_no18_open110_survey_diagnostic_04.py, er011_open107_opened_tts_diagnostic_trial_01.py,
er011_open112_theme2_audio_review_fix_02_subtaskg_apply_slowdown_01.py,
er011_open112_trend_theme2_b_full_audio_trial_13.py,
er011_open117_keyphrase_display_tts_separation_trial_02.py,
er011_open117_keyphrase_tilde_gate_recheck_01.py,
er011_open121_trial12_a2_full_story_part1_slowdown_apply_01.py,
er011_open121_tts_repetition_general_qa_trial_01.py,
er011_tts_cooldown_observation_harness_helpers_01.py,
er012_b_family_editorial_type_registry_01.py

(注: 上記65件には、`import`元経由で間接的にTTS呼び出しへ到達するファイル
[`er003_v1_n3_01_assemble.py`/`er003_v1_n3_01_tts_generate.py`/
`er003_v1_sing01_*.py`等のProduction call site本体6ファイルを含む]が含まれる。
これらは`er006_batch_tts_wiring_01.make_batch_tts_call_fn()`の**呼び出し先**
であり、`TTS_EXECUTION_MODE`の設定自体は常に**呼び出し元[runner]の責務**
という既存設計[ER-011-TTS-EXECUTION-MODE-SWITCH-PRODUCTION-WIRING-01]に
従うため、call site自体を編集する対象ではない。)

## 判断基準の補足

- 「今回のE2E runner・今後新設する開発用runner・Trial harness」という
  委任範囲に照らし、既に完了・実行済みの一回限りHistoricalスクリプト
  (G2、特定Topic/Trial/regen番号に紐づく)は、今後再利用される設計では
  ないため是正対象に含めなかった。編集しても既存evidence
  ([`er0XX_output/`]配下)には一切影響しない一方、無関係な既存差分を
  大量に増やす(133ファイル中93ファイル相当)ことになり、CLAUDE.md
  「無関係な既存差分を編集・stageしない」「大きな変更を行う前に…説明する」
  との整合を優先した。この判断自体をUSER_DECISION_REQUIREDとしてではなく
  事実列挙として報告する(範囲拡大の可否はFable/ユーザー判断)。
