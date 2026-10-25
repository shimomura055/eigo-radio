# TEST_PLAN_02(Opus条件Aレビュー反映後のtest計画)

管理ID: PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_02 / 日付: 2026-10-25。実施済み=module単位(mock、API 0)。未実施=委任_03(runner/er119統合・runtime evidence)。

## 1. 実施結果(2026-10-25)
`py -m pytest er120_part2_grammar_production_01_test_01.py` = **99 PASS**(委任_01の77件を回帰として維持[M-1に伴い一部assertを更新、後述]+新規22件)。API 0の証明: autouse fixtureが実client生成(`b1s.get_client`)をblockし、呼ばれたら失敗。LLMは全てcall_fn mockで呼出回数をassert。Trial同一性(Prompt byte一致・29標本`select_tiered`一致・Step B実出力7/7構造検査通過・有料promptのsha再現)は全て維持。

回帰で更新したassert(不整合な出力を期待値にしない): D1(call数3→2、T1訳の参考訳渡しを撤回)/D7(pool一致時のみ参考訳)/D12(budget guard stage `part2_translate`が消える)/D14(T1失敗testを「T1関数が残っていない」testへ置換)/C6・C7・C9(reason必須・`review_status`・auto宣言dict)/E3〜E5・D3〜D6(`require_fresh_part2`の新引数)。

## 2. Opus追加testの対応表
| Opus追加 | test(新規) | 区分 |
|---|---|---|
| M-1 訳の出所・pool一致時のみref_ja・T1 call 0 | `test_M1_screen_translation_is_stepB_own_…`、`test_M1_lookup_ref_ja_is_trial07_exact_match_…`、`test_M1_matches_trial07_ref_ja_rule_source`(Trial規則の出所行を照合)、`test_D1`/`test_D7`/`test_D14` | module |
| R-7 pool変更で失効検出 | `test_M1_R7_pool_change_invalidates_cached_result_and_fresh_check` | module |
| M-2 事後top2変更後に旧結果が全入口で拒否 | `test_M2_post_review_top2_rejects_old_auto_result_at_every_entrance`(入口名6種をwhereに指定)、`test_M2_omit_and_zero_…`、`test_M2_tampered_…`(署名偽装・auto宣言欠落・前進不可status・材料欄改変・explain_signature・訳すり替え・引数省略) | module(全入口への呼出はrunner統合testで) |
| M-3 mode取得 | `test_M3_auto_only_via_er119_declaration_dict`(全関数の既定値にautoなし・os.environ不使用) | module(runner引数・hooksからautoにできないことの静的testは委任_03) |
| M-3 KPと文法の待機がrc=4の1回 | — | **委任_03**(統合) |
| M-4 input_sha・再finalizeで再抽出0回・PENDING | `test_M4_stage_input_shas_and_refinalize_without_extraction`(確定が変わるとinput_sha変化/候補なし・古い=Stale/`Part2PendingReview`・出力ファイル0) | module |
| M-5 NG 3方式 | `test_M5_ng_three_way_matching`、`test_M5_ng_persists_across_runs_even_with_different_quote_range` | module |
| M-5 枯渇でも自動ZEROにならない・`human_rejected_all` | `test_M5_exhaustion_never_auto_zero_and_human_rejected_all`(waitでもauto宣言でも待機) | module |
| M-5 再抽出上限・reselect上限 | `test_M5_reextract_once_then_limit_stop`、`test_M5_reselect_limit_is_two_and_choice_hidden_afterwards` | module |
| M-5 NGとNOT_SELECTEDの区別 | `test_M5_ng_vs_not_selected_distinction` | module |
| M-5(a) 別runでのNG保持(共有store) | module側はI/F(`ng=`引数)で上記testがrun間保持を再現。store本体の書込・lockはer119 | **委任_03**(er119) |
| M-6 ZEROがREVIEWED扱いにならない・理由必須・history | `test_M6_reason_required_and_history_records_rejected_details`、`test_M6_zero_is_never_reviewed_and_auto_never_counted_as_reviewed`(集計でauto_top1をレビュー済みに数えない、accept_aiの記録) | module |
| M-7 再開時に有料API 0回 | `test_M7_resume_after_stepB_failure_does_not_reextract`(Step A'' 0回・失敗記録`part2_failed.json`)。support・KPの呼出0はrunner側 | module(runner統合は委任_03) |
| R-1 Part 1が空のときもCSS | `test_R1_compose_includes_css_when_part1_is_empty` | module |
| R-2 Standardページに出ない | — | **委任_03**(静的test) |
| R-3 確定↔result↔md↔HTML | `test_R3_verify_selection_matches_outputs`(top2確定後に旧md/HTMLを拒否) | module(呼出はrunner) |
| R-4 範囲重なり除外・候補1件でtop2なし | `test_R4_overlapping_ranges_dropped_and_top2_hidden_when_single`、`test_R4_does_not_change_top1_on_29_samples`(19/4/6不変) | module |

変異検査(testの検出力): `require_fresh_part2`の結果↔確定照合を無効化→FAIL、`rank_eligible`の範囲重なり除外を無効化→`test_R4`がFAIL、reselect上限を無効化→`test_M5_reselect_limit`がFAIL、枯渇判定(`exhausted`)を外す→`test_M5_exhaustion`と`test_M5_reextract`がFAIL。いずれも元に戻して99 PASS。

## 3. 委任_03で実施するもの(runtime evidence含む。Opus指定)
- 統合test(mock): M-3 KPと文法の待機がrc=4の1回/M-4 `--regenerate-stage part2_b1b`で再抽出0回(runner経由)/M-5(a) 共有registryでのNG引継ぎ/M-7 再開時のsupport・KP・Step A''呼出0/R-2 Standardページ非表示/runner引数・hooks・環境変数から`auto`にできない静的test/`test_P3`(未配線assert)を「配線済み」assertへ置換。
- runtime evidence(X・Z各1 run以上): 実際のstage順でPart 2がTTS前に生成(stage順序logを添付)/pages・page_verifyと公開ページの一致検証(R-3)/HRなし(auto宣言)とHRあり(top2またはreselect)/rc=4からの再開でAPI 0/omitまたは0件の表示(mockで可)。copy-runの証跡だけでは弱いので、stage順序のlogを添える。
- 費用: `BUDGET_PLAN_02.md`参照。
