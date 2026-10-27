# TEST_PLAN_02 文法解説の事前生成(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02)

TEST_PLAN_01のT1〜T15のうち、共通核で検証できるものを`er120_part2_pregen_test_01.py`(36 test)で実装済み。runner/KCP/フォーム/CLI/evidence側の残分は委任_03/04/05。全てmock・API 0(実client生成はblock)。

| T | 内容 | test(`er120_part2_pregen_test_01.py`) | 状態 |
|---|---|---|---|
| T1 | 既定の待機(rc=4)維持。事前生成前に決められない・自動確定しない | `T1_DefaultWait` | 実装済み |
| T2 | Step B呼出点の単一化(spyで呼出元=`pregen_explanations`のみ)、呼出回数の固定(再実行/確定/finalize/require=0)、finalizeにLLM引数なし、事前生成なしfinalizeはAPI 0でfail-closed | `T2_StepBSingleCallSite` | 実装済み |
| T3 | legacy_postselect(review v1かつresult v1のみ再利用)、v1確定済み・結果なしの選定済みidのみpregen(stepB_generated)、未確定v1のv2置換、v2成果物ありで事前生成物なし=INTEGRITY(旧経路/再生成へ落ちない) | `T3_LegacyAndIntegrity` | 実装済み |
| T4 | reselect後に依頼書を『古い/未完成』へ置換し、事前生成後に全候補版へ。NG済み候補の解説は捨て、残りは再利用 | `T8_ReviewV2::test_selection_after_reselect...` | 実装済み |
| T5 | Part 1訳との食い違い=ISSUE(rc=4、凍結の有無に関係なく)、解消手段(了承は`--user-ref`必須・冪等・Part 1訳が変われば無効)、別候補選択、一致/無関係poolは問題なし | `T5_TranslationIssue` | 実装済み |
| T6 | level必須(全API。既定値なし)、`b1b`既定値/`LEVEL_KEY`/`g.LEVEL`参照0(AST/Grep)、候補docのlevel不一致fail-closed、`discover_dirs(level)`が候補docのlevel欄で確認、`study_dir_for`/`stage_names` | `T6_LevelRequired` | 実装済み |
| T7 | v1互換読取(v1 result/review の検査・描画・突合、1件はv1とバイト同一) | `T3`/`T9_ResultV2` | 実装済み |
| T8 | review v2: pick上限/理由/accept_ai規則、拒否時状態不変、id別sha記録、クリック順非依存(selection/署名/結果)、フォーム0件=omit同ロック・冪等、フォーム事前生成未完了は拒否、auto=TOP1のみ、候補0件の確定+空の事前生成物 | `T8_ReviewV2` | 実装済み |
| T9 | result v2: 本文出現順、1セクション/2 study-item、1件はv1とバイト同一、確定時sha固定(差替え検出)、改ざんresult拒否 | `T9_ResultV2` | 実装済み |
| T10 | PREGEN_MAX超過(8件生成・2件未生成表示・9番目は選べない・フォームn_not_generated)、失敗時の成果物/再開/fail-closed、予算STOP | `T10_CapAndFailure` | 実装済み |
| T11 | 失敗終了時の最終成果物(部分的な事前生成物+part2_failed.json+『未完成』依頼書。exporter/HR/grammar-showはデータを出さない) | `T10_CapAndFailure`/`T14_FormData` | 実装済み |
| T12 | Prompt sha不変・Trial-08選定定数不変・事前生成はref_ja=None | `T12_PromptsUnchanged` | 実装済み |
| T13 | 節単位4者一致(取り違え/欠落/重複を検出)、Std levelの独立dir・独立NG registry | `T18_StandardLevelAndSectionCheck` | 実装済み |
| T14 | `form_grammar_items`契約(キー・並び・AI推奨)、explanations_sha不一致でデータを出さない | `T14_FormData` | 実装済み |
| T15 | 新flag/環境変数なし、旧規則のGrep | `T20_StaticBoundaries`/`T6`/`T2` | 実装済み |
| T16 | 公開builder(`public_study_html`)のlevel必須・Std(Part 1なし)・未確定=待機、凍結値優先・KCP v1は1件のみ/2件以上はfail-closed・KCP v2 APIの自動利用 | `T19_PublicBuilderAndKcpCompat` | 実装済み |

## 回帰
- `er120_part2_grammar_production_01_test_01.py` 99件(pytest) PASS、`er119_grammar_review_test_01.py` 28件(27 PASS + HEAD既存失敗1)、`er120_part2_pregen_test_01.py` 36件 PASS。
- 意図的な失敗(runner未配線): IMPLEMENTATION_02 §3。

## 委任_03/04/05で追加するtest
- 03: X/Y/Z adapter(両level・runner統合)、`*_WRONG_LEVEL_SECTION`検査、`public_study_html`両level、`build_pages(study_html_by_level)`、旧integration testの更新、Dangling Grep。
- 04: KCP v2(`load_frozen_grammar_items`等)・`cmd_from_form`の文法照合とロック/書込み順・冪等、exporter接続、CLI(`--level/--ids`・了承・all-candidates)、`discover_dirs(run)[0]`撤去。
- 05: evidence(6セルの非0件経路、2件採用の1経路、所要時間・費用)。
