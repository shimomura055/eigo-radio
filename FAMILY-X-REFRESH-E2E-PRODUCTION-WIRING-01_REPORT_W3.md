# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 §W3

委任: `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_03.md`
(委任プロンプトチェック: FAIL — 実行コマンド全文中の`unittest`モジュール
名指定/`grep`検索語を「引数/絶対パス欠落」と誤検出する既知のfalse
positive。TTS/API支出関連の警告も「TTSなし」「API支出なし」という
本文自体がキーワード一致しただけの誤検出。委任本文は事前指定Read/Grep・
実行コマンド・SSOT追記文・Git節を全て充足しており、内容上の不備なし)。

本節はW2([`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`]を
作成中)と別ファイルで記録する(統合は後続)。

## 実装

1. **MAJOR-1(Japanese Title→J3統一)**: `er019_family_x_audio_
   production_runner_01.py`の`generate_family_x_a2_segments()`内、
   japanese_title呼び出し(旧L764-770)へ`style_prefix_override=
   _role_style_ja()`を追加(preview/comment_1-4と同一関数・同一backend
   ゲート)。Advanced(B1B)側`generate_family_x_b1_segments()`
   (L468-631)には日本語title相当segmentが存在しないため「該当なし」
   (Grep+Read確認)。
2. **MAJOR-3(cache version guard)**: `FAMILY_X_VARIABLE_ROLE_STYLE_
   VERSION = "v2_j3_e2_title"`を新設し、`tts_generation_results.json`
   トップレベルへ`style_version`として保存(b1/a2両方)。`_generate_or_
   reuse()`冒頭で`cached.get("style_version") != FAMILY_X_VARIABLE_
   ROLE_STYLE_VERSION`(欠落含む)なら即`generate_fn()`へフォールバック
   し、可変segmentのreuseを行わない。`_generate_or_reuse_kp()`・
   `shared_narration`(shell/Master Audio Store)は無変更。
3. **MAJOR-2(Advanced英語経路のruntime evidence)**:
   `er003_v1_sing01_voice01_generate.py`(`generate_charon_english`)/
   `er003_v1_sing01_news_tail_fix.py`
   (`generate_news_narration_wide_margin`)/
   `er003_v1_sing01_point_headings_aoede.py`(`generate`)の各OK/
   ASR_VALIDATION_UNCERTAIN戻り値へ`style_prefix`・`tts_model_id`を
   追加(`voice`は3ファイルとも既存。news_tail_fixのみ`voice`も追加)。
   既存キーは変更なし(追加のみ)。
4. **MINOR-A(既定時ラベル化)**: `er003_b1_p9a_audio.py`
   `generate_narration_snippet()`の`style_prefix`記録、および上記3
   ファイルを、override指定時は実値・既定時は
   `"<default:ENGLISH_STYLE_PREFIX>"`/`"<default:JAPANESE_STYLE_
   PREFIX>"`に統一(200字truncate方式は不採用、Opus案どおり)。
5. **MINOR-B**: 本節に明記する。「runner配線(japanese_title/preview等が
   どのstyleを選ぶか)」は`RunnerBackendGateTests`等mockによる単体
   テストで確認済み。「実際に生成した音声へstyleが反映されていること」
   のruntime実測(E2E)は本W3の範囲外(¥0上限のため)であり、後続の
   E2Eで取得する2段構成。

## テスト・regression結果(実行済み、runtime evidence)

- `er019_family_x_variable_role_style_wiring_01_test_01.py`拡張(新規
  `CacheVersionGuardTests`5件・`RuntimeEvidenceKeysTests`3件・
  `P9aDefaultLabelTests`1件、既存`RunnerBackendGateTests`の1メソッドを
  MAJOR-1反映に更新): `.venv\Scripts\python.exe -m unittest
  er019_family_x_variable_role_style_wiring_01_test_01 -v` → **22件
  全PASS**。
- `run_project_regression.py --pattern "er019*_test_*.py"`: 166件中
  **165 PASS / 1 FAIL**。FAILは`er019_family_x_pointless_01_test_01.
  FamilyAUnchangedTest`(Family A無変更検証)で、原因は並行W2が
  `er006_audio_cost_pilot_02_shared_narration.py`(Family A共有ファイル)
  を編集中であるため(`git diff --stat HEAD -- "er0*.py"`で確認、本
  ファイルは所有5ファイル+テスト2ファイルに含まれない=W3起因ではない)。
  なお本パターン初回実行時は`GenerateOrReuseTextSafetyTests`の既存2件
  もFAILしていたが、これはMAJOR-3のcache version guard新設に伴う
  想定内の後方互換更新漏れであり、既存test(`er019_family_x_audio_
  production_runner_01_test_01.py`、非所有だが直接影響を受けたため
  最小修正)のcached fixtureへ`style_version`を追加して解消した
  (2件ともPASSへ復帰、再実行で確認済み)。
- `run_project_regression.py --pattern "er003*_test_*.py"`: 1557件中
  1553 PASS/3 FAIL/1 ERROR。いずれも本タスク非所有ファイル
  (`er003_test_p2j_investigate.py`のtest件数集計整合性・
  `er015_standard_a2_6000_generation_first_trial_01.py`のProduction
  STOP guard)で、W3の変更対象と無関係(`git diff --stat`で確認)。
  test件数集計はリポジトリ全体のtest数が継続的に増減するため既知の
  drift性質のものと判断。
- `run_project_regression.py --pattern "er033*_test_*.py"`: 64件全
  PASS。
- `run_project_regression.py --pattern "er044*_test_*.py"`: 11件全
  PASS。

## AN3 reminder不在の再確認(ユーザー指示4)

- `grep -rn "再び増やさない" er0*.py`: Production側0件(唯一の一致は
  `er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py`
  の`assertNotIn("再び増やさない", ...)`という「不在を確認する」
  assertion自体)。
- `grep -n "CONCRETENESS_CONTROL_AN3_REMINDER"
  er019_family_x_ja_writer_o_r1_r2_01.py`: 0件(R1/R2・must-fix・
  symbol・fallback経路いずれにも存在しない)。
- 変更なし(確認のみ)。

## 費用

¥0(TTS/ASR/LLM呼び出し0件、実行したのはunittest[全mock]・
run_project_regression.py・grepのみ)。

## Opus L2論点の残存

- MINOR-C(SSOTのruntime evidence記述がB1B対象外であることを明記
  すべき、との所見): 本W3ではコード実装のみで、SSOT本体
  (`CURRENT_SPEC.md`)編集権は無い。RESULT_PACKETへ文案を提示し、
  SSOT反映はユーザー判断・Fable経由で行う。

## 変更ファイル(本タスク由来のみ)

- `er019_family_x_audio_production_runner_01.py`
- `er019_family_x_audio_production_runner_01_test_01.py`(既存test 2件、
  cache version guard追加に伴う後方互換fixture更新)
- `er003_b1_p9a_audio.py`
- `er003_v1_sing01_voice01_generate.py`
- `er003_v1_sing01_news_tail_fix.py`
- `er003_v1_sing01_point_headings_aoede.py`
- `er019_family_x_variable_role_style_wiring_01_test_01.py`
- `docs/pm/design_family_x_refresh_e2e_production_wiring_01.md`(§9-W3
  追記のみ)
- `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_03.md`
  + `_check.json`
