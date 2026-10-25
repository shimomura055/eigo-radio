# TEST_PLAN_02(検証7点に対応するtest・runtime evidence計画。Opus追加testを含む)

管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02 / 日付: 2026-10-25 / **単体test(mock、API 0)は本委任で作成・実行済み**。runtime evidence(実API R1〜R4)は翌日JST 10/26以降の別委任。
TEST_PLAN_01からの差分: Opus追加test(M-1〜M-9・R-3・Z hooks)の追加、E-0(Prompt 2-R同等性確認)の削除(R-1採用でPrompt 2無変更)、evidenceへ「前のroundでNG→不在宣言→AUTOでNGがskipされる」の組込み。証跡置き場は従来どおり `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/`(新置き場なし)。

## 1. 新規testファイルと件数(全て API 0。LLM由来関数・TTS・実clientはmock、呼出回数をcounterで確認)
| ファイル | 件数 | 内容 |
|---|---|---|
| `er119_kp_human_review_01_test_01.py` | 56 | 核(Prompt 2-V、候補生成、flow/finalize、AUTO、宣言範囲、NG永続、resume/stale、消費者検査、並行制御、grammar kind fixture) |
| `er119_kp_human_review_cli_01_test_01.py` | 9 | CLI(status/show/select/--from-json/reselect/ng/unng/declare-absent/resolve-gloss、拒否=rc2で状態不変) |
| `er119_x_wiring_test_01.py` | 12 | Xの`main()`経由: 宣言なし=rc4、再実行でAPI 0・support再生成なし(M-4)、select後に先へ進む、`--kp-review auto`、tts入口のrc4/rc3、旧run互換、Part 1入力 |
| `er119_z_wiring_test_01.py` | 14 | Z: 両レベル候補生成→1回待機、再実行でAPI 0、hooksからmodeを渡せない、M-2/M-3(a)(b)、旧run互換、`main()`のrc=4+マーカー、RESTART_STORM間隔 |
| `er119_isolation_test_01.py` | 7 | `sc.run_key_phrases`無変更(source sha固定)、er119をimportするのはX/Z runnerのみ、grammar kindがProductionに無い、環境変数/getenvを読まない、runner既定=待機 |
| `er119_kp_human_review_outputs_test_01.py` | 6 | `verify_selection_matches_outputs`(TTS/study_text/ページ不一致の検出)、`mark-published`/`published_diff` |
| 合計 | **104** | |
- 共通fixture: `er119_test_support_01.py`(`Env`=5つのLLM由来関数をmockしcounter付き、`KpTestCase`)。
- 既存testの編集(回帰維持のための最小変更。Production挙動を変えるものではなく、「Human不在を明示宣言したctx」にする/X Productionの新KP入口をmockする/期待値を新仕様へ更新する):
  - Z mock系: `declare_in_mock_contexts`/`declare_ctx`/`predeclare`で「Human不在を明示宣言」(通常の`add_declaration`=宣言ファイル。runnerのProductionコードに暗黙のauto経路は作らない): `er026_family_z_e2e_integration_test_01`、`er026_family_z_src_posthoc_01_test_01`、`er026_family_z_stop_sentinel_test_01`(subprocess起動前に当該runへ宣言)、`er003_kp_general_explanation_01_runner_integration_test_01`、`er003_test_kp_gloss_alignment_{stop_paths,wiring}`、`er003_test_kp_gloss_person_alignment`。
  - X: `sc.run_key_phrases`をmockしていたtestは`er119_kp_wiring_01.run_kp_with_review`をmockする(X Productionは確認付きKP経路を通るため): `er019_family_x_kp_stage_fail_closed_01_test_01`、`er003_test_kp_fulltext_wiring_runners_01`、`er003_kp_general_explanation_01_runner_integration_test_01`、`er003_test_kp_gloss_alignment_stop_paths.pat_scaffold_passthrough`。**これを怠ると、旧mockをすり抜けて実LLMに到達する(後述「API 0の事故と是正」)**。
  - import許可集合: `er105_..._test_01.TestIsolation.ALLOWED`・`er108_..._test_01.Importers.ALLOWED`にer119を追加(意味を限定: 候補生成がer105の選定関数/er108のCMU gateを再利用)。
  - Part 1の件数: 単語解説は最大5件(`vocab_confirmed.json`)なので、`er003_kp_general_explanation_01_runner_integration_test_01`のZ Part 1 testの期待を3→5件へ更新(`len(doc["items"])`、`<dt>`の件数)。

### 意図的に期待を更新した既存assert(意味を残して限定。不整合な出力を期待値にしていない)
| test | 旧 | 新 | 理由 |
|---|---|---|---|
| `er026_family_z_src_posthoc_01_test_01.test_gate_stop_blocks_install_and_downstream` | `FAMILY_Z_SRC_UNRESOLVED`+監査JSON | `FAMILY_Z_KP_REVIEW_STOP`(採用可能0件)+install前に停止 | 出典を解決できない候補は候補単位にSRC D1で除外(M-7b)。推測補完せずSTOPする点は不変 |
| `er003_test_kp_fulltext_wiring_01.test_mock_kp_fn_is_three_items` | `[:3]` | `n_max=3`既定 | mock候補生成だけn_max=8 |
| `er003_test_kp_gloss_person_alignment.test_regenerate_path_goes_through_gate` | 再選定→REPAIRED・factory 2回 | 再finalize→CLEAN・factory 1回 | M-3(b): `--regenerate-stage kp_<lv>`は再選定しない。修復済みの確定物は書き直さない(idempotent finalize) |
| `er003_test_kp_gloss_alignment_wiring.test_z_stage_kp_reuse_of_pre_on_stage_stops_with_regenerate_instruction` | `GLOSS_ALIGNMENT_UNEVALUATED` | 同左 または `gloss未評価`(M-9の消費側検査) | 止まる理由は同じ。層が前段に1つ増えた |
| `er003_test_kp_gloss_alignment_wiring.test_regenerate_hr_resolve_rerun_uses_snapshot_and_old_asset_not_left` | regenerateで選定を引き直しHR停止 | regenerateは再選定せず、reselectで引き直した候補のHRはAUTO対象外 | M-3(b)。「旧glossが通らない/HR itemが確定に混入しない」不変条件は維持 |
| `er003_test_kp_gloss_alignment_stop_paths` T3(j)/(m)/(l-Z)/(exit) | HR itemを含む確定でZ stage停止 | HR候補はAUTO対象外=確定に入らない/resolve-gloss+Human選定で人間確定glossが入る/宣言なしはKP_REVIEW_PENDINGで非0終了 | HR候補は候補段階で旗付け。**T3(h-Z)は撤去**(Zのstage_kpでHR報告の書込失敗を検証する対象=確定物にHRが残る経路が無くなったため。X側T3(h)=`run_key_phrases`側の同検証は残置) |

### API 0の事故と是正(RESULT_PACKET_KPHR2.md参照)
`sc.run_key_phrases`をmockする既存X testが、X Productionの新KP入口(`run_kp_with_review`)をmockしていなかったため、実LLM(selector等)に到達した。是正: 該当testをmock、以後の回帰は**ネットワーク遮断harness**(`socket.connect`/`getaddrinfo`を遮断、huggingfaceのみ許可)で実行し、遮断下で`api.openai.com`への接続試行が0であることを確認した。

## 2. ユーザー検証7点 × test/evidence
| # | 検証 | 単体/統合test(mock、API 0) | runtime evidence(実API。別委任) |
|---|---|---|---|
| 1 | TOP 8/TOP 2が仕様どおり選定・保存 | Prompt 2無変更+sha固定、Prompt 2-Vの差分限定・sha固定・schema順(`phrase,reason_ja,word_count`)・user message(`TestPrompt2V`)。候補スキーマ/hash/Gate順序/dropped理由/dedup/outer retry条件(M-7c)/canonicalization INVALID再実行(M-7a)/qa_fail旗/gloss_hr旗/Redundancy旗(`TestCandidateGeneration`)。**M-1: 候補生成直後に`kp_dir/keywords_canonicalized.json`等が存在しない**(`test_candidates_generated_in_work_dir_not_kp_dir_M1`) | R1〜R4で実LLMの8件候補を取得し、Gate除外率・shortfallを実測 |
| 2 | Human選定が最終出力へ反映 | select検証(件数/NG交差/重複pair/qa_fail明示/gloss HR)、finalizeが`keywords_canonicalized.json`(KP)・`vocab_confirmed.json`(5件)・署名を書く、Part 1がvocab 5件を読む(`part1_items`、M-9)、`verify_selection_matches_outputs`(TTS/study_text/ページ)(`TestVerifyOutputs`)、Xでselect後の再開 | 選んだ3+5が最終成果物・TTS結果・study_text・公開ページに現れる(一致検証) |
| 3 | 未レビュー時 KP TOP3/解説TOP5で継続 | 宣言なし→PENDING・rc=4・副作用ファイル0・下流API 0(核/X/Z)、`auto`宣言→`UNREVIEWED_AUTO_ADOPTED`・`ai_rank`順・`auto_eligible`外とpair片方をskip・shortfall継続・0件はSTOP、未レビュー≠NG、**M-8: AUTOは確定集合Redundancy NGで次候補へ繰り上げ**、**M-6: 宣言→reselect→新roundはPENDING** | R2/R4(`--kp-review auto`)で上位3/5で継続し完走。`status=UNREVIEWED_AUTO_ADOPTED`の表示 |
| 4 | NG候補は自動採用されない | **M-5: 別run dirでも共有storeのNGで除外**、reselect後にLLMがNG句を再返却→`dropped(human_ng)`、AUTO走査skip、手編集でNGを混入した確定を拒否、used_form_key(所有格正規化)と`similar_to_ng`旗(R-2)、unngの記録 | R2で「R1で登録したNG句が新runのAUTO候補に出ても採用されない」(不在宣言→AUTO)を確認 |
| 5 | 再生成・再開時も選定結果保持 | resume(sha一致→API 0)、本文変更→STALE・NG保持、再選定上限2、旧候補archive、**M-2: gloss HR snapshotの署名不一致を退避**、**M-3(a)(b): input_shaに署名、事後Reviewで確定が変わると親sha不一致STOP、`--regenerate-stage kp_<lv>`=再finalize(再選定なし)+子孫stale化**、**M-3(c): rankキーでなくcandidate_idで同期**、idempotent finalize(署名同じなら本名ファイル不変)、**M-4: X再開でsupport・選定API 0** | Z: 確定後に`--stage kp`再実行で選定不変・API 0。X: 通常scaffold再実行でsupport再生成なし |
| 6 | 各Familyの正式経路で機能 | X: `main()`経由(scaffold/tts入口)。Z: `stage_kp`→`load_level_inputs`/`stage_pages`/`page_verify`の消費側検査。**Y: 経路なし=未整備として記録(PRODUCTION_WIREDにしない)**、A/B/C: `sc.run_key_phrases`のsource sha固定+既存回帰 | X・Zの正式入口で発火(entry_point/summaryに`kp_review`記録) |
| 7 | 既存Gate・音声構成に意図しない変更なし | §3の回帰(failed/errorsが基準から増えない)+Gate判定基準を変えていないことの確認(CMU/Validator/canon template/gloss規則はer119で未編集、`git diff`で対象ファイル限定) | 非KP音声はMaster Store再利用、KP segmentのみ生成し構成確認 |

### Opus追加testの対応表
| Opus項目 | test識別子 |
|---|---|
| M-1 候補dir分離 | `TestCandidateGeneration.test_candidates_generated_in_work_dir_not_kp_dir_M1` |
| M-2 snapshot旧選定復元防止 | `er119_z_wiring_test_01.TestZSignatureAndConsumers.test_M2_gloss_hr_snapshot_is_invalidated_when_signature_differs`(+署名不一致の同期拒否) |
| M-3 句とglossの取り違え/来歴/regenerate | `TestZPostHocReviewAndRegenerate.test_M3a_input_sha_includes_signature_and_M3b_regenerate_is_refinalize`、`TestZSignatureAndConsumers.test_M3a_stage_input_sha_changes_with_selection_signature`、`TestResumeStaleRegenerate`/`test_regenerate_equivalent_refinalize_keeps_files_when_signature_same` |
| M-4 X再開で有料API 0 | `er119_x_wiring_test_01.TestXWaitAndResume.test_rerun_while_pending_makes_no_llm_call_and_does_not_regenerate_support_M4` |
| M-5 別runでNG保持 | `TestNgPersistence.test_ng_shared_store_applies_to_other_run_dir_of_same_article_M5` |
| M-6 宣言失効 | `TestDeclarationScope.test_declaration_must_not_leak_to_next_round_after_reselect_M6`ほか |
| M-7a INVALID時の部分集合再実行 | `TestCandidateGeneration.test_canonicalization_invalid_item_excluded_and_rerun_M7a` |
| M-7c retry条件 | `test_outer_retry_only_when_auto_lt3_and_gate_drop_M7c`、`test_shortfall_without_gate_drop_does_not_retry` |
| M-8 確定集合Redundancy QA | `test_select_then_finalize_writes_confirmed_files_and_runs_final_redundancy_M8`、`test_final_redundancy_ng_on_human_selection_returns_to_pending_M8`、`test_auto_final_redundancy_ng_advances_to_next_candidate_M8` |
| M-9 vocab fail-closed/消費側Gate | `TestConsumerGuards.test_part1_items_fail_closed_when_vocab_missing_with_review_M9`、`test_vocab_items_subject_to_consumer_gates_M9`、`test_part1_items_is_vocab_5_and_ranks_independent_from_kp_rank_M9` |
| R-3 ロック競合 | `TestConcurrencyR3`(3件) |
| R-4 RESTART_STORM間隔 | `er119_z_wiring_test_01.TestRestartStormInterval` |
| C-4 Z hooksからmode不可 | `er119_z_wiring_test_01.TestZWait.test_hooks_cannot_carry_the_mode`、`TestDeclarationScope.test_no_environment_or_default_path_to_auto` |
| API 0の証明 | 各testの`Env.n`/`total_llm_calls()`counter、Zは`forbid`patch(実client/Redundancy QA/selector到達で即失敗)+mock_api_calls.jsonlのkind |

## 3. 回帰(既存test。`.venv\Scripts\python.exe -m unittest <module>`、1 moduleずつ逐次)
対象: er003_kp_general_explanation_01_runner_integration_test_01 / er003_test_kp_fulltext_wiring_01 / er003_test_kp_fulltext_wiring_runners_01 / er003_test_kp_outer_retry_exclusion_01 / er003_test_kp_review_required_retry_01 / er019_family_x_kp_stage_fail_closed_01_test_01 / er019_family_x_kp_structure_wiring_01_test_01 / er019_family_x_audio_production_runner_01_test_01 / er026_family_z_e2e_integration_test_01 / er026_family_z_fiction_production_runner_01_test / er026_family_z_src_posthoc_01_test_01 / er026_family_z_stop_sentinel_test_01 / er062_family_z_writer_01_test_01 / er063_family_z_audio_01_test_01 / er105_kp_fulltext_selector_01_test_01 / er108_kp_cmu_lexicon_gate_01_test_01 / er109_wiring_golden_test_01 / er109_xz_isolation_01_test_01 / er106_joint_runtime_evidence_01_test_01 / er117_x_chunk_wiring_test_01 / er117_z_chunk_wiring_test_01 / er003_test_kp_gloss_alignment_{stop_paths,wiring} / er003_test_kp_gloss_person_alignment / er003_test_kp_possessor_roles_wiring_01 / er003_kp_general_explanation_01_test_01(Part 1)。
基準: 実装前(HEAD)のfailed/errorsを基準とし、増やさない。結果表はRESULT_PACKET_KPHR2.mdおよびACTIVE_TASKに記録。**既存失敗(本変更と無関係・実装前[HEAD]から存在)**: `er109_wiring_golden_test_01`の3件(g0022|rejudge等)、`er109_xz_isolation_01_test_01.StaticIsolation`の2件(`test_importers_of_scope_module_are_a_fixed_production_list`・`test_m3_scope_entry_call_sites_are_fixed_and_literal`。他taskの`er118_*`/`er019_family_x_clobber_restore_03.py`が原因。HEADの一時worktreeで同2件がFAILすることを確認)。
- 意図的に期待を更新した既存assert(意味を残して限定): `er026_family_z_src_posthoc_01_test_01.test_gate_stop_blocks_install_and_downstream`(出典を解決できない候補はKP Human Reviewでは候補単位にSRC D1で除外され、採用可能0件ならSTOP=install前に停止。旧: `FAMILY_Z_SRC_UNRESOLVED`と監査JSON。実LLMのHuman不在でも候補段階で拒否される点は不変)、`er003_test_kp_fulltext_wiring_01.test_mock_kp_fn_is_three_items`(`[:3]`→`n_max=3`既定)。

## 4. runtime evidence run(本委任では実行しない。BUDGET_PLAN_02 §2)
| run | Family | 経路 | 確認 |
|---|---|---|---|
| R1 | X(既存記事1本) | HRあり: 候補生成→`select`→再開→TTS差分(KP segmentのみ)→player/ページ+`reselect` 1回(NG登録) | 検証1,2,4,5,6,7 |
| R2 | X(同記事の別run) | HRなし: `--kp-review auto`→継続→完走。**R1で登録したNGが共有storeでAUTOにskipされる**(NG句を含む記事で確認) | 検証3,4,6,7、`UNREVIEWED_AUTO_ADOPTED`表示 |
| R3 | Z(既存作品1本の複製run) | HRあり: kp stage→pending→`select`→`--stages provision_shell,gate,assemble,pages,page_verify`(1起動)で再開→page_verify | 検証1,2,4,5,6,7 |
| R4 | Z(同作品の別複製run) | HRなし: auto宣言→完走 | 検証3,6,7 |
- 公開ページは本番公開先へ書かない(複製runのpages_dir分離)。既公開ページの差替えはしない。Family Yはrunしない(`production_reachable=False`のまま、出力不変のみtestで確認)。
- 各runでは、有料launchの前に`tools/stop_scope_check_01.py`を実行(rc=3なら新規API呼出なし)。再起動は委任文が許す回数のみ。

## 5. PRODUCTION_WIRED判定(Family別、Fable独立受入)に必要な証拠
正式初回経路実装(済) / retry・fallback・regeneration・resume整合(§2の#5、単体済) / **正式runtime発火証拠(R1〜R4、未)** / Regression・Validator・integration PASS(§3) / 選定・Human介入・自動継続の実証拠(R1〜R4) / SSOT更新(OPEN-518=IMPLEMENTED_PENDING_EVIDENCE、DECISION_LOG、OPEN-484(g)) / Git / ユーザー承認仕様との一致(検証7点)。文法はPart 2採用確認後に別途。Yは未整備として追跡。**現時点は`PRODUCTION_WIRED`ではない。**
