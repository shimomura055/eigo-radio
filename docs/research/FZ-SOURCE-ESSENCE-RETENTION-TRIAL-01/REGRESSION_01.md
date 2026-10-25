# REGRESSION_01: 案A Production配線の全回帰結果(2026-10-25、委任_04、費用0・API 0)

実装commit=`53ce7b397`(`er062_family_z_writer_01.py`+test+Seed 5作品+DEV guard)。実行は開発tree(未コミットの他agent差分・未追跡資産あり)で、Production実装を工作treeに置いた状態(実装commit前の同一内容)。

## 1. 実行結果
| 系統 | コマンド | 結果 |
|---|---|---|
| unittest群 | `PYTHONIOENCODING=utf-8 .venv\Scripts\python.exe run_project_regression.py` | collected=7,179 / passed=7,165 / failed=3 / errors=1 / skipped=10(rc=1) |
| pytest群(er078*/er103/er104*/er105/er106/er108/er109) | `.venv\Scripts\python.exe -m pytest <対象> -q` | 1,132 passed / 11 failed |
| Z writer 直接 | `pytest er062_family_z_source_essentials_test_01.py er062_family_z_writer_01_test_01.py er026_family_z_story_registry_*_test_01.py` | 実装直後の途中結果: 211 passed + 意図した4件のみ失敗(§2) → 期待値差替え後 全PASS。最終: `er062_family_z_source_essentials_test_01.py` 38 passed / 10 subtests |

## 2. 期待値を差し替えた既存test(設計どおり。理由)
| test | 理由 | 変更 |
|---|---|---|
| `ProductionSeedTest.test_production_seed_equals_t2_trial_seed` → `…_plus_narration_voice` | Seedに`narration_voice`が1キー増えた(案A) | 『T2 Seed + narration_voice 1キーのみ』をdict比較 |
| `TrialPromptMatchTest.test_r0_byte_identical_to_t2_and_t3_dumps` → `test_r0_matches_t2_and_t3_dumps_except_narration_line` | 開いた窓R0にNarration行が1行入る(導入2行の直後) | 期待値=旧dump+Narration行1行(意図した差分1点のみ) |
| `test_r1_r2_match_t3_dumps_except_intended_name_diff` | R1/R2にNarration行+`in third person`→欄参照句の置換 | `_revise_expect`に意図した2点(Narration行・置換)を加算 |
| `test_std_byte_identical_to_t3_dumps` → `test_std_matches_t3_dumps_except_narration_line` | StdにNarration行 | 期待値=旧dump+Narration行 |
| `test_checklist_generated_from_essentials` | CPにnarration行 | needleに`narration`を追加 |
| `fz_essence_dev_runner_01_test_01.py` | DEV runnerは歴史的資産化(fail-fast guard) | import時SystemExitなら`pytest.skip(allow_module_level)`。性質は`NarrationVoiceWiringTest`へ移植済み(欄なし=例外・描画位置・REVISE置換・Melos byte固定) |

新規追加test(`NarrationVoiceWiringTest`、課金0): 描画位置/Std伝達/REVISE置換/R0 Narration/narration_voice必須fail-closed(5種の不正値)/stage log用戻り値/通常・regenerate・部分runのdump/narration_voice変更でresume STOP/`in third person`残置はMelos用ベース文言のみ+`ESSENTIALS_EXEMPT_STORIES == ("melos",)`固定/Seed記入規則の構造検査/CP narration行+処置規則整合/本番→DEV runner参照0/DEV runner fail-fast guard/**4作品(賢者・開いた窓・猿の手=p2_s1、告げ口心臓=1b_s1)のR0/R1/R2/Std PromptがTrialが実送信したdumpとbyte一致(4×4=16/16)**。Melos GOLD sha(`MelosUnchangedTest`)は無変更で通る。

## 3. 残った失敗の分類(自分起因=0)
| 失敗 | 分類 | 根拠 |
|---|---|---|
| unittest `er053_family_x_factlock_ja_writer_01_test_01.StaticTests.test_w1_rf_queue_contract_referenced_only_by_entertainment_runner_after_c2` | 他agent起因(FX-CORE-NUMERIC-RETENTION-TRIAL-01の`er115_fx_numeric_retention_trial_01.py`がer053を参照) | assertメッセージに`er115_fx_numeric_retention_trial_01.py`。writer/Seedを参照しない |
| unittest `er095_b3_core_number_rounding_01_test_01.TestIsolation.test_not_imported_by_any_production_py_in_c1` | 同上(`er115_…`が許可リスト外でimport) | 同上 |
| unittest `er064_kp_int_01_test_01.ProductionUnchanged.test_no_tracked_py_or_template_modified` | 「未コミットの追跡.pyが無いこと」を検査。実行時は本実装が未commitだったため自分の4 fileも列挙(実装commit後の再実行では他agentの`er114_fz_narration_chunk_trial_01*.py`のみが列挙=他agent起因) | 実装commit後に再実行して確認 |
| unittest `er003_test_bad`(FixtureTests) | 意図的に失敗する入れ子fixtureの出力(`failed`集計に含まれない既知。TEST-HYGIENE-02 REGRESSION_BASELINE_01 §2) | 集計failed=3はer053/er095/er064のみ |
| pytest 11 failed(`er103_run_entity_table_test_01`5、`er104_kp_vote_wiring_test_01`1、`er109_wiring_golden_test_01`3、`er109_xz_isolation_01_test_01`2) | RET/ASR(er103/er104/er109)領域。他agentの進行中・未コミット差分(`er103_ret_baseline_signature_01.py`等)が原因 | 4 fileとも`er062_family_z_writer_01`/Seed/`narration_voice`を参照しない(`grep`)。失敗メッセージはRET entity_table KeyError・golden signature・import許可リスト |
| 自分が導入した1件(`test_historical_dev_runner_fail_fast_guard`のsubprocess出力がcp932でNoneType) | 自分起因 → 修正済み(`encoding="utf-8"`, `PYTHONIOENCODING`) | 再実行 38 passed |

自分起因の最終failed/errors=0(上記の自分起因1件は修正し再実行でPASS)。

## 4. 既存作品の副作用(再生成しない)
- Production builder(実Seed)で組んだR0/R1/R2/Std Promptが、Trialが実送信したdumpとbyte一致: 賢者の贈り物・開いた窓・猿の手(`fz_essence_01/<story>/p2_s1/writer/`)・告げ口心臓(`…/the_tell_tale_heart/1b_s1/writer/`)の**4作品×4段=16/16**(`test_four_works_prompts_match_trial_dumps_byte_for_byte`)。委任_03の先行検証(scratchpad複製)と同じ結論をProductionコードで再確認。
- 二十年後: Trial dumpなし。構造検査のみ(Narration行1件・位置・REVISE置換・Seed記入規則)。
- Melos: GOLD sha3種(r0/revise/std)不変、`in third person`はessentials=None経路のみ。
- 限界(記録): 猿の手の段落数+8(Trial Phase 2、事前基準±4未達)はノイズか副作用か未確定。
