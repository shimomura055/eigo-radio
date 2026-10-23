# IMPLEMENTATION_01(ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ①固有名詞 Run Entity Table [RET] / OPEN-472 / 委任_04、2026-10-23)

Status: **IMPLEMENTED(X evidence取得済み)_PENDING_Z_EVIDENCE_AND_FABLE**。PRODUCTION_WIREDはFable受入後(X/Z双方のevidence必須、Z=B工程)。
承認根拠: ユーザー原文 `docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER_02.md`(APPROVED_FOR_PRODUCTION、UDR #168)。11-7限定例外は使わない(承認済み正式採用に基づくProduction実装)。RET-3は`er103`本体G3の直接変更。
設計: `WIRING_DESIGN_01.md`+`WIRING_DESIGN_02.md`(OF反映差分表)、Opus条件C所見=`OPUS_REVIEW_02_COND_C.md`。証跡=`RUNTIME_EVIDENCE_01.md`。

## 1. 変更ファイル(file:line、2026-10-23 HEAD+本実装)
| file | 内容 |
|---|---|
| 新`er103_run_entity_table_01.py` | flag`RUN_ENTITY_TABLE_ENABLED=True`・`is_enabled()`(:39)・`is_active_for_run()`(:43、=flag∧`pnap.is_active_for_run()`)・`Entry`/`EntityTable`(位置紐づけ`occurrences`/`grant_for_phrase`/`entity_run_for_span`/`ret3_check`[W-05]/`audit_block`)・`restore_from_audit_block`(:337)/`entity_contributed`(:345)/`restorable`(:353)・`run_table`/`adapter_table`(W-04)・決定論導出`derive_entries`(:537、W-03)・`rules_version`/`builder_version`(W-10)・lockfile保存(`_file_lock`/`_save`、W-11)・`default_llm`/`ensure_table`(:782)/`ensure_table_safe`・`XProvider`(:911)/`ZProvider`(:955)・`operator_report_lines`(:1005) |
| `er103_proper_noun_alarm_policy_01.py` | `evaluate_alarm_eligibility(..., entity_table=None)`(:301): G3 RET-3(:370-390、不受理分岐でのみ)・G5反実仮想(:406-437)・`detail["entity_table"]`/`alarm_labels`(:439-442)。`evaluate_for_adapter(entity_table=None)`(:775、明示渡しのみ)。`build_alarm_records`(`entity_table_basis`)・`build_audit_block`(`entity_table`)・`render_operator_report`(根拠の別欄) |
| `er103_pnap_runner_hooks_01.py` | `run_with_alarm_hook(..., _ret_provider=)`(:37、構築点=ここ1か所)・`family_scope`(:98-102、X)・`emit_alarm_report(level_dir, table)`(:16) |
| `er063_family_z_audio_01.py` | `run_tts_stage`(:1300-1304、Z、`ZProvider`を渡す1呼出。dry_runはhookを通らない) |
| `er006_secondary_asr_01.py` | import(:202)・`_pnap_try_accept`の`entity_table=pnap_ret.adapter_table()`(:832、W-04: 自動取得はここだけ) |
| `er019_family_x_validation_inheritance_01.py` | 継承再判定(:360-369): 復元表 or None を明示。受理時に`pronunciation_alarm.entity_table`をdetailで更新(:389-) |
| `er078_reuse_value_guard_01.py` | Store guard(:62-67)・再判定後(:110)(W-06)。※UKUS commit `719de3adc`が同ファイルのcommitに本hunkを同梱(下記「運用上の事実」) |
| `er006_model_routing_contract_01.py` | `RUN_ENTITY_TABLE_MODEL="gpt-6-luna"`(:53)。`er006_model_routing_pricing_coverage_test_01.py`の対象に追加 |
| 新`er103_ret_baseline_signature_01.py` + `er103_ret_baseline_signature_v1.json` | 実装**前**に凍結した現行出力署名(1516件)。commit `78a2c7c6e` |
| 新`er103_run_entity_table_test_01.py` | 新test 97件 |
| `er111_pn_entity_table_trial_01_test_01.py` | 旧drift guard(複製元hash)を「Trial関数 vs Production本体」の差分testへ再構成(skipせず)。`entity_table`文字列の非存在assertを緩和(Trial moduleへの参照が無いことだけを固定) |

## 2. 安全条件の不変(受理境界は無変更)
`MIN_SPAN_SIMILARITY`・`R_GENERAL_WORD`・P-03・G3二重ASR・数値/否定・脱落・`MAX_DIFFS_PER_SEGMENT`・KP/JA/HEADING除外・slot下限・P-01入口・HR Lock・retry/fallback/regeneration・Gateはコード変更0。表が緩めるのは2点のみで、**いずれも従来不受理になる場合だけ**作用する(W-01の反実仮想で構造的に保証。表なし受理は表ありでもバイト一致をテスト固定)。
- 既定値のGrep: `RUN_ENTITY_TABLE_ENABLED = True`(1定義のみ、AST test)。env/argv/argparse参照0。rollback=Falseの1行(Store guard/継承でRET由来音声は再生成へ)。
- 失敗終了時の最終成果物: NER失敗/STOP/設定不備以外の例外は`status!=OK`で縮退=表なし=現行挙動(HR行き)。設定不備(cost logger未init・単価未登録の`RuntimeError`)は握りつぶさず伝播。

## 3. test結果(自分起因の失敗0)
- 新規 `er103_run_entity_table_test_01.py` 97 passed(位置紐づけ・W-01反実仮想・RET-3[W-05/W-02c]・負例回帰・構築[OF-03/05/10]・保存/resume[W-03/09/10/11]・継承[W-04]・Store guard[W-06]・DefaultOn scope isolation/AST・LLM失敗注入/STOP/config・等価性[W-02 a/b/c・凍結署名1516件・Trial関数との差分0]・retry/fallback整合・adapter統合[W-13]・Z runner統合・E-Grep)。
- 既存: `er103_proper_noun_alarm_policy_test_01.py` 52 passed / `er103_pnap_wiring_test_01.py` 71 passed / `er111_pn_entity_table_trial_01_test_01.py` 40 passed / er019継承・runner、er063 Z、er078、er104(KP vote guard lifted/wiring)、er109(golden・xz_scope・xz_isolation)、routing pricing coverage 等 868 passed(下記の既存失敗を除く)。
- 既存失敗(HEADの清浄worktreeでも同一に失敗=自分起因ではない): `er078_asr_unified_wiring_static_audit_01.py::test_asr_call_inventory_matches_allowlist`(allowlistが古い: hr_residual_summary・er104等。`er0*_test_*.py`の回帰patternに含まれない)・`er104_kp_vote_wiring_test_01.py::test_AST_attempt_ctx_vote_flag_is_forwarded_from_strict_only`。いずれも本件で触れていない(allowlist再生成は他agentの変更も取り込むため実施せず)。
- 全回帰 `run_project_regression.py`(pattern `er0*_test_*.py`、unittest discover): collected=6951 passed=6937 failed=4 errors=0 skipped=10(summary=`/tmp`の一時json、本文は下記)。失敗4件の分類(自分起因0): (1) `er003_test_bad.FixtureTests.test_case_0`=意図的な不良fixture(単独実行でも同じエラー、本件無関係)。(2) `er019_family_x_fx_20261016_wiring_01_test_01...test_fallback_used_consumers_do_not_read_kp_english_entries`=KP英語entry読取側allowlistにer110_family_y_*・er019_nws2_eval等が未登録(Family Y/他taskの追加ファイル、本件無関係)。(3) `er020_tts_retry_local_rewrite_fullseg_test_01...test_recorded_candidates`=er011_output記録データ(local_rewrite_recovery)に依存、本件無関係。(4) `er026...test_dry_run_all_stages_zero_side_effects`=共有ログのsnapshot比較で並行agent(UKUS等)の書込と競合、単独再実行でPASS(flaky)。加えて `er064_kp_int_01_test_01...test_no_tracked_py_or_template_modified` は回帰時点で未commitだった自分のevidence script(x1/x2 *.py)の差分を検出していた(commitで解消)。

## 4. 運用上の事実(隠さず記録)
1. **HEADの一時不整合**: UKUS 委任_04のcommit `719de3adc`(18:39 JST)が `er078_reuse_value_guard_01.py` を `git commit --only` した際、私の作業中hunk(`import er103_run_entity_table_01`)が同梱され、私のcommit `8dd3d4d7e`(新module)が入るまでの短時間、origin/mainのer078が未commitのmoduleをimportしていた(共有worktreeでの同一ファイル近接hunkの構造的リスク。W-15の想定どおり)。`8dd3d4d7e`でmoduleを追加して解消。再発防止=共有ファイルは編集直後に即commit(今回は回帰実行中でcommitを遅らせたのが原因)。
2. **本番監査ログへの混入と除去**: X-2(正式runner関数の実行)で`er011_output/attempt_history.jsonl`(append-only共有ログ)に私の隔離run由来の2行が追記された(`theme_id=theme_n8`、path=本evidence dir)。ファイル末尾の2行のみで、他agentの追記が後ろに無いことを確認したうえで、サイズ不変を検証して**その2行だけを除去**した(`grep RUNTIME_EVIDENCE_01`=0)。他の共有ログ(HR queue・Ledger・Master Store manifest・reuse_telemetry)への混入は0(grep済み、HR queue/Stage1[Ledger upsert・Perplexity]は隔離runでstub)。
3. 本番Ledgerへのupsert 0・HR Lock解除 0・Bertie 4clip/Z stage実行 0・`er109`系の編集 0・`er111_*`の削除 0。
4. W-13: Stage 1(`_resolve_unresolved_entity_for_review`)のrun単位memoは、既存の`pronun_ledger`(成功結果をupsert、次回はLedger hit)+negative cache(TTL)が永続memoとして機能し、一時失敗(401等)は意図的に保存しない(S1-03: 一時失敗を否定記録にしない)。run単位memoを足すとクレジット復旧後の同run内再試行が止まるため追加しない。**受理判定は呼出より前**で、Perplexity結果は受理を左右しない(None/{}/dictで同一acceptをtest固定)。operator報告は発音の根拠(Ledger/Perplexity)と実体表の根拠を別欄。
5. W-08(DECISION_LOG記録): LR時にNERは呼ばない(fail-closed許容)。LRで新たに出た固有名詞は表外=現行挙動(受理範囲は縮小方向)。LRで名前を残したtextは既存entryの`occurrences`で証拠が付く。
