# FIX_Z_01 — 差分要約(委任_03)

| file | 変更 |
|---|---|
|`er117_chunk_tts_production_01.py`|`plan_z_clip` のレベル条件撤去(:156-157削除)+docstring/ヘッダ更新。他は無変更(X/Y部分は触らない)|
|`er063_family_z_audio_01.py`|DESIGN_Z_01 §2 #2〜#6、§3(`_std_chunk_slowdown_check` 新設、`verify_std_english_slowdown(…, chunk_plans=)`、呼出側regex拡張)|
|`er117_z_chunk_wiring_test_01.py`|旧『Stdはchunk化しない』固定2箇所を書換え(Std narrator>100語はchunk、dialogue・他spec不変)|
|`er117_chunk_tts_production_01_test_01.py`|`test_plan_z_level_marks_lost_and_unchanged_clips`: a2が非chunkというアサートを『Advと同一規則』へ|
|`er117_std_chunk_wiring_test_01.py`|`test_z_planner_level_condition_is_still_in_place_until_next_delegation` を撤去→『レベル条件撤去済み・Std/Advのplan同一』へ置換|
|`er063_z_std_chunk_test_01.py`(新規)|15 test: chunk entry減速記録/親集約/Adv表示不変/部分欠落→親False/cache位置(M3)/resume TTS 0/R7 LR/R6 dialogue・story_clips_from_plan・extract_context同一/M2 Gate(弱証拠救済なし・長さ記録欠落・比率範囲外・plan欠落・plan無し)/実共有Gate+組立0.2秒/legacy非chunk/Adv golden一致|
|`measure_z/`|golden凍結script・golden JSON・事前確認script・evidence準備script・計測JSON|

## 撤去・残置(11-8 / Charter 8)
- 撤去: `er117:plan_z_clip` の `level != "b1b"` 条件とreason文言 `level!=b1b(Std対象外…)`、`er063` `level == "b1b"` のchunk展開条件、旧testの『Stdはchunk化しない』固定(上記3 test)。
- 残置(意図): `kind == "narrator"` 条件(dialogue対象外)、`_z_chunk_parent_display` b1bの `slowdown_applied: None`、`er063` Adv検査(`kind == "narrator" and level == "b1b"` → `slowdown_applied is True` は違反)。
- 残存Grep: `grep -n 'level!=b1b' er117*.py er063*.py` → 本文0(testの `assertNotIn` 文字列のみ)。

## 回帰(遮断harness `PYTHONPATH=netblock_harness_01`、`.venv`)
- er117*: 106 PASS / 0 FAIL(変更前の本作業中runでは旧前提の2 FAIL→書換えで解消)。er063*: 130 PASS(新規15含む、既存115)/0 FAIL。er026*: 222 PASS / 2 skip / 0 FAIL。er122*: pytestで69 PASS(`run_project_regression` は同patternで0件collect=既存の挙動、本変更と無関係)。
- 注意(既存の非冪等): `er063_family_z_audio_01_test_01.py::WiringTest::test_preview_comment_kp_styles` は相対path `x/a2/audit/review_lock_state.json`(repo root直下の `x/`、untracked)を残し、残存すると次回以降ERRORになる(cwd相対のReview Lock。本変更と無関係、HEADでも同じ)。`x/` を各回帰前に削除して実行した。
- ログ: `regression_z/`。API 0。
