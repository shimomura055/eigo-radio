# Regression: 既存failure(本委任と無関係)の切り分け(2026-10-15)

legacy既定(Production)での新規failureは0。下記は本委任の変更前(HEAD)から存在するfailureで、本委任の変更とは無関係であることを確認した。

| suite | 件数(全/PASS/FAIL+ERR) | failure | 切り分け根拠 |
|---|---|---|---|
| er003*_test_*.py | 1659/1655/3+1 | `er003_test_bad.FixtureTests.test_case_0`(regression runner自身が一時dirに作る**意図的に失敗するfixture**)、`er003_test_p2j_investigate`の3件(歴史的test件数の算術 1037!=1032, 665!=660, 6263!=2070)+1件ERROR(`er015_standard_a2_6000_generation_first_trial_01`のimport時STOPガード) | 当該test module群を単独importしても本委任の変更4module(gloss_alignment/scaffold/er019 runner/er026 runner)は`sys.modules`に現れない(import graph検査)。内容も無関係(過去時点のtest件数の算術、別trialのprompt前提STOP) |
| er011*_test_*.py | 292/289/3 | `TestBuildCommonBlockDefaultByteParity`3件(Trend synthesis common blockのbyte parity) | 同上(変更4moduleを一切importしない)。Prompt文面の差(時刻表記コロンの例外文)で、gloss再整合と無関係 |
| er026*_test_*.py | 86/79/7 | `er026_cs_audit_regression_01_test_01`4件、`er026_post_slowdown_cascade_rescue_01_test_01`3件(ASR cascade/connected speech/post-slowdown rescue) | **HEAD版の変更4moduleに差し替えて同じ2 test moduleを実行しても同じ7件がfail**(`run_head.py`、sys.path先頭にHEAD版を置く方式。28 tests中fail=7、同一id)。= 変更前からの既存failure。なお`test_shared_state_files_unchanged_by_mock_run`は他regressionと**並列実行したときだけ**共有state(attempt_history等)の変化で落ちる(順次実行では通る=1回目の並列run時の失敗1件は並列起因。ログは`er026.log`が順次run) |
| er008 gate | pytest 10/10 | なし | `run_project_regression.py`は同fileを0件収集(関数形式testのため。既存の仕様)。pytestで直接実行して10 PASS(`er008_pytest.log`) |

修正した新規failure(実装中に検出→是正済み、最終結果には残っていない):
- `er030_key_phrase_db_hybrid_m2_supply_01_test_01.test_kp_backend_remains_last_default` / `er030_..._family_x_production_wiring_01_test.test_run_key_phrases_default_kp_backend_is_strategy_l` / `..._source_reference_contract_01_test...`: `run_theme_scaffold`/`run_key_phrases`の`__defaults__[-1]`が`kp_backend`であることを固定するtestが、新引数`gloss_alignment_mode`を位置引数の末尾に足した初版で落ちた。**keyword-only引数(`*, gloss_alignment_mode=...`)に変更して是正**(`run_key_phrase_canonicalization`も同様)。最終: er030*_test* 108/108 PASS。

最終結果の件数: er003_test_key_words* 402/402(旧366+新規36) / er003_v1_n3_01*_test* 55/55 / er019 421/421 / er030*_test* 108/108 / er063 59/59 / er008 gate 10/10 / 単体 `er003_test_key_words_gloss_alignment.py` 70(旧34+新36)/70。
