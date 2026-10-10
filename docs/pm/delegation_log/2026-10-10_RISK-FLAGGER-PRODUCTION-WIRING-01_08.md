# RISK-FLAGGER-PRODUCTION-WIRING-01 委任_08 = Phase 2 C2(Writer差替え+旧Checker撤去+RF呼出配線)実装ログ

- 日付: 2026-10-10 / 実行: Sonnet(実行層) / ユーザーGo: 2026-10-10 / **課金API 0件**(API呼出部はstub test・stub E2E)
- ブランチ: `feature/factlock-rf-wiring-01`(mainへは一切commitしない。終了時 main へ checkout 済み。SSOT/ACTIVE_TASK/RESULT_PACKET未編集)
- 設計正本: DESIGN_03(1〜14節+15節 Opus再レビュー・15-2是正v3.1)、DESIGN_01 14節(必須修正8点)、委任ログ_06/_07。ユーザー確定: U-1 / U-2 / M1(a) Advanced限定・無条件ON / S3-1 案A。
- 使用モデル(PM_GOVERNANCE 25節): 本作業のLLM呼出0件。コード中の予定モデル=W-1 R0 `gpt-6-luna`・R1/R2 `gpt-6-astra`、RF `gpt-6-luna`/`gemini-3.5-flash-lite`(いずれもC1でroutingへリテラル固定済み、旧/下位モデルなし)。

## 0. git手順の実績

1. `git status --porcelain` を作業開始時に記録(514行、他タスク由来のdirty/untrackedは不触)。`git checkout feature/factlock-rf-wiring-01` -> `git merge main`(**fast-forward**。競合なし。ブランチ先頭 adcdf3e2 = C1 は main の祖先 f71dbb41 に含まれており、main側に取り込むべき凍結対象の変更なし)。
2. C2の変更を論理単位で4 commit(明示add、`-A`/`-f`未使用)。push は本ログ commit 後。
3. 作業中に **他agent由来の新規untracked** が出現(`docs/pm/delegation_log/2026-10-10_B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02_01.md`、`er052_output/b3_rootfix_trial_02/`)。本タスク由来ではないため不触・不add(委任文は「他agentは動いていない」だったが、作業ツリーを共有している並行作業が存在した可能性。mainへの checkout は影響しない)。

## 1. commit一覧(f71dbb41..HEAD)

| # | hash | 内容 |
|---|---|---|
| 1 | 11db202b | 本体: jaw/er012_e/entertainment runner(Writer差替え・旧Checker物理削除・M1(a)・RF配線・U-1/U-2・S3-2)+reconstruction legacy注記 |
| 2 | b4fdbd4a | 既存test更新(旧Fact Check系test削除/置換、ja_recheck test無効化、Trial testのlegacy skip) |
| 3 | 2a2ba645 | 新規test(旧Checker不到達static/配線順序/契約fail-closed/U-1/U-2/技術QA維持)・E5 golden・dangling after C2 |
| 4 | af8f9e7e | stub E2E runtime evidence・C2 test結果記録 |
| 5 | (本ログ) | 委任ログ_08 |

変更規模(f71dbb41..HEAD、本ログ除く、`git diff --numstat`): 23 files, +2,379 / -1,499。

| 種別 | ファイル | +/- |
|---|---|---|
| 本体 | er012_e_family_entertainment_two_level_runner_01.py | +76 / -463 |
| 本体 | er019_family_x_entertainment_production_runner_01.py | +121 / -80 |
| 本体 | er019_family_x_ja_writer_o_r1_r2_01.py | +37 / -230 |
| 本体(注記のみ) | er019_writer_run_summary_reconstruction_01.py | +5 / -0 |
| 更新test | er012_e..._test_01.py +134/-89 / er019_..._runner_01_test_01.py +302/-74 / er019_..._ja_writer_..._test_01.py +55/-149 / er019_..._ja_recheck_retry_01_test_01.py +24/-374 / er019_..._concreteness_an3_..._test_01.py +12/-31 / er053_family_x_factlock_ja_writer_01_test_01.py +37/-6 / er052_factlock_astra_e2e_runner_01_test.py +3 / er052_factlock_sweep_01_test_01.py +2/-2 / er052_factlock_writer_trial_01_test_01.py +1/-1 / er052_open243_m123_trial_test_01.py +4 | |
| 新規test | er053_c2_old_checker_removal_test_01.py +245 / er053_c2_wiring_test_01.py +279 | |
| 証跡(`er053_output/risk_flagger_production_wiring_01/`) | dangling_after_c2.json / gen_dangling_after_c2_01.py / gen_plain_golden_pre_c2_01.py / golden/w1_golden_plain_pre_c2_01.json / run_stub_e2e_c2_01.py / stub_e2e_c2_01/summary.json / c2_test_results_01.md | |

Prompt・schema変更: **0件**(A3/A4/W-1 Prompt・queue schema・contract は無変更。jaw/efamのPrompt定数は無変更)。

## 2. 撤去28行の実施状況(R-01〜R-28)

| ID | 対象 | 状況 |
|---|---|---|
| R-01 | jaw Original直後Fact Check+must-fix再生成+STOP | **実施**(物理削除) |
| R-02 | jaw R2直後Fact Check+R2 must-fix+STOP | **実施** |
| R-03 | jaw `build_must_fix_block` / `build_original_prompt(must_fix, full_ledger_text)` / `original_must_fix` | **実施**(`build_original_prompt(storyline, brief)`の2引数のみ。通常promptの出力はC2前と完全一致=E5 golden) |
| R-04 | jaw `_major_deviations`/`_must_fix_from_deviations` | **実施** |
| R-05 | jaw `full_ledger_text`ゲート | **実施** |
| R-06 | runner `run_ja_writer`のFact Check STOPハンドラ/`deviation_checks`保存/`fact_checks_summary` | **実施**(関数ごとW-1 glueへ置換) |
| R-07 | runner main `full_ledger_text=` / `storyline_line`/`selected_fact_brief_text`をefamへ渡す案B有効化 | **実施** |
| R-08 | efam `JARecheckRequiredError` | **実施** |
| R-09 | efam `_major_deviations`/`_must_fix_from_deviations` | **実施** |
| R-10 | efam M1(b)/G3(`open243_majors_only_in_summary`/`open243_m1_summary_only_retry`/`open243_g3_record_translation_minor`) | **実施** |
| R-11 | efam Advanced deviation check | **実施** |
| R-12 | efam Advanced `origin==ja_source`->JARecheck | **実施** |
| R-13 | efam M1(b)要約のみ再生成経路 | **実施** |
| R-14 | efam Advanced must-fix full regeneration+Hard STOP(`rejected_advanced_*`含む) | **実施** |
| R-15 | efam Standard deviation check | **実施** |
| R-16 | efam Standard ja_source->JARecheck | **実施** |
| R-17 | efam Standard must-fix regeneration+Hard STOP | **実施** |
| R-18 | efam `run_writer_stage` wrapper(案B: JA差し戻し・JA再生成・`ja_recheck_attempt*`) | **実施**(wrapperは`_run_writer_stage_once`の1行委譲のみ) |
| R-19 | efam main `fact_selection_evidence.json`読込による案B有効化 | **実施**(U-2でCLI自体を封鎖) |
| R-20 | evidence/audit出力(`must_fix_used`/`retried_for_deviation`/`deviation_overall_status`/`audit/deviation_check(s)`) | **実施**(`writer_run_summary.json`のキーも削除) |
| R-21 | `vfl01.run_deviation_check`+`DEVIATION_PROMPT`/`ORIGIN_ENUM` | **持ち越し(設計どおり共有関数残置)**: legacy A/B/C用。Family X経路からの参照は0(AST+spy test) |
| R-22 | `er019_writer_run_summary_reconstruction_01.py` | **実施(legacy注記)**: docstringにLEGACY/無効化注記。旧run再構成用に残置、新runからは呼ばない |
| R-23 | efam `open243_m1_enabled`ラッパ | **実施** |
| R-24 | efam `_open243_iol` | **実施**: `_advanced_in_one_line`へ改名、**環境変数条件を除去しM1(a)入力(`ja_text`+`ledger_text`)を常に渡す**。Advanced限定(Standardは呼ばない)。初回・段落retry再生成で同一関数 |
| R-25 | efam `OPEN243_G3_TELEMETRY_PATH` | **実施** |
| R-26 | `adv_gen`のM1 Prompt/`OPEN243_M1_ENV`/`open243_m1_enabled` | **技術QA/Trial側残置**(Prompt無変更・Trial用)。Production参照0(static test) |
| R-27 | `vfl01`の`OPEN243_M2`環境変数 | **持ち越し(共有関数残置)**。Family X経路から不到達 |
| R-28 | Trial runner `ARM_FLAGS`/`FLAG_KEYS` | **Trial側残置**(無変更)。HEAD上では旧腕は動かない(S3-4、再現はf71dbb41のworktree) |

`E2E_STUB`不使用(W-1 moduleのcall_astraから削除済み=C1)、G3/M2 env依存除去(Production経路のenv読取: `OPEN243_*`/`OPEN233_*` 0件、static testで固定)。

### 共用していた箇所の分離差分(技術QA側を残しFact Check側だけ外した)
- **`JAFactCheckStopError`**: jaw上で Fact Check(`stage=original/r2`)と記号QA(`stage=original_symbol/r2_symbol`)が共用 -> **`JASymbolCheckStopError`(記号QA専用、属性=`stage`/`rejected_text`/`findings`)へ改名・分離**。Fact用は削除。記号QAの挙動(検出->1回再生成->なお残ればSTOP、stage tag、evidence key)は不変。W-1 module側にも別の`JASymbolCheckStopError`あり(C1)。
- **`must_fix`**: `adv_gen/std_gen.generate_*(must_fix=…)`・`build_must_fix_block`(adv_gen側)・`_FAMILY_X_PARAGRAPH_RETRY_MUST_FIX`は**維持**(段落3分割retry専用。技術QA T-04)。外したのは Checker由来の `_must_fix_from_deviations`・jaw側`build_must_fix_block`・efamの Checker起点`must_fix_used`のみ。
- jaw/efam の `MAJOR`/`must_fix` 語の残存(36件)は dangling after C2 で分類(技術QA語彙11・Opus所見ラベル25・孤立0。5節)。

## 3. 維持した技術QA 18行+T-19(確認表)

| ID | 内容 | 状況・確認test |
|---|---|---|
| T-01 | R0直後 記号QA(Layer 2、1回再生成->STOP) | 維持(W-1に再実装済=C1)。jaw側(Trial互換)も維持: `SymbolQaMaintainedTests`(4) / W-1 `FlowTests` |
| T-02 | R2直後 記号QA | 維持。Astra段は案A(S3-1)=W-1(C1)。jaw側`test_r2_symbol_*` |
| T-03 | previous_response_id fallback | 維持(jaw、Trial互換)。`JawFallbackPathNoCheckerTests`(fallback経路でも旧Checker不到達) |
| T-04 | 段落3分割retry(1回)->STOP | 維持。`test_paragraph_retry_*`(M1(a)の「In one line」も同関数で再生成) |
| T-05 | `generate_family_x_*`の構造validation・`fallback_detected` | 維持(無変更)。`test_paragraph_retry_and_model_fallback_detected_path_without_checker` |
| T-06 | 予算ガード/単価未登録fail-closed | 維持。runner:各stage後+RF前後+W-1内`budget_check`=`efam.assert_budget_ok`。`test_budget_guard_*` |
| T-07〜T-16 | audio runner側(scaffold Gate/TTS retry/ASR/KP/assemble Gate/backend fail-fast等) | **無変更**(C2はaudio runnerに触れない)。既存audio系testは全suiteで回帰確認 |
| T-15 | OPEN-228封鎖stub(scaffold/tts/assemble/player) | 維持。efam test `TtsStageJapaneseTitleInjectionTests` |
| T-17 | B3 Fact ID整合STOP | 維持。`test_T17_*`+既存b3 test |
| T-18 | research_ledger検証(`run_verification_for_topic`) | 維持。`test_T18_*` |
| T-19 | 注記済みB3契約検証(V1〜V10) | 維持・**Writer入口で必須化**。runner `run_ja_writer`->`w1.run_w1_writer`->`validate_annotated_b3`、再利用分岐でも`load_reused_ja_text`が再検証。`ContractFailClosedTests`(3)+契約/W-1 test |

## 4. 実装箇所(ユーザー確定事項)

- **U-1**(W-1来歴なし旧Writer記事は通常Production経路でSTOP): `er019_family_x_entertainment_production_runner_01.py` `load_reused_ja_text()`(L206)・`LegacyWriterProvenanceStop`(L187)。再利用分岐(main L404)で `ja_writer/runtime_evidence.json` の存在・`chain_method=="W-1"`・契約再検証(`validate_annotated_b3`)・`annotated_md_sha256`一致を確認。違反は英訳・RFへ進まずSTOP。test: `ReusedJaProvenanceTests`(5)・`ResumeAndRegenerationPathTests`(U-1 2件)。
- **U-2**(`--ja-article` 入口封鎖): `er012_e_family_entertainment_two_level_runner_01.py` `guard_standalone_cli()`(L745)・`U2_CLI_BLOCK_MESSAGE`(L735、管理ID+理由+旧経路再現手順)。`main()`冒頭(L780、**課金・ファイル出力より前**)で `--ja-article`/`--stage writer|all`/`--regenerate-stage` をSTOP。残る単体CLI機能は`--stage ledger`のみ。`--ja-article`は引数としては残し(指定されたら明確なエラー)。test: `U2StandaloneCliBlockTests`(5、subprocessでout_dir未作成も確認)。
- **M1(a)**(Advanced限定・無条件ON、env廃止): efam `_advanced_in_one_line()`(L325)。`OPEN243_M1`参照0、`adv_gen.open243_m1_enabled`の呼出0。test: `test_m1a_in_one_line_always_gets_ja_text_and_ledger_advanced_only`・static test。
- **S3-1 案A**(Astra段記号QA、R2のみ同一R1生出力で1回再実行): C1(`er053_family_x_factlock_ja_writer_01.run_w1_writer`)で実装済み。C2の配線は`budget_check`をR1前/R1-R2間/再実行前後に渡す(`run_ja_writer`)。Prompt不変。
- **S3-2**(Standard派生元sha観測記録、判定・STOPに使わない): efam standard branch が `a2/audit/derived_from_advanced_sha256.json`(`derived_from_advanced_sha256`・`standard_article_sha256`)と `writer_run_summary.json`の`standard.derived_from_advanced_sha256`へ記録。test: `test_standard_records_derived_from_advanced_sha256_observation_only`。**S3-2は「Fable判断で採否」だったが、委任文の C に「Standard派生元sha(S3-2)を記録」とあるため採用**(観測のみ、新仕様判断を含まない軽微)。
- **RF配線**: runner `run_post_en_risk_flag()`(L245)。呼出は main の `with cl.logging_context(...)` ブロックの**外**(advanced直後 L422、standard直後 L434)。`rf.run_risk_flagger(article_path=<level>/article.md, ledger_path=research_ledger/verified_fact_ledger.txt[完全台帳], article_level=b1b|a2, producer=W-1 evidenceの注記manifest producer, run_label=--run-label, budget_check=efam.assert_budget_ok)` -> `rq.save_queue`。4条件逐次はRF module(C1)。非Blocking(例外はBudgetCheckStop/ArticleModifiedErrorのみ伝播、RF_UNAVAILABLE/PARTIAL/Queue保存失敗/想定外例外でも次工程へ)。記事sha不変assert(RF module+runner側で二重)。
  - **挿入位置の解釈**: 委任文Cは「er012_e のAdvanced英訳完了直後」だが、cl.logging_context の外で呼ぶ(Opus所見)ためにはefam内(runnerの`with`ブロック内で呼ばれる)ではなく、DESIGN_03 4-2の主挿入点=entertainment runner mainの`efam.run_writer_stage(only=…)`直後に置いた。順序(Advanced英訳 -> Advanced RF -> Standard生成 -> Standard RF -> Queue)は設計どおり。
- `--run-label`(記録専用の自由文字列、制御に影響しない)をentertainment runnerに追加(DESIGN_03 11-3/15-2 #9)。`entry_point.json`にRF/契約/Queue moduleのsha256も記録。

## 5. Dangling reference(`er053_output/risk_flagger_production_wiring_01/dangling_after_c2.json`)

| 指標 | C1 baseline | after C2 |
|---|---|---|
| Production scope 9ファイル 総ヒット(語単位) | 385 | **36** |
| うち Fact Checker専用シンボル25種(JAFactCheckStopError/JARecheckRequiredError/run_deviation_check/open243_*/OPEN243_*/ja_recheck/full_ledger_text= 等) | 多数 | **0** |
| 残件の分類 | - | 技術QA語彙11(段落retryの`must_fix`kwarg・記号QAのstage tag/evidence key) / Opus L2所見ラベル25(`MAJOR-n`。うちaudio runner 20、er012_e 5) / Trial・historical 0 / **本当に孤立 0** |

「該当件数0」の根拠: Fact Checker専用シンボルは0。残る36は`must_fix`(技術QA段落retry・記号QA)と`MAJOR-n`(Opusレビュー所見の通し番号ラベル。旧Checkerのseverity語とは無関係)で、規則(分類regex)と全residual行をJSONに保存。audio runnerのMAJOR 20件はC3の対象外(コメント/文字列のラベルのみ)。

## 6. test結果(詳細: `er053_output/risk_flagger_production_wiring_01/c2_test_results_01.md`)

- **C2対象set: 610 passed / 14 skipped / 0 failed**(skip 14 = Trial旧腕の削除済み機能を対象にしたlegacy test。理由はtest内に明記)。
- **全suite(er* 249ファイル、er015_standard_a2_6000…除外)**: 37 failed / 5733 passed / 14 skipped。pre-C2 f71dbb41のworktreeで同suiteを実行した結果と比較:
  - 32件はpre-C2でも同一に失敗(既存。asr/tts/batch/openのprice/…など、C2と無関係)。
  - 4件(er006_secondary_asr)は順序依存(`er002_test_ja_free_markdown_restore*.py`の後に失敗、単独は29 passed。bisect済み、C2無関係)。
  - 1件は **C1のflaky(`er053_review_queue_01._IndexLock`がWindowsでO_EXCL競合時に`PermissionError`を投げる。25試行中3回再現)**: 本C2では修正せず報告のみ(Production影響小: save_queueは非Blocking)。推奨1行修正=`except (FileExistsError, PermissionError):`。
- テストでtracked fileが変わった副作用(`er005_output/cost_baseline_01/cost_summary.json`、`er025_output/.../telemetry.jsonl`)は`git checkout --`で復元済み。
- 旧Checker不到達の実行証跡: stub E2E(`stub_e2e_c2_01/summary.json`): runner.main()を実コード駆動(契約検証・W-1[client scripted]・efam writer stage[生成関数のみstub]・RF[実module、API呼出関数のみstub]・Queue[実module、一時dir])、`vfl01.run_deviation_check`を「呼ばれたら失敗」にして完走。イベント順=`budget(research) -> W-1 R0(luna)->R1(astra)->R2(astra) -> advanced_translation -> in_one_line(M1a ja_text=True ledger_text=True) -> RF b1b(luna×2->gemini×2) -> queue_save:b1b -> standard_level_adjust -> RF a2(4条件) -> queue_save:a2`、2回目`--stage standard`(再利用+W-1来歴確認、W-1 API呼出0)も完走。`audit/deviation_check*.json`は生成されない。

## 7. 要確認・Fable判断が要る点

1. **挿入位置の解釈**(4節): efam内ではなくrunner mainに置いた(設計どおり、Opus所見のlogging_context外条件のため)。委任文の「er012_e のAdvanced英訳完了直後」という表現との差。
2. **S3-2採用**(上記): 観測のみ。不採用ならefamの該当約10行を削除するだけ。
3. **E5置換**: 関数ソースsha固定test(C1の`test_E5_..._pre_c2_only`)を、C2前(f71dbb41)のjawを`git show`から実行して保存したplain promptのgolden(17本)との**文字列完全一致**+Trial patched経路golden+Production `build_r0_prompt`一致の3者比較に置換(`test_E5_golden_after_c2_prompt_assembly_unchanged`)。
4. **C1 flaky(Queue lock PermissionError)**の修正をC3で行うか。
5. 他agent由来のuntracked(§0-3)。
6. `main`にtag(`rollback/pre-factlock-rf-wiring-01-20261010`)は未付与(`git tag`は空)。U-2エラー文言はtagではなくcommit `f71dbb41`のworktreeを案内している。

## 8. C3持ち越し

- audio runner TTS直前の三者sha照合(`ensure_rf_record`、S3-2の観測値も使える)
- audio側 `compute_cost_jpy_so_far` のfail-closed化(G-4)
- runnerのcost.json(`compute_stage_cost_breakdown`)をgemini対応の`compute_stage_cost_breakdown_multi`へ切替(現状openaiのみ。RFのGemini費用は`raw_usage_log.jsonl`と`efam.compute_cost_jpy_so_far`には入る)
- Astra pricing note更新(OPEN-246文言)
- (任意)C1の`_IndexLock` PermissionError対策
- 参考: Lane B(B3注記自動化)の配線が済むまで、通常Production runnerは新規記事で `AnnotatedB3ContractViolation` によりWriter入口でSTOPする(S3-3の想定どおり。mainへ統合するまで既存Production[旧Writer+旧Checker]は動き続ける)

## 9. 禁止事項の遵守

Agent起動なし・課金API 0件・main へcommitなし・SSOT(DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC/REPORT/REPORT_LEDGER)・`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET.md`未編集。Prompt/schema変更なし。旧Checker関連のenv/CLI/隠れswitchの新設なし(「Production到達可能な旧Checker経路」=0)。
