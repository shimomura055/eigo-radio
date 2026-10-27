# IMPLEMENTATION_02 文法解説の事前生成: 共通核の実装記録(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02)

Status: **IMPLEMENTED(核)**。到達上限=IMPLEMENTED(核)。X/Y/Z runner・ページbuilder・KCP(er128)・フォームexporter・CLI・evidenceは未配線(PRODUCTION_WIREDではない)。API 0・JPY0。
設計=`DESIGN_02.md`、契約=`SCHEMA_CONTRACT_01.md`、test=`TEST_PLAN_02.md`。承認済みPrompt/閾値/辞書/正規表現は編集していない(sha不変test)。新flagなし(承認済みProduction仕様の本配線の核)。

## 1. 変更したファイル(所有範囲)
| ファイル | 内容 |
|---|---|
| `er120_part2_grammar_production_01.py` | `LEVELS`/`level_name`/`check_doc_level`(level必須)、`pregen_explanations`(Step B唯一の呼出点)・`validate_explanations`・`explanations_complete`、`select_from_candidates_v2`(pick<=2)・`review_request_v2`・`finalize_review_record_v2`・`_grammar_selection_signature_v2`、`build_result_v2`・`finalize_part2_v2`(LLM 0)・`result_items`・`translation_issues`、`_expected_outcome_v2`・`_require_fresh_part2_v2`(`require_fresh_part2`が自動判別)、`render_markdown`/`render_html_block`のitems対応(1件はv1とバイト同一)、`count_grammar_blocks`、`write/load_explanations`、`Part2IntegrityError`。v1関数は読取互換のため残置(`LEVEL`定数含む)。`run_part2`はv1 legacy orchestratorとして残し、Step Bは`pregen_explanations`経由かつexplain_call_fn/client明示時のみ |
| `er120_part2_wiring_01.py` | `study_dir_for`/`stage_names`、`candidate_stage`(level必須)、`pregen_stage`/`candidate_and_pregen_stage`、`finalize_stage`(LLM 0・legacy限定・INTEGRITY・翻訳ISSUE)、`require_final`/`verify_outputs`(level必須・節単位)、`form_grammar_bundle`/`form_grammar_items`、`public_study_html(level=)`、凍結のlist[item]互換層(`_frozen_loaded/_frozen_for_selected/_cc_verify_and_freeze`)。旧`CAND_STAGE`/`FINAL_STAGE`定数は撤去(`stage_names(level)`へ) |
| `er119_grammar_review_01.py` | `LEVEL_KEY`撤去(levelは必須引数/`article_key.level`)、review v2(`new_pending_review`)、`ensure_grammar_review(level=)`(未確定v1をv2へ置換・依頼書は事前生成後のみ全候補版)、`op_decide`(pick/ids・v2は事前生成完了必須・id別sha記録)、`apply_form_selection`(文法0件=omit同ロック・冪等)、`op_accept_translation_diff`、`render_request_md`(全候補の文法名+解説全文・fail-closed)、`discover_dirs(run, level)`、古い依頼書の置換 |
| `er120_part2_pregen_test_01.py`(新) | 36 test(TEST_PLAN_02) |
| `er120_part2_grammar_production_01_test_01.py` | 既存99件。`level="b1b"`を渡すだけの呼出更新(19呼出)+P3許可リストへer128追加(KCP 02B導入時から失敗していた取りこぼし) |
| `er119_grammar_review_test_01.py` | 既存28件。helperに`level`/`pregen`を追加、assertの期待値を3箇所更新(下記) |

## 2. 既存testの期待値変更(理由付き・最小)
| test | 変更 | 理由 |
|---|---|---|
| `er119_grammar_review_test_01.py` GrammarCase.ensure/final/decide | `level="b1b"`渡し、decideはv2でpregen済みを前提、finalは確定済みなら選定済みidのpregenを先に実行 | levelが必須。Step Bは事前生成stageのみ |
| `...test_top1_accept_ai_top2_requires_reason...` | `rec["selection"]["choice"]=="top2"` -> `("pick", decision.choice=="top2")`、結果は`items[]` | v2はtop1/top2をpickへ正規化しdecisionに入力を残す |
| `...test_hand_edited_review_or_candidates_is_detected` | 改ざん対象を`selection.candidate_ids`に | v2のフィールド |
| `...TestCli...` | `grammar-show`の文言(『AI推奨 1』+解説全文)、事前生成後に選択 | 依頼書が全候補+解説全文になったため |
| `er120_part2_grammar_production_01_test_01.py` P3 | 許可リストにer128 | 既存の取りこぼし(HEADで失敗) |

## 3. 既存失敗/新規の未解消(責任範囲の切り分け)
- **本委任で意図的に失敗するようになったもの(runner/他モジュールが`level`を渡していないため。TypeErrorでAPI呼出前に停止=fail-closed)**:
  - `er120_part2_wiring_integration_test_01.py` 14件(Z/X runner経由)、`er119_z_wiring_test_01.py` 12件+`test_main_returns_4_with_marker_when_pending`(`2 != 4`。rc=4のはずがTypeErrorでrc=2)、`er119_kp_p7w5_e2e_test_01.py` 1件、`er128_*_test_*.py` 12件(Zrunner経由)。いずれも `TypeError: candidate_stage() missing 1 required keyword-only argument: 'level'`。委任_03のadapter(`level`引数・`pregen_stage`・`cand_marker(level=)`)で解消。
- **HEADで既に失敗していたもの(本委任と無関係)**: `er119_grammar_review_test_01.py::test_grammar_files_not_tracked_dirs`(untrackedの`er119_output/`[2026-10-25作成]が実リポジトリに存在)、`er119_isolation_test_01.py::test_only_x_z_runners_import_er119`(er121/er123/er124がallowedに無い)。
- 実行できるProduction経路は未接続(runnerが旧API呼出のまま)。到達上限=IMPLEMENTED(核)。

## 4. 次委任への引継ぎ(修正へ進む。委任_03/04)
**委任_03 (adapter/ページ/Validator)**:
1. X(`er019`): scaffoldで`candidate_and_pregen_stage`を両levelに(`study_dir_for("x",…)`)、`--stage study_text`のlevel許容(Adv限定撤去)、tts/assemble/player入口の`"b1b" in levels`をlevel別に、`build_player_html`にStd節の文法ブロック、`public_study_html(level=)`、記事別page scriptは今後のものから両level検査(公開済みは書換えない)。
2. Y(`er121`): `UNIT_NAMES/DEPENDENTS`に`stage_names(level)`(葉ノード)、`stage_kp`で両levelの`candidate_and_pregen_stage`(KP候補生成の前)、`_assert_study_ready`はpages/page_verifyのみ、`stage_pages`でlvd別差込、検証を`verify_outputs(level, html_text=節)`へ。
3. Z(`er026/er062/er063`): `DEPENDENTS/ALL_STAGES`、`load_level_inputs`のb1b限定撤去、`build_pages(study_html_by_level)`、`_verify_part2_outputs`を節単位へ、`cand_marker(…, level=)`・`finalize_stage`(LLM関数引数なし)・`require_final(level=)`。
4. runner/他の`p2w.*`呼出に`level`を渡す。`*_ON_STANDARD_PAGE`検査の置換、旧Dangling Grep、`er120_part2_wiring_integration_test_01`/`er119_z_wiring_test_01`/`er128`系の更新。
**委任_04 (KCP/FORM/CLI)**:
5. KCP(er128): 契約§4の4関数(`load_frozen_grammar_items`等)、`cmd_from_form`の文法照合(`explanation_full==explanations[id].explanation_md`バイト一致・id/title/件数<=2/重複なし)と**呼出順**(検証->KPロック->`gr.apply_form_selection`->sidecar->KPレコード保存[commit点])、`_write_grammar_sidecar`の`discover_dirs(run)[0]`を`discover_dirs(run, level)`へ(level必須・level別study dir)、`guard_grammar`の複数id対応、M8再バインドのitem反復。`confirm-revise`で文法集合を変える場合は`revoke`が必要(`apply_form_selection`は確定集合と異なるpickを`guard_grammar`で拒否)。
6. フォームexporter: `p2w.form_grammar_bundle(study_dir, level=)`を`export_form_data_01.main()`へ接続(`grammar_status`3値、`body`=`explanation_full`)。UI不変。
7. CLI(`er119_kp_human_review_cli_01.py`): `grammar-select --level --ids`(`choice=pick`)、`grammar-show`が`study_dir`を渡す(現状はrun dir+levelから特定)、`grammar-accept-translation`(`gr.op_accept_translation_diff`)、`grammar-pregen --all-candidates`(auto採用済みrunの事後Review用・有料opt-in)。`er119_kp_human_review_01.SLOT_RULES`の文法max(1)は文法reviewでは未使用(影響なし)。
**委任_05 (evidence)**: EVIDENCE_PLAN再設定(O-8)。6セルで非0件経路、2件採用を1経路で実証、所要時間(2分超なら並行化)、費用上限¥150。

## 5. 旧ルール撤去・残置のGrep(Charter 8)
| 識別子 | 状態 | 確認(Grep) |
|---|---|---|
| `LEVEL_KEY`(er119_grammar_review) | 撤去 | `grep -n LEVEL_KEY er119_grammar_review_01.py er120_part2_wiring_01.py` = 0件 |
| `CAND_STAGE`/`FINAL_STAGE`(wiring) | 撤去(`stage_names(level)`へ) | `grep -n "CAND_STAGE\|FINAL_STAGE" er120_part2_wiring_01.py` = 0件(runnerは独自定数) |
| `or "b1b"`/`discover_dirs(run)[0]`相当の暗黙既定 | 本委任の所有ファイルでは0件 | test T6(AST: `level*`引数にb1b/a2既定なし、`discover_dirs(run)[0]`文字列0件)。**er128.py:850,1255-1258は未編集(委任_04)** |
| `g.LEVEL`/`m.LEVEL`の新コード参照 | 0件(定数はv1読取専用として残置) | test T6 |
| `generate_explanation(`の呼出 | `pregen_explanations`内の1箇所のみ | test T2(定義+1呼出、wiring/gr=0) |
| `finalize_part2`/`run_part2`のv1 | 残置(legacy orchestrator。Production配線は呼ばない)。Step Bは明示opt-in時のみ | test T3 |
| `ON_STANDARD_PAGE`系 | 本委任の対象外(runner側。委任_03) | - |
