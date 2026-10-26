# TEST_PLAN_01: テスト計画と実績(KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01)

2026-10-26 / API 0 / ネットワーク接続試行0(socket.connect/create_connectionを例外化したharness内で実行)。実行はすべて`.venv\Scripts\python.exe`。

## 1. 委任文 test (a)〜(j) との対応と実績

| 委任文 | 内容 | 実体 | 結果 |
|---|---|---|---|
| (a) | 11件の期待結果 | `er125_kp_rescue_production_test_01.py::TestEleven`(#1〜#11、#7bは未配線で従来どおり除外) | PASS |
| (b) | 敵対的85件で誤受理0 | `TestAdversarialNoFalseAccept`(conversions reject全件がrevertのみ、accept/preexisting_acceptは救済不要、idiom 15件)+`er105_kp_rule_compliance_test_01.py::TestAdversarial85`(85件固定) | PASS |
| (c) | 実データ315種で誤受理0 | `tools/quant_newly_accepted_01.py`(量化詞guardの新規受理: 133候補中**0**、単調性違反0)・`tools/make_rescue_eval_prod_01.py`(過去成果物334対: gate合格331のうち救済で変化**0**、不合格3は救済対象外) | PASS |
| (d) | A/B/C golden 1002件バイト一致 | `gen_abc_golden_01.py`再生成を`abc_golden_01.json`とcmp: BYTE_IDENTICAL。`TestAbcByteIdentical` | PASS |
| (e) | Human NG迂回不可 | `TestHumanNgNotBypassed`(原句・救済形の両方でexact一致、`auto_eligible_now`) | PASS |
| (f) | 決定論 | `test_determinism_same_input_same_output`(3回同一JSON)、`test_postprocess_does_not_mutate_input` | PASS |
| (g) | resume読み戻し一致 | `test_resume_readback_is_stable_and_self_consistent`(candidates_sha256不変・再annotate冪等・改ざん検出)、`TestAiIslandHrCandidatesUntouched`(AI島a2/b1bの既存候補不変・ファイルsha不変) | PASS |
| (h) | 辞書fail-closed | `TestLexiconFailClosed`(欠落dir/改ざん/メタ不一致/CRLF/空表で全経路無効) | PASS |
| (i) | 縮約形・所有格スロットの正規化 | `TestIdiomMechanism`(`can’t`/`can't`、`had our hands tied`等) | PASS |
| (j) | 量化詞限定詞guardの正負例 | `er105_kp_rule_compliance_test_01.py::test_quant_determiner_guard_applied_positive_and_negative`、`er125...::TestQuantifierGuardRegression` | PASS |

追加: kill switch(`EIGO_KP_RESCUE=0`)で全hook無効、gate hook連鎖の順序(roles->rescue)、gate内retry非消費(呼出1回)、Production非配線(`TestUnwiredInProduction`: 9ファイルがer125/er123を参照しない、er119をimportしない)、gloss/QAの失敗時にauto不可、QA再判定のkey不一致時NOT_REJUDGED、D1の曖昧/窓なし/違法正規化(`heated debate`型)の非救済、再帰遮断。

## 2. 実行結果(最終)

| suite | 件数 | 結果 | 備考 |
|---|---|---|---|
| `run_project_regression.py --pattern "er125*_test_*.py"` | 53 | 53 PASS | 本委任の新規 |
| `--pattern "er105*_test_*.py"` | 52 | 52 PASS | 量化詞guard追加後。`er105_kp_rule_compliance_test_01.py`は19件PASS。`TestIsolation.ALLOWED`へer125追加(旧規則の更新) |
| `--pattern "er119*_test_*.py"` | 133 | 131 PASS / 2 FAIL | **HEAD既存失敗2件**(`er119_grammar_review_test_01::test_grammar_files_not_tracked_dirs`=`er119_output/`が存在、`er119_isolation_test_01::test_only_x_z_runners_import_er119`=er121/er123/er124がimport。いずれも本委任以前から。offendersにer125は含まれない) |
| `pytest er123_kp_rescue_dev_01_test_01.py` | 154 | 154 PASS | DEV。unittest harnessではpytest形式を収集しないためpytestで実行(DESIGN-02と同じ) |
| `--pattern "er003*_test_*.py"`(Production回帰) | 1911 | 1910 PASS / 1 skip / failed 0 | 共有validatorへの副作用なし |

## 3. DEV/Production parity(量化詞guard)
`tools/quant_parity_01.py`(git HEADのer105+DEV `RulePatch(aux, quant)` vs 現worktree): parity=true、不一致0(`quant_parity_01.json`)。

## 4. 委任_02で追加するtest
配線後の`er105_kp_rule_compliance_test_01.py::test_rescue_flow_not_wired_in_er105`の改訂、H1〜H4それぞれの統合test(`generate_candidates`をmock LLMで通し、救済候補が`rescue`メタ付きで永続化され、resume・HR/HRなしで一貫すること、旧経路`run_key_phrases`が出力バイト同一であること)、Y/Z経路のSRC D1・人称整合との合成。
