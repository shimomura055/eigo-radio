# IMPLEMENTATION_02: KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_02 実装記録(2026-10-15)

Status: **WIRED_PENDING_EVIDENCE**(`PRODUCTION_WIRED`は宣言しない。runtime evidence=委任_03、最終判定=Fable)。費用 JPY0(有料API 0・TTS 0)。provenance: 全test/Regression/harness自己検証=synthetic(mock/fake client)+fresh。E2E自己確認=No。

## 1. 手順の実績
0. golden先行: 撤去前HEAD `64d3ec975` で `golden/make_alignment_request_golden_01.py` を実行し `golden/alignment_request_golden_01.json`(kwargs本文+sha)を固定、commit `4dff72f10`(委任_02a)。combined sha256 = `47fe3cd757a464ebbd5c228fa1771ec08556f7b0206d00acec7905489211d8cb`(2回実行で同値=決定論)。撤去後に同じscriptを実行し同一sha(`test_alignment_request_bytes_match_golden` PASS)。
1. ga(`er003_key_words_gloss_alignment.py`)、2. sc、3. X(er019)、4. Z(er026)、5. test、6. harness+旧Trial script、7. Regression、8. 残置Grep。

## 2. 撤去実績(`er003_key_words_gloss_alignment.py` 1118行→853行)
- 関数11を撤去: `build_user_message`、`kp_has_slot_word`、`gloss_has_unjustified_slot`、`validate_alignment_response`、`run_alignment_gate`、`revert_to_candidate_allowed`、`apply_alignment`、`build_gloss_alignment_fallback_record`、`write_failed_notice`、`format_failed_stdout`、`resolve_mode`。
- 分岐1: `align_glosses` legacy本体+dispatchを撤去し、`_align_glosses_corrected`を`align_glosses`へ改名統合(`mode`引数削除)。
- 定数9を撤去: `FALLBACK_KEEP_KP`/`FALLBACK_REVERT_IF_SAFE`/`GLOSS_ALIGNMENT_FALLBACK_MODE`、`SLOT_TOKENS`、`_TILDE_RE`、`GLOSS_ALIGNMENT_NOTICE_FILENAME`、`GLOSS_ALIGNMENT_MODE_LEGACY`/`_CORRECTED`/`_MODES`/`GLOSS_ALIGNMENT_MODE`。
- schema: legacy schemaを撤去し、修正版schemaを`GLOSS_ALIGNMENT_JSON_SCHEMA`として直接定義(`name`=`key_phrase_gloss_alignment_corrected`、property順・required順・strict無変更。golden shaで固定)。`copy`/`deepcopy`依存を除去。
- sc: `gloss_alignment_mode`引数(`run_key_phrase_canonicalization`/`run_key_phrases`/`_run_key_phrases_impl`の3箇所)と分岐(schema切替・align呼出2系統・unresolved_ranks条件・legacy fallback節[event/NOTICE.md/stdout])を全撤去。
- er019: `run_theme_scaffold`の`gloss_alignment_mode`引数・`_gm_kwargs`・summaryの条件付き出力。er026: `E2EContext.gloss_alignment_mode`・`_kp_fn_for_ctx`のcorrected節・`stage_kp`内の`== "corrected"`条件4箇所。
- testの削除/書換(`er003_test_key_words_gloss_alignment.py` 79→70): 置換なしで削除12(Alignment 7=fallback系3・default_mode_keep・digit/paren[legacy validator]・slot・stale slot、NoticeFiles 1、ModeSeparation 4)、書換26中14(ScaffoldIntegration失敗系1、ScaffoldCorrected 5、DefaultOffIsolation 8)→新規17(ScaffoldCorrected 7、DefaultOnKillSwitch 6、OldFailedAndUnevaluated 3、ScaffoldIntegration書換1)。
- 「legacy」語: gaで0件(`rg -n -i legacy er003_key_words_gloss_alignment.py` 0行)。

## 3. 追加/変更した機構(既存関数の拡張のみ。新Validator/Hook/管理機構なし)
- ga: `_read_flag_env`/`flag_effective`/`announce_flag`(OF-11)、`collect_unevaluated`(OF-08)、`STATUS_OLD_FAILED`(OF-14)、`HR_RESOLVE_RUNBOOK`、`UNEVALUATED_REASON`、VERSION `ER-003-KP-GLOSS-ALIGN-02`(OF-02)。
- sc: `run_key_phrases`のHR判定をディスクartifact基準に(OF-03)、`gloss_alignment_run_status`(OF-04)、`gloss_alignment_metrics`(OF-16)。
- er019: summary 6キー、`_gloss_hr_levels_from_artifacts`(OF-05)、`print_gloss_hr_final_line`のartifact基準、解説cache署名(OF-06)、未評価検出(OF-08)、main try/finally+rc=2(OF-03/04)、assembleのlevel単位捕捉(OF-19)、実効flag記録(OF-11)。
- er026: `stage_kp`冒頭`ga.preflight()`、署名(OF-07)、未評価検出(OF-08)、snapshot優先復元+raise前`install_kp_assets`/`mark_stale_descendants`(OF-09)、実効flag(`gloss_alignment_flag.json`+summary)(OF-11)、metrics(OF-16)。
- runbook: `docs/pm/runbooks/KP_GLOSS_ALIGNMENT_HR_RESOLVE_01.md`(原本`HR_RESOLVE_PROCEDURE_01.md`は履歴として無変更)。

## 4. 設計との差異・事実メモ(Fable向け)
- `er062_family_z_writer_01.py`の`DEPENDENTS`は`kp_*`の子stageを持たない(`kp_expl_b1b`は子として登録されていない)ため、`mark_stale_descendants("kp_<lv>")`は現状no-op。OF-09の指示どおり呼出は実装したが、実際の保護はsnapshot優先復元+asset配備で成立している(Zの`kp_expl_b1b`は署名不一致で`FamilyZProvenanceMismatchStop`となり、runbookの手順どおり`--regenerate-stage kp_expl_b1b`を明示する)。
- `--regenerate-stage kp_<lv>`で未消費snapshotがある場合、snapshotを優先復元する(OF-09)。HR停止後に「あえて選定から作り直したい」場合は、snapshot(`gloss_alignment_pending_result.json`)を削除してから再実行する(runbook 手順4に明記)。
- 未評価検出(OF-08)は`_gloss_alignment_hr_unresolved`の戻りに`_unevaluated=True`付きitemを混ぜる形で実装したため、assemble前チェック(`_assert_no_gloss_alignment_hr`)とページ生成(`_build_level_table`)にも同じ判定が及ぶ。ON化前に完成済みで対象itemを持つXのrunは、assemble再実行・ページ再生成時に停止する(委任文はTTS関所とZ stage_kp再利用後を指定。assemble/ページは同一関数を共有するため結果として適用された)。
- 旧Trial scriptのSystemExit: 委任文の「6本」に加え、`er071_gloss_alignment_correction_01_trial.py`(削除済みの`GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED`を参照し、実LLMを呼ぶ経路を持つ)も停止対象にした(計7本)。`er071_completion_04_gloss_census_replay.py`/`er071_completion_04_gloss_realign.py`は設計§2-1の対象で、旧方式の再現用のため停止対象に含めた。T3 mock(`er071_gloss_alignment_correction_01_t3_mock.py`)は移植元として無変更(mockのみ・API 0だが、`gloss_alignment_mode`引数削除によりそのままでは実行できない)。
- T3 27シナリオ中、移植26+撤去1(`T3(k-ga)`=legacy版とHEAD版の出力同一性比較。legacy撤去で意味が消滅、API request bytesの同一性はgolden testが担う)。移植先は独立ファイル`er003_test_kp_gloss_alignment_stop_paths.py`(理由はファイル冒頭docstring)。
- `ga.announce_flag`のOFF警告文は設計§3の文言に準拠(`[GLOSS-ALIGN][WARN] DISABLED by EIGO_KP_GLOSS_ALIGNMENT=0 (承認済み仕様の無効化)...`)。

## 5. Regression(`regression_02/`)
実行環境: `OPENAI_API_KEY=""`、`.venv\Scripts\python.exe`、直列・単独(`regression_02/_run_regression.sh`)。コマンド: `run_project_regression.py --pattern <pat> --json-summary regression_02/summary_<name>.json`(--helpで確認: `--pattern`/`--json-summary`)。
| suite | collected | passed | failed | errors | 既存failure集合との差分 |
|---|---|---|---|---|---|
| er003*_test_*.py | 1682 | 1678 | 3 | 1 | 差分なし。`er003_test_p2j_investigate`の4件(FAIL3+ERROR1)は撤去前HEAD(git worktree)でも同一の4件がFAIL。別subrunの`er003_test_bad`fixture 1件も既存。baseline(VALIDATION_03 §3-2)1668→1682(-9+20+3=+14) |
| er019*_test_*.py | 421 | 420 | 0 | 1 | 差分なし。1件=`er019_family_x_variable_role_style_wiring_01_test_01.FallbackPathUnaffectedTests.test_fallback_minimal_instruction_ignores_style_prefix_override`が`OPENAI_API_KEY=""`で`OpenAI()`構築に失敗(`er006_asr_provider_routing_01.py:66`)。**撤去前HEAD(git worktree)でも同一失敗**=gloss変更とは無関係の環境要因(委任文が要求する空キー実行で顕在化) |
| er026*_test_*.py | 86 | 79 | 7 | 0 | 差分なし(7件=`er026_cs_audit_regression_01_test_01`4+`er026_post_slowdown_cascade_rescue_01_test_01`3、VALIDATION_03 §3-2の既存7件) |
| er062*_test_*.py | 64 | 64 | 0 | 0 | - |
| er063*_test_*.py | 59 | 59 | 0 | 0 | - |
| er030*_test_*.py | 37 | 37 | 0 | 0 | - |
| er008_audio_validation_gate_05_test.py(pytest) | 10 | 10 | 0 | 0 | - |
新規failure 0。
API 0の証拠: 実行前後で`**/raw_usage_log.jsonl`+er005/er006/er011/er021/er025/er030配下の全12,004ファイルのsha256を比較(`snap.py`)。Regression全体で変化=2ファイル(`er011_output/attempt_history.jsonl`・`er021_output/.../telemetry.jsonl`。いずれも作業前から未commitの既存差分で、既存er026の音声retry mock testが追記する。`raw_usage_log.jsonl`の変化は0)。新規test3ファイル(93 passed + 26 subtests)単独実行・harness自己検証の前後比較は**変化0**(`_snap_diff2.json`〜`_snap_diff5.json`)。この2ファイルはaddしない。
